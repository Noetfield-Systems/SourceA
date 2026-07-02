#!/usr/bin/env bash
# validate-controlled-autorun-skill-v1.sh — skill v3 + laws + reconciler wired (light, Mac-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-controlled-autorun-skill-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" ]] || fail "missing controlled-autorun SKILL.md"
[[ -f "$ROOT/.cursor/skills/controlled-autorun/references/sourcea-wiring.md" ]] || fail "missing sourcea-wiring.md"
[[ -f "$ROOT/.cursor/skills/controlled-autorun/references/receipt-schemas.md" ]] || fail "missing receipt-schemas.md"
[[ -f "$ROOT/.cursor/skills/controlled-autorun/references/deterministic-loops.md" ]] || fail "missing deterministic-loops.md (v3)"
[[ -f "$ROOT/docs/CONTROLLED_AUTORUN_LAWS_v3.md" ]] || fail "missing CONTROLLED_AUTORUN_LAWS_v3.md"
[[ -f "$ROOT/scripts/phase_reconciler_v1.py" ]] || fail "missing phase_reconciler_v1.py"
[[ -f "$ROOT/scripts/verify_autorun_zero_manual_v1.py" ]] || fail "missing verify_autorun_zero_manual_v1.py"
[[ -f "$ROOT/scripts/autorun_pending_v1.py" ]] || fail "missing autorun_pending_v1.py"

grep -q 'name: controlled-autorun' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL frontmatter missing controlled-autorun name"
grep -q 'Controlled Autorun v3' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL not v3"
grep -q 'L13' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL missing L13 determinism law"
grep -q 'sourcea-wiring.md' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL not wired to sourcea-wiring"
grep -q 'deterministic-loops.md' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL not wired to deterministic-loops"
grep -q 'CONTROLLED_AUTORUN_LAWS_v3' "$ROOT/docs/CONTROLLED_AUTORUN_LAWS_v3.md" \
  || fail "laws v3 schema missing"

echo "PASS: validate-controlled-autorun-skill-v1.sh"
