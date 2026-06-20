# Source A — Document Sequence & Dating Registry (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Classification:** INTERNAL ONLY — Desktop `sourceA/` — never commit to public git  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/sourceA/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 — **governs dating and order only**, not ecosystem law  
**Maintainer:** ASF (only human who may edit this registry or Source A locks)  
**Locked:** 2026-06-02

---

> **Purpose.**  
> Every Source A file must have a **known write date**, **sequence position**, and **supersession link** so agents and ASF never guess “which doc came first” or “which doc wins for agents & automation.”  
> **Chronological order ≠ authority order.** Read order is in SSOT §13 + addendum + unified blueprint §17.

---

## 1. Mandatory header block (every Source A file)

When ASF **creates or materially edits** any file in `Desktop/sourceA/`, the header MUST include:

| Field | Required | Example |
|-------|----------|---------|
| **Version** | Yes | `1.0 — FINAL LOCKED` |
| **Locked** | Yes | `2026-06-02` (date ASF locks the version) |
| **sequence_id** | Yes | `SA-2026-06-02-007` (see §2) |
| **Supersedes** | If replacing prior doc | `SINAAI_AGENT_STACK_POLICY_v1.md` |
| **Status** | Yes | `ACTIVE` · `SUPERSEDED` · `MIRROR` · `INDEX ONLY` · `ADDENDUM` |
| **Authority** | Yes | Subordinate to SSOT v3 (or “master law” if SSOT) |

At file bottom, **Document control** table MUST append a row (never delete history):

```markdown
| Version | Date | sequence_id | Change |
|---------|------|-------------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-007 | Initial lock — … |
```

**Rule D1:** `Locked` date = semantic lock date ASF declares — may differ from filesystem `mtime` by hours; **registry wins** for sequence.

**Rule D2:** Agents **read only** Source A. Only ASF edits locks and this registry.

**Rule D3:** Minor typo fixes → patch version (`1.0.1`) + new registry row. Semantic change → bump minor/major + new `sequence_id`.

---

## 2. sequence_id format (locked)

```text
SA-YYYY-MM-DD-NNN
```

| Part | Meaning |
|------|---------|
| `SA` | Source A |
| `YYYY-MM-DD` | Lock date (first lock of that version) |
| `NNN` | Daily sequence 001–999 (order **first written that day** → last) |

**Example day 2026-06-02:**

- `SA-2026-06-02-001` — first doc locked that day  
- `SA-2026-06-02-007` — seventh doc locked that day  

When two files lock same day, **lower NNN = earlier in time / foundation first** unless `supersedes` says otherwise.

---

## 3. Three orderings (do not confuse)

| Order type | Question | Source |
|------------|----------|--------|
| **A — Chronological (write sequence)** | What was written when? | **This registry §4** |
| **B — Authority (read precedence)** | What wins on conflict? | SSOT v3 §13 + addendum + role of each doc |
| **C — Supersession (doctrine merge)** | Which file replaces which topic? | Unified blueprint §0 + registry `Status` column |

**Agent rule:** Never use “newest file present” as law. Use **authority order (B)**. Use **chronological (A)** only for history and “what changed when.”

---

## 4. Master chronology — Source A (locked snapshot 2026-06-02)

Sorted by **sequence_id** (first → last). `Status` as of this registry lock.

