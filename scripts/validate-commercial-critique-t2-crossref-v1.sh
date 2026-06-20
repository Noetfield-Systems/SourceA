#!/usr/bin/env bash
# validate-commercial-critique-t2-crossref-v1.sh — sa-0563 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0563-commercial-critique-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0513-commercial-critique-vs-program-progress-locks_LOCKED_v1.md"
critic_law = root / "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
receipt = root / "receipts/sa-0513-receipt.json"

assert cross.is_file(), "missing sa-0563 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0513",
    "sa-0538",
    "sa-0563",
    "sa-0513-commercial-critique-vs-program-progress-locks_LOCKED_v1.md",
    "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0513 attachment missing"
assert critic_law.is_file(), "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0513 receipt missing"
for marker in ("MASTER_NEXT_PLANS_SYNTHESIS", "Critic claims vs lock truth", "build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("commercial_critique_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.commercial_critique_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0513":
    raise SystemExit("FAIL: canonical_sa must be sa-0513")
if hook.get("t1_echo_sa") != "sa-0538":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0538")
if "sa-0563-commercial-critique-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0563 attachment")

print("OK: validate-commercial-critique-t2-crossref-v1 · canonical=sa-0513 · t1=sa-0538 · sa-0563")
PY

bash validate-commercial-critique-program-progress-locks-v1.sh
