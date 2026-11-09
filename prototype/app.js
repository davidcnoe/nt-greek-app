// NT Greek prototype: Metzger's New Testament vocabulary in Telamon's session-based memory system.
// A port of Telamon's prototype (the Homer trainer): same pages, layout and memory system; the Homer-only
// parts (passages, audio, dialect, verb forms, translations, Hecatomb, the gem) are left out.
// Progress lives in this browser's localStorage; the real app will keep it in SQLite.
import { fsrs, generatorParameters, createEmptyCard, Rating } from "./vendor/ts-fsrs-5.4.2/index.mjs";

const APP_VERSION = "0.1.0 (prototype)";
// ?profile=name keeps a separate set of progress (for testing without touching real progress).
const PROFILE = new URLSearchParams(location.search).get("profile");
const STORE = "ntgreek:progress-v1" + (PROFILE ? `-${PROFILE}` : "");
// The app shows only what a learner sees. ?notes=1 turns on notes for David (keyboard hints,
// the prototype tag); anything marked class="note".
if (new URLSearchParams(location.search).get("notes") === "1") document.documentElement.classList.add("notes");
// The memory system (Telamon's, David, 2026-10-31 to 2026-11-06):
// - Session 1 brings 5 new words; session 2 reviews them with none new; each later session adds the
//   number set by Settings → Pace (3, 5, 8 or 12; 5 by default). The active set holds ACTIVE_LIMIT (25)
//   or 4 × pace + 1, whichever is more.
// - Every session first reviews every word in the active set (shuffled). Each must be answered
//   right once; a miss sends the word back a few cards later. Only then do the new words appear,
//   and they too must each be answered right once.
// - A word is mastered once it has been answered right on the first try in 5 sessions in a row, on 5
//   different days, not counting the session that introduced it; a miss starts the count again.
// - When the active set grows past its limit, its longest-held mastered words retire from it and come
//   back as spot checks on a timed rotation (FSRS due dates). A missed spot check puts the word back in
//   the active set, to be learned again.
// - English -> Greek (Settings, Direction): a second card for each word, kept under the key "r:" + id,
//   with its own tally and the same rules; only for words mastered Greek -> English; always multiple choice.
// Word order: Metzger's path (lexicon.json units, in order: frequency lists interleaved with root families).
const FIRST_SESSION_NEW = 5;
const PACE = {
  gentle: { label: "Gentle", n: 3 },
  standard: { label: "Standard", n: 5 },
  brisk: { label: "Brisk", n: 8 },
  intensive: { label: "Intensive", n: 12 }, // Telamon's "Achilles"
};
const newPerSession = () => (PACE[state.settings.pace] || PACE.standard).n;
const sessionsToFinish = n => 2 + Math.ceil((words.length - FIRST_SESSION_NEW) / n) + SESSIONS_TO_LEARN;
const SESSIONS_TO_LEARN = 5;
const ACTIVE_LIMIT = 25;
const activeLimit = () => Math.max(ACTIVE_LIMIT, (SESSIONS_TO_LEARN + 1) * newPerSession() + 1);
const REQUEUE_GAP = 3; // a missed word comes back after this many other cards
const CHOICES = 3; // multiple choice: one right answer, two wrong
// Timed advance after a multiple-choice answer (Settings); milliseconds.
const ADVANCE = {
  quick: { label: "Hare", right: 1000, wrong: 2500 },
  standard: { label: "Standard", right: 1500, wrong: 4000 },
  relaxed: { label: "Relaxed", right: 2500, wrong: 6000 },
  extended: { label: "Tortoise", right: 4000, wrong: 10000 },
};
let advanceTimer = null;

// Presses the Continue button after the chosen delay, unless the learner touches anything else
// first; the button fills as time runs out.
function autoAdvance(button, right) {
  clearTimeout(advanceTimer);
  const a = ADVANCE[state.settings.advance];
  if (!a || !button) return;
  const ms = right ? a.right : a.wrong;
  button.style.setProperty("--advance-ms", `${ms}ms`);
  button.classList.add("counting");
  const stop = e => {
    if (e && button.contains(e.target)) return;
    clearTimeout(advanceTimer);
    button.classList.remove("counting");
    document.removeEventListener("pointerdown", stop, true);
  };
  document.addEventListener("pointerdown", stop, true);
  advanceTimer = setTimeout(() => {
    document.removeEventListener("pointerdown", stop, true);
    if (button.isConnected) button.click();
  }, ms);
}
const scheduler = fsrs(generatorParameters({ enable_fuzz: true, request_retention: 0.9 }));

const app = document.getElementById("app");
// words: Metzger's words in path order, each {id: Metzger's form, ...lexicon fields}.
let words = [], byId = {}, families = {}, unitOf = {}, meta = {}, state, session = null;
let maxCoverage = 1;

// ---------- data and storage ----------

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function load() {
  let s = null;
  try { s = JSON.parse(localStorage.getItem(STORE)); } catch { /* private mode or bad data */ }
  s = s || {};
  s.cards = s.cards || {};
  s.studyDays = s.studyDays || [];
  s.sessions = s.sessions ?? 0;
  // moss: "studied" = the learner has done MossMethod (the Expo app's mossGraduate).
  s.settings = { mode: "recall", direction: "ge", pace: "standard", theme: "system", labels: "en", labelCase: "normal", advance: "standard", moss: "no", ...s.settings };
  // tally[id]: {correct: sessions in a row counted toward mastery, last: last such session, day: its
  // date, since: session the word entered the active set, retired: true while out on spot-check rotation}.
  s.tally = s.tally || {};
  s.studyMs = s.studyMs || 0;
  for (const c of Object.values(s.cards)) {
    c.due = new Date(c.due);
    if (c.last_review) c.last_review = new Date(c.last_review);
  }
  return s;
}

function save() {
  try { localStorage.setItem(STORE, JSON.stringify(state)); } catch { /* storage full or blocked */ }
}

// ---------- the memory system ----------

const REV = "r:";
const isRev = key => key.startsWith(REV);
const idOf = key => isRev(key) ? key.slice(REV.length) : key;
const tracks = () => ({ ge: [false], eg: [true], both: [false, true] })[state.settings.direction] || [false];

const isLearned = key => (state.tally[key]?.correct || 0) >= SESSIONS_TO_LEARN;
const learnedIds = () => Object.keys(state.tally).filter(k => !isRev(k) && isLearned(k) && byId[k]);
const seenIds = (rev = false) => Object.keys(state.cards).filter(k => isRev(k) === rev && byId[idOf(k)]);
const activeIds = (rev = false) => seenIds(rev).filter(k => !state.tally[k]?.retired);
const mossOn = () => state.settings.moss === "yes";

// Percentages are whole numbers, and never below 1% once the learner has started a session.
function pct(fraction) {
  const n = Math.round(fraction * 100);
  return n < 1 && fraction > 0 && (state.pending || seenIds().length) ? 1 : n;
}

// Share of the NT's running words (137,554) whose lemma is in the given words; each lemma counted once.
function tokenShare(ids) {
  const lemmas = new Map();
  for (const id of ids) { const w = byId[id]; if (w) lemmas.set(w.l, w.c); }
  let n = 0;
  for (const c of lemmas.values()) n += c;
  return n / meta.nt_tokens;
}
const coverage = () => tokenShare(learnedIds());
// Settings → MossMethod → Studied: Moss's words not yet mastered count as familiar (Progress only).
function familiarShare() {
  if (!mossOn()) return 0;
  const learned = new Set(learnedIds().map(id => byId[id].l));
  return tokenShare(words.filter(w => w.m && !learned.has(w.l)).map(w => w.id));
}

