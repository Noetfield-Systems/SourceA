#!/usr/bin/env bash
# Brain mechanical session gate — disk SSOT before any routing reply.
# Law: BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Fast Brain default — route Worker INBOX; skip hospital/E2E/slow hub rebuild on every start
export SINA_BRAIN_FAST="${SINA_BRAIN_FAST:-1}"
export SINA_COMMERCIAL_LOOP="${SINA_COMMERCIAL_LOOP:-1}"

# Intent router — resolve rule collisions before any shell (INCIDENT-026)
FOUNDER_MSG="${BRAIN_FOUNDER_MSG:-}"
python3 scripts/brain_intent_gate_v1.py --message "$FOUNDER_MSG" --write --json >/dev/null 2>&1 || true

# Ecosystem heartbeat — read ACTIVE_NOW.md first (law: ACTIVE_NOW_HEARTBEAT_LOCKED_v1)
python3 scripts/active_now_v1.py --heartbeat --caller brain-session-start || exit 1

if [ "$SINA_BRAIN_FAST" = "1" ] || [ "$SINA_BRAIN_FAST" = "true" ] || [ "$SINA_BRAIN_FAST" = "yes" ]; then
  # Fast path (<3s): hub · bind heal · brain validate · no agentic/hospital chain
  self_heal_ok="$(python3 scripts/brain_fast_startup_v1.py --caller brain-session-start --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo "false")"
else
  self_heal_ok="$(python3 scripts/brain_self_heal_startup_v1.py --caller brain-session-start --json-only 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo "false")"
fi
if [ "$self_heal_ok" != "True" ] && [ "$self_heal_ok" != "true" ]; then
  echo "BRAIN_SELF_HEAL_FAIL — P0 blocker; see ~/.sina/brain-fast-startup-v1.json or brain-self-heal-startup-v1.json" >&2
  exit 1
fi

python3 scripts/factory_validation_lock_v1.py sweep --json >/dev/null 2>&1 || true
python3 scripts/active_now_sync_from_factory_now_v1.py --json >/dev/null 2>&1 || true
python3 scripts/brain_session_guard_v1.py --write --json >/dev/null 2>&1 || true
python3 scripts/brain_sync_lib_v1.py --mode light >/dev/null 2>&1 || true
python3 scripts/anti_staleness_auto_wire_v1.py --role brain --tier session --json >/dev/null 2>&1 || true
if [ "$SINA_BRAIN_FAST" != "1" ] && [ "$SINA_BRAIN_FAST" != "true" ] && [ "$SINA_BRAIN_FAST" != "yes" ]; then
  python3 scripts/l1_agent_pipeline_wire_v1.py --json --no-sync >/dev/null 2>&1 || exit 1
  python3 scripts/agentic_layer_pipeline_v2.py --json --tier fast --no-sync >/dev/null 2>&1 || exit 1
fi

RECEIPT="${HOME}/.sina/brain_session_receipt_v1.json"
GATE_RECEIPT="${HOME}/.sina/cursor_entry_gate_receipt_v1.json"
PRIORITY="${ROOT}/brain-os/plan-registry/SOURCEA-PRIORITY.md"
ASSIGNMENT="${ROOT}/brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md"

# Layer 3 — hash entry + law files (fails if missing)
gate_json="$(python3 scripts/cursor_entry_gate.py --role brain 2>/dev/null | tail -1)"
gate_id="$(echo "$gate_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gate_id',''))" 2>/dev/null || echo "")"
gate_hash8="$(echo "$gate_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gate_hash8',''))" 2>/dev/null || echo "")"
gate_line="$(echo "$gate_json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('reply_line1',''))" 2>/dev/null || echo "")"

# Outbound Cloud Forge Run has no mono-asf pick — do not fail session on empty pick (pipefail)
pick_line="$(bash scripts/plan-no-asf-run.sh pick 1 2>/dev/null | awk '/^sa-[0-9]/{print; exit}' || true)"
next_pick="${pick_line%%$'\t'*}"
next_pick_path="$(echo "$pick_line" | awk -F'\t' '{print $2}')"
if [ -z "$next_pick" ]; then
  next_pick="$(python3 -c "import json; from pathlib import Path; p=Path.home()/'.sina/worker-prompt-inbox-v1.json'; d=json.loads(p.read_text()) if p.exists() else {}; print(d.get('meta',{}).get('sa_id','') or '')" 2>/dev/null || echo "")"
  next_pick_path="~/.sina/worker-prompt-inbox-v1.json"
fi
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
    "brain-os/law/entry/START_HERE_LOCKED_v1.md",
    "brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
    "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    "brain-os/law/enforcement/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
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
