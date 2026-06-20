# SourceA — Agentic layer stack (LOCKED v2)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order  
**Supersedes:** `archive/attachments/2026-06-12/ASF_OPERATIONAL_LAYER_STACK_LOCKED_v1.md` (L3 maintainer placement)  
**Sync:** `agentic_layer_pipeline_v2.py` · Brain `58148ac9` · Governance `e54ddfa8`  
**Machine:** `~/.sina/agentic-layer-pipeline-v2.json` · `~/.sina/l1-agent-pipeline-wire-v1.json` · `~/.sina/governance-brain-wire-v1.json`

---

## One sentence

> **ASF decides · Brain is first after human · machine Python pipeline next · L1 advocates · L2 builds spine · L3 portfolio repos.**

---

## Stack (founder-facing)

```text
L0   ASF + Hub ........................ you decide · Form PICKs

L0.5 Machine pipeline (Python) ....... validators · scripts · ~/.sina receipts
                                    (not a chat — runs under Brain + Gov wire)

L1   FIRST LAYER (after human)
     1  Brain ........................ pick · reconcile · handoff
     2  Governance Specialist ......... law · heal · wired TO Brain via pipeline
     3  Commercial Specialist ........ money · GTM · wired TO Brain via pipeline
     4  Brief Specialist ............. research brief · wired TO Brain via pipeline

L2   SECOND LAYER
     5  Worker ....................... one sa-XXXX · run inbox
     6  Researcher 2 ................. vault · filtered digest
     7  Maintainer 2 ............... hub law SHIP · H2 · n8n
     8  Maintainer 3 ............... MonoRepo anchor · runtime E2E

L3   THIRD LAYER (portfolio repos)
     9+ TrustField · Noetfield · Forge · other repos
```

---

## Layer 1 — first after human (fixed order)

| Rank | Role | Chat | Workspace | execution_authority | Job |
|------|------|------|-----------|---------------------|-----|
| **1** | **Brain** | `58148ac9` | SourceA | **true** (pick · reconcile · handoff) | First agent after ASF · routes all · never implements sa-XXXX |
| **2** | **Governance Specialist** | `e54ddfa8` | SinaaiMonoRepo | false | Law · risk · cascade · heal · **wired TO Brain via pipeline** |
| **3** | **Commercial Specialist** | `6245d9dd` | TrustField Technologies | false | Money · GTM · **wired TO Brain via pipeline** · never picks sa |
| **4** | **Brief Specialist** | `85dd7cd4` | SourceA | false | Research brief · **wired TO Brain via pipeline** · no build orders |

**Brain ↔ Governance sync (mandatory):**

```bash
python3 ~/Desktop/SourceA/scripts/l1_agent_pipeline_wire_v1.py --json
```

**L1 → Brain pipeline (ALL first layer wired TO Brain through Python):**

| SSOT | Purpose |
|------|---------|
| `~/.sina/l1-agent-pipeline-wire-v1.json` | L1 → Brain hub — Gov · Commercial · Brief read Brain via `l1_wired.shared` |
| `~/.sina/l1-brain-pipeline-wire-v1.json` | Alias — same payload |
| `~/.sina/governance-brain-wire-v1.json` | Brain decisions source · `active_decisions[]` · queue head |

Every L1 subordinate (ranks 2–4) **must** load pipeline → `l1_to_brain.subordinates[]` + `l1_wired.shared` before reply. Brain (rank 1) **feeds** the pipeline. When `reconciled_decision.stale=true` → **IGNORE** archaeology · obey Brain disk via pipeline.

**One command (refresh all L1 + L2 wires — pipeline v2):**

```bash
python3 ~/Desktop/SourceA/scripts/agentic_layer_pipeline_v2.py --json
bash ~/Desktop/SourceA/scripts/validate-agentic-layer-pipeline-v2.sh
```

Fast tier (session gates · no brain snapshot sync):

```bash
python3 ~/Desktop/SourceA/scripts/agentic_layer_pipeline_v2.py --json --tier fast
```

Self-heal on drift:

```bash
python3 ~/Desktop/SourceA/scripts/agentic_layer_pipeline_v2.py --json --self-heal
```

**Two hubs (H1 + H2) heal + validate:**

```bash
python3 ~/Desktop/SourceA/scripts/hub_dual_heal_v1.py --json
bash ~/Desktop/SourceA/scripts/validate-two-hub-v1.sh
```

