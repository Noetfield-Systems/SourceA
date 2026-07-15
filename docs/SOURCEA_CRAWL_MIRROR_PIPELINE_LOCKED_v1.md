# SourceA Crawl–Mirror Pipeline — architecture, Wil AI analysis, commercial build draft (LOCKED v1)

**Version:** 1.4 · **Saved:** 2026-06-16T10:00:00Z · **v1.4:** session gate wired (step 14 DONE) · W10 crawl validator wired · gap audit cross-link  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_CRAWL_MIRROR_PIPELINE_LOCKED_v1.md`  
**Authority:** ASF SAVE order  
**Related:** `AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md` · `AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md` · `SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md` · `docs/SOURCEA_ECOSYSTEM_GAP_AUDIT_AND_SYSTEM_MAP_LOCKED_v1.md` · `.cursor/skills/skill-architecting-pipelines-pro/SKILL.md` · `product/SINA_AUDIENCE_HUB_FREE_TIER_SPEC.md` · `product/PHASE1_MARKET_RESEARCH_2026.md`  
**Reference implementation (external):** `~/Desktop/YA5/` (Wil AI local site — mirror + brand pipeline)

---

## 0. One sentence

> **Crawl discovers truth from messy sources; mirror projects ranked truth into every surface agents and customers read — with validators as the ship gate, not chat.**

### Vocabulary (mandatory — v1.2)

| Forbidden | Use instead | Why |
|-----------|-------------|-----|
| **rebrand** / **rebrand:*** | **local-brand** / **brand:disk** / **brand:assets** | Implies unauthorized rewrite — conflicts with mirror fidelity + supersession law |
| bulk rebrand / bulk rewrite | **disk local-brand pass** | Display-layer only; canonical URLs and SSOT paths stay untouched |
| rebrand fork / white-label fork | **local-brand mirror overlay** | Mirror stays tied to source — not a fork |
| bulk find-replace on law | **supersession cascade** | SourceA LOCKED docs only |

**Rule:** Change what the user **sees** (display name, local CSS, manifest title). Never rename SSOT paths, canonical URLs, production APIs, or LOCKED law files via display passes.

---

## 1. Why SourceA needs a unified crawl–mirror pipeline

| Problem logged today | What crawl–mirror fixes |
|-----------------------|-------------------------|
| Chat ≠ SSOT but chats hold intent | Crawl transcripts → extract decisions → mirror to disk rows |
| 102+ LOCKED laws + hub + `.mdc` + validators | Crawl law graph → mirror seven surfaces together |
| 5+ repos (SourceA, Mono, TrustField, mergepack, YA5…) | Crawl portfolio state → one progress truth |
| Hub JSON vs `~/.sina` vs brain inject drift | Mirror pipeline keeps them aligned every session |
| Hospital criticals (NAV, WTM, authority index) | Validators become downstream gate, not whack-a-mole |
| Founder never Terminal | Crawl runs on machine schedule; founder sees H1 only |

**Philosophy:** SoT foundation (018) — truth emerges from execution first. Crawl captures execution artifacts; mirror propagates them. Chat summaries are leaf noise; disk receipts are thorn truth.

**What already exists (mirror half):**

| Component | Script | Output |
|-----------|--------|--------|
| Disk live wire | `disk_live_wire_sync_v1.py` | `agent-live-surfaces-v1.json` |
| Memory mirror | `agent_memory_mirror_v1.py` | `agent-memory-mirror-v1.json` |
| Anti-staleness orchestrator | `anti_staleness_auto_wire_v1.py` | L0.5→L1→L2 receipt |
| Ecosystem catalog | `ecosystem_master_catalog_v1.py` | Portfolio inventory JSON |
| Research mirror | `research_root_sync.py` | RESEARCH vault rows |
| Governance projection | `governance_projection_g3_v1.py` | Hub/catalog materializer |

**Gap:** No single **crawl → extract → rank → mirror → prove** orchestrator feeding all of the above from one graph.

---

## 2. Pipeline architecture (six stages)

```text
CRAWL → EXTRACT → RANK → MIRROR → PROVE → SERVE
```

### Stage 1 — Crawlers (discover, read-only)

| ID | Crawler | Sources | Why |
|----|---------|---------|-----|
| C1 | Law graph | `*_LOCKED*.md`, `.cursor/rules`, authority index | Canonical law DAG — which doc wins |
| C2 | Repo inventory | SourceA, Mono, TrustField, mergepack, YA5, SinaPromptOS | Portfolio map; extends ecosystem catalog |
| C3 | Execution log | `REPO_EXECUTION_LOGS/`, broker receipts, closeout | Pre-LLM truth — intent vs evidence |
| C4 | Factory queue | `factory-now-v1.json`, worker inbox, next-10 | Single queue SSOT |
| C5 | Hub API | `GET /api/worker-hub/v1`, rules-in-charge, WTM | Detect hub↔disk drift |
| C6 | Transcript | `~/.cursor/projects/*/agent-transcripts/*.jsonl` | FOUND corrections only — not full paste |
| C7 | Validator output | `find_critical_bugs`, `validate-*` receipts | Machine health graph |
| C8 | Lane attest | TrustField Track, MergePack KPI, DevBridge | Commercial proof vs “built” |
| C9 | Research vault | `RESEARCH/by_date/` | Brief intake without duplicating law |
| C10 | Runtime spine | `~/.sina/tool_graph*.json`, C1–C7, dispatch_policy | Pre-LLM spine state |

**Crawl rule:** Append receipts only on source read. Never mutate crawl source in place.

### Stage 2 — Extractors (normalize)

| ID | Extractor | Output SSOT |
|----|-----------|-------------|
| E1 | Governance unify | `~/.sina/governance-unify-v1.json` (conceptual) |
| E2 | Truth bundle | `last-truth-bundle-v1.json` |
| E3 | Program progress | `PROGRAM_PROGRESS.json` |
| E4 | Incident adjacency | Near-miss + open P0 rows |
| E5 | Decision extractor | `governance-brain-wire-v1.json` `active_decisions[]` |

### Stage 3 — Authority ranker (truth tree)

| ID | Rule |
|----|------|
| R1 | Thorn filter: ASF order > LOCKED vN > machine SSOT > smart judgment > attachments > chat |
| R2 | Supersession: vN wins; `archive/superseded/` excluded |
| R3 | Conflict: same topic, two active laws → SKILL-007 queue |
| R4 | Stale phrase: dead AUTO-RUN, legacy hub brand, prohibition inject (INCIDENT-034) |

### Stage 4 — Mirrors (project ranked truth)

| ID | Target | Writer |
|----|--------|--------|
| M1 | `agent-memory-mirror-v1.json` | `agent_memory_mirror_v1.py --sync` |
| M2 | `agent-live-surfaces-v1.json` | `disk_live_wire_sync_v1.py` |
| M3 | `brain-live-context-v1.json` | `brain_live_context_v1.py` |
| M4 | `worker-live-context-v1.json` | `worker_live_context_v1.py` |
| M5 | Hub command-data / worker-hub API | `build-sina-command-panel.py` (scheduled) |
| M6 | `MANDATORY_READ_BY_ROLE` | Maintainer on law ship |
| M7 | `.cursor/rules` + validators | Supersession cascade |
| M8 | `l1-agent-pipeline-wire-v1.json` | `agentic_layer_pipeline_v2.py` |
| M9 | WTM / system-roadmap hub tab | `governance_projection_g3_v1.py` |
| M10 | Research mirror (summary + pointer) | `research_root_sync.py` |
| M11 | Lane workspace mirrors | `audit_private_agent_pages.py` pattern |

**Mirror rule:** One crawl receipt → many mirrors in one transaction. Fail-closed if any mirror validation fails.

### Stage 5 — Proof gates

| ID | Gate |
|----|------|
| V1 | `validate-law-supersession-surfaces-v1.sh` |
| V2 | `validate-anti-staleness-bundle-v1.sh` |
| V3 | `find_critical_bugs.py` (fast session / full nightly) |
| V4 | `validate-disk-live-wire-v1.sh` |
| V5 | `queue_ssot_unify_v1.py` truth_match |

**Exit:** `critical_count: 0` + `mirror.validation.ok: true` → hospital quarantine clear.

### Stage 6 — Serve (consumers)

| Consumer | Reads | Trigger |
|----------|-------|---------|
| Session gate | anti-staleness + mirror inject | Every agent session |
| Worker | inbox + worker-live-context | RUN INBOX |
| Brain | brain-live-context + governance-brain-wire | Spawn / handoff |
| Founder H1 | worker-hub API + next-10 | Refresh |
| Hospital / Maze | crawl health + critical graph | Founder one word |
| Commercial | lane attest + GTM mirror | Weekly |

### Proposed orchestrator

```bash
python3 scripts/sourcea_crawl_mirror_pipeline_v1.py --tier session --role any --json
```

| Tier | When | Depth |
|------|------|-------|
| `session` | Session gate (≤90s) | C4 + C7 fast + M1–M4 |
| `worker` | Worker turn | session + C3 execution tail |
| `nightly` | Cron / hub Action | Full C1–C10 + V3 full |
| `law_ship` | Maintainer law edit | C1 + M1–M7 + V1 |

Wraps `anti_staleness_auto_wire_v1.py` — does not replace it.

### Forbidden crawl targets

- Full mega-chat paste into inject
- `archive/superseded/` as active law
- Customer-facing crawl of internal orchestrator vocabulary
- Hub `command-data.json` as crawl **source** (mirror sink only)
- AUTO-RUN / prompt-feed confirm paths (INCIDENT-024/028)

---

## 3. Analysis — Wil AI brand pipeline vs SourceA crawl–mirror

### 3.1 What Wil AI (YA5) actually is

Wil AI is a **local product skin on mirrored content** — three layers:

| Layer | Mechanism | Persistence |
|-------|-----------|-------------|
| **L1 Disk** | `brand:disk` + `brand:assets` (local-brand pass) | ~11k HTML — display strings + asset paths only |
| **L2 Serve** | `enhanceHtmlForLocal()` + `applyBrandToManifest()` | Every HTTP response |
| **L3 Browser** | `local-brand.js` wordmark, badge, title guard | Runtime DOM |

**SSOT:** `scripts/lib/config.mjs` — `BRAND`, `BRAND_TAGLINE`, `BRAND_THEME`. Logic in `brand.mjs`; constants never duplicated.

**Fidelity rule:** Change what the user **sees** as brand; keep canonical URLs, production API fallbacks, `@markaicode` handles, PWA protocol — mirror stays tied to source.

**Verification:** `verify:pipeline` = staleness (17) + `audit:names` + `audit:all-pages` (11,150 HTML) + browser flows (25) + Wil AI E2E (5).

**Current disk note (2026-06-16):** YA5 `config.mjs` sets `SITE_FROZEN = true` — local frozen snapshot; external crawl disabled. Pipeline **pattern** remains valid; refresh workflow is `mirror → brand:disk → brand:assets → build:search → verify:pipeline` when unfrozen.

### 3.2 Structural mapping — same pattern, different domain

| Wil AI (customer site) | SourceA (agent OS) | Shared principle |
|------------------------|-------------------|------------------|
| Crawl markaicode.com → `site/` | Crawl repos + hub + receipts → `~/.sina/` | **Mirror source to disk first** |
| `config.mjs` BRAND constants | `agent-memory-mirror-v1.json` inject block | **Single SSOT for vocabulary** |
| `brand:disk` local-brand pass | Law supersession + seven-surface sync | **Persistent layer — search/indexable** |
| `enhanceHtmlForLocal` serve-time | Session gate + live context inject | **Safety net on every read** |
| `local-brand.js` runtime | Brain/Worker stale scrub + title guard | **Edge cases agents miss** |
| Keep canonical URLs | Keep production APIs + dispatch_ready false | **Fidelity over fork** |
| `verify:pipeline` ship gate | `find_critical_bugs` + anti-staleness bundle | **No ship without proof** |
| Pagefind rebuild after disk | Queue SSOT unify after mirror | **Derived indexes must refresh** |

### 3.3 What Wil AI teaches SourceA commercially

1. **Three-layer stack is the right product pattern** — disk local-brand pass (indexable) + serve inject (always fresh) + runtime guard (edge cases). SourceA internal pipeline should mirror this exactly.

2. **Capital-M / URL-safe rules** — Wil AI only replaces display brand, not infrastructure identifiers. SourceA equivalent: positive inject (Worker Hub, RUN INBOX) without breaking factory SSOT paths or `sa-*` IDs.

3. **verify:pipeline as SKU DNA** — Wil AI sells because users trust **11,150 pages audited**. SourceA commercial angle: **RunReceipt + crawl-mirror receipt** = “we proved the mirror matches source.” Aligns with Phase 1 market research: **evidence beats generation**.

4. **Separate repo, shared law** — YA5 is portfolio L3 (customer-facing). SourceA is L0.5 governance. Commercial build = **new repo or `product/wil-ai-hub/`** consuming SourceA validators — not bloating SourceA hub with 11k HTML.

5. **Frozen vs live crawl** — Wil AI can freeze for dev velocity. SourceA factory queue must stay **live** (SINGLE_SA); only **customer content mirror** can freeze between releases.

### 3.4 Gaps Wil AI has that SourceA crawl–mirror must add

| Wil AI has | SourceA needs |
|------------|---------------|
| Single origin (markaicode.com) | Multi-origin (5+ repos + hub + transcripts) |
| Display-only local-brand layer | Authority-ranked truth (thorn→leaf) |
| HTML/CSS/JS domain | JSON receipts + LOCKED law + agent inject |
| npm verify | Python validators in `find_critical_bugs` chain |
| No role separation | L1 Brain wire + L2 Worker execute |

### 3.5 Risk if conflated

- **Do not** run Wil AI `brand:disk` (display local-brand pass) on SourceA LOCKED laws — use supersession cascade only.
- **Do not** expose SourceA session gate inject on public Wil AI pages.
- **Do not** treat Wil AI mirror as SSOT for factory queue — opposite direction.

---

## 4. Commercial purpose — what to sell

From `PHASE1_MARKET_RESEARCH_2026.md` and `PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md`:

| Buyer pain | Crawl–mirror commercial artifact |
|------------|----------------------------------|
| “Prove AI did the work” | **RunReceipt** + mirror fidelity receipt |
| “Is this site/docs copy current?” | **Mirror audit pack** (Wil AI `verify:pipeline` pattern) |
| “Local-brand overlay without breaking links” | **Local-brand mirror pipeline** (YA5 as reference) |
| “Trust but verify agent output” | **Crawl–mirror receipt JSON** per release |

**Not sold:** SourceA orchestrator, Brain/Worker lanes, dispatch spine, 102 LOCKED laws.

**Sold:** Outcome artifacts — audited local site, PASS/FAIL receipt, branded mirror with canonical fidelity.

---

## 5. Commercial build draft — phased

### Phase 0 — Spec lock (1 week, no code in SourceA root)

| Deliverable | Owner | Proof |
|-------------|-------|-------|
| This doc promoted to build charter | ASF | File logged ✓ |
| Brand SSOT for commercial skin | Commercial | `config.mjs` pattern per product |
| SKU pick: Wil AI hub vs RunReceipt vs both | Brain pick on Form | `PROGRAM_PROGRESS` row |
| Legal: mirror fidelity disclaimer | Governance | Pointer in `/terms` |

### Phase 1 — Extract YA5 pattern into reusable module (2 weeks)

**Repo:** `~/Desktop/YA5/` (existing) or `product/commercial-mirror-kit/`

| Task | Output |
|------|--------|
| Document `mirror → brand:disk → brand:assets → build:search → verify:pipeline` as `COMMERCIAL_MIRROR_KIT_README.md` | Portable workflow |
| Extract `config.mjs` + `brand.mjs` + `html.mjs` into `@sina/local-brand-kit` npm package (private) | Reusable L1–L3 |
| Add `receipt.json` emitter to `verify:pipeline` | RunReceipt-compatible proof |
| Wire `audit:all-pages` count + 0-legacy-name into receipt schema | Customer-facing PASS badge |

**Acceptance:** `npm run verify:pipeline` exits 0 + writes `~/.sina/commercial-mirror-receipt-v1.json`.

### Phase 2 — SourceA internal crawl–mirror v0 (3 weeks, Maintainer 2)

**Repo:** `~/Desktop/SourceA/scripts/`

| Task | Script | Proof |
|------|--------|-------|
| Orchestrator skeleton | `sourcea_crawl_mirror_pipeline_v1.py` | `--tier session` ≤90s |
| Wire C4 factory + C7 fast + M1–M4 | Calls existing scripts | Hospital H7b improves |
| Receipt schema | `~/.sina/crawl-mirror-receipt-v1.json` | JSON schema validated |
| Validator | `validate-crawl-mirror-v1.sh` | **Standalone PASS** · **W10 vocab gate wired** (2026-06-16) |

**Acceptance (honest — v1.4):** Scaffold + validator PASS (`sourcea_crawl_mirror_pipeline_v1.py --tier session`). **Wave 1 step 14 DONE:** `agent_session_gate_run_v1.py` calls orchestrator after SASCIP + zero-drift live wire (receipt step `sourcea_crawl_mirror_pipeline`). **Remaining gap:** full C1–C10 crawl graph + nightly tier (Phase 5) · hub-dependent WTM when `:13020` down.

### Phase 3 — Sina Audience Hub P0 (2 weeks, commercial lane)

From `SINA_AUDIENCE_HUB_FREE_TIER_SPEC.md`:

| Task | Output |
|------|--------|
| Next.js homepage — three products, no orchestrator vocab | Public URL |
| Embed Wil AI mirror as **read-only demo** (/demo/ecosystem-intelligence) | YA5 `dev` behind reverse proxy or static export subset |
| Free tier signup stub | Email capture only |
| CTA → TrustField / Noetfield / RunReceipt | Upgrade paths |

**Acceptance:** Founder Refresh shows link; `verify:pipeline` PASS on demo subset.

### Phase 4 — RunReceipt + mirror receipt union (4 weeks)

| Task | Output |
|------|--------|
| Extend RunReceipt schema with `mirror_fidelity` block | Agent run + site audit in one receipt |
| Customer PDF/HTML “proof pack” | G3 attest ready |
| TrustField pilot hook | Track tab attest when pilot ships |

**Acceptance:** One receipt proves agent run **and** branded mirror fidelity.

### Phase 5 — Full crawl graph (6+ weeks)

Implement C1–C10, E1–E5, M5–M11, nightly tier, hospital quarantine auto-clear at critical=0.

---

## 6. Commercial SKU matrix (draft)

| SKU | Buyer | Price narrative | Built from |
|-----|-------|-----------------|------------|
| **Wil AI Local** | Devs, agencies | Free tier / pro hosting | YA5 pipeline |
| **Mirror Audit Pack** | Teams mirroring docs/sites | One-time audit receipt | `verify:pipeline` export |
| **RunReceipt Pro** | AI ops buyers | Subscription per run proof | SourceA closeout + mirror receipt |
| **Local-brand Mirror Kit** | Agencies | License + `@sina/local-brand-kit` | Phase 1 npm kit |
| **Sina Hub Free** | Portfolio audience | $0 → upgrade | Audience Hub spec |

---

## 7. Build priority (founder one pick)

| Priority | Build | Why first |
|----------|-------|-----------|
| **P0** | YA5 `verify:pipeline` → RunReceipt receipt union | Fastest path to sellable proof |
| **P1** | SourceA `sourcea_crawl_mirror_pipeline_v1.py` session tier | Fixes daily drift + hospital |
| **P2** | Sina Audience Hub P0 homepage | Customer front door |
| **P3** | Full C1–C10 crawl graph | Enterprise closure |

---

## 8. Success metrics

| Metric | Target |
|--------|--------|
| Wil AI disk legacy names | 0 (already true on YA5) |
| `verify:pipeline` | exit 0 on golden pages |
| SourceA `find_critical_bugs` critical | 0 |
| Hospital quarantine | cleared without MAZE |
| Commercial receipt | 1 paying pilot citing mirror audit |
| Time mirror refresh → verified | <15 min unattended |

---

## 9. Mental model (Wil AI + SourceA unified)

```text
SOURCES                    TRANSFORM                    SURFACES
─────────                  ─────────                    ────────
markaicode.com      →      mirror.mjs            →      site/           (Wil AI L0)
repos/hub/receipts  →      crawl extractors      →      ~/.sina/        (SourceA L0)
ranked truth        →      local-brand / inject  →      disk + serve    (L1)
edge cases          →      brand.js / scrub      →      browser/agents  (L2)
ship gate           →      verify / validators   →      receipt PASS    (L3)
```

**Wil AI = customer-facing mirror–brand pipeline (L3 portfolio).**  
**SourceA crawl–mirror = governance-facing truth pipeline (L0.5).**  
**Commercial win = union receipt proving both.**

---

## 10. Next actions (machine-ready)

```bash
# Wil AI — prove commercial mirror gate (existing)
cd ~/Desktop/YA5 && npm run verify:pipeline

# SourceA — when Phase 2 ships
cd ~/Desktop/SourceA && python3 scripts/sourcea_crawl_mirror_pipeline_v1.py --tier session --json

# Commercial — Brain pick one P0 row
# PROGRAM_PROGRESS: RunReceipt G3 attest OR Audience Hub P0
```

---

*End SOURCEA_CRAWL_MIRROR_PIPELINE_LOCKED_v1*
