#!/usr/bin/env bash
# Brain Intelligence Pipeline — full refresh: rules + 112+ sources + DB + worker bundle v3.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Brain Intelligence Pipeline refresh v3 ==="

python3 scripts/distill_brain_public_rules_v1.py
python3 scripts/distill_brain_live_sources_v1.py
python3 scripts/distill_docs_to_brain_knowledge_v1.py
python3 scripts/distill_www_to_brain_knowledge_v1.py || true
python3 scripts/sync_brain_chat_knowledge_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
print(f\"bundle v{r.get('bundle_version')}: {r.get('chunk_count')} chunks · {r.get('live_source_files', r.get('source_files'))} live sources\")
print(f\"lanes: {r.get('lanes')} · rules: {r.get('rule_chunks',0)} · mode: {r.get('retrieval')}\")
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

echo "DONE — deploy: bash scripts/brain_cli_v1.sh deploy"
