#!/usr/bin/env python3
"""Apply receipt for 015_executive_mesh_v1 + optional row probe."""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    for p in (
        Path.home() / ".sourcea-secrets/portfolio-spine.env",
        Path.home() / ".sourcea-secrets/portfolio-spine-db.env",
    ):
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main() -> int:
    load_env()
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    tables = [
        "executive_runs",
        "role_runs",
        "role_decision_packets",
        "mesh_decisions",
        "mesh_commitments",
        "mesh_work_packets",
        "mesh_evidence_receipts",
        "mesh_outbox_events",
        "canonical_state_versions",
    ]
    probes = {}
    for table in tables:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select=*&limit=1",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                probes[table] = {"ok": True, "status": resp.status}
        except Exception as exc:  # noqa: BLE001
            probes[table] = {"ok": False, "error": str(exc)[:160]}

    receipt = {
        "schema": "sourcea.executive_mesh.migration_apply_receipt.v1",
        "decision_id": "NF-EXECUTIVE-MESH-V1",
        "migration": "015_executive_mesh_v1.sql",
        "applied_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "psycopg2",
        "project_ref": os.environ.get("SUPABASE_PROJECT_ID"),
        "probes": probes,
        "verdict": "PASS" if all(p.get("ok") for p in probes.values()) else "FAIL",
    }
    out = ROOT / "receipts/executive/executive-mesh-v1-supabase-015-apply.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(out), "verdict": receipt["verdict"]}, indent=2))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
