"""Assemble Nunn's Appendix II readings from the proofread page files.

Usage: python scripts/build_nunn_readings.py

Reads data/readings/nunn-appendix-ii/pages/p-NNN.md (one file per PDF page,
proofread against the page images; Nunn's footnote numbers kept as printed).
Writes, in data/readings/nunn-appendix-ii/:
  readings.json  sections -> paragraphs (text with note ids) + notes + coverage
  NN-<slug>.md   one readable file per reading, notes renumbered 1..N
  coverage.tsv   vocabulary coverage of each reading against the NT and the app

Nunn's note numbers restart at each new passage, sometimes mid-page, and a few
markers point back to a note printed on an earlier page. Markers are resolved
page by page: a marker uses the current group of notes on its page, moves on
to the next group when the current one lacks its number, and otherwise falls
back to the most recent note with that number earlier in the same reading.
"""

import collections
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "readings" / "nunn-appendix-ii"
MORPHGNT = pathlib.Path("/home/claude/morphgnt")
MARK = re.compile(r"\[(\d+)\](?:\[sic\])?")
GREEK = re.compile(r"[Ͱ-Ͽἀ-῿]+(?:['’᾽][Ͱ-Ͽἀ-῿]*)?")

SLUGS = [  # first words of each major heading -> (slug, short title, author, date)
    ("AN EARLY ACCOUNT", "didache", "The Didache: baptism and the eucharist", "Didache", "c. 100"),
    ("APOSTLES AND PROPHETS", "didache-apostles", "The Didache: apostles and prophets", "Didache", "c. 100"),
    ("EXTRACTS FROM THE EPISTLE OF CLEMENT", "1-clement", "1 Clement: extracts", "Clement of Rome", "c. 95"),
    ("A VISION OF HERMAS", "hermas", "Hermas: a vision of the Church", "Hermas", "2nd c."),
    ("A SELECTION FROM THE GOSPEL", "gospel-of-peter", "The Gospel of Peter", "Gospel of Peter", "2nd c."),
    ("THE CHRISTIANS IN THE WORLD", "diognetus", "The Christians in the world (Diognetus)", "Epistle to Diognetus", "2nd c."),
    ("THE MARTYRDOM OF IGNATIUS", "ignatius", "The Martyrdom of Ignatius", "Acts of Ignatius", ""),
    ("THE MARTYRDOM OF CARPUS", "carpus", "The Martyrdom of Carpus", "Acts of Carpus", ""),
    ("THE MARTYRDOM OF POLYCARP", "polycarp", "The Martyrdom of Polycarp", "Martyrdom of Polycarp", "155"),
    ("A DESCRIPTION OF THE EUCHARIST", "justin", "Justin Martyr on the eucharist", "Justin Martyr, 1 Apology", "2nd c."),
    ("A HOSTILE OUTSIDER", "lucian", "A hostile outsider's view (Lucian)", "Lucian, Peregrinus", "2nd c."),
    ("THE LAST WORDS OF SOCRATES", "socrates", "The last words of Socrates", "Plato, Apology", "4th c. B.C."),
]


def bare(word: str) -> str:
    word = unicodedata.normalize("NFD", word.lower())
    word = "".join(c for c in word if not unicodedata.combining(c))
    return word.replace("ς", "σ").strip("'’᾽")


def parse_page(path: pathlib.Path):
    """Yield events in page order: heading, intro, para, notes-group."""
    pdf = int(re.search(r"p-(\d+)", path.name).group(1))
    events, in_notes, group, prev_heading = [], False, [], False
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = re.sub(r"<!--.*?-->", "", raw).strip()
        if raw.strip().startswith("<!--") and not line:
            continue
        if line.startswith("### Notes"):
            in_notes, group = True, []
            events.append(("notes", group))
            continue
        if line.startswith("## "):
            in_notes = False
            events.append(("heading", line[3:].strip()))
            prev_heading = True
            continue
        if not line:
            if in_notes and group:
                group = []
                events.append(("notes", group))
            continue
        if in_notes:
            m = re.match(r"\[(\d+|cont\.)\]\s*(.*)", line)
            if m:
                group.append([m.group(1), m.group(2)])
            elif group:
                group[-1][1] += " " + line
            continue
        events.append(("para", line))
    return pdf, [e for e in events if e[0] != "notes" or e[1]]


