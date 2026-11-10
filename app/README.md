# Tertius: The NT Greek Vocab Trainer (Expo app)

The store app for iOS and Android, and its web build. Since 2026-11-09 (David's choice) it **wraps the
prototype**: the whole app is `../prototype/`, built into one offline page and shown full screen, so every
change to the prototype carries over and there is one codebase.

## How it fits together

- `scripts/build-embed.mjs` bundles the prototype (app.js with ts-fsrs, style.css, the data files, the logo,
  and the fonts: Vollkorn, Inter, and Gentium Plus for accented Greek) into one page, with nothing loaded
  from the network. It writes `src/embedded/page.ts` (the page as a string; generated, do not edit) and
  `src/embedded/page.html` (the same page, for opening in a browser to check).
- `src/embedded/TertiusView.tsx` (iOS, Android) shows the page in a web view
  ([react-native-webview](https://github.com/react-native-webview/react-native-webview)):
  - **Progress** is saved by the page and also handed to the app, which keeps a copy in AsyncStorage and
    puts it back into the page at start, so it survives if the system clears the web view's storage.
  - **Outside links** open in the phone's browser.
  - **Safe areas**: the page runs edge to edge and pads its own header and bottom bar by the device's
    insets (CSS `--safe-top`, `--safe-bottom`); it reports its theme so the status bar stays legible.
- `src/embedded/TertiusView.web.tsx` (web) shows the page in a full-window iframe.
- The page knows it is inside the app by `window.__TERTIUS` (see `EMBED` in `../prototype/app.js`).

## After changing the prototype

    node scripts/build-embed.mjs     # rebuild the page; commit src/embedded/page.ts
    npx tsc --noEmit                 # typecheck

## Run and build

    npm install
    npx expo start                   # a development build is needed: react-native-webview is native code
    ./scripts-preview.sh             # web export to dist/ (artifact hosting reserves "_" paths)
    npx eas-cli@latest build         # store builds, in the cloud

Bundle identifiers are `com.latinperdiem.tertius` (iOS and Android); they are fixed once an app is
published, so confirm before the first store build.

## Still to do

- **Audio**: when the headword recordings exist, ship them with the app and let the page play them through
  `window.__TERTIUS.audioUrl(key)` (the hook is in place; the files are not yet bundled).
- Test on a real iPhone and Android phone (development build or TestFlight / internal testing).
