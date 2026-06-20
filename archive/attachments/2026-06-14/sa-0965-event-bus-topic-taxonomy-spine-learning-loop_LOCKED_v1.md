# sa-0965 — Event bus topic taxonomy for spine learning loop

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules · No bus_v1 code edits**

## One-line verdict

> **Spine learning loop closes on `spine.bridge` (founder act) + `feedback.loop` (machine learn).** Bus is minimal append-only JSONL — taxonomy is **research registry** until ASF orders schema v2 + consumer wiring.

---

## Fabric today (disk truth)

| Field | Value |
|-------|--------|
| **Module** | `scripts/runtime/event_bus/bus_v1.py` |
| **Log** | `~/.sina/events_v1.jsonl` |
| **API** | `GET/POST /api/event-bus-v1` |
| **Schema** | `event-bus-v1` row: `at` · `topic` · `source` · `payload` |
| **Hub panel** | `event_bus` in `build_payload` · tail last 12 rows |

**Live topics (2026-06-14 tail):** `spine.bridge` · `feedback.loop` · `validate.event_bus`

---

## Spine learning loop (PRIORITY §Spine)

```text
founder Action → spine.bridge event → execution_spine progress_sync → feedback.loop signals → ranking/state
```

| Stage | Topic | Publisher | Consumer (declared) | Authority |
|-------|-------|-----------|-------------------|-----------|
| **Act** | `spine.bridge` | `founder_action` (`sina_command_lib`) | hub tail · PRIORITY proof | **Founder tap only** (sa-0409) |
| **Learn** | `feedback.loop` | `loop_engine.py` | `feedback_loop` module | Machine — no ASF verify |
| **Probe** | `validate.event_bus` | `validate-event-bus-v1.sh` | validator CI | Machine |
| **Sync** | *(no topic yet)* | `progress_sync` implied | execution_spine | Disk validators |

**Loop closure law:** SOURCEA-PRIORITY — `spine.bridge` · founder_action receipts · `progress_sync`. Not all stages emit bus events today.

---

## Proposed topic taxonomy (research — not enforced)

### Tier T0 — Spine (founder-gated)

| Topic | Payload keys | Emit rule |
|-------|--------------|-----------|
| `spine.bridge` | `action_id`, `ok` | Founder Action success only — **never agent-fabricated** |
| `spine.dispatch` | `policy_class`, `eval_1b_gate_ok` | Deferred — dispatch policy amend |
| `spine.gate` | `gate_id`, `mode` shadow/enforce | Deferred — ENFORCE flip |

### Tier T1 — Learning (machine)

| Topic | Payload keys | Emit rule |
|-------|--------------|-----------|
| `feedback.loop` | `signals_count`, `patterns_count` | After `loop_engine` run |
| `feedback.ranking` | `top_signal`, `by_signal_type` | Sub-event of loop — **not separate today** |
| `governance.drift` | `drift_score`, `warn_count` | Align `governance_drift` consumer name |

### Tier T2 — Factory receipts

| Topic | Payload keys | Emit rule |
|-------|--------------|-----------|
| `factory.worker_verify` | `sa_id`, `round_type` | Deferred — broker receipt mirror |
| `gate.receipt` | `gate_id`, `checksum` | Align `gate_receipts` consumer |

### Tier T3 — Validator probes

| Topic | Payload keys | Emit rule |
|-------|--------------|-----------|
| `validate.*` | `probe: true` | CI only · e.g. `validate.event_bus` |

**Naming rule (proposed):** `{domain}.{verb}` dot-separated · no free-form chat topics.

---

## Consumer map (declared vs wired)

`event_bus_payload()` lists consumers: `feedback_loop` · `governance_drift` · `gate_receipts`.

| Consumer | Reads topic(s) today? | Gap |
|----------|----------------------|-----|
| `feedback_loop` | `feedback.loop` (publisher self) | No subscribe API — tail by topic only |
| `governance_drift` | — | **Not publishing** `governance.drift` |
| `gate_receipts` | — | **Not publishing** `gate.receipt` |
| Hub UI | all recent | Display only — not learning |

**Implement defer:** formal `subscribe(topic, handler)` — out of scope for research sa.

---

## Learning loop honesty rules

| Rule | Law |
|------|-----|
| No fake spine events | sa-0409 · founder Action required |
| Machine learn ≠ ASF verify | `feedback.loop` is signal only |
| Tail ≠ SSOT | `events_v1.jsonl` is audit trail; decisions live in feedback state files |
| Critic paste | Compare loop-closure claims to tail — EXTERNAL_CRITIC only |

---

## Duplicate sa titles

Same task at **sa-0915**, **sa-0940**, **sa-0990**, **sa-0965**. Canonical research for sa-0965 VERIFY closeout.

---

## Verdict

**Three live topics prove the bus works; taxonomy is the debt.** Spine learning loop = **T0 `spine.bridge` + T1 `feedback.loop`** — extend with T2 receipts when ASF orders consumer wiring. Research doc only — no `bus_v1.py` amend in this sa.

**One-line:** Act on `spine.bridge`, learn on `feedback.loop` — formal taxonomy deferred, loop partially closed logged.
