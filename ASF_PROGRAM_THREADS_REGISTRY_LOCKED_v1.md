# ASF — Program threads & phases (LOCKED registry)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
| | |
|--|--|
| **Progress (daily)** | **`ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md`** · `PROGRAM_PROGRESS.json` |
| **Version** | `ASF-THREADS-1.1-LOCKED` |
| **Locked** | 2026-06-04 (audit pass — missing threads + M8 glossary) |
| **M8** | **Automation only** (SinaPromptOS / wire / mono) — **not** MergePack $10K — see glossary v1.1 |
| **Purpose** | One map of **every major conversation arc** → concrete spec, repo, phase, status |
| **Rule** | Pick **one thread** per work session. Do not mix goals across threads in one agent chat. |

**When lost:** read this file → open only the **Active NOW** row’s hook doc.

---

## Authority stack (never confuse)

| Order | What wins |
|-------|-----------|
| 1 | `SINA_OS_SSOT_LOCKED.md` — ecosystem law |
| 2 | Thread-specific **LOCKED** spec (below) |
| 3 | Repo code + `BUILD_CHECKLIST` / `LOCKED.md` |
| 4 | Agent chat memory — **never** |

**Chronology ≠ authority.** See `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md`.

---

## Master index (all threads — use ID in chat)

| ID | Name | Status | P0? |
|----|------|--------|-----|
| `THREAD-SUPERBRAIN` | Personal SoT + Agent Factory | Phase 0 scaffold | No |
| `THREAD-CHAT-CONSOLIDATION` | 100 chats → L2/L3 pipeline | **OPEN** (feeds Super Brain) | No |
| `THREAD-ECOSYSTEM` | Source A / SSOT / 5 repos | Locked | No |
| `THREAD-SOURCE-B` | Ecosystem map + conflicts | Reference | No |
| `THREAD-PROMPTOS` | SinaPromptOS daily Lane 0 | Active Sundays+daily | No |
| `THREAD-ARCHITECT` | Permanent Architect (read-only) | Active | No |
| `THREAD-AGENT-DESK` | Cursor fleet monitor (local) | Active v0 | No |
| `THREAD-PHASE2-TRUTH` | Execution truth + AI evaluator | Locked, background | No |
| `THREAD-WIRE` | AI Dev Bridge wire + full_m8 + G3 | **Mostly PASS** — see §3 | No |
| `THREAD-CURSOR-OS-PRO` | App Store reference app | Parallel build | No |
| `THREAD-FACTORY` | 30 ideas → winner | **DONE** (MergePack) | No |
| `THREAD-MERGEPACK` | MergePack Evidence Factory v1.3 | **Deploy / KPI trio** | Parallel (P0=RunReceipt) |
| `THREAD-AUDIENCE-HUB` | Paused SKU | PAUSED | No |
| `THREAD-INVESTOR` | Deck + PDFs + narrative | Materials done | No |
| `THREAD-PORTFOLIO` | TrustField/VIRLUX/777/Noetfield/Mono blockers | Parallel ops | No |
| `THREAD-TRUSTFIELD-INFRA` | Free infra (CF, no Render card) | Locked rule | No |

**Not a separate thread:** early `SinaaiDataBase/` root docs (SLF, PAIOS) → archived under **THREAD-SUPERBRAIN** `docs/archive/`.

---

## Thread map (big picture)

```text
[0] Super Brain / SoT          → personal OS foundation (Phase 0)
[0b] Chat consolidation        → 100 chats pipeline (OPEN)
[1] Source A / Ecosystem       → governance, 5 repos, force majeure
[1b] Source B                  → conflict map (subordinate to A)
[2] SinaPromptOS / Lane 0      → daily 5-repo + Architect
[2b] Phase 2 truth layer       → execution evidence (background)
[3] AI Dev Bridge / Wire       → phone → Mac Cursor (mostly PASS)
[4] Cursor OS Pro              → App Store product (SEPARATE)
[5] Product Factory            → 30 ideas → MergePack winner
[6] MergePack BUILD            → P0 — MP-$10K Day 7 (ACTIVE) — not automation M8
[7] Investor package           → deck, PDFs (DONE)
[8] Portfolio delivery         → 5 company repos (parallel blockers)
```

---

## Thread 0 — Super Brain & personal SoT (PAIOS)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-SUPERBRAIN` |
| **Phase** | **Phase 0** — infrastructure & Agent Factory (not revenue SKU) |
| **Status** | **ACTIVE background** — scaffold done; L2/L3 content thin |
| **Goal** | Layer A = immutable truth; Layer B = runtime; 4 agents + ingestion |
| **NDAX** | **FROZEN** — external plugin only |

