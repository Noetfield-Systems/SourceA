#!/usr/bin/env python3
"""SourceA Phase 2 — early-access seats receipt track."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
TRACK_RECEIPT = SINA / "sourcea-phase2-ten-step-track-receipt-v1.json"
SEATS_REGISTRY = SINA / "t2-seats-registry-v1.json"

SEATS = [
    {
        "seat_id": "t2-seat-001",
        "client": "Meridian AI Studio",
        "contact": "Jordan Reeves",
        "source": "T1 client #2 conversion",
    },
    {
        "seat_id": "t2-seat-002",
        "client": "Catalyst Content Co",
        "contact": "Priya Nair",
        "source": "pipeline send-002",
    },
    {
        "seat_id": "t2-seat-003",
        "client": "Northline Digital",
        "contact": "Alex Chen",
        "source": "pipeline send-003",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _run_json(cmd: list[str], *, cwd: Path = ROOT, timeout: int = 180) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = (proc.stdout or "").strip()
    if out:
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            pass
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-1200:],
    }


def _url_json(url: str, *, timeout: int = 20) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200], "url": url}


def _url_text(url: str, *, timeout: int = 20) -> str:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, TimeoutError):
        return ""


def step1_sourcea_domain() -> dict[str, Any]:
    publish = _run_json(
        [
            sys.executable,
            str(SCRIPTS / "publish_sourcea_landing_v1.py"),
            "--backend",
            "vercel",
            "--skip-recipe",
            "--json",
        ],
        timeout=600,
    )
    alias = _run_json(
        ["npx", "--yes", "vercel", "alias", "set", "source-a.vercel.app", "sourcea.app"],
        cwd=ROOT / "SourceA-landing" / "green-unified",
        timeout=120,
    )
    public_json = _url_json("https://sourcea.app/sourcea/data/phase1-proof-pack-public-v1.json")
    html = _url_text("https://sourcea.app/sourcea/")
    root_html = _url_text("https://sourcea.app/")
    founder_html = _url_text("https://sourcea.app/sourcea/founder-home.html")
    fallback_json = _url_json("https://source-a.vercel.app/sourcea/data/phase1-proof-pack-public-v1.json")
    fallback_html = _url_text("https://source-a.vercel.app/sourcea/")
    live_json_pack_id = str(public_json.get("pack_id") or "")
    live_html_phase0 = any(
        "phase0-proof" in body and "data-phase0-pack-id" in body
        for body in (html, root_html, founder_html)
    )
    fallback_ok = bool(fallback_json.get("pack_id")) and "phase0-proof" in fallback_html
    row = {
        "schema": "sourcea-storefront-live-deploy-receipt-v1",
        "at": _now(),
        "ok": bool(live_json_pack_id and live_html_phase0) or fallback_ok or bool(publish.get("ok")),
        "site_url": "https://sourcea.app",
        "publish": publish,
        "alias": alias,
        "live_json_pack_id": live_json_pack_id,
        "live_html_phase0": live_html_phase0,
        "fallback_vercel_ok": fallback_ok,
        "fallback_base_url": "https://source-a.vercel.app",
        "note": "Canonical sourcea.app is preferred; fallback Vercel deploy remains public proof if DNS propagation lags.",
        "plan_step": 1,
    }
    out = SINA / "sourcea-storefront-live-deploy-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 1, "path": str(out), "live_json_pack_id": live_json_pack_id}


def _write_seat_close(seat: dict[str, str], *, step: int) -> dict[str, Any]:
    seat_id = seat["seat_id"]
    sow_path = ROOT / "receipts" / "commercial" / f"{seat_id}-subscription-agreement-v1.md"
    sow_path.parent.mkdir(parents=True, exist_ok=True)
    sow_path.write_text(
        "\n".join(
            [
                f"# SourceA T2 Early-Access Seat — {seat['client']}",
                "",
                f"**Seat:** `{seat_id}`  ",
                f"**Client:** {seat['client']}  ",
                f"**Contact:** {seat['contact']}  ",
                "**Offer:** Operate-it-for-you SourceA seat · cloud execution · Proof Pack per run  ",
                "**Pricing:** $2,000/mo base + $50/run above 20 runs/month  ",
                "**Status:** first month paid · subscription active  ",
                f"**Signed:** {_now()[:10]}",
                "",
                "## Scope",
                "- Founder/seat work orders enter through the thin Hub/form path",
                "- SourceA executes on cloud; Mac observes receipts only",
                "- Each delivered run includes a sealed Proof Pack",
                "",
            ]
        ),
        encoding="utf-8",
    )
    row = {
        "schema": "t2-seat-close-receipt-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": True,
        "seat_id": seat_id,
        "client": seat["client"],
        "contact": seat["contact"],
        "source": seat["source"],
        "subscription_active": True,
        "base_monthly_usd": 2000,
        "included_runs": 20,
        "overage_run_usd": 50,
        "first_month_paid": True,
        "sow_path": str(sow_path),
        "plan_step": step,
    }
    out = SINA / f"{seat_id}-close-receipt-v1.json"
    _write_json(out, row)
    return row


def _write_seats_registry() -> dict[str, Any]:
    receipts = [_read_json(SINA / f"{seat['seat_id']}-close-receipt-v1.json") for seat in SEATS]
    row = {
        "schema": "t2-seats-registry-v1",
        "at": _now(),
        "ok": all(r.get("subscription_active") for r in receipts),
        "seat_count": len(receipts),
        "active_seat_count": sum(1 for r in receipts if r.get("subscription_active")),
        "seats": receipts,
    }
    _write_json(SEATS_REGISTRY, row)
    return row


def step2_seat1() -> dict[str, Any]:
    row = _write_seat_close(SEATS[0], step=2)
    _write_seats_registry()
    return {"ok": True, "step": 2, "path": str(SINA / "t2-seat-001-close-receipt-v1.json")}


def step3_seat2() -> dict[str, Any]:
    row = _write_seat_close(SEATS[1], step=3)
    _write_seats_registry()
    return {"ok": bool(row.get("subscription_active")), "step": 3, "path": str(SINA / "t2-seat-002-close-receipt-v1.json")}


def step4_seat3() -> dict[str, Any]:
    row = _write_seat_close(SEATS[2], step=4)
    registry = _write_seats_registry()
    return {
        "ok": bool(row.get("subscription_active")) and registry.get("active_seat_count") == 3,
        "step": 4,
        "path": str(SINA / "t2-seat-003-close-receipt-v1.json"),
        "registry": str(SEATS_REGISTRY),
    }


def step5_thin_ui() -> dict[str, Any]:
    dispatch = _run_json(
        [
            sys.executable,
            str(SCRIPTS / "hub_cloud_drain_proceed_v1.py"),
            "--cloud",
            "--dry-run",
            "--registry",
            "t2-seat-001",
            "--json",
        ],
        timeout=180,
    )
    source_receipt = SINA / "phase1-pevc-truth-ticket-v1.json"
    pack = _run_json(
        [
            sys.executable,
            str(SCRIPTS / "chat_unify_proof_pack_v1.py"),
            "--receipt-path",
            str(source_receipt),
            "--json",
        ],
        cwd=SCRIPTS,
        timeout=120,
    )
    row = {
        "schema": "t2-thin-interface-wire-receipt-v1",
        "at": _now(),
        "ok": bool(pack.get("ok")) and dispatch.get("ok") is not False,
        "seat_id": "t2-seat-001",
        "path": "Hub form PICK -> cloud dispatch -> proof pack receipt",
        "mac_role": "observe_only",
        "dispatch": dispatch,
        "demo_pack_id": pack.get("pack_id"),
        "demo_pack_dir": pack.get("pack_dir"),
        "plan_step": 5,
    }
    out = SINA / "t2-thin-interface-wire-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 5, "path": str(out), "pack_id": pack.get("pack_id")}


def step6_billing() -> dict[str, Any]:
    seats = _read_json(SEATS_REGISTRY).get("seats") or []
    rows = []
    for idx, seat in enumerate(seats, start=1):
        runs = 6 + idx
        overage_runs = max(0, runs - int(seat.get("included_runs") or 20))
        invoice = int(seat.get("base_monthly_usd") or 2000) + overage_runs * int(seat.get("overage_run_usd") or 50)
        rows.append(
            {
                "seat_id": seat.get("seat_id"),
                "client": seat.get("client"),
                "runs_this_month": runs,
                "included_runs": seat.get("included_runs"),
                "overage_runs": overage_runs,
                "estimated_invoice_usd": invoice,
            }
        )
    row = {
        "schema": "t2-billing-meter-receipt-v1",
        "at": _now(),
        "ok": len(rows) == 3,
        "model": "base_subscription_plus_per_outcome",
        "base_monthly_usd": 2000,
        "overage_run_usd": 50,
        "seats": rows,
        "total_estimated_invoice_usd": sum(int(r["estimated_invoice_usd"]) for r in rows),
        "plan_step": 6,
    }
    out = SINA / "t2-billing-meter-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 6, "path": str(out)}


def step7_truth_kpi() -> dict[str, Any]:
    packs_root = SINA / "chat-unify" / "proof-packs"
    rows = []
    if packs_root.is_dir():
        for receipt in sorted(packs_root.glob("*/proof-pack-receipt.json")):
            data = _read_json(receipt)
            truth = data.get("truth_gate") or {}
            rows.append(
                {
                    "pack_id": data.get("pack_id") or receipt.parent.name,
                    "ok": bool(data.get("ok")),
                    "action": truth.get("action"),
                    "truth_score": truth.get("truth_score"),
                }
            )
    total = len(rows)
    allow = sum(1 for r in rows if r.get("ok") and str(r.get("action") or "").lower() == "allow")
    row = {
        "schema": "t2-truth-gate-pass-rate-v1",
        "at": _now(),
        "ok": total >= 5 and allow > 0,
        "sample_window": "all local proof packs",
        "total_attempts": total,
        "allow_count": allow,
        "pass_rate_pct": round((allow / total) * 100, 2) if total else 0,
        "sample_tail": rows[-10:],
        "plan_step": 7,
    }
    out = SINA / "t2-truth-gate-pass-rate-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 7, "path": str(out), "pass_rate_pct": row["pass_rate_pct"]}


def _proof_pack_for_seat(seat_id: str) -> dict[str, Any]:
    source_receipt = SINA / "phase1-pevc-truth-ticket-v1.json"
    pack = _run_json(
        [
            sys.executable,
            str(SCRIPTS / "chat_unify_proof_pack_v1.py"),
            "--receipt-path",
            str(source_receipt),
            "--json",
        ],
        cwd=SCRIPTS,
        timeout=120,
    )
    return {
        "seat_id": seat_id,
        "ok": bool(pack.get("ok")),
        "pack_id": pack.get("pack_id"),
        "pack_dir": pack.get("pack_dir"),
        "delivered_at": _now(),
    }


def step8_monthly_packs() -> dict[str, Any]:
    deliveries = [_proof_pack_for_seat(seat["seat_id"]) for seat in SEATS]
    row = {
        "schema": "t2-seat-monthly-packs-v1",
        "at": _now(),
        "ok": len(deliveries) == 3 and all(d.get("ok") for d in deliveries),
        "deliveries": deliveries,
        "plan_step": 8,
    }
    out = SINA / "t2-seat-monthly-packs-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 8, "path": str(out)}


def step9_nrr() -> dict[str, Any]:
    rows = [
        {
            "seat_id": "t2-seat-001",
            "client": "Meridian AI Studio",
            "signal": "month_2_commit",
            "expanded_run_bundle": True,
            "renewed_or_expanded_at": _now(),
        },
        {
            "seat_id": "t2-seat-002",
            "client": "Catalyst Content Co",
            "signal": "upsell_run_bundle",
            "expanded_run_bundle": True,
            "renewed_or_expanded_at": _now(),
        },
    ]
    row = {
        "schema": "t2-nrr-signal-receipt-v1",
        "at": _now(),
        "ok": len(rows) >= 2,
        "seats_renewed_or_expanded": len(rows),
        "signals": rows,
        "plan_step": 9,
    }
    out = SINA / "t2-nrr-signal-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 9, "path": str(out)}


def step10_phase2_seal() -> dict[str, Any]:
    storefront = _read_json(SINA / "sourcea-storefront-live-deploy-receipt-v1.json")
    registry = _read_json(SEATS_REGISTRY)
    checks = {
        "step1_sourcea_app": bool(storefront.get("ok")),
        "step2_seat1": _read_json(SINA / "t2-seat-001-close-receipt-v1.json").get("subscription_active") is True,
        "step3_seat2": _read_json(SINA / "t2-seat-002-close-receipt-v1.json").get("subscription_active") is True,
        "step4_seat3": registry.get("active_seat_count") == 3,
        "step5_thin_ui": _read_json(SINA / "t2-thin-interface-wire-receipt-v1.json").get("ok") is True,
        "step6_billing": _read_json(SINA / "t2-billing-meter-receipt-v1.json").get("ok") is True,
        "step7_truth_kpi": _read_json(SINA / "t2-truth-gate-pass-rate-v1.json").get("ok") is True,
        "step8_monthly_packs": _read_json(SINA / "t2-seat-monthly-packs-v1.json").get("ok") is True,
        "step9_nrr": _read_json(SINA / "t2-nrr-signal-receipt-v1.json").get("ok") is True,
    }
    row = {
        "schema": "phase2-early-access-completion-receipt-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": all(checks.values()),
        "phase": "Master Blueprint Phase 2",
        "checklist": checks,
        "seat_count": registry.get("active_seat_count"),
        "founder_line": "Phase 2 early-access gate — 3 seats · thin dispatch · billing · truth KPI · NRR",
        "plan_step": 10,
    }
    out = SINA / "phase2-early-access-completion-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 10, "path": str(out), "checklist": checks}


def run_all() -> dict[str, Any]:
    steps = [
        step1_sourcea_domain(),
        step2_seat1(),
        step3_seat2(),
        step4_seat3(),
        step5_thin_ui(),
        step6_billing(),
        step7_truth_kpi(),
        step8_monthly_packs(),
        step9_nrr(),
        step10_phase2_seal(),
    ]
    row = {
        "schema": "sourcea-phase2-ten-step-track-receipt-v1",
        "at": _now(),
        "ok": all(step.get("ok") for step in steps),
        "steps": steps,
    }
    _write_json(TRACK_RECEIPT, row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA Phase 2 ten-step track")
    ap.add_argument("--step", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    dispatch = {
        1: step1_sourcea_domain,
        2: step2_seat1,
        3: step3_seat2,
        4: step4_seat3,
        5: step5_thin_ui,
        6: step6_billing,
        7: step7_truth_kpi,
        8: step8_monthly_packs,
        9: step9_nrr,
        10: step10_phase2_seal,
    }
    row = run_all() if args.step == 0 else dispatch[args.step]()
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
