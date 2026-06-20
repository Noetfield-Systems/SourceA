#!/usr/bin/env bash
# validate_rrl_per_account_history_v1.sh — U031 acceptance gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate_rrl_per_account_history_v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "history module"
import sys
sys.path.insert(0, "scripts")
from response_reality_layer_v1 import append_history, history_for_account, MAX_HISTORY_PER_ACCOUNT
assert MAX_HISTORY_PER_ACCOUNT == 10
PY

test -f scripts/response_reality_layer_v1.py || fail "missing response_reality_layer_v1.py"

HIST="$HOME/.sina/response-reality-layer-history-v1.jsonl"
if [[ -f "$HIST" ]]; then
  python3 - <<'PY' || fail "history trim check"
import json
from pathlib import Path
from collections import Counter
p = Path.home() / ".sina" / "response-reality-layer-history-v1.jsonl"
counts = Counter()
for line in p.read_text().splitlines():
    if not line.strip():
        continue
    r = json.loads(line)
    counts[str(r.get("account_id") or "unknown")] += 1
bad = {k: v for k, v in counts.items() if v > 10}
if bad:
    raise SystemExit(f"account exceeds 10 sims: {bad}")
print("OK: history per-account cap 10")
PY
fi

echo "OK: validate_rrl_per_account_history_v1 · append-only history wired"
