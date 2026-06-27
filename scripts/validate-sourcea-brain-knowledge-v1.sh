#!/usr/bin/env bash
# Light Brain knowledge + live worker smoke (founder-session safe, ≤90s).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${ROOT}/SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json"
BUNDLE="${ROOT}/cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"
DB="${ROOT}/data/chatbot-knowledge/brain_knowledge_v1.sqlite"
RECEIPT="${HOME}/.sina/e2e-logs/validate-sourcea-brain-knowledge-v1.log"
mkdir -p "$(dirname "$RECEIPT")"

echo "=== brain knowledge disk ===" | tee "$RECEIPT"
[[ -f "$BUNDLE" ]] || { echo "FAIL: missing $BUNDLE — run brain_cli refresh"; exit 1; }
[[ -f "$DB" ]] || { echo "FAIL: missing $DB — run brain_cli refresh"; exit 1; }
python3 -c "
import json
b=json.load(open('$BUNDLE'))
assert b.get('chunk_count',0) >= 100, b.get('chunk_count')
assert b.get('schema') in ('sourcea-brain-knowledge-bundle-v3', 'sourcea-brain-knowledge-bundle-v4', 'sourcea-brain-knowledge-bundle-v5')
print('OK bundle', b['chunk_count'], 'chunks', b.get('bundle_version'))
" | tee -a "$RECEIPT"

WORKER_URL="$(python3 -c "import json; print(json.load(open('$CONFIG'))['api_worker_url'])")"

echo "=== brain worker knowledge health ===" | tee -a "$RECEIPT"
curl -fsS "$WORKER_URL" | python3 -c "
import json,sys
d=json.load(sys.stdin)
k=d.get('knowledge') or {}
assert k.get('chunk_count',0) >= 100, k
assert k.get('mode') in ('brain_intelligence_v3', 'brain_intelligence_v4', 'brain_intelligence_v5'), k.get('mode')
assert k.get('pipeline') in (None, 'rules_first_bm25_hybrid', 'rules_first_bm25_page_aware', 'rules_first_bm25_vector_live_tools'), k.get('pipeline')
assert k.get('live_source_files', k.get('source_files',0)) >= 100, k
print('OK live knowledge', k['chunk_count'], 'chunks v', k.get('bundle_version'))
" | tee -a "$RECEIPT"

echo "=== brain live chat + citations ===" | tee -a "$RECEIPT"
curl -fsS -X POST "$WORKER_URL" \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is Forge Terminal?"}' | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d.get('reply')
assert len(d.get('citations') or []) >= 1, 'no citations'
reply=(d.get('reply') or '').lower()
assert 'forge' in reply
print('OK chat citations', len(d['citations']))
" | tee -a "$RECEIPT"

echo "validate-sourcea-brain-knowledge-v1.sh: ALL PASS" | tee -a "$RECEIPT"
