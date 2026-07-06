#!/usr/bin/env bash
# Brain Intelligence Pipeline — prefer smart refresh (gate-aware, less dirty tree).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "${BRAIN_FORCE_FULL_REFRESH:-}" == "1" ]]; then
  echo "=== Brain full refresh (BRAIN_FORCE_FULL_REFRESH=1) ==="
  python3 scripts/distill_brain_public_rules_v1.py
  python3 scripts/distill_brain_live_sources_v1.py
  python3 scripts/distill_docs_to_brain_knowledge_v1.py
  python3 scripts/distill_www_to_brain_knowledge_v1.py || true
  python3 scripts/sync_brain_chat_knowledge_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
print(f\"bundle v{r.get('bundle_version')}: {r.get('chunk_count')} chunks\")
"
else
  exec bash "$ROOT/scripts/brain_smart_refresh_v1.sh"
fi
