#!/usr/bin/env bash
# validate-gha-improvement-queue-v1.sh — GHA sweep + validate wiring logged
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

for wf in validate.yml repo-health-daily-v1.yml security-sweep-weekly-v1.yml; do
  [[ -f "${ROOT}/.github/workflows/${wf}" ]] || fail "missing workflow ${wf}"
done

for script in improvement_queue_insert_v1.py gha_repo_health_sweep_v1.py gha_security_sweep_v1.py; do
  [[ -f "${ROOT}/scripts/${script}" ]] || fail "missing script ${script}"
done

[[ -f "${ROOT}/data/github-main-branch-protection-v1.json" ]] || fail "missing branch protection SSOT"

python3 -c "
import json
from pathlib import Path
row = json.loads(Path('${ROOT}/data/github-main-branch-protection-v1.json').read_text())
assert 'validate' in (row.get('required_status_checks') or {}).get('contexts', [])
" || fail "branch protection SSOT missing validate context"

grep -q 'improvement_queue' "${ROOT}/scripts/gha_repo_health_sweep_v1.py" || fail "repo health missing queue insert"
grep -q 'improvement_queue' "${ROOT}/scripts/gha_security_sweep_v1.py" || fail "security sweep missing queue insert"
grep -q 'SA-T-validate-main' "${ROOT}/data/trigger-registry-v1.json" || fail "trigger registry missing SA-T-validate-main"

echo "OK: validate-gha-improvement-queue-v1"
