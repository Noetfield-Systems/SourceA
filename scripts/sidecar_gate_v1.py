#!/usr/bin/env python3
"""CLI ACT must not run blind — Scout (B) + Prep (C) first, then CLI."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SCOUT_DIR = Path.home() / ".sina" / "sidecar" / "api-scout"
PREP_DIR = Path.home() / ".sina" / "sidecar" / "cli-prep"
SIDECAR_PID = Path.home() / ".sina" / "sidecar-engines-watch-v1.pid"
MAX_AGE_SEC = 3600


def _usable(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 120:
        return False
    body = path.read_text(encoding="utf-8", errors="replace").lower()
    junk = ("don't have access", "cannot retrieve", "paste the content", "no scout yet")
    return not any(j in body for j in junk)


def _fresh(path: Path) -> bool:
    return _usable(path) and (time.time() - path.stat().st_mtime) < MAX_AGE_SEC


def scout_prep_status(*, sa_id: str) -> dict:
    scout = SCOUT_DIR / f"{sa_id}-scout.md"
    prep = PREP_DIR / f"{sa_id}-prep.md"
    return {
        "sa_id": sa_id,
        "scout_path": str(scout),
        "prep_path": str(prep),
        "scout_ok": _usable(scout),
        "prep_ok": _usable(prep),
        "scout_fresh": _fresh(scout),
        "prep_fresh": _fresh(prep),
        "ready": _usable(scout) and _usable(prep),
    }


def _run_sidecar_once() -> dict:
    rows = []
    for script in ("sidecar_scout_api_v1.py", "sidecar_prep_cli_v1.py"):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / script), "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ROOT),
        )
        try:
            body = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except json.JSONDecodeError:
            body = {"raw": proc.stdout[:500], "stderr": proc.stderr[:300]}
        rows.append({"script": script, "rc": proc.returncode, "body": body})
    return {"ok": all(r["rc"] == 0 for r in rows), "runs": rows}


def ensure_scout_prep_for_act(*, sa_id: str) -> dict:
    """Run Scout+Prep once if missing — cheap API before expensive CLI."""
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from paid_engine_gate_v1 import block_paid  # noqa: WPS433

    gate = block_paid(engine="api", caller="sidecar_gate")
    if gate:
        st = scout_prep_status(sa_id=sa_id)
        if st.get("ready"):
            return {"ok": True, "skipped": "scout_prep_ready", **st}
        return {"ok": False, "reason": "paid_api_blocked", **gate, **st}

    st = scout_prep_status(sa_id=sa_id)
    if st.get("ready"):
        return {"ok": True, "skipped": "scout_prep_ready", **st}

    ran = _run_sidecar_once()
    st = scout_prep_status(sa_id=sa_id)
    if st.get("ready"):
        return {"ok": True, "ensured": True, "sidecar_run": ran, **st}
    return {
        "ok": False,
        "reason": "scout_prep_missing",
        "hint": "Start B Scout watch or wait for sidecar tick",
        "sidecar_run": ran,
        **st,
    }


def sidecar_watch_alive() -> bool:
    if not SIDECAR_PID.is_file():
        return False
    try:
        pid = int(SIDECAR_PID.read_text().strip())
        import os

        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--sa-id", required=True)
    p.add_argument("--ensure", action="store_true")
    args = p.parse_args()
    if args.ensure:
        print(json.dumps(ensure_scout_prep_for_act(sa_id=args.sa_id), indent=2))
    else:
        print(json.dumps(scout_prep_status(sa_id=args.sa_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
