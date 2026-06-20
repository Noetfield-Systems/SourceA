#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
INBOX="${HOME}/.sina/worker-prompt-inbox-v1.json"
BIND="${HOME}/.sina/goal1-worker-turn-bind-v1.json"
BACKUP_INBOX=""
BACKUP_BIND=""

cleanup() {
  if [[ -n "$BACKUP_INBOX" && -f "$BACKUP_INBOX" ]]; then
    cp "$BACKUP_INBOX" "$INBOX"
    rm -f "$BACKUP_INBOX"
  fi
  if [[ -n "$BACKUP_BIND" && -f "$BACKUP_BIND" ]]; then
    cp "$BACKUP_BIND" "$BIND"
    rm -f "$BACKUP_BIND"
  elif [[ -f "$BACKUP_BIND" ]]; then
    rm -f "$BIND"
  fi
}
trap cleanup EXIT

test -f "$ROOT/scripts/goal1_lane_broker.py"
python3 "$ROOT/scripts/goal1_lane_broker.py" status >/dev/null
python3 "$ROOT/scripts/goal1_lane_broker.py" pickup >/dev/null
grep -q "WORKER_ROUND_REPORT" "$ROOT/scripts/goal1_lane_broker.py"
grep -q "brain-poll" "$ROOT/scripts/goal1_lane_broker.py"
grep -q "check_stdin_report" "$ROOT/scripts/goal1_lane_broker.py"
grep -q "check-stdin" "$ROOT/scripts/goal1_lane_broker.py"

if [[ -f "$INBOX" ]]; then
  BACKUP_INBOX="${INBOX}.validate-broker-bak"
  cp "$INBOX" "$BACKUP_INBOX"
fi
if [[ -f "$BIND" ]]; then
  BACKUP_BIND="${BIND}.validate-broker-bak"
  cp "$BIND" "$BACKUP_BIND"
fi

python3 <<'PY'
import json
from pathlib import Path

home = Path.home() / ".sina"
# agent_cli check-stdin prefers active_turn_snapshot over pending INBOX — clear for fixture.
snap = home / "goal1-active-turn-snapshot-v1.json"
if snap.is_file():
    snap.unlink()
prompt = (
    "[GOAL1_HEALTHY_DRAIN 4/30] SourceA Worker — role=check · sa=sa-0999\n"
    "REGISTRY bind: sa-0999\n"
)
home.mkdir(parents=True, exist_ok=True)
(home / "worker-prompt-inbox-v1.json").write_text(
    json.dumps(
        {
            "schema": "worker-prompt-inbox-v1",
            "pending": True,
            "prompt": prompt,
            "meta": {"sa_id": "sa-WRONG", "queue_role": "check", "queue_pos": 4, "queue_total": 30},
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
(home / "goal1-worker-turn-bind-v1.json").write_text(
    json.dumps(
        {
            "schema": "goal1-worker-turn-bind-v1",
            "sa_id": "sa-0999",
            "queue_role": "check",
            "at": "fixture",
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print("fixture inbox written")
PY

REPORT_FIXTURE="${TMPDIR:-/tmp}/broker-stdin-fixture.yaml"
cat >"$REPORT_FIXTURE" <<'YAMLFIX'
status: WORKER_ROUND_REPORT
round_type: audit
sa_focus: sa-0999
validate:
  spine: PASS
  critical_bugs: 0
summary: broker stdin parse fixture
YAMLFIX

python3 "$ROOT/scripts/goal1_lane_broker.py" check-stdin --file "$REPORT_FIXTURE" --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('sa_focus') == 'sa-0999', d
bind = d.get('bind') or {}
assert bind.get('prompt_sa') == 'sa-0999', bind
assert bind.get('expected_sa') == 'sa-0999', bind
print('PASS: check-stdin sa_focus matches INBOX bind (prompt header over drifted meta)')
"
rm -f "$REPORT_FIXTURE"

bash "$ROOT/scripts/validate-broker-spine-v1.sh"

echo "OK: validate-goal1-lane-broker-v1"
