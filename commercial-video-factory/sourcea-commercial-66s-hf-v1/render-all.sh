#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Installing bundled ffmpeg + ffprobe..."
npm install ffmpeg-static@5.2.0 ffprobe-static@3.1.0 --no-save

# ffmpeg-static downloads the binary via postinstall — run explicitly if missing
if [[ ! -f node_modules/ffmpeg-static/ffmpeg ]]; then
  echo "Downloading ffmpeg binary..."
  node node_modules/ffmpeg-static/install.js
fi

mkdir -p .bin
FFMPEG_BIN="$(node --input-type=commonjs -e "console.log(require('ffmpeg-static'))")"
FFPROBE_BIN="$(node --input-type=commonjs -e "console.log(require('ffprobe-static').path)")"
ln -sf "$FFMPEG_BIN" .bin/ffmpeg
ln -sf "$FFPROBE_BIN" .bin/ffprobe
export PATH="$(pwd)/.bin:$PATH"

if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
  echo "FAIL: bundled ffmpeg/ffprobe not on PATH"
  echo "  ffmpeg:  ${FFMPEG_BIN:-missing}"
  echo "  ffprobe: ${FFPROBE_BIN:-missing}"
  exit 1
fi

echo "Using ffmpeg: $(command -v ffmpeg)"
echo "Using ffprobe: $(command -v ffprobe)"

npx hyperframes@0.7.4 render -o renders/SourceA-Commercial-Fast-23s-v1.mp4 -q standard --fps 30
