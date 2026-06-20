#!/usr/bin/env python3
"""Plain-English Hub home payload — ASF HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
BROKER_EVENTS = Path.home() / ".sina" / "goal1-lane-broker-events.jsonl"
EVENT_BUS = Path.home() / ".sina" / "events_v1.jsonl"
SCHEMA = "hub-home-founder-v2-light"
SCHEMA_FULL = "hub-home-founder-v1"

_EVENT_LABELS: dict[str, str] = {
    "INBOX_DELIVERED": "Worker inbox updated — next task ready",
    "DECISION_RECONCILED": "Brain chose next queue item",
    "BATCH_START": "Started automated batch",
    "WORKER_SUBMIT": "Worker finished a round",
    "WORKER_SUBMIT_AUTO": "Worker auto-submitted a round",
    "BROKER_ACCEPT": "Broker approved delivery",
    "BROKER_REJECT": "Broker blocked delivery — check run inbox / factory-now",
    "VALIDATOR_PASS": "Validators passed",
    "VALIDATOR_FAIL": "Validators failed — see Backlog",
    "AGENT_START": "Agent run started",
    "AGENT_STOP": "Agent run stopped",
    "BOUNDARY_TEST": "Authority check ran",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _tail_jsonl(path: Path, *, n: int = 20) -> list[dict]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    out: list[dict] = []
    for line in lines[-n * 2 :]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out[-n:]


def _daily_events(*, n: int = 12) -> list[dict]:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = Path.home() / ".sina" / "events" / f"{day}.jsonl"
    return _tail_jsonl(path, n=n)


def _format_time(at: str) -> str:
    if not at:
        return "—"
    try:
        if at.endswith("Z"):
            at = at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(at)
        return dt.strftime("%H:%M")
    except ValueError:
        return at[:5] if len(at) >= 5 else at


def _plain_event_label(row: dict) -> str:
    kind = row.get("kind") or row.get("event") or ""
    if kind in _EVENT_LABELS:
        base = _EVENT_LABELS[kind]
        data = row.get("data") or {}
        if kind == "BATCH_START":
            size = data.get("batch_size") or row.get("batch_size")
            if size:
                return f"Started automated batch ({size} prompts)"
        if kind in ("WORKER_SUBMIT", "WORKER_SUBMIT_AUTO"):
            rt = row.get("round_type") or data.get("queue_role")
            if rt:
                return f"Worker finished a {rt} round"
        return base
    topic = row.get("topic")
    if topic:
        return f"System event — {topic.replace('.', ' ')}"
    return "System activity recorded"


def _event_icon(kind: str) -> str:
    if kind in ("INBOX_DELIVERED",):
        return "inbox"
    if kind in ("BATCH_START", "AGENT_START"):
        return "play"
    if kind in ("WORKER_SUBMIT", "WORKER_SUBMIT_AUTO"):
        return "check"
    if kind in ("BROKER_REJECT", "VALIDATOR_FAIL", "AGENT_STOP"):
        return "warn"
    if kind in ("DECISION_RECONCILED",):
        return "brain"
    return "dot"


def _status_tone(*, busy: bool, pending: bool, blocked: bool) -> str:
    if blocked:
        return "blocked"
    if busy:
        return "busy"
    if pending:
        return "ready"
    return "ready"


def _plain_status(*, g1: dict, rail: dict, inbox: dict, orch: dict, cc: dict) -> dict:
    exec_state = g1.get("executor") or {}
    ua = g1.get("unified_autorun") or {}
    tp = g1.get("turn_progress") or {}
    busy = bool(exec_state.get("busy") or ua.get("running") or tp.get("status") == "RUNNING")
    pending = bool(inbox.get("pending"))
    blocked = bool(rail.get("blocked") or rail.get("stop_inject"))

    if busy:
        headline = "Working on a task"
        subline = "Automated work is running — do not paste into worker chat"
        next_plain = "Open Run tab — tap Stop if it feels stuck for 5+ minutes"
        tone = "busy"
    elif pending:
        headline = "Ready — next task waiting"
        subline = "The next audit is queued and ready"
        next_plain = "Open Run when you're ready to start the next task"
        tone = _status_tone(busy=busy, pending=pending, blocked=blocked)
    elif blocked:
        headline = "Paused"
        subline = "Something blocked the queue — run Safety check first"
        next_plain = "Tap Safety check, then refresh"
        tone = "blocked"
    else:
        headline = "Ready for you"
        subline = "Everything is idle — no action needed right now"
        next_plain = "Refresh to update progress, or open Run when ready"
        tone = "ready"

    return {
        "headline": headline,
        "subline": subline,
        "next_plain": next_plain,
        "tone": tone,
    }


def _proof_counter() -> dict:
    """Canonical honest SSOT — program-1000-honest-status-v1 (not raw REGISTRY done)."""
    import importlib.util

    cache = Path.home() / ".sina" / "PROGRAM_1000_HONEST_STATUS.json"
    row: dict = {}
    try:
        mod_path = SOURCE_A / "scripts" / "program-1000-honest-status-v1.py"
        spec = importlib.util.spec_from_file_location("program_1000_honest_status_v1", mod_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            row = mod.build_status()
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    except Exception:
        row = _read_json(cache)
    verified = int(row.get("honest_done") or 0)
    total = int(row.get("total") or 1000)
    unproven = int(row.get("unproven_done") or 0)
    drift = int(row.get("drift") or 0)
    pct = float(row.get("pct") or round(100.0 * verified / max(total, 1), 2))
    kill = "RED" if unproven > 0 or drift > 0 else "GREEN"
    kill_reason = ""
    if unproven > 0:
        kill_reason = f"{unproven} unproven done logged"
    elif drift > 0:
        kill_reason = f"{drift} drift vs receipts"
    factory = _read_json(Path.home() / ".sina" / "factory-now-v1.json")
    if factory.get("kill_flag") or factory.get("freeze_on"):
        kill = "RED"
        kill_reason = kill_reason or "Factory FROZEN — founder-gated resume only"
    return {
        "verified_done": verified,
        "total": total,
        "pct": pct,
        "unproven_done": unproven,
        "drift": drift,
        "kill": kill,
        "kill_reason": kill_reason,
        "label": f"{verified} verified receipts · not REGISTRY done alone",
        "ssot": str(cache),
        "at": row.get("at") or _now(),
    }


def _honest_progress() -> dict:
    """Deprecated alias — use proof_counter."""
    pc = _proof_counter()
    return {
        "honest_done": pc["verified_done"],
        "total": pc["total"],
        "pct": pc["pct"],
        "left": pc["total"] - pc["verified_done"],
    }


def _goals(*, cc: dict) -> list[dict]:
    pc = _proof_counter()
    return [
        {
            "id": "goal1-honest-receipts",
            "title": "Progress toward 1,000 verified tasks",
            "progress_pct": pc["pct"],
            "status_label": f"{pc['verified_done']}/{pc['total']} verified · {pc['total'] - pc['verified_done']} left",
        }
    ]


def _next_steps(*, busy: bool, pending: bool, blocked: bool) -> list[dict]:
    """Plain numbered steps — always visible on Home (no hunting for ghost buttons)."""
    if busy:
        return [
            {"n": 1, "text": "Open Run tab and watch progress"},
            {"n": 2, "text": "If stuck 5+ minutes → tap Stop factory"},
            {"n": 3, "text": "Still stuck? Tap Safety check on Home or Actions"},
        ]
    if blocked:
        return [
            {"n": 1, "text": "Tap Safety check — read the result in Actions → Output"},
            {"n": 2, "text": "If it fails → tap Fix everything (~2 min)"},
            {"n": 3, "text": "Then open Run when you're ready"},
        ]
    if pending:
        return [
            {"n": 1, "text": "Open Run to start the next task"},
            {"n": 2, "text": "Or tap Safety check if something feels wrong"},
            {"n": 3, "text": "Refresh updates your progress count"},
        ]
    return [
        {"n": 1, "text": "Tap Refresh (top right) to reload progress"},
        {"n": 2, "text": "Open Run when you're ready for the next task"},
        {"n": 3, "text": "Weekly or after errors → Safety check"},
    ]


def _worker_health() -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:13030/health", timeout=2) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {
                "ok": resp.status == 200 and bool(body.get("ok")),
                "port": int(body.get("port") or 13030),
                "service": body.get("service") or "hub-rebuild-worker",
            }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError, ValueError):
        return {"ok": False, "port": 13030, "service": "hub-rebuild-worker"}


def _home_actions(*, busy: bool, g1: dict | None = None) -> list[dict]:
    ua = (g1 or {}).get("unified_autorun") or {}
    active = bool(ua.get("active"))
    running = bool(ua.get("running") or busy)
    status_line = ua.get("message") or ""
    return [
        {
            "id": "founder-goal1-autorun-start",
            "label": "RUN INBOX (Brain routes)",
            "hint": "LEGACY hidden — Cursor AUTO-RUN does not exist",
            "kind": "primary",
            "disabled": True,
            "hidden": True,
        },
        {
            "id": "founder-goal1-autorun-stop",
            "label": "Factory STOP",
            "hint": "FREEZE factory drain · stop receipt · spawn gate ON",
            "kind": "stop",
            "disabled": not (active or running),
        },
        {
            "id": "founder-ecosystem-safety",
            "label": "Safety check",
            "hint": "Checks factory lock, hub health, monitor truth, INBOX sync (~10s)",
            "kind": "safety",
        },
        {
            "id": "founder-restart-rebuild-worker",
            "label": "Restart rebuild worker",
            "hint": "Restart :13030 queue consumer (~5s) — no Terminal",
            "kind": "repair",
        },
        {
            "id": "founder-ecosystem-fix-all",
            "label": "Fix ecosystem",
            "hint": "Full repair if Safety fails — unstick, hygiene, ladder (~2 min)",
            "kind": "repair",
        },
        {
            "id": "founder-refresh",
            "label": "Refresh",
            "hint": "Reload honest count + loop status",
            "kind": "secondary",
        },
        {
            "id": "founder-next-steps",
            "label": "Next steps",
            "hint": "Live next 10 queue turns — optional big-picture commentary",
            "kind": "tab",
            "tab": "next-steps",
        },
        {
            "id": "founder-export-event-chain",
            "label": "Export event chain",
            "hint": "Download JSONL for current queue sa_id — one-sa verification",
            "kind": "export",
        },
        {
            "id": "founder-overnight-verify-readonly",
            "label": "Overnight check (read-only)",
            "hint": "5 disk CHECK turns · semi-auto founder-gated · no drain",
            "kind": "verify",
        },
    ]


def _merge_events(*, limit: int = 10) -> list[dict]:
    rows: list[dict] = []
    for row in _daily_events(n=limit):
        kind = row.get("event") or row.get("kind") or ""
        rows.append(
            {
                "at": row.get("at"),
                "time_label": _format_time(str(row.get("at") or "")),
                "label": _plain_event_label(row),
                "icon": _event_icon(kind),
                "kind": kind,
                "raw": row,
            }
        )
    if len(rows) < limit:
        for row in _tail_jsonl(BROKER_EVENTS, n=limit):
            kind = row.get("kind") or ""
            rows.append(
                {
                    "at": row.get("at"),
                    "time_label": _format_time(str(row.get("at") or "")),
                    "label": _plain_event_label(row),
                    "icon": _event_icon(kind),
                    "kind": kind,
                    "raw": row,
                }
            )
    rows.sort(key=lambda r: str(r.get("at") or ""), reverse=True)
    out: list[dict] = []
    seen: set[str] = set()
    for r in rows:
        key = f"{r.get('at')}|{r.get('kind')}|{r.get('label')}"
        if key in seen:
            continue
        seen.add(key)
        out.append({k: v for k, v in r.items() if k != "raw"})
        if len(out) >= limit:
            break
    return out


def _technical_detail(*, g1: dict, rail: dict, inbox: dict, orch: dict) -> dict:
    queue = g1.get("queue") or rail or {}
    raw_events = _merge_events(limit=8)
    raw_full = _daily_events(n=8) + _tail_jsonl(BROKER_EVENTS, n=8)
    sa = queue.get("sa_id") or g1.get("live_pick", {}).get("id")
    task_title = queue.get("sa_title") or queue.get("title") or g1.get("live_pick", {}).get("title") or ""
    task_title = re.sub(r"^\[(CHECK|ACT|VERIFY)\]\s*", "", str(task_title), flags=re.I)
    task_title = re.sub(r"^sa-\d{4}\s*[—–-]\s*", "", task_title).strip()
    return {
        "sa_id": sa,
        "task_title": task_title[:120] if task_title else "Next audit task",
        "queue_pos": queue.get("queue_pos") or g1.get("queue_pos"),
        "queue_total": queue.get("queue_total") or g1.get("queue_total") or 30,
        "queue_role": queue.get("queue_role") or g1.get("queue_role"),
        "rail": queue.get("rail") or rail.get("rail") or "A",
        "broker_state": "busy" if g1.get("broker_ok") is False else (orch.get("state") or "idle"),
        "orchestrator_state": orch.get("state") or orch.get("phase") or "idle",
        "inbox_pending": bool(inbox.get("pending")),
        "brief": queue.get("brief") or g1.get("brief"),
        "recent_events_plain": raw_events,
        "raw_events": raw_full[-12:],
    }


def _live_wires(*, founder_form: dict, factory_state: dict) -> list[dict]:
    """Only surfaces with disk/API proof — no stale projection."""
    wh = _worker_health()
    form_n = int(founder_form.get("open_questions_count") or 0)
    wires = [
        {
            "id": "form",
            "label": "Form open",
            "value": str(form_n),
            "tone": "gold" if form_n > 0 else "green",
            "live": bool(founder_form.get("ok")),
            "hint": "M1 Canvas · Submit when done",
            "tab": None,
            "canvas_path": str(
                Path.home()
                / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
            ),
        },
        {
            "id": "factory",
            "label": "Factory",
            "value": "FROZEN" if factory_state.get("freeze") else "idle",
            "tone": "blocked" if factory_state.get("freeze") else "green",
            "live": True,
            "hint": factory_state.get("line") or "factory-now-v1.json",
        },
        {
            "id": "worker",
            "label": "Rebuild worker",
            "value": "up" if wh.get("ok") else "down",
            "tone": "green" if wh.get("ok") else "blocked",
            "live": True,
            "hint": f":{wh.get('port', 13030)} health",
        },
    ]
    return wires


def _light_actions(*, busy: bool, factory_state: dict) -> list[dict]:
    """Founder one-tap set — no ghost RUN INBOX."""
    out = [
        {
            "id": "founder-refresh",
            "label": "Refresh",
            "hint": "Reload live wires from disk",
            "kind": "secondary",
        },
        {
            "id": "founder-ecosystem-safety",
            "label": "Safety check",
            "hint": "Factory lock · hub health · inbox (~10s)",
            "kind": "safety",
        },
        {
            "id": "founder-open-m1-canvas",
            "label": "Open M1 form",
            "hint": "Canvas — pick · confirm · Submit",
            "kind": "canvas",
        },
    ]
    try:
        import sys

        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from w3_outbound_batch_approve_v1 import card_status, hub_card_visible  # noqa: WPS433

        if hub_card_visible() and not card_status().get("founder_approved"):
            out.insert(
                0,
                {
                    "id": "founder-approve-outbound-batch",
                    "label": "Approve outbound batch",
                    "hint": card_status().get("summary") or "9.07 A · W3 — one tap before send",
                    "kind": "primary",
                },
            )
    except Exception:
        pass
    out.extend(
        [
        {
            "id": "founder-tab-actions",
            "label": "Actions",
            "hint": "One-tap commands — no Terminal",
            "kind": "tab",
            "tab": "actions",
        },
    ]
    )
    if factory_state.get("freeze") or busy:
        out.insert(
            0,
            {
                "id": "founder-goal1-autorun-stop",
                "label": "Factory STOP",
                "hint": "Halt drain while frozen/busy",
                "kind": "stop",
                "disabled": False,
            },
        )
    return out


def hub_home_founder_payload(*, hub_payload: dict | None = None, light: bool = True) -> dict:
    """Build plain-English home view; optional full hub payload for context."""
    hub = hub_payload or {}
    cc = hub.get("command_center") or {}
    g1 = hub.get("goal1_auto_run") or hub.get("goal1_loop") or {}
    rail = hub.get("healthy_drain_rail") or g1.get("queue") or {}
    inbox = hub.get("worker_inbox") or g1.get("inbox") or {}
    orch = hub.get("healthy_drain_orchestrator") or g1.get("orchestrator") or {}
    exec_state = g1.get("executor") or {}
    busy = bool(exec_state.get("busy"))

    status = _plain_status(g1=g1, rail=rail, inbox=inbox, orch=orch, cc=cc)
    # Strip accidental sa codes from default strings
    for key in ("headline", "subline", "next_plain"):
        val = status.get(key) or ""
        status[key] = re.sub(r"\bsa-\d{4}\b", "next task", val, flags=re.I)

    pending = bool(inbox.get("pending"))
    blocked = bool(rail.get("blocked") or rail.get("stop_inject"))
    next_steps = _next_steps(busy=busy, pending=pending, blocked=blocked)

    detail = _technical_detail(g1=g1, rail=rail, inbox=inbox, orch=orch)
    pc = _proof_counter()
    hp = _honest_progress()
    events = _merge_events(limit=10)
    if not events:
        events = [{"at": _now(), "time_label": "—", "label": "No events yet — run one turn", "icon": "dot", "kind": ""}]

    factory_state: dict = {}
    try:
        import sys

        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now()
        factory_state = {
            "freeze": bool(fn.get("kill_flag")),
            "mode": fn.get("mode") or "FREEZE",
            "line": fn.get("line") or "",
            "stop_receipt_open": bool(fn.get("stop_receipt_open")),
            "queue_sa": fn.get("queue_sa") or "",
        }
    except Exception:
        factory_state = {"freeze": False, "line": ""}

    if factory_state.get("freeze"):
        freeze_line = factory_state.get("line") or ""
        freeze_line = re.sub(r"\bsa-\d{4}\b", "next task", freeze_line, flags=re.I)
        status = {
            "headline": "FROZEN",
            "subline": "Factory drain blocked — kill flag ON",
            "next_plain": freeze_line
            or "FROZEN — Hub Stop or ASF: resume drain — max N — receipt required",
            "tone": "blocked",
        }
        next_steps = [
            {"n": 1, "text": "Factory FROZEN — no drain until ASF resume token"},
            {"n": 2, "text": "Resume only: ASF: resume drain — max N — receipt required"},
            {"n": 3, "text": "Need help? Tap 🛡 Safety check — read result in Actions"},
        ]

    missed_card: dict = {}
    worker_drain: dict = {}
    try:
        from sync_founder_missed_actions_v1 import sync_founder_missed_actions  # noqa: WPS433

        sync_out = sync_founder_missed_actions(write=True)
        missed_card = sync_out.get("card") or {}
        worker_drain = sync_out.get("worker_drain_next_10") or {}
    except Exception:
        missed_card = _read_json(Path.home() / ".sina" / "founder-missed-actions-card-v1.json")
        worker_drain = _read_json(Path.home() / ".sina" / "worker-drain-next-10-v1.json")

    founder_form: dict = {}
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        founder_form = live_form_payload()
    except Exception:
        founder_form = {"ok": False, "needs_asf_fill": True}

    judge_alarm_strip: dict = {}
    try:
        from hub_judge_alarm_strip_v1 import build_strip  # noqa: WPS433

        judge_alarm_strip = build_strip()
    except Exception:
        judge_alarm_strip = {"ok": False, "schema": "hub-judge-alarm-strip-v1"}

    if light:
        wires = _live_wires(founder_form=founder_form, factory_state=factory_state)
        pc = _proof_counter()
        return {
            "ok": True,
            "schema": SCHEMA,
            "hub_light": True,
            "built_at": _now(),
            "spec": "brain-os/system/HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md · light mode",
            "founder_decision_form": founder_form,
            "judge_alarm_strip": judge_alarm_strip,
            "status": status,
            "live_wires": wires,
            "actions": _light_actions(busy=busy, factory_state=factory_state),
            "next_steps": next_steps[:2],
            "factory_state": factory_state,
            "optional_progress": {
                "label": f"{pc['verified_done']}/{pc['total']} verified receipts ({pc['pct']}%)",
                "pct": pc["pct"],
                "ssot": pc.get("ssot"),
                "note": "Factory program backlog — not form open count",
            },
            "proof_counter": pc,
            "technical_detail": detail,
        }

    return {
        "ok": True,
        "schema": SCHEMA_FULL,
        "hub_light": False,
        "built_at": _now(),
        "spec": "brain-os/system/HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md",
        "founder_decision_form": founder_form,
        "judge_alarm_strip": judge_alarm_strip,
        "assigned_sa": "sa-0821",
        "proof_counter": pc,
        "honest_progress": hp,
        "proof_export": {
            "sa_id": detail.get("sa_id"),
            "api": f"/api/event-chain-export-v1?sa_id={detail.get('sa_id') or ''}&customer=1",
            "label": "Export one-sa event chain (JSONL)",
        },
        "status": status,
        "goals": _goals(cc=cc),
        "actions": (
            [
                {
                    "id": "founder-goal1-autorun-stop",
                    "label": "Factory STOP",
                    "hint": "Halt orchestrator + agent · idempotent while frozen",
                    "kind": "stop",
                    "disabled": False,
                },
                *[
                    a
                    for a in _home_actions(busy=busy, g1=g1)
                    if a.get("id") != "founder-goal1-autorun-start"
                ],
            ]
            if factory_state.get("freeze")
            else _home_actions(busy=busy, g1=g1)
        ),
        "next_steps": next_steps,
        "missed_actions_card": missed_card if missed_card.get("ok") else {},
        "worker_drain_next_10": worker_drain if worker_drain.get("ok") else {},
        "safety_panel": {
            "title": "Factory safety",
            "lead": "Not the red ⛔ Emergency button (that kills the hub). This checks locks, monitor, and INBOX.",
            "safety_id": "founder-ecosystem-safety",
            "repair_id": "founder-ecosystem-fix-all",
            "worker_health": _worker_health(),
            "worker_restart_id": "founder-restart-rebuild-worker",
        },
        "factory_state": factory_state,
        "primary_action_id": (
            "founder-goal1-autorun-stop"
            if factory_state.get("freeze")
            else (g1.get("primary_action_id") or "founder-goal1-autorun-start")
        ),
        "recent_events": events,
        "technical_detail": detail,
    }


if __name__ == "__main__":
    print(json.dumps(hub_home_founder_payload(), indent=2))
