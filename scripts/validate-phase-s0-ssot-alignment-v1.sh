#!/usr/bin/env bash
# phase-s0-ssot-alignment pack — sa-0002..sa-0010 machine proof
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

bash validate-honest-score-not-here-v1.sh
bash validate-strategic-synthesis-v1.sh
python3 audit_essentials_nav.py

python3 - <<'PY'
# sa-0012 — _phase_d_complete() must match full D1–D16 artifact set
from system_roadmap import _phase_d_complete, _pre_llm_shipped_count

ship = _pre_llm_shipped_count()
pdc = _phase_d_complete()
assert pdc == (ship == 16), f"_phase_d_complete={pdc} vs shipped={ship}/16"
if pdc:
    assert ship == 16, f"phase_d_complete true but only {ship}/16 artifacts"
print(f"OK: phase_d_complete aligned · shipped={ship}/16 · pdc={pdc}")
PY

python3 - <<'PY'
# sa-0014 — app.js must have zero WORLD_TARGET_MODEL_MAP_LOCKED_v2 references
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hub_worker_mode_v1 import worker_hub_mode

if worker_hub_mode():
    print("OK: sa-0014 skipped — Worker Hub (H1) retired monolith app.js")
else:
    app = Path(__file__).resolve().parents[1] / "agent-control-panel" / "assets" / "app.js"
    text = app.read_text(encoding="utf-8")
    hits = re.findall(r"WORLD_TARGET_MODEL_MAP_LOCKED_v2", text)
    assert not hits, f"stale v2 map in app.js: {hits!r}"
    print("OK: app.js zero WORLD_TARGET_MODEL_MAP_LOCKED_v2 hits (sa-0014)")
PY

python3 - <<'PY'
# sa-0015 — strict build must refresh PROGRAM_PROGRESS signals_auto.synced_at
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
build_py = Path(__file__).resolve().parent / "build-sina-command-panel.py"
text = build_py.read_text(encoding="utf-8")
assert "_run_update_program_progress" in text, "build missing _run_update_program_progress (sa-0015)"
assert "update-program-progress.py" in text, "build must invoke update-program-progress.py (sa-0015)"
assert "SINA_SKIP_NESTED_BOWL" in text, "build must set SINA_SKIP_NESTED_BOWL on progress sync (sa-0015)"

prog = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
synced = (prog.get("signals_auto") or {}).get("synced_at")
assert synced, "PROGRAM_PROGRESS signals_auto.synced_at missing (sa-0015)"
assert prog.get("updated_by") == "update-program-progress.py", prog.get("updated_by")
print(f"OK: PROGRAM_PROGRESS signals_auto.synced_at present · {synced} (sa-0015)")
PY

python3 - <<'PY'
# sa-0016 — index.html lazy bootstrap + shell payload under 500KB
import json
import sys
from pathlib import Path

from sina_command_lib import HEAVY_PAYLOAD_KEYS, SHELL_MAX_BYTES

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hub_worker_mode_v1 import worker_hub_mode

root = Path(__file__).resolve().parents[1]
shell = root / "agent-control-panel" / "command-data-shell.json"
assert shell.is_file(), "command-data-shell.json missing (sa-0016)"
size = shell.stat().st_size
assert size <= SHELL_MAX_BYTES, f"shell {size} bytes > {SHELL_MAX_BYTES} (sa-0016)"
if "fleet" in json.loads(shell.read_text(encoding="utf-8")):
    raise AssertionError("fleet leaked into command-data-shell.json (sa-0016)")

if worker_hub_mode():
    boot = root / "agent-control-panel" / "worker-hub" / "boot.json"
    assert boot.is_file(), "worker-hub/boot.json missing in H1 mode (sa-0016)"
    print(f"OK: H1 worker-hub shell {size} bytes ≤ {SHELL_MAX_BYTES} · boot.json present (sa-0016)")
