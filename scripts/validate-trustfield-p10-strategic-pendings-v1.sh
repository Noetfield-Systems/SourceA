#!/usr/bin/env bash
# sa-0518 — TrustField P10 pending in strategic pendings cross-check
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0518-trustfield-p10-strategic-pendings_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
python3 - <<'PY'
import json
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("ssh", Path("scripts/strategic_synthesis_hub.py"))
ssh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ssh)

p10 = next((p for p in ssh.pendings() if p.get("id") == "P10"), None)
if not p10:
    raise SystemExit("FAIL: P10 missing from strategic_synthesis_hub pendings")
if p10.get("status") != "in_progress":
    raise SystemExit(f"FAIL: P10 status {p10.get('status')!r} expected in_progress")
if p10.get("owner") != "trustfield":
    raise SystemExit(f"FAIL: P10 owner {p10.get('owner')!r}")

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
tf = (pp.get("signals_auto") or {}).get("trustfield_p10") or {}
for key in ("crossref_doc", "hub_status", "portfolio_note", "commercial_pick"):
    if key not in tf:
        raise SystemExit(f"FAIL: signals_auto.trustfield_p10 missing {key}")
if "sa-0518-trustfield-p10" not in str(tf.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0518 attachment")

port = next((p for p in pp.get("parallel_plans", []) if p.get("id") == "PORTFOLIO"), None)
if not port or "P10" not in (port.get("next_action") or ""):
    raise SystemExit("FAIL: PORTFOLIO next_action must mention P10")

pick = Path.home() / ".sina/commercial-p0-five-step-pick-v1.json"
if pick.is_file():
    data = json.loads(pick.read_text(encoding="utf-8"))
    if not any(s.get("id") == "11.01" for s in data.get("steps", [])):
        raise SystemExit("FAIL: commercial pick 11.01 missing")

print("OK: validate-trustfield-p10-strategic-pendings-v1 · sa-0518")
PY
