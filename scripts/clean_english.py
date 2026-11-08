"""Correct systematic OCR errors in the English of Souter's entries.

Usage: python scripts/clean_english.py

Reads data/souter/entries.jsonl, adds a "text_clean" field to each entry, and writes
data/souter/entries.clean.jsonl. The raw "text" is kept unchanged for comparison.
Every change is listed in data/souter/english_fixes.tsv (entry id, old, new) for review.

Rules, in order:
1. The italic first-person "I" that Tesseract reads as 7, J, 1, £, Z, or / before a
   lowercase word at the start of a gloss ("7 seek" -> "I seek").
2. A fixed list of frequent misreadings in Souter's italic: fo/lo -> to, lhe/ihe -> the, ...
3. For any other word that is not English (by word frequency), try single-character
   swaps from Tesseract's known confusions in this typeface (l/t, f/t, !/t, i/t, r/i, s/i,
   c/e, o/c, Z/T, ...) and accept a swap only if it gives a common English word.
Words inside parentheses are left alone: Souter puts Latin equivalents there
("(quaero)", "(carnalis)"), which must not be turned into English.
"""

import json
import pathlib
import re

from wordfreq import zipf_frequency

ROOT = pathlib.Path(__file__).resolve().parent.parent

# A lone 7, J, £, Z, /, 77 before a lowercase word is always the italic "I". A lone 1 is "I"
# only when the next word is not one that follows a numeral in references ("1 and 2").
I_PATTERN = re.compile(r"(?<![\w.])(7\)?|77|71|J|£|Z|/|1)\s+(?=([a-z][a-z'-]*))")
NOT_AFTER_ONE = {"and", "or", "the", "of", "in", "to", "f", "ff", "times"}

FIXED = {
    "fo": "to", "lo": "to", "70": "to", "79": "to", "lhe": "the", "ihe": "the", "tke": "the",
    "Zhe": "The", "thal": "that", "oul": "out", "pul": "put", "wnto": "unto", "wilh": "with", "withou!": "without", "sce": "see",
    "@": "a",
}
# Greek-looking misreadings of italic English; applied only when the next word is English,
# since τῷ, ἐς, ἅ and the rest are also real Greek words that Souter cites.
GREEK_LOOKALIKES = {"ἃ": "a", "α": "a", "τῷ": "is", "ἐς": "is", "ἦε": "be", "ἠὲ": "in", "ἧς": "his"}

CONFUSIONS = {
    "l": "t", "f": "t", "!": "t", "i": "t", "r": "i", "s": "i", "c": "e", "e": "c", "o": "c",
    "Z": "T", "J": "I", "u": "n", "n": "u", "m": "in", "t": "l", "h": "b", "d": "cl",
}


def english(w: str) -> float:
    return zipf_frequency(w.lower(), "en")


def fix_word(w: str) -> str:
    core = re.match(r"^([^\w@!]*)([\w@!']+?)([^\w@!']*)$", w)
    if not core:
        return w
    pre, body, post = core.groups()
    if body in FIXED:
        return pre + FIXED[body] + post
    if not re.fullmatch(r"[A-Za-z!]+", body) or len(body) < 3 or english(body) >= 1.5:
        return w
    best, best_score = body, 0.0
    if body.endswith("iy") and english(body[:-2] + "ly") >= 2.5:  # purposelessiy -> purposelessly
        return pre + body[:-2] + "ly" + post
    for i, ch in enumerate(body):
        if ch in CONFUSIONS:
            cand = body[:i] + CONFUSIONS[ch] + body[i + 1:]
            score = english(cand)
            if score > best_score:
                best, best_score = cand, score
    # Two confusions in one word ("unieltered" -> "unlettered" needs more; leave those).
    return pre + (best if best_score >= 3.0 else body) + post


def clean(text: str) -> tuple[str, list[tuple[str, str]]]:
    changes: list[tuple[str, str]] = []
    text = I_PATTERN.sub(
        lambda m: m.group(0) if m.group(1) == "1" and m.group(2) in NOT_AFTER_ONE else "I ", text)
    out, depth = [], 0
    toks = text.split(" ")
    for k, tok in enumerate(toks):
        before = depth
        depth += tok.count("(") - tok.count(")")
        if before > 0 or tok.startswith("("):
            out.append(tok)
            continue
        nxt = toks[k + 1] if k + 1 < len(toks) else ""
        if tok in GREEK_LOOKALIKES and re.match(r"[a-z]{2,}", nxt) and english(nxt.strip(",.;:")) >= 3:
            new = GREEK_LOOKALIKES[tok]
        else:
            new = fix_word(tok)
        if new != tok:
            changes.append((tok, new))
        out.append(new)
    return " ".join(out), changes


def unknown_rate(texts: list[str]) -> float:
    words = [w for t in texts for w in re.findall(r"\b[A-Za-z]{3,}\b", re.sub(r"\([^)]*\)", " ", t))]
    bad = sum(english(w) < 1.0 for w in words)
    return bad / len(words) if words else 0.0


def main() -> None:
    src = ROOT / "data/souter/entries.jsonl"
    entries = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines()]
    log = []
    for e in entries:
        e["text_clean"], ch = clean(e["text"])
        log += [(e["id"], a, b) for a, b in ch]
    (ROOT / "data/souter/entries.clean.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries), encoding="utf-8")
    (ROOT / "data/souter/english_fixes.tsv").write_text(
        "id\told\tnew\n" + "".join(f"{i}\t{a}\t{b}\n" for i, a, b in log), encoding="utf-8")
    raw = unknown_rate([e["text"] for e in entries])
    new = unknown_rate([e["text_clean"] for e in entries])
    n_i = sum(len(re.findall(r"(?:^|[,;:)]\s+)I\s+[a-z]", e["text_clean"])) for e in entries)
    print(f"{len(log)} word fixes plus I-restorations ({n_i} 'I + verb' glosses now read correctly)")
    print(f"non-English words outside parentheses: {raw:.1%} before, {new:.1%} after")


if __name__ == "__main__":
    main()
