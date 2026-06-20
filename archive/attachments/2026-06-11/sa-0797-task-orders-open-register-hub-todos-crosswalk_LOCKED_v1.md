# sa-0797 ACT — TASK_ORDERS_OPEN_REGISTER sync with hub todos crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Document how **task orders** (`TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` → `~/.sina/task-orders/orders.jsonl` → hub `order_guardian`) relate to **founder hub todos** (`asf_todos` / `open_todos_all` from daily bowl + `PROGRAM_PROGRESS.json`) — what syncs live, what drifts, and what machine proof exists.

## Authority order

| Layer | Source | Role |
|-------|--------|------|
| Register law | `TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` | Human LOCKED table · last consolidated **2026-06-06** |
| Order Guardian law | `ORDER_GUARDIAN_AGENT_LOCKED_v1.md` | Agent + advisory contract |
| Machine module | `scripts/task_orders_guardian.py` | Seed · `orders_payload()` · hub signals · advisory |
| Hub embed | `scripts/sina_command_lib.py` | `order_guardian = orders_payload(out)` on panel build |
| Founder todos | `scripts/build-sina-daily-bowl.py` · `PROGRAM_PROGRESS.json` | `asf_todos` / `open_todos_all` — **separate ID namespace** |
| Ops cards | `sina_command_lib` `ops_cards` | `MP-SHIP` · `WIRE-G3` · `B-001` — semantic overlap only |
| Governance entry | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | Points to register for open/partial/deferred orders |
| Prior closeout | **sa-0772** (T2) | Same task title; receipt `receipts/sa-0772-receipt.json` — no 2026-06-11 crosswalk |

## Three parallel todo surfaces (canonical matrix)

| Surface | ID scheme | Source | Hub field / tab |
|---------|-----------|--------|-----------------|
| **Task orders** | `TO-*` · `NF-*` | `orders.jsonl` + register law | `order_guardian` · Order Guardian tab |
| **ASF todos** | `T-*` (e.g. `T-WIRE-1`) | Bowl + program progress | `command_center.founder.asf_todos` |
| **Ops cards** | `MP-SHIP` · `WIRE-G3` · `B-001` | Missed-actions + blockers | `command_center.founder.ops_cards` |

**Law sentence:** Task orders are the **maintainer register** + smart advisor; ASF todos are **today's founder picks** from program progress; ops cards are **blocker highlights**. They are **not** one merged SSOT — overlap is semantic, not machine-linked.

## Semantic overlap (manual map)

| Task order | Related hub todo / ops | Link type |
|------------|------------------------|-----------|
| `TO-WIRE` | `T-WIRE-1` · `WIRE-G3` ops card | Same thread · **no shared ID** |
| `TO-MP` | `MP-SHIP` ops card | MergePack ship · **no shared ID** |
| `NF-UKE` | `T-IC-1` (Noetfield spec review) | Portfolio lane · **no shared ID** |
| `TO-008` | Fleet essay discourse | Advisory uses `essay_gap` signal |
| `TO-009` | Agent scoreboard | Advisory uses `scoreboard_verified` signal |
| `TO-BOWL` | Daily bowl drift | Disk **shipped** · register still **open** (prose drift) |

## Machine chain (Order Guardian)

```
build-sina-command-panel.py / hub_self_refresh
  → sina_command_lib.build_command_payload()
       → task_orders_guardian.orders_payload(hub)
            → seed_if_empty()          # ~/.sina/task-orders/orders.jsonl
            → compute_advisory(rows, hub)  # live essay_gap · scoreboard · drift_score
  → command-data.json order_guardian { ok, total, actionable_count, advisory, by_status }
```

**API:** `POST /api/order-guardian` · hub Order Guardian tab (`app.js` register_doc hero).

## Live disk proof (ACT)

| Check | Result |
|-------|--------|
| Register table IDs | **22** unique (`TO-*` / `NF-*` / `TO-DRIFT` etc.) |
| `orders.jsonl` rows | **24** (all 22 register IDs present + `TO-OG-001` + `NF-DRIFT`) |
| `order_guardian.ok` | **true** |
| `total` / `actionable_count` | **24** / **17** |
| Fleet live (hub) | **8/8** reported · **8/8** verified · nudges **0** |
| Advisory signals | `essay_gap: 0` · `scoreboard_verified: 8` · `drift_score: 100` |
| `asf_todos` count | **2** — `T-WIRE-1`, `T-IC-1` |
| `do_now` (advisory) | `TO-012` Essay auto-nudges in hub |

## Staleness gaps (register + disk status)

| ID | Register prose (2026-06-06) | Disk `orders.jsonl` status | Live hub truth |
|----|----------------------------|----------------------------|----------------|
| `TO-008` | "2/8 posted" | `needs_activation` | Fleet **8/8** essays · `essay_gap: 0` |
| `TO-009` | "1 report, 0 verified" | `needs_activation` | Scoreboard **8/8** `auto_pass` |
| `TO-BOWL` | `open` | `shipped` | Bowl drift fix shipped (sa prior) |
| `TO-012` | `open` | `open` | Nudge UI still missing — **correctly open** |

**Advisory side-effect:** `TO-008` still scores in top-5 because `needs_activation` status weight applies even when `essay_gap: 0` — status field not auto-reconciled from fleet validators.

## What syncs automatically vs not

| Sync path | Automatic? | Proof |
|-----------|------------|-------|
| Register law → `SEED_ROWS` → `orders.jsonl` | **Once** (seed_if_empty) | 22/22 IDs on disk |
| Hub build → `order_guardian` payload | **Every build/refresh** | `command-data.json` embed |
| Hub signals → advisory scores | **Every `orders_payload()`** | `essay_gap` · `scoreboard_verified` live |
| Fleet green → `TO-008`/`TO-009` status flip | **No** | Status frozen at seed |
| `asf_todos` ↔ task-order IDs | **No** | Parallel namespaces |
| LOCKED register prose ↔ live fleet | **No** | Maintainer edit only |
| Dedicated sync validator | **No** | OPEN-4 |

## OPEN (informational — maintainer / ASF)

1. **OPEN-1:** Refresh `TASK_ORDERS_OPEN_REGISTER_LOCKED_v1.md` §A rows for `TO-008`, `TO-009`, `TO-BOWL` (law prose only).
2. **OPEN-2:** Reconcile `orders.jsonl` `TO-008`/`TO-009` → `shipped` or `open` when fleet signals green (script or hub action).
3. **OPEN-3:** Optional ID bridge table `T-WIRE-1` ↔ `TO-WIRE` in register or bowl — not required for factory green.
4. **OPEN-4:** Future validator `validate-task-orders-register-sync-v1.sh` — register IDs ⊆ disk · stale fleet rows warn.
5. **OPEN-5:** Duplicate 1000-pack prompts (sa-0722, sa-0747, sa-0772, sa-0797) — REGISTRY backlog; this crosswalk is queue proof.

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0
- `validate-spine-bridge-founder-v1.sh` — PASS
- `validate-dispatch-policy-v1.sh` — PASS · gate_ok=True
- `validate-governance-event-spine-v1.sh` — PASS
- `find_critical_bugs.py` — critical **0**

## Verdict

**ACT complete** — Order Guardian wired; register ⊆ disk; hub advisory uses live fleet signals; **hub todos remain parallel** with documented drift on stale register/status rows. T3 crosswalk only — no code change required for factory green.
