"""Build prototype/data/accents.json: diacriticals (accents and breathings) that change meaning in the NT.

Usage: python scripts/build_accents.py [MORPHGNT_DIR]   (default /home/claude/morphgnt)

Each set lists words spelled alike but for accent or breathing. Every member is identified in
MorphGNT (SBLGNT) by its normalized form plus lemma or part of speech, so the example verses are
real occurrences of that word, not of its look-alike. For each member: its NT count and up to
40 example verses (shortest first), with the token's position so the app can highlight it.
"""

import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/morphgnt")
BOOKS = ["Matt", "Mark", "Luke", "John", "Acts", "Rom", "1 Cor", "2 Cor", "Gal", "Eph", "Phil", "Col",
         "1 Thess", "2 Thess", "1 Tim", "2 Tim", "Titus", "Phlm", "Heb", "Jas", "1 Pet", "2 Pet",
         "1 John", "2 John", "3 John", "Jude", "Rev"]

N = lambda s: unicodedata.normalize("NFC", s)
# SBLGNT's text-critical signs (⸀ ⸂ ⸃ ⸄ ⸅ …) are left out of the verses shown.
CRIT = dict.fromkeys(range(0x2E00, 0x2E10))

# MorphGNT's normalized forms write the indefinite enclitics with a grave (τὶς, τὶ) and the
# enclitic πως under the lemma πώς.
# Each member: id, Greek as cited, meaning shown in the quiz, and a test on a MorphGNT token
# (ref, pos, parse, text, word, norm, lemma).
SETS = [
    {"id": "ei", "title": "εἰ and εἶ", "note": "εἰ is a proclitic and has no accent of its own; εἶ, from εἰμί, has a circumflex.",
     "members": [
         {"g": "εἰ", "m": "if", "t": lambda t: t["norm"] == N("εἰ") and t["lemma"] == N("εἰ")},
         {"g": "εἶ", "m": "you are", "t": lambda t: t["norm"] == N("εἶ") and t["lemma"] == N("εἰμί")},
     ]},
    {"id": "e", "title": "ἡ, ἥ, and ἤ", "note": "The article ἡ is a proclitic, with no accent; the relative ἥ has a rough breathing and an accent; the conjunction ἤ has a smooth breathing.",
     "members": [
         {"g": "ἡ", "m": "the (feminine)", "t": lambda t: t["norm"] == N("ἡ") and t["pos"] == "RA"},
         {"g": "ἥ", "m": "who, which (feminine)", "t": lambda t: t["norm"] == N("ἥ") and t["pos"] == "RR"},
         {"g": "ἤ", "m": "or, than", "t": lambda t: t["norm"] == N("ἤ") and t["pos"] == "C-"},
     ]},
    {"id": "o", "title": "ὁ and ὅ", "note": "The article ὁ has no accent; the relative ὅ (neuter) has one.",
     "members": [
         {"g": "ὁ", "m": "the (masculine)", "t": lambda t: t["norm"] == N("ὁ") and t["pos"] == "RA"},
         {"g": "ὅ", "m": "which, what (neuter)", "t": lambda t: t["norm"] == N("ὅ") and t["pos"] == "RR"},
     ]},
    {"id": "ou", "title": "οὐ and οὗ", "note": "οὐ, not, has a smooth breathing and no accent; οὗ, of whom or where, has a rough breathing and a circumflex.",
     "members": [
         {"g": "οὐ", "m": "not", "t": lambda t: t["norm"] == N("οὐ") and t["lemma"] == N("οὐ")},
         {"g": "οὗ", "m": "of whom, of which; where", "t": lambda t: t["norm"] == N("οὗ")},
     ]},
    {"id": "en", "title": "ἐν and ἕν", "note": "The preposition ἐν is a proclitic with a smooth breathing; ἕν, one, has a rough breathing and an accent.",
     "members": [
         {"g": "ἐν", "m": "in", "t": lambda t: t["norm"] == N("ἐν") and t["pos"] == "P-"},
         {"g": "ἕν", "m": "one (neuter)", "t": lambda t: t["norm"] == N("ἕν") and t["lemma"] == N("εἷς")},
     ]},
    {"id": "eis", "title": "εἰς and εἷς", "note": "The preposition εἰς is a proclitic with a smooth breathing; εἷς, one, has a rough breathing and a circumflex.",
     "members": [
         {"g": "εἰς", "m": "into, to", "t": lambda t: t["norm"] == N("εἰς") and t["pos"] == "P-"},
         {"g": "εἷς", "m": "one (masculine)", "t": lambda t: t["norm"] == N("εἷς")},
     ]},
    {"id": "en2", "title": "ἦν and ἥν", "note": "ἦν, from εἰμί, has a smooth breathing and a circumflex; ἥν, the relative, a rough breathing and an acute.",
     "members": [
         {"g": "ἦν", "m": "was", "t": lambda t: t["norm"] == N("ἦν") and t["lemma"] == N("εἰμί")},
         {"g": "ἥν", "m": "whom, which (feminine)", "t": lambda t: t["norm"] == N("ἥν") and t["pos"] == "RR"},
     ]},
    {"id": "on", "title": "ὤν and ὧν", "note": "ὤν, the participle of εἰμί, has a smooth breathing and an acute; ὧν, the relative, a rough breathing and a circumflex.",
     "members": [
         {"g": "ὤν", "m": "being", "t": lambda t: t["norm"] == N("ὤν") and t["lemma"] == N("εἰμί")},
         {"g": "ὧν", "m": "of whom, of which", "t": lambda t: t["norm"] == N("ὧν") and t["pos"] == "RR"},
     ]},
    {"id": "alla", "title": "ἀλλά and ἄλλα", "note": "The conjunction is accented on the last syllable; ἄλλα, other things, on the first.",
     "members": [
         {"g": "ἀλλά", "m": "but", "t": lambda t: t["norm"] == N("ἀλλά") and t["pos"] == "C-"},
         {"g": "ἄλλα", "m": "other things", "t": lambda t: t["norm"] == N("ἄλλα") and t["lemma"] == N("ἄλλος")},
     ]},
    {"id": "aute", "title": "αὐτή and αὕτη", "note": "αὐτή, from αὐτός, has a smooth breathing on the diphthong; αὕτη, this, a rough breathing.",
     "members": [
         {"g": "αὐτή", "m": "she; herself; the same", "t": lambda t: t["norm"] == N("αὐτή") and t["lemma"] == N("αὐτός")},
         {"g": "αὕτη", "m": "this (feminine)", "t": lambda t: t["norm"] == N("αὕτη") and t["lemma"] == N("οὗτος")},
     ]},
    {"id": "tis", "title": "τίς and τις", "note": "The interrogative always keeps its acute; the indefinite τις is an enclitic, often written without an accent.",
     "members": [
         {"g": "τίς", "m": "who?", "t": lambda t: t["norm"] == N("τίς") and t["lemma"] == N("τίς")},
         {"g": "τις", "m": "someone, anyone", "t": lambda t: t["lemma"] == N("τις") and t["norm"] == N("τὶς")},
     ]},
    {"id": "ti", "title": "τί and τι", "note": "The same pair in the neuter: τί asks; τι, enclitic, is indefinite.",
     "members": [
         {"g": "τί", "m": "what? why?", "t": lambda t: t["norm"] == N("τί") and t["lemma"] == N("τίς")},
         {"g": "τι", "m": "something, anything", "t": lambda t: t["lemma"] == N("τις") and t["norm"] == N("τὶ")},
     ]},
    {"id": "pos", "title": "πῶς and πως", "note": "πῶς asks; πως, enclitic, is indefinite.",
     "members": [
         {"g": "πῶς", "m": "how?", "t": lambda t: t["norm"] == N("πῶς")},
         {"g": "πως", "m": "somehow, perhaps", "t": lambda t: t["lemma"] == N("πώς")},
     ]},
    {"id": "pou", "title": "ποῦ and που", "note": "ποῦ asks; που, enclitic, is indefinite.",
     "members": [
         {"g": "ποῦ", "m": "where?", "t": lambda t: t["norm"] == N("ποῦ")},
         {"g": "που", "m": "somewhere; about", "t": lambda t: t["lemma"] == N("πού")},
     ]},
    {"id": "pote", "title": "πότε and ποτέ", "note": "πότε asks; ποτέ, enclitic, is indefinite.",
     "members": [
         {"g": "πότε", "m": "when?", "t": lambda t: t["lemma"] == N("πότε")},
         {"g": "ποτέ", "m": "once, ever", "t": lambda t: t["lemma"] == N("ποτέ")},
     ]},
    {"id": "ara", "title": "ἄρα and ἆρα", "note": "ἄρα draws a conclusion; ἆρα, with a circumflex, asks a question.",
     "members": [
         {"g": "ἄρα", "m": "then, therefore", "t": lambda t: t["lemma"] == N("ἄρα")},
         {"g": "ἆρα", "m": "(asks a question)", "t": lambda t: t["lemma"] == N("ἆρα")},
     ]},
    {"id": "krino", "title": "κρίνει and κρινεῖ", "note": "Liquid verbs form the future with a contraction, so present and future differ only in the accent: κρίνει, he judges; κρινεῖ, he will judge.",
     "members": [
         {"g": "κρίνει", "m": "judges (present)", "t": lambda t: t["norm"] == N("κρίνει") and t["lemma"] == N("κρίνω")},
         {"g": "κρινεῖ", "m": "will judge (future)", "t": lambda t: t["norm"] == N("κρινεῖ") and t["lemma"] == N("κρίνω")},
     ]},
    {"id": "meno", "title": "μένει and μενεῖ", "note": "Another liquid verb: μένει, remains; μενεῖ, will remain.",
     "members": [
         {"g": "μένει", "m": "remains (present)", "t": lambda t: t["norm"] == N("μένει") and t["lemma"] == N("μένω")},
         {"g": "μενεῖ", "m": "will remain (future)", "t": lambda t: t["norm"] == N("μενεῖ") and t["lemma"] == N("μένω")},
     ]},
]


