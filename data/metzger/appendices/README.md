# Metzger 1946, appendices (pp. 95–110)

`page-NNN.tsv` transcribes the appendices from the page images in `source/metzger-1946/`, checked as for Parts I and II. `scripts/build_appendices.py` assembles them into `../appendices.json`.

The 1946 edition has three appendices (the later editions add principal parts of verbs and second-declension feminine nouns, which are not in this edition):

| Appendix | Pages | Contents |
| --- | --- | --- |
| I. The Indo-European Family of Languages | 95–101 | Prose on comparative philology and Grimm's law, with footnotes; Table I (the Indo-European languages, a five-column grid, pp. 96–97); the square of mutes and Greek–English cognate pairs (pp. 100–101) |
| II. Prepositions in Composition with Verbs | 102–109 | Introduction on the perfective use (p. 102); Table II, a geometric arrangement of the prepositions with their cases and meanings (p. 103); then each preposition's root meaning and senses with the NT compounds that show them, 84 verbs (pp. 104–109) |
| III. Table of Correlative Pronouns and Adverbs | 110 | Interrogative, indefinite, demonstrative, and relative forms for quality, quantity, place, time, and manner |

## Record types (tab-separated)

| Record | Fields |
| --- | --- |
| `HEADING` | appendix title, table title, or sense heading as typed ("ἀνά (1) Root meaning upwards", "(2) Again, anew, thoroughly") |
| `NOTE` | prose paragraph or footnote (markers as superscripts) |
| `ROW` | one row of a table, cells left to right; stacked items in one cell joined with " / "; empty cells kept so columns line up |
| `WORD` | Greek; forms or grammatical info; gloss; (Appendix I only) English cognate |
| `UNCERTAIN` | follows a hard-to-read record; says what |

In `appendices.json`, each Appendix II compound carries the preposition and sense heading it is listed under, plus its SBLGNT lemma and Souter entry. All 84 compounds match NT lemmas. The 8 Greek words in Appendix I that do not are Metzger's illustrations of Grimm's law (βύρσα, κύβος, δρῦς, ὀδόντ-, φράτηρ, μέθυ, ὀχέω, χήν), not NT vocabulary.

Pencilled notes by a later reader of the Michigan copy (e.g. "Yiddish" beside German in Table I) are not transcribed.
