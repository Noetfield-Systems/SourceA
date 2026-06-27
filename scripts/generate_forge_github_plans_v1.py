#!/usr/bin/env python3
"""Generate plans/*.json for Forge v0.2 GitHub source (real field names, not forge-native).

Exports secondary-cloud-forge-run plans using a GitHub-friendly schema so Stage 0b
adapter must map plan_id→id, version→schema_version, target→destination_repo, etc.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAIN = ROOT / "data" / "secondary-cloud-forge-run-next-100-v1.json"
OUT = ROOT / "plans"
CAPABILITY = {
    "mac_control": "mac_control_cockpit_observe",
    "ws-ux": "competitor_evidence_pipeline",
    "ws-pricing": "competitor_evidence_pipeline",
    "ws-run": "worker_run_dashboard",
    "ws-onboard": "competitor_evidence_pipeline",
    "ws-integrate": "cloud_worker_dispatch_api",
}
PROBLEM = {
    "mac_control": "P4-mac-cockpit-only",
    "ws-ux": "P2-onboard-friction",
    "ws-pricing": "P3-pricing-clarity",
    "ws-run": "P1-run-visibility",
    "ws-onboard": "P2-onboard-friction",
    "ws-integrate": "P0-trust-receipt-gap",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    doc = json.loads(DRAIN.read_text(encoding="utf-8"))
    plans = doc.get("plans") or []
    OUT.mkdir(parents=True, exist_ok=True)

    for p in plans:
        pid = str(p.get("id") or "")
        ws = str(p.get("workstream") or p.get("plane") or "mac_control")
        action = str(p.get("cloud_action") or p.get("title") or "")
        plan = {
            "plan_id": pid,
            "version": "secondary-cloud-forge-run-next-100-v1",
            "target": "sourcea/fbe-cloud-worker",
            "validation": "cloud_forge_incident_038",
            "metadata": {
                "core_capability": CAPABILITY.get(ws, "forge_deterministic_router"),
                "client_problem_id": PROBLEM.get(ws, "P0-trust-receipt-gap"),
                "workstream": ws if ws != "mac_control" else "mac_control",
                "competitor": p.get("competitor"),
                "tier": p.get("tier"),
                "cost_tier": p.get("cost_tier"),
                "maps_registry": p.get("maps_registry"),
            },
            "inputs": {
                "plane": p.get("plane"),
                "action": action,
                "workstream": ws if ws != "mac_control" else "mac_control",
                "tier": p.get("tier"),
                "competitor": p.get("competitor"),
                "maps_registry": p.get("maps_registry"),
            },
            "outputs": {
                "artifact": "cloud_receipt",
                "receipt_url": f"/receipts/cloud-dispatch/{pid}.json" if pid.startswith("CLOUD") else None,
            },
        }
        out_path = OUT / f"{pid}.json"
        out_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema": "forge-github-plans-manifest-v1",
        "saved_at": _now(),
        "count": len(plans),
        "source": str(DRAIN.relative_to(ROOT)),
        "note": "GitHub-friendly field names for Forge v0.2 adapter inspect stage",
    }
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(plans)} plans to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
