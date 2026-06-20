#!/usr/bin/env bash
# CRITICAL: REGISTRY done must equal honest receipt count — no YAML inflate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import json
import sys
from pathlib import Path

root = Path(".")
sys.path.insert(0, str(root / "scripts"))
from registry_honest_lib_v1 import audit_registry_done, enforce_honest_registry  # noqa: E402

before = audit_registry_done()
if before["unproven_done"] > 0:
    enforced = enforce_honest_registry(dry_run=False)
    after = enforced.get("after") or audit_registry_done()
    if after["unproven_done"] > 0:
        print(
            f"FAIL: REGISTRY_HONEST_GATE unproven_done={after['unproven_done']} "
            f"raw={after['raw_done']} honest={after['honest_done']}",
            file=sys.stderr,
        )
        print(json.dumps(after, indent=2), file=sys.stderr)
        sys.exit(1)
    print(
        f"OK: auto-reverted {enforced.get('reverted_count', 0)} unproven done "
        f"→ honest {after['honest_done']}/{after['total']}"
    )
else:
    print(f"OK: REGISTRY honest gate · {before['honest_done']}/{before['total']} done · 0 unproven")

audit = audit_registry_done()
if audit["unproven_done"] != 0:
    print("FAIL: unproven_done still > 0 after enforce", file=sys.stderr)
    sys.exit(1)
print("OK: validate-registry-honest-gate-v1")
PY

bash "$ROOT/scripts/validate-monitor-honesty-v1.sh"
