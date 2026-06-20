# Agent three pipelines — Orientation · Hospital · Maze (LOCKED v2)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF design order  
**Supersedes body:** v1 (same filename — tier model + enhanced machines)  
**Extends:** `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md`  
**Machine SSOT:** `~/.sina/agent-three-pipelines-registry-v1.json` · `scripts/agent_three_pipelines_lib_v1.py`  
**Router:** `scripts/agent_three_pipelines_router_v1.py`  
**Orchestrators:** `agent_orientation_pipeline_v1.py` · `agent_hospital_pipeline_v1.py` · `agent_maze_pipeline_v1.py`

---

## One sentence

> **Orientation (short, mandatory) teaches WHY + gate + tree · Hospital (medium) heals working agents · Maze (long, worst) quarantines the sick until disk proves full understanding.**

---

## Tier model (length + severity)

| Tier | Pipeline | Trigger | Length | Who | Job |
|------|----------|---------|--------|-----|-----|
| **1** | **Orientation** (Atlas) | `orientation` | **Short** · 15–30 min read | **Every** raw AI · new Cursor · first visit | WHY · good **gate** · good **tree** · ecosystem map · **no execution** |
| **2** | **Hospital** (Clinic) | `hospital` | **Medium** · 5–15 min | Working agents (Worker · Brain · …) | Remember · remind · memory · heal · discharge |
| **3** | **Maze** (Quarantine) | `maze` | **Speed ~15–90 s** when disk green · **Full 30–90+ min** when sick | Very sick agents · founder refresh | Passport · speed reuses fresh receipts · full when `critical>0` |

**Rule:** Orientation < Hospital < Maze in severity. **Length:** Maze **speed mode** (default when `find_critical` fresh · critical=0) is **shorter than Hospital**. Maze **full gauntlet** (`SINA_MAZE_FORCE_FULL=1`) is longest. Never send a new arrival to Maze. Never skip Orientation.

---

## Architecture (corrected)

```text
                         ASF (one word)
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
    TIER 1 ORIENTATION   TIER 2 HOSPITAL    TIER 3 MAZE
    (Atlas · SHORT)      (Clinic · MED)     (Quarantine · SPEED or FULL)
           │                  │                  │
    gate + tree + WHY   memory+remind+heal   re-orient (skip if cert fresh)
    reading pack        session gate fast    10 mandatory reads
    ecosystem map       dual hub heal        disk proof (reuse receipts)
    zero authority      H7b find_critical    session gate ×1 role (speed)
           │            role skill remind    governance fast / full
           │                  │               lane law + incidents
           │                  │               3 FOUND comprehension
           ▼                  ▼                  ▼
    certificate          discharge note       passport
    (no authority)       (back to duty)       (clears quarantine)
           │                  │                  │
           └──────────────────┴──────────────────┘
                              │
                   H1 one-line · H2 maze table · Operator (Maze only)
```

**Escalation:** Hospital → Maze when `critical_count > 0` or repeat incident · never Maze → Hospital shortcut.

---

## Speed balance (INCIDENT-035 — mandatory)

| Situation | Do | Do not |
|-----------|-----|--------|
| Session start | Session gate only | Auto-run Hospital / Maze / Orientation |
| Hospital green · `escalate_maze: false` | Stop · RUN INBOX | Self-trigger full Maze |
| Founder says **maze** · disk green | **Speed mode** (~15–90 s) · passport refresh | Block founder on 30–90 min wall |
| `critical>0` · repeat incident | Full gauntlet · `SINA_MAZE_FORCE_FULL=1` | Trust speed skips |
| Stale red maze receipt logged | Ignore for daily ops · quote `maze_line` | Treat passport as daily blocker |

**Helpers (lib):** `find_critical_fresh()` · `hospital_green_fresh()` · `anti_staleness_bundle_fresh()` · `maze_speed_mode()` · `maze_status_line()`

**Truth bundle line:** `maze_line` from `~/.sina/agent-live-surfaces-v1.json` — e.g. `MAZE PASSPORT · speed · quarantine=clear · optional not daily`