else:
    index = root / "agent-control-panel" / "index.html"
    ih = index.read_text(encoding="utf-8")
    assert "__COMMAND_DATA_LAZY" in ih, "index.html missing __COMMAND_DATA_LAZY (sa-0016)"
    assert "window.COMMAND_DATA = {" not in ih, "index.html embeds full COMMAND_DATA (sa-0016)"
    assert "fleet" in HEAVY_PAYLOAD_KEYS, "fleet must be deferred from shell (sa-0016)"
    print(f"OK: __COMMAND_DATA_LAZY + shell {size} bytes ≤ {SHELL_MAX_BYTES} (sa-0016)")
PY

python3 feedback_hub_sync_assert_v1.py --label sa-0017
echo "OK: FEEDBACK_AGGREGATE hub_built_at aligned (sa-0017)"

python3 - <<'PY'
# sa-0018 — reject unconditional L8 not_here when hybrid shipped
from pathlib import Path

import system_roadmap as sr

scripts = Path(__file__).resolve().parent
root = scripts.parent
assert (scripts / "validate-honest-score-l8-skip-v1.sh").is_file(), "missing l8-skip validator (sa-0018)"
assert (scripts / "validate-honest-score-not-here-drift-v1.sh").is_file(), "missing not-here-drift validator (sa-0018)"
assert hasattr(sr, "_l8_hybrid_live"), "system_roadmap missing _l8_hybrid_live (sa-0018)"

embed = root / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
index = Path.home() / ".sina" / "vector_index_v1.json"
if embed.is_file() and index.is_file():
    stale = (
        "full L8 embeddings later",
        "Embedding index (D5 is token retrieval today)",
        "L8 hybrid scaffold",
    )
    nh = (sr._build_world_target_map().get("honest_score") or {}).get("not_here") or []
    for s in stale:
        assert not any(s in str(line) for line in nh), f"stale L8 not_here {s!r} (sa-0018)"
print("OK: honest_score L8 hybrid skip wired (sa-0018)")
PY

bash validate-honest-score-l8-skip-v1.sh

python3 - <<'PY'
# sa-0027 — skip L8 embeddings-later in not_here when hybrid shipped
from pathlib import Path

import system_roadmap as sr

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-honest-score-l8-skip-v1.sh").is_file(), "missing sa-0027 l8-skip validator"
embed = scripts.parent / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
index = Path.home() / ".sina" / "vector_index_v1.json"
hybrid = embed.is_file() and index.is_file()
assert sr._l8_hybrid_live() == hybrid, f"_l8_hybrid_live drift: {sr._l8_hybrid_live()} vs {hybrid}"
if hybrid:
    nh = (sr._build_world_target_map().get("honest_score") or {}).get("not_here") or []
    for stale in ("full L8 embeddings later", "Embedding index (D5 is token retrieval today)", "L8 hybrid scaffold"):
        assert not any(stale in str(line) for line in nh), f"stale L8 not_here {stale!r} (sa-0027)"
print(f"OK: L8 embeddings-later skip when hybrid shipped (sa-0027) · hybrid={hybrid}")
PY

bash validate-strategic-synthesis-this-week-v1.sh

python3 - <<'PY'
# sa-0028 — strategic_synthesis_hub this_week wired in phase-s0 pack
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-strategic-synthesis-this-week-v1.sh").is_file(), "missing sa-0028 validator"
print("OK: strategic_synthesis this_week spine+fleet+wire G3 wired (sa-0028)")
PY

bash validate-goal-dispatch-closure-v1.sh

python3 - <<'PY'
# sa-0029 — goal-dispatch-closure in_progress + spine bridge blocker
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-goal-dispatch-closure-v1.sh").is_file(), "missing sa-0029 validator"
print("OK: goal-dispatch-closure spine bridge blocker wired (sa-0029)")
PY

bash validate-strategic-synthesis-p2-pendings-v1.sh

python3 - <<'PY'
# sa-0030 / sa-0055 — P2 L0-full pendings partial not open
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-strategic-synthesis-p2-pendings-v1.sh").is_file(), "missing sa-0030/sa-0055 validator"
hub = (scripts / "strategic_synthesis_hub.py").read_text(encoding="utf-8")
assert '"P2", "L0-full editor telemetry"' in hub and '"partial"' in hub, "hub P2 partial missing (sa-0055)"
print("OK: P2 L0-full pendings partial wired (sa-0030 · sa-0055)")
PY

