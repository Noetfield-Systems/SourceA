#!/usr/bin/env bash
# validate-nerve-system-cart-v1.sh — BQ1–BQ5 + NS1–NS2 cart rows
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-nerve-system-cart-v1 — $*" >&2; exit 1; }

python3 scripts/better_loop_pulse_v1.py --init-cart >/dev/null || fail "init cart"
test -f "${SINA}/better-loop-checkcart-v1.json" || fail "missing checkcart"

python3 - <<'PY' || fail "BQ/NS rows missing"
import json
from pathlib import Path

cart = json.loads((Path.home() / ".sina/better-loop-checkcart-v1.json").read_text())
ids = {r.get("id") for r in cart.get("mandatory_after_every_pulse") or []}
need = {"BQ1", "BQ2", "BQ3", "BQ4", "BQ5", "NS1", "NS2"}
missing = need - ids
if missing:
    raise SystemExit(f"missing cart rows: {sorted(missing)}")
print(f"OK: cart has {len(need)} BQ/NS rows")
PY

python3 scripts/best_loop_oqg_score_v1.py --json >/dev/null || fail "BQ1 oqg score"
python3 scripts/agent_nerve_system_v1.py --json >/dev/null || fail "NS1 nerve pulse"
bash scripts/validate-agent-nerve-system-v1.sh || fail "NS2 nerve validator"

python3 - <<'PY' || fail "BQ3 hub slices"
import json, subprocess
out = subprocess.check_output(["python3", "scripts/worker_hub_v1.py", "--extended", "--json"], text=True)
hub = json.loads(out[out.find("{"):])
for k in ("nerve_system", "best_loop_oqg", "better_loop"):
    if k not in hub:
        raise SystemExit(f"missing hub slice {k}")
print("OK: hub nerve + oqg slices")
PY

echo "PASS: validate-nerve-system-cart-v1"
