#!/usr/bin/env python3
"""Main problem trigger — founder says 'main problem' → PREPARE next action (not report).

SSOT: data/sourcea-main-problem-trigger-v1.json
Receipt: ~/.sina/main-problem-trigger-receipt-v1.json
"""
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

FORM_PAGE_URL = "http://127.0.0.1:13023/form/"
CW_COCKPIT_URL = "http://127.0.0.1:13027/"
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/sourcea-main-problem-trigger-v1.json"
RECEIPT = SINA / "main-problem-trigger-receipt-v1.json"
FLAG = SINA / "main-problem-trigger-active-v1.flag"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _expand(raw: str) -> Path:
    return Path(str(raw or "").replace("~", str(Path.home()))).expanduser()


def _matches_trigger(text: str, phrases: list[str]) -> bool:
    t = (text or "").lower()
    return any(p.lower() in t for p in phrases)


def _fbe_health(url: str) -> bool:
    if not url.startswith("https://"):
        return False
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/health", timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return bool(body.get("ok")) and str(body.get("service", "")).startswith("fbe")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return False


def _disk_snapshot() -> dict:
    cfg = _read(ROOT / "data/fbe_cloud_worker_config_v1.json")
    fbe_url = str(cfg.get("worker_url") or "")
    deploy = _read(SINA / "fbe-cloud-deploy-receipt-v1.json")
    bay = _read(SINA / "fbe-bay-run-receipt-v1.json")
    tf = _read(SINA / "trustfield-sandbox-receipt-v1.json")
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    form: dict = {}
    try:
        sys.path.insert(0, str(SCRIPTS))
        from live_founder_decision_form_v1 import payload  # noqa: WPS433

        form = payload()
    except Exception:
        pass
    portfolio = _read(SINA / "portfolio-fix-plan-pulse-v1.json")
    wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    drain = _read(ROOT / "data/cloud-forge-run-queue-active-v1.json")
    cloud_batch_complete = bool(drain.get("queue_batch_complete"))
    return {
        "fbe_url": fbe_url,
        "fbe_public_ok": _fbe_health(fbe_url),
        "deploy_ok": bool(deploy.get("ok")),
        "nf_bay_ok": bool(bay.get("ok")),
        "tf_sandbox_ok": bool(tf.get("ok")),
        "form_open": int(form.get("open_questions_count") or 0),
        "cloud_batch_complete": cloud_batch_complete,
        "cloud_workers_cockpit": CW_COCKPIT_URL,
        "form_page_url": FORM_PAGE_URL,
        "factory_now_line": surfaces.get("factory_now_line") or "",
        "cloud_300_line": surfaces.get("cloud_practical_300_line") or "",
        "portfolio_line": portfolio.get("portfolio_fix_line") or "",
        "work_order_bay": wo.get("bay_slug") or "",
        "execution_mode": wo.get("execution_mode") or "",
    }


def _pick_next_action(ssot: dict, snap: dict) -> dict:
    """One bounded next action on north star — not a report list."""
    if not snap.get("fbe_public_ok"):
        return {
            "id": "P2",
            "action": "wire_fbe_railway",
            "command": "python3 scripts/cloud_factory_10_steps_v1.py --step 2 --json",
            "because": "Public FBE cloud worker must be live before bays count as cloud-first",
        }
    if not snap.get("nf_bay_ok"):
        return {
            "id": "P0",
            "action": "dispatch_noetfield_freemium_bay",
            "command": "python3 scripts/cloud_factory_10_steps_v1.py --step 5 --json",
            "because": "Phase 0 north star starts with Noetfield freemium on cloud",
        }
    if not snap.get("tf_sandbox_ok"):
        return {
            "id": "P1",
            "action": "run_trustfield_sandbox_bay",
            "command": "python3 scripts/cloud_factory_10_steps_v1.py --step 8 --json",
            "because": "TrustField sandbox is P1 after NF bay on cloud path",
        }
    if snap.get("form_open", 0) > 0:
        batch_note = " · batch200=COMPLETE" if snap.get("cloud_batch_complete") else ""
        return {
            "id": "P3",
            "action": "form_batch_submit_ready",
            "surface": FORM_PAGE_URL,
            "cockpit": CW_COCKPIT_URL,
            "because": (
                f"{snap['form_open']} founder PICKs open — batch submit on Chat Unify /form/ "
                f"wires nerves to disk{batch_note}"
            ),
        }
    return {
        "id": "P4",
        "action": "portfolio_or_commercial_parallel",
        "because": "Cloud bays green — parallel track is portfolio/commercial defer (WitnessBC prod)",
        "ssot": "data/portfolio-fix-plan-v1.json",
    }


def activate(*, founder_text: str = "", write: bool = True) -> dict:
    ssot = _read(SSOT)
    phrases = ssot.get("trigger_phrases") or ["main problem"]
    triggered = _matches_trigger(founder_text, phrases) if founder_text else True
    snap = _disk_snapshot()
    next_action = _pick_next_action(ssot, snap)
    mp = ssot.get("main_problem") or {}
    row = {
        "schema": "main-problem-trigger-receipt-v1",
        "at": _now(),
        "ok": True,
        "triggered": triggered,
        "mode": "PREPARE_NOT_REPORT",
        "north_star": ssot.get("north_star"),
        "main_problem_summary": (mp.get("summary") or "")[:400],
        "forbidden_now": mp.get("forbidden_when_triggered") or [],
        "prepare_mode": mp.get("prepare_mode") or {},
        "disk_snapshot": snap,
        "next_action": next_action,
        "main_problem_line": (
            f"main-problem · PREPARE · next={next_action.get('id')} · "
            f"{next_action.get('action')} · fbe={'PASS' if snap.get('fbe_public_ok') else 'RED'} · "
            f"batch200={'COMPLETE' if snap.get('cloud_batch_complete') else 'OPEN'} · "
            f"form_open={snap.get('form_open', 0)} · form={FORM_PAGE_URL}"
        ),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        FLAG.write_text(f"activated_at={row['at']}\nmode=PREPARE_NOT_REPORT\n", encoding="utf-8")
    return row


def inject_slice() -> dict:
    ssot = _read(SSOT)
    mp = ssot.get("main_problem") or {}
    out = {
        "trigger_phrases": ssot.get("trigger_phrases") or [],
        "north_star": ssot.get("north_star"),
        "one_law": ssot.get("one_law"),
        "summary": mp.get("summary"),
        "prepare_mode": mp.get("prepare_mode"),
        "forbidden_when_triggered": mp.get("forbidden_when_triggered") or [],
        "command_on_trigger": "python3 scripts/main_problem_trigger_v1.py --activate --text '<founder message>' --json",
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if FLAG.is_file():
        row = _read(RECEIPT)
        out["active"] = True
        out["mode"] = row.get("mode") or "PREPARE_NOT_REPORT"
        out["next_action"] = row.get("next_action")
        out["main_problem_line"] = row.get("main_problem_line")
        out["disk_snapshot"] = row.get("disk_snapshot")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Main problem trigger v1")
    ap.add_argument("--text", default="", help="Founder message to match triggers")
    ap.add_argument("--activate", action="store_true", help="Write receipt + flag (PREPARE mode)")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.inject:
        row = inject_slice()
    elif args.activate or _matches_trigger(args.text, _read(SSOT).get("trigger_phrases") or []):
        row = activate(founder_text=args.text, write=args.activate or bool(args.text))
    else:
        row = {"ok": True, "triggered": False, "note": "no trigger phrase in text"}
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("main_problem_line") or row.get("note") or json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
