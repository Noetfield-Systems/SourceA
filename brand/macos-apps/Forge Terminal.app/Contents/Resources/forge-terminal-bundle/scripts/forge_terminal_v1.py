#!/usr/bin/env python3
"""Forge Terminal v1 — thin product layer: idea → LLM → decision card → Cursor or Cloud.

Reuses: chat_unify_prompt_forge_v1 · model_dispatch · founder_language · worker inbox · cloud proxy.

Receipt: ~/.sina/forge-terminal-latest-v1.json
Outbox: ~/.sina/forge-terminal-outbox/<run_id>.json
Telemetry: ~/.sina/forge-terminal-telemetry-v1.jsonl
Failures: ~/.sina/forge-terminal-failures-v1.jsonl
Orchestration: ~/.sina/forge-terminal-orchestration-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SECRETS = SINA / "secrets.env"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ai_unify_api_v1 import bootstrap_secrets_env  # noqa: E402

bootstrap_secrets_env(force=True, log=False)
RUNS_DIR = SINA / "forge-terminal-runs"
OUTBOX_DIR = SINA / "forge-terminal-outbox"
LATEST = SINA / "forge-terminal-latest-v1.json"
ORCH_RECEIPT = SINA / "forge-terminal-orchestration-v1.json"
SCHEMA = "forge-terminal-run-v1"
CHAT_SETTINGS = SINA / "forge-chat-settings-v1.json"
CHAT_SETTINGS_SCHEMA = "forge-chat-settings-v1"

LLM_SYSTEM = """You are SourceA Forge Terminal — answer the bounded mission in markdown.
Include: goal, suggested files/paths, risks, and a short WORK line for Cursor Worker.
Be concrete. No filler. Under 1200 words unless the mission requires more detail."""

RISK_HIGH = re.compile(
    r"\b(payment|custody|fintrac|msb|wire transfer|private.?key|secret|password)\b",
    re.I,
)
RISK_MED = re.compile(r"\b(deploy|production|migration|delete|drop table|force push)\b", re.I)
FILE_PATH = re.compile(
    r"(?:^|\s)((?:apps|scripts|brain-os|data|infra)/[\w./\-]+|\~/?\.sina/[\w./\-]+)",
    re.M,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run_path(run_id: str) -> Path:
    safe = "".join(c for c in run_id if c.isalnum() or c in "-_")
    return RUNS_DIR / f"{safe}.json"


def _outbox_path(run_id: str) -> Path:
    safe = "".join(c for c in run_id if c.isalnum() or c in "-_")
    return OUTBOX_DIR / f"{safe}.json"


def _freeze_active() -> bool:
    try:
        import sys

        sys.path.insert(0, str(SCRIPTS))
        from mac_focus_freeze_v1 import is_focus_freeze  # noqa: WPS433

        return bool(is_focus_freeze())
    except Exception:
        return (SINA / "auto-run-disabled-v1.flag").is_file()


def _estimate_cost_usd(*, input_chars: int, output_chars: int, provider: str = "") -> tuple[float, str]:
    tokens = (input_chars + output_chars) / 4.0
    prov = (provider or "").lower()
    rate = 0.0000004 if "flash" in prov or prov in ("forge_only", "openrouter") else 0.000003
    usd = max(round(tokens * rate, 4), 0.01)
    return usd, f"~{int(tokens)} tokens · {provider or 'openrouter'}"


def _infer_risk(text: str) -> str:
    blob = text or ""
    if RISK_HIGH.search(blob):
        return "high"
    if RISK_MED.search(blob):
        return "medium"
    return "low"


def _infer_files(text: str) -> tuple[int, list[str]]:
    hints = list(dict.fromkeys(m.group(1).strip() for m in FILE_PATH.finditer(text or "")))
    if hints:
        return len(hints), hints[:12]
    loose = re.findall(r"`([^`]+)`", text or "")
    paths = [p for p in loose if "/" in p][:12]
    if paths:
        return len(paths), paths
    return 0, []


def _extract_goal(founder_text: str, simplified: str) -> str:
    first = (founder_text or "").strip().split("\n")[0][:160]
    if len(first) >= 12:
        return first
    for line in (simplified or "").splitlines():
        line = line.strip()
        if line.lower().startswith("goal:"):
            return line[5:].strip()[:160]
        if line and not line.startswith("#"):
            return line[:160]
    return (founder_text or "Mission")[:160]


def build_decision_card(
    *,
    run_id: str,
    founder_input: str,
    simplified: str,
    cursor_prompt: str,
    llm_meta: dict | None = None,
    decision: str = "pending",
    execution_plane: str = "mac_terminal",
) -> dict[str, Any]:
    llm_meta = llm_meta or {}
    combined = f"{founder_input}\n{simplified}\n{cursor_prompt}"
    file_count, file_hints = _infer_files(combined)
    risk = _infer_risk(combined)
    in_ch = int(llm_meta.get("input_chars") or len(founder_input))
    out_ch = int(llm_meta.get("output_chars") or len(simplified))
    cost_usd, cost_note = _estimate_cost_usd(
        input_chars=in_ch,
        output_chars=out_ch,
        provider=str(llm_meta.get("provider") or ""),
    )
    summary_lines = [ln.strip() for ln in (simplified or "").splitlines() if ln.strip()]
    summary = summary_lines[0][:240] if summary_lines else cursor_prompt[:240]
    return {
        "schema": "forge-terminal-decision-card-v1",
        "run_id": run_id,
        "goal": _extract_goal(founder_input, simplified),
        "files": file_count,
        "file_hints": file_hints,
        "risk": risk,
        "cost_usd": cost_usd,
        "cost_note": cost_note,
        "decision": decision,
        "summary": summary,
        "cursor_prompt": cursor_prompt,
        "founder_input": founder_input,
        "execution_plane": execution_plane,
    }


def _llm_models(provider: str, model: str = "") -> tuple[str, str, bool]:
    from model_dispatch import resolve_explicit_model  # noqa: WPS433

    resolved = resolve_explicit_model(model)
    if resolved.get("explicit"):
        route = {
            "gemini_direct": "gemini",
            "openrouter": "openrouter",
            "openai": "openai",
            "anthropic_direct": "anthropic",
        }.get(resolved["provider"], "auto")
        return route, resolved["forge_model_id"], True

    import os

    from model_dispatch import FORGE_DEFAULT_MODEL  # noqa: WPS433

    gemini_model = os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
    or_model = os.environ.get("OPENROUTER_MODEL") or "google/gemini-2.5-flash"
    p = (provider or "auto").lower()
    if p == "gemini":
        return "gemini", gemini_model, False
    if p == "openrouter":
        return "openrouter", or_model, False
    if p == "openai":
        return "openai", "gpt-4o", False
    if p == "anthropic":
        return "anthropic", "claude-sonnet-4-6", False
    return "auto", FORGE_DEFAULT_MODEL, False


def _llm_answer(
    *,
    mission_prompt: str,
    task_id: str,
    provider: str = "auto",
    model: str = "",
    use_dispatch: bool = True,
) -> dict[str, Any]:
    bootstrap_secrets_env(force=True, log=False)
    from ai_unify_api_v1 import dispatch_raw  # noqa: WPS433

    prov, model_id, explicit = _llm_models(provider, model)
    user = mission_prompt[:12000]
    return dispatch_raw(
        system=LLM_SYSTEM,
        user=user,
        provider=prov,
        model=model_id or None,
        task_id=task_id,
        source="forge-terminal-v1",
        light_gate=not use_dispatch and not explicit,
        explicit_model=explicit,
    )


def cloud_workers_live() -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    try:
        from cloud_workers_hub_v1 import chain_status  # noqa: WPS433

        chain = chain_status()
    except Exception as exc:
        chain = {"ok": False, "error": str(exc)[:200]}
    live = bool(chain.get("ok"))
    row = {
        "schema": "forge-terminal-orchestration-v1",
        "at": _now(),
        "cloud_workers": "LIVE" if live else "DEGRADED",
        "freeze_active": _freeze_active(),
        "execution_default": "cloud" if _freeze_active() else "cursor_or_cloud",
        "chain": chain,
    }
    _write_json(ORCH_RECEIPT, row)
    return row


_PILL_CACHE: dict[str, Any] = {"at": 0.0, "row": {}}
_PILL_TTL_S = 8.0
_MESH_LIGHT_CACHE: dict[str, Any] = {"at": 0.0, "row": {}}
_MESH_LIGHT_TTL_S = 30.0


def _mesh_light_payload() -> dict[str, Any]:
    import time

    now = time.time()
    cached = _MESH_LIGHT_CACHE.get("row") or {}
    if cached and (now - float(_MESH_LIGHT_CACHE.get("at") or 0)) < _MESH_LIGHT_TTL_S:
        return cached
    try:
        from forge_terminal_desktop_mesh_v1 import desktop_mesh_status  # noqa: WPS433

        mesh = desktop_mesh_status(fast=True)
        row = {
            "live_peers": mesh.get("live_peers"),
            "mesh_ready": mesh.get("mesh_ready"),
            "chat_unify": next(
                (p.get("status") for p in mesh.get("peers") or [] if p.get("id") == "chat_unify"),
                "offline",
            ),
            "cloud_workers_peer": next(
                (p.get("status") for p in mesh.get("peers") or [] if p.get("id") == "cloud_workers"),
                "offline",
            ),
            "peers": mesh.get("peers") or [],
        }
    except Exception:
        row = {"live_peers": 0, "mesh_ready": False, "peers": []}
    _MESH_LIGHT_CACHE["at"] = now
    _MESH_LIGHT_CACHE["row"] = row
    return row


def warm_status_light_cache() -> None:
    """Pre-warm status pills on server boot so first UI poll stays under 500ms."""
    try:
        status_light()
    except Exception:
        pass


def status_light(*, workspace_path: str | None = None) -> dict[str, Any]:
    """Fast status for UI pills — cached, no heavy imports per tick."""
    import time

    from forge_workspace_open_v1 import list_recent  # noqa: WPS433

    now = time.time()
    cached = _PILL_CACHE.get("row") or {}
    if cached and (now - float(_PILL_CACHE.get("at") or 0)) < _PILL_TTL_S:
        pills = cached
    else:
        from ai_unify_api_v1 import status_payload as ai_status  # noqa: WPS433

        ai = ai_status()
        orch = cloud_workers_live()
        from model_dispatch import forge_models_payload  # noqa: WPS433

        models = forge_models_payload()
        pills = {
            "cloud_workers": orch.get("cloud_workers"),
            "freeze_active": orch.get("freeze_active"),
            "llm": {
                "openrouter_ready": ai.get("openrouter_ready"),
                "openai_ready": ai.get("openai_ready"),
                "anthropic_ready": ai.get("anthropic_ready"),
                "gemini_ready": ai.get("gemini_direct_ready"),
            },
            "models": models.get("models") or [],
            "model_groups": models.get("groups") or [],
            "model_roles": models.get("roles") or [],
            "keys_ready": models.get("keys_ready") or {},
            "default_model": models.get("default_model"),
            "default_role": models.get("default_role"),
            "secrets_template": "data/forge-secrets-env-template-v1.env",
        }
        pills["desktop_mesh"] = _mesh_light_payload()
        _PILL_CACHE["at"] = now
        _PILL_CACHE["row"] = pills

    ws_root = _resolve_workspace_root(workspace_path=workspace_path)
    return {
        "ok": True,
        "schema": "forge-terminal-status-light-v1",
        "at": _now(),
        "workspace_open": bool(ws_root),
        "active_workspace_path": str(ws_root) if ws_root else "",
        "active_workspace_name": ws_root.name if ws_root else "",
        "recent_folders": list_recent(),
        **pills,
    }


def workspace_snapshot(*, workspace_path: str | None = None, workspace_id: str | None = None) -> dict[str, Any]:
    """One round-trip: tree + agents + tasks + receipts for open folder."""
    from forge_workspace_open_v1 import scan_workspace  # noqa: WPS433
    from workspace_kernel_v2 import kernel_status, list_agents, list_receipts, list_tasks, workspace_ready  # noqa: WPS433

    root = _resolve_workspace_root(workspace_path=workspace_path, workspace_id=workspace_id)
    if not root:
        return {"ok": False, "error": "no_workspace_open", "message": "Open a folder first."}
    ready = workspace_ready(root)
    agents_row = list_agents(root) if ready.get("ok") else {"agents": []}
    return {
        "ok": True,
        "schema": "forge-workspace-snapshot-v1",
        "path": str(root),
        "name": root.name,
        "ready": ready.get("ok"),
        "kernel": kernel_status(root),
        "scan": scan_workspace(root),
        "agents": agents_row.get("agents") or [],
        "tasks": (list_tasks(root, limit=15).get("tasks") or []) if ready.get("ok") else [],
        "receipts": (list_receipts(root, limit=10).get("receipts") or []) if ready.get("ok") else [],
    }


def _resolve_workspace_root(
    *,
    workspace_path: str | None = None,
    workspace_id: str | None = None,
) -> Path | None:
    """Path-first workspace (Cursor-style). No default catalog project."""
    from workspace_kernel_v2 import workspace_ready  # noqa: WPS433

    explicit = (workspace_path or "").strip()
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.is_dir():
            return p

    from forge_workspace_open_v1 import active_path  # noqa: WPS433

    session = active_path()
    if session and session.is_dir():
        return session

    from forge_workspace_open_v1 import read_session  # noqa: WPS433

    for item in read_session().get("recent") or []:
        raw = str(item.get("path") or "").strip()
        if not raw:
            continue
        p = Path(raw).expanduser().resolve()
        if p.is_dir() and workspace_ready(p)["ok"]:
            return p

    for candidate in (
        os.environ.get("SOURCEA_WORKSPACE_ROOT", "").strip(),
        os.environ.get("FORGE_WORKSPACE_ROOT", "").strip(),
    ):
        if candidate:
            p = Path(candidate).expanduser().resolve()
            if p.is_dir() and workspace_ready(p)["ok"]:
                return p

    if workspace_id:
        from forge_workspace_catalog_v2 import resolve_for_request  # noqa: WPS433

        return resolve_for_request(workspace_id)

    env_id = os.environ.get("FORGE_WORKSPACE_ID", "").strip()
    if env_id:
        from forge_workspace_catalog_v2 import resolve_for_request  # noqa: WPS433

        return resolve_for_request(env_id)

    from workspace_kernel_v2 import find_workspace_root  # noqa: WPS433

    for start in (Path.cwd(), ROOT):
        found = find_workspace_root(start)
        if found and workspace_ready(found)["ok"]:
            return found
    return None


def _kernel_project_root(
    workspace_id: str | None = None,
    workspace_path: str | None = None,
) -> Path | None:
    return _resolve_workspace_root(workspace_path=workspace_path, workspace_id=workspace_id)


def status_payload(*, workspace_id: str | None = None, workspace_path: str | None = None) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from ai_unify_api_v1 import status_payload as ai_status  # noqa: WPS433
    from forge_workspace_open_v1 import list_recent  # noqa: WPS433
    from forge_terminal_telemetry_v1 import summary as telemetry_summary  # noqa: WPS433
    from model_dispatch import forge_models_payload  # noqa: WPS433
    from workspace_kernel_v2 import kernel_status as ws_kernel_status, workspace_ready  # noqa: WPS433

    ws_root = _resolve_workspace_root(workspace_path=workspace_path, workspace_id=workspace_id)
    ws_open = bool(ws_root and workspace_ready(ws_root)["ok"])

    ai = ai_status()
    orch = cloud_workers_live()
    models = forge_models_payload()
    outbox_count = len(list(OUTBOX_DIR.glob("*.json"))) if OUTBOX_DIR.is_dir() else 0
    latest = _read_json(LATEST)
    return {
        "ok": True,
        "schema": "forge-terminal-status-v2",
        "at": _now(),
        "cloud_workers": orch.get("cloud_workers"),
        "freeze_active": orch.get("freeze_active"),
        "execution_default": orch.get("execution_default"),
        "telemetry": telemetry_summary(tail=10),
        "kernel": ws_kernel_status(ws_root) if ws_root else {"ok": False, "error": "no_workspace_open"},
        "workspace_open": ws_open,
        "active_workspace_path": str(ws_root) if ws_root else "",
        "active_workspace_name": ws_root.name if ws_root else "",
        "recent_folders": list_recent(),
        "llm": {
            "openrouter_ready": ai.get("openrouter_ready"),
            "openai_ready": ai.get("openai_ready"),
            "anthropic_ready": ai.get("anthropic_ready"),
            "gemini_ready": ai.get("gemini_direct_ready"),
            "auto_provider": ai.get("auto_provider"),
            "gate_mode": ai.get("gate_mode"),
        },
        "models": models.get("models") or [],
        "model_groups": models.get("groups") or [],
        "model_roles": models.get("roles") or [],
        "keys_ready": models.get("keys_ready") or {},
        "default_model": models.get("default_model"),
        "default_role": models.get("default_role"),
        "secrets_template": "data/forge-secrets-env-template-v1.env",
        "outbox_pending": outbox_count,
        "latest_run_id": latest.get("run_id"),
        "api": {
            "run": "POST /api/forge-terminal/v1 {\"action\":\"run\",\"text\":\"…\",\"full_llm\":true}",
            "execute": "POST {\"action\":\"execute\",\"run_id\":\"…\"}",
            "outbox_write": "POST {\"action\":\"outbox_write\",\"run_id\":\"…\",\"payload\":{}}",
        },
    }


def run_terminal(
    *,
    founder_text: str,
    use_ai_forge: bool = False,
    full_llm: bool = True,
    fast: bool = True,
    provider: str = "auto",
    model: str = "",
    workspace_id: str | None = None,
    workspace_path: str | None = None,
) -> dict[str, Any]:
    from forge_terminal_telemetry_v1 import detect_portfolio, log_event  # noqa: WPS433

    t0 = time.perf_counter()
    bootstrap_secrets_env(force=True, log=False)
    text = (founder_text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_text", "message": "Type your idea first."}

    run_id = f"ft-{uuid.uuid4().hex[:12]}"
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from workspace_kernel_v2 import workspace_ready  # noqa: WPS433

    ws_root = _resolve_workspace_root(workspace_path=workspace_path, workspace_id=workspace_id)
    chat_only = not ws_root
    if not chat_only:
        ready = workspace_ready(ws_root)
        if not ready.get("ok"):
            return {
                "ok": False,
                "error": "workspace_not_ready",
                "message": "This folder needs a .sourcea workspace. Use Open Folder — we auto-init on first open.",
                "path": str(ws_root),
                "missing": ready.get("missing") or [],
            }
    mission = text
    forge: dict[str, Any]
    ws_label = str(ws_root) if ws_root else ""

    if fast and not chat_only:
        forge = {
            "ok": True,
            "mode": "live_chat",
            "used_llm": False,
            "receipt_path": None,
            "workspace": ws_label,
            "chat_only": False,
        }
    else:
        from chat_unify_prompt_forge_v1 import run_prompt_forge_loop  # noqa: WPS433

        forge = run_prompt_forge_loop(
            founder_text=text,
            use_ai=use_ai_forge and not chat_only,
            write_receipt=not chat_only,
        )
        if not forge.get("ok"):
            if chat_only:
                forge = {
                    "ok": True,
                    "mode": "global_chat",
                    "used_llm": False,
                    "receipt_path": None,
                    "workspace": "",
                    "chat_only": True,
                }
                mission = text
            else:
                return forge
        else:
            mission = (forge.get("prompt") or "").strip()
            if not mission:
                return {"ok": False, "error": "empty_mission", "message": "Prompt forge produced no mission."}
            forge["chat_only"] = chat_only
            forge["workspace"] = ws_label

    llm: dict[str, Any] = {"ok": True, "skipped": True, "provider": "forge_only"}
    raw_response = mission

    if full_llm:
        if chat_only:
            scoped_user = (
                "CONTEXT: Founder using Forge Terminal living chat (no workspace folder open yet).\n"
                "Answer in plain English — bottom line, business meaning, blockers, next step.\n"
                "Suggest opening a folder when code execution or file edits are needed.\n\n"
                f"Mission:\n{mission[:10000]}"
            )
        else:
            from forge_workspace_open_v1 import workspace_context_for_llm  # noqa: WPS433

            project_ctx = workspace_context_for_llm(ws_root)
            scoped_user = (
                f"Workspace root (jail — only reference paths under here): {ws_root}\n\n"
                f"Project context (read before answering):\n{project_ctx}\n\n"
                f"Mission:\n{mission[:10000]}"
            )
        llm = _llm_answer(
            mission_prompt=scoped_user,
            task_id=run_id,
            provider=provider,
            model=model,
            use_dispatch=not bool((model or "").strip()),
        )
        if not llm.get("ok") and not llm.get("skipped"):
            err_msg = llm.get("message") or llm.get("response") or "Model call failed"
            log_event(
                "run",
                run_id=run_id,
                success=False,
                elapsed_ms=(time.perf_counter() - t0) * 1000,
                model=model or llm.get("model"),
                provider=llm.get("provider"),
                decision="pending",
                portfolio=detect_portfolio(text),
                error=str(err_msg)[:200],
            )
            return {
                "ok": False,
                "error": llm.get("error") or "llm_failed",
                "message": str(err_msg)[:500],
                "run_id": run_id,
                "llm": llm,
            }
        raw_response = (llm.get("response") or "").strip() or mission

    from chat_founder_language_v1 import translate_for_founder  # noqa: WPS433

    simplified_row = translate_for_founder(
        draft=raw_response[:8000],
        founder_message=text,
        prefer_ai=True,
    )
    simplified = (simplified_row.get("founder_text") or raw_response[:2500]).strip()

    from forge_quality_gate_v1 import _looks_like_json_blob, response_for_display  # noqa: WPS433

    if _looks_like_json_blob(simplified):
        simplified_row = translate_for_founder(
            draft=raw_response[:8000],
            founder_message=text,
            prefer_ai=True,
        )
        simplified = (simplified_row.get("founder_text") or raw_response[:2500]).strip()

    cursor_prompt = mission
    if simplified and len(simplified) < len(mission) * 2:
        cursor_prompt = f"{mission}\n\n---\nFounder summary:\n{simplified}"

    card = build_decision_card(
        run_id=run_id,
        founder_input=text,
        simplified=simplified,
        cursor_prompt=cursor_prompt,
        llm_meta={
            "provider": llm.get("provider") or provider,
            "model": llm.get("model"),
            "input_chars": len(mission),
            "output_chars": len(raw_response),
            "gate": llm.get("gate"),
            "blocked": llm.get("blocked"),
        },
        decision="pending",
        execution_plane="cloud" if _freeze_active() else "mac_terminal",
    )

    from forge_quality_gate_v1 import (  # noqa: WPS433
        apply_gate_to_decision_card,
        evaluate_quality_gate,
        write_quality_receipt,
    )

    quality = evaluate_quality_gate(
        run_id=run_id,
        doc={
            "schema": SCHEMA,
            "run_id": run_id,
            "at": _now(),
            "founder_input": text,
            "response": simplified,
            "llm": llm,
            "forge": forge,
            "decision_card": card,
        },
        workspace_path=ws_label,
        full_llm=full_llm,
        eval_shadow=bool(full_llm),
    )
    write_quality_receipt(quality)
    card = apply_gate_to_decision_card(card, quality)
    display_text = response_for_display(response=simplified, card=card)

    doc = {
        "schema": SCHEMA,
        "ok": True,
        "run_id": run_id,
        "at": _now(),
        "founder_input": text,
        "forge": {
            "mode": forge.get("mode"),
            "used_llm": forge.get("used_llm"),
            "receipt_path": forge.get("receipt_path"),
            "workspace": ws_label,
            "fast": fast,
            "chat_only": chat_only,
        },
        "llm": {
            "ok": llm.get("ok"),
            "skipped": llm.get("skipped"),
            "provider": llm.get("provider"),
            "model": llm.get("model"),
            "blocked": llm.get("blocked"),
            "gate": llm.get("gate"),
            "full_llm": full_llm,
        },
        "response": simplified,
        "display_response": display_text,
        "raw_llm_chars": len(raw_response),
        "decision_card": card,
        "quality_gate": quality,
        "orchestration": {
            "cloud_workers": cloud_workers_live().get("cloud_workers"),
            "freeze_active": _freeze_active(),
        },
    }
    _write_json(_run_path(run_id), doc)
    _write_json(LATEST, {"run_id": run_id, "at": doc["at"], "decision_card": card})
    log_event(
        "run",
        run_id=run_id,
        success=True,
        elapsed_ms=(time.perf_counter() - t0) * 1000,
        model=str(llm.get("model") or model or ""),
        provider=str(llm.get("provider") or provider or ""),
        decision=str(card.get("decision") or "pending"),
        cost_usd=float(card.get("cost_usd") or 0),
        portfolio=detect_portfolio(text),
        plane=str(card.get("execution_plane") or ""),
        extra={
            "quality_verdict": quality.get("verdict"),
            "quality_score": quality.get("score"),
            "eval_shadow": (quality.get("eval_shadow") or {}).get("verdict"),
        },
    )
    kroot = _kernel_project_root(workspace_id, workspace_path)
    if kroot:
        from workspace_kernel_v2 import sync_forge_run  # noqa: WPS433

        sync_forge_run(kroot, phase="run", run_id=run_id, founder_text=text)
    return doc


def decide(
    *,
    run_id: str,
    decision: str,
    note: str = "",
    workspace_id: str | None = None,
    workspace_path: str | None = None,
) -> dict[str, Any]:
    dec = (decision or "").strip().lower()
    if dec not in ("approved", "rejected", "revise"):
        return {"ok": False, "error": "invalid_decision", "allowed": ["approved", "rejected", "revise"]}
    path = _run_path(run_id)
    doc = _read_json(path)
    if not doc.get("run_id"):
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    card = doc.get("decision_card") or {}
    card["decision"] = "approved" if dec == "approved" else ("rejected" if dec == "rejected" else "revise")
    if note:
        card["decision_note"] = note[:500]
    doc["decision_card"] = card
    doc["decided_at"] = _now()
    _write_json(path, doc)
    _write_json(LATEST, {"run_id": run_id, "at": doc["decided_at"], "decision_card": card})
    from forge_terminal_telemetry_v1 import detect_portfolio, log_event  # noqa: WPS433

    log_event(
        "decide",
        run_id=run_id,
        success=True,
        decision=dec,
        portfolio=detect_portfolio(str(doc.get("founder_input") or "")),
    )
    kroot = _kernel_project_root(workspace_id, workspace_path)
    if kroot:
        from workspace_kernel_v2 import sync_forge_run  # noqa: WPS433

        sync_forge_run(kroot, phase="decide", run_id=run_id, decision=dec)
    return {"ok": True, "run_id": run_id, "decision_card": card}


def quality_rerun(
    *,
    run_id: str,
    founder_text: str = "",
    workspace_path: str | None = None,
    full_llm: bool | None = None,
) -> dict[str, Any]:
    path = _run_path(run_id)
    doc = _read_json(path)
    if not doc.get("run_id"):
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    if founder_text.strip():
        doc["founder_input"] = founder_text.strip()
        card = doc.get("decision_card") or {}
        card["founder_input"] = founder_text.strip()
        card["goal"] = _extract_goal(founder_text, doc.get("response") or "")
        doc["decision_card"] = card
    ws = workspace_path or (doc.get("forge") or {}).get("workspace") or ""
    from forge_quality_gate_v1 import (  # noqa: WPS433
        apply_gate_to_decision_card,
        evaluate_quality_gate,
        write_quality_receipt,
    )

    llm = doc.get("llm") or {}
    use_llm = bool(llm.get("ok") and not llm.get("skipped")) if full_llm is None else bool(full_llm)
    quality = evaluate_quality_gate(
        run_id=run_id,
        doc=doc,
        workspace_path=str(ws) if ws else None,
        full_llm=use_llm,
        eval_shadow=False,
    )
    write_quality_receipt(quality)
    card = apply_gate_to_decision_card(doc.get("decision_card") or {}, quality)
    doc["decision_card"] = card
    doc["quality_gate"] = quality
    doc["quality_rerun_at"] = _now()
    _write_json(path, doc)
    return {"ok": True, "run_id": run_id, "decision_card": card, "quality_gate": quality}


def write_outbox(*, run_id: str, payload: dict[str, Any], source: str = "cloud_worker") -> dict[str, Any]:
    row = {
        "schema": "forge-terminal-outbox-v1",
        "run_id": run_id,
        "at": _now(),
        "source": source,
        "payload": payload,
    }
    _write_json(_outbox_path(run_id), row)
    path = _run_path(run_id)
    doc = _read_json(path)
    if doc.get("run_id"):
        doc["outbox"] = row
        doc["outbox_at"] = row["at"]
        _write_json(path, doc)
    return {"ok": True, "run_id": run_id, "outbox": row}


def poll_outbox(*, run_id: str) -> dict[str, Any]:
    row = _read_json(_outbox_path(run_id))
    if not row:
        return {"ok": True, "run_id": run_id, "empty": True}
    return {"ok": True, "run_id": run_id, "outbox": row}


def _quality_execution_block(doc: dict[str, Any]) -> dict[str, Any] | None:
    from forge_quality_gate_v1 import execution_allowed  # noqa: WPS433

    ok, gate_row = execution_allowed(doc)
    if ok:
        return None
    return {
        "ok": False,
        "error": gate_row.get("error") or "quality_gate_blocked",
        "run_id": doc.get("run_id"),
        "quality_gate": gate_row.get("quality_gate") or gate_row,
        "verdict": gate_row.get("verdict"),
        "hint": gate_row.get("hint"),
        "for_founder": {
            "show_this": (
                f"Quality gate blocked execution ({gate_row.get('verdict') or 'FAIL'}) — "
                f"{gate_row.get('passed_layers', '?')}/11 layers passed. Re-run mission after revise."
            ),
        },
    }


def _record_prompt_learning(compiled: dict[str, Any] | None, execution: dict[str, Any]) -> dict[str, Any] | None:
    """Record adaptive learning outcome when advisor/swarm completes."""
    if not compiled or not compiled.get("ok"):
        return None
    try:
        from forge_prompt_os_compiler_v2 import record_execution_outcome  # noqa: WPS433

        state = str(execution.get("state") or "")
        if not state and execution.get("swarm_v3"):
            state = str((execution.get("swarm_v3") or {}).get("state") or "")
        qg = execution.get("quality_gate") or {}
        verdict = str(qg.get("verdict") or execution.get("verdict") or "")
        ok = bool(execution.get("ok"))
        if execution.get("agent") and execution["agent"].get("done"):
            ok = ok or True
        if state.upper() == "DONE":
            ok = True
        return record_execution_outcome(
            compiled=compiled,
            execution_ok=ok,
            execution_state=state,
            quality_verdict=verdict,
            run_id=str(execution.get("advisor_id") or execution.get("swarm_id") or ""),
        )
    except Exception:
        return None


def _resolve_swarm_run(body: dict[str, Any], root: Path) -> dict[str, Any]:
    """Route swarm to cloud dispatch or local kernel."""
    goal = str(body.get("goal") or body.get("text") or "")
    dry_run = bool(body.get("dry_run"))
    if body.get("cloud"):
        from forge_swarm_blackboard_v1 import load_blackboard  # noqa: WPS433
        from forge_swarm_cloud_dispatch_v1 import dispatch_swarm_cloud  # noqa: WPS433

        return dispatch_swarm_cloud(
            goal=goal,
            workspace_path=str(root),
            parallel=body.get("parallel", True) is not False,
            planner_count=int(body.get("planner_count") or 3),
            critic_count=int(body.get("critic_count") or 3),
            blackboard_snapshot=load_blackboard(),
            dry_run=dry_run,
        )
    from forge_agent_kernel_v3_swarm import run_swarm_loop  # noqa: WPS433

    return run_swarm_loop(
        goal=goal,
        workspace_path=str(root),
        max_tasks=int(body.get("max_tasks") or 5),
        max_steps_per_task=int(body.get("max_steps") or 4),
        dry_run=dry_run,
        parallel=body.get("parallel", True) is not False,
        parallel_build=body.get("parallel_build", True) is not False,
        planner_count=int(body.get("planner_count") or 3),
        critic_count=int(body.get("critic_count") or 3),
    )


def send_to_cloud(
    *,
    run_id: str,
    dry_run: bool = False,
    workspace_id: str | None = None,
    workspace_path: str | None = None,
) -> dict[str, Any]:
    path = _run_path(run_id)
    doc = _read_json(path)
    if not doc.get("run_id"):
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    card = doc.get("decision_card") or {}
    if card.get("decision") == "rejected":
        return {"ok": False, "error": "decision_rejected", "run_id": run_id}
    blocked = _quality_execution_block(doc)
    if blocked:
        return blocked

    prompt = (card.get("cursor_prompt") or doc.get("response") or "").strip()
    founder_input = str(doc.get("founder_input") or card.get("founder_input") or "")
    if not prompt:
        return {"ok": False, "error": "empty_prompt"}

    import sys

    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib.hub_cloud_proxy_v1 import cloud_worker_url, proxy_to_cloud  # noqa: WPS433

    url = cloud_worker_url()
    if not url and not dry_run:
        return {
            "ok": False,
            "error": "cloud_worker_unreachable",
            "hint": "Set FBE_CLOUD_WORKER_URL or data/fbe_cloud_worker_config_v1.json",
        }

    body = {
        "draft": prompt,
        "founder_message": founder_input,
        "context_id": run_id,
        "job_id": run_id,
        "forge_context": {
            "origin": "forge_terminal_v1",
            "run_id": run_id,
            "goal": card.get("goal"),
            "dry_run": dry_run,
        },
    }

    if dry_run:
        cloud_row = {
            "ok": True,
            "dry_run": True,
            "execution_plane": "cloud_deferred",
            "would_post": "/api/fbe/comprehension-loop/v1",
            "cloud_url": url,
            "body_preview": prompt[:400],
        }
    else:
        cloud_row = proxy_to_cloud(
            path="/api/fbe/comprehension-loop/v1",
            body=body,
            timeout_s=300,
        )

    outbox_payload = {
        "kind": "cloud_execution",
        "dry_run": dry_run,
        "cloud_ok": cloud_row.get("ok"),
        "accepted_founder_text": cloud_row.get("accepted_founder_text") or cloud_row.get("response"),
        "receipt_path": cloud_row.get("receipt_path"),
        "logs": cloud_row.get("for_founder") or cloud_row.get("show_this"),
        "raw": {k: cloud_row.get(k) for k in ("ok", "error", "execution_plane", "proxied", "status")},
    }
    write_outbox(run_id=run_id, payload=outbox_payload, source="forge_terminal_cloud")

    doc["cloud_execution"] = cloud_row
    doc["sent_at"] = _now()
    if card.get("decision") == "pending":
        card["decision"] = "approved"
    card["execution_plane"] = "cloud"
    doc["decision_card"] = card
    _write_json(path, doc)
    _write_json(LATEST, {"run_id": run_id, "at": doc["sent_at"], "decision_card": card})

    show = "Cloud comprehension loop dispatched."
    if isinstance(cloud_row.get("for_founder"), dict):
        show = str(cloud_row["for_founder"].get("show_this") or show)
    elif cloud_row.get("for_founder"):
        show = str(cloud_row["for_founder"])

    from forge_terminal_telemetry_v1 import detect_portfolio, log_event, log_failure  # noqa: WPS433

    cloud_ok = bool(cloud_row.get("ok"))
    log_event(
        "execute_cloud",
        run_id=run_id,
        success=cloud_ok,
        decision=str(card.get("decision") or ""),
        portfolio=detect_portfolio(founder_input),
        plane="cloud",
        error=None if cloud_ok else str(cloud_row.get("error") or show)[:200],
        extra={"dry_run": dry_run},
    )
    if not cloud_ok and not dry_run:
        log_failure(
            run_id=run_id,
            stage="cloud_execute",
            founder_input=founder_input,
            decision=str(card.get("decision") or ""),
            plane="cloud",
            error=str(cloud_row.get("error") or show),
            cloud_raw=outbox_payload.get("raw"),
        )

    kroot = _kernel_project_root(workspace_id, workspace_path)
    if kroot and not dry_run:
        from workspace_kernel_v2 import sync_forge_run  # noqa: WPS433

        sync_forge_run(kroot, phase="execute_start", run_id=run_id)
        sync_forge_run(
            kroot,
            phase="execute_done",
            run_id=run_id,
            success=cloud_ok,
            error=str(cloud_row.get("error") or "") if not cloud_ok else "",
        )

    return {
        "ok": cloud_ok,
        "run_id": run_id,
        "execution_plane": "cloud",
        "cloud_workers": cloud_workers_live().get("cloud_workers"),
        "cloud": cloud_row,
        "outbox": str(_outbox_path(run_id)),
        "decision_card": card,
        "for_founder": {"show_this": show if cloud_row.get("ok") else f"Cloud failed: {cloud_row.get('error') or 'unknown'}"},
    }


def send_to_cursor(*, run_id: str) -> dict[str, Any]:
    path = _run_path(run_id)
    doc = _read_json(path)
    if not doc.get("run_id"):
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    blocked = _quality_execution_block(doc)
    if blocked:
        return blocked
    card = doc.get("decision_card") or {}
    if card.get("decision") not in ("approved", "pending"):
        return {
            "ok": False,
            "error": "decision_not_approved",
            "decision": card.get("decision"),
            "hint": "Approve before sending to Cursor.",
        }
    prompt = (card.get("cursor_prompt") or doc.get("response") or "").strip()
    if not prompt:
        return {"ok": False, "error": "empty_prompt"}

    import sys

    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import deliver_to_worker_inbox  # noqa: WPS433

    meta = {
        "sa_id": f"forge-terminal-{run_id}",
        "queue_role": "act",
        "queue_pos": 1,
        "queue_total": 1,
        "origin": "forge_terminal_v1",
        "forge_terminal_run_id": run_id,
    }
    inj = deliver_to_worker_inbox(prompt, source="forge_terminal_v1", meta=meta, fast=True)
    doc["cursor_bridge"] = inj
    doc["sent_at"] = _now()

    if inj.get("blocked_by_freeze") or inj.get("prompt_blocked_by_freeze"):
        cloud_fallback = send_to_cloud(run_id=run_id, dry_run=False)
        cloud_fallback["cursor_blocked"] = True
        cloud_fallback["for_founder"] = {
            "show_this": (
                "FREEZE blocked local INBOX — routed to Cloud Workers instead. "
                + str((cloud_fallback.get("for_founder") or {}).get("show_this") or "")
            ),
        }
        return cloud_fallback

    if not inj.get("ok"):
        from forge_terminal_telemetry_v1 import detect_portfolio, log_event, log_failure  # noqa: WPS433

        founder_input = str(doc.get("founder_input") or card.get("founder_input") or "")
        err = str(inj.get("error") or "inbox_write_failed")
        log_event(
            "execute_cursor",
            run_id=run_id,
            success=False,
            decision=str(card.get("decision") or ""),
            portfolio=detect_portfolio(founder_input),
            plane="cursor_inbox",
            error=err,
        )
        log_failure(
            run_id=run_id,
            stage="cursor_inbox",
            founder_input=founder_input,
            decision=str(card.get("decision") or ""),
            plane="cursor_inbox",
            error=err,
        )
        return {
            "ok": False,
            "error": inj.get("error") or "inbox_write_failed",
            "run_id": run_id,
            "cursor_bridge": inj,
            "decision_card": card,
        }

    if card.get("decision") == "pending":
        card["decision"] = "approved"
    card["execution_plane"] = "cursor_inbox"
    doc["decision_card"] = card
    _write_json(path, doc)
    write_outbox(
        run_id=run_id,
        payload={"kind": "cursor_inbox", "inbox": str(SINA / "worker-prompt-inbox-v1.json"), "inj": inj},
        source="forge_terminal_cursor",
    )
    from forge_terminal_telemetry_v1 import detect_portfolio, log_event, log_failure  # noqa: WPS433

    founder_input = str(doc.get("founder_input") or card.get("founder_input") or "")
    log_event(
        "execute_cursor",
        run_id=run_id,
        success=True,
        decision=str(card.get("decision") or ""),
        portfolio=detect_portfolio(founder_input),
        plane="cursor_inbox",
    )
    return {
        "ok": True,
        "run_id": run_id,
        "inbox": str(SINA / "worker-prompt-inbox-v1.json"),
        "cursor_bridge": inj,
        "decision_card": card,
        "for_founder": {
            "show_this": "Sent to Cursor Worker INBOX — open SourceA Worker chat and RUN INBOX.",
        },
    }


def execute(*, run_id: str, prefer: str = "auto") -> dict[str, Any]:
    """Auto-route: cloud when FREEZE or prefer=cloud; else Cursor INBOX."""
    path = _run_path(run_id)
    doc = _read_json(path)
    if not doc.get("run_id"):
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    blocked = _quality_execution_block(doc)
    if blocked:
        return blocked
    card = doc.get("decision_card") or {}
    dec = str(card.get("decision") or "pending").lower()
    if dec == "rejected":
        return {"ok": False, "error": "decision_rejected", "run_id": run_id}
    if dec == "revise":
        return {
            "ok": False,
            "error": "decision_revise",
            "run_id": run_id,
            "hint": "Revise the mission before execute.",
        }
    pref = (prefer or "auto").lower()
    if dec == "pending":
        decide(run_id=run_id, decision="approved")
    if pref == "cloud" or (pref == "auto" and _freeze_active()):
        return send_to_cloud(run_id=run_id)
    return send_to_cursor(run_id=run_id)


def get_run(*, run_id: str = "") -> dict[str, Any]:
    rid = (run_id or "").strip()
    if not rid:
        latest = _read_json(LATEST)
        rid = str(latest.get("run_id") or "")
    if not rid:
        return status_payload()
    doc = _read_json(_run_path(rid))
    if not doc:
        return {"ok": False, "error": "run_not_found", "run_id": rid}
    ob = _read_json(_outbox_path(rid))
    if ob:
        doc["outbox"] = ob
    return doc


def _body_workspace(body: dict[str, Any]) -> tuple[str | None, str | None]:
    ws_path = str(
        body.get("workspace_path") or body.get("project_root") or body.get("folder") or ""
    ).strip() or None
    ws_id_raw = str(body.get("workspace_id") or body.get("workspace") or "").strip().lower()
    ws_id = ws_id_raw or None
    return ws_path, ws_id


def _default_chat_settings() -> dict[str, Any]:
    return {
        "schema": CHAT_SETTINGS_SCHEMA,
        "default_model": "gpt-4o",
        "default_provider": "auto",
        "fallback_openrouter": True,
        "cloud_worker_url": "http://127.0.0.1:13027/",
        "brain_worker_url": (
            "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1"
        ),
        "chat_unify_url": "http://127.0.0.1:13023/",
        "require_workspace_for_chat": False,
        "extra_models": [],
    }


def chat_settings_get() -> dict[str, Any]:
    row = _default_chat_settings()
    if CHAT_SETTINGS.is_file():
        try:
            disk = json.loads(CHAT_SETTINGS.read_text(encoding="utf-8"))
            if isinstance(disk, dict):
                row.update(disk)
        except Exception:
            pass
    if row.get("default_model") in ("gemini-3.1-flash-lite",):
        row["default_model"] = "gpt-4o"
    pub = ROOT / "apps" / "forge-terminal-v1" / "data" / "forge-terminal-models-public-v1.json"
    models: list[dict[str, Any]] = []
    if pub.is_file():
        try:
            models = json.loads(pub.read_text(encoding="utf-8")).get("models") or []
        except Exception:
            models = []
    return {
        "ok": True,
        "settings": row,
        "path": str(CHAT_SETTINGS),
        "models_public_path": str(pub),
        "models": models,
        "brain_config_path": str(
            ROOT / "SourceA-landing" / "green-unified" / "data" / "sourcea-brain-chat-config-v1.json"
        ),
    }


def chat_settings_save(body: dict[str, Any]) -> dict[str, Any]:
    incoming = body.get("settings") if isinstance(body.get("settings"), dict) else body
    row = _default_chat_settings()
    if isinstance(incoming, dict):
        for key in row:
            if key in incoming:
                row[key] = incoming[key]
        if row.get("default_model") in ("gemini-3.1-flash-lite",):
            row["default_model"] = "gpt-4o"
        if isinstance(incoming.get("extra_models"), list):
            row["extra_models"] = incoming["extra_models"]
    row["schema"] = CHAT_SETTINGS_SCHEMA
    row["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    CHAT_SETTINGS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "settings": row, "path": str(CHAT_SETTINGS)}


def handle_post(body: dict[str, Any]) -> dict[str, Any]:
    ws_path, ws_id = _body_workspace(body)
    action = str(body.get("action") or "run").strip().lower()
    if action == "status":
        if body.get("light"):
            return status_light(workspace_path=ws_path)
        return status_payload(workspace_path=ws_path, workspace_id=ws_id)
    if action == "status_light":
        return status_light(workspace_path=ws_path)
    if action == "workspace_snapshot":
        return workspace_snapshot(workspace_path=ws_path, workspace_id=ws_id)
    if action in ("open_folder", "workspace_open"):
        from forge_workspace_open_v1 import open_folder  # noqa: WPS433

        return open_folder(
            str(body.get("path") or body.get("workspace_path") or ws_path or ""),
            auto_init=bool(body.get("auto_init", True)),
            profile=str(body.get("profile") or "startup"),
        )
    if action == "recent_folders":
        from forge_workspace_open_v1 import list_recent  # noqa: WPS433

        return {"ok": True, "recent": list_recent()}
    if action in ("workspace_clear", "close_folder"):
        from forge_workspace_open_v1 import clear_session  # noqa: WPS433

        return clear_session()
    if action == "workspaces_list":
        from forge_workspace_open_v1 import list_recent  # noqa: WPS433

        return {"ok": True, "recent": list_recent(), "deprecated": "use recent_folders"}
    if action == "run":
        return run_terminal(
            founder_text=str(body.get("text") or body.get("founder_text") or ""),
            use_ai_forge=bool(body.get("use_ai_forge", False)),
            full_llm=bool(body.get("full_llm", True)),
            fast=bool(body.get("fast", body.get("live_chat", True))),
            provider=str(body.get("provider") or body.get("llm_provider") or "auto"),
            model=str(body.get("model") or body.get("llm_model") or ""),
            workspace_id=ws_id,
            workspace_path=ws_path,
        )
    if action == "chat":
        text = str(body.get("text") or "")
        row = run_terminal(
            founder_text=text,
            full_llm=True,
            fast=True,
            provider=str(body.get("provider") or "auto"),
            model=str(body.get("model") or ""),
            workspace_id=ws_id,
            workspace_path=ws_path,
        )
        if row.get("ok"):
            from forge_terminal_desktop_mesh_v1 import append_turn  # noqa: WPS433

            append_turn(
                workspace_path=ws_path,
                role="assistant",
                text=str(row.get("display_response") or row.get("response") or ""),
                meta={
                    "run_id": row.get("run_id"),
                    "model": (row.get("llm") or {}).get("model"),
                    "quality_gate": row.get("quality_gate"),
                    "summary": (row.get("decision_card") or {}).get("summary"),
                    "goal": (row.get("decision_card") or {}).get("goal"),
                },
            )
        return row
    if action == "chat_turn":
        text = str(body.get("text") or "")
        session_id = str(body.get("session_id") or "").strip() or None
        row = run_terminal(
            founder_text=text,
            full_llm=bool(body.get("full_llm", True)),
            fast=bool(body.get("fast", False)),
            provider=str(body.get("provider") or "auto"),
            model=str(body.get("model") or ""),
            workspace_id=ws_id,
            workspace_path=ws_path,
        )
        if row.get("ok"):
            from forge_terminal_desktop_mesh_v1 import append_turn  # noqa: WPS433

            append_turn(
                workspace_path=ws_path,
                role="user",
                text=text,
                meta={"kind": "chat_turn"},
                session_id=session_id,
            )
            append_turn(
                workspace_path=ws_path,
                role="assistant",
                text=str(row.get("display_response") or row.get("response") or ""),
                meta={
                    "run_id": row.get("run_id"),
                    "model": (row.get("llm") or {}).get("model"),
                    "quality_gate": row.get("quality_gate"),
                    "summary": (row.get("decision_card") or {}).get("summary"),
                    "goal": (row.get("decision_card") or {}).get("goal"),
                },
                session_id=session_id,
            )
            row["session_id"] = session_id
        return row
    if action == "chat_thread":
        from forge_terminal_desktop_mesh_v1 import load_thread  # noqa: WPS433

        return load_thread(
            workspace_path=ws_path,
            session_id=str(body.get("session_id") or "").strip() or None,
        )
    if action == "chat_sessions_list":
        from forge_terminal_desktop_mesh_v1 import list_chat_sessions  # noqa: WPS433

        return list_chat_sessions(workspace_path=ws_path)
    if action == "chat_session_create":
        from forge_terminal_desktop_mesh_v1 import create_chat_session  # noqa: WPS433

        return create_chat_session(
            workspace_path=ws_path,
            title=str(body.get("title") or "New chat"),
        )
    if action == "chat_session_delete":
        from forge_terminal_desktop_mesh_v1 import delete_chat_session  # noqa: WPS433

        return delete_chat_session(
            workspace_path=ws_path,
            session_id=str(body.get("session_id") or ""),
        )
    if action == "chat_thread_clear":
        from forge_terminal_desktop_mesh_v1 import clear_thread  # noqa: WPS433

        return clear_thread(
            workspace_path=ws_path,
            session_id=str(body.get("session_id") or "").strip() or None,
        )
    if action == "workspace_read_file":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        rel = str(body.get("path") or body.get("file") or "").strip().lstrip("/")
        if not rel:
            return {"ok": False, "error": "path_required"}
        fp = (root / rel).resolve()
        try:
            fp.relative_to(root.resolve())
        except ValueError:
            return {"ok": False, "error": "path_outside_workspace"}
        if not fp.is_file():
            return {"ok": False, "error": "not_a_file"}
        if fp.stat().st_size > 512_000:
            return {"ok": False, "error": "file_too_large"}
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "path": str(fp), "rel": rel, "content": content}
    if action == "agent_dev_loop":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open", "message": "Open a folder first."}
        from forge_agent_kernel_v1 import run_agent_dev_loop  # noqa: WPS433

        return run_agent_dev_loop(
            goal=str(body.get("goal") or body.get("text") or ""),
            workspace_path=str(root),
            model=str(body.get("model") or ""),
            verifier_model=str(body.get("verifier_model") or ""),
            max_steps=int(body.get("max_steps") or 8),
            dry_run=bool(body.get("dry_run")),
        )
    if action == "agent_self_improve":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open", "message": "Open a folder first."}
        from forge_agent_kernel_v1 import run_self_improve_loop  # noqa: WPS433

        rid = str(body.get("run_id") or "")
        cloud_l3 = bool(body.get("cloud_l3"))
        if rid:
            doc = _read_json(_run_path(rid))
            if not doc.get("run_id"):
                return {"ok": False, "error": "run_not_found", "run_id": rid}
            return run_self_improve_loop(
                workspace_path=str(root),
                quality_gate=doc.get("quality_gate") or {},
                founder_text=str(doc.get("founder_input") or ""),
                response=str(doc.get("display_response") or doc.get("response") or ""),
                run_id=rid,
                model=str(body.get("model") or ""),
                dry_run=bool(body.get("dry_run")),
                cloud_l3=cloud_l3,
            )
        qg = body.get("quality_gate")
        if not isinstance(qg, dict):
            return {"ok": False, "error": "missing_quality_gate_or_run_id"}
        return run_self_improve_loop(
            workspace_path=str(root),
            quality_gate=qg,
            founder_text=str(body.get("text") or body.get("founder_text") or ""),
            response=str(body.get("response") or ""),
            run_id=rid,
            model=str(body.get("model") or ""),
            dry_run=bool(body.get("dry_run")),
            cloud_l3=cloud_l3,
        )
    if action == "agent_swarm_run":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        row = _resolve_swarm_run(body, root)
        if row.get("schema") == "forge-swarm-cloud-dispatch-v1":
            return row
        return row
    if action == "compile_prompt":
        from forge_prompt_os_compiler_v3 import compile_and_dispatch_hint  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        return compile_and_dispatch_hint(
            raw=str(body.get("text") or body.get("goal") or body.get("raw") or ""),
            workspace_path=str(root) if root else str(body.get("workspace_path") or ""),
            adaptive=body.get("adaptive", True) is not False,
        )
    if action == "autonomous_run":
        from forge_prompt_os_compiler_v3 import autonomous_execute  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        return autonomous_execute(
            raw=str(body.get("text") or body.get("goal") or body.get("raw") or ""),
            workspace_path=str(root),
            dry_run=body.get("dry_run", True) is not False,
            cloud=bool(body.get("cloud")),
            adaptive=body.get("adaptive", True) is not False,
            max_steps=int(body.get("max_steps") or 6),
            max_tasks=int(body.get("max_tasks") or 3),
            use_compiled_goal=body.get("use_compiled_goal", True) is not False,
        )
    if action == "legal_arbitrate":
        from forge_governance_legal_v3 import process_violation  # noqa: WPS433

        return process_violation(
            agent_id=str(body.get("agent_id") or "builder-001"),
            agent_role=str(body.get("agent_role") or "builder"),
            action_type=str(body.get("action_type") or "write_file"),
            payload=dict(body.get("payload") or {}),
            violation=str(body.get("violation") or "rule_conflict"),
            checks=list(body.get("checks") or []),
            conflict=body.get("conflict", True) is not False,
            dry_run=body.get("dry_run", True) is not False,
        )
    if action == "legal_appeal":
        from forge_governance_legal_v3 import appeal  # noqa: WPS433

        return appeal(
            str(body.get("case_id") or ""),
            agent_id=str(body.get("agent_id") or "builder-001"),
            dry_run=body.get("dry_run", True) is not False,
        )
    if action == "geo_sign_treaty":
        from forge_geopolitical_legal_v4 import sign_treaty  # noqa: WPS433

        return sign_treaty(
            party_a=str(body.get("party_a") or "nation-sourcea"),
            party_b=str(body.get("party_b") or "nation-cloudforge"),
            terms=list(body.get("terms") or ["mutual_access"]),
            allowed_actions=list(body.get("allowed_actions") or ["read_file", "list_files"]),
        )
    if action == "geo_impose_sanction":
        from forge_geopolitical_legal_v4 import impose_sanction  # noqa: WPS433

        return impose_sanction(
            issuer=str(body.get("issuer") or "nation-sourcea"),
            target=str(body.get("target") or "nation-labs"),
            reason=str(body.get("reason") or "violation"),
            restrictions=list(body.get("restrictions") or []),
            severity=float(body.get("severity") or 0.5),
        )
    if action == "geo_legal_tick":
        from forge_geopolitical_legal_v4 import geo_legal_tick  # noqa: WPS433

        return geo_legal_tick(dry_run=body.get("dry_run", True) is not False)
    if action == "self_build_tick":
        from forge_self_build_v1 import self_build_tick  # noqa: WPS433

        return self_build_tick(dry_run=body.get("dry_run", True) is not False)
    if action == "self_build_safe_evolve":
        from forge_self_build_v2 import safe_evolve_tick  # noqa: WPS433

        return safe_evolve_tick(dry_run=body.get("dry_run", True) is not False)
    if action == "self_build_swarm_evolve":
        from forge_self_build_v3 import swarm_evolve_tick  # noqa: WPS433

        return swarm_evolve_tick(
            dry_run=body.get("dry_run", True) is not False,
            pool_size=int(body.get("pool_size") or 5),
            rounds=int(body.get("rounds") or 2),
        )
    if action == "civilization_code_tick":
        from forge_civilization_code_v4 import civilization_code_tick  # noqa: WPS433

        return civilization_code_tick(dry_run=body.get("dry_run", True) is not False)
    if action == "world_system_tick":
        from forge_world_system_v6 import world_system_tick  # noqa: WPS433

        return world_system_tick(dry_run=body.get("dry_run", True) is not False)
    if action == "planetary_consciousness_tick":
        from forge_planetary_consciousness_v7 import planetary_consciousness_tick  # noqa: WPS433

        return planetary_consciousness_tick(
            dry_run=body.get("dry_run", True) is not False,
            run_world=body.get("run_world", True) is not False,
        )
    if action == "consciousness_status":
        from forge_planetary_consciousness_v7 import consciousness_status  # noqa: WPS433

        return consciousness_status()
    if action == "reality_consciousness_tick":
        from forge_reality_consciousness_v8 import reality_consciousness_tick  # noqa: WPS433

        return reality_consciousness_tick(
            dry_run=body.get("dry_run", True) is not False,
            run_v7=body.get("run_v7", True) is not False,
        )
    if action == "reality_consciousness_status":
        from forge_reality_consciousness_v8 import reality_consciousness_status  # noqa: WPS433

        return reality_consciousness_status()
    if action == "advisor_run":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        goal_text = str(body.get("goal") or body.get("text") or "")
        compiled = None
        if body.get("compile", True) is not False:
            from forge_prompt_os_compiler_v3 import compile_prompt  # noqa: WPS433

            compiled = compile_prompt(raw=goal_text, workspace_path=str(root), adaptive=body.get("adaptive", True) is not False)
            if compiled.get("ok") and body.get("use_compiled_goal"):
                goal_text = str(compiled.get("cursor_mission") or goal_text)
        use_swarm = body.get("swarm", True)
        if use_swarm:
            if body.get("cloud"):
                swarm = _resolve_swarm_run({**body, "goal": goal_text, "text": goal_text}, root)
            else:
                from forge_agent_kernel_v3_swarm import run_swarm_loop  # noqa: WPS433

                swarm = run_swarm_loop(
                    goal=goal_text,
                    workspace_path=str(root),
                    max_tasks=int(body.get("max_tasks") or 5),
                    dry_run=bool(body.get("dry_run")),
                    parallel=body.get("parallel", True) is not False,
                    parallel_build=body.get("parallel_build", True) is not False,
                    planner_count=int(body.get("planner_count") or 3),
                    critic_count=int(body.get("critic_count") or 3),
                )
            if swarm.get("schema") == "forge-swarm-cloud-dispatch-v1":
                out = {
                    "ok": swarm.get("ok"),
                    "schema": "forge-advisor-run-v1",
                    "advisor_id": swarm.get("dispatch_id"),
                    "swarm": True,
                    "cloud": True,
                    "compiled": compiled,
                    "swarm_v3": swarm,
                    "founder_summary": f"Swarm queued to cloud · {swarm.get('cloud_status')}",
                    "at": swarm.get("at"),
                }
                learn = _record_prompt_learning(compiled, out)
                if learn:
                    out["learning"] = learn
                return out
            from forge_advisor_orchestrator_v1 import _founder_summary  # noqa: WPS433

            out = {
                "ok": swarm.get("ok"),
                "schema": "forge-advisor-run-v1",
                "advisor_id": swarm.get("swarm_id"),
                "swarm": True,
                "compiled": compiled,
                "swarm_v3": swarm,
                "agent": {"steps": [], "done": swarm.get("state") == "DONE"},
                "founder_summary": _founder_summary(
                    goal=goal_text,
                    agent_out={"done": swarm.get("state") == "DONE"},
                    gate={},
                    locale=str(body.get("locale") or "en"),
                ),
                "at": swarm.get("at"),
            }
            learn = _record_prompt_learning(compiled, out)
            if learn:
                out["learning"] = learn
            return out
        from forge_advisor_orchestrator_v1 import run_advisor  # noqa: WPS433

        return run_advisor(
            goal=str(body.get("goal") or body.get("text") or ""),
            workspace_path=str(root),
            locale=str(body.get("locale") or "en"),
            run_id=str(body.get("run_id") or ""),
            dry_run=bool(body.get("dry_run")),
            max_steps=int(body.get("max_steps") or 6),
        )
    if action == "agent_self_improve_l3":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        from forge_agent_self_improve_l3_v1 import run_self_improve_cloud  # noqa: WPS433

        qg = body.get("quality_gate") or {}
        if body.get("run_id"):
            doc = _read_json(_run_path(str(body.get("run_id"))))
            qg = doc.get("quality_gate") or qg
        return run_self_improve_cloud(
            run_id=str(body.get("run_id") or ""),
            workspace_path=str(root),
            quality_gate=qg if isinstance(qg, dict) else {},
            founder_text=str(body.get("text") or ""),
            dry_run=bool(body.get("dry_run", True)),
        )
    if action == "desktop_mesh_status":
        from forge_terminal_desktop_mesh_v1 import desktop_mesh_status  # noqa: WPS433

        return desktop_mesh_status(ensure_peers=bool(body.get("ensure_peers")))
    if action == "peer_dispatch":
        from forge_terminal_desktop_mesh_v1 import peer_dispatch  # noqa: WPS433

        return peer_dispatch(peer=str(body.get("peer") or ""), body=body)
    if action == "workspace_ls":
        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        from workspace_kernel_v2 import workspace_ready  # noqa: WPS433

        return {"ok": True, "path": str(root), **workspace_ready(root)}
    if action == "kernel_status":
        from workspace_kernel_v2 import kernel_status  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        return kernel_status(root)
    if action == "agents_list":
        from workspace_kernel_v2 import list_agents  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open", "message": "Open a folder first."}
        return list_agents(root)
    if action == "receipts_list":
        from workspace_kernel_v2 import list_receipts  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        return list_receipts(root, limit=int(body.get("limit") or 30))
    if action == "kernel_init":
        from workspace_kernel_v2 import init_workspace  # noqa: WPS433

        path = str(body.get("path") or body.get("project_root") or ws_path or "")
        if not path:
            wr = _kernel_project_root(ws_id, ws_path)
            if wr:
                path = str(wr)
            else:
                return {"ok": False, "error": "no_workspace_open", "message": "Open a folder first."}
        return init_workspace(
            Path(path),
            name=str(body.get("name") or Path(path).name),
            profile=str(body.get("profile") or "startup"),
        )
    if action == "task_list":
        from workspace_kernel_v2 import list_tasks  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        return list_tasks(root, limit=int(body.get("limit") or 50))
    if action == "events_tail":
        from workspace_kernel_v2 import tail_events  # noqa: WPS433

        root = _kernel_project_root(ws_id, ws_path)
        if not root:
            return {"ok": False, "error": "no_workspace_open"}
        return tail_events(root, limit=int(body.get("limit") or 30))
    if action == "decide":
        return decide(
            run_id=str(body.get("run_id") or ""),
            decision=str(body.get("decision") or ""),
            note=str(body.get("note") or ""),
            workspace_id=ws_id,
            workspace_path=ws_path,
        )
    if action in ("send_cursor", "send_to_cursor"):
        return send_to_cursor(run_id=str(body.get("run_id") or ""))
    if action in ("send_cloud", "cloud_execute", "cloud_forge_run"):
        return send_to_cloud(
            run_id=str(body.get("run_id") or ""),
            dry_run=bool(body.get("dry_run")),
            workspace_id=ws_id,
            workspace_path=ws_path,
        )
    if action in ("execute", "approve_send", "approve_execute"):
        run_id = str(body.get("run_id") or "")
        if body.get("decision") == "approved" or action.startswith("approve"):
            decide(run_id=run_id, decision="approved", workspace_id=ws_id, workspace_path=ws_path)
        prefer = str(body.get("prefer") or body.get("execution") or "auto")
        if action == "approve_send" and body.get("target") == "cursor":
            return send_to_cursor(run_id=run_id)
        if action == "approve_send" and body.get("target") == "cloud":
            return send_to_cloud(run_id=run_id, workspace_id=ws_id, workspace_path=ws_path)
        return execute(run_id=run_id, prefer=prefer)
    if action == "outbox_write":
        return write_outbox(
            run_id=str(body.get("run_id") or ""),
            payload=body.get("payload") if isinstance(body.get("payload"), dict) else {"raw": body.get("payload")},
            source=str(body.get("source") or "cloud_worker"),
        )
    if action == "poll_outbox":
        return poll_outbox(run_id=str(body.get("run_id") or ""))
    if action in ("quality_rerun", "quality_gate_rerun"):
        fl = body.get("full_llm")
        full_llm_flag = None if fl is None else bool(fl)
        return quality_rerun(
            run_id=str(body.get("run_id") or ""),
            founder_text=str(body.get("text") or body.get("founder_text") or ""),
            workspace_path=ws_path,
            full_llm=full_llm_flag if body.get("full_llm") is not None else False,
        )
    if action == "quality_receipt":
        from forge_quality_gate_v1 import load_quality_receipt  # noqa: WPS433

        rid = str(body.get("run_id") or "")
        gate = load_quality_receipt(rid)
        return {"ok": bool(gate), "run_id": rid, "quality_gate": gate}
    if action == "get":
        return get_run(run_id=str(body.get("run_id") or ""))
    if action == "chat_settings_get":
        return chat_settings_get()
    if action == "chat_settings_save":
        return chat_settings_save(body)
    if action == "platform_session_get":
        from forge_user_workspace_v1 import list_user_workspaces, read_platform_session  # noqa: WPS433

        return {
            "ok": True,
            "session": read_platform_session(),
            "workspaces": list_user_workspaces(),
            "session_path": str(Path.home() / ".sina" / "sourcea-platform-session-v1.json"),
        }
    if action == "platform_session_save":
        from forge_user_workspace_v1 import write_platform_session  # noqa: WPS433

        incoming = body.get("session") if isinstance(body.get("session"), dict) else body
        if not isinstance(incoming, dict):
            return {"ok": False, "error": "invalid_session"}
        cur = write_platform_session(incoming)
        return {"ok": True, "session": cur}
    if action == "provision_user_workspace":
        from forge_user_workspace_v1 import provision_user_workspace  # noqa: WPS433

        return provision_user_workspace(
            email=str(body.get("email") or ""),
            name=str(body.get("name") or ""),
            org=str(body.get("org") or ""),
            project_name=str(body.get("project_name") or body.get("project") or ""),
            slug=str(body.get("slug") or body.get("workspace_slug") or ""),
            profile=str(body.get("profile") or "startup"),
        )
    if action == "open_user_workspace":
        from forge_user_workspace_v1 import resolve_user_workspace  # noqa: WPS433

        slug = str(body.get("slug") or body.get("workspace_slug") or "")
        if not slug:
            return {"ok": False, "error": "missing_slug"}
        resolved = resolve_user_workspace(slug)
        if not resolved.get("ok"):
            return resolved
        from forge_workspace_open_v1 import open_folder  # noqa: WPS433

        opened = open_folder(resolved["path"])
        opened["workspace_slug"] = resolved.get("slug")
        return opened
    return {
        "ok": False,
        "error": "unknown_action",
        "actions": [
            "status",
            "status_light",
            "open_folder",
            "workspace_snapshot",
            "run",
            "chat",
            "decide",
            "agent_dev_loop",
            "agent_self_improve",
            "agent_self_improve_l3",
            "advisor_run",
            "compile_prompt",
            "autonomous_run",
            "legal_arbitrate",
            "legal_appeal",
            "geo_sign_treaty",
            "geo_impose_sanction",
            "geo_legal_tick",
            "self_build_tick",
            "self_build_safe_evolve",
            "self_build_swarm_evolve",
            "civilization_code_tick",
            "world_system_tick",
            "planetary_consciousness_tick",
            "consciousness_status",
            "reality_consciousness_tick",
            "reality_consciousness_status",
            "agent_swarm_run",
            "quality_rerun",
            "execute",
            "send_cursor",
            "send_cloud",
            "outbox_write",
            "poll_outbox",
            "get",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Forge Terminal v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--action", default="run")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--decision", default="approved")
    ap.add_argument("--provider", default="auto")
    ap.add_argument("--full-llm", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.action == "run":
        row = run_terminal(founder_text=args.text, full_llm=args.full_llm, provider=args.provider)
    elif args.action == "status":
        row = status_payload()
    elif args.action == "decide":
        row = decide(run_id=args.run_id, decision=args.decision)
    elif args.action == "send_cursor":
        row = send_to_cursor(run_id=args.run_id)
    elif args.action == "send_cloud":
        row = send_to_cloud(run_id=args.run_id)
    elif args.action == "execute":
        row = execute(run_id=args.run_id)
    else:
        row = get_run(run_id=args.run_id)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        card = row.get("decision_card") or {}
        print(card.get("summary") or row.get("message") or row.get("cloud_workers") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
