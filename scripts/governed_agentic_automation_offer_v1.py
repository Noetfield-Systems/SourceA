#!/usr/bin/env python3
"""Asset B — governed agentic automation DFY offer receipt + outreach pack."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "governed-agentic-automation-offer-v1.json"
EMAIL_TEMPLATES = SINA / "governed-agentic-automation-email-templates-v1.json"
OUTREACH = SINA / "governed-agentic-automation-outreach-v1.json"
LAW = SOURCE_A / "brain-os/law/SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md"
SENDER_LAW = SOURCE_A / "brain-os/law/SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md"
POLICY_PACK_LAW = SOURCE_A / "docs/SOURCEA_ASSET_B_POLICY_PACK_LOCKED_v1.md"
POLICY_PACK_REGISTRY = SOURCE_A / "data/asset-b-policy-pack-v1.json"
POLICY_PACK_SOW = SOURCE_A / "docs/asset-b-policy-pack/SOW_MAPPING_LOCKED_v1.md"
FROM_EMAIL = "hello@sourcea.app"
FROM_NAME = "SourceA"
COMPANY_URL = "https://sourcea.com"
FOUNDER_NAME = os.environ.get("SOURCEA_FOUNDER_NAME", "Sina Kazemnezhad").strip() or "Sina Kazemnezhad"
OPT_OUT = 'Reply "stop" and I won\'t follow up.'
SIGNATURE = (
    f"—\n{FOUNDER_NAME}\nSourceA · governed agentic automation\n{FROM_EMAIL}\n{COMPANY_URL}\n\n{OPT_OUT}"
)

SKUS: list[dict[str, Any]] = [
    {
        "id": "SKU-DFY-001",
        "name": "Agent Loop Build",
        "price_min_usd": 3000,
        "price_max_usd": 10000,
        "type": "project",
        "timeline_weeks": "2-3",
        "w3_threshold_usd": 3000,
        "deliverable": "One governed agent loop live · handoff doc · 30-day fix window",
    },
    {
        "id": "SKU-RET-001",
        "name": "Agent Loop Retainer",
        "price_min_usd": 2000,
        "price_max_usd": 5000,
        "type": "retainer",
        "timeline_weeks": "ongoing",
        "w3_threshold_usd": 2000,
        "deliverable": "Loop ops · weekly receipt export · approval-gated changes",
    },
    {
        "id": "SKU-COMBO-001",
        "name": "Governed Automation + Receipts",
        "price_min_usd": 3000,
        "price_max_usd": 15000,
        "type": "combo",
        "timeline_weeks": "2-4",
        "w3_threshold_usd": 3000,
        "deliverable": "DFY or retainer plus signed receipt chain · tamper export · replay demo",
    },
    {
        "id": "SKU-OPS-002",
        "name": "Ops Health Audit",
        "price_min_usd": 750,
        "price_max_usd": 750,
        "type": "feeder",
        "timeline_weeks": "0.5",
        "w3_threshold_usd": 750,
        "deliverable": "SourceA spine audit · PDF — feeder to DFY",
    },
]

OUTREACH_TARGETS: list[dict[str, Any]] = [
    {
        "id": "AB-T01",
        "segment": "Cursor agency (client agent loops)",
        "channel": "LinkedIn DM",
        "priority": "P0",
        "sku": "SKU-DFY-001",
        "snippet": "We run a self-healing agent factory daily. Done-for-you client loop in 2–3 weeks from $3K.",
    },
    {
        "id": "AB-T02",
        "segment": "Fractional CTO / ops lead",
        "channel": "Warm intro",
        "priority": "P0",
        "sku": "SKU-RET-001",
        "snippet": "$2K/mo — governed outreach or ops loop with weekly receipt export your stakeholders can forward.",
    },
    {
        "id": "AB-T03",
        "segment": "Pre-seed founder (outreach stall)",
        "channel": "Twitter/X · DM",
        "priority": "P0",
        "sku": "SKU-DFY-001",
        "snippet": "Research → draft → approval → send. One loop live in weeks, not a hiring cycle.",
    },
    {
        "id": "AB-T04",
        "segment": "Automation consultant",
        "channel": "Email",
        "priority": "P1",
        "sku": "SKU-COMBO-001",
        "snippet": "Build the loop plus cryptographic receipts — separates you from every generic agent freelancer.",
    },
]

EMAIL_TEMPLATES_BODY: dict[str, Any] = {
    "sender": {
        "from_email": FROM_EMAIL,
        "from_name": FROM_NAME,
        "company_url": COMPANY_URL,
        "law": "SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md",
        "send_script": "scripts/send_ab1_single_v1.py",
    },
    "ab1_primary": {
        "variant": "polished_proof_led",
        "label": "Polished proof-led (default send)",
        "subject": "Can you prove what your agents executed last night?",
        "body": (
            "Hi{Name},\n\n"
            "Quick question for teams shipping Cursor agents for clients: when something goes wrong, can you "
            "prove what ran, what was blocked, and whether it is safe to run again tomorrow?\n\n"
            "We run a self-healing multi-agent factory every day — policy before execution, signed receipts "
            "on disk — and build the same for clients:\n\n"
            "• Agent Loop Build — one governed loop live in 2–3 weeks ($3–10K project)\n"
            "• Agent Loop Retainer — weekly proof export + ongoing ops ($2–5K/month)\n\n"
            "No deck. I attach three buyer policy JSONs (outreach / ops / creative) — "
            "happy to screen-share block → allow → signed receipt in 15 minutes.\n\n"
            "Worth a look?\n\n"
            f"{SIGNATURE}"
        ),
    },
    "ab1_short_punchy": {
        "variant": "short_punchy",
        "label": "Short punchy (A/B)",
        "subject": "Receipts for your agent loops?",
        "body": (
            "Hi{Name},\n\n"
            "Your Cursor agents run. Can you prove what they executed last night?\n\n"
            "We ship governed agent loops with signed receipts — $3–10K build or $2–5K/mo retainer. "
            "Fifteen-minute screen-share, no deck.\n\n"
            "Interested?\n\n"
            f"{SIGNATURE}"
        ),
    },
    "ab1_followup": {
        "subject": "Re: factory receipts — 15 min screen-share?",
        "body": (
            "Following up — happy to show today's session gate and export bundle live "
            "(what ran, what was blocked, what policy applied). No slides.\n\n"
            "Does a 15-minute slot work this week?\n\n"
            f"{SIGNATURE}"
        ),
    },
    "ab1_combo_bridge": {
        "subject": "Same build — agent loop plus audit trail",
        "body": (
            "If compliance or diligence matters on your side, we instrument the same agent loop with "
            "signed receipts and tamper-checked exports — one engagement, loop live now, governance "
            "proof when you need it.\n\n"
            "Worth starting with the loop scope?\n\n"
            f"{SIGNATURE}"
        ),
    },
    "ab1_chain_tool": {
        "subject": "PASS or BLOCK before your agents run",
        "body": (
            "Quick intro — we ship chain tools for agentic projects (Graphify-class infrastructure, "
            "not another agent).\n\n"
            "Try: pip install sourcea-boot && sourcea-boot\n"
            "→ BOOT_REPORT.json · four disk checks · safe to execute or BLOCK with reason.\n\n"
            "We also build governed agent loops for teams that want done-for-you delivery. "
            "Happy to show both in 15 minutes.\n\n"
            f"{SIGNATURE}"
        ),
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _factory_line() -> str:
    live = SINA / "agent-live-surfaces-v1.json"
    blob = _read_json(live, {})
    return str(blob.get("factory_now_line") or blob.get("truth_bundle", {}).get("factory_now_line") or "")


def _session_gate_ok() -> bool:
    try:
        proc = subprocess.run(
            ["python3", str(SOURCE_A / "scripts" / "agent_session_gate_run_v1.py"), "--role", "any", "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=SOURCE_A,
        )
        if proc.returncode != 0:
            return False
        data = json.loads(proc.stdout)
        return bool(data.get("ok"))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return False


def build_receipt(*, refresh_gate: bool = False) -> dict[str, Any]:
    gate_ok = _session_gate_ok() if refresh_gate else None
    if gate_ok is None:
        gate_receipt = _read_json(SINA / "agent_session_gate_receipt_v1.json", {})
        gate_ok = bool(gate_receipt.get("ok"))

    w3_log = _read_json(SINA / "governed-agentic-automation-w3-v1.json", {"events": []})
    events = w3_log.get("events") or []
    ab1_met = any(
        (e.get("sku") in ("SKU-DFY-001", "SKU-RET-001") and float(e.get("amount_usd") or 0) >= float(e.get("threshold_usd") or 0))
        for e in events
    )

    return {
        "version": "1.0",
        "asset": "B",
        "law": "SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md",
        "updated_at": _now_iso(),
        "commercial_ready": bool(gate_ok) and LAW.is_file(),
        "session_gate_ok": bool(gate_ok),
        "factory_now_line": _factory_line(),
        "skus": SKUS,
        "speed_to_cash_rank": [
            {"rank": 1, "motion": "DFY governed agentic automation", "timeline": "weeks"},
            {"rank": 2, "motion": "Noetfield NW1 pilot", "timeline": "1-3 months", "parallel": True},
            {"rank": 3, "motion": "Combined DFY + governance receipts", "timeline": "same engagement"},
        ],
        "win_codes": {
            "AB1": {"met": ab1_met, "rule": "DFY >= $3K or retainer first month >= $2K"},
            "AB2": {"met": len([e for e in events if e.get("sku") in ("SKU-DFY-001", "SKU-RET-001")]) >= 2},
            "AB3": {"met": any(e.get("case_study") for e in events)},
        },
        "fixed_run_cost_usd_month": 200,
        "outreach_targets": OUTREACH_TARGETS,
        "policy_pack": {
            "law": str(POLICY_PACK_LAW),
            "registry": str(POLICY_PACK_REGISTRY),
            "sow_mapping": str(POLICY_PACK_SOW),
            "demo_script": str(SOURCE_A / "scripts/demo-asset-b-policy-v1.sh"),
            "policies": {
                "outreach": str(SOURCE_A / "docs/asset-b-policy-pack/outreach_loop_v1.json"),
                "ops": str(SOURCE_A / "docs/asset-b-policy-pack/ops_spend_v1.json"),
                "creative": str(SOURCE_A / "docs/asset-b-policy-pack/creative_publish_v1.json"),
            },
            "talk_track": (
                "We ship your first governable agent in 48 hours. Outreach can't send without "
                "your approval ref. Ops can't spend over $50. Nothing posts without human handoff. "
                "Every allowed action emits a signed receipt you can export."
            ),
        },
        "paths": {
            "law": str(LAW),
            "sender_law": str(SENDER_LAW),
            "from_email": FROM_EMAIL,
            "email_templates": str(EMAIL_TEMPLATES),
            "outreach": str(OUTREACH),
            "w3_log": str(SINA / "governed-agentic-automation-w3-v1.json"),
            "policy_pack_law": str(POLICY_PACK_LAW),
            "policy_pack_sow": str(POLICY_PACK_SOW),
        },
    }


def pack() -> dict[str, Any]:
    _write_json(EMAIL_TEMPLATES, {"version": "1.0", "updated_at": _now_iso(), "templates": EMAIL_TEMPLATES_BODY})
    _write_json(OUTREACH, {"version": "1.0", "updated_at": _now_iso(), "targets": OUTREACH_TARGETS})
    receipt = build_receipt()
    _write_json(RECEIPT, receipt)
    return receipt


def log_w3(sku: str, amount_usd: float, *, client: str = "", case_study: bool = False) -> dict[str, Any]:
    path = SINA / "governed-agentic-automation-w3-v1.json"
    blob = _read_json(path, {"events": []})
    events: list[dict[str, Any]] = list(blob.get("events") or [])
    threshold = 3000 if sku == "SKU-DFY-001" else 2000 if sku == "SKU-RET-001" else 750
    events.append(
        {
            "at": _now_iso(),
            "sku": sku,
            "amount_usd": amount_usd,
            "threshold_usd": threshold,
            "client": client,
            "case_study": case_study,
            "w3_signal": amount_usd >= threshold,
        }
    )
    blob["events"] = events
    _write_json(path, blob)
    receipt = build_receipt()
    _write_json(RECEIPT, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Asset B governed agentic automation offer")
    parser.add_argument("--pack", action="store_true", help="Write outreach pack + receipt")
    parser.add_argument("--status", action="store_true", help="Print receipt (refresh metadata)")
    parser.add_argument("--log-w3", action="store_true", help="Log W3 economic signal")
    parser.add_argument("--sku", default="SKU-DFY-001")
    parser.add_argument("--amount-usd", type=float, default=0)
    parser.add_argument("--client", default="")
    parser.add_argument("--case-study", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.log_w3:
        if args.amount_usd <= 0:
            print("amount-usd required for --log-w3", file=sys.stderr)
            return 1
        data = log_w3(args.sku, args.amount_usd, client=args.client, case_study=args.case_study)
    elif args.pack:
        data = pack()
    else:
        data = build_receipt(refresh_gate=args.status)
        if args.status or not RECEIPT.is_file():
            _write_json(RECEIPT, data)

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"commercial_ready={data.get('commercial_ready')} AB1={data.get('win_codes', {}).get('AB1', {}).get('met')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
