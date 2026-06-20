#!/usr/bin/env python3
"""
Private workspace per Sina Command agent — governance, real needs, loop packs.

Each agent: ~/.sina/agent-workspaces/<id>/ + <repo>/.sina-agent/
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from agent_workspace_registry import AGENT_WORKSPACES, GOVERNANCE_VERSION, get_workspace
from loop_pack_registry import pack_paths

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
WORKSPACES_ROOT = SINA_HOME / "agent-workspaces"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _governance_md(spec: dict, private_root: Path) -> str:
    forbidden = spec.get("forbidden_roots") or []
    forb = "\n".join(f"- `{p}`" for p in forbidden) or "- (none besides SourceA for non-maintainers)"
    needs = "\n".join(f"- {n}" for n in spec.get("real_needs") or [])
    arts = "\n".join(f"- `{a}`" for a in spec.get("artifacts") or [])
    may = spec.get("may_edit_source_a")
    edit_block = (
        "You **may** edit `~/Desktop/SourceA` when ASF approves Command changes.\n"
        if may
        else "**Never** edit `~/Desktop/SourceA` — use `POST /api/agent-review` or Backlog → Agent reports.\n"
    )
    return f"""# GOVERNANCE_LOCKED — {spec["label"]}

**Version:** {GOVERNANCE_VERSION}  
**Agent id:** `{spec["id"]}`  
**Thread:** {spec.get("thread", "")} · **Lane:** {spec.get("lane", "")} · **Plane:** {spec.get("plane", "")}

## Focus

{spec.get("governance_focus", "")}

## Code vs private scratch

| Zone | Path |
|------|------|
| **Product code** | `{spec["repo_root"]}` |
| **Private workspace** | `{private_root}` |

## Forbidden roots (do not edit)

{forb}

## Real needs (this agent)

{needs}

## Key artifacts

{arts}

## Daily ops (founder — Worker chat)

**Primary:** Cursor **{spec["label"]}** chat — **RUN INBOX** one sa/turn.  
**Optional glance:** Hub H1 `http://127.0.0.1:13020/` · Machine Hub H2 `/machines/` · Safety one-tap.  
**Command brand:** DELETED — Hub only (no `/legacy/` · no monolith).

{spec.get("command_tabs", "")}

## Edit lock

{edit_block}

## Founder law

Never ask the founder to run Terminal. Executor runs shell; founder uses Worker chat + optional Worker Hub one-tap Safety.

## Cursor

Open folder: **{spec.get("cursor_workspace_hint", "")}**

Law: `~/Desktop/SourceA/brain-os/law/SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md`

## Workspace vault — app middle layer (mandatory)

**Law:** `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md`

Worker Hub vault API gathers work deposits when legacy UI is open. Every session:

1. **Deposit documents** — reports, deliverables, evidence (Private page → Workspace vault)
2. **Register repo refs** — paths to files you shipped in `{spec["repo_root"]}`
3. **Log activity** — what you started and finished (`activity.jsonl`)
4. Loop rounds and Mind Share **auto-deposit** — still log manual work

Storage: `{private_root}/vault/` · API: `POST /api/workspace-vault`

**Never** leave significant work only in Cursor chat or Finder.

## Council, Mind Share & reporting (never edit SourceA)

- **Mind Share:** Council Room → post **insight / opinion / procedure** — all agents read shared rules + compare repo lenses (`AGENT_MIND_SHARE_LOCKED_v1.md`).
- **Paradox:** Flag divergent opinions in Council — compare with other agents before assuming your lane law is universal.
- **Hub/app changes:** **Backlog → Agent reports** only — not code edits.
- **Council Room:** `AGENT_COUNCIL_ROOM_LOCKED_v1.md` · **Unification:** `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md`
{_layer_a_block(spec)}
"""


def _layer_a_block(spec: dict) -> str:
    if not spec.get("layer_a_training"):
        return ""
    return """
## Layer A (Personal Database)

Copy agents train on **Layer A** — `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/data/`.

1. Read `~/Desktop/SourceA/brain-os/law/SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md`
2. Use Layer A disk paths — cite entry `id` when stating founder truth (legacy Personal DB tab archived)
3. One loop round: reference `data/L4-agents/` + one promoted L2 entry

Never invent founder facts not in Layer A.
"""


def _cursor_rule(spec: dict, private_root: Path) -> str:
    forbidden = spec.get("forbidden_roots") or []
    extra = "".join(f"\n- **Forbidden:** `{p}`" for p in forbidden)
    may = spec.get("may_edit_source_a")
    source_a = (
        "- You **may** edit `~/Desktop/SourceA` for approved Command work.\n"
        if may
        else "- **Never** edit `~/Desktop/SourceA`.\n"
    )
    return f"""---
