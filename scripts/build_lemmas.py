"""Build the NT lemma frequency list from MorphGNT (SBLGNT).

Usage: python scripts/build_lemmas.py MORPHGNT_DIR

MORPHGNT_DIR holds the 27 files NN-Bk-morphgnt.txt from
https://github.com/morphgnt/sblgnt. Each line is:
bcv  part-of-speech  parse-code  text  word  normalized  lemma

Writes data/nt/lemmas.tsv: lemma, part(s) of speech, NT count, rank.
"""

import collections
import pathlib
import sys
import unicodedata

POS = {
    "A-": "adjective", "C-": "conjunction", "D-": "adverb", "I-": "interjection",
    "N-": "noun", "P-": "preposition", "RA": "article", "RD": "demonstrative",
    "RI": "interrogative/indefinite", "RP": "personal pronoun", "RR": "relative pronoun",
    "V-": "verb", "X-": "particle",
}


def main(src: str) -> None:
    counts: collections.Counter[str] = collections.Counter()
    pos: dict[str, set[str]] = collections.defaultdict(set)
    files = sorted(pathlib.Path(src).glob("*-morphgnt.txt"))
    if len(files) != 27:
        sys.exit(f"expected 27 MorphGNT files in {src}, found {len(files)}")
    for f in files:
        for line in f.read_text(encoding="utf-8").splitlines():
            cols = line.split()
            lemma = unicodedata.normalize("NFC", cols[6])
            counts[lemma] += 1
            pos[lemma].add(POS.get(cols[1], cols[1]))
    out = pathlib.Path(__file__).resolve().parent.parent / "data" / "nt" / "lemmas.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    with out.open("w", encoding="utf-8") as fh:
        fh.write("lemma\tpos\tcount\trank\n")
        for rank, (lemma, n) in enumerate(rows, 1):
            fh.write(f"{lemma}\t{'/'.join(sorted(pos[lemma]))}\t{n}\t{rank}\n")
    total = sum(counts.values())
    print(f"{len(rows)} lemmas, {total} tokens -> {out}")
    for floor in (50, 25, 10):
        k = sum(1 for _, n in rows if n >= floor)
        cov = sum(n for _, n in rows if n >= floor) / total
        print(f"  {k} lemmas at {floor}+ occurrences cover {cov:.1%} of tokens")


if __name__ == "__main__":
    main(sys.argv[1])
