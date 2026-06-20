#!/usr/bin/env bash
# validate-copy-safety-hub-v1.sh — DIRECTION-LOCK-040 forbidden copy in hub projections
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-copy-safety-hub-v1 — $*" >&2; exit 1; }

python3 scripts/external_critic_default_v1.py --wire >/dev/null 2>&1 || true

python3 <<'PY'
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from rt_live_gate_v1 import receipt_pass

root = Path(".")
errors: list[str] = []

# Forbidden in founder-facing hub JSON when RT LIVE receipt PASS
if receipt_pass():
    bad_rt = re.compile(r"prove\s+(rt\s+live|cascade)", re.I)
    for rel in (
        "agent-control-panel/command-data.json",
        "agent-control-panel/command-data-shell.json",
    ):
        p = root / rel
        if not p.is_file():
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        if bad_rt.search(raw):
            errors.append(f"{rel}: stale 'prove RT LIVE/cascade' when receipt PASS")

forbidden = [
    (r"start auto run", "AUTO-RUN promote"),
    (r"goal 1 auto-run", "AUTO-RUN promote"),
    (r"\$100m close", "FT-01"),
    (r"trust os", "FT-02 build claim"),
    (r"auto-paste to cursor", "INCIDENT-028 class"),
    (r"confirm.*auto-send", "INCIDENT-028 class"),
    (r"automatic recommended picks", "INCIDENT-037 form supremacy"),
    (r"open form · submit", "INCIDENT-037 agent invitation"),
    (r"open form · submit only", "INCIDENT-037 agent invitation"),
    (r"rows · automatic", "INCIDENT-037 agent-answered UI"),
    (r"one next tap", "founder-no-invitation"),
    (r"click submit", "founder-no-invitation"),
    (r"tap here", "founder-no-invitation"),
    (r"submit when ready", "founder-no-invitation"),
    (r"submit only", "founder-no-invitation"),
    (r"founder pick", "founder-no-invitation"),
]
cmd = root / "agent-control-panel/command-data.json"
if cmd.is_file():
    data = json.loads(cmd.read_text(encoding="utf-8"))
    founder = (data.get("command_center") or {}).get("founder") or {}
    surfaces = [
        json.dumps(founder.get("p0") or {}),
        json.dumps(founder.get("must_do_today") or []),
        json.dumps((data.get("home_founder_view") or {}).get("quick_actions") or []),
    ]
    blob = "\n".join(surfaces).lower()
    for pat, label in forbidden:
        if re.search(pat, blob, re.I):
            errors.append(f"founder surfaces: forbidden {label}")

ok_fr, msg_fr = __import__("external_critic_default_v1", fromlist=["validate_wiring"]).validate_wiring()
if not ok_fr:
    errors.append(f"FR-003: {msg_fr}")

if errors:
    print("FAIL: validate-copy-safety-hub-v1")
    for e in errors:
        print(f"  - {e}")
    raise SystemExit(1)

print("OK: validate-copy-safety-hub-v1 · FR-003 wired · hub copy clean")
PY
