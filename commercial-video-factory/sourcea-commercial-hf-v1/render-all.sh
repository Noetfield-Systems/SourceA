#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "Installing bundled ffmpeg + ffprobe..."
npm install ffmpeg-static@5.2.0 ffprobe-static@3.1.0 --no-save

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
  exit 1
fi

echo "Using ffmpeg: $(command -v ffmpeg)"

npx hyperframes@0.7.4 render -o renders/sourcea-commercial-v1.mp4 -q standard --fps 30
npx hyperframes@0.7.4 render -c compositions/sourcea-sting-v1.html -o renders/sourcea-sting-v1.mp4 -q standard --fps 30
