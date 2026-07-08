#!/usr/bin/env python3
"""SourceA auth domains audit machine — app · ca · uk only.

SSOT: data/sourcea-auth-domains-machine-v1.json
Plan: data/sourcea-auth-upgrade-plan-v1.json

Modes:
  dist  — after build (files, config schema, no login-wall copy in tier0 dist)
  live  — after publish (HTTPS 200 + body checks on all SourceA domains)
  both  — dist then live

Receipts:
  reports/sourcea-auth-domains-audit-latest-v1.json
  ~/.sina/sourcea-auth-domains-audit-receipt-v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MACHINE = ROOT / "data" / "sourcea-auth-domains-machine-v1.json"
DIST = ROOT / "SourceA-landing" / "green-unified" / "dist"
REPORT = ROOT / "reports" / "sourcea-auth-domains-audit-latest-v1.json"
RECEIPT_HOME = Path.home() / ".sina" / "sourcea-auth-domains-audit-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_machine() -> dict[str, Any]:
    if not MACHINE.is_file():
        raise SystemExit(f"FAIL: machine SSOT missing: {MACHINE}")
    return json.loads(MACHINE.read_text(encoding="utf-8"))


def _fetch(url: str, *, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "sourcea-auth-domains-audit/1.0",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            body = raw.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "url": url,
                "http_code": int(resp.status),
                "body": body,
                "body_bytes": len(raw),
                "body_sha256": hashlib.sha256(raw).hexdigest(),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read() if exc.fp else b""
        body = raw.decode("utf-8", errors="replace") if raw else ""
        return {
            "ok": False,
            "url": url,
            "http_code": int(exc.code),
            "body": body,
            "body_bytes": len(raw),
            "body_sha256": hashlib.sha256(raw).hexdigest() if raw else "",
            "error": str(exc),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "url": url, "http_code": 0, "body": "", "error": str(exc)}


def _finding(check_id: str, severity: str, detail: str, **meta: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"id": check_id, "severity": severity, "detail": detail}
    row.update(meta)
    return row


def audit_dist(machine: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    passes: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    gates = machine.get("dist_gates") or {}

    for rel in gates.get("required_files") or []:
        path = DIST / rel
        if path.is_file():
            passes.append({"id": f"dist_file:{rel}", "detail": "present"})
        else:
            findings.append(_finding(f"dist_file:{rel}", "FAIL", f"missing {path.relative_to(ROOT)}"))

    index = DIST / "index.html"
    if index.is_file():
        text = index.read_text(encoding="utf-8")
        for needle in gates.get("index_must_contain") or []:
            if needle in text:
                passes.append({"id": f"index_contains:{needle}", "detail": "ok"})
            else:
                findings.append(_finding(f"index_contains:{needle}", "FAIL", f"index.html missing {needle!r}"))
        for bad in gates.get("forbidden_in_tier0_dist") or []:
            if bad.lower() in text.lower():
                findings.append(_finding("tier0_login_wall", "FAIL", f"index.html contains forbidden {bad!r}"))
            else:
                passes.append({"id": f"index_forbidden_absent:{bad}", "detail": "ok"})

    cfg_path = DIST / "sourcea" / "data" / "sourcea-platform-auth-config-v1.json"
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(_finding("auth_config_json", "FAIL", str(exc)))
            cfg = {}
        if cfg.get("schema") != gates.get("auth_config_schema"):
            findings.append(
                _finding(
                    "auth_config_schema",
                    "FAIL",
                    f"schema {cfg.get('schema')!r} != {gates.get('auth_config_schema')!r}",
                )
            )
        elif cfg.get("venture") != gates.get("auth_config_venture"):
            findings.append(
                _finding(
                    "auth_config_venture",
                    "FAIL",
                    f"venture {cfg.get('venture')!r} != {gates.get('auth_config_venture')!r}",
                )
            )
        elif not cfg.get("configured"):
            findings.append(_finding("auth_config_configured", "FAIL", "configured is false"))
        elif "service_role" in json.dumps(cfg).lower():
            findings.append(_finding("auth_config_secrets", "FAIL", "service_role leaked in public config"))
        else:
            urls = cfg.get("redirect_urls") or []
            if not any("auth/callback" in u for u in urls):
                findings.append(_finding("auth_config_callback", "FAIL", "no auth/callback in redirect_urls"))
            else:
                passes.append({"id": "auth_config", "detail": "schema venture callback ok"})
    else:
        findings.append(_finding("auth_config_missing", "FAIL", str(cfg_path)))

    return passes, findings


def audit_live(machine: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    passes: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    gates = machine.get("live_gates") or {}

    for url in gates.get("tier0_expect_200") or []:
        row = _fetch(url)
        if row.get("http_code") == 200:
            passes.append({"id": f"tier0_200:{url}", "detail": "200", "sha256": row.get("body_sha256", "")[:16]})
        else:
            findings.append(
                _finding(
                    f"tier0_200:{url}",
                    "FAIL",
                    f"http={row.get('http_code')} err={row.get('error', '')}",
                )
            )

    for url in gates.get("auth_expect_200") or []:
        row = _fetch(url)
        if row.get("http_code") == 200:
            passes.append({"id": f"auth_200:{url}", "detail": "200"})
        else:
            findings.append(
                _finding(f"auth_200:{url}", "FAIL", f"http={row.get('http_code')} err={row.get('error', '')}")
            )

    for check in gates.get("body_checks") or []:
        url = str(check.get("url") or "")
        needle = str(check.get("must_contain") or "")
        label = str(check.get("label") or url)
        row = _fetch(url)
        body = row.get("body") or ""
        if row.get("http_code") == 200 and needle in body:
            passes.append({"id": f"body:{label}", "detail": needle})
        else:
            findings.append(
                _finding(
                    f"body:{label}",
                    "FAIL",
                    f"http={row.get('http_code')} missing {needle!r}",
                )
            )

    cfg_url = "https://sourcea.app/sourcea/data/sourcea-platform-auth-config-v1.json"
    cfg_row = _fetch(cfg_url)
    if cfg_row.get("http_code") == 200:
        try:
            cfg = json.loads(cfg_row.get("body") or "{}")
            if cfg.get("venture") == "sourcea" and cfg.get("configured"):
                passes.append({"id": "live_auth_config", "detail": "ok"})
            else:
                findings.append(_finding("live_auth_config", "FAIL", "venture or configured invalid"))
        except json.JSONDecodeError:
            findings.append(_finding("live_auth_config", "FAIL", "invalid JSON"))
    else:
        findings.append(_finding("live_auth_config", "FAIL", f"http={cfg_row.get('http_code')}"))

    return passes, findings


def run(*, mode: str) -> dict[str, Any]:
    machine = _load_machine()
    all_passes: list[dict[str, Any]] = []
    all_findings: list[dict[str, Any]] = []

    if mode in ("dist", "both"):
        p, f = audit_dist(machine)
        all_passes.extend(p)
        all_findings.extend(f)

    if mode in ("live", "both"):
        p, f = audit_live(machine)
        all_passes.extend(p)
        all_findings.extend(f)

    fail_count = sum(1 for x in all_findings if x.get("severity") == "FAIL")
    ok = fail_count == 0

    receipt: dict[str, Any] = {
        "schema": "sourcea-auth-domains-audit-v1",
        "at": _now(),
        "mode": mode,
        "loop_id": machine.get("loop_id"),
        "venture": machine.get("venture"),
        "domains": [d.get("host") for d in machine.get("domains") or []],
        "verdict": "PASS" if ok else "FAIL",
        "ok": ok,
        "pass_count": len(all_passes),
        "fail_count": fail_count,
        "passes": all_passes,
        "findings": all_findings,
        "machine_ssot": str(MACHINE.relative_to(ROOT)),
        "plan_ssot": "data/sourcea-auth-upgrade-plan-v1.json",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    RECEIPT_HOME.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_HOME.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    return receipt


def main() -> int:
    p = argparse.ArgumentParser(description="SourceA auth domains audit machine")
    p.add_argument("--mode", choices=("dist", "live", "both"), default="live")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    receipt = run(mode=args.mode)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"sourcea_auth_domains_audit_v1: {receipt['verdict']} "
            f"mode={args.mode} pass={receipt['pass_count']} fail={receipt['fail_count']}"
        )
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
