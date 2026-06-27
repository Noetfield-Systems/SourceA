# Chatbot knowledge runbook

**Saved:** 2026-06-27T05:30:00Z  
**Owner:** CHATBOT_KNOWLEDGE_OWNER (assign in ops)  
**Manifest:** `data/CHATBOT_KNOWLEDGE_MANIFEST.json`

---

## Overview

Public Brain on sourcea.app uses a **manifest-driven knowledge pipeline** (v2 — full corpus):

1. **Auto-crawl** all public www HTML (68 pages) + JSON catalogs (24 files)
2. Distill allowlisted public docs (10+ files)
3. **SQLite FTS5** database for hub-side search (`brain_knowledge_v1.sqlite`)
4. Sync → compact `knowledge-bundle.json` (~281KB, 371 chunks) for Cloudflare Worker
5. **BM25 + intent** hybrid retrieval at query time
6. Eval against canonical questions before deploy

---

## Weekly operator flow

```bash
cd ~/Desktop/SourceA
bash scripts/brain_chatbot_refresh_v1.sh
# Redeploy worker (cloud CI / wrangler deploy)
```

Skip live eval on Mac founder session:

```bash
SKIP_BRAIN_EVAL=1 bash scripts/brain_chatbot_refresh_v1.sh
```

---

## Add a new public knowledge source

1. Edit `data/CHATBOT_KNOWLEDGE_MANIFEST.json` — add `sources[]` row
2. Set `lane`, `public: true`, `distill: www|docs|manual`, `output` path
3. Run distill + sync
4. Add eval question if P0
5. Redeploy worker

---

## Health check

```bash
curl -s "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1" | jq '.knowledge'
```

Expected fields: `bundle_version`, `chunk_count`, `chars`, `mode`, `lanes`

---

## CI checks (cloud ship window)

| Check | Command |
|-------|---------|
| Source not missing | `sync_brain_chat_knowledge_v1.py --check-only` |
| Distill fresh | output mtime ≥ source mtime |
| P0 eval | `test_brain_chat_quality_v1.py` ≥90% |
| Pricing sync | pricing-matrix.md matches `/sourcea/pricing` bands |

---

## Anti-patterns

- Dumping all `docs/` or `brain-os/` into prompt
- Hand-editing `knowledge-bundle.json` (regenerate via sync)
- Shipping worker without redeploy after sync
- Stale `_EXTRA_MD` dependency (removed — use manifest)

---

## Freshness SLA

`freshness_sla_hours: 168` (7 days) — alert if distill not run within SLA.

---

## Public changelog

After each refresh, append to site or status:

> Assistant knowledge updated YYYY-MM-DD (bundle vX.Y.Z)

---

## Related

- `brain-os/plan-registry/SOURCEA_BRAIN_CHATBOT_100_PLAN_LOCKED_v1.md`
- `docs/BRAIN_CHATBOT_GAP_REPORT_LOCKED_v1.md`
- `.cursor/skills/sourcea-brain-chatbot-audit/SKILL.md`
