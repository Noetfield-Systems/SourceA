#!/usr/bin/env python3
"""Auto-note autorun pending blockers — every cycle, no manual founder reminder.

Law: CONTROLLED_AUTORUN_LAWS_v2 L3/L4/L12 — pending = {decision, reason, evidence}.
Receipt: receipts/cloud/autorun-pending/pending-latest-v1.json
Mirror: ~/.sina/autorun-pending-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
EXTERNAL_VERIFY_DIR = ROOT / "receipts" / "cloud" / "external-verify"
PENDING_DIR = ROOT / "receipts" / "cloud" / "autorun-pending"
CYCLE_DIR_REPO = ROOT / "receipts" / "cloud" / "autonomous-forge-run-cycles"
CYCLE_DIR_MAC = SINA / "autonomous-forge-run-cycle-receipts"
PENDING_RECEIPT = PENDING_DIR / "pending-latest-v1.json"
PENDING_MIRROR = SINA / "autorun-pending-v1.json"
GITHUB_ACTIONS_EXTERNAL_VERIFY = (
    "https://github.com/noetfield-systems/sourcea/actions/workflows/external-verify.yml"
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


def _write(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _parse_iso(iso: str) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    if not url or not key:
        spine = Path.home() / ".sourcea-secrets" / "portfolio-spine.env"
        if spine.is_file():
            for line in spine.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == "SUPABASE_URL" and not url:
                    url = v
                if k == "SUPABASE_SERVICE_ROLE_KEY" and not key:
                    key = v
    return {"url": url, "key": key}


def _latest_external_verify_truth_log(*, since: datetime) -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"found": False, "error": "supabase_not_configured"}
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = urllib.parse.urlencode(
        {
            "select": "id,recorded_at,event,source,receipt_id,payload",
            "source": "eq.github_actions",
            "event": "eq.EXTERNAL_VERIFY_PASS",
            "recorded_at": f"gte.{since_iso}",
            "order": "recorded_at.desc",
            "limit": "1",
        }
    )
    req_url = f"{cfg['url'].rstrip('/')}/rest/v1/truth_log?{params}"
    req = urllib.request.Request(
        req_url,
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            if not rows:
                return {"found": False, "source": "supabase_truth_log"}
            row = rows[0]
            payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
            return {
                "found": True,
                "source": "supabase_truth_log",
                "truth_log_id": row.get("id"),
                "at": row.get("recorded_at"),
                "ok": True,
                "github_run_id": payload.get("github_run_id"),
                "run_url": payload.get("run_url"),
                "conclusion": payload.get("conclusion"),
            }
    except Exception as exc:
        return {"found": False, "error": str(exc)[:200], "source": "supabase_truth_log"}


def _latest_external_verify_disk() -> dict[str, Any]:
    if not EXTERNAL_VERIFY_DIR.is_dir():
        return {"found": False, "path": str(EXTERNAL_VERIFY_DIR)}
    paths = sorted(EXTERNAL_VERIFY_DIR.glob("external-verify-*-v1.json"))
    if not paths:
        return {"found": False, "path": str(EXTERNAL_VERIFY_DIR)}
    latest = paths[-1]
    doc = _read(latest)
    return {
        "found": True,
        "path": str(latest),
        "ok": bool(doc.get("ok")),
        "at": doc.get("at"),
        "github_run_id": doc.get("github_run_id"),
        "github_sha": doc.get("github_sha"),
        "run_url": doc.get("run_url"),
    }


def _latest_external_verify_receipt() -> dict[str, Any]:
    """L4 PASS = Supabase truth_log only; disk is mirror evidence."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    truth = _latest_external_verify_truth_log(since=since)
    if truth.get("found"):
        return truth
    disk = _latest_external_verify_disk()
    if disk.get("found"):
        return {**disk, "mirror_only": True, "l4_pass": False}
    return disk


def _pending_external_verify_evidence() -> dict[str, Any]:
    return _latest_external_verify_receipt()


def _latest_cycle_schema() -> dict[str, Any]:
    paths: list[Path] = []
    for d in (CYCLE_DIR_REPO, CYCLE_DIR_MAC):
        if d.is_dir():
            paths.extend(sorted(d.glob("cycle-*.json")))
    if not paths:
        return {"found": False}
    latest = paths[-1]
    doc = _read(latest)
    return {
        "found": True,
        "path": str(latest),
        "schema": doc.get("schema"),
        "at": doc.get("at"),
        "v2": str(doc.get("schema") or "").endswith("-v2"),
    }


