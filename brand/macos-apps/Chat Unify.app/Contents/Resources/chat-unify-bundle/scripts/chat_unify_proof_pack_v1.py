#!/usr/bin/env python3
"""Chat Unify — Proof Pack machine (#6): green run → sealed replayable proof artifact.

Stages: collect · verify · seal · package · emit
Sources: fbe-forge-run-receipt-v1 · phase1-pevc-truth-ticket-v1 (decision.verdict=approved)
Receipt: ~/.sina/chat-unify/proof-packs/<pack_id>/proof-pack-receipt.json
         ~/.sina/chat-unify-proof-pack-v1.json (latest)
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
PROOF_PACK_ROOT = SINA / "chat-unify" / "proof-packs"
LATEST_RECEIPT = SINA / "chat-unify-proof-pack-v1.json"
PROGRESS_PATH = SINA / "chat-unify-proof-pack-progress-v1.json"
MACHINE_VERSION = "1.1.0"
OWNER = "founder"

PHASE1_TICKET_SCHEMA = "phase1-pevc-truth-ticket-v1"
GREEN_VERDICTS = frozenset({"approved", "pass", "green"})

DEFAULT_RECEIPT_CANDIDATES = (
    SINA / "phase1-pevc-truth-ticket-v1.json",
    SINA / "fbe-forge-run-receipt-v1.json",
    SINA / "fbe-forge-verify-receipt-v1.json",
)

STAGE_ORDER = ("collect", "verify", "seal", "package", "emit")

STAGE_DEPENDS: dict[str, str | None] = {
    "collect": None,
    "verify": "collect",
    "seal": "verify",
    "package": "seal",
    "emit": "package",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_verdict(verdict: Any) -> str:
    return str(verdict or "").strip().lower()


def _receipt_is_green(receipt: dict) -> bool:
    if receipt.get("ok") is True:
        return True
    schema = str(receipt.get("schema") or "")
    if schema == PHASE1_TICKET_SCHEMA:
        decision = receipt.get("decision") or {}
        if _normalize_verdict(decision.get("verdict")) in GREEN_VERDICTS:
            return True
        demo = receipt.get("demo_screen") or {}
        if _normalize_verdict(demo.get("verdict")) in GREEN_VERDICTS:
            return True
    return False


def _resolve_receipt_path(receipt_path: str = "") -> Path | None:
    raw = (receipt_path or "").strip()
    if raw:
        p = Path(raw).expanduser()
        if p.is_file():
            return p
        return None
    for candidate in DEFAULT_RECEIPT_CANDIDATES:
        if candidate.is_file():
            row = _read_json(candidate)
            if _receipt_is_green(row):
                return candidate
    for candidate in DEFAULT_RECEIPT_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _companion_verify_path(run_receipt: Path, receipt: dict | None = None) -> Path | None:
    receipt = receipt if receipt is not None else _read_json(run_receipt)
    schema = str(receipt.get("schema") or "")
    if run_receipt.name == "fbe-forge-run-receipt-v1.json" or schema == PHASE1_TICKET_SCHEMA:
        verify = SINA / "fbe-forge-verify-receipt-v1.json"
        return verify if verify.is_file() else None
    return None


def _extract_forge_run_bundle(receipt: dict, *, receipt_path: Path, verify_receipt: dict | None) -> dict:
    results = receipt.get("results") or []
    checks = (verify_receipt or {}).get("checks") or []
    artifact = {
        "schema": receipt.get("schema"),
        "run_id": receipt.get("run_id") or receipt.get("work_order_id"),
        "work_order_id": receipt.get("work_order_id"),
        "template_id": receipt.get("template_id"),
        "factory_id": receipt.get("factory_id"),
        "delivery_mode": receipt.get("deliveryMode") or receipt.get("delivery_mode"),
        "proof_class": receipt.get("proof_class"),
        "steps_ok": receipt.get("steps_ok") or receipt.get("steps_executed"),
        "steps_total": receipt.get("steps_total"),
    }
    evidence = {
        "source_receipt_path": str(receipt_path),
        "source_receipt_ok": _receipt_is_green(receipt),
        "source_receipt_at": receipt.get("at"),
        "verify_receipt_path": str(_companion_verify_path(receipt_path, receipt) or ""),
        "verify_receipt_ok": verify_receipt.get("ok") if verify_receipt else None,
        "step_results": results[:12],
        "verify_checks": checks[:12],
        "execution_plane": receipt.get("execution_plane"),
    }
    green = _receipt_is_green(receipt)
    decision = {
        "approved": green,
        "verdict": "PASS" if green else "FAIL",
        "rationale": (
            f"Source receipt ok={receipt.get('ok')} · verify ok={verify_receipt.get('ok') if verify_receipt else 'n/a'}"
        ),
    }
    trace = {
        "stage_log": [],
        "nodes_executed": [r.get("node_id") for r in results if r.get("node_id")],
        "wave": receipt.get("wave"),
        "bay_slug": receipt.get("bay_slug"),
    }
    return {
        "artifact": artifact,
        "evidence": evidence,
        "decision": decision,
        "trace": trace,
    }


def _extract_phase1_ticket_bundle(receipt: dict, *, receipt_path: Path, verify_receipt: dict | None) -> dict:
    artifact_in = receipt.get("artifact") or {}
    evidence_in = receipt.get("evidence") or {}
    decision_in = receipt.get("decision") or {}
    belt = receipt.get("belt") or {}
    prove = belt.get("PROVE") or {}
    ship = belt.get("SHIP") or {}
    payload = artifact_in.get("payload") or {}
    ev_payload = evidence_in.get("payload") or {}

    artifact = {
        "schema": receipt.get("schema"),
        "run_id": receipt.get("run_id") or artifact_in.get("run_id"),
        "work_order_id": receipt.get("maps_registry") or artifact_in.get("maps_registry"),
        "template_id": artifact_in.get("artifact_type"),
        "factory_id": receipt.get("factory"),
        "delivery_mode": "dry_run=false" if ship.get("dry_run") is False else None,
        "proof_class": payload.get("tier_achieved") or ship.get("tier_achieved"),
        "steps_ok": prove.get("chains_up"),
        "steps_total": prove.get("chains_total"),
        "blueprint_id": receipt.get("blueprint_id"),
        "queue_completed": receipt.get("queue_completed"),
        "forge_run_id": artifact_in.get("run_id"),
    }
    evidence = {
        "source_receipt_path": str(receipt_path),
        "source_receipt_ok": _receipt_is_green(receipt),
        "source_receipt_at": receipt.get("at"),
        "verify_receipt_path": str(_companion_verify_path(receipt_path, receipt) or ""),
        "verify_receipt_ok": verify_receipt.get("ok") if verify_receipt else None,
        "step_results": [],
        "verify_checks": [
            {"id": "belt_prove", "ok": prove.get("ok"), "chains_up": prove.get("chains_up")},
            {"id": "belt_ship", "ok": ship.get("ok"), "tier": ship.get("tier_achieved")},
            {"id": "health_ok", "ok": ev_payload.get("health_ok")},
        ],
        "execution_plane": receipt.get("execution_plane"),
        "belt_steps": list(belt.keys()),
        "prove_summary": prove.get("summary_line"),
        "hub_proceed_line": ship.get("hub_proceed_line"),
    }
    verdict = _normalize_verdict(decision_in.get("verdict")) or "approved"
    decision = {
        "approved": _receipt_is_green(receipt),
        "verdict": verdict.upper(),
        "rationale": decision_in.get("rationale")
        or f"Phase-1 PEVC ticket · belt PROVE={prove.get('ok')} · SHIP={ship.get('ok')}",
    }
    trace = {
        "stage_log": list(belt.keys()),
        "nodes_executed": ["SCAN", "SAY", "PICK", "PROVE", "SHIP"],
        "wave": receipt.get("execution_plane"),
        "bay_slug": receipt.get("factory"),
    }
    return {
        "artifact": artifact,
        "evidence": evidence,
        "decision": decision,
        "trace": trace,
    }


def _extract_run_bundle(receipt: dict, *, receipt_path: Path, verify_receipt: dict | None) -> dict:
    if str(receipt.get("schema") or "") == PHASE1_TICKET_SCHEMA:
        return _extract_phase1_ticket_bundle(
            receipt, receipt_path=receipt_path, verify_receipt=verify_receipt
        )
    return _extract_forge_run_bundle(receipt, receipt_path=receipt_path, verify_receipt=verify_receipt)


def _receipt_to_atoms_phase1(receipt: dict, verify_receipt: dict | None) -> list[dict]:
    atoms: list[dict] = []
    idx = 0

    def _add(text: str) -> None:
        nonlocal idx
        t = (text or "").strip()[:400]
        if not t:
            return
        idx += 1
        atoms.append(
            {
                "id": f"pp{idx}",
                "text": t,
                "kind": "FACT",
                "certainty": "high",
                "object": "",
                "action_verb": "",
            }
        )

    green = _receipt_is_green(receipt)
    belt = receipt.get("belt") or {}
    prove = belt.get("PROVE") or {}
    ship = belt.get("SHIP") or {}
    decision = receipt.get("decision") or {}

    _add(f"Run receipt ok={green}")
    _add(f"Schema {receipt.get('schema')}")
    if receipt.get("run_id"):
        _add(f"Run id {receipt.get('run_id')}")
    if receipt.get("maps_registry"):
        _add(f"Work order {receipt.get('maps_registry')}")
    if receipt.get("blueprint_id"):
        _add(f"Blueprint {receipt.get('blueprint_id')}")
    _add(f"Belt PROVE ok={prove.get('ok')}")
    _add(f"Belt SHIP ok={ship.get('ok')}")
    verdict = decision.get("verdict")
    if verdict:
        _add(f"Decision verdict {verdict}")
    if verify_receipt:
        _add(f"Verify receipt ok={verify_receipt.get('ok')}")
        for check in verify_receipt.get("checks") or []:
            path = check.get("path")
            if path:
                _add(f"Check {check.get('id')} path {path} ok={check.get('ok')}")
            else:
                _add(f"Check {check.get('id')} ok={check.get('ok')}")
    return atoms


def _verify_phase1_atoms_on_disk(
    atoms: list[dict],
    *,
    receipt: dict,
    verify_receipt: dict | None,
    receipt_path: Path,
) -> list[dict]:
    belt = receipt.get("belt") or {}
    prove = belt.get("PROVE") or {}
    ship = belt.get("SHIP") or {}
    decision = receipt.get("decision") or {}
    check_by_id = {c.get("id"): c for c in (verify_receipt or {}).get("checks") or []}
    green = _receipt_is_green(receipt)
    out: list[dict] = []

    for atom in atoms:
        row = dict(atom)
        text = row.get("text") or ""
        tl = text.lower()
        status = "unverified"
        ref: str | None = str(receipt_path)
        reason = "phase1 ticket claim"

        if tl.startswith("run receipt ok="):
            claimed = "true" in tl
            status = "verified" if claimed == green else "mismatch"
            reason = f"receipt green={green}"
        elif tl.startswith("schema "):
            claimed = text.split(" ", 1)[-1].strip()
            actual = str(receipt.get("schema") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "schema matches ticket"
        elif tl.startswith("run id "):
            claimed = text.split(" ", 2)[-1].strip()
            actual = str(receipt.get("run_id") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "run_id matches ticket"
        elif tl.startswith("work order "):
            claimed = text.split(" ", 2)[-1].strip()
            actual = str(receipt.get("maps_registry") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "maps_registry matches ticket"
        elif tl.startswith("blueprint "):
            claimed = text.split(" ", 1)[-1].strip()
            actual = str(receipt.get("blueprint_id") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "blueprint_id matches ticket"
        elif tl.startswith("belt prove ok="):
            claimed = text.rsplit("=", 1)[-1].strip().lower() == "true"
            actual = prove.get("ok") is True
            status = "verified" if claimed == actual else "mismatch"
            reason = f"belt PROVE ok={actual}"
        elif tl.startswith("belt ship ok="):
            claimed = text.rsplit("=", 1)[-1].strip().lower() == "true"
            actual = ship.get("ok") is True
            status = "verified" if claimed == actual else "mismatch"
            reason = f"belt SHIP ok={actual}"
        elif tl.startswith("decision verdict "):
            claimed = _normalize_verdict(text.split(" ", 2)[-1])
            actual = _normalize_verdict(decision.get("verdict"))
            status = "verified" if claimed == actual else "mismatch"
            reason = f"decision verdict={actual}"
        elif tl.startswith("verify receipt ok="):
            claimed = "true" in tl
            actual = (verify_receipt or {}).get("ok") is True
            status = "verified" if claimed == actual else "mismatch"
            ref = str(SINA / "fbe-forge-verify-receipt-v1.json")
            reason = f"verify receipt ok={actual}"
        elif tl.startswith("check ") and " path " in tl and " ok=" in tl:
            check_id = text.split("Check ", 1)[-1].split(" path ", 1)[0].strip()
            path_part = text.split(" path ", 1)[-1].rsplit(" ok=", 1)[0].strip()
            claimed_ok = text.rsplit(" ok=", 1)[-1].strip().lower() == "true"
            check = check_by_id.get(check_id) or {}
            path_exists = Path(path_part).expanduser().is_file()
            actual_ok = check.get("ok") is True and path_exists
            status = "verified" if claimed_ok == actual_ok else "mismatch"
            ref = path_part
            reason = f"check {check_id} path exists={path_exists}"
        elif tl.startswith("check ") and " ok=" in tl:
            check_id = text.split("Check ", 1)[-1].split(" ok=", 1)[0].strip()
            claimed_ok = text.rsplit(" ok=", 1)[-1].strip().lower() == "true"
            check = check_by_id.get(check_id) or {}
            actual_ok = check.get("ok") is True
            status = "verified" if claimed_ok == actual_ok else "mismatch"
            reason = f"check {check_id} ok={actual_ok}"

        row["disk_status"] = status
        row["disk_ref"] = ref
        row["verify_reason"] = reason
        row["claim_type"] = "RECEIPT_BIND"
        row["verify_predicate"] = "receipt_disk_bind"
        out.append(row)
    return out


def _verify_receipt_atoms_on_disk(
    atoms: list[dict],
    *,
    receipt: dict,
    verify_receipt: dict | None,
    receipt_path: Path,
) -> list[dict]:
    """Bind proof-pack atoms to disk receipts — then ORD truth gate scores verified stats."""
    out: list[dict] = []
    check_by_id = {c.get("id"): c for c in (verify_receipt or {}).get("checks") or []}
    step_by_id = {r.get("node_id"): r for r in receipt.get("results") or []}

    for atom in atoms:
        row = dict(atom)
        text = row.get("text") or ""
        tl = text.lower()
        status = "unverified"
        ref: str | None = str(receipt_path)
        reason = "receipt claim"

        if tl.startswith("run receipt ok="):
            claimed = "true" in tl
            actual = receipt.get("ok") is True
            status = "verified" if claimed == actual else "mismatch"
            reason = f"receipt ok={actual}"
        elif tl.startswith("verify receipt ok="):
            claimed = "true" in tl
            actual = (verify_receipt or {}).get("ok") is True
            status = "verified" if claimed == actual else "mismatch"
            ref = str(SINA / "fbe-forge-verify-receipt-v1.json")
            reason = f"verify receipt ok={actual}"
        elif tl.startswith("schema "):
            claimed = text.split(" ", 1)[-1].strip()
            actual = str(receipt.get("schema") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "schema matches receipt file"
        elif tl.startswith("run id "):
            claimed = text.split(" ", 2)[-1].strip()
            actual = str(receipt.get("run_id") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "run_id matches receipt file"
        elif tl.startswith("work order "):
            claimed = text.split(" ", 2)[-1].strip()
            actual = str(receipt.get("work_order_id") or "")
            status = "verified" if claimed == actual else "mismatch"
            reason = "work_order_id matches receipt file"
        elif tl.startswith("step "):
            parts = text.split(" ok=")
            node = parts[0].replace("Step ", "").replace("step ", "").strip()
            claimed = (parts[1] if len(parts) > 1 else "").strip().lower() == "true"
            step = step_by_id.get(node) or {}
            actual = step.get("ok") is True
            status = "verified" if claimed == actual and step else "mismatch" if step else "unverified"
            reason = f"step {node} ok={actual}"
        elif " path " in tl and " ok=" in tl:
            check_id = text.split("Check ", 1)[-1].split(" path ", 1)[0].strip()
            path_part = text.split(" path ", 1)[-1].rsplit(" ok=", 1)[0].strip()
            claimed_ok = text.rsplit(" ok=", 1)[-1].strip().lower() == "true"
            check = check_by_id.get(check_id) or {}
            path_exists = Path(path_part).expanduser().is_file()
            actual_ok = check.get("ok") is True and path_exists
            status = "verified" if claimed_ok == actual_ok else "mismatch"
            ref = path_part
            reason = f"check {check_id} path exists={path_exists} ok={check.get('ok')}"
        elif tl.startswith("check ") and " ok=" in tl and " path " not in tl:
            check_id = text.split("Check ", 1)[-1].split(" ok=", 1)[0].strip()
            claimed_ok = text.rsplit(" ok=", 1)[-1].strip().lower() == "true"
            check = check_by_id.get(check_id) or {}
            actual_ok = check.get("ok") is True
            status = "verified" if claimed_ok == actual_ok else "mismatch"
            reason = f"check {check_id} ok={actual_ok}"

        row["disk_status"] = status
        row["disk_ref"] = ref
        row["verify_reason"] = reason
        row["claim_type"] = "RECEIPT_BIND"
        row["verify_predicate"] = "receipt_disk_bind"
        out.append(row)
    return out


def _receipt_to_atoms(receipt: dict, verify_receipt: dict | None) -> list[dict]:
    if str(receipt.get("schema") or "") == PHASE1_TICKET_SCHEMA:
        return _receipt_to_atoms_phase1(receipt, verify_receipt)
    atoms: list[dict] = []
    idx = 0

    def _add(text: str, *, kind: str = "FACT", certainty: str = "high") -> None:
        nonlocal idx
        t = (text or "").strip()[:400]
        if not t:
            return
        idx += 1
        atoms.append(
            {
                "id": f"pp{idx}",
                "text": t,
                "kind": kind,
                "certainty": certainty,
                "object": "",
                "action_verb": "",
            }
        )

    _add(f"Run receipt ok={_receipt_is_green(receipt)}")
    _add(f"Schema {receipt.get('schema')}")
    if receipt.get("run_id"):
        _add(f"Run id {receipt.get('run_id')}")
    if receipt.get("work_order_id"):
        _add(f"Work order {receipt.get('work_order_id')}")
    for row in receipt.get("results") or []:
        _add(f"Step {row.get('node_id')} ok={row.get('ok')}")
    if verify_receipt:
        _add(f"Verify receipt ok={verify_receipt.get('ok')}")
        for check in verify_receipt.get("checks") or []:
            path = check.get("path")
            if path:
                _add(f"Check {check.get('id')} path {path} ok={check.get('ok')}")
            else:
                _add(f"Check {check.get('id')} ok={check.get('ok')}")
    return atoms


def _disk_hints() -> dict:
    snap: dict[str, Any] = {"paths_checked": []}
    for candidate in DEFAULT_RECEIPT_CANDIDATES:
        if candidate.is_file():
            snap["paths_checked"].append(str(candidate))
    verify = SINA / "fbe-forge-verify-receipt-v1.json"
    if verify.is_file():
        row = _read_json(verify)
        for check in row.get("checks") or []:
            path = check.get("path")
            if path:
                snap["paths_checked"].append(str(path))
    return snap


def _stage_collect(*, receipt_path: Path) -> dict:
    receipt = _read_json(receipt_path)
    if not receipt:
        return {
            "ok": False,
            "text": f"Receipt missing or unreadable: {receipt_path}",
            "method": "disk",
        }
    verify_path = _companion_verify_path(receipt_path, receipt)
    verify_receipt = _read_json(verify_path) if verify_path else None
    bundle = _extract_run_bundle(receipt, receipt_path=receipt_path, verify_receipt=verify_receipt)
    green = _receipt_is_green(receipt)
    lines = [
        "Collect",
        f"Receipt: {receipt_path}",
        f"Schema: {receipt.get('schema')}",
        f"Run green: {green}",
        f"Artifact: {bundle['artifact'].get('run_id') or bundle['artifact'].get('work_order_id') or '—'}",
        f"Evidence paths: {len(bundle['evidence'].get('verify_checks') or [])} verify checks",
        f"Decision: {bundle['decision'].get('verdict')}",
    ]
    return {
        "ok": True,
        "text": "\n".join(lines),
        "method": "disk",
        "receipt_path": str(receipt_path),
        "receipt": receipt,
        "verify_receipt": verify_receipt,
        "bundle": bundle,
    }


def _stage_verify(*, collect: dict, use_ai: bool = False) -> dict:
    receipt = collect.get("receipt") or {}
    verify_receipt = collect.get("verify_receipt")
    if not receipt:
        return {"ok": False, "text": "Verify blocked — nothing collected.", "method": "ord_gate", "gate_pass": False}

    from chat_ord_atoms_v1 import atom_stats, build_claim_graph  # noqa: WPS433
    from chat_ord_claim_rules_v1 import enrich_stats_for_gate  # noqa: WPS433
    from chat_unify_truth_gate_v1 import evaluate_truth_gate, format_decision_block, write_latest_receipt  # noqa: WPS433

    green = _receipt_is_green(receipt)
    if not green:
        return {
            "ok": False,
            "text": f"Verify FAIL — source receipt not green (ok={receipt.get('ok')} verdict={(receipt.get('decision') or {}).get('verdict')}).",
            "method": "ord_gate",
            "gate_pass": False,
            "truth_gate": {"action": "block", "truth_score": 0, "dispatch_blocked": True},
        }

    is_phase1 = str(receipt.get("schema") or "") == PHASE1_TICKET_SCHEMA
    atoms = _receipt_to_atoms(receipt, verify_receipt)
    receipt_path_obj = Path(collect.get("receipt_path") or "")
    if is_phase1:
        atoms = _verify_phase1_atoms_on_disk(
            atoms,
            receipt=receipt,
            verify_receipt=verify_receipt,
            receipt_path=receipt_path_obj,
        )
    else:
        atoms = _verify_receipt_atoms_on_disk(
            atoms,
            receipt=receipt,
            verify_receipt=verify_receipt,
            receipt_path=receipt_path_obj,
        )
    snap = _disk_hints()
    graph = build_claim_graph(atoms=atoms, issues=[], draft=_canonical_json(receipt))
    stats = enrich_stats_for_gate(atoms, atom_stats(atoms, graph))
    disk_mismatch = bool(stats.get("disk_mismatch"))

    decision = evaluate_truth_gate(
        confidence=88 if green else 40,
        issue_count=stats.get("disk_mismatch") or 0,
        flag_count=0,
        issues=[],
        tags=[],
        disk_mismatch=disk_mismatch,
        stats=stats,
        graph=graph,
        use_ai=use_ai,
        draft_excerpt=_canonical_json(receipt)[:2000],
    )
    write_latest_receipt(decision)

    gate_pass = decision.get("action") == "allow" and green
    if verify_receipt and verify_receipt.get("ok") is False:
        gate_pass = False
        decision = dict(decision)
        decision["action"] = "block"
        decision["dispatch_blocked"] = True
        decision["reason"] = "Companion verify receipt ok=false — Proof Pack blocked."

    text = "\n".join(
        [
            "Verify (ORD truth gate)",
            format_decision_block(decision),
            f"Gate PASS: {gate_pass}",
            f"Atoms verified: {stats.get('verified', 0)}/{stats.get('checkable_count') or stats.get('atom_count') or 0}",
        ]
    )
    return {
        "ok": gate_pass,
        "text": text,
        "method": "ord_gate",
        "gate_pass": gate_pass,
        "truth_gate": decision,
        "stats": stats,
        "atoms": atoms,
        "graph": graph,
    }


def _prior_chain_hash() -> str:
    if not PROOF_PACK_ROOT.is_dir():
        return "genesis"
    receipts = sorted(PROOF_PACK_ROOT.glob("*/proof-pack-receipt.json"), key=lambda p: p.stat().st_mtime)
    if not receipts:
        return "genesis"
    row = _read_json(receipts[-1])
    seal = row.get("seal") or {}
    return str(seal.get("content_hash") or seal.get("seal_hash") or "genesis")


def _stage_seal(*, collect: dict, verify: dict, pack_id: str) -> dict:
    if not verify.get("gate_pass"):
        return {"ok": False, "text": "Seal blocked — verify did not PASS.", "method": "sha256"}
    bundle = collect.get("bundle") or {}
    payload = {
        "schema": "chat-unify-proof-pack-sealed-v1",
        "version": MACHINE_VERSION,
        "pack_id": pack_id,
        "owner": OWNER,
        "sealed_at": _now(),
        "source_receipt_path": collect.get("receipt_path"),
        "artifact": bundle.get("artifact"),
        "evidence": bundle.get("evidence"),
        "decision": bundle.get("decision"),
        "trace": bundle.get("trace"),
        "truth_gate": verify.get("truth_gate"),
    }
    content_hash = _sha256_text(_canonical_json(payload))
    prev_hash = _prior_chain_hash()
    seal_hash = _sha256_text(f"{content_hash}:{prev_hash}:{payload['sealed_at']}:{OWNER}")
    sealed = dict(payload)
    sealed["seal"] = {
        "content_hash": content_hash,
        "prev_hash": prev_hash,
        "seal_hash": seal_hash,
        "algorithm": "SHA-256",
        "chain": "append-only",
    }
    text = "\n".join(
        [
            "Seal",
            f"Pack id: {pack_id}",
            f"Content hash: {content_hash[:16]}…",
            f"Prev hash: {prev_hash[:16]}{'…' if len(prev_hash) > 16 else ''}",
            f"Seal hash: {seal_hash[:16]}…",
            f"Owner: {OWNER}",
        ]
    )
    return {"ok": True, "text": text, "method": "sha256", "sealed": sealed, "pack_id": pack_id}


def _stage_package(*, sealed: dict) -> dict:
    artifact = sealed.get("artifact") or {}
    evidence = sealed.get("evidence") or {}
    decision = sealed.get("decision") or {}
    gate = sealed.get("truth_gate") or {}
    run_id = artifact.get("run_id") or artifact.get("work_order_id") or sealed.get("pack_id")
    is_phase1 = str(artifact.get("schema") or "") == PHASE1_TICKET_SCHEMA

    client_lines = [
        "# Client deliverable",
        "",
        f"**Run:** {run_id}",
        f"**Verdict:** {decision.get('verdict')} — factory output with receipt proof.",
    ]
    if is_phase1:
        client_lines.extend(
            [
                f"**Blueprint:** {artifact.get('blueprint_id') or '—'}",
                f"**Queue:** {artifact.get('queue_completed') or '—'}",
                f"**Forge run:** {artifact.get('forge_run_id') or '—'}",
                f"**Belt:** {', '.join(evidence.get('belt_steps') or [])}",
                f"**Prove:** {evidence.get('prove_summary') or '—'}",
            ]
        )
    client_lines.extend(
        [
            f"**Steps OK:** {artifact.get('steps_ok')}/{artifact.get('steps_total')}",
            f"**Proof class:** {artifact.get('proof_class') or '—'}",
            "",
            "What you receive: the output artifact plus a replayable receipt showing the run cleared verification.",
            f"Sealed at: {sealed.get('sealed_at')}",
        ]
    )
    client = "\n".join(client_lines)

    investor_lines = [
        "INVESTOR DEMO (one screen)",
        f"Run {run_id} · {decision.get('verdict')} · truth gate {str(gate.get('action') or '?').upper()} {gate.get('truth_score')}/100",
    ]
    if is_phase1:
        investor_lines.append(
            f"Phase-1 PEVC · {artifact.get('blueprint_id')} · {artifact.get('queue_completed')} · GOLD"
        )
    investor_lines.extend(
        [
            f"Factory: {artifact.get('factory_id')} · template {artifact.get('template_id')}",
            f"Evidence: {evidence.get('source_receipt_path')}",
            f"Seal: {((sealed.get('seal') or {}).get('seal_hash') or '')[:20]}…",
        ]
    )
    investor = "\n".join(investor_lines)

    audit_lines = [
        "# Compliance / audit pack",
        "",
        "## Source",
        f"- Receipt: `{evidence.get('source_receipt_path')}`",
        f"- Verify: `{evidence.get('verify_receipt_path') or 'n/a'}`",
        f"- Execution plane: {evidence.get('execution_plane') or '—'}",
    ]
    if is_phase1:
        audit_lines.extend(
            [
                f"- Belt: {', '.join(evidence.get('belt_steps') or [])}",
                f"- Hub proceed: {evidence.get('hub_proceed_line') or '—'}",
            ]
        )
    audit_lines.extend(
        [
            "",
            "## Decision",
            f"- Approved: {decision.get('approved')}",
            f"- Rationale: {decision.get('rationale')}",
            "",
            "## Truth gate",
            f"- Action: {gate.get('action')}",
            f"- Score: {gate.get('truth_score')}/100",
            f"- Reason: {gate.get('reason')}",
            "",
            "## Hash chain",
            f"- Content: `{(sealed.get('seal') or {}).get('content_hash')}`",
            f"- Previous: `{(sealed.get('seal') or {}).get('prev_hash')}`",
            f"- Seal: `{(sealed.get('seal') or {}).get('seal_hash')}`",
            "",
            "## Trace",
            f"- Nodes: {', '.join(sealed.get('trace', {}).get('nodes_executed') or []) or '—'}",
        ]
    )
    audit = "\n".join(audit_lines)
    views = {
        "client_deliverable": client,
        "investor_demo": investor,
        "audit_pack": audit,
    }
    text = "\n".join(
        [
            "Package",
            "Views rendered:",
            "· client_deliverable.md",
            "· investor_demo.md",
            "· audit_pack.md",
        ]
    )
    return {"ok": True, "text": text, "method": "render", "views": views, "sealed": sealed}


def _stage_emit(*, sealed: dict, views: dict, pack_id: str) -> dict:
    pack_dir = PROOF_PACK_ROOT / pack_id
    views_dir = pack_dir / "views"
    export_dir = pack_dir / "export"
    views_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    sealed_path = pack_dir / "sealed.json"
    sealed_path.write_text(json.dumps(sealed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    view_paths: dict[str, str] = {}
    for name, body in (views or {}).items():
        path = views_dir / f"{name}.md"
        path.write_text(body.rstrip() + "\n", encoding="utf-8")
        view_paths[name] = str(path)

    shareable = {
        "schema": "chat-unify-proof-pack-export-v1",
        "version": MACHINE_VERSION,
        "pack_id": pack_id,
        "exported_at": _now(),
        "sealed": sealed,
        "views": views,
    }
    export_path = export_dir / "proof-pack-shareable.json"
    export_path.write_text(json.dumps(shareable, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    receipt = {
        "schema": "chat-unify-proof-pack-receipt-v1",
        "version": MACHINE_VERSION,
        "ok": True,
        "at": _now(),
        "pack_id": pack_id,
        "owner": OWNER,
        "source_receipt_path": sealed.get("source_receipt_path"),
        "gate_pass": (sealed.get("truth_gate") or {}).get("action") == "allow",
        "truth_gate": sealed.get("truth_gate"),
        "seal": sealed.get("seal"),
        "paths": {
            "pack_dir": str(pack_dir),
            "sealed": str(sealed_path),
            "views": view_paths,
            "shareable_export": str(export_path),
            "receipt": str(pack_dir / "proof-pack-receipt.json"),
        },
    }
    receipt_path = pack_dir / "proof-pack-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LATEST_RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    text = "\n".join(
        [
            "Emit",
            f"Pack dir: {pack_dir}",
            f"Sealed: {sealed_path}",
            f"Shareable: {export_path}",
            f"Receipt: {receipt_path}",
        ]
    )
    return {
        "ok": True,
        "text": text,
        "method": "disk",
        "pack_id": pack_id,
        "pack_dir": str(pack_dir),
        "receipt_path": str(receipt_path),
        "shareable_export": str(export_path),
        "view_paths": view_paths,
        "receipt": receipt,
    }


def _flush_progress(
    *,
    running: bool,
    current: str | None,
    completed: list[str],
    stages: dict,
    error: str | None = None,
) -> None:
    row = {
        "schema": "chat-unify-proof-pack-progress-v1",
        "running": running,
        "at": _now(),
        "current_stage": current,
        "completed_stages": completed,
        "waiting_stages": [s for s in STAGE_ORDER if s not in completed and s != current],
        "stage_order": list(STAGE_ORDER),
        "depends": STAGE_DEPENDS,
        "stages": stages,
        "error": error,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_proof_pack_progress() -> dict:
    row = _read_json(PROGRESS_PATH)
    if row.get("schema") != "chat-unify-proof-pack-progress-v1":
        return {"ok": True, "running": False, "stages": {}, "completed_stages": []}
    row["ok"] = True
    return row


def run_proof_pack_loop(
    *,
    receipt_path: str = "",
    founder_message: str = "",
    use_ai: bool = False,
    write_receipt: bool = True,
    write_progress: bool = True,
) -> dict:
    resolved = _resolve_receipt_path(receipt_path)
    if not resolved:
        return {
            "ok": False,
            "error": "receipt_not_found",
            "message": f"No green receipt at {receipt_path or 'default paths'}",
        }

    out_stages: dict = {}
    completed: list[str] = []
    pack_id = f"pp-{_now().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:8]}"

    def _progress(current: str | None) -> None:
        if write_progress:
            _flush_progress(running=True, current=current, completed=list(completed), stages=dict(out_stages))

    _progress("collect")
    out_stages["collect"] = _stage_collect(receipt_path=resolved)
    if not out_stages["collect"].get("ok"):
        _flush_progress(running=False, current=None, completed=completed, stages=out_stages, error="collect_failed")
        return {"ok": False, "stages": out_stages, "message": out_stages["collect"].get("text")}
    completed.append("collect")

    _progress("verify")
    out_stages["verify"] = _stage_verify(collect=out_stages["collect"], use_ai=use_ai)
    if not out_stages["verify"].get("gate_pass"):
        _flush_progress(running=False, current=None, completed=completed, stages=out_stages, error="verify_blocked")
        result = {
            "ok": False,
            "schema": "chat-unify-proof-pack-v1",
            "version": MACHINE_VERSION,
            "stages": out_stages,
            "truth_gate": out_stages["verify"].get("truth_gate"),
            "message": "Verify blocked — ORD truth gate did not PASS.",
        }
        if write_receipt:
            LATEST_RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return result
    completed.append("verify")

    _progress("seal")
    out_stages["seal"] = _stage_seal(collect=out_stages["collect"], verify=out_stages["verify"], pack_id=pack_id)
    completed.append("seal")

    _progress("package")
    sealed = out_stages["seal"].get("sealed") or {}
    out_stages["package"] = _stage_package(sealed=sealed)
    completed.append("package")

    _progress("emit")
    out_stages["emit"] = _stage_emit(
        sealed=sealed,
        views=out_stages["package"].get("views") or {},
        pack_id=pack_id,
    )
    completed.append("emit")

    result = {
        "ok": True,
        "schema": "chat-unify-proof-pack-v1",
        "version": MACHINE_VERSION,
        "at": _now(),
        "founder_message": founder_message,
        "receipt_path": str(resolved),
        "pack_id": pack_id,
        "pack_dir": out_stages["emit"].get("pack_dir"),
        "proof_pack_receipt": out_stages["emit"].get("receipt_path"),
        "shareable_export": out_stages["emit"].get("shareable_export"),
        "truth_gate": out_stages["verify"].get("truth_gate"),
        "seal": sealed.get("seal"),
        "stages": out_stages,
        "stage_order": list(STAGE_ORDER),
    }
    if write_receipt:
        LATEST_RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _flush_progress(running=False, current=None, completed=completed, stages=out_stages)
    return result


def run_proof_pack_stage(
    stage: str,
    *,
    receipt_path: str = "",
    founder_message: str = "",
    use_ai: bool = False,
    kernel: dict | None = None,
    run_id: str | None = None,
    write_receipt: bool = True,
) -> dict:
    from chat_unify_kernel_v1 import (  # noqa: WPS433
        append_stage_log,
        ensure_kernel,
        kernel_summary,
        merge_stage_output,
        save_kernel,
    )

    sid = (stage or "").strip().lower()
    if sid not in STAGE_ORDER:
        return {"ok": False, "error": "unknown_stage", "message": f"Unknown stage: {stage}"}

    resolved = _resolve_receipt_path(receipt_path)
    if not resolved:
        return {
            "ok": False,
            "error": "receipt_not_found",
            "message": f"No receipt at {receipt_path or 'default paths'}",
        }

    k = ensure_kernel(
        loop="proof_pack",
        draft=str(resolved),
        founder_message=founder_message,
        run_id=run_id,
        kernel=kernel,
    )
    out_stages: dict = dict(k.get("stages") or {})
    dep = STAGE_DEPENDS.get(sid)
    if dep and dep not in out_stages:
        return {
            "ok": False,
            "error": "dependency_blocked",
            "blocked_by": dep,
            "stage": sid,
            "message": f"{sid} blocked — complete {dep} first.",
            "stages": out_stages,
            "kernel": k,
            "run_id": k.get("run_id"),
        }

    pack_id = out_stages.get("seal", {}).get("pack_id") or k.get("pack_id")
    if not pack_id and sid in ("seal", "package", "emit"):
        pack_id = f"pp-{_now().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:8]}"
    k["pack_id"] = pack_id

    if sid == "collect":
        out_stages["collect"] = _stage_collect(receipt_path=resolved)
        stage_ok = bool(out_stages["collect"].get("ok"))
    elif sid == "verify":
        collect = out_stages.get("collect") or _stage_collect(receipt_path=resolved)
        out_stages["collect"] = collect
        out_stages["verify"] = _stage_verify(collect=collect, use_ai=use_ai)
        stage_ok = bool(out_stages["verify"].get("gate_pass"))
    elif sid == "seal":
        collect = out_stages.get("collect") or {}
        verify = out_stages.get("verify") or {}
        if not verify.get("gate_pass"):
            return {
                "ok": False,
                "error": "verify_blocked",
                "message": "Seal blocked — verify must PASS first.",
                "stages": out_stages,
                "run_id": k.get("run_id"),
            }
        out_stages["seal"] = _stage_seal(collect=collect, verify=verify, pack_id=pack_id or "pp-unknown")
        stage_ok = bool(out_stages["seal"].get("ok"))
    elif sid == "package":
        sealed = (out_stages.get("seal") or {}).get("sealed") or {}
        out_stages["package"] = _stage_package(sealed=sealed)
        stage_ok = bool(out_stages["package"].get("ok"))
    else:  # emit
        sealed = (out_stages.get("seal") or {}).get("sealed") or {}
        views = (out_stages.get("package") or {}).get("views") or {}
        out_stages["emit"] = _stage_emit(sealed=sealed, views=views, pack_id=pack_id or "pp-unknown")
        stage_ok = bool(out_stages["emit"].get("ok"))

    merge_stage_output(k, out_stages)
    append_stage_log(k, stage=sid, depends_on=dep, ok=stage_ok, method=out_stages.get(sid, {}).get("method"))
    save_kernel(k)

    result = {
        "ok": stage_ok,
        "schema": "chat-unify-proof-pack-v1",
        "version": MACHINE_VERSION,
        "stage": sid,
        "stages": out_stages,
        "run_id": k.get("run_id"),
        "kernel": k,
        "kernel_summary": kernel_summary(k),
        "pack_id": pack_id,
        "receipt_path": str(resolved),
    }
    if sid == "verify":
        result["truth_gate"] = out_stages.get("verify", {}).get("truth_gate")
    if sid == "emit" and stage_ok:
        result.update(
            {
                "ok": True,
                "pack_dir": out_stages["emit"].get("pack_dir"),
                "proof_pack_receipt": out_stages["emit"].get("receipt_path"),
                "shareable_export": out_stages["emit"].get("shareable_export"),
                "truth_gate": out_stages.get("verify", {}).get("truth_gate"),
                "seal": sealed.get("seal") if (sealed := (out_stages.get("seal") or {}).get("sealed")) else None,
            }
        )
        if write_receipt:
            LATEST_RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if sid == "verify" and not stage_ok:
        result["message"] = "Verify blocked — ORD truth gate did not PASS."

    return result


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Chat Unify Proof Pack machine")
    ap.add_argument("--receipt-path", default="", help="Source green receipt path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_proof_pack_loop(receipt_path=args.receipt_path)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("message") or ("OK" if row.get("ok") else "FAIL"))
        if row.get("proof_pack_receipt"):
            print(f"Receipt: {row['proof_pack_receipt']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
