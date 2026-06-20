#!/usr/bin/env python3
"""AI direction + optional commentary outline from last chat response — confirm stamps only."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
STATE_PATH = Path.home() / ".sina" / "prompt-direction.json"
PROMPTOS = Path.home() / "Desktop" / "SinaPromptOS"

PROPOSE_SYSTEM = """You are the Sina OS session planner for founder ASF.
You receive the AI's LAST reply in a Cursor meta/planning chat and optional live command snapshot.
Your job: show the BIG PICTURE direction (~what happens next) before any work runs.

Output ONLY valid JSON (no markdown fences):
{
  "direction_title": "short headline (6-12 words)",
  "big_picture": "3-5 sentences: overall direction, threads, what success looks like",
  "connection_to_last_reply": "2 sentences: how this plan directly continues the last AI response",
  "prompt_outline": [
    {
      "step": 1,
      "title": "short label",
      "repo": null or "trustfield"|"sinaai_mono"|"virlux"|"noetfield"|"seven77",
      "thread": "THREAD-..." or null,
      "intent": "one sentence — what this Cursor prompt accomplishes"
    }
  ]
}
Rules:
- Exactly 10 items in prompt_outline, numbered step 1..10.
- Each step must logically follow from the previous and from the last reply (not generic todos).
- Mix repos only when the last reply implies multi-repo work; else keep repo null for meta chat.
- Respect THREAD boundaries (factory vs wire vs mergepack revenue)."""


GENERATE_SYSTEM = """You are the Sina OS prompt writer for founder ASF.
You receive: last AI reply, approved big picture, and a 10-step outline.
Write 10 FULL Cursor prompts (self-contained: scope, done criteria, IMPLEMENT-style clarity).

