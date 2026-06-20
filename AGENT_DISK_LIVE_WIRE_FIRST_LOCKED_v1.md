# Agent disk live wire first (LOCKED v1.1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF — **one law** for agent hub vocabulary · live disk always wired automatically  
**Supersedes agent behavior:** `001-founder-zero-sina-command-name.mdc` · `HUB_DEACTIVATED` prohibition tables · dual “never say / say instead” law  
**Canonical sync:** `scripts/disk_live_wire_sync_v1.py` (L0.5 slice) · **Parent orchestrator:** `scripts/anti_staleness_auto_wire_v1.py` (L0.5→L1→L2)  
**Receipt:** `~/.sina/disk-live-wire-receipt-v1.json` · `~/.sina/anti-staleness-auto-wire-v1.json`  
**Extends:** `RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md`

---

## One sentence

**Disk is live and wired automatically — agents read synced JSON, quote `factory_now_line`, never maintain parallel prohibition vocabulary.**

---

## Automatic wire (machine — no manual step)

Every session start runs the **full stack** via session gate:

```bash
python3 scripts/agent_session_gate_run_v1.py --role <role> --json
# → anti_staleness_auto_wire_v1.py (L0.5→L1→L2)
```

L0.5 slice only (sub-component):

```bash
python3 scripts/disk_live_wire_sync_v1.py --role <role> --json
```

Wired inside `agent_session_gate_run_v1.py` · `brain-session-start.sh` · `worker_turn_entry_v1.sh`.

| Output | Path |
|--------|------|
| Truth bundle cache | `~/.sina/last-truth-bundle-v1.json` |
| Live surfaces (all roles) | `~/.sina/agent-live-surfaces-v1.json` |
| Brain live pack | `~/.sina/brain/BRAIN_LIVE_SURFACES_v1.json` |
| Wire receipt | `~/.sina/disk-live-wire-receipt-v1.json` |
| Memory mirror | `~/.sina/agent-memory-mirror-v1.json` |

**Validator:** `bash scripts/validate-disk-live-wire-v1.sh`

---

## Live surfaces (positive — quote these)

| Surface | URL / path |
|---------|------------|
| **H1 Daily** | `http://127.0.0.1:13020/` · `GET /api/worker-hub/v1` |
| **H2 Machines** | `http://127.0.0.1:13020/machines/` |
| **Founder museum** | `http://127.0.0.1:13020/legacy/` |
| **Factory SSOT** | `~/.sina/factory-now-v1.json` |
| **Next steps disk** | `~/.sina/live-ongoing-prompts-next-10-v1.json` |

**Founder daily ops:** Worker chat → **RUN INBOX** · optional H1 glance · quote **`factory_now_line`**.

---

## Session start (all roles)

```bash
python3 scripts/agent_session_gate_run_v1.py --role <role> --json
```

Gate runs disk live wire sync automatically. Read `agent-live-surfaces-v1.json` — not stale brain markdown.

---

## What is NOT SSOT

| Stale | Why |
|-------|-----|
| `command-data.json` hero | Museum projection · LAG |
| `prompt-direction` context blob | May embed command-data |
| Hand-edited `~/.sina/brain/*.md` without sync marker | Static |
| Chat transcript | Not disk |

---

## When agent steers wrong

1. Run `disk_live_wire_sync_v1.py`  
2. Fix **stale source file** logged  
3. Re-run validator — **no new ban rule**

---

## Related (not duplicate agent vocabulary law)

| Doc | Scope |
|-----|-------|
| `SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md` | Incident read policy only — superseded for hub vocabulary |
| `000-dead-law-stubs.mdc` | Dead **features** (auto-send, read-all-incidents) — not word bans |
| INCIDENT-034 | Why prohibition-first failed |

**END**
