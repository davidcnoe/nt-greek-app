#!/usr/bin/env bash
# OCR one page range of the Souter scan into data/souter/ocr/page-NNN.txt (text)
# and data/souter/tsv/page-NNN.tsv (word positions, used to find hanging indents).
# Usage: scripts/ocr_souter.sh FIRST LAST   (needs tesseract with grc + eng models in $TESSDATA_PREFIX)
set -euo pipefail
cd "$(dirname "$0")/.."
PDF=source/souter-pocket-lexicon-1917-textkit.pdf
mkdir -p data/souter/ocr data/souter/tsv
TMP=$(mktemp -d)
export PDF TMP
seq "$1" "$2" | xargs -P "$(nproc)" -I{} bash -c '
  n=$(printf "%03d" {})
  [ -s "data/souter/ocr/page-$n.txt" ] && [ -s "data/souter/tsv/page-$n.tsv" ] && exit 0
  pdftoppm -f {} -l {} -r 300 -gray "$PDF" "$TMP/p$n"
  tesseract "$TMP"/p$n*.pgm "$TMP/page-$n" -l grc+eng --psm 4 \
    -c tessedit_create_txt=1 -c tessedit_create_tsv=1 >/dev/null 2>&1
  mv "$TMP/page-$n.txt" data/souter/ocr/
  mv "$TMP/page-$n.tsv" data/souter/tsv/
  rm -f "$TMP"/p$n*.pgm
'
rmdir "$TMP" 2>/dev/null || true
