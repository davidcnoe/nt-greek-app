"""Beyond Metzger: Souter's entries for the NT words Metzger leaves out (fewer than ten occurrences),
proper names included (David, 2026-11-09), for Tertius's brush-up mode.

Reads data/souter/beyond/out/batch-NN.jsonl (proofread against the page images, with a short gloss in
Souter's own words) and writes prototype/data/beyond.json:
  {"meta": {"count": n, "proofread": n}, "words": [{"l": lemma, "c": NT count, "g": gloss, "s": entry}, ...]}
commonest first, then in Souter's order. Words not yet proofread are left out.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUTER = os.path.join(ROOT, "data", "souter")

entries = [json.loads(l) for l in open(os.path.join(SOUTER, "entries.clean.jsonl"), encoding="utf-8")]
order = {e["id"]: i for i, e in enumerate(entries)}
count = {e["id"]: e["nt_count"] for e in entries}

# Rows for the quiz: proofread, with a gloss. Two wrong_entry rows are kept because the word is
# treated inside another entry and the gloss is the word's own (κατωτέρω under κάτω, Κεδρών under κέδρος).
# Cross-references ("see ...", "= ...") are left out: they are spellings of words found elsewhere.
KEEP_WRONG = {2799, 2812}
XREF = ("see ", "= ", "a phonetic spelling")
rows = {}
for path in sorted(glob.glob(os.path.join(SOUTER, "beyond", "out", "batch-*.jsonl"))):
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["status"] in ("wrong_entry", "not_found") and r["entry_id"] not in KEEP_WRONG:
            continue
        if not r.get("gloss") or not r.get("text") or r["gloss"].lower().startswith(XREF):
            continue
        rows.setdefault(r["lemma"], []).append(r)

done = {}
for lemma, rs in rows.items():
    # A lemma with more than one entry: prefer entries whose headword's case matches the lemma's
    # (φιλαδελφία, not the city Φιλαδελφία); drop duplicates; join what is left (βάτος, σύνειμι).
    same = [r for r in rs if r["text"][:1].isupper() == lemma[:1].isupper()] or rs
    uniq = []
    for r in sorted(same, key=lambda r: order[r["entry_id"]]):
        if all(r["text"] != u["text"] for u in uniq):
            uniq.append(r)
    first = dict(uniq[0])
    if len(uniq) > 1:
        first["gloss"] = "; ".join(u["gloss"].strip().rstrip(".") for u in uniq)
        first["text"] = " ".join(u["text"] for u in uniq)
    done[lemma] = first

# The word as shown, where David corrects MorphGNT's form (2026-11-09).
SHOWN = {"Ἁρέτας": "Ἀρέτας"}

words = sorted(done.values(), key=lambda r: (-count[r["entry_id"]], order[r["entry_id"]]))
out = {
    "meta": {"count": len(words), "source": "Souter, A Pocket Lexicon to the Greek New Testament (1916), proofread against the 1917 printing"},
    "words": [{"l": SHOWN.get(r["lemma"], r["lemma"]), "c": count[r["entry_id"]], "g": r["gloss"].strip().rstrip("."), "s": r["text"]} for r in words],
}
dest = os.path.join(ROOT, "prototype", "data", "beyond.json")
with open(dest, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"{len(words)} words -> {dest}")
