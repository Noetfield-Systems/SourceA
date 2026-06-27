# Brain Intelligence Pipeline (LOCKED v1)

**Saved:** 2026-06-27T08:00:00Z  
**Law:** Brain v4 — page-aware retrieval-first, rule-aware, guardrailed, 112+ live sources.

---

## Architecture

```text
Live sources (112+ files)
  → distill_brain_live_sources_v1.py
  → distill_brain_public_rules_v1.py
  → SQLite brain_knowledge_v1.sqlite
  → knowledge-bundle.json (worker)
  → brainRetrieve() per query (+ page_path boost)
  → assembleBrainPrompt() + confidence
  → OpenRouter (Gemini Flash) OR retrieval-only fallback
  → post-filter guardrails (forbidden phrases, lead-price)
```

## Components

| Script | Role |
|--------|------|
| `distill_brain_live_sources_v1.py` | Crawl 68 HTML + 24 JSON + public data |
| `distill_brain_public_rules_v1.py` | Rule chunks from SSOT (not prompt) |
| `brain_retrieval_engine_v1.py` | Rules-first BM25 + confidence |
| `brain_intelligence_pipeline_v1.py` | Orchestrator (hub + tests) |
| `sync_brain_chat_knowledge_v1.py` | DB + bundle v3 export |
| `retrieval.js` | Worker-side mirror of pipeline |

## Brain vs chatbot

| Chatbot | Brain |
|---------|-------|
| Hardcoded FAQ prompt | Minimal BRAIN_CORE + retrieved blocks |
| Static answers | BM25 over 112+ live sources every turn |
| No rules layer | Public rules retrieved first every turn |
| No confidence | confidence: high/medium/low per reply |

## Operator

```bash
cd ~/Desktop/SourceA
bash scripts/brain_chatbot_refresh_v1.sh
bash scripts/brain_cli_v1.sh deploy
bash scripts/brain_cli_v1.sh pipeline -m "What factories do you offer?"
```

## Health (live worker)

Expect: `mode: brain_intelligence_v3` · `live_source_files >= 112` · `rule_chunks >= 1`
