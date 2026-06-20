#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
fail() { echo "FAIL: validate-cross-doc-linkage-v1 — $*" >&2; exit 1; }

DOC="$ROOT/SOURCEA_CROSS_DOC_LINKAGE_AND_AUDIT_LOCKED_v1.md"
[[ -f "$DOC" ]] || fail "missing linkage doc"

declare -a CLUSTER=(
  "brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
  "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md"
  "SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md"
  "SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md"
  "prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md"
  "SOURCEA_COMPLEX_SITUATION_FORK_MACHINE_LOCKED_v1.md"
  "prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md"
  "SOURCEA_SYSTEM_INTEGRITY_100_STEP_PLAYBOOK_LOCKED_v1.md"
  "SOURCEA_INTEGRITY_STACK_UNIFIED_BLUEPRINT_BATCH_2_LOCKED_v1.md"
)

for f in "${CLUSTER[@]}"; do
  [[ -f "$ROOT/$f" ]] || fail "missing cluster doc $f"
  grep -q "$(basename "$f")" "$DOC" || fail "linkage doc missing inventory row for $f"
done

grep -q "CROSS_DOC_LINKAGE" "$SINA_AUTHORITY_INDEX" || fail "authority row"
grep -q "CROSS_DOC_LINKAGE" "$ROOT/scripts/important_docs_index.py" || fail "doc library"
grep -q "CROSS_DOC_LINKAGE" "$ROOT/brain-os/law/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md" || fail "MANDATORY_READ"
grep -q "cross_doc_linkage" "$ROOT/scripts/agent_rules_in_charge.py" || fail "agent_rules"
grep -q "Human channel" "$DOC" || fail "human channel matrix"
grep -q "Machine channel" "$DOC" || fail "machine channel matrix"
grep -q "Dual-language" "$DOC" || fail "dual-language map"
grep -q "SESSION-INTEGRITY-10" "$DOC" || fail "cluster id"
grep -q "Document originality" "$DOC" || fail "originality algorithm §11"
grep -q "Three different" "$DOC" || fail "priority systems §12"

echo "OK: validate-cross-doc-linkage-v1"
