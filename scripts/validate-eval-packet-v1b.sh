#!/usr/bin/env bash
# Eval-1b — behavioral packet vs raw (scaffold; live when vault key present)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request

from eval_packet_v1b.runner import run_eval

rep = run_eval(write_report=True, live=False)
assert rep.get("schema") == "eval-packet-v1b", rep
assert rep.get("mode") == "scaffold", rep
assert rep.get("task_count", 0) >= 3, rep
assert rep.get("scaffold_ok"), f"scaffold arm failed: {rep.get('scaffold_win_pct')}%"
assert int(rep.get("scaffold_win_pct") or 0) >= 70, rep
rows = rep.get("rows") or []
assert len(rows) >= 3, rows
for row in rows:
    sc = row.get("scaffold") or {}
    assert "raw" in sc and "packet" in sc, row.get("id")
    assert sc.get("packet_wins") is not None, row.get("id")
print(
    f"OK: eval-1b scaffold arm · {rep.get('scaffold_wins')}/{rep.get('task_count')} "
    f"({rep.get('scaffold_win_pct')}%) — survives after live pass"
)

with urllib.request.urlopen("http://127.0.0.1:13020/api/eval-packet-v1b", timeout=90) as resp:
    api = json.loads(resp.read().decode())
assert api.get("schema") == "eval-packet-v1b", api
assert api.get("ok") is not None, api
print("OK: validate-eval-packet-v1b")
PY