def main() -> None:
    verses, tokens = {}, []
    for f in sorted(SRC.glob("*-morphgnt.txt")):
        for line in f.read_text(encoding="utf-8").splitlines():
            ref, pos, parse, text, word, norm, lemma = line.split()
            t = {"ref": ref, "pos": pos, "parse": parse, "text": N(text), "word": N(word), "norm": N(norm), "lemma": N(lemma)}
            v = verses.setdefault(ref, [])
            t["i"] = len(v)
            v.append(t["text"].translate(CRIT))
            tokens.append(t)

    def cite(ref: str) -> str:
        b, c, v = int(ref[:2]), int(ref[2:4]), int(ref[4:])
        return f"{BOOKS[b - 1]} {c}:{v}"

    out = []
    for s in SETS:
        members = []
        for m in s["members"]:
            hits = [t for t in tokens if m["t"](t)]
            seen, ex = set(), []
            for t in sorted(hits, key=lambda t: (len(verses[t["ref"]]), t["ref"])):
                if t["ref"] in seen or len(verses[t["ref"]]) > 24:
                    continue
                seen.add(t["ref"])
                ex.append({"ref": cite(t["ref"]), "w": verses[t["ref"]], "i": t["i"]})
                if len(ex) == 40:
                    break
            members.append({"g": m["g"], "m": m["m"], "count": len(hits), "ex": ex})
            print(f"{s['id']:6} {m['g']:8} {len(hits):6} occurrences, {len(ex)} examples")
        out.append({"id": s["id"], "title": s["title"], "note": s["note"], "members": members})
    dest = ROOT / "prototype" / "data" / "accents.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(dest, dest.stat().st_size)


if __name__ == "__main__":
    main()
