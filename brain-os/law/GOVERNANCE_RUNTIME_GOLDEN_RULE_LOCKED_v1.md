# Governance Runtime — Golden Rule (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-GOV-GOLDEN-RULE  
**Authority:** ASF · north star for **Controlled Agentic Runtime**  
**Parent:** `SOURCEA_GOVERNANCE_EVENT_SPINE_SCHEMA_LOCKED_v1.md` · `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md`  
**Row ID:** `GOV_GOLDEN_RULE` (pointer — prose lives here; spine row `GOV_EVENT_SPINE`)

---

## Golden rule (one paragraph — LOCK)

> **State is canonical. Events are history. Graph is intelligence. Projections are disposable. Validators are authority. Router is governor. Workers are replaceable.**

| Phrase | In the repository today |
|--------|----------------|
| **State is canonical** | `brain-os/` law · authority index rows · `PROGRAM_PROGRESS` · inbox truth |
| **Events are history** | `governance-event-spine-v1.jsonl` · broker events · governance events |
| **Graph is intelligence** | `governance-reference-graph-v1.json` · impact scan |
| **Projections are disposable** | `command-data.json` · catalog JSON · monitor mirror — materialize only |
| **Validators are authority** | `validate-*` bundle — exit 0 or FAIL |
| **Router is governor** | `goal1_lane_broker` · `governance_propagation_cascade` |
| **Workers are replaceable** | Worker lane · one sa/turn · crash → replay (G4) |

---

## Closed-loop control (Track 2 — runtime kernel)

```text
Intent (ASF)
  → Pick (FIVE-STEP / Canvas)
  → Event (spine append)
  → Ledger (jsonl)
  → Router (broker + cascade)
  → Reference graph
  → Impact analysis
  → Execution queue (inbox / broker)
  → Worker(s)
  → Validator (proof)
  → Projection materializer (align / build panel / catalog)
  → Monitor (feedback)
  → Replay / recovery (G4 — `governance_replay_worker_v1.py`)
  → Stable state (receipt + PASS)
```

**Not an event bus alone** — feedback closes the loop when validator + projection regen complete the cycle.

**G3:** `governance_projection_g3_v1.py` — `LAW_TOUCHED` → queue → selective materialize · hub write gate on `write_panel_outputs`.

**G7:** `governance_self_heal_daemon_v1.py` — unified scan/heal · delegates S10 + conscious-recovery + G3/G4.

---

## Context routers (small-model pattern)

```text
Global router   — governance entry · role · domain (governance|technical|ui|research|portfolio)
Domain router   — agent_truth_bundle + one skill + one authority row
Worker          — working set only (inbox sa + law slice) — never full repo
```

Machine: `agent_truth_bundle_v1.py` · `MANDATORY_READ_BY_ROLE` · `agent_domain_matrix` in catalog JSON.

---

## P1 — Canonical / Runtime projection split

```text
Materializer → command-data-canonical.json  (deterministic — validator hashes this)
            → command-data-runtime.json     (ephemeral — monitor only)
            → command-data.json             (merged — hub UI)
```

Runtime never enters fingerprint surface — **not** via growing exclusion lists.

**Canonical allowlist:** `CANONICAL_ROOT_KEYS` in `hub_projection_canonical_v1.py`  
**Runtime bucket:** broker poll · agent_loop · fleet · queues · `goal1_auto_run`  
**Projection meta (closed):** `built_at` · `updated_at` · `generated_at` · `last_evaluated_at` — stripped from canonical subtrees only

## Projection acceptance test

```bash
cd ~/Desktop/SourceA && bash scripts/validate-hub-projection-disposable-v1.sh
```

Delete hub projections → materialize → **same canonical view**.

---

*End golden rule*
