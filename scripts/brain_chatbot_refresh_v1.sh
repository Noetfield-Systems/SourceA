#!/usr/bin/env bash
# Brain chatbot knowledge refresh — full crawl → distill → SQLite DB → worker bundle.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== brain chatbot refresh v2 (full corpus) ==="

python3 scripts/distill_www_crawl_brain_knowledge_v1.py
python3 scripts/distill_www_to_brain_knowledge_v1.py || true
python3 scripts/distill_docs_to_brain_knowledge_v1.py
python3 scripts/sync_brain_chat_knowledge_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
print(f\"bundle: {r.get('chunk_count')} chunks · {r.get('total_chars',0):,} chars · lanes={r.get('lanes')}\")
"

if [[ "${SKIP_BRAIN_EVAL:-}" != "1" ]]; then
  python3 scripts/test_brain_chat_quality_v1.py --write-report --json 2>/dev/null | python3 -c "
import json,sys
try:
    r=json.load(sys.stdin)
    print('eval:', 'PASS' if r.get('ok') else 'FAIL')
    for b in r.get('buckets',[]):
        print(f\"  {b['bucket']}: {b['score']} ({'PASS' if b['pass'] else 'FAIL'})\")
except Exception as e:
    print('eval: skipped (', e, ')')
" || echo "WARN: eval did not pass — see reports/chat_eval_last_run.json"
fi

echo "brain_chatbot_refresh_v1: DONE — redeploy worker: cd cloud/workers/sourcea-brain-chat-v1 && wrangler deploy"
