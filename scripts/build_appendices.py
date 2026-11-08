"""Assemble Metzger's appendices (pp. 95-110) and link the Greek words to SBLGNT and Souter.

Usage: python scripts/build_appendices.py

Reads data/metzger/appendices/page-NNN.tsv (HEADING, NOTE, ROW, WORD, UNCERTAIN records) and
writes data/metzger/appendices.json as a list of sections, each with its heading and records
in page order. WORD records get lemma, match, nt_count and souter_id. In Appendix II each
compound verb is also tagged with the preposition and sense heading it is listed under.
"""

import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from metzger_match import Matcher  # noqa: E402

PREP_LINE = re.compile(r"^([Ͱ-Ͽἀ-῿]+)\s+\(1\)")


def main() -> None:
    M = Matcher()
    sections: list[dict] = []
    cur = None
    prep = sense = None
    for path in sorted((ROOT / "data/metzger/appendices").glob("page-*.tsv")):
        page = int(path.stem.split("-")[1])
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = line.split("\t")
            kind = r[0]
            if kind == "HEADING" and r[1].upper().startswith("APPENDIX"):
                cur = {"appendix": r[1], "page": page, "records": []}
                sections.append(cur)
                prep = sense = None
                continue
            if cur is None:
                cur = {"appendix": "(untitled)", "page": page, "records": []}
                sections.append(cur)
            rec = {"type": kind.lower(), "page": page, "fields": r[1:]}
            if kind == "HEADING":
                m = PREP_LINE.match(r[1])
                if m:
                    prep = m.group(1)
                sense = r[1]
            if kind == "WORD":
                rec.update(M.link(r[1]))
                if prep and cur["appendix"].upper().startswith("APPENDIX II"):
                    rec.update(preposition=prep, sense=sense)
            if kind == "UNCERTAIN" and cur["records"]:
                cur["records"][-1].setdefault("uncertain", []).append(r[1] if len(r) > 1 else "")
                continue
            cur["records"].append(rec)
    out = ROOT / "data/metzger/appendices.json"
    out.write_text(json.dumps(sections, ensure_ascii=False, indent=1), encoding="utf-8")
    for s in sections:
        c = Counter(r["type"] for r in s["records"])
        print(f"{s['appendix']} (from p. {s['page']}): {dict(c)}")
    words = [r for s in sections for r in s["records"] if r["type"] == "word"]
    print("WORD lemma match:", dict(Counter(w["match"] for w in words)))
    for w in words:
        if w["match"] in ("none", "fuzzy"):
            print(f"  check p.{w['page']}: {w['fields'][0]} -> {w['match']} {w['lemma']}")


if __name__ == "__main__":
    main()
