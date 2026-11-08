# Survey of four public-domain N.T. Greek grammars for the NT Greek app

Surveyed 8 November 2026. Source PDFs are in `Greek Lexica, Grammars, etc/` (user uploads). All five PDFs are pre-1929 printings and US public domain. "PDF p." means the page index in the PDF file; "p." alone means the printed page number.

Extracts made for v1 are in `data/grammars/` (list at the end).

## How each book was checked

- `pdfinfo` for page counts; `pdftotext` on sample pages to judge the text layer; `pdftoppm` at 100–300 dpi plus Tesseract (grc+eng) for scans without a usable layer; page images read directly to check Greek.
- Printed-page offsets were confirmed at several points in each book.

---

## 1. Nunn, *A Short Syntax of New Testament Greek* (1920)

- **Edition:** Rev. H. P. V. Nunn, M.A., *A Short Syntax of New Testament Greek*, Cambridge: at the University Press, 1920. Third edition (1st 1912, 2nd 1913; preface to the third edition dated Heaton Moor, Stockport, January 1920). Same author's *Elements of New Testament Greek* is advertised opposite the title.
- **File:** `Nunn, P.V. A Short Syntax of New Testament Greek, 1920.pdf`, 200 PDF pages (Internet Archive scan, Blackwell's copy). Main text PDF p. = printed p. + 16. Appendices I–II are separately paginated (pp. 1–36 = PDF pp. 161–196).
- **Text layer:** good. Internet Archive OCR with Greek: English is nearly clean; Greek is mostly right but has scattered errors (ev for ἐν, wap é€avto for παρ᾽ ἑαυτῷ, Sid for διά), so every extract still needs checking against the image. **Exception:** the verb tables, pp. 130–134 (PDF pp. 146–150), are printed sideways and the text layer is garbage; they had to be rotated and OCR'd.
- **Note on the user's clippings:** "6 differences between Attic and Koine, page 27" is p. 27 (PDF p. 43). "One difference between Attic and Koine" is § 51, p. 50 (PDF p. 66). Both are in the PDF and match it.
- **Contents:**
  - Front: prefaces; **Glossary of Grammatical Terms** with etymologies (pp. ix–xii).
  - **Part I** (pp. 1–24): English grammar for students who lack it: parts of speech, parsing, nouns, adjectives, verbs (voice, deponents, tense, mood, participles, infinitive), sentences, noun, adjectival, and adverbial clauses.
  - **Part II** (pp. 25–129): The Greek of the N.T. (pp. 25–27); Prepositions with Appendix "Prepositions in Composition" (pp. 28–36); subject and predicate; cases; adjectives; pronouns (§ 51 αὐτός); the article; verb: mood, voice, tense (§§ 77–112); sentences; subjunctive, imperative, prohibitions; infinitive and noun clauses; adverbial and adjectival clauses; participles; οὐ and μή; questions; the particle ἄν (pp. 128–129).
  - **Appendix** (p. 129) and **Classes of Verbs** (pp. 130–134): principal-parts tables in ten classes.
  - Indexes (English, Greek, texts), pp. 135–144.
  - **Appendix I** (pp. 1–3): Acts 10 printed with footnotes keyed to the syntax paragraphs.
  - **Appendix II** (pp. 4–36): graded readings from early Christian Greek (Didache, 1 Clement, Hermas, Diognetus, Ignatius, Martyrdoms of Carpus and Polycarp, Gospel of Peter, Justin's *Apology*, a hostile outsider's view of Christianity, and "The last words of Socrates to his judges"), with footnotes keyed to the syntax and glosses of rare words.

**Useful sections, ranked**

1. **pp. 25–27, "The Greek of the New Testament," with the six differences from Attic, plus § 51 (p. 50) on αὐτός** → a "From Moss to the New Testament" primer screen. This is the clearest short statement of what changes for an Attic-trained reader. **Extracted.**
2. **pp. 130–134, Classes of Verbs** (about 70 of the commonest N.T. verbs, six principal parts plus meaning, grouped by how the present stem is built) → principal-parts panel on verb cards; a "stem class" tag for each verb; drills. **Extracted.**
3. **§§ 1–7, pp. 28–31, prepositions table (root meaning in capitals, uses by case)** and **Appendix, pp. 31–36, Prepositions in Composition** (each preposition's root meaning shown inside 80-odd compound verbs and nouns, plus a note on "perfective" prepositions) → preposition cards, and the explanation layer for compound verbs in Metzger's root families (ἔρχομαι → ἀπ-, δι-, εἰσ-, ἐξ-, προσ-). **Extracted.**
4. **Appendix II** (pp. 4–36): extra-biblical Koine readings with grammar notes and glosses → a later "beyond the N.T." reading module; vocabulary-coverage tests against the app's word list. Greek in the text layer would need full proofreading. Not extracted.
5. **Scattered "Classical vs N.T." notes** that extend the six differences (each is a short paragraph): neuter plural subject with plural verb, p. 37 (§ 10); genitive of definition "not in Classical Greek," p. 43 (§ 31); reflexive rule broken in N.T., p. 46; οὐ μή, p. 82 (§ 123); ἵνα clauses replacing the infinitive, pp. 88, 104–108 (§§ 186–192, several marked "Not Classical"); ὅπως + future in Classical vs N.T. infinitive, p. 100; subjunctive without ἄν for Classical optative, p. 113; οὐ in protases, pp. 116, 126; potential ἄν rare in the N.T., p. 128 → each can become a one-line "Attic vs Koine" tip linked from the primer screen. Not extracted (short; easy to add later).
6. **§§ 77–112, pp. 61–79, the verb (mood, voice, tense)** → grammar tips. Clear and simple, but Burton covers tense better for this app.
7. **The Particle ἄν, pp. 128–129** → a card for ἄν/ἐάν/ὅταν.
8. **Glossary of Grammatical Terms** (pp. ix–xii) → tooltip definitions for grammar words, with the Greek/Latin etymologies homeschool users will like.

**Not useful:** Part I (English grammar) is too elementary for the stated audience; Appendix I is only Acts 10, which the app will have anyway; the indexes.

---

## 2. Burton, *Syntax of the Moods and Tenses in New Testament Greek* (1898)

- **Edition:** Ernest De Witt Burton (University of Chicago), *Syntax of the Moods and Tenses in New Testament Greek*, third edition, Edinburgh: T. & T. Clark, 1898. Copyright 1892; first issued as a pamphlet 1888; preface September 1893; note to the third edition June 1898. (The user called this "Brunner"; it is Burton.)
- **File:** `Burton, Syntax of the Moods and Tenses in New Testament Greek, 1898.pdf`, 242 PDF pages (Google Books scan, 600-dpi bitonal). PDF p. = printed p. + 28 (p. 1 = PDF p. 29).
- **Text layer:** none (only the Google boilerplate page). Tesseract grc+eng at 300 dpi reads it very well: English nearly perfect, Greek good with occasional errors (els for εἰς, yap for γάρ, numerals in references). Clean, high-quality scan.
- **Contents:** Introductory §§ 1–4 (form and function; the interpreter and grammar; four moods and seven tenses). **Tenses** §§ 5–166: the indicative tenses one by one (progressive, conative, gnomic, historical present; imperfect; aorist §§ 35–57 with inceptive, resultative, gnomic, epistolary, dramatic uses and English equivalents; future; perfect §§ 74–88; pluperfect; future perfect); tenses of the dependent moods §§ 95–114; tenses of the participle §§ 115–156. **Moods** §§ 157–486: moods in principal clauses (indicative, hortatory, prohibitory and deliberative subjunctive, optative, imperative); moods in subordinate clauses: final (ἵνα, ὅπως, μή) §§ 188–227, causal, result, conditional §§ 238–277, concessive, relative, temporal, indirect discourse; the infinitive; the participle; negatives with infinitive and participle. Indexes.

**Useful sections, ranked**

1. **§§ 5–7 (pp. 6–7) and § 95, 96, 98 (pp. 46–47): what a tense means: progress (aspect) in every mood, time only in the indicative** → the core "tense" tip shown on every verb card and in the parsing help. **Extracted.**
2. **Lexically specific tense notes**: § 16 ἥκω "I have come," πάρειμι, ἀκούω "I am informed" (p. 10); § 47 ἀπέθανον, ἐξέστην, ἔγνων with perfect force (p. 22); § 35 inceptive and resultative aorists (σιγᾶν/σιγῆσαι, κωλύειν/κωλῦσαι) (pp. 16–17); §§ 74–77 perfects of existing state and intensive perfects (πέποιθα, μέμνημαι, γέγραπται, πεπίστευκα) (pp. 37–38); §§ 56–57 ἔλεγον vs εἶπον (pp. 30–31) → notes attached to the specific verb cards. **Extracted** (one file with the general sections).
3. **§§ 52–55, English equivalents of the aorist indicative (pp. 23–30)** → translation hints. Not extracted.
4. **§§ 160–184, hortatory/prohibitory/deliberative subjunctive and the imperative** (pp. 74–81) → tips on μή + aorist subjunctive vs μή + present imperative. Not extracted; candidate for v2.
5. **§§ 188–227, final particles and ἵνα clauses** (pp. 83–96) → supports Nunn's point (3); a "ἵνα in the N.T." screen. v2.
6. **§§ 238–277, conditional sentences** (pp. 100–112) → a conditional-sentence chart. v2; more a reading-course topic than a vocabulary-app one.

**Not useful for this app:** most of the book is fine-grained syntax for exegesis (indirect discourse, relative and temporal clauses, infinitive and participle subtypes). Good reference, too detailed for cards. Its many English-usage discussions add length without vocabulary value.

---

## 3. Blass, *Grammar of New Testament Greek* (1898)

- **Edition:** Friedrich Blass, *Grammar of New Testament Greek*, translated by Henry St. John Thackeray, London: Macmillan, 1898 (printed at Glasgow by Robert MacLehose), from the first German edition (1896). The ancestor of Blass–Debrunner–Funk.
- **File:** `Blass, Friedrich - Grammar of New Testament Greek, 1898.pdf`, 360 PDF pages (Internet Archive scan, grayscale, about 400 dpi). PDF p. = printed p. + 16 throughout (checked at pp. 4, 52, 324).
- **Text layer:** English good; **Greek unusable** (Latin-letter garbage such as "Kouu-TwoYa"). Tesseract grc+eng on fresh 300-dpi renders reads the Greek decently, but this book is dense with small Greek, manuscript sigla, and references, so OCR errors are frequent (e.g. "Phryn. 241" for 294, "3. 16" for 2. 16). Every extract must be proofread line by line against enlarged crops.
- **Contents (Part I, Introduction, Phonetics and Accidence):** § 1 Introduction; § 2 Elements of the N.T. language (Latin, Hebrew/Aramaic elements) pp. 2–6; §§ 3–6 orthography, accents, elision, sound changes; §§ 7–13 declensions, indeclinables, adjectives, numerals, pronouns; §§ 14–23 conjugation (augment, futures, first and second aorist, terminations, contract verbs, -μι verbs) pp. 36–52; **§ 24 Table of noteworthy verbs** pp. 52–58; § 25 adverbs; **§ 26 Particles** pp. 60–61; **§ 27 Word-formation by terminations and suffixes** pp. 61–65; **§ 28 Word-formation by composition** pp. 65–70; § 29 proper names. **Part II, Syntax:** §§ 30–38 agreement and cases; **§§ 39–43 prepositions** pp. 121–140; §§ 44–51 adjectives, article, pronouns; §§ 52–74 verb (voices, tenses, moods, remains of the optative § 67, infinitive, ἵνα and ὅτι, participle); §§ 75–78 negatives, adverbs, particles; §§ 79–82 sentence connection, word order, ellipse, figures. Indexes of subjects, Greek words, passages.

**Useful sections, ranked**

1. **§ 27 Word-formation by suffixes, pp. 61–65** → the suffix inventory behind root families: -όω, -ίζω, -εύω verbs; -μός (action), -μα (result), -σις (abstract), -της (agent), -ότης, -σύνη, diminutives, -ικός, -ινός, each with N.T. examples. Suffix tips on root-family screens. **Extracted.**
2. **§ 26 Particles, pp. 60–61** → the complete list of particles that occur in the N.T., and the Attic particles that never do (ἀτάρ, ἅτε, αὖ, γοῦν, δῆθεν, δῆτα, εἴθε, μῶν …). Directly serves Moss students. **Extracted.**
3. **§ 24 Table of noteworthy verbs, pp. 52–58** → alphabetical list of verbs whose N.T. forms differ from Attic (e.g. ἀκούσω beside ἀκούσομαι, ἥμαρτον/ἡμάρτησα, κατεάξω), with references and the Attic form. The best single source for "Attic form → N.T. form" notes on verb cards, but very dense (sigla, MS evidence) and about six pages of small Greek. **Recommended next extract (v1.1).** Use alongside Nunn's verb classes.
4. **§ 28 Word-formation by composition, pp. 65–70** → compound types, verbs with two prepositions, compound adjectives in -τος; complements Nunn's composition appendix. v2.
5. **§ 2 Elements of the N.T. language, pp. 2–6** → Latinisms (κουστωδία, σουδάριον, κεντυρίων) and Hebraisms (πρόσωπον λαμβάνειν, σκάνδαλον) for a "loanwords" tag in the vocabulary data. v2.
6. **§ 67 Remains of the optative, p. 221**, and **§ 69 ἵνα** → evidence for Nunn's points (2) and (3); quotable in the primer's "read more" layer.
7. **§§ 39–43 Prepositions, pp. 121–140** → thorough but long; Nunn's table is the better fit for cards. Use only to settle doubtful senses.

**Not useful for this app:** orthography and accent sections (§§ 3–6), proper names, word order and figures (§§ 80–82), and most of the case syntax, which are scholarly apparatus rather than learner material. The English translation is close to the German and often reads stiffly.

---

## 4a. Winer–Moulton, *A Treatise on the Grammar of New Testament Greek* (1882)

- **Edition:** G. B. Winer, *A Treatise on the Grammar of New Testament Greek, regarded as a sure basis for New Testament exegesis*, translated with large additions and full indices by W. F. Moulton, third edition, revised (ninth English edition), Edinburgh: T. & T. Clark, 1882. Translated from Winer's sixth German edition with the additions for the seventh.
- **File:** `Winer, A Treatise of the Grammar of New Testament Greek, 1882.pdf`, 884 PDF pages, 55 MB (Internet Archive scan). PDF p. = printed p. + 32 (checked at pp. 13, 68, 98, 268, 468, 668, 798).
- **Text layer:** English fair to good (some broken words, small-type notes jumbled); **Greek unusable** (Latin-letter garbage), same LuraDocument recoding as Blass. Needs OCR for any Greek.
- **Contents:** Introduction (object, treatment, history of N.T. grammar) pp. 1–11. **Part I**, character of N.T. diction (opinions; its basis; Hebrew-Aramaic colouring; grammatical character) pp. 12–41. **Part II, Accidence** §§ v–xvi pp. 42–128: orthography, accent, punctuation; unusual forms in the declensions; foreign and indeclinable nouns; adjectives; augment; unusual verb forms; -μι and irregular verbs (p. 93); **defective verbs** (pp. 98–112, alphabetical); **formation of derivative and compound words** (pp. 112–128). **Part III, Syntax** pp. 129–800: article, pronouns, noun and cases, adjectives, numerals, verb (voices, tenses, moods, ἄν, imperative, infinitive, participle), particles and prepositions (pp. 447–540), conjunctions, adverbs, negatives, interrogatives, sentence structure, anacoluthon, ellipsis, pleonasm, attraction, paronomasia. Indexes of passages, subjects, Greek words (pp. 801–).

**Useful sections, ranked**

1. **§ xv Defective verbs, pp. 98–112** → alphabetical list of irregular N.T. verbs with forms and references; overlaps Blass § 24 and is longer. Use as a cross-check for verb-card notes. Not extracted.
2. **§ xvi Formation of derivative and compound words, pp. 112–128** → covers the same ground as Blass §§ 27–28 at greater length; useful to resolve doubtful derivations in root families. Not extracted.
3. **§ lii Construction of verbs compounded with prepositions, pp. 529–541** → supports compound-verb notes. Not extracted.
4. **Part I §§ ii–iv, pp. 20–41** → the older (pre-papyri) view that N.T. Greek is a Hebraic dialect; useful only as historical background. Nunn already reports the newer view.

**Not useful:** for a vocabulary app almost all of this 800-page reference work is too detailed, and its view of the language predates the papyri. Its Greek would have to be OCR'd from scratch. It is a scholar's lookup tool, not a source of learner text.

## 4b. Winer, *A Greek Grammar of the New Testament* (Andover, 1825), identified

- **Identification:** this second "Winer" file is the **first American translation**: *A Greek Grammar of the New Testament*, translated from the German of George Benedict Winer by **Moses Stuart** and **Edward Robinson**, Andover: printed at the Codman Press by Flagg and Gould, **1825** (translators' preface dated Andover Theological Seminary, January 1825). It renders an early German edition of Winer's *Grammatik des neutestamentlichen Sprachidioms* (first German edition 1822). Stuart translated up to the syntax of verbs, Robinson the rest. Harvard College Library copy, Google Books scan.
- **File:** `Winer, Greek Grammar of the NT.pdf`, 189 PDF pages. About 175 printed pages. PDF p. is roughly printed p. + 7 in the syntax (offset not checked throughout).
- **Text layer:** none. Scan is a noisy bitonal Google scan; Tesseract output for Greek is poor (sample from the article section, PDF p. 61, garbled most Greek words).
- **Contents:** Introduction (design, method, history) pp. 1–16; Part I character of N.T. diction (§§ 1–4) pp. 17–35; Part II forms of words (§§ 5–11: contraction and crasis, unusual noun inflections, foreign words, unusual verb inflections, -μι and irregular verbs, defective verbs) pp. 36–48; Part III syntax (§§ 12–54: article, pronouns, cases, adjectives, voices, tenses, moods, ἄν, infinitive, participles, prepositions, adverbs, negatives, paronomasia, attraction, anacoluthon, word order, ellipsis, pleonasm) pp. 49–176.

**Useful sections:** none worth extracting. Everything in it is superseded by the 1882 Moulton translation of a much later edition, and the scan is the worst of the set. Its only interest is historical (an early landmark of American N.T. scholarship). The translators themselves call Winer's treatment of prepositions "rather ingenious than solid."

---

## Recommended short list for v1 (transcribed)

| # | Extract | Source pages | App use | File |
|---|---|---|---|---|
| 1 | Nunn, The Greek of the N.T.; six differences from Attic; § 51 αὐτός | pp. 25–27, 50 | "From Moss to the N.T." primer screen | `data/grammars/nunn-attic-vs-koine.md` |
| 2 | Nunn, Classes of Verbs (principal parts, 10 classes, about 70 verbs) | pp. 129–134 | principal-parts panel and stem-class tag on verb cards | `data/grammars/nunn-classes-of-verbs.md` |
| 3 | Nunn, Prepositions §§ 1–7 and Prepositions in Composition | pp. 28–36 | preposition cards; meaning layer for compound verbs in root families | `data/grammars/nunn-prepositions.md` |
| 4 | Blass § 27, word-formation by suffixes | pp. 61–65 | suffix tips on root-family screens | `data/grammars/blass-word-formation-suffixes.md` |
| 5 | Blass § 26, particles in and absent from the N.T. | pp. 60–61 | particle list; "Attic particles you won't meet" tip | `data/grammars/blass-particles.md` |
| 6 | Burton, tense essentials (§§ 5–7, 16, 35, 47, 56–57, 74–77, 95–96, 98) | pp. 6–7, 10, 16–17, 22, 30–31, 37–38, 46–47 | aspect tip on verb cards; verb-specific notes (ἥκω, ἀπέθανον, πέποιθα, οἶδα-type perfects) | `data/grammars/burton-tense-essentials.md` |

**Next in line (v1.1/v2), not yet transcribed:** Blass § 24 Table of noteworthy verbs (pp. 52–58); the scattered Nunn "Classical vs N.T." notes listed under Nunn item 5; Nunn Appendix II readings; Blass § 28 composition and § 2 loanwords; Burton §§ 160–184 (prohibitions) and §§ 188–227 (ἵνα).

## Problems found

- **Nunn:** the verb tables (PDF pp. 146–150) are rotated and their text layer is garbage; they were rotated and OCR'd. Two misprints in the tables are kept and marked [sic] (πέμπομαι for πέπεμμαι; ἄφηκα). In the print the "Meaning" column is badly aligned with the verbs; meanings were matched to their verbs by sense. PDF pp. 1–5 and 197–200 are covers, bookplates, and blank leaves; no text pages are missing.
- **Blass and Winer–Moulton:** Greek in the text layer is unusable throughout; every Greek extract needs fresh OCR and close proofreading. No missing pages were found at the points checked (offset constant across each book).
- **Burton and Winer 1825:** no text layer. Burton's scan is excellent; the 1825 Winer scan is poor.
- **Doubtful readings** in the extracts are marked [?]: the vowel points of two Hebrew phrases in Blass § 27, the length marks Nunn prints over ι in the Class 6 heading and in ἔκρῑνα, and the faint last digit of Burton's preface date (1893).
