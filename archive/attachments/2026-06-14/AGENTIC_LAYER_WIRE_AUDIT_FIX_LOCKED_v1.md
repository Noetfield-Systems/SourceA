# Agentic layer wire — full audit fix 2026-06-14

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority:** ASF — CHECK AND FIX THEM ALL

## Issues found + fixed

| Issue | Fix |
|-------|-----|
| Standalone `brain_governance_wire_v1.py` stripped `l1_pipeline` cross-ref | Preserve/embed from `l1-agent-pipeline-wire-v1.json` on every brain wire write |
| Deprecated `l1_governance` singleton | Replaced with `l1_wired_to_brain` + `l1_pipeline` |
| No single sync command | Added `agentic_layer_wire_sync_v1.py` |
| No master validator | Added `validate-agentic-layer-wire-v1.sh` |
| n8n / governance_n8n redundant brain-only refresh | Use `agentic_layer_wire_sync_v1.py` |
| Layer stack founder text stale | L1 all show wired TO Brain via pipeline |
| Truth bundle validator pipe bug | Fixed heredoc vs pipe in master validator |

## One command (fix all wires)

```bash
python3 scripts/agentic_layer_wire_sync_v1.py --json
bash scripts/validate-agentic-layer-wire-v1.sh
```

## SSOT map

| Layer | Script | Receipt |
|-------|--------|---------|
| L1→Brain | `l1_agent_pipeline_wire_v1.py` | `~/.sina/l1-agent-pipeline-wire-v1.json` |
| Brain decisions + L2 | `brain_governance_wire_v1.py` | `~/.sina/governance-brain-wire-v1.json` |
| All layers | `agentic_layer_wire_sync_v1.py` | `~/.sina/agentic-layer-wire-sync-v1.json` |
