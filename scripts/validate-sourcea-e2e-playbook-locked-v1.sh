#!/usr/bin/env bash
# LOCK seal — SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md must exist, indexed, Rules 0–7 present.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
PLAYBOOK="$ROOT/SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md"
RECEIPT="${HOME}/.sina/sourcea-e2e-playbook-lock-v1.json"

test -f "$PLAYBOOK"
grep -q "SOURCEA-E2E-PLAYBOOK-1.0-LOCKED" "$PLAYBOOK"
grep -q "status: LOCKED" "$PLAYBOOK"
grep -q "Rule 0" "$PLAYBOOK"
grep -q "Rule 7" "$PLAYBOOK"
grep -q "feedback_hub_sync_assert_v1.py" "$PLAYBOOK"
grep -q "validate-sourcea-e2e-standard-v1.sh" "$PLAYBOOK"

grep -q "SA-2026-06-09-E2E-PLAYBOOK" "$ROOT/SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md"
grep -q "SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md" "$ROOT/ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md"
grep -q "SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md" "$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"
grep -q "SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md" "$ROOT/brain-os/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md"
grep -q "SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md" "$SCRIPTS/important_docs_index.py"

python3 <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path("$ROOT")
playbook = root / "SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md"
text = playbook.read_text(encoding="utf-8")
required = [
    "Golden recommendation",
    "Rule 0",
    "Rule 1",
    "Rule 2",
    "Rule 3",
    "Rule 4",
    "Rule 5",
    "Rule 6",
    "Rule 7",
    "SAVE / LOCK / IMPLEMENT",
    "Session threads captured",
]
missing = [r for r in required if r not in text]
if missing:
    raise SystemExit(f"FAIL: playbook missing sections: {missing}")

receipt = {
    "schema": "sourcea-e2e-playbook-lock-v1",
    "locked": True,
    "version": "SOURCEA-E2E-PLAYBOOK-1.0-LOCKED",
    "sequence_id": "SA-2026-06-09-E2E-PLAYBOOK",
    "path": str(playbook),
    "validated_at": datetime.now(timezone.utc).isoformat(),
    "validator": "validate-sourcea-e2e-playbook-locked-v1.sh",
    "rules": list(range(8)),
    "indexes": [
        "SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md",
        "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md",
        "SOURCEA-PRIORITY.md",
        "BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md",
        "important_docs_index.py",
    ],
}
out = Path("$RECEIPT".replace("$HOME", str(Path.home())))
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(f"OK: lock receipt → {out}")
PY

echo "PASS: validate-sourcea-e2e-playbook-locked-v1"
