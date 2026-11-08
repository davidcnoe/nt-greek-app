# Metzger 1946, Part I transcription

`page-NNN.tsv` transcribes Part I ("Words classified according to their frequency"), pages 1–51, from the page images in `source/metzger-1946/`. Pages 1–7 are Metzger's introduction; the frequency lists run from page 8 to page 51.

The pages were transcribed by reading the images directly and checked against the SBLGNT lemma list and Tesseract's OCR of the same page. The lists hold exactly 1,052 words, the total Metzger prints on page 51 (συνίημι is listed twice, on pp. 23 and 29, as typed). Every word is linked to an SBLGNT lemma; links that needed a decision are in `../lemma_overrides.tsv`.

## Record types (tab-separated)

| Record | Fields |
| --- | --- |
| `TIER` | frequency heading as typed ("Words Occurring 42 to 45 Times") |
| `WORD` | headword; grammatical info (forms, article); gloss as typed; English derivative or memory aid (the final parenthetical, without its parentheses; empty if none) |
| `NOTE` | introduction paragraphs (one per paragraph), footnotes, the total, and notes on entries that run onto the next page |
| `UNCERTAIN` | follows a record whose letters, accents, breathings, or punctuation were hard to read; says what |

An entry that runs onto the next page is recorded whole on the page where it starts, with a NOTE on the next page explaining the overflow.

Metzger's spellings, accents, glosses, and English are kept as typed, including slips (κωμή; πολεμός, -οῦ; πληρής; παράχρημα; ἐπιγνώσκω; "boundries"; "cemetary"; "hamartialogy").

## Notes on the 1946 list

- Metzger counted from Thayer's lexicon (1886), so his frequency bands differ from SBLGNT counts in places. `scripts/build_part1.py` reports the large differences; most come from lemmatization (MorphGNT files εἶδον and ὄψομαι under ὁράω, ἐρῶ under λέγω, πλείων under πολύς). One is Metzger's own placement: ἕτοιμος appears in the 91–100 band.
- Compared with the later edition's list, the 1946 list lacks καλέω, ἐμός, ἰσχύω, κατεσθίω, and a few others (confirmed against the page images), and treats ἰδού and ἴδε under εἶδον.
