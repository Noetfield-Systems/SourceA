#!/usr/bin/env bash
# Disable Copilot scheduled automations — SSOT data/copilot-scheduled-automations-v1.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSOT="${ROOT}/data/copilot-scheduled-automations-v1.json"
BACKLOG="${ROOT}/data/autorun-kaizen-backlog-v1.json"

python3 -c "
import json
from datetime import datetime, timezone
from pathlib import Path

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
ssot = json.loads(Path('$SSOT').read_text())
ssot['enabled'] = False
ssot['disabled_at'] = now
Path('$SSOT').write_text(json.dumps(ssot, indent=2) + '\n')

backlog = json.loads(Path('$BACKLOG').read_text())
for item in backlog.get('items') or []:
    if isinstance(item, dict) and 'copilot' in str(item.get('id','')).lower():
        item['status'] = 'wont_fix'
        item['blocked_reason'] = 'copilot_scheduled_automations_disabled_v1'
Path('$BACKLOG').write_text(json.dumps(backlog, indent=2) + '\n')
print('OK: copilot automations disabled in SSOT')
"

# Cursor scheduled automations (if present)
CURSOR_AUTO="${HOME}/.cursor/automations"
if [[ -d "$CURSOR_AUTO" ]]; then
  find "$CURSOR_AUTO" -name '*.json' -print0 2>/dev/null | while IFS= read -r -d '' f; do
    python3 -c "
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
try:
    row = json.loads(p.read_text())
except Exception:
    sys.exit(0)
if isinstance(row, dict):
    row['enabled'] = False
    row['disabled_by'] = 'disable_copilot_scheduled_automations_v1.sh'
    p.write_text(json.dumps(row, indent=2) + '\n')
" "$f" 2>/dev/null || true
  done
  echo "OK: cursor automations folder patched (enabled=false)"
fi

echo "DONE: disable_copilot_scheduled_automations_v1"
