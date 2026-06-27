#!/usr/bin/env python3
"""Forge Advisor Orchestrator v1 — PLAN → ACT → VERIFY → GATE (bilingual)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-advisor-latest-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _plan_phase(*, goal: str, locale: str) -> dict[str, Any]:
    from model_dispatch import pick_roi_model  # noqa: WPS433

    model = pick_roi_model("reason")
    prompt = f"Goal: {goal}\nLocale: {locale}\nReply JSON only: {{\"plan\": \"3-5 step plan\", \"risks\": [\"...\"]}}"
    try:
        from ai_unify_api_v1 import chat_completion  # noqa: WPS433

        row = chat_completion(
            messages=[
                {"role": "system", "content": "You are a senior advisor. Output JSON only."},
                {"role": "user", "content": prompt},
            ],
            model=model,
            source="forge-advisor-plan",
        )
        text = str(row.get("text") or row.get("content") or "")
        start = text.find("{")
        end = text.rfind("}") + 1
        parsed = json.loads(text[start:end]) if start >= 0 and end > start else {"plan": goal}
        return {"ok": True, "phase": "PLAN", "model": model, "parsed": parsed}
    except Exception as exc:
        return {"ok": True, "phase": "PLAN", "model": model, "parsed": {"plan": goal}, "fallback": str(exc)[:120]}


def _founder_summary(*, goal: str, agent_out: dict[str, Any], gate: dict[str, Any], locale: str) -> str:
    try:
        from chat_founder_language_v1 import translate_for_founder  # noqa: WPS433

        raw = (
            f"Goal: {goal}\nAgent done: {agent_out.get('done')}\n"
            f"Quality: {gate.get('verdict')} ({gate.get('passed_layers')}/{gate.get('total_layers')})"
        )
        row = translate_for_founder(
            draft=raw,
            founder_message=goal,
            prefer_ai=True,
        )
        return str(row.get("founder_text") or row.get("display") or row.get("text") or raw)
    except Exception:
        return f"Advisor complete · gate {gate.get('verdict', '?')}"


def run_advisor(
    *,
    goal: str,
    workspace_path: str,
    locale: str = "en",
    run_id: str = "",
    dry_run: bool = False,
    max_steps: int = 6,
) -> dict[str, Any]:
    """Full advisor cycle: plan → agent act → verify harness → quality gate."""
    from forge_agent_kernel_v1 import run_agent_dev_loop, run_verify_harness_static  # noqa: WPS433

    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "empty_goal"}

    root = Path(workspace_path).expanduser().resolve()
    if not root.is_dir():
        return {"ok": False, "error": "invalid_workspace", "path": workspace_path}

    advisor_id = f"adv-{uuid.uuid4().hex[:10]}"
    locale = (locale or "en").lower()[:2]
    phases: list[dict[str, Any]] = []

    plan = _plan_phase(goal=goal, locale=locale)
    phases.append(plan)
    plan_text = str((plan.get("parsed") or {}).get("plan") or goal)

    agent_out = run_agent_dev_loop(
        goal=f"{plan_text}\n\nOriginal: {goal}",
        workspace_path=str(root),
        max_steps=max_steps,
        dry_run=dry_run,
    )
    phases.append({"ok": agent_out.get("ok"), "phase": "ACT", "agent_run_id": agent_out.get("run_id"), "steps": len(agent_out.get("steps") or [])})

    harness = run_verify_harness_static(workspace_path=str(root))
    phases.append({"ok": harness.get("ok"), "phase": "VERIFY", **harness})

    gate: dict[str, Any] = {}
    if run_id and not dry_run:
        from forge_terminal_v1 import quality_rerun  # noqa: WPS433

        qr = quality_rerun(run_id=run_id, founder_text=goal, workspace_path=str(root), full_llm=False)
        gate = qr.get("quality_gate") or {}
        phases.append({"ok": qr.get("ok"), "phase": "GATE", "verdict": gate.get("verdict")})
    else:
        phases.append({"ok": True, "phase": "GATE", "verdict": "SKIP", "note": "no run_id or dry_run"})

    summary = _founder_summary(goal=goal, agent_out=agent_out, gate=gate, locale=locale)
    out = {
        "ok": bool(agent_out.get("ok")),
        "schema": "forge-advisor-run-v1",
        "advisor_id": advisor_id,
        "run_id": run_id,
        "goal": goal,
        "locale": locale,
        "workspace_path": str(root),
        "phases": phases,
        "agent": agent_out,
        "verify_harness": harness,
        "quality_gate": gate,
        "founder_summary": summary,
        "at": _now(),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
