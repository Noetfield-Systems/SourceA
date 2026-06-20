#!/usr/bin/env bash
# validate-h2-light-refresh-no-panel-build-v1.sh — sa-0817 Hub 2 light refresh must not run build-sina-command-panel
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-light-refresh-no-panel-build-v1 — $*" >&2; exit 1; }

for f in \
  "$ROOT/scripts/hub_dual_heal_v1.py" \
  "$ROOT/scripts/worker_hub_heal_v1.py" \
  "$ROOT/scripts/machine_hub_v1.py" \
  "$ROOT/scripts/machine_hub_bundle_v1.py" \
  "$ROOT/SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md"; do
  [[ -f "$f" ]] || fail "missing $f"
done

python3 - <<'PY' || fail "static chain audit"
from pathlib import Path

ROOT = Path(".")
BLOCK = "build-sina-command-panel.py"
ALLOW_IMPORT_ONLY = {
    "sina_command_lib.py": "_apply_factory_freeze_from_lib",
}

def audit(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if BLOCK not in text:
        return
    if path.name == "sina_command_lib.py":
        if ALLOW_IMPORT_ONLY["sina_command_lib.py"] in text and text.count("subprocess") == 0:
            return
    if "subprocess" in text and BLOCK in text:
        raise SystemExit(f"{path}: subprocess invokes panel build")
    if "Popen" in text and BLOCK in text:
        raise SystemExit(f"{path}: Popen invokes panel build")
    if f'bash", str(SOURCE_A / "scripts" / "{BLOCK}"' in text:
        raise SystemExit(f"{path}: bash panel build")
    if f'["bash", str(ROOT / "scripts" / "{BLOCK}"' in text:
        raise SystemExit(f"{path}: bash panel build")

for rel in (
    "scripts/hub_dual_heal_v1.py",
    "scripts/worker_hub_heal_v1.py",
    "scripts/machine_hub_v1.py",
    "scripts/machine_hub_bundle_v1.py",
):
    audit(ROOT / rel)

lib = (ROOT / "scripts/sina_command_lib.py").read_text(encoding="utf-8")
if "def hub_light_refresh" not in lib:
    raise SystemExit("hub_light_refresh missing")
if "run_refresh_scripts=False" not in lib and "HUB-LITE" not in lib:
    raise SystemExit("hub_light_refresh must avoid full refresh scripts")
if "get_hub_payload(run_refresh_scripts=False" not in lib:
    raise SystemExit("hub_light_refresh must use run_refresh_scripts=False path")

mh = (ROOT / "scripts/machine_hub_v1.py").read_text(encoding="utf-8")
if '"mode": "light"' not in mh:
    raise SystemExit("machine_hub actions missing light refresh mode")

law = (ROOT / "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md").read_text(encoding="utf-8")
if "never" not in law.lower() or "build" not in law.lower():
    raise SystemExit("SUPER_FAST_HUB law missing no-rebuild clause")

print("OK: static audit — H2 heal chain has no panel build subprocess")
PY

python3 "$ROOT/scripts/hub_dual_heal_v1.py" --json >/dev/null || fail "hub_dual_heal dry run"

python3 - <<'PY' || fail "live heal receipt"
import json
import os
from pathlib import Path

receipt = Path(os.path.expanduser("~/.sina/two-hub-heal-receipt-v1.json"))
if not receipt.is_file():
    raise SystemExit("missing two-hub-heal-receipt after heal")
row = json.loads(receipt.read_text())
steps = {s["step"]: s for s in row.get("steps") or []}
for need in ("h2_registry_sync", "h2_payload_refresh"):
    if not steps.get(need, {}).get("ok"):
        raise SystemExit(f"heal step failed: {need}")
text = json.dumps(row)
if "build-sina-command-panel" in text:
    raise SystemExit("heal receipt mentions panel build execution")
print(f"OK: hub_dual_heal receipt ok={row.get('ok')} at={row.get('at')}")
PY

echo "OK: validate-h2-light-refresh-no-panel-build-v1 · sa-0817"
