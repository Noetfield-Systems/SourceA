#!/usr/bin/env python3
"""World-model + platform-neutral plan check loop.

Absorb best WTM takes · forbid public Mac-only gates · route good ideas to product lanes.
Receipt: ~/.sina/world-model-plan-check-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "platform-neutral-world-model-v1.json"
WTM = ROOT / "brain-os" / "wtm" / "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md"
RECEIPT = SINA / "world-model-plan-check-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict | str:
    if not path.is_file():
        return {} if path.suffix == ".json" else ""
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            return json.loads(text)
        return text
    except (OSError, json.JSONDecodeError):
        return {} if path.suffix == ".json" else ""


def _load_ssot() -> dict:
    row = _read(SSOT)
    return row if isinstance(row, dict) and row.get("schema") else {}


def _extract_strings(obj, out: list[str]) -> None:
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _extract_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _extract_strings(v, out)


def _scan_forbidden(text: str, forbidden: list[str], *, allow_mac_guard: bool) -> list[dict]:
    hits: list[dict] = []
    low = text.lower()
    for phrase in forbidden:
        if phrase not in low:
            continue
        if allow_mac_guard and "mac guard" in low:
            continue
        hits.append({"phrase": phrase, "snippet": text[:120]})
    return hits


def _route_takes(strings: list[str], routes: list[dict]) -> list[dict]:
    found: list[dict] = []
    blob = " ".join(strings).lower()
    for route in routes:
        lane = str(route.get("lane") or "")
        keys = route.get("keywords") or []
        matched = [k for k in keys if k in blob]
        if matched:
            found.append({"lane": lane, "keywords": matched[:5], "sku_only": bool(route.get("sku_only"))})
    return found


def _wtm_glance() -> dict:
    text = str(_read(WTM) or "")
    active = "D2" if "D2" in text and "●" in text else "unknown"
    return {
        "ssot": str(WTM.relative_to(ROOT)) if WTM.is_file() else "",
        "active_phase": active,
        "version": "5.2" if "5.2" in text else "",
        "gate_artifact": "llm_context_packet_v1.json",
    }


def run_check(*, write: bool = True) -> dict:
    ssot = _load_ssot()
    policy = ssot.get("platform_neutral_policy") or {}
    forbidden = list(policy.get("forbidden_public_framing") or [])
    routes = list(ssot.get("product_routes") or [])
    targets = list((ssot.get("plan_check_loop") or {}).get("scan_targets") or [])

    violations: list[dict] = []
    advisory: list[dict] = []
    scanned = 0
    all_strings: list[str] = []

    strict_targets = [
        "agent-control-panel/worker-hub/index.html",
        "data/tool-pick-two-phase-v1.json",
        "data/platform-neutral-world-model-v1.json",
    ]
    plan_targets = [
        "data/outbound-factory-100-upgrade-plan-v1.json",
        "data/sourcea-full-stack-100-fix-plan-v1.json",
        "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
    ]
    targets = list((ssot.get("plan_check_loop") or {}).get("scan_targets") or strict_targets + plan_targets)

    forbidden_catalog = {str(x).lower() for x in forbidden}

    for rel in targets:
        path = ROOT / rel
        if not path.is_file():
            continue
        scanned += 1
        strict = rel in strict_targets
        if path.suffix == ".json":
            data = _read(path)
            strings: list[str] = []
            _extract_strings(data, strings)
        else:
            strings = [str(_read(path))]
        all_strings.extend(strings)
        bucket = violations if strict else advisory
        for s in strings:
            if len(s) < 12:
                continue
            if rel == "data/platform-neutral-world-model-v1.json" and s.lower() in forbidden_catalog:
                continue
            allow_mac = "mac guard" in s.lower() or "sku-ops" in s.lower() or "l0" in s.lower()
            for hit in _scan_forbidden(s, forbidden, allow_mac_guard=allow_mac):
                bucket.append({"file": rel, "strict": strict, **hit})

    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    if isinstance(surfaces, dict):
        for key in ("factory_now_line", "plans_unified_line", "tool_pick_line", "mcp_stack_line"):
            line = str(surfaces.get(key) or "")
            if line:
                all_strings.append(line)
                for hit in _scan_forbidden(line, forbidden, allow_mac_guard=False):
                    violations.append({"file": f"~/.sina/agent-live-surfaces-v1.json:{key}", **hit})

    product_routes = _route_takes(all_strings, routes)
    wtm = _wtm_glance()
    ok = len(violations) == 0

    row = {
        "schema": "world-model-plan-check-receipt-v1",
        "saved_at": _now(),
        "ok": ok,
        "world_model_line": (
            f"WTM check · phase={wtm.get('active_phase')} · scanned={scanned} · "
            f"public={'PASS' if ok else 'FAIL'} · advisory={len(advisory)} · "
            f"routes={len(product_routes)}"
        ),
        "one_law": ssot.get("one_law") or policy.get("routing_law"),
        "platform_neutral_ok": ok,
        "wtm": wtm,
        "violations": violations[:20],
        "violation_count": len(violations),
        "advisory_plan_framing": advisory[:15],
        "advisory_count": len(advisory),
        "product_routes_detected": product_routes[:12],
        "stripe_buyer_copy": (policy.get("stripe_buyer_copy_template") or "")[:200],
        "stripe_billing": policy.get("stripe_billing") or {},
        "stripe_statement_descriptor": (policy.get("stripe_billing") or {}).get("statement_descriptor"),
        "stripe_statement_descriptor_short": (policy.get("stripe_billing") or {}).get("statement_descriptor_short"),
        "surfaces": policy.get("surfaces"),
        "developer_stacks": policy.get("developer_stacks"),
        "hub_api": "POST /api/world-model-plan-check/tick/v1",
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def handle_hub_post(_body: dict | None = None) -> dict:
    row = run_check(write=True)
    return {**row, "ok": bool(row.get("ok"))}


def hub_slice() -> dict:
    row = _read(RECEIPT)
    if not row or row.get("schema") != "world-model-plan-check-receipt-v1":
        row = run_check(write=True)
    return {
        "schema": "worker-hub-world-model-plan-check-v1",
        "ok": bool(row.get("ok")),
        "world_model_line": row.get("world_model_line"),
        "violation_count": row.get("violation_count"),
        "product_routes_detected": row.get("product_routes_detected"),
        "stripe_buyer_copy": row.get("stripe_buyer_copy"),
        "stripe_statement_descriptor": row.get("stripe_statement_descriptor"),
        "stripe_statement_descriptor_short": row.get("stripe_statement_descriptor_short"),
        "hub_api": row.get("hub_api"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="World-model platform-neutral plan check")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_check(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("world_model_line") or "—")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
