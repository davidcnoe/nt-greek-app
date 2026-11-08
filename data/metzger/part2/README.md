# Metzger 1946, Part II transcription

`page-NNN.tsv` transcribes Part II ("Words classified according to their root") page by page from the page images in `source/metzger-1946/`. Pages 65–94 are done; page 64 is still missing from the scans.

The pages were transcribed by reading the images directly (the typescript's hand-added accents defeat OCR), then checked two ways: every headword against the SBLGNT lemma list, and against Tesseract's independent OCR of the same page. All 705 headwords match an NT lemma except σθένος, which Metzger himself marks "not in the New Testament". Where the OCR disagreed with the transcription (46 words), the transcription matched a real lemma exactly in every case.

## Record types (tab-separated)

| Record | Fields |
| --- | --- |
| `ROOT` | root as typed, in Greek capitals (Metzger's typed Latin F for digamma is written Ϝ); root gloss |
| `BREAK` | extra vertical space separating two families |
| `WORD` | headword; grammatical info (genitive, article, adjective endings); gloss as typed |
| `NOTE` | any other line |
| `UNCERTAIN` | follows a record whose letters, accents, or breathings were hard to read; says what |

Metzger's spellings and glosses are kept as typed, including slips (κωμή, -ῆς; δύνατος; "vengence"; the root gloss "shire" for *shine* on p. 91). Corrections belong in the app data, not here.

## Other files

- `page_starts.tsv` pages that open a new family although no root header is typed there (pp. 76 and 85), decided by eye and by etymology. Every other page continues the family from the page before.
- `../lemma_overrides.tsv` links Metzger's forms to SBLGNT lemmas where they differ: principal parts (εἶδον, ὄψομαι → ὁράω; ἐρῶ → λέγω), comparatives (πλείων → πολύς), and middle/active or spelling differences.
- `../families.json` the assembled families, built by `scripts/build_families.py`: root, gloss, pages, and each word with its gloss, SBLGNT lemma, NT count, Souter entry id, OCR agreement, and any uncertainty notes.

διαλογίζομαι appears in two families (p. 81 and p. 82), as Metzger typed it.
