# Proofreading Souter's rarer words (Beyond Metzger) against the printed page

You have one batch folder: `work/batch-NN/` (under `data/souter/beyond/`). It holds `targets.json` and page
images `page-PPP.png` (the 1917 printing of Souter, *A Pocket Lexicon to the Greek New Testament*; PPP is the
PDF page).

`targets.json` maps a page number to the entries on it. Each has `entry_id`, `lemma` (the New Testament
word, from MorphGNT), `headword_ocr`, `current_text` (a machine reading, often garbled and sometimes cut
short), and `nt_count` (how often the word occurs in the NT). These are the rarer words (fewer than ten
occurrences), including proper names.

For every target entry:
1. Open the page image (use the Read tool on the PNG) and find the entry whose headword is `lemma`
   (the headword may differ slightly in accent or spelling; use the current text as a guide).
2. Transcribe the WHOLE entry exactly as printed, from its headword to its last word, including any
   lines that run onto the next page (`page-(PPP+1).png` is in the folder when needed).
   - Plain text, one line; join hyphenated line breaks (`mean-ing` → `meaning`) unless the hyphen is
     a real one.
   - Greek exactly as printed, with every accent, breathing, and iota subscript, in precomposed
     Unicode. A capital with a breathing printed before it (᾿Α) is written as one letter (Ἀ).
   - Keep Souter's punctuation, references (Mk. vii 4, Ac. xxv 13: roman numerals in lower case as
     printed), brackets, and abbreviations. No italics or other markup.
   - Never correct or modernize Souter: transcribe what the page says.
3. Give a short `gloss` for a vocabulary quiz: Souter's own first English meaning, copied word for word
   from your transcription, never paraphrased or added to. Usually the words after the headword up to the
   first semicolon or colon, e.g. `a star`, `I shine`, `peace-making, peace-maker`, `maimed`,
   `Aaron, son of Amram and Jochebed, younger brother of Moses`. Rules:
   - Leave out Latin equivalents, etymologies, and grammatical notes in brackets before the meaning
     (`κυλλός (debilis), maimed.` → `maimed`), Souter's `(a)`/`(b)` labels, references, and a final full stop.
   - Keep it under about 60 characters: if the first meaning is longer, stop at a comma where the words
     still make sense. For a proper name, give the name and, if short, who or what it is
     (`Aaron, brother of Moses` is NOT allowed: copy contiguous words, `Aaron, son of Amram and Jochebed`).
   - If the entry gives no English meaning (only a cross-reference such as `see ἄλφα`), give the
     cross-reference as printed.
4. Write one JSON line per entry to `out/batch-NN.jsonl` (under `data/souter/beyond/`; create `out/` if
   needed), with these keys: `entry_id`, `lemma`, `page`, `text` (your transcription), `gloss`, `status`:
   - `ok`: you are confident the transcription matches the page;
   - `doubt`: some character or word is unclear on the image (say which in `note`);
   - `wrong_entry`: the entry on the page is not for this lemma (say in `note` which headword it is);
   - `not_found`: you cannot find it (say why in `note`).
   and `note` (empty unless needed).
5. When finished, check that `out/batch-NN.jsonl` has exactly one line per target entry and valid JSON on
   every line, then reply with the counts by status and every `doubt`, `wrong_entry`, and `not_found`
   line in brief.

Work page by page. Read each page image once and transcribe all its targets from it. Write to the output
file as you go (append after each page), so no work is lost.