function retireOldest() {
  for (const rev of [false, true]) {
    const active = activeIds(rev);
    let extra = active.length - activeLimit();
    if (extra <= 0) continue;
    const oldest = active.filter(isLearned).sort((a, b) => state.tally[a].since - state.tally[b].since);
    for (const key of oldest) {
      if (extra-- <= 0) break;
      state.tally[key].retired = true;
    }
  }
}

function spotChecksDue(now = new Date()) {
  return tracks().flatMap(rev => seenIds(rev).filter(k => state.tally[k]?.retired && state.cards[k].due <= now));
}

function sessionPlan(now = new Date()) {
  const number = state.sessions + 1;
  const review = [...tracks().flatMap(rev => activeIds(rev)), ...spotChecksDue(now)];
  if (state.pending?.session === number) return { number, review: review.filter(id => !state.pending.newIds.includes(id)), newIds: state.pending.newIds };
  const newIds = [];
  if (tracks().includes(false)) {
    const count = state.sessions === 0 ? FIRST_SESSION_NEW : state.sessions === 1 ? 0 : newPerSession();
    newIds.push(...words.filter(w => !state.cards[w.id]).slice(0, Math.max(0, count - (state.sessions === 0 ? review.length : 0))).map(w => w.id));
  }
  if (tracks().includes(true)) {
    newIds.push(...words.filter(w => isLearned(w.id) && !state.cards[REV + w.id]).slice(0, newPerSession()).map(w => REV + w.id));
  }
  return { number, review, newIds };
}

function streak() {
  const days = new Set(state.studyDays);
  let n = 0;
  const d = new Date();
  if (!days.has(today())) d.setDate(d.getDate() - 1);
  for (;;) {
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    if (!days.has(key)) return n;
    n++;
    d.setDate(d.getDate() - 1);
  }
}

// ---------- rendering helpers ----------

const esc = s => String(s).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
const times = n => `${n.toLocaleString()} time${n === 1 ? "" : "s"}`;

