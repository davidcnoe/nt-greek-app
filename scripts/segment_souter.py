"""Split the raw Souter OCR into entries and check headwords against the NT lemma list.

Usage: python scripts/segment_souter.py

Reads data/souter/ocr/page-008.txt .. page-297.txt and data/nt/lemmas.tsv.
Writes data/souter/entries.jsonl, one entry per line:
  id, headword (as OCR read it), page, text (the full entry, lines joined),
  match: "exact" | "accent" | "none", lemma (the MorphGNT lemma matched, if any),
  nt_count.
Prints a summary of match rates.
"""

import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIRST_PAGE, LAST_PAGE = 8, 297

GREEK = re.compile(r"[Ͱ-Ͽἀ-῿]")
# A headword: a run of Greek letters, combining marks and the koronis/psili signs,
# optionally preceded by a detached breathing (᾿ or ῾) the OCR separates out.
HEAD = re.compile(r"^\s*([᾿῾ʼ']?\s*[Ͱ-Ͽἀ-῿̀-ͯ]+)")


def strip_accents(s: str) -> str:
    d = unicodedata.normalize("NFD", s)
    d = "".join(c for c in d if unicodedata.category(c) != "Mn")
    return d.lower().replace("ς", "σ")


def clean_head(raw: str) -> str:
    s = raw.replace(" ", "")
    # Rejoin a detached breathing mark with the first vowel: ᾿Α -> Ἀ, ῾Α -> Ἁ.
    if s[:1] in "᾿ʼ'":
        s = unicodedata.normalize("NFC", s[1:2] + "̓" + s[2:])
    elif s[:1] == "῾":
        s = unicodedata.normalize("NFC", s[1:2] + "̔" + s[2:])
    return unicodedata.normalize("NFC", s)


def load_lemmas() -> tuple[dict[str, int], dict[str, list[str]]]:
    exact: dict[str, int] = {}
    loose: dict[str, list[str]] = {}
    for line in (ROOT / "data/nt/lemmas.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        lemma, _pos, count, _rank = line.split("\t")
        exact[lemma] = int(count)
        loose.setdefault(strip_accents(lemma), []).append(lemma)
    return exact, loose


def blocks(page: int) -> list[str]:
    """Paragraph blocks on one page, running head removed."""
    text = (ROOT / f"data/souter/ocr/page-{page:03d}.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    lines = lines[1:]  # running head (guide word)
    out, cur = [], []
    for ln in lines:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    # Join hyphenated line breaks; otherwise join with a space.
    joined = []
    for b in out:
        s = ""
        for ln in b:
            s = s[:-1] + ln if s.endswith("-") else (s + " " + ln if s else ln)
        joined.append(s)
    return joined


def starts_entry(block: str, exact: dict[str, int], loose: dict[str, list[str]]) -> bool:
    # Proper names whose Greek capitals Tesseract read as Latin: '"Abdel (Hebr.),' etc.
    if re.match(r'^\W{0,2}[A-Z][a-zA-Z]{1,15}\s*\((Hebr|Aram|Lat)', block):
        return True
    m = HEAD.match(block)
    if not m:
        return False
    head = clean_head(m.group(1))
    rest = block[m.end():m.end() + 3]
    # Headwords are followed by a comma, an opening parenthesis, or " (" ; prose is not.
    if rest[:1] in ",(" or rest.lstrip()[:1] in ",(":
        return True
    return head in exact or strip_accents(head) in loose


# Latin letters Tesseract returns for identical-looking Greek capitals.
LATIN_TO_GREEK = str.maketrans("ABEZHIKMNOPTYX", "ΑΒΕΖΗΙΚΜΝΟΡΤΥΧ")


def ocr_candidates(h: str) -> list[str]:
    """Plausible corrections for known Tesseract confusions in Souter's typeface."""
    base = unicodedata.normalize("NFC", h.replace("ϑ", "θ").translate(LATIN_TO_GREEK))
    cands = [base]
    if "ξ" in base:
        cands.append(base.replace("ξ", "ζ"))
        cands.append(base.replace("ξζ", "ζ").replace("ζξ", "ζ"))
    if base.endswith("υ"):
        cands.append(base[:-1] + "ι")
    if base[:1] == "δ":  # rough-breathing ὁ / ὑ misread as δ
        cands += ["ὁ" + base[1:], "ὑ" + base[1:], "ὀ" + base[1:]]
    if base[:1] == "ο":
        cands.append("α" + base[1:])
    return cands


def lev1(a: str, b: str) -> bool:
    """True if a and b differ by at most one insertion, deletion, or substitution."""
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    if len(a) > len(b):
        a, b = b, a
    return any(a == b[:i] + b[i + 1:] for i in range(len(b)))


def match(h: str, exact: dict[str, int], loose: dict[str, list[str]], by_first: dict[str, list[str]]):
    for i, c in enumerate(ocr_candidates(h)):
        if c in exact:
            return ("exact" if i == 0 and c == h else "ocr-fix"), c
    for c in ocr_candidates(h):
        if strip_accents(c) in loose:
            return "accent", max(loose[strip_accents(c)], key=lambda x: exact[x])
    key = strip_accents(ocr_candidates(h)[0])
    near = [l for l in by_first.get(key[:1], []) if lev1(key, strip_accents(l))]
    if len(near) == 1:
        return "fuzzy", near[0]
    return "none", None


def main() -> None:
    exact, loose = load_lemmas()
    by_first: dict[str, list[str]] = {}
    for l in exact:
        by_first.setdefault(strip_accents(l)[:1], []).append(l)
    entries: list[dict] = []
    for page in range(FIRST_PAGE, LAST_PAGE + 1):
        for b in blocks(page):
            if len(GREEK.findall(b[:40])) == 0 and entries and not starts_entry(b, exact, loose):
                entries[-1]["text"] += " " + b  # continuation from previous page/column
                continue
            if starts_entry(b, exact, loose) or not entries:
                head = clean_head(HEAD.match(b).group(1)) if HEAD.match(b) else ""
                entries.append({"id": len(entries) + 1, "headword": head, "page": page, "text": b})
            else:
                entries[-1]["text"] += " " + b
    stats: dict[str, int] = {}
    for e in entries:
        kind, lemma = match(e["headword"], exact, loose, by_first)
        e.update(match=kind, lemma=lemma, nt_count=exact.get(lemma, 0) if lemma else 0)
        e["xref"] = bool(re.match(r"^[^,]*,\s*(another spelling of|see)\b", e["text"]))
        stats[kind] = stats.get(kind, 0) + 1
    out = ROOT / "data/souter/entries.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    matched = {e["lemma"] for e in entries if e["lemma"]}
    print(f"{len(entries)} entries -> {out}")
    print(f"  headword matches: {stats}")
    print(f"  distinct NT lemmas covered: {len(matched)} of {len(exact)}")
    for floor in (10, 1):
        want = {l for l, n in exact.items() if n >= floor}
        print(f"  lemmas at {floor}+ found in Souter: {len(want & matched)} of {len(want)}")


if __name__ == "__main__":
    main()
