"""Worker drain paste text — hub Actions only; founder never runs Terminal."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from healthy_queue_ssot_lib import healthy_queue_path, healthy_queue_state_path  # noqa: E402

STATE = Path.home() / ".sina/healthy-queue-state-v1.json"
DRAIN_NEXT_10 = Path.home() / ".sina/worker-drain-next-10-v1.json"


def _queue_path() -> Path:
    return healthy_queue_path()


def _run_script(name: str) -> tuple[int, str]:
    script = ROOT / "scripts" / name
    proc = subprocess.run(
        ["bash", str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _deliver_worker(text: str, *, source: str, meta: dict | None = None) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from worker_inject_lib import inject_worker_prompt  # noqa: WPS433

    out = inject_worker_prompt(text, source=source, meta=meta)
    out["output"] = text
    return out


def healthy_drain_paste(*, clipboard_inject: bool = False, worker_chat_inject: bool = False) -> dict:
    st = healthy_queue_status()
    if not st.get("ok"):
        return {"ok": False, "error": st.get("error") or "queue status failed"}
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from healthy_prompt_turn_v1 import build_turn_prompt  # noqa: WPS433

    queue_path = _queue_path()
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    items = queue.get("queue") or []
    pos = int(st.get("queue_pos") or 1)
    if pos < 1 or pos > len(items):
        pos = 1
    item = items[pos - 1]
    text = build_turn_prompt(item=item, pos=pos, total=len(items), engine="WORKER")
    meta = {
        "queue_pos": st.get("queue_pos"),
        "queue_total": st.get("queue_total"),
        "queue_role": st.get("queue_role"),
        "sa_id": st.get("sa_id"),
        "phase": item.get("phase") or "",
    }
    import os
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from worker_inject_lib import inject_worker_prompt  # noqa: WPS433

    worker_mode = worker_chat_inject or os.environ.get("SINA_WORKER_CHAT_RESUME_INJECT", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ) or clipboard_inject or os.environ.get("SINA_WORKER_CLIPBOARD_INJECT", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if worker_mode:
        out = inject_worker_prompt(
            text,
            source="goal1_healthy_drain",
            meta=meta,
            delivery_mode="worker_chat",
        )
    else:
        out = inject_worker_prompt(text, source="goal1_healthy_drain", meta=meta, delivery_mode="inbox")
    if out.get("worker_chat_inject") or out.get("conversation_id"):
        out["message"] = (
            f"Healthy drain → Worker chat {out.get('conversation_id')} via agent --resume + INBOX logged."
        )
    else:
        out["message"] = (
            "Healthy drain in Worker INBOX — open SourceA Worker chat "
            "(attach rule 099-worker-inbox-active.mdc or say run inbox)"
        )
    return out


def worker_drain_paste() -> dict:
    code, text = _run_script("generate-worker-drain-paste.sh")
    if code != 0:
        return {"ok": False, "error": "worker drain paste failed", "output": text[:2000]}
    out = _deliver_worker(text, source="worker_drain")
    out["message"] = (
        "Worker drain in INBOX — open SourceA Worker chat "
        "(not pasted into focused Brain chat)"
    )
    return out


def healthy_queue_status() -> dict:
    """Active Goal 1 rail — REGISTRY-bound check→act→verify (not legacy queue tab)."""
    queue_path = _queue_path()
    if not queue_path.is_file():
        return {"ok": False, "error": "healthy-queue-30-active.json missing", "rail": "goal1_healthy_drain"}
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    items = queue.get("queue") or []
    if not items:
        return {"ok": False, "error": "empty queue", "rail": "goal1_healthy_drain"}
    state = {}
    pos = 1
    if STATE.is_file():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
            pos = int(state.get("next_pos") or 1)
        except (json.JSONDecodeError, ValueError, TypeError):
            pos = 1
    if pos < 1 or pos > len(items):
        pos = 1
    item = items[pos - 1]
    role = (item.get("queue_role") or item.get("step_type") or "check").upper()
    sa = item.get("sa_id") or "—"
    brief = f"Queue {pos}/{len(items)} · {role} · {sa}"
    next_10: list[str] = []
    drain_doc: dict = {}
    if DRAIN_NEXT_10.is_file():
        try:
            drain_doc = json.loads(DRAIN_NEXT_10.read_text(encoding="utf-8"))
            next_10 = [r.get("sa_id") for r in (drain_doc.get("drain") or []) if r.get("sa_id")]
        except (OSError, json.JSONDecodeError):
            next_10 = []
    return {
        "ok": True,
        "schema": "healthy-drain-rail-v1",
        "rail": "goal1_healthy_drain",
        "law": "os/plan-library/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
        "queue_path": str(queue_path),
        "pack": state.get("pack") or queue.get("product"),
        "queue_pos": pos,
        "queue_total": len(items),
        "queue_role": item.get("queue_role"),
        "step_type": item.get("step_type"),
        "sa_id": sa,
        "sa_title": (item.get("sa_title") or "")[:80],
        "brief": brief,
        "worker_drain_next_10": next_10,
        "worker_drain_next_10_path": str(DRAIN_NEXT_10),
        "founder_action": "Home → Missed actions → ▶ Drain healthy queue",
        "ignore_rail": "Legacy queue tab / generic prompt queue — not Goal 1 REGISTRY drain",
        "pev": {"planner": "generate-healthy-prompt-pack-v1.py", "executor": "SourceA Worker", "verifier": "worker_verify_fast_v1.sh"},
    }


def advance_healthy_queue() -> dict:
    proc = subprocess.run(
        [str(ROOT / "scripts" / "advance-healthy-queue-v1.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr or "advance failed"}
    try:
        row = json.loads(proc.stdout)
    except json.JSONDecodeError:
        row = {"raw": proc.stdout}
    return {
        "ok": True,
        "message": f"Healthy queue advanced → next pos {row.get('next_pos')}",
        "queue": row,
    }
