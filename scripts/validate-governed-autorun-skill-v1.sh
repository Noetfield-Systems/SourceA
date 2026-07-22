#!/usr/bin/env bash
# validate-governed-autorun-skill-v1.sh — skill v3 + laws + reconciler wired (light, Mac-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-governed-autorun-skill-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/.cursor/skills/governed-autorun/SKILL.md" ]] || fail "missing governed-autorun SKILL.md"
[[ -f "$ROOT/.cursor/skills/governed-autorun/references/sourcea-wiring.md" ]] || fail "missing sourcea-wiring.md"
[[ -f "$ROOT/.cursor/skills/governed-autorun/references/receipt-schemas.md" ]] || fail "missing receipt-schemas.md"
[[ -f "$ROOT/.cursor/skills/governed-autorun/references/deterministic-loops.md" ]] || fail "missing deterministic-loops.md (v3)"
[[ -f "$ROOT/docs/GOVERNED_AUTORUN_LAWS_v3.md" ]] || fail "missing GOVERNED_AUTORUN_LAWS_v3.md"
[[ -f "$ROOT/scripts/phase_reconciler_v1.py" ]] || fail "missing phase_reconciler_v1.py"
[[ -f "$ROOT/scripts/verify_autorun_zero_manual_v1.py" ]] || fail "missing verify_autorun_zero_manual_v1.py"
[[ -f "$ROOT/scripts/autorun_pending_v1.py" ]] || fail "missing autorun_pending_v1.py"

grep -q 'name: governed-autorun' "$ROOT/.cursor/skills/governed-autorun/SKILL.md" \
  || fail "SKILL frontmatter missing governed-autorun name"
grep -q 'Governed Autorun v3' "$ROOT/.cursor/skills/governed-autorun/SKILL.md" \
  || fail "SKILL not v3"
grep -q 'L13' "$ROOT/.cursor/skills/governed-autorun/SKILL.md" \
  || fail "SKILL missing L13 determinism law"
grep -q 'sourcea-wiring.md' "$ROOT/.cursor/skills/governed-autorun/SKILL.md" \
  || fail "SKILL not wired to sourcea-wiring"
grep -q 'deterministic-loops.md' "$ROOT/.cursor/skills/governed-autorun/SKILL.md" \
  || fail "SKILL not wired to deterministic-loops"
grep -q 'GOVERNED_AUTORUN_LAWS_v3' "$ROOT/docs/GOVERNED_AUTORUN_LAWS_v3.md" \
  || fail "laws v3 schema missing"

echo "PASS: validate-governed-autorun-skill-v1.sh"
