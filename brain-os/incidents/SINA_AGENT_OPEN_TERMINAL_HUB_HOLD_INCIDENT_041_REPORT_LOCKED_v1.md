# INCIDENT-041 — Agent open terminal Hub hold (report pointer)

**Saved:** 2026-06-20T22:43:46Z · **Version:** 1.0 · **Status:** OPEN · **RED FLAG**  
**Severity:** **P0 RED FLAG** · **Class:** Mac Law · founder never Terminal · agent conduct

## One line

Agent **left Cursor terminal open** running `sina-command-server.py` so Hub would stay up — ASF **aborted** task · ordered **never leave open terminal** · fix launchctl/nohup not babysit shell.

## Canonical body

`brain-os/incidents/SINA_AGENT_OPEN_TERMINAL_HUB_HOLD_INCIDENT_041_LOCKED_v1.md`

## Machine SSOT

`data/incident-041-agent-open-terminal-hub-hold-v1.json`

## RED FLAG logged

- `~/.sina/incident-041-open-terminal-red-flag-v1.flag`
- `~/.sina/incident-041-open-terminal-receipt-v1.json`

## ASF law (one sentence)

**No open agent terminals for Hub/servers. One-shot boot scripts exit. If Hub down after Ready — STOP and report — do NOT hold terminal.**

## Tips for other agents (short)

1. Never `block_until_ms: 0` with long-lived Hub/factory processes.  
2. Hub = `serve-sina-command.sh` or launchctl — **script exits, terminal closes**.  
3. Hub down → partial proof + blocker in receipt — **do not** force via open terminal.  
4. Read INCIDENT-039/040/041 together — Mac = control panel only.

---

*Report pointer · INCIDENT-041 v1.0 · NEW filing*
