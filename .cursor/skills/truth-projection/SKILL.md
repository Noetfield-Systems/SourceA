---
name: truth-projection
description: >-
  Disk truth vs hub projection — agent truth bundle, factory-now, dual-pick law.
  Use when quoting progress, hub state, or detecting stale AUTO-RUN copy.
disable-model-invocation: true
---

# Truth projection (all factory roles)

## Founder T0 (verbatim)

**Cursor AUTO-RUN does not exist.** If you mention it, you are **stale** — read disk same turn.

## Session start

```bash
cd ~/Desktop/Noetfield-Systems/SourceA
python3 scripts/agent_truth_bundle_v1.py --json
python3 scripts/factory_control_v1.py now
```

Or: `GET http://127.0.0.1:13020/api/agent-truth-bundle-v1`

## Two planes

| Plane | SSOT |
|-------|------|
| Control | `factory-now-v1.json` · `run-inbox-disk-truth-v1.json` |
| Projection | `command-data.json` — rebuild via `hub_projection_sync_v1` |

Never trust chat memory for counts. Quote `factory-now` line in status replies.

## Dual-pick law

`live_pick` (goal-progress) must equal `queue_sa` (run-inbox truth). Mismatch = projection bug.
