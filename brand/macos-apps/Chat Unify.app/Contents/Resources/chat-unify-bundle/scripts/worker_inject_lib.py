#!/usr/bin/env python3
"""Deliver Worker prompts — disk INBOX default; batch AUTO-RUN uses clipboard+osascript.

Disk INBOX + rule 099: requires SourceA Worker chat open for rules to fire.
Batch loop (SINA_WORKER_CLIPBOARD_INJECT=1): paste into focused Cursor window (Brain-style).
Law: brain-os/laws/WORKER_CLIPBOARD_INJECT_LOCKED_v1.md
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INBOX_JSON = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
ACTIVE_RULE = ROOT / ".cursor/rules" / "099-worker-inbox-active.mdc"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _loop_auto_enabled() -> bool:
    cfg_path = INBOX_JSON.parent / "loop-specialist-config-v1.json"
    if not cfg_path.is_file():
        return False
    try:
        return bool(json.loads(cfg_path.read_text(encoding="utf-8")).get("loop_auto_dispatch_enabled"))
    except (OSError, json.JSONDecodeError):
        return False


def _outbound_plan_complete() -> bool:
    plan_path = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
    if not plan_path.is_file():
        return False
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        upgrades = plan.get("upgrades") or []
        done = sum(1 for u in upgrades if u.get("status") == "done")
        return len(upgrades) > 0 and done >= len(upgrades)
    except (OSError, json.JSONDecodeError):
        return False


def _outbound_queue_active() -> bool:
    """Outbound factory upgrade drain — kill_flag autorun off must not block ACT."""
    hq_path = INBOX_JSON.parent / "healthy-queue-30-active.json"
    if not hq_path.is_file():
        return False
    try:
        hq = json.loads(hq_path.read_text(encoding="utf-8"))
        if hq.get("stop_reason") == "outbound_factory_complete":
            return bool(_loop_auto_enabled())
        if str(hq.get("thread") or "") == "OUTBOUND-FACTORY":
            return True
        if str(hq.get("product") or "").startswith("Outbound Factory"):
            return True
        queue = hq.get("queue") or []
        if queue and "outbound-factory" in str(queue[0].get("phase") or ""):
            return True
    except (OSError, json.JSONDecodeError):
        pass
    return False


def _smart_loop_active() -> bool:
    """Auto Runtime specialist auto owns ACT delivery — not founder resume / Hub Deliver."""
    if not _loop_auto_enabled():
        return False
    if _outbound_queue_active() or _outbound_plan_complete():
        return True
    hq_path = INBOX_JSON.parent / "healthy-queue-30-active.json"
    if hq_path.is_file():
        try:
            hq = json.loads(hq_path.read_text(encoding="utf-8"))
            if hq.get("queue") and not hq.get("queue_exhausted"):
                return True
        except (OSError, json.JSONDecodeError):
            pass
    return False


def act_blocked_by_freeze(*, queue_role: str = "act") -> dict:
    """Block ACT prompt delivery when kill flag ON and no valid resume token."""
    role = str(queue_role or "act").lower()
    if role not in ("act", "implement", "drain"):
        return {"blocked": False}
    if _smart_loop_active():
        return {
            "blocked": False,
            "prompt_blocked_by_freeze": False,
            "outbound_queue_override": True,
            "smart_loop_override": True,
        }
    sys.path.insert(0, str(SCRIPTS))
    from factory_control_v1 import kill_flag_active, load_factory_now, load_resume_token  # noqa: WPS433

    fn = load_factory_now()
    kill = bool(fn.get("kill_flag")) or kill_flag_active()
    resume = load_resume_token()
    if kill and not resume:
        return {
            "blocked": True,
            "reason": "kill_flag_no_resume",
            "action": "ASF: Cloud Forge Run",
            "prompt_blocked_by_freeze": True,
        }
    return {"blocked": False, "prompt_blocked_by_freeze": False}


TURN_BIND_JSON = Path.home() / ".sina" / "goal1-worker-turn-bind-v1.json"
ACTIVE_TURN_SNAPSHOT_JSON = Path.home() / ".sina" / "goal1-active-turn-snapshot-v1.json"
_BIND_SA_PATTERNS = (
    re.compile(r"\[GOAL1_HEALTHY_DRAIN[^\]]*\bsa=(sa-\d+)", re.I),
    re.compile(r"REGISTRY bind:\s*(sa-\d+)", re.I),
    re.compile(r"role=\w+\s*·\s*sa=(sa-\d+)", re.I),
)


def normalize_sa_id(sa: str) -> str:
    """Normalize B1000 / sa-B1000 / sa-0999 to lowercase sa-* broker form."""
    s = str(sa or "").strip()
    if not s:
        return ""
    if s.lower().startswith("sa-"):
        return s.lower()
    if re.match(r"^B\d{4}$", s, re.I):
        return f"sa-{s}".lower()
    if re.match(r"^\d{4}$", s):
        return f"sa-{s}".lower()
    return s.lower()


def parse_prompt_bind_sa(prompt: str) -> str:
    """Authoritative sa_id from healthy-drain prompt header (meta may drift)."""
    for pat in _BIND_SA_PATTERNS:
        m = pat.search(prompt or "")
        if m:
            return m.group(1).lower()
    return ""


def heal_inbox_meta(meta: dict | None, prompt: str) -> dict:
    """Align meta.sa_id with prompt header — prevents broker sa_mismatch."""
    out = dict(meta or {})
    psa = parse_prompt_bind_sa(prompt)
    if psa:
        out["sa_id"] = normalize_sa_id(psa)
    elif out.get("sa_id"):
        out["sa_id"] = normalize_sa_id(str(out["sa_id"]))
    return out


def clear_idle_turn_artifacts() -> dict:
    """Remove stale turn bind / headsup when queue is lawfully exhausted."""
    cleared: list[str] = []
    idle_bind = {
        "schema": "goal1-worker-turn-bind-v1",
        "sa_id": "",
        "queue_role": "",
        "queue_pos": 0,
        "queue_total": 0,
        "queue_exhausted": True,
        "at": _now(),
    }
    TURN_BIND_JSON.parent.mkdir(parents=True, exist_ok=True)
    TURN_BIND_JSON.write_text(json.dumps(idle_bind, indent=2) + "\n", encoding="utf-8")
    cleared.append(str(TURN_BIND_JSON))
    headsup = Path.home() / ".sina" / "worker-loop-headsup-v1.json"
    if headsup.is_file():
        headsup.write_text(
            json.dumps(
                {
                    "schema": "worker-loop-headsup-v1",
                    "at": _now(),
                    "sa_id": "",
                    "queue_exhausted": True,
                    "note": "Goal 1 idle — no active turn",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        cleared.append(str(headsup))
    try:
        ACTIVE_TURN_SNAPSHOT_JSON.unlink(missing_ok=True)
        cleared.append(str(ACTIVE_TURN_SNAPSHOT_JSON))
    except OSError:
        pass
    return {"ok": True, "cleared": cleared}


def write_turn_bind(*, meta: dict, prompt: str = "") -> dict:
    """Snapshot bind at AGENT START — broker uses this over stale inbox meta."""
    healed = heal_inbox_meta(meta, prompt)
    sa = str(healed.get("sa_id") or "")
    if not sa.startswith("sa-"):
        return {"ok": False, "error": "bind_missing_sa_id"}
    row = {
        "schema": "goal1-worker-turn-bind-v1",
        "sa_id": sa,
        "queue_role": healed.get("queue_role"),
        "queue_pos": healed.get("queue_pos"),
        "queue_total": healed.get("queue_total"),
        "at": _now(),
    }
    TURN_BIND_JSON.parent.mkdir(parents=True, exist_ok=True)
    TURN_BIND_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "bind": row}


def load_turn_bind() -> dict:
    if not TURN_BIND_JSON.is_file():
        return {}
    try:
        return json.loads(TURN_BIND_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_active_turn_snapshot(*, meta: dict, prompt: str = "") -> dict:
    """Immutable bind for agent_cli broker submit — survives INBOX redeliver mid-turn."""
    healed = heal_inbox_meta(meta, prompt)
    sa = str(healed.get("sa_id") or "")
    if not sa.startswith("sa-"):
        return {"ok": False, "error": "snapshot_missing_sa_id"}
    row = {
        "schema": "goal1-active-turn-snapshot-v1",
        "sa_id": sa,
        "queue_role": healed.get("queue_role"),
        "queue_pos": healed.get("queue_pos"),
        "queue_total": healed.get("queue_total"),
        "at": _now(),
    }
    ACTIVE_TURN_SNAPSHOT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_TURN_SNAPSHOT_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "snapshot": row}


def load_active_turn_snapshot() -> dict:
    if not ACTIVE_TURN_SNAPSHOT_JSON.is_file():
        return {}
    try:
        return json.loads(ACTIVE_TURN_SNAPSHOT_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def clear_active_turn_snapshot() -> dict:
    try:
        ACTIVE_TURN_SNAPSHOT_JSON.unlink(missing_ok=True)
    except OSError:
        pass
    return {"ok": True}


def write_active_inbox_rule(text: str, *, meta: dict | None = None) -> dict:
    """Cursor rule so Worker chat sees active turn without clipboard (Brain must refuse)."""
    m = meta or {}
    sa = m.get("sa_id") or "?"
    role = m.get("queue_role") or "?"
    pos = m.get("queue_pos") or "?"
    total = m.get("queue_total") or 30
    assignment_id = m.get("assignment_id") or ""
    execution_plane = m.get("execution_plane") or "cloud_api_worker"
    ssot_line = (
        f"**Assignment:** `{assignment_id}` · **execution_plane:** `{execution_plane}` · "
        f"SSOT: `data/sourcea-worker-professional-assignment-v1.json`\n\n"
        if assignment_id
        else ""
    )
    body = f"""---
