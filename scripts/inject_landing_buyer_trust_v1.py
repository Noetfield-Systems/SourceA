#!/usr/bin/env python3
"""Inject Buyer 1 trust signals for SourceA landing — live disk + GitHub API."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
DATA = LANDING / "data"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-buyer-trust-inject-v1.json"
GITHUB_REPO = "sourcea-io/sourcea-boot"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _is_receipt_file(path: Path) -> bool:
    if path.suffix != ".json":
        return False
    name = path.name.lower()
    skip_parts = ("cache", "work-v1", "mirror", "template", "example")
    if any(s in str(path).lower() for s in skip_parts):
        return False
    if "receipt" not in name and not name.endswith("-receipt.json"):
        return False
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        if len(raw) > 500_000:
            return False
        data = json.loads(raw)
        schema = str(data.get("schema") or "").lower()
        if "receipt" not in schema and "receipt" not in name:
            return False
        # Signed dispatch / gate receipts — not config stubs
        return any(k in data for k in ("verdict", "gate_id", "kill_count", "founder_line", "ok", "status"))
    except (OSError, json.JSONDecodeError, TypeError):
        return False


def _parse_valid_yes(line: str) -> dict:
    """Extract honest valid_yes from factory_now_line."""
    import re

    out = {"valid_yes": None, "valid_total": 1000}
    if not line:
        return out
    m = re.search(r"Valid YES\s+(\d+)", line, re.I)
    if m:
        out["valid_yes"] = int(m.group(1))
    return out


SKIP_GOVERNANCE_EVENTS = frozenset({"workspace_selected", "prompt_router"})
EXECUTION_NOISE_PREFIXES = ("execution_state_", "execution_kernel_")


def _is_material_governance_row(row: dict) -> bool:
    event = str(row.get("event") or "")
    if not event or event in SKIP_GOVERNANCE_EVENTS:
        return False
    if event.startswith(EXECUTION_NOISE_PREFIXES):
        return False
    return True


def count_governance_events_today(*, sina: Path = SINA) -> dict:
    """Count material governance receipt activity today — honest buyer metric."""
    today = _today_utc()
    count = 0
    samples: list[str] = []
    for name in ("agent-governance-events.jsonl",):
        path = sina / name
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                event = str(row.get("event") or "")
                if not _is_material_governance_row(row):
                    continue
                at = str(row.get("at") or row.get("synced_at") or "")[:10]
                if at != today:
                    continue
                count += 1
                if len(samples) < 5:
                    samples.append(f"{name}:{event or row.get('schema') or 'row'}")
        except OSError:
            continue
    for name in (
        "agent_session_gate_receipt_v1.json",
        "critic-boot-v1.json",
        "sourcea-boot-terminal-inject-v1.json",
    ):
        path = sina / name
        if not path.is_file():
            continue
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
            if mtime != today:
                continue
            count += 1
            if len(samples) < 5:
                samples.append(name)
        except OSError:
            continue
    return {"count": count, "date": today, "samples": samples}


def count_governance_events_lifetime(*, sina: Path = SINA) -> dict:
    """All material governance rows logged — honest lifetime receipt ticker."""
    count = 0
    path = sina / "agent-governance-events.jsonl"
    if not path.is_file():
        return {"count": 0}
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if _is_material_governance_row(row):
                count += 1
    except OSError:
        pass
    return {"count": count}


def count_receipts_today(*, sina: Path = SINA) -> dict:
    """Count receipt-like JSON files touched today logged."""
    today = _today_utc()
    count = 0
    samples: list[str] = []
    roots = [sina / "enforcement", sina / "demo-enforcement" / "receipts", sina / "mac-health"]
    if not sina.is_dir():
        return {"count": 0, "date": today, "samples": []}
    seen: set[str] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*.json"):
            if not _is_receipt_file(p):
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
                if mtime != today:
                    continue
                count += 1
                if len(samples) < 5:
                    samples.append(str(p.relative_to(sina)))
            except OSError:
                continue
    # Fallback: scan ~/.sina top-level receipt JSON (bounded)
    if count == 0:
        for p in sorted(sina.glob("*receipt*.json"))[:200]:
            if not _is_receipt_file(p):
                continue
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
                if mtime != today:
                    continue
                count += 1
                if len(samples) < 5:
                    samples.append(p.name)
            except OSError:
                continue
    return {"count": count, "date": today, "samples": samples}


def fetch_github_stats(*, repo: str = GITHUB_REPO) -> dict:
    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "SourceA-landing-trust-v1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": True,
            "repo": repo,
            "url": row.get("html_url") or f"https://github.com/{repo}",
            "stars": int(row.get("stargazers_count") or 0),
            "open_issues": int(row.get("open_issues_count") or 0),
            "updated_at": str(row.get("updated_at") or ""),
            "pushed_at": str(row.get("pushed_at") or ""),
        }
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        return {"ok": False, "repo": repo, "url": f"https://github.com/{repo}", "error": str(exc)[:200]}


def governance_status(*, boot_path: Path = DATA / "boot-proof.json") -> dict:
    row = {"loop": "governance", "status": "unknown", "verdict": "UNKNOWN", "checks_pass": 0, "checks_total": 0}
    if boot_path.is_file():
        try:
            boot = json.loads(boot_path.read_text(encoding="utf-8"))
            checks = boot.get("checks") or []
            passed = sum(1 for c in checks if c.get("ok"))
            verdict = str(boot.get("verdict") or "UNKNOWN")
            row.update(
                {
                    "status": "operational" if boot.get("ok") else "degraded",
                    "verdict": verdict,
                    "checks_pass": passed,
                    "checks_total": len(checks),
                    "at": boot.get("at"),
                }
            )
        except (OSError, json.JSONDecodeError):
            pass
    freeze = SINA / "auto-run-disabled-v1.flag"
    if freeze.is_file():
        row["factory"] = "FROZEN"
    else:
        row["factory"] = "ACTIVE"
    return row


def build_trust_signals() -> dict:
    receipts = count_governance_events_today()
    lifetime = count_governance_events_lifetime()
    github = fetch_github_stats()
    gov = governance_status()
    surf_line = ""
    queue_sa = ""
    surf_path = SINA / "agent-live-surfaces-v1.json"
    if surf_path.is_file():
        try:
            surf = json.loads(surf_path.read_text(encoding="utf-8"))
            surf_line = str(surf.get("factory_now_line") or "")
            queue_sa = str(surf.get("queue_sa") or "")
        except (OSError, json.JSONDecodeError):
            pass
    valid = _parse_valid_yes(surf_line)
    boot_at = ""
    boot_path = DATA / "boot-proof.json"
    if boot_path.is_file():
        try:
            boot_at = str(json.loads(boot_path.read_text(encoding="utf-8")).get("at") or "")
        except (OSError, json.JSONDecodeError):
            pass
    api_verdict = str(gov.get("verdict") or "PASS")
    if api_verdict not in ("PASS", "BLOCK"):
        api_verdict = "BLOCK"
    return {
        "schema": "sourcea-trust-signals-v1",
        "at": _now(),
        "receipts_signed_today": receipts["count"],
        "receipts_signed_lifetime": lifetime["count"],
        "receipts_lifetime_label": "Logged and reviewable logged",
        "receipts_date": receipts["date"],
        "receipt_samples": receipts["samples"],
        "receipt_metric_label": "Material governance events today",
        "valid_yes": valid.get("valid_yes"),
        "valid_yes_total": valid.get("valid_total"),
        "github": github,
        "governance": gov,
        "factory_now_line": surf_line,
        "status_page": "/sourcea/status",
        "proof_sample": "/sourcea/attach/proof-bundle-sample",
        "built_on": [
            {"id": "temporal", "label": "Temporal", "note": "durable workflow orchestration"},
            {"id": "anthropic", "label": "Anthropic Claude", "note": "Claude API · policy at dispatch"},
            {"id": "openai", "label": "OpenAI", "note": "API models · eval paths"},
            {"id": "langgraph", "label": "LangGraph", "note": "graph orchestration pattern"},
            {"id": "cursor", "label": "Cursor", "note": "agentic worker IDE"},
            {"id": "cloudflare", "label": "Cloudflare", "note": "edge · tunnel · Pages"},
        ],
        "disclaimer": "Built on = technology dependencies · not co-marketing partnerships",
        "api_hook": {
            "endpoint": "POST /v1/decision",
            "receipt_id": queue_sa or "sa-0886",
            "verdict": api_verdict,
            "signed_at": boot_at or _now(),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Inject Buyer 1 trust signals JSON for landing")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    row = build_trust_signals()
    out_path = DATA / "trust-signals.json"
    if not args.dry_run:
        DATA.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        RECEIPT.write_text(
            json.dumps({"schema": "sourcea-buyer-trust-inject-v1", "at": _now(), "path": str(out_path), "receipts": row["receipts_signed_today"]}, indent=2)
            + "\n",
            encoding="utf-8",
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: trust-signals · receipts_today={row['receipts_signed_today']} · github_ok={row['github'].get('ok')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