bash validate-eval-critic-synthesis-alignment-v1.sh

python3 - <<'PY'
# sa-0019 — synthesis Eval line wired to disk report
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-eval-critic-synthesis-alignment-v1.sh").is_file(), "missing sa-0019 validator"
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "eval_synthesis_critic_drift_errors" in audit, "audit missing eval synthesis drift check (sa-0019)"
print("OK: eval critic synthesis alignment wired (sa-0019)")
PY

bash validate-synthesis-eval-line-v1.sh

python3 - <<'PY'
# sa-0031 — synthesis Eval-1b pendings row aligned to disk report
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-synthesis-eval-line-v1.sh").is_file(), "missing sa-0031 validator"
print("OK: synthesis Eval line disk sync wired (sa-0031)")
PY

bash validate-eval-live-not-here-regression-v1.sh

python3 - <<'PY'
# sa-0032 — live eval ok must not leave Eval-1b in honest_score.not_here
from pathlib import Path

scripts = Path(__file__).resolve().parent
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert (scripts / "validate-eval-live-not-here-regression-v1.sh").is_file(), "missing sa-0032 validator"
assert "_check_honest_score_not_here_regression" in audit, "audit missing eval not_here regression (sa-0032)"
assert "Eval-1b behavioral proof" in audit, "audit missing Eval-1b stale guard (sa-0032)"
print("OK: eval live not_here regression wired (sa-0032)")
PY

bash validate-map-pointer-docs-v1.sh

python3 - <<'PY'
# sa-0033 — MAP_POINTER_DOCS reference v5 map only
from pathlib import Path

import audit_hub_source_alignment as audit

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-map-pointer-docs-v1.sh").is_file(), "missing sa-0033 validator"
assert audit.MAP_DOC.endswith("WORLD_TARGET_MODEL_MAP_LOCKED_v5.md"), audit.MAP_DOC
assert len(audit.MAP_POINTER_DOCS) >= 10, audit.MAP_POINTER_DOCS
print("OK: MAP_POINTER_DOCS v5-only wired (sa-0033)")
PY

bash validate-governance-drift-zero-items-v1.sh

python3 - <<'PY'
# sa-0034 — governance drift items must be 0
from pathlib import Path

scripts = Path(__file__).resolve().parent
fcb = (scripts / "find_critical_bugs.py").read_text(encoding="utf-8")
assert (scripts / "validate-governance-drift-zero-items-v1.sh").is_file(), "missing sa-0034 validator"
assert "validate-governance-drift-v1.sh" in fcb, "find_critical_bugs missing governance-drift chain"
print("OK: governance drift zero-items wired (sa-0034)")
PY

bash validate-strategic-synthesis-api-alignment-v1.sh

python3 - <<'PY'
# sa-0035 — STRATEGIC_NEXT_STEPS doc vs /api/strategic-synthesis-v1
from pathlib import Path

scripts = Path(__file__).resolve().parent
server = (scripts / "sina-command-server.py").read_text(encoding="utf-8")
assert (scripts / "validate-strategic-synthesis-api-alignment-v1.sh").is_file(), "missing sa-0035 validator"
assert "/api/strategic-synthesis-v1" in server, "hub missing strategic-synthesis API (sa-0035)"
print("OK: strategic synthesis API doc alignment wired (sa-0035)")
PY

bash validate-enforce-not-here-regression-v1.sh

python3 - <<'PY'
# sa-0036 — ENFORCE-only not_here drops when gate_mode is enforce
from pathlib import Path

import system_roadmap as sr

scripts = Path(__file__).resolve().parent
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert (scripts / "validate-enforce-not-here-regression-v1.sh").is_file(), "missing sa-0036 validator"
assert "_gate_is_enforce" in dir(sr), "system_roadmap missing _gate_is_enforce (sa-0036)"
assert "ENFORCE-only not_here" in audit, "audit missing ENFORCE-only regression (sa-0036)"
print("OK: ENFORCE-only not_here enforce-gate wired (sa-0036)")
PY

