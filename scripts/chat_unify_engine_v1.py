#!/usr/bin/env python3
"""Chat Unify — independent multi-agent engine (not Forge Terminal motor).

Receipts: ~/.sina/chat-unify-engine/
API: POST /api/chat-unify-engine/v1
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENGINE_VERSION = "1.3.0"
ENGINE_SCHEMA = "chat-unify-engine-v1"
SINA = Path.home() / ".sina"
ENGINE_DIR = SINA / "chat-unify-engine"
THREAD_DIR = ENGINE_DIR / "threads"
RECEIPT_DIR = ENGINE_DIR / "receipts"

DEFAULT_AGENTS = [
    {"id": "planner", "role": "planner", "description": "Break founder intent into bounded tasks", "model_ref": "planner"},
    {"id": "builder", "role": "builder", "description": "Execute approved tasks in workspace jail", "model_ref": "executor"},
    {"id": "verifier", "role": "verifier", "description": "Verify receipts and block fake-green", "model_ref": "verifier"},
]

MACHINES = [
    {"id": "home", "label": "Chat", "engine": "chat_unify_merge", "actions": ["paste", "verify", "unify", "save"]},
    {"id": "start", "label": "Start", "engine": "onboarding", "actions": ["guide"]},
    {"id": "forge", "label": "Prompt Forge", "engine": "prompt_forge", "actions": ["mission"]},
    {"id": "connect", "label": "Connect", "engine": "integrations", "actions": ["hook", "manifest"]},
    {"id": "founder", "label": "Verify & Act", "engine": "founder_loop", "actions": ["verify", "gate"]},
    {"id": "ord", "label": "Audit Trail", "engine": "ord_loop", "actions": ["trace", "atoms"]},
    {"id": "form", "label": "Decisions", "engine": "form_official", "actions": ["submit", "picks"]},
    {"id": "api", "label": "Tasks", "engine": "api_station", "actions": ["queue", "dispatch"]},
    {"id": "hubpro", "label": "Operations", "engine": "hub_pro_skills", "actions": ["skills", "log"]},
    {"id": "proofpack", "label": "Proof Pack", "engine": "proof_pack", "actions": ["seal"]},
    {"id": "vocab", "label": "Vocabulary", "engine": "vocabulary", "actions": ["scan"]},
    {"id": "plan_registry", "label": "Plan Registry", "engine": "sourcea_plan_registry", "actions": ["count", "next_rows", "lookup"]},
    {"id": "intent_approval", "label": "Intent Approval", "engine": "founder_intent_approval", "actions": ["classify", "critic", "approve"]},
    {"id": "living-chat", "label": "Living chat", "engine": "chat_unify_engine", "actions": ["chat_turn", "multi_agent_run"]},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sourcea_root() -> Path:
    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (Path.home() / "Desktop" / "SourceA", Path(__file__).resolve().parents[1]):
        if (candidate / ".sourcea" / "agents.yaml").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


def _workspace_root(workspace_path: str | None) -> Path | None:
    if not workspace_path:
        return None
    p = Path(workspace_path).expanduser().resolve()
    if (p / ".sourcea" / "agents.yaml").is_file():
        return p
    return None


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    try:
        row = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return row if isinstance(row, dict) else {}


def _agent_file(root: Path, agent_id: str) -> Path:
    return root / ".sourcea" / "agents" / f"{agent_id}.yaml"


def list_agents(workspace_path: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspace_path) or _sourcea_root()
    rows: list[dict[str, Any]] = []
    try:
        from workspace_kernel_v2 import list_agents as ws_list  # noqa: WPS433

        row = ws_list(root)
        if row.get("ok") and row.get("agents"):
            rows = list(row["agents"])
    except Exception:
        rows = []
    if not rows:
        manifest = _load_yaml(root / ".sourcea" / "agents.yaml")
        agents = manifest.get("agents") if isinstance(manifest.get("agents"), dict) else {}
        for aid, meta in agents.items():
            if isinstance(meta, dict):
                rows.append({"id": aid, **meta})
    if not rows:
        rows = list(DEFAULT_AGENTS)
    return {"ok": True, "engine": ENGINE_SCHEMA, "agents": rows, "project_root": str(root)}


def _resolve_model(agent_id: str, workspace_path: str | None = None) -> tuple[str, str]:
    root = _workspace_root(workspace_path) or _sourcea_root()
    agents_row = list_agents(workspace_path)
    agents = {str(a.get("id")): a for a in agents_row.get("agents") or []}
    meta = agents.get(agent_id) or agents.get("builder") or DEFAULT_AGENTS[1]
    model_ref = str(meta.get("model_ref") or "executor")
    models_doc = _load_yaml(root / ".sourcea" / "models.yaml")
    catalog = models_doc.get("catalog") if isinstance(models_doc.get("catalog"), dict) else {}
    spec = catalog.get(model_ref) if isinstance(catalog.get(model_ref), dict) else {}
    provider = str(spec.get("provider") or "auto")
    model = str(spec.get("model") or "gpt-4o")
    return provider, model


def _agent_system(agent_id: str, workspace_path: str | None = None) -> str:
    root = _workspace_root(workspace_path) or _sourcea_root()
    doc = _load_yaml(_agent_file(root, agent_id))
    system = str(doc.get("system") or "").strip()
    if system:
        return system
    defaults = {
        "planner": "You are the Planner agent. Convert founder missions into deterministic tasks.",
        "builder": "You are the Builder agent. Execute bounded tasks with receipts and plain founder language.",
        "verifier": "You are the Verifier agent. Check claims against disk receipts. PASS or BLOCK only.",
    }
    return defaults.get(agent_id, defaults["builder"])


def _thread_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return THREAD_DIR / f"{safe or 'default'}.json"


def _new_session_id() -> str:
    return f"cu-{uuid.uuid4().hex[:12]}"


def load_thread(session_id: str | None = None) -> dict[str, Any]:
    sid = (session_id or "").strip() or "default"
    path = _thread_path(sid)
    if not path.is_file():
        return {
            "ok": True,
            "session_id": sid,
            "session_title": "Chat",
            "turns": [],
        }
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "error": "thread_read_failed", "session_id": sid, "turns": []}
    return {
        "ok": True,
        "session_id": row.get("session_id") or sid,
        "session_title": row.get("session_title") or "Chat",
        "turns": row.get("turns") or [],
    }


def clear_thread(session_id: str | None = None) -> dict[str, Any]:
    sid = (session_id or "").strip() or "default"
    path = _thread_path(sid)
    if path.is_file():
        try:
            path.unlink()
        except OSError:
            pass
    return {"ok": True, "session_id": sid, "cleared": True}


def _save_thread(row: dict[str, Any]) -> None:
    THREAD_DIR.mkdir(parents=True, exist_ok=True)
    sid = str(row.get("session_id") or "default")
    row["updated_at"] = _now()
    _thread_path(sid).write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def append_turn(
    *,
    session_id: str | None,
    role: str,
    text: str,
    agent_id: str = "",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sid = (session_id or "").strip() or _new_session_id()
    thread = load_thread(sid)
    turns = list(thread.get("turns") or [])
    turns.append(
        {
            "role": role,
            "text": text,
            "at": _now(),
            "agent_id": agent_id or None,
            "meta": meta or {},
        }
    )
    title = thread.get("session_title") or "Chat"
    if role == "user" and title == "Chat":
        title = (text[:48] + "…") if len(text) > 48 else text
    row = {
        "schema": "chat-unify-thread-v1",
        "session_id": sid,
        "session_title": title,
        "turns": turns,
        "updated_at": _now(),
    }
    _save_thread(row)
    return row


def _write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    rid = str(payload.get("run_id") or uuid.uuid4().hex[:12])
    path = RECEIPT_DIR / f"{rid}.json"
    payload["receipt_at"] = _now()
    try:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def smart_route(
    text: str,
    *,
    workspace_path: str | None = None,
    explicit_agent: str | None = None,
    explicit_machine: str | None = None,
) -> dict[str, Any]:
    from chat_unify_smart_router_v1 import route_request  # noqa: WPS433

    return route_request(
        text,
        workspace_path=workspace_path,
        explicit_agent=explicit_agent,
        explicit_machine=explicit_machine,
    )


def smart_chat_turn(
    *,
    text: str,
    agent_id: str = "auto",
    session_id: str | None = None,
    workspace_path: str | None = None,
    model: str = "",
    fast: bool = True,
) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_text"}
    aid = (agent_id or "auto").strip().lower()
    route: dict[str, Any] | None = None
    if aid in ("auto", "smart", ""):
        route = smart_route(text, workspace_path=workspace_path)
        if route.get("use_multi_agent"):
            row = multi_agent_run(
                text=text,
                session_id=session_id,
                workspace_path=workspace_path,
                agents=route.get("agent_team"),
            )
            row["smart_route"] = route
            return row
        aid = str(route.get("primary_agent") or "builder")
        model = model or str(route.get("model_id") or "")
    row = chat_turn(
        text=text,
        agent_id=aid,
        session_id=session_id,
        workspace_path=workspace_path,
        model=model,
        provider=str(route.get("provider") or "") if route else "",
        fast=fast,
    )
    if route:
        row["smart_route"] = route
        row["machine_tab"] = route.get("machine_tab")
        row["routing_reason"] = route.get("reasoning")
    return row


def chat_turn(
    *,
    text: str,
    agent_id: str = "builder",
    session_id: str | None = None,
    workspace_path: str | None = None,
    model: str = "",
    provider: str = "",
    fast: bool = True,
) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_text"}
    agent_id = (agent_id or "builder").strip().lower()
    run_id = f"cu-run-{uuid.uuid4().hex[:12]}"
    prov, mdl = _resolve_model(agent_id, workspace_path)
    if provider:
        prov = provider
    if model:
        mdl = model
    system = _agent_system(agent_id, workspace_path)
    from ai_unify_api_v1 import dispatch_raw  # noqa: WPS433

    llm = dispatch_raw(
        system=system,
        user=text,
        provider=prov,
        model=mdl,
        task_id=run_id,
        source=f"chat-unify-engine:{agent_id}",
        light_gate=fast,
    )
    if not llm.get("ok"):
        return {
            "ok": False,
            "run_id": run_id,
            "agent_id": agent_id,
            "error": llm.get("error") or "llm_failed",
            "message": llm.get("error") or "LLM failed",
        }
    reply = str(llm.get("text") or llm.get("response") or llm.get("content") or "").strip()
    sid = (session_id or "").strip() or _new_session_id()
    append_turn(session_id=sid, role="user", text=text, agent_id=agent_id)
    thread = append_turn(
        session_id=sid,
        role="assistant",
        text=reply,
        agent_id=agent_id,
        meta={"run_id": run_id, "model": mdl},
    )
    row = {
        "ok": True,
        "engine": ENGINE_SCHEMA,
        "run_id": run_id,
        "agent_id": agent_id,
        "session_id": thread.get("session_id"),
        "display_response": reply,
        "response": reply,
        "llm": {"provider": prov, "model": mdl, "agent_id": agent_id},
        "decision_card": {
            "goal": text[:200],
            "summary": reply[:400],
            "agent_id": agent_id,
        },
    }
    _write_receipt(row)
    return row


def multi_agent_run(
    *,
    text: str,
    session_id: str | None = None,
    workspace_path: str | None = None,
    agents: list[str] | None = None,
) -> dict[str, Any]:
    """Sequential planner → builder → verifier chain."""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_text"}
    chain = agents or ["planner", "builder", "verifier"]
    stages: list[dict[str, Any]] = []
    current = text
    run_id = f"cu-multi-{uuid.uuid4().hex[:12]}"
    sid = (session_id or "").strip() or _new_session_id()
    append_turn(session_id=sid, role="user", text=text, agent_id="multi")
    for aid in chain:
        prov, mdl = _resolve_model(aid, workspace_path)
        system = _agent_system(aid, workspace_path)
        from ai_unify_api_v1 import dispatch_raw  # noqa: WPS433

        llm = dispatch_raw(
            system=system,
            user=current,
            provider=prov,
            model=mdl,
            task_id=f"{run_id}-{aid}",
            source=f"chat-unify-multi:{aid}",
            light_gate=True,
        )
        if not llm.get("ok"):
            return {"ok": False, "run_id": run_id, "stages": stages, "error": llm.get("error")}
        reply = str(llm.get("text") or llm.get("response") or "").strip()
        stages.append({"agent_id": aid, "ok": True, "response": reply, "model": mdl})
        current = reply
    final = stages[-1].get("response") if stages else ""
    append_turn(
        session_id=sid,
        role="assistant",
        text=final,
        agent_id="multi",
        meta={"run_id": run_id, "stages": [s["agent_id"] for s in stages]},
    )
    return {
        "ok": True,
        "engine": ENGINE_SCHEMA,
        "run_id": run_id,
        "stages": stages,
        "display_response": final,
        "response": final,
        "session_id": sid,
    }


def machines_status() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": ENGINE_SCHEMA,
        "machines": MACHINES,
        "multi_agent_chain": ["planner", "builder", "verifier"],
        "forge_terminal_peer": f"http://127.0.0.1:{os.environ.get('FORGE_TERMINAL_PORT', '13029')}/",
    }


def plan_registry_read(body: dict[str, Any]) -> dict[str, Any]:
    """Bounded read-only plan registry tool for Chat Unify."""
    from sourcea_plan_registry_client_v1 import contains_secret_like, get_plan, query_rows  # noqa: WPS433

    plan_id = str(body.get("plan_id") or "").strip()
    if plan_id:
        row = get_plan(plan_id)
        mode = "lookup"
    else:
        try:
            limit = int(body.get("limit") or 5)
        except (TypeError, ValueError):
            limit = 5
        try:
            offset = int(body.get("offset") or 0)
        except (TypeError, ValueError):
            offset = 0
        limit = max(1, min(limit, 10))
        row = query_rows(
            limit=limit,
            offset=max(0, offset),
            status=str(body.get("status") or "").strip(),
            lane=str(body.get("lane") or "").strip(),
        )
        mode = "next_rows"
    row["ok"] = bool(row.get("ok"))
    row["engine"] = ENGINE_SCHEMA
    row["machine"] = "plan_registry"
    row["mode"] = mode
    row["contract"] = "sourcea-plan-registry-read-v1"
    row["max_limit"] = 10
    row["summary"] = {
        "total": row.get("total"),
        "count": row.get("count"),
        "plan_id": plan_id or None,
        "found": row.get("found") if plan_id else None,
    }
    if contains_secret_like(row):
        return {"ok": False, "engine": ENGINE_SCHEMA, "machine": "plan_registry", "error": "secret_like_response_blocked"}
    return row


def status_payload(workspace_path: str | None = None) -> dict[str, Any]:
    agents = list_agents(workspace_path)
    return {
        "ok": True,
        "engine": ENGINE_SCHEMA,
        "version": ENGINE_VERSION,
        "service": "chat-unify-engine",
        "agents": agents.get("agents") or [],
        "machines": MACHINES,
        "smart_router": "chat_unify_smart_router_v1",
        "smart_router_ssot": "data/chat-unify-smart-router-v1.json",
        "thread_dir": str(THREAD_DIR),
        "forge_terminal_motor": "peer_only",
    }


def handle_post(body: dict[str, Any]) -> dict[str, Any]:
    body = body or {}
    action = str(body.get("action") or "status").strip().lower()
    ws = str(body.get("workspace_path") or body.get("folder") or "").strip() or None
    if action in ("status", "engine_status"):
        return status_payload(ws)
    if action == "list_agents":
        return list_agents(ws)
    if action == "machines_status":
        return machines_status()
    if action in ("plan_registry", "plan_registry_read", "plan_registry_lookup"):
        return plan_registry_read(body)
    if action == "smart_route":
        return smart_route(
            str(body.get("text") or ""),
            workspace_path=ws,
            explicit_agent=str(body.get("agent_id") or body.get("agent") or "") or None,
            explicit_machine=str(body.get("machine") or body.get("machine_tab") or "") or None,
        )
    if action == "smart_chat_turn":
        return smart_chat_turn(
            text=str(body.get("text") or ""),
            agent_id=str(body.get("agent_id") or body.get("agent") or "auto"),
            session_id=str(body.get("session_id") or "").strip() or None,
            workspace_path=ws,
            model=str(body.get("model") or ""),
            fast=bool(body.get("fast", True)),
        )
    if action == "chat_turn":
        aid = str(body.get("agent_id") or body.get("agent") or "auto").strip().lower()
        if aid in ("auto", "smart"):
            return smart_chat_turn(
                text=str(body.get("text") or ""),
                agent_id="auto",
                session_id=str(body.get("session_id") or "").strip() or None,
                workspace_path=ws,
                model=str(body.get("model") or ""),
                fast=bool(body.get("fast", True)),
            )
        return chat_turn(
            text=str(body.get("text") or ""),
            agent_id=str(body.get("agent_id") or body.get("agent") or "builder"),
            session_id=str(body.get("session_id") or "").strip() or None,
            workspace_path=ws,
            model=str(body.get("model") or ""),
            provider=str(body.get("provider") or ""),
            fast=bool(body.get("fast", True)),
        )
    if action == "multi_agent_run":
        agents = body.get("agents")
        if isinstance(agents, list):
            chain = [str(a) for a in agents]
        else:
            chain = None
        return multi_agent_run(
            text=str(body.get("text") or ""),
            session_id=str(body.get("session_id") or "").strip() or None,
            workspace_path=ws,
            agents=chain,
        )
    if action == "chat_thread":
        return load_thread(str(body.get("session_id") or "").strip() or None)
    if action == "chat_thread_clear":
        return clear_thread(str(body.get("session_id") or "").strip() or None)
    return {"ok": False, "error": f"unknown_action:{action}"}
