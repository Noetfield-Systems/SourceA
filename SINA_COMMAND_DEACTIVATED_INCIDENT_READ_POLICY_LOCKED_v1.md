# Sina Command deactivated + incident read policy — LOCKED v1.1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-14 · **Authority:** ASF order  
**Superseded for hub vocabulary:** use **`AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`** only — no parallel prohibition law  
**This doc scope:** incident read policy + archive routing only  
**Related:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · INCIDENT-028 · INCIDENT-031 · INCIDENT-034

---

## 0. One sentence

**Legacy monolith is museum at `/legacy/` — daily ops = RUN INBOX + live surfaces JSON; session gate replaces “read all incidents”.**

---

## 1. Live surfaces (agent SSOT — auto-synced)

Read `~/.sina/agent-live-surfaces-v1.json` after session gate.  
Sync: `python3 scripts/disk_live_wire_sync_v1.py --json`

| Surface | URL |
|---------|-----|
| H1 daily | `http://127.0.0.1:13020/` |
| H2 machines | `http://127.0.0.1:13020/machines/` |
| Founder museum | `http://127.0.0.1:13020/legacy/` |

**Primary daily ops:** Worker chat → **RUN INBOX** · quote `factory_now_line`.

---

## 2. Incident read policy (all agents)

### Do not instruct founder

- “Read all incidents” / incident compendium / paste `INCIDENT_REPORT_ALWAYS.md`
- Listing 10+ incident IDs as mandatory pre-work

### Correct session start

```bash
python3 scripts/agent_session_gate_run_v1.py --role <role> --json
```

Mirror incidents **by id only** when gate inject lists: **024 · 028 · 016 · 002**

---

## 3. Agent close-line (founder)

- **RUN INBOX** in Worker chat for next sa
- Optional: Worker Hub → Next steps
- Quote live `factory_now_line` from disk-live-wire receipt

---

## 4. Verification

```bash
bash scripts/validate-disk-live-wire-v1.sh
python3 scripts/agent_session_gate_run_v1.py --role any --json
```

**END**
