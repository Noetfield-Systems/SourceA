# Anti-staleness auto wire — layer sync law (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF — always wired automatically L0.5 → L1 → L2  
**Machine:** `scripts/anti_staleness_auto_wire_v1.py`  
**Receipt:** `~/.sina/anti-staleness-auto-wire-v1.json`  
**Extends:** `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md` · `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` · `AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`

---

## One sentence

**Every agent session runs one Python orchestrator that syncs L0.5 disk truth → L1 pipeline → L2 brain wire — automatically, before any reply.**

---

## Layer stack (what auto-wire runs)

| Layer | Name | Auto-wire steps | SSOT receipt |
|-------|------|-----------------|--------------|
| **L0.5** | Machine pipeline | `disk_live_wire_sync` · `queue_ssot_unify` · monitor light | `disk-live-wire-receipt-v1.json` · `agent-live-surfaces-v1.json` |
| **L1** | Brain · Gov · Commercial · Brief | `agentic_layer_pipeline_v2` → `l1-agent-pipeline-wire-v1.json` | `agentic-layer-pipeline-v2.json` |
| **L2** | Worker · R2 · M2 · M3 | same pipeline → `governance-brain-wire-v1.json` | `governance-brain-wire-v1.json` |

**L0** (ASF + Hub) is human — not synced by agents.

---

## One command (all roles)

```bash
python3 scripts/anti_staleness_auto_wire_v1.py --role <role> --tier session --json
```

**Wired automatically inside:**

- `agent_session_gate_run_v1.py` — every session start
- `brain-session-start.sh`
- `worker_turn_entry_v1.sh` — worker tier

---

## Tiers

| Tier | When | Extra |
|------|------|-------|
| `session` | Session gate · Brain start | L0.5 + L1/L2 fast |
| `worker` | Worker turn entry | session + `worker_anti_staleness_heal` |
| `full` | Governance cascade · explicit heal | session + pipeline full + brain snapshot |

---

## Agent read order (after wire)

1. `~/.sina/anti-staleness-auto-wire-v1.json` — ok + queue_sa + layer status  
2. `~/.sina/agent-live-surfaces-v1.json` — hub URLs + factory_now_line  
3. `~/.sina/agentic-layer-pipeline-v2.json` — L1/L2 health  
4. Role receipt from session gate

**Never** trust chat memory or stale `~/.sina/brain/*.md` over wired JSON.

---

## Validator

```bash
bash scripts/validate-anti-staleness-auto-wire-v1.sh
```

Included in anti-staleness bundle · check cart W9.

---

## Supersedes scattered manual sync

Agents must **not** run L0.5 / L1 / L2 scripts separately on session start — use orchestrator only.

**END**
