"""Match Metzger's headwords to SBLGNT lemmas and Souter entries (shared by Part I and Part II).

Order of attempts for a headword:
1. data/metzger/lemma_overrides.tsv (reviewed by hand: principal parts, comparatives, spellings);
2. the word as typed, then its spelling variants: the other half of "X and Y", unassimilated
   prefixes (συνκαλέω -> συγκαλέω, ἐνκόπτω -> ἐγκόπτω), middle <-> active (-ομαι/-ω, -εμαι/-αμαι/-ημι);
3. ignoring accents and breathings;
4. one letter off a single lemma ("fuzzy"; reviewed).
"""

import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from segment_souter import ALIAS, lev1, load_lemmas, strip_accents  # noqa: E402

PREFIX_BEFORE = ("ἀπο", "ἐπι", "κατ", "ἐξ", "δι", "προ", "ἀντι", "παρα", "ὑπο")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


class Matcher:
    def __init__(self) -> None:
        self.exact, self.loose = load_lemmas()
        self.by_first: dict[str, list[str]] = {}
        for l in self.exact:
            self.by_first.setdefault(strip_accents(l)[:1], []).append(l)
        self.overrides: dict[str, str] = {}
        for line in (ROOT / "data/metzger/lemma_overrides.tsv").read_text(encoding="utf-8").splitlines()[1:]:
            m, lemma, _why = line.split("\t")
            self.overrides[nfc(m)] = lemma
        self.souter: dict[str, dict] = {}
        for line in (ROOT / "data/souter/entries.clean.jsonl").read_text(encoding="utf-8").splitlines():
            e = json.loads(line)
            if e["lemma"] and e["lemma"] not in self.souter:
                self.souter[e["lemma"]] = e

    @staticmethod
    def variants(word: str) -> list[str]:
        w = re.sub(r"\s*\([^)]*\)", "", nfc(word))  # ἑκατοντάρχης (or -αρχος)
        out = [p.strip() for p in re.split(r"\s+(?:and|or)\s+|,\s*", w) if p.strip()]
        more = []
        for v in out:
            for pre, opts in (("συν", ("συγ", "συλ", "συμ", "συσ", "συ")), ("ἐν", ("ἐγ", "ἐμ", "ἐλ"))):
                i = v.find(pre)
                if i == 0 or (i > 0 and v[:i] in PREFIX_BEFORE):
                    more += [v[:i] + o + v[i + len(pre):] for o in opts]
            for a, b in (("ομαι", "ω"), ("εμαι", "ημι"), ("αμαι", "ημι"), ("ημι", "αμαι"), ("ημι", "εμαι")):
                if v.endswith(a):
                    more.append(v[: -len(a)] + b)
            if v.endswith("ω") and not v.endswith("ομαι"):
                more.append(v[:-1] + "ομαι")
        return out + [nfc(m) for m in more]

    def match_one(self, word: str) -> tuple[str, str | None]:
        w = ALIAS.get(nfc(word), nfc(word))
        if w in self.exact:
            return "exact", w
        k = strip_accents(w)
        if k in self.loose:
            return "accent", max(self.loose[k], key=lambda x: self.exact[x])
        return "none", None

    def fuzzy(self, word: str) -> tuple[str, str | None]:
        k = strip_accents(nfc(word))
        near = [l for l in self.by_first.get(k[:1], []) if lev1(k, strip_accents(l))]
        return ("fuzzy", near[0]) if len(near) == 1 else ("none", None)

    def match(self, word: str) -> tuple[str, str | None]:
        w0 = nfc(word)
        if w0 in self.overrides:
            return "override", self.overrides[w0]
        for i, v in enumerate(self.variants(w0)):
            how, lemma = self.match_one(v)
            if how != "none":
                return (how if i == 0 else "variant"), lemma
        w0 = re.sub(r"\s*\([^)]*\)", "", w0)
        return self.fuzzy(re.split(r"\s+(?:and|or)\s+|,\s*", w0)[0])

    def link(self, word: str) -> dict:
        how, lemma = self.match(word)
        sid = self.souter[lemma]["id"] if lemma in self.souter else None
        if sid is None:  # Souter may enter the word under Metzger's form (χρύσεος, not χρυσοῦς)
            for v in self.variants(word):
                alt = self.match_one(v)[1]
                if alt in self.souter:
                    sid = self.souter[alt]["id"]
                    break
        return {"lemma": lemma, "match": how, "nt_count": self.exact.get(lemma, 0) if lemma else 0,
                "souter_id": sid}
