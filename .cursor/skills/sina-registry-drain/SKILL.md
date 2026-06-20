---
name: sina-registry-drain
description: >-
  Honest REGISTRY drain — receipts, quarantine fake YAML, hygiene gates. Use when
  closing sa-####, receipts, Valid YES, enforce-registry-hygiene, quarantine batch
  YAML, or proving broker CHECK ACT VERIFY chain.
disable-model-invocation: true
---

# Registry drain (honest closeout)

**Law:** `REGISTRY_DRAIN_PROCESS_LOCKED_v1.md` · progress = receipt files logged.

## Valid cycle

```text
CHECK → ACT (if gap) → VERIFY → receipts/sa-XXXX-receipt.json → honest done
```

## Does not count as done

- Chat YAML closeout without receipt file
- Batch pack stamp / overnight mark
- REGISTRY `status: done` without `receipts/sa-XXXX-receipt.json`
- 495 quarantined YAMLs in `QUARANTINE_BATCH_YAML/`

## Proof commands

```bash
cd ~/Desktop/SourceA/scripts
bash enforce-registry-hygiene-v1.sh
bash validate-registry-honest-gate-v1.sh
bash validate-closeout-gate-v1.sh
python3 program-1000-honest-status-v1.py --write
```

## Receipt requirements

- Path: `brain-os/plan-registry/sourcea-1000/receipts/sa-XXXX-receipt.json`
- `source` ∈ allowed gate (`goal1_lane_broker`, `worker_inbox`, `api`, …)
- Broker events in `~/.sina/goal1-lane-broker-events.jsonl` for full chain

## Worker + Brain

- **Worker** executes drain turns (`@sina-sourcea-worker`)
- **Brain** quotes Valid YES after hygiene — does not hand-close sa without receipt

*End sina-registry-drain*