description: Governance — {spec["label"]} ({spec["id"]})
alwaysApply: true
---

# {spec["id"]} — workspace governance

Read `{private_root}/GOVERNANCE_LOCKED.md` every session.

- **Code:** `{spec["repo_root"]}`{extra}
- **Private:** `{private_root}`
{source_a}
- **Founder:** one-tap Actions only — never Terminal instructions.
- **10-pack loop:** RUN INBOX in Cursor **{spec["label"]}** — Hub H1/H2 optional glance only.
"""


def _readonly_mdc(spec: dict, private_root: Path) -> str:
    """Repo-root Sina Command read-only rule (portfolio repos)."""
    return f"""---
description: Do not edit Sina Command (SourceA) — report via API only
alwaysApply: true
---

# Sina Command — read only

Never modify `~/Desktop/SourceA/` or Sina Command UI/scripts from this chat.

**Private workspace:** `{private_root}/` (notes, INBOX) — product code in `{spec["repo_root"]}` only. Marker: `.sina-agent/README.md`.

**Founder law:** No Terminal for founder — add **Actions** one-tap or run commands yourself.

Report app bugs: `POST /api/agent-review`. Hub code: SourceA Worker chat + ASF only.
"""


def _semej_readonly_mdc(private_root: Path) -> str:
    return f"""---
description: SEMEJ — SourceA read-only; browser automation only
alwaysApply: true
---

# SEMEJ — no SourceA code edits

**Never** modify `~/Desktop/SourceA/**` (hub, panel, scripts). Use **Backlog → Agent reports** if Command is broken.

**Allowed:** `~/.sina/semej-*`, `{private_root}/`, Chrome/Playwright automation via SEMEJ tab.

**Founder:** one-tap Actions only — never Terminal.
"""


def _repo_marker(spec: dict, private_root: Path) -> str:
    return f"""# `.sina-agent` — {spec["label"]}

**Agent id:** `{spec["id"]}`  
**Private workspace:** `{private_root}`  
**Governance:** `{private_root}/GOVERNANCE_LOCKED.md`

## Founder (Worker chat)

**RUN INBOX** in Cursor for this agent. Hub H1 `/` · H2 `/machines/` — Command deleted.

## Agent rules

