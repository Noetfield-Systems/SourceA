#!/usr/bin/env bash
# validate-no-agent-invitation-v1.sh — guard-only copy; no founder action invitations
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-no-agent-invitation-v1 — $*" >&2; exit 1; }

FLAG="$HOME/.sina/founder-no-agent-invitation-v1.flag"
[[ -f "$FLAG" ]] || fail "founder-no-agent-invitation-v1.flag missing (law requires ON)"

python3 <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(".")
errors: list[str] = []

# Agent-facing guard scripts must not print founder action steps
guard_scripts = [
    "scripts/wbc-form-check.sh",
    "scripts/wbc-ui-first-check.sh",
    "scripts/wbc-guard-check.sh",
]
invite_pat = re.compile(
    r"FOUNDER PATH|one next tap|click submit|tap here|submit when ready|"
    r"hard refresh|cmd\+shift\+r|open form · submit",
    re.I,
)
for rel in guard_scripts:
    p = root / rel
    if not p.is_file():
        continue
    raw = p.read_text(encoding="utf-8", errors="replace")
    if invite_pat.search(raw):
        errors.append(f"{rel}: invitation language in guard script")

# Hub founder surfaces — same forbidden set as copy-safety
forbidden = [
    (r"automatic recommended picks", "INCIDENT-037"),
    (r"open form · submit", "INCIDENT-037 invitation"),
    (r"one next tap", "founder-no-invitation"),
    (r"click submit", "founder-no-invitation"),
    (r"tap here", "founder-no-invitation"),
    (r"submit only", "founder-no-invitation"),
    (r"founder pick", "founder-no-invitation"),
]
cmd = root / "agent-control-panel/command-data.json"
if cmd.is_file():
    data = json.loads(cmd.read_text(encoding="utf-8"))
    founder = (data.get("command_center") or {}).get("founder") or {}
    blob = "\n".join(
        [
            json.dumps(founder.get("p0") or {}),
            json.dumps(founder.get("must_do_today") or []),
            json.dumps((data.get("home_founder_view") or {}).get("quick_actions") or []),
        ]
    ).lower()
    for pat, label in forbidden:
        if re.search(pat, blob, re.I):
            errors.append(f"command-data founder surfaces: {label}")

# form route SSOT — button must be guard label not invitation
sys.path.insert(0, "scripts")
from form_official_canvas_route_v1 import hub_canvas_target  # noqa: E402

route = hub_canvas_target()
btn = str(route.get("button_label") or "")
if re.search(r"open form|submit", btn, re.I):
    errors.append(f"form_official_canvas_route button_label invitation: {btn!r}")

# behavior settings — flag must be active
settings_path = root / "data/agent-behavior-settings-v1.json"
if settings_path.is_file():
    ssot = json.loads(settings_path.read_text(encoding="utf-8"))
    no_inv = ssot.get("founder_no_invitation") or {}
    if not no_inv.get("active"):
        errors.append("agent-behavior-settings founder_no_invitation.active != true")

if errors:
    print("FAIL: validate-no-agent-invitation-v1")
    for e in errors:
        print(f"  - {e}")
    raise SystemExit(1)

# Live wire receipts — no invitation in agent-injected surfaces (allow prohibition inject)
sina = Path.home() / ".sina"
invite_live = re.compile(
    r"open form · submit|submit only|one next tap|tap here|submit when ready|"
    r"tap safety|hub →.*submit|prove rt live",
    re.I,
)
for rel in (
    "agent-live-surfaces-v1.json",
    "live-founder-decision-form-v1.json",
):
    p = sina / rel
    if not p.is_file():
        continue
    raw = p.read_text(encoding="utf-8", errors="replace")
    for line in raw.splitlines():
        low = line.lower()
        if "never one next tap" in low or "no invitation" in low:
            continue
        if invite_live.search(line):
            errors.append(f"~/.sina/{rel}: stale invitation language")
            break

# Truth bundle — check hub projection slice only
tb = sina / "last-truth-bundle-v1.json"
if tb.is_file():
    try:
        row = json.loads(tb.read_text(encoding="utf-8"))
        founder = ((row.get("command_center") or {}).get("founder") or {})
        blob = json.dumps(founder).lower()
        for pat, label in forbidden:
            if re.search(pat, blob, re.I):
                errors.append(f"truth-bundle founder: {label}")
    except (OSError, json.JSONDecodeError):
        pass

if errors:
    print("FAIL: validate-no-agent-invitation-v1")
    for e in errors:
        print(f"  - {e}")
    raise SystemExit(1)

print("OK: validate-no-agent-invitation-v1 · flag ON · guard scripts clean · hub copy clean · live wire clean")
PY
