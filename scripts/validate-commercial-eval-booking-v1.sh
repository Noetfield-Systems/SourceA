#!/usr/bin/env bash
# validate-commercial-eval-booking-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-commercial-eval-booking-v1 — $*" >&2; exit 1; }

[[ -f scripts/commercial_eval_booking_agent_v1.py ]] || fail "missing eval booking agent"
[[ -f scripts/mark_eval_booking_sent_v1.py ]] || fail "missing mark_eval_booking_sent"

python3 scripts/commercial_eval_booking_agent_v1.py --row-id cp-a0c7c6c607 --json >/dev/null \
  || fail "eval booking agent run"

[[ -f "${SINA}/eval-booking-receipt-v1.json" ]] || fail "missing eval-booking-receipt"
PACK="$(python3 -c "import json; print(json.load(open('${SINA}/eval-booking-receipt-v1.json'))['pack_dir'])")"
[[ -f "${PACK}/pack.json" ]] || fail "missing pack.json"
[[ -f "${PACK}/body.txt" ]] || fail "missing body.txt"

python3 - <<'PY' || fail "pack contract"
import json
from pathlib import Path
pack = json.loads(Path.home().joinpath(".sina/eval-booking-receipt-v1.json").read_text())
assert pack.get("schema") == "eval-booking-receipt-v1"
assert pack.get("row_id")
assert pack.get("proof_url", "").startswith("http")
body = Path(pack["pack_dir"]).joinpath("body.txt").read_text()
assert "15-minute" in body or "15-min" in body
assert "proof" in body.lower()
assert "127.0.0.1" not in body and "localhost" not in body
w1 = pack.get("w1_film_url") or ""
assert w1.startswith("https://"), f"w1 must be public https, got {w1!r}"
print("OK: eval booking pack contract")
PY

echo "PASS: validate-commercial-eval-booking-v1"
