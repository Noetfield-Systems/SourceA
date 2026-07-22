# Agent Decision Stack & Smart Judgment (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-AGENT-JUDGMENT  
**Authority:** ASF · subordinate to `SINA_OS_SSOT_LOCKED.md` and `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md`  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §0c  
**Umbrella:** `META_REASONING_POLICY_STACK_LOCKED_v1.md` (L0–L12 stack — read first for governance loops)  
**Index:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` row `AGENT_JUDGMENT`  
**Machine mirror:** `system_roadmap.authorities.agent_judgment_*`

---

## 0. One sentence

**ASF/SSOT owns truth and build order; agents add smart judgment only to harden contracts, prevent repeat incidents, and improve implementation quality — never to invert authority or steer from critic paste alone.**

---
**Canonical WTM map:** `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`


## 1. What every agent needs (decision inventory)

Use this checklist before any non-trivial build, refactor, or governance edit.

### 1.1 Authority & law (who wins)

| Layer | Source | Use for |
|-------|--------|---------|
| **Apex** | `SINA_OS_SSOT_LOCKED.md` | Mono structure, ports, phases |
| **Router** | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | Which branch law to open |
| **Registry** | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | “Which doc wins?” per topic |
| **Alignment** | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | 12-order compare → keep → attach → convince |
| **Critic** | `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | GPT/ChatGPT paste class + label rule |
| **Fleet** | `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` | Who may edit SourceA |
| **Edit lock** | `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md` | Write permission |

### 1.2 Build truth (what step, what done)

| Layer | Source | Use for |
|-------|--------|---------|
| **WTM machine SSOT** | `scripts/system_roadmap.py` | `CURRENT_*_STEP`, `STEP_CATALOG`, `do_now`, phases |
| **WTM human map** | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | Founder-readable 33-step map |
| **WTM contracts** | `WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md` | Graph, memory, planning, packet boundaries |
| **Hub procedure** | `HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md` | SSOT → build → audit chain |
| **Hub audit** | `scripts/audit_hub_source_alignment.py` | Drift gate on every rebuild |

### 1.3 Runtime verification (is it real?)

| Layer | Source | Use for |
|-------|--------|---------|
| **Step validators** | `scripts/validate-*-v1.sh` | Per-step PASS/FAIL |
| **Spine** | `scripts/validate-execution-spine.sh` | Phase A gate |
| **Governance E2E** | `scripts/audit_agent_governance_e2e.py` | Agent fleet alignment |
| **Artifacts** | `~/.sina/*_v1.json` | Live keys in `STEP_CATALOG` |
| **Hub API** | `http://127.0.0.1:13020/api/*` | Runtime mirror of modules |

### 1.4 Blueprints & companions (structure, not override)

| Layer | Source | Role |
|-------|--------|------|
| **Unified blueprint** | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` | Agent/automation plane |
| **Big picture** | `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md` | Phase narrative |
| **Phase companions** | Exec intel · runtime · pre-LLM LOCKED v2 | Chapter detail for A/B/C/D |
| **Daily ops** | `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` | P0 / progress (not WTM step order) |

**Rule:** Blueprints inform. They do **not** override LOCKED source or `system_roadmap.py`.

### 1.5 Incidents & near-misses (what failed before)

| Layer | Source | Use for |
|-------|--------|---------|
| **Incident index** | `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` | Where incident docs live |
| **WTM UI incident** | `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | Never delete hub tables |
| **Phase naming** | `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` | INCIDENT-003/004 — stable step IDs |
| **Auto-paste** | `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` | No critic auto-steer |
| **Step migration** | `WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md` | ID history law |
| **Conflict / incident rooms** | `SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md` · `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` | Triage workflow |

### 1.6 Trace & self-healing logs

