#!/usr/bin/env python3
"""Buyer-proof hotfix verification — path leaks, live markers, intake, guards."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
LANDING = ROOT / "SourceA-landing" / "green-unified"
DIST = LANDING / "dist"

FORBIDDEN = ("/Users/", "sinakazemnezhad", "Desktop/SourceA")

BUYER_GLOBS = (
    "eval.html",
    "proof.html",
    "proof/live.html",
    "attach/agency-onepager.html",
    "data/aeg-live.json",
    "data/factory-live.json",
    "sourcea-aeg-live.js",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-buyer-proof-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return int(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return int(exc.code), body


DIST_BUYER_FILES = (
    "sourcea/eval.html",
    "sourcea/proof.html",
    "sourcea/proof/live.html",
    "sourcea/attach/agency-onepager.html",
    "sourcea/data/aeg-live.json",
    "sourcea/data/factory-live.json",
)


def grep_buyer_sources() -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for rel in BUYER_GLOBS:
        path = LANDING / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in FORBIDDEN:
            if needle in text:
                hits.append({"path": str(path.relative_to(ROOT)), "needle": needle})
    dist_root = LANDING / "dist"
    for rel in DIST_BUYER_FILES:
        path = dist_root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in FORBIDDEN:
            if needle in text:
                hits.append({"path": str(path.relative_to(ROOT)), "needle": needle})
    return {"ok": not hits, "hits": hits}


def verify_live_page(*, base: str, path: str, markers: list[str], forbidden: list[str]) -> dict[str, Any]:
    url = f"{base.rstrip('/')}{path}"
    code, body = _fetch(url)
    missing = [m for m in markers if m not in body]
    hits = [f for f in forbidden if f in body]
    bad_placeholders = [p for p in ("loading…", "Loading pipeline from factory repository", 'id="sa-aeg-verdict">—') if p in body]
    ok = code == 200 and not missing and not hits and not bad_placeholders
    return {
        "ok": ok,
        "url": url,
        "http_code": code,
        "markers_missing": missing,
        "forbidden_hits": hits,
        "bad_placeholders": bad_placeholders,
    }


def run_script(script: str, *args: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return {"ok": proc.returncode == 0, "script": script, "code": proc.returncode, "tail": (proc.stdout or proc.stderr)[-400:]}


def verify_all(*, base: str = "https://sourcea.app") -> dict[str, Any]:
    eval_markers = ['data-sa-page="sourcea-boot-eval"', "pip install sourcea-boot", "receipts/sourcea-boot/BOOT_REPORT.json"]
    proof_markers = ['data-sa-page="proof-live"', "Evidence ID · aeg-", "Factory verdict:"]
    if "aeg-20260702" not in proof_markers[1]:
        proof_markers.append("PASS")
    row = {
        "schema": "buyer-proof-hotfix-verify-v1",
        "at": _now(),
        "grep": grep_buyer_sources(),
        "eval_live": verify_live_page(
            base=base,
            path="/eval",
            markers=eval_markers,
            forbidden=list(FORBIDDEN),
        ),
        "proof_live": verify_live_page(
            base=base,
            path="/sourcea/proof/live",
            markers=[
                'data-sa-page="proof-live"',
                "Evidence ID · aeg-",
                "Factory verdict:",
                "PASS",
                "sa-aeg-bootstrap",
            ],
            forbidden=list(FORBIDDEN) + ["Evidence ID · loading", "Loading pipeline from factory repository"],
        ),
        "batch_summary_validator": run_script("validate_cloud_forge_batch_summary_v1.py", "--batch-id", "77", "--json"),
        "dirty_tree_guard": run_script("deploy_dirty_tree_guard_v1.py", "--scope", "landing", "--json"),
    }
    row["ok"] = all(
        [
            row["grep"]["ok"],
            row["eval_live"]["ok"],
            row["proof_live"]["ok"],
            row["batch_summary_validator"]["ok"],
        ]
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="https://sourcea.app")
    ap.add_argument("--grep-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.grep_only:
        row = grep_buyer_sources()
    else:
        row = verify_all(base=args.base)
    receipt = SINA / "buyer-proof-hotfix-verify-v1.json"
    receipt.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    elif row.get("ok"):
        print("PASS buyer-proof-hotfix-verify")
    else:
        print("FAIL buyer-proof-hotfix-verify", file=sys.stderr)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
