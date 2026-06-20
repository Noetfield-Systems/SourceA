#!/usr/bin/env bash
# validate-anti-staleness-vocabulary-gate-v1.sh — disk live + vocabulary (KEY pair)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Anti-staleness (disk live wire) ==="
bash scripts/validate-disk-live-wire-v1.sh || fail=1

echo "=== Vocabulary (positive inject + forbidden phrases) ==="
python3 scripts/vocabulary_guard_v1.py --strict-disk --json >/dev/null || fail=1

echo "=== Law supersession surfaces ==="
bash scripts/validate-law-supersession-surfaces-v1.sh || fail=1

echo "=== Anti-staleness auto-wire receipt fresh ==="
python3 - <<'PY' || fail=1
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home() / ".sina/anti-staleness-auto-wire-v1.json"
if not p.is_file():
    raise SystemExit("missing anti-staleness-auto-wire receipt — run session gate")
r = json.loads(p.read_text())
if not r.get("ok"):
    raise SystemExit(f"anti-staleness receipt ok=false tier={r.get('tier')}")
at = r.get("at") or ""
dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
age = (datetime.now(timezone.utc) - dt).total_seconds()
if age > 3600:
    raise SystemExit(f"anti-staleness receipt stale age_sec={age:.0f}")
print(f"OK: anti-staleness receipt fresh age_sec={age:.0f} queue={r.get('queue_sa')}")
PY

echo "=== SASCIP stranger safety (W10 bundle) ==="
bash scripts/validate-stranger-agent-safety-v1.sh || fail=1

echo "=== SASCIP live wire (ADMIT→PROBE→PANIC→WATCH→SERVE) ==="
bash scripts/validate-stranger-agent-safety-live-wire-v1.sh || fail=1

echo "=== Voyage AI L8 live wire ==="
bash scripts/validate-voyage-ai-live-wire-v1.sh || fail=1

echo "=== Orient routing (Wave 1 cascade) ==="
bash scripts/validate-orient-routing-v1.sh || fail=1

echo "=== Crawl-mirror session tier (W10 bundle) ==="
bash scripts/validate-crawl-mirror-v1.sh || fail=1

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-anti-staleness-vocabulary-gate-v1"
  exit 0
fi
echo "FAIL: validate-anti-staleness-vocabulary-gate-v1"
exit 1
