# sa-0974 — PROGRAM_PROGRESS machine sync vs manual ASF edit incidents (CHECK)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**SA:** sa-0974 · phase-s9-research-models · T2  
**Duplicates:** sa-0924 · sa-0949 · sa-0999 (same title — canonical here)  
**Law:** `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` · `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` · INCIDENT-016 · INCIDENT-006

## Thesis

`PROGRAM_PROGRESS.json` is the **founder command-center projection** (P0 threads, parallel plans, locks, signals_auto) — but **factory honest progress** lives in REGISTRY + receipts (`Valid YES 652/1000`). Manual ASF edits (chat todos, hand-tweaked JSON, REGISTRY status) caused recurring **incidents** when they bypassed machine sync. Law: **machine rebuild wins** on build; ASF edits **locks/strategy only**, never verify authority.

## Two-speed progress model

| Clock | SSOT | Updated by | Measures |
|-------|------|------------|----------|
| **A — Strategic** | `PROGRAM_PROGRESS.json` | `update-program-progress.py` (+ ASF lock edits) | P0 id, parallel plans %, next_action, signals_auto |
| **B — Factory** | `REGISTRY.json` + `receipts/sa-*` | Broker closeout only | Valid YES count, dual_proof, backlog |

**Insight (sa-0967):** Clock A is founder north-star; Clock B is honest drain. They must not be conflated — chat citing PROGRAM_PROGRESS % does not prove sa done.

## Machine sync path

```text
build-sina-command-panel.py (strict/full)
  → _run_update_program_progress
  → update-program-progress.py (SINA_SKIP_NESTED_BOWL=1)
  → PROGRAM_PROGRESS.json
       updated_by: "update-program-progress.py"
       signals_auto.synced_at: ISO timestamp
  → build-sina-daily-bowl.py (reads progress — sequential dep, sa-0962)
  → hub command-data projection (founder.p0, parallel_plans)
```

**Validator:** `validate-program-progress-build-sync-v1.sh` — asserts build invokes progress script + `synced_at` present.

## Manual ASF edit incident class

| Incident | Manual edit / chat signal | Disk truth drift | Fix class |
|----------|---------------------------|------------------|-----------|
| **INCIDENT-006** | YAML/chat claims done | 607 REGISTRY without receipts | Receipt law · honest gate |
| **INCIDENT-016** | Cursor plan todos "4/4 completed" | Drain frozen · inbox cleared | PLAN_REVOKED · cancel all todos |
| **INCIDENT-007** | Broker STALE | Worker PASS without broker cycles | `goal1_lane_broker` repair |
| **INCIDENT-030** | YAML-only closeout | Fake green without receipt | `worker_verify_fast` auto-revert |
| **Manual REGISTRY** | Chat `status: done` | No `receipts/sa-*` | `worker_verify_closeout_v1.sh` only path |

**Pattern:** Manual ASF/session layer **reactivates ghost work**; machine sync layer **overwrites projection** on build but **cannot** fake factory receipts.

## What ASF may edit vs forbidden

| Action | Allowed | Forbidden |
|--------|---------|-----------|
| Update `locks.*` / parallel plan status when blocker clears | ASF hub tap or bounded order | — |
| Set REGISTRY `done` by hand | — | **Always** — closeout only |
| Mark verify PASS in chat | — | Machine validators + broker |
| Edit `progress_pct` without rebuild | Short-lived only — next build may overwrite | Treat as SSOT for factory |
| Cancel pending work | STOP + freeze + `PLAN_REVOKED` | Partial todo cancel (INCIDENT-016) |

## Live snapshot (2026-06-14)

| Field | Value |
|-------|-------|
| `updated_by` | `update-program-progress.py` |
| `updated_at` | `2026-06-14T00:58:27Z` |
| `founder_p0_id` | `STRATEGIC-SLICE` |
| `signals_auto` | present (synced_at in file) |
| Factory Valid YES | **652** (REGISTRY+receipt — separate SSOT) |
| `validate-program-progress-build-sync-v1` | PASS path when run after build |

## Industry comparators

| Pattern | Norm | SourceA delta |
|---------|------|---------------|
| Dashboard % complete | Manual PM updates | `update-program-progress.py` from repo signals |
| Sprint board drag-drop | Human moves cards | ASF todos (`T-*`) separate from task orders (`TO-*`) |
| CI truth | Pipeline badge | Receipt + broker PASS = done |
| Chat memory progress | Agent claims | **Chat memory is not SSOT** (000-workspace-lock) |

## ACT backlog

| Item | Owner |
|------|-------|
| `validate-program-progress-factory-divergence-v1.sh` — alert when PROGRAM_PROGRESS % disagrees with Valid YES trend | Worker ACT |
| Document INCIDENT-016 playbook in progress law companion | Maintainer |

## WTM thread

- **Spine:** Founder command center · factory honesty · STRATEGIC-SLICE P0  
- **Related:** sa-0960 no-ASF-verify · sa-0962 progress/bowl seq · sa-0797 task-orders vs todos  
- **Deferred:** Auto-reconcile PROGRAM_PROGRESS % from REGISTRY (research only)

## CHECK verdict

PROGRAM_PROGRESS **machine sync is wired and validated**; manual ASF edit incidents are a **documented failure class** — strategic projection vs factory receipts must stay split, with closeout-only done authority.
