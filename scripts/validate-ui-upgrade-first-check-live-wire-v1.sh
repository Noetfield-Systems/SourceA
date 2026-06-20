#!/usr/bin/env bash
# UI FIRST CHECK live wire — session gate + pre-write + registry + 7 ledgers
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-ui-upgrade-first-check-live-wire-v1 — $*" >&2; exit 1; }

[[ -f .cursor/rules/025-ui-upgrade-first-check-live-wire.mdc ]] || fail "rule 025 missing"
[[ -f scripts/ui_upgrade_path_classifier_v1.py ]] || fail "classifier missing"
[[ -f scripts/ui_upgrade_first_check_v1.py ]] || fail "first_check missing"

bash scripts/validate-ui-upgrade-mandatory-v1.sh || fail "mandatory validator"

python3 scripts/ui_upgrade_first_check_v1.py --wire --surface worker_hub --json >/dev/null || fail "wire"
[[ -f ~/.sina/ui-upgrade-first-check-receipt-v1.json ]] || fail "wire receipt missing"

python3 - <<'PY' || fail "receipt schema"
import json
from pathlib import Path
p = Path.home() / ".sina/ui-upgrade-first-check-receipt-v1.json"
row = json.loads(p.read_text())
assert row.get("schema") == "ui-upgrade-first-check-receipt-v1"
assert row.get("wire_ok") is True
assert row.get("first_check_cmd")
print("OK: wire receipt · wire_ok=True")
PY

python3 scripts/ui_upgrade_path_classifier_v1.py --path agent-control-panel/form/index.html --json | grep -q '"surface_id": "hub_form"' || fail "hub_form classify"
python3 scripts/ui_upgrade_path_classifier_v1.py --path agent-control-panel/worker-hub/index.html --json | grep -q '"surface_id": "worker_hub"' || fail "worker_hub classify"

# Pre-write must block UI without ack (isolate from prior test acks)
ACKS="$HOME/.sina/ui-upgrade-surface-acks-v1.json"
ACK_BACKUP=""
if [[ -f "$ACKS" ]]; then
  ACK_BACKUP="$(mktemp)"
  cp "$ACKS" "$ACK_BACKUP"
  python3 - <<'PY' || fail "ack isolate"
import json
from pathlib import Path
p = Path.home() / ".sina/ui-upgrade-surface-acks-v1.json"
if not p.is_file():
    row = {"schema": "ui-upgrade-surface-acks-v1", "acks": {}}
else:
    try:
        row = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"corrupt acks file — repair ~/.sina/ui-upgrade-surface-acks-v1.json: {exc}")
    if row.get("schema") != "ui-upgrade-surface-acks-v1":
        row = {"schema": "ui-upgrade-surface-acks-v1", "acks": {}}
acks = row.get("acks") or {}
acks.pop("hub_form", None)
acks.pop("worker_hub", None)
row["acks"] = acks
p.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
PY
fi

python3 - <<PY || fail "pre_write should block form UI without ack"
import json, subprocess, sys
from pathlib import Path
ROOT = Path("""$ROOT""")
proc = subprocess.run(
    [sys.executable, "scripts/pre_write_guard_v1.py", "check", "--agent", "cursor", "--path", "agent-control-panel/form/index.html", "--json"],
    cwd=str(ROOT),
    capture_output=True,
    text=True,
)
row = json.loads(proc.stdout or "{}")
if row.get("ok") is True:
    sys.exit(1)
print("OK: pre_write blocks hub_form without ack")
PY

python3 scripts/ui_upgrade_first_check_v1.py --surface hub_form --ack --json >/dev/null || fail "hub_form ack"
python3 - <<PY || fail "pre_write should allow after ack"
import json, subprocess, sys
from pathlib import Path
ROOT = Path("""$ROOT""")
proc = subprocess.run(
    [sys.executable, "scripts/pre_write_guard_v1.py", "check", "--agent", "cursor", "--path", "agent-control-panel/form/index.html", "--json"],
    cwd=str(ROOT),
    capture_output=True,
    text=True,
)
row = json.loads(proc.stdout or "{}")
if row.get("ok") is not True:
    sys.exit(1)
print("OK: pre_write allows hub_form after ack")
PY

if [[ -n "$ACK_BACKUP" && -f "$ACK_BACKUP" ]]; then
  cp "$ACK_BACKUP" "$ACKS"
  rm -f "$ACK_BACKUP"
fi

echo "PASS: validate-ui-upgrade-first-check-live-wire-v1"
