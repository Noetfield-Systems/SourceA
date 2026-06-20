# Sina Command Center — vision & architecture (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
| | |
|--|--|
| **Version** | `SINA-COMMAND-1.0-LOCKED` |
| **Product name** | **Sina Command** (working title) |
| **Home** | Sina AI Personal Database — Layer A face |
| **Physical path (v1)** | `SinaaiMonoRepo/SinaaiDataBase/command-center/` |
| **HQ workspace** | `~/Desktop/SinaaiDataBase` (Cursor shell → points here) |

---

## Problem (why we need this)

| Symptom | Cause |
|---------|--------|
| Agent reads “last sentence” only | 40+ Source A docs, 14 chats, no single surface |
| Drift | mergepack evidence vs “parked” in JSON; M8 vs MP-* |
| Lost components | Same truth in SourceA, mono governance, Prompt OS, Runtime |
| No supervision view | Fleet exists but not tied to roles, P0, blockers |
| ASF fatigue | You are the merge layer — should be the UI |

---

## North star

> **One laptop home.** See every agent, every role, your duties, today’s law, and drift — in one chic local app. Earphones get a 2-minute brief. Sources stay abundant underground; the **bowl** is what you read daily.

---

## Three-layer product (permanent)

```text
┌─────────────────────────────────────────────────────────┐
│  SINA COMMAND (chic UI)     port :13020 local only      │
│  Tabs: Today · Fleet · Roles · Plans · Sources · Audio  │
└───────────────────────────┬─────────────────────────────┘
                            │ reads
┌───────────────────────────▼─────────────────────────────┐
│  THE BOWL (generated)     sina-bowl/state.json + .md    │
└───────────────────────────┬─────────────────────────────┘
                            │ aggregates
┌───────────────────────────▼─────────────────────────────┐
│  SOURCES (abundant, organized)                          │
│  SourceA · Mono L0-L4 · PromptOS · Runtime · Repos      │
└─────────────────────────────────────────────────────────┘
```

---

## What SinaaiDataBase **is** (name truth)

| Layer | Path | Role |
|-------|------|------|
| **Personal Database (Layer A)** | `SinaaiMonoRepo/SinaaiDataBase/data/` | Who you are, agents, knowledge — **wins on conflict** |
| **Governance** | `.../governance/` | Registry, notices, cognitive contract |
| **Command Center (new face)** | `.../command-center/` | **Observation + control** — not SSOT author |
| **Desktop shell** | `~/Desktop/SinaaiDataBase/` | Cursor HQ workspace + START_HERE bridges |

Command Center **does not replace** Layer A — it **sits on top** and reads it + Source A.

---

## UI — Sina Command v1 (chic, local)

### Design principles

- Dark, flat, DevBridge-quality spacing (proven on phone desk)
- No gradient slop; accent only for P0 and drift
- **One screen answers:** “What matters today?”
- Click through to canon files — never duplicate bodies in UI

### Tabs

| Tab | Shows |
|-----|--------|
| **Today** | Bowl rendered: P0, todos, blockers, drift badges, wire proof |
| **Fleet** | All Cursor workspaces; active 24h; preview; thread guess |
| **Roles** | ASF, HQ, Architect, 5 lanes, PAIOS 4, Runtime workers — expandable |
| **Plans** | `parallel_plans` kanban-style by status |
| **Sources** | Tier map: what to read when; link open in Finder |
| **Audio** | Play morning brief (macOS `say` or in-app TTS) |

### Tech (recommended)

| Piece | Choice | Why |
|-------|--------|-----|
| UI | **Next.js 15** in `command-center/` | Same stack as MergePack; pretty; local |
| Data | `state.json` from bowl builder | No DB for v1 |
| API | Optional tiny FastAPI on `:13021` | Fleet scan, bowl rebuild on button |
| Phone | PWA later | Same URL on LAN as DevBridge pattern |

**v1 today:** Sina Command v2 static UI (`agent-control-panel/assets/`) + bowl. **v2:** Next.js in mono. **v3:** Prompt OS tab + Runtime health.

---

## Earphones / morning brief

Script: `scripts/sina-morning-brief.sh`

