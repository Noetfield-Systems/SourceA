#!/usr/bin/env bash
# sa-0525 — G3 vault visibility probe; PRIORITY append only when visible
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
ROOT="$(cd .. && pwd)"

python3 - <<PY
import json
import sys
from pathlib import Path

root = Path("$ROOT")
sys.path.insert(0, str(root / "scripts"))
from commercial_lane_g3_vault_v1 import (
    append_priority_g3_evidence_if_visible,
    probe_g3_vault_visibility,
    wire_g3_disk_status,
)

attach = root / "archive/attachments/2026-06-14/sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md"
wire_doc = root / "brain-os/law/WIRE_LANE_PROGRESS.md"
assert attach.is_file(), attach
assert wire_doc.is_file(), wire_doc

disk = wire_g3_disk_status()
probe = probe_g3_vault_visibility()
if not probe.get("ok"):
    raise SystemExit(f"FAIL: probe failed {probe}")

# Current disk: G3 pending — must not append yet
if probe.get("visible") and disk not in ("pass", "done", "green", "true"):
    raise SystemExit(f"FAIL: visible without disk pass inconsistent {probe}")

priority_before = (root / "brain-os/plan-registry/SOURCEA-PRIORITY.md").read_text(encoding="utf-8")
had_row = "sa-0525 Append commercial lane evidence" in priority_before

out = append_priority_g3_evidence_if_visible(dry_run=False)
if probe.get("visible"):
    if not out.get("appended") and out.get("reason") not in ("already_present",):
        raise SystemExit(f"FAIL: visible but not appended {out}")
else:
    if out.get("appended"):
        raise SystemExit("FAIL: must not append PRIORITY when G3 not visible")
    if out.get("reason") != "g3_not_visible":
        raise SystemExit(f"FAIL: expected g3_not_visible got {out.get('reason')}")

priority_after = (root / "brain-os/plan-registry/SOURCEA-PRIORITY.md").read_text(encoding="utf-8")
if not probe.get("visible") and "sa-0525 Append commercial lane evidence" in priority_after and not had_row:
    raise SystemExit("FAIL: PRIORITY row added while G3 not visible")

print(f"OK: validate-commercial-lane-g3-vault-evidence-v1 · sa-0525 · visible={probe.get('visible')} disk={disk}")
PY
