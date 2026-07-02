#!/usr/bin/env python3
"""Emit data/sourcea-cursor-skills-index-v1.json from .cursor/skills/."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / ".cursor/skills"


def main() -> None:
    skills = []
    for d in sorted(PROJECT.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        name = d.name
        for line in text.splitlines()[:20]:
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
                break
        skills.append(
            {
                "id": d.name,
                "name": name,
                "path": f".cursor/skills/{d.name}/SKILL.md",
                "user_path": f"~/.cursor/skills/{d.name}/SKILL.md",
            }
        )

    row = {
        "schema": "sourcea-cursor-skills-index-v1",
        "version": "1.1.0",
        "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skills_root": ".cursor/skills",
        "user_skills_root": "~/.cursor/skills",
        "sync_script": "scripts/sync-all-cursor-skills-v1.sh",
        "skill_count": len(skills),
        "skills": skills,
    }
    out = ROOT / "data/sourcea-cursor-skills-index-v1.json"
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(f"OK index: {len(skills)} skills → {out}")


if __name__ == "__main__":
    main()
