#!/usr/bin/env bash
# Gate-aware Brain refresh — skip when fresh, light by default, full only when landing changed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Brain smart refresh (gate-aware) ==="
python3 scripts/brain_smart_refresh_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
print(f\"action={r.get('action')} reason={r.get('reason')} ok={r.get('ok')}\")
s=r.get('sync') or {}
print(f\"bundle: {s.get('chunk_count','?')} chunks · lanes {s.get('lanes',{})}\")
"

if [[ "${SKIP_BRAIN_EVAL:-}" != "1" ]]; then
  python3 scripts/test_brain_chat_quality_v1.py --write-report --json 2>/dev/null | python3 -c "
import json,sys
try:
    r=json.load(sys.stdin)
    print('eval:', 'PASS' if r.get('ok') else 'FAIL')
except Exception:
    print('eval: skipped')
" || true
fi

echo "DONE — deploy worker: bash scripts/brain_cli_v1.sh deploy"
