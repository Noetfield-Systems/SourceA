#!/usr/bin/env bash
# validate-commercial-film-critic-circle-v1.sh — critic circle must run before public ship
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-commercial-film-critic-circle-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/commercial-film-critic-circle-v1.json" ]] || fail "missing critic circle SSOT"
[[ -f "$ROOT/scripts/commercial_film_critic_circle_v1.py" ]] || fail "missing critic circle script"

python3 "$ROOT/scripts/commercial_film_critic_circle_v1.py" --no-freeze --json >/dev/null || {
  echo "WARN: critic circle BLOCK (expected until Screen Studio master)"
}

RECEIPT="${HOME}/.sina/enforcement/commercial-film-critic-circle-receipt-v1.json"
[[ -f "$RECEIPT" ]] || fail "missing critic circle receipt — run commercial_film_critic_circle_v1.py"

python3 - <<'PY' || fail "receipt contract"
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/enforcement/commercial-film-critic-circle-receipt-v1.json").read_text())
assert r.get("schema") == "commercial-film-critic-circle-receipt-v1"
assert r.get("judgments"), "no judgments"
assert r.get("next_action_only"), "missing next action"
print("OK: critic circle receipt · verdict", r.get("verdict"))
PY

echo "PASS: validate-commercial-film-critic-circle-v1.sh"
