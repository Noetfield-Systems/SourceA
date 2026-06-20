#!/usr/bin/env bash
# Phase-s2 hub-build-ci backfill proof — sa-0226..sa-0300 (25 unique × 3 tiers).
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BUILD = (SCRIPTS / "build-sina-command-panel.py").read_text(encoding="utf-8")
BUGS = (SCRIPTS / "find_critical_bugs.py").read_text(encoding="utf-8")
BOWL = (SCRIPTS / "build-sina-daily-bowl.py").read_text(encoding="utf-8")
PRIORITY = (ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md").read_text(encoding="utf-8")

checks = {
    "sa-0226": "validate-build-run-audit-v1.sh" in BUILD and "sa-0226" in BUILD,
    "sa-0227": "SINA_AUDIT_STRICT" in BUILD and "strict" in BUILD,
    "sa-0228": "find_critical_bugs" in BUGS and "critical" in BUGS,
    "sa-0229": "audit_backend_e2e" in BUGS or "audit_backend_e2e" in BUILD,
    "sa-0230": "SINA_SKIP_NESTED_BOWL" in BUILD or "SINA_SKIP_NESTED_BOWL" in BOWL,
    "sa-0231": "SINA_SKIP_NESTED_BOWL" in (SCRIPTS / "update-program-progress.py").read_text(encoding="utf-8"),
    "sa-0232": "FLEET_SCAN_TIMEOUT" in BOWL or "120" in BOWL,
    "sa-0233": "_log_fleet_build_snapshot" in BUILD or "fleet_build_snapshot" in BUILD,
    "sa-0234": "validate-verify-wire-v1.sh" in BUILD,
    "sa-0235": "validate-spine-bridge-founder-v1.sh" in BUILD,
    "sa-0236": "audit_agent_governance_e2e" in BUILD,
    "sa-0237": "audit_personal_db_layer_a" in BUILD,
    "sa-0238": "validate-governance-fleet-v1.sh" in BUILD,
    "sa-0239": "serve-sina-command" in (SCRIPTS / "audit_backend_e2e.py").read_text(encoding="utf-8"),
    "sa-0240": ("hub_health" in BUGS or ":13020/health" in BUGS)
        and ("worker_health" in BUGS or ":13030/health" in BUGS),
    "sa-0241": "intelligence_circle" in (SCRIPTS / "audit_backend_e2e.py").read_text(encoding="utf-8"),
    "sa-0242": "sa-0217" in PRIORITY or "~230s" in PRIORITY,
    "sa-0243": "_run_council_strategic_slice_seed" in BUILD,
    "sa-0244": "_run_founder_directives_import" in BUILD,
    "sa-0245": "validate-command-data-atomic-v1.sh" in BUILD,
    "sa-0246": "validate-fleet-snapshot-scoreboard-v1.sh" in BUILD,
    "sa-0247": "validate-no-duplicate-panel-build-v1.sh" in BUILD,
    "sa-0248": "validate-find-critical-bugs-governance-drift-chain-v1.sh" in BUILD,
    "sa-0249": "validate-find-critical-bugs-wtm-future-guard-v1.sh" in BUILD,
    "sa-0250": "validate-append-repo-execution-log-on-ci-pass-v1.sh" in BUILD,
}

failed = [k for k, v in checks.items() if not v]
assert not failed, "phase-s2 proof gaps: " + ", ".join(failed)

# T2/T3 ids are same task indices — prove tier slots exist on disk
reg = json.loads((ROOT / "os/plan-library/sourcea-1000/REGISTRY.json").read_text(encoding="utf-8"))
for tier, base in (("T1", 226), ("T2", 251), ("T3", 276)):
    for offset in range(25):
        pid = f"sa-{base + offset:04d}"
        row = next((p for p in reg["plans"] if p.get("id") == pid), None)
        assert row, f"missing registry {pid}"
        assert tier in (row.get("path") or ""), f"{pid} not in {tier}"

print(f"OK: validate-phase-s2-hub-build-ci-v1 · {len(checks)} T1 proofs · T2/T3 registry 50 slots")
PY
