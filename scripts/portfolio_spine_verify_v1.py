#!/usr/bin/env python3
"""Portfolio-spine verify loop — REAL buyer-proof + recipe-queue verification on cron.

Closes the spine gap found 2026-07-12: cycle_receipts rows for buyer-proof-verify and
recipe-queue-builder had NO scheduled writer (kept alive only by one-shot repairs), so the
NOOS control panel flagged them BLOCKED/stale every 30 minutes.

Law (L2 honesty): verdicts here come from running the actual checks each tick —
verify_buyer_proof_hotfix_v1 (raw external HTTPS fetch of public buyer surfaces) and a
client-proof recipe-queue integrity check. GREEN is earned per run, never manufactured;
check failure writes a RED row (visible on the panel), and missing Supabase config returns
BLOCKED without writing anything.

Dispatched via CF cron */15 -> FBE /api/fbe/portfolio-spine/verify/v1 (loop-specialist
dispatch table). Runnable manually: python3 scripts/portfolio_spine_verify_v1.py --json
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECIPE_QUEUE = ROOT / "data" / "client-proof-recipe-queue-v1.json"
RECIPE_RUBRIC = ROOT / "data" / "client-proof-recipe-rubric-v1.json"
VERIFY_TIMEOUT_SEC = int(os.environ.get("SPINE_VERIFY_TIMEOUT_SEC", "180"))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def spine_cfg() -> tuple[str, str] | None:
    """Supabase target for cycle_receipts. Same env contract as the NOOS spine heartbeat."""
    url = (
        os.environ.get("PORTFOLIO_SPINE_SUPABASE_URL", "").strip()
        or os.environ.get("SUPABASE_URL", "").strip()
    )
    key = (
        os.environ.get("PORTFOLIO_SPINE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    if not url or not key:
        return None
    return url.rstrip("/"), key


def supabase_post(base: str, key: str, table: str, row: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        f"{base}/rest/v1/{table}",
        data=json.dumps(row).encode("utf-8"),
        method="POST",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"ok": 200 <= resp.status < 300, "status": resp.status}
    except Exception as exc:  # noqa: BLE001 — recorded, never raised past the loop
        return {"ok": False, "error": str(exc)[:200]}


def check_buyer_proof() -> dict[str, Any]:
    """Run the LAW-authoritative external buyer-proof checks (raw HTTPS fetch of the PUBLIC
    hostnames). Container-safe: the workspace-hygiene parts of verify_all (dist greps,
    repo-script gates) stay owned by the GHA external-verify path and are NOT re-run here."""
    started = time.monotonic()
    try:
        from verify_buyer_proof_hotfix_v1 import verify_eval_live, verify_proof_live  # noqa: WPS433

        hosts = ("https://sourcea.app", "https://www.sourcea.app")
        rows = {}
        for host in hosts:
            rows[host] = {"eval": verify_eval_live(host), "proof": verify_proof_live(host)}
        fails = [
            f"{host}:{kind}"
            for host, pair in rows.items()
            for kind, row in pair.items()
            if not row.get("ok")
        ]
        ok = not fails
        detail = "" if ok else "live check failed: " + ",".join(fails)
    except Exception as exc:  # noqa: BLE001 — a broken import/transport is a RED verdict, never a crash
        ok, detail = False, f"buyer-proof verify unavailable: {exc}"
    return {"ok": ok, "detail": detail[:300], "duration_ms": int((time.monotonic() - started) * 1000)}


def check_recipe_queue() -> dict[str, Any]:
    """Integrity check of the curated client-proof recipe queue (read-only)."""
    started = time.monotonic()
    ok, detail = False, ""
    try:
        if not RECIPE_QUEUE.is_file():
            detail = f"missing {RECIPE_QUEUE.name}"
        elif not RECIPE_RUBRIC.is_file():
            detail = f"missing {RECIPE_RUBRIC.name}"
        else:
            data = json.loads(RECIPE_QUEUE.read_text(encoding="utf-8"))
            items = data.get("items") or data.get("queue") or (data if isinstance(data, list) else [])
            if not items:
                detail = "recipe queue empty"
            else:
                ok = True
                detail = f"{len(items)} recipes"
    except (OSError, json.JSONDecodeError) as exc:
        detail = f"queue unreadable: {exc}"[:200]
    return {"ok": ok, "detail": detail[:300], "duration_ms": int((time.monotonic() - started) * 1000)}


def build_cycle_row(*, execution_id: str, check: dict[str, Any], now: str) -> dict[str, Any]:
    verdict = "GREEN" if check["ok"] else "RED"
    return {
        "cycle_id": f"cycle-{execution_id}-{now}",
        "execution_id": execution_id,
        "verdict": verdict,
        "trigger_source": "cloudflare_cron",
        "queue_head_before": None,
        "queue_head_after": None,
        "created_at": now,
        "started_at": now,
        "finished_at": now,
        "duration_ms": max(1, int(check.get("duration_ms") or 1)),
    }


def run(body: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = spine_cfg()
    if not cfg:
        return {
            "schema": "portfolio-spine-verify-v1",
            "ok": False,
            "status": "BLOCKED",
            "blocker": "portfolio_spine_supabase_not_configured",
            "at": utc_now(),
        }
    base, key = cfg
    now = utc_now()
    buyer = check_buyer_proof()
    recipe = check_recipe_queue()
    writes = {
        "buyer_proof": supabase_post(
            base, key, "cycle_receipts",
            build_cycle_row(execution_id="buyer-proof-hotfix-verify-v1", check=buyer, now=now),
        ),
        "recipe_queue": supabase_post(
            base, key, "cycle_receipts",
            build_cycle_row(execution_id="client-proof-recipe-queue-v1", check=recipe, now=now),
        ),
    }
    ok = all(w.get("ok") for w in writes.values())
    return {
        "schema": "portfolio-spine-verify-v1",
        "ok": ok,
        "at": now,
        "checks": {
            "buyer_proof": {"verdict": "GREEN" if buyer["ok"] else "RED", "detail": buyer["detail"]},
            "recipe_queue": {"verdict": "GREEN" if recipe["ok"] else "RED", "detail": recipe["detail"]},
        },
        "writes": writes,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="run checks, skip Supabase writes")
    args = ap.parse_args()
    if args.dry_run:
        now = utc_now()
        buyer, recipe = check_buyer_proof(), check_recipe_queue()
        row = {
            "schema": "portfolio-spine-verify-v1",
            "dry_run": True,
            "at": now,
            "buyer_proof": buyer,
            "recipe_queue": recipe,
            "rows_preview": [
                build_cycle_row(execution_id="buyer-proof-hotfix-verify-v1", check=buyer, now=now),
                build_cycle_row(execution_id="client-proof-recipe-queue-v1", check=recipe, now=now),
            ],
        }
    else:
        row = run({})
    print(json.dumps(row, indent=2) if args.json else ("PASS" if row.get("ok") or row.get("dry_run") else "FAIL"))
    return 0 if (row.get("ok") or row.get("dry_run")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
