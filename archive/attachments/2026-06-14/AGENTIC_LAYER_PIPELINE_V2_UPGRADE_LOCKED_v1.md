# Agentic layer pipeline v2 upgrade

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Authority:** ASF — UPGRADE THE PIPELINE

## What's new in v2

| Feature | v1 | v2 |
|---------|----|----|
| SSOT | Multiple files | `~/.sina/agentic-layer-pipeline-v2.json` master receipt |
| Stack manifest | L1 only | L0–L3 full stack |
| Health probes | None | Wire age · dual-pick · memory mirror · L1/L2 counts |
| Cross-ref validation | Manual | Automatic L1↔Brain alignment |
| Self-heal | None | `--self-heal` re-sync on drift |
| Tiers | One speed | `--tier fast` (gates) · `full` (sync) |

## Commands

```bash
# Full sync
python3 scripts/agentic_layer_pipeline_v2.py --json

# Fast (session gates)
python3 scripts/agentic_layer_pipeline_v2.py --json --tier fast

# Self-heal on drift
python3 scripts/agentic_layer_pipeline_v2.py --json --self-heal

# Validate
bash scripts/validate-agentic-layer-pipeline-v2.sh
bash scripts/validate-agentic-layer-wire-v1.sh
```

## New files

- `scripts/agentic_pipeline_lib_v1.py` — shared paths · agents · health
- `scripts/agentic_layer_pipeline_v2.py` — upgraded orchestrator
- `scripts/validate-agentic-layer-pipeline-v2.sh` — v2 validator

## Hooks upgraded

- `agentic_layer_wire_sync_v1.py` → delegates to v2
- `governance_center_run_v1.py` → v2 fast tier
- `agent_session_gate_run_v1.py` → v2 for L1 + L2
- `agent_truth_bundle_v1.py` → `agentic_pipeline_v2` section
- `brain-session-start.sh` · `worker_turn_entry_v1.sh` → v2 fast
- n8n · governance_n8n → v2
