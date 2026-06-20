#!/usr/bin/env bash
# Mechanical pack law — Worker 1 unified REGISTRY + paste queue (v1.3).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REG="$ROOT/brain-os/plan-registry/worker-dual-40/REGISTRY.json"
W1_Q="$ROOT/.sina-loop/WORKER-1-PASTE-QUEUE.md"

test -f "$REG"
test -f "$W1_Q"
test -f "$ROOT/scripts/generate-worker-dual-40.py"
test ! -f "$ROOT/.sina-loop/OLD-WORKER-PASTE-QUEUE.md"
test ! -f "$ROOT/.sina-loop/NEW-WORKER-PASTE-QUEUE.md"
test ! -f "$ROOT/scripts/finish-worker-2-autoloop-block-v1.sh"
test ! -f "$ROOT/scripts/validate_worker2_closeout_proofs_v1.py"

python3 <<PY
import json, sys
from pathlib import Path

root = Path("$ROOT")
reg = json.loads((root / "brain-os/plan-registry/worker-dual-40/REGISTRY.json").read_text())
schema = reg.get("schema") or ""
assert schema.startswith("worker-1-unified"), schema
assert reg.get("worker_1_only") is True, reg
assert "worker_2" not in reg, "worker_2 field must be purged"
assert reg.get("count") == 40, reg.get("count")
plans = reg["plans"]
assert len(plans) == 40, len(plans)
sa = [p for p in plans if p.get("kind") == "sa"]
loop = [p for p in plans if p.get("kind") == "autoloop"]
assert len(sa) == 20 and len(loop) == 20, (len(sa), len(loop))
assert all(p.get("worker") == 1 for p in plans)

forbidden = ("CHECK ONLY", "ACT ONLY", "wait STOP before next", "NEW WORKER", "OLD WORKER")
for p in plans:
    pos = p["position"]
    gates = []
    if pos % 3 == 0:
        gates.append("E2E-3")
    if pos % 5 == 0:
        gates.append("DEBUG-5")
    assert p.get("gates") == gates, (p["id"], p.get("gates"), gates)
    text = p["prompt"]
    assert not any(x in text for x in forbidden), p["id"]
    if "E2E-3" in gates:
        assert "PLUS E2E-3 GATE" in text, p["id"]
    if "DEBUG-5" in gates:
        assert "PLUS DEBUG-5 GATE" in text, p["id"]
    if p.get("kind") == "sa":
        sa_id = p["sa_id"]
        path = root / f"brain-os/plan-registry/sourcea-1000/prompts/phase-s1-eval-dispatch/T1/{sa_id}.md"
        assert path.is_file(), path

w1 = (root / ".sina-loop/WORKER-1-PASTE-QUEUE.md").read_text()
assert "Worker 1 unified" in w1 or "Worker 1 — unified" in w1
assert "Worker 2" not in w1, "Worker 2 references must be purged from paste queue"
assert "w1-40" in w1
assert "one paste = one full turn" in w1

print("OK: validate-worker-dual-40-pack-v1")
PY
