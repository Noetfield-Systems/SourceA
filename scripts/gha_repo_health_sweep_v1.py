#!/usr/bin/env python3
"""Daily repo-health sweep — findings → improvement_queue (no markdown reports)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "gha_repo_health_daily"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def _finding(
    text: str,
    *,
    roi: float = 5.0,
    machine_safe: bool = True,
) -> dict[str, Any]:
    return {
        "finding": text,
        "source": SOURCE,
        "expected_roi": roi,
        "machine_safe": machine_safe,
    }


def sweep_trigger_registry() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    code, out = _run([sys.executable, "scripts/sandbox_health_sweep_v1.py", "--json"])
    try:
        row = json.loads(out)
    except json.JSONDecodeError:
        findings.append(
            _finding(
                f"repo_health: sandbox_health_sweep failed to parse JSON (exit={code})",
                roi=8.0,
            )
        )
        return findings

    if not row.get("ok"):
        for dead in row.get("dead_or_mismatch") or []:
            tid = dead.get("trigger_id", "?")
            reason = dead.get("reason", "unknown")
            findings.append(
                _finding(
                    f"trigger_drift dead_or_mismatch trigger_id={tid} reason={reason}",
                    roi=7.5,
                )
            )
        for unreg in row.get("unregistered_live") or []:
            sig = unreg.get("signature", "?")
            path = unreg.get("path", "?")
            findings.append(
                _finding(
                    f"trigger_drift unregistered_live signature={sig} path={path}",
                    roi=6.5,
                )
            )
    return findings


def sweep_repo_policy() -> list[dict[str, Any]]:
    code, out = _run([sys.executable, "scripts/check_sourcea_repo_policy.py"])
    if code == 0:
        return []
    line = out.splitlines()[-1] if out else f"exit={code}"
    return [_finding(f"repo_policy_fail: {line[:500]}", roi=9.0, machine_safe=False)]


def sweep_workflow_lint() -> list[dict[str, Any]]:
    script = ROOT / "scripts" / "validate-github-workflows-v1.sh"
    if not script.is_file():
        return [_finding("repo_health: missing validate-github-workflows-v1.sh", roi=8.0)]
    code, out = _run(["bash", str(script)])
    if code == 0:
        return []
    tail = out[-600:] if out else f"exit={code}"
    return [_finding(f"github_workflow_lint_fail: {tail}", roi=7.0)]


def sweep_required_workflows() -> list[dict[str, Any]]:
    required = (
        ".github/workflows/validate.yml",
        ".github/workflows/repo-health-daily-v1.yml",
        ".github/workflows/security-sweep-weekly-v1.yml",
    )
    findings: list[dict[str, Any]] = []
    for rel in required:
        if not (ROOT / rel).is_file():
            findings.append(_finding(f"missing_required_workflow: {rel}", roi=8.5))
    return findings


def sweep_supabase_sink() -> list[dict[str, Any]]:
    code, out = _run(
        [sys.executable, "scripts/improvement_queue_insert_v1.py", "--probe", "--json"]
    )
    try:
        row = json.loads(out)
    except json.JSONDecodeError:
        return [_finding("improvement_queue_probe: invalid JSON from probe", roi=9.0)]
    if row.get("ok"):
        return []
    err = row.get("error") or row.get("status") or "unknown"
    return [
        _finding(
            f"improvement_queue_unreachable: {err}",
            roi=9.5,
            machine_safe=False,
        )
    ]


def run_sweep(*, insert: bool = False) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    findings.extend(sweep_required_workflows())
    findings.extend(sweep_trigger_registry())
    findings.extend(sweep_repo_policy())
    findings.extend(sweep_workflow_lint())
    if insert:
        findings.extend(sweep_supabase_sink())

    insert_result: dict[str, Any] | None = None
    if insert and findings:
        tmp = ROOT / "receipts" / "gha" / "repo-health-findings-v1.json"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps({"findings": findings}, indent=2), encoding="utf-8")
        code, out = _run(
            [
                sys.executable,
                "scripts/improvement_queue_insert_v1.py",
                "--findings",
                str(tmp),
                "--json",
            ]
        )
        try:
            insert_result = json.loads(out)
        except json.JSONDecodeError:
            insert_result = {"ok": False, "error": "insert_parse_fail", "raw": out[:300]}
        if code != 0 and insert_result and not insert_result.get("ok"):
            pass  # hygiene — still return sweep row
    elif insert and not findings:
        insert_result = {"ok": True, "inserted": 0, "note": "no_findings"}

    return {
        "schema": "gha-repo-health-sweep-v1",
        "version": "1.0.0",
        "at": _now(),
        "source": SOURCE,
        "finding_count": len(findings),
        "findings": findings,
        "insert": insert_result,
        "ok": True,
        "report_line": (
            "repo_health_clean"
            if not findings
            else f"repo_health_findings={len(findings)} queued"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--insert", action="store_true", help="POST findings to improvement_queue")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = run_sweep(insert=args.insert)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))

    if args.insert and isinstance(row.get("insert"), dict) and not row["insert"].get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
