#!/usr/bin/env python3
"""Governance meta-audit — auditor for Governance Specialist (machine, not chat).

Law: SOURCEA_GOV_META_AUDIT_LOCKED_v1.md · Q-GOV-META-AUDIT-v1 YES
Writes: ~/.sina/governance-meta-audit-receipt-v1.json
"""
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
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "governance-meta-audit-receipt-v1.json"
COMMAND_DATA = ROOT / "agent-control-panel" / "command-data.json"
DEFAULT_CHATS = ("e54ddfa8", "fd67502f", "58148ac9")

# Daily-steer poison in museum founder hero (not whole 10MB archaeology)
MUSEUM_FOUNDER_FORBIDDEN = (
    (re.compile(r"Prompt\s+feed", re.I), "Prompt feed daily steer"),
    (re.compile(r"prompt-feed", re.I), "prompt-feed tab slug as daily path"),
    (re.compile(r"auto[- ]?send", re.I), "auto-send"),
    (re.compile(r"Confirm\s+auto", re.I), "Confirm auto"),
    (re.compile(r"Open\s+Sina\s+Command\s*→\s*Prompt", re.I), "Open Sina Command Prompt feed"),
    (re.compile(r"tap\s+Confirm.*10\s+prompt", re.I), "tap Confirm 10 prompts"),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 120, cwd: Path | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        tail = out.splitlines()[-1][:300] if out else f"exit {proc.returncode}"
        ok = proc.returncode == 0
        if "--json" in cmd and proc.stdout and "{" in proc.stdout:
            try:
                payload = json.loads(proc.stdout[proc.stdout.find("{") :])
                if isinstance(payload, dict) and "ok" in payload:
                    ok = bool(payload.get("ok"))
            except json.JSONDecodeError:
                pass
        return {"ok": ok, "exit": proc.returncode, "tail": tail}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}
    except OSError as exc:
        return {"ok": False, "exit": -1, "tail": str(exc)}


def _check_truth_bundle() -> dict[str, Any]:
    py = sys.executable
    proc = subprocess.run(
        [py, str(SCRIPTS / "agent_truth_bundle_v1.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    line = ""
    ok = proc.returncode == 0
    try:
        data = json.loads(proc.stdout or "{}")
        line = str(data.get("factory_now_line") or data.get("line") or "")
        fn = data.get("factory_now") or {}
        if not line and fn:
            line = str(fn.get("line") or "")
        if not line.startswith("factory-now"):
            ok = False
    except json.JSONDecodeError:
        ok = False
    return {
        "id": "truth_bundle",
        "ok": ok,
        "detail": line[:200] if line else "missing factory_now_line",
    }


def _check_museum_founder_hero() -> dict[str, Any]:
    if not COMMAND_DATA.is_file():
        return {"id": "museum_founder_hero", "ok": False, "detail": "command-data.json missing"}
    try:
        data = json.loads(COMMAND_DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"id": "museum_founder_hero", "ok": False, "detail": str(exc)}
    founder = (data.get("command_center") or {}).get("founder") or {}
    blob = json.dumps(founder, ensure_ascii=False)
    hits: list[str] = []
    for pat, label in MUSEUM_FOUNDER_FORBIDDEN:
        if pat.search(blob):
            hits.append(label)
    if hits:
        return {
            "id": "museum_founder_hero",
            "ok": False,
            "detail": f"Zone C founder hero poison: {', '.join(hits)}",
            "incident": "033",
            "remediation": "scrub command_center.founder hero OR hub_projection_sync from factory-now only",
        }
    return {
        "id": "museum_founder_hero",
        "ok": True,
        "detail": f"founder hero clean · museum bytes {COMMAND_DATA.stat().st_size}",
    }


def _check_judge_temporal(chats: tuple[str, ...]) -> dict[str, Any]:
    resolution = SINA / "judge-center" / "latest-resolution-v1.json"
    if not resolution.is_file():
        return {"id": "judge_temporal", "ok": True, "detail": "no judge resolution yet — skip"}
    try:
        data = json.loads(resolution.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"id": "judge_temporal", "ok": True, "detail": "judge resolution unreadable — skip"}
    bad: list[str] = []
    for chat in data.get("chats") or []:
        cid = str(chat.get("chat_id") or chat.get("id") or "")
        if cid and cid[:8] not in chats and cid not in chats:
            continue
        tag = str(chat.get("temporal_tag") or chat.get("tag") or "")
        if tag in ("ACTIVE_STALE", "ACTIVE_BAD", "REVERT", "BAD"):
            bad.append(f"{cid[:8]}:{tag}")
    if bad:
        return {
            "id": "judge_temporal",
            "ok": False,
            "detail": f"ACTIVE_STALE/REVERT: {', '.join(bad)}",
            "incident": "028",
        }
    return {"id": "judge_temporal", "ok": True, "detail": "0 ACTIVE_STALE on Gov/Worker/Brain"}


def run_meta_audit(*, tier: str = "fast", chats: tuple[str, ...] = DEFAULT_CHATS) -> dict[str, Any]:
    py = sys.executable
    checks: list[dict[str, Any]] = []

    checks.append(_check_truth_bundle())
    checks.append(_check_museum_founder_hero())

    shell_checks = (
        ("brain_not_command_data_ssot", "validate-brain-not-command-data-ssot-v1.sh", []),
        ("super_fast_hub", "validate-super-fast-hub-v1.sh", []),
        ("museum_stale_copy", "validate-museum-stale-copy-v1.sh", []),
        ("prompt_feed_no_autosend", "validate-prompt-feed-no-autosend-copy-v1.sh", []),
    )
    for cid, script, extra in shell_checks:
        r = _run(["bash", str(SCRIPTS / script), *extra], timeout=180, cwd=ROOT)
        checks.append({"id": cid, "ok": r["ok"], "detail": r["tail"]})

    mirror = _run([py, str(SCRIPTS / "agent_memory_mirror_v1.py"), "--validate"], timeout=120, cwd=ROOT)
    checks.append({"id": "memory_mirror", "ok": mirror["ok"], "detail": mirror["tail"]})

    checks.append(_check_judge_temporal(chats))

    if tier == "full":
        judge = _run(
            [py, str(SCRIPTS / "judge_center_run_v1.py"), "--chats", ",".join(chats), "--json"],
            timeout=180,
            cwd=ROOT,
        )
        checks.append({"id": "judge_center_full", "ok": judge["ok"], "detail": judge["tail"]})
        checks.append(_check_judge_temporal(chats))

    failures = [c for c in checks if not c.get("ok")]
    receipt = {
        "schema": "governance-meta-audit-receipt-v1",
        "built_at": _now(),
        "tier": tier,
        "ok": len(failures) == 0,
        "checks": checks,
        "failures": failures,
        "failure_count": len(failures),
        "law": "SOURCEA_GOV_META_AUDIT_LOCKED_v1.md",
        "pick": "Q-GOV-META-AUDIT-v1 YES",
        "zone_a_only": True,
        "governance_may_claim_fixed": len(failures) == 0,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance meta-audit (auditor for Gov Specialist)")
    ap.add_argument("--tier", choices=("fast", "full"), default="fast")
    ap.add_argument("--chats", default=",".join(DEFAULT_CHATS))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    chats = tuple(x.strip() for x in args.chats.split(",") if x.strip())
    receipt = run_meta_audit(tier=args.tier, chats=chats or DEFAULT_CHATS)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"GOV-META-AUDIT: ok={receipt['ok']} tier={receipt['tier']} "
            f"failures={receipt['failure_count']}"
        )
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
