"""Assemble Metzger's Part I frequency lists and link each word to SBLGNT and Souter.

Usage: python scripts/build_part1.py [COMPARE_LIST]

Reads data/metzger/part1/page-NNN.tsv (records: TIER, WORD, NOTE, UNCERTAIN; see
data/metzger/part1/README.md). Writes data/metzger/part1.json:
  {"introduction": [paragraphs], "tiers": [{heading, min, max, words: [...]}], "notes": [...]}
Each word: greek, grammar, gloss, derivative, page, lemma, match, nt_count, souter_id,
ocr_agrees, uncertain.

COMPARE_LIST (optional) is a plain-text word list from a later edition, one headword per line
under "Words occurring ..." headings. It is used only to print a comparison report; nothing
from it is written to the repository.
"""

import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from metzger_match import Matcher, nfc  # noqa: E402
from segment_souter import strip_accents  # noqa: E402


def parse_tier(h: str) -> tuple[int, int | None]:
    nums = [int(n) for n in re.findall(r"\d+", h)]
    if re.search(r"more than", h, re.I):
        return nums[0] + 1, None
    if len(nums) >= 2:
        return min(nums), max(nums)
    return (nums[0], nums[0]) if nums else (0, None)


def main() -> None:
    M = Matcher()
    intro: list[str] = []
    notes: list[dict] = []
    tiers: list[dict] = []
    for path in sorted((ROOT / "data/metzger/part1").glob("page-*.tsv")):
        page = int(path.stem.split("-")[1])
        ocr_path = ROOT / f"data/metzger/ocr/page-{page:03d}.txt"
        ocr_keys = strip_accents(ocr_path.read_text(encoding="utf-8")) if ocr_path.exists() else ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = line.split("\t")
            kind = r[0]
            if kind == "TIER":
                lo, hi = parse_tier(r[1])
                tiers.append({"heading": r[1], "min": lo, "max": hi, "page": page, "words": []})
            elif kind == "WORD":
                if not tiers:
                    tiers.append({"heading": "(before first heading)", "min": 0, "max": None,
                                  "page": page, "words": []})
                head = r[1].strip()
                w = {"greek": head, "grammar": r[2] if len(r) > 2 else "",
                     "gloss": r[3] if len(r) > 3 else "", "derivative": r[4] if len(r) > 4 else "",
                     "page": page, **M.link(head),
                     "ocr_agrees": strip_accents(head.split(" and ")[0]) in ocr_keys, "uncertain": []}
                tiers[-1]["words"].append(w)
            elif kind == "NOTE":
                (intro if not tiers else notes).append(r[1] if not tiers else {"page": page, "text": r[1]})
            elif kind == "UNCERTAIN" and tiers and tiers[-1]["words"]:
                tiers[-1]["words"][-1]["uncertain"].append(r[1] if len(r) > 1 else "")

    out = ROOT / "data/metzger/part1.json"
    out.write_text(json.dumps({"introduction": intro, "tiers": tiers, "notes": notes},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    words = [w for t in tiers for w in t["words"]]
    print(f"{len(tiers)} tiers, {len(words)} words, {len(intro)} introduction paragraphs -> {out}")
    print("  lemma match:", dict(Counter(w["match"] for w in words)))
    print(f"  linked to a Souter entry: {sum(1 for w in words if w['souter_id'])}")
    print(f"  with an English derivative: {sum(1 for w in words if w['derivative'])}")
    print(f"  OCR agrees with transcription: {sum(w['ocr_agrees'] for w in words)} of {len(words)}")
    print(f"  marked uncertain by the transcriber: {sum(1 for w in words if w['uncertain'])}")
    for w in words:
        if w["match"] in ("none", "fuzzy"):
            print(f"    check p.{w['page']}: {w['greek']} -> {w['match']} {w['lemma']}")
    # Metzger counted from Thayer (1886); flag words whose SBLGNT count is far outside his tier.
    odd = []
    for t in tiers:
        for w in t["words"]:
            n = w["nt_count"]
            if w["lemma"] and (n < t["min"] * 0.6 or (t["max"] and n > t["max"] * 1.6)):
                odd.append((t["heading"], w["greek"], n))
    print(f"  words whose SBLGNT count is far outside Metzger's tier: {len(odd)}")
    for h, g, n in odd[:40]:
        print(f"    {g}: SBLGNT {n}, Metzger tier '{h}'")

    lemmas_1946 = {w["lemma"] for w in words if w["lemma"]}
    if len(sys.argv) > 1:
        later = []
        for line in pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.lower().startswith(("words occurring", "bruce")):
                continue
            later.append(nfc(line.split(",")[0].strip()))
        later_lemmas = {}
        for h in later:
            later_lemmas.setdefault(M.match(h)[1] or h, h)
        only_later = [h for l, h in later_lemmas.items() if l not in lemmas_1946]
        only_1946 = [w["greek"] for w in words if w["lemma"] and w["lemma"] not in later_lemmas]
        print(f"\nComparison with later-edition list ({len(later)} headwords):")
        print(f"  in both: {len(lemmas_1946 & set(later_lemmas))}")
        print(f"  only in the later edition ({len(only_later)}): {', '.join(only_later)}")
        print(f"  only in 1946 ({len(only_1946)}): {', '.join(only_1946)}")


if __name__ == "__main__":
    main()
