"""Split a long recording of headwords into one clip per word (David, 2026-11-02; reworked 2026-11-03).

David reads the words in learning order, each once, with a pause between words and a short break
between the forms on one line (ὁ, ἡ, τό). His pauses vary from take to take (1.1–1.8 s in the test
take, 0.5–1.1 s in takes 1 and 2), and a break inside a line can be as long as a short pause between
words, so silence length alone cannot say where a word ends. The script therefore matches the sounds
to the script's lines:

  1. Loudness in 10 ms frames. Speech is any frame within SPEECH_DB of the take's loud level (its
     99th percentile); bursts under 60 ms are dropped as clicks. Sounds less than UNIT_GAP apart (the
     stops inside a word, under 0.3 s) are joined into one unit: a word, or one form of a line.
  2. The units are matched to the script's lines in order by dynamic programming. Each line takes one
     unit per form it prints (ὁ, ἡ, τό: 1 to 3; one more costs extra) and should last about
     a·forms + b·syllables seconds of speech, a and b fitted to the take itself. A long silence inside a
     line, or a pause much longer than the take's usual one before a line, costs extra. Sounds before
     the first word and after the last may be set aside (rustling, talk before or after the take), but
     only cheaply if they are well below the take's usual word loudness.
  3. Each clip runs from just before its first sound to just after its last (PAD_IN, PAD_OUT, never past
     the middle of the silence), with 10 ms fades, then is normalized: speech RMS to TARGET_DB, peaks
     no higher than PEAK_DB.

The review page marks lines whose length or number of units is far from the fit, and lists the sounds
set aside (written as aside_NN.mp3) so David can hear them. If there are fewer units than lines, a word
is missing and nothing is matched. Checked on the test take: the same 20 clips David approved. Clips are
MP3 (64 kbps mono, via lameenc) for the app; with --wav also 16-bit WAV.

Usage (from scripts/):
  python split_audio.py <take.wav> <script.csv> <out folder>
script.csv has columns n, id, greek, english (audio/script_test.csv). Writes <out>/<id>.mp3 and
<out>/review.html, a page that plays each clip beside its Greek.
"""
import csv
import html
import json
import os
import re
import sys
import unicodedata
import wave

import numpy as np

FRAME = 0.010     # s
SPEECH_DB = 22    # speech frames: within this many dB of the take's loud level
MIN_SOUND = 0.06  # s; shorter bursts are clicks
UNIT_GAP = 0.35   # s; sounds closer than this are one unit (gaps inside a word are under 0.3 s)
HISS_DB = 15      # high-band level above its floor that still counts as a sibilant
PAD_IN, PAD_OUT = 0.08, 0.20  # s kept before the first and after the last sound
FADE = 0.010      # s
TARGET_DB, PEAK_DB = -20.0, -1.0
RATE_OUT = 48000
MID_SKIP = 15     # most a sound between two words may cost to set aside (a word said twice)
GAIN_OVERRIDES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio", "gain_overrides.csv")
# clips whose start reaches back over a quiet initial fricative (see hiss_edges)
ONSET_OVERRIDES = os.path.join(os.path.dirname(GAIN_OVERRIDES), "onset_overrides.csv")
# by-ear fixes per take: kind "skip" sets aside the sound starting nearest `at` seconds (a misreading
# David said again), kind "missing" says the word `id` was not said at all (record it again), kind
# "redo" marks a clip David wants recorded again (cut as usual; audio_bundle.py leaves it out of the app),
# kind "split" cuts the sound holding `at` in two (two words run together), kind "join" adds the sound
# nearest `at` to the one before (a second reading on one line, e.g. πλέων (πλείων)), kind "pin" makes
# the word `id` start at the sound nearest `at` (where the matcher's guess was wrong), kind "lead" keeps
# only `at` seconds before the word `id` instead of PAD_IN (David: "clip a tiny bit at the front")
TAKE_FIXES = os.path.join(os.path.dirname(GAIN_OVERRIDES), "take_fixes.csv")


def read_wav(path):
    with wave.open(path) as w:
        ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        x = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        x = np.where(x >= 1 << 23, x - (1 << 24), x) / 2 ** 23
    elif width == 2:
        x = np.frombuffer(raw, dtype="<i2") / 2 ** 15
    elif width == 4:
        x = np.frombuffer(raw, dtype="<i4") / 2 ** 31
    else:
        sys.exit(f"unsupported sample width {width}")
    x = x.reshape(-1, ch).mean(axis=1)
    return x.astype(np.float64), rate


