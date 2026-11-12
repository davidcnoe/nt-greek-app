"""List the words David must record again (David, 2026-11-04: "prep. separate list of rerecords").

Reads audio/take_fixes.csv: kind "missing" (a word not said in its take) and "redo" (a clip he wants
again). A word drops off the list once a re-record take (audio/clips/take_rN/) holds its clip.
Writes audio/script/rerecord.csv (n, id, greek, english, the script split_audio.py matches against)
and audio/script/rerecord.html (printable, as script.html). Run after editing take_fixes.csv.

When David has recorded the list as audio/take_rN.wav (N = 1, 2 …), copy rerecord.csv to
take_rN.csv and split it like any take:
  python split_audio.py ../audio/take_rN.wav ../audio/script/take_rN.csv ../audio/clips/take_rN
audio_bundle.py then takes the new clips (it skips the "redo" clips in their old takes).
"""
import csv
import html
import os
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXES = ROOT / "audio" / "take_fixes.csv"
SCRIPT = ROOT / "audio" / "script"
CLIPS = ROOT / "audio" / "clips"


def main():
    with open(FIXES, encoding="utf-8-sig", newline="") as fh:
        fixes = [r for r in csv.DictReader(fh) if r["kind"] in ("missing", "redo")]
    # a re-record that is itself marked redo (take_r4, 1351: David 2026-11-05) does not count as done
    redone = {(r["take"], r["id"]) for r in fixes if r["kind"] == "redo"}
    done = {f.stem for d in CLIPS.glob("take_r*") if d.is_dir() for f in d.glob("*.mp3")
            if (d.name, f.stem) not in redone}
    latest = {r["id"]: r for r in fixes}  # one line per word: its latest fix row
    lines = []
    for r in latest.values():
        if r["id"] in done:
            continue
        with open(SCRIPT / f"{r['take']}.csv", encoding="utf-8-sig", newline="") as fh:
            w = next(x for x in csv.DictReader(fh) if x["id"] == r["id"])
        why = "not said" if r["kind"] == "missing" else r["note"].split(":", 1)[-1].strip().split(";")[0]
        lines.append({**w, "greek": unicodedata.normalize("NFC", w["greek"]), "take": r["take"], "why": why})
    lines.sort(key=lambda w: int(w["n"]))
    with open(SCRIPT / "rerecord.csv", "w", encoding="utf-8", newline="") as fh:
        out = csv.writer(fh)
        out.writerow(["n", "id", "greek", "english"])
        for w in lines:
            out.writerow([w["n"], w["id"], w["greek"], w["english"]])
    rows = "".join(
        f'<tr><td class="n">{w["n"]}</td><td class="g" lang="grc">{html.escape(w["greek"])}</td>'
        f'<td class="e">{html.escape(w["english"])}<div class="why">{html.escape(w["take"].replace("_", " "))}: '
        f'{html.escape(w["why"])}</div></td></tr>' for w in lines)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Tertius audio: words to record again</title>
<link href="https://fonts.googleapis.com/css2?family=Vollkorn:wght@400;600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<style>
body {{ font: 16px/1.5 "Source Sans 3", sans-serif; color: #222; max-width: 720px; margin: 32px auto; padding: 0 16px; }}
h1 {{ font: 600 26px Vollkorn, serif; margin: 0 0 4px; }}
.how {{ background: #f4f1ea; border-radius: 8px; padding: 12px 18px; margin: 16px 0 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ border-bottom: 1px solid #ddd; padding: 10px 8px; vertical-align: baseline; }}
.n {{ width: 48px; color: #888; text-align: right; }}
.g {{ font: 32px Vollkorn, "GFS Didot", serif; }}
.e {{ color: #777; font-size: 14px; }}
.why {{ color: #8a5a00; font-size: 13px; }}
/* dark mode (David, 2026-11-11) */
:root {{ color-scheme: dark; }}
body {{ background: #14171c; color: #e6e2da; }} h1 {{ color: #f1ece2; }} a {{ color: #7cc4c4; }}
.how {{ background: #232830; color: #e6e2da; }} td {{ border-bottom-color: #333a44; }} tr.on td {{ background: #20402f; }}
.g {{ color: #f1ece2; }} .e, .t, .n {{ color: #9a9fa8; }} .bad, .why .ok {{ color: #f08a6c; }} .ok {{ color: #7cc4c4; }}
button {{ background: #1d2229; color: #7cc4c4; border-color: #3f8f8f; }}
</style></head><body>
<h1>Words to record again</h1>
<div>{len(lines)} word{"s" if len(lines) != 1 else ""}, in learning order.</div>
<div class="how">Record them as one take, like the others: 2 seconds of silence, each word once, about 1½ seconds
between words. Save it as <code>audio/take_r1.wav</code> (the next one <code>take_r2.wav</code>, and so on).
The list can wait until it is longer; it grows as you review the takes.</div>
<table>{rows}</table>
</body></html>
"""
    (SCRIPT / "rerecord.html").write_text(page, encoding="utf-8")
    print(f"{len(lines)} words to record again: " + ", ".join(f"{w['n']} {w['greek']}" for w in lines))


if __name__ == "__main__":
    main()
