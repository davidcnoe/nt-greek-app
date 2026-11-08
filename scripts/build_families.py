"""Assemble Metzger's Part II root families and link each word to the NT lemma list and Souter.

Usage: python scripts/build_families.py

Reads the page transcriptions data/metzger/part2/page-NNN.tsv (records: ROOT, BREAK, WORD,
NOTE, UNCERTAIN; see data/metzger/part2/README.md), data/nt/lemmas.tsv, and
data/souter/entries.clean.jsonl. Writes data/metzger/families.json and prints a check report.

A family starts at a ROOT header or after a BREAK. At the top of a page the previous page's
family continues unless the page opens with a ROOT header; such families are marked
"crosses_page" so a reviewer can confirm the join.

Each word is checked three ways:
- lemma: matched to an SBLGNT lemma (exact, ignoring accents, or one letter off);
- nt_count: its NT frequency (Metzger required 3+ words per family occurring 10+ times);
- ocr_agrees: whether Tesseract's independent OCR of the same page contains the word
  (accents ignored), as a cross-check on the transcription.
"""

import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from segment_souter import strip_accents  # noqa: E402
from metzger_match import Matcher  # noqa: E402


def main() -> None:
    M = Matcher()

    pages = sorted((ROOT / "data/metzger/part2").glob("page-*.tsv"))
    families: list[dict] = []
    cur: dict | None = None

    def new_family(page: int, root: str | None = None, gloss: str | None = None) -> dict:
        f = {"id": len(families) + 1, "root": root, "root_gloss": gloss, "pages": [page],
             "crosses_page": False, "words": [], "notes": []}
        families.append(f)
        return f

    # Pages that open with a new family even though no root header is typed there (reviewed by eye).
    new_at_top = {int(l.split("\t")[0]) for l in
                  (ROOT / "data/metzger/part2/page_starts.tsv").read_text(encoding="utf-8").splitlines()[1:]
                  if l.split("\t")[1] == "yes"}

    for path in pages:
        page = int(path.stem.split("-")[1])
        if page in new_at_top:
            cur = None
        ocr_path = ROOT / f"data/metzger/ocr/page-{page:03d}.txt"
        ocr_keys = strip_accents(ocr_path.read_text(encoding="utf-8")) if ocr_path.exists() else ""
        recs = [r.split("\t") for r in path.read_text(encoding="utf-8").splitlines() if r.strip()]
        first = True
        for r in recs:
            kind = r[0]
            if kind == "ROOT":
                cur = new_family(page, r[1] if len(r) > 1 else None, r[2] if len(r) > 2 else None)
            elif kind == "BREAK":
                cur = None
            elif kind == "WORD":
                if cur is None:
                    cur = new_family(page)
                elif first and page not in cur["pages"]:
                    cur["pages"].append(page)
                    cur["crosses_page"] = True
                head = r[1].strip()
                if first and cur["words"] and cur["words"][-1]["greek"] == head:
                    first = False
                    continue  # word typed again at the top of the next page (διαλογίζομαι, pp. 81-82)
                w = {"greek": head, "grammar": r[2] if len(r) > 2 else "",
                     "gloss": r[3] if len(r) > 3 else "", "page": page, **M.link(head),
                     "ocr_agrees": strip_accents(head) in ocr_keys, "uncertain": []}
                cur["words"].append(w)
            elif kind == "NOTE":
                (cur or new_family(page))["notes"].append(r[1] if len(r) > 1 else "")
            elif kind == "UNCERTAIN" and cur and cur["words"]:
                cur["words"][-1]["uncertain"].append(r[1] if len(r) > 1 else "")
            first = False

    families = [f for f in families if f["words"]]
    for i, f in enumerate(families, 1):
        f["id"] = i
        f["frequent_members"] = sum(w["nt_count"] >= 10 for w in f["words"])
    out = ROOT / "data/metzger/families.json"
    out.write_text(json.dumps(families, ensure_ascii=False, indent=1), encoding="utf-8")

    words = [w for f in families for w in f["words"]]
    from collections import Counter
    print(f"{len(families)} families, {len(words)} words, "
          f"{sum(1 for f in families if f['root'])} with a stated root -> {out}")
    print("  lemma match:", dict(Counter(w["match"] for w in words)))
    print(f"  linked to a Souter entry: {sum(1 for w in words if w['souter_id'])}")
    print(f"  OCR agrees with transcription: {sum(w['ocr_agrees'] for w in words)} of {len(words)}")
    print(f"  marked uncertain by the transcriber: {sum(1 for w in words if w['uncertain'])}")
    print(f"  families with fewer than 3 words at 10+ (Metzger's own rule; check joins): "
          f"{sum(1 for f in families if f['frequent_members'] < 3)}")
    print(f"  families crossing a page break (check joins): {sum(f['crosses_page'] for f in families)}")


if __name__ == "__main__":
    main()