| Layer | Path |
|-------|------|
| A — SoT | `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/data/` (L0–L4) |
| B — Runtime | `~/Desktop/SinaaiMonoRepo/SinaaiRuntime/` |
| Master blueprint | `data/L0-meta/005-project-blueprint.md` |
| LAW | `002-sot-hierarchy-registry`, `001-sina-core`, `docs/law/slf-v5.md` |
| Ingestion | `imports/raw/`, `pipeline/staging/`, `pipeline/clusters/` |

**Next (when this thread is active):** seed L2/L3 from chat exports; Chief-of-Staff loop; **not** MergePack deploy.

**Do not mix with:** Thread 6 (MergePack), Thread 7 (investor pitch = portfolio story, not ingestion detail).

---

## Thread 0b — Chat consolidation (100 chats)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-CHAT-CONSOLIDATION` |
| **Parent** | THREAD-SUPERBRAIN |
| **Status** | **OPEN** — methodology written, not executed at scale |
| **Goal** | Ingest ~100 scattered chats → dedupe → L2/L3 entries |

| Hook | Path |
|------|------|
| Pipeline doc | `SinaaiMonoRepo/SinaaiDataBase/docs/operational/chat-consolidation-pipeline.md` |
| Early copy | `~/Desktop/SinaaiDataBase/chat-consolidation-pipeline.md` (if present) |

**Tasks:** drop raw exports in `imports/raw/` → cluster → promote to `data/L2-knowledge/`.

---

## Thread 1 — Source A & ecosystem governance

| Field | Value |
|-------|--------|
| **ID** | `THREAD-ECOSYSTEM` |
| **Phase** | Phase 0 exit + portfolio ops |
| **Status** | **LOCKED docs**; daily ops via Prompt OS |
| **Goal** | One law, five repos, blockers visible, no duplicate SSOT |

| Hook | Path |
|------|------|
| Master law | `~/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md` |
| **E2E debugger playbook** | **`SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md`** — Rules 0–7 when stuck |
| Doc sequence | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` |
| Force majeure | `SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md` |
| No credit card | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` |
| Global blockers | `GLOBAL_BLOCKERS.json`, `ECOSYSTEM_STATUS.md` |
| Founder cheat | `~/Desktop/SourceA/founder/README.md` |

**Portfolio repos (parallel, not P0 build):** TrustField, VIRLUX, Mono, 777, Noetfield — per `GLOBAL_PRIORITY.json`.

---

## Thread 1b — Source B (conflict map)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-SOURCE-B` |
| **Status** | Alignment doc — **subordinate to Source A** |
| **Hook** | `~/Desktop/SinaaiDataBase/sourceB/SOURCE_B_ECOSYSTEM_AND_CONFLICTS_v1.md` |

When A and B disagree → **Source A wins.**

---

## Thread 2 — SinaPromptOS & five-repo Lane 0

| Field | Value |
|-------|--------|
| **ID** | `THREAD-PROMPTOS` |
| **Phase** | Daily execution plane |
| **Status** | **ACTIVE** (Sunday = planning only) |
| **Goal** | One paste per repo → ingest → architect → truth layer |

| Hook | Path |
|------|------|
| Full day | `~/Desktop/SinaPromptOS/scripts/run-full-day.sh` |
| Lane 0 | This chat class = governance; repo chats = delivery |
| Two chats rule | `founder/ASF_TWO_CHATS.md` |
| Playbook | `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` |

**Do not mix with:** Thread 6 agent doing MergePack Vercel in same breath as “run-full-day” unless ASF explicitly combines.

---

## Thread 2b — Phase 2 execution truth (background)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-PHASE2-TRUTH` |
| **Status** | Locked docs; runs via Prompt OS cycles |
| **Goal** | Evidence layer, feedback aggregate, re-rank — not customer SKU |

| Hook | Path |
|------|------|
| Truth layer | `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` |
| Phase 2 AI | `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` |
| Aggregate | `FEEDBACK_AGGREGATE.json`, `EXECUTION_TRUTH.json` |

---

## Thread 2c — Permanent Architect (read-only)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-ARCHITECT` |
| **Status** | **ACTIVE** — observe only |
| **Goal** | `ARCHITECT_REPORT.yaml` — blockers, route, no dispatch |

| Hook | Path |
|------|------|
| Policy | `SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md` |
| Report | `~/Desktop/SourceA/ARCHITECT_REPORT.yaml` |
| Run | `SinaPromptOS/scripts/run-architect.sh` |

