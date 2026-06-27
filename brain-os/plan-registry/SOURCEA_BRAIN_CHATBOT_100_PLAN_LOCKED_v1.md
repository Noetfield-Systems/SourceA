# SourceA Brain chatbot — 10 phases · 100 plans (LOCKED v1)

**Saved:** 2026-06-27T08:49:37Z  
**Adapted from:** Noetfield CHAT-P blueprint + SourceA brain_intelligence_v3 audit  
**Machine SSOT:** `data/brain-chatbot-100-plans-v1.json`  
**Manifest:** `data/CHATBOT_KNOWLEDGE_MANIFEST.json`  
**Progress:** 38/100 done (38.0%)  

---

## Phase 1 — Knowledge corpus (foundation)

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P1-01 | Corpus manifest SSOT | SHIPPED | P0 |
| BRAIN-P1-02 | Public copy ingest | SHIPPED | P0 |
| BRAIN-P1-03 | FAQ pack | TODO | P1 |
| BRAIN-P1-04 | API surface ingest | IN PROGRESS | P1 |
| BRAIN-P1-05 | Public rules guardrail snippets | SHIPPED | P0 |
| BRAIN-P1-06 | llms.txt + sitemap sync | TODO | P2 |
| BRAIN-P1-07 | Forbidden corpus denylist | SHIPPED | P0 |
| BRAIN-P1-08 | Chunk strategy | SHIPPED | P0 |
| BRAIN-P1-09 | Corpus rebuild on deploy | SHIPPED | P0 |
| BRAIN-P1-10 | Verify gate | SHIPPED | P0 |

## Phase 2 — Vector index & retrieval

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P2-01 | Embedding provider | SHIPPED | P1 |
| BRAIN-P2-02 | Vector store | SHIPPED | P1 |
| BRAIN-P2-03 | Hybrid BM25 + vector merge | SHIPPED | P1 |
| BRAIN-P2-04 | Retriever service | SHIPPED | P0 |
| BRAIN-P2-05 | Page-aware boost | SHIPPED | P0 |
| BRAIN-P2-06 | Intent routing buckets | IN PROGRESS | P1 |
| BRAIN-P2-07 | Citation objects | SHIPPED | P0 |
| BRAIN-P2-08 | Stale chunk detection | TODO | P2 |
| BRAIN-P2-09 | Re-index cron | TODO | P1 |
| BRAIN-P2-10 | Retrieval eval set — 50 golden | IN PROGRESS | P0 |

## Phase 3 — LLM orchestration (replace hardcode)

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P3-01 | ChatBrain service | SHIPPED | P0 |
| BRAIN-P3-02 | System prompt lock | SHIPPED | P0 |
| BRAIN-P3-03 | Provider adapter | SHIPPED | P0 |
| BRAIN-P3-04 | Fallback ladder | SHIPPED | P1 |
| BRAIN-P3-05 | History window | SHIPPED | P0 |
| BRAIN-P3-06 | Dynamic chip generator | TODO | P2 |
| BRAIN-P3-07 | Streaming SSE | TODO | P1 |
| BRAIN-P3-08 | Token + cost logging | TODO | P2 |
| BRAIN-P3-09 | Rate limit + Turnstile | TODO | P1 |
| BRAIN-P3-10 | Feature flag BRAIN_RAG_LEGACY | TODO | P2 |

## Phase 4 — Guardrails & compliance (public-safe)

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P4-01 | Pre-filter input | TODO | P1 |
| BRAIN-P4-02 | Post-filter positioning CI | SHIPPED | P0 |
| BRAIN-P4-03 | Forbidden phrase scanner | IN PROGRESS | P0 |
| BRAIN-P4-04 | Agentic-first CTA law | SHIPPED | P0 |
| BRAIN-P4-05 | No invitation law | IN PROGRESS | P0 |
| BRAIN-P4-06 | Confidence gate UI | SHIPPED | P0 |
| BRAIN-P4-07 | Human escalate contact | TODO | P1 |
| BRAIN-P4-08 | CASL-safe chat | SHIPPED | P1 |
| BRAIN-P4-09 | Audit trail chunk IDs | TODO | P1 |
| BRAIN-P4-10 | verify_brain_guardrails.sh | SHIPPED | P0 |

## Phase 5 — Live product context (read-only tools)

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P5-01 | Tool: boot-proof snapshot | SHIPPED | P1 |
| BRAIN-P5-02 | Tool: products catalog | SHIPPED | P1 |
| BRAIN-P5-03 | Tool: factories catalog | SHIPPED | P0 |
| BRAIN-P5-04 | Tool: pricing tiers | SHIPPED | P0 |
| BRAIN-P5-05 | Tool: site map resolver | TODO | P1 |
| BRAIN-P5-06 | Forge Terminal live probe | TODO | P1 |
| BRAIN-P5-07 | Tool: positioning JSON live | TODO | P2 |
| BRAIN-P5-08 | Tool registry allowlist | TODO | P1 |
| BRAIN-P5-09 | Read-only enforcement | SHIPPED | P0 |
| BRAIN-P5-10 | Tool eval — 20 live questions | TODO | P1 |

