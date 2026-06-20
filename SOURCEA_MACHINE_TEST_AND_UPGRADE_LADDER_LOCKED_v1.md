# SourceA — Machine test & upgrade ladder (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`  
**Extends:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` · `ENFORCEMENT-6MO-MASTER-PLAN-v1.md`  
**Runner:** `scripts/machine_test_ladder_run_v1.py`  
**Receipt:** `~/.sina/machine-test-ladder-receipt-v1.json`  
**Validator:** `scripts/validate-machine-test-ladder-v1.sh`

---

## One sentence

> **Test by cadence logged receipts — not by “green UI.” Upgrade only when a W1/W2/W3 win moves, with a validator before code and a baseline before/after photo.**

---

## 0. What testing is NOT

| Wrong | Right |
|-------|-------|
| Click until hub looks green | Run tiered validators · read receipts |
| Run all 355 `validate-*.sh` daily | Run **intent groups** at the right cadence |
| Trust legacy 9MB monolith | H1 ~4KB API + disk SSOT |
| Chat “looks fixed” | Broker advanced · receipt moved |
| Rebuild hub on Refresh whim | Schedule or Form PICK only |

**Law:** If UI and receipt disagree, **receipt wins** (`SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md`).

---

## 1. Four layers (mental model)

```text
┌─────────────────────────────────────────────────────────────────┐
│  LAYER A — FOUNDER SURFACES (what you see)                      │
│  H1 Super Fast  http://127.0.0.1:13020/     daily bookmark      │
│  H2 Machine Hub http://127.0.0.1:13020/machines/  weekly depth  │
│  Legacy archive /legacy/                     never daily truth  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ reads
┌─────────────────────────────────────────────────────────────────┐
│  LAYER B — DISK SSOT (what machines write)                      │
│  ~/.sina/*-receipt-v1.json · agentic-layer-pipeline-v2.json     │
│  find-bugs/last-run.json · h2-pending-registry-v1.json          │
│  worker-prompt-inbox-v1.json · goal1-worker-turn-bind-v1.json   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ proven by
┌─────────────────────────────────────────────────────────────────┐
│  LAYER C — VALIDATORS (355+ validate-*.sh + Python gates)       │
│  Intent groups — not one mega-run                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ feeds
┌─────────────────────────────────────────────────────────────────┐
│  LAYER D — FACTORY / BROKER (did work actually happen?)         │
│  goal1_lane_broker · WORKER_ROUND_REPORT · orchestrator idle    │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Question | Skip cost |
|-------|----------|-----------|
| **H1** | Can I work today? (task · queue · form · health) | False green · slow hub |
| **H2** | What is pending for later phases? | Heavy clutter on daily |
| **Disk** | What is true right now? | Chat fiction |
| **Validators** | Is truth honest and wired? | Ship lies |
| **Broker** | Did Worker finish a turn? | Orphan sa · stuck queue |

---

## 2. Machine refinement pipelines (parallel to agent care)

**Unified law:** `REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md`  
**Machine law:** `MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md`

| Pipeline | Trigger | Tier | Job |
|----------|---------|------|-----|
| **Calibrate** | `calibrate` | 1 short | Map machines · validators · upgrade board |
| **Tune** | `tune` | 2 medium | Runs test ladder (daily/3day) · baseline · heal |
| **Forge** | `forge` | 3 long | Upgrade gauntlet · before/after baseline · passport |

**Tune** embeds this document's tiered ladder. **Forge** runs weekly+monthly ladder + PROVEN lines.

Escalation: `critical_count > 0` at tune → **forge** (same logic as agent hospital → maze).

```bash
python3 scripts/refinement_unified_router_v1.py machine calibrate --json
python3 scripts/refinement_unified_router_v1.py both hospital tune --role worker --json
```

---

## 2b. Agent care pipelines (test context)

Three pipelines are **not** the daily test ladder — they are **agent lifecycle machines**. Test them separately.

| Pipeline | Trigger | Test when | Proof |
|----------|---------|-----------|-------|
| **Orientation** | `orientation` | New workspace · new agent | `agent-orientation-receipt-v1.json` · reading pack |
| **Hospital** | `hospital` | Drift · weekly health | `agent-hospital-receipt-v1.json` · discharge note |
| **Maze** | `maze` | `critical_count > 0` · repeat incident | `agent-maze-passport-v1.json` |

**Hospital H8 fork (machine decides — not agent):**

```text
Hospital runs H0–H9
H8 reads ~/.sina/find-bugs/last-run.json → critical_count
  critical_count == 0  →  discharge · back to duty
  critical_count > 0   →  quarantine tag · must run Maze
```

**Quarantine** = status file `~/.sina/agent-maze-quarantine-v1.json` (`active: true`) — not a hub, not a running process. Cleared only by Maze passport.

**Who sets `critical_count`?** → `find_critical_bugs.py` (weekly tier + Maze). Hospital **reads** it; Hospital does **not** re-run the full bug hunt at H8.

Smoke: `bash scripts/validate-agent-three-pipelines-v1.sh`

---

## 3. Tiered test ladder (cadence — not mood)

Run the ladder machine:

```bash
python3 scripts/machine_test_ladder_run_v1.py --tier daily   --role worker --json
python3 scripts/machine_test_ladder_run_v1.py --tier 3day    --role worker --json
python3 scripts/machine_test_ladder_run_v1.py --tier weekly  --role worker --json
python3 scripts/machine_test_ladder_run_v1.py --tier monthly --role worker --json
```

Receipt: `~/.sina/machine-test-ladder-receipt-v1.json`

### Daily (~2 min you · agents run disk)

**You (H1 only — no Terminal):**

1. Open Super Fast Hub — task · queue · form count · health pill
2. Tap **Safety check** if anything feels stale
3. Read **one-line** Judge/Thread alarms — full tables only on H2

**Agents / Maintainer (automated ladder `daily`):**

| Step | Proves |
|------|--------|
| `validate-super-fast-hub-v1.sh` | H1 light · payload bounded · no monolith prefetch |
| `validate-two-hub-v1.sh` | H1 + H2 siblings fresh |
| `governance_center_run_v1.py --tier fast` | Self-heal · pipeline · drift · inbox sync |
| `agentic_layer_pipeline_v2.py --tier fast` | L1→Brain · L2 wire · health |
| `agent_session_gate_run_v1.py --role <role>` | Memory · truth · conduct (**use your lane role**) |
| `validate-agent-three-pipelines-v1.sh` | Orientation/Hospital/Maze scripts alive |

**Read after daily:**

- `~/.sina/two-hub-heal-receipt-v1.json`
- `~/.sina/governance-center-receipt-v1.json`
- `~/.sina/agentic-layer-pipeline-v2.json`

### Every 3 days (`3day` tier)

| Step | Proves |
|------|--------|
| Daily bundle | (included) |
| `validate-founder-docs-no-terminal-v1.sh` | UI never pushes Terminal on you |
| `validate-hub-p0-no-autorun-v1.sh` | INCIDENT-028 class · no AUTO-RUN |
| `validate-agentic-layer-wire-v1.sh` | Brain/L1/L2 master wire |

### Weekly — H2 day (`weekly` tier)

| Step | Proves |
|------|--------|
| 3-day bundle | (included) |
| `governance_center_run_v1.py --tier full` | Judge · Thread · planner chain |
| `validate-anti-staleness-bundle-v1.sh` | Full AS chain |
| `find_critical_bugs.py` | **`critical_count` must be 0 before ship talk** |
| `validate-broker-receipt-cycle-v1.sh` | Done rows have honest receipts |

**You on H2:** Judge + Thread buttons · pending registry vs Form open count.

**Rule:** If `critical_count > 0`, Hospital will **refuse discharge** and tag quarantine — fix or run Maze before claiming green.

### Monthly — strict (`monthly` tier)

| Step | Proves |
|------|--------|
| Weekly bundle | (included) |
| `audit_hub_source_alignment.py` | WTM steps match hub surface |
| `ecosystem_master_catalog_v1.py --json` | Machine index still honest |

**Strict hub build:** ASF Action only · Legacy/H2 — **never** daily Refresh path.

---

## 4. Receipt checklist — “did the machine work?”

Never ask “is the hub green?” Ask **“which receipt moved?”**

| Machine | Success | Failure |
|---------|---------|---------|
| Dual hub heal | `two-hub-heal-v1` ok · H1/H2 `fresh` | stale · `form_aligned: false` |
| Agentic pipeline v2 | `health.status: ok` · `issues: []` | L1/L2 wire stale |
| Governance center | All fast-tier steps ok | drift_engine · inbox_drift fail |
| Worker broker | `WORKER_ROUND_REPORT` · orchestrator advanced | sa_mismatch · turn open |
| find_critical_bugs | `critical_count: 0` | any critical → Maze path |
| PromptOS ingest | `outputs/inbox/rejected/` empty | B-001 class |
| Test ladder | `machine-test-ladder-receipt-v1.json` `ok: true` | step tail shows FAIL |
| Hospital | `escalate_maze: false` · discharge note | quarantine written |
| Maze | passport ok · quarantine cleared | incomplete phases |

---

## 5. Validator map — run by intent (not 355 at once)

Use `ecosystem_master_catalog_v1.py --json` when **planning** — not as a daily bash loop.

| Intent | Master gates | Protects |
|--------|--------------|----------|
| **Daily ops** | two-hub · super-fast-hub · worker-inbox-drift | H1 law |
| **Agentic wiring** | agentic-layer-wire · brain-l2-wire · l1-agent-pipeline | L1/L2/Brain stack |
| **Governance spine** | governance-center · governance-event-spine · broker-receipt-cycle | G4/G7 |
| **Enforcement demo** | demo-enforcement · universe-invariants · closeout-gate | W1/W2 |
| **Anti-staleness** | anti-staleness-bundle | AS-01..AS-18 |
| **Fleet honesty** | registry-honest · monitor-honesty · no-fake-progress | INCIDENT-006/007 |
| **Agent pipelines** | validate-agent-three-pipelines-v1.sh | Orientation/Hospital/Maze |
| **Test ladder** | validate-machine-test-ladder-v1.sh | Cadence runner alive |

---

## 6. Upgrade planning loop (future goals → safe changes)

### A — Baseline snapshot (before any change)

Capture **before photo** to `archive/attachments/YYYY-MM-DD/` or H2 registry row:

| Field | Path |
|-------|------|
| Queue head | `live-ongoing-prompts-next-10-v1.json` · broker status |
| Agentic health | `~/.sina/agentic-layer-pipeline-v2.json` |
| Critical bugs | `~/.sina/find-bugs/last-run.json` → `critical_count` |
| H2 pending | `~/.sina/h2-pending-registry-v1.json` → `pending_total` |
| Form open | `live_founder_decision_form_v1.py --json` |
| Ladder | `machine_test_ladder_run_v1.py --tier daily` receipt |

No baseline = no honest upgrade story.

### B — Win condition delta (W1 / W2 / W3)

From `ENFORCEMENT-6MO-MASTER-PLAN-v1.md`:

| Win | Upgrade must move… |
|-----|-------------------|
| **W1 Demo** | BLOCK / ALLOW / TAMPER visible on camera |
| **W2 Kernel** | Fewer bypass paths · receipt↔spine bind |
| **W3 Money** | TrustField / Noetfield shippable surface — **not** SourceA hub creep |

If an upgrade does not move W1–W3 or daily H1 truth → **defer** to H2 `next_phase` bucket.

### C — Contract first, code second (anti-wheel)

1. LOCKED law or sub-step (one doc · one topic)
2. Validator that **fails before** the feature exists
3. Machine script that **writes a receipt**
4. Hub surface — H1 **alarm line** OR H2 **table** — never both inline
5. Form PICK if cadence or founder-facing behavior changes

### D — Tier the new validator

| Tier | Cadence | Example |
|------|---------|---------|
| **P0 daily** | Session gate · super-fast · two-hub | Hub must never lie |
| **P1 weekly** | Governance full · Judge | Strategic machines |
| **P2 on ship** | Strict build · demo enforcement | Investor-facing |
| **P5 hatch** | Experimental | RAGAS CI · research |

Add to `validate-anti-staleness-bundle-v1.sh` only when stable — not first draft.

### E — Prove with same ladder (after ship)

1. Re-run **daily** tier — must stay green
2. Re-run **weekly** if Judge/Thread/registry touched
3. Append H2 `maintainer_ship` row until verified
4. Brain closeout cites **receipt paths** — not chat summary

---

## 7. H2 upgrade board (living — not chat)

Brain updates `~/.sina/h2-pending-registry-v1.json` each session:

| ID | Future goal | Win | Baseline receipt | New validator | Cadence | Form PICK? |
|----|-------------|-----|------------------|---------------|---------|------------|
| UP-01 | RAGAS CI vs Eval-1b | W2 | eval_packet_v1b_report | TBD hatch | Quarterly | No |
| UP-02 | Demo film W1 | W1 | demo-enforcement validators | validate-demo-enforcement | Weekly | Yes if hub button |
| UP-03 | Kernel single write path | W2 | sourcea_execute + gatekeeper | universe-invariants | Daily | No |
| UP-04 | Test ladder machine | H1 truth | machine-test-ladder-receipt | validate-machine-test-ladder | Daily | No |
| UP-05 | Agent pipeline v2 tiers | Agent health | hospital/maze receipts | validate-agent-three-pipelines | Daily smoke | No |

Multi-sentence founder decisions → **Form** → H2 bucket → scheduled build.

---

## 8. Who does what

| You (founder) | Agents / Maintainer |
|---------------|---------------------|
| Bookmark H1 daily · H2 weekly | Run `machine_test_ladder_run_v1.py` by cadence |
| Safety + light refresh | Dual heal · pipeline sync · broker |
| Form PICKs for cadence changes | Write receipts + attachments |
| Judge “W1/W2/W3?” | Add validators **before** features |
| Never legacy for daily truth | Never full rebuild on Refresh |
| Say **orientation** / **hospital** / **maze** when agent state needs it | Execute pipeline · post receipt |

---

## 9. Decision tree — “which test do I run?”

```text
What are you trying to learn?
│
├─ Can we work TODAY?
│    └─ daily ladder + H1 Safety
│
├─ Is factory honest THIS WEEK?
│    └─ weekly ladder + find_critical_bugs + H2 pending vs Form
│
├─ Is an agent lost or sick?
│    ├─ New arrival        → orientation
│    ├─ Drifting worker    → hospital
│    └─ critical_count>0  → maze (machine blocks hospital discharge)
│
├─ Planning a feature?
│    └─ baseline snapshot → W1/W2/W3 delta → validator first → H2 UP-* row
│
└─ Investor / strict audit?
     └─ monthly ladder + strict hub Action (ASF only)
```

---

## 10. One sentence to remember

**Run the tiered ladder logged receipts; read what moved; upgrade only where W1/W2/W3 or H1 truth gains a provable delta — contract and validator before code, schedule before whim.**

---

*End SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1*
