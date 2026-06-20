#!/usr/bin/env bash
# validate-witnessbc-proof-lab-v1.sh — Proof Lab factory bay + publish gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f data/witnessbc-proof-lab-v1.json ]] || fail "missing witnessbc-proof-lab SSOT"
[[ -f data/factory-specs/witnessbc-proof-lab-factory-v1.json ]] || fail "missing factory spec"
[[ -f scripts/fbe/witnessbc_proof_lab_bay_v1.py ]] || fail "missing bay script"
[[ -f scripts/witnessbc_proof_lab_publish_v1.py ]] || fail "missing publish script"
[[ -f witnessbc-site/data/proof-scenarios-v1.json ]] || fail "missing proof scenarios"

python3 scripts/fbe/witnessbc_proof_lab_bay_v1.py --json >/dev/null || fail "bay verify"
python3 scripts/witnessbc_proof_lab_publish_v1.py --skip-recipe --json >/dev/null || fail "publish dry-run"

grep -q 'cat-witnessbc-proof-lab' data/fbe_catalog_v1.json || fail "catalog row missing"
grep -q witnessbc_tier_A_hero data/commercial-film-routing-v1.json || fail "film routing missing"

echo "PASS: validate-witnessbc-proof-lab-v1 · Proof Lab factory wired"
