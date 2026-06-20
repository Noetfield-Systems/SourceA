#!/usr/bin/env python3
"""Inject live trust signals for Witness AI site — factory repository + governance events."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "trust-signals.json"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "witnessbc-trust-signals-inject-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _parse_valid_yes(line: str) -> int | None:
    import re

    m = re.search(r"Valid YES\s+(\d+)", line or "", re.I)
    return int(m.group(1)) if m else None


def _count_governance_events_today() -> dict:
    path = SINA / "agent-governance-events.jsonl"
    today = _today()
    count = 0
    samples: list[str] = []
    if not path.is_file():
        return {"count": 0, "samples": [], "date": today}
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            at = str(row.get("at") or row.get("timestamp") or "")
            if not at.startswith(today):
                continue
            event = str(row.get("event") or "")
            if not event or event in {"workspace_selected", "prompt_router"}:
                continue
            count += 1
            if len(samples) < 5:
                samples.append(f"agent-governance-events.jsonl:{event}")
    except OSError:
        pass
    return {"count": count, "samples": samples, "date": today}


def build_signals() -> dict:
    live = _read_json(SINA / "agent-live-surfaces-v1.json") or {}
    gate = _read_json(SINA / "agent-session-gate-receipt_v1.json") or _read_json(
        SINA / "agent_session_gate_receipt_v1.json"
    ) or {}
    factory_line = live.get("factory_now_line") or ""
    if not factory_line and isinstance(gate.get("steps"), list):
        for step in gate["steps"]:
            if step.get("factory_now_line"):
                factory_line = step["factory_now_line"]
                break
    valid_yes = _parse_valid_yes(factory_line)
    gov = _count_governance_events_today()
    conduct = gate.get("conduct") or {}
    verdict = "PASS" if conduct.get("ok") else "BLOCK"
    if gate.get("ok") is False:
        verdict = "BLOCK"

    return {
        "schema": "witnessbc-trust-signals-v1",
        "at": _now(),
        "receipts_signed_today": gov["count"],
        "receipts_date": gov["date"],
        "receipt_samples": gov["samples"],
        "receipt_metric_label": "Governance events today",
        "valid_yes": valid_yes,
        "valid_yes_total": 1000,
        "factory_now_line": factory_line,
        "governance": {
            "verdict": verdict,
            "session_gate_ok": bool(gate.get("ok")),
            "at": gate.get("at") or _now(),
        },
        "deploy": {
            "bundle": "witnessbc-site-v8",
            "local_port": 8090,
            "status": "ship-local",
        },
        "proof_demo_url": json.loads((ROOT / "data" / "cta.json").read_text(encoding="utf-8")).get(
            "live_demo_url", ""
        ),
        "disclaimer": "Live factory signals · product metrics labeled separately · not certification",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = build_signals()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": "witnessbc-trust-signals-inject-v1",
        "ok": True,
        "at": row["at"],
        "out": str(OUT),
        "receipts_signed_today": row["receipts_signed_today"],
        "valid_yes": row.get("valid_yes"),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"OK: trust-signals · receipts_today={row['receipts_signed_today']} · valid_yes={row.get('valid_yes')}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
