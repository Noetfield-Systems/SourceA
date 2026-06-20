#!/usr/bin/env bash
# sa-0131–sa-0140 — Eval-1b phase-s1 T1 validator bundle (no duplicate live OpenRouter)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

run() {
  bash "$1"
}

run validate-eval-packet-v1b-grounding.sh
run validate-eval-packet-v1b-bugfix-gate-grounding-v1.sh
run validate-eval-packet-v1b-scorer-plan-paths-v1.sh
run validate-eval-packet-v1b-retrieve-dispatch-grounding-v1.sh
run validate-eval-packet-v1b-factory-runreceipt-grounding-v1.sh
run validate-eval-packet-v1b-l8-hybrid-grounding-v1.sh
run validate-eval-packet-v1b-scaffold-after-live-v1.sh
run validate-eval-packet-v1b-strict-build-chain-v1.sh
run validate-dispatch-policy-alignment-v1.sh
run validate-graph-executor-pos-dispatch-v1.sh
run validate-find-critical-bugs-governance-drift-chain-v1.sh

python3 - <<'PY'
from eval_packet_v1b.grounding import (
    cross_check_bugfix_gate_grounding,
    cross_check_factory_runreceipt_grounding,
    cross_check_l8_hybrid_grounding,
    cross_check_retrieve_dispatch_grounding,
)
from eval_packet_v1b.scorer import cross_check_plan_eval_1b_path_citations
from eval_report_capture import cross_check_scaffold_survives_after_live

checks = [
    ("bugfix-gate", cross_check_bugfix_gate_grounding()),
    ("plan-eval-1b paths", cross_check_plan_eval_1b_path_citations()),
    ("retrieve-dispatch", cross_check_retrieve_dispatch_grounding()),
    ("factory-runreceipt", cross_check_factory_runreceipt_grounding()),
    ("l8-hybrid", cross_check_l8_hybrid_grounding()),
    ("scaffold-after-live", cross_check_scaffold_survives_after_live()),
]
for label, errs in checks:
    if errs:
        for e in errs:
            print(f"FAIL: {label}: {e}")
        raise SystemExit(1)

print("OK: validate-eval-packet-v1b-phase-s1-t1-bundle-v1 · sa-0131–sa-0140 cross_checks PASS")
PY
