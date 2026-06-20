#!/usr/bin/env python3
"""Incident fix ownership — role obligations + close gate (law SSOT)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAW = ROOT / "SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md"
REGISTRY = ROOT / "brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"

ROLE_OBLIGATIONS = {
    "governance_specialist": "Own all governance fixes; cascade + proof; law audit; no fixed without receipt",
    "worker": "VERIFY via broker + receipt; never hand-edit REGISTRY",
    "specialist": "Advisory only — execution_authority false — no sa closeout",
    "brain": "Route INBOX — no substitute Worker execution",
    "machine": "Fail-closed gates; auto-revert unproven done",
    "stairlift": "Propagate law to all agents via governance_stairlift_sync_v1.py",
    "executor": "Build logged; POST loop response; obey stairlift payload",
    "advisor": "Coach only — never reorder roadmap or close sa",
    "vinny": "Named operator surface — load stairlift SSOT; zero chat-only law sync",
}

# Every surface that must receive stairlift payload (no drift / no stasis)
AGENT_SURFACES = (
    "governance_specialist",
    "worker",
    "brain",
    "specialist",
    "executor",
    "advisor",
    "vinny",
    "semej",
    "sourcea_worker",
    "sourcea_brain",
    "trustfield",
    "virlux",
    "ai_dev_bridge_os",
    "noetfield_local",
    "noetfield_cloud",
    "seven77",
)

STANDING_VALIDATORS = [
    ("validate-broker-receipt-cycle-v1.sh", "machine"),
    ("validate-worker-factory-heal-v1.sh", "governance_specialist"),
]

STAIRLIFT_OUT = Path.home() / ".sina" / "governance-stairlift-v1.json"
VALIDATOR_RECEIPT = Path.home() / ".sina" / "governance-validator-receipt-v1.json"
RECEIPT_TTL_SEC = 3600


def _check_stairlift_shipped() -> tuple[bool, str]:
    if not STAIRLIFT_OUT.is_file():
        return False, "missing ~/.sina/governance-stairlift-v1.json"
    try:
        payload = json.loads(STAIRLIFT_OUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"bad stairlift payload: {exc}"
    missing = [s for s in AGENT_SURFACES if s not in (payload.get("surfaces") or [])]
    if missing:
        return False, f"surfaces missing: {','.join(missing[:5])}"
    if not payload.get("roles"):
        return False, "roles missing in stairlift payload"
    return True, "stairlift payload ok"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_receipt() -> dict:
    if not VALIDATOR_RECEIPT.is_file():
        return {}
    try:
        return json.loads(VALIDATOR_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_receipt(rows: list[dict]) -> None:
    VALIDATOR_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATOR_RECEIPT.write_text(
        json.dumps({"at": _now(), "rows": {r["artifact"]: r for r in rows if r.get("ok")}}, indent=2) + "\n",
        encoding="utf-8",
    )


def _receipt_fresh(script: str, receipt: dict) -> bool:
    row = (receipt.get("rows") or {}).get(f"scripts/{script}")
    if not row or not row.get("ok"):
        return False
    try:
        at = datetime.fromisoformat(str(receipt.get("at", "")).replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - at).total_seconds()
        return age < RECEIPT_TTL_SEC
    except (TypeError, ValueError):
        return False


def standing_fix_matrix(*, use_receipt_cache: bool = False) -> list[dict]:
    receipt = _load_receipt() if use_receipt_cache else {}
    rows = []
    for script, role in STANDING_VALIDATORS:
        path = ROOT / "scripts" / script
        ok = False
        detail = ""
        cached = use_receipt_cache and _receipt_fresh(script, receipt)
        if cached:
            ok = True
            detail = "receipt cache hit"
        elif path.is_file():
            proc = subprocess.run(
                ["bash", str(path)],
                cwd=str(ROOT / "scripts"),
                capture_output=True,
                text=True,
                timeout=120,
            )
            ok = proc.returncode == 0
            detail = ((proc.stdout or "") + (proc.stderr or "")).strip()[-200:]
        rows.append(
            {
                "role": role,
                "obligation": ROLE_OBLIGATIONS.get(role, ""),
                "artifact": f"scripts/{script}",
                "validator": f"bash scripts/{script}",
                "status": "shipped" if ok else "open",
                "ok": ok,
                "detail": detail,
            }
        )
    ok, detail = _check_stairlift_shipped()
    rows.append(
        {
            "role": "stairlift",
            "obligation": ROLE_OBLIGATIONS["stairlift"],
            "artifact": str(STAIRLIFT_OUT),
            "validator": "governance_stairlift_sync_v1.py + payload surfaces",
            "status": "shipped" if ok else "open",
            "ok": ok,
            "detail": detail,
        }
    )
    return rows


def audit_standing(*, run_validators: bool = True, use_receipt_cache: bool = False) -> dict:
    if run_validators:
        rows = standing_fix_matrix(use_receipt_cache=use_receipt_cache)
        if rows and not use_receipt_cache:
            _save_receipt([r for r in rows if r.get("role") != "stairlift"])
        elif rows and use_receipt_cache:
            ran = [r for r in rows if r.get("detail") != "receipt cache hit" and r.get("role") != "stairlift"]
            if ran:
                _save_receipt(rows)
    else:
        ok, detail = _check_stairlift_shipped()
        rows = [
            {
                "role": "stairlift",
                "obligation": ROLE_OBLIGATIONS["stairlift"],
                "artifact": str(STAIRLIFT_OUT),
                "validator": "payload surfaces",
                "status": "shipped" if ok else "open",
                "ok": ok,
                "detail": detail,
            }
        ]
    open_rows = [r for r in rows if r.get("status") != "shipped"]
    return {
        "ok": len(open_rows) == 0,
        "schema": "incident-fix-ownership-audit-v1",
        "at": _now(),
        "law": str(LAW.name),
        "rows": rows,
        "open_count": len(open_rows),
        "law_file_ok": LAW.is_file(),
        "registry_ok": REGISTRY.is_file(),
    }


def payload_for_agents() -> dict:
    audit = audit_standing(run_validators=False)
    founder_directive: dict = {}
    try:
        from founder_directive_ssot_v1 import directive_payload  # noqa: WPS433

        founder_directive = directive_payload()
    except Exception:
        pass
    return {
        "schema": "governance-stairlift-v1",
        "at": _now(),
        "law": "SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md",
        "one_line": "No incident closes without fix matrix + validator PASS; stairlift updates every agent.",
        "roles": ROLE_OBLIGATIONS,
        "surfaces": list(AGENT_SURFACES),
        "mandatory_validators": [s for s, _ in STANDING_VALIDATORS],
        "standing_audit_ok": audit.get("ok"),
        "founder_directive": founder_directive,
        "no_hub": founder_directive.get("no_hub"),
        "hub_status": founder_directive.get("hub_status"),
    }
