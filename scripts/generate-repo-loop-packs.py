#!/usr/bin/env python3
"""Generate loop-suggestions-100.json + loop-pack-10-active.json for portfolio repos."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_pack(root: Path, product: str, repo: str, thread: str, goal: str, author_note: str, categories: list) -> int:
    prompts = root / "prompts"
    prompts.mkdir(parents=True, exist_ok=True)
    suggestions = []
    sid = 0
    for cat_title, cat, items in categories:
        for intent in items:
            sid += 1
            title = intent[:72] + ("…" if len(intent) > 72 else "")
            suggestions.append({
                "id": sid,
                "category": cat,
                "category_label": cat_title,
                "title": title,
                "intent": intent,
                "thread": thread,
                "repo": repo,
                "workspace": str(root),
                "source": f"{repo}_catalog",
            })
    if len(suggestions) != 100:
        raise ValueError(f"{product}: expected 100 suggestions, got {len(suggestions)}")
    ts = datetime.now(timezone.utc).isoformat()
    catalog = {
        "schema": "loop-suggestions-catalog.v1",
        "product": product,
        "repo": repo,
        "thread": thread,
        "count": 100,
        "suggestions": suggestions,
        "updated_at": ts,
    }
    (prompts / "loop-suggestions-100.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pack10 = []
    for idx, (cat_title, cat, _items) in enumerate(categories):
        s = next(x for x in suggestions if x["category"] == cat)
        pack10.append({**s, "step": idx + 1, "loop_round": idx + 1})
    pack10[9] = {
        **suggestions[-1],
        "step": 10,
        "loop_round": 10,
        "title": "Loop closeout — Worker chat summary",
        "intent": "Round closeout: one-line summary + full body in Worker chat",
    }
    pack = {
        "schema": "loop-pack-10.v1",
        "product": product,
        "goal_default": goal,
        "author_note": author_note,
        "catalog": "loop-suggestions-100.json",
        "suggestions": pack10,
        "updated_at": ts,
    }
    (prompts / "loop-pack-10-active.json").write_text(
        json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    readme = prompts / "README.md"
    if not readme.is_file():
        readme.write_text(
            f"# {product} — loop prompts\n\n"
            f"- `loop-suggestions-100.json` — full library\n"
            f"- `loop-pack-10-active.json` — legacy 10-round pack (archive)\n\n"
            f"Activate (founder): RUN INBOX in Worker chat — legacy /legacy/ loop if ASF enables.\n",
            encoding="utf-8",
        )
    return 100


# TrustField + VIRLUX category data loaded in main via import from strings file - keep inline for single file
