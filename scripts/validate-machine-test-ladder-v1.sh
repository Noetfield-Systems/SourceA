#!/usr/bin/env bash
# validate-machine-test-ladder-v1.sh — ladder script compiles + daily smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="${ROOT}/SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md"

fail() { echo "FAIL: validate-machine-test-ladder-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing law"
[[ -f "${ROOT}/scripts/machine_test_ladder_run_v1.py" ]] || fail "missing ladder runner"
python3 -m py_compile "${ROOT}/scripts/machine_test_ladder_run_v1.py" || fail "py_compile"

echo "== daily ladder smoke =="
python3 "${ROOT}/scripts/machine_test_ladder_run_v1.py" --tier daily --role worker --json > /tmp/ladder-smoke.json \
  || true

REC="${HOME}/.sina/machine-test-ladder-receipt-v1.json"
[[ -f "$REC" ]] || fail "receipt missing"
python3 - <<'PY' "$REC" /tmp/ladder-smoke.json
import json, sys
rec_path, smoke_path = sys.argv[1], sys.argv[2]
r = json.loads(open(rec_path).read())
if r.get("schema") != "machine-test-ladder-receipt-v1":
    raise SystemExit("receipt schema")
if r.get("tier") != "daily":
    raise SystemExit("expected daily tier in smoke")
core = {"D1_super_fast_hub", "D2_two_hub", "D6_three_pipelines_smoke"}
steps = {s["id"]: s.get("ok") for s in (r.get("steps") or [])}
if not all(steps.get(c) for c in core):
    bad = [c for c in core if not steps.get(c)]
    raise SystemExit(f"core daily steps failed: {bad}")
print(f"OK: ladder receipt tier={r.get('tier')} passed={r.get('steps_passed')}/{r.get('steps_total')} core=PASS")
PY

echo "OK: validate-machine-test-ladder-v1"
