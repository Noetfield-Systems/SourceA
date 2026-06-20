#!/usr/bin/env python3
"""Create loop-suggestions-100 + loop-pack-10 for seven77 and noetfield_cloud if missing."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from loop_pack_registry import PACKS, pack_paths


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_pack(pack_id: str, product: str, repo: str, thread: str, goal: str, note: str, intents: list[str]) -> None:
    if len(intents) != 100:
        raise ValueError(f"{pack_id}: need 100 intents")
    _cat, pack_path, spec = pack_paths(pack_id)
    if not spec:
        raise ValueError(f"unknown pack {pack_id}")
    root = pack_path.parent.parent if pack_path else Path(spec["root"])
    if not root.is_dir():
        root = Path(spec["root"])
    prompts = root / "prompts"
    prompts.mkdir(parents=True, exist_ok=True)
    suggestions = []
    for i, intent in enumerate(intents, start=1):
        suggestions.append({
            "id": i,
            "category": pack_id,
            "category_label": product,
            "title": intent[:72] + ("…" if len(intent) > 72 else ""),
            "intent": intent,
            "thread": thread,
            "repo": repo,
            "workspace": str(root),
            "source": f"{pack_id}_catalog",
        })
    catalog = {
        "schema": "loop-suggestions-catalog.v1",
        "product": product,
        "repo": repo,
        "thread": thread,
        "count": 100,
        "suggestions": suggestions,
        "updated_at": _ts(),
    }
    (prompts / "loop-suggestions-100.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pack10 = []
    for step, s in enumerate(suggestions[:9], start=1):
        pack10.append({**s, "step": step, "loop_round": step})
    pack10.append({
        **suggestions[9],
        "step": 10,
        "loop_round": 10,
        "title": "Loop closeout — Submit round in Sina Command",
        "intent": "Round 10: summarize ship/ops state; founder Submit round in app — no Terminal",
    })
    pack = {
        "schema": "loop-pack-10.v1",
        "product": product,
        "pack_id": pack_id,
        "goal_default": goal,
        "author_note": note,
        "catalog": "loop-suggestions-100.json",
        "suggestions": pack10,
        "updated_at": _ts(),
    }
    if pack_id == "noetfield_cloud":
        pack["workspace_primary"] = str(root)
        pack["workspace_forbidden"] = [str(Path.home() / "Desktop/Noetfield-All-Documents")]
    (prompts / "loop-pack-10-active.json").write_text(
        json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _fill_100(base: list[str]) -> list[str]:
    out = []
    while len(out) < 100:
        for b in base:
            if len(out) >= 100:
                break
            out.append(b.replace("{n}", str(len(out) + 1)))
    return out[:100]


def bootstrap_missing() -> dict:
    created = []
    nf_cloud_intents = _fill_100([
        "SESSION: workspace MUST be ~/Desktop/Noetfield only — never edit Noetfield-All-Documents",
        "Read README + ship status — summarize public repo purpose",
        "Check .github/workflows — list CI jobs and last-known status",
        "vercel.json / deploy config — what is production URL?",
        "Compare cloud repo vs local SSOT — what must NOT be copied from local folder",
        "Open issue / drift — one doc fix for deploy instructions (no founder Terminal)",
        "AGENT_LOOP_ACTIVATION.md — confirm founder uses Agent loop pack button",
        "Health/smoke: request Actions one-tap for deploy verify (agent review if missing)",
        "Tag release checklist stub — version, changelog, founder clicks only",
        "Round {n}: cloud ship hygiene — docs, CI, or deploy artifact",
    ])
    seven77_intents = _fill_100([
        "Read os/plan.json — restate 3 next_tasks for founder",
        "Gate 0: ops/gate0-week1-execution.md — one outreach item status",
        "C3: translation sprint — admin queue / contribution_ledger sanity",
        "web/ health route — document expected adminRead behavior",
        "Supabase migrations list — newest 3 filenames + purpose",
        "Vercel deploy:prod-close — what founder should tap in Actions (not npm in Terminal)",
        "docs/c1-ops-close.md — open items table",
        "guild stats / showcase — one metric founder can see on Live products",
        "SEVEN77 vault naming — confirm no secrets in repo",
        "Round {n}: 777 web ops — gate0, C3, or deploy evidence file",
    ])
    specs = [
        ("noetfield_cloud", "Noetfield cloud ship", "noetfield_cloud", "noetfield", "THREAD-PORTFOLIO",
         "Noetfield CLOUD repo only (Desktop/Noetfield): GitHub ship, CI, Vercel — never edit Noetfield-All-Documents.",
         "Cloud ship pack · never touch local SSOT folder",
         nf_cloud_intents),
        ("seven77", "The 777 Foundation", "seven77", "seven77", "THREAD-PORTFOLIO",
         "777 Foundation: Gate 0, C3 translation cohort, web+Supabase+Vercel — founder uses Actions not Terminal.",
         "777 ops pack · gate0 + C3 + deploy",
         seven77_intents),
    ]
    for pack_id, product, pid, repo, thread, goal, note, intents in specs:
        _c, pack_p, _ = pack_paths(pack_id)
        if pack_p and pack_p.is_file():
            continue
        _write_pack(pack_id, product, repo, thread, goal, note, intents)
        created.append(pack_id)
    return {"ok": True, "created": created}


if __name__ == "__main__":
    print(bootstrap_missing())