bash validate-phase-d-complete-artifacts-v1.sh

python3 - <<'PY'
# sa-0037 — _phase_d_complete matches D1–D16 in-repo artifacts
from pathlib import Path

import audit_hub_source_alignment as audit
from system_roadmap import _phase_d_complete, _pre_llm_shipped_count

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-phase-d-complete-artifacts-v1.sh").is_file(), "missing sa-0037 validator"
assert hasattr(audit, "_check_phase_d_complete_artifacts_regression"), "missing audit regression (sa-0037)"
assert _phase_d_complete() == (_pre_llm_shipped_count() == 16), "phase_d_complete drift"
print("OK: phase_d_complete D1–D16 artifacts wired (sa-0037)")
PY

bash validate-essentials-nav-sync-v1.sh

python3 - <<'PY'
# sa-0038 — audit_essentials_nav sidebar tabs match app.js
from pathlib import Path

import audit_hub_source_alignment as audit

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-essentials-nav-sync-v1.sh").is_file(), "missing sa-0038 validator"
assert (scripts / "audit_essentials_nav.py").is_file(), "missing audit_essentials_nav.py"
assert hasattr(audit, "_check_essentials_nav_regression"), "missing audit nav regression (sa-0038)"
print("OK: essentials nav sync wired (sa-0038)")
PY

bash validate-app-js-no-stale-map-v2-v1.sh

python3 - <<'PY'
# sa-0039 — app.js zero WORLD_TARGET_MODEL_MAP_LOCKED_v2 references
from pathlib import Path

scripts = Path(__file__).resolve().parent
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert (scripts / "validate-app-js-no-stale-map-v2-v1.sh").is_file(), "missing sa-0039 validator"
assert "WORLD_TARGET_MODEL_MAP_LOCKED_v2" in audit, "audit missing v2 stale guard (sa-0039)"
print("OK: app.js no stale map v2 wired (sa-0039)")
PY

bash validate-program-progress-build-sync-v1.sh

python3 - <<'PY'
# sa-0040 — PROGRAM_PROGRESS signals_auto.synced_at updates on build
from pathlib import Path

scripts = Path(__file__).resolve().parent
build = (scripts / "build-sina-command-panel.py").read_text(encoding="utf-8")
assert "_run_update_program_progress" in build, "build missing progress sync hook (sa-0040)"
assert (scripts / "validate-program-progress-build-sync-v1.sh").is_file(), "missing sa-0040 validator"
print("OK: PROGRAM_PROGRESS build sync wired (sa-0040)")
PY

bash validate-command-data-lazy-shell-v1.sh

python3 - <<'PY'
# sa-0041 — index.html __COMMAND_DATA_LAZY + shell under 500KB
from pathlib import Path

import audit_hub_source_alignment as audit

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-command-data-lazy-shell-v1.sh").is_file(), "missing sa-0041 validator"
src = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "__COMMAND_DATA_LAZY" in src, "audit missing lazy-load guard (sa-0041)"
assert "SHELL_MAX_BYTES" in src, "audit missing shell cap (sa-0041)"
print("OK: command-data lazy shell wired (sa-0041)")
PY

bash validate-feedback-aggregate-hub-sync-v1.sh

python3 - <<'PY'
# sa-0042 — FEEDBACK_AGGREGATE execution_truth hub_built_at matches hub build
from pathlib import Path

scripts = Path(__file__).resolve().parent
build = (scripts / "build-sina-command-panel.py").read_text(encoding="utf-8")
assert "_run_sync_feedback_aggregate" in build, "build missing feedback sync hook (sa-0042)"
assert (scripts / "sync_feedback_aggregate_hub_built_at_v1.py").is_file(), "missing sync script (sa-0042)"
assert (scripts / "validate-feedback-aggregate-hub-sync-v1.sh").is_file(), "missing sa-0042 validator"
print("OK: FEEDBACK_AGGREGATE hub sync wired (sa-0042)")
PY

bash validate-honest-score-l8-hybrid-v1.sh

python3 - <<'PY'
# sa-0043 — reject unconditional L8 line in honest_score when hybrid shipped
from pathlib import Path

