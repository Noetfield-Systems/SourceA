#!/usr/bin/env python3
"""Verify SourceA autorun is fully autonomous — scheduled receipts, zero manual ticks.

Checks (default 24h window):
  1. CF cron CRON_FIRED truth_log rows (~6/hour at */10)
  2. Railway cycle receipts — trigger_source cloudflare_cron only (no manual)
  3. Every cycle receipt has sink_invariant; mismatch → BLOCKED_WITH_REASON
  4. Daily heartbeat receipt present for UTC today
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_CONFIG = ROOT / "data" / "cloud-auto-runtime-v1.json"
KAIZEN_DIR = ROOT / "receipts" / "cloud" / "kaizen"
KAIZEN_RECEIPT = KAIZEN_DIR / "kaizen-autorun-health-miss-latest-v1.json"
CF_HEALTH = "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
OBSERVER = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1"
AUTONOMOUS = frozenset({"cloudflare_cron", "cloudflare_scheduled", "headless_cloud_auto_tick"})
MANUAL_MARKERS = frozenset({"manual", "mac_auto_tick", "hub_proceed", "founder"})
AUTONOMY_VERDICTS = frozenset({"IDLE_NO_WORK", "BLOCKED_WITH_REASON"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _fetch_json(url: str, *, timeout: float = 30.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "verify-autorun-zero-manual/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"ok": False, "http_code": exc.code, "error": body[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _parse_iso(iso: str) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_workflow_config() -> dict[str, Any]:
    if not WORKFLOW_CONFIG.is_file():
        return {}
    try:
        return json.loads(WORKFLOW_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_kaizen_receipt(*, row: dict[str, Any], scores: dict[str, int], threshold_pct: int) -> None:
    if row.get("ok") and scores.get("score_pct", 0) >= threshold_pct:
        return
    receipt = {
        "schema": "kaizen-improvement-receipt-v1",
        "version": "1.0.0",
        "at": _now(),
        "law": "controlled-autorun L4/L13 · workflow-health miss",
        "classification": "machine_safe",
        "id": "kaizen-autorun-health-miss",
        "diff_summary": "Autorun health now files a Kaizen proof receipt on SLO miss or drift.",
        "expected_effect": "Keep heartbeat and zero-manual regressions visible in the live demo.",
        "expected_roi": "faster workflow recovery · tighter health telemetry",
        "rollback_command": "remove the Kaizen receipt writer from scripts/verify_autorun_zero_manual_v1.py",
        "files_touched": ["scripts/verify_autorun_zero_manual_v1.py", "data/cloud-auto-runtime-v1.json"],
        "before": "SLO misses only surfaced in console output.",
        "after": "SLO misses also file a Kaizen proof receipt under receipts/cloud/kaizen.",
        "score_pct": scores.get("score_pct"),
        "threshold_pct": threshold_pct,
        "heartbeat_score_pct": scores.get("heartbeat_score_pct"),
        "drift": not bool(row.get("ok")),
        "ok": bool(row.get("ok")),
    }
    KAIZEN_DIR.mkdir(parents=True, exist_ok=True)
    KAIZEN_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def _truth_log_cron_count(*, since: datetime) -> dict[str, Any]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    if not url or not key:
        return {"ok": False, "skipped": True, "error": "supabase_not_configured"}
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = urllib.parse.urlencode(
        {
            "select": "id,created_at,event,source,queue_head",
            "event": "eq.CRON_FIRED",
            "source": "eq.cloudflare_cron",
            "created_at": f"gte.{since_iso}",
            "order": "created_at.desc",
        }
    )
    req_url = f"{url.rstrip('/')}/rest/v1/truth_log?{params}"
    req = urllib.request.Request(
        req_url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Prefer": "count=exact",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(body) if body.strip() else []
            count_hdr = resp.headers.get("Content-Range", "")
            total = None
            if "/" in count_hdr:
                try:
                    total = int(count_hdr.split("/")[-1])
                except ValueError:
                    total = len(rows)
            return {
                "ok": True,
                "count": total if total is not None else len(rows),
                "sample": rows[:3],
                "since": since_iso,
            }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _load_local_cycles(limit: int = 200) -> list[dict[str, Any]]:
    dirs = [
        ROOT / "receipts" / "cloud" / "autonomous-forge-run-cycles",
        Path.home() / ".sina" / "autonomous-forge-run-cycle-receipts",
    ]
    paths: list[Path] = []
    for d in dirs:
        if d.is_dir():
            paths.extend(sorted(d.glob("cycle-*.json")))
    out: list[dict[str, Any]] = []
    for p in paths[-limit:]:
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def _heartbeat_today_local() -> dict[str, Any]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    paths = [
        ROOT / "receipts" / "cloud" / "autonomous-forge-run-heartbeat" / f"heartbeat-{today}-v1.json",
        Path.home() / ".sina" / "autonomous-forge-run-daily-heartbeat-v1.json",
    ]
    for p in paths:
        if p.is_file():
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
                return {"ok": True, "path": str(p), "doc": doc}
            except (OSError, json.JSONDecodeError):
                continue
    return {"ok": False, "error": "no_heartbeat_today", "date": today}


def verify(*, hours: float = 24.0) -> dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    expected_min_cron = int((hours * 60) / 10) - 2  # */10 cadence, tolerance
    workflow_cfg = _load_workflow_config()
    slo_targets = workflow_cfg.get("slo_targets") if isinstance(workflow_cfg.get("slo_targets"), dict) else {}
    threshold_pct = int(slo_targets.get("score_pass_threshold_pct") or 90)

    cf = _fetch_json(CF_HEALTH)
    observer = _fetch_json(OBSERVER)
    truth = _truth_log_cron_count(since=since)
    heartbeat = _heartbeat_today_local()

    cycles_cloud = _load_local_cycles()
    cycles_observer = observer.get("cycles") or []

    manual_triggers: list[str] = []
    missing_sink: list[str] = []
    sink_blocked: list[str] = []
    idle_no_work = 0
    scheduled_in_window = 0
    observer_in_window = 0

    for doc in cycles_cloud:
        at = _parse_iso(str(doc.get("at") or ""))
        if at and at < since:
            continue
        scheduled_in_window += 1
        src = str(doc.get("trigger_source") or "")
        if src not in AUTONOMOUS or any(m in src for m in MANUAL_MARKERS):
            manual_triggers.append(f"{doc.get('at')}:{src}")
        inv = doc.get("sink_invariant")
        if not isinstance(inv, dict):
            missing_sink.append(str(doc.get("at")))
        elif not inv.get("ok") and not inv.get("skipped"):
            sink_blocked.append(str(doc.get("at")))
        verdict = (doc.get("decision") or {}).get("verdict")
        if verdict == "IDLE_NO_WORK":
            idle_no_work += 1

    autonomy_observer: list[dict[str, Any]] = []
    for c in cycles_observer:
        at = _parse_iso(str(c.get("at") or ""))
        if at and at < since:
            continue
        observer_in_window += 1
        src = str(c.get("trigger_source") or "")
        verdict = str(c.get("verdict") or "")
        if src not in AUTONOMOUS or any(m in src for m in MANUAL_MARKERS):
            manual_triggers.append(f"{c.get('at')}:{src}:observer")
        if verdict in AUTONOMY_VERDICTS:
            autonomy_observer.append(c)
        if c.get("sink_invariant") is None and verdict in AUTONOMY_VERDICTS:
            missing_sink.append(f"{c.get('at')}:observer_no_sink_field")
        inv = c.get("sink_invariant")
        if isinstance(inv, dict) and not inv.get("ok") and not inv.get("skipped"):
            sink_blocked.append(str(c.get("at")))

    latest_autonomy = None
    if autonomy_observer:
        latest_autonomy = max(
            autonomy_observer,
            key=lambda row: _parse_iso(str(row.get("at") or "")) or datetime.min.replace(tzinfo=timezone.utc),
        )
    latest_inv = (latest_autonomy or {}).get("sink_invariant")
    latest_sink_ok = isinstance(latest_inv, dict) and bool(latest_inv.get("ok") or latest_inv.get("skipped"))

    cron_ok = truth.get("ok") and int(truth.get("count") or 0) >= max(1, expected_min_cron // 2)
    if truth.get("skipped"):
        cron_ok = cf.get("ok") and cf.get("auto_proceed_ready") and observer_in_window >= 1

    zero_manual = len(manual_triggers) == 0
    sink_every_cycle = len(missing_sink) == 0 and (latest_sink_ok if latest_autonomy else len(sink_blocked) == 0)
    heartbeat_ok = heartbeat.get("ok") or bool(observer.get("daily_heartbeat"))

    scores = {
        "cron_score_pct": min(100, round(100 * int(truth.get("count") or 0) / max(1, expected_min_cron))),
        "zero_manual_score_pct": 100 if zero_manual else 0,
        "sink_score_pct": 100 if sink_every_cycle else 0,
        "heartbeat_score_pct": 100 if heartbeat_ok else 0,
    }
    score_pct = round(sum(scores.values()) / len(scores))
    slo_ok = score_pct >= threshold_pct

    ok = (
        cf.get("ok")
        and observer.get("ok")
        and zero_manual
        and sink_every_cycle
        and heartbeat_ok
        and slo_ok
    )
    row = {
        "schema": "autorun-zero-manual-verify-v1",
        "version": "1.0.0",
        "at": _now(),
        "commit_sha": _git_sha(),
        "window_hours": hours,
        "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "score_pct": score_pct,
        "threshold_pct": threshold_pct,
        "heartbeat_score_pct": scores["heartbeat_score_pct"],
        "scores": scores,
        "slo_targets": slo_targets,
        "ok": ok,
        "cf_cron": {
            "health": cf,
            "expected_min_fires": max(1, expected_min_cron),
            "truth_log": truth,
            "pass": cron_ok,
            "score_pct": scores["cron_score_pct"],
        },
        "zero_manual_proof": {
            "cycles_in_window": scheduled_in_window,
            "observer_cycles_in_window": observer_in_window,
            "manual_triggers": manual_triggers[:20],
            "pass": zero_manual,
            "score_pct": scores["zero_manual_score_pct"],
        },
        "sink_invariant": {
            "missing_on_cycles": missing_sink[:20],
            "blocked_cycles": sink_blocked[:20],
            "pass": sink_every_cycle,
            "score_pct": scores["sink_score_pct"],
        },
        "idle_no_work_receipts": idle_no_work,
        "daily_heartbeat": heartbeat,
        "observer_tail": cycles_observer[:5],
        "report_line": (
            f"autorun {'PASS' if ok else 'FAIL'} · score={score_pct}% · heartbeat={scores['heartbeat_score_pct']}% · "
            f"sha { _git_sha()[:8] } · cron_fires={truth.get('count', 'n/a')} · cycles={scheduled_in_window} · obs={observer_in_window} · "
            f"manual={len(manual_triggers)}"
        ),
    }
    _write_kaizen_receipt(row=row, scores={**scores, 'score_pct': score_pct}, threshold_pct=threshold_pct)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    row = verify(hours=args.hours)
    if args.write_receipt:
        out = Path.home() / ".sina" / "autorun-zero-manual-verify-v1.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
