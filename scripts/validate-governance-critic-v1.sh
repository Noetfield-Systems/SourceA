#!/usr/bin/env bash
# validate-governance-critic-v1.sh — deterministic Critic fixture matrix (GAC wire)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-governance-critic-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/demo/governance/critic_fixtures_v1.json" ]] || fail "fixtures missing"

python3 governance_critic_eval_v1.py --fixtures --json >/tmp/gov-critic-fixtures.json \
  || fail "fixture run exit nonzero"

python3 - <<'PY' || fail "fixture expectations"
import json
from pathlib import Path
p = Path("/tmp/gov-critic-fixtures.json")
d = json.loads(p.read_text())
if not d.get("ok"):
    bad = [r for r in d.get("rows", []) if not r.get("ok")]
    raise SystemExit(f"fixture failures: {[b.get('fixture_id') for b in bad]}")
print(f"OK: governance critic fixtures {d.get('passed')}/{d.get('total')}")
PY

[[ -f "${HOME}/.sina/governance-critic-eval-latest-v1.json" ]] \
  || fail "latest critic receipt missing"

echo "OK: validate-governance-critic-v1 · deterministic Critic · no LLM duplicate"
