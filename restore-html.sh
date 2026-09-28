#!/bin/sh
set -e
cd "$(dirname "$0")"
if [ -f requirement_scratch.html.gz.b64 ]; then
  base64 -d requirement_scratch.html.gz.b64 | gzip -d > requirement_scratch.html
elif [ -f requirement_scratch.html.gz.b64.part1 ] && [ -f requirement_scratch.html.gz.b64.part2 ]; then
  cat requirement_scratch.html.gz.b64.part1 requirement_scratch.html.gz.b64.part2 | base64 -d | gzip -d > requirement_scratch.html
else
  echo "Missing requirement_scratch.html.gz.b64 (or .part1/.part2)" >&2
  exit 1
fi
echo "Restored requirement_scratch.html ($(wc -c < requirement_scratch.html) bytes)"
