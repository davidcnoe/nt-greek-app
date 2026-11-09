"""Build app/assets/data/readings.json from Nunn's Appendix II readings.

Usage: python scripts/build_app_readings.py   (after build_nunn_readings.py and build_app_data.py)

Each paragraph becomes a list of pieces:
  "text"              punctuation and spaces
  ["surface", key]    a Greek word; key is the app card (Metzger form) for its lemma,
                      "~lemma" for a lemma the app does not teach, or "" if no lemma is
                      known; a leading "?" marks a lemma guessed from shared NT stems
Lemmas come from the form in the NT (SBLGNT), else from Celano's Morpheus-lemmatized
corpus (data/readings/form_lemmas.tsv) when that lemma is an NT lemma, else a guess: the single NT lemma whose forms
share the longest prefix (at least 5 letters, all but 4 at most) with the word.
Paragraphs split by a page break in mid-sentence are joined.
  {"n": "note-id"}    one of Nunn's footnote markers
Readings are ordered by the share of their words the app teaches (easiest first).
"""

import bisect
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "readings" / "nunn-appendix-ii" / "readings.json"
APP = ROOT / "app" / "assets" / "data"
MORPHGNT = pathlib.Path("/home/claude/morphgnt")
# Kept in data/readings but left out of the app at David's request (apocryphal).
EXCLUDE = {"gospel-of-peter"}
TOKEN = re.compile(r"(\[\^[^\]]+\])|([Ͱ-Ͽἀ-῿]+(?:['’᾽](?![Ͱ-Ͽἀ-῿]))?)")


def bare(word: str) -> str:
    word = unicodedata.normalize("NFD", word.lower())
    word = "".join(c for c in word if not unicodedata.combining(c))
    return word.replace("ς", "σ").strip("'’᾽")


def main() -> None:
    form_lemma = {}
    for f in sorted(MORPHGNT.glob("*-morphgnt.txt")):
        for line in f.read_text(encoding="utf-8").splitlines():
            c = line.split()
            form_lemma.setdefault(bare(c[5]), unicodedata.normalize("NFC", c[6]))
    celano = {}
    for line in (ROOT / "data" / "readings" / "form_lemmas.tsv").read_text(encoding="utf-8").splitlines():
        form, lemma, _ = line.split("\t")
        celano[form] = lemma
    forms = sorted(form_lemma)

    def guess(b: str):
        for n in range(len(b) - 1, max(4, len(b) - 4) - 1, -1):
            i, found = bisect.bisect_left(forms, b[:n]), set()
            while i < len(forms) and forms[i].startswith(b[:n]):
                found.add(form_lemma[forms[i]])
                i += 1
            if found:
                return found.pop() if len(found) == 1 else None
        return None

    words = json.loads((APP / "lexicon.json").read_text(encoding="utf-8"))["words"]
    lemma_key = {}
    for key, w in words.items():
        lemma_key.setdefault(w["l"], key)
        lemma_key.setdefault(bare(w["l"]), key)
        lemma_key.setdefault(bare(key), key)
    nt_lemmas = set(form_lemma.values())

    def key_for(surface: str) -> str:
        b = bare(surface)
        lemma, mark = form_lemma.get(b) or celano.get(b), ""
        if not lemma or lemma not in nt_lemmas:  # Morpheus lemmas outside the NT: try NT stems
            g = guess(b)
            if g:
                lemma, mark = g, "?"
        if not lemma:
            return ""
        key = lemma_key.get(lemma) or lemma_key.get(bare(lemma))
        return mark + (key if key else f"~{lemma}")

    out = []
    for sec in json.loads(SRC.read_text(encoding="utf-8")):
        if sec["slug"] == "preface" or sec["slug"] in EXCLUDE:
            continue
        paras, toks, taught = [], 0, 0
        for p in sec["paras"]:
            if "subheading" in p:
                paras.append({"h": p["subheading"]})
                continue
            pieces, pos = [], 0
            for m in TOKEN.finditer(p["text"]):
                if m.start() > pos:
                    pieces.append(p["text"][pos:m.start()])
                if m.group(1):
                    pieces.append({"n": m.group(1)[2:-1]})
                else:
                    surface = m.group(2)
                    key = key_for(surface)
                    pieces.append([surface, key])
                    toks += 1
                    taught += key.lstrip("?") in words
                pos = m.end()
            if pos < len(p["text"]):
                pieces.append(p["text"][pos:])
            # tidy: drop the space Nunn's marker leaves before a word
            tidy = []
            for x in pieces:
                if isinstance(x, str) and tidy and isinstance(tidy[-1], dict):
                    x = x.lstrip() if x.strip() else ""
                    if not x:
                        continue
                tidy.append(x)
            prev = paras[-1] if paras and "p" in paras[-1] else None
            last = next((x for x in reversed(prev["p"]) if isinstance(x, (str, list))), None) if prev else None
            ends = (last if isinstance(last, str) else last[0] if last else "").rstrip()
            if prev and p["page"] != prev["pg"] and ends and ends[-1] not in ".;·:!?»\"”":
                prev["p"] += [" "] + tidy
            else:
                paras.append({"p": tidy, "pg": p["page"]})
        out.append({
            "slug": sec["slug"], "title": sec["title"], "author": sec["author"], "date": sec["date"],
            "heading": sec["heading"], "intro": sec["intro"], "pages": [sec["pages"][0], sec["pages"][-1]],
            "words": toks, "taught": round(taught / toks, 3),
            "paras": paras,
            "notes": {o["id"]: o["text"] for o in sec["notes"]},
        })
    out.sort(key=lambda r: -r["taught"])
    (APP / "readings.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for r in out:
        print(r["slug"], r["words"], r["taught"])


if __name__ == "__main__":
    main()
