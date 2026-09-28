#!/bin/sh
set -e
cd "$(dirname "$0")"
base64 -d requirement_scratch.html.gz.b64 | gzip -d > requirement_scratch.html
echo "Restored requirement_scratch.html ($(wc -c < requirement_scratch.html) bytes)"
