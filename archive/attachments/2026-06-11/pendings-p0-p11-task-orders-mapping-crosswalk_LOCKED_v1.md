# T3 crosswalk — WTM pendings P0–P11 ↔ task orders TO-*/NF-*

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no implementation** · archive only

## Scope

Semantic mapping between:

| SSOT A | Module | IDs |
|--------|--------|-----|
| **WTM pendings** | `scripts/strategic_synthesis_hub.py` `pendings()` | P0–P11 |
| **Task orders** | `~/.sina/task-orders/orders.jsonl` | TO-* · NF-* |

**Law:** These are **parallel surfaces** — no machine sync. This table is **maintainer reference only** until ASF orders a reconcile script or hub link table.

**Related:** `sa-0797` (orders ↔ hub todos) · `sa-0798` (judgments ↔ pendings) · `sa-0798-to-008-to-009-fleet-reconcile-check-note`

---

## Master mapping table (2026-06-11 disk)

| Pending | Pend title | Pend status | Best task-order match | Order status · judgment | Link type | Align? |
|---------|------------|-------------|----------------------|-------------------------|-----------|--------|
| **P0** | Eval-1b sustain — 5+ live tasks + CI | done | — (no TO row) | — | Indirect · eval spine | N/A |
| **P1** | ENFORCE bypass map LOCKED + hub | done | `TO-003` (GPT report-only) | open · missed | Policy overlap | **Partial** — P1 done · TO-003 still open |
| **P2** | L0-full editor telemetry | partial | **`TO-DRIFT`** | partial · partial | Drift / L0 telemetry | **OK** |
| **P3** | L0/L1 deepen | open | `TO-DRIFT` (secondary) | partial · partial | Strategic slice L0/L1 | **Partial** — P3 open · TO-DRIFT partial |
| **P4** | Dispatch policy + eval gate | done | — (no dedicated TO) | — | Machine gate only | N/A |
| **P5** | graph_executor + spine_bridge | done | — (build hook only) | — | CI / build chain | N/A |
| **P6** | L8 embeddings hybrid | done | `TO-ML` | deferred · different_goal | WTM D5+ deferred | **OK** (both deferred/done diff scope) |
| **P7** | L5/L6 semantic history | done | — | — | Roadmap done | N/A |
| **P8** | Learning loop + event bus | done | `TO-008` (weak) | needs_activation · needs_activation | Essays ≠ event bus | **DRIFT** |
| **P9** | Lane Scoreboard + vault attests | done | **`TO-009`** | needs_activation · needs_activation | Fleet scoreboard + vault | **DRIFT** |
| **P10** | TrustField outreach / pilot | in_progress | `TO-SKU` · portfolio lane | deferred · different_goal | Product / GTM | **Partial** — different_goal vs in_progress |
| **P11** | Wire RunReceipt / verify:wire | done | **`TO-WIRE`** | open · missed | Wire G3 / M8 | **DRIFT** |

### NF-* rows (no P0–P11 id; ecosystem / portfolio)

| Task order | Status | Semantic pendings / threads | Notes |
|------------|--------|----------------------------|-------|
| `NF-DRIFT` | lane_shipped | P2/P3 drift family | Noetfield lane shipped on Mac |
| `NF-UKE` | open · missed | — | UKE merge · not a P-row |
| `NF-PUSH` / `NF-CLOUD` | needs_activation | — | Noetfield activation |
| `NF-PRIVATE` | partial | — | Annex sync |
| `TO-MP` | open · missed | — | MergePack · ops card MP-SHIP |
| `TO-PDB` | partial | — | Personal DB Layer A |
| `TO-BOWL` | shipped | — | Bowl drift — aligned shipped |
| `TO-012` | open · missed | P8/P9 (nudge UI) | Essay nudges UI still missing |

---

## Required pairs (detail)

### P2 ↔ TO-DRIFT (aligned)

