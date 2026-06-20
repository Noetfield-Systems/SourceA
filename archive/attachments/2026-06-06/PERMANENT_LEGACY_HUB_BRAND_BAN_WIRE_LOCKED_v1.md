# Permanent legacy hub brand ban — enforcement wire (LOCKED v1)

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-06 · **Authority:** ASF order — governance in charge

## Why agents kept saying it (root cause)

1. **Rules taught the name** — tables like "Hub = Sina Command" in always-injected `.mdc` files
2. **No output gate** — session gate did not scan draft replies; only disk scripts
3. **Hub archive still contains the brand** — `command-data.json`, `sina_command_lib.py` (ASF-only edit) — agents read stale copy from chat memory + old rules
4. **Forbid-by-naming** — skills said "never say Sina Command" which **injects the phrase**

## Permanent fix (machine-enforced)

| Layer | Mechanism |
|-------|-----------|
| **Rule** | `.cursor/rules/001-founder-zero-sina-command-name.mdc` — alwaysApply |
| **Output gate** | `founder_close_line_gate_v1.py` **F23** — blocks bare brand in draft text |
| **Pre-ship** | `agent_session_gate_run_v1.py --pre-ship --scan-text "<draft>"` — mandatory per 001 rule |
| **Validator** | `validate-founder-zero-sina-command-v1.sh` — in anti-staleness bundle |
| **Mirror** | `agent_memory_mirror_v1.py` — required rule 001 · inject without brand name |
| **Scripts** | `agent_loop.py` — legacy loop copy cleaned |
| **Skills** | Worker skill — HUB_DEACTIVATED row pointer, no brand in NEVER list |

## Founder hears from agents now

- **RUN INBOX** · **Worker Hub** · **legacy archive** — never the old brand name

## Still contains brand (expected — not agent close-lines)

- `agent-control-panel/` hub UI JSON — ASF maintainer workspace only
- `scripts/sina-command-server.py` — process name — excluded from mirror scan
- Edit-lock rule `sina-command-protected.mdc` — internal only

## Verify

```bash
bash scripts/validate-founder-zero-sina-command-v1.sh
python3 scripts/agent_memory_mirror_v1.py --sync --validate
```
