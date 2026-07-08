#!/usr/bin/env python3
"""WORKFLOW_CENSUS audit — four deterministic weekly rules → improvement_queue findings."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

SOURCE = "workflow_census_audit_v1"


def _parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def _finding(rule: str, text: str, *, roi: float, machine_safe: bool) -> dict[str, Any]:
    return {
        "rule": rule,
        "finding": text,
        "source": SOURCE,
        "expected_roi": roi,
        "machine_safe": machine_safe,
    }


def findings_from_census(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply advisor four rules deterministically."""
    findings: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=14)

    meta_cost = 0.0
    guard_cost = 0.0
    revenue_cost = 0.0
    revenue_count = 0

    for row in rows:
        vc = str(row.get("value_class") or "")
        cost = float(row.get("cost_usd_monthly") or 0.0)
        if vc == "META":
            meta_cost += cost
        elif vc == "GUARD":
            guard_cost += cost
        elif vc == "REVENUE":
            revenue_cost += cost
            revenue_count += 1

        last_at = _parse_ts(row.get("last_receipt_at"))
        name = str(row.get("name") or row.get("loop_key") or "?")

        # Rule 3: every loop must name its receipt
        if not row.get("receipt_named"):
            findings.append(
                _finding(
                    "R3_unnamed_receipt",
                    f"workflow_census: loop '{name}' cannot name its receipt — block or wire receipt",
                    roi=8.0,
                    machine_safe=False,
                )
            )

        # Rule 1: NONE for 14 days → propose retirement
        if vc == "NONE" or (last_at and last_at < stale_cutoff):
            if vc == "NONE" or not last_at:
                findings.append(
                    _finding(
                        "R1_retire_candidate",
                        f"workflow_census: propose retirement for '{name}' — no receipt in 14d (founder-gated kill)",
                        roi=6.0,
                        machine_safe=False,
                    )
                )

    # Rule 2: META cost > GUARD+REVENUE → RED
    guard_rev = guard_cost + revenue_cost
    if meta_cost > guard_rev and meta_cost > 0:
        findings.append(
            _finding(
                "R2_meta_grooming_red",
                (
                    f"workflow_census: META cost ${meta_cost:.2f}/mo > "
                    f"GUARD+REVENUE ${guard_rev:.2f}/mo — system grooming itself (RED)"
                ),
                roi=9.5,
                machine_safe=False,
            )
        )

    # Rule 4: REVENUE lane may never be empty
    if revenue_count == 0:
        findings.append(
            _finding(
                "R4_revenue_lane_empty",
                "workflow_census: REVENUE lane empty — zero loops touch lead/offer/delivery; ship offers (§7)",
                roi=10.0,
                machine_safe=False,
            )
        )

    # Traffic conversion diagnostic (advisor add-on)
    for row in rows:
        if row.get("loop_key") != "metric:traffic-intake-conversion":
            continue
        ref = row.get("last_receipt_ref") or {}
        visits = int(ref.get("web_visits_24h") or 0)
        leads = int(ref.get("intake_leads_24h") or 0)
        if visits > 1000 and leads == 0:
            findings.append(
                _finding(
                    "R4_traffic_zero_conversion",
                    (
                        f"workflow_census: {visits} web visits/24h → 0 non-probe intake leads — "
                        "funnel or bot traffic; cheapest revenue experiment uninstrumented"
                    ),
                    roi=9.0,
                    machine_safe=False,
                )
            )
        break

    return findings
