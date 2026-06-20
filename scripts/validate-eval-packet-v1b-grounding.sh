#!/usr/bin/env bash
# Eval-1b grounding — bugfix-gate paths (no OpenRouter)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

python3 - <<'PY'
from eval_packet_v1b.grounding import build_task_grounding

prompt = "Fix model_dispatch when gate_eligible is false in enforce mode"
keywords = ["gate_eligible", "enforce", "model_dispatch", "block"]
g = build_task_grounding(task_id="bugfix-gate", prompt=prompt, keywords=keywords)
paths = list(g.get("expected_paths") or [])
assert "scripts/model_dispatch.py" in paths, paths
assert "scripts/gate_receipts_hub.py" in paths, paths
snips = {s["path"]: s["snippet"] for s in (g.get("snippets") or [])}
assert "scripts/model_dispatch.py" in snips, snips.keys()
assert "scripts/gate_receipts_hub.py" in snips, snips.keys()
md = (snips["scripts/model_dispatch.py"] + snips["scripts/gate_receipts_hub.py"]).lower()
assert "gate_eligible" in md, "model_dispatch/gate_receipts snippet must mention gate_eligible"
assert "enforce" in md, "snippet must mention enforce"
print("OK: validate-eval-packet-v1b-grounding · bugfix-gate paths + snippets")

from eval_packet_v1b.scorer import expected_path_hits

plan_paths = [
    "scripts/eval_packet_v1b/runner.py",
    "scripts/eval_packet_v1/runner.py",
    "scripts/eval_packet_v1b/scorer.py",
]
weak = "Use runner.py for the eval harness."
assert expected_path_hits(weak, plan_paths) == 0, "basename-only must not count for plan-eval-1b"
one = "See scripts/eval_packet_v1b/runner.py for live_pilot A/B."
assert expected_path_hits(one, plan_paths) == 1, one
two = (
    "Compare `scripts/eval_packet_v1b/runner.py` vs "
    "`scripts/eval_packet_v1/runner.py`; scoring in eval_packet_v1b/scorer.py."
)
assert expected_path_hits(two, plan_paths) == 3, two
g_plan = build_task_grounding(
    task_id="plan-eval-1b",
    prompt="Plan Eval-1b behavioral harness comparing packet context vs raw LLM on fixed tasks",
    keywords=["eval", "packet", "raw", "", "A/B"],
)
plan_grounded = list(g_plan.get("expected_paths") or [])
assert "scripts/eval_packet_v1b/scorer.py" in plan_grounded, plan_grounded
print("OK: validate-eval-packet-v1b-grounding · plan-eval-1b path citation hardened")

rd_prompt = "Where is dispatch_ready set false in the runtime orchestrator?"
rd_keywords = ["dispatch_ready", "orchestrator", "false", "runtime"]
g_rd = build_task_grounding(task_id="retrieve-dispatch", prompt=rd_prompt, keywords=rd_keywords)
rd_paths = list(g_rd.get("expected_paths") or [])
assert "scripts/runtime/orchestrator/orchestrator_engine.py" in rd_paths, rd_paths
assert "scripts/runtime/multi_step_planner/planner_engine.py" in rd_paths, rd_paths
rd_snips = {s["path"]: s["snippet"] for s in (g_rd.get("snippets") or [])}
assert "scripts/runtime/orchestrator/orchestrator_engine.py" in rd_snips, rd_snips.keys()
assert "scripts/runtime/multi_step_planner/planner_engine.py" in rd_snips, rd_snips.keys()
orch_md = rd_snips["scripts/runtime/orchestrator/orchestrator_engine.py"].lower()
plan_md = rd_snips["scripts/runtime/multi_step_planner/planner_engine.py"].lower()
assert "dispatch_ready" in orch_md, "orchestrator snippet must mention dispatch_ready"
assert "dispatch_ready" in plan_md, "planner_engine snippet must mention dispatch_ready"
print("OK: validate-eval-packet-v1b-grounding · retrieve-dispatch orchestrator + planner_engine")

fr_prompt = "Define RunReceipt artifacts run.jsonl summary.json HTML pack for wire lane"
fr_keywords = ["run.jsonl", "summary", "receipt", "wire", "PASS"]
g_fr = build_task_grounding(task_id="factory-runreceipt", prompt=fr_prompt, keywords=fr_keywords)
fr_paths = list(g_fr.get("expected_paths") or [])
schema_doc = "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md"
assert schema_doc in fr_paths, fr_paths
assert "scripts/runreceipt/pack_v1.py" in fr_paths, fr_paths
fr_snips = {s["path"]: s["snippet"] for s in (g_fr.get("snippets") or [])}
assert schema_doc in fr_snips, fr_snips.keys()
assert "scripts/runreceipt/pack_v1.py" in fr_snips, fr_snips.keys()
schema_md = fr_snips[schema_doc].lower()
pack_md = fr_snips["scripts/runreceipt/pack_v1.py"].lower()
assert "run.jsonl" in schema_md, "RUNRECEIPT schema doc must mention run.jsonl"
assert "summary.json" in schema_md, "RUNRECEIPT schema doc must mention summary.json"
assert "run.jsonl" in pack_md, "pack_v1 snippet must mention run.jsonl"
print("OK: validate-eval-packet-v1b-grounding · factory-runreceipt RUNRECEIPT schema doc")

l8_prompt = "How does L8 hybrid embedding retrieval extend D5 token index?"
l8_keywords = ["embedding", "vector", "hybrid", "retrieval"]
g_l8 = build_task_grounding(task_id="l8-hybrid", prompt=l8_prompt, keywords=l8_keywords)
l8_paths = list(g_l8.get("expected_paths") or [])
embed_py = "scripts/pre_llm/vector_retrieval/embedding_provider.py"
assert embed_py in l8_paths, l8_paths
l8_snips = {s["path"]: s["snippet"] for s in (g_l8.get("snippets") or [])}
assert embed_py in l8_snips, l8_snips.keys()
embed_md = l8_snips[embed_py].lower()
assert "embedding" in embed_md, "embedding_provider snippet must mention embedding"
assert "hybrid" in embed_md or "embed_text" in embed_md, embed_md[:200]
print("OK: validate-eval-packet-v1b-grounding · l8-hybrid embedding_provider.py")
PY