Output ONLY valid JSON:
{
  "prompts": [
    {
      "step": 1,
      "title": "same as outline title",
      "repo": null or repo id,
      "thread": "THREAD-..." or null,
      "text": "full prompt text to paste into Cursor (200-800 words ok, be specific)"
    }
  ]
}
Rules:
- Exactly 10 prompts, matching the outline order and intent.
- Each text must reference specifics from the last reply and big picture (not boilerplate).
- Do not tell the human to open Terminal."""


def _load_state() -> dict:
    if not STATE_PATH.is_file():
        return {"status": "idle", "last_response": "", "user_note": "", "proposal": None}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(data: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        STATE_PATH.chmod(0o600)
    except OSError:
        pass


def _parse_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None


def _chat(system: str, user: str) -> tuple[bool, str]:
    sys.path.insert(0, str(PROMPTOS))
    try:
        from core.openrouter_client import chat_completion  # noqa: WPS433

        return chat_completion(system=system, user=user, temperature=0.35, timeout=120)
    except Exception as e:
        return False, str(e)


def _has_openrouter() -> bool:
    from sina_ai_advisory import _load_vault_key  # noqa: WPS433

    return bool(_load_vault_key())


def direction_payload() -> dict:
    st = _load_state()
    prop = st.get("proposal")
    last = st.get("last_response") or ""
    live: dict = {}
    try:
        from live_prompt_overrides_v1 import payload as live_payload  # noqa: WPS433

        live = live_payload()
    except Exception as exc:
        live = {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "status": st.get("status", "idle"),
        "last_response_preview": last[:400],
        "last_response_text": last,
        "has_last_response": bool(last.strip()),
        "user_note": st.get("user_note") or "",
        "proposal": prop,
        "confirmed_at": st.get("confirmed_at"),
        "generated_at": st.get("generated_at"),
        "error": st.get("error"),
        "live_ongoing_prompts": live.get("live_ongoing_prompts") or {},
        "live_overrides": live.get("overrides") or {},
        "machine_order_ssot": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
    }


def set_context(*, last_response: str, user_note: str = "") -> dict:
    text = (last_response or "").strip()
    if not text:
        return {"ok": False, "error": "last_response required"}
    st = _load_state()
    st["last_response"] = text[:80000]
    st["user_note"] = (user_note or "").strip()[:2000]
    st["proposal"] = None
    st["status"] = "idle"
    st["error"] = None
    _save_state(st)
    return {"ok": True, "message": "Last response saved — tap See big picture", "has_last_response": True}


def propose_direction(*, payload: dict | None = None) -> dict:
    if not _has_openrouter():
        return {
            "ok": False,
            "error": "OpenRouter not configured — add key to ~/.sina/secrets.env",
        }
    st = _load_state()
    last = (st.get("last_response") or "").strip()
    if not last:
        return {"ok": False, "error": "Save the AI last response first"}

    snap = {}
    if payload:
        from sina_ai_advisory import build_snapshot  # noqa: WPS433

        snap = build_snapshot(payload)

    from execution_intelligence.planner_influence import planner_context_block  # noqa: WPS433

    user_msg = json.dumps(
        {
            "last_ai_response": last[:12000],
            "founder_note": st.get("user_note") or "",
            "command_snapshot": snap,
            **planner_context_block(),
        },
        indent=2,
        ensure_ascii=False,
    )[:16000]

    ok, raw = _chat(PROPOSE_SYSTEM, user_msg)
    if not ok:
        st["error"] = raw
        _save_state(st)
        return {"ok": False, "error": raw}

    parsed = _parse_json(raw)
    if not parsed or not parsed.get("prompt_outline"):
        st["error"] = "AI did not return a valid direction plan"
        _save_state(st)
        return {"ok": False, "error": st["error"], "_raw": raw[:2000]}

    outline = parsed.get("prompt_outline") or []
    if len(outline) < 10:
        return {"ok": False, "error": f"Expected 10 outline steps, got {len(outline)}"}

    parsed["prompt_outline"] = outline[:10]
    st["proposal"] = parsed
    st["status"] = "proposed"
    st["generated_at"] = datetime.now(timezone.utc).isoformat()
    st["error"] = None
    _save_state(st)
    return {
        "ok": True,
        "proposal": parsed,
        "message": "Optional commentary ready — machine execution order unchanged",
    }


def confirm_and_launch(
    *,
    payload: dict | None = None,
    auto_paste: bool = True,
    deliver_first: bool = False,
) -> dict:
    """Save optional commentary stamp from approved outline — machine queue SSOT unchanged."""
    if not _has_openrouter():
        return {"ok": False, "error": "OpenRouter not configured"}

    from prompt_queue import (  # noqa: WPS433
        add_prompts_batch,
        clear_queue,
        deliver_next,
        set_auto_feed,
    )

    st = _load_state()
    prop = st.get("proposal")
    if not prop or st.get("status") != "proposed":
        return {"ok": False, "error": "No proposal to confirm — run See big picture first"}

    last = (st.get("last_response") or "")[:12000]
    user_msg = json.dumps(
        {
            "last_ai_response": last,
            "approved_direction": prop,
        },
        indent=2,
        ensure_ascii=False,
    )[:20000]

    ok, raw = _chat(GENERATE_SYSTEM, user_msg)
    if not ok:
        return {"ok": False, "error": raw}

    parsed = _parse_json(raw)
    prompts = (parsed or {}).get("prompts") or []
    if len(prompts) < 10:
        return {"ok": False, "error": f"Expected 10 prompts, got {len(prompts)}", "_raw": raw[:1500]}

    items = []
    for p in prompts[:10]:
        items.append({
            "title": f"Step {p.get('step', len(items)+1)}: {p.get('title', 'Prompt')}",
            "repo": p.get("repo"),
            "thread": p.get("thread"),
            "text": p.get("text") or "",
            "source": "direction_confirmed",
        })

    # Optional commentary only — machine execution order stays on healthy queue SSOT.
    st["status"] = "commentary_confirmed"
    st["confirmed_at"] = datetime.now(timezone.utc).isoformat()
    st["commentary_prompts"] = items
    _save_state(st)
    try:
        from live_prompt_overrides_v1 import handle_action as override_action  # noqa: WPS433

        override_action({"action": "confirm"})
    except Exception:
        pass
    return {
        "ok": True,
        "message": "Optional commentary stamp saved — machine order unchanged (live ongoing prompts SSOT).",
        "prompt_count": 10,
        "auto_feed": False,
        "execution_ssot": "live-ongoing-prompts-next-10-v1.json",
        "first_delivery": None,
    }


def cancel_proposal() -> dict:
    st = _load_state()
    st["proposal"] = None
    st["status"] = "idle"
    st["error"] = None
    _save_state(st)
    return {"ok": True, "message": "Direction cancelled"}


def handle_action(body: dict, *, payload: dict | None = None) -> dict:
    action = (body.get("action") or "status").strip().lower()
    if action == "status":
        return direction_payload()
    if action == "set_context":
        return set_context(last_response=body.get("last_response", ""), user_note=body.get("user_note", ""))
    if action == "propose":
        return propose_direction(payload=payload)
    if action == "confirm":
        return confirm_and_launch(
            payload=payload,
            auto_paste=body.get("paste", True),
            deliver_first=bool(body.get("deliver_first")),
        )
    if action == "cancel":
        return cancel_proposal()
    if action in ("live_override", "override", "live_overrides"):
        from live_prompt_overrides_v1 import handle_action as override_action  # noqa: WPS433

        obody = dict(body)
        sub = body.get("override_action") or body.get("sub_action")
        if sub:
            obody["action"] = sub
        return override_action(obody)
    if action == "live_rebuild":
        from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

        return rebuild(write=True)
    return {"ok": False, "error": f"unknown action: {action}"}
