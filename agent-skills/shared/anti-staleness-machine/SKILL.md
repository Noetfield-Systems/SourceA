---
name: anti-staleness-machine
description: >-
  Zero-latency hub projection sync — anti-staleness bundle, build choke, purge
  Cursor AUTO-RUN copy. Use when hub/command-data drifts, AS-01 FAIL, or law
  change must latch same turn.
disable-model-invocation: true
---

# Anti-staleness machine (Maintainer)

**Law:** `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md`

## Founder T0

**Cursor AUTO-RUN does not exist.** If you see `START AUTO RUN` or recommend it, you are **stale**.

## Commands

```bash
cd ~/Desktop/SourceA
bash scripts/validate-anti-staleness-bundle-v1.sh
python3 scripts/hub_projection_sync_v1.py --caller maintainer --json
python3 scripts/align_command_data_ui_v1.py
bash scripts/validate-hub-p0-no-autorun-v1.sh
```

## Zero-latency hooks (mandatory)

After honest writes, hub projection must refresh without founder manual Refresh:

- `brain_sync_lib_v1.sync_brain_snapshot`
- `factory_control_v1.write_stop_receipt` / `write_resume_token`
- `stop_goal1_auto_run_v1.py`

All call `hub_projection_sync_v1.sync_hub_projection`.

## Build choke

| Path | Must run AS-01 |
|------|----------------|
| `build-sina-command-panel.py` STRICT | yes |
| `hub_self_refresh_v1.py` | yes |
| `serve-sina-command.sh` panel build | fail not swallowed |
