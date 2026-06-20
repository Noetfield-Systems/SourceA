#!/usr/bin/env bash
# validate-gtm-moat-governance-scoreboard-t2-crossref-v1.sh — sa-0570 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0570-gtm-moat-governance-scoreboard-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0520-gtm-moat-governance-scoreboard_LOCKED_v1.md"
moat_doc = root / "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md"
law_doc = root / "AGENT_SCOREBOARD_LOCKED_v1.md"
receipt = root / "receipts/sa-0520-receipt.json"

assert cross.is_file(), "missing sa-0570 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0520",
    "sa-0545",
    "sa-0570",
    "sa-0520-gtm-moat-governance-scoreboard_LOCKED_v1.md",
    "AGENT_SCOREBOARD_LOCKED_v1.md",
    "validate-gtm-moat-governance-scoreboard-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0520 attachment missing"
assert moat_doc.is_file(), "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md missing"
assert law_doc.is_file(), "AGENT_SCOREBOARD_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0520 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("gtm_moat_governance_scoreboard_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.gtm_moat_governance_scoreboard_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0520":
    raise SystemExit("FAIL: canonical_sa must be sa-0520")
if hook.get("t1_echo_sa") != "sa-0545":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0545")
if "sa-0570-gtm-moat-governance-scoreboard-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0570 attachment")

print("OK: validate-gtm-moat-governance-scoreboard-t2-crossref-v1 · canonical=sa-0520 · t1=sa-0545 · sa-0570")
PY

bash validate-gtm-moat-governance-scoreboard-v1.sh
