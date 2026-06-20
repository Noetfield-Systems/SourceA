#!/usr/bin/env bash
# validate-app-js-lazy-bootstrap-v1.sh — sa-0801 / sa-0851 legacy app.js lazy bootstrap
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-command-data-lazy-shell-v1.sh

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
app = root / "agent-control-panel" / "assets" / "app.js"
text = app.read_text(encoding="utf-8")

required = [
    ("__COMMAND_DATA_LAZY", "lazy flag referenced"),
    ("loadCommandDataShell", "shell bootstrap fn"),
    ("command-data-shell.json", "shell fetch path"),
    ("loadCommandDataFull", "deferred full load fn"),
    ("command-data.json", "full payload fetch path"),
    ("tabNeedsFullLoad", "heavy tab gate"),
    ("HEAVY_TAB_KEYS", "heavy tab map"),
    ("scheduleIdleFullPrefetch", "idle prefetch hook"),
]
for needle, label in required:
    assert needle in text, f"app.js missing {label}: {needle}"

assert "no idle 9MB prefetch" in text or "HUB-LITE Phase 0.1" in text, (
    "scheduleIdleFullPrefetch must be noop (no idle 9MB prefetch)"
)

# Boot must not eagerly fetch full command-data before shell path
boot_idx = text.find("await loadCommandData()")
full_idx = text.find("async function loadCommandDataFull()")
shell_idx = text.find("async function loadCommandDataShell()")
assert shell_idx > 0 and full_idx > 0, "bootstrap functions missing"
assert "return loadCommandDataShell()" in text, "loadCommandData must default to shell"

# loadCommandDataShell sets lazy true; full load clears it
assert "window.__COMMAND_DATA_LAZY = true" in text, "shell load must set __COMMAND_DATA_LAZY true"
assert "window.__COMMAND_DATA_LAZY = false" in text, "full load must clear __COMMAND_DATA_LAZY"

print("OK: validate-app-js-lazy-bootstrap-v1 · legacy app.js lazy bootstrap contract (sa-0851)")
PY
