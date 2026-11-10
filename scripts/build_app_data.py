"""Write the compact data file the app loads: app/assets/data/lexicon.json.

Usage: python scripts/build_app_data.py

From data/app/lexicon.json and data/metzger/families.json. Output:
  {
    "meta": {"nt_tokens": total NT word count, "built": ..., "sources": [...]},
    "words": {Metzger form: {l: SBLGNT lemma, c: NT count of the lemma, r: rank, g: card gloss,
                      gr: grammar, d: derivative, t: Metzger tier, f: family id,
                      m: in Moss, mg: Moss meaning, s: Souter entry text}},
    "families": [{id, root, gloss, members: [lemma]}],
    "units": [{id, kind: "family"|"frequency", title, subtitle, family?, words: [lemma]}]
  }

Every card is a word Metzger lists (Part I or Part II), with his gloss: his Part I gloss where
the word is in Part I, else his Part II gloss. Nothing is invented.

Learning path ("units"): root-family units (a family's NT words in Metzger's order, split into
parts of at most 10) and frequency units (Part I words in no family, in Metzger's order, 12 per
unit), all ordered by their most frequent word so the commonest words come first.
"""

import json
import pathlib
import re
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent



# Moss's vocabulary cites the page of the Reader where a sense first occurs ("account, 147, mention, 144");
# those page numbers mean nothing in the app, so they are dropped.
def moss_clean(t: str) -> str:
    return re.sub(r",\s*\d{2,3}(?=\s*(?:[,.;]|$))", "", t).strip()

def souter_first(text: str) -> str:
    # First clause after the headword, without parenthetical etymology; short.
    t = re.sub(r"^[^,]*,\s*", "", text, count=1)
    t = re.sub(r"\([^)]*\)", "", t)
    t = re.split(r"[;:]|\. ", t)[0].strip(" ,.")
    return t[:80]


def tidy(s: str) -> str:
    """No space before , ; : . ! ? ) and none after (."""
    return re.sub(r"\(\s+", "(", re.sub(r"\s+([,;:.!?)])", r"\1", s))


