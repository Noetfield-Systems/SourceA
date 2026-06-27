# Brain chatbot gap report (LOCKED v2)

**Saved:** 2026-06-27T14:15:00Z  
**Supersedes:** v1 (2026-06-27T05:30:00Z)  
**Purpose:** Track public Brain failures vs Cursor parity — not narrative closeout.  
**Master plan:** `brain-os/plan-registry/SOURCEA_BRAIN_CHATBOT_100_PLAN_LOCKED_v1.md`  
**Machine SSOT:** `data/brain-chatbot-100-plans-v1.json` (25/100 done)  
**E2E receipts:** `reports/sourcea-app-e2e-all-pages-v1.json` · `~/.sina/sourcea-app-e2e-all-pages-v1.json`

---

## Baseline evolution

| Version | Date | Chunks | Chars | Retrieval | Notes |
|---------|------|--------|-------|-----------|-------|
| v1 | 2026-06-27 early | 31 | ~7k | prompt-only | Pre-manifest |
| v2 | 2026-06-27 | 371 | ~179k | BM25 + SQLite FTS5 | Manifest + distill pipeline |
| **v3** | 2026-06-27 | **503** | **~218k** | rules-first BM25 + intent | `brain_intelligence_v3` · bundle 3.0.0 |
| **v4 (now)** | 2026-06-27 | **503** | **~218k** | page-aware BM25 + guardrails + fallback | `brain_intelligence_v4` · bundle 4.0.0 |

**Source files (v3):** 121 total · 112 live www/json · 6 rule chunks · lanes: rules 6 · core 290 · developer 149 · buyer 53 · investor 5

---

## Production E2E — sourcea.app (2026-06-27)

| Bundle | Result | Receipt / script |
|--------|--------|------------------|
| All pages HTTP (225 routes) | **PASS** | `~/.sina/sourcea-app-e2e-all-pages-v1.json` |
| Forge mobile 375/466px | **PASS** | `validate-sourcea-forge-mobile-v1.sh` |
| Brain worker (workers.dev direct) | **PASS** | OpenRouter · CORS · stranger prompts OK |
| Brain live validator | **PARTIAL** | P0-GAP-A below |
| Same-origin `/api/brain/chat/v1` | **OPEN** | P0-GAP-B below |
| Same-origin `/health` | **OPEN** | P0-GAP-B below |

**Visitor impact:** Brain chat **works** — widget uses `api_worker_url` on Cloudflare Worker. Open gaps affect same-origin API, docs accuracy, and CI honesty — not primary chat UX.

---

## Open P0 gaps (fix before next publish)

### P0-GAP-A — Eval vs rule mismatch (`records-recovery`)

| Field | Value |
|-------|-------|
| **Symptom** | `validate-sourcea-brain-live-v1.sh` fails on 3rd stranger prompt |
| **Worker** | `ok:true` — reply uses **proof** + **Forge** (correct) |
| **Root cause** | Validator requires `"record" in reply`; rule SSOT says reframe with **proof** |
| **Rule** | `data/brain-public-rules-v1.json` → `records-recovery` |
| **Fix** | `scripts/validate-sourcea-brain-live-v1.sh` ~L109: accept `record\|receipt\|proof\|verif` |
| **Plan step** | BRAIN-P4-02 / edge steps 004 in routing phase |

### P0-GAP-B — Same-origin API returns HTML

| Field | Value |
|-------|-------|
| **Symptom** | `curl sourcea.app/api/brain/chat/v1` → 200 `text/html` (SPA shell) |
| **Symptom** | `curl sourcea.app/health` → 200 `text/html` |
| **Root cause** | `sourcea-app-proxy-v1` passthrough to Pages static; Pages Functions not serving JSON on live deploy |
| **Fix (primary)** | Proxy Brain + `/health` in `cloud/workers/sourcea-app-proxy-v1/src/index.js` before Pages fetch |
| **Fix (belt)** | Redeploy Pages with `functions/` — verify `sourcea-com.pages.dev/api/brain/chat/v1` → JSON |
| **Plan step** | BRAIN-P1-04 API surface ingest · BRAIN-P10-09 machine verify stack |

### P0-GAP-C — E2E crawl false positives

| Field | Value |
|-------|-------|
| **Symptom** | All-pages crawl marked `/api/*` and `/health` PASS on HTML 200 |
| **Fix** | Assert `Content-Type: application/json` + JSON parse for API paths |
| **Plan step** | BRAIN-P10-09 |

---

## Architecture (corrected — 2026-06-27)

```text
sourcea.app/*
  → sourcea-app-proxy-v1 (zone Worker)
       → /api/chat-unify-*     → Railway ✅
       → /api/brain/chat/v1    → ❌ HTML today (should proxy to brain worker)
       → /health               → ❌ HTML today (should return JSON)
       → else                  → sourcea-com.pages.dev (static)

sourcea-chatbot.js (production)
  → api_worker_url (workers.dev) ✅ bypasses broken same-origin path

sourcea-brain-chat-v1 Worker
  → retrieval.js + knowledge-bundle.json (503 chunks)
  → OpenRouter
```

