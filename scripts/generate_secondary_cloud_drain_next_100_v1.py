#!/usr/bin/env python3
"""Generate data/secondary-cloud-drain-next-100-v1.json — INCIDENT-038 v1.1 law."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-competitor-1000/REGISTRY.json"
OUT = ROOT / "data/secondary-cloud-drain-next-100-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    backlog = [p for p in reg.get("plans") or [] if p.get("status") == "backlog"][:90]
    out: list[dict] = []
    mac_rows = [
        ("MAC-CTL-001", "W-CLOUD-001", "Mac control CHECK: validate-mac-control-plane + forge dry-run"),
        ("MAC-CTL-002", "W-CLOUD-002", "Mac control ACT: wire live Railway FBE dispatch receipt"),
        ("MAC-CTL-003", "W-CLOUD-003", "Mac control VERIFY: brain cloud pulse B0001→B1000"),
        ("MAC-CTL-004", None, "validate-mac-worker-vs-factory-vocabulary-v1.sh PASS"),
        ("MAC-CTL-005", None, "Hub POST dry-run /api/cloud-worker/dispatch/v1"),
        ("MAC-CTL-006", None, "forge_cloud_env_load — secrets in ~/.sourcea-secrets only"),
        ("MAC-CTL-007", None, "validate-forge-mvp-baseline + portfolio-competitor-1000"),
        ("MAC-CTL-008", None, "loop_specialist_tick dry-run — cloud tick not Mac motor"),
        ("MAC-CTL-009", None, "Read fbe-cloud-adapter receipt — Mac glance only"),
        ("MAC-CTL-010", None, "Confirm FREEZE + no fbe_motor_delegate on Mac"),
    ]
    for i, (cid, bind, title) in enumerate(mac_rows, 1):
        out.append(
            {
                "n": i,
                "id": cid,
                "bind": bind,
                "plane": "mac_control",
                "mac_role": "observe · validate · optional dispatch POST · read receipt",
                "mac_build_forbidden": True,
                "mac_executes_plan_body": False,
                "title": title,
            }
        )
    for j, p in enumerate(backlog, 11):
        out.append(
            {
                "n": j,
                "id": f"CLOUD-SEC-{j - 10:03d}",
                "maps_registry": p["id"],
                "plane": "cloud_forge",
                "mac_role": "none — batch dispatch POST optional · read receipt after",
                "mac_executes_plan_body": False,
                "stack": "sourcea",
                "competitor": p.get("competitor"),
                "workstream": p.get("workstream"),
                "tier": p.get("tier"),
                "cost_tier": "free" if p.get("tier") == "T0" else "openrouter_cap",
                "cloud_action": (p.get("title") or "")[:220],
            }
        )
    doc = {
        "schema": "secondary-cloud-drain-next-100-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "authority": "INCIDENT-038 v1.1",
        "one_law": "1-10 Mac control only. 11-100 cloud secondary drain. Mac NEVER executes sa-mkt bodies.",
        "forbidden": [
            "Worker on Mac runs every plan",
            "RUN INBOX per sa-mkt on Mac",
            "sa-mkt as Mac implement queue",
        ],
        "incident_ref": "brain-os/incidents/SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md",
        "count": len(out),
        "plans": out,
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(OUT), "count": len(out)}, indent=2))
    return 0 if len(out) == 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
