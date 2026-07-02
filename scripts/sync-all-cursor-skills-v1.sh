#!/usr/bin/env bash
# sync-all-cursor-skills-v1.sh — upgrade all SourceA skills → project + ~/.cursor/skills
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
DEST="${HOME}/.cursor/skills"
PROJECT="${ROOT}/.cursor/skills"

fail() { echo "FAIL: sync-all-cursor-skills-v1 — $*" >&2; exit 1; }

echo "== 1/4 agent-skills registry → user + project mirror =="
bash "$ROOT/scripts/sync-cursor-agent-skills.sh"

echo "== 2/4 controlled-autorun v3 =="
bash "$ROOT/scripts/sync-controlled-autorun-skill-v1.sh"

echo "== 3/4 signal-factory v1 =="
bash "$ROOT/scripts/sync-signal-factory-skill-v1.sh"

echo "== 4/4 project .cursor/skills → user mirror =="
mkdir -p "$DEST"
count=0
for skill_dir in "$PROJECT"/*/; do
  [[ -f "${skill_dir}SKILL.md" ]] || continue
  name="$(basename "$skill_dir")"
  out="$DEST/$name"
  mkdir -p "$out"
  cp "$skill_dir/SKILL.md" "$out/SKILL.md"
  [[ -d "${skill_dir}references" ]] && mkdir -p "$out/references" && cp -R "${skill_dir}references/." "$out/references/"
  [[ -d "${skill_dir}tests" ]] && mkdir -p "$out/tests" && cp -R "${skill_dir}tests/." "$out/tests/"
  [[ -d "${skill_dir}reports" ]] && mkdir -p "$out/reports" && cp -R "${skill_dir}reports/." "$out/reports/"
  for ref in reference.md FORGE_FACTORY_DIRECTORY.md NODE_*.md; do
    [[ -f "${skill_dir}${ref}" ]] && cp "${skill_dir}${ref}" "$out/${ref}"
  done
  count=$((count + 1))
done

bash "$ROOT/scripts/write-cursor-skills-index-v1.sh" || fail "skills index write failed"

echo "OK: sync-all-cursor-skills-v1 — ${count} project skills mirrored to ${DEST}"
