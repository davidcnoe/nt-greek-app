#!/usr/bin/env bash
# Build the web preview for artifact hosting, which reserves paths beginning with "_":
# move Expo's /_expo/ folder to /expo-static/ and rewrite every reference to it.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf dist
npx expo export --platform web --output-dir dist
mv dist/_expo dist/expo-static
grep -rl "_expo/" dist | xargs sed -i 's#/_expo/#/expo-static/#g; s#"_expo/#"expo-static/#g'
