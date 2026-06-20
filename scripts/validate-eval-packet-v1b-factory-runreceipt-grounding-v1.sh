#!/usr/bin/env bash
# sa-0138 — factory-runreceipt grounding includes RUNRECEIPT schema doc
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_packet_v1b.grounding import (
    FACTORY_RUNRECEIPT_PATHS,
    FACTORY_RUNRECEIPT_SCHEMA_DOC,
    build_task_grounding,
    cross_check_factory_runreceipt_grounding,
)

errs = cross_check_factory_runreceipt_grounding()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)

g = build_task_grounding(
    task_id="factory-runreceipt",
    prompt="Define RunReceipt artifacts run.jsonl summary.json HTML pack for wire lane",
    keywords=["run.jsonl", "summary", "receipt", "wire", "PASS"],
)
paths = list(g.get("expected_paths") or [])
assert paths == list(FACTORY_RUNRECEIPT_PATHS), paths
assert FACTORY_RUNRECEIPT_SCHEMA_DOC in paths, paths

print(
    "OK: validate-eval-packet-v1b-factory-runreceipt-grounding-v1 · "
    "RUNRECEIPT schema doc + pack_v1 (sa-0138)"
)
PY
