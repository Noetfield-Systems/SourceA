# sourcea-brain-chat-v1 (Cloudflare Worker)

Public Brain chat proxy for sourcea.app — OpenRouter + BM25 knowledge retrieval.

## Deploy (from repo root — not this folder alone)

```bash
cd ~/Desktop/SourceA
bash scripts/brain_cli_v1.sh deploy
```

Or manually:

```bash
cd ~/Desktop/SourceA
bash scripts/brain_chatbot_refresh_v1.sh
cd cloud/workers/sourcea-brain-chat-v1
wrangler deploy
cd ~/Desktop/SourceA
bash scripts/validate-sourcea-brain-knowledge-v1.sh
```

## Test commands (must run from SourceA root)

```bash
cd ~/Desktop/SourceA
bash scripts/brain_cli_v1.sh health
bash scripts/brain_cli_v1.sh search "What factories do you offer?"
bash scripts/brain_cli_v1.sh chat "How much does Build tier cost?"
```

## Live URL

`https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1`

Expected health: `knowledge.chunk_count` ≥ 100 · `mode: bm25_hybrid_v1`

## Knowledge pipeline

See `docs/CHATBOT_KNOWLEDGE_RUNBOOK.md`
