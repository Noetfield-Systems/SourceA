#!/usr/bin/env bash
# validate-governance-ssot-registry-v1.sh — one active operating law · no stale SSOT plane docs
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/sourcea_governance_ssot_registry_v1.py --json --write-receipt
