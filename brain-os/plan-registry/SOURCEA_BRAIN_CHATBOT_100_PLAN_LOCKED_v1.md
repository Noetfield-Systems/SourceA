# SourceA Brain chatbot — 10 phases · 100 plans (LOCKED v1)

**Saved:** 2026-06-27T05:30:00Z  
**Adapted from:** Noetfield NF-ENG chatbot knowledge program  
**Manifest:** `data/CHATBOT_KNOWLEDGE_MANIFEST.json`  
**Skills:** `sourcea-brain-chatbot-audit` · `sourcea-cursor-agent-knowledge-audit`

---

## Phase 1 — Audit & SSOT map (Plans 001–010)

| Plan | Action | SourceA path / status |
|------|--------|------------------------|
| 001 | Inventory chatbot code paths | `sourcea-chatbot.js`, worker, hub `sourcea_brain_chat_v1.py` |
| 002 | Document live deploy path | www → Pages proxy → CF worker → OpenRouter |
| 003 | Map indexed files vs live pages | manifest `sources[]` · `/`, `/sourcea/pricing`, `/forge/terminal` |
| 004 | Flag stale sources | gap report · positioning JSON vs founder-home |
| 005 | List public-safe vs internal docs | manifest allowlist / internal prefixes |
| 006 | Define CHATBOT_KNOWLEDGE_MANIFEST.json | **SHIPPED** `data/CHATBOT_KNOWLEDGE_MANIFEST.json` |
| 007 | Cross-link positioning SSOT | `SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md` |
| 008 | Pull public product catalog slice | `sourcea-products-catalog-v1.json` |
| 009 | Baseline health endpoint | GET worker → `knowledge.chars`, `bundle_version`, `mode` |
| 010 | Publish gap report | **SHIPPED** `docs/BRAIN_CHATBOT_GAP_REPORT_LOCKED_v1.md` |

## Phase 2 — Knowledge corpus expansion (011–020)

| Plan | Topic | Output |
|------|-------|--------|
| 011 | forge-runtime.md | Forge Terminal vs homepage |
| 012 | developer-tools.md | Cursor bridge, /eval, kernel |
| 013 | intelligence-lane.md | Agency / SME positioning (future) |
| 014 | pricing-matrix.md | Synced from pricing.html |
| 015 | faq-live.md | Distill FAQ page when live |
| 016 | sandbox-freemium.md | 48h MVP / sandbox paths |
| 017 | trust-ledger-public.md | Proof / receipt public slice |
| 018 | copilot-pack.md | Procurement FAQ (future) |
| 019 | site-map.md | www routes table |
| 020 | products-catalog.md | Platform products table |

**Status:** 011–012, 014, 016, 019–020 shipped in `data/chatbot-knowledge/`

## Phase 3 — Distillation pipeline (021–030)

| Plan | Script | Status |
|------|--------|--------|
| 021 | `distill_www_to_brain_knowledge_v1.py` | SHIPPED |
| 022 | `distill_docs_to_brain_knowledge_v1.py` | SHIPPED |
| 023 | Strip secrets / internal paths | In distill_docs |
| 024 | Frontmatter lane, updated, public | All chunks |
| 025 | `brain_chatbot_refresh_v1.sh` | SHIPPED |
| 026 | CI: pricing matches pricing-matrix | TODO cloud CI |
| 027 | CI: manifest source missing | `sync --check-only` |
| 028 | Version bump bundle_version | manifest + bundle |
| 029 | Remove _EXTRA_MD dependency | N/A SourceA |
| 030 | External repo distill | TODO if noetfeld-os public slice needed |

## Phase 4 — Chunking & sync (031–040)

| Plan | Action | Status |
|------|--------|--------|
| 031 | sync reads manifest + dirs | SHIPPED |
| 032 | Chunk by ## max 2k | SHIPPED in sync |
| 033 | lane, url_citations, content_hash | SHIPPED |
| 034 | knowledge_sync_runs audit table | TODO platform Postgres |
| 035 | Deploy runbook wire | RUNBOOK.md |
| 036 | Health chunk count by lane | worker `knowledge.lanes` |
| 037 | Soft delete on source removal | TODO |
| 038 | Nightly Railway sync | TODO |
| 039 | L2 allowlist backfill only | manifest enforced |
| 040 | CHATBOT_KNOWLEDGE_RUNBOOK.md | SHIPPED |

## Phase 5 — Vector RAG (041–050)