description: "Worker INBOX sa-{sa} {role} — attach ONLY to SourceA Worker chat (never Brain)"
alwaysApply: false
globs:
---

# ACTIVE WORKER INBOX (pending)

**Queue:** {pos}/{total} · **role:** {role} · **sa:** {sa}

## You are Worker — execute on first message (do not wait for paste)

```bash
cd ~/Desktop/SourceA && python3 scripts/goal1_lane_broker.py pickup
```

{ssot_line}Read mac_proof receipts (Read tool only) · optional one Hub POST · complete ONE turn · STOP.
Forbidden: validate-* bash chains on Mac.

End with WORKER_ROUND_REPORT YAML +:

```bash
python3 scripts/goal1_lane_broker.py worker-submit --stdin
python3 scripts/worker_inject_lib.py --clear
```

Brain polls: `python3 scripts/goal1_lane_broker.py brain-poll`

---

## Active prompt

{text}
"""
    ACTIVE_RULE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_RULE.write_text(body, encoding="utf-8")
    return {"ok": True, "rule": str(ACTIVE_RULE)}


def clear_active_inbox_rule() -> None:
    if ACTIVE_RULE.is_file():
        ACTIVE_RULE.write_text(
            "---\ndescription: (no active inbox)\nalwaysApply: false\n---\n",
            encoding="utf-8",
        )


def open_inbox_in_editor(*, background: bool = True) -> dict:
    """Open INBOX.md in Cursor editor — no Cmd+V, no chat hijack, no force Worker on top."""
    if not INBOX_MD.is_file():
        return {"ok": False, "error": "inbox_md_missing"}
    path = str(INBOX_MD.resolve())
    # -g: open in background (do not bring Cursor to front / steal focus from current chat).
    cmd = ["open", "-g", "-a", "Cursor", path] if background else ["open", "-a", "Cursor", path]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout or "open failed").strip(), "path": path}
    return {"ok": True, "opened": path, "background": background, "method": "open_g_cursor"}


def _is_worker_chat(hook_input: dict | None) -> bool:
    """Best-effort: only Worker chat gets full prompt on sessionStart."""
    if not hook_input:
        return False
    blob = json.dumps(hook_input).lower()
    worker_markers = (
        "sourcea worker",
        "worker chat",
        "goal1 worker",
        "mandatory_sourcea_worker",
    )
    if any(m in blob for m in worker_markers):
        return True
    # Explicit marker file — founder tags dedicated Worker chat once.
    marker = Path.home() / ".sina" / "worker-chat-marker-v1.json"
    if marker.is_file():
        try:
            m = json.loads(marker.read_text(encoding="utf-8"))
            cid = hook_input.get("conversation_id") or hook_input.get("session_id")
            if cid and cid == m.get("conversation_id"):
                return True
        except (OSError, json.JSONDecodeError):
            pass
    return False


def session_start_context(*, hook_input: dict | None = None) -> dict:
    """sessionStart hook: Worker chat → full prompt; Brain/other → heads-up only."""
    st = inbox_status()
    if not st.get("pending"):
        return {}
    meta = st.get("meta") or {}
    if _is_worker_chat(hook_input):
        try:
            data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
            prompt = (data.get("prompt") or "").strip()
        except (OSError, json.JSONDecodeError):
            prompt = ""
        ctx = f"""WORKER INBOX PENDING — execute this turn in SourceA Worker chat.

