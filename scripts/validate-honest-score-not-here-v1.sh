#!/usr/bin/env bash
# sa-0001 — honest_score.not_here must not list stale gaps after live Eval-1b / L8 ship
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
from pathlib import Path

from system_roadmap import _build_world_target_map

m = _build_world_target_map()
hs = m.get("honest_score") or {}
here = hs.get("here") or []
not_here = hs.get("not_here") or []
built = (m.get("reality_alignment") or {}).get("built") or []

assert any("Execution Spine" in str(x) for x in here), here
assert "Execution Spine" in built, built

report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
if report_path.is_file():
    rep1b = json.loads(report_path.read_text(encoding="utf-8"))
    if rep1b.get("mode") == "live" and rep1b.get("live_ok", rep1b.get("ok")):
        for stale in (
            "Eval-1b behavioral proof",
            "Eval-1b live LLM A/B",
            "Eval-1b below threshold",
        ):
            assert not any(stale in str(line) for line in not_here), (
                f"stale not_here after live pass: {stale!r} in {not_here!r}"
            )

root = Path(__file__).resolve().parents[1]
embed_path = root / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
if embed_path.is_file():
    assert not any("full L8 embeddings later" in str(line) for line in not_here), not_here

# sa-0011 — ENFORCE-only not_here rows must drop when gate_mode is enforce
import importlib
import os

import model_dispatch
import system_roadmap

_prev = os.environ.get("SINA_GATE_MODE")
os.environ["SINA_GATE_MODE"] = "enforce"
importlib.reload(model_dispatch)
importlib.reload(system_roadmap)
assert system_roadmap._gate_is_enforce(), "SINA_GATE_MODE=enforce must resolve enforce"
m_enf = system_roadmap._build_world_target_map()
nh_enf = (m_enf.get("honest_score") or {}).get("not_here") or []
tgt_enf = (m_enf.get("reality_alignment") or {}).get("target") or []
_enforce_only = (
    "ENFORCE gate in production (shadow today)",
    "ENFORCE gate flip",
)
for stale in _enforce_only:
    assert not any(stale in str(line) for line in nh_enf), (
        f"ENFORCE-only not_here stale under enforce gate: {stale!r} in {nh_enf!r}"
    )
    assert not any(stale in str(line) for line in tgt_enf), (
        f"ENFORCE-only target stale under enforce gate: {stale!r} in {tgt_enf!r}"
    )
if _prev is None:
    os.environ.pop("SINA_GATE_MODE", None)
else:
    os.environ["SINA_GATE_MODE"] = _prev
importlib.reload(model_dispatch)
importlib.reload(system_roadmap)

print(
    f"OK: validate-honest-score-not-here-v1 · not_here={len(not_here)} rows · no stale drift · enforce gate ok"
)
PY
