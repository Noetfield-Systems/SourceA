#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from founder_request_tracker import sync_shipped_from_disk

src = Path("founder_request_tracker.py").read_text(encoding="utf-8")
assert "sa-0310" in src or "sa-0310–0312" in src, "sa-0310 marker missing"
assert "FR-2026-06-05-007" in src and "FR-2026-06-05-010" in src and "FR-2026-06-05-011" in src, (
    "FR-007/010/011 sync missing"
)
assert "FR-2026-06-05-008" in src, "FR-008 nudge rule missing"
assert "FR-2026-06-05-009" in src and "auto_pass_count" in src, "FR-009 auto_pass rule missing"

out = sync_shipped_from_disk()
assert out.get("ok"), out
print(f"OK: validate-founder-request-fleet-sync-v1 · synced {out.get('count', 0)} rows (sa-0310–0312)")
PY