import system_roadmap as sr

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-honest-score-l8-hybrid-v1.sh").is_file(), "missing sa-0043 validator"
assert hasattr(sr, "_l8_hybrid_live"), "missing _l8_hybrid_live (sa-0043)"
print("OK: honest_score L8 hybrid guard wired (sa-0043)")
PY

bash validate-eval-critic-claim-v1.sh

python3 - <<'PY'
# sa-0044 — ChatGPT critic Eval claim vs ~/.sina/eval_packet_v1b_report.json
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-eval-critic-claim-v1.sh").is_file(), "missing sa-0044 validator"
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "eval_synthesis_critic_drift_errors" in audit, "audit missing critic drift guard (sa-0044)"
print("OK: eval critic claim wired (sa-0044)")
PY

bash validate-enforce-dispatch-policy-alignment-v1.sh

python3 - <<'PY'
# sa-0020 — ENFORCE synthesis aligned to dispatch-policy API gate_mode
from pathlib import Path

import model_dispatch

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-enforce-dispatch-policy-alignment-v1.sh").is_file(), "missing sa-0020 validator"
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "enforce_synthesis_critic_drift_errors" in audit, "audit missing ENFORCE synthesis drift (sa-0020)"
pe = (scripts / "runtime" / "dispatch_policy" / "policy_engine.py").read_text(encoding="utf-8")
assert '"gate_mode"' in pe, "dispatch_policy_payload missing gate_mode (sa-0020)"
assert hasattr(model_dispatch, "enforce_synthesis_critic_drift_errors")
print(f"OK: ENFORCE dispatch-policy alignment wired (sa-0020) · gate={model_dispatch.current_gate_mode()}")
PY

bash validate-council-ssot-trust-order-v1.sh

python3 - <<'PY'
# sa-0021 — COUNCIL_BRIEF SSOT trust order bullet + payload field
from pathlib import Path

from council_strategic_brief import SSOT_TRUST_ORDER, strategic_brief_payload

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-council-ssot-trust-order-v1.sh").is_file(), "missing sa-0021 validator"
p = strategic_brief_payload()
assert p.get("ssot_trust_order") == SSOT_TRUST_ORDER, p.get("ssot_trust_order")
print(f"OK: COUNCIL_BRIEF ssot_trust_order wired (sa-0021) · {SSOT_TRUST_ORDER}")
PY

bash validate-dispatch-ready-lock-v1.sh

python3 - <<'PY'
# sa-0022 — reject global dispatch_ready=true in runtime scripts
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "dispatch_ready_lock.py").is_file(), "missing dispatch_ready_lock.py (sa-0022)"
assert (scripts / "validate-dispatch-ready-lock-v1.sh").is_file(), "missing sa-0022 validator"
print("OK: dispatch_ready global true lock wired (sa-0022)")
PY

python3 - <<'PY'
# sa-0023 — strategic_synthesis bottleneck must reflect live dispatch_ready SSOT
from strategic_synthesis_hub import strategic_synthesis_payload
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

p = strategic_synthesis_payload()
bottleneck = p.get("bottleneck") or ""
exp_ready, exp_blockers, _ = orchestrator_dispatch_ready()
assert "dispatch_ready=" in bottleneck.lower(), bottleneck
gates = p.get("machine_gates") or {}
assert bool(gates.get("dispatch_ready")) == exp_ready, (gates, exp_blockers)
print(f"OK: strategic_synthesis bottleneck dispatch_ready={exp_ready} (sa-0023) · {bottleneck}")
PY

bash validate-eval-packet-v1b-strict-without-live-env-v1.sh

python3 - <<'PY'
# sa-0024 — strict build runs validate-eval-packet-v1b-live without SINA_EVAL_1B_LIVE=1
from pathlib import Path

