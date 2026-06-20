# Stale law sweep — full disk sync (LOCKED v1)

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-06 · **Authority:** ASF order  
**Law:** `SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md`

## Result

| Check | Status |
|-------|--------|
| `agent_memory_mirror_v1.py --sync` | **PASS** (`mirror_hash8=f54f9138`) |
| `agent_session_gate_run_v1.py --role any` | **PASS** |
| Mirror scan roots | scripts · agent-skills · `.cursor/rules` · `.cursor/skills` · brain-os/entry |
| Hub panel (`agent-control-panel/`) | **Excluded** — ASF-only archive; stale UI strings expected |

## Surfaces updated

- **Rules:** `000-dead-law-stubs.mdc` · `prompt-queue.mdc` · `agent-loop.mdc` · `agent-memory-mirror.mdc` · `semej-agent.mdc`
- **Skills:** `agent-skills/sourcea_worker/SKILL.md` · `.cursor/skills/sina-sourcea-worker/SKILL.md` · `agent-self-audit-loop/SKILL.md`
- **Entry:** `AGENT_DESK_START_HERE.md` · `MANDATORY_READ_BY_ROLE` header · `FOUNDER_LANE_SEPARATION`
- **Scripts:** activate-* loops · lane_briefs · build-sina-daily-bowl · agent_private_workspaces templates · agent_system_unified · brain_governance_wire · generate-repo-loop-packs · intelligence_circle · live-agent-cursor-reply
- **Docs:** `COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md`

## Founder truth (frozen)

1. **Sina Command** brand = **DEACTIVATED** — never instruct
2. **Daily** = Cursor Worker chat **RUN INBOX** + disk truth bundle
3. **Optional** = Worker Hub `http://127.0.0.1:13020/` Next steps · Safety
4. **Incidents** = session gate only — not compendium · not read-all

## Still archive-only (not agent close-lines)

- `agent-control-panel/assets/app.js` — legacy monolith UI (ASF edit lock)
- `scripts/sina-command-server.py` — infra process name
- Historical attachments under `archive/attachments/` — chronology only
