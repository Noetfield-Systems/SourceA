#!/usr/bin/env bash
# G1.1 — role-scoped .mdc: executor stack alwaysApply whitelist
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import sys
from pathlib import Path

ROOT = Path(".")
rules = ROOT / ".cursor/rules"
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from agent_memory_mirror_v1 import REQUIRED_ALWAYS_RULES  # noqa: WPS433
except Exception:
    REQUIRED_ALWAYS_RULES = ()

global_allow = {
    "000-entry-gate.mdc",
    "000-workspace-lock.mdc",
    "000-cross-lane-edit-forbidden.mdc",
    "000-dead-law-stubs.mdc",
    "agent-memory-mirror.mdc",
    "ecosystem-rule-conflict-resolution.mdc",
    "lost-link-recovery-reward.mdc",
    *REQUIRED_ALWAYS_RULES,
}
SEMEJ_SYNC = {"sina-command-readonly.mdc"}

always = []
for p in sorted(rules.glob("*.mdc")):
    text = p.read_text(encoding="utf-8")
    if "alwaysApply: true" in text:
        always.append(p.name)

bad = [n for n in always if n not in global_allow and n not in SEMEJ_SYNC]
if bad:
    print(f"FAIL: non-global alwaysApply (role rules need globs): {bad}", file=sys.stderr)
    sys.exit(1)
max_global = len(global_allow) + len([n for n in SEMEJ_SYNC if n in always])
if len(always) > max_global:
    print(f"FAIL: {len(always)} alwaysApply rules (max {max_global}): {always}", file=sys.stderr)
    sys.exit(1)
print(f"OK: validate-cursor-rules-scoping-v1 · alwaysApply={len(always)}")
PY
