# NT Greek App

Data and code for a New Testament Greek vocabulary app: words taught by root family, with Souter's *Pocket Lexicon* built in.

## Sources

| File | What it is | Status |
| --- | --- | --- |
| `source/souter-pocket-lexicon-1917-textkit.pdf` | Alexander Souter, *A Pocket Lexicon to the Greek New Testament* (Oxford, 1916; 1917 printing), Textkit scan, 297 pages, 200 dpi black and white | Public domain (US: pre-1929; UK/EU: author d. 1949) |
| `source/metzger-1946/` | Bruce M. Metzger, *Lexical Aids for Students of New Testament Greek* (Princeton: the author, 1946), typescript. Page images from the HathiTrust full view of the University of Michigan copy (Google-digitized), HathiTrust record 001181348. `page-NNN.png` is the printed page number; `epigraph.png` is the unnumbered epigraph page. Pages 52 and 64 are blank in the original and are not included. | US public domain: no renewal in the NYPL or Stanford renewal records, and open at HathiTrust. The text cites Thayer's count of 5,594 words, not Morgenthaler's, confirming it predates the 1969 edition. Do not use material from the 1969 or 1998 editions. |

## Layout

- `source/` original scans, never edited
- `scripts/` processing scripts
- `data/souter/ocr/page-NNN.txt` raw OCR, one file per PDF page. Pages 1–7 are front matter; the lexicon runs from page 8 to page 297. The first line of each lexicon page is the running head (guide word), not an entry.

- `data/metzger/ocr/page-NNN.txt` raw OCR of the Metzger pages (Tesseract grc+eng, psm 4). Part I (frequency lists) is pages 1–51, Part II (words by root) pages 53–94, appendices pages 95–110.
- `data/nt/lemmas.tsv` every lemma in the SBLGNT with its part of speech, NT count, and rank (5,461 lemmas; 1,125 occur 10+ times). Counted from [MorphGNT](https://github.com/morphgnt/sblgnt) (morphology CC BY-SA 3.0; SBLGNT text CC BY 4.0) by `scripts/build_lemmas.py`.
- `data/souter/tsv/page-NNN.tsv` Tesseract word positions for each lexicon page.
- `data/souter/entries.jsonl` Souter split into 5,747 entries by `scripts/segment_souter.py`. Entries are split at the hanging indent (each page's flush-left edge is fitted as a slanted line, since the scan is skewed); entries the OCR ran together are then split where a sentence ends and a later NT headword follows ("… gain. καπνός, smoke. … καρδία (Lat. cor …"), marked `split_from_merge`. Each entry records the headword as OCR read it, the PDF page, the raw text, and how the headword matched a MorphGNT lemma:
    - `exact`: matched as read
    - `ocr-fix`: matched after a known OCR correction (ξ→ζ, ϑ→θ or δ, δ→ὁ/ὑ, Latin capitals→Greek) or an SBLGNT optional-letter spelling (οὕτως for οὕτω(ς))
    - `accent`: matched ignoring accents and breathings
    - `fuzzy`: one letter off a single lemma that no other entry matched outright; usually a Westcott–Hort spelling (ἐνκ- for ἐγκ-); needs review
    - `position`: headword unreadable (often read as Latin letters: "ydp" γάρ, "Ldw" ζάω, "pita" ῥίζα), assigned the lemma that fits its alphabetical slot and resembles its shape; needs review
    - `reviewed`: decided by hand in `data/souter/entry_overrides.tsv`
    - `none`: no NT lemma (Souter includes variant-reading words), or a fragment

  Coverage: 5,348 of the 5,461 SBLGNT lemmas, and 1,122 of the 1,125 that occur 10+ times. Every word in Metzger's Part I links to its Souter entry. Where several entries carry the same lemma, links go to the strongest match (then the longest entry).
- `data/souter/entries.clean.jsonl` the same entries with a `text_clean` field from `scripts/clean_english.py`, which corrects Tesseract's systematic misreadings of Souter's italic English: *I* read as `7`, `J`, `1`, or `£` (2,621 glosses), *to* as `fo` or `lo`, *the* as `lhe`, *a* as `@`, and about 1,150 other single-letter confusions checked against an English word list. Latin in parentheses and Greek citations are left alone. Every word changed is listed in `data/souter/english_fixes.tsv`.

Still to do in the English: two-letter errors (`unieltered` for *unlettered*), mangled scripture references (`Johniv 5`), and Latin outside parentheses.

## Reproducing the OCR

Needs `pdftoppm` (poppler) and Tesseract 5 with the `grc` and `eng` models from [tessdata_best](https://github.com/tesseract-ocr/tessdata_best).

```
export TESSDATA_PREFIX=/path/to/tessdata
scripts/ocr_souter.sh 1 297
```

The script renders each page at 300 dpi and skips pages already done.

## App data

- `data/moss/moss_lexicon.json` the Vocabulary of C. M. Moss, *A First Greek Reader* (1893), 2,123 entries, as prepared for the MossMethod app (see April's notes for the format). Used to mark NT words a MossMethod student already knows: 568 of the 1,125 NT lemmas occurring 10+ times are in Moss, about 78% of NT word tokens.

- `data/app/lexicon.json` one record per lemma (1,363: every lemma occurring 10+ times in the NT plus every word in Metzger), built by `scripts/build_spine.py` from all of the above: NT count and rank; Metzger's 1946 tier, gloss, grammar, and English derivative; his root family (root, gloss, members); the Appendix II preposition and sense for compound verbs; the Souter entry (cleaned text); whether the word is in Moss (`moss`) and which members of its family are (`family.moss_known`), and a `review` list of reasons a person should check the record (153 records). Of the 1,125 lemmas at 10+, 1,029 are in Metzger's Part I (the rest are mostly proper names, which he excluded), 470 are in a root family, and 1,122 have a Souter entry.

Rebuild everything after a change, in order:

```
python scripts/build_lemmas.py MORPHGNT_DIR
python scripts/segment_souter.py
python scripts/clean_english.py
python scripts/build_part1.py
python scripts/build_families.py
python scripts/build_appendices.py
python scripts/build_spine.py
```
