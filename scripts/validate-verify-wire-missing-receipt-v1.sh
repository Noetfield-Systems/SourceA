#!/usr/bin/env bash
# sa-0522 — negative probe: verify:wire must fail when run receipt artifacts absent
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from runreceipt.pack_v1 import OUT_DIR, REQUIRED_ARTIFACT_FILES, assert_runreceipt_artifacts

# Ensure positive path works when artifacts present
built = assert_runreceipt_artifacts()
if not built.get("ok"):
    from runreceipt.pack_v1 import build_pack

    pack = build_pack(status="PASS")
    if not pack.get("ok"):
        raise SystemExit(f"FAIL: build_pack for negative probe: {pack}")
    built = assert_runreceipt_artifacts()
    if not built.get("ok"):
        raise SystemExit(f"FAIL: artifacts still missing after build: {built}")

backup = Path(tempfile.mkdtemp(prefix="verify-wire-missing-"))
try:
    for name in REQUIRED_ARTIFACT_FILES:
        src = OUT_DIR / name
        if src.is_file():
            shutil.move(str(src), str(backup / name))

    probe = assert_runreceipt_artifacts()
    if probe.get("ok"):
        raise SystemExit("FAIL: assert_runreceipt_artifacts must fail when artifacts removed")

    proc = subprocess.run(["bash", "validate-verify-wire-v1.sh"], capture_output=True, text=True)
    if proc.returncode == 0:
        raise SystemExit("FAIL: validate-verify-wire-v1.sh must exit non-zero when artifacts missing")
    if "missing run receipt" not in (proc.stdout + proc.stderr).lower():
        raise SystemExit(
            f"FAIL: expected missing-receipt message, got rc={proc.returncode} out={proc.stdout!r} err={proc.stderr!r}"
        )
finally:
    for name in REQUIRED_ARTIFACT_FILES:
        src = backup / name
        dst = OUT_DIR / name
        if src.is_file():
            if dst.is_file():
                dst.unlink()
            shutil.move(str(src), str(dst))
    backup.rmdir()

print("OK: validate-verify-wire-missing-receipt-v1 · negative probe PASS")
PY
