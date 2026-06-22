#!/usr/bin/env python3
"""Live precondition probes for phase transitions — probe beats file.

Never trust closeout receipt alone. Validates ff-001..ff-010 receipts on disk,
queue counters, Hub :13020, Railway FBE health.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
QUEUE_SSOT = ROOT / "data" / "forge-factory-queue-cycle2-v1.json"
RECEIPTS = ROOT / "receipts"
FBE_HEALTH = "https://sourcea-fbe-runner-production.up.railway.app/health"
HUB_HEALTH = "http://127.0.0.1:13020/health"

FF_RECEIPT_RE = re.compile(
    r"^ff-\d{3}-sa-\d{4}-(?:check|act|verify)-receipt-v1\.json$",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _http_probe(url: str, *, timeout: float = 4.0) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(300).decode("utf-8", errors="replace")
            return {"ok": resp.status == 200, "status": resp.status, "body": body[:160], "url": url}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"ok": False, "url": url, "error": str(exc)[:160]}


def _queue_slots() -> list[dict[str, Any]]:
    doc = _read(QUEUE_SSOT)
    return list(doc.get("queue") or [])


def _find_ff_receipt(*, hp_id: str, sa_id: str) -> Path | None:
    if not RECEIPTS.is_dir():
        return None
    hp = hp_id.lower()
    sa = sa_id.lower()
    matches: list[Path] = []
    for path in RECEIPTS.glob("ff-*-receipt-v1.json"):
        name = path.name.lower()
        if not FF_RECEIPT_RE.match(name):
            continue
        if hp in name and sa in name:
            matches.append(path)
    if not matches:
        return None
    return sorted(matches, key=lambda p: p.stat().st_mtime)[-1]


def probe_ff_cycle2_receipts() -> dict[str, Any]:
    """Live probe each ff-001..ff-010 slot — not closeout file."""
    slots = _queue_slots()
    rows: list[dict[str, Any]] = []
    ok_count = 0
    for slot in slots:
        hp_id = str(slot.get("hp_id") or "")
        sa_id = str(slot.get("sa_id") or "")
        role = str(slot.get("queue_role") or slot.get("step_type") or "")
        path = _find_ff_receipt(hp_id=hp_id, sa_id=sa_id)
        if not path:
            rows.append(
                {
                    "hp_id": hp_id,
                    "sa_id": sa_id,
                    "role": role,
                    "ok": False,
                    "error": "receipt_missing_on_disk",
                    "expected_pattern": f"receipts/ff-*-{sa_id}-*-receipt-v1.json",
                }
            )
            continue
        body = _read(path)
        slot_ok = bool(body.get("ok"))
        if slot_ok:
            ok_count += 1
        rows.append(
            {
                "hp_id": hp_id,
                "sa_id": sa_id,
                "role": role,
                "ok": slot_ok,
                "receipt_path": str(path.relative_to(ROOT)),
                "receipt_at": body.get("at"),
                "schema": body.get("schema"),
            }
        )
    total = len(slots) or 10
    return {
        "ok": ok_count == total and total == 10,
        "probe": "ff_cycle2_receipts",
        "ok_count": ok_count,
        "total": total,
        "rows": rows,
        "law": "closeout_receipt_not_authoritative",
    }


def probe_queue_counters() -> dict[str, Any]:
    st = _read(SINA / "healthy-queue-state-v1.json")
    hq = _read(SINA / "healthy-queue-30-active.json")
    obs = _read(SINA / "phase-observed-v1.json")
    next_pos = int(st.get("next_pos") or 0)
    exhausted = bool(st.get("queue_exhausted") or hq.get("queue_exhausted") or obs.get("queue_exhausted"))
    era = str(st.get("era") or hq.get("era") or obs.get("era") or "")
    # Transition allowed when queue cursor past last slot OR explicitly exhausted post-reconcile
    cursor_ok = exhausted or next_pos > 10
    return {
        "ok": cursor_ok,
        "probe": "queue_counters",
        "next_pos": next_pos,
        "queue_exhausted": exhausted,
        "era": era,
        "expected": "next_pos>10 or queue_exhausted=true",
    }


def probe_hub() -> dict[str, Any]:
    row = _http_probe(HUB_HEALTH)
    row["probe"] = "hub_health"
    return row


def probe_railway() -> dict[str, Any]:
    row = _http_probe(FBE_HEALTH)
    row["probe"] = "railway_fbe_health"
    return row


def probe_cycle2_to_market_preconditions() -> dict[str, Any]:
    sys_path_insert = ROOT / "scripts"
    import sys

    if str(sys_path_insert) not in sys.path:
        sys.path.insert(0, str(sys_path_insert))
    from phase_desired_read_v1 import (  # noqa: WPS433
        desired_targets_phase_market,
        read_desired_active,
        read_phase_record,
        validate_desired_readable,
    )

    issues: list[str] = []
    desired_ok, desired_issues = validate_desired_readable()
    issues.extend(desired_issues)
    active = read_desired_active()
    if not desired_targets_phase_market():
        issues.append("founder_desired_not_phase_market")
    ff = read_phase_record("forge-factory-cycle2")
    if str(ff.get("status") or "") != "complete":
        issues.append("founder_desired_forge_cycle2_not_marked_complete")

    ff_probe = probe_ff_cycle2_receipts()
    queue_probe = probe_queue_counters()
    hub_probe = probe_hub()
    railway_probe = probe_railway()

    if not ff_probe.get("ok"):
        issues.append(f"ff_receipt_probe_{ff_probe.get('ok_count')}_of_{ff_probe.get('total')}")
    if not queue_probe.get("ok"):
        issues.append("queue_counter_not_ready")
    if not hub_probe.get("ok"):
        issues.append("hub_health_down")
    if not railway_probe.get("ok"):
        issues.append("railway_fbe_health_down")

    ok = len(issues) == 0
    return {
        "schema": "phase-transition-probe-v1",
        "ok": ok,
        "at": _now(),
        "transition": "cycle2_to_market",
        "issues": issues,
        "desired_active": active,
        "probes": {
            "ff_cycle2": ff_probe,
            "queue_counters": queue_probe,
            "hub": hub_probe,
            "railway": railway_probe,
        },
        "closeout_note": "forge-factory-cycle2-closeout-v1.json is documentary only — not used as gate",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase transition live probes")
    ap.add_argument("--transition", default="cycle2-to-market", choices=["cycle2-to-market"])
    ap.add_argument("--ff-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.ff_only:
        row = probe_ff_cycle2_receipts()
    elif args.transition == "cycle2-to-market":
        row = probe_cycle2_to_market_preconditions()
    else:
        row = {"ok": False, "error": "unknown_transition"}

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps({"ok": row.get("ok"), "issues": row.get("issues", [])}))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
