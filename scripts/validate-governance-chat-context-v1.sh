#!/usr/bin/env bash
# validate-governance-chat-context-v1.sh — M17 chat role map SSOT
set -euo pipefail
CTX="${HOME}/.sina/governance-chat-context-v1.json"
fail() { echo "FAIL: validate-governance-chat-context-v1 — $*" >&2; exit 1; }

[[ -f "$CTX" ]] || fail "missing $CTX"

python3 - <<'PY' || fail "role map invalid"
import json
from pathlib import Path

ctx = json.loads(Path.home().joinpath(".sina/governance-chat-context-v1.json").read_text())
role_map = ctx.get("role_map") or {}
expected = {
    "brain": "58148ac9",
    "commercial": "6245d9dd",
    "governance": "e54ddfa8",
    "worker": "fd67502f",
    "maintainer_m2": "74f5ccab",
}
for role, eid in expected.items():
    got = role_map.get(role) or role_map.get("worker_primary" if role == "worker" else "", "")
    assert got == eid, f"role_map.{role}={got!r} want {eid!r}"

threads = {t["id"]: t for t in (ctx.get("threads") or []) if t.get("id")}
for role, eid in expected.items():
    t = threads.get(eid)
    assert t, f"missing thread {eid}"
    want_role = "maintainer" if role == "maintainer_m2" else role
    assert t.get("role") == want_role, f"thread {eid} role={t.get('role')!r} want {want_role!r}"

# forbid swapped brain/commercial labels from M13 regression
brain = threads.get("58148ac9", {})
comm = threads.get("6245d9dd", {})
assert brain.get("role") == "brain", brain
assert comm.get("role") == "commercial", comm
assert "Commercial" not in (brain.get("label") or ""), brain.get("label")
assert "Brain" not in (comm.get("label") or "") or "Commercial" in (comm.get("label") or ""), comm.get("label")

print("OK: validate-governance-chat-context-v1 · role_map + threads aligned")
PY
