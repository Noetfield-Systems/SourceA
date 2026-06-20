#!/usr/bin/env bash
# sa-0035 / sa-0085 — STRATEGIC_NEXT_STEPS doc vs /api/strategic-synthesis-v1
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
import urllib.request

from strategic_synthesis_hub import DOC, strategic_synthesis_payload

local = strategic_synthesis_payload()
assert local.get("ok"), f"missing {DOC}"
assert local.get("schema") == "strategic-synthesis-v1", local.get("schema")

req = urllib.request.Request("http://127.0.0.1:13020/api/strategic-synthesis-v1")
with urllib.request.urlopen(req, timeout=30) as resp:
    assert resp.status == 200, resp.status
    api = json.loads(resp.read().decode("utf-8"))

assert api.get("ok") is True, api
assert api.get("doc_path") == DOC, (api.get("doc_path"), DOC)

keys = (
    "schema",
    "doc_path",
    "one_line",
    "bottleneck",
    "do_now_primary",
    "machine_gates",
    "strategic_goals",
    "next_plans",
    "pendings",
    "this_week",
)
for key in keys:
    assert api.get(key) == local.get(key), f"API/local drift on {key!r}"

assert len(api.get("strategic_goals") or []) >= 3, api
assert len(api.get("next_plans") or []) >= 5, api
assert len(api.get("pendings") or []) >= 8, api
assert (api.get("body_chars") or 0) > 0, "body_markdown empty"

print(
    f"OK: validate-strategic-synthesis-api-alignment-v1 · "
    f"{DOC} · goals={len(api['strategic_goals'])} · API aligned"
)
PY
