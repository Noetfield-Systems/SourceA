#!/usr/bin/env bash
# INCIDENT-025 — forbid invented Hub tab titles for advisor-discussion
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-hub-advisor-track-naming-v1 — $*" >&2; exit 1; }

FORBIDDEN=(
  'title: "Pending discussions"'
  "Pending discussions — live"
  'title: "Pending discussions"'
)

scan() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  for pat in "${FORBIDDEN[@]}"; do
    if grep -qF "$pat" "$f" 2>/dev/null; then
      fail "forbidden rename in $f: $pat — use Advisor track (INCIDENT-025)"
    fi
  done
}

scan scripts/founder_advisor_discussion_v1.py
scan scripts/site_guide.py
scan scripts/hub_essentials_index.py

# Legacy Command app.js — skip when Worker Hub mode (H1) retired app.js
WORKER_HUB=$(
  python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from hub_worker_mode_v1 import worker_hub_mode
print("1" if worker_hub_mode() else "0")
PY
)

if [[ "$WORKER_HUB" == "1" ]]; then
  scan agent-control-panel/worker-hub/index.html
  grep -q '>Advisor track<' agent-control-panel/worker-hub/index.html \
    || fail 'worker-hub/index.html missing Advisor track section title'
  grep -q 'founder-advisor-discussion' agent-control-panel/worker-hub/index.html \
    || fail 'worker-hub/index.html missing founder-advisor-discussion poll'
  python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from founder_advisor_discussion_v1 import founder_advisor_discussion_payload
from hub_essentials_index import hub_essentials_payload

payload = founder_advisor_discussion_payload()
if payload.get("hub_tab") != "advisor-discussion":
    raise SystemExit(f"founder_advisor hub_tab={payload.get('hub_tab')!r} expected advisor-discussion")

idx = hub_essentials_payload()
found = False
for pillar in idx.get("pillars") or []:
    for row in pillar.get("items") or []:
        if row.get("tab") == "advisor-discussion":
            found = True
            if row.get("title") != "Advisor track":
                raise SystemExit(f"hub essentials title={row.get('title')!r} expected Advisor track")
if not found:
    raise SystemExit("hub essentials missing advisor-discussion tab row")
PY
else
  scan agent-control-panel/assets/app.js
  grep -q 'title: "Advisor track"' agent-control-panel/assets/app.js \
    || fail 'app.js NAV missing title: "Advisor track"'
fi

python3 -c "
import json, re
from pathlib import Path
text = Path('scripts/founder_advisor_discussion_v1.py').read_text()
if 'Pending discussions' in text and 'tagline' in text:
    m = re.search(r'\"tagline\":\s*\"([^\"]+)\"', text)
    if m and 'Pending discussions' in m.group(1):
        raise SystemExit('tagline still uses Pending discussions')
"

echo "OK: validate-hub-advisor-track-naming-v1"
