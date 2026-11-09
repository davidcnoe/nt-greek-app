"""Recording script for Tertius's headword audio, after Telamon's (David, 2026-11-09).

All 1,287 headwords in learning order (the app's path: units in order, each word once), read as the
app prints them: Metzger's forms (οὐ, οὐκ, οὐχ), no genitive or article. Cut into takes of TAKE words
so a slip costs only one short take. Each word has a fixed clip key (T0001 …) kept in
audio/audio_ids.json: a key, once given, never changes, so a reordered path never mislabels a clip.

Writes, in audio/script/:
  script.html    every take, each on its own printed page, with the reading instructions
  take_NN.csv    n, id (clip key), greek, english for each take: what split_audio.py matches clips to

Run from scripts/. Then, per take:
  python split_audio.py ../audio/take_NN.wav ../audio/script/take_NN.csv ../audio/clips/take_NN
"""
import csv
import html
import json
import os
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audio", "script")
IDS = os.path.join(ROOT, "audio", "audio_ids.json")
TAKE = 100


def path_words():
    lex = json.load(open(os.path.join(ROOT, "prototype", "data", "lexicon.json"), encoding="utf-8"))
    seen, out = set(), []
    for u in lex["units"]:
        for form in u["words"]:
            if form in seen or form not in lex["words"]:
                continue
            seen.add(form)
            out.append({"word": form, "english": lex["words"][form]["g"]})
    return out


def keys_for(words):
    ids = json.load(open(IDS, encoding="utf-8")) if os.path.exists(IDS) else {}
    n = max((int(k[1:]) for k in ids.values()), default=0)
    for w in words:
        if w["word"] not in ids:
            n += 1
            ids[w["word"]] = f"T{n:04d}"
    with open(IDS, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=0)
    return ids


def note(greek):
    if "(or " in greek:
        return "Two spellings: say both in full."
    if "," in greek:
        return "Several forms: read them all, with only a short break between them."
    return ""


def main():
    words = path_words()
    ids = keys_for(words)
    os.makedirs(OUT, exist_ok=True)
    takes = [words[i:i + TAKE] for i in range(0, len(words), TAKE)]
    flagged, body = 0, []
    for t, take in enumerate(takes, 1):
        first = (t - 1) * TAKE + 1
        with open(os.path.join(OUT, f"take_{t:02d}.csv"), "w", encoding="utf-8", newline="") as f:
            out = csv.writer(f)
            out.writerow(["n", "id", "greek", "english"])
            for i, w in enumerate(take):
                out.writerow([first + i, ids[w["word"]], unicodedata.normalize("NFC", w["word"]), w["english"]])
        rows = []
        for i, w in enumerate(take):
            n = note(w["word"])
            flagged += bool(n)
            rows.append(f'<tr{" class=flag" if n else ""}><td class="n">{first + i}</td>'
                        f'<td class="g" lang="grc">{html.escape(unicodedata.normalize("NFC", w["word"]))}'
                        f'{f"<div class=note>{html.escape(n)}</div>" if n else ""}</td>'
                        f'<td class="e">{html.escape(w["english"])}</td></tr>')
        body.append(f'<section><h2>Take {t} <span>words {first}–{first + len(take) - 1} · save as '
                    f'<code>take_{t:02d}</code></span></h2>\n<table>{"".join(rows)}</table></section>')
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Tertius audio: recording script</title>
<link href="https://fonts.googleapis.com/css2?family=Vollkorn:wght@400;600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>
body {{ font: 16px/1.5 "Source Sans 3", sans-serif; color: #222; max-width: 720px; margin: 32px auto; padding: 0 16px; }}
h1 {{ font: 600 26px Vollkorn, serif; margin: 0 0 4px; color: #103166; }}
h2 {{ font: 600 22px Vollkorn, serif; margin: 32px 0 8px; color: #103166; }}
h2 span {{ font: 15px "Source Sans 3", sans-serif; color: #777; margin-left: 8px; }}
.how {{ background: #F3EDE2; border-radius: 8px; padding: 12px 18px; margin: 16px 0 24px; }}
.how li {{ margin: 3px 0; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ border-bottom: 1px solid #ddd; padding: 10px 8px; vertical-align: baseline; }}
tr.flag td {{ background: #f9eeda; }}
.n {{ width: 48px; color: #888; text-align: right; }}
.g {{ font: 32px Vollkorn, "GFS Didot", serif; }}
.note {{ font: 14px "Source Sans 3", sans-serif; color: #8a5a00; }}
.e {{ color: #777; font-size: 14px; }}
@media print {{ .how {{ break-after: page; }} section {{ break-before: page; }} section:first-of-type {{ break-before: auto; }} tr {{ break-inside: avoid; }} }}
</style></head><body>
<h1>Tertius audio: recording script</h1>
<div>All {len(words):,} words in learning order, as the app shows them, in {len(takes)} takes of up to {TAKE}.</div>
<ol class="how">
<li>As for Telamon: a quiet room, about a hand's width from the microphone, mono WAV.</li>
<li>Aim for the loudest words near −12 dBFS.</li>
<li>Start each take with 2 seconds of silence. Say each word once, then pause about 1½ seconds. Don't say the numbers.</li>
<li>Where a line has several forms (οὐ, οὐκ, οὐχ), read them all, with only a short break between them.</li>
<li>If you misread a word, stop the take and start it again: a take is only a few minutes long.</li>
<li>Save each take in this <code>audio</code> folder under the name shown in its heading (<code>take_01.wav</code> …).</li>
<li>The {flagged} highlighted words carry a note on how to read them.</li>
</ol>
{chr(10).join(body)}
</body></html>
"""
    with open(os.path.join(OUT, "script.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"{len(words)} words in {len(takes)} takes; {flagged} highlighted; written to {OUT}")


if __name__ == "__main__":
    main()
