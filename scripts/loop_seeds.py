#!/usr/bin/env python3
"""10 prompt suggestions before loop — portfolio packs + executing agent override."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from loop_pack_registry import PACKS, pack_paths  # noqa: E402

SEED_PATH = Path.home() / ".sina" / "loop-seed-suggestions.json"
LOOP_CONFIG_PATH = Path.home() / ".sina" / "loop-config.json"
SOURCE_A = Path(__file__).resolve().parents[1]


def _load_file() -> dict | None:
    if not SEED_PATH.is_file():
        return None
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def _load_loop_config() -> dict:
    if not LOOP_CONFIG_PATH.is_file():
        return {}
    try:
        return json.loads(LOOP_CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_pack_file(pack_id: str) -> dict | None:
    _catalog, pack_path, _spec = pack_paths(pack_id)
    if not pack_path or not pack_path.is_file():
        return None
    return json.loads(pack_path.read_text(encoding="utf-8"))


def _load_catalog(pack_id: str) -> dict | None:
    catalog_path, _pack_path, _spec = pack_paths(pack_id)
    if not catalog_path or not catalog_path.is_file():
        return None
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def activate_seed_pack(pack_id: str, *, sync_ui_file: bool = True) -> dict:
    """Activate a registered pack (ai_dev_bridge_os | trustfield | virlux)."""
    spec = PACKS.get(pack_id)
    if not spec:
        return {"ok": False, "error": f"unknown pack: {pack_id}. Choose: {', '.join(PACKS)}"}
    pack = _load_pack_file(pack_id)
    if not pack or not pack.get("suggestions"):
        _c, pack_path, _ = pack_paths(pack_id)
        return {"ok": False, "error": f"missing pack file: {pack_path}"}
    _cat, _pack_p, _ = pack_paths(pack_id)
    cfg = {
        "active_pack": pack_id,
        "goal_default": pack.get("goal_default", ""),
        "catalog_path": str(_cat) if _cat else "",
        "pack_path": str(_pack_p) if _pack_p else "",
        "thread": spec["thread"],
        "repo": spec["repo"],
        "label": spec["label"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if spec.get("workspace_rule"):
        cfg["workspace_rule"] = spec["workspace_rule"]
        cfg["workspace_primary"] = spec.get("root") or pack.get("workspace_primary", "")
        cfg["workspace_forbidden"] = spec.get("workspace_forbidden", "")
        cfg["cursor_workspace"] = spec.get("cursor_workspace", "")
    try:
        from agent_workspace_registry import AGENT_WORKSPACES  # noqa: WPS433

        for ws_spec in AGENT_WORKSPACES:
            if ws_spec.get("pack_id") == pack_id:
                cfg["active_workspace"] = ws_spec["id"]
                break
    except Exception:
        pass
    LOOP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOOP_CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    rows = []
    for i, s in enumerate(pack["suggestions"][:10], start=1):
        rows.append({
            "step": s.get("step", i),
            "title": (s.get("title") or f"Step {i}")[:120],
            "intent": (s.get("intent") or "")[:500],
            "thread": s.get("thread", spec["thread"]),
            "repo": s.get("repo", spec["repo"]),
            "source": spec["source"],
            "loop_round": s.get("loop_round", i),
            "catalog_id": s.get("id"),
        })
    note = pack.get("author_note", "")
    if sync_ui_file:
        set_seed_suggestions(rows, author_note=note, source=spec["source"])
    cat = _load_catalog(pack_id)
    return {
        "ok": True,
        "pack_id": pack_id,
        "count": len(rows),
        "catalog_size": (cat or {}).get("count", 100),
        "goal_default": pack.get("goal_default"),
        "message": f"{spec['label']} pack active on private agent page",
    }


def activate_devbridge_seed_pack(*, sync_ui_file: bool = True) -> dict:
    return activate_seed_pack("ai_dev_bridge_os", sync_ui_file=sync_ui_file)


def load_devbridge_catalog() -> dict | None:
    return _load_catalog("ai_dev_bridge_os")


def _pack_seeds_payload(pack_id: str) -> dict | None:
    pack = _load_pack_file(pack_id)
    if not pack or not pack.get("suggestions"):
        return None
    spec = PACKS[pack_id]
    cat = _load_catalog(pack_id)
    return {
        "seed_suggestions": pack["suggestions"][:10],
        "seed_source": spec["source"],
        "seed_updated_at": pack.get("updated_at"),
        "seed_author_note": pack.get("author_note", ""),
        "seed_catalog_size": (cat or {}).get("count", 100),
        "seed_catalog_path": str(pack_paths(pack_id)[0]),
        "seed_goal_default": pack.get("goal_default", ""),
        "seed_pack_label": spec["label"],
    }


def build_seeds_from_payload(payload: dict) -> list[dict]:
    """Heuristic 10 steps from live command center — executing agent may override via file."""
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    p0 = founder.get("p0") or {}
    seeds: list[dict] = []
    n = 0

    def add(title: str, intent: str, thread: str | None = None, repo: str | None = None):
        nonlocal n
        n += 1
        seeds.append({
            "step": n,
            "title": title[:120],
            "intent": intent[:400],
            "thread": thread,
            "repo": repo,
            "source": "locked_plans",
        })

    add(
        "Confirm P0 RunReceipt scope",
        f"Thread {p0.get('thread', 'THREAD-FACTORY')}: {p0.get('next_action', 'wire artifacts')}",
        p0.get("thread"),
    )
    for card in (founder.get("ops_cards") or [])[:3]:
        add(card.get("title", "Ops"), card.get("action", ""), None)
    for duty in (founder.get("must_do_today") or [])[:2]:
        add("Must-do today", duty, None)
    for plan in (payload.get("bowl") or {}).get("parallel_plans") or []:
        if n >= 8:
            break
        if plan.get("status") == "active" or (plan.get("progress_pct") or 0) < 100:
            add(
                plan.get("title", plan.get("id", "Program"))[:80],
                plan.get("next_action") or plan.get("hook", "")[:200],
                plan.get("thread"),
            )
    for prod in (payload.get("live_products") or [])[:2]:
        if n >= 10:
            break
        if prod.get("open_url"):
            add(f"Live · {prod.get('title', 'product')}", prod.get("next_action") or "Verify live URL", None)

    while n < 10:
        add(
            f"Round {n + 1} follow-up",
            "Continue the founder goal after prior rounds — Advisor will refine on trigger.",
            None,
        )
    return seeds[:10]


def portfolio_packs_meta() -> list[dict]:
    """Legacy pack metadata (API compat); founder UI uses Private agents pages."""
    rows = []
    for pack_id, spec in PACKS.items():
        _cat, pack_path, _ = pack_paths(pack_id)
        rows.append({
            "id": pack_id,
            "label": spec["label"],
            "hint": (spec.get("workspace_rule") or "")[:160],
            "ready": bool(pack_path and pack_path.is_file()),
        })
    return rows


def _founder_law_fields() -> dict:
    from founder_law import founder_law_payload  # noqa: WPS433

    return founder_law_payload()


def seeds_payload(payload: dict | None = None) -> dict:
    cfg = _load_loop_config()
    ws_id = cfg.get("active_workspace")
    if ws_id:
        try:
            from agent_workspace_registry import get_workspace  # noqa: WPS433

            spec = get_workspace(ws_id)
            if spec and not spec.get("pack_id"):
                base = {
                    "seed_suggestions": [],
                    "seed_source": ws_id,
                    "seed_author_note": f"{spec['label']} — no 10-pack on this private page",
                    "seed_updated_at": None,
                }
                base.update(_founder_law_fields())
                return base
        except Exception:
            pass
    pack_id = cfg.get("active_pack")
    if pack_id and pack_id in PACKS:
        out = _pack_seeds_payload(pack_id)
        if out:
            out.update(_founder_law_fields())
            return out
    file_data = _load_file()
    if file_data and file_data.get("suggestions"):
        items = file_data["suggestions"][:10]
        out = {
            "seed_suggestions": items,
            "seed_source": file_data.get("source", "executing_agent"),
            "seed_updated_at": file_data.get("updated_at"),
            "seed_author_note": file_data.get("author_note", ""),
        }
        src = file_data.get("source")
        pid = src if src in PACKS else ("noetfield_local" if src == "noetfield_local" else None)
        if pid in PACKS:
            cat = _load_catalog(pid)
            if pid:
                out["seed_catalog_size"] = (cat or {}).get("count", 100)
                out["seed_catalog_path"] = str(pack_paths(pid)[0])
                out["seed_pack_label"] = PACKS[pid]["label"]
        out.update(_founder_law_fields())
        return out
    if payload:
        items = build_seeds_from_payload(payload)
        return {
            "seed_suggestions": items,
            "seed_source": "locked_plans",
            "seed_updated_at": None,
            "seed_author_note": "From P0, ops, programs, live products — refresh panel to update",
            **_founder_law_fields(),
        }
    base = {"seed_suggestions": [], "seed_source": None}
    base.update(_founder_law_fields())
    return base


def clear_seed_ui_file(*, source: str = "", author_note: str = "") -> None:
    """No-pack workspace — empty global seed file so loop_payload does not leak prior pack."""
    data = {
        "suggestions": [],
        "source": source or "none",
        "author_note": author_note[:2000],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def clear_active_pack_in_config(workspace_id: str) -> dict:
    """Drop pack activation; keep active_workspace only."""
    cfg = _load_loop_config()
    cfg["active_workspace"] = workspace_id
    for key in (
        "active_pack",
        "goal_default",
        "catalog_path",
        "pack_path",
        "thread",
        "repo",
        "label",
        "workspace_rule",
        "workspace_primary",
        "workspace_forbidden",
        "cursor_workspace",
    ):
        cfg.pop(key, None)
    cfg["updated_at"] = datetime.now(timezone.utc).isoformat()
    LOOP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOOP_CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return cfg


def set_seed_suggestions(
    suggestions: list[dict],
    *,
    author_note: str = "",
    source: str = "executing_agent",
) -> dict:
    if len(suggestions) < 1:
        return {"ok": False, "error": "need at least 1 suggestion"}
    rows = []
    for i, s in enumerate(suggestions[:10], start=1):
        rows.append({
            "step": s.get("step", i),
            "title": (s.get("title") or f"Step {i}")[:120],
            "intent": (s.get("intent") or s.get("text", ""))[:500],
            "thread": s.get("thread"),
            "repo": s.get("repo"),
            "source": source,
        })
    data = {
        "suggestions": rows,
        "source": source,
        "author_note": author_note[:2000],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"ok": True, "count": len(rows), "message": "Seed suggestions saved for private agent page UI"}
