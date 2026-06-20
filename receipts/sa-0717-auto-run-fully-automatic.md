# sa-0717 receipt — AUTO-RUN fully automatic

**Install:** `bash scripts/install-autorun-launchd-v1.sh`
**Daemon:** `com.sourcea.autorun-worker` (KeepAlive, RunAtLoad, 30s poll)
**Engine:** `scripts/auto_run_worker_batch_v1.py`
**Chain:** batch `finally` → `schedule_after_batch` → kickstart + respawn
**Kill switch:** `~/.sina/auto-run-disabled-v1.flag`