**Law:** `docs/SOURCEA_APP_CLOUDFLARE_PAGES_ONLY_LOCKED_v1.md` · `cloud/pages-functions/api/brain/chat/v1.js`

---

## Closed gaps (v1 → v3)

| Gap | Bot before | Fix | Status |
|-----|------------|-----|--------|
| No RAG / manifest | Prompt-only | Manifest + bundle + hybrid retrieval | ✅ v2 |
| No health knowledge fields | `openrouter_ready` only | `knowledge.*` on GET status | ✅ |
| No eval harness | 4 smoke curls | `test_brain_chat_quality_v1.py` | ✅ |
| Pricing drift | Hardcoded prompt | `pricing-matrix.md` distill | ✅ |
| Forge vs homepage | Implicit | `forge-runtime.md` + eval | ✅ |
| Internal leak risk | Long prompt | Allowlist + secret strip | ✅ |
| Keyword-only retrieval | Lite match | BM25 + rules-first + intent | ✅ v3 |

---

## Known P0 regressions to watch (eval)

| ID | Question | Required behavior |
|----|----------|-------------------|
| what-is-sourcea | What is SourceA? | Forge + execution; **no lead price** |
| ide-cloud | Do you have IDE cloud? | Forge Terminal path; **no "we don't offer"** |
| records-recovery | You just give me records?? | Acknowledge pushback + reframe: **Forge runs work, proof shows what ran** (word *record* not required) |
| try-without-install | Try Forge without install? | Browser demo URL `/sourcea/forge/terminal`; must not refuse |

---

## Stale sources flagged

- `founder-home.html` if diverges from `sourcea-positioning-v1.json` v3.2+
- Any copy still saying "book a call" as primary CTA (agentic-first law · `brain-public-rules-v1.json`)
- Manifest `deploy_path.vercel_proxy` docs vs live edge routing (align on publish)

---

## Not in public KB (by design)

- Mac control plane ports (`:13020`, `:13027`)
- `brain-os/` incidents and governance law (except public-safe plan summaries)
- OpenRouter keys, wrangler secrets
- Factory autorun / Cloud Forge Run internals

---

## Next gaps (mapped to 100-plan phases)

| Priority | Gap | Target | Plan IDs |
|----------|-----|--------|----------|
| P0 | Same-origin API + health JSON | Edge proxy patch + deploy | P1-04 · P10-09 |
| P0 | Eval assertion drift | Align validator to rules SSOT | P4-02 · P4-10 |
| P0 | Widget citations visible | Show `citations[]` in bubble | P2-07 · P6-08 |
| P1 | Vector RAG | pgvector + hybrid rerank | P2-01–P2-03 |
| P1 | 100 canonical eval questions | Expand eval JSON | P2-10 · P6-10 |
| P1 | Intent classifier v2 | buyer / developer / investor boost | P2-06 |
| P2 | Live health in answers | Worker cache + tool | P5-01 · P5-06 |
| P2 | Deflection metrics | Site Pulse + intake funnel | P7-02 · P7-04 · P8-09 |

**Progress:** 25/100 plans done per `data/brain-chatbot-100-plans-v1.json`

---

## Scoreboard

| Area | Now | Target |
|------|-----|--------|
| Knowledge chunks | 503 | 800+ curated |
| P0 eval | ~90% (1 flaky assert) | ≥90% stable |
| Same-origin API | ❌ HTML | ✅ JSON |
| Citations in widget | API only | Visible UI |
| Vector RAG | ❌ | Hybrid BM25+embed |
| 100-plan completion | 25% | 100% + exit sign-off |

---

## Update protocol

When founder reports "Brain got X wrong":

1. Reproduce on live worker (`api_worker_url` from config JSON)
2. Classify: **PUBLIC_SHOULD_KNOW** vs **INTERNAL_ONLY**
3. If public — manifest + distill + sync + eval + **this file** + bump plan row in `brain-chatbot-100-plans-v1.json`
4. If internal — add anti-ICP eval question
5. After fix — run `validate-sourcea-brain-live-v1.sh` + `test_brain_chat_quality_v1.py --write-report`

---

## Operator commands

```bash
bash scripts/brain_chatbot_refresh_v1.sh
python3 scripts/test_brain_chat_quality_v1.py --write-report --json
SOURCEA_E2E_BASE=https://sourcea.app bash scripts/validate-sourcea-brain-live-v1.sh
python3 scripts/generate_brain_chatbot_100_plans_v1.py
bash scripts/validate-brain-chatbot-100-plans-v1.sh
```

Deploy worker after every bundle sync; deploy edge proxy after API routing changes.
