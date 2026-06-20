#!/usr/bin/env bash
# Governance bundle — SAVE · WORK · EDIT ALLOWED laws + cross-lane guard
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
test -f "$ROOT/brain-os/law/enforcement/AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md"
test -f "$ROOT/brain-os/incidents/SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md"
bash "$ROOT/scripts/validate-cross-lane-edit-v1.sh"
echo "PASS: validate-governance-agent-verbs-v1"
