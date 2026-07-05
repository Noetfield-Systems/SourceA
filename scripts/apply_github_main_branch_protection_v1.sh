#!/usr/bin/env bash
# Apply main branch protection — required check: validate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSOT="${ROOT}/data/github-main-branch-protection-v1.json"

command -v gh >/dev/null || { echo "FAIL: gh CLI required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "FAIL: python3 required" >&2; exit 1; }
[[ -f "$SSOT" ]] || { echo "FAIL: missing $SSOT" >&2; exit 1; }

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
BODY="$(python3 -c "
import json
from pathlib import Path
row = json.loads(Path('$SSOT').read_text())
checks = row.get('required_status_checks') or {}
print(json.dumps({
  'required_status_checks': {
    'strict': bool(checks.get('strict', True)),
    'contexts': list(checks.get('contexts') or ['validate']),
  },
  'enforce_admins': bool(row.get('enforce_admins', False)),
  'required_pull_request_reviews': row.get('required_pull_request_reviews'),
  'restrictions': row.get('restrictions'),
}))
")"
BRANCH="$(python3 -c "import json; print(json.loads(open('$SSOT').read())['branch'])")"
CONTEXT="$(python3 -c "import json; print(json.loads(open('$SSOT').read())['required_status_checks']['contexts'][0])")"

echo "Applying branch protection on ${REPO}:${BRANCH} — required check: ${CONTEXT}"

gh api \
  --method PUT \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<<"$BODY"

echo "OK: main branch protection applied — required check ${CONTEXT}"