**Specialist precedence (Brain reconciles):** Governance **>** Commercial **>** Brief — unless ASF overrides on Form/Hub.

---

## Layer 2 — second layer (spine builders + maintainers)

| Rank | Role | Chat | Workspace | Job |
|------|------|------|-----------|-----|
| **5** | **Worker** | `fd67502f` | SourceA | One sa-XXXX per turn · run inbox · broker submit |
| **6** | **Researcher 2** | `20b12e67` | SourceA | Register · sync vault · filtered research root |
| **7** | **Maintainer 2** | `74f5ccab` | SinaaiDataBase | Hub law SHIP · H2 `/machines/` · projection · n8n import |
| **8** | **Maintainer 3** | `3369d11c` | SinaaiMonoRepo | Mono SSOT anchor · runtime E2E · mx law |

**Law:** Layer 1 **always beats** Layer 2 on routing conflict. M2/M3 **never** override Brain picks · Form JSON · Worker receipts.

**Brain wire (mandatory — every L2 session + every turn):**

```bash
python3 ~/Desktop/SourceA/scripts/brain_governance_wire_v1.py --json
```

| L2 role | Chat | Wire |
|---------|------|------|
| Worker | `fd67502f` | `~/.sina/governance-brain-wire-v1.json` → `active_decisions[]` |
| Researcher 2 | `20b12e67` | same |
| Maintainer 2 | `74f5ccab` | same |
| Maintainer 3 | `3369d11c` | same |

When `reconciled_decision.stale=true` → **IGNORE** archaeology · obey `active_decisions[]` + `queue_head`. Chat memory **never** outranks Brain wire on the same turn.

Machine hooks: `agent_session_gate_run_v1.py` · `worker_anti_staleness_heal_v1.py` · `goal1_lane_broker.py pickup` · `agent_truth_bundle_v1.py`.

---

## Layer 3 — third layer (portfolio product repos)

| Rank | Role | Workspace | Job |
|------|------|-----------|-----|
| **9+** | **TrustField** | TrustField Technologies | MSB/compliance product · prod smoke |
| **9+** | **Noetfield** | Noetfield | Advisory / auth packs |
| **9+** | **Forge** | DevBridge / Cursor OS Pro | No-code · desk parity |
| **9+** | **Other repos** | VIRLUX · Seven77 · … | Scoped delivery · Brain assigns lane only |

**Law:** L3 **never** overrides L1/L2 routing · Brain pick · Worker sa for SourceA spine · portfolio chats use **lane** `os/plan.json` — not raw SourceA sa paste.

**Maintainer 1** (`a53f3fa1`): **RETIRED** · search-only reference — not live authority.

---

## Machine pipeline (Python — not a chat rank)

Runs under Brain + Governance wire — **first infrastructure after human:**

| Class | Examples |
|-------|----------|
| Validators | `validate-*-v1.sh` · anti-staleness bundle |
| Orchestrators | `governance_center_run_v1.py` · `live_founder_decision_form_v1.py` |
| Wire | `agentic_layer_pipeline_v2.py` · `agentic_pipeline_lib_v1.py` · `l1_agent_pipeline_wire_v1.py` · `brain_governance_wire_v1.py` |
| Receipts | `~/.sina/*-v1.json` · governance event spine |

**Rule:** Chat memory **never** outranks machine pipeline output on the same turn.

---

## Forbidden inversions

| Wrong | Right |
|-------|-------|
| Governance decides build order alone | Brain reconciles · Governance constrains |
| Commercial picks sa-XXXX | Brain pick · Worker executes |
| Maintainer 2 headlines queue over Form | Form JSON + Brain wire first |
| Brief Specialist assigns Worker tasks | Brain handoff only |
| M3 overrides Brain two-hub law | Brain + SUPER_FAST_HUB LOCKED wins |
| Portfolio repo chat picks SourceA queue order | L3 lane plan only · Brain routes |

---

## Related (do not duplicate prose)

| Doc | Role |
|-----|------|
| `CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md` | OS charter |
| `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md` | L0–L6 machine numbering (reconcile pointer) |
| `GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md` | Paste blocks per specialist |
| `BRAIN_GOVERNANCE_WIRE_GAP_LOCKED_v1.md` | Wire gap fix receipt |
| `L1_BRAIN_PIPELINE_WIRE_LOCKED_v1.md` | L1→Brain pipeline receipt |
| `BRAIN_L2_WIRE_ALL_LOCKED_v1.md` | L2 Brain wire receipt |

---

*End SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2*
