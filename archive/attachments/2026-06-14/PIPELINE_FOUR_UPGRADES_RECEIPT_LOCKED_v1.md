# Pipeline four upgrades — Maintainer receipt (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Role:** Maintainer  
**Scope:** `scripts/` · `~/.sina/` · `.cursor/rules/` only  
**Forbidden respected:** no `agent-control-panel/` · no `sina-command*.py` · no hub rebuild · no Maze run

---

## Summary

Queue SSOT unified · Hospital H7b fixed · maze quarantine auto-clear · hospital trigger-gated.

---

## UPGRADE 1 — Queue SSOT single writer (P0) ✅

| Item | Ship |
|------|------|
| Canonical head | `queue_ssot_unify_v1.queue_head()` from `healthy-queue-state-v1.json` + `healthy-queue-30-active.json` |
| Single sync | `monitor_live_sync_v1.sync_disk` → `unify_queue_ssot(write_brain=False)` |
| Brain validation | `unify_queue_ssot` writes `brain-goal1-validation-v1.json` via `validate_goal1()` |
| Stale last_completed | `brain_validate_goal1_v1.py` flags `last_completed_stale` when ahead of queue head without broker closeout |
| Brain poll | `goal1_lane_broker.brain_poll` exposes `queue_ssot_head` + `queue_head_match` |
| Validator | `validate-queue-ssot-unified-v1.sh` — factory-now · run-inbox · monitor-live.here_sa · truth_match |

**Verify:**
```
python3 scripts/run_inbox_disk_truth_v1.py --sync --write → truth_match: true
bash scripts/validate-queue-ssot-unified-v1.sh → PASS
python3 scripts/goal1_lane_broker.py brain-poll --json → queue_head_match: true
```

---

## UPGRADE 2 — Hospital H7b JSON parse (P1) ✅

| Item | Ship |
|------|------|
| Parser | `_parse_json_tail()` — last balanced JSON before trailing `OK:` lines |
| Accept | `_fcb_accept_ok()` — critical=0 · disk last-run · ok:true |
| H7b | Excluded from `core_ok` discharge authority (H8 owns critical) |

**Verify:**
```
python3 scripts/agent_hospital_pipeline_v1.py --role worker --json
→ ok:true · H7b ok:true · critical_count:0 · escalate_maze:false
```

---

## UPGRADE 3 — Maze quarantine auto-clear (P1) ✅

| Item | Ship |
|------|------|
| Helper | `agent_three_pipelines_lib_v1.clear_maze_quarantine_if_critical_zero()` |
| Hospital H8 | Writes `active:false` · `reason:critical_zero` (not repeat_incident) |
| Maze exit | Clears on incomplete exit when critical=0; passport path unchanged |

**Verify:**
```
After hospital with critical=0 and prior quarantine active:true:
→ {"active": false, "reason": "critical_zero", ...}
```

---

## UPGRADE 4 — Hospital trigger gate (P2) ✅

| Item | Ship |
|------|------|
| Rule | `.cursor/rules/002-hospital-trigger-only.mdc` (alwaysApply) |
| Law | `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` §Session start |
| Duty card | D23 · session_start_order excludes pipelines |
| Session gate | `pipelines_policy` on receipt |
| Validator | `validate-founder-hospital-gate-v1.sh` in anti-staleness bundle |

**Verify:**
```
bash scripts/validate-founder-hospital-gate-v1.sh → PASS
```

---

## Verify bundle (2026-06-14)

| Check | Result |
|-------|--------|
| `SINA_FCB_FAST=1 find_critical_bugs.py` | critical:0 |
| `agent_hospital_pipeline_v1.py --role brain` | ok:true |
| `agent_hospital_pipeline_v1.py --role worker` | ok:true |
| `validate-queue-ssot-unified-v1.sh` | PASS |
| `run-inbox truth_match` + `queue.sa_id` | true · sa-0519 (at verify time) |

---

## Founder line

**Queue SSOT unified · Hospital H7b fixed · maze quarantine auto-clear · hospital trigger-gated.**

Tap nothing — disk is aligned. Say **RUN INBOX** for Worker. Say **hospital** only when you want the clinic pipeline.

---

*End PIPELINE_FOUR_UPGRADES_RECEIPT_LOCKED_v1*
