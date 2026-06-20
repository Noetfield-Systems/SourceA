# sa-0798 ACT — Order guardian judgments vs pendings statuses crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Cross-check **Order Guardian** `judgment` + `status` fields logged against **WTM strategic synthesis pendings** (P0–P11) — internal consistency, cross-SSOT drift, and hub UI exposure.

## Authority order

| Layer | Source | Role |
|-------|--------|------|
| Order Guardian | `scripts/task_orders_guardian.py` | `STATUSES` · `JUDGMENTS` · `orders_payload()` · advisory signals |
| Pendings | `scripts/strategic_synthesis_hub.py` `pendings()` | P0–P11 · machine-gate driven (`eval_1b_gate_ok`, etc.) |
| Hub UI | `agent-control-panel/assets/app.js` | `orderGuardianRow()` · Ship/Defer set status+judgment |
| Related crosswalk | `sa-0797` | Task orders ↔ hub todos (parallel SSOTs) |
| Prior closeout | **sa-0773** (T2) | Same task title; receipt `receipts/sa-0773-receipt.json` |

## Field semantics (Order Guardian)

| Field | Meaning | Example values |
|-------|---------|----------------|
| **status** | Workflow bucket (UI label via `OG_STATUS_LABELS`) | `open` · `partial` · `needs_activation` · `shipped` · `deferred` |
| **judgment** | Why stopped / action class (advisory weight) | `missed` · `needs_activation` · `partial` · `shipped` · `different_goal` |

**Seed contract:** `open`→`missed` · `needs_activation`→`needs_activation` · `partial`→`partial` · `shipped`→`shipped` · `deferred`→`different_goal` · `lane_shipped`→`lane_shipped` · `different_goal`→`different_goal`

## Internal disk proof (judgment × status)

| status | judgment | count |
|--------|----------|------:|
| open | missed | 10 |
| needs_activation | needs_activation | 4 |
| partial | partial | 3 |
| deferred | different_goal | 3 |
| shipped | shipped | 2 |
| lane_shipped | lane_shipped | 1 |
| different_goal | different_goal | 1 |

**Total:** 24 rows · **0** seed-contract mismatches logged.

## Pendings vs orders (cross-SSOT map)

Pendings and task orders are **separate SSOTs** — no machine sync. Curated semantic pairs:

| Pending | Pend status | Order ID | Order status · judgment | Align? |
|---------|-------------|----------|-------------------------|--------|
| P0 | done (eval_1b) | — | — | N/A (no TO row) |
| P2 | partial | `TO-DRIFT` | partial · partial | **OK** |
| P8 | done | `TO-008` | needs_activation · needs_activation | **DRIFT** |
| P9 | done | `TO-009` | needs_activation · needs_activation | **DRIFT** |
| P10 | in_progress | `TO-SKU` | deferred · different_goal | Different scope |
| P11 | done | `TO-WIRE` | open · missed | **DRIFT** |

Live fleet at ACT (2026-06-11T22:11Z): `nudge_count: 0` · `essay_count: 9` · `scoreboard_verified: 8/8` · `eval_1b_gate_ok: true`

**Advisory bug (OPEN-6):** `orders_payload()` without hub JSON reports `essay_gap: 8` · `scoreboard_verified: 0` — stale/misleading vs live fleet above. Maintainer: wire `_hub_signals()` from built hub snapshot on align.

## Why drift persists (machine explanation)

1. **Pendings** flip `done` from `_machine_gates()` / `eval_1b_gate_ok` on every hub build.
2. **Task orders** seed once into `orders.jsonl` — **no auto-reconcile** when fleet goes 8/8.
3. **Advisory** uses live signals for *scoring* but `needs_activation` status still adds +50 weight → `TO-008` can rank top-5 despite `essay_gap: 0`.
4. **P8** title ("Learning loop") ≠ **TO-008** (fleet essays) — semantic overlap is indirect; drift is expected without explicit link table.

## Hub UI gap

| UI element | Shows judgment? | Notes |
|------------|-----------------|-------|
| `orderGuardianRow()` | **No** — status only | `OG_STATUS_LABELS[st]` |
| Shipped button | Sets both | `status: shipped` + `judgment: shipped` |
| Defer button | Sets both | `status: deferred` + `judgment: different_goal` |
| WTM pendings panel | Status only | `renderStrategicSynthesisPanel` · no order ID |

## UI → disk contract (founder actions)

```
Shipped click → POST /api/order-guardian update { status: shipped, judgment: shipped }
Defer click   → POST /api/order-guardian update { status: deferred, judgment: different_goal, defer_reason }
```

## OPEN (informational — maintainer)

1. **OPEN-1:** Reconcile `TO-008`/`TO-009` to `shipped` when `essay_gap: 0` and `scoreboard_verified: 8` (disk or hub action).
2. **OPEN-2:** Reconcile `TO-WIRE` when P11 `done` and wire verification built in — or document intentional lag.
3. **OPEN-3:** Show `judgment` in Order Guardian row (display-only).
4. **OPEN-4:** Validator `validate-order-guardian-judgment-sync-v1.sh` — seed-contract + optional fleet signal reconcile warn.
5. **OPEN-5:** Link table in `TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` for P8/P9/P11 ↔ TO rows.

## Validators (ACT — Q2 · 2026-06-11T22:11Z)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0 verify_gap 0
- `validate-spine-bridge-founder-v1.sh` — PASS
- `validate-dispatch-policy-v1.sh` — PASS · gate_ok=True
- `validate-governance-event-spine-v1.sh` — PASS
- `find_critical_bugs.py` — critical **3** (global: anti-staleness · authority-index INCIDENT-027 orphan · eval P0 — blocks VERIFY not this ACT doc)

## Verdict

**ACT complete (Q2)** — crosswalk refreshed logged; judgment/status internally consistent (0 mismatches); pendings↔orders cross-SSOT drift unchanged (P8/P9/P11 vs TO-008/009/WIRE); fleet 8/8 green vs stale `orders.jsonl`; **no hub code diff** per T3 spike + FREEZE/repair-only.
