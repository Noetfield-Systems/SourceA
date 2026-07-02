#!/usr/bin/env bash
# sourcea-sdk lightweight validator — import · sign · replay · portable paths only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="${ROOT}/packages/sourcea-sdk"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export PKG_ROOT="$PKG"

cd "$TMP"
export PYTHONPATH="${PKG}/src:${PYTHONPATH:-}"

python3 - <<'PY'
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

pkg = Path(os.environ["PKG_ROOT"])
sys.path.insert(0, str(pkg / "src"))

from sourcea_sdk import sign_receipt, verify_receipt, append_spine_event, tail_spine

work = Path(tempfile.mkdtemp(prefix="sourcea-sdk-"))
os.chdir(work)

# 1 import
print("OK: sourcea-sdk import")

# 2 sign roundtrip
intent = {"intent_id": "validate-sdk-v1", "object_id": "validate-sdk-v1", "action": "probe"}
spine = append_spine_event(
    event_type="VALIDATOR_PASS",
    object_id="validate-sourcea-sdk-v1",
    object_kind="system",
    payload={"probe": True},
)
assert spine["ok"], spine
rec = sign_receipt(intent=intent, bind_spine=True, spine_event=spine)
ok, reason = verify_receipt(rec)
assert ok, reason
print("OK: sign + replay roundtrip")

# 3 spine tail
rows = tail_spine(n=3)
assert rows, "spine empty"
print(f"OK: spine-tail · {len(rows)} row(s)")

# 4 portable paths only
assert (work / ".sourcea" / "spine-v1.jsonl").is_file()
assert (work / ".sourcea" / "receipts" / "latest.json").is_file()
print("OK: portable .sourcea/ paths")

# 5 CLI smoke
proc = subprocess.run(
    ["python3", "-m", "sourcea_sdk.cli", "replay", "--last"],
    cwd=work,
    env={**os.environ, "PYTHONPATH": str(pkg / "src")},
    capture_output=True,
    text=True,
)
assert proc.returncode == 0, proc.stderr
print("OK: validate-sourcea-sdk-v1 · standalone package")
PY