def main() -> None:
    pages = sorted((DIR / "pages").glob("p-*.md"))
    sections, cur, sub = [], None, None
    for path in pages:
        pdf, events = parse_page(path)
        page = pdf - 160
        page_paras, page_groups = [], []
        for kind, val in events:
            if kind == "heading":
                page_paras.append((None, None))
                major = next((s for s in SLUGS if val.upper().startswith(s[0])), None)
                if val == "APPENDIX II":
                    cur = {"slug": "preface", "heading": val, "intro": [], "paras": [], "notes": [], "pages": []}
                    sections.append(cur)
                elif major:
                    cur = {"slug": major[1], "title": major[2], "author": major[3], "date": major[4],
                           "heading": val, "intro": [], "paras": [], "notes": [], "pages": []}
                    sections.append(cur)
                    sub = None
                else:
                    sub = val
                    cur["paras"].append({"subheading": val})
            elif kind == "para" and not GREEK.search(val[:40]) and not any("text" in q for q in cur["paras"]):
                cur["intro"].append(val)
            elif kind == "para":
                p = {"page": page, "text": val}
                cur["paras"].append(p)
                page_paras.append((cur, p))
            else:
                if val[0][0] == "cont.":
                    owner = sections[-1] if not page_paras else page_paras[0][0]
                    prev = [s for s in sections if s["notes"]]
                    target = owner if owner["notes"] else prev[-1]
                    target["notes"][-1]["text"] += " " + val[0][1]
                    val = val[1:]
                    if not val:
                        continue
                page_groups.append(val)
            if cur and page not in cur["pages"]:
                cur["pages"].append(page)
        # attach this page's note groups to the section of the paragraphs they follow
        group_objs = []
        for k, g in enumerate(page_groups):
            objs = []
            for num, text in g:
                objs.append({"key": f"p{page}" + (f"{'abc'[k]}" if len(page_groups) > 1 else "") + f"n{num}",
                             "n": int(num), "page": page, "text": text})
            group_objs.append(objs)
        gi, used = 0, False
        for sec, p in page_paras:
            if p is None:  # a heading starts a new run of notes
                if used:
                    gi, used = gi + 1, False
                continue
            def resolve(m, sec=sec):
                nonlocal gi, used
                if m.group(0).endswith("[sic]"):
                    return m.group(0)  # Nunn's orphan marker, kept as printed
                n = int(m.group(1))
                for j in range(gi, len(group_objs)):
                    hit = next((o for o in group_objs[j] if o["n"] == n), None)
                    if hit:
                        gi, used = j, True
                        break
                else:
                    hit = next((o for o in reversed(sec["notes"]) if o["n"] == n), None)
                if hit is None:
                    return m.group(0)  # orphan marker, left as printed
                if "id" not in hit:
                    hit["id"] = hit.pop("key")
                    sec["notes"].append(hit)
                return f"[^{hit['id']}]"
            p["text"] = MARK.sub(resolve, p["text"])
        unused = [o for g in group_objs for o in g if "id" not in o]
        for o in unused:
            print(f"warning: p. {page} note {o['n']} has no marker")

    # vocabulary coverage
    form_lemma, lemma_count = {}, collections.Counter()
    for f in sorted(MORPHGNT.glob("*-morphgnt.txt")):
        for line in f.read_text(encoding="utf-8").splitlines():
            c = line.split()
            lemma = unicodedata.normalize("NFC", c[6])
            form_lemma.setdefault(bare(c[5]), lemma)
            lemma_count[lemma] += 1
    lex = json.loads((ROOT / "data" / "app" / "lexicon.json").read_text(encoding="utf-8"))
    taught = {r["lemma"] for r in lex if r.get("metzger")}
    moss = {r["lemma"] for r in lex if r.get("moss")}
    rows = []
    for sec in sections:
        if sec["slug"] == "preface":
            continue
        toks = [bare(w) for p in sec["paras"] if "text" in p for w in GREEK.findall(re.sub(r"\[\^[^\]]+\]", "", p["text"]))]
        lemmas = [form_lemma.get(t) for t in toks]
        n = len(toks)
        cov = {
            "tokens": n,
            "nt_form": round(100 * sum(1 for l in lemmas if l) / n, 1),
            "metzger": round(100 * sum(1 for l in lemmas if l in taught) / n, 1),
            "moss": round(100 * sum(1 for l in lemmas if l in moss) / n, 1),
            "unknown_forms": sorted({t for t, l in zip(toks, lemmas) if not l}),
        }
        sec["coverage"] = cov
        rows.append((sec["slug"], n, cov["nt_form"], cov["metzger"], cov["moss"], len(cov["unknown_forms"])))

    DIR.joinpath("readings.json").write_text(json.dumps(sections, ensure_ascii=False, indent=1), encoding="utf-8")
    with DIR.joinpath("coverage.tsv").open("w", encoding="utf-8") as fh:
        fh.write("reading\ttokens\tpct_form_in_NT\tpct_Metzger_word\tpct_Moss_word\tdistinct_non_NT_forms\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")

    # readable markdown, notes renumbered per reading
    for old in DIR.glob("[0-9][0-9]-*.md"):
        old.unlink()
    k = 0
    for sec in sections:
        if sec["slug"] == "preface":
            name = "00-preface.md"
        else:
            k += 1
            name = f"{k:02d}-{sec['slug']}.md"
        num = {o["id"]: i + 1 for i, o in enumerate(sec["notes"])}
        sub_ = lambda t: re.sub(r"\[\^([^\]]+)\]", lambda m: f"[{num[m.group(1)]}]", t)
        pg = sec["pages"]
        out = [f"# {sec['heading']}", "",
               f"*Nunn, A Short Syntax of New Testament Greek (1920), Appendix II, pp. {pg[0]}–{pg[-1]}.*", ""]
        out += [*sec["intro"], ""] if sec["intro"] else []
        for p in sec["paras"]:
            out += [f"## {p['subheading']}" if "subheading" in p else sub_(p["text"]), ""]
        if sec["notes"]:
            out += ["## Notes", ""]
            out += [f"{num[o['id']]}. {o['text']}  " for o in sec["notes"]]
        DIR.joinpath(name).write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    for r in rows:
        print(*r, sep="\t")


if __name__ == "__main__":
    main()