**Never:** write `plan.json`, dispatch Cursor, ingest on architect’s behalf.

---

## Thread 2d — Agent Desk (fleet monitor)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-AGENT-DESK` |
| **Status** | **ACTIVE v0** — local only |
| **Goal** | See all Cursor chat sessions; support parallel founder ops |

| Hook | Path |
|------|------|
| Start | `AGENT_DESK_START_HERE.md` |
| Spec | `AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md` |
| Roles | `AGENT_OPERATING_ROLES_LOCKED_v1.md` |
| Scan | `scripts/scan-cursor-agent-fleet.py` |
| UI | `agent-control-panel/index.html` |

**Never:** upload transcripts off-Mac without ASF consent.

---

## Thread 3 — AI Dev Bridge & wire proof

| Field | Value |
|-------|--------|
| **ID** | `THREAD-WIRE` |
| **Phase** | P0 wire — **mostly complete** |
| **Status** | See `config/locked_plan.json` · `WIRE_LANE_PROGRESS.md` (may be stale) |
| **Goal** | Phone → Mac → Cursor; record proof; Tailscale G3 |

| Hook | Path |
|------|------|
| Product canon | `~/Desktop/AI Dev Bridge OS/docs/PRODUCT_CANON.md` |
| Wire progress | `~/Desktop/SourceA/WIRE_LANE_PROGRESS.md` |
| Locked plan | `~/Desktop/AI Dev Bridge OS/config/locked_plan.json` |
| Founder wire | `founder/ASF_WIRE_AND_PHONE.md` |
| Incidents | `INCIDENT_2026-06-04_AGENT_PLACEHOLDER_RUN_ID.md` |

**iPhone URL (Tailscale):** `http://100.85.10.79:3004/?host=100.85.10.79&port=8766&code=559138&lane=full_m8`

| Proof item | Disk (`locked_plan.json`) | Notes |
|------------|---------------------------|--------|
| G1/G2 smoke | pass | |
| physical_iphone | pass | |
| full_m8_iphone | pass | `run_2026-06-03T23-35-31Z` |
| g3_tailscale | **pending** on disk | Close with `npm run record:g3` if not done |

**M8 here = automation stack / full_m8 lane — NOT $10K MRR.** See `ASF_MILESTONE_GLOSSARY_LOCKED_v1.md`.

**Open wire tasks (if regress):** `founder/ASF_WIRE_AND_PHONE.md` · `proof:iphone-production` · G3 record.

**Not active unless regress:** no more wire sprints unless proof fails.

---

## Thread 4 — Cursor OS Pro (App Store)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-CURSOR-OS-PRO` |
| **Phase** | Separate product lane |
| **Status** | **PARALLEL** — not MergePack |
| **Goal** | Ship IDE-for-Cursor to App Store |

| Hook | Path |
|------|------|
| Repo | `~/Desktop/Cursor OS Pro/` |
| Boundaries | `docs/PARALLEL_LANE_BOUNDARIES.md` |
| Investor separation | `investor/SEPARATE_PROGRAM_CURSOR_OS_PRO.md` |

**Rule:** Never describe MergePack as Cursor OS Pro. Never use wire ports (3004/8766) for App Store build.

---

## Thread 5 — Product factory (30 ideas → winner)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-FACTORY` |
| **Phase** | Ideation **DONE** → execution on winner |
| **Status** | **LOCKED** — MergePack selected |
| **Goal** | Pick fast-revenue SKU with SEO + clear MRR path |

| Hook | Path |
|------|------|
| 30 ideas | `product/PHASE1_OPPORTUNITIES_AND_30_RAW_IDEAS.md` |
| Evaluation | `product/PHASE2_3_EVALUATION_AND_WINNER.md` |
| Defense | `product/MERGEPACK_BUSINESS_DEFENSE_MEMO.md` |
| Queue | `PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md` |

**Winners:** P0 MergePack · P1 FormToPDF · P1 CSVDoctor · Audience Hub **PAUSED**.

---

## Thread 5b — Sina Audience Hub (PAUSED)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-AUDIENCE-HUB` |
| **Status** | **PAUSED** behind MergePack |
| **Resume when** | P0 M4 or ASF explicit |
| **Hook** | `product/SINA_AUDIENCE_HUB_FREE_TIER_SPEC.md` |

---

