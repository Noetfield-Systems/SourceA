#!/usr/bin/env bash
# sa-0136 — scorer.py plan-eval-1b path citation hardening
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_packet_v1b.grounding import build_task_grounding
from eval_packet_v1b.scorer import cross_check_plan_eval_1b_path_citations

errs = cross_check_plan_eval_1b_path_citations()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

g_plan = build_task_grounding(
    task_id="plan-eval-1b",
    prompt="Plan Eval-1b behavioral harness comparing packet context vs raw LLM on fixed tasks",
    keywords=["eval", "packet", "raw", "benchmark", "A/B"],
)
plan_grounded = list(g_plan.get("expected_paths") or [])
assert "scripts/eval_packet_v1b/scorer.py" in plan_grounded, plan_grounded

print("OK: validate-eval-packet-v1b-scorer-plan-paths-v1 · plan-eval-1b path citations hardened (sa-0136)")
PY
