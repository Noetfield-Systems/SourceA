#!/usr/bin/env bash
# Validate plan registry consumer wiring without heavy E2E.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== sourcea plan registry consumers ==="

SOURCEA_ROOT="$ROOT" python3 - <<'PY'
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

root = Path(os.environ["SOURCEA_ROOT"])
sys.path.insert(0, str(root / "scripts"))

from sourcea_plan_registry_client_v1 import contains_secret_like, get_plan, query_rows  # noqa: E402
from chat_unify_engine_v1 import MACHINES, handle_post  # noqa: E402

doc = root / "docs/SOURCEA_PLAN_REGISTRY_CONSUMER_ROLLOUT_LOCKED_v1.md"
assert doc.is_file(), doc
assert "Do not prune TrustField rows" in doc.read_text(encoding="utf-8")
split_script = (root / "scripts/noetfield_trustfield_plan_registry_import_v1.py").read_text(encoding="utf-8")
assert "import_not_confirmed" in split_script
assert "--prune-spine" in split_script

rows = query_rows(limit=1)
assert rows["ok"], rows
assert int(rows.get("total") or 0) >= 23485, rows
sample_id = rows["rows"][0]["plan_id"]
detail = get_plan(sample_id)
assert detail["ok"] and detail["found"], detail

machine_ids = {str(m.get("id")) for m in MACHINES}
assert "plan_registry" in machine_ids, machine_ids

cu_list = handle_post({"action": "plan_registry", "limit": 2})
assert cu_list["ok"], cu_list
assert cu_list["count"] <= 2, cu_list
assert cu_list["max_limit"] == 10, cu_list
cu_detail = handle_post({"action": "plan_registry", "plan_id": sample_id})
assert cu_detail["ok"] and cu_detail["found"], cu_detail

for payload in (rows, detail, cu_list, cu_detail):
    assert not contains_secret_like(payload), payload

server = subprocess.Popen(
    [sys.executable, str(root / "scripts/sina-command-server.py")],
    cwd=str(root),
    env={**os.environ, "SINA_COMMAND_PORT": "13120"},
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    time.sleep(1.5)
    with urllib.request.urlopen("http://127.0.0.1:13120/api/sourcea/plan-registry/v1?limit=1", timeout=10) as resp:
        hub = json.loads(resp.read().decode("utf-8"))
    assert hub["ok"], hub
    assert hub["count"] == 1, hub
    assert not contains_secret_like(hub), hub
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()

html = (root / "agent-control-panel/worker-hub/index.html").read_text(encoding="utf-8")
assert "plan-registry-card" in html
assert "btn-plan-registry-lookup" in html

catalog = json.loads((root / "data/chat-unify-platform-catalog-v1.json").read_text(encoding="utf-8"))
assert any(m.get("id") == "plan_registry" for m in catalog.get("machines") or [])

print("OK sample_plan", sample_id)
print("OK hub_route", "/api/sourcea/plan-registry/v1")
print("OK chat_unify_machine", "plan_registry")
PY

echo "validate-sourcea-plan-registry-consumers-v1.sh: ALL PASS"
