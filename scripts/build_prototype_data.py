"""Copy the app's word and reading data into the web prototype.

Usage: python scripts/build_prototype_data.py   (after build_app_data.py and build_app_readings.py)

Writes prototype/data/lexicon.json and prototype/data/readings.json, unchanged in content
(compact JSON). Bump VERSION in prototype/sw.js afterwards so the offline cache refreshes.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "app" / "assets" / "data"
OUT = ROOT / "prototype" / "data"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("lexicon.json", "readings.json"):
        data = json.loads((SRC / name).read_text(encoding="utf-8"))
        (OUT / name).write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
