# Agent pipeline / Maze speed trap — executors stuck on proof (INCIDENT-035 LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-15-INCIDENT-035  
**Classification:** MANDATORY READ — Brain · Worker · Governance · Maintainer · any agent running validators  
**Parent:** INCIDENT-008 (stall/timing) · INCIDENT-026 (Brain validator recursion) · INCIDENT-033 (false PASS while stuck) · INCIDENT-034 (complexity over wiring)  
**ASF order:** *Nobody stuck in Maze or pipelines — speed is important; balance proof with execution.*  
**Agent at fault:** Cursor Governance executor (2026-06-14/15) — ran 15–20 min Maze/find_critical during incident audit when Hospital already green  
**Root pointer:** `SINA_AGENT_PIPELINE_MAZE_SPEED_TRAP_INCIDENT_035_REPORT_LOCKED_v1.md`

---

## 1. Executive summary

**Verdict:** Executors treated **long pipelines as default hygiene** and **blocked founder velocity**. Law already says session start = session gate only — agents violated it by self-triggering Hospital/Maze during governance chats, incident reads, and “make sure clean” audits.

| What founder needed | What executor did |
|---------------------|-------------------|
| Fast honest disk quote + targeted fix | Chained **find_critical** (~8 min) + **anti-staleness bundle** (~3.5 min) + **Maze** (~15+ min) |
| RUN INBOX / product work | Sat in **Quarantine** receipt while queue advanced (sa-0554 → sa-0586) |
| Balance: proof when sick, speed when green | Ran **full Maze** when Hospital `escalate_maze: false` |

**One-line law:** **`AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` §Speed balance — session gate + fast validators default; Maze only on founder word `maze`; reuse fresh disk when green.**

---

## 2. Symptom (founder-visible)

- Governance chat “check incidents / clean layers” → agent silent 15+ minutes  
- User: *“why stuck?”* · *“no nobody stuck in maze or pipelines”*  
- Queue head moved during validator wall — looked like agent frozen  
- Maze receipt `ok: false` 16/19 left on disk — **optional passport**, not daily blocker, but agents treated it as mandatory

---

## 3. Root causes

| # | Cause |
|---|--------|
| R1 | **Audit template = run everything** — no “Hospital green → stop” gate in agent behavior |
| R2 | **Maze Phase C always re-runs find_critical** (~467s full fleet) even when `last-run.json` ≤1h · critical=0 |
| R3 | **find_critical bundle timeout** was 180s < 210s runtime → false critical → false Maze escalation narrative |
| R4 | **Governance meta chat confused with “sick patient”** — Maze is Tier 3 quarantine, not incident janitor |
| R5 | **No disk receipt reuse** — pipelines did not trust their own Hospital discharge |

---

## 4. Executor mistakes (this session)

| # | Mistake |
|---|---------|
| M1 | Ran **full Maze** twice during governance audit |
| M2 | Continued Maze after Hospital **H7b critical_count=0** |
| M3 | Did not **pre-sync queue** before long validators → `truth_match` drift |
| M4 | Marked poison **10/10 closed** while Maze receipt still red (cosmetic, but noisy) |
| M5 | Suggested founder wait for Maze passport as if daily ops required it |

---

## 5. Remediation (shipped)

| Item | Path / behavior |
|------|-----------------|
| Speed balance helpers | `scripts/agent_three_pipelines_lib_v1.py` — `find_critical_fresh()` · `hospital_green_fresh()` · `maze_speed_mode()` |
| Maze speed_mode | Reuse fresh find_critical + bundle receipts; orientation cert skip; governance `--tier fast` when Hospital green ≤24h |
| Hospital H7b skip | Reuse find_critical disk ≤2h when critical=0 |
| Queue self-heal | `validate-queue-ssot-unified-v1.sh` pre-unify + truth write |
| Law | `AGENT_THREE_PIPELINES_*` §Speed balance |
| Rule | `.cursor/rules/002-hospital-trigger-only.mdc` — never Maze on governance audit |

**Force full fleet (maintainer/founder only):** `SINA_MAZE_FORCE_FULL=1`

---

## 6. Agent rules (10 — mandatory)

1. **Session start** = `agent_session_gate_run_v1.py` only — never auto Hospital/Maze.  
2. **Governance / incident audit** = session gate + fast validators — **never Maze**.  
3. **Hospital green** (`escalate_maze: false`) → **stop** — do not run Maze unless founder says **maze**.  
4. **RUN INBOX** beats passport — Worker queue is the product spine.  
5. **Before long validators** → `queue_ssot_unify` + `run_inbox_disk_truth --write`.  
6. **Trust fresh disk** — find_critical ≤4h · critical=0 is proof enough for speed_mode.  
7. **Report timing** — if >2 min machine, say what runs and ETA.  
8. **Maze is quarantine** — sick agent gauntlet, not “clean all incidents” button.  
9. **Balance** — full proof when critical>0 or repeat incident; fast path when green.  
10. **Do not ask founder to wait** for optional Maze passport.

---

## 7. Close criteria

| Gate | Owner |
|------|-------|
| Speed helpers in lib + maze + hospital | **Verified shipped** 2026-06-16 · `maze_line` on truth bundle |
| Law §Speed balance + rule 002 update | **Shipped** |
| Agents stop self-Maze on governance chat | **Behavior — verify next sessions** |
| Registry row | **This incident** |
| Formal **remediated** | ASF confirms no repeat stuck sessions |

---

## 8. Related open (not this incident)

- INCIDENT-032 museum link — Maintainer  
- INCIDENT-033/034 registry rows — ASF formal close  
- Stale Maze receipt on disk — refresh only if founder says **maze**

---

**END INCIDENT-035**
