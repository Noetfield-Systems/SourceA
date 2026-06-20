#!/usr/bin/env bash
# Agent skills registry — all registered SKILL.md exist + sync script runnable
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REG="$ROOT/agent-skills/REGISTRY_LOCKED_v1.json"
test -f "$REG"

python3 <<'PY'
import json
import subprocess
import sys
from pathlib import Path

root = Path(".")
reg = json.loads((root / "agent-skills/REGISTRY_LOCKED_v1.json").read_text(encoding="utf-8"))
errors = []
required_agents = {"sourcea_worker", "sourcea_brain"}
seen_agents = set()

for row in list(reg.get("shared") or []) + list(reg.get("agents") or []):
    rel = row.get("path") or ""
    src = root / "agent-skills" / rel
    if not src.is_file():
        errors.append(f"missing: {src}")
        continue
    text = src.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"no frontmatter: {src}")
    if "name:" not in text.split("---")[1]:
        errors.append(f"no name in frontmatter: {src}")
    if "description:" not in text.split("---")[1]:
        errors.append(f"no description: {src}")
    aid = row.get("agent_id") or row.get("id")
    if aid:
        seen_agents.add(aid)

for aid in required_agents - seen_agents:
    errors.append(f"required agent missing from registry: {aid}")

worker = root / "agent-skills/sourcea_worker/SKILL.md"
if worker.is_file():
    w = worker.read_text(encoding="utf-8")
    for needle in ("WORKER_ROUND_REPORT", "goal1_lane_broker", "REGISTRY_DRAIN"):
        if needle not in w:
            errors.append(f"worker skill missing {needle}")

if errors:
    print("FAIL: validate-agent-skills-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: validate-agent-skills-v1 · agents={len(reg.get('agents') or [])} shared={len(reg.get('shared') or [])}")
PY

bash "$ROOT/scripts/sync-cursor-agent-skills.sh" >/dev/null
test -f "$HOME/.cursor/skills/sina-sourcea-worker/SKILL.md"
test -f "$ROOT/.cursor/skills/sina-sourcea-worker/SKILL.md"
echo "OK: sync installed sina-sourcea-worker (user + project)"
