# AUTO-RUN fully automatic (LOCKED v1)

**Saved:** 2026-06-10T09:43:37Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Superseded wiring:** 2026-06-09 · **Authority:** ASF · **sa:** sa-0730  
**Superseded priority (2026-06-10):** `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` — Cursor AUTO-RUN is **not a goal**; flag stays ON; legacy wiring retained for rollback only.

## Rule (Choice 1+ — current)

Founder taps **▶ START AUTO RUN** once on **Today** (or Goal 1 auto-run). Hub runs up to **30 turns** via orchestrator + headless agent — **no paste**, **no OpenRouter** on this path.

| Control | Action id |
|---------|-----------|
| Start | `founder-goal1-autorun-start` |
| Stop | `founder-goal1-autorun-stop` |

Legacy batch buttons (`founder-start-worker-batch-5/10`, `founder-execute-turn`, `founder-execute-loop-3`) are **hidden** on primary surfaces — not removed from disk for rollback.

## Components (Choice 1+)

| Piece | Path |
|-------|------|
| Unified entry | `scripts/goal1_unified_autorun_v1.py` |
| Deliver + spawn | `scripts/goal1_auto_run_deliver_v1.py` → `goal1_auto_run_v1.py` |
| Worker turn | `scripts/start_goal1_worker_turn_v1.py` (`agent --resume` + worker marker) |
| Orchestrator | `scripts/healthy-drain-orchestrator-v1.py` `watch(max_turns=30)` |
| Hub APIs | `POST /api/goal1-autorun-start` · `POST /api/goal1-autorun-stop` |
| Status poll | `GET /api/goal1-auto-run-status` (every ~4s on Today / Goal 1) |
| Validator | `scripts/validate-goal1-unified-autorun-v1.sh` |

## Kill switches (split)

| Flag | Blocks |
|------|--------|
| `~/.sina/auto-run-disabled-v1.flag` | Legacy `auto_run_worker_batch_v1.py`, launchd batch, clipboard inject |
| `~/.sina/goal1-orchestrator-autorun-v1.json` | **Set on START · cleared on STOP** — enables Choice 1+ only; does **not** re-enable legacy batch |

Unified START must **not** route through `autorun_dispatcher_v1.py` or `goal1_worker_batch_loop_v1.py`.

## Legacy batch (frozen — not primary)

| Piece | Path |
|-------|------|
| Hub-start script | `scripts/auto_start_worker_batch_on_hub_v1.sh` |
| Autorun engine | `scripts/auto_run_worker_batch_v1.py` |
| Batch loop | `scripts/goal1_worker_batch_loop_v1.py` |

Still blocked when `auto-run-disabled-v1.flag` is present.

## Founder instruction

**Today → ▶ START AUTO RUN → walk away → ⏹ STOP when done.**

*End AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1*
