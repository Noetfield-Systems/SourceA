#!/usr/bin/env bash
# sa-0137 — retrieve-dispatch grounding paths orchestrator + planner_engine
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_packet_v1b.grounding import (
    RETRIEVE_DISPATCH_PATHS,
    build_task_grounding,
    cross_check_retrieve_dispatch_grounding,
)

errs = cross_check_retrieve_dispatch_grounding()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

g = build_task_grounding(
    task_id="retrieve-dispatch",
    prompt="Where is dispatch_ready set false in the runtime orchestrator?",
    keywords=["dispatch_ready", "orchestrator", "false", "runtime"],
)
paths = list(g.get("expected_paths") or [])
assert paths == list(RETRIEVE_DISPATCH_PATHS), paths

print(
    "OK: validate-eval-packet-v1b-retrieve-dispatch-grounding-v1 · "
    "orchestrator + planner_engine dispatch_ready (sa-0137)"
)
PY
