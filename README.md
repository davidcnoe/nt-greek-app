# NT Greek App

Data and code for a New Testament Greek vocabulary app: words taught by root family, with Souter's *Pocket Lexicon* built in.

## Sources

| File | What it is | Status |
| --- | --- | --- |
| `source/souter-pocket-lexicon-1917-textkit.pdf` | Alexander Souter, *A Pocket Lexicon to the Greek New Testament* (Oxford, 1916; 1917 printing), Textkit scan, 297 pages, 200 dpi black and white | Public domain (US: pre-1929; UK/EU: author d. 1949) |
| Metzger, *Lexical Aids for Students of New Testament Greek* (1946) | Part II root groupings and appendices | Not yet in the repository. The 1946 edition shows no copyright renewal and is open as public domain at HathiTrust (record 001181348). Do not use material from the 1969 or 1998 editions. |

## Layout

- `source/` original scans, never edited
- `scripts/` processing scripts
- `data/souter/ocr/page-NNN.txt` raw OCR, one file per PDF page. Pages 1–7 are front matter; the lexicon runs from page 8 to page 297. The first line of each lexicon page is the running head (guide word), not an entry.

## Reproducing the OCR

Needs `pdftoppm` (poppler) and Tesseract 5 with the `grc` and `eng` models from [tessdata_best](https://github.com/tesseract-ocr/tessdata_best).

```
export TESSDATA_PREFIX=/path/to/tessdata
scripts/ocr_souter.sh 1 297
```

The script renders each page at 300 dpi and skips pages already done.
