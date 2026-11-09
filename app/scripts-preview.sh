#!/usr/bin/env bash
# Build the web preview for artifact hosting.
# The host reserves paths beginning with "_" and serves the page from a versioned
# subfolder (/_f/<version>/), so:
#  - move Expo's /_expo/ folder to expo-static/;
#  - load the entry scripts by relative path;
#  - in the bundles, prefix chunk and asset paths with the folder the page was
#    served from (globalThis.__B, set in index.html), since the router later
#    rewrites the address bar to "/" and relative paths would then break.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf dist
npx expo export --platform web --output-dir dist
mv dist/_expo dist/expo-static
sed -i 's#src="/_expo/#src="expo-static/#g; s#href="/favicon.ico"#href="favicon.ico"#g' dist/index.html
sed -i 's#<head>#<head><script>globalThis.__B=location.pathname.replace(/[^/]*$/,"");</script>#' dist/index.html
find dist/expo-static -name '*.js' -print0 | xargs -0 sed -i \
  -e 's#"/_expo/#(globalThis.__B||"/")+"expo-static/#g' \
  -e 's#"/assets/#(globalThis.__B||"/")+"assets/#g'
! grep -rq '"/_expo/' dist
