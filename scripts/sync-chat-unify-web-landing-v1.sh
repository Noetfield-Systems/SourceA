#!/usr/bin/env bash
# Sync Chat Unify standalone UI → green-unified/unify/ and /unify-demo/ for sourcea.app
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/scripts/chat-unify-standalone"
GREEN="$ROOT/sites/SourceA-landing/green-unified"
TARGET="${1:-all}"

sync_one() {
  local name="$1"
  local dest="$GREEN/$name"
  mkdir -p "$dest"
  if [[ "$name" == "unify-demo" ]]; then
    rm -rf "$dest/terminal"
    rsync -a --delete \
      --exclude '.DS_Store' \
      --exclude 'terminal/' \
      "$SRC/" "$dest/"
  else
    rsync -a --delete \
      --exclude '.DS_Store' \
      "$SRC/" "$dest/"
  fi
  echo "✓ synced → $dest"
}

if [[ ! -f "$SRC/index.html" ]]; then
  echo "FAIL: missing $SRC/index.html" >&2
  exit 1
fi

case "$TARGET" in
  unify) sync_one unify ;;
  unify-demo) sync_one unify-demo ;;
  all)
    sync_one unify
    sync_one unify-demo
    ;;
  *)
    echo "Usage: $0 [unify|unify-demo|all]" >&2
    exit 1
    ;;
esac

export SINA_SOURCE_A="$ROOT"
python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SINA_SOURCE_A"])
green = root / "sites" / "SourceA-landing" / "green-unified"
src = root / "scripts" / "chat-unify-standalone"
ver = "unknown"
index = src / "index.html"
if index.is_file():
    for line in index.read_text(encoding="utf-8").splitlines():
        if "chat-unify-ui-version" in line and "content=" in line:
            ver = line.split('content="', 1)[1].split('"', 1)[0]
            break
rows = []
for name, url in (("unify", "https://sourcea.app/unify/"), ("unify-demo", "https://sourcea.app/unify-demo/")):
    dest = green / name
    if not dest.is_dir():
        continue
    rows.append({
        "target": name,
        "dest": str(dest),
        "ui_version": ver,
        "public_url": url,
        "file_count": sum(1 for p in dest.rglob("*") if p.is_file()),
        "has_terminal": (dest / "terminal" / "terminal.js").is_file(),
    })
receipt = {
    "schema": "chat-unify-web-sync-receipt-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "ui_version": ver,
    "targets": rows,
}
out = Path.home() / ".sina" / "chat-unify-web-sync-receipt-v1.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt))
PY
