# CHECK note — TO-008 / TO-009 vs live fleet signals (2026-06-11)

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · CHECK only · **no code diff** · no `orders.jsonl` write (await ASF reconcile order)

## Question

Should `TO-008` and `TO-009` in `~/.sina/task-orders/orders.jsonl` flip from `needs_activation` → **`shipped`** given live fleet signals?

## Verdict

| Order | Flip to shipped? | Confidence |
|-------|------------------|------------|
| **TO-008** | **YES** | High |
| **TO-009** | **YES** | High |

## Disk state (orders.jsonl)

| ID | status | judgment | Title (stale fragment) |
|----|--------|----------|------------------------|
| TO-008 | `needs_activation` | `needs_activation` | Fleet essays — governance drift **(6/8 remaining)** |
| TO-009 | `needs_activation` | `needs_activation` | Scoreboard fleet reports + **ASF verify** |

## Live fleet proof (2026-06-11T21:50Z)

| Signal | Value | Source |
|--------|-------|--------|
| `essay_gap` | **0** | `order_guardian.advisory.signals` |
| `essay_total` | 8 | same |
| Essays logged | **9** rows · **8/8** agents | `~/.sina/essay-discourse/essays.jsonl` |
| Active subject | `governance-drift-detection` | `assignments.json` |
| `nudge_count` | **0** | hub `essay_discourse` |
| `scoreboard_reports` | **8** | advisory signals |
| `scoreboard_verified` | **8** | advisory signals |
| `reported_count` | **8** | `agent_scoreboard` |
| `verified_count` | **8** | `agent_scoreboard` |
| `auto_pass_count` | **8** | `agent_scoreboard` |
| `fleet_verify_gap` | **[]** | `agent_scoreboard` |
| `fleet_report_gap` | **[]** | `agent_scoreboard` |
| `validate-governance-fleet-v1` | **PASS** · nudges 0 | disk validator |

## Per-order rationale

### TO-008 — fleet essays
- **Activation criterion:** all agents post essay for active subject (`governance-drift-detection`).
- **Machine truth:** 8/8 agents · `essay_gap: 0` · `nudge_count: 0` · fleet validator PASS.
- **Disk title** still says "6/8 remaining" — **seed-era stale**, not live.
- **Recommended:** `status: shipped` · `judgment: shipped` · `shipped_evidence: fleet 8/8 essays · nudge_count 0 · sa-0791/sa-0794 proof`

### TO-009 — scoreboard fleet + verify
- **Activation criterion:** all 8 agents report + compliance green.
- **Machine truth:** 8/8 reported · 8/8 verified · `auto_pass` (not founder click-verify per sa-0795).
- **Disk title** still says "ASF verify" — **law drift**; machine verify is `auto_pass` / `verified_by: auto`.
- **Recommended:** `status: shipped` · `judgment: shipped` · `shipped_evidence: fleet 8/8 auto_pass · verify_gap [] · sa-0795 crosswalk`

## Stale layers (do not block shipped flip)

| Layer | TO-008 prose | TO-009 prose |
|-------|--------------|--------------|
| `TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` | "2/8 posted" | "1 report, 0 verified" |
| `orders.jsonl` title field | "6/8 remaining" | "ASF verify" |
| WTM pending P8/P9 | `done` | `done` |

Register + order titles need **maintainer law edit** separately; fleet signals already green.

## Reconcile paths (no action taken)

| Path | Owner | Mechanism |
|------|-------|-----------|
| **A — Hub one-tap** | ASF | Order Guardian tab → **Shipped** on TO-008 + TO-009 |
| **B — API** | Maintainer | `POST /api/order-guardian` `action: update` per row |
| **C — Script** | Maintainer on ASF order | `reconcile_task_orders_fleet_v1.py` (not present locally — **needs ASF yes**) |
| **D — Auto on build** | Maintainer backlog | `orders_payload()` reconcile hook when signals green (OPEN from sa-0798) |

## Law alignment

- Q-RT-LIVE YES: hub repair-only — **no reconcile script shipped in this CHECK**.
- Worker: **document only** per ASF request.
- Flipping status is **consistent** with fleet validators and sa-0795 (machine verify, not ASF verify).

## Next step

ASF or Maintainer executes path **A** or **B** when ready — then refresh advisory (TO-008 should drop from top-5 scoring).
