# Three pipelines — implementation complete (2026-06-14)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Law:** `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md`

## Shipped

| Pipeline | Trigger | Script | Receipt |
|----------|---------|--------|---------|
| P1 Orientation (Atlas) | `orientation` | `scripts/agent_orientation_pipeline_v1.py` | `~/.sina/agent-orientation-receipt-v1.json` |
| P2 Hospital (Clinic) | `hospital` | `scripts/agent_hospital_pipeline_v1.py` | `~/.sina/agent-hospital-receipt-v1.json` |
| P3 Maze (Quarantine) | `maze` | `scripts/agent_maze_pipeline_v1.py` | `~/.sina/agent-maze-receipt-v1.json` + passport |

**Registry:** `~/.sina/agent-three-pipelines-registry-v1.json`  
**Validator:** `scripts/validate-agent-three-pipelines-v1.sh` — PASS (orientation smoke)

## Verified

- Orientation: `ok=True` · 9 stations · `execution_authority: false`
- Hospital (worker): `ok=True` · no maze escalation · discharge note generated

## Founder one-word triggers

- New/raw agent → say **orientation**
- Working agent drift/off → say **hospital**
- Sick/repeat incident/critical → say **maze**

## Backlog (not in scope v1)

- H1 one-tap Hospital · H2 maze station table UI (Maintainer SHIP)
- Operator M10 comprehension quiz (shadow)
- n8n maze webhook
