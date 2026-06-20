#!/usr/bin/env bash
# validate-queue-ssot-unified-v1.sh — factory-now.queue_sa == run-inbox.queue.sa_id · truth_match true
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FACTORY="${HOME}/.sina/factory-now-v1.json"
TRUTH="${HOME}/.sina/run-inbox-disk-truth-v1.json"
MONITOR="${HOME}/.sina/monitor-live-v1.json"

[[ -f "$FACTORY" ]] || { echo "FAIL: factory-now-v1.json missing"; exit 1; }
[[ -f "$TRUTH" ]] || { echo "FAIL: run-inbox-disk-truth-v1.json missing"; exit 1; }

python3 <<'PY'
import json
import sys
from pathlib import Path

SINA = Path.home() / ".sina"
factory = json.loads((SINA / "factory-now-v1.json").read_text(encoding="utf-8"))
truth = json.loads((SINA / "run-inbox-disk-truth-v1.json").read_text(encoding="utf-8"))
monitor = {}
mp = SINA / "monitor-live-v1.json"
if mp.is_file():
    try:
        monitor = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass

assert factory.get("schema") == "factory-now-v1", "factory-now schema"
assert truth.get("schema") == "run-inbox-disk-truth-v1", "run-inbox truth schema"

fn_sa = str(factory.get("queue_sa") or "")
q = truth.get("queue") or {}
truth_sa = str(q.get("sa_id") or "")
inbox = truth.get("inbox") or {}
truth_match = inbox.get("truth_match")
here_sa = str(monitor.get("here_sa") or "")
freeze = bool(factory.get("kill_flag"))
exhausted = bool(q.get("queue_exhausted")) or bool(
    q.get("pos") and q.get("total") and int(q.get("pos") or 0) > int(q.get("total") or 0)
)
lawful_exhausted = exhausted and int(factory.get("backlog") or 0) == 0 and int(factory.get("valid_yes") or 0) >= 1000

if not fn_sa and not lawful_exhausted:
    print("FAIL: factory-now.queue_sa empty")
    sys.exit(1)
if not truth_sa and not lawful_exhausted:
    print("FAIL: run-inbox.queue.sa_id empty")
    sys.exit(1)
if fn_sa != truth_sa and not lawful_exhausted:
    print(f"FAIL: factory-now.queue_sa {fn_sa!r} != run-inbox.queue.sa_id {truth_sa!r}")
    sys.exit(1)
if truth_match is not True:
    print(f"FAIL: run-inbox.inbox.truth_match is {truth_match!r} (expected True)")
    sys.exit(1)
if here_sa and not freeze and not lawful_exhausted and here_sa != fn_sa:
    print(f"FAIL: monitor-live.here_sa {here_sa!r} != factory-now.queue_sa {fn_sa!r}")
    sys.exit(1)

if lawful_exhausted:
    print("OK: queue SSOT unified · lawful exhaustion · Goal 1 honest 1000/1000 idle")
else:
    print(f"OK: queue SSOT unified · factory-now={fn_sa} · run-inbox={truth_sa} · truth_match=True")
if here_sa:
    print(f"OK: monitor-live.here_sa={here_sa}")
print(f"OK: queue pos {q.get('pos')}/{q.get('total')} role={q.get('role')}")
PY

echo "OK: validate-queue-ssot-unified-v1"
