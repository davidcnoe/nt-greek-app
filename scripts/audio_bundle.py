"""Copy David's approved word clips into the prototype (after Telamon's audio_bundle.py).

Reads audio/clips/<take>/<key>.mp3 (written by split_audio.py; aside_NN.mp3 files are skipped) for the
takes listed in audio/approved_takes.txt, copies each to prototype/audio/<key>.mp3, and writes
prototype/data/audio.json: {word id: clip key} for every word with a recording. Clips marked "redo" in
audio/take_fixes.csv stay out. Words not on the list show a dummy play button that does nothing.
"""
import csv
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "audio" / "clips"
OUT = ROOT / "prototype" / "audio"
LIST = ROOT / "prototype" / "data" / "audio.json"
KEY = re.compile(r"^T\d{4}$")


def main():
    ids = json.loads((ROOT / "audio" / "audio_ids.json").read_text(encoding="utf-8"))
    word_of = {k: w for w, k in ids.items()}
    fixes = ROOT / "audio" / "take_fixes.csv"
    rows = []
    if fixes.exists():
        with open(fixes, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    redo = {(r["take"], r["id"]) for r in rows if r["kind"] == "redo"}
    lst = ROOT / "audio" / "approved_takes.txt"
    approved = {l.strip() for l in lst.read_text(encoding="utf-8-sig").splitlines() if l.strip()} if lst.exists() else set()
    OUT.mkdir(exist_ok=True)
    have = {}
    for take in sorted(p for p in CLIPS.iterdir() if p.is_dir() and p.name in approved):
        for f in sorted(take.glob("*.mp3")):
            if not KEY.match(f.stem) or (take.name, f.stem) in redo:
                continue
            if f.stem in have:
                raise SystemExit(f"{f.stem} is in both {have[f.stem]} and {take.name}")
            if f.stem not in word_of:
                raise SystemExit(f"{f.stem} ({take.name}) is not a clip key in audio_ids.json")
            have[f.stem] = take.name
            shutil.copyfile(f, OUT / f.name)
    for f in OUT.glob("*.mp3"):
        if f.stem not in have:
            f.unlink()
    LIST.write_text(json.dumps({word_of[k]: k for k in sorted(have)}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(have)} clips copied; {len(ids) - len(have)} words have none yet")
    owed = sorted({r["id"] for r in rows if r["kind"] in ("redo", "missing") and r["take"] in approved and r["id"] not in have})
    print(f"{len(owed)} redo/missing words from approved takes still owed a re-record: {' '.join(owed)}" if owed
          else "every redo/missing word from approved takes has an approved re-record")


if __name__ == "__main__":
    main()
