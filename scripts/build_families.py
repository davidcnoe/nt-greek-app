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
from segment_souter import ALIAS, lev1, load_lemmas, strip_accents  # noqa: E402


def main() -> None:
    exact, loose = load_lemmas()
    by_first: dict[str, list[str]] = {}
    for l in exact:
        by_first.setdefault(strip_accents(l)[:1], []).append(l)

    souter: dict[str, dict] = {}
    for line in (ROOT / "data/souter/entries.clean.jsonl").read_text(encoding="utf-8").splitlines():
        e = json.loads(line)
        if e["lemma"] and e["lemma"] not in souter:
            souter[e["lemma"]] = e

    def variants(word: str) -> list[str]:
        """Spellings to try for a Metzger headword, in order: as typed, then the other half of
        "X and Y", then assimilated prefixes (συνκαλέω -> συγκαλέω), then the active of a middle."""
        w = unicodedata.normalize("NFC", word)
        out = [w] + [p.strip() for p in w.split(" and ")[1:]] if " and " in w else [w]
        if " and " in w:
            out[0] = w.split(" and ")[0].strip()
        more = []
        for v in out:
            for pre, opts in (("συν", ("συγ", "συλ", "συμ", "συσ", "συ")), ("ἐν", ("ἐγ", "ἐμ", "ἐλ"))):
                i = v.find(pre)
                if i in (0, 2, 3, 4) and (i == 0 or v[:i] in ("ἀπο", "ἐπι", "κατ", "ἐξ", "δι", "προ")):
                    more += [v[:i] + o + v[i + len(pre):] for o in opts]
            if v.endswith("ομαι"):
                more.append(v[:-4] + "ω")
            if v.endswith("εμαι"):
                more.append(v[:-4] + "ημι")
            if v.endswith("αμαι"):
                more.append(v[:-4] + "ημι")
        return out + [unicodedata.normalize("NFC", m) for m in more]

    overrides = {}
    for line in (ROOT / "data/metzger/lemma_overrides.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        m, lemma, _why = line.split("\t")
        overrides[unicodedata.normalize("NFC", m)] = lemma

    def match(word: str) -> tuple[str, str | None]:
        w0 = unicodedata.normalize("NFC", word)
        if w0 in overrides:
            return "override", overrides[w0]
        for v in variants(word):
            how, lemma = match_one(v)
            if how in ("exact", "accent"):
                return ("exact" if v == unicodedata.normalize("NFC", word) else "variant") if how == "exact" else how, lemma
        return match_one(unicodedata.normalize("NFC", word))

    def match_one(word: str) -> tuple[str, str | None]:
        w = unicodedata.normalize("NFC", word)
        w = ALIAS.get(w, w)
        if w in exact:
            return "exact", w
        k = strip_accents(w)
        if k in loose:
            return "accent", max(loose[k], key=lambda x: exact[x])
        near = [l for l in by_first.get(k[:1], []) if lev1(k, strip_accents(l))]
        if len(near) == 1:
            return "fuzzy", near[0]
        return "none", None

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
                how, lemma = match(head)
                w = {"greek": head, "grammar": r[2] if len(r) > 2 else "",
                     "gloss": r[3] if len(r) > 3 else "", "page": page,
                     "lemma": lemma, "match": how, "nt_count": exact.get(lemma, 0) if lemma else 0,
                     "souter_id": souter[lemma]["id"] if lemma in souter else None,
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