scripts = Path(__file__).resolve().parent
build = (scripts / "build-sina-command-panel.py").read_text(encoding="utf-8")
assert (scripts / "validate-eval-packet-v1b-strict-without-live-env-v1.sh").is_file(), (
    "missing sa-0024 validator"
)
assert "validate-eval-packet-v1b-live.sh" in build, "build missing eval-1b live validator (sa-0024)"
assert "validate-eval-packet-v1b-strict-build-chain-v1.sh" in build, (
    "build missing strict eval chain (sa-0024/sa-0127)"
)
print("OK: eval-1b live in strict without SINA_EVAL_1B_LIVE env wired (sa-0024)")
PY

python3 - <<'PY'
# sa-0025 — SOURCEA-PRIORITY SSOT alignment PASS row + append helper
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "append_ssot_alignment_priority_v1.py").is_file(), "missing append_ssot_alignment_priority_v1 (sa-0025)"
assert (scripts / "validate-sourcea-priority-ssot-row-v1.sh").is_file(), "missing sa-0025 validator"
print("OK: SOURCEA-PRIORITY SSOT alignment row wired (sa-0025)")
PY

bash validate-sourcea-priority-ssot-row-v1.sh

python3 - <<'PY'
# sa-0075 — SOURCEA-PRIORITY SSOT alignment PASS row for sa-0075
from pathlib import Path

scripts = Path(__file__).resolve().parent
pri = (scripts.parent / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md").read_text(encoding="utf-8")
assert "sa-0075" in pri and "SSOT alignment PASS" in pri, "missing sa-0075 PRIORITY row"
append = (scripts / "append_ssot_alignment_priority_v1.py").read_text(encoding="utf-8")
assert "--marker" in append, "append helper missing --marker for sa-0075"
print("OK: SOURCEA-PRIORITY sa-0075 SSOT alignment row wired (sa-0075)")
PY

bash validate-honest-score-not-here-drift-v1.sh

python3 - <<'PY'
# sa-0026 — audit_hub_source_alignment strict + honest_score not_here drift
import subprocess
import sys
from pathlib import Path

scripts = Path(__file__).resolve().parent
assert (scripts / "validate-honest-score-not-here-drift-v1.sh").is_file(), "missing sa-0026 drift validator"
proc = subprocess.run(
    [sys.executable, "audit_hub_source_alignment.py", "strict"],
    cwd=str(scripts),
    capture_output=True,
    text=True,
)
assert proc.returncode == 0 and "OK:" in proc.stdout, proc.stdout + proc.stderr
print("OK: audit_hub_source_alignment strict + not_here drift (sa-0026)")
PY

python3 - <<'PY'
from pathlib import Path
from strategic_synthesis_hub import strategic_synthesis_payload, this_week, strategic_goals, pendings

p = strategic_synthesis_payload()
tw = this_week()
assert any("spine" in (x.get("action") or "").lower() for x in tw), tw
assert any("fleet" in (x.get("action") or "").lower() for x in tw), tw
assert any("g3" in (x.get("action") or "").lower() or "wire" in (x.get("who") or "").lower() for x in tw), tw

goals = strategic_goals()
gdc = next((g for g in goals if g.get("id") == "goal-dispatch-closure"), {})
from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready
exp_ready, _, _ = orchestrator_dispatch_ready()
exp_status = "done" if exp_ready else "in_progress"
assert gdc.get("status") == exp_status, gdc
assert "spine" in (gdc.get("blocker") or "").lower(), gdc

pend = pendings()
p2 = next((x for x in pend if x.get("id") == "P2"), {})
assert p2.get("status") == "partial", p2
assert p2.get("status") != "open", p2

gates = p.get("machine_gates") or {}
if gates.get("eval_1b_gate_ok"):
    assert "eval_1b_gate_ok=true" in (p.get("one_line") or ""), p.get("one_line")

# MAP_POINTER_DOCS reference current MAP (sa-0008)
import audit_hub_source_alignment as audit

root = audit.SOURCE_A
for rel in audit.MAP_POINTER_DOCS:
    p = root / rel
    assert p.is_file(), f"missing pointer doc {rel}"
    assert audit.MAP_DOC.split("/")[-1] in p.read_text(encoding="utf-8"), rel

print("OK: validate-phase-s0-ssot-alignment-v1 · sa-0002..0044 pack checks")
PY

bash validate-governance-drift-v1.sh
