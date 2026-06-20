#!/usr/bin/env bash
# Gate: run inbox disk truth SSOT present and matches queue cursor.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TRUTH="${HOME}/.sina/run-inbox-disk-truth-v1.json"
EXEC="${HOME}/.sina/execution-lane-v1.json"

[[ -f "$TRUTH" ]] || { echo "FAIL: run-inbox-disk-truth-v1.json missing"; exit 1; }
[[ -f "$EXEC" ]] || { echo "FAIL: execution-lane-v1.json missing"; exit 1; }

python3 <<'PY'
import json, sys
from pathlib import Path
truth = json.loads(Path.home().joinpath(".sina/run-inbox-disk-truth-v1.json").read_text())
exec_lane = json.loads(Path.home().joinpath(".sina/execution-lane-v1.json").read_text())
assert truth.get("schema") == "run-inbox-disk-truth-v1"
assert exec_lane.get("execution") == "run_inbox"
advisory = exec_lane.get("advisory") or ""
assert advisory in ("prompt_feed", "prompt_feed_live_mirror"), f"unexpected advisory={advisory!r}"
q = truth.get("queue") or {}
assert q.get("sa_id"), "queue sa_id missing"
assert q.get("pos") and q.get("total"), "queue pos/total missing"
print(f"OK: disk truth {q.get('pos')}/{q.get('total')} {q.get('sa_id')} {q.get('role')}")
print(f"OK: execution=run_inbox advisory={advisory}")
PY

echo "OK: validate-run-inbox-disk-truth-v1"
