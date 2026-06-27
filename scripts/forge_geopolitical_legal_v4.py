#!/usr/bin/env python3
"""Forge Geopolitical Legal Layer v4 — nations as legal systems, treaties, sanctions.

Cross-system law: each nation has jurisdiction; treaties bridge nations; sanctions enforce.
Store: ~/.sina/forge-geopolitical-legal-v4.json
Receipt: ~/.sina/forge-geopolitical-legal-latest-v4.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_V4_LOCKED_v1.md
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
GEO_STORE = SINA / "forge-geopolitical-legal-v4.json"
GEO_RECEIPT = SINA / "forge-geopolitical-legal-latest-v4.json"
SCHEMA = "forge-geopolitical-legal-v4"
GEO_VERSION = "4.0.0"

NATION_LEGAL_SYSTEMS: dict[str, dict[str, Any]] = {
    "nation-sourcea": {
        "name": "SourceA Mac Control Plane",
        "strictness": 0.85,
        "constitution": "controlled_automation",
        "allowed_cross_border": ["read_file", "list_files", "search_code"],
        "jurisdiction": "mac_control_plane",
    },
    "nation-cloudforge": {
        "name": "Cloud Forge Railway",
        "strictness": 0.7,
        "constitution": "execution_body",
        "allowed_cross_border": ["deploy", "run_shell", "write_file", "read_file"],
        "jurisdiction": "cloud_execution",
    },
    "nation-labs": {
        "name": "Labs Sandbox",
        "strictness": 0.5,
        "constitution": "experimentation",
        "allowed_cross_border": ["read_file", "list_files", "patch_file"],
        "jurisdiction": "labs_sandbox",
    },
}

SEED_TREATIES: list[dict[str, Any]] = [
    {
        "id": "treaty-sourcea-cloudforge-v1",
        "parties": ["nation-sourcea", "nation-cloudforge"],
        "terms": ["mutual_compute_access", "shared_precedent_recognition", "deploy_handoff"],
        "allowed_actions": ["read_file", "list_files", "deploy", "search_code", "write_file"],
        "status": "active",
    },
    {
        "id": "treaty-cloudforge-labs-v1",
        "parties": ["nation-cloudforge", "nation-labs"],
        "terms": ["sandbox_access", "experiment_export"],
        "allowed_actions": ["read_file", "list_files", "patch_file", "search_code"],
        "status": "active",
    },
]

AGENT_NATION_HINTS: dict[str, str] = {
    "planner-001": "nation-sourcea",
    "builder-001": "nation-sourcea",
    "critic-001": "nation-sourcea",
    "repair-001": "nation-sourcea",
    "optimizer-001": "nation-sourcea",
    "deployer-001": "nation-cloudforge",
    "lab-001": "nation-labs",
    "lab-builder-001": "nation-labs",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path: Path, data: Any) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _empty_geo() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": GEO_VERSION,
        "treaties": [dict(t) for t in SEED_TREATIES],
        "sanctions": [],
        "agent_nations": dict(AGENT_NATION_HINTS),
        "international_cases": [],
        "updated_at": _now(),
    }


def load_geo_legal() -> dict[str, Any]:
    doc = _load_json(GEO_STORE, _empty_geo())
    if not doc.get("treaties"):
        doc["treaties"] = [dict(t) for t in SEED_TREATIES]
    if not doc.get("agent_nations"):
        doc["agent_nations"] = dict(AGENT_NATION_HINTS)
    return doc


def save_geo_legal(doc: dict[str, Any]) -> dict[str, Any]:
    doc["updated_at"] = _now()
    _save_json(GEO_STORE, doc)
    return doc


def nation_for_agent(agent_id: str) -> str:
    doc = load_geo_legal()
    mapped = (doc.get("agent_nations") or {}).get(agent_id)
    if mapped:
        return mapped
    aid = (agent_id or "").lower()
    if "lab" in aid:
        return "nation-labs"
    if "cloud" in aid or "deploy" in aid:
        return "nation-cloudforge"
    return "nation-sourcea"


def infer_target_nation(*, action_type: str, payload: dict[str, Any]) -> str:
    if payload.get("cloud") or action_type == "deploy":
        return "nation-cloudforge"
    path = str(payload.get("path") or payload.get("workspace_path") or "").lower()
    if "labs" in path or "sandbox" in path:
        return "nation-labs"
    if payload.get("target_nation"):
        return str(payload["target_nation"])
    return nation_for_agent(str(payload.get("agent_id") or "builder-001"))


def get_nation_legal_system(nation_id: str) -> dict[str, Any]:
    sys = NATION_LEGAL_SYSTEMS.get(nation_id)
    if sys:
        return {"nation_id": nation_id, **sys}
    return {"nation_id": nation_id, "strictness": 0.5, "constitution": "default", "allowed_cross_border": []}


def _treaty_covers(home: str, target: str, action_type: str) -> dict[str, Any] | None:
    for treaty in load_geo_legal().get("treaties") or []:
        if treaty.get("status") != "active":
            continue
        parties = set(treaty.get("parties") or [])
        if home in parties and target in parties:
            allowed = treaty.get("allowed_actions") or []
            if action_type in allowed or "*" in allowed:
                return treaty
    return None


def _active_sanction(*, home: str, target: str) -> dict[str, Any] | None:
    for s in load_geo_legal().get("sanctions") or []:
        if s.get("status") != "active":
            continue
        issuer = str(s.get("issuer") or "")
        tgt = str(s.get("target") or "")
        if (issuer == home and tgt == target) or (issuer == target and tgt == home):
            return s
    return None


def check_geopolitical(
    *,
    agent_id: str,
    action_type: str,
    payload: dict[str, Any] | None = None,
    target_nation: str = "",
) -> dict[str, Any]:
    """Cross-border legal check — treaties, sanctions, jurisdiction."""
    payload = dict(payload or {})
    home = nation_for_agent(agent_id)
    target = target_nation or infer_target_nation(action_type=action_type, payload=payload)
    home_law = get_nation_legal_system(home)
    target_law = get_nation_legal_system(target)

    meta = {
        "home_nation": home,
        "target_nation": target,
        "cross_border": home != target,
        "home_law": home_law.get("constitution"),
        "target_law": target_law.get("constitution"),
    }

    if home == target:
        return {"status": "ALLOW", "reason": "domestic_jurisdiction", "geo": meta}

    sanction = _active_sanction(home=home, target=target)
    if sanction:
        return {
            "status": "DENY",
            "reason": "sanction_active",
            "sanction_id": sanction.get("id"),
            "geo": meta,
        }

    treaty = _treaty_covers(home, target, action_type)
    if treaty:
        meta["treaty_id"] = treaty.get("id")
        return {"status": "ALLOW", "reason": "treaty_permits", "geo": meta, "treaty": treaty.get("id")}

    if action_type in (home_law.get("allowed_cross_border") or []):
        return {"status": "ALLOW", "reason": "unilateral_cross_border_allow", "geo": meta}

    return {
        "status": "DENY",
        "reason": "no_treaty_coverage",
        "geo": meta,
    }


def sign_treaty(
    *,
    party_a: str,
    party_b: str,
    terms: list[str],
    allowed_actions: list[str] | None = None,
) -> dict[str, Any]:
    doc = load_geo_legal()
    treaty = {
        "id": f"treaty-{uuid.uuid4().hex[:10]}",
        "parties": sorted([party_a, party_b]),
        "terms": terms,
        "allowed_actions": allowed_actions or ["read_file", "list_files"],
        "status": "active",
        "signed_at": _now(),
    }
    doc["treaties"] = (doc.get("treaties") or []) + [treaty]
    save_geo_legal(doc)
    return {"ok": True, "treaty": treaty}


def impose_sanction(
    *,
    issuer: str,
    target: str,
    reason: str,
    restrictions: list[str] | None = None,
    severity: float = 0.5,
) -> dict[str, Any]:
    doc = load_geo_legal()
    row = {
        "id": f"sanction-{uuid.uuid4().hex[:10]}",
        "issuer": issuer,
        "target": target,
        "reason": reason,
        "restrictions": restrictions or ["deny_deploy", "block_cross_border_credits"],
        "severity": round(severity, 3),
        "status": "active",
        "at": _now(),
    }
    doc["sanctions"] = (doc.get("sanctions") or []) + [row]
    save_geo_legal(doc)
    return {"ok": True, "sanction": row}


def lift_sanction(sanction_id: str) -> dict[str, Any]:
    doc = load_geo_legal()
    found = False
    for s in doc.get("sanctions") or []:
        if s.get("id") == sanction_id:
            s["status"] = "lifted"
            s["lifted_at"] = _now()
            found = True
    if found:
        save_geo_legal(doc)
    return {"ok": found, "sanction_id": sanction_id}


def international_court(
    *,
    agent_id: str,
    action_type: str,
    payload: dict[str, Any],
    violation: str,
    geo_check: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Cross-border dispute resolution — v3 legal + treaty/precedent influence."""
    from forge_governance_legal_v3 import arbitrate, create_case  # noqa: WPS433

    checks = [
        {"status": "ALLOW", "reason": "domestic_permission"},
        {"status": "DENY", "reason": violation},
        geo_check,
    ]
    case = create_case(
        action={"action_type": action_type, "payload": payload, "geo": geo_check.get("geo")},
        agent_id=agent_id,
        violation=violation,
        checks=checks,
        conflict=True,
    )
    case["international"] = True
    case["home_nation"] = geo_check.get("geo", {}).get("home_nation")
    case["target_nation"] = geo_check.get("geo", {}).get("target_nation")
    judgment = arbitrate(case, dry_run=dry_run)

    treaty_id = geo_check.get("treaty") or geo_check.get("geo", {}).get("treaty_id")
    if treaty_id and str(judgment.get("verdict")) == "GUILTY":
        judgment["verdict"] = "PARTIAL"
        judgment["reasoning"] = (judgment.get("reasoning") or "") + f"; treaty {treaty_id} moderates penalty"

    doc = load_geo_legal()
    intl_row = {
        "case_id": case.get("id"),
        "judgment_id": judgment.get("caseId"),
        "verdict": judgment.get("verdict"),
        "home_nation": case.get("home_nation"),
        "target_nation": case.get("target_nation"),
        "at": _now(),
    }
    doc["international_cases"] = ((doc.get("international_cases") or []) + [intl_row])[-200:]
    save_geo_legal(doc)

    allow = str(judgment.get("verdict")) == "NOT_GUILTY"
    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": GEO_VERSION,
        "case": case,
        "judgment": judgment,
        "governance_status": "ALLOW" if allow else "DENY",
        "international": True,
        "at": _now(),
    }
    GEO_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def process_cross_border_violation(
    *,
    agent_id: str,
    agent_role: str,
    action_type: str,
    payload: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Full cross-border flow when geo check fails."""
    geo = check_geopolitical(agent_id=agent_id, action_type=action_type, payload=payload)
    if geo.get("status") == "ALLOW":
        return {"ok": True, "schema": SCHEMA, "governance_status": "ALLOW", "geo": geo}
    return international_court(
        agent_id=agent_id,
        action_type=action_type,
        payload=payload,
        violation=str(geo.get("reason") or "geo_denied"),
        geo_check=geo,
        dry_run=dry_run,
    )


def geo_legal_tick(*, dry_run: bool = True) -> dict[str, Any]:
    """Geopolitical legal tick — sync world nations, decay sanctions, diplomacy."""
    from forge_world_state_v1 import load_world, save_world, world_tick  # noqa: WPS433

    world = load_world()
    doc = load_geo_legal()
    nations = world.get("nations") or {}
    synced = 0
    for nid in nations:
        if nid in NATION_LEGAL_SYSTEMS:
            synced += 1

    decayed = 0
    for s in doc.get("sanctions") or []:
        if s.get("status") == "active" and float(s.get("severity") or 0) < 0.2:
            s["status"] = "expired"
            decayed += 1

    diplomacy_edges = []
    for treaty in doc.get("treaties") or []:
        if treaty.get("status") == "active":
            parties = treaty.get("parties") or []
            if len(parties) >= 2:
                diplomacy_edges.append({"from": parties[0], "to": parties[1], "type": "treaty", "id": treaty.get("id")})

    world["diplomacy_graph"] = {"edges": diplomacy_edges}
    save_world(world)
    save_geo_legal(doc)

    wt = world_tick(dry_run=dry_run)
    out = {
        "ok": True,
        "schema": "forge-geopolitical-legal-tick-v4",
        "version": GEO_VERSION,
        "dry_run": dry_run,
        "nations_synced": synced,
        "treaties_active": sum(1 for t in doc.get("treaties") or [] if t.get("status") == "active"),
        "sanctions_active": sum(1 for s in doc.get("sanctions") or [] if s.get("status") == "active"),
        "sanctions_decayed": decayed,
        "world_tick": wt,
        "at": _now(),
    }
    GEO_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def seed_geo_legal() -> dict[str, Any]:
    """Idempotent seed — treaties + agent nations."""
    doc = load_geo_legal()
    if len(doc.get("treaties") or []) >= len(SEED_TREATIES):
        return {"ok": True, "seeded": False, "reason": "already_seeded"}
    doc = _empty_geo()
    save_geo_legal(doc)
    return {"ok": True, "seeded": True, "treaties": len(doc.get("treaties") or [])}
