---
name: sourcea-brain-chatbot-audit
description: >-
  SourceA Brain public chatbot audit — 10 phases · 100 plans. SSOT manifest,
  knowledge corpus, distill/sync pipeline, eval buckets, gap vs Cursor parity.
  Use before Brain worker edits, landing chatbot changes, or public KB updates.
---

# SourceA Brain chatbot audit skill

**Saved:** 2026-06-27T05:30:00Z  
**Master plan:** `brain-os/plan-registry/SOURCEA_BRAIN_CHATBOT_100_PLAN_LOCKED_v1.md`  
**Manifest:** `data/CHATBOT_KNOWLEDGE_MANIFEST.json`  
**Runbook:** `docs/CHATBOT_KNOWLEDGE_RUNBOOK.md`  
**Gap report:** `docs/BRAIN_CHATBOT_GAP_REPORT_LOCKED_v1.md`

---

## When to load

- Founder asks about Brain chat quality, stale answers, or public KB
- Before editing `cloud/workers/sourcea-brain-chat-v1/` or `sourcea-chatbot.js`
- After landing/pricing/forge page copy changes
- Weekly `make`-equivalent refresh: `bash scripts/brain_chatbot_refresh_v1.sh`

---

## Deploy path (live)

```text
sourcea.app (www)
  → Vercel/Pages /api/brain/chat/v1 proxy
  → Cloudflare Worker sourcea-brain-chat-v1 (OpenRouter)
  → Widget: sites/SourceA-landing/green-unified/sourcea-chatbot.js
```

Hub fallback (Mac): `scripts/sourcea_brain_chat_v1.py` via `:13020`

---

## Audit ritual (Phase 1 — every session)

1. Read `data/CHATBOT_KNOWLEDGE_MANIFEST.json` — sources, lanes, stale flags
2. Read gap report — known bot vs Cursor failures
3. `GET` worker health — expect `knowledge.chunk_count`, `knowledge.bundle_version`
4. Never paste 4,642 markdown files raw — allowlist only

```bash
curl -s "$(python3 -c "import json;print(json.load(open('SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json'))['api_worker_url'])")" | python3 -m json.tool
```

---

## Knowledge lanes

| Lane | Routes strangers to |
|------|---------------------|
| **buyer** | pricing, offer, sandbox, proof |
| **developer** | Forge Terminal, Cursor bridge, kernel, /eval |
| **partner** | intake, procurement (future) |
| **investor** | `/sourcea/investors` |
| **core** | positioning, site map, products catalog |

---

## Operator commands

```bash
# Full refresh (distill → sync → eval)
bash scripts/brain_chatbot_refresh_v1.sh

# Steps individually
python3 scripts/distill_www_to_brain_knowledge_v1.py --json
python3 scripts/distill_docs_to_brain_knowledge_v1.py --json
python3 scripts/sync_brain_chat_knowledge_v1.py --json
python3 scripts/test_brain_chat_quality_v1.py --write-report --json

# Freshness CI check
python3 scripts/sync_brain_chat_knowledge_v1.py --check-only --json
```

After sync: **redeploy worker** so `knowledge-bundle.json` ships.

---

## Eval buckets (P0 block deploy if fail)

| Bucket | Threshold | File |
|--------|-----------|------|
| p0_positioning | 90% | `data/brain-chat-eval-canonical-v1.json` |
| p1_pricing | 85% | |
| p2_developer | 85% | |
| p3_anti_icp | 90% | |

Report: `reports/chat_eval_last_run.json`

---

## Hard bans (public Brain)

- Invented pricing, custody claims, secrets
- OpenRouter / model names / API keys / Mac ports
- Governance jargon (PASS/BLOCK, factory internals)
- Leading with dollar amounts

---

## Anti-patterns

| Wrong | Right |
|-------|-------|
| Dump whole `docs/` to prompt | Manifest allowlist → distill → chunks |
| Manual-only KB forever | `distill_*` + `sync_*` on refresh |
| Chat history as SSOT | Disk manifest + bundle version |
| Skip eval before ship | P0 ≥90% on canonical questions |

---

## Exit criteria (Phase 10)

Brain answers Forge, pricing, homepage vs Forge Terminal, Cursor try-path with citations at **90%+ P0 eval** — parity with public Cursor answers, **not** private build context.