function shuffle(list) {
  const a = [...list];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const GLOSS_STOP = new Set(["i", "a", "an", "the", "be", "am", "is", "one", "oneself", "myself", "with", "gen", "dat", "acc",
  "singular", "plural", "something", "someone", "etc", "or", "of", "to", "and", "in", "on"]);
const meaningWords = s => s.toLowerCase().replace(/[^a-z]+/g, " ").trim().split(" ").filter(t => t && !GLOSS_STOP.has(t));

// Metzger gives no part of speech; a rough kind from his grammatical note, for plausible wrong answers.
function kindOf(w) {
  if (/(^|[\s,])(ὁ|ἡ|τό)(\s|,|$)/.test(w.gr)) return "noun";
  if (w.gr.startsWith("-")) return "adjective";
  if (/(ω|ομαι|μι|μαι)$/.test(w.id)) return "verb";
  return "other";
}

// One right answer and two wrong ones, of the same kind and, where possible, nearby on the path.
function makeChoices(key) {
  const id = idOf(key);
  const w = byId[id];
  const at = words.indexOf(w);
  const kind = kindOf(w);
  const used = new Set(meaningWords(w.g));
  const clash = x => (w.f != null && x.f === w.f) || meaningWords(x.g).some(t => used.has(t));
  const wrong = [];
  for (const [test, near] of [[x => kindOf(x) === kind, 150], [x => kindOf(x) === kind, Infinity], [() => true, Infinity]]) {
    for (const x of shuffle(words.filter((x, i) => x !== w && test(x) && Math.abs(i - at) <= near))) {
      if (wrong.length === CHOICES - 1) break;
      if (clash(x) || wrong.includes(x)) continue;
      wrong.push(x);
      for (const t of meaningWords(x.g)) used.add(t);
    }
  }
  return shuffle([w, ...wrong]).map(x => ({ id: x.id, english: x.g, right: x.id === id }));
}

// The Greek heading with Metzger's genitive and article (or adjective endings), as on the Expo word page.
const greekHtml = w => `<span lang="grc">${esc(w.id)}</span>${w.gr ? `<span class="forms" lang="grc">, ${esc(w.gr)}</span>` : ""}`;

// The card's label line: where the word sits in Metzger's path (a root family or a frequency list).
function unitLabel(w) {
  const u = unitOf[w.id];
  if (!u) return "";
  if (u.kind === "family") return u.title.replace(/\s*\((?:\d+|\d+ of \d+)\)$/, "");
  return `occurs ${u.subtitle}`;
}

// ---------- screens ----------

function renderHome() {
  session = null;
  const plan = sessionPlan();
  const review = plan.review.length;
  const fresh = plan.newIds.length;
  const paused = pausedSession();
  const cov = coverage();
  app.innerHTML = `
    <section class="home">
      <h1 class="home-title">Master New Testament Vocabulary<small>one word at a time</small></h1>
      <button class="primary" id="start" ${paused || review + fresh ? "" : "disabled"}>${paused
        ? `resume session ${paused.number} · ${paused.passed.length} of ${paused.total} done`
        : review + fresh ? `start session ${plan.number}` : "all caught up"}</button>
      <div class="home-progress"><span>${pct(cov)}%</span><span>${learnedIds().length} mastered</span></div>
      <div class="meter" role="img" aria-label="${pct(cov)} percent of the words in the New Testament; the bar is full at ${pct(maxCoverage)} percent, all ${words.length.toLocaleString()} words">
        <i style="width:${Math.min(100, cov * 100 / maxCoverage)}%"></i></div>
      <p class="home-tagline">Metzger's New Testament vocabulary, most frequent first, with root families and Souter's lexicon.</p>
    </section>`;
  document.getElementById("start").onclick = paused ? resumeSession : startSession;
}

function progressText() {
  const days = streak();
  return [
    "My NT Greek progress (New Testament vocabulary)",
    `${learnedIds().length} words mastered, ${pct(coverage())}% of the words in the New Testament`,
    `${state.sessions} session${state.sessions === 1 ? "" : "s"}${days ? `, ${days}-day streak` : ""}`,
  ].join("\n");
}

async function shareProgress(button) {
  const text = progressText();
  try {
    if (navigator.share) return await navigator.share({ title: "My NT Greek progress", text });
    await navigator.clipboard.writeText(text);
    button.textContent = "Copied to clipboard";
  } catch (e) {
    if (e.name === "AbortError") return;
    try { await navigator.clipboard.writeText(text); button.textContent = "Copied to clipboard"; }
    catch { button.textContent = "Couldn't share"; }
  }
}

function timeSpent(ms) {
  const min = Math.round(ms / 60000);
  if (min < 1) return ms ? "under a minute" : "none yet";
  return min < 60 ? `${min} min` : `${Math.floor(min / 60)}h ${min % 60}m`;
}

// Settings → Progress: where the learner stands, in figures.
function progressHtml() {
  const mastered = learnedIds().length;
  const started = seenIds().length;
  const reverse = Object.keys(state.tally).filter(k => isRev(k) && isLearned(k)).length;
  const fam = familiarShare();
  const stat = (n, l) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`;
  return `
    <div class="coverage progress-card">
      <div class="big">${mastered.toLocaleString()} <small>of ${words.length.toLocaleString()} words mastered</small></div>
      <div class="meter" role="img" aria-label="${pct(mastered / words.length)} percent of the words">
        <i style="width:${mastered / words.length * 100}%"></i></div>
      <p style="margin:8px 0 0;font-size:13px">${pct(mastered / words.length)}% of Metzger's words ·
        ${pct(coverage())}% of the words in the New Testament</p>
      ${fam ? `<p style="margin:4px 0 0;font-size:13px">Another ${pct(fam)}% of the New Testament is familiar from MossMethod.</p>` : ""}
      <p style="margin:4px 0 0;font-size:12px">Mastering all ${words.length.toLocaleString()} words covers about ${pct(maxCoverage)}% of the New Testament; the bar on the home page shows your progress toward that goal.</p>
    </div>
    <div class="stats">
      ${stat(started - mastered, "words in progress")}
      ${reverse ? stat(reverse, "mastered English → Greek") : ""}
      ${stat(timeSpent(state.studyMs), "time spent")}
      ${stat(state.sessions, `session${state.sessions === 1 ? "" : "s"} completed`)}
      ${stat(state.studyDays.length, `day${state.studyDays.length === 1 ? "" : "s"} of study`)}
      ${stat(streak(), "day streak")}
    </div>`;
}

// Bottom-bar labels in English, Latin or Greek, as in Telamon (David's picks there, 2026-10-31 and 11-03).
const TAB_LABELS = {
  en: { home: "Home", tools: "Tools", settings: "Settings", about: "About" },
  la: { home: "Sedes", tools: "Opera", settings: "Mea", about: "Nuntia" },
  gr: { home: "Οἶκος", tools: "Τέχναι", settings: "Τάξις", about: "Μήνυμα" },
};
const TAB_LANG = { en: "en", la: "la", gr: "grc" };
// Majuscule: Greek capitals drop accents and breathings, as in inscriptions (ΟΙΚΟΣ).
const capitals = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().normalize("NFC");
function applyTabLabels() {
  const which = TAB_LABELS[state?.settings.labels] ? state.settings.labels : "en";
  const caps = state?.settings.labelCase === "caps";
  for (const b of document.querySelectorAll(".tabs button")) {
    const span = b.querySelector("span");
    if (span) span.textContent = caps ? capitals(TAB_LABELS[which][b.dataset.go]) : TAB_LABELS[which][b.dataset.go];
    b.lang = TAB_LANG[which];
  }
}

function applyTheme() {
  const t = state?.settings.theme;
  if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
  else delete document.documentElement.dataset.theme;
  applyTabLabels();
}

function renderSettings() {
  session = null;
  const s = state.settings;
  const mossCount = words.filter(w => w.m).length;
  const option = (name, value, label, hint) => `
    <label class="option">
      <input type="radio" name="${name}" value="${value}" ${s[name] === value ? "checked" : ""}>
      <span><b>${label}</b>${hint ? `<small>${hint}</small>` : ""}</span>
    </label>`;
  // Each setting is a one-line row showing its current choice; tap it to open its options. One open at a time.
  const section = (title, body) => `
      <details class="set" name="settings">
        <summary><span class="set-name">${title}</span><span class="set-value"></span><span class="set-chev" aria-hidden="true">›</span></summary>
        <div class="set-body">${body}</div>
      </details>`;
  app.innerHTML = `
    <section class="about settings-page">
      <h1>Settings</h1>
      <div class="sets">
      ${section("Answer mode", `
      <fieldset>
        <legend class="sr-only">Answer mode</legend>
        ${option("mode", "recall", "Manual", "Remember the meaning, show the answer, then mark ✓ (correct) or ✗ (incorrect).")}
        ${option("mode", "choice", "Multiple choice", "Pick the meaning from three choices. English → Greek cards are always multiple choice.")}
      </fieldset>
      <div class="subsection">
        <h3 class="sub">Timed advance</h3>
        <p class="hint">After a multiple-choice answer, go on by itself. An incorrect answer waits longer so you can read the correct one. Tapping anything on the card stops the timer.</p>
        <fieldset>
          <legend class="sr-only">Timed advance</legend>
          ${option("advance", "off", "Off", "Tap Continue or press Space.")}
          ${Object.entries(ADVANCE).map(([k, a]) => option("advance", k, a.label,
            `${a.right / 1000} sec. after a correct answer, ${a.wrong / 1000} sec. after an incorrect one.`)).join("")}
        </fieldset>
      </div>`)}

      ${section("Direction", `
      <fieldset>
        <legend class="sr-only">Direction</legend>
        ${option("direction", "ge", "Greek → English", "")}
        ${option("direction", "both", "Both", "New words start Greek → English. Once mastered, they also come English → Greek.")}
        ${option("direction", "eg", "English → Greek", "Only words you have mastered Greek → English; no new words.")}
      </fieldset>`)}

      ${section("Pace", `
      <fieldset>
        <legend class="sr-only">Pace</legend>
        ${Object.entries(PACE).map(([k, p]) => {
          const n = sessionsToFinish(p.n);
          const months = Math.round(n / 30.4);
          const span = months >= 12 ? `${Math.floor(months / 12)} year${months >= 24 ? "s" : ""}${months % 12 ? ` ${months % 12} month${months % 12 > 1 ? "s" : ""}` : ""}` : `${months} months`;
          return option("pace", k, p.label, `${p.n} new words per session; all ${words.length.toLocaleString()} in about ${n} sessions (${span} at one per day).`);
        }).join("")}
      </fieldset>`)}

      ${section("Appearance", `
      <fieldset>
        <legend class="sr-only">Theme</legend>
        ${option("theme", "system", "Match this device", "")}
        ${option("theme", "light", "Light", "")}
        ${option("theme", "dark", "Dark", "")}
      </fieldset>`)}

      ${section("Button labels", `
      <fieldset>
        <legend class="sr-only">Button labels</legend>
        ${option("labels", "en", "English", "Home, Tools, Settings, About")}
        ${option("labels", "la", "Latin", "Sedes, Opera, Mea, Nuntia")}
        ${option("labels", "gr", "Greek", '<span lang="grc">Οἶκος, Τέχναι, Τάξις, Μήνυμα</span>')}
      </fieldset>
      <div class="subsection">
        <fieldset>
          <legend class="sr-only">Letters</legend>
          ${option("labelCase", "normal", "Minuscule", 'Home, Sedes, <span lang="grc">Οἶκος</span>')}
          ${option("labelCase", "caps", "Majuscule", 'HOME, SEDES, <span lang="grc">ΟΙΚΟΣ</span>')}
        </fieldset>
      </div>`)}

      ${section("MossMethod", `
      <p class="hint">${mossCount} of Metzger's words are in the vocabulary of Moss's <i>First Greek Reader</i>, the reader MossMethod uses.</p>
      <fieldset>
        <legend class="sr-only">MossMethod</legend>
        ${option("moss", "no", "Not studied", "")}
        ${option("moss", "yes", "Studied", "Cards also show Moss's meaning, and Progress counts Moss's words as familiar.")}
      </fieldset>`)}
      </div>

      <h2>Progress</h2>
      ${progressHtml()}
      <p class="hint">Your progress is kept on this device. Time is counted from showing each card to answering it.</p>
      ${state.sessions ? `<h3 class="sub">Share progress</h3>
      <p class="hint">Send a friend or study partner a short summary: progress, number of sessions, streak.</p>
      <div class="row" style="margin-bottom:18px"><button class="quiet" id="share">Share progress</button></div>` : ""}
      <button class="quiet danger" id="reset">Erase all progress</button>
    </section>`;
  const settingValue = d => {
    d.querySelector(".set-value").textContent = d.querySelector("fieldset input:checked")?.closest("label").querySelector("b").textContent || "";
  };
  for (const d of app.querySelectorAll(".set")) {
    settingValue(d);
    d.ontoggle = () => { if (d.open) for (const o of app.querySelectorAll(".set[open]")) if (o !== d) o.open = false; };
  }
  for (const input of app.querySelectorAll("input[type=radio]")) {
    input.onchange = () => {
      s[input.name] = input.value; save(); applyTheme(); settingValue(input.closest(".set"));
      if (input.name === "moss") { // the Progress figures change with it
        const open = input.closest(".set");
        const tmp = document.createElement("div");
        tmp.innerHTML = progressHtml();
        app.querySelector(".progress-card").replaceWith(tmp.querySelector(".progress-card"));
        open.open = true;
      }
    };
  }
  const share = document.getElementById("share");
  if (share) share.onclick = () => shareProgress(share);
  document.getElementById("reset").onclick = () => {
    if (confirm("Erase all progress on this device? This can't be undone.")) {
      const keep = state.settings;
      localStorage.removeItem(STORE);
      state = load();
      state.settings = keep;
      save();
      setTab("home");
      renderHome();
    }
  };
}

function startSession() {
  const plan = sessionPlan();
  state.pending = { session: plan.number, newIds: plan.newIds };
  save();
  session = {
    number: plan.number,
    phase: "review",
    queue: shuffle(plan.review),
    fresh: [...plan.newIds],
    passed: new Set(),
    missed: new Set(),
    answers: 0,
    total: plan.review.length + plan.newIds.length,
  };
  if (!session.queue.length) startNewPhase();
  nextCard();
}

// New words: a "meet the word" card for each first, in path order, then the questions shuffled.
function startNewPhase() {
  session.phase = "new";
  const intros = session.fresh.filter(k => !isRev(k)).map(k => "@intro:" + k);
  session.queue = [...intros, ...shuffle(session.fresh)];
}

// Not graded: the word and its meaning, then Continue.
function renderIntro(id) {
  session.info = true;
  session.current = id;
  session.choices = null;
  const w = byId[id];
  app.innerHTML = `
    <div class="progress"><span>New words</span><span>${session.passed.size} of ${session.total} correct</span></div>
    <article class="card">
      <div class="meta">${esc(unitLabel(w))} · <span class="flag">meet the word</span></div>
      <div class="greek">${greekHtml(w)}</div>
      <div id="back"></div>
    </article>
    <div class="actions single"><button class="primary" id="continue">Continue</button></div>`;
  showBack();
  document.getElementById("continue").onclick = nextCard;
  document.getElementById("continue").focus();
}

function nextCard() {
  clearTimeout(advanceTimer);
  if (!session.queue.length && session.phase === "review") startNewPhase();
  const id = session.queue.shift();
  if (!id) return finishSession();
  session.slot = id;
  session.answered = false;
  keepSession();
  if (id.startsWith("@intro:")) return renderIntro(id.slice(7));
  session.info = false;
  session.current = id;
  session.revealed = false;
  session.shownAt = Date.now();
  session.choices = isRev(id) || state.settings.mode === "choice" ? makeChoices(id) : null;
  renderCard();
}

function renderCard() {
  const key = session.current;
  const rev = isRev(key);
  const w = byId[idOf(key)];
  const isNew = !state.cards[key];
  const spot = state.tally[key]?.retired;
  const choice = !!session.choices;
  const badge = spot ? "spot check" : isNew && !rev ? "new word" : "";
  app.innerHTML = `
    <div class="progress"><span>${session.phase === "review" ? "Review" : "New words"}</span><span>${session.passed.size} of ${session.total} correct</span></div>
    <article class="card">
      <div class="meta">${esc(unitLabel(w))}${rev ? ' · <span class="flag">English → Greek</span>' : ""}${badge ? ` · <span class="flag">${badge}</span>` : ""}</div>
      ${rev ? `<div class="prompt-en">${esc(w.g)}</div>` : `<div class="greek">${greekHtml(w)}</div>`}
      <div id="back"></div>
    </article>
    <div id="controls"></div>
    <div class="keys note">${choice ? "1–3 to choose · Space to continue" : "Space to reveal · 1 ✓ · 2 ✗"}</div>`;
  const controls = document.getElementById("controls");
  if (choice) {
    controls.innerHTML = `<div class="choices">${session.choices.map((c, i) =>
      `<button class="choice${rev ? " greek-choice" : ""}" data-i="${i}"><small class="note">${i + 1}</small><span>${rev ? greekHtml(byId[c.id]) : esc(c.english)}</span></button>`).join("")}</div>`;
    for (const b of controls.querySelectorAll(".choice")) b.onclick = () => choose(+b.dataset.i);
  } else {
    controls.innerHTML = `<div class="actions single"><button class="primary" id="reveal">Show answer</button></div>`;
    document.getElementById("reveal").onclick = reveal;
  }
}

// The answer: Metzger's gloss, his English derivative ("Cf. …"), Moss's gloss (Settings → MossMethod),
// the NT count, and the lexicon entry.
function showBack() {
  const id = idOf(session.current);
  const w = byId[id];
  const moss = mossOn() && w.m && w.mg && w.mg !== w.g;
  document.getElementById("back").innerHTML = `
    <div class="answer">
      ${isRev(session.current) ? `<p class="english answer-greek">${greekHtml(w)}</p>` : `<p class="english">${esc(w.g)}</p>`}
      ${w.d ? `<p class="cf">Cf. ${esc(w.d)}</p>` : ""}
      ${moss ? `<p class="moss-gloss"><b>Moss:</b> ${esc(w.mg)}</p>` : ""}
      <div class="count">${times(w.c)} in the New Testament${w.l !== id ? ` (as <span lang="grc">${esc(w.l)}</span>)` : ""}</div>
      <button class="quiet translate" id="lexlink">Lexicon entry</button>
    </div>`;
  document.getElementById("lexlink").onclick = () => openWord(id);
}

function reveal() {
  if (session.revealed || session.choices) return;
  session.revealed = true;
  showBack();
  document.getElementById("controls").innerHTML = `<div class="actions two">
      <button class="grade good" data-right="1" aria-label="Correct"><b class="mark">✓</b><small class="note">1</small></button>
      <button class="grade again" data-right="0" aria-label="Incorrect"><b class="mark">✗</b><small class="note">2</small></button>
    </div>`;
  for (const b of document.querySelectorAll(".grade")) b.onclick = () => { answer(b.dataset.right === "1"); nextCard(); };
}

function choose(i) {
  if (session.revealed || !session.choices) return;
  session.revealed = true;
  const right = session.choices[i].right;
  document.querySelectorAll(".choice").forEach((b, j) => {
    b.disabled = true;
    if (session.choices[j].right) b.classList.add("right");
    else if (j === i) b.classList.add("wrong");
  });
  answer(right);
  showBack();
  document.querySelector("#back .answer").insertAdjacentHTML("afterbegin",
    `<p class="verdict ${right ? "right" : "wrong"}">${right ? "✓ Correct" : "✗ Incorrect"}</p>`);
  document.getElementById("controls").insertAdjacentHTML("beforeend",
    `<div class="actions single"><button class="primary" id="continue">Continue</button></div>`);
  document.getElementById("continue").onclick = nextCard;
  document.getElementById("continue").focus();
  autoAdvance(document.getElementById("continue"), right);
}

function answer(right) {
  const id = session.current;
  const now = new Date();
  const wasNew = !state.cards[id];
  const t = state.tally[id] || (state.tally[id] = { correct: 0, last: 0, since: session.number, retired: false });
  if (wasNew) t.since = session.number;
  state.cards[id] = scheduler.next(state.cards[id] || createEmptyCard(now), now, right ? Rating.Good : Rating.Again).card;
  if (right) {
    // Counts toward mastery only if right on the first try this session, not in the session that
    // introduced the word, and not already counted today.
    const intro = t.since === session.number && !isRev(id);
    if (t.last !== session.number && !session.missed.has(id) && !intro && t.day !== today()) {
      t.correct++; t.last = session.number; t.day = today();
    }
    session.passed.add(id);
  } else {
    session.missed.add(id);
    t.correct = 0;
    if (t.retired) { t.retired = false; t.since = session.number; }
    session.queue.splice(Math.min(REQUEUE_GAP, session.queue.length), 0, id);
  }
  if (!state.studyDays.includes(today())) state.studyDays.push(today());
  if (session.shownAt) state.studyMs += Math.min(Date.now() - session.shownAt, 120000);
  session.answers++;
  session.answered = true;
  keepSession();
}

// Pause and resume: leaving a session keeps it; Home offers to resume it the same day.
function keepSession() {
  if (!session) return;
  state.paused = {
    day: today(), number: session.number, phase: session.phase, queue: session.queue, fresh: session.fresh,
    passed: [...session.passed], missed: [...session.missed], answers: session.answers, total: session.total,
    slot: session.slot, answered: !!session.answered,
  };
  save();
}

const pausedSession = () => state.paused?.day === today() && state.paused.number === state.sessions + 1 ? state.paused : null;

function resumeSession() {
  const p = pausedSession();
  if (!p) return startSession();
  session = { ...p, passed: new Set(p.passed), missed: new Set(p.missed) };
  if (!p.answered && p.slot) session.queue.unshift(p.slot);
  nextCard();
}

function finishSession() {
  state.sessions = session.number;
  delete state.pending;
  delete state.paused;
  retireOldest();
  save();
  const cov = coverage();
  app.innerHTML = `
    <div class="done">
      <h2>Session ${session.number} complete</h2>
      <p>${session.missed.size
          ? `${session.total - session.missed.size} of ${session.total} words correct on the first try;
             ${session.missed.size === 1 ? "1 word needed" : `${session.missed.size} words needed`} another try.`
          : `All ${session.total} words correct on the first try.`}
        You have mastered ${learnedIds().length} words, covering <b>${pct(cov)}%</b> of the New Testament.</p>
      <button class="primary" data-go="home">Back to overview</button>
    </div>`;
  session = null;
}

// ---------- Tools: Lexicon (Metzger's words with Souter's entries) and Readings (Nunn) ----------

async function renderTools() {
  session = null;
  acc = null;
  app.innerHTML = `<h1 class="tools-title">Tools</h1>${lexiconHtml()}
    <section class="about dialect-page tool" id="tool-accents">
      <h2>Diacriticals that change meaning</h2>
      <p class="lex-source">Words spelled alike except for an accent or breathing. Each card shows a verse of the
        New Testament: choose what the underlined word means. (An acute on the last syllable is written as a grave
        when another word follows: <span lang="grc">ἀλλά, ἀλλὰ</span>.)</p>
      <button class="primary" id="acc-quiz">Quiz</button>
      <div id="acc-list"></div>
    </section>
    <section class="about tool" id="tool-readings">
      <h2>Readings</h2>
      <p class="lex-source">Early Christian Greek beyond the New Testament, with H. P. V. Nunn's notes (1920), easiest first.</p>
      <div id="read-list"><p class="lex-more">Loading readings…</p></div>
    </section>`;
  wireLexicon();
  document.getElementById("acc-quiz").onclick = startAccentQuiz;
  loadAccents().then(() => {
    const el = document.getElementById("acc-list");
    if (el) el.innerHTML = accentListHtml();
  }).catch(() => {});
  try {
    await loadReadings();
    document.getElementById("read-list").innerHTML = readingsListHtml();
    document.getElementById("read-list").onclick = e => {
      const b = e.target.closest("[data-reading]");
      if (b) renderReading(b.dataset.reading);
    };
  } catch {
    const el = document.getElementById("read-list");
    if (el) el.innerHTML = `<p class="lex-more">The readings could not be loaded. Connect once to download them.</p>`;
  }
}

// Accent-, breathing- and case-insensitive; Latin letters are read as Greek ("logos" finds λόγος).
const LATIN = [["th", "θ"], ["ph", "φ"], ["ch", "χ"], ["kh", "χ"], ["ps", "ψ"], ["a", "α"], ["b", "β"], ["g", "γ"],
  ["d", "δ"], ["e", "ε"], ["z", "ζ"], ["h", ""], ["i", "ι"], ["k", "κ"], ["c", "κ"], ["l", "λ"], ["m", "μ"], ["n", "ν"],
  ["x", "ξ"], ["o", "ο"], ["p", "π"], ["r", "ρ"], ["s", "σ"], ["t", "τ"], ["u", "υ"], ["y", "υ"], ["f", "φ"], ["w", "ω"]];
function lexKey(s) {
  s = s.normalize("NFD").toLowerCase().replace(/[̀-ͯ]/g, "").replace(/ς/g, "σ");
  if (/[a-z]/.test(s)) for (const [l, g] of LATIN) s = s.split(l).join(g);
  return s.replace(/[^α-ω]/g, "");
}
const looseKey = k => k.replace(/η/g, "ε").replace(/ω/g, "ο");
// Search keys for each word: Metzger's forms ("ἐκ, ἐξ" gives ἐκ and ἐξ).
let searchKeys = null;
function buildSearchKeys() {
  searchKeys = words.map(w => {
    const parts = w.id.split(/,\s*/).map(lexKey).filter(Boolean);
    return { w, keys: parts, loose: parts.map(looseKey) };
  });
}

function lexiconHtml() {
  return `
    <section class="about lexica tool" id="tool-lexicon">
      <h2>Lexicon</h2>
      <p class="lex-source">Metzger, <i>Lexical Aids for Students of New Testament Greek</i> (1946), with Souter, <i>A Pocket Lexicon to the Greek New Testament</i> (1916)</p>
      <input id="lex-q" type="search" placeholder="Greek, Latin letters, English: λόγος, logos" autocomplete="off" autocapitalize="off" spellcheck="false">
      <div class="letters" aria-label="Greek keyboard">${"αβγδεζηθικλμνξοπρστυφχψω".split("").map(c => `<button data-letter="${c}" lang="grc">${c}</button>`).join("")}
        <button data-key="back" class="wide" aria-label="Delete last letter">⌫</button>
        <button data-key="clear" class="wide">Clear</button></div>
      <p class="lex-source">Accents and breathings aren't needed.</p>
      <div id="lex-results"></div>
    </section>`;
}

// One search result: the heading, then Metzger's gloss.
function entryPreview(w) {
  return `<b lang="grc">${esc(w.id)}</b> <span class="snip en-snip">${esc(w.g)}</span>`;
}

function searchWords(q) {
  q = q.trim();
  if (!q) return [];
  if (!searchKeys) buildSearchKeys();
  const latin = /[a-z]/i.test(q);
  const k = latin ? looseKey(lexKey(q)) : lexKey(q);
  const hits = [], seen = new Set();
  const push = w => { if (!seen.has(w)) { seen.add(w); hits.push(w); } };
  if (k) {
    const g = searchKeys.filter(s => (latin ? s.loose : s.keys).some(x => x.startsWith(k)));
    // closest to what was typed first, then the commonest
    const len = s => Math.min(...(latin ? s.loose : s.keys).filter(x => x.startsWith(k)).map(x => x.length));
    g.sort((a, b) => len(a) - len(b) || a.w.r - b.w.r).forEach(s => push(s.w));
  }
  if (latin) {
    const re = new RegExp(`\\b${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`, "i");
    const byRank = [...words].sort((a, b) => a.r - b.r);
    for (const w of byRank) if (re.test(w.g)) push(w);
    for (const w of byRank) if (re.test(w.mg)) push(w);
    for (const w of byRank) if (re.test(w.s)) push(w);
  }
  return hits;
}

function wireLexicon() {
  const input = document.getElementById("lex-q");
  const results = document.getElementById("lex-results");
  const show = q => {
    if (!q.trim()) { results.innerHTML = ""; return; }
    const hits = searchWords(q);
    results.innerHTML = hits.length
      ? `<ul class="lex-list">${hits.slice(0, 80).map(w => `<li><button data-form="${esc(w.id)}">${entryPreview(w)}</button></li>`).join("")}</ul>
         ${hits.length > 80 ? `<p class="lex-more">${hits.length - 80} more; type more letters to narrow the list.</p>` : ""}`
      : `<p class="lex-more">No word matches that.</p>`;
  };
  input.oninput = () => show(input.value);
  for (const b of app.querySelectorAll("[data-letter]")) b.onclick = () => { input.value += b.dataset.letter; show(input.value); };
  app.querySelector("[data-key=back]").onclick = () => { input.value = [...input.value].slice(0, -1).join(""); show(input.value); };
  app.querySelector("[data-key=clear]").onclick = () => { input.value = ""; show(""); input.focus(); };
  results.onclick = e => { const b = e.target.closest("[data-form]"); if (b) openWord(b.dataset.form); };
}

// The dialog that opens over whatever is on screen (Telamon's dialog#entry), so a session is not interrupted.
function openDialog(html) {
  let dlg = document.getElementById("entry");
  if (!dlg) {
    dlg = document.createElement("dialog");
    dlg.id = "entry";
    dlg.addEventListener("click", e => {
      if (e.target === dlg || e.target.closest("[data-close]")) return dlg.close();
      const f = e.target.closest("[data-form]");
      if (f) return openWord(f.dataset.form);
      const n = e.target.closest("[data-note]");
      if (n && reading) openNote(n.dataset.note);
    });
    dlg.addEventListener("close", () => app.querySelector(".reading-text .w.sel")?.classList.remove("sel"));
    document.body.append(dlg);
  }
  dlg.innerHTML = `<div class="entry-inner">${html}<button class="quiet" data-close>Close</button></div>`;
  if (!dlg.open) dlg.showModal();
  dlg.scrollTop = 0;
}

// A word's full entry: Metzger (gloss, derivative, count, root family), Moss, then Souter.
function openWord(form) {
  const w = byId[form];
  if (!w) return;
  const fam = w.f != null ? families[w.f] : null;
  const famHtml = fam ? `<p class="lex-meta">${fam.root ? `Root <span lang="grc">${esc(fam.root)}</span>` : "Family"}${fam.gloss ? `, ${esc(fam.gloss)}` : ""}:
      ${fam.members.filter(m => byId[m]).map(m => m === form ? `<b lang="grc">${esc(m)}</b>`
        : `<button class="link" data-form="${esc(m)}" lang="grc">${esc(m)}</button>`).join(", ")}</p>` : "";
  openDialog(`
    <h2 class="lex-head" lang="grc">${esc(w.id)}${w.gr ? `<span class="forms">, ${esc(w.gr)}</span>` : ""}</h2>
    <p class="lex-gloss">${esc(w.g)}</p>
    ${w.d ? `<p class="lex-meta">Cf. ${esc(w.d)}</p>` : ""}
    <p class="lex-meta">${times(w.c)} in the New Testament${w.l !== w.id ? ` (as <span lang="grc">${esc(w.l)}</span>)` : ""}${w.t ? ` · Metzger: ${esc(w.t.replace("Words Occurring ", "").toLowerCase())}` : ""}</p>
    ${famHtml}
    ${w.m && w.mg ? `<p class="lex-meta">Moss, <i>First Greek Reader</i>: ${esc(w.mg)}</p>` : ""}
    ${w.s ? `<h3 class="lex-sub">Souter</h3><div class="lex-body souter" lang="grc">${esc(w.s)}</div>` : ""}
    <p class="lex-source">Metzger, <i>Lexical Aids</i> (1946)${w.s ? "; Souter, <i>Pocket Lexicon</i> (1916), machine-read and still being proofread" : ""}</p>`);
}

// ---------- Readings (Nunn 1920, Appendix II) ----------

let readings = null, reading = null, noteNo = {};
async function loadReadings() {
  if (!readings) readings = await fetch("data/readings.json").then(r => r.json());
  return readings;
}
// Every word token of a reading, as its app key (Metzger form), "~lemma" or "".
const tokenKeys = r => r.paras.flatMap(p => p.p ? p.p.filter(Array.isArray).map(x => x[1].replace(/^\?/, "")) : []);
const plain = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/ς/g, "σ");
// Nunn's notes in this reading that mention the word (accents ignored).
function notesFor(r, surface) {
  const w = plain(surface).replace(/['’᾽]/g, "");
  if (w.length < 3) return [];
  return Object.entries(r.notes).filter(([, t]) => plain(t).split(/[^α-ω]+/).includes(w)).map(([id]) => id);
}
// Nunn marks his English renderings *thus*.
const noteHtml = t => esc(t).replace(/\*([^*]+)\*/g, "<i>$1</i>");

function readingsListHtml() {
  return `<ul class="lex-list read-list">${readings.map(r => {
    const keys = tokenKeys(r);
    const k = keys.filter(isLearned).length / keys.length;
    return `<li><button data-reading="${esc(r.slug)}"><b>${esc(r.title)}</b>
      <span class="snip">${esc(r.author)}${r.date ? ` · ${esc(r.date)}` : ""} · ${r.words.toLocaleString()} words · you know ${pct(k)}% · taught here ${Math.round(r.taught * 100)}%</span>
      <div class="meter" aria-hidden="true"><i style="width:${k * 100}%"></i></div></button></li>`;
  }).join("")}</ul>
  <p class="lex-source" style="margin-top:10px">Text and notes: Nunn, <i>A Short Syntax of New Testament Greek</i> (Cambridge, 1920), Appendix II.</p>`;
}

// One reading: tap a word for its gloss, or a raised number for Nunn's note. Words you have mastered are
// in ink; words in the app not yet mastered in the accent colour; words not in the app muted.
async function renderReading(slug) {
  await loadReadings();
  const r = readings.find(x => x.slug === slug);
  if (!r) return renderTools();
  reading = r;
  noteNo = Object.fromEntries(Object.keys(r.notes).map((id, i) => [id, i + 1]));
  const words = [];
  const body = r.paras.map(para => {
    if (para.h) return `<h3 class="sub">${esc(para.h)}</h3>`;
    return `<p class="reading-text" lang="grc">${para.p.map(x => {
      if (typeof x === "string") return esc(x);
      if (!Array.isArray(x)) return `<span class="nn" role="button" data-note="${esc(x.n)}">${noteNo[x.n]}</span>`;
      const [surface, raw] = x;
      const key = raw.replace(/^\?/, "");
      const cls = !byId[key] ? "out" : isLearned(key) ? "" : "learning";
      words.push([surface, raw]);
      return `<span class="w ${cls}" data-i="${words.length - 1}">${esc(surface)}</span>`;
    }).join("")}</p>`;
  }).join("");
  app.innerHTML = `
    <section class="about reading">
      <p class="read-head">${esc(r.author)}${r.date ? ` · ${esc(r.date)}` : ""} · Nunn, pp. ${r.pages[0]}–${r.pages[1]}</p>
      <h1 class="tools-title">${esc(r.title)}</h1>
      ${r.intro.map(t => `<p class="intro">${esc(t)}</p>`).join("")}
      <p class="legend">Colour key: <span class="known">mastered</span> · <span class="learning">in your course, not yet mastered</span> · <span class="out">not in Metzger's list</span>. Tap any word for its meaning.</p>
      ${body}
      <p class="lex-source">Text and notes: H. P. V. Nunn, <i>A Short Syntax of New Testament Greek</i> (1920). Numbers in the notes refer to sections of his Syntax.</p>
    </section>`;
  scrollTo(0, 0);
  app.querySelector(".reading").onclick = e => {
    const n = e.target.closest("[data-note]");
    if (n) return openNote(n.dataset.note);
    const s = e.target.closest(".reading-text .w");
    if (!s) return;
    app.querySelector(".reading-text .w.sel")?.classList.remove("sel");
    s.classList.add("sel");
    openReadingWord(...words[+s.dataset.i]);
  };
}

function openNote(id) {
  openDialog(`<p class="lex-source">Nunn's note ${noteNo[id]}</p>
    <div class="lex-body" lang="grc" style="margin-top:6px">${noteHtml(reading.notes[id])}</div>`);
}

function openReadingWord(surface, raw) {
  const guessed = raw.startsWith("?");
  const key = raw.replace(/^\?/, "");
  const w = byId[key];
  let html = `<h2 class="lex-head" lang="grc">${esc(surface)}</h2>`;
  if (w) {
    html += `<p class="lex-meta">${guessed ? "Probably from" : "From"} <span lang="grc">${esc(w.id)}</span>${w.gr ? `<span lang="grc">, ${esc(w.gr)}</span>` : ""}</p>
      <p class="lex-gloss">${esc(w.g)}</p>
      <p class="lex-meta">${times(w.c)} in the New Testament${isLearned(key) ? " · mastered" : state.cards[key] ? " · learning" : ""}</p>
      <button class="quiet go" data-form="${esc(w.id)}">Lexicon entry</button>`;
  } else if (key.startsWith("~")) {
    html += `<p class="lex-meta">${guessed ? "Probably from" : "From"} <span lang="grc">${esc(key.slice(1))}</span>, which is not in Metzger's list.</p>`;
  } else {
    html += `<p class="lex-meta">A rare word: not in Metzger's list.</p>`;
  }
  html += notesFor(reading, surface).slice(0, 2).map(id =>
    `<p class="lex-note" data-note="${esc(id)}" role="button"><b>Nunn ${noteNo[id]}:</b> <span lang="grc">${noteHtml(reading.notes[id])}</span></p>`).join("");
  openDialog(html);
}

// ---------- About ----------

// ---------- Diacriticals that change meaning (Tools) ----------
// Sets of words spelled alike but for accent or breathing (data/accents.json, built from MorphGNT by
// scripts/build_accents.py). The quiz shows a real NT verse with one member underlined; the choices are
// the meanings of the set's members. 20 cards; every set and member comes up, rare ones included.
const ACC_LENGTH = 20;
let accents = null, acc = null;
async function loadAccents() {
  if (!accents) accents = await fetch("data/accents.json").then(r => r.json());
  return accents;
}
const verseHtml = ex => ex.w.map((t, i) => i === ex.i ? `<strong>${esc(t)}</strong>` : esc(t)).join(" ");
function accentListHtml() {
  return `<details class="dia-all">
      <summary>Browse all ${accents.length} sets</summary>
      <div class="dia-list">${accents.map(a => `
        <details>
          <summary lang="grc">${esc(a.title)}</summary>
          <div class="dia-card">
            <p class="dia-body">${esc(a.note)}</p>
            <table class="dia-pairs"><tr><th>Word</th><th>Meaning</th><th>In the NT</th></tr>
              ${a.members.map(m => `<tr><td lang="grc">${esc(m.g)}</td><td class="ui">${esc(m.m)}</td><td class="ui">${times(m.count)}</td></tr>`).join("")}</table>
            ${a.members.filter(m => m.ex.length).map(m => `<p class="passage acc-ex" lang="grc">${verseHtml(m.ex[0])}</p>
              <p class="passage-ref">${esc(m.ex[0].ref)} · <span lang="grc">${esc(m.g)}</span>, ${esc(m.m)}</p>`).join("")}
          </div>
        </details>`).join("")}</div>
      <p class="lex-source">Verses: SBL Greek New Testament, parsed by MorphGNT (CC BY-SA).</p>
    </details>`;
}
async function startAccentQuiz() {
  await loadAccents();
  const deck = [], used = new Set();
  // Each round goes through every set once in random order, so all sets come up.
  while (deck.length < ACC_LENGTH) {
    for (const a of shuffle(accents.slice())) {
      if (deck.length >= ACC_LENGTH) break;
      const members = a.members.filter(m => m.ex.length);
      const m = members[Math.floor(Math.random() * members.length)];
      const fresh = m.ex.filter(e => !used.has(e.ref + e.i));
      const ex = (fresh.length ? fresh : m.ex)[Math.floor(Math.random() * (fresh.length || m.ex.length))];
      used.add(ex.ref + ex.i);
      deck.push({ set: a, member: m, ex });
    }
  }
  acc = { deck, n: 0, right: 0, answered: false };
  renderAccentCard();
}
function renderAccentCard() {
  const q = acc.deck[acc.n];
  acc.answered = false;
  acc.choices = q.set.members.filter(m => m.ex.length);
  app.innerHTML = `
    <div class="progress"><span>Diacriticals · ${acc.n + 1} of ${acc.deck.length}</span><span>${acc.right} correct</span></div>
    <article class="card acc-card">
      <div class="meta">What does the underlined word mean here?</div>
      <p class="passage acc-verse" lang="grc">${verseHtml(q.ex)}</p>
      <p class="passage-ref">${esc(q.ex.ref)}</p>
      <div id="acc-back"></div>
    </article>
    <div id="controls"><div class="choices">${acc.choices.map((m, i) =>
      `<button class="choice" data-i="${i}"><small class="note">${i + 1}</small><span>${esc(m.m)}</span></button>`).join("")}</div></div>
    <div class="keys note">1–${acc.choices.length} to choose · Space to continue</div>`;
  for (const b of document.querySelectorAll(".choice")) b.onclick = () => chooseAccent(+b.dataset.i);
}
function chooseAccent(i) {
  if (!acc || acc.answered) return;
  acc.answered = true;
  const q = acc.deck[acc.n];
  const right = acc.choices[i] === q.member;
  if (right) acc.right++;
  document.querySelectorAll(".choice").forEach((b, j) => {
    b.disabled = true;
    if (acc.choices[j] === q.member) b.classList.add("right");
    else if (j === i) b.classList.add("wrong");
  });
  document.getElementById("acc-back").innerHTML = `<div class="answer">
      <p class="verdict ${right ? "right" : "wrong"}">${right ? "✓ Correct" : "✗ Incorrect"}</p>
      <p class="english"><span lang="grc" class="answer-greek">${esc(q.member.g)}</span>, ${esc(q.member.m)}</p>
      <p class="dia-body">${esc(q.set.note)}</p>
    </div>`;
  document.querySelector(".progress span:last-child").textContent = `${acc.right} correct`;
  document.getElementById("controls").insertAdjacentHTML("beforeend",
    `<div class="actions single"><button class="primary" id="continue">Continue</button></div>`);
  document.getElementById("continue").onclick = nextAccent;
  document.getElementById("continue").focus();
}
function nextAccent() {
  if (!acc || !acc.answered) return;
  acc.n++;
  if (acc.n < acc.deck.length) return renderAccentCard();
  const { right, deck } = acc;
  acc = null;
  app.innerHTML = `<div class="done">
      <h2>Quiz complete</h2>
      <p>${right} of ${deck.length} correct.</p>
      <div class="row" style="justify-content:center">
        <button class="primary" id="acc-again">Another quiz</button>
        <button class="quiet" data-go="tools">Back to Tools</button>
      </div>
    </div>`;
  document.getElementById("acc-again").onclick = startAccentQuiz;
}
document.addEventListener("keydown", e => {
  if (!acc || e.target.closest?.("input, select, textarea") || document.getElementById("entry")?.open) return;
  if (!acc.answered && /^[1-9]$/.test(e.key) && +e.key <= acc.choices.length) chooseAccent(+e.key - 1);
  else if (acc.answered && (e.key === " " || e.key === "Enter")) { e.preventDefault(); nextAccent(); }
});

function renderAbout() {
  session = null;
  const link = (href, text) => `<a href="${href}" target="_blank" rel="noopener">${text}</a>`;
  const cc = link("https://creativecommons.org/licenses/by-sa/3.0/", "CC BY-SA 3.0");
  app.innerHTML = `
    <section class="about">
      <h1>About</h1>
      <p><b>NT Greek: The New Testament Vocabulary Trainer.</b> The name is a working title.</p>
      <p class="version">Version ${esc(APP_VERSION)}${meta.built ? ` · word data built ${esc(meta.built)}` : ""}</p>

      <h2>How sessions work</h2>
      <p>Each training session starts with the words learned so far. Once those are answered correctly, new words are added:
        ${newPerSession()} per session at your pace (Settings → Pace).
        A word is counted as mastered once you've answered it correctly on the first try in ${SESSIONS_TO_LEARN} consecutive
        sessions on ${SESSIONS_TO_LEARN} different days, after the session where you first met it. A wrong answer starts the count again.
        Mastered words return at regular intervals for review.
        If you choose Both or English → Greek in Settings → Direction, mastered words are also asked in reverse: you see the English and pick the Greek.
        A word is considered mastered English to Greek on the same terms.</p>

      <h3 class="sub">The approach</h3>
      <p><b>Most frequent first.</b> Metzger listed the words that occur ten times or more in the New Testament,
        commonest first. A few hundred common words make up most of every page, so each word you master
        covers as much of the text as possible.</p>
      <p><b>Then by root families.</b> Metzger's second part groups words by their roots. Here the families are
        woven into the frequency lists: when a common word comes up, its relatives follow, so a new word is learned
        alongside the words from which it is built.</p>
      <p><b>With an English cognate.</b> Where Metzger gives one, an English derivative or memory aid comes with
        the meaning ("Cf. apostasy").</p>
      <p><b>Recall, not rereading.</b> After a first look at a new word, you are asked for its meaning
        before you see it. Retrieving a word from memory fixes it far better than looking at it again.</p>
      <p><b>Spaced over days.</b> A word counts as mastered only when you have recalled it at the first
        attempt on ${SESSIONS_TO_LEARN} separate days in a row. After that it returns at growing intervals, timed to come
        back just before you would forget it.</p>
      <p><b>Review before new.</b> New words wait until the session's review is done, and a missed word
        comes back a few cards later until you get it right, so gaps are filled before more is added.</p>
      <p><b>Recognition, then production.</b> Reading asks you to know what a Greek word means. Once that is
        secure, English → Greek asks you to find the Greek word yourself.</p>

      <h2>Credits</h2>
      <p>Scheduling: ${link("https://github.com/open-spaced-repetition/ts-fsrs", "ts-fsrs")} 5.4.2, MIT License.
        Fonts: Vollkorn (Friedrich Althausen) and Inter (Rasmus Andersson), SIL Open Font License.</p>

      <h2>Privacy</h2>
      <p>Your progress stays on this device; the app has no accounts, advertising or tracking.</p>

      <h2>Sources</h2>
      <dl>
        <dt>Word list, learning order, glosses and English derivatives</dt>
        <dd>Bruce M. Metzger, <i>Lexical Aids for Students of New Testament Greek</i> (Princeton, 1946). Public domain.</dd>
        <dt>Lexicon</dt>
        <dd>Alexander Souter, <i>A Pocket Lexicon to the Greek New Testament</i> (Oxford, 1916). Public domain.
          The text is machine-read from the 1917 printing and is still being proofread.</dd>
        <dt>MossMethod meanings</dt>
        <dd>Charles Melville Moss, <i>A First Greek Reader, with Notes and Vocabulary</i>, revised edition (Boston, 1893), Vocabulary. Public domain.</dd>
        <dt>Word counts</dt>
        <dd>${link("https://github.com/morphgnt/sblgnt", "MorphGNT")} SBLGNT, licensed ${cc}; the counts drawn from it are
          shared under the same license.</dd>
        <dt>Readings</dt>
        <dd>H. P. V. Nunn, <i>A Short Syntax of New Testament Greek</i> (Cambridge, 1920), Appendix II: texts and notes. Public domain.</dd>
      </dl>
    </section>`;
}

// ---------- events ----------

function setTab(go) {
  for (const b of document.querySelectorAll(".tabs button")) {
    if (b.dataset.go === go) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current");
  }
}

document.addEventListener("click", e => {
  const go = e.target.closest("[data-go]")?.dataset.go;
  if (!go) return;
  setTab(go);
  reading = null;
  acc = null;
  if (go === "home") renderHome();
  else if (go === "about") renderAbout();
  else if (go === "settings") renderSettings();
  else if (go === "tools") renderTools();
});

document.addEventListener("keydown", e => {
  if (!session || e.target.closest?.("input, select, textarea") || document.getElementById("entry")?.open) return;
  if (session.info) {
    if (e.key === " " || e.key === "Enter") { e.preventDefault(); nextCard(); }
    return;
  }
  if (session.choices) {
    if (!session.revealed && /^[1-9]$/.test(e.key) && +e.key <= session.choices.length) choose(+e.key - 1);
    else if (session.revealed && (e.key === " " || e.key === "Enter")) { e.preventDefault(); nextCard(); }
    return;
  }
  if (!session.revealed && (e.key === " " || e.key === "Enter")) { e.preventDefault(); reveal(); }
  else if (session.revealed && (e.key === "1" || e.key === "2")) { answer(e.key === "1"); nextCard(); }
});

// ---------- boot ----------

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
navigator.storage?.persist?.().catch(() => {});

(async () => {
  try {
    const lex = await fetch("data/lexicon.json").then(r => r.json());
    meta = lex.meta;
    for (const f of lex.families) families[f.id] = f;
    // The path: units in order, each word once, where it first appears.
    for (const u of lex.units) for (const form of u.words) {
      if (unitOf[form] || !lex.words[form]) continue;
      unitOf[form] = u;
      const w = { id: form, ...lex.words[form] };
      words.push(w);
      byId[form] = w;
    }
    maxCoverage = tokenShare(words.map(w => w.id));
    state = load();
    applyTheme();
    renderHome();
  } catch (err) {
    app.innerHTML = `<p class="loading">Could not load the word data (${esc(err.message)}). Serve this folder over http rather than opening the file directly.</p>`;
  }
})();
