# SourceA Founder ↔ Machine Terminology Dictionary (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-TERMINOLOGY-DICT  
**Authority:** ASF · **human + machine shared vocabulary**  
**Parent:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` §LAW PURITY · `SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md` §12  
**Machine:** `governance_completion_backlog_audit.py` · `validate-governance-completion-backlog-v1.sh`  
**Big picture / P0–P7 / live cascade:** `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` (pointer only)

---

## 0. One sentence

> **One dictionary — founder plain words on the left, machine/registry words on the right, SSOT path for each — so humans and agents speak the same system without mixing topics.**

---

## 1. Did we find the “first Noetfield SSOT”?

**Yes — found. Not merged into SourceA apex.**

| What you may remember | Where it lives | Status |
|----------------------|----------------|--------|
| **POSA v3.0 Source of Truth** (autonomous OS layer — perception→learning loop) | `~/Desktop/Noetfield-All-Documents/hierarchy/L0-law/posa_system__posa-v3-0-source-of-truth.md` | **Noetfield L0-law** · pre-SourceA era |
| POSA v2/v3 uploads | `Noetfield-All-Documents/uploaded/2026-05-batch-003/` etc. | Archive copies |
| PAIOS SSOT blueprint | `hierarchy/L0-law/paios_system__paios-source-of-truth-blueprint-v1.md` | Reference product SSOT |
| Orchestration policy layer SSOT 2026 | `hierarchy/L0-law/developer_os_strategy__orchestration-policy-layer-source-of-truth-2026.md` | Strategy SSOT |
| Noetfield registry JSON | `Noetfield-All-Documents/registry/source_of_truth_registry.json` | Product registry |

**Not in SourceA `archive/` as one file** — Noetfield corpus stayed in `Noetfield-All-Documents/`.

**Ecosystem SSOT today (wins over Noetfield POSA for mono structure):**

| Layer | SSOT path | Governs |
|-------|-----------|---------|
| **Ecosystem apex** | `SINA_OS_SSOT_LOCKED.md` | Whole mono structure · phases · authority table |
| **Law registry** | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | Topic → canonical path · LAW PURITY |
| **Law router** | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | Which branch to read |
| **Noetfield product** | `NOETFIELD_CLOUD` row · `Noetfield/docs/ops/*_LOCKED.md` | Ship repo · **local-only** until Layer A SSOT (Phase 2 pick) |
| **Noetfield archive agent** | `~/Desktop/Noetfield-All-Documents` | Docs hierarchy · **not** ecosystem law |

**Rule:** POSA/PAIOS docs = **historical Noetfield product truth**. SourceA `SINA_OS_SSOT` = **governance truth** for the whole machine. Never invert.

---

## 2. How to write SSOT and find it among rules

### 2.1 Resolution algorithm (machine + human)

```text
1. What TOPIC?  (one subject only — LAW PURITY §4)
2. Lookup authority index ROW for that topic
3. Open canonical PATH in that row — that file is law for topic T
4. If unsure → ASK ASF (never guess row or invent tab name)
5. PROVE with validator listed on row or §6 below
6. SHIP receipt + Track row
```

### 2.2 Tier stack (do not mix priority words)

From Cross-doc §12.4 — **G0→G8**:

| Tier | Plain | Machine |
|------|-------|---------|
| **G0** | You decide | ASF · PICK · SAVE/LOCK |
| **G1** | Ecosystem shape | `SINA_OS_SSOT` |
| **G2** | Which file is law | Authority index row |
| **G3** | Rule text | Topic LOCKED doc at path |
| **G4** | Which doc when | Batch 2 · Cross-doc (not law) |
| **G5** | Boot / UI | Prompts · Canvas (not law) |
| **G6** | Live state | Hub · `~/.sina` (verify vs G3) |
| **G7** | Staging | RESEARCH · attachments |
| **G8** | Input | Chat |

### 2.3 How to write new law (GOV_UNIFY)

1. One topic · one new or bumped `*_LOCKED_vN.md` at root  
2. Add **one** authority index row  
3. Pointer-only in companions — no duplicate prose  
4. Archive superseded vN  
5. Run `validate-law-purity-ssot-v1.sh` + `validate-authority-root-coverage-v1.sh`

---

## 3. Founder language ↔ machine dictionary (core)

| Founder says / hears (human) | Machine term | SSOT |
|------------------------------|--------------|------|
| “Which law wins?” | Authority index row | `SINA_AUTHORITY_INDEX_MAP` |
| “Law = law” | LAW PURITY policy | Same · §LAW PURITY |
| “The path is law” | Canonical path for topic T | Row → `Canonical doc` column |
| “Original doc” | Index row for topic — **not** newest file | Cross-doc §11 |
| “Pick A / confirm” | `ASF: FIVE-STEP — PICK:` + Effect | Batch 2 §10 |
| “ALL CAPS order” / “same word caps or not” | **NORM-CAPS** — 100% equivalent | `FOUNDER_MSG_NORM` |
| “Live form / what’s pending” | `LIVE_DECISION_FORM` §ANSWERED · §OPEN | `live_founder_decision_form_v1.py` |
| “What’s logged?” | SCAN / disk truth | Five-step §3.1 |
| “Plain cards” | SAY | Five-step §3.2 · §7 |
| “I accept this consequence” | PICK gate | Batch 2 §14 |
| “Prove it” | PROVE · validators | Appendix B · §6 enforcers |
| “Close the session” | SHIP · RESULT_POLICY | Result-driven §4 |
| “Open fork / not done” | `founder_open` · FR-* · SESSION_LOG F row | `governance_completion_backlog_audit.py` |
| “Hub headline P0” | `founder_p0_id` STRATEGIC-SLICE | `GOAL_HIERARCHY` · hub Today |
| **“Hub” / “Sina Command” (archive)** | Legacy monolith — `/legacy/` · **not daily** | `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §5 |
| **“Super Fast Hub” / H1 daily** | Daily Necessities — **`http://127.0.0.1:13020/`** (~4 KB) · zero mistakes | `GET /api/worker-hub/v1` |
| **“Machine Hub” / H2 heavy** | Heavy machines — **`/machines/`** · disk receipts · scheduled builds only | `integration-fabric-registry-v1.yaml` `two_hub_model` |
| “Next steps” | **Super Fast Hub daily** — live next-10 + optional direction commentary | `LIVE_ONGOING_PROMPTS` |
| “Prompt feed” (deprecated) | **Do not use** for daily — say **Next steps** | INCIDENT-028 rename |
| “Legacy queue tab” / “prompt-feed tab” | **Legacy archive only** — `/legacy/?tab=prompt-feed` | INCIDENT-024/028 |
| “Factory parallel SKU” | T2b bucket · RunReceipt thread | `PROGRAM_PROGRESS` locks |
| “One sa per turn” | SINGLE_SA · `resume --max-turns 1` | `ACTIVE_NOW` |
| “Incident reports pile” | INCIDENT_CORPUS · 31 paths | `ecosystem_incidents_index.py` |
| “Registry incomplete” | T3_ORPHAN | `authority_root_coverage_audit.py` |
| “Drift score” | Governance drift engine | `governance_drift_engine.py` |
| “Honest progress” | Valid YES tier | `VALID_YES_VERDICT` |
| “Never AUTO-RUN P0” | `auto-run-disabled-v1.flag` | `FOUNDER_AGENTIC_POLICY` |
| “Complex chat” | Fork Machine T1–T5 | `FORK_MACHINE` |
| “Deep system exam” | 100-step · Canvas | `SYS_INTEGRITY_100` |
| “POSA / old Noetfield SSOT” | L0-law archive only | `Noetfield-All-Documents/hierarchy/L0-law/` |
| “Founder language / how I talk” | FOUNDER_LANGUAGE_CORPUS v3 | `archive/attachments/founder-language/FOUNDER_LANGUAGE_CORPUS_v3/` |

### 3.2 Agent domains — Specialist = Skill + Gate + Proof (balance law)

**Law of balance:** More rules ≠ better. One narrow job · hard bounds · **exit 0 or FAIL** — not a list of 200 latent abilities.

**Unification:** One human word ↔ one machine row ↔ one proof command. **No new doc** — extend registry or `mega_chat_anchors`-style JSON only.

| Domain | Founder says | Specialist (skill) | Gate (mechanical) | Proof (must run) | Reference on **us** (not talk) |
|--------|--------------|-------------------|-------------------|------------------|--------------------------------|
| **Governance** | law · pick · fork | `@sina-conscious-recovery` | `cursor_entry_gate.py` | `validate-integrity-batch-2-v1.sh` | `governance_propagation_cascade` receipt |
| **Technical** | worker · factory · sa | `@sina-sourcea-worker` | `goal1_lane_broker` worker-submit | `cursor_entry_gate --role worker` | `~/.sina/cursor_entry_gate_receipt_v1.json` |
| **VC / investor** | pitch · diligence | `@sina-research-intake` | `EXTERNAL_ADVISOR_CONTRACT` | research pipeline evaluate ≥ threshold | `investor/` + classify L1 only |
| **UI / hub** | hub · today · panel | `@anti-staleness-machine` | hub edit → AS bundle | `validate-serve-panel-build-v1.sh` | hub `built_at` + command-data |
| **Debug / E2E** | FAIL · bug · trace | `truth-projection` | `find_critical_bugs` | `validate-anti-staleness-bundle-v1.sh` | `SOURCEA_DISK_TRUTH_E2E_MATRIX` RT row |
| **Research** | paste · critic · idea | `@sina-research-intake` | `prompt_feasibility_gate` | Agent Hub evaluate scores | `~/.sina/agent-research/items.jsonl` |
| **Portfolio** | TrustField · ship | `@sina-trustfield` etc. | lane handoff index | lane-specific verify script | fleet registry + receipts |

**Memory (no overload):** Agent loads **only** `agent_truth_bundle` → role MANDATORY_READ slice → **one** domain skill → **one** authority row if law touched. Full repo forbidden (GPT Layer 7 = our router).

**Machine payload:** `python3 scripts/ecosystem_master_catalog_v1.py --json` → `agent_domain_matrix`

### 3.3 Direction era + integrity pack words (2026-06-12)

**Law:** `SOURCEA_FOUNDER_DIRECTION_TERMINOLOGY_LOCKED_v1.md` · **vault mirror:** `archive/attachments/founder-language/`

| Founder says | Machine | Notes |
|--------------|---------|-------|
| Canva form | Cursor Canvas `sourcea-system-integrity-100.canvas.tsx` | Not Canva.com |
| 5 pack | INTEGRITY PACK A–E (Batch 2) | Five-step · playbook · canvas · precedence |
| Refine everything | DIRECTION-LOCK projections + PICKs | Not bulk law rewrite (3.07 gates GOV_UNIFY) |
| 3.07 NO | Phase 3 index-only · skip GOV_UNIFY batch | PICK 2026-06-12 |
| Film it / W1 | ENFORCEMENT demo film | Not factory 616 hero |
| First dollar | W3 NF-001 / TF-001 | Agentic outreach |

### 3.4 Founder language corpus §4 (2026-06-12 — merged from FOUNDER_LANGUAGE_CORPUS v3)

**Authority:** `FOUNDER_LANGUAGE_CORPUS` · **vault:** `archive/attachments/founder-language/FOUNDER_LANGUAGE_CORPUS_v3/` · **machine:** `phrase-corpus.yaml` (45 entries)

#### 3.4A — Daily operator

| Founder says | Machine meaning |
|--------------|-----------------|
| Short / precisely | No essay · RESULT table |
| What do I paste | Hub Action or INBOX — one step |
| Disk wins | Receipt beats hero |
| Nothing lost | Search M1 · FOUND path |
| Big picture | T30 scan · two clocks |
| Refine not drift | Projections + picks — not law factory |
| Film it | W1 — highest ROI |
| First dollar | W3 — only traction proof |

#### 3.4B — Integrity / form

| Founder says | Machine meaning |
|--------------|-----------------|
| Canva form | **Cursor Canvas** `sourcea-system-integrity-100.canvas.tsx` |
| 5 pack | INTEGRITY PACK A–E (Batch 2) |
| 100 questions | 100 playbook steps + ~26 Canvas forks |
| PICK batch | `ASF: FIVE-STEP — PICK:` |
| 3.07 NO | No GOV_UNIFY merge sprint · Phase 3 index-only |

#### 3.4C — Portfolio names

| Name | Job |
|------|-----|
| SourceA | Engine |
| Noetfield | Product · W3 primary |
| TrustField | Money lane · W3 backup |
| Thunderfield | VC comfort · post-W3 |
| Forge / MergePack | Background SKUs |

#### 3.4D — Advisor paste

| Founder says | Agent must |
|--------------|------------|
| Claude said / GPT said | `INPUT CLASS: EXTERNAL_CRITIC` |
| MUSK STYLE ship | Compare to W1+W3 — no reorder |
| $100M | Narrative upside label only |

#### 3.4E — Urgency (trust signals)

| Signal | Agent response |
|--------|----------------|
| ALL CAPS | Same intent as mixed case (NORM-CAPS) |
| Duplicate send | Show disk certainty |
| Insult / frustration | Stop rituals · one receipt · one tap |
| “I'm tired” (keys) | Point to vault + hub |

**Evolution vs drift:** New pick + receipt + validator = evolution · hero/chat contradicting form = drift (INCIDENT + scrub).

### 3.5 Form office · Judge Center · Thread Room (2026-06-12)

**Blueprint:** `archive/attachments/2026-06-12/SINA_ROOMS_UNIFIED_BLUEPRINT_DRAFT_v1.md` · Form forks `Q-JUDGE-STACK-v1` · `Q-THREAD-ROOM-v1`

| Founder says | Machine term | Job | Not this |
|--------------|--------------|-----|----------|
| Everything on the form | **FORM_OFFICE** | M1 Canvas · §OPEN · PICK | Chat authority |
| Who is right / stale / bad | **JUDGE_CENTER** | Audit→Lawyer→Judge · alarms | Thread map |
| Nothing lost in threads | **THREAD_ROOM** | Scout→Cartographer→Curator · T30 | Alarm court |
| Law vs policy vs blueprint | **G3 vs G4/G5** | LOCKED+row = binding · map = inform | “Policy is soft” |
| Building metaphor | registry / law / blueprint / room | Index / code / poster / department | One mega-chat |

**Terminology rule:** **Policy** in a `*_LOCKED` filename with authority row = **G3 law** (same binding as “law”).

---

### 3.1 Specialized glossaries (pointer-only — do not duplicate here)

| Topic | Doc |
|-------|-----|
| Plan status words | `PLAN_STATUS_VOCAB_LOCKED_v1.md` |
| M8 / milestone labels | `ASF_MILESTONE_GLOSSARY_LOCKED_v1.md` |
| Execution OS stop/start | `CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md` §4 |
| Integrity pack terms | `SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md` §7 |
| Plain topic/row/path | `SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md` §12 |
| Three rooms | `SINA_ROOMS_UNIFIED_BLUEPRINT_DRAFT_v1.md` |
| Five-step founder phrasing | `SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` §7 |
| ASF inclusive/exclusive | `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md` §1.0 |

---

## 4. Registry · resolution · integrity — complete stack list

### 4.1 Declaration layer (what exists)

| # | Artifact | Role |
|---|----------|------|
| 1 | `SINA_OS_SSOT_LOCKED.md` | Ecosystem apex |
| 2 | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | Law registry + LAW PURITY |
| 3 | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | Router |
| 4 | `brain-os/entry/LAW_ROOT_INDEX_LOCKED_v1.md` | Topic map (T2) |
| 5 | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` | Chronology only |
| 6 | `ECOSYSTEM_IMPORTANT_DOCS_INDEX_LOCKED_v1.md` | Read urgency P0/P1/P2 |
| 7 | `SOURCEA_AUTHORITY_REGISTRY_GOV_UNIFY_BATCH_2026-06-11_LOCKED_v1.md` | Batch manifest |
| 8 | `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | Incident corpus parent |
| 9 | `SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` | Navigation tree |

### 4.2 Resolution layer (topic → act)

| # | Artifact | Role |
|---|----------|------|
| 10 | `SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md` | Link clusters · audit method |
| 11 | `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` | Batch merge/archive |
| 12 | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | 12-order alignment |
| 13 | `SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` | Daily SCAN→SHIP |
| 14 | `SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md` | Complex forks |
| 15 | `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` | Closeout shape |
| 16 | `SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md` | Deep audit |
| 17 | `SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md` | Pack map |
| 18 | `SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md` | Phase 2 receipt |

### 4.3 Enforcer layer (prove + don’t forget)

| # | Script / tool | Catches |
|---|---------------|---------|
| E1 | `validate-law-purity-ssot-v1.sh` | LAW PURITY alive |
| E2 | `validate-authority-root-coverage-v1.sh` | T3 orphan laws |
| E3 | `validate-authority-index-coverage-v1.sh` | E1 + E2 bundle |
| E4 | `validate-governance-completion-backlog-v1.sh` | **Open founder forks** (AS-19) |
| E5 | `governance_completion_backlog_audit.py` | PROGRAM_PROGRESS `founder_open` · SESSION_LOG · FR-* |
| E6 | `validate-anti-staleness-bundle-v1.sh` | AS-01..AS-19 latch chain |
| E7 | `validate-integrity-batch-2-v1.sh` | Integrity pack 5 wiring |
| E8 | `validate-cross-doc-linkage-v1.sh` | SESSION-INTEGRITY-10 cluster |
| E9 | `validate-ecosystem-safety-v1.sh` | Hub · monitor · dual-pick |
| E10 | `find_critical_bugs.py` | CRITICAL validator rollup |
| E11 | `governance_drift_engine.py` | Drift score 0–100 |
| E12 | `founder_request_tracker.py` | FR-* never-forget Track |
| E13 | `agent_rules_in_charge.py` | Laws governing NOW |
| E14 | `research_save_enforcer.py` | RESEARCH before closeout |
| E15 | `governance_propagation_cascade_v1.py` | G0 change / worker-done → monitor+hub RT |
| E16 | `validate-governance-propagation-live-v1.sh` | Cascade wiring probe |

**Agent rule:** Before SHIP — run E5 (or read its output). If backlog lists integrity `founder_open` — **SAY it** in closeout; do not let it drop. Worker ends with broker submit — E15 runs; **never** ask founder to refresh monitor.

---

## 4b. Lost link recovery (founder ↔ machine)

| Founder says | Machine term | Canonical |
|--------------|--------------|-----------|
| “Go to messages” / “big picture” / “you missed it” | **LOST_LINK_RECOVERY** | `LOST_LINK_ETHICS` row |
| “I found it” / complete reward | **FOUND report** | Ethics §2 + Cursor rule |
| Chicken / egg / first blueprint | **First egg model** | 018 · SSOT_FOUNDATION §3 |
| Bring frozen rules to life | **FROZEN_REVIVAL** | `FROZEN_ARCHIVE_REVIVAL_AUDIT` |
| Archive as genealogy only | **ARCHIVE ban** | 002 § enforcement · `validate-no-archive-as-law` |

**Agent line:** `FOUND — <path> · WAS — <mistake> · PROOF — <row/receipt> · USE — <now>`

| Routine skill | `@sina-conscious-recovery` | `CONSCIOUS_RECOVERY` row · `MANDATORY_READ` v1.3 |
| Session ledger | `@agent-self-audit-loop` | `cursor_agent_self_audit.py` |
| Skill sync | `sync-cursor-agent-skills.sh` | `agent-skills/REGISTRY_LOCKED_v1.json` v1.2 |

---

## 5. Open completion items (live mirror — 2026-06-11)

Run: `python3 scripts/governance_completion_backlog_audit.py`

| Severity | Item | Owner |
|----------|------|-------|
| high | Phase 1.10 closeout · Phases 3–10 Canvas (`SYS-INTEGRITY-100`) | ASF + Maintainer |
| medium | 100-step playbook `in_progress` | ASF |
| high | FR-2026-06-05-003 GPT report-only lock | Maintainer |
| high | FR-2026-06-06-1013f0 Commercial closure pass | Maintainer |

**Phase 2 batch:** **DONE** — `SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md`

---

*End terminology dictionary*
