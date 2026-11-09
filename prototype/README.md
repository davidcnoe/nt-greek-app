# NT Greek (working name): web prototype

A working prototype of the New Testament vocabulary app, built to look and work like Telamon (the Homer
trainer): the same pages, layout, type and memory system, ported from Telamon's prototype, in a
MossMethod variation of its palette. Vanilla JS, no build step.

## Run it

From the `nt-greek-app` folder:

```
python -m http.server 8642 --directory prototype
```

Then open http://localhost:8642. (Opening `index.html` directly from disk will not load the data.)
After changes, reload with Ctrl+Shift+R: the browser and the offline cache hold on to old copies.
All paths are relative, so the folder also works when served from a subfolder (e.g. `https://host/_f/<version>/`).

## What it does

- Metzger's 1,287 words (*Lexical Aids*, 1946) in his learning path: the units in `lexicon.json`, in order
  (frequency lists interleaved with root families), each word once, where it first appears.
- Telamon's session-based memory system, unchanged (see the comment at the top of `app.js`): every word in
  the active set answered right once per session before new words; a "meet the word" card for each new word;
  mastered = right on the first try in 5 sessions on 5 different days, not counting the introducing session;
  past the active limit, mastered words become FSRS-timed spot checks (`vendor/ts-fsrs-5.4.2`, MIT);
  pause and resume the same day; a summary at the end of each session.
- Cards: the Greek headword with Metzger's genitive and article (or adjective endings); the label line gives
  the word's place in the path (its root family, or Metzger's frequency band); the answer is Metzger's gloss,
  his English derivative ("Cf. …"), the NT count, and a Lexicon entry button. Moss's gloss shows only when
  Settings → MossMethod is Studied.
- Home: percentage = share of the NT's 137,554 running words covered by mastered words (each SBLGNT lemma
  counted once); the bar is full when all 1,287 words are mastered (about 90% of the NT).
- Bottom bar: four buttons labelled 1, 2, 3, 4 (names left open): Home, Tools, Settings, About.
- Tools: Lexicon (Metzger's words with Souter's entries; search in Greek, Latin letters or English, with the
  Greek letter keypad) and Readings (Nunn's Appendix II, easiest first; tap a word for its gloss, a raised
  number for Nunn's note; mastered words in ink, words in the app not yet mastered in the accent colour,
  words not in the app muted).
- Settings: Answer mode (with Timed advance), Direction, Pace, Appearance, MossMethod; Progress (with
  Moss's words counted as familiar when MossMethod is Studied), Share progress, Erase all progress.
- Progress is stored in this browser's localStorage under `ntgreek:progress-v1` (`?profile=name` keeps a
  separate store, for testing; `?notes=1` shows keyboard hints).
- Works offline after one visit (`sw.js`). Add any new file the app loads to `SHELL` in `sw.js` and bump `VERSION`.

## Rebuilding the data

```
python scripts/build_prototype_data.py
```

Copies `app/assets/data/lexicon.json` and `readings.json` into `prototype/data/`. Bump `VERSION` in `sw.js` afterwards.