| seq_id | Locked | File | Role | Status |
|--------|--------|------|------|--------|
| SA-2025-05-31-001 | 2026-05-31 | `SINA_OS_SSOT_LOCKED.md` | Master ecosystem law | ACTIVE |
| SA-2025-05-31-002 | 2026-05-31 | `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` | Phase 1 work plan (not SSOT) | ACTIVE |
| SA-2025-05-31-003 | 2026-05-31 | `SINAAI_AGENT_STACK_POLICY_v1.md` | Runtime LLM policy (was DESIGN) | **SUPERSEDED** → unified §8 |
| SA-2026-06-01-001 | 2026-06-01 | `VIRELUX_REPO_ALIGNMENT.md` | DELIVERY bridge VIRLUX | ACTIVE |
| SA-2026-06-01-002 | 2026-06-01 | `SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` | Full ecosystem roadmap | ACTIVE |
| SA-2026-06-01-003 | 2026-06-01 | `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` | Multi-plane conflict doctrine | ACTIVE |
| SA-2026-06-01-004 | 2026-06-01 | `AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md` | Worked example only | ACTIVE (example) |
| SA-2026-06-01-005 | 2026-06-02 | `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | Prompt OS spec + Farsi §4 | **MIRROR** — unified §5; keep for Farsi |
| SA-2026-06-01-006 | 2026-06-02 | `SINA_PROMPT_OS_CORE_v1.md` | Short index | **INDEX ONLY** |
| SA-2026-06-01-007 | 2026-06-02 | `SINA_OS_SSOT_READ_ORDER_ADDENDUM_v1.md` | Pending SSOT v3.1 insert | ADDENDUM |
| SA-2026-06-02-001 | 2026-06-02 | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` | **Single agents & automation blueprint** | **ACTIVE — canonical** |
| SA-2026-06-02-002 | 2026-06-02 | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` | **This file** | ACTIVE |
| SA-2026-06-02-010 | 2026-06-02 | `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` | Full day execute playbook | ACTIVE |
| SA-2026-06-02-011 | 2026-06-02 | `SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md` | 10x runnable architecture | ACTIVE |
| SA-2026-06-02-012 | 2026-06-02 | `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md` | **Conflict resolution + operating model** | **ACTIVE — read #2** |
| SA-2026-06-02-013 | 2026-06-02 | `PROMPT_OS_CORE_MVP_BUILD_ORDER_LOCKED_v1.md` | MVP build order (9 deliverables) | ACTIVE |
| SA-2026-06-02-014 | 2026-06-02 | `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` | Phase 2 evidence + re-rank | **ACTIVE** |
| SA-2026-06-02-015 | 2026-06-02 | `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` | AI evaluator + planner + semantic | **ACTIVE** |
| SA-2026-06-02-016 | 2026-06-02 | `SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md` | **Final handoff + next plan** | **ACTIVE — read when lost** |
| SA-2026-06-02-017 | 2026-06-02 | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` | No credit card infra rule | ACTIVE |
| SA-2026-06-02-018 | 2026-06-02 | `SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md` | YAML ingest Phase 1 law | ACTIVE |
| SA-2026-06-02-019 | 2026-06-02 | `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` | **SA-019 ops freeze** | **ACTIVE — wins daily** |
| SA-2026-06-02-020 | 2026-06-02 | `SINAAI_PERMANENT_ARCHITECT_AGENT_LOCKED_v1.md` | Architect read-only layer | ACTIVE |
| SA-2026-06-02-021 | 2026-06-02 | `README_SOURCE_A.md` | Source A entry + phase prefixes | ACTIVE |
| SA-2026-06-02-022 | 2026-06-02 | `ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md` | 5 repos + Lane 0 | ACTIVE |
| SA-2026-06-02-023 | 2026-06-02 | `AGENT_OUTPUT_CONTRACT_v1.yaml` | Ingest YAML schema | ACTIVE |
| SA-2026-06-02-024 | 2026-06-02 | `ARCHITECT_REPORT.yaml` | Architect output (regenerated) | RUNTIME |
| SA-2026-06-02-025 | 2026-06-02 | `SECRETS_VAULT.md` | Vault ops pointer | ACTIVE |
| SA-2026-06-02-026 | 2026-06-02 | `SINAAI_ARCHITECT_V2_INDUSTRIAL_POLICY_LOCKED_v1.md` | Architect v2 — reduce cognitive load | ACTIVE |
| SA-2026-06-06-META-REASONING-STACK | 2026-06-06 | `META_REASONING_POLICY_STACK_LOCKED_v1.md` | L0–L12 decision governance umbrella | ACTIVE |
| SA-2026-06-09-E2E-PLAYBOOK | 2026-06-09 | `SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` | **E2E debugger + Worker/Brain process SSOT** | **ACTIVE — read when E2E stuck** |
| SA-2026-06-09-RESULT-POLICY | 2026-06-09 | `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` | **Result-driven closeout for every founder ask** | **ACTIVE** |
| SA-2026-06-11-RESULT-POLICY-v1.1 | 2026-06-11 | `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` | **v1.1 hyper-active conduct** — option matrix, golden insight, founder next actions | **ACTIVE** |
| SA-2026-06-09-WORKER-E2E-POSTMORTEM | 2026-06-09 | `SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md` | **Worker E2E verdict + sa-0042 timeline + permanent fix** | **ACTIVE** |
| SA-2026-06-09-SESSION-INDEX | 2026-06-09 | `SOURCEA_SESSION_20260609_COMPLETE_INDEX_LOCKED_v1.md` | **Full session table — all topics, actions, recommendations** | **ACTIVE — read when lost** |
| SA-2026-06-09-GOLDEN-INSIGHT | 2026-06-09 | `SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` | **Two-company model · golden OS · safety ship** | **ACTIVE — pin this** |
| SA-2026-06-09-BRAIN-MONITOR-REPORT | 2026-06-09 | `SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1.md` | **Brain monitor truth · STALE/HERE bugs · :13020 vs :13021** | **ACTIVE** |
| SA-2026-06-10-MASTER-MANIFEST | 2026-06-10 | `SOURCEA_MASTER_SESSION_MANIFEST_LOCKED_v1.md` | **Full thread catalog · gaps · cross-repo map** | **ACTIVE — master inventory** |
| SA-2026-06-10-FOUNDER-PINNED | 2026-06-10 | `SOURCEA_FOUNDER_PINNED_ACTIONS_LOCKED_v1.md` | **PIN — 9-row result table · factory 3 taps · counter law** | **ACTIVE — founder daily** |
| SA-2026-06-10-1000PACK-JUDGE | 2026-06-10 | `SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md` | **1000-pack specialist verdict · trace 018 · three-track** | **ACTIVE — Brain cite** |
| SA-2026-06-10-LAYERED-ADVISORY | 2026-06-10 | `SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md` | **Multi-focus advisory · 13 layers · lens weights · earn path** | **ACTIVE — advisory SSOT** |
| SA-2026-06-10-MARKET-RECEIPT-ARCH | 2026-06-10 | `SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1.md` | **Enterprise positioning · receipt-native governance SKU** | **ACTIVE — external narrative** |

