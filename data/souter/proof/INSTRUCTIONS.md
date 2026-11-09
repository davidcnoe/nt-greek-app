# Proofreading Souter's Pocket Lexicon entries against the printed page

You have one batch folder: `work/batch-NN/`. It holds `targets.json` and page images `page-PPP.png`
(the 1917 printing of Souter, *A Pocket Lexicon to the Greek New Testament*; PPP is the PDF page).

`targets.json` maps a page number to the entries on it that the Tertius app uses. Each has `entry_id`,
`lemma` (the New Testament word the app links it to), `headword_ocr`, and `current_text` (a machine
reading, often garbled and often cut short).

For every target entry:
1. Open the page image (use the Read tool on the PNG) and find the entry whose headword is `lemma`
   (or the form the app linked: the headword may differ slightly in accent or spelling; use the
   current text as a guide to which entry is meant).
2. Transcribe the WHOLE entry exactly as printed, from its headword to its last word, including any
   lines that run onto the next page (`page-(PPP+1).png` is in the folder when needed).
   - Plain text, one line; join hyphenated line breaks (`mean-ing` → `meaning`) unless the hyphen is
     a real one.
   - Greek exactly as printed, with every accent, breathing, and iota subscript, in precomposed
     Unicode. A capital with a breathing printed before it (᾿Α) is written as one letter (Ἀ).
   - Keep Souter's punctuation, references (Mk. vii 4, Ac. xxv 13: roman numerals in lower case as
     printed), brackets, and abbreviations. No italics or other markup.
   - Never correct or modernize Souter: transcribe what the page says.
3. Write one JSON line per entry to `out/batch-NN.jsonl` (create `out/`), with these keys:
   `entry_id`, `lemma`, `page`, `text` (your transcription), `status`:
   - `ok`: you are confident the transcription matches the page;
   - `doubt`: some character or word is unclear on the image (say which in `note`);
   - `wrong_entry`: the app's link looks wrong (the entry on the page is not for this lemma; say in
     `note` which headword it should be and give the text of the right entry if it is on these pages);
   - `not_found`: you cannot find it (say why in `note`).
   and `note` (empty unless needed).
4. When finished, check that `out/batch-NN.jsonl` has exactly one line per target entry, then reply
   with the counts by status and every `doubt`, `wrong_entry`, and `not_found` line in brief.

Work page by page. Read each page image once and transcribe all its targets from it.
