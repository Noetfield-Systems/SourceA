#!/usr/bin/env bash
# validate-brain-not-command-data-ssot-v1.sh — Brain/Worker must not treat command-data as runtime SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-brain-not-command-data-ssot-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "SSOT checks"
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
ROOT = Path(".")
SINA = Path.home() / ".sina"

# 1) Boss queue must not be empty in SINGLE_SA — unless lawful exhaustion (cycle2 done · s8 skipped only)
fn_path = SINA / "factory-now-v1.json"
if fn_path.is_file():
    fn = json.loads(fn_path.read_text())
    mode = str(fn.get("mode") or "")
    if mode == "SINGLE_SA" and not fn.get("kill_flag"):
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
        if lawful_exhausted:
            print(
                f"OK: queue exhausted lawful — only skipped backlog "
                f"(pos={head.get('pos')}/{head.get('total')})"
            )
        else:
            from healthy_queue_ssot_lib import load_healthy_queue, queue_items  # noqa: WPS433
            try:
                _, q = load_healthy_queue()
                items = queue_items(q)
            except Exception as exc:
                raise SystemExit(f"healthy queue load failed: {exc}") from exc
            if len(items) == 0:
                raise SystemExit("healthy queue empty while SINGLE_SA — cart must FAIL")
            if not str(fn.get("queue_sa") or "").startswith("sa-"):
                raise SystemExit(f"factory-now.queue_sa empty/stale: {fn.get('queue_sa')!r}")

# 2) brain-current-action must not lag brain receipt > 10 min when both exist
bca = SINA / "brain-current-action-v1.json"
bval = SINA / "brain-goal1-validation-v1.json"
if bca.is_file() and bval.is_file():
    a = json.loads(bca.read_text())
    v = json.loads(bval.read_text())
    sa_a = ((a.get("inbox") or {}).get("sa_id") or "")
    sa_v = ((v.get("queue_head") or {}).get("sa_id") or "")
    if sa_a and sa_v and sa_a != sa_v:
        raise SystemExit(f"brain-current-action {sa_a} != brain validation {sa_v}")

# 3) queue_ssot_unify must ok — or lawful exhaustion (cycle2 done · s8 skipped only)
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("qsu", Path("scripts/queue_ssot_unify_v1.py"))
mod = module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)
head = mod.queue_head()
if not head.get("ok"):
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
    if head.get("queue_exhausted") and len(open_non_skipped) == 0:
        print(f"OK: queue_head exhausted lawful — pos={head.get('pos')}/{head.get('total')}")
    else:
        raise SystemExit(f"queue_head not ok: {head}")
else:
    print(f"OK: queue_head {head.get('sa_id')} {head.get('role')} {head.get('pos')}/{head.get('total')}")

print("OK: validate-brain-not-command-data-ssot-v1 · queue · brain surfaces aligned")
PY

echo "OK: validate-brain-not-command-data-ssot-v1"