Reads `sina-bowl/brief.txt` (plain language):

- Good morning. P0 is RunReceipt. Two blockers need you. Wire G3 pending. Fourteen agent workspaces; six active yesterday. Open Sina Command for detail.

Languages: EN default; FA optional flag. **2 minutes max.**

---

## Source unification (anti-drift)

### Tier system (only these hit daily)

| Tier | Count | Examples |
|------|-------|----------|
| **0 Bowl** | 1 generated | `DAILY_BOWL.md` |
| **1 Daily** | 5 | README_SOURCE_A, command center, Understanding Roles, thread registry, bowl spec |
| **2 Thread** | 1 active | e.g. MERGEPACK_SUITE when in that thread |
| **3 Archive** | everything else | `_archive/`, `_TOPICS/`, old DAY*.md |

### Drift rules (auto in bowl)

| Check | Alert when |
|-------|------------|
| P0 lock vs mergepack progress | Evidence v1.3 but JSON says parked |
| Thread registry vs command center | THREAD-MERGEPACK status mismatch |
| M8 label in chat | User says M8 but means MP-* |
| Architect vs GLOBAL_PRIORITY | B-001 still critical |

ASF resolves drift by editing **one** JSON lock — bowl regenerates.

---

## Agent company map (who the UI supervises)

### Cursor plane (14+ workspaces)

Five **delivery** lanes + wire + HQ + utilities + investor + smoke workspaces.

### Prompt OS plane

Orchestrator, dispatch, ingest — **meta**, not daily lane 6.

### Runtime plane (PAIOS)

Telegram company — separate tab in v2; read-only health in v1.

### Subagents

Parent session only; counted in fleet, not separate employees.

---

## HQ agent (`ROLE-CURSOR-HQ`) — full duties in Command Center

The Cursor agent in **SinaaiDataBase** workspace is the **steward** of Sina Command:

| Duty | Deliverable |
|------|-------------|
| Keep bowl builder accurate | `build-sina-daily-bowl.py` |
| Keep drift rules updated | `DRIFT.json` schema |
| Do not own five repo delivery | Lane chats |
| Unify docs when ASF locks | Source A + mono L0 pointer entries |
| Report fleet | Scanner |

---

## Phased build (no rush — permanent)

| Phase | Deliverable | Time |
|-------|-------------|------|
| **0** ✅ | Bowl spec, vision, fleet scanner, desk HTML | Done |
| **1** | `build-sina-daily-bowl.py` + `DAILY_BOWL.md` + drift | This week |
| **2** | Next.js Sina Command MVP (Today + Fleet + Roles) | 1–2 weeks |
| **3** | Audio brief + Plans tab + open-file actions | +1 week |
| **4** | Prompt OS dispatch tab; VERIFY ingest | +2 weeks |
| **5** | Runtime roster; phone PWA | Later |

---

## What we will NOT do

- Cloud SaaS multi-tenant dashboard
- Replace Source A SSOT with UI edits (v1 read-only; ASF edits files)
- Merge Runtime into Cursor mentally in one chat
- 100-agent simulation before 5 lanes work

---

## Files (this program)

| Doc | Role |
|-----|------|
| `SINA_DAILY_BOWL_LOCKED_v1.md` | Bowl contract |
| `UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md` | Role map |
| `AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md` | Fleet v0 |
| `SINA_COMMAND_CENTER_VISION_LOCKED_v1.md` | This file |
| `sina-bowl/` | Generated daily |
| `SinaaiMonoRepo/.../command-center/` | UI v1 home |

---

**LOCKED pending ASF answers in § Questions below.**

---

## Questions for ASF (before Phase 2 UI code)

1. **P0 truth for bowl header:** RunReceipt only, or RunReceipt + MergePack KPI trio in parallel?
2. **Command Center root:** build UI in **mono** `SinaaiDataBase/command-center/` or **Desktop** shell repo?
3. **Morning brief language:** English, Farsi, or bilingual?
4. **Edit from UI in v1:** read-only only, or allow “mark todo done” → writes JSON?
5. **Earphones:** macOS `say` enough, or integrate ElevenLabs / AirPods shortcut?

---

**LOCKED.**
