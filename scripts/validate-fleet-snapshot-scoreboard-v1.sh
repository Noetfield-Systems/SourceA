#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

from agent_essay_discourse import essay_discourse_payload
from agent_scoreboard import scoreboard_payload

snap_path = Path.home() / ".sina" / "fleet_build_snapshot_v1.json"
assert snap_path.is_file(), "fleet_build_snapshot_v1.json missing — run build first"
snap = json.loads(snap_path.read_text(encoding="utf-8"))
sb = scoreboard_payload()
ed = essay_discourse_payload()
assert sb.get("ok"), sb

pairs = [
    ("reported_count", snap.get("reported_count"), sb.get("reported_count")),
    ("agent_count", snap.get("agent_count"), sb.get("agent_count")),
    ("fleet_auto_green_count", snap.get("fleet_auto_green_count"), sb.get("fleet_auto_green_count")),
    ("nudge_count", snap.get("nudge_count"), ed.get("nudge_count")),
    ("fleet_report_gap", sorted(snap.get("fleet_report_gap") or []), sorted(sb.get("fleet_report_gap") or [])),
    ("fleet_verify_gap", sorted(snap.get("fleet_verify_gap") or []), sorted(sb.get("fleet_verify_gap") or [])),
]
errors = [f"{name}: snapshot={a!r} live={b!r}" for name, a, b in pairs if a != b]
assert not errors, "fleet snapshot drift: " + "; ".join(errors)
print(
    "OK: validate-fleet-snapshot-scoreboard-v1 · "
    f"reports {sb.get('reported_count')}/{sb.get('agent_count')} · "
    f"auto-green {sb.get('fleet_auto_green_count')} · nudges {ed.get('nudge_count')}"
)
PY
