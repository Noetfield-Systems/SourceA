#!/usr/bin/env bash
# sa-0523 — mergepack PROGRAM_PROGRESS.json read must not block build paths
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
ROOT="$(cd .. && pwd)"

python3 - <<PY
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path("$ROOT")
mp = Path.home() / "Desktop/mergepack/PROGRAM_PROGRESS.json"
backup = Path(tempfile.mkdtemp(prefix="mergepack-progress-missing-"))

sys.path.insert(0, str(root / "scripts"))
from mergepack_progress_read_v1 import read_mergepack_progress_safe

try:
    if mp.is_file():
        shutil.move(str(mp), str(backup / "PROGRAM_PROGRESS.json"))

    probe = read_mergepack_progress_safe()
    if probe.get("ok"):
        raise SystemExit("FAIL: read_mergepack_progress_safe must fail ok when file missing")
    if not probe.get("missing"):
        raise SystemExit(f"FAIL: expected missing=True, got {probe}")

    env = {
        **__import__("os").environ,
        "SINA_SKIP_NESTED_BOWL": "1",
        "SINA_SKIP_FLEET_SCAN": "1",
    }
    proc = subprocess.run(
        [sys.executable, str(root / "scripts/update-program-progress.py")],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"FAIL: update-program-progress must not block when mergepack missing "
            f"rc={proc.returncode} err={proc.stderr[:300]}"
        )

    import importlib

    lib = importlib.import_module("sina_command_lib")
    payload = lib.build_payload(run_refresh_scripts=False)
    if not payload.get("command_center"):
        raise SystemExit("FAIL: build_payload must succeed when mergepack progress missing")
finally:
    if (backup / "PROGRAM_PROGRESS.json").is_file():
        if mp.is_file():
            mp.unlink()
        shutil.move(str(backup / "PROGRAM_PROGRESS.json"), str(mp))
    backup.rmdir()

print("OK: validate-mergepack-progress-nonblocking-v1 · sa-0523")
PY