**Last locked today (handoff):** `SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md`  
**Last locked today (AI control):** `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md`  
**Last locked today (execution truth):** `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`  
**Last locked today (agents topic):** `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md`  
**First locked (ecosystem law):** `SINA_OS_SSOT_LOCKED.md`

---

## 5. Authority read order (agents & automation sessions)

Not the same as §4 chronology:

```text
0. README_SOURCE_A.md
1. ARCHITECT_REPORT.yaml (morning — high/critical only)
2. SINA_OS_SSOT_LOCKED.md v3
3. SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md
3. AUTO_CONFLICT_ENGINE_V3_LOCKED.md  (if plane clash)
4. SinaaiMonoRepo governance/AGENT_READ_FIRST.md
5. Repo os/plan.json
6. SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md §4  (Farsi human mirror — optional)
```

Roadmap-only questions → add `SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` after step 2, not before SSOT.

---

## 6. When ASF adds a new Source A file

1. Assign next `sequence_id` for today (`SA-YYYY-MM-DD-NNN`).  
2. Add header fields (§1).  
3. Append row to **this registry §4** (or §7 changelog).  
4. If superseding: set old file `Status: SUPERSEDED` in registry; add `Supersedes:` in new file.  
5. If read order changes: update `SINA_OS_SSOT_READ_ORDER_ADDENDUM_v1.md` or SSOT v3.1 manually.  
6. Run `./scripts/sync-sourceA-desktop.sh` if mono mirror exists (optional).

**Never:** silent overwrite without version bump + registry row.

---

## 7. Changelog (registry itself)

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-002 | Initial registry — chronology through unified blueprint lock |
| 1.0 addendum | 2026-05-27 | SA-2026-05-27-GOVERNANCE-ENTRY | Governance entry router + authority index — anti-fragmentation |
| 1.0 addendum | 2026-05-27 | SA-2026-05-27-AUTHORITY-INDEX | Authority index map registry |
| 1.0 addendum | 2026-06-05 | SA-2026-06-05-SOURCE-ALIGNMENT-LAW | Whole-system alignment law v1.1 |
| 1.0 addendum | 2026-05-27 | SA-2026-05-27-CHATGPT-CRITIC-LAW | External critic law v1.1 |
| 1.0 addendum | 2026-06-05 | SA-2026-06-05-WTM-v5 | WTM MAP v5.x + authority law v1.1 + hub procedure |
| 1.0 addendum | 2026-06-05 | SA-2026-06-05-AGENT-JUDGMENT | Agent decision stack + smart judgment + self-healing loop |

---

## 8. ASF sign-off

| Field | Value |
|-------|--------|
| Document dating rule adopted | ☐ ASF |
| Registry §4 accurate for today | ☐ ASF |
| Date | __________ |
