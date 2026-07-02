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


LOADING_PLACEHOLDERS = (
    "loading…",
    "Loading…",
    "Loading pipeline from factory repository",
    "Loading checks…",
    "Loading transcript…",
)

AEG_EMDASH_SLOTS = (
    'id="sa-aeg-verdict">—',
    'id="sa-aeg-proof-viewed">—',
    'id="sa-aeg-eval-scheduled">—',
    'id="sa-aeg-deposits">—',
)

PROOF_EMDASH_SLOTS = AEG_EMDASH_SLOTS + (
    "data-trust-valid-yes>—",
    "data-trust-governance>—",
)


def verify_live_page(
    *, base: str, path: str, markers: list[str], forbidden: list[str], emdash_slots: tuple[str, ...] = AEG_EMDASH_SLOTS
) -> dict[str, Any]:
    url = f"{base.rstrip('/')}{path}"
    code, body = _fetch(url)
    missing = [m for m in markers if m not in body]
    hits = [f for f in forbidden if f in body]
    bad_placeholders = [p for p in LOADING_PLACEHOLDERS if p in body]
    emdash = [p for p in emdash_slots if p in body]
    ok = code == 200 and not missing and not hits and not bad_placeholders and not emdash
    return {
        "ok": ok,
        "url": url,
        "http_code": code,
        "markers_missing": missing,
        "forbidden_hits": hits,
        "bad_placeholders": bad_placeholders,
        "emdash_slots": emdash,
    }


def run_script(script: str, *args: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return {"ok": proc.returncode == 0, "script": script, "code": proc.returncode, "tail": (proc.stdout or proc.stderr)[-400:]}


PROOF_MARKERS = [
    'data-sa-page="proof-live"',
    "Evidence ID · aeg-",
    "Factory verdict:",
    "PASS",
    "sa-aeg-bootstrap",
    "[PASS] provider",
]


def _extract_terminal_pre(body: str) -> str:
    m = re.search(r'id="sa-aeg-terminal"[^>]*>(.*?)</pre>', body, re.DOTALL)
    return m.group(1) if m else ""


# Raw markers that must never appear anywhere in buyer-facing proof HTML
# (page shell, hydrated slots, or the bootstrap JSON blob).
BLOCK_MARKERS = (
    "CRITIC_BOOT",
    "BLOCK ok=False",
    "ok=False",
    "[FAIL]",
    "gate_fresh",
    "last session gate receipt ok=false",
)


def check_proof_contradiction(body: str) -> list[str]:
    issues: list[str] = []
    hero_pass = (
        'id="sa-aeg-verdict">PASS' in body
        or 'sa-aeg-verdict-hero is-pass" id="sa-aeg-verdict">PASS' in body
    )
    no_blockers = "No blockers" in body
    # Strict: fail on ANY raw BLOCK/FAIL marker anywhere in the public body.
    global_hits = sorted({m for m in BLOCK_MARKERS if m in body})
    if global_hits:
        issues.append(f"block_markers_in_public_html:{global_hits}")
    if hero_pass and global_hits:
        issues.append("hero_pass_with_block_markers")
    if no_blockers and global_hits:
        issues.append("no_blockers_with_block_markers")
    return issues


def verify_eval_live(base: str) -> dict[str, Any]:
    row = verify_live_page(
        base=base,
        path="/eval",
        markers=['data-sa-page="sourcea-boot-eval"', "pip install sourcea-boot", "receipts/sourcea-boot/BOOT_REPORT.json"],
        forbidden=list(FORBIDDEN),
    )
    row["local_path_leak"] = row.get("forbidden_hits") or []
    row["ok"] = bool(row.get("ok")) and not row["local_path_leak"]
    return row


def _verify_proof_url(url: str) -> dict[str, Any]:
    code, body = _fetch(url)
    missing = [m for m in PROOF_MARKERS if m not in body]
    hits = [f for f in FORBIDDEN if f in body]
    bad_placeholders = [p for p in LOADING_PLACEHOLDERS if p in body]
    emdash = [p for p in PROOF_EMDASH_SLOTS if p in body]
    contradictions = check_proof_contradiction(body)
    ok = code == 200 and not missing and not hits and not bad_placeholders and not emdash and not contradictions
    return {
        "ok": ok,
        "url": url,
        "http_code": code,
        "markers_missing": missing,
        "forbidden_hits": hits,
        "bad_placeholders": bad_placeholders,
        "emdash_slots": emdash,
        "contradictions": contradictions,
    }


def verify_proof_live(base: str) -> dict[str, Any]:
    b = base.rstrip("/")
    # Verify both the clean path and the .html variant of the deployed public HTML.
    primary = _verify_proof_url(f"{b}/sourcea/proof/live")
    html_variant = _verify_proof_url(f"{b}/sourcea/proof/live.html")
    primary["html_variant"] = html_variant
    primary["ok"] = bool(primary["ok"]) and bool(html_variant["ok"])
    return primary


def verify_all(*, base: str = "https://sourcea.app", hosts: list[str] | None = None) -> dict[str, Any]:
    hosts = hosts or ["https://sourcea.app", "https://www.sourcea.app"]
    eval_by_host = {h: verify_eval_live(h) for h in hosts}
    proof_by_host = {h: verify_proof_live(h) for h in hosts}
    row = {
        "schema": "buyer-proof-hotfix-verify-v1",
        "at": _now(),
        "grep": grep_buyer_sources(),
        "eval_live": eval_by_host.get(base, verify_eval_live(base)),
        "eval_live_hosts": eval_by_host,
        "proof_live": proof_by_host.get(base, verify_proof_live(base)),
        "proof_live_hosts": proof_by_host,
        "batch_summary_validator": run_script("validate_cloud_forge_batch_summary_v1.py", "--batch-id", "77", "--json"),
        "dirty_tree_guard": run_script("deploy_dirty_tree_guard_v1.py", "--scope", "landing", "--json"),
    }
    row["ok"] = all(
        [
            row["grep"]["ok"],
            all(v["ok"] for v in eval_by_host.values()),
            all(v["ok"] for v in proof_by_host.values()),
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
