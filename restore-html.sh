#!/bin/sh
set -e
cd "$(dirname "$0")"
if [ -f requirement_scratch.html.part0 ] && [ -f requirement_scratch.html.part1 ] && [ -f requirement_scratch.html.part2 ]; then
  cat requirement_scratch.html.part0 requirement_scratch.html.part1 requirement_scratch.html.part2 > requirement_scratch.html
  echo "Joined requirement_scratch.html ($(wc -c < requirement_scratch.html) bytes)"
elif [ -f requirement_scratch.html.gz.b64 ]; then
  base64 -d requirement_scratch.html.gz.b64 | gzip -d > requirement_scratch.html
  echo "Decompressed requirement_scratch.html ($(wc -c < requirement_scratch.html) bytes)"
else
  echo "Missing HTML parts or .gz.b64" >&2
  exit 1
fi
