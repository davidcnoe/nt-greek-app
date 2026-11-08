# Nunn, *A Short Syntax of New Testament Greek* (Cambridge 1920), Appendix II

Twelve graded readings from early Christian Greek (plus Socrates' last words), with Nunn's footnotes: section references to his *Syntax* and glosses of rarer words. Public domain.

- `pages/p-NNN.md`: one file per PDF page (printed page = PDF − 160), proofread word by word against 400 dpi page images. Nunn's footnote numbers are kept as printed. Nunn's misprints are kept and marked [sic]; the two uncertain readings are marked [?] (ἔκαυσεν, p. 31; λοιπὸν, p. 32). Printing blemishes are noted in HTML comments.
- `NN-<slug>.md`: one readable file per reading, footnotes renumbered 1…N within the reading.
- `readings.json`: the same for the app: intro, paragraphs (with `[^id]` note links), subheadings, notes, pages, and vocabulary coverage.
- `coverage.tsv`: share of each reading's word tokens whose form occurs in the NT (SBLGNT), whose NT lemma is in Metzger's list, and whose lemma is in the MossMethod list. Forms not found in the NT are not lemmatized, so the Metzger and Moss figures are lower bounds.

Rebuild: `python scripts/build_nunn_readings.py` (needs MorphGNT SBLGNT in /home/claude/morphgnt).

Nunn's note numbers restart with each passage, sometimes mid-page, and a few markers point back to a note on an earlier page (p. 14 [26] → p. 13; p. 32 [6] → p. 31). The build script resolves these; see its docstring.
