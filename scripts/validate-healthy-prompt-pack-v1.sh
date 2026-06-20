#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 "$ROOT/scripts/generate-healthy-prompt-pack-v1.py" >/dev/null

CAT="$ROOT/brain-os/plan-registry/sourcea-1000/prompts/healthy-prompt-pack-100.json"
QUE="$ROOT/brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json"
LAW="$ROOT/brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md"

test -f "$CAT"
test -f "$QUE"
test -f "$LAW"
test -x "$ROOT/scripts/generate-healthy-drain-paste.sh"

python3 <<PY
import json
from pathlib import Path

cat = json.loads(Path("$CAT").read_text())
que = json.loads(Path("$QUE").read_text())
assert cat["count"] == 100, cat["count"]
assert len(cat["suggestions"]) == 100
types = {s["step_type"] for s in cat["suggestions"]}
assert len(types) == 10, types
assert que["count"] == 30, que["count"]
roles = [q["queue_role"] for q in que["queue"]]
assert roles.count("check") == 10
assert roles.count("act") == 10
assert roles.count("verify") == 10
for i in range(0, 30, 3):
    assert roles[i:i+3] == ["check", "act", "verify"], roles[i:i+3]
for q in que["queue"]:
    assert q.get("mandatory_reads"), q["hp_id"]
    assert "UNATTENDED BATCH" in str(q.get("forbidden"))
import sys
sys.path.insert(0, "$ROOT/scripts")
from worker_drain_lib import healthy_queue_status
from healthy_queue_blocker_lib import live_eval_available, sa_requires_live_eval, filter_achievable_picks
import json
st = healthy_queue_status()
assert st.get("ok") and st.get("brief"), st
assert "Queue" in st["brief"] and st.get("sa_id"), st
q = json.loads(Path("$QUE").read_text())
for item in q.get("queue") or []:
    if item.get("queue_role") in ("act", "verify") and item.get("live_eval_required"):
        ok, reason = live_eval_available()
        assert ok, f"ACT/VERIFY must not require live eval when blocked: {item.get('sa_id')} {reason}"
print("OK: validate-healthy-prompt-pack-v1 · 100 catalog · 30 queue check→act→verify")
print(f"OK: healthy_drain_rail brief={st['brief']}")
PY
