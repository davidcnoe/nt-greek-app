"""Combine everything into one record per NT lemma: the data the app reads.

Usage: python scripts/build_spine.py

Inputs: data/nt/lemmas.tsv, data/metzger/part1.json, data/metzger/families.json,
data/metzger/appendices.json, data/souter/entries.clean.jsonl.
Output: data/app/lexicon.json, a list of records for every lemma that occurs 10+ times in the
NT or appears anywhere in Metzger, sorted by NT frequency:

  lemma, pos, nt_count, nt_rank,
  metzger: {tier, tier_min, tier_max, greek, grammar, gloss, derivative, page} or null,
  family: {id, root, root_gloss, members: [lemmas]} or null,
  compound_of: {preposition, sense} or null      (Appendix II),
  souter: {entry_id, text, match} or null,
  review: [reasons a person should check this record]

Glosses are Metzger's and Souter's as typed; none are invented here.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from metzger_match import Matcher  # noqa: E402


def main() -> None:
    M = Matcher()
    lemmas = {}
    for line in (ROOT / "data/nt/lemmas.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        lemma, pos, count, rank = line.split("\t")
        lemmas[lemma] = {"lemma": lemma, "pos": pos, "nt_count": int(count), "nt_rank": int(rank),
                         "metzger": None, "family": None, "compound_of": None, "souter": None,
                         "review": []}

    part1 = json.loads((ROOT / "data/metzger/part1.json").read_text(encoding="utf-8"))
    for t in part1["tiers"]:
        for w in t["words"]:
            rec = lemmas.get(w["lemma"])
            if rec is None:
                continue
            if rec["metzger"] is None:
                rec["metzger"] = {"tier": t["heading"], "tier_min": t["min"], "tier_max": t["max"],
                                  "greek": w["greek"], "grammar": w["grammar"], "gloss": w["gloss"],
                                  "derivative": w["derivative"], "page": w["page"]}
            if w["match"] in ("fuzzy", "override"):
                rec["review"].append(f"Metzger Part I headword {w['greek']} linked by {w['match']}")
            if w["uncertain"]:
                rec["review"].append(f"Part I transcription uncertain: {'; '.join(w['uncertain'])}")

    families = json.loads((ROOT / "data/metzger/families.json").read_text(encoding="utf-8"))
    for f in families:
        members = [w["lemma"] for w in f["words"] if w["lemma"]]
        for w in f["words"]:
            rec = lemmas.get(w["lemma"])
            if rec is None:
                continue
            if rec["family"] is None:
                rec["family"] = {"id": f["id"], "root": f["root"], "root_gloss": f["root_gloss"],
                                 "members": members, "gloss_in_family": w["gloss"]}
            if w["uncertain"]:
                rec["review"].append(f"Part II transcription uncertain: {'; '.join(w['uncertain'])}")
        if f["crosses_page"]:
            for l in members:
                if l in lemmas and lemmas[l]["family"] and lemmas[l]["family"]["id"] == f["id"]:
                    pass  # joins were reviewed by eye; see data/metzger/part2/page_starts.tsv

    for s in json.loads((ROOT / "data/metzger/appendices.json").read_text(encoding="utf-8")):
        for r in s["records"]:
            if r["type"] == "word" and r.get("preposition") and r.get("lemma") in lemmas:
                lemmas[r["lemma"]]["compound_of"] = {"preposition": r["preposition"], "sense": r["sense"]}

    for lemma, rec in lemmas.items():
        e = M.souter.get(lemma)
        if e:
            rec["souter"] = {"entry_id": e["id"], "text": e["text_clean"], "match": e["match"],
                             "page": e["page"]}
            if e["match"] in ("fuzzy", "position"):
                rec["review"].append(f"Souter entry identified by {e['match']} (headword unreadable or spelled differently)")

    # MossMethod: which NT words a Moss student has met (data/moss/moss_lexicon.json, Moss's
    # First Greek Reader vocabulary). Match on lemma as typed, then ignoring accents.
    from segment_souter import strip_accents
    moss = json.loads((ROOT / "data/moss/moss_lexicon.json").read_text(encoding="utf-8"))["entries"]
    moss_by_lemma: dict[str, dict] = {}
    moss_by_key: dict[str, dict] = {}
    for m in moss:
        if m.get("type") != "lemma" or m.get("is_stem"):
            continue
        moss_by_lemma.setdefault(m["lemma"], m)
        moss_by_key.setdefault(strip_accents(m["lemma"]), m)
    for lemma, rec in lemmas.items():
        m = moss_by_lemma.get(lemma) or moss_by_key.get(strip_accents(lemma))
        rec["moss"] = {"id": m["id"], "meaning": m["meaning"]} if m else None
    for f in families:
        known = [w["lemma"] for w in f["words"] if w["lemma"] in lemmas and lemmas[w["lemma"]]["moss"]]
        for w in f["words"]:
            rec = lemmas.get(w["lemma"])
            if rec and rec["family"] and rec["family"]["id"] == f["id"]:
                rec["family"]["moss_known"] = known

    keep = [r for r in lemmas.values() if r["nt_count"] >= 10 or r["metzger"] or r["family"]]
    keep.sort(key=lambda r: r["nt_rank"])
    out = ROOT / "data/app/lexicon.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(keep, ensure_ascii=False, indent=1), encoding="utf-8")

    n = len(keep)
    print(f"{n} lemma records -> {out}")
    print(f"  with a Metzger Part I entry: {sum(1 for r in keep if r['metzger'])}")
    print(f"  in a Metzger root family: {sum(1 for r in keep if r['family'])}")
    print(f"  listed as a prepositional compound: {sum(1 for r in keep if r['compound_of'])}")
    print(f"  with a Souter entry: {sum(1 for r in keep if r['souter'])}")
    print(f"  known from Moss: {sum(1 for r in keep if r['moss'])}; "
          f"in a family with a Moss word: {sum(1 for r in keep if r['family'] and r['family'].get('moss_known'))}")
    print(f"  flagged for review: {sum(1 for r in keep if r['review'])}")
    freq = [r for r in keep if r["nt_count"] >= 10]
    print(f"  of the {len(freq)} lemmas at 10+: {sum(1 for r in freq if r['metzger'])} in Metzger Part I, "
          f"{sum(1 for r in freq if r['family'])} in a family, {sum(1 for r in freq if r['souter'])} in Souter")


if __name__ == "__main__":
    main()