def main() -> None:
    lex = json.loads((ROOT / "data/app/lexicon.json").read_text(encoding="utf-8"))
    fams = json.loads((ROOT / "data/metzger/families.json").read_text(encoding="utf-8"))
    nt_tokens = sum(int(l.split("\t")[2]) for l in
                    (ROOT / "data/nt/lemmas.tsv").read_text(encoding="utf-8").splitlines()[1:])

    by_lemma = {r["lemma"]: r for r in lex}
    # Souter as proofread against the page images (data/souter/proof/, 2026-11-09): replaces the OCR text,
    # including five links corrected by hand (οὐ, ὁ, ὦ, εὐθύς, μήν).
    proof = json.loads((ROOT / "data/souter/proofread.json").read_text(encoding="utf-8"))
    part1 = json.loads((ROOT / "data/metzger/part1.json").read_text(encoding="utf-8"))

    # Cards are keyed by Metzger's own form (ἐρῶ, εἶδον, ὄψομαι stay distinct from λέγω, ὁράω);
    # NT count, Souter, and Moss come from the SBLGNT lemma the form is linked to.
    words: dict[str, dict] = {}

    def add(form: str, lemma: str | None, gloss: str, grammar: str, deriv: str, tier: str,
            fam: int | None) -> None:
        if not lemma or lemma not in by_lemma:
            return
        # Metzger sometimes writes "cf." before his derivative; the app already prints "Cf.".
        deriv = re.sub(r"^\s*cf\.\s*", "", deriv or "", flags=re.I)
        r = by_lemma[lemma]
        w = words.get(form)
        if w is None:
            words[form] = w = {
                "l": lemma, "c": r["nt_count"], "r": r["nt_rank"], "g": gloss, "gs": "Metzger",
                "gr": grammar, "d": deriv, "t": tier, "f": fam,
                "m": bool(r["moss"]), "mg": moss_clean(r["moss"]["meaning"]) if r["moss"] else "",
                "s": proof[lemma]["text"] if lemma in proof else (r["souter"]["text"] if r["souter"] else ""),
            }
        else:
            w["gr"] = w["gr"] or grammar
            w["d"] = w["d"] or deriv
            w["t"] = w["t"] or tier
            w["f"] = w["f"] if w["f"] is not None else fam

    for t in part1["tiers"]:
        for x in t["words"]:
            add(x["greek"], x["lemma"], x["gloss"], x["grammar"], x["derivative"], t["heading"], None)
    for f in fams:
        for x in f["words"]:
            add(x["greek"], x["lemma"], x["gloss"], x["grammar"], "", "", f["id"])

    families, units = [], []
    for f in fams:
        members = []
        for w in f["words"]:
            if w["greek"] in words and w["greek"] not in members:
                members.append(w["greek"])
        if not members:
            continue
        families.append({"id": f["id"], "root": f["root"], "gloss": f["root_gloss"], "members": members})
    for f in families:
        head = max(f["members"], key=lambda m: words[m]["c"])
        title = f"root {f['root']}" if f["root"] else f"{head} and its family"
        parts = [f["members"][i:i + 10] for i in range(0, len(f["members"]), 10)]
        for k, part in enumerate(parts, 1):
            units.append({"id": f"fam-{f['id']}" + (f"-{k}" if len(parts) > 1 else ""), "kind": "family",
                          "family": f["id"],
                          "title": title + (f" ({k} of {len(parts)})" if len(parts) > 1 else ""),
                          "subtitle": f["gloss"] or words[head]["g"], "words": part})
    in_family = {m for f in families for m in f["members"]}
    rest = []
    for t in part1["tiers"]:
        for w in t["words"]:
            if w["greek"] in words and w["greek"] not in in_family and w["greek"] not in rest:
                rest.append(w["greek"])
    for i in range(0, len(rest), 12):
        chunk = rest[i:i + 12]
        units.append({"id": f"freq-{i // 12 + 1}", "kind": "frequency",
                      "title": f"Frequency list {i // 12 + 1}",
                      "subtitle": words[chunk[0]]["t"].replace("Words Occurring ", "").lower() or "",
                      "words": chunk})
    # One path: every unit ordered by its most frequent word, so the commonest words come first
    # whether or not they belong to a family. Parts of one family stay together, in order.
    def top(u):
        fam_units = [v for v in units if v.get("family") is not None and v.get("family") == u.get("family")]
        group = fam_units if fam_units else [u]
        return -max(words[w]["c"] for v in group for w in v["words"])
    units.sort(key=lambda u: (top(u), u["id"]))
    n = 0
    for u in units:  # number the frequency lessons in path order
        if u["kind"] == "frequency":
            n += 1
            u["title"] = f"Common words {n}"

    # The sources print a space before , ; : and the like (Moss: "both, and ; 2. often …"); close it up.
    for w in words.values():
        for f, v in w.items():
            if isinstance(v, str):
                w[f] = tidy(v)
    out = ROOT / "app/assets/data/lexicon.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {"meta": {"nt_tokens": nt_tokens, "built": date.today().isoformat(),
                     "sources": ["Metzger, Lexical Aids for Students of New Testament Greek (1946)",
                                 "Souter, A Pocket Lexicon to the Greek New Testament (1916)",
                                 "Moss, A First Greek Reader (1893), Vocabulary",
                                 "MorphGNT SBLGNT (CC BY-SA 3.0) for NT frequencies"]},
            "words": words, "families": families, "units": units}
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(words)} words, {len(families)} families, {len(units)} units "
          f"({sum(u['kind'] == 'family' for u in units)} family, {sum(u['kind'] == 'frequency' for u in units)} frequency) "
          f"-> {out} ({out.stat().st_size // 1024} KB); NT tokens {nt_tokens}")


if __name__ == "__main__":
    main()
