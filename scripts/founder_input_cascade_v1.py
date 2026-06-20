#!/usr/bin/env python3
"""Founder input cascade — ONE intake → ALL layers automatically (no agent rule sprawl).

Law: ASF input must affect every machine surface immediately — not 10 chat rules.
Receipt: ~/.sina/founder-input-cascade-receipt-v1.json
Events: ~/.sina/founder-input-cascade-events.jsonl
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
RECEIPT = SINA / "founder-input-cascade-receipt-v1.json"
EVENTS = SINA / "founder-input-cascade-events.jsonl"

# Every layer that MUST reflect founder input (machine proof — not agent memory)
CASCADE_TARGETS = (
    "latch",
    "stairlift",
    "routing",
    "disk_truth",
    "inbox_prompt",
    "monitor_rail",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _text_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode()).hexdigest()[:12]


def verify_layers(*, require_no_hub: bool = False) -> dict:
    """Check every cascade target — returns ok + per-target status."""
    import sys
    from pathlib import Path as P

    sys.path.insert(0, str(P(__file__).resolve().parent))
    from founder_directive_ssot_v1 import hub_closed, execution_rail_line  # noqa: WPS433

    latch = _read_json(SINA / "worker-asf-directive-latch-v1.json")
    stair = _read_json(SINA / "governance-stairlift-v1.json")
    routing = _read_json(SINA / "run-inbox-routing-v1.json")
    truth = _read_json(SINA / "run-inbox-disk-truth-v1.json")
    inbox = _read_json(SINA / "worker-prompt-inbox-v1.json")

    closed = hub_closed()
    rail = execution_rail_line()
    prompt = inbox.get("prompt") or ""
    hub_rail_tokens = ("ARCHIVED", "RETIRED", "QUARANTINE")

    checks = {
        "latch": {
            "ok": bool(latch.get("schema")),
            "no_hub": latch.get("no_hub"),
        },
        "stairlift": {
            "ok": bool(stair.get("schema")) and stair.get("no_hub") == latch.get("no_hub"),
            "no_hub": stair.get("no_hub"),
            "founder_directive": bool(stair.get("founder_directive")),
        },
        "routing": {
            "ok": (not closed) or any(tok in (routing.get("order") or "") for tok in hub_rail_tokens),
            "order": (routing.get("order") or "")[:60],
        },
        "disk_truth": {
            "ok": (not closed)
            or any(tok in (truth.get("phase_strict_order") or "") for tok in hub_rail_tokens)
            or bool(
                (truth.get("queue") or {}).get("sa_id")
                and (truth.get("inbox") or {}).get("truth_match")
                and not (truth.get("queue") or {}).get("queue_exhausted")
            ),
            "phase_strict_order": (truth.get("phase_strict_order") or "")[:60],
        },
        "inbox_prompt": {
            "ok": (not closed)
            or (not inbox.get("pending"))
            or (
                "FOUNDER DIRECTIVE" in prompt
                and any(tok in prompt for tok in ("ARCHIVED", "RETIRED", "QUARANTINE"))
            ),
            "pending": inbox.get("pending"),
        },
        "monitor_rail": {
            "ok": (not closed) or any(tok in rail for tok in hub_rail_tokens),
            "rail": rail[:60],
        },
    }
    if require_no_hub and closed:
        for name in ("latch", "stairlift"):
            checks[name]["ok"] = checks[name]["ok"] and bool(checks[name].get("no_hub"))

    failed = [k for k, v in checks.items() if not v.get("ok")]
    return {
        "ok": len(failed) == 0,
        "schema": "founder-input-cascade-verify-v1",
        "at": _now(),
        "hub_closed": closed,
        "checks": checks,
        "failed": failed,
    }


def cascade_founder_input(
    text: str,
    *,
    source: str = "founder",
    apply_latch: bool = True,
) -> dict:
    """Single entry: founder text → latch → sync ALL layers → verify → receipt."""
    t0 = time.monotonic()
    text = (text or "").strip()
    latch_row: dict = {}
    sync_row: dict = {}

    import sys
    from pathlib import Path as P

    scripts = P(__file__).resolve().parent
    sys.path.insert(0, str(scripts))

    if apply_latch and text and source not in (
        "governance_center",
        "governance_center_auto",
        "validator_proof",
    ):
        from worker_asf_directive_latch_v1 import detect_and_apply  # noqa: WPS433

        latch_row = detect_and_apply(text)

    from founder_directive_ssot_v1 import sync_all_layers  # noqa: WPS433

    sync_row = sync_all_layers(stairlift=True)

    inbox_row: dict = {}
    try:
        from run_inbox_disk_truth_v1 import ensure_inbox_truth  # noqa: WPS433

        inbox_row = ensure_inbox_truth(redeliver=False)
    except Exception as exc:
        inbox_row = {"ok": False, "error": str(exc)}

    verify = verify_layers(require_no_hub=bool(latch_row.get("no_hub")))

    pivot_row: dict = {}
    if text:
        try:
            from founder_pivot_router_v1 import route_founder_pivot  # noqa: WPS433

            pivot_row = route_founder_pivot(text, source=source, run_machines=False, write=True)
        except Exception as exc:
            pivot_row = {"matched": False, "error": str(exc)}

    ms = int((time.monotonic() - t0) * 1000)
    receipt = {
        "ok": verify.get("ok", False),
        "schema": "founder-input-cascade-receipt-v1",
        "at": _now(),
        "ms": ms,
        "source": source,
        "text_hash": _text_hash(text) if text else "",
        "text_preview": text[:120] if text else "",
        "latch": {
            "no_hub": latch_row.get("no_hub"),
            "plan_only": latch_row.get("plan_only"),
        },
        "sync": {"truth_ok": sync_row.get("truth", {}).get("ok"), "stairlift": sync_row.get("stairlift")},
        "inbox_action": inbox_row.get("action"),
        "verify": verify,
        "founder_pivot": {
            "matched": pivot_row.get("matched"),
            "pivot_id": pivot_row.get("pivot_id"),
            "inject_line": pivot_row.get("inject_line"),
            "work_template": pivot_row.get("work_template"),
        }
        if pivot_row.get("matched")
        else {"matched": False},
        "law": "ONE intake → ALL layers — agents read receipt, not 10 rules",
    }

    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**receipt, "event": "CASCADE"}, ensure_ascii=False) + "\n")

    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Founder input cascade — one intake, all layers")
    ap.add_argument("--text", default="", help="Founder message to apply")
    ap.add_argument("--source", default="cli")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.verify_only:
        row = verify_layers()
    elif args.text:
        row = cascade_founder_input(args.text, source=args.source)
    else:
        row = cascade_founder_input("", source=args.source, apply_latch=False)

    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
