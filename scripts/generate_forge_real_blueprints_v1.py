#!/usr/bin/env python3
"""Generate Forge-v0.1 real blueprint payload from secondary-cloud-forge-run-next-100 SSOT.

Output: data/forge-real-blueprints-v01.json (cloud-fetchable · one repo batch)
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS_PATH = ROOT / "data" / "secondary-cloud-forge-run-next-100-v1.json"
SCORING_PATH = ROOT / "data" / "forge-scoring-ssot-v01.json"
OUT_PATH = ROOT / "data" / "forge-real-blueprints-v01.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _infer_capability(plan: dict, scoring: dict) -> str:
    plane = str(plan.get("plane") or "")
    ws = str(plan.get("workstream") or "mac_control")
    if plane == "mac_control":
        return str(scoring.get("workstream_core_capability", {}).get("mac_control", "mac_control_cockpit_observe"))
    return str(scoring.get("workstream_core_capability", {}).get(ws, "forge_deterministic_router"))


def _infer_client_problem(plan: dict, scoring: dict) -> str:
    plane = str(plan.get("plane") or "")
    ws = str(plan.get("workstream") or "mac_control")
    if plane == "mac_control":
        return str(scoring.get("workstream_client_problem", {}).get("mac_control", "P4-mac-cockpit-only"))
    return str(scoring.get("workstream_client_problem", {}).get(ws, "P0-trust-receipt-gap"))


def _dependencies(plan: dict) -> list[str]:
    tier = str(plan.get("cost_tier") or "free")
    if tier == "free":
        return []
    if tier == "openrouter_cap":
        return ["openrouter"]
    return ["openrouter"]


def _output_artifact(plan: dict) -> dict:
    ws = str(plan.get("workstream") or "mac_control")
    pid = str(plan.get("id") or "")
    reg = str(plan.get("maps_registry") or "")
    artifacts = {
        "ws-ux": "ux_evidence_row",
        "ws-pricing": "pricing_evidence_row",
        "ws-run": "run_dashboard_spec",
        "ws-onboard": "onboard_checklist_spec",
        "ws-integrate": "dispatch_contract_spec",
        "mac_control": "mac_observe_receipt",
    }
    return {
        "artifact": artifacts.get(ws, "cloud_receipt"),
        "maps_registry": reg or None,
        "receipt_url": f"/receipts/cloud-dispatch/{pid}.json" if pid.startswith("CLOUD-SEC-") else None,
        "hub_glance": "http://127.0.0.1:13020/" if str(plan.get("plane")) == "mac_control" else None,
    }


def _already_signature(plan: dict, scoring: dict) -> str | None:
    pid = str(plan.get("id") or "")
    if pid in (scoring.get("already_implemented_plan_ids") or []):
        return "_evidence_fetch_receipt_pass" if pid.startswith("CLOUD-SEC-") else "hub_post_dispatch_dry_run_v1"
    action = str(plan.get("cloud_action") or plan.get("title") or "")
    if re.search(r"\bfetch\b.*\bevidence\b", action, re.I) and pid.startswith("CLOUD-SEC-"):
        return "_evidence_fetch_receipt_pass"
    if re.search(r"dispatch.*dry-run|POST dispatch", action, re.I):
        return "hub_post_dispatch_dry_run_v1"
    return None


def plan_to_blueprint(plan: dict, scoring: dict) -> dict:
    pid = str(plan.get("id") or "")
    plane = str(plan.get("plane") or "cloud_forge")
    action = str(plan.get("cloud_action") or plan.get("title") or "")
    ws = str(plan.get("workstream") or ("mac_control" if plane == "mac_control" else "ws-ux"))
    target = str(scoring.get("target_repo") or "sourcea/fbe-cloud-worker")
    sig = _already_signature(plan, scoring)

    inputs: dict = {
        "plane": plane,
        "workstream": ws,
        "tier": plan.get("tier"),
        "cost_tier": plan.get("cost_tier"),
        "action": action,
        "maps_registry": plan.get("maps_registry"),
        "": plan.get(""),
        "mac_role": plan.get("mac_role"),
        "plan_fingerprint": f"real-{pid}-{_infer_capability(plan, scoring)}",
    }
    if sig:
        inputs["implementation_signature"] = sig

    return {
        "id": pid,
        "schema_version": "secondary-cloud-forge-run-next-100-v1",
        "inputs": inputs,
        "outputs": _output_artifact(plan),
        "destination_repo": target,
        "validation_rule": "cloud_forge_incident_038",
        "dependencies": _dependencies(plan),
        "core_capability": _infer_capability(plan, scoring),
        "client_problem": _infer_client_problem(plan, scoring),
        "notes": action[:240],
    }


def generate() -> dict:
    plans_doc = _load(PLANS_PATH)
    scoring = _load(SCORING_PATH)
    raw = plans_doc.get("plans") or []
    blueprints = [plan_to_blueprint(p, scoring) for p in raw]
    if len(blueprints) != 100:
        raise SystemExit(f"Expected 100 blueprints, got {len(blueprints)}")

    return {
        "schema": "forge-real-blueprints-v01",
        "version": "1.0.0",
        "saved_at": _now(),
        "source": "data/secondary-cloud-forge-run-next-100-v1.json",
        "scoring_ssot": "data/forge-scoring-ssot-v01.json",
        "target_repo": scoring.get("target_repo"),
        "count": len(blueprints),
        "blueprints": blueprints,
    }


def main() -> int:
    doc = generate()
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(OUT_PATH), "count": doc["count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
