# Brain L2 wire — ALL second layer bound

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Authority:** ASF order — ALL L2 SHOULD BE WIRED TO BRAIN  
**Law:** `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md`

## Shipped

| Component | Change |
|-----------|--------|
| `scripts/brain_governance_wire_v1.py` | `l2_wired.agents[]` (Worker, R2, M2, M3) · alias `~/.sina/brain-wire-v1.json` · fixed Brain chat `58148ac9` |
| `scripts/agent_truth_bundle_v1.py` | `brain_wire` section in truth bundle |
| `scripts/agent_session_gate_run_v1.py` | `brain_l2_wire` step for L2 gate roles |
| `scripts/worker_anti_staleness_heal_v1.py` | Brain wire on every AS-heal |
| `scripts/goal1_lane_broker.py` | `brain_wire` block on pickup |
| `scripts/worker_turn_entry_v1.sh` | Brain wire before factory heal |
| `.cursor/rules/brain-wire-l2-mandatory.mdc` | L2 mandatory read rule |
| `.cursor/rules/sourcea-worker-inbox.mdc` | Brain wire before pickup |
| `~/.sina/governance-chat-context-v1.json` | All L2 threads `sync_before_reply` |
| `scripts/validate-brain-l2-wire-v1.sh` | Wiring validator |

## L2 agents wired

| Rank | Role | Chat |
|------|------|------|
| 5 | Worker | `fd67502f` |
| 6 | Researcher 2 | `20b12e67` |
| 7 | Maintainer 2 | `74f5ccab` |
| 8 | Maintainer 3 | `3369d11c` |

## SSOT paths

- Primary: `~/.sina/governance-brain-wire-v1.json`
- Alias: `~/.sina/brain-wire-v1.json`

## Verify

```bash
python3 scripts/brain_governance_wire_v1.py --json
bash scripts/validate-brain-l2-wire-v1.sh
python3 scripts/agent_session_gate_run_v1.py --role worker --json
```
