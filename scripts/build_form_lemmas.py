"""Build a form -> lemma table from G. Celano's lemmatized Greek corpus (Morpheus analyses).

Usage: python scripts/build_form_lemmas.py CELANO_TEXTS_DIR

Used only as a fallback for forms that do not occur in the NT, so that a reading's
βαπτίσατε still finds βαπτίζω. Only lemmas Morpheus gave for the tagged part of speech
(<l1>) are used; for each accentless form the commonest lemma wins.
Writes data/readings/form_lemmas.tsv (form, lemma, count).
Source: https://github.com/gcelano/LemmatizedAncientGreekXML (CC BY-SA 4.0).
"""

import collections
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = re.compile(r"<f>([^<]+)</f>\s*<l[^>]*>\s*<l1[^>]*>([^<]+)</l1>")


def bare(word: str) -> str:
    word = unicodedata.normalize("NFD", word.lower())
    word = "".join(c for c in word if not unicodedata.combining(c))
    return word.replace("ς", "σ").strip("'’᾽")


def main(src: str) -> None:
    table: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for f in sorted(pathlib.Path(src).glob("*.xml")):
        for form, lemma in TOK.findall(f.read_text(encoding="utf-8")):
            lemma = re.sub(r"\d+$", "", unicodedata.normalize("NFC", lemma.strip()))
            table[bare(form)][lemma] += 1
    out = ROOT / "data" / "readings" / "form_lemmas.tsv"
    with out.open("w", encoding="utf-8") as fh:
        for form in sorted(table):
            lemma, n = table[form].most_common(1)[0]
            fh.write(f"{form}\t{lemma}\t{n}\n")
    print(len(table), "forms")


if __name__ == "__main__":
    main(sys.argv[1])
