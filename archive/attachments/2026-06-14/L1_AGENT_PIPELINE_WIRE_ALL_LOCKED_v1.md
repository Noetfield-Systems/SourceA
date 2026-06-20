# L1 agent pipeline — ALL first layer wired

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Authority:** ASF order — ALL L1 SHOULD BE WIRED TO EACH OTHER THROUGH PIPELINE MACHINE PYTHON  
**Law:** `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md`

## Shipped

| Component | Change |
|-----------|--------|
| `scripts/l1_agent_pipeline_wire_v1.py` | L1 mesh orchestrator — calls brain wire · writes pipeline SSOT |
| `~/.sina/l1-agent-pipeline-wire-v1.json` | L1 peer sync receipt |
| `scripts/governance_center_run_v1.py` | L1 pipeline replaces standalone brain wire step |
| `scripts/agent_session_gate_run_v1.py` | `l1_agent_pipeline_wire` step for L1 roles |
| `scripts/agent_truth_bundle_v1.py` | `l1_pipeline` section |
| `scripts/brain-session-start.sh` | L1 pipeline on Brain session start |
| `.cursor/rules/l1-agent-pipeline-mandatory.mdc` | Always-on L1 mandate |
| `~/.sina/governance-chat-context-v1.json` | All 4 L1 threads `sync_before_reply` |
| `scripts/validate-l1-agent-pipeline-v1.sh` | Wiring validator |

## L1 agents wired (peer mesh)

| Rank | Role | Chat |
|------|------|------|
| 1 | Brain | `58148ac9` |
| 2 | Governance | `e54ddfa8` |
| 3 | Commercial | `6245d9dd` |
| 4 | Brief Specialist | `85dd7cd4` |

## SSOT paths

- L1 mesh: `~/.sina/l1-agent-pipeline-wire-v1.json`
- Brain decisions: `~/.sina/governance-brain-wire-v1.json`

## Verify

```bash
python3 scripts/l1_agent_pipeline_wire_v1.py --json
bash scripts/validate-l1-agent-pipeline-v1.sh
python3 scripts/agent_session_gate_run_v1.py --role governance --json
```