def _drift_pending() -> dict[str, Any] | None:
    import subprocess

    committed_sha = "unknown"
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            committed_sha = proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    live_railway_sha = (
        os.environ.get("RAILWAY_GIT_COMMIT_SHA", "").strip()
        or os.environ.get("GIT_COMMIT_SHA", "").strip()
        or os.environ.get("SOURCE_VERSION", "").strip()
    )
    if live_railway_sha and committed_sha not in ("unknown", "") and live_railway_sha[:12] != committed_sha[:12]:
        return {
            "id": "drift_railway_deploy",
            "status": "pending",
            "severity": "P1",
            "law": "L12",
            "reason": "railway_deploy mismatch — committed vs deployed truth diverged",
            "evidence": {
                "command": "git rev-parse HEAD vs RAILWAY_GIT_COMMIT_SHA",
                "exit_code": 0,
                "output": json.dumps(
                    {"committed_sha": committed_sha[:12], "live_railway_sha": live_railway_sha[:12]}
                )[:400],
                "committed_sha": committed_sha,
                "live_railway_sha": live_railway_sha,
            },
            "action": "deploy motor to committed SHA or reconcile drift receipt",
        }
    return None


def pending_snapshot(*, max_age_hours: float = 24.0) -> dict[str, Any]:
    """Collect all auto-noted pending items — no manual founder reminder."""
    items: list[dict[str, Any]] = []
    since = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    ev = _latest_external_verify_receipt()
    ev_ok = (
        ev.get("source") == "supabase_truth_log"
        and ev.get("found")
        and ev.get("ok")
    )
    if not ev_ok:
        items.append(
            {
                "id": "external_verify_l4",
                "status": "pending",
                "severity": "P0",
                "law": "L4",
                "reason": (
                    "no_EXTERNAL_VERIFY_PASS_in_supabase_truth_log"
                    if not ev.get("found")
                    else "external_verify_truth_log_stale_or_not_ok"
                ),
                "evidence": {
                    "command": "GET /rest/v1/truth_log?event=eq.EXTERNAL_VERIFY_PASS",
                    "exit_code": 0 if ev.get("found") else 1,
                    "output": json.dumps(ev)[:400],
                    "truth_log_id": ev.get("truth_log_id"),
                    "run_url": ev.get("run_url"),
                },
                "action": "machine: read_action_runs_v1.py --dispatch --wait · sink auto-updates on PASS",
            }
        )

    drift_item = _drift_pending()
    if drift_item:
        items.append(drift_item)

    cycle = _latest_cycle_schema()
    if cycle.get("found") and not cycle.get("v2"):
        items.append(
            {
                "id": "cycle_receipt_schema_v2",
                "status": "pending",
                "severity": "P2",
                "law": "Tier0-3",
                "reason": "latest_cycle_not_v2_schema",
                "evidence": {
                    "command": f"read {cycle.get('path')}",
                    "exit_code": 0,
                    "output": str(cycle.get("schema")),
                },
                "action": "Railway motor deploy picks up cycle receipt v2 writer",
            }
        )

    if not (ROOT / ".github/workflows/external-verify.yml").is_file():
        items.append(
            {
                "id": "external_verify_workflow_missing",
                "status": "pending",
                "severity": "P0",
                "law": "L4",
                "reason": "external-verify.yml not logged",
                "evidence": {"path": ".github/workflows/external-verify.yml"},
                "action": "restore workflow",
            }
        )

    oldest_age_seconds = 0
    if items:
        oldest_age_seconds = 0

    row = {
        "schema": "autorun-pending-v1",
        "version": "1.0.0",
        "at": _now(),
        "count": len(items),
        "p0_count": sum(1 for i in items if i.get("severity") == "P0"),
        "items": items,
        "oldest_id": items[0]["id"] if items else "",
        "age_seconds": oldest_age_seconds,
        "ok": len(items) == 0,
        "report_line": (
            f"pending=0 · autorun clear"
            if not items
            else f"pending={len(items)} · P0={sum(1 for i in items if i.get('severity')=='P0')} · "
            f"head={items[0]['id']} · {items[0].get('reason')}"
        ),
    }
    return row


def write_pending_receipt(*, max_age_hours: float = 24.0) -> dict[str, Any]:
    row = pending_snapshot(max_age_hours=max_age_hours)
    _write(PENDING_RECEIPT, row)
    _write(PENDING_MIRROR, row)
    row["receipt_path"] = str(PENDING_RECEIPT)
    row["mirror_path"] = str(PENDING_MIRROR)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=24.0, help="external verify freshness window")
    ap.add_argument("--write", action="store_true", help="write pending-latest receipt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = write_pending_receipt(max_age_hours=args.hours) if args.write else pending_snapshot(max_age_hours=args.hours)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
