#!/usr/bin/env python3
"""Noetfield copilot runtime — policy gate before agent acts (LaunchDarkly-shaped)."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "noetfield-copilot-runtime-receipt-v1.json"
FACTORY_ID = "noetfield-copilot-factory-v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _single_eval(
    *,
    action: str,
    payload: dict[str, Any],
    tenant: str,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    allowed = set(cfg.get("allowed_actions") or [])
    block_pii = bool(cfg.get("block_pii_export"))
    block_send = bool(cfg.get("block_external_send"))

    if action not in allowed:
        return {
            "verdict": "BLOCKED",
            "reason": "action_not_allowed",
            "for_founder": {
                "blocked": True,
                "why": f"Copilot action `{action}` is not permitted under policy {cfg.get('policy_strictness')}.",
            },
        }
    if block_pii and (action == "export_pii" or payload.get("contains_pii")):
        return {
            "verdict": "BLOCKED",
            "reason": "pii_export_blocked",
            "for_founder": {
                "blocked": True,
                "why": "Exporting PII is blocked until TrustField sandbox promotion.",
            },
        }
    if block_send and action == "external_send":
        return {
            "verdict": "BLOCKED",
            "reason": "external_send_blocked",
            "for_founder": {
                "blocked": True,
                "why": "Outbound send stays blocked — dispatch requires signed TLE receipt first.",
            },
        }

    show = (
        f"Copilot `{action}` allowed for {tenant} under {cfg.get('policy_strictness')} policy "
        f"· cfg {cfg.get('config_version')}."
    )
    return {
        "verdict": "ALLOW",
        "for_founder": {"show_this": show},
        "for_agent": {"instruction": "Proceed with signed TLE receipt on completion."},
    }


def evaluate_copilot_action(
    *,
    action: str,
    payload: dict[str, Any] | None = None,
    tenant: str = "pilot-tenant-a",
    context_id: str = "",
    variation_key: str | None = None,
    write_receipt: bool = False,
    allow_escalation: bool = True,
) -> dict[str, Any]:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from agent_runtime_config_v1 import load_factory_runtime_config  # noqa: WPS433

    payload = payload or {}
    cfg = load_factory_runtime_config(
        FACTORY_ID,
        context_id=context_id or tenant,
        variation_key=variation_key,
    )
    attempts: list[dict[str, Any]] = []
    first = _single_eval(action=action, payload=payload, tenant=tenant, cfg=cfg)
    attempts.append(
        {
            "variation_key": cfg.get("variation_key"),
            "config_version": cfg.get("config_version"),
            "verdict": first.get("verdict"),
        }
    )

    row = dict(first)
    escalated = False
    if (
        allow_escalation
        and first.get("verdict") == "BLOCKED"
        and cfg.get("retry_on_blocked")
        and cfg.get("fallback_variation")
    ):
        fb = str(cfg.get("fallback_variation"))
        cfg2 = load_factory_runtime_config(FACTORY_ID, context_id=context_id or tenant, variation_key=fb)
        second = _single_eval(action=action, payload=payload, tenant=tenant, cfg=cfg2)
        attempts.append(
            {
                "variation_key": cfg2.get("variation_key"),
                "config_version": cfg2.get("config_version"),
                "verdict": second.get("verdict"),
            }
        )
        if second.get("verdict") == "ALLOW":
            row = dict(second)
            escalated = True
            cfg = cfg2

    out = {
        "schema": "noetfield-copilot-runtime-receipt-v1",
        "receipt_id": f"noetfield-copilot-{uuid.uuid4().hex[:12]}",
        "at": _now(),
        "ok": row.get("verdict") == "ALLOW",
        "factory_id": FACTORY_ID,
        "bay_slug": cfg.get("bay_slug"),
        "tenant": tenant,
        "action": action,
        "verdict": row.get("verdict"),
        "config_version": cfg.get("config_version"),
        "variation_key": cfg.get("variation_key"),
        "policy_strictness": cfg.get("policy_strictness"),
        "require_tle_receipt": bool(cfg.get("require_tle_receipt")),
        "escalated": escalated,
        "attempts": attempts,
        "for_founder": row.get("for_founder") or {},
        "for_agent": row.get("for_agent") or {},
        "execution_plane": "headless_cloud",
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Noetfield copilot runtime v1")
    ap.add_argument("--action", required=True)
    ap.add_argument("--tenant", default="pilot-tenant-a")
    ap.add_argument("--variation-key", default="")
    ap.add_argument("--payload", default="{}")
    ap.add_argument("--no-write", action="store_true", help="Skip ~/.sina receipt (validators/mac-light)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    payload = json.loads(args.payload)
    row = evaluate_copilot_action(
        action=args.action,
        payload=payload,
        tenant=args.tenant,
        variation_key=args.variation_key or None,
        write_receipt=not args.no_write,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        ff = row.get("for_founder") or {}
        print(ff.get("show_this") or ff.get("why") or row.get("verdict"))
    # JSON mode = machine contract; caller asserts verdict (validators use --no-write).
    return 0 if args.json else (0 if row.get("ok") else 1)


if __name__ == "__main__":
    raise SystemExit(main())