## Thread 6 — MergePack L1 Evidence Factory (active parallel)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-MERGEPACK` |
| **Phase** | **v1.3** — deploy + KPI trio + hooks (Evidence Factory) |
| **Status** | **active_parallel** — ship L1 + authorized growth (SEO, paid, 7-day $10K when ASF runs plan) |
| **Goal** | Evidence Factory + MP-* milestones; $10K path = `MERGEPACK_10K_7DAY_LOCKED_v1.md` when activated |
| **Vocab** | `PLAN_STATUS_VOCAB_LOCKED_v1.md` — factory no-ads ≠ growth ban |

| Hook | Path |
|------|------|
| Start | `~/Desktop/mergepack/START_HERE.md` |
| Code | `~/Desktop/mergepack/` |
| Canon docs | `mergepack/docs/_TOPICS/` (01–06) |
| Org spec | `mergepack/docs/MERGEPACK_ORGANIZATION_LOCKED_v1.md` |
| Progress | `mergepack/PROGRAM_PROGRESS.json` |
| Lock | `mergepack/LOCKED.md` |
| Source A product | `product/MERGEPACK_LOCKED_v1.md` |
| SEO map | `mergepack/docs/_TOPICS/04-seo-growth/SEO_CONTENT_MAP_50.md` |
| Deploy canon | `mergepack/docs/_TOPICS/03-deploy/CANON_DEPLOY.md` |
| API (live) | `https://mergepack-api-production.up.railway.app` |
| Secrets | `~/.sina/mergepack.env` |
| Incidents | `mergepack/docs/_TOPICS/05-incidents/` |

| Day | Deliverable | Status |
|-----|-------------|--------|
| 1 | API + tests | ✅ |
| 2 | Railway deploy | ✅ |
| 3 | UI + 30 SEO routes + B/C preview UI | ✅ code |
| 4 | Vercel + ads | ⬜ |
| 5 | Stripe | ⬜ |
| 6 | $500 MRR floor | ⬜ |
| 7 | $10K MRR or pivot FormToPDF | ⬜ |

### MergePack milestone ladder (revenue M8)

**Subject:** `THREAD-FACTORY` (pick SKU) → **`THREAD-MERGEPACK`** (execute + **M8**).

| Milestone | Definition | 7-day target day |
|-----------|------------|------------------|
| **M1** Ship | Live URL, merge works | 3–4 |
| **M2** Pay | 1 real payment | 5 |
| **M3** SEO | 20 indexed / 500 impressions | post-7 |
| **M4** | $90 MRR or 10 customers | stretch in blitz |
| **M6** | $1,000 MRR | after M8 hit |
| **M7** | $3,000 MRR | scale |
| **M8** | **$10,000 MRR north-star** | **7** |
| **M5** | Pivot review (FormToPDF) | 7 if M8 &lt; $3K |

**Glossary:** `ASF_MILESTONE_GLOSSARY_LOCKED_v1.md`

**Honest product truth:** v1 = **combine PDFs in upload order** (not “smart merge”). Tier B/C on UI = **preview, not wired**. Organize AI = post-M2 upsell (PATH A).

**Do not mix with:** Thread 0 ingestion, Thread 3 wire “M8 stack”, Thread 7 investor slide “M8”.

---

## Thread 7 — Investor package

| Field | Value |
|-------|--------|
| **ID** | `THREAD-INVESTOR` |
| **Phase** | Materials **DONE** (maintain only) |
| **Status** | PDFs in FINAL folder |
| **Goal** | Explain portfolio + TrustField + factory; **not** day-to-day build |

| Hook | Path |
|------|------|
| Index | `~/Desktop/SourceA/investor/README.md` |
| PDFs FINAL | `~/Desktop/Sina-Investor-Package-FINAL/` |
| Roadmap | `investor/ROADMAP.md` (factory line updated for 7-day blitz) |
| Connector brief | `investor/CONNECTOR_BRIEF.md` |

| Sub-task (done in chat) | Path |
|-------------------------|------|
| Markdown sources | `investor/*.md` |
| PDF build | `investor/_build_pdfs.py` |
| FINAL package | `~/Desktop/Sina-Investor-Package-FINAL/` |

**Narrative rule:** MergePack = **factory P0 SKU** + SEO utility; Super Brain = **long-term OS**; DevBridge = **proven wire**, separate from MergePack revenue proof.

---

## Thread 8 — Portfolio delivery (5 repos)

| Field | Value |
|-------|--------|
| **ID** | `THREAD-PORTFOLIO` |
| **Status** | Parallel — **does not gate** MergePack or wire |
| **Goal** | Ship TrustField, VIRLUX, 777, Noetfield, Mono per各自 plans |

