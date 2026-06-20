#!/usr/bin/env bash
# sa-0520 — GTM moat notes vs governance scoreboard law cross-check
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0520-gtm-moat-governance-scoreboard_LOCKED_v1.md"
ARCH="SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md"
LAW="AGENT_SCOREBOARD_LOCKED_v1.md"
SYNTH="archive/attachments/2026-06-11/sa-0786-governance-moat-synthesis-lesson_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
test -f "$ARCH" || { echo "FAIL: missing $ARCH"; exit 1; }
test -f "$LAW" || { echo "FAIL: missing $LAW"; exit 1; }
test -f "$SYNTH" || { echo "FAIL: missing $SYNTH"; exit 1; }
python3 - <<'PY'
import json
import importlib.util
from pathlib import Path

arch = Path("SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md").read_text(encoding="utf-8")
for needle in (" moat", "Factory honesty", "Honest progress"):
    if needle not in arch:
        raise SystemExit(f"FAIL: reference arch missing {needle!r}")

spec_ssh = importlib.util.spec_from_file_location("ssh", Path("scripts/strategic_synthesis_hub.py"))
ssh = importlib.util.module_from_spec(spec_ssh)
spec_ssh.loader.exec_module(ssh)
goals = {g.get("id"): g for g in ssh.strategic_goals()}
if goals.get("goal-governance-moat", {}).get("status") not in ("active", "in_progress", "done"):
    raise SystemExit(f"FAIL: goal-governance-moat status {goals.get('goal-governance-moat', {}).get('status')!r}")

spec_asb = importlib.util.spec_from_file_location("asb", Path("scripts/agent_scoreboard.py"))
asb = importlib.util.module_from_spec(spec_asb)
spec_asb.loader.exec_module(asb)
sb = asb.scoreboard_payload()
if not sb.get("ok"):
    raise SystemExit(f"FAIL: scoreboard_payload {sb}")
if sb.get("law_doc") != "AGENT_SCOREBOARD_LOCKED_v1.md":
    raise SystemExit(f"FAIL: law_doc {sb.get('law_doc')!r}")
tagline = (sb.get("tagline") or "").lower()
if "auto-checks" not in tagline or "not asf verify" not in tagline:
    raise SystemExit("FAIL: scoreboard tagline must deny ASF verify authority")
if int(sb.get("fleet_auto_green_count") or 0) < int(sb.get("agent_count") or 0):
    raise SystemExit("FAIL: fleet not fully auto-green")

cd = json.loads(Path("agent-control-panel/command-data.json").read_text(encoding="utf-8"))
hub_sb = cd.get("agent_scoreboard") or {}
if hub_sb.get("law_doc") != "AGENT_SCOREBOARD_LOCKED_v1.md":
    raise SystemExit(f"FAIL: command-data scoreboard law {hub_sb.get('law_doc')!r}")

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
gms = (pp.get("signals_auto") or {}).get("gtm_moat_scoreboard") or {}
for key in ("moat_doc", "scoreboard_law", "crossref_doc", "synthesis_doc", "aligned_moat_claims"):
    if key not in gms:
        raise SystemExit(f"FAIL: signals_auto.gtm_moat_scoreboard missing {key}")
if "sa-0520-gtm-moat" not in str(gms.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0520 attachment")
if gms.get("scoreboard_law") != "AGENT_SCOREBOARD_LOCKED_v1.md":
    raise SystemExit("FAIL: scoreboard_law path mismatch")

print("OK: validate-gtm-moat-governance-scoreboard-v1 · sa-0520")
PY