| Layer | Path | Use for |
|-------|------|---------|
| **Governance events** | `~/.sina/agent-governance-events.jsonl` | Agent decisions & remediations |
| **Agent reviews** | `~/.sina/agent-command-reviews.jsonl` | Review submissions |
| **Chronology** | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` | What changed when (not authority order) |

---

## 2. Authority hierarchy (never invert)

Higher rank wins. Agent judgment sits **between** machine SSOT and external input — it may **implement and harden**, not **reorder or replace** source.

| Rank | Class | Examples | Agent may |
|------|-------|----------|-----------|
| **0** | `ASF_ORDER` | “D1”, “build C4”, “do not commit” | Execute when explicit |
| **1** | LOCKED SOURCE | `*_LOCKED_vN.md` at root | Read, cite, upgrade only via alignment Orders 7–12 |
| **2** | MACHINE SSOT | `system_roadmap.py`, validators, audits | Edit with matching law doc + rebuild |
| **3** | SMART JUDGMENT | This doc §4–§6 | Contract harden, quality, incident prevention |
| **4** | Blueprints / companions | Unified blueprint, phase chapters | Inform only |
| **5** | Attachments | `archive/attachments/` | Stage until convince gate |
| **6** | `EXTERNAL_CRITIC` | GPT / ChatGPT paste | Compare only — label first line |

**Chronology registry** is history — never rank 1.

---

## 3. Judgment process (mandatory on external paste)

When input is not explicit `ASF_ORDER`:

| Step | Action |
|------|--------|
| **1 Classify** | `ASF_ORDER` · `SOURCE` · `EXTERNAL_CRITIC` · `SUGGESTION` |
| **2 Locate SSOT** | Step ID, phase, gate, live_key from `system_roadmap.py` |
| **3 Compare** | Same · extra · repeat · contradict · contract gap |
| **4 Keep order** | Do not move `CURRENT_*_STEP` from critic alone |
| **5 Decide line** | §4 — cross beneficial line? |
| **6 Act** | Implement · attach · reject · harden |
| **7 Verify** | Validator + audit + hub rebuild if SSOT touched |
| **8 Record** | Near-miss or material fix → governance event / incident pointer |

---

## 4. The beneficial line (smart progress)

Agents must seek **progress and best possible upgrade** for ASF — not passive compliance only.

### 4.1 Safe to cross (beneficial)

| Pattern | Example | Why healthy |
|---------|---------|-------------|
| **Contract alignment** | D1: normalize JSON to canonical schema when scope matches `STEP_CATALOG` | Downstream D2/C5 need stable SSOT |
| **Implementation quality** | Split modules for testability within same step ID | Better gates, same authority |
| **Incident hardening** | Add audit check after UI table deletion near-miss | Self-healing |
| **Validator truth** | Tighten `validate-*` when false PASS discovered | Dynamic healing |
| **Doc pointer** | Add index row — no restated prose | Anti-fragmentation |

### 4.2 Do not cross (unhealthy)

**No fake progress (ASF law):** `SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` — never report progress without proven evidence, meaningful effect, and durable output. UI green · form 0 open · chat “done” without disk = **forbidden**.

| Pattern | Why forbidden |
|---------|---------------|
| Fake progress / soft green reports | Violates NO_FAKE_PROGRESS · INCIDENT-006 |
| Reorder steps from critic | Violates alignment §0 |
| New step ID from paste without convince gate | Sub-step law |
| Scope creep (D1 adds embeddings) | Phase boundary violation |
| Hub UI content from critic tables | INCIDENT-002 |
| Replace LOCKED doc with chat prose | Rank inversion |

### 4.3 Line test (ask before acting)

All must be **yes** to cross the line with a code/law change:

1. **Scope** — Still the same SSOT step / topic?  
2. **Authority** — Rank 0–2 unchanged or properly upgraded (vN+1)?  
3. **Benefit** — Clear gain for founder: fewer incidents, clearer gates, faster next step?  
4. **Reversible** — Validator + audit prove the change?  
5. **No critic steering** — Would you do this if the paste never existed, given SSOT gap alone?

---

## 5. Dynamic self-healing loop

```
detect → classify → remediate → harden → verify → record
```

| Phase | Triggers | Actions |
|-------|----------|---------|
| **Detect** | Validator FAIL · audit FAIL · stale hub · incident report · session near-miss | Stop; do not stack fixes blindly |
| **Classify** | Authority violation · implementation gap · contract drift · env (stale server) | Pick rank-appropriate response |
| **Remediate** | Minimal diff — fix root cause | One problem at a time |
| **Harden** | Validator · audit script · law pointer · cursor rule | Prevent repeat |
| **Verify** | Full gate chain for touched layer | PASS before “done” |
| **Record** | `agent-governance-events.jsonl` · incident room if material | Learning retained |

**Near-miss:** Almost violated rank order or shipped false PASS — log and harden even if user did not file incident.

### 5b. Miss / confusion / wrong user answer (disk-first — mandatory)

**Law:** `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md`

When ASF corrects you, or you notice routing/assignment/authority drift in your own reply:

1. **Edit the root-cause doc on disk** (handoff, index, notice) — not a chat-only correction.  
2. **Wire** index · brain-pack · PRIORITY evidence.  
3. **Then** tell ASF what was wrong + what disk now says (≤1 screen).

**Forbidden:** Apology or “correction of last message” **before** disk hardening.

---

## 6. Learning from mistakes (incident → law)

| Lesson type | Where it lives | Agent action |
|-------------|----------------|--------------|
| Stable step IDs | INCIDENT-004 migration law | Never aesthetic rename |
| Hub table preservation | UI incident report | Shape only, never delete rows |
| Critic ≠ order | Critic law + auto-paste incident | Label + compare |
| Phase B frozen | WTM authority law | Read-only upstream |
| Contract vs hub wrapper | D1 canonical schema | Prefer machine-consumable SSOT |

New material incident → one canonical incident report + index row + optional audit/validator hardening — not a parallel roadmap.

---

## 7. Agent reply discipline

| Situation | First lines |
|-----------|-------------|
| GPT paste | `INPUT CLASS: EXTERNAL_CRITIC` |
| ASF “D1” / “build X” | Acknowledge step ID from `system_roadmap.py` |
| Contract alignment chosen | State: SSOT step unchanged; normalizing contract gap |
| Reject critic steer | Cite rank + locked doc — no debate essay |

---

## 8. Maintainer sync

When editing this topic:

1. This file (canonical).  
2. `system_roadmap.authorities.agent_judgment_*` fields.  
3. `SINA_AUTHORITY_INDEX_MAP` row `AGENT_JUDGMENT` + `NO_FAKE_PROGRESS`.  
4. `.cursor/rules/agent-smart-judgment.mdc` + `.cursor/rules/no-fake-progress.mdc`.  
5. `python3 scripts/build-sina-command-panel.py` → `audit_hub_source_alignment.py` OK.

---

**LOCKED** — Decision stack + smart judgment. Topic laws unchanged; agents gain explicit line for beneficial progress under ASF/SSOT.
