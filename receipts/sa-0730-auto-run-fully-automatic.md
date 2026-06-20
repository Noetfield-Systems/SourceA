# sa-0730 receipt — AUTO-RUN fully automatic (no tap)

**Authority:** ASF directive — remove all manual START WORKER BATCH taps.

## Shipped

| Piece | Path |
|-------|------|
| Hub-start trigger | `scripts/auto_start_worker_batch_on_hub_v1.sh` |
| Autorun engine | `scripts/auto_run_worker_batch_v1.py` |
| Batch loop | `goal1_worker_batch_loop_v1.py --batch-size 5 --max-batches 6` |
| Hub kick | `sina-command-server.py` → `_kick_autorun_on_hub_start` |
| serve hook | `serve-sina-command.sh` after health OK |
| launchd login | `com.sourcea.autorun-worker` (KeepAlive, 30s poll) |
| launchd hub | `com.sourcea.hub` → `install-autorun-launchd-v1.sh` |
| Batch chain | `schedule_after_batch` on batch `finally` |
| Cursor preflight | `cursor_window_preflight_v1.py` before every inject |

## Install

```bash
bash scripts/install-hub-launchd-v1.sh
# or
bash scripts/install-autorun-launchd-v1.sh
```

## Kill switch (executor only)

`touch ~/.sina/auto-run-disabled-v1.flag`

## Verify

```bash
bash scripts/validate-auto-run-fully-automatic-v1.sh
python3 scripts/auto_run_worker_batch_v1.py --status --json
```
