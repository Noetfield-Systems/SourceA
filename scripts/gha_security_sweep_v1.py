#!/usr/bin/env python3
"""Weekly security sweep — findings → improvement_queue (no markdown reports)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "gha_security_sweep_weekly"
WF_DIR = ROOT / ".github" / "workflows"

SENSITIVE_PATH_RE = re.compile(
    r"(^|/)(\.env($|\.local)|.*\.(pem|p12|pfx)$|(^|/)id_rsa$|(^|/)id_dsa$|credentials\.json$)",
    re.IGNORECASE,
)
SECRET_LIKE_RE = re.compile(
    r"(?i)(api[_-]?key|secret[_-]?key|private[_-]?key|password)\s*=\s*['\"]([A-Za-z0-9_\-]{20,})['\"]",
)
PLACEHOLDER_RE = re.compile(
    r"(?i)(example|placeholder|changeme|your[_-]|xxx+|todo|replace|dummy|test[_-]?key)",
)
UNPINNED_ACTION_RE = re.compile(r"uses:\s*[^\s@]+@(main|master|latest|HEAD)\b")
PR_TARGET_WRITE_RE = re.compile(
    r"pull_request_target:",
    re.IGNORECASE,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_ls_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _finding(
    text: str,
    *,
    roi: float = 8.0,
    machine_safe: bool = False,
) -> dict[str, Any]:
    return {
        "finding": text,
        "source": SOURCE,
        "expected_roi": roi,
        "machine_safe": machine_safe,
    }


def sweep_sensitive_paths() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel in _git_ls_files():
        if ".example" in rel or rel.endswith(".sample"):
            continue
        if rel.endswith(".md") or rel.startswith("docs/"):
            continue
        if SENSITIVE_PATH_RE.search(rel):
            findings.append(
                _finding(
                    f"sensitive_path_tracked: {rel}",
                    roi=9.5,
                )
            )
    return findings


def sweep_secret_literals() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    scan_roots = ("scripts", "cloud", "apps", "infra")
    skip_suffix = (".md", ".json", ".example", ".sample", ".lock")
    for rel in _git_ls_files():
        if not rel.startswith(scan_roots):
            continue
        if "/dist/" in f"/{rel}/" or rel.endswith(skip_suffix):
            continue
        if ".example" in rel or "config.example" in rel:
            continue
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size > 200_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in SECRET_LIKE_RE.finditer(text):
            value = match.group(2) or ""
            if PLACEHOLDER_RE.search(value):
                continue
            if value.startswith("${") or value.startswith("process.env"):
                continue
            findings.append(
                _finding(
                    f"secret_literal_pattern: {rel}",
                    roi=10.0,
                )
            )
            break
    return findings


def sweep_workflow_hygiene() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not WF_DIR.is_dir():
        return [_finding("security_sweep: missing .github/workflows", roi=7.0)]

    for wf in sorted(WF_DIR.glob("*.yml")):
        text = wf.read_text(encoding="utf-8", errors="replace")
        rel = str(wf.relative_to(ROOT))
        for match in UNPINNED_ACTION_RE.finditer(text):
            findings.append(
                _finding(
                    f"unpinned_github_action: {rel} line≈{text[:match.start()].count(chr(10))+1} uses={match.group(0)}",
                    roi=6.0,
                    machine_safe=True,
                )
            )
        if PR_TARGET_WRITE_RE.search(text) and "contents: write" in text:
            findings.append(
                _finding(
                    f"pull_request_target_with_write: {rel}",
                    roi=9.0,
                )
            )
    return findings


def sweep_branch_protection_ssot() -> list[dict[str, Any]]:
    ssot = ROOT / "data" / "github-main-branch-protection-v1.json"
    if not ssot.is_file():
        return [_finding("missing_branch_protection_ssot: data/github-main-branch-protection-v1.json", roi=7.5)]
    try:
        row = json.loads(ssot.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [_finding("invalid_branch_protection_ssot JSON", roi=7.5)]
    contexts = (
        row.get("required_status_checks", {}).get("contexts")
        if isinstance(row.get("required_status_checks"), dict)
        else None
    )
    if not isinstance(contexts, list) or "validate" not in contexts:
        return [_finding("branch_protection_ssot missing required check validate", roi=8.0)]
    return []


def run_sweep(*, insert: bool = False) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    findings.extend(sweep_branch_protection_ssot())
    findings.extend(sweep_sensitive_paths())
    findings.extend(sweep_secret_literals())
    findings.extend(sweep_workflow_hygiene())

    insert_result: dict[str, Any] | None = None
    if insert and findings:
        tmp = ROOT / "receipts" / "gha" / "security-sweep-findings-v1.json"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps({"findings": findings}, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/improvement_queue_insert_v1.py",
                "--findings",
                str(tmp),
                "--json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            insert_result = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            insert_result = {"ok": False, "error": "insert_parse_fail"}
    elif insert:
        insert_result = {"ok": True, "inserted": 0, "note": "no_findings"}

    return {
        "schema": "gha-security-sweep-v1",
        "version": "1.0.0",
        "at": _now(),
        "source": SOURCE,
        "finding_count": len(findings),
        "findings": findings,
        "insert": insert_result,
        "ok": True,
        "report_line": (
            "security_sweep_clean"
            if not findings
            else f"security_findings={len(findings)} queued"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--insert", action="store_true")
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