Queue: {meta.get('queue_pos', '?')}/{meta.get('queue_total', '?')} · role={meta.get('queue_role', '?')} · sa={meta.get('sa_id', '?')}
Editor: {INBOX_MD}

--- WORKER PROMPT START ---
{prompt}
--- WORKER PROMPT END ---

After STOP: python3 {ROOT}/scripts/worker_inject_lib.py --clear
"""
    else:
        try:
            data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
            prompt = (data.get("prompt") or "").strip()
        except (OSError, json.JSONDecodeError):
            prompt = ""
        ctx = f"""INBOX pending — lane detect required.

**Brain chat:** reply `status: BRAIN_REFUSE_WORKER_PROMPT` only — do NOT execute.
**Worker chat:** execute immediately (user said run inbox or rule 099-worker-inbox-active.mdc is loaded).

Queue: {meta.get('queue_pos', '?')}/{meta.get('queue_total', '?')} · {meta.get('queue_role', '?')} · {meta.get('sa_id', '?')}
Rule: .cursor/rules/099-worker-inbox-active.mdc
Broker poll: python3 scripts/brain_worker_broker_v1.py --poll

--- WORKER PROMPT ---
{prompt}
--- END ---
"""
    return {"additional_context": ctx, "additionalContext": ctx}


def _clipboard_inject_enabled(*, delivery_mode: str = "auto", allow_fallback: bool = False) -> bool:
    if delivery_mode in ("clipboard", "worker_chat"):
        return True
    if delivery_mode == "inbox":
        return False
    if allow_fallback:
        return True
    if os.environ.get("SINA_WORKER_CHAT_RESUME_INJECT", "").strip().lower() in ("1", "true", "yes"):
        return True
    return os.environ.get("SINA_WORKER_CLIPBOARD_INJECT", "").strip().lower() in ("1", "true", "yes")


def paste_into_focused_cursor(
    text: str,
    *,
    caller: str = "worker_inject",
    activate_delay: float = 0.8,
    submit: bool = True,
) -> dict:
    """Paste Worker prompt into frontmost Cursor chat (same mechanism as Brain inject)."""
    allow = os.environ.get("SINA_ALLOW_CURSOR_PASTE", "").strip().lower() in ("1", "true", "yes")
    worker_clip = os.environ.get("SINA_WORKER_CLIPBOARD_INJECT", "").strip().lower() in ("1", "true", "yes")
    if not allow and not worker_clip:
        return {"ok": False, "skipped": True, "reason": "worker_clipboard_inject_disabled"}

    from cursor_window_preflight_v1 import run_cursor_window_preflight  # noqa: WPS433

    preflight = run_cursor_window_preflight(caller=caller, sleep_sec=1.0, target="worker")
    if not preflight.get("ok"):
        return {"ok": False, "reason": "cursor_preflight_failed", "preflight": preflight}
    if preflight.get("focus_steal_skipped"):
        return {
            "ok": True,
            "skipped": True,
            "reason": "cursor_focus_steal_disabled",
            "preflight": preflight,
            "message": "Research mode ON — prompt not pasted; use Worker INBOX or copy manually.",
        }

    proc_read = subprocess.run(["pbpaste"], capture_output=True, check=False)
    backup = proc_read.stdout if proc_read.returncode == 0 else b""
    try:
        subprocess.run(["pbcopy"], input=(text or "").encode("utf-8"), check=False)
        delay = max(0.2, min(float(activate_delay), 2.0))
        keystroke = (
            """
          keystroke return
        """
            if submit
            else ""
        )
        script = f"""
        tell application "Cursor" to activate
        delay {delay}
        tell application "System Events"
          keystroke "v" using command down
          delay 0.25
{keystroke}
        end tell
        """
        proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "osascript inject failed").strip()
            return {"ok": False, "error": err, "clipboard_only": True}
        return {
            "ok": True,
            "injected": True,
            "clipboard_paste": True,
            "method": "osascript_cmd_v",
            "caller": caller,
            "chars": len(text or ""),
        }
    finally:
        if backup:
            subprocess.run(["pbcopy"], input=backup, check=False)


def deliver_to_worker_inbox(
    text: str,
    *,
    source: str = "hub",
    meta: dict | None = None,
    mark_pending: bool = True,
    open_editor: bool = False,
    fast: bool = False,
) -> dict:
    """Write prompt for SourceA Worker — no clipboard, no osascript, no focus steal."""
    sys.path.insert(0, str(SCRIPTS))
    healed_meta_early = heal_inbox_meta(meta, text or "")
    probe_sa = str((healed_meta_early or {}).get("sa_id") or "")
    probe_role = str((healed_meta_early or {}).get("queue_role") or "act")
    freeze_gate = act_blocked_by_freeze(queue_role=probe_role)
    if source != "validate" and freeze_gate.get("blocked"):
        cleared = clear_inbox(reason="freeze_blocked_act_delivery")
        return {
            "ok": True,
            "blocked_by_freeze": True,
            "prompt_blocked_by_freeze": True,
            "action": freeze_gate.get("action"),
            "cleared_inbox": cleared,
            "sa_id": probe_sa,
        }
    if source != "validate" and (probe_sa.endswith("-TEST") or probe_sa == "sa-TEST"):
        return {"ok": False, "error": "SA_TEST_REJECTED", "sa_id": probe_sa}
    from duplicate_inject_guard_v1 import preflight_inject  # noqa: WPS433

    guard = preflight_inject(meta=healed_meta_early, source=source, prompt=text or "")
    if guard.get("blocked"):
        return {
            "ok": False,
            "error": guard.get("reason") or "DUPLICATE_INJECT_BLOCKED",
            "action": guard.get("action"),
            "duplicate_guard": guard,
            "law": "NO_DUPLICATE_INJECT_LOCKED_v1.md",
        }

    from authority_enforce_p1_lib import (  # noqa: WPS433
        check_prompt_pick_authority,
        check_rail_manual_inject,
        check_reconciled_before_inject,
        check_tracker_operational,
    )

    tracker_gate = check_tracker_operational()
    if not tracker_gate.get("ok"):
        return {"ok": False, "authority_p1": tracker_gate}

    if not fast:
        from cursor_window_preflight_v1 import run_worker_chat_preflight  # noqa: WPS433

        preflight = run_worker_chat_preflight(caller=f"worker_inject:{source}")
        if not preflight.get("ok"):
            return {"ok": False, "preflight": preflight, "error": "CURSOR_WINDOW_PREFLIGHT_FAILED"}

    rail_gate = check_rail_manual_inject(source=source)
    if not rail_gate.get("ok"):
        return {"ok": False, "authority_p1": rail_gate}

    pick_gate = check_prompt_pick_authority(text=text, source=source, meta=meta)
    if not pick_gate.get("ok"):
        return {"ok": False, "authority_p1": pick_gate}

    sa_probe = str((meta or {}).get("sa_id") or "")
    recon_gate = check_reconciled_before_inject(source=source, sa_id=sa_probe or None)
    if not recon_gate.get("ok"):
        return {"ok": False, "authority_p1": recon_gate}

    if sa_probe:
        from healthy_queue_ssot_lib import sa_closeout_complete  # noqa: WPS433

        if sa_closeout_complete(sa_probe):
            return {
                "ok": False,
                "error": "SA_ALREADY_CLOSEDOUT",
                "sa_id": sa_probe,
                "hint": "Receipt DONE + REGISTRY done — queue poison blocked",
                "law": "REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
            }

    try:
        from founder_directive_ssot_v1 import block_hub_item, hub_closed  # noqa: WPS433

        if hub_closed():
            from founder_directive_ssot_v1 import _resolve_item_phase  # noqa: WPS433

            phase = _resolve_item_phase(sa_probe, str((meta or {}).get("phase") or ""))
            blocked, reason = block_hub_item({"sa_id": sa_probe, "phase": phase})
            if blocked:
                return {
                    "ok": False,
                    "error": "HUB_CLOSED_LATCH",
                    "hint": reason,
                    "law": "INCIDENT-031 · founder_directive_ssot",
                }
    except Exception:
        pass

    healed_meta = heal_inbox_meta(meta, text or "")
    payload = {
        "schema": "worker-prompt-inbox-v1",
        "pending": mark_pending,
        "delivered_at": _now(),
        "source": source,
        "lane": "sourcea_worker",
        "workspace": str(ROOT),
        "chars": len(text or ""),
        "prompt": text or "",
        "meta": healed_meta,
        "pickup": {
            "founder_line": "Founder says RUN INBOX — read disk · no Hub · no app",
            "inbox_json": str(INBOX_JSON),
            "inbox_md": str(INBOX_MD),
            "law": "RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md",
        },
    }
    INBOX_JSON.parent.mkdir(parents=True, exist_ok=True)
    INBOX_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    header = healed_meta
    pos = header.get("queue_pos", "?")
    total = header.get("queue_total", "?")
    role = header.get("queue_role", "?")
    sa = header.get("sa_id", "?")

    md = f"""<!-- WORKER_INBOX pending=1 source={source} queue={pos}/{total} role={role} sa={sa} -->
