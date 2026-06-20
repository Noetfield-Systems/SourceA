# ASF operational layer stack (LOCKED v1)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-12 · **Authority:** ASF order  
**Purpose:** Founder-facing L1–L4 agent stack (distinct from `authority.yaml` L0–L6 machine numbering)  
**Machine pointer:** `brain-os/system/authority.yaml` · `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` — reconcile when ASF says lock machine map

---

## One sentence

> **ASF overrides · Brain routes · L3 high agents advocate · L4 Worker + Researcher 2 act · Disk remembers.**

---

## Layer stack

| Layer | Roles | execution_authority |
|-------|--------|---------------------|
| **L1** | ASF + Hub | human override |
| **L2** | Brain (SourceA Execution Core) | **true** (pick · reconcile · handoff) |
| **L3** | High agents (see table below) | **false** (advocate · hub · SSOT · briefs) |
| **L4** | SourceA Worker · Researcher 2 (Research Acquisitor) | **false** (build · verify · vault) |

---

## L3 — high agents

| Founder name | Machine id | Workspace | Chat | Status |
|--------------|------------|-----------|------|--------|
| **Gov Specialist** | `governance_goal_specialist` | SinaaiMonoRepo | `e54ddfa8` | active |
| **Commercial Specialist** | `commercial_goal_specialist` | TrustField Technologies | `6245d9dd` | active |
| **Research Brief** (Researcher 1) | research brief lane | SourceA | `85dd7cd4` | active |
| **Maintainer 1** | `MAINTAINER_1` / ECOSYSTEM megachat | SinaaiDataBase | `a53f3fa1` | **RETIRED** · search only |
| **Maintainer 2** | `sinaai_maintainer` | SinaaiDataBase | `74f5ccab` | active · hub · FR-003 · projection |
| **Maintainer 3 · Anchor** | `MONOREPO` anchor | SinaaiMonoRepo | `3369d11c` | active · mx SSOT · runtime E2E |

## Precedence law (ASF order)

**0 — ASF + Hub** beats everyone.

**1 — Maintainer 1 = reference for everyone**  
Chat `a53f3fa1` · **RETIRED from ops** · **not** live authority. All agents (Brain, Gov, Commercial, Brief, Worker, Researcher 2, M2, M3) **search M1 first** before inventing narrative or redoing history. **Disk wins** when M1 transcript conflicts with live JSON.

**2 — SourceA agents beat Maintainer 2 and Maintainer 3**  
On conflict between **SourceA spine agents** and **M2 or M3**, SourceA wins:

| SourceA agents (win) | vs | Maintainers (yield) |
|----------------------|-----|---------------------|
| Brain · Gov · Commercial · Research Brief · Worker · Researcher 2 | **>** | Maintainer 2 · Maintainer 3 |

M2/M3 implement Hub projection and Mono anchor — they **do not override** Brain picks, specialist advocacy, Worker receipts, or live form JSON.

**3 — Goal specialists (L3):** Governance **>** Commercial **>** Research Brief — unless ASF overrides on Hub. Brain reconciles before Worker handoff.

**Maintainer roles (summary):** M1 = universal reference · M2 = Hub/FR-003/projection (subordinate to SourceA agents) · M3 = MonoRepo SSOT anchor (subordinate to SourceA agents; read spine, never second Brain).

---

## L4 — doers

| Founder name | Machine id | Workspace | Chat |
|--------------|------------|-----------|------|
| **Worker SourceA** | `sourcea_worker` | SourceA | `fd67502f` |
| **Researcher 2** | `research_acquisitor` | SourceA | `20b12e67` |

Both: `execution_authority: false` · Worker builds one sa/turn · Researcher 2 vault + filtered digest only.

---

## Disk anchors

| Anchor id | Path |
|-----------|------|
| MEGA_CHAT_ANCHORS | `scripts/ecosystem_master_catalog_v1.py` |
| M1 EOS | `archive/attachments/2026-06-11/MAINTAINER_1_END_OF_SERVICE_HANDOFF_2026-06-11.md` |
| M2 synthesis | `archive/attachments/2026-06-12/MAINTAINER_2_CROSS_CHAT_GOV_COMMERCIAL_INCIDENT_SYNTHESIS_LOCKED_v1.md` |
| Fleet cast | `FOUNDER_BRAIN_MAINTAINER_STRATEGIC_EXTRACTION_100M_v2.md` §II |

---

## Hub projection (pending)

L3 maintainers + L4 Researcher 2 need live Hub wires (founder one-tap visibility). Backlog: `AR-e41e6a5d9c` + maintainer L3 extension.

---

*End ASF_OPERATIONAL_LAYER_STACK_LOCKED_v1*
