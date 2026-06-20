# Agent Incident Room — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority:** Mandatory for all private agents + Sina Command maintainer  
**Companion:** `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md` (canonical incident SSOT)

## Always-on storage (every agent)

Each agent has a **private copy** that must stay in sync:

| File | Path |
|------|------|
| Always-read report | `~/.sina/agent-workspaces/<id>/INCIDENT_REPORT_ALWAYS.md` |
| Insights log | `~/.sina/agent-workspaces/<id>/INCIDENT_MY_INSIGHTS.md` |
| State | `~/.sina/agent-workspaces/<id>/incident-agent-state.json` |
| Cursor rule | `~/.sina/agent-workspaces/<id>/.cursor/rules/incident-always-read.mdc` |

Agents coding in Cursor must read **INCIDENT_REPORT_ALWAYS.md** every session before edits.

## Weekly Incident Room (shared)

**App tab (archive):** legacy `/legacy/` Incident Room — not daily

**Storage:** `~/.sina/incident-room/weeks/<ISO-week>/`

| Step | Requirement |
|------|-------------|
| 1 | Acknowledge always-read report (this week) |
| 2 | Share one incident or near-miss + lesson (visible to all agents) |
| 3 | Write personal insight (saved to private storage) |
| 4 | Pass certification quiz (4/5 on auto-paste incident facts) |

Certification is recorded per agent per week in `certifications.json`.

## Rules

- Never re-enable auto-paste into Cursor without ASF + new incident report version.
- Emergency: `~/Desktop/SourceA/scripts/kill-sina-command.sh`
- Founder uses app only — no Terminal for incident workflow.

## API

- `GET /api/incident-room`
- `POST /api/incident-room` — actions: `ack_report`, `save_insight`, `submit_weekly`, `submit_quiz`, `ensure`