## Phase 6 — Conversation quality & memory

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P6-01 | Session summary compress | TODO | P2 |
| BRAIN-P6-02 | Clarifying questions | TODO | P1 |
| BRAIN-P6-03 | Multi-turn /start guide | TODO | P1 |
| BRAIN-P6-04 | Developer mode | IN PROGRESS | P1 |
| BRAIN-P6-05 | Agency operator mode | TODO | P2 |
| BRAIN-P6-06 | Investor mode routing | TODO | P2 |
| BRAIN-P6-07 | Language EN-CA default | SHIPPED | P2 |
| BRAIN-P6-08 | Widget ARIA + keyboard | TODO | P1 |
| BRAIN-P6-09 | Offline graceful degrade | IN PROGRESS | P1 |
| BRAIN-P6-10 | Golden transcript tests | TODO | P1 |

## Phase 7 — Admin, analytics & learning loop

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P7-01 | Admin chat logs tab | TODO | P2 |
| BRAIN-P7-02 | Thumbs up/down | TODO | P1 |
| BRAIN-P7-03 | Gap queue | TODO | P1 |
| BRAIN-P7-04 | Site Pulse brain metrics | IN PROGRESS | P1 |
| BRAIN-P7-05 | Founder alert mirror | DEFERRED | P2 |
| BRAIN-P7-06 | Weekly corpus diff report | TODO | P2 |
| BRAIN-P7-07 | A/B retrieval metrics | TODO | P2 |
| BRAIN-P7-08 | Search Console → FAQ | TODO | P2 |
| BRAIN-P7-09 | llms.txt auto-update | TODO | P2 |
| BRAIN-P7-10 | Weekly analytics JSON | TODO | P2 |

## Phase 8 — Commercial intelligence (SourceA buyers)

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P8-01 | Agency wedge vocabulary | TODO | P2 |
| BRAIN-P8-02 | Build vs Rent vs Own explainer | SHIPPED | P0 |
| BRAIN-P8-03 | Forge handoff explainer | SHIPPED | P0 |
| BRAIN-P8-04 | Proof/receipt framing | SHIPPED | P0 |
| BRAIN-P8-05 | Competitor-safe answers | SHIPPED | P1 |
| BRAIN-P8-06 | Objection handling playbook | TODO | P1 |
| BRAIN-P8-07 | DEMO async path | IN PROGRESS | P0 |
| BRAIN-P8-08 | Qualification intent tags | TODO | P2 |
| BRAIN-P8-09 | Handoff to intake form | TODO | P1 |
| BRAIN-P8-10 | Outbound policy sync | IN PROGRESS | P1 |

## Phase 9 — Multi-channel parity

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P9-01 | Shared brain module | SHIPPED | P0 |
| BRAIN-P9-02 | Hub ASK same backend | TODO | P2 |
| BRAIN-P9-03 | n8n webhook ask | TODO | P2 |
| BRAIN-P9-04 | Forge Terminal product mode | SHIPPED | P0 |
| BRAIN-P9-05 | Email async defer | DEFERRED | P2 |
| BRAIN-P9-06 | Widget rollout audit | SHIPPED | P1 |
| BRAIN-P9-07 | Embeddable snippet defer | DEFERRED | P2 |
| BRAIN-P9-08 | Voice defer | DEFERRED | P2 |
| BRAIN-P9-09 | Internal Slack ops defer | DEFERRED | P2 |
| BRAIN-P9-10 | verify_chat_channels.sh | TODO | P1 |

## Phase 10 — Production hardening & north star

| ID | Plan | Status | Priority |
|----|------|--------|----------|
| BRAIN-P10-01 | Prod deploy RAG always-on | SHIPPED | P0 |
| BRAIN-P10-02 | Latency SLO streaming | TODO | P1 |
| BRAIN-P10-03 | Cache hot FAQs at build | TODO | P2 |
| BRAIN-P10-04 | DR rebuild < 5 min | SHIPPED | P1 |
| BRAIN-P10-05 | Prompt injection suite | TODO | P1 |
| BRAIN-P10-06 | Privacy page disclosure | TODO | P1 |
| BRAIN-P10-07 | SEO FAQ schema | TODO | P2 |
| BRAIN-P10-08 | AI search citation | TODO | P2 |
| BRAIN-P10-09 | Machine verify stack | IN PROGRESS | P0 |
| BRAIN-P10-10 | North star metric | TODO | P1 |

---

## Exit criteria

Public Brain answers **Forge Terminal**, **pricing**, **homepage vs Forge**, **try without install**, and **Cursor path** with citations at **90%+ P0 eval** — parity with public pages only.

## Commands

```bash
python3 scripts/generate_brain_chatbot_100_plans_v1.py
bash scripts/validate-brain-chatbot-100-plans-v1.sh
bash scripts/brain_cli_v1.sh deploy
python3 scripts/test_brain_chat_quality_v1.py --write-report --json
```
