#!/usr/bin/env bash
# Brain mechanical session gate — disk SSOT before any routing reply.
# Law: BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

RECEIPT="${HOME}/.sina/brain_session_receipt_v1.json"
GATE_RECEIPT="${HOME}/.sina/cursor_entry_gate_receipt_v1.json"
PRIORITY="${ROOT}/brain-os/plan-registry/SOURCEA-PRIORITY.md"
ASSIGNMENT="${ROOT}/brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md"

# Layer 3 — hash entry + law files (fails if missing)
gate_json="$(python3 scripts/cursor_entry_gate.py --role brain 2>/dev/null | tail -1)"
gate_id="$(echo "$gate_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gate_id',''))" 2>/dev/null || echo "")"
gate_hash8="$(echo "$gate_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gate_hash8',''))" 2>/dev/null || echo "")"
gate_line="$(echo "$gate_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('reply_line1',''))" 2>/dev/null || echo "")"

pick_line="$(bash scripts/plan-no-asf-run.sh pick 1 2>/dev/null | awk '/^sa-[0-9]/{print; exit}')"
next_pick="${pick_line%%$'\t'*}"
next_pick_path="$(echo "$pick_line" | awk -F'\t' '{print $2}')"
goal_json="$(python3 scripts/goal-progress-v1.py --json 2>/dev/null || echo '{}')"
goal_done="$(echo "$goal_json" | python3 -c "import sys,json; g=json.load(sys.stdin).get('goal_1',{}); print(g.get('done','?'))" 2>/dev/null || echo "?")"
goal_pct="$(echo "$goal_json" | python3 -c "import sys,json; g=json.load(sys.stdin).get('goal_1',{}); print(g.get('pct','?'))" 2>/dev/null || echo "?")"

feas_json="$(python3 scripts/prompt_feasibility_gate.py --role brain --json 2>/dev/null || echo '{}')"
feas_ok="$(echo "$feas_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo "false")"
feas_action="$(echo "$feas_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('action','?'))" 2>/dev/null || echo "?")"

eval_mode="$(grep -E 'Eval-1b live' "$PRIORITY" 2>/dev/null | head -1 | sed 's/.*|//' | xargs || echo 'unknown')"
dispatch_ready="false"

receipt_id="brain-$(date -u +%Y%m%dT%H%M%SZ)-$$"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$(dirname "$RECEIPT")"
RECEIPT_PATH="$RECEIPT" python3 - <<PY
import json, os
from pathlib import Path

receipt = {
  "receipt_id": "$receipt_id",
  "at": "$ts",
  "law": "BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
  "workspace": "$ROOT",
  "gate_id": "$gate_id",
  "gate_hash8": "$gate_hash8",
  "gate_line1": "$gate_line",
  "next_pick": "$next_pick",
  "next_pick_path": "$next_pick_path",
  "goal_1_done": "$goal_done",
  "goal_1_pct": "$goal_pct",
  "worker_paste_cmd": "bash scripts/generate-worker-drain-paste.sh",
  "goal_execution_ssot": "brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
  "assignment_ssot": "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
  "one_worker": True,
  "dispatch_ready": "$dispatch_ready",
  "eval_1b_live": "$eval_mode",
  "prompt_feasibility_ok": $feas_ok,
  "prompt_feasibility_action": "$feas_action",
  "prompt_feasibility_law": "SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
  "research_library_index": str(Path.home() / ".sina/brain/research-library/INDEX.yaml"),
  "research_library_law": "~/.sina/brain/BRAIN_RESEARCH_LIBRARY_LOCKED_v1.md",
  "disk_reads_required": [
    "~/.sina/brain/research-library/INDEX.yaml",
    "brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md",
    "brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
    "brain-os/entry/START_HERE_LOCKED_v1.md",
    "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
    "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    "brain-os/enforcement/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
    "brain-os/INDEX_LOCKED_v1.md",
  ],
  "forbidden_routing_labels": [
    "FORGE builder",
    "FORGE builder chat",
    "parallel FORGE lane",
    "open FORGE workspace to build as separate assignee",
  ],
  "say_instead": "SourceA Worker — FORGE-scoped task (same chat, ~/Desktop/forge/)",
}
Path(os.environ["RECEIPT_PATH"]).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
PY

echo "BRAIN_SESSION_START ok receipt_id=$receipt_id"
echo "$gate_line"
echo "RECEIPT=$RECEIPT"
echo "GATE_RECEIPT=$GATE_RECEIPT"
echo "NEXT_PICK=$next_pick"
echo "NEXT_PICK_PATH=$next_pick_path"
echo "ASSIGNMENT_SSOT=$ASSIGNMENT"
echo "DISPATCH_READY=$dispatch_ready"
cat "$RECEIPT"
