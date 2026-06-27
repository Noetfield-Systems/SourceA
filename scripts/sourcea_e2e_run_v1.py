#!/usr/bin/env python3
"""SourceA E2E run orchestrator — read-before · bundle run · write-after report.

Law: brain-os/law/enforcement/SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md
Registry: data/sourcea-e2e-check-registry-v1.json
Last report: ~/.sina/sourcea-e2e-last-report-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
REGISTRY = ROOT / "data" / "sourcea-e2e-check-registry-v1.json"
OVERRIDES = ROOT / "data" / "sourcea-e2e-check-registry-overrides-v1.json"
LAST_REPORT = SINA / "sourcea-e2e-last-report-v1.json"
WEEKLY_RECEIPT = SINA / "sourcea-e2e-weekly-checklist-receipt-v1.json"
LOG_DIR = SINA / "e2e-logs"
ARCHIVE_DIR = ROOT / "receipts" / "e2e-reports"
AUDIT_DIR = ROOT / "docs" / "system-audits"
SCHEMA = "sourcea-e2e-last-report-v1"

CADENCE_HOURS = {"daily": 24, "weekly": 24 * 7, "monthly": 24 * 30, "3day": 72}

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _git_head() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (proc.stdout or "").strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _context() -> str:
    try:
        from mac_pipeline_validator_pressure_v1 import founder_session_active, ship_window_open  # noqa: WPS433

        if ship_window_open():
            return "ship_window"
        if founder_session_active():
            return "founder_session"
    except Exception:
        pass
    return "cloud_ci"


def _check_blocked(check: dict[str, Any], ctx: str) -> str | None:
    allowed = check.get("allowed_context") or []
    tier = check.get("unified_tier") or ""
    if ctx == "founder_session" and tier not in ("T0_probe", "T1_fast"):
        return f"blocked: {tier} forbidden during founder session (INCIDENT-039)"
    if ctx == "founder_session" and allowed and "founder_session" not in allowed:
        return "blocked: not allowed during founder session"
    return None


def _gate_script(name: str) -> bool:
    try:
        from founder_session_gate_v1 import check_heavy_gate  # noqa: WPS433

        row = check_heavy_gate(script_name=name)
        return not row.get("blocked")
    except Exception:
        return True


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def _fresh(check_id: str, last: dict, cadence: str, *, force: bool) -> bool:
    if force:
        return False
    hours = CADENCE_HOURS.get(cadence, 24 * 7)
    for c in last.get("checks") or []:
        if c.get("id") != check_id:
            continue
        if not c.get("ok"):
            return False
        at = _parse_ts(c.get("at"))
        if not at:
            return False
        age_h = (datetime.now(timezone.utc) - at).total_seconds() / 3600.0
        return age_h < hours
    return False


def _run_http_probe(probe: dict[str, Any], log_path: Path) -> dict[str, Any]:
    url = str(probe.get("url") or "")
    cid = str(probe.get("id") or "probe")
    lines = [f"=== {cid} {url} {_now()} ==="]
    ok = False
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=8) as resp:
            ok = 200 <= resp.status < 400
            lines.append(f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        lines.append(f"HTTPError {e.code}")
    except Exception as e:
        lines.append(f"FAIL {e}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "id": cid,
        "ok": ok,
        "at": _now(),
        "log": str(log_path),
        "tail": lines[-1],
        "kind": "http_probe",
    }


def _run_script(
    check: dict[str, Any],
    log_path: Path,
    *,
    timeout: int,
) -> dict[str, Any]:
    cid = str(check.get("id") or "")
    script = check.get("script")
    kind = check.get("kind") or "shell"
    if not script:
        return {"id": cid, "ok": False, "at": _now(), "log": "", "tail": "no script", "kind": kind}
    path = ROOT / str(script)
    if kind == "python":
        cmd = [sys.executable, str(path), "--json"]
    else:
        if not _gate_script(path.name):
            return {
                "id": cid,
                "ok": False,
                "at": _now(),
                "log": "",
                "tail": "BLOCKED by founder session gate",
                "kind": kind,
                "blocked": True,
            }
        cmd = ["bash", str(path)]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        log_path.write_text(out, encoding="utf-8")
        tail = out.strip()[-400:] if out.strip() else ""
        return {
            "id": cid,
            "ok": proc.returncode == 0,
            "at": _now(),
            "log": str(log_path),
            "tail": tail,
            "kind": kind,
            "exit": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        log_path.write_text("TIMEOUT\n", encoding="utf-8")
        return {"id": cid, "ok": False, "at": _now(), "log": str(log_path), "tail": "timeout", "kind": kind}


def _run_runner(runner: str, log_path: Path, *, timeout: int) -> dict[str, Any]:
    parts = runner.split()
    if parts[0].endswith(".py"):
        cmd = [sys.executable] + [str(ROOT / p) if not p.startswith("-") else p for p in parts]
        cmd = [sys.executable, str(ROOT / parts[0])] + parts[1:]
    else:
        cmd = ["bash", str(ROOT / parts[0])] + parts[1:]
    if not _gate_script(Path(parts[0]).name):
        return {
            "id": Path(parts[0]).stem,
            "ok": False,
            "at": _now(),
            "log": "",
            "tail": "BLOCKED by founder session gate",
            "blocked": True,
        }
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "") + (proc.stderr or "")
        log_path.write_text(out, encoding="utf-8")
        return {
            "id": Path(parts[0]).stem,
            "ok": proc.returncode == 0,
            "at": _now(),
            "log": str(log_path),
            "tail": out.strip()[-400:],
            "kind": "runner",
            "exit": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"id": Path(parts[0]).stem, "ok": False, "at": _now(), "log": str(log_path), "tail": "timeout"}


def _checks_by_id(registry: dict) -> dict[str, dict]:
    return {str(c.get("id")): c for c in registry.get("checks") or [] if c.get("id")}


def read_last_report() -> dict[str, Any]:
    last = _read(LAST_REPORT)
    stale: list[str] = []
    blockers = list(last.get("blockers") or [])
    registry = _read(REGISTRY)
    now = datetime.now(timezone.utc)
    for c in registry.get("checks") or []:
        cid = str(c.get("id") or "")
        cadence = str(c.get("cadence") or "weekly")
        hours = CADENCE_HOURS.get(cadence, 168)
        found = False
        for prev in last.get("checks") or []:
            if prev.get("id") == cid:
                found = True
                at = _parse_ts(prev.get("at"))
                if not at or (now - at).total_seconds() / 3600.0 > hours:
                    stale.append(cid)
                elif not prev.get("ok"):
                    blockers.append({"check_id": cid, "fail_section": prev.get("tail", "")[:200]})
                break
        if not found and cadence in ("daily", "weekly"):
            stale.append(cid)
    return {
        "schema": "sourcea-e2e-read-last-v1",
        "at": _now(),
        "last_report_path": str(LAST_REPORT),
        "last_exists": LAST_REPORT.is_file(),
        "last_run_id": last.get("run_id"),
        "last_at": last.get("run_id") or last.get("at"),
        "summary": last.get("summary") or {},
        "blockers": blockers,
        "stale_checks": stale[:50],
        "stale_count": len(stale),
        "e2e_last_report_line": _e2e_line(last),
        "next_agent_read": "Read ~/.sina/sourcea-e2e-last-report-v1.json before any E2E re-run",
    }


def _e2e_line(last: dict) -> str:
    if not last:
        return "E2E: no last report — read ~/.sina/sourcea-e2e-last-report-v1.json"
    s = last.get("summary") or {}
    total = s.get("total", "?")
    passed = s.get("pass", "?")
    failed = s.get("fail", 0)
    run_id = last.get("run_id") or "never"
    return f"E2E {run_id}: {passed}/{total} PASS · {failed} FAIL · read {LAST_REPORT}"


def sync_surfaces_line(last: dict) -> None:
    surf_path = SINA / "agent-live-surfaces-v1.json"
    surf = _read(surf_path)
    if not surf:
        surf = {"schema": "agent-live-surfaces-v1"}
    surf["e2e_last_report_line"] = _e2e_line(last)
    surf["e2e_last_report_path"] = str(LAST_REPORT)
    surf["e2e_synced_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    surf_path.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")


def _markdown_report(report: dict) -> str:
    lines = [
        f"# E2E Report — {report.get('run_id')}",
        "",
        f"**Saved:** {_now()}",
        f"**Context:** {report.get('context')} · **Cadence:** {report.get('cadence')}",
        f"**Agent:** {report.get('agent')} · **Role:** {report.get('role')}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
    ]
    s = report.get("summary") or {}
    for k in ("total", "pass", "fail", "skip_fresh", "blocked"):
        lines.append(f"| {k} | {s.get(k, 0)} |")
    lines.extend(["", "## Bundles", ""])
    for b in report.get("bundles") or []:
        status = "PASS" if b.get("ok") else "FAIL"
        lines.append(f"- **{b.get('id')}** — {status} — `{b.get('log', '')}`")
    fails = [c for c in report.get("checks") or [] if not c.get("ok") and not c.get("skipped_fresh")]
    if fails:
        lines.extend(["", "## Failures", ""])
        for c in fails:
            lines.append(f"- `{c.get('id')}` — {c.get('tail', '')[:120]}")
    blockers = report.get("blockers") or []
    if blockers:
        lines.extend(["", "## Blockers", ""])
        for bl in blockers:
            lines.append(f"- `{bl.get('check_id')}` — rule {bl.get('playbook_rule', '?')}")
    lines.extend(["", f"**Next agent:** {report.get('next_agent_read')}", ""])
    return "\n".join(lines)


def write_report(report: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    LAST_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    run_id = str(report.get("run_id") or _now_id())
    archive = ARCHIVE_DIR / f"{run_id}.json"
    archive.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raw_id = run_id.replace("E2E-", "", 1)
    day = raw_id[:10] if len(raw_id) >= 10 and raw_id[4] == "-" else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md_path = AUDIT_DIR / f"E2E_REPORT_{day}.md"
    md_path.write_text(_markdown_report(report), encoding="utf-8")
    if report.get("cadence") == "weekly":
        WEEKLY_RECEIPT.write_text(
            json.dumps(
                {
                    "schema": "sourcea-e2e-weekly-checklist-receipt-v1",
                    "at": _now(),
                    "run_id": run_id,
                    "ok": (report.get("summary") or {}).get("fail", 1) == 0,
                    "report": str(LAST_REPORT),
                    "archive": str(archive),
                    "markdown": str(md_path),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    sync_surfaces_line(report)


def run_bundle(
    bundle_id: str,
    *,
    force: bool = False,
    role: str = "maintainer",
    agent: str | None = None,
    write_report_flag: bool = True,
    cadence: str = "weekly",
) -> dict[str, Any]:
    import time

    t0 = time.time()
    registry = _read(REGISTRY)
    overrides = _read(OVERRIDES)
    bundles = {**(registry.get("bundles") or {}), **(overrides.get("bundles") or {})}
    bdef = bundles.get(bundle_id)
    if not bdef:
        return {"ok": False, "error": f"unknown bundle {bundle_id}"}

    ctx = _context()
    last = _read(LAST_REPORT)
    by_id = _checks_by_id(registry)
    check_results: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    skip_fresh = 0
    ts = _now_id()
    log_bundle = LOG_DIR / f"bundle-{bundle_id}-{ts}.log"

    bundle_ok = True

    if bdef.get("runner_first"):
        runner_log = LOG_DIR / f"bundle-{bundle_id}-runner-first-{ts}.log"
        first_res = _run_runner(
            str(bdef["runner_first"]),
            runner_log,
            timeout=int(bdef.get("est_wall_sec") or 3600),
        )
        check_results.append({**first_res, "id": f"{first_res.get('id')}-boot"})
        if not first_res.get("ok"):
            bundle_ok = False

    for cid in bdef.get("checks") or []:
        check = by_id.get(str(cid))
        if not check:
            check_results.append({"id": cid, "ok": False, "at": _now(), "tail": "not in registry"})
            bundle_ok = False
            continue
        c_cadence = str(check.get("cadence") or cadence)
        if _fresh(str(cid), last, c_cadence, force=force):
            check_results.append({"id": cid, "ok": True, "skipped_fresh": True, "at": _now()})
            skip_fresh += 1
            continue
        block = _check_blocked(check, ctx)
        if block:
            check_results.append({"id": cid, "ok": False, "at": _now(), "tail": block, "blocked": True})
            bundle_ok = False
            continue
        log_path = LOG_DIR / f"{cid}-{ts}.log"
        if check.get("kind") == "http_probe":
            res = _run_http_probe(check, log_path)
        else:
            res = _run_script(check, log_path, timeout=int(check.get("est_wall_sec") or 300) + 60)
        check_results.append(res)
        if not res.get("ok"):
            bundle_ok = False
            blockers.append(
                {
                    "check_id": cid,
                    "fail_section": str(res.get("tail") or "")[:300],
                    "playbook_rule": 1,
                }
            )

    for py_cmd in bdef.get("python_checks") or []:
        parts = py_cmd.split()
        script = parts[0]
        log_path = LOG_DIR / f"{Path(script).stem}-{ts}.log"
        res = _run_runner(py_cmd, log_path, timeout=120)
        check_results.append(res)
        if not res.get("ok"):
            bundle_ok = False

    if bdef.get("runner") and not bdef.get("runner_first"):
        runner_log = LOG_DIR / f"bundle-{bundle_id}-runner-{ts}.log"
        runner_res = _run_runner(
            str(bdef["runner"]),
            runner_log,
            timeout=int(bdef.get("est_wall_sec") or 3600),
        )
        check_results.append(runner_res)
        if not runner_res.get("ok"):
            bundle_ok = False
            blockers.append(
                {
                    "check_id": str(runner_res.get("id") or "runner"),
                    "fail_section": str(runner_res.get("tail") or "")[:300],
                    "playbook_rule": 1,
                }
            )
        log_bundle = runner_log
    elif bdef.get("runner") and bdef.get("runner_first"):
        # runner_first already ran — append summary row only if different id needed
        log_bundle = LOG_DIR / f"bundle-{bundle_id}-{ts}.log"

    elapsed = int(time.time() - t0)
    passed = sum(1 for c in check_results if c.get("ok") and not c.get("skipped_fresh"))
    failed = sum(1 for c in check_results if not c.get("ok"))
    report = {
        "schema": SCHEMA,
        "run_id": f"E2E-{ts}",
        "at": _now(),
        "agent": agent or os.environ.get("SINA_AGENT_ID", "cursor-auto"),
        "role": role,
        "context": ctx,
        "cadence": cadence,
        "git_head": _git_head(),
        "elapsed_sec": elapsed,
        "summary": {
            "total": len(check_results),
            "pass": passed,
            "fail": failed,
            "skip_fresh": skip_fresh,
            "blocked": sum(1 for c in check_results if c.get("blocked")),
        },
        "bundles": [{"id": bundle_id, "ok": bundle_ok, "log": str(log_bundle)}],
        "checks": check_results,
        "blockers": blockers,
        "next_agent_read": "Read ~/.sina/sourcea-e2e-last-report-v1.json before any E2E re-run",
    }
    if write_report_flag:
        write_report(report)
    report["ok"] = bundle_ok and failed == 0
    return report


def run_cadence(
    cadence: str,
    *,
    force: bool = False,
    role: str = "maintainer",
    write_report_flag: bool = True,
    all_checks: bool = False,
) -> dict[str, Any]:
    import time

    t0 = time.time()
    registry = _read(REGISTRY)
    overrides = _read(OVERRIDES)
    bundles = overrides.get("bundles") or registry.get("bundles") or {}
    cadence_bundles = [bid for bid, b in bundles.items() if isinstance(b, dict) and b.get("cadence") == cadence]

    if cadence == "weekly" and not cadence_bundles:
        cadence_bundles = [
            "mac_daily_smoke",
            "machine_ladder_weekly",
            "hub_e2e_core",
            "disk_truth_matrix",
            "h2_weekly",
        ]

    all_check_results: list[dict[str, Any]] = []
    bundle_rows: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    skip_fresh = 0
    ok_all = True

    if all_checks and cadence == "monthly":
        ctx = _context()
        if ctx == "founder_session":
            return {"ok": False, "error": "monthly full catalog forbidden during founder session"}
        by_tier: dict[str, list[dict]] = {}
        for c in registry.get("checks") or []:
            if c.get("kind") == "http_probe":
                continue
            tier = str(c.get("unified_tier") or "T1_fast")
            by_tier.setdefault(tier, []).append(c)
        ts = _now_id()
        last = _read(LAST_REPORT)

        def _run_one(check: dict) -> dict:
            cid = str(check.get("id"))
            if _fresh(cid, last, "monthly", force=force):
                return {"id": cid, "ok": True, "skipped_fresh": True, "at": _now()}
            block = _check_blocked(check, ctx)
            if block:
                return {"id": cid, "ok": False, "at": _now(), "tail": block, "blocked": True}
            log_path = LOG_DIR / f"{cid}-{ts}.log"
            if check.get("kind") == "http_probe":
                return _run_http_probe(check, log_path)
            return _run_script(check, log_path, timeout=int(check.get("est_wall_sec") or 120) + 30)

        for tier in ("T0_probe", "T1_fast", "T2_medium", "T3_heavy", "T4_marathon"):
            batch = by_tier.get(tier, [])
            max_workers = 4 if tier in ("T0_probe", "T1_fast") else 2
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futs = {pool.submit(_run_one, c): c for c in batch}
                for fut in as_completed(futs):
                    res = fut.result()
                    all_check_results.append(res)
                    if res.get("skipped_fresh"):
                        skip_fresh += 1
                    elif not res.get("ok"):
                        ok_all = False
                        blockers.append({"check_id": res.get("id"), "fail_section": str(res.get("tail", ""))[:200]})
    else:
        for bid in cadence_bundles:
            sub = run_bundle(
                bid,
                force=force,
                role=role,
                write_report_flag=False,
                cadence=cadence,
            )
            bundle_rows.append({"id": bid, "ok": sub.get("ok"), "log": (sub.get("bundles") or [{}])[0].get("log", "")})
            all_check_results.extend(sub.get("checks") or [])
            blockers.extend(sub.get("blockers") or [])
            skip_fresh += (sub.get("summary") or {}).get("skip_fresh", 0)
            if not sub.get("ok"):
                ok_all = False

    elapsed = int(time.time() - t0)
    passed = sum(1 for c in all_check_results if c.get("ok") and not c.get("skipped_fresh"))
    failed = sum(1 for c in all_check_results if not c.get("ok"))
    ts = _now_id()
    report = {
        "schema": SCHEMA,
        "run_id": f"E2E-{ts}",
        "at": _now(),
        "agent": os.environ.get("SINA_AGENT_ID", "cursor-auto"),
        "role": role,
        "context": _context(),
        "cadence": cadence,
        "git_head": _git_head(),
        "elapsed_sec": elapsed,
        "summary": {
            "total": len(all_check_results),
            "pass": passed,
            "fail": failed,
            "skip_fresh": skip_fresh,
            "blocked": sum(1 for c in all_check_results if c.get("blocked")),
        },
        "bundles": bundle_rows,
        "checks": all_check_results,
        "blockers": blockers,
        "next_agent_read": "Read ~/.sina/sourcea-e2e-last-report-v1.json before any E2E re-run",
    }
    if write_report_flag:
        write_report(report)
    report["ok"] = ok_all and failed == 0
    return report


def ingest_external_run(
    *,
    bundle_id: str,
    ok: bool,
    log_path: str | None = None,
    check_results: list[dict] | None = None,
    cadence: str = "weekly",
    role: str = "maintainer",
) -> dict[str, Any]:
    """Write report from an existing runner (no re-execution)."""
    ts = _now_id()
    checks = check_results or []
    if not checks and bundle_id:
        checks = [{"id": bundle_id, "ok": ok, "at": _now(), "log": log_path or "", "kind": "runner"}]
    passed = sum(1 for c in checks if c.get("ok"))
    failed = sum(1 for c in checks if not c.get("ok"))
    report = {
        "schema": SCHEMA,
        "run_id": f"E2E-{ts}",
        "at": _now(),
        "agent": os.environ.get("SINA_AGENT_ID", "cursor-auto"),
        "role": role,
        "context": _context(),
        "cadence": cadence,
        "git_head": _git_head(),
        "elapsed_sec": 0,
        "summary": {
            "total": len(checks),
            "pass": passed,
            "fail": failed,
            "skip_fresh": 0,
            "blocked": 0,
        },
        "bundles": [{"id": bundle_id, "ok": ok, "log": log_path or ""}],
        "checks": checks,
        "blockers": [] if ok else [{"check_id": bundle_id, "fail_section": "ingest fail", "playbook_rule": 1}],
        "next_agent_read": "Read ~/.sina/sourcea-e2e-last-report-v1.json before any E2E re-run",
        "ingest": True,
    }
    write_report(report)
    report["ok"] = ok and failed == 0
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA E2E run orchestrator")
    ap.add_argument("--read-last", action="store_true", help="Read last report only (no run)")
    ap.add_argument("--bundle", help="Run single bundle id")
    ap.add_argument("--cadence", choices=["daily", "3day", "weekly", "monthly"])
    ap.add_argument("--all", action="store_true", help="Monthly full catalog parallel run")
    ap.add_argument("--force", action="store_true", help="Ignore freshness skip")
    ap.add_argument("--write-report", action="store_true", help="Write last report JSON")
    ap.add_argument("--ingest-bundle", help="Write report for external runner (no re-run)")
    ap.add_argument("--ingest-ok", action="store_true", help="Mark ingested run PASS")
    ap.add_argument("--ingest-fail", action="store_true", help="Mark ingested run FAIL")
    ap.add_argument("--log-path", default="", help="Log path for ingest")
    ap.add_argument("--role", default="maintainer")
    ap.add_argument("--agent", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.ingest_bundle:
        ok = args.ingest_ok or not args.ingest_fail
        out = ingest_external_run(
            bundle_id=args.ingest_bundle,
            ok=ok,
            log_path=args.log_path or None,
            cadence=args.cadence or "weekly",
            role=args.role,
        )
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"E2E_INGEST ok={out.get('ok')} bundle={args.ingest_bundle}")
        return 0 if out.get("ok") else 1

    if args.read_last:
        out = read_last_report()
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(out.get("e2e_last_report_line"))
        return 0

    write_flag = args.write_report or bool(args.bundle or args.cadence)

    if args.bundle:
        out = run_bundle(
            args.bundle,
            force=args.force,
            role=args.role,
            agent=args.agent,
            write_report_flag=write_flag,
            cadence=args.cadence or "weekly",
        )
    elif args.cadence:
        out = run_cadence(
            args.cadence,
            force=args.force,
            role=args.role,
            write_report_flag=write_flag,
            all_checks=args.all,
        )
    else:
        ap.print_help()
        return 1

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        s = out.get("summary") or {}
        print(f"E2E_RUN ok={out.get('ok')} pass={s.get('pass')} fail={s.get('fail')} skip={s.get('skip_fresh')}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
