#!/usr/bin/env python3
"""Anti-Poison Engine v2 — unified detect · classify · sanitize · receipt.

T0 Safety node — law poison + projection poison + positive inject schema.
Law: SINA_POISON_TRACKING_METHOD_LOCKED_v1.md · agent-memory-mirror-poison-law-v1.json
Mac founder session: validate-only · no scrub marathon (INCIDENT-039).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "anti-poison-engine-v2-receipt-v1.json"

sys.path.insert(0, str(SCRIPTS))
from anti_poison_lib_v1 import (  # noqa: E402
    _now,
    check_positive_inject,
    load_registry,
    mac_founder_session,
    sanitize_projection_file,
    scan_repo,
    ship_window_active,
)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run_scrub_validate() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "agent_mirror_poison_scrub_v1.py"), "--validate", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    out = proc.stdout or ""
    i = out.find("{")
    row = json.loads(out[i:]) if i >= 0 else {"ok": False, "raw": out[:300]}
    row["exit"] = proc.returncode
    return row


def _run_vocab() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "vocabulary_guard_v1.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    out = proc.stdout or ""
    i = out.find("{")
    return json.loads(out[i:]) if i >= 0 else {"ok": False, "raw": out[:300]}


def classify_hits(law_hits: list[dict], proj_hits: list[dict]) -> list[str]:
    classes: list[str] = []
    if law_hits:
        classes.append("P1-INJECT")
    if proj_hits:
        classes.append("P5-PROJECTION")
    for h in law_hits + proj_hits:
        inc = str(h.get("incident") or "")
        m = str(h.get("match") or "").lower()
        if inc in ("042", "043") or "full_pack" in m or "cloud-sec" in m:
            if "P11-DRAIN" not in classes:
                classes.append("P11-DRAIN")
        if "13020" in m or "worker hub" in m.lower():
            if "P13-SURFACE-TRASH" not in classes:
                classes.append("P13-SURFACE-TRASH")
        if "sourcea.com" in m or "hello@sourcea" in m:
            if "P12-URL" not in classes:
                classes.append("P12-URL")
    return classes or (["CLEAN"] if not law_hits and not proj_hits else ["P1-INJECT"])


def run(
    *,
    tier: str = "fast",
    sanitize: bool = False,
    dry_run: bool = False,
) -> dict:
    reg = load_registry()
    law_hits = scan_repo(projection=False)
    proj_hits = scan_repo(projection=True) if tier in ("full", "projection") else []

    # Dedupe projection hits already in law scan
    law_paths = {h.get("path") for h in law_hits}
    proj_hits = [h for h in proj_hits if h.get("path") not in law_paths or h.get("projection")]

    scrub = _run_scrub_validate()
    vocab = _run_vocab() if tier == "full" else {"ok": True, "skipped": "fast_tier"}

    mirror = _read_json(SINA / "agent-memory-mirror-v1.json")
    positive = check_positive_inject(mirror.get("inject") or {})

    sanitized: list[dict] = []
    if sanitize and ship_window_active() and not mac_founder_session():
        panel = ROOT / "agent-control-panel"
        for path in list(panel.glob("command-data*.json")) + [panel / "worker-hub" / "boot.json"]:
            sanitized.append(sanitize_projection_file(path, dry_run=dry_run))
    elif sanitize and mac_founder_session():
        sanitized.append({"skipped": "mac_founder_session — sanitize ship window only"})

    p_classes = classify_hits(law_hits, proj_hits)
    law_ok = len(law_hits) == 0 and scrub.get("ok", False)
    proj_ok = len(proj_hits) == 0
    surfaces = _read_json(SINA / "agent-live-surfaces-v1.json")
    realtime_blockers: list[dict] = []
    if not str(surfaces.get("factory_now_line") or "").strip():
        realtime_blockers.append(
            {
                "id": "empty_factory_now_line",
                "class": "realtime_blocker",
                "fix": "python3 scripts/disk_live_wire_sync_v1.py --json",
            }
        )
    if proj_hits:
        realtime_blockers.append(
            {
                "id": "hub_projection_poison",
                "class": "realtime_blocker",
                "count": len(proj_hits),
                "fix": "python3 scripts/projection_poison_sanitize_v1.py --json (ship window)",
            }
        )

    if tier == "fast":
        report_ok = law_ok
    elif tier == "projection":
        report_ok = proj_ok
    else:
        report_ok = law_ok and proj_ok and positive.get("ok", True) and vocab.get("ok", True)
    report = {
        "schema": "anti-poison-engine-v2",
        "version": "2.0.0",
        "at": _now(),
        "tier": tier,
        "registry_version": reg.get("version"),
        "p_class": p_classes,
        "law_hits": law_hits,
        "projection_hits": proj_hits,
        "law_ok": law_ok,
        "projection_ok": proj_ok,
        "scrub": {"ok": scrub.get("ok"), "hits": len(scrub.get("poison_hits") or [])},
        "vocabulary": {"ok": vocab.get("ok"), "violations": vocab.get("violations") or []},
        "positive_inject": positive,
        "realtime_blockers": realtime_blockers,
        "sanitized": sanitized,
        "ok": report_ok,
        "mac_session": mac_founder_session(),
        "ship_window": ship_window_active(),
        "mandatory_next": (
            "Read ~/.sina/anti-poison-engine-v2-receipt-v1.json · fix projection writer · re-run ship window sanitize"
            if proj_hits
            else "Law poison clean — maintain positive inject + live surfaces wire"
        ),
    }
    try:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        fallback = ROOT / "data" / "anti-poison-engine-v2-receipt-v1.json"
        fallback.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["receipt_fallback"] = str(fallback)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Anti-Poison Engine v2")
    ap.add_argument("--tier", choices=("fast", "full", "projection"), default="fast")
    ap.add_argument("--sanitize", action="store_true", help="Rewrite projection files (ship window only)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = run(tier=args.tier, sanitize=args.sanitize, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"ANTI_POISON_V2 ok={report['ok']} law={len(report['law_hits'])} "
            f"proj={len(report['projection_hits'])} class={report['p_class']}"
        )
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
