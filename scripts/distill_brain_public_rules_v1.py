#!/usr/bin/env python3
"""Distill public Brain rules from SSOT — rule-aware retrieval, not hardcoded prompt."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from brain_chat_knowledge_lib_v1 import chunk_text, strip_secrets  # noqa: E402

RULES_JSON = ROOT / "data" / "brain-public-rules-v1.json"
POSITIONING = ROOT / "sites/SourceA-landing/green-unified/data/sourcea-positioning-v1.json"
POSITIONING_LAW = ROOT / "docs/SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md"
OUT = ROOT / "data/chatbot-knowledge/rules/brain-public-rules.md"


def frontmatter() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"---\nlane: rules\nkind: rule\nupdated: {now}\n"
        f"source_path: data/brain-public-rules-v1.json\npublic: true\npinned: true\n---\n\n"
    )


def main() -> int:
    rules = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    pos = json.loads(POSITIONING.read_text(encoding="utf-8")) if POSITIONING.is_file() else {}
    law = strip_secrets(POSITIONING_LAW.read_text(encoding="utf-8")) if POSITIONING_LAW.is_file() else ""

    lines = [frontmatter(), "# Brain public rules (live SSOT)", ""]
    lines.append(f"## Identity\n{rules['identity']['role']}")
    lines.append(f"\n## One line\n{rules.get('one_line') or pos.get('one_line', '')}")
    lines.append("\n## Conversation rules")
    for r in rules.get("conversation_rules", []):
        lines.append(f"- **{r['id']}**: {r['rule']}")
    lines.append("\n## Primary CTAs")
    for c in rules.get("primary_ctas", []):
        lines.append(f"- [{c['label']}]({c['url']})")
    if pos:
        lines.append(f"\n## Positioning SSOT\n- one_line: {pos.get('one_line')}")
        lines.append(f"- primary_cta: {pos.get('primary_cta')} ({pos.get('primary_cta_label')})")
        lines.append(f"- agentic_first_law: {pos.get('agentic_first_law')}")
    if law:
        for sec in chunk_text(law, max_chars=3000)[:2]:
            lines.append(f"\n{sec}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(lines).strip() + "\n"
    OUT.write_text(body, encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(OUT.relative_to(ROOT)), "chars": len(body)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