# SourceA Worker — prompt ready (INBOX delivery)

**Do not expect clipboard paste.** Hub/autoloop wrote this file so Brain chat is not hijacked.

**Lane:** SourceA Worker only — if you are Brain, ignore this file.

**Updated:** {payload["delivered_at"]}

---

{text}

---

**Worker:** execute fully · `WORKER_ROUND_REPORT` · STOP  
**Founder:** stay in Brain or Hub — open Worker chat when ready; no Terminal
"""
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(md, encoding="utf-8")
    # AUTO-RUN: pop Worker editor foreground before inject (never background -g on batch path).
    editor = {"ok": True, "skipped": True, "reason": "deferred_to_worker_chat_pop"}
    if (
        not fast
        and os.environ.get("SINA_WORKER_CHAT_RESUME_INJECT", "").strip().lower() in ("1", "true", "yes")
    ):
        try:
            from worker_chat_inject_v1 import pop_worker_editor_window  # noqa: WPS433

            editor = pop_worker_editor_window(caller=f"deliver_inbox:{source}")
        except Exception as exc:
            editor = {"ok": False, "error": str(exc)}
    elif open_editor:
        editor = open_inbox_in_editor(background=False)

    try:
        from brain_lane_guard import write_loop_headsup  # noqa: WPS433

        write_loop_headsup(
            queue_pos=int((meta or {}).get("queue_pos") or 0) or 1,
            queue_total=int((meta or {}).get("queue_total") or 0) or 30,
            role=str((meta or {}).get("queue_role") or "check"),
            sa_id=str((meta or {}).get("sa_id") or ""),
        )
    except Exception:
        pass

    rule = write_active_inbox_rule(text, meta=healed_meta)

    try:
        from execution_event_log_v1 import append_event  # noqa: WPS433

        append_event(
            event="INBOX_DELIVERED",
            actor="healthy-drain-orchestrator" if source == "healthy-drain-orchestrator" else "broker_validators",
            data={
                "source": source,
                "sa_id": healed_meta.get("sa_id"),
                "queue_role": healed_meta.get("queue_role"),
                "chars": payload["chars"],
            },
        )
    except Exception:
        pass

    return {
        "ok": True,
        "delivered": "inbox",
        "injected": False,
        "clipboard_paste": False,
        "reason": "worker_inbox_delivery",
        "message": (
            "Founder says RUN INBOX — prompt logged · no Hub · no app · read inbox JSON",
            "(editor tab NOT opened — that was not loop start)"
        ),
        "inbox_json": str(INBOX_JSON),
        "inbox_md": str(INBOX_MD),
        "editor_open": editor,
        "active_rule": rule.get("rule"),
        "chars": payload["chars"],
        "clipboard_paste": False,
        "focus_steal": False,
    }


def inbox_status() -> dict:
    if not INBOX_JSON.is_file():
        return {"ok": True, "pending": False}
    try:
        data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "pending": False, "error": "corrupt inbox"}
    meta = data.get("meta") or {}
    qpos = meta.get("queue_pos")
    qtotal = meta.get("queue_total")
    return {
        "ok": True,
        "pending": bool(data.get("pending")),
        "delivered_at": data.get("delivered_at"),
        "source": data.get("source"),
        "meta": meta,
        "sa_id": meta.get("sa_id"),
        "queue_role": meta.get("queue_role"),
        "queue": f"{qpos}/{qtotal}" if qpos and qtotal else None,
        "chars": data.get("chars"),
        "prompt": data.get("prompt") or "",
        "preview": (data.get("prompt") or "")[:200],
    }


def _orchestrator_idle_if_orphaned() -> None:
    """INBOX cleared without worker-submit — orchestrator must not stay awaiting_worker."""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "orch", ROOT / "scripts/healthy-drain-orchestrator-v1.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        st = mod.orchestrator_state()
        if st.get("status") == "awaiting_worker":
            mod.reset(reason="inbox_cleared")
    except Exception:
        return


def _cleared_inbox_header(*, sa_id: str, role: str, pos: int, total: int, source: str) -> str:
    return (
        f"<!-- WORKER_INBOX pending=0 source={source} "
        f"queue={pos}/{total} role={role} sa={sa_id} -->\n"
        "# SourceA Worker — INBOX cleared\n\n"
        "**Lane:** SourceA Worker only — if you are Brain, ignore this file.\n\n"
        f"**Updated:** {_now()}\n\n"
        "---\n\n"
        f"No pending turn. Next queue head: **{sa_id}** ({role}) · {pos}/{total}.\n"
    )


def _queue_head_for_cleared_inbox() -> tuple[str, str, int, int]:
    """Best-effort SSOT for cleared INBOX header (avoids sa-TEST drift)."""
    sa_id, role, pos, total = "", "", 1, 0
    try:
        sys.path.insert(0, str(SCRIPTS))
        from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

        head = queue_head()
        pos = int(head.get("pos") or 1)
        total = int(head.get("total") or 0)
        sa_id = str(head.get("sa_id") or "")
        role = str(head.get("role") or "")
        if head.get("queue_exhausted") or sa_id:
            return sa_id, role, pos, total
    except Exception:
        pass
    state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
    queue_path = Path.home() / ".sina" / "healthy-queue-30-active.json"
    try:
        if queue_path.is_file():
            q = json.loads(queue_path.read_text(encoding="utf-8"))
            items = q.get("queue") or []
            total = len(items) or total
            pos = 1
            if state_path.is_file():
                pos = int(json.loads(state_path.read_text()).get("next_pos") or 1)
            if 1 <= pos <= len(items):
                item = items[pos - 1]
                sa_id = str(item.get("sa_id") or sa_id)
                role = str(item.get("queue_role") or role)
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        pass
    return sa_id, role, pos, total


def ensure_inbox_shell(*, reason: str = "ensure_inbox_shell") -> dict:
    """Create cleared worker-prompt-inbox-v1.json when missing (hub_closed / post-clear drift)."""
    if INBOX_JSON.is_file():
        return {"ok": True, "created": False, "reason": "exists"}
    sa_id, role, pos, total = _queue_head_for_cleared_inbox()
    directive_stub = ""
    try:
        from founder_directive_ssot_v1 import truth_block_lines  # noqa: WPS433

        lines = truth_block_lines()
        if lines:
            directive_stub = "\n".join(lines) + "\n"
    except Exception:
        pass
    stub = (
        f"INBOX cleared ({reason}) · pending=false · next head {sa_id} {role} {pos}/{total}\n"
        f"{directive_stub}"
    ).strip() + "\n"
    payload = {
        "schema": "worker-prompt-inbox-v1",
        "pending": False,
        "prompt": stub,
        "chars": len(stub),
        "sa_id": sa_id,
        "meta": {
            "sa_id": sa_id,
            "queue_role": role,
            "queue_pos": pos,
            "queue_total": total,
            "healed_at": _now(),
            "heal_reason": reason,
        },
        "source": reason,
        "cleared_at": _now(),
    }
    INBOX_JSON.parent.mkdir(parents=True, exist_ok=True)
    INBOX_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(
        _cleared_inbox_header(sa_id=sa_id, role=role, pos=pos, total=total, source=reason),
        encoding="utf-8",
    )
    return {"ok": True, "created": True, "reason": reason, "sa_id": sa_id, "queue_pos": pos}


def clear_inbox(*, reason: str = "worker_ack") -> dict:
    sa_id, role, pos, total = _queue_head_for_cleared_inbox()
    if not INBOX_JSON.is_file():
        ensure_inbox_shell(reason=reason)
    if INBOX_JSON.is_file():
        try:
            data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
            data["pending"] = False
            data["cleared_at"] = _now()
            data["clear_reason"] = reason
            directive_stub = ""
            try:
                from founder_directive_ssot_v1 import truth_block_lines  # noqa: WPS433

                lines = truth_block_lines()
                if lines:
                    directive_stub = "\n".join(lines) + "\n"
            except Exception:
                pass
            stub = (
                f"INBOX cleared ({reason}) · pending=false · next head {sa_id} {role} {pos}/{total}\n"
                f"{directive_stub}"
            ).strip() + "\n"
            data["prompt"] = stub
            data.pop("preview", None)
            data["chars"] = len(stub)
            data["meta"] = {
                "queue_pos": pos,
                "queue_total": total,
                "queue_role": role,
                "sa_id": sa_id,
            }
            data["sa_id"] = sa_id
            if reason == "brain_outbound_work_order":
                data["pickup"] = {
                    "hub": "Worker Hub → Next steps · Brain work-order active",
                    "ignore_if_brain": True,
                }
            INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(
        _cleared_inbox_header(
            sa_id=sa_id,
            role=role,
            pos=pos,
            total=total,
            source=reason,
        ),
        encoding="utf-8",
    )
    clear_active_inbox_rule()
    if reason != "broker_worker_submit":
        _orchestrator_idle_if_orphaned()
    return {"ok": True, "cleared": True, "reason": reason, "sa_id": sa_id, "queue_pos": pos}


def inject_worker_prompt(
    text: str,
    *,
    source: str = "hub",
    meta: dict | None = None,
    allow_clipboard_fallback: bool = False,
    delivery_mode: str = "auto",
    fast: bool = False,
) -> dict:
    """Default: manual Worker — no inject. Auto only with worker-auto-inject-v1.flag."""
    from worker_manual_only_v1 import is_manual_only, manual_hint  # noqa: WPS433

    if is_manual_only():
        m = meta or {}
        return {
            "ok": True,
            "skipped_inject": True,
            "mode": "manual_only",
            "injected": False,
            "clipboard_paste": False,
            "message": manual_hint(
                sa_id=str(m.get("sa_id") or ""),
                role=str(m.get("queue_role") or ""),
                pos=f"{m.get('queue_pos')}/{m.get('queue_total')}",
            ),
        }

    result = deliver_to_worker_inbox(text, source=source, meta=meta, fast=fast)
    if not result.get("ok"):
        return result

    if fast:
        return result

    use_worker_chat = _clipboard_inject_enabled(
        delivery_mode=delivery_mode,
        allow_fallback=allow_clipboard_fallback,
    ) or delivery_mode == "worker_chat"
    if not use_worker_chat:
        return result

    from worker_chat_inject_v1 import inject_into_worker_chat  # noqa: WPS433

    inj = inject_into_worker_chat(
        text,
        caller=f"worker_inject:{source}",
        execute=False,
    )
    result["worker_chat_inject"] = inj
    result["clipboard_paste"] = False
    result["injected"] = bool(inj.get("ok"))
    result["delivery"] = "inbox+worker_chat_resume" if inj.get("ok") else "inbox_only"
    result["conversation_id"] = inj.get("conversation_id")
    result["message"] = (
        f"Worker chat {inj.get('conversation_id')} focused via agent --resume + INBOX logged. "
        "Batch run_turn executes in Worker chat only — never Brain."
        if inj.get("ok")
        else f"INBOX logged — worker chat focus failed: {inj.get('error') or inj.get('stderr')}"
    )
    return result


def main() -> int:
    import argparse
    import os

    p = argparse.ArgumentParser(description="Worker inbox inject (no wrong-chat paste)")
    p.add_argument("--status", action="store_true")
    p.add_argument("--clear", action="store_true")
    p.add_argument("--open-editor", action="store_true", help="Open INBOX.md in editor (background)")
    p.add_argument("--session-start", action="store_true", help="Cursor sessionStart hook output")
    p.add_argument("--mark-worker-chat", metavar="CONVERSATION_ID", help="Tag this chat as Worker")
    p.add_argument("--stdin", action="store_true", help="Read prompt body from stdin")
    p.add_argument("--source", default="cli")
    args = p.parse_args()

    if args.status:
        print(json.dumps(inbox_status(), indent=2))
        return 0
    if args.clear:
        print(json.dumps(clear_inbox(), indent=2))
        return 0
    if args.open_editor:
        print(json.dumps(open_inbox_in_editor(background=True), indent=2))
        return 0
    if args.session_start:
        raw = os.environ.get("WORKER_HOOK_INPUT") or ""
        hook_input = {}
        if raw.strip():
            try:
                hook_input = json.loads(raw)
            except json.JSONDecodeError:
                hook_input = {}
        out = session_start_context(hook_input=hook_input)
        print(json.dumps(out if out else {}))
        return 0
    if args.mark_worker_chat:
        marker = Path.home() / ".sina" / "worker-chat-marker-v1.json"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps(
                {
                    "conversation_id": args.mark_worker_chat,
                    "marked_at": _now(),
                    "law": "SourceA Worker dedicated chat",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"ok": True, "marked": args.mark_worker_chat}, indent=2))
        return 0
    body = sys.stdin.read() if args.stdin else ""
    if not body.strip():
        print("FAIL: empty prompt", file=sys.stderr)
        return 1
    print(json.dumps(inject_worker_prompt(body, source=args.source), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