---

## Why three (not one mega-heal)

| Problem | Wrong fix | Right pipeline |
|---------|-----------|----------------|
| Raw Cursor / new AI | Dump 9MB hub | **Orientation** — read-only map, no authority |
| Drifted Worker/Brain | Light refresh only | **Hospital** — memory + remind + lane + heal |
| Repeat incidents / critical bugs | Same hospital again | **Maze** — hard gauntlet, no exit without PASS |

**Founder triggers (one word):**

| Say | Pipeline | Agent action |
|-----|----------|--------------|
| **orientation** | P1 Atlas | Read map · no implement |
| **hospital** | P2 Clinic | Remind · memory · heal · discharge note |
| **maze** | P3 Quarantine | Full gauntlet · H2 + Operator · pass to exit |

**Session start (every chat — no founder word):**

| Allowed | Forbidden |
|---------|-----------|
| `agent_session_gate_run_v1.py --role <role> --json` only | **orientation** · **hospital** · **maze** pipelines |
| Daily duty card · truth bundle · mirror inject | `agent_orientation_pipeline_v1.py` on start |
| | `agent_hospital_pipeline_v1.py` on start |
| | `agent_maze_pipeline_v1.py` on start |

> **Law:** Session start = session gate only. Hospital / Maze / Orientation run **ONLY** when founder says one word: `orientation` · `hospital` · `maze`. **Stale maze receipt `ok:false` does not block RUN INBOX** — passport is optional hygiene.

---

## P1 — ORIENTATION (Atlas · Tier 1 · SHORT)

**Audience:** **Everyone** entering the system — raw AI · new Cursor · SEMEJ · portfolio first visit.

**Goal:** WHY we exist · **good gate** (governance entry) · **good tree** (decision stack + branches) · full map · **zero execution authority**.

### Stations (O1–O20 · SSOT: `data/sourcea_agentic_unified_bundle_v1.json`)

| # | Station | Source / node |
|---|---------|---------------|
| O1 | Start here | `brain-os/law/entry/START_HERE_LOCKED_v1.md` |
| O2 | Governance gate | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` |
| O3 | Authority index | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` |
| O4 | Decision stack / gate tree | `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` |
| O5 | WHY entry | `README_SOURCE_A.md` |
| O6 | Agentic stack | `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` → `agentic_layer_fast` |
| O7 | Two hubs | `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` |
| O8 | Three pipelines law | this file → `orientation_pipeline_v1` |
| O9 | Roles | `UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md` |
| O10 | Architecture | `docs/ARCHITECTURE.md` |
| O11 | Onboarding | `docs/ONBOARDING.md` |
| O12 | Reading pack written | `~/.sina/agent-orientation-reading-pack-v1.json` |
| O13 | Ecosystem catalog | probe · `ecosystem_master_catalog_v1.py` |
| O14 | Truth bundle | probe · `agent_truth_bundle_v1.py` |
| O15 | Orient routing | `docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md` → `orient_routing_v1` |
| O16 | Node mesh plan | `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md` |
| O17 | Foundational index | `docs/SOURCEA_FOUNDATIONAL_AGENTIC_SYSTEMS_INDEX_LOCKED_v1.md` |
| O18 | Agentic pipeline map | probe → `agentic_layer_fast` |
| O19 | Orient routing cascade | probe → `orient_routing_v1` |
| O20 | Graph LAT dry-run | probe → `pipeline_node_graph_runner_v1` · tier T_lat |

### Python

```bash
python3 scripts/agent_three_pipelines_router_v1.py orientation --role any --json
# or
python3 scripts/agent_orientation_pipeline_v1.py --role any --json
```

Receipt: `~/.sina/agent-orientation-receipt-v1.json` (schema v2)

---

## P2 — HOSPITAL (Clinic · Tier 2 · MEDIUM · shorter than Maze)

**Audience:** Existing working agents — not new arrivals (they need Orientation first).

**Goal:** Not auto-heal alone — **remember who you are**, sync memory, remind laws, heal disk, discharge note.

