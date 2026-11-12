// Offline support (as Telamon's sw.js): every file the app needs is cached on first visit.
// Own files are network-first, so edits show up whenever the server is reachable and the
// cached copy is used when it isn't. Google Fonts are cache-first (they never change).
// Paths are relative, so the app also works from a subfolder. Bump VERSION when the file list changes.
const VERSION = "ntgreek-v53";
const FONTS = "ntgreek-fonts-v1";
const SHELL = [
  "./",
  "index.html",
  "style.css",
  "app.js",
  "vendor/ts-fsrs-5.4.2/index.mjs",
  "data/lexicon.json",
  "data/readings.json",
  "data/accents.json",
  "data/translations.json",
  "data/audio.json",
  "data/blass24.json",
  "manifest.webmanifest",
  "icons/favicon.svg",
  "icons/mark.svg",
  "icons/icon-192.png",
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith("ntgreek-") && k !== VERSION && k !== FONTS).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    e.respondWith(
      // no-cache: revalidate with the server so a rebuilt data file is never served stale.
      fetch(req.url, { cache: "no-cache" })
        .then(res => {
          if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
          return res;
        })
        .catch(() => caches.match(req, { ignoreSearch: true }))
    );
  } else if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        const copy = res.clone();
        caches.open(FONTS).then(c => c.put(req, copy));
        return res;
      }))
    );
  }
});
