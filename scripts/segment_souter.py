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


ALIAS: dict[str, str] = {}  # alternative spelling -> SBLGNT lemma


def load_lemmas() -> tuple[dict[str, int], dict[str, list[str]]]:
    exact: dict[str, int] = {}
    loose: dict[str, list[str]] = {}
    for line in (ROOT / "data/nt/lemmas.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        lemma, _pos, count, _rank = line.split("\t")
        exact[lemma] = int(count)
        loose.setdefault(strip_accents(lemma), []).append(lemma)
    # SBLGNT marks optional final letters: οὕτω(ς), ἔξεστι(ν). Let either spelling match.
    for lemma in [l for l in exact if "(" in l]:
        for form in (re.sub(r"\((\w+)\)", r"\1", lemma), re.sub(r"\(\w+\)", "", lemma)):
            ALIAS[form] = lemma
            loose.setdefault(strip_accents(form), []).append(lemma)
    return exact, loose


def tsv_lines(page: int) -> list[tuple[int, str]]:
    """(left edge in px, text) for each OCR line on a page, from Tesseract's TSV output."""
    import csv
    path = ROOT / f"data/souter/tsv/page-{page:03d}.tsv"
    lines: dict[tuple[str, str, str], list[dict]] = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["level"] == "5" and r["text"].strip():
                lines.setdefault((r["block_num"], r["par_num"], r["line_num"]), []).append(r)
    out = []
    for ws in lines.values():
        ws.sort(key=lambda w: int(w["left"]))
        out.append((int(ws[0]["left"]), int(ws[0]["top"]), " ".join(w["text"] for w in ws)))
    out.sort(key=lambda x: x[1])
    return out


def flush_edge(lines: list[tuple[int, int, str]]) -> tuple[float, float]:
    """Fit the page's flush-left edge as left = a*top + b (the scan is slightly skewed).

    Start from a line through all lines, then repeatedly refit through the lines at or left of it,
    which converges on the leftmost (entry-start) lines; drop lone strays far left of the rest.
    """
    pts = [(top, left) for left, top, _ in lines]
    if len(pts) < 3:
        m = min(l for _, l in pts) if pts else 0
        return 0.0, float(m)

    def fit(ps):
        n = len(ps)
        mx = sum(x for x, _ in ps) / n
        my = sum(y for _, y in ps) / n
        sxx = sum((x - mx) ** 2 for x, _ in ps)
        a = sum((x - mx) * (y - my) for x, y in ps) / sxx if sxx else 0.0
        return a, my - a * mx

    a, b = fit(pts)
    for _ in range(6):
        below = [(x, y) for x, y in pts if y - (a * x + b) <= 5]
        if len(below) < 3:
            break
        a, b = fit(below)
    # Ignore strays more than 30 px left of the fitted edge, then refit once.
    core = [(x, y) for x, y in pts if -30 <= y - (a * x + b) <= 10]
    if len(core) >= 3:
        a, b = fit(core)
    return a, b


def blocks(page: int) -> list[str]:
    """Entry blocks on one page, split at hanging indents; running head and page number removed.

    Entry lines start flush left; continuation lines are indented about 40 px at 300 dpi.
    The scan is slightly skewed, so each line is compared with the leftmost line near it.
    """
    lines = tsv_lines(page)
    if lines:
        lines = lines[1:]  # running head (guide word)
    # Drop page numbers and specks: very short lines with no Greek or Latin word in them.
    lines = [(l, top, t) for l, top, t in lines
             if not (len(t.strip()) <= 4 and not re.search(r"[Ͱ-Ͽἀ-῿]{2}|[A-Za-z]{3}", t))]
    a, b = flush_edge(lines)
    out: list[tuple[bool, str]] = []
    for left, top, text in lines:
        flush = left - (a * top + b) < 20
        if flush or not out:
            out.append((flush, text.strip()))
        else:
            f, prev = out[-1]
            out[-1] = (f, prev[:-1] + text.strip() if prev.endswith("-") else prev + " " + text.strip())
    return out


def blocks_from_text(page: int) -> list[str]:
    """Older splitter on blank lines in the plain-text OCR; kept for comparison."""
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
        c = ALIAS.get(c, c)
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


def sort_key(s: str) -> str:
    return strip_accents(s).replace("̓", "").replace("̔", "")


def recover_by_position(entries: list[dict], exact: dict[str, int]) -> None:
    """Assign unmatched entries a lemma from their alphabetical slot.

    Souter is alphabetical. For an unmatched entry, take the nearest matched entries before
    and after it; if exactly one unused NT lemma sorts between them (and there is exactly one
    unmatched entry in the gap), that lemma is almost certainly the entry's headword.
    Marked match="position" so a reviewer checks it.
    """
    used = {e["lemma"] for e in entries if e["lemma"]}
    ordered = sorted(exact, key=sort_key)
    keys = [sort_key(l) for l in ordered]
    import bisect
    i = 0
    while i < len(entries):
        if entries[i]["lemma"] or entries[i]["xref"]:
            i += 1
            continue
        j = i
        while j < len(entries) and not entries[j]["lemma"]:
            j += 1
        gap = entries[i:j]
        k = i - 1
        while k >= 0 and not entries[k]["lemma"]:
            k -= 1
        lo = sort_key(entries[k]["lemma"]) if k >= 0 else ""
        hi = sort_key(entries[j]["lemma"]) if j < len(entries) else "￿"
        if lo < hi:
            a, b = bisect.bisect_right(keys, lo), bisect.bisect_left(keys, hi)
            cands = [l for l in ordered[a:b] if l not in used]
            open_slots = [e for e in gap if not e["xref"]]
            if len(cands) == 1 and len(open_slots) == 1:
                e = open_slots[0]
                e.update(match="position", lemma=cands[0], nt_count=exact[cands[0]])
                used.add(cands[0])
        i = j


def main() -> None:
    exact, loose = load_lemmas()
    by_first: dict[str, list[str]] = {}
    for l in exact:
        by_first.setdefault(strip_accents(l)[:1], []).append(l)
    entries: list[dict] = []
    for page in range(FIRST_PAGE, LAST_PAGE + 1):
        for flush, b in blocks(page):
            if not flush and entries:
                # Indented first line of a page: the previous page's last entry continues.
                entries[-1]["text"] += " " + b
                continue
            m = HEAD.match(b)
            head = clean_head(m.group(1)) if m else ""
            entries.append({"id": len(entries) + 1, "headword": head, "page": page, "text": b})
    # Drop a page's running head when it survived as an entry: a bare headword repeated next.
    entries = [e for i, e in enumerate(entries)
               if not (i + 1 < len(entries) and e["text"].strip() == e["headword"]
                       and entries[i + 1]["headword"] == e["headword"])]
    for i, e in enumerate(entries, 1):
        e["id"] = i
    stats: dict[str, int] = {}
    for e in entries:
        kind, lemma = match(e["headword"], exact, loose, by_first) if e["headword"] else ("none", None)
        e.update(match=kind, lemma=lemma, nt_count=exact.get(lemma, 0) if lemma else 0)
        e["xref"] = bool(re.match(r"^[^,]*,\s*(another spelling of|see)\b", e["text"]))
    recover_by_position(entries, exact)
    for e in entries:
        stats[e["match"]] = stats.get(e["match"], 0) + 1
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
