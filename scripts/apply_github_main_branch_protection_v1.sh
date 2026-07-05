#!/usr/bin/env bash
# Apply main branch protection — required check: validate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSOT="${ROOT}/data/github-main-branch-protection-v1.json"

command -v gh >/dev/null || { echo "FAIL: gh CLI required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "FAIL: python3 required" >&2; exit 1; }
[[ -f "$SSOT" ]] || { echo "FAIL: missing $SSOT" >&2; exit 1; }

read -r BRANCH STRICT CONTEXT <<<"$(python3 -c "
import json
from pathlib import Path
row = json.loads(Path('$SSOT').read_text())
checks = row.get('required_status_checks') or {}
ctx = checks.get('contexts') or ['validate']
print(row.get('branch', 'main'), 'true' if checks.get('strict') else 'false', ctx[0])
")"

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
echo "Applying branch protection on ${REPO}:${BRANCH} — required check: ${CONTEXT}"

gh api \
  --method PUT \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  -f "required_status_checks[strict]=${STRICT}" \
  -f "required_status_checks[contexts][]=${CONTEXT}" \
  -f enforce_admins=false \
  -f required_pull_request_reviews=null \
  -f restrictions=null

echo "OK: main branch protection applied — required check ${CONTEXT}"
