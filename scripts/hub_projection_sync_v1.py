#!/usr/bin/env python3
"""Zero-latency hub projection sync — rebuild command-data after honest writes (AS zero-latency)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def sync_hub_projection(*, caller: str = "", strict: bool = False, timeout: int = 120) -> dict:
    """Align command-data from SSOT builders; optional strict full panel build."""
    script = "build-sina-command-panel.py" if strict else "align_command_data_ui_v1.py"
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = {
        "ok": proc.returncode == 0,
        "caller": caller,
        "script": script,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-500:],
        "stderr_tail": (proc.stderr or "")[-500:],
    }
    if proc.returncode == 0 and not strict:
        chk = subprocess.run(
            ["bash", str(SCRIPTS / "validate-hub-p0-no-autorun-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        out["as01_ok"] = chk.returncode == 0
        out["ok"] = out["ok"] and chk.returncode == 0
        if chk.returncode != 0:
            out["as01_stderr"] = (chk.stderr or chk.stdout or "")[-300:]
    return out


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Sync hub projection from disk SSOT")
    p.add_argument("--caller", default="cli")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = sync_hub_projection(caller=args.caller, strict=args.strict)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