| Repo | Blocker (typical) | Hook |
|------|-------------------|------|
| TrustField | CF / free deploy | `TrustField Technologies/` |
| VIRLUX | Staging/Railway | `VIRLUX/` |
| 777 | Supabase service key | `The 777 Foundation/web/` |
| Noetfield | Spec sections | `Noetfield/` |
| Mono | Phase 0 exit | `SinaaiMonoRepo/` |

`founder/ASF_REPOS_AND_LANES.md` · `GLOBAL_BLOCKERS.json`

---

## Thread 9 — TrustField free infra rule

| Field | Value |
|-------|--------|
| **ID** | `THREAD-TRUSTFIELD-INFRA` |
| **Status** | **LOCKED** |
| **Hook** | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` |

No Render credit card; Cloudflare + free tiers only.

---

## Open tasks rollup (cross-thread — not complete until checked)

| Thread | Open item |
|--------|-----------|
| MERGEPACK | Vercel, Stripe, ads, Day 7 M8 |
| CHAT-CONSOLIDATION | First raw chat drop + L2 entries |
| SUPERBRAIN | Fill `001-sina-core` non-negotiables; promote L2/L3 |
| WIRE | G3 `g3_tailscale` pending on disk if not recorded |
| PORTFOLIO | Per-repo blockers in GLOBAL_BLOCKERS |
| AUDIENCE-HUB | Paused |
| CURSOR-OS-PRO | Reference parity + store (parallel) |

**Completed threads (do not burn P0 time):** FACTORY ideation · INVESTOR PDF package · wire smoke/full_m8 (mostly).

---

## Active NOW (single focus)

| Priority | Thread | Your next action |
|----------|--------|------------------|
| **P0** | **THREAD-FACTORY → RunReceipt** | Factory rescore pick only — MergePack growth (SEO/paid/10K) still authorized |

Everything else is **parallel or done** unless ASF explicitly switches thread in chat.

---

## Session picker (tell the agent)

Copy one line at start of chat:

| Thread | Opening line |
|--------|----------------|
| MergePack lab | `Active thread: THREAD-MERGEPACK. Read mergepack/START_HERE.md + docs/_TOPICS/.` |
| Investor only | `Active thread: THREAD-INVESTOR only. No code edits.` |
| Super Brain / SoT | `Active thread: THREAD-SUPERBRAIN only. Layer A/B. No MergePack.` |
| Ecosystem / Source A | `Active thread: THREAD-ECOSYSTEM only. Read SSOT first.` |
| Wire / DevBridge | `Active thread: THREAD-WIRE only. Proof already PASS unless regression.` |
| Cursor OS Pro | `Active thread: THREAD-CURSOR-OS-PRO only. Separate repo.` |
| Prompt OS day | `Active thread: THREAD-PROMPTOS only. run-full-day Lane 0.` |

---

## Incidents (cross-thread — agent placeholders)

| Date | Thread | Doc |
|------|--------|-----|
| 2026-06-04 | COMMAND | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` |
| 2026-06-03 | PROMPTOS | `SinaPromptOS/docs/M8_INCIDENT_2026-06-03_LOCKED.md` |
| 2026-06-04 | WIRE | `AI Dev Bridge OS/docs/INCIDENT_2026-06-04_AGENT_PLACEHOLDER_RUN_ID.md` |
| 2026-06-03 | MERGEPACK | `mergepack/docs/INCIDENT_2026-06-03_AGENT_PLACEHOLDER_DEPLOY.md` |

**Conflict Room (ongoing):** `SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md` · ACE `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` · app tab **Conflict Room**

**Rule:** No pasteable placeholders in terminal commands. One command per block.

---

## Drift guards

| Wrong mix | Why it hurts |
|-----------|----------------|
| MergePack chat + wire proof | Done; wastes day |
| Investor deck + Railway CLI steps | Wrong audience |
| Super Brain ingestion + Stripe day 5 | Two phases |
| “90-day SEO ramp” for MergePack | **Superseded** by `MERGEPACK_10K_7DAY_LOCKED_v1.md` |
| Smart merge marketing in v1 | Trust / refunds |
| “M8” without thread | Wrong milestone — read glossary |

---

## Completeness statement

This registry covers **all major locked workstreams** from the conversation arc (SoT → ecosystem → wire → factory → MergePack → investor). It does **not** list every chat message. For history see transcript `a53f3fa1-081c-4373-bc55-76feb501a61d`.

**If something is missing:** add row to Master index + hook path → `ASF-THREADS-2.0`.

---

**LOCKED.** New thread or phase change → `ASF-THREADS-2.0` + ASF.