def runs(mask):
    """[(start, end)] of True runs in a boolean array (end exclusive)."""
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def find_units(x, rate):
    """Units of speech: start and end in seconds, and peak loudness in dB."""
    f = int(rate * FRAME)
    frames = x[: len(x) // f * f].reshape(-1, f)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    loud = np.percentile(db, 99)
    units = []
    for s, e in runs(db > loud - SPEECH_DB):
        if (e - s) * FRAME < MIN_SOUND:
            continue
        if units and (s - units[-1][1]) * FRAME < UNIT_GAP:
            units[-1][1] = e
        else:
            units.append([s, e])
    st = np.array([u[0] for u in units]) * FRAME
    en = np.array([u[1] for u in units]) * FRAME
    pk = np.array([db[s:e].max() for s, e in units])
    return st, en, pk


LABEL = re.compile(r"\((pl|gen|fut)\.\)")
DIPHTHONGS = {"αι", "ει", "οι", "υι", "αυ", "ευ", "ου", "ηυ", "ωυ"}


def syllables(greek):
    """Syllables as read aloud: vowels, diphthongs counted once, a diaeresis splitting them."""
    t = unicodedata.normalize("NFD", LABEL.sub("", greek).replace("(", "").replace(")", "").lower())
    count, prev = 0, ""
    for ch in t:
        if ch == "̈":
            prev = ""
        elif unicodedata.combining(ch):
            continue
        elif ch in "αεηιουω":
            if prev and prev + ch in DIPHTHONGS:
                prev = ""
            else:
                count, prev = count + 1, ch
        else:
            prev = ""
    return max(count, 1)


def forms(greek):
    return len([p for p in LABEL.sub("", greek).split(",") if p.strip()])


def match(st, en, pk, rows, pins=None):
    """Match units to script lines. Returns ([(first unit, end unit)] per line, set-aside units, flags).
    pins: {line index: unit index} lines that must start at that unit (take_fixes.csv, kind "pin")."""
    pins = pins or {}
    M, L = len(st), len(rows)
    if M < L:
        return None, list(range(M)), {}
    fo = np.array([forms(r["greek"]) for r in rows], float)
    sy = np.array([syllables(r["greek"]) for r in rows], float)
    speech = en - st
    drop = np.clip(2 + 3 * (pk - (np.median(pk) - 10)), 2, 40)  # cheap only well below the words
    cum = np.concatenate([[0], np.cumsum(drop)])
    gmed = np.median(st[1:] - en[:-1])

    def run(a, b, sigma):
        INF = 1e18
        dp = np.full((L + 1, M + 1), INF)
        dp[0] = cum[:M + 1]
        back = {}
        for i in range(L):
            pred = a * fo[i] + b * sy[i]
            spread = sigma * np.sqrt(max(pred, 0.3) / 0.6)
            for j in range(M):
                if dp[i][j] >= INF:
                    continue
                if i and j < M - 1:  # a sound between words set aside: a click, or a word said twice
                    c = dp[i][j] + min(drop[j], MID_SKIP)
                    if c < dp[i][j + 1]:
                        dp[i][j + 1] = c
                        back[(i, j + 1)] = ("skip", j)
                if i in pins and j != pins[i]:
                    continue
                pause = 0.0
                if i:
                    g = max(st[j] - en[j - 1], 0.05)
                    pause = min(6.0, 6 * np.log(g / gmed) ** 2)
                for k in range(1, int(fo[i]) + 2):
                    e = j + k
                    if e > M:
                        break
                    c = ((speech[j:e].sum() - pred) / spread) ** 2 + pause
                    c += (((st[j + 1:e] - en[j:e - 1]) / UNIT_GAP) ** 4).sum()
                    if k > fo[i]:
                        c += 6
                    if dp[i][j] + c < dp[i + 1][e]:
                        dp[i + 1][e] = dp[i][j] + c
                        back[(i + 1, e)] = j
        total = dp[L] + (cum[M] - cum)
        e = int(np.argmin(total))
        if total[e] >= INF:
            return None
        groups, i = [], L
        while i:
            j = back[(i, e)]
            if isinstance(j, tuple):  # a skipped sound
                e = j[1]
                continue
            groups.append((j, e))
            e, i = j, i - 1
        return groups[::-1]

    a, b, sigma = 0.30, 0.15, 0.12
    for _ in range(3):  # fit the take's own pace to the match, then match again
        groups = run(a, b, sigma)
        if groups is None:
            return None, list(range(M)), {}
        dur = np.array([speech[j:e].sum() for j, e in groups])
        (a, b), *_ = np.linalg.lstsq(np.stack([fo, sy], 1), dur, rcond=None)
        res = dur - (a * fo + b * sy)
        sigma = max(0.10, 1.4826 * np.median(np.abs(res - np.median(res))))
    used = {k for j, e in groups for k in range(j, e)}
    flags = {}
    for i, (j, e) in enumerate(groups):
        z = res[i] / sigma
        if e - j > fo[i]:
            flags[i] = "more sounds than forms"
        elif abs(z) > 2.5:
            flags[i] = "longer than expected" if z > 0 else "shorter than expected"
    return groups, [j for j in range(M) if j not in used], flags


def hiss_edges(x, rate, spans, sibilant, onset=frozenset()):
    """Lengthen a span over a quiet final sibilant (ς) that falls below SPEECH_DB and outlasts PAD_OUT.

    Hiss is measured on the first difference of the signal, which favours high frequencies; David's
    room noise is a low hum, so between words this band sits near its floor. A span grows, 10 ms at a
    time, while the band stays HISS_DB above the floor (gaps up to 30 ms allowed), never past the middle
    of the silence to the next span. (David, 2026-11-03: πρῶτος in take 2 lost its ς.)

    Starts move only for ids in `onset` (audio/onset_overrides.csv, David's by-ear list): a quiet
    initial fricative such as the χ of χθών (take 4, 2026-11-04) that begins more than PAD_IN before
    the measured start. Done per word because widening every start took in breaths."""
    f = int(rate * FRAME)
    d = np.diff(x, prepend=0)
    hi = 20 * np.log10(np.sqrt((d[: len(d) // f * f].reshape(-1, f) ** 2).mean(axis=1)) + 1e-12)
    loud = hi > np.percentile(hi, 20) + HISS_DB
    out = []
    for i, (s, e, name) in enumerate(spans):
        lo = (spans[i - 1][1] + s) // 2 // f if i else 0
        hi_lim = (e + spans[i + 1][0]) // 2 // f if i + 1 < len(spans) else len(loud)
        a, b = s // f, e // f
        k, miss = b, 0
        while k < hi_lim and miss <= 3:
            miss = 0 if loud[k] else miss + 1
            k += 1
            if loud[k - 1]:
                b = k
        # only where the hiss outlasts the usual padding: other clips stay exactly as they were, and
        # starts are never moved (widening them took in breaths before words)
        # and only on lines ending in a sibilant (ς, ξ, ψ): a trail after ἤδη is breath, not the word
        end = e if name not in sibilant or (b * f - e) / rate <= PAD_OUT else b * f
        start = s
        if name in onset:
            k, miss = a - 1, 0
            while k > lo and miss <= 3:
                miss = 0 if loud[k] else miss + 1
                if loud[k]:
                    a = k
                k -= 1
            if (s - a * f) / rate > PAD_IN:
                start = a * f
        out.append((start, end, name))
    return out


def clip(x, rate, spans, i, pad_in=PAD_IN):
    """Clip spans[i] (start, end in samples; spans sorted by time), never past the middle of a silence."""
    s, e = spans[i]
    lo = (spans[i - 1][1] + s) // 2 if i else 0
    hi = (e + spans[i + 1][0]) // 2 if i + 1 < len(spans) else len(x)
    y = x[max(lo, s - int(pad_in * rate)): min(hi, e + int(PAD_OUT * rate))].copy()
    n = int(FADE * rate)
    y[:n] *= np.linspace(0, 1, n)
    y[-n:] *= np.linspace(1, 0, n)
    f = int(rate * FRAME)
    rms = np.sqrt((y[: len(y) // f * f].reshape(-1, f) ** 2).mean(axis=1))
    speech = rms[rms > rms.max() / 10 ** (SPEECH_DB / 20)]
    gain = 10 ** (TARGET_DB / 20) / np.sqrt((speech ** 2).mean())
    gain = min(gain, 10 ** (PEAK_DB / 20) / np.abs(y).max())
    return y * gain


def limit(y, rate, ceiling):
    """Hold peaks under `ceiling` (linear) by turning down only the few ms around each one.

    Used when a by-ear gain override asks for more than the clip's peak allows: the peak is
    usually a π burst, and pulling just the burst down lets the vowel come up (David,
    2026-11-04: πέμπω still quiet after +4 dB, which its two π bursts had capped at +4.8)."""
    need = np.minimum(1.0, ceiling / np.maximum(np.abs(y), 1e-12))
    w = max(1, int(0.005 * rate))  # hold the reduction 5 ms either side of each peak
    from numpy.lib.stride_tricks import sliding_window_view
    held = sliding_window_view(np.pad(need, w, mode="edge"), 2 * w + 1).min(axis=1)
    smooth = np.convolve(np.pad(held, w, mode="edge"), np.ones(2 * w + 1) / (2 * w + 1), mode="valid")
    # each held value is the least gain within 5 ms, so a 5 ms average of them never exceeds the
    # gain a sample needs: the peaks stay under the ceiling and the turn-down has no hard edges
    return y * smooth


def write_mp3(path, y, rate):
    import lameenc
    enc = lameenc.Encoder()
    enc.set_bit_rate(64)
    enc.set_in_sample_rate(rate)
    enc.set_channels(1)
    enc.set_quality(2)
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    with open(path, "wb") as out:
        out.write(enc.encode(pcm) + enc.flush())


def write_wav(path, y, rate):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())


def review_page(path, rows, clips, asides, flags, take, loud, missing=(), redo=()):
    """One row per script word, flagged lines marked, then the sounds set aside.
    clips and flags are keyed by word id; missing lists ids David found not said in this take."""
    items = []
    for r in rows:
        c = clips.get(r["id"])
        flag = ("missing: record again" if r["id"] in missing
                else "redo: record again" if r["id"] in redo else flags.get(r["id"], ""))
        items.append({"n": r["n"], "id": r["id"], "greek": r["greek"], "english": r["english"],
                      "src": c and c["file"], "at": c and c["at"], "len": c and c["len"], "flag": flag})
    for k, c in enumerate(asides, 1):
        items.append({"n": "", "id": "", "greek": f"set aside {k}", "english": "not matched to a word",
                      "src": c["file"], "at": c["at"], "len": c["len"], "flag": "aside"})
    ok = len(clips) + len(missing) == len(rows)
    if not ok:
        status = (f"Fewer sounds than words ({len(asides)} sounds for {len(rows)} words): a word is missing, "
                  "so nothing was matched. The sounds are listed below in order.")
    else:
        status = (f"{len(rows)} words matched to the script's lines. "
                  + (f"{len(flags)} marked ‹?› because their length is off: listen to those first. " if flags else "")
                  + (f"{len(asides)} sounds before the first word or after the last were set aside; they are "
                     "at the end of the list." if asides else ""))
    level = (f"Peak level of the take: {loud:.0f} dBFS. Each clip is normalized, but a take peaking near "
             "−12 dBFS keeps hiss lower.")
    data = json.dumps(items, ensure_ascii=False)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Tertius audio: clip review</title>
<link href="https://fonts.googleapis.com/css2?family=Vollkorn:wght@400;600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>
body {{ font: 16px/1.5 "Source Sans 3", sans-serif; color: #222; max-width: 760px; margin: 32px auto; padding: 0 16px; }}
h1 {{ font: 600 26px Vollkorn, serif; margin: 0 0 4px; }}
.how {{ background: #f4f1ea; border-radius: 8px; padding: 12px 18px; margin: 16px 0 20px; }}
.bad {{ color: #a8402a; font-weight: 600; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ border-bottom: 1px solid #ddd; padding: 8px; vertical-align: middle; }}
tr.on td {{ background: #e5f4e4; }}
.n {{ width: 32px; color: #888; text-align: right; }}
.g {{ font: 30px Vollkorn, "GFS Didot", serif; }}
.e, .t {{ color: #777; font-size: 14px; }}
button {{ font: inherit; padding: 6px 14px; border-radius: 6px; border: 1px solid #1b6b6b; background: #fff; color: #1b6b6b; cursor: pointer; }}
button.play {{ padding: 4px 10px; }}
</style></head><body>
<h1>Tertius audio: clip review</h1>
<div>From <code>{html.escape(take)}</code>.</div>
<div class="how"><div class="{'' if ok else 'bad'}">{html.escape(status)}</div><div>{html.escape(level)}</div>
<div>Press <b>Play all</b> and read along; the row being played is highlighted. Click any row to hear that clip.</div></div>
<p><button id="all">Play all</button> <button id="stop">Stop</button></p>
<table id="t"></table>
<script>
const items = {data};
const t = document.getElementById("t"), audio = new Audio();
let queue = [];
items.forEach((it, i) => {{
  const tr = t.insertRow();
  tr.innerHTML = `<td class="n">${{it.n}}</td><td class="g" lang="grc"></td><td class="e"></td>
    <td class="t">${{it.flag && it.flag !== "aside" ? "<span class=bad>‹?› " + it.flag + "</span><br>" : ""}}${{it.src ? it.at.toFixed(1) + " s · " + it.len.toFixed(2) + " s" : "<span class=bad>no clip</span>"}}</td>
    <td>${{it.src ? '<button class="play">▶</button>' : ""}}</td>`;
  tr.cells[1].textContent = it.greek;
  tr.cells[2].textContent = it.english;
  if (it.src) tr.onclick = () => {{ queue = []; play(i); }};
}});
function play(i) {{
  [...t.rows].forEach((r, j) => r.classList.toggle("on", j === i));
  audio.src = items[i].src;
  audio.play();
}}
audio.onended = () => {{ if (queue.length) setTimeout(() => play(queue.shift()), 400); else [...t.rows].forEach(r => r.classList.remove("on")); }};
document.getElementById("all").onclick = () => {{ queue = items.map((it, i) => i).filter(i => items[i].src); play(queue.shift()); }};
document.getElementById("stop").onclick = () => {{ queue = []; audio.pause(); [...t.rows].forEach(r => r.classList.remove("on")); }};
</script></body></html>
"""
    with open(path, "w", encoding="utf-8") as out:
        out.write(page)


def split_unit(x, rate, st, en, pk, at):
    """Split the unit holding `at` seconds into the speech before and after it."""
    k = int(np.flatnonzero((st <= at) & (en > at))[0])
    f = int(rate * FRAME)
    frames = x[: len(x) // f * f].reshape(-1, f)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    speech = db > np.percentile(db, 99) - SPEECH_DB
    a, b, m = int(round(st[k] / FRAME)), int(round(en[k] / FRAME)), int(round(at / FRAME))
    left = np.flatnonzero(speech[a:m])
    right = np.flatnonzero(speech[m:b])
    if not len(left) or not len(right):
        sys.exit(f"take_fixes split at {at} s: no speech on one side")
    e1, s2 = a + left[-1] + 1, m + right[0]
    st = np.insert(st, k + 1, s2 * FRAME)
    en = np.insert(en, k, e1 * FRAME)
    pk = np.insert(pk, k + 1, db[s2:b].max())
    pk[k] = db[a:e1].max()
    return st, en, pk


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 3:
        sys.exit(__doc__)
    take, script, out = args
    rows = [{k: unicodedata.normalize("NFC", v) for k, v in r.items()}
            for r in csv.DictReader(open(script, encoding="utf-8-sig"))]
    x, rate = read_wav(take)
    st, en, pk = find_units(x, rate)
    # David's by-ear fixes for this take: a sound to set aside (a misreading), a word not said at all
    tname = os.path.splitext(os.path.basename(take))[0]
    fixes = []
    if os.path.exists(TAKE_FIXES):
        fixes = [r for r in csv.DictReader(open(TAKE_FIXES, encoding="utf-8-sig")) if r["take"] == tname]
    for r in fixes:  # two words said with too short a break between them to be told apart
        if r["kind"] == "split":
            st, en, pk = split_unit(x, rate, st, en, pk, float(r["at"]))
        elif r["kind"] == "join":  # a second reading of the line before (πλέων (πλείων)): one clip
            k = int(np.argmin(np.abs(st - float(r["at"]))))
            en[k - 1], pk[k - 1] = en[k], max(pk[k - 1], pk[k])
            st, en, pk = np.delete(st, k), np.delete(en, k), np.delete(pk, k)
    missing = {r["id"] for r in fixes if r["kind"] == "missing"}
    redo = {r["id"] for r in fixes if r["kind"] == "redo"}  # cut as usual, kept out of the app
    forced = {int(np.argmin(np.abs(st - float(r["at"])))) for r in fixes if r["kind"] == "skip"}
    said = [r for r in rows if r["id"] not in missing]
    keep = [j for j in range(len(st)) if j not in forced]
    pos = {r["id"]: i for i, r in enumerate(said)}
    pins = {pos[r["id"]]: keep.index(int(np.argmin(np.abs(st - float(r["at"])))))
            for r in fixes if r["kind"] == "pin"}
    groups, aside, flags = match(st[keep], en[keep], pk[keep], said, pins)
    groups = [(keep[j], keep[e - 1] + 1) for j, e in groups or []]
    aside = sorted([keep[j] for j in aside] + list(forced))
    flags = {said[i]["id"]: why for i, why in flags.items()}
    # every span to cut, in time order: matched lines by id, set-aside sounds as aside_NN
    spans = [(int(st[j] * rate), int(en[e - 1] * rate), said[i]["id"]) for i, (j, e) in enumerate(groups)]
    spans += [(int(st[j] * rate), int(en[j] * rate), f"aside_{k:02d}") for k, j in enumerate(aside, 1)]
    spans.sort()
    sibilant = {r["id"] for r in rows
                if re.sub(r"[^\w]", "", unicodedata.normalize("NFC", LABEL.sub("", r["greek"])))[-1:] in "ςξψ"}
    onset = set()
    if os.path.exists(ONSET_OVERRIDES):
        onset = {r["id"] for r in csv.DictReader(open(ONSET_OVERRIDES, encoding="utf-8-sig"))}
    spans = hiss_edges(x, rate, spans, sibilant, onset)
    os.makedirs(out, exist_ok=True)
    for old in os.listdir(out):  # clear clips from an earlier run of this take
        if old.endswith((".mp3", ".wav")):
            os.remove(os.path.join(out, old))
    # David's by-ear corrections: dB added to a clip after normalizing, never past PEAK_DB
    extra = {}
    if os.path.exists(GAIN_OVERRIDES):
        extra = {r["id"]: float(r["db"]) for r in csv.DictReader(open(GAIN_OVERRIDES, encoding="utf-8-sig"))}
    lead = {r["id"]: float(r["at"]) for r in fixes if r["kind"] == "lead"}
    made = {}
    for i, (s, e, name) in enumerate(spans):
        y = clip(x, rate, [(a, b) for a, b, _ in spans], i, lead.get(name, PAD_IN))
        if name in extra:
            # the full by-ear gain; where that would pass PEAK_DB, only the peaks are turned down
            y = y * 10 ** (extra[name] / 20)
            if np.abs(y).max() > 10 ** (PEAK_DB / 20):
                y = limit(y, rate, 10 ** (PEAK_DB / 20))
        write_mp3(os.path.join(out, name + ".mp3"), y, rate)
        if "--wav" in sys.argv:
            write_wav(os.path.join(out, name + ".wav"), y, rate)
        made[name] = {"file": name + ".mp3", "at": s / rate, "len": len(y) / rate}
    clips = {r["id"]: made[r["id"]] for r in rows if r["id"] in made}
    asides = [made[n] for _, _, n in spans if n.startswith("aside_")]
    peak = 20 * np.log10(np.abs(x).max() + 1e-9)
    review_page(os.path.join(out, "review.html"), rows, clips, asides, flags, os.path.basename(take), peak, missing, redo)
    if not groups:
        print(f"{len(st)} sounds for {len(said)} words: A WORD IS MISSING, nothing matched; written to {out}")
        return
    print(f"{len(clips)} clips for {len(rows)} words; {len(asides)} sounds set aside; peak {peak:.0f} dBFS; written to {out}")
    for r in rows:
        if r["id"] in missing:
            print(f"  missing {r['n']} {r['greek']}: not said in this take (take_fixes.csv)")
        elif r["id"] in redo:
            print(f"  redo {r['n']} {r['greek']}: to record again (take_fixes.csv)")
        elif r["id"] in flags:
            print(f"  check {r['n']} {r['greek']}: {flags[r['id']]}")


if __name__ == "__main__":
    main()
