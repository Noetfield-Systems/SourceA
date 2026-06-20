#!/usr/bin/env bash
# validate-program-progress-factory-divergence-v1.sh — sa-0974 ACT two-speed clock crosswalk
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-program-progress-build-sync-v1.sh

python3 - <<'PY'
import json
from pathlib import Path

from registry_honest_lib_v1 import audit_registry_done

root = Path(__file__).resolve().parents[1]
prog = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))

# Machine sync markers — manual ASF JSON edit would break updated_by contract
updated_by = prog.get("updated_by") or ""
assert updated_by == "update-program-progress.py", (
    f"PROGRAM_PROGRESS must be machine-synced, got updated_by={updated_by!r}"
)
synced = (prog.get("signals_auto") or {}).get("synced_at")
assert synced, "signals_auto.synced_at missing — manual edit or stale build"

audit = audit_registry_done()
unproven = int(audit.get("unproven_done") or 0)
honest = int(audit.get("honest_done") or 0)
total = int(audit.get("total") or 1000)
assert unproven == 0, f"manual/fake REGISTRY done rows: {unproven}"

factory_pct = round(100.0 * honest / total, 1) if total else 0.0
p0_id = (prog.get("locks") or {}).get("founder_p0_id") or ""

# Strategic clock may show 100% on parallel rows while factory is ~65% — document, don't fail
parallel = prog.get("parallel_plans") or []
high_pct = [p for p in parallel if isinstance(p.get("progress_pct"), (int, float)) and p["progress_pct"] >= 90]
divergence_note = (
    f"Clock A parallel rows at ≥90%: {len(high_pct)} · "
    f"Clock B factory honest: {honest}/{total} ({factory_pct}%)"
)

law = root / "ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md"
assert law.is_file(), "ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md missing"

inc = root / "brain-os" / "incidents" / "SINA_AGENT_PLAN_TODO_GHOST_REACTIVATION_INCIDENT_016_LOCKED_v1.md"
assert inc.is_file(), "INCIDENT-016 missing"

print(
    "OK: validate-program-progress-factory-divergence-v1 · "
    f"p0={p0_id} synced_at={synced[:19]} · "
    f"factory={honest}/{total} unproven=0 · {divergence_note} · sa-0974"
)
PY