### Stations (H0–H9)

| # | Station | Purpose |
|---|---------|---------|
| H0 | Orientation certificate | Must have completed Tier 1 (or re-run orientation) |
| H1 | Memory mirror | Skills + NEVER lines |
| H2 | Rules in charge | What law wins now |
| H3 | Truth bundle | Factory-now · queue head |
| H4 | Session gate (fast) | Conduct + wire |
| H5 | Conscious recovery | Thread link if thin context |
| H6 | Dual hub heal | H1/H2 fresh |
| H7 | Agentic pipeline fast | L1/L2 health |
| H7b | Critical bugs refresh | Reuse `find-bugs/last-run.json` ≤2h when critical=0 |
| H8 | Critical bugs check | Escalate to Maze if > 0 |
| H9 | Role skill reminder | Job + forbidden paths |

### Python

```bash
python3 scripts/agent_three_pipelines_router_v1.py hospital --role worker --json
```

Receipt: `~/.sina/agent-hospital-receipt-v1.json` (schema v2)

---

## P3 — MAZE (Quarantine · Tier 3 · LONG · WORST)

**Audience:** Very sick agents — critical bugs · repeat incident · lane cross · ASF says **maze**.

**Goal:** Passport when founder says **maze** · **speed** when disk already green · **full** when sick.

### Phases (speed skips marked · full with `SINA_MAZE_FORCE_FULL=1`)

| Phase | ID | What |
|-------|-----|------|
| **A** | Re-orientation | Orientation replay — **skip** if cert ≤24h (speed) |
| **B** | Clarification | 10 mandatory reads + reading pack gate tree |
| **C** | Disk proof | Hub health · find_critical (**reuse** if fresh) · anti-staleness (**reuse** if fresh) · wire · two-hub (**defer** speed) · session gate **×1 role** · governance **fast/full** · registry honest |
| **D** | Lane law | Role SKILL exam · brain_lane_guard |
| **E** | Incident spine | governance spine + incident dir awareness |
| **F** | Comprehension | Agent writes **3 FOUND lines** → `~/.sina/agent-maze-comprehension-v1.json` |
| **G** | Operator + H2 | Shadow quiz · `/machines/` maze_blockers bucket |

### Python

```bash
python3 scripts/agent_three_pipelines_router_v1.py maze --role worker --json
# Speed (default when disk green):
python3 scripts/agent_maze_pipeline_v1.py --role worker --json
# Full gauntlet (maintainer / critical>0):
SINA_MAZE_FORCE_FULL=1 python3 scripts/agent_maze_pipeline_v1.py --role worker --json
python3 scripts/agent_maze_pipeline_v1.py --write-found "FOUND: …" --write-found "FOUND: …" --write-found "FOUND: …" --json
```

Receipt: `~/.sina/agent-maze-receipt-v1.json` (includes `duration_mode` · `elapsed_sec` · `maze_status_line`) · Passport: `~/.sina/agent-maze-passport-v1.json`

---

---

## Registry (unified SSOT)

File: `~/.sina/agent-three-pipelines-registry-v1.json` (schema v2 body)  
Lib: `scripts/agent_three_pipelines_lib_v1.py` · Router: `scripts/agent_three_pipelines_router_v1.py`

---

## Validators

```bash
bash scripts/validate-agent-three-pipelines-v1.sh
```

---

## Implementation status (v2)

| Item | Status |
|------|--------|
| Tier model + gate tree + reading pack | **SHIPPED** |
| Router + lib + enhanced orchestrators | **SHIPPED** v2 |
| Maze 7 phases · comprehension attest | **SHIPPED** |
| Maze speed mode + `maze_line` truth bundle | **SHIPPED** 2026-06-16 · INCIDENT-035 |
| H1 worker-hub H1-aware validators (no stale app.js) | **SHIPPED** 2026-06-16 |
| H1/H2 UI buttons | Maintainer backlog |
| Operator quiz | Shadow · Form PICK |

---

*End AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v2 (file v1 name retained)*
