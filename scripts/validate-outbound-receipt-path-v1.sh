#!/usr/bin/env bash
# Validate outbound execution truth — no theater bypasses
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/validate_outbound_receipt_path_v1.py --json >/dev/null
python3 scripts/validate_outbound_plan_execution_proof_v1.py --json >/dev/null
python3 scripts/validate_outbound_acceptance_proof_v1.py --json >/dev/null
python3 scripts/outbound_queue_coherence_v1.py assess --json >/dev/null
echo "OK: validate-outbound-receipt-path-v1 · plan-proof · acceptance-proof · queue-coherence · execution honesty (strict)"