1. Work in repo for product code; private folder for INBOX + notes.  
2. Follow GOVERNANCE_LOCKED.md — forbidden roots are hard limits.  
3. No founder Terminal — request Actions buttons via agent review.  
"""


def ensure_workspace(agent_id: str) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}

    private_root = WORKSPACES_ROOT / agent_id
    private_root.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    gov = private_root / "GOVERNANCE_LOCKED.md"
    gov.write_text(_governance_md(spec, private_root), encoding="utf-8")

    needs_file = private_root / "NEEDS.md"
    needs_file.write_text(
        f"# Real needs — {spec['label']}\n\n"
        + "\n".join(f"- {n}" for n in spec.get("real_needs") or [])
        + "\n",
        encoding="utf-8",
    )

    inbox = private_root / "INBOX.md"
    if not inbox.is_file():
        inbox.write_text(
            f"# INBOX — {spec['label']}\n\n| Added | Task | Status |\n|-------|------|--------|\n"
            f"| {date} | Governance v{GOVERNANCE_VERSION} applied | done |\n",
            encoding="utf-8",
        )

    notes = private_root / "notes.md"
    if not notes.is_file():
        notes.write_text(f"# Notes — {spec['label']}\n\nPrivate scratch — not in repo unless you promote.\n", encoding="utf-8")

    rules_dir = private_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "workspace-governance.mdc").write_text(_cursor_rule(spec, private_root), encoding="utf-8")

    repo_root = Path(spec["repo_root"])
    agent_id = spec["id"]
    if repo_root.is_dir():
        marker = repo_root / ".sina-agent"
        marker.mkdir(parents=True, exist_ok=True)
        (marker / "README.md").write_text(_repo_marker(spec, private_root), encoding="utf-8")
        repo_rules = marker / ".cursor" / "rules"
        repo_rules.mkdir(parents=True, exist_ok=True)
        (repo_rules / "workspace-governance.mdc").write_text(_cursor_rule(spec, private_root), encoding="utf-8")

        if not spec.get("may_edit_source_a"):
            root_rules = repo_root / ".cursor" / "rules"
            root_rules.mkdir(parents=True, exist_ok=True)
            if agent_id == "semej":
                (root_rules / "sina-command-readonly.mdc").write_text(
                    _semej_readonly_mdc(private_root), encoding="utf-8"
                )
            elif repo_root.resolve() != SOURCE_A.resolve():
                (root_rules / "sina-command-readonly.mdc").write_text(
                    _readonly_mdc(spec, private_root), encoding="utf-8"
                )

    (private_root / "manifest.json").write_text(
        json.dumps(
            {
                "agent_id": agent_id,
                "label": spec["label"],
                "repo_root": spec["repo_root"],
                "private_root": str(private_root),
                "pack_id": spec.get("pack_id"),
                "governance_version": GOVERNANCE_VERSION,
                "thread": spec.get("thread"),
                "lane": spec.get("lane"),
                "updated_at": _now(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    try:
        from agent_incident_system import ensure_agent_incident_files  # noqa: WPS433

        ensure_agent_incident_files(agent_id)
    except Exception:
        pass
    try:
        from agent_workspace_vault import ensure_vault  # noqa: WPS433

        ensure_vault(agent_id)
    except Exception:
        pass
    try:
        from agent_doc_tags import ensure_agent_doc_tag_standard  # noqa: WPS433

        ensure_agent_doc_tag_standard(agent_id, private_root)
    except Exception:
        pass
    smart_src = SOURCE_A / ".cursor" / "rules" / "agent-smart-judgment.mdc"
    if smart_src.is_file():
        (rules_dir / "agent-smart-judgment.mdc").write_text(
            smart_src.read_text(encoding="utf-8"), encoding="utf-8"
        )

    return {"ok": True, "agent_id": agent_id, "private_root": str(private_root)}


def ensure_all_workspaces() -> dict:
    try:
        from bootstrap_workspace_loop_packs import bootstrap_missing  # noqa: WPS433

        bootstrap_missing()
    except Exception:
        pass
    created = []
    for spec in AGENT_WORKSPACES:
        ensure_workspace(spec["id"])
        created.append(spec["id"])
    return {"ok": True, "agents": created}


def _preview_private_file(path: Path, *, limit: int = 1400) -> str:
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…"


def _private_scratch_preview(private_root: Path) -> dict:
    """Founder-facing snippets — workspace lives in Sina Command, not Finder."""
    inbox = _preview_private_file(private_root / "INBOX.md")
    notes = _preview_private_file(private_root / "notes.md")
    needs = _preview_private_file(private_root / "NEEDS.md", limit=800)
    return {
        "inbox_preview": inbox,
        "notes_preview": notes,
        "needs_preview": needs,
        "has_inbox": bool(inbox),
        "has_notes": bool(notes),
    }


def _workspace_id_for_pack(pack_id: str | None) -> str | None:
    if not pack_id:
        return None
    for spec in AGENT_WORKSPACES:
        if spec.get("pack_id") == pack_id:
            return spec["id"]
    return None


def loop_workspaces_payload() -> dict:
    """Private agent pages: all workspaces with embedded 10-pack prompts + governance."""
    from loop_seeds import _load_loop_config, _pack_seeds_payload  # noqa: WPS433

    ensure_all_workspaces()
    cfg = _load_loop_config()
    selected = cfg.get("active_workspace") or _workspace_id_for_pack(cfg.get("active_pack"))

    mind_rows: list[dict] = []
    try:
        from agent_council_room import _load_mind_share  # noqa: WPS433

        mind_rows = _load_mind_share()
    except Exception:
        mind_rows = []

    items = []
    for spec in AGENT_WORKSPACES:
        private_root = WORKSPACES_ROOT / spec["id"]
        pid = spec.get("pack_id")
        pack_ready = False
        pack_suggestions: list = []
        seed_catalog_size = 0
        seed_goal_default = ""
        seed_author_note = ""
        if pid:
            _c, pack_p, _ = pack_paths(pid)
            pack_ready = bool(pack_p and pack_p.is_file())
            pd = _pack_seeds_payload(pid)
            if pd:
                pack_suggestions = pd.get("seed_suggestions") or []
                seed_catalog_size = pd.get("seed_catalog_size") or 0
                seed_goal_default = pd.get("seed_goal_default") or ""
                seed_author_note = pd.get("seed_author_note") or ""
        forbidden = spec.get("forbidden_roots") or []
        from agent_governance_events import tail_events  # noqa: WPS433

        recent = tail_events(workspace_id=spec["id"], limit=3)
        scratch = _private_scratch_preview(private_root)
        incident = {}
        conflict = {}
        try:
            from agent_incident_system import agent_incident_summary  # noqa: WPS433

            incident = agent_incident_summary(spec["id"])
        except Exception:
            incident = {}
        try:
            from agent_conflict_room import agent_conflict_summary  # noqa: WPS433

            conflict = agent_conflict_summary(spec["id"])
        except Exception:
            conflict = {}
        vault = {}
        workspace_mirror = {}
        try:
            from agent_workspace_vault import vault_summary  # noqa: WPS433

            vault = vault_summary(spec["id"], doc_limit=6, activity_limit=8)
        except Exception:
            vault = {}
        try:
            from agent_workspace_mirror import workspace_mirror_payload  # noqa: WPS433

            workspace_mirror = workspace_mirror_payload(spec["id"], detail="summary")
        except Exception:
            workspace_mirror = {}
        agent_mind = [m for m in mind_rows if m.get("agent_id") == spec["id"]][:5]
        items.append(
            {
                **spec,
                "private_root": str(private_root),
                "private_ready": private_root.is_dir(),
                "incident": incident,
                "conflict": conflict,
                "vault": vault,
                "workspace_mirror": workspace_mirror,
                "mind_shares": agent_mind,
                **scratch,
                "pack_ready": pack_ready,
                "pack_suggestions": pack_suggestions,
                "seed_catalog_size": seed_catalog_size,
                "seed_goal_default": seed_goal_default,
                "seed_author_note": seed_author_note,
                "may_edit_source_a": bool(spec.get("may_edit_source_a")),
                "governance_path": str(private_root / "GOVERNANCE_LOCKED.md"),
                "governance_focus": spec.get("governance_focus", ""),
                "forbidden_summary": "; ".join(Path(p).name for p in forbidden[:2]),
                "forbidden_roots_full": list(forbidden),
                "governance_version": GOVERNANCE_VERSION,
                "recent_events": recent,
            }
        )
    if not selected and items:
        selected = next((w["id"] for w in items if w.get("pack_ready")), items[0]["id"])
    return {
        "loop_workspaces": items,
        "selected_workspace_id": selected,
        "workspace_count": len(items),
    }


def workspaces_payload() -> dict:
    ensure_all_workspaces()
    items = []
    for spec in AGENT_WORKSPACES:
        private_root = WORKSPACES_ROOT / spec["id"]
        pack_ready = False
        pid = spec.get("pack_id")
        if pid:
            _c, pack_p, _ = pack_paths(pid)
            pack_ready = bool(pack_p and pack_p.is_file())
        items.append(
            {
                **spec,
                "private_root": str(private_root),
                "private_ready": private_root.is_dir(),
                "pack_ready": pack_ready,
                "may_edit_source_a": bool(spec.get("may_edit_source_a")),
                "governance_path": str(private_root / "GOVERNANCE_LOCKED.md"),
            }
        )
    return {
        "ok": True,
        "built_at": _now(),
        "root": str(WORKSPACES_ROOT),
        "count": len(items),
        "workspaces": items,
        "governance_version": GOVERNANCE_VERSION,
        "tagline": "Each agent: governance rules, real needs, private scratch, loop pack — wired like portfolio peers.",
        "law_doc": "SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md",
    }


def select_loop_workspace(workspace_id: str, *, sync_ui_file: bool = True) -> dict:
    """Founder opened a private agent page — activate that agent's pack only (no stale pack leak)."""
    from loop_seeds import activate_seed_pack, clear_active_pack_in_config, clear_seed_ui_file  # noqa: WPS433

    spec = get_workspace(workspace_id)
    if not spec:
        return {"ok": False, "error": f"unknown workspace: {workspace_id}"}
    pack_id = spec.get("pack_id")
    if pack_id:
        result = activate_seed_pack(pack_id, sync_ui_file=sync_ui_file)
        if not result.get("ok"):
            return result
        out = {
            **result,
            "workspace_id": workspace_id,
            "message": f"{spec['label']} — private page active · 10 prompts on this page only",
        }
    else:
        clear_active_pack_in_config(workspace_id)
        if sync_ui_file:
            clear_seed_ui_file(
                source=workspace_id,
                author_note=f"{spec['label']} — no 10-pack; use custom goal or Backlog → Agent reports",
            )
        out = {
            "ok": True,
            "workspace_id": workspace_id,
            "pack_id": None,
            "count": 0,
            "message": f"{spec['label']} — private page · no 10-pack (custom goal or agent report)",
        }

    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "workspace_selected",
        workspace_id=workspace_id,
        detail=out.get("message", ""),
    )
    return out


def handle_workspace_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    if action == "select":
        return select_loop_workspace(
            body.get("workspace_id") or body.get("id") or "",
            sync_ui_file=body.get("sync_ui", True),
        )
    if action == "ensure":
        aid = body.get("agent_id") or body.get("id")
        if aid:
            return ensure_workspace(aid)
        return ensure_all_workspaces()
    return workspaces_payload()
