# Broker Pack 1000 — LOCKED (Goal1 lane broker)

**Count:** 1000 unique prompts · **IDs:** `br-0001` … `br-1000`  
**Scope:** `goal1_lane_broker` · worker-submit · brain-poll/ack · orchestrator · batch log  
**NOT:** sourcea-1000 drain · ft-* fast-track · retired ac-* pack

## Pick (curriculum — when broker breaks)

```bash
bash scripts/plan-broker-pack-run.sh pick 1
```

## Regenerate

```bash
python3 scripts/generate-broker-pack-1000.py
```

## Runtime default

**Hub ▶ AUTO-RUN 50** + `goal1_run_loop_v1.py` — parallel **Cloud Forge Run:** `plan-no-asf-run.sh pick 1`

## Grid

10 phases × 100 unique broker probes — zero tier mirrors.