| Field | Pending P2 | Order TO-DRIFT |
|-------|------------|----------------|
| Title | L0-full editor telemetry | Governance drift enterprise runtime (8-layer) |
| Status | **partial** | **partial** |
| Judgment | — | **partial** |
| Owner | maintainer | hub / THREAD-MAINTAINER |
| Interpretation | Hub Phase 1 drift score high; full enterprise engine on roadmap | `shipped_evidence`: governance_drift_engine.py Phase 1 |

**Verdict:** Best **explicit align** in the set — both `partial`, same strategic-slice / drift thread.

---

### P9 ↔ TO-009 (drift — fleet green)

| Field | Pending P9 | Order TO-009 |
|-------|------------|----------------|
| Title | Lane Scoreboard + vault attests | Scoreboard fleet reports + ASF verify |
| Status | **done** | **needs_activation** |
| Live fleet | 8/8 reported · 8/8 verified · auto_pass | `scoreboard_verified: 8` |
| Interpretation | WTM pending flips `done` from machine gates | Order row frozen at seed; title still says "ASF verify" |

**Verdict:** **Should reconcile → shipped** per `sa-0798-to-008-to-009-fleet-reconcile-check-note`. P9 `done` and TO-009 `needs_activation` is **cross-SSOT drift**.

---

### P11 ↔ TO-WIRE (drift)

| Field | Pending P11 | Order TO-WIRE |
|-------|-------------|---------------|
| Title | Wire RunReceipt / verify:wire | Wire G3 Tailscale proof |
| Status | **done** | **open** · missed |
| Related hub | `WIRE-G3` ops card · `T-WIRE-1` ASF todo | Same THREAD-WIRE · no shared ID |
| Interpretation | P11 `done` when eval/spine gates green | TO-WIRE tracks **physical G3 proof** — may lag intentionally |

**Verdict:** **Semantic cousins** not strict duplicates. P11 `done` ≠ G3 logged. TO-WIRE **open** may be correct until founder/repo records G3 in `WIRE_LANE_PROGRESS.md`. Document as **intentional lag** unless wire proof exists in the repository.

---

## P8 ↔ TO-008 (weak pair — called out in sa-0798)

| Pending P8 | Order TO-008 |
|------------|--------------|
| Learning loop + event bus · **done** | Fleet essays governance drift · **needs_activation** |
| Different WTM workstream | Essay discourse for `governance-drift-detection` |

**Verdict:** **Do not hard-link** in reconcile script without ASF yes. Fleet essays (TO-008) should still flip **shipped** on fleet signals alone.

---

## Status alignment summary

| Alignment | Pairs |
|-----------|-------|
| **OK** | P2↔TO-DRIFT |
| **DRIFT (reconcile candidate)** | P9↔TO-009 · P8↔TO-008 (fleet) |
| **DRIFT (may be intentional)** | P11↔TO-WIRE |
| **Partial** | P1↔TO-003 · P3↔TO-DRIFT · P10↔TO-SKU |
| **No TO row** | P0 · P4 · P5 · P7 |

---

## Machine behavior (why table does not auto-apply)

```
strategic_synthesis_hub.pendings()
  → status from _machine_gates() / eval_1b on every hub build

task_orders_guardian.run_seed() / orders.jsonl
  → written once; update only via hub API or manual edit

No import edge between modules — mapping is human/maintainer only.
```

---

## OPEN (informational)

1. **OPEN-1:** Add §Pendings map to `TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` (law prose).
2. **OPEN-2:** Optional `pendings_task_order_map_v1.json` machine mirror — **ASF order only**.
3. **OPEN-3:** Reconcile TO-008/009 per fleet check note before trusting P9/P8 alignment.
4. **OPEN-4:** Clarify P11 vs TO-WIRE: separate acceptance criteria in WTM doc.
5. **OPEN-5:** `validate-pendings-task-orders-map-v1.sh` warn on P9 done + TO-009 not shipped.

---

## Verdict

**T3 complete** — P0–P11 ↔ TO/NF mapping documented; P2↔TO-DRIFT aligned; P9↔TO-009 and P11↔TO-WIRE drift characterized; no code shipped.
