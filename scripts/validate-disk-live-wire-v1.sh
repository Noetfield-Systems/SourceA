#!/usr/bin/env bash
# validate-disk-live-wire-v1.sh — single live-wire law (supersedes validate-founder-zero)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-disk-live-wire-v1 — $*" >&2; exit 1; }

test -f AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md || fail "missing AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md"
test -f .cursor/rules/agent-disk-live-wire-first.mdc || fail "missing agent-disk-live-wire-first.mdc"
test -f scripts/disk_live_wire_sync_v1.py || fail "missing disk_live_wire_sync_v1.py"

grep -q 'alwaysApply: true' .cursor/rules/agent-disk-live-wire-first.mdc || fail "agent-disk-live-wire-first must be alwaysApply"
grep -q 'alwaysApply: false' .cursor/rules/001-founder-zero-sina-command-name.mdc || fail "001-founder-zero must be superseded (alwaysApply false)"

grep -q 'anti_staleness_auto_wire_v1.py' scripts/agent_session_gate_run_v1.py || fail "session gate must call anti_staleness_auto_wire"
grep -q 'anti_staleness_auto_wire_v1.py' scripts/brain-session-start.sh || fail "brain-session-start must call anti_staleness_auto_wire"

python3 scripts/disk_live_wire_sync_v1.py --json >/dev/null || fail "disk_live_wire_sync run"

test -f "${SINA}/last-truth-bundle-v1.json" || fail "missing last-truth-bundle-v1.json"
test -f "${SINA}/agent-live-surfaces-v1.json" || fail "missing agent-live-surfaces-v1.json"
test -f "${SINA}/disk-live-wire-receipt-v1.json" || fail "missing disk-live-wire-receipt-v1.json"
test -f "${SINA}/brain/BRAIN_LIVE_SURFACES_v1.json" || fail "missing BRAIN_LIVE_SURFACES_v1.json"
test -f "${SINA}/worker-live-context-v1.json" || fail "missing worker-live-context-v1.json (run worker_live_context_v1.py)"
test -f "${SINA}/brain-live-context-v1.json" || fail "missing brain-live-context-v1.json (run brain_live_context_v1.py)"

python3 - <<'PY' || fail "inject must not contain prohibition prose (INCIDENT-034)"
import json, re
from pathlib import Path
p = Path.home() / ".sina/agent-memory-mirror-v1.json"
if p.is_file():
    m = json.loads(p.read_text())
    inj = json.dumps(m.get("inject") or {})
else:
    import sys
    sys.path.insert(0, "scripts")
    from agent_memory_mirror_v1 import INJECT_LAW
    inj = json.dumps(INJECT_LAW)
bad = [
    (r"never say", "never-say"),
    (r"deprecated founder word", "deprecated-founder-word"),
    (r"not Prompt feed", "not-prompt-feed"),
    (r"forbidden_close_lines", "forbidden_close_lines"),
    (r"no Prompt feed", "no-prompt-feed"),
]
for pat, label in bad:
    if re.search(pat, inj, re.I):
        raise SystemExit(f"mirror inject still has prohibition: {label}")
if re.search(r"prompt-feed|Prompt feed", inj, re.I):
    raise SystemExit("mirror inject still mentions Prompt feed (use Next steps + disk path)")
print("OK: mirror inject positive-only (INCIDENT-034)")
PY

python3 - <<'PY' || fail "healthy queue check"
import json
import sys
from pathlib import Path

ROOT = Path(".")
SINA = Path.home() / ".sina"
fn = json.loads((SINA / "factory-now-v1.json").read_text())
mode = fn.get("mode") or ""
queue_sa = fn.get("queue_sa") or ""
inbox_sa = fn.get("inbox_sa") or ""
sys.path.insert(0, str(Path("scripts").resolve()))
from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

head = queue_head()
reg = json.loads((ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json").read_text())
skip_phases = {"phase-s8-hub-ui-ux", "s8", "phase-s8"}
cfg_path = SINA / "phase-strict-drain-v1.json"
if cfg_path.is_file():
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        for ph in cfg.get("skip_phases") or []:
            skip_phases.add(str(ph).lower())
            skip_phases.add(f"phase-{str(ph).lower()}-hub-ui-ux")
    except (OSError, json.JSONDecodeError):
        pass
open_non_skipped = [
    p
    for p in reg.get("plans") or []
    if p.get("status") != "done"
    and str(p.get("phase") or "").lower() not in skip_phases
    and not str(p.get("phase") or "").startswith("phase-s8")
]
lawful_exhausted = bool(head.get("queue_exhausted")) and len(open_non_skipped) == 0
if mode == "SINGLE_SA" and not queue_sa and not inbox_sa and not lawful_exhausted:
    raise SystemExit("SINGLE_SA with empty queue_sa and inbox_sa")
hq_path = SINA / "healthy-queue-30-active.json"
n = 0
if mode == "SINGLE_SA" and hq_path.is_file():
    hq = json.loads(hq_path.read_text())
    n = len(hq.get("queue") or hq.get("items") or [])
    if n == 0 and not lawful_exhausted:
        raise SystemExit("healthy queue empty in SINGLE_SA")
if lawful_exhausted:
    print(f"OK: factory mode={mode} queue exhausted lawful backlog=0")
else:
    print(f"OK: factory mode={mode} queue_sa={queue_sa} healthy_queue={n if mode=='SINGLE_SA' else 'n/a'}")
PY

bash scripts/validate-worker-disk-no-prompt-feed-v1.sh >/dev/null || fail "worker disk Prompt feed steer"
bash scripts/validate-brain-disk-no-prompt-feed-v1.sh >/dev/null || fail "brain disk Prompt feed steer"

python3 - <<'PY' || fail "live surfaces loop + oqg lines"
import json
from pathlib import Path
s = json.loads((Path.home() / ".sina/agent-live-surfaces-v1.json").read_text())
for key in ("factory_now_line", "zero_drift_line", "better_loop_line", "best_loop_oqg_line"):
    if not s.get(key):
        raise SystemExit(f"missing {key} — run disk_live_wire_sync + better_loop pulse + oqg score")
print("OK: live surfaces factory + zero-drift + better-loop + oqg")
PY

python3 - <<'PY' || fail "mirror live_surfaces inject"
import json
from pathlib import Path
m = json.loads((Path.home() / ".sina/agent-memory-mirror-v1.json").read_text())
ls = (m.get("inject") or {}).get("live_surfaces") or {}
if not ls.get("factory_now_line"):
    raise SystemExit("mirror inject missing live_surfaces.factory_now_line — run agent_memory_mirror --sync")
if not ls.get("best_loop_oqg_line"):
    raise SystemExit("mirror inject missing best_loop_oqg_line")
if not ls.get("nerve_system_line"):
    raise SystemExit("mirror inject missing nerve_system_line")
print("OK: mirror live_surfaces inject wired")
PY

bash scripts/validate-agent-nerve-system-v1.sh >/dev/null || fail "nerve system validator"

echo "OK: validate-disk-live-wire-v1 · unified live wire"
