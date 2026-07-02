#!/usr/bin/env bash
# Sync SourceA agent-skills → ~/.cursor/skills/sina-* and SourceA/.cursor/skills (project)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${HOME}/.cursor/skills"
PROJECT_SKILLS="${ROOT}/.cursor/skills"
REG="${ROOT}/agent-skills/REGISTRY_LOCKED_v1.json"

mkdir -p "$DEST" "$PROJECT_SKILLS"
PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"

"$PY" << PY
import json, shutil
from pathlib import Path

root = Path("${ROOT}")
dest = Path("${DEST}")
proj = Path("${PROJECT_SKILLS}")
reg = json.loads(Path("${REG}").read_text(encoding="utf-8"))
rows = list(reg.get("shared") or []) + list(reg.get("agents") or [])
# All shared + core SourceA agents → project .cursor/skills (factory routine)
project_mirror_names = {
    "sina-sourcea-worker", "sina-sourcea-brain",
    "sina-research-intake", "sina-registry-drain", "sina-conscious-recovery",
    "sina-narrative-translator",
    "truth-projection", "anti-staleness-machine",
}

for row in rows:
    rel = row["path"]
    src = root / "agent-skills" / rel
    name = row.get("cursor_name") or row.get("agent_id")
    if not src.is_file():
        print(f"SKIP missing: {src}")
        continue
    out_dir = dest / name
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out_dir / "SKILL.md")
    ref = src.parent / "reference.md"
    if ref.is_file():
        shutil.copy2(ref, out_dir / "reference.md")
    print(f"OK user: {name}")
    aid = row.get("agent_id") or row.get("id") or ""
    if aid in ("sourcea_worker", "sourcea_brain") or name in project_mirror_names:
        pdir = proj / name
        pdir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, pdir / "SKILL.md")
        if ref.is_file():
            shutil.copy2(ref, pdir / "reference.md")
        print(f"OK project: {name}")

print(f"Done — user skills: {dest}")
print(f"Done — project skills: {proj}")
PY
