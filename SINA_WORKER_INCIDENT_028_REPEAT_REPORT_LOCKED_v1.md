# INCIDENT-028-REPEAT — Worker stale close-line (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** REMEDIATED 2026-06-13 · mechanical gate + entry gate defense  
**LOCKED body:** `brain-os/incidents/SINA_WORKER_INCIDENT_028_REPEAT_LOCKED_v1.md`  
**Parent:** INCIDENT-028

## Main reason

Agents used **stale Cursor rule injection + hub literals** instead of **disk truth** before founder-facing close-lines. No mechanical fail-closed on reply text.

## Fix stack

| Layer | Script |
|-------|--------|
| Scan | `founder_close_line_gate_v1.py` |
| Conduct | `agentic_conduct_gate_v1.py` |
| Session | `agent_session_gate_run_v1.py --scan-text` |
| Entry | `cursor_entry_gate.py --scan-text` (worker) |
| Hub | `sina_command_lib.py` must_do_today |

## Verify

```bash
bash scripts/validate-founder-close-line-gate-v1.sh
bash scripts/validate-anti-staleness-bundle-v1.sh   # 42 steps
```