| Plan | Action | Status |
|------|--------|--------|
| 041–045 | pgvector + embeddings | TODO platform |
| 046 | retrieve_chunks hybrid | **LITE:** keyword + pinned in worker |
| 047 | Replace prompt overflow | SHIPPED hybrid inject |
| 048 | Citations in response | SHIPPED `citations[]` |
| 049 | Langfuse retrieval scores | TODO |
| 050 | A/B shadow hybrid vs keyword | TODO |

## Phase 6 — Prompt & policy (051–060)

| Plan | Action | Status |
|------|--------|--------|
| 051 | SKU list from manifest | products-catalog chunk |
| 052 | Lanes: buyer/developer/investor | retrieval lane boost |
| 053 | Procedural dev answers | developer-tools chunk |
| 054 | Hard bans | prompt + anti-ICP eval |
| 055 | Homepage vs Forge compare | forge-runtime + eval |
| 056 | Multi-turn memory | history[12] existing |
| 057 | Telegram bot parity | N/A |
| 058 | Proxy-only rules | worker + hub mirror |
| 059 | Widget citation links | TODO UI |
| 060 | Welcome reflects lanes | positioning JSON greet |

## Phase 7 — Quality & eval (061–070)

| Plan | Action | Status |
|------|--------|--------|
| 061 | test_brain_chat_quality_v1.py | SHIPPED |
| 062 | Canonical questions JSON | SHIPPED 11 questions |
| 063 | Buckets P0–P3 | SHIPPED |
| 064 | Golden required/forbidden phrases | In eval JSON |
| 065 | Nightly staging eval | TODO cloud CI |
| 066 | Block deploy if P0 <90% | TODO CI gate |
| 067 | PyPI org regression | Add when public |
| 068 | GEL/Forge acronym regression | forge-runtime eval |
| 069 | chat_eval_last_run.json | SHIPPED path |
| 070 | Founder review queue failed Q | TODO |

## Phase 8 — Live truth sync (071–080)

| Plan | Action | Status |
|------|--------|--------|
| 071 | Weekly PRODUCT_TRUTH public slice | TODO |
| 072 | API health in live-surfaces | TODO |
| 073 | Bot says API up/down from cache | TODO tool |
| 074 | www E2E → freshness metadata | TODO |
| 075 | Auto-update gel-runtime from /gel/ | N/A — use forge-runtime |
| 076–078 | PyPI/npm links when shipped | TODO |
| 079 | Cloud inventory public summary | site-map |
| 080 | freshness_sla_hours 168 alerts | manifest set |

## Phase 9 — Smarter behaviors (081–090)

| Plan | Action | Status |
|------|--------|--------|
| 081 | Intent classifier pre-retrieve | TODO |
| 082 | Off-topic polite redirect | prompt rule |
| 083 | Structured cards (Pricing/Intake/Docs) | TODO widget |
| 084 | Form-filling template mode | TODO |
| 085 | GET ecosystem health tool | TODO |
| 086 | Sitemap search tool | TODO |
| 087 | Rate-limit by lane | TODO worker |
| 088 | Thumbs → Langfuse | Site Pulse partial |
| 089 | Session RID footer tie-in | TODO |
| 090 | Partner/investor intake URLs | investors chunk |

## Phase 10 — Operate & scale (091–100)

| Plan | Action | Status |
|------|--------|--------|
| 091 | CHATBOT_KNOWLEDGE_OWNER | RUNBOOK |
| 092 | Weekly chatbot-refresh | `brain_chatbot_refresh_v1.sh` |
| 093 | Monthly prune unused chunks | TODO |
| 094 | Quarterly OFFERINGS reconciliation | positioning JSON |
| 095 | Anti-pattern doc | RUNBOOK + skills |
| 096 | Train ops: SSOT→distill→sync→eval | RUNBOOK |
| 097 | Public changelog date | TODO status page |
| 098 | Deflection rate metrics | TODO |
| 099 | Auth console assistant separate KB | Phase 2 optional |
| 100 | **Exit:** GEL/Forge/pricing/homepage @90%+ P0 | **IN PROGRESS** |

---

## Exit criteria

Public Brain answers **Forge Terminal**, **pricing**, **homepage vs Forge**, **try without install**, and **Cursor path** with citations at **90%+ P0 eval** — parity with what Cursor would say from **public pages only**, not private build context.

---

## Commands

```bash
bash scripts/brain_chatbot_refresh_v1.sh
python3 scripts/test_brain_chat_quality_v1.py --write-report --json
```

Deploy worker after every bundle sync.
