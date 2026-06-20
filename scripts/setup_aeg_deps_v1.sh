#!/usr/bin/env bash
# Install AEG capture deps — asciinema (terminal .cast) + Playwright (UI png/webm).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
RECEIPT="${SINA}/aeg-deps-receipt-v1.json"

say() { printf '%s\n' "$*"; }

asciinema_ok=false
playwright_ok=false
asciinema_path=""
playwright_path=""

if command -v asciinema >/dev/null 2>&1; then
  asciinema_ok=true
  asciinema_path="$(command -v asciinema)"
else
  say "Installing asciinema (brew)..."
  if command -v brew >/dev/null 2>&1; then
    brew install asciinema
    asciinema_ok=true
    asciinema_path="$(command -v asciinema)"
  else
    say "WARN: brew missing — terminal capture will use transcript fallback"
  fi
fi

if python3 -c "import playwright" 2>/dev/null; then
  playwright_ok=true
else
  say "Installing playwright (pip)..."
  python3 -m pip install --user playwright
  playwright_ok=true
fi

if python3 -c "import playwright" 2>/dev/null; then
  say "Installing Chromium for Playwright..."
  python3 -m playwright install chromium
  playwright_path="$(python3 -c "import playwright; print(playwright.__file__)")"
fi

mkdir -p "$SINA"
python3 -c "
import json
from pathlib import Path
from datetime import datetime, timezone
r = {
  'schema': 'aeg-deps-receipt-v1',
  'at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
  'asciinema': '$asciinema_ok',
  'asciinema_path': '$asciinema_path',
  'playwright': '$playwright_ok',
  'playwright_path': '$playwright_path',
}
Path('$RECEIPT').write_text(json.dumps(r, indent=2) + '\n')
"

say "PASS: setup_aeg_deps_v1"
say "  asciinema: ${asciinema_ok} (${asciinema_path:-missing})"
say "  playwright: ${playwright_ok}"
say "  receipt: ${RECEIPT}"
