#!/usr/bin/env python3
"""Single commit gate — intent → gatekeeper → spine → receipt.

Law: brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md

Usage:
  python3 scripts/commit_intent_v1.py --intent demo/enforcement/intent-allow.json --json
  python3 scripts/commit_intent_v1.py --intent demo/enforcement/intent-deny.json --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT_DIR = SINA / "receipts/enforcement"
COPILOT_RECEIPT_DIR = SINA / "demo-enforcement/receipts"
RECEIPT_LOG = RECEIPT_DIR / "receipts.jsonl"
COPILOT_RECEIPT_LOG = SINA / "demo-enforcement/receipt-log.jsonl"
LATEST_DEMO = RECEIPT_DIR / "latest-demo-receipt.json"
COPILOT_INTENTS = ROOT / "brain-os/demo/governance_demo_intents_v1.json"
ASSET_B_REGISTRY = ROOT / "data/asset-b-policy-pack-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(body: dict) -> str:
    stripped = {k: v for k, v in body.items() if k != "receipt_checksum"}
    raw = json.dumps(stripped, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def verify_receipt_checksum(rec: dict) -> bool:
    expected = rec.get("receipt_checksum")
    if not expected:
        return False
    return _checksum(rec) == expected


def _write_receipt(rec: dict, *, bind_spine: bool) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    rec = dict(rec)
    rec.pop("receipt_checksum", None)
    rec.pop("spine_event_id", None)
    rec.pop("spine_checksum", None)

    if bind_spine:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        LATEST_DEMO.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        spine_res = append_event(
            event_type="VALIDATOR_PASS",
            object_id=str(rec.get("object_id") or "ENFORCEMENT-DEMO"),
            object_kind="system",
            agent_id=str(rec.get("agent_id") or "commit_intent_v1"),
            law_id=str(rec.get("rule_id") or "ENFORCEMENT_6MO"),
            skill_id="commit_intent_v1",
            validator_set=["validate-enforcement-demo-v1.sh", "validate-universe-invariants-v1.sh"],
            affected_objects=[str(rec.get("object_id") or "ENFORCEMENT-DEMO")],
            gate="commit_intent",
            proof=str(LATEST_DEMO),
            payload={
                "intent_id": rec.get("intent_id"),
                "outcome": rec.get("outcome"),
                "action": rec.get("action"),
            },
        )
        if spine_res.get("ok"):
            ev = spine_res["event"]
            rec["spine_event_id"] = ev.get("event_id")
            rec["spine_checksum"] = ev.get("checksum")
            rec["proof_path"] = str(LATEST_DEMO)

    rec["receipt_checksum"] = _checksum(rec)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_DEMO.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    with RECEIPT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def _load_copilot_case(case: str) -> dict:
    data = json.loads(COPILOT_INTENTS.read_text(encoding="utf-8"))
    key = "block_case" if case == "block" else "allow_case"
    intent = dict(data.get(key) or {})
    intent["intent_id"] = f"copilot-{case}-{uuid.uuid4().hex[:8]}"
    intent["rule_id"] = "P-001"
    return intent


def _load_asset_b_intent(policy_key: str, case: str) -> tuple[dict, dict]:
    registry = json.loads(ASSET_B_REGISTRY.read_text(encoding="utf-8"))
    row = (registry.get("policies") or {}).get(policy_key)
    if not row:
        raise FileNotFoundError(f"asset-b policy missing: {policy_key}")
    policy_path = ROOT / str(row.get("path") or "")
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    intent_rel = (row.get("demo_intents") or {}).get(case)
    if not intent_rel:
        raise FileNotFoundError(f"asset-b intent missing: {policy_key}/{case}")
    intent_path = ROOT / str(intent_rel)
    intent = json.loads(intent_path.read_text(encoding="utf-8"))
    intent["intent_id"] = f"ab-{policy_key}-{case}-{uuid.uuid4().hex[:8]}"
    return intent, policy


def commit_asset_b_policy(policy_key: str, case: str, *, dry_run: bool = False) -> dict:
    """Asset B buyer policy demo — outreach / ops / creative."""
    sys.path.insert(0, str(SCRIPTS))
    from asset_b_policy_gate_v1 import evaluate  # noqa: WPS433

    intent, policy = _load_asset_b_intent(policy_key, case)
    gate = evaluate(intent, policy)
    intent_id = intent.get("intent_id")
    object_id = str(intent.get("object_id") or f"ASSET-B-{policy_key.upper()}-DEMO")
    policy_id = str(policy.get("policy_id") or policy_key)

    base = {
        "schema": "enforcement-action-receipt-v1",
        "receipt_id": f"RCP-{uuid.uuid4().hex[:12]}",
        "intent_id": intent_id,
        "action": str(intent.get("action") or policy.get("intent") or "execute"),
        "object_id": object_id,
        "rule_id": policy_id,
        "agent_id": str(intent.get("agent_id") or "asset_b_demo"),
        "policy_id": policy_id,
        "approval_ref": intent.get("approval_ref"),
        "demo_case": case,
        "asset_b_policy": policy_key,
        "gate_status": "PASS" if gate.get("safe_to_execute") else "DENY",
        "gate_reasons": [] if gate.get("safe_to_execute") else [gate.get("reason") or "policy DENY"],
        "created_at": _now(),
        "law": "docs/SOURCEA_ASSET_B_POLICY_PACK_LOCKED_v1.md",
    }

    if not gate.get("safe_to_execute"):
        base["outcome"] = "BLOCKED"
        receipt = _write_copilot_receipt(base, bind_spine=False)
        return {"ok": False, "blocked": True, "asset_b_gate": gate, "receipt": receipt}

    if dry_run:
        base["outcome"] = "DRY_RUN"
        base["evidence"] = "EXECUTE_STUB: asset-b policy applied (dry-run)"
        base["receipt_fields"] = (gate.get("receipt") or {}).get("include") or []
        return {"ok": True, "dry_run": True, "asset_b_gate": gate, "receipt_preview": base}

    base["outcome"] = "COMMITTED"
    base["status"] = "DONE"
    base["evidence"] = "EXECUTE_STUB: asset-b policy applied"
    base["receipt_fields"] = (gate.get("receipt") or {}).get("include") or []
    for field in base["receipt_fields"]:
        if field in intent and field not in base:
            base[field] = intent.get(field)
    receipt = _write_copilot_receipt(base, bind_spine=True)
    return {"ok": True, "asset_b_gate": gate, "receipt": receipt}


def commit_copilot_demo(case: str, *, dry_run: bool = False) -> dict:
    """Copilot wedge demo — governance_demo_gate only (no factory queue bypass)."""
    sys.path.insert(0, str(SCRIPTS))
    from governance_demo_gate_v1 import evaluate  # noqa: WPS433

    intent = _load_copilot_case(case)
    gate = evaluate(intent)
    intent_id = intent.get("intent_id")
    object_id = str(intent.get("object_id") or "NF-COPILOT-POLICY-DEMO")

    base = {
        "schema": "enforcement-action-receipt-v1",
        "receipt_id": f"RCP-{uuid.uuid4().hex[:12]}",
        "intent_id": intent_id,
        "action": str(intent.get("action") or "enable"),
        "object_id": object_id,
        "rule_id": "P-001",
        "agent_id": str(intent.get("agent_id") or "investor_demo"),
        "policy_id": intent.get("policy_id"),
        "approval_ref": intent.get("approval_ref"),
        "demo_case": case,
        "gate_status": "PASS" if gate.get("safe_to_execute") else "DENY",
        "gate_reasons": [] if gate.get("safe_to_execute") else [gate.get("reason") or "P-001 DENY"],
        "created_at": _now(),
        "law": "brain-os/demo/governance_demo_policy_v1.json",
    }

    if not gate.get("safe_to_execute"):
        base["outcome"] = "BLOCKED"
        receipt = _write_copilot_receipt(base, bind_spine=False)
        return {"ok": False, "blocked": True, "demo_gate": gate, "receipt": receipt}

    if dry_run:
        base["outcome"] = "DRY_RUN"
        base["evidence"] = "EXECUTE_STUB: policy applied (dry-run)"
        return {"ok": True, "dry_run": True, "demo_gate": gate, "receipt_preview": base}

    base["outcome"] = "COMMITTED"
    base["status"] = "DONE"
    base["evidence"] = "EXECUTE_STUB: policy applied"
    receipt = _write_copilot_receipt(base, bind_spine=True)
    return {"ok": True, "demo_gate": gate, "receipt": receipt}


def _write_copilot_receipt(rec: dict, *, bind_spine: bool) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    rec = dict(rec)
    rec.pop("receipt_checksum", None)
    rec.pop("spine_event_id", None)
    rec.pop("spine_checksum", None)

    COPILOT_RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = COPILOT_RECEIPT_DIR / f"demo-{uuid.uuid4().hex[:12]}.json"

    if bind_spine:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        receipt_path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        spine_res = append_event(
            event_type="VALIDATOR_PASS",
            object_id=str(rec.get("object_id") or "NF-COPILOT-POLICY-DEMO"),
            object_kind="system",
            agent_id=str(rec.get("agent_id") or "commit_intent_v1"),
            law_id="P-001",
            skill_id="governance_demo_gate_v1",
            validator_set=["validate-demo-enforcement-v1.sh"],
            affected_objects=[str(rec.get("object_id") or "NF-COPILOT-POLICY-DEMO")],
            gate="demo_enforcement",
            proof=str(receipt_path),
            payload={
                "intent_id": rec.get("intent_id"),
                "outcome": rec.get("outcome"),
                "policy_id": rec.get("policy_id"),
                "evidence": rec.get("evidence"),
            },
        )
        if spine_res.get("ok"):
            ev = spine_res["event"]
            rec["spine_event_id"] = ev.get("event_id")
            rec["spine_checksum"] = ev.get("checksum")
            rec["proof_path"] = str(receipt_path)

    rec["receipt_checksum"] = _checksum(rec)
    receipt_path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    LATEST_COPILOT = COPILOT_RECEIPT_DIR / "latest-demo-receipt.json"
    LATEST_COPILOT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    COPILOT_RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with COPILOT_RECEIPT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def commit(intent: dict, *, dry_run: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from gatekeeper_v1 import run_gatekeeper  # noqa: WPS433

    intent_id = intent.get("intent_id") or f"INT-{uuid.uuid4().hex[:8]}"
    action = str(intent.get("action") or "execute")
    object_id = str(intent.get("object_id") or "ENFORCEMENT-DEMO")
    rule_id = str(intent.get("rule_id") or "SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1")
    sa_id = str(intent.get("sa_id") or "")
    role = str(intent.get("role") or "read")
    engine = str(intent.get("engine") or "api")
    agent_id = str(intent.get("agent_id") or "demo_agent")

    gate = run_gatekeeper(
        sa_id=sa_id,
        role=role,
        engine=engine,
        caller="commit_intent_v1",
    )

    base = {
        "schema": "enforcement-action-receipt-v1",
        "receipt_id": f"RCP-{uuid.uuid4().hex[:12]}",
        "intent_id": intent_id,
        "action": action,
        "object_id": object_id,
        "rule_id": rule_id,
        "agent_id": agent_id,
        "gate_status": gate.get("status"),
        "gate_reasons": gate.get("reasons") or [],
        "created_at": _now(),
        "law": "brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md",
    }

    if not gate.get("safe_to_execute"):
        base["outcome"] = "BLOCKED"
        receipt = _write_receipt(base, bind_spine=False)
        return {"ok": False, "blocked": True, "gatekeeper": gate, "receipt": receipt}

    if dry_run:
        base["outcome"] = "DRY_RUN"
        return {"ok": True, "dry_run": True, "gatekeeper": gate, "receipt_preview": base}

    base["outcome"] = "COMMITTED"
    receipt = _write_receipt(base, bind_spine=True)
    return {"ok": True, "gatekeeper": gate, "receipt": receipt}


def main() -> int:
    ap = argparse.ArgumentParser(description="commit(intent) — single enforcement gate")
    ap.add_argument("--intent", default="", help="Path to intent JSON")
    ap.add_argument("--demo-enforcement", action="store_true", help="Copilot P-001 demo path")
    ap.add_argument(
        "--asset-b-policy",
        choices=("outreach", "ops", "creative"),
        default="",
        help="Asset B buyer policy demo (outreach|ops|creative)",
    )
    ap.add_argument("--case", choices=("block", "allow"), default="allow")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.asset_b_policy:
        out = commit_asset_b_policy(args.asset_b_policy, args.case, dry_run=args.dry_run)
    elif args.demo_enforcement:
        out = commit_copilot_demo(args.case, dry_run=args.dry_run)
    else:
        if not args.intent:
            print(json.dumps({"ok": False, "error": "--intent required unless --demo-enforcement"}))
            return 1
        path = Path(args.intent)
        if not path.is_file():
            print(json.dumps({"ok": False, "error": f"intent missing: {path}"}))
            return 1
        intent = json.loads(path.read_text(encoding="utf-8"))
        out = commit(intent, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    elif out.get("blocked"):
        print("BLOCKED:", "; ".join(out.get("receipt", {}).get("gate_reasons") or ["gatekeeper FAIL"]))
    elif out.get("ok"):
        r = out.get("receipt") or out.get("receipt_preview") or {}
        print(f"OK: {r.get('outcome')} intent={r.get('intent_id')} receipt={r.get('receipt_id', 'preview')}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
