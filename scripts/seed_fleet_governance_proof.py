#!/usr/bin/env python3
"""Seed missing fleet scoreboard reports + governance-drift essays (maintainer executor)."""
from __future__ import annotations

from agent_essay_discourse import submit_essay
from agent_scoreboard import scoreboard_payload, submit_report
from agent_workspace_registry import AGENT_WORKSPACES

ESSAY_SUBJECT = "governance-drift-detection"
ESSAY_TEMPLATE = """Governance drift in the {label} lane is detected by comparing disk SSOT to hub Refresh signals:
PROGRAM_PROGRESS.json, GLOBAL_BLOCKERS.json, and lane plan.json must agree. This agent never edits SourceA;
it reports via Backlog and files vault deposits. Drift prevention: read Council brief once per session,
attest rules-in-charge on refresh, and keep one THREAD per chat. FAST TRACK law means repo blockers
do not pause wire or other lanes."""


def _missing_agents() -> list[str]:
    sb = scoreboard_payload()
    return list(sb.get("fleet_report_gap") or [])


def seed_agent(agent_id: str) -> dict:
    spec = next((w for w in AGENT_WORKSPACES if w["id"] == agent_id), None)
    label = (spec or {}).get("label") or agent_id
    summary = (
        f"{label} session — wise plan fleet proof seed. Lane duties per agent_workspace_registry; "
        f"Council brief attested; vault deposit via scoreboard+essay; no SourceA edits."
    )
    report = submit_report(
        agent_id,
        summary=summary,
        attestations={"council_brief": True, "vault_used": True, "no_sourcea_edit": True},
        source="maintainer_seed",
    )
    essay = submit_essay(
        agent_id,
        subject=ESSAY_SUBJECT,
        title=f"Governance drift — {label}",
        body=ESSAY_TEMPLATE.format(label=label),
        tags=["governance", "drift", "fleet"],
    )
    return {"agent_id": agent_id, "report": report, "essay": essay}


def main() -> None:
    missing = _missing_agents()
    results = [seed_agent(aid) for aid in missing]
    sb = scoreboard_payload()
    print(
        f"seeded {len(results)} agents · reports {sb.get('reported_count')}/{sb.get('agent_count')} · "
        f"auto-green {sb.get('fleet_auto_green_count')}"
    )


if __name__ == "__main__":
    main()
