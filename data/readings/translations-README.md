# English translations for Nunn's Appendix II readings

`prototype/data/translations.json` holds public-domain English translations, matched paragraph by paragraph to the Greek in `prototype/data/readings.json`, for the app's "English" button. The Gospel of Peter is left out. Each paragraph covers the same text as Nunn's Greek. Where Nunn leaves out text, the English leaves it out too and marks the gap with " … ". Subheadings and Nunn's source line ("Plato, Apology (abridged).") are `null`. The translators' notes, marginal headings, and page numbers are removed. Their spelling, punctuation, and square-bracketed words are kept as printed (in ANF, the brackets mark words the translators supplied).

| Reading | Translator | Title | Year | Passage | Text taken from |
|---|---|---|---|---|---|
| didache | Kirsopp Lake | The Apostolic Fathers, Loeb, vol. 1 | 1912 | Didache 7, 9–10, 14–15 | PerseusDL/canonical-greekLit `tlg1311.tlg001.perseus-eng1.xml` |
| didache-apostles | Kirsopp Lake | same | 1912 | Didache 11.3–12 | same file |
| 1-clement | Kirsopp Lake | same | 1912 | 1 Clement 5, 24–25, 49, 50.1–2, 42, 44.1–5, 47–48 | canonical-greekLit `tlg1271.tlg001.perseus-eng1.xml` |
| hermas | Kirsopp Lake | The Apostolic Fathers, Loeb, vol. 2 | 1913 | Vision III 2.4 (second half)–7.6 | canonical-greekLit `tlg1419.tlg001.perseus-eng1.xml` |
| diognetus | Kirsopp Lake | same | 1913 | Diognetus 5, 6, 7.1–6 | canonical-greekLit `tlg0646.tlg004.perseus-eng1.xml` |
| polycarp | Kirsopp Lake | same | 1913 | Martyrdom of Polycarp 5–18 | canonical-greekLit `tlg1484.tlg001.perseus-eng1.xml` |
| socrates | Harold North Fowler | Plato, vol. 1, Loeb | 1914 | Apology 40c–41a, 41c–d, 42a (abridged as in Nunn) | canonical-greekLit `tlg0059.tlg002.perseus-eng2.xml` |
| lucian | H. W. Fowler and F. G. Fowler | The Works of Lucian of Samosata, vol. 4 (Clarendon Press) | 1905 | The Death of Peregrine 11–13, 14 (first sentence) | canonical-greekLit `tlg0062.tlg042.perseus-eng4.xml` |
| justin | Marcus Dods | Ante-Nicene Fathers, vol. 1 (Roberts and Donaldson, eds.; American ed.) | 1885 | First Apology 65–67 | CCEL ThML `anf01.xml`, from the GitHub repo GZancewicz/ante-nicene-fathers (`sources/xml/anf01.xml`) |
| ignatius | Roberts and Donaldson, eds. | Ante-Nicene Fathers, vol. 1, "The Martyrdom of Ignatius" | 1885 | Chapters 1–2, 6 (end), 7 (abridged as in Nunn) | same `anf01.xml` |
| carpus | E. C. E. Owen | Some Authentic Acts of the Early Martyrs (Oxford) | 1927 | not obtained | none yet. Every paragraph is `null`, and the entry has `"missing": true` |

I checked each TEI file's header for the translator. The Perseus Fowler Plato is a digitization of the Loeb text (the header gives a later printing). The Perseus Lucian file `perseus-eng2` is A. M. Harmon's Loeb translation, so I did not use it.

## Corrections to the digitized text

The Perseus Lake and Fowler-Lucian files are OCR and contain scanning errors. I corrected only obvious ones. These paragraphs are in the `check` lists and should be compared with the printed books:
- 1 Clement: showred → showed; ground,, → ground,; wrhen → when; Having· → Having; liolily → holily; \o them → to them; "Lord; ”" → "Lord;”".
- Hermas: "water. Lady?" → "water, Lady?"; bv → by; "know. Lady," / "who. Lady," → comma.
- Diognetus 6: "body. that" → "body, that"; removed a stray section number "10.".
- Polycarp: graqe → grace; wras → was; "sacrifice. as" → "sacrifice, as"; "martyr. Polycarp" → "martyr, Polycarp"; Alee → Alce; removed the stray space after an opening quotation mark.
- Lucian: "prison, This" → "prison. This"; amade → a made; thaa → than; themszlves → themselves. Removed the opening quotation mark of the speaker's speech at §11 and §14.

## Gaps marked with " … " (Nunn's omissions)
- Hermas Vis. III 3.1: "and that they may be made more joyful,"
- Polycarp 15.2: "as bread that is being baked, or"; 16.1: "a dove, and"
- Plato and Ignatius: abridged as in Nunn (see the passages above).
- Ignatius 7: the date sentence and the final "Amen." are left out because Nunn's Greek lacks them.
