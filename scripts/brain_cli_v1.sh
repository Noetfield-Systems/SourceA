#!/usr/bin/env bash
# Brain chatbot CLI — run from anywhere (fixes wrong cwd after wrangler deploy).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

cmd="${1:-help}"
shift || true

case "$cmd" in
  search)
    python3 scripts/brain_chat_knowledge_db_v1.py --search "${1:-What is SourceA?}" --json
    ;;
  chat)
    python3 scripts/sourcea_brain_chat_v1.py -m "${1:-What is SourceA?}" --json
    ;;
  refresh)
    bash scripts/brain_chatbot_refresh_v1.sh
    ;;
  health)
    URL="$(python3 -c "import json; print(json.load(open('SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json'))['api_worker_url'])")"
    curl -s "$URL" | python3 -m json.tool
    ;;
  deploy)
    bash scripts/brain_chatbot_refresh_v1.sh
    : "${CF_MAIN_TOKEN:?CF_MAIN_TOKEN must be loaded; refusing to use human login state}"
    (cd cloud/workers/sourcea-brain-chat-v1 && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler deploy)
    bash scripts/validate-sourcea-brain-knowledge-v1.sh
    ;;
  deploy-verified|deploy-no-refresh)
    # Gate path: deploy the already-committed, verifier-signed bundle as-is.
    : "${CF_MAIN_TOKEN:?CF_MAIN_TOKEN must be loaded; refusing to use human login state}"
    (cd cloud/workers/sourcea-brain-chat-v1 && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler deploy)
    bash scripts/validate-sourcea-brain-knowledge-v1.sh
    ;;
  deploy-verified-dry-run|deploy-no-refresh-dry-run)
    # Phase 0.4 proof path: validate upload/auth without publishing a Worker version.
    : "${CF_MAIN_TOKEN:?CF_MAIN_TOKEN must be loaded; refusing to use human login state}"
    (cd cloud/workers/sourcea-brain-chat-v1 && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler deploy --dry-run)
    bash scripts/validate-sourcea-brain-knowledge-v1.sh
    ;;
  pipeline)
    python3 scripts/brain_intelligence_pipeline_v1.py -m "${2:-What is SourceA?}" --json
    ;;
  help|*)
    cat <<EOF
Brain Intelligence CLI (always run via repo root path)

  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh search "What factories do you offer?"
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh chat "How much does Build tier cost?"
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh health
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh pipeline "What is SourceA?"
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh refresh
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh deploy
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh deploy-verified
  bash ~/Desktop/SourceA/scripts/brain_cli_v1.sh deploy-verified-dry-run

Repo root: $ROOT
Docs: docs/BRAIN_INTELLIGENCE_PIPELINE_LOCKED_v1.md
EOF
    ;;
esac
