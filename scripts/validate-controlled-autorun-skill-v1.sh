#!/usr/bin/env bash
# validate-controlled-autorun-skill-v1.sh — skill + laws + reconciler wired (light, Mac-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-controlled-autorun-skill-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" ]] || fail "missing controlled-autorun SKILL.md"
[[ -f "$ROOT/.cursor/skills/controlled-autorun/references/sourcea-wiring.md" ]] || fail "missing sourcea-wiring.md"
[[ -f "$ROOT/.cursor/skills/controlled-autorun/references/receipt-schemas.md" ]] || fail "missing receipt-schemas.md"
[[ -f "$ROOT/docs/CONTROLLED_AUTORUN_LAWS_v2.md" ]] || fail "missing CONTROLLED_AUTORUN_LAWS_v2.md"
[[ -f "$ROOT/scripts/phase_reconciler_v1.py" ]] || fail "missing phase_reconciler_v1.py"
[[ -f "$ROOT/scripts/verify_autorun_zero_manual_v1.py" ]] || fail "missing verify_autorun_zero_manual_v1.py"
[[ -f "$ROOT/.github/workflows/external-verify.yml" ]] || fail "missing external-verify workflow"

grep -q 'name: controlled-autorun' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL frontmatter missing controlled-autorun name"
grep -q 'sourcea-wiring.md' "$ROOT/.cursor/skills/controlled-autorun/SKILL.md" \
  || fail "SKILL not wired to sourcea-wiring"
grep -q 'controlled-autorun' "$ROOT/docs/CONTROLLED_AUTORUN_LAWS_v2.md" \
  || fail "laws doc missing skill pointer"

echo "PASS: validate-controlled-autorun-skill-v1.sh"
