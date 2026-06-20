#!/usr/bin/env bash
# validate-crawl-mirror-v1.sh — crawl–mirror session tier scaffold (Wave 0)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f scripts/sourcea_crawl_mirror_pipeline_v1.py || {
  echo "FAIL: missing sourcea_crawl_mirror_pipeline_v1.py"
  exit 1
}

python3 scripts/sourcea_crawl_mirror_pipeline_v1.py --tier session --role any --json >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

p = Path.home() / ".sina/crawl-mirror-receipt-v1.json"
assert p.is_file(), "missing crawl-mirror-receipt-v1.json"
row = json.loads(p.read_text(encoding="utf-8"))
assert row.get("schema") == "crawl-mirror-receipt-v1", row.get("schema")
assert row.get("stages"), "missing stages"
assert "C4" in (row.get("stages") or {}).get("crawl", {}) or row.get("steps")
print(f"OK: validate-crawl-mirror-v1 · ok={row.get('ok')} · queue={row.get('queue_sa')} · elapsed={row.get('elapsed_sec')}s")
PY
