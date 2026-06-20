#!/usr/bin/env python3
"""Debug Mac Law E2E — NDJSON evidence for cockpit + session gate chains."""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEBUG_LOG = ROOT / ".cursor" / "debug-baabac.log"
SESSION_ID = "baabac"
SINA = Path.home() / ".sina"


def _ts() -> int:
    return int(time.time() * 1000)


def _dbg(*, hypothesis_id: str, location: str, message: str, data: dict, run_id: str = "pre-fix") -> None:
    # #region agent log
    row = {
        "sessionId": SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": _ts(),
    }
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    # #endregion


def _probe(url: str, *, timeout: float = 3.0) -> dict:
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            code = int(getattr(resp, "status", 200) or 200)
            body = resp.read(256).decode("utf-8", errors="replace")
        return {"ok": code < 400, "http": code, "ms": round((time.monotonic() - t0) * 1000, 1), "preview": body[:80]}
    except Exception as exc:
        return {"ok": False, "http": 0, "ms": round((time.monotonic() - t0) * 1000, 1), "error": str(exc)[:100]}


def _launchd(label: str) -> dict:
    uid = subprocess.check_output(["id", "-u"], text=True).strip()
    try:
        out = subprocess.check_output(["launchctl", "print", f"gui/{uid}/{label}"], text=True, stderr=subprocess.STDOUT, timeout=5)
        return {"loaded": True, "state": "running" if "state = running" in out else "unknown", "preview": out[:200]}
    except subprocess.CalledProcessError as exc:
        return {"loaded": False, "error": (exc.output or str(exc))[:120]}


def _flags() -> dict:
    names = [
        "mac-control-plane-v1.flag",
        "founder-work-mode-v1.flag",
        "cli-disabled-v1.flag",
        "api-disabled-v1.flag",
        "auto-run-disabled-v1.flag",
        "mac-health-quiet-v1.flag",
    ]
    return {n: (SINA / n).is_file() for n in names}


def run(*, run_id: str = "pre-fix") -> dict:
    surfaces = [
        ("mac_law", "http://127.0.0.1:8781/", "http://127.0.0.1:8781/api/mac-law/health", "com.sourcea.mac-law"),
        ("routing_panel", "http://127.0.0.1:8780/", "http://127.0.0.1:8780/api/panel/health", "com.sourcea.routing-panel"),
        ("hub", "http://127.0.0.1:13020/", "http://127.0.0.1:13020/health", "com.sourcea.hub"),
        ("mac_health", "http://127.0.0.1:13024/", "http://127.0.0.1:13024/health", None),
    ]

    # H1: launchd not loaded
    for sid, _page, _health, label in surfaces:
        if label:
            ld = _launchd(label)
            _dbg(hypothesis_id="H1", location="debug_mac_law_e2e_v1.py:launchd", message="launchd state", data={"surface": sid, "label": label, **ld}, run_id=run_id)

    # H2/H4: HTTP probe per surface
    probe_rows = []
    for sid, page, health, label in surfaces:
        hp = _probe(health)
        pp = _probe(page)
        row = {"id": sid, "health": hp, "page": pp, "label": label}
        probe_rows.append(row)
        _dbg(hypothesis_id="H2", location="debug_mac_law_e2e_v1.py:probe", message="url probe", data=row, run_id=run_id)

    # H3: control plane flag drift
    fl = _flags()
    _dbg(
        hypothesis_id="H3",
        location="debug_mac_law_e2e_v1.py:flags",
        message="control plane flags",
        data=fl,
        run_id=run_id,
    )

    # H4: surfaces API aggregate
    api = _probe("http://127.0.0.1:8781/api/mac-law/surfaces", timeout=8)
    api_body: dict = {}
    if api.get("ok"):
        try:
            api_body = json.loads(urllib.request.urlopen("http://127.0.0.1:8781/api/mac-law/surfaces", timeout=8).read())
        except Exception:
            pass
    _dbg(hypothesis_id="H4", location="debug_mac_law_e2e_v1.py:surfaces_api", message="surfaces API", data={"probe": api, "ok": api_body.get("ok"), "passed": api_body.get("passed"), "total": api_body.get("total")}, run_id=run_id)

    # H5: session gate better_loop
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "better_loop_pulse_v1.py"), "--json"],
            text=True,
            timeout=90,
            cwd=str(ROOT),
            capture_output=True,
        )
        bl = json.loads(proc.stdout) if proc.stdout.strip() else {"ok": False, "parse_error": True}
        reds = [c.get("id") for c in (bl.get("ship_checks") or bl.get("checks") or []) if not c.get("ok", True)]
        _dbg(
            hypothesis_id="H5",
            location="debug_mac_law_e2e_v1.py:better_loop",
            message="better_loop_pulse",
            data={"ok": bl.get("ok"), "exit": proc.returncode, "red_checks": reds[:12], "line": (bl.get("better_loop_line") or "")[:100]},
            run_id=run_id,
        )
    except Exception as exc:
        _dbg(hypothesis_id="H5", location="debug_mac_law_e2e_v1.py:better_loop", message="better_loop error", data={"error": str(exc)[:120]}, run_id=run_id)
        bl = {"ok": False}

    cockpit_ok = all(r["health"].get("ok") and r["page"].get("ok") for r in probe_rows)
    mandatory_bad = not fl.get("mac-control-plane-v1.flag") or not fl.get("auto-run-disabled-v1.flag")
    return {
        "ok": cockpit_ok and not mandatory_bad,
        "cockpit_ok": cockpit_ok,
        "mandatory_flags_ok": not mandatory_bad,
        "better_loop_ok": bl.get("ok"),
        "probes": probe_rows,
        "flags": fl,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--run-id", default="pre-fix")
    args = ap.parse_args()
    row = run(run_id=args.run_id)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"cockpit_ok={row['cockpit_ok']} mandatory_flags_ok={row['mandatory_flags_ok']} better_loop_ok={row['better_loop_ok']}")
    return 0 if row.get("cockpit_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
