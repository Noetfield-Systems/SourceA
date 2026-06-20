# Goal Hierarchy — anti-drift law (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-06  
**Authority:** ASF correction — MSB/TrustField is **never** north star · **RunReceipt has no standalone numbered goal**  
**Parent:** `CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md` · `BRAIN_FOUNDER_INTENT_REGISTRY_LOCKED_v1.md`  
**Purpose:** Default brain/SYNC context order — Execution Core reads this before reconciling picks, research, or founder answers.

---

## Rule

**Disk wins.** When tiers conflict, **lower tier number wins** for "what is next."  
**Tier 5 runs in parallel only** — never replaces T0–T4 in default routing.

---

## Hub founder P0 (ASF locked 2026-06-11 — integrity Phase 2 pick 1.02)

**STRATEGIC-SLICE** — WTM execution spine — **sole hub headline P0.**  
**RunReceipt** and other T2b SKUs = **factory parallel only** — never replace STRATEGIC-SLICE on hub Today/Track.  
Receipt: `SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11_LOCKED_v1.md`

---

## T0 — North star

**Controlled automation factory** — minimal founder design, machine validators as truth, Hub-only control.

- Sellable outcome: **FORGE** (controlled app factory ASF can ship)
- Path: `sourcea-1000` REGISTRY → 10k ecosystem prompts
- Honesty: **Level 1 semi-auto NOW** · Level 3 zero-human **NOT claimed**
- Gates: `dispatch_ready` = `orchestrator_dispatch_ready()` when eval live + enforce · `eval_1b_gate_ok` required

---

## T1 — Reference targets (research only — not internal names)

External analogs for Goal A positioning. **Research Acquisitor compares; Execution Core decides.**

| Target | Use |
|--------|-----|
| **RAIS-class** | Autonomous agent / controlled automation analog |
| **Lovable** | Rapid app generation / hybrid UX analog |
| **Devin** | Long-horizon coding agent analog |
| **Cursor** | IDE-native agent analog |

**Law:** Never name these as internal layers, step IDs, or REGISTRY phases.

---

## T2 — Products (ship lanes)

### T2 primary — sellable app (default product clock)

| Product | Path | Role |
|---------|------|------|
| **FORGE** | `~/Desktop/forge/` | **Primary sellable app** — ports SourceA spine; PRD + `docs/LAUNCH_CHECKLIST.md` |

Default product focus for automation clock: **FORGE beta path** before any other SKU.

### T2b — Side SKUs (one bucket — parallel factory lanes only)

**Law:** MergePack · RunReceipt · Cursor OS Pro are **one bucket**. **Forbidden:** standalone numbered goal for RunReceipt (or any single side SKU).

| SKU | Path / thread | Role |
|-----|---------------|------|
| **MergePack** | `~/Desktop/mergepack` · `THREAD-MERGEPACK` | Evidence factory · revenue proof · KPI trio |
| **RunReceipt** | `product/` · `THREAD-FACTORY` | Factory PASS/FAIL receipt pack — **NOT** automation loop · **NOT** RAIS · **NOT** spine SSOT (`SINA_BIG_PICTURE_ROADMAP` §0.5) |
| **Cursor OS Pro** | `~/Desktop/AI Dev Bridge OS/mobile` | App Store SKU — `MANDATORY_CURSOR_OS_PRO_CHAT_LOCKED_v1.md` |

**Hub `P0-RUNRECEIPT`:** legacy factory tracker UI only — **must not** drive Brain default routing.

**REGISTRY s5:** may contain factory SKU tasks inside the 100-pack — label **parallel lane work**, never north star.

---

## Mandatory goals map (`hundred_steps_per_goal` — LOCKED numbering)

Brain **must** use this table for step-count queries. **Do not invent Goal 2 = RunReceipt.**

| Goal # | Tier | Name | Step model |
|--------|------|------|------------|
| **1** | T0 + T4 | Controlled automation factory + remote M8 | **1000-pack** (10×100) · live `sa-XXXX` · **NOT RunReceipt** |
| **2** | T3 | World Target Model + Pre-LLM | **33 steps** (WTM A→D) + strategic phases 0–5 |
| **3** | T2 primary | **FORGE** | PRD 8-week MVP + **10-item** launch checklist |
| **4** | T1 | Research sensor (RAIS-class, Lovable, Devin, voice…) | Sector briefs · no 100-pack · no pick reorder |
| **5** | **T2b** | **Side SKUs (one bucket)** | MergePack + **RunReceipt** + Cursor OS Pro — parallel only |
| **6** | — | Strategic engineering (dispatch path) | Phases 0–5 (`STRATEGIC_NEXT_STEPS_SYNTHESIS`) |
| **7** | T5 | TrustField MSB | Commercial vault — **suppressed** in default routing |

**Forbidden map shapes:**
- Goal 2 = RunReceipt (standalone)
- RunReceipt listed as peer to REGISTRY / WTM / FORGE north star
- Hub P0-RUNRECEIPT as default “what is next”

---

## T3 — World Target Model + Pre-LLM

| Asset | Path |
|-------|------|
| **WTM map** | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` — A→D execution map; Hub tab `system-roadmap` |
| **Pre-LLM code** | `scripts/pre_llm/` — D1–D16 modules |
| **Runtime packet** | `~/.sina/llm_context_packet_v1.json` |

**Bottleneck (honest):** dispatch/eval closure **after** packet — not new D-modules (`STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md`).

---

## T4 — Execution spine

| Lane | Path / handoff |
|------|----------------|
| **SourceA workers** | `sa-XXXX` via `plan-no-asf-run.sh` · `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` |
| **SinaPromptOS** | `~/Desktop/SinaPromptOS` · thin Cursor adapter |
| **M8 / Wire** | AI Dev Bridge OS · `THREAD-WIRE` |

### T4b — n8n (runtime glue only)

**Law:** `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`

- n8n = **runtime glue** for triggers/webhooks — not architecture SSOT
- Spine authority = SourceA execution kernel + validators + Hub Actions
- Never reorder REGISTRY or WTM from n8n workflow changes alone

---

## T5 — Parallel clocks (never default "what is next")

| Clock | Scope | Trigger |
|-------|-------|---------|
| **TrustField MSB P10** | Agentic outreach · 3 agent-booked demos · CanadaBuys | **`@sina-agentic-commercial`** — founder never email/call |

**Forbidden default:** MSB, demos, insurance, or GTM lectures as first answer to system/automation questions.

---

## SYNC reconciliation (Execution Core)

On every SYNC or "what now":

1. State active tier (usually T0 + T2 FORGE + T3 WTM + T4 pick)
2. Note T5 **only if** ASF invoked founder-mode revenue
3. One `sa-XXXX` worker handoff when machine lane due
4. Research pause when REGISTRY + FORGE checklist beat new sector scans

---

## Wire

| File | Role |
|------|------|
| `BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md` | §Goal Hierarchy · §Products |
| `FOUNDER_ADVISOR_PROFILE_LOCKED_v1.md` | §8–§9 default answer shape |
| `sync-brain-pack.sh` | Mirror to `~/.sina/brain/` |

---

*End GOAL HIERARCHY v1*
