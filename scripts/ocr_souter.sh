#!/usr/bin/env bash
# OCR one page range of the Souter scan into data/souter/ocr/page-NNN.txt.
# Usage: scripts/ocr_souter.sh FIRST LAST   (needs tesseract with grc + eng models in $TESSDATA_PREFIX)
set -euo pipefail
cd "$(dirname "$0")/.."
PDF=source/souter-pocket-lexicon-1917-textkit.pdf
OUT=data/souter/ocr
TMP=$(mktemp -d)
seq "$1" "$2" | xargs -P "$(nproc)" -I{} bash -c '
  n=$(printf "%03d" {})
  [ -s "'"$OUT"'/page-$n.txt" ] && exit 0
  pdftoppm -f {} -l {} -r 300 -gray "'"$PDF"'" "'"$TMP"'/p$n"
  tesseract "'"$TMP"'"/p$n*.pgm "'"$OUT"'/page-$n" -l grc+eng --psm 4 >/dev/null 2>&1
  rm -f "'"$TMP"'"/p$n*.pgm
'
rmdir "$TMP" 2>/dev/null || true
