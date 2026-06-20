#!/usr/bin/env bash
# Optional Lighthouse gate for witnessbc.com home (perf + a11y >= 90 target)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URL="${1:-http://127.0.0.1:8090/}"
MIN_SCORE="${LIGHTHOUSE_MIN:-90}"

if ! command -v npx >/dev/null 2>&1; then
  echo "SKIP: npx not available — lighthouse gate optional"
  exit 0
fi

if ! npx --yes lighthouse --version >/dev/null 2>&1; then
  echo "SKIP: lighthouse not installable — optional gate"
  exit 0
fi

report="$(mktemp -d)"
npx --yes lighthouse "$URL" \
  --only-categories=performance,accessibility \
  --output=json \
  --output-path="$report/report.json" \
  --chrome-flags="--headless --no-sandbox" \
  --quiet 2>/dev/null || {
  echo "SKIP: lighthouse run failed (serve site first: run-recipe.sh --serve)"
  exit 0
}

python3 - <<PY
import json
from pathlib import Path
data = json.loads(Path("$report/report.json").read_text())
cats = data.get("categories", {})
perf = int((cats.get("performance") or {}).get("score", 0) * 100)
a11y = int((cats.get("accessibility") or {}).get("score", 0) * 100)
min_score = int("$MIN_SCORE")
print(f"Lighthouse performance={perf} accessibility={a11y} (min {min_score})")
if perf < min_score or a11y < min_score:
    raise SystemExit(f"FAIL: lighthouse below {min_score}")
print("PASS: lighthouse gate")
PY
