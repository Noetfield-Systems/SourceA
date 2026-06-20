#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-narrative-bridge-v1 — $*" >&2; exit 1; }

LAW="$ROOT/brain-os/narrative-bridge/NARRATIVE_BRIDGE_TOUCH_BASE_LOCKED_v1.md"
LATEST="$ROOT/brain-os/narrative-bridge/LATEST_TOUCH_BASE_LOCKED_v1.md"
SKILL="$ROOT/agent-skills/shared/narrative-translator/SKILL.md"

[[ -f "$LAW" ]] || fail "missing bridge law"
[[ -f "$LATEST" ]] || fail "missing LATEST_TOUCH_BASE"
[[ -f "$SKILL" ]] || fail "missing narrative-translator skill"
grep -q "NARRATIVE_BRIDGE" "$ROOT/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md" || fail "authority row"
grep -q "narrative-translator" "$ROOT/agent-skills/REGISTRY_LOCKED_v1.json" || fail "REGISTRY entry"
grep -q "narrative-translator" "$ROOT/SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md" || fail "CURSOR_RULES_MAP"
grep -q "sina-narrative-translator" "$ROOT/brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md" || fail "MANDATORY_READ"
grep -q "LATEST_TOUCH_BASE" "$ROOT/brain-os/lanes/MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md" || fail "handoff index"
grep -q "a53f3fa1" "$LATEST" || fail "LATEST missing megachat anchor"
grep -q "TRANSLATE" "$SKILL" || fail "skill missing reply shape"
grep -q "sina-narrative-translator" "$ROOT/scripts/sync-cursor-agent-skills.sh" || fail "sync script mirror"

bash "$ROOT/scripts/sync-cursor-agent-skills.sh" >/dev/null || fail "sync-cursor-agent-skills"
[[ -f "$ROOT/.cursor/skills/sina-narrative-translator/SKILL.md" ]] || fail "project skill mirror"
[[ -f "${HOME}/.cursor/skills/sina-narrative-translator/SKILL.md" ]] || fail "user skill mirror"

bash "$ROOT/scripts/validate-mega-chat-anchors-v1.sh"

echo "OK: validate-narrative-bridge-v1"
