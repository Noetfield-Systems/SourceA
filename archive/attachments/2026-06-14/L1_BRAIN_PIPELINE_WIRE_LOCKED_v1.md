# L1 → Brain pipeline — ALL L1 wired TO Brain

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Authority:** ASF order — ALL L1 SHOULD BE WIRED TO BRAIN THROUGH PIPELINE MACHINE PYTHON  
**Law:** `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md`

## Model

```text
Brain (58148ac9) — L1 hub · execution authority
    ↑ fed by Python pipeline
    ├── Governance (e54ddfa8)   wired_to_brain
    ├── Commercial (6245d9dd)   wired_to_brain
    └── Brief (85dd7cd4)        wired_to_brain
```

## SSOT

| Path | Role |
|------|------|
| `~/.sina/l1-agent-pipeline-wire-v1.json` | L1 → Brain pipeline receipt |
| `~/.sina/l1-brain-pipeline-wire-v1.json` | Alias |
| `~/.sina/governance-brain-wire-v1.json` | Brain decisions source |

## Key fields

- `brain_hub` — Brain feeds all L1
- `l1_to_brain.subordinates[]` — Gov · Commercial · Brief with `wired_to_brain: true`
- `l1_wired.shared` — Brain `active_decisions[]` + `queue_head` for all L1

## Verify

```bash
python3 scripts/l1_agent_pipeline_wire_v1.py --json
bash scripts/validate-l1-agent-pipeline-v1.sh
```
