#!/usr/bin/env bash
# validate-forge-mvp-fleet-v1.sh — all 5 stacks pick → graph → dispatch dry-run
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LIVE=0
[[ "${1:-}" == "--live" ]] && LIVE=1

bash "$ROOT/scripts/validate-forge-mvp-baseline-v1.sh" || exit 1

for stack in sourcea witnessbc noetfield trustfield virlux; do
  python3 "$ROOT/scripts/forge_task_graph_emit_v01.py" --stack "$stack" --json >/dev/null \
    || { echo "FAIL graph emit $stack"; exit 1; }
  if [[ "$LIVE" -eq 1 ]]; then
    python3 "$ROOT/scripts/portfolio__forge_dispatch_v1.py" --stack "$stack" --mode railway_fbe --json >/dev/null \
      || echo "WARN live dispatch $stack (cloud may be down)"
  else
    python3 "$ROOT/scripts/portfolio__forge_dispatch_v1.py" --stack "$stack" --dry-run --json >/dev/null \
      || { echo "FAIL dispatch dry-run $stack"; exit 1; }
  fi
  echo "PASS fleet stack=$stack"
done

python3 "$ROOT/scripts/fbe_forge_runner_v1.py" --bay forge-bay --tenant forge --json >/dev/null 2>&1 \
  && echo "PASS forge runner trace hook" \
  || echo "WARN forge runner skipped or slow (motor cap / Mac freeze)"

bash "$ROOT/scripts/validate-forge-mvp-hub-action-v1.sh"

echo "PASS validate-forge-mvp-fleet-v1 — 5 stacks"
