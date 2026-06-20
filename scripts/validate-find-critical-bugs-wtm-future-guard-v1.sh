#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

src = Path("find_critical_bugs.py").read_text(encoding="utf-8")
assert "_check_wtm_future_column" in src, "WTM future guard helper missing"
assert "sa-0224" in src, "sa-0224 marker missing"
assert "hub_up" in src or "hub_up:" in src, "hub-up conditional missing"
assert '/api/system-roadmap' in src, "system-roadmap probe missing"
print("OK: validate-find-critical-bugs-wtm-future-guard-v1 · helper wired when hub up")
PY
