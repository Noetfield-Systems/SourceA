"""Collect read-only memory slots from D6 + B-layer SSOT."""
from __future__ import annotations

import json
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
PATTERNS_PATH = STATE_DIR / "execution_patterns_v1.json"
DECISIONS_PATH = STATE_DIR / "execution_decisions_v1.jsonl"
FEEDBACK_PATH = STATE_DIR / "execution_feedback_signals.jsonl"


def _tail_jsonl(path: Path, limit: int) -> list[dict]:
    if not path.is_file():
        return []
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    rows: list[dict] = []
    for line in lines[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def collect_d6_slots(*, text: str, repo_root: str | None, task_id: str, force_refresh: bool) -> list[dict]:
    from pre_llm.memory_git_bridge.bridge_engine import run_bridge  # noqa: WPS433
    from pre_llm.memory_git_bridge.query_engine import filter_slots  # noqa: WPS433
    from pre_llm.memory_git_bridge.store import load_canonical  # noqa: WPS433

    live = run_bridge(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not live.get("ok"):
        return []
    canonical = load_canonical()
    slots = filter_slots(canonical.get("slots") or [], text, top_k=20)
    for slot in slots:
        slot.setdefault("source_plane", "D6")
    return slots


def collect_b_layer_slots(*, limit: int = 8) -> list[dict]:
    slots: list[dict] = []

    if PATTERNS_PATH.is_file():
        try:
            data = json.loads(PATTERNS_PATH.read_text(encoding="utf-8"))
            for i, pat in enumerate((data.get("patterns") or [])[-limit:]):
                sig = pat.get("signature") or pat.get("type") or "pattern"
                slots.append(
                    {
                        "slot_id": f"pat-{i}",
                        "kind": "execution_pattern",
                        "summary": f"pattern {pat.get('type')}: {sig}",
                        "excerpt": json.dumps(pat, default=str)[:400],
                        "path": str(PATTERNS_PATH),
                        "producer": "B1",
                        "source_plane": "B",
                        "read_only": True,
                    }
                )
        except json.JSONDecodeError:
            pass

    for i, rec in enumerate(_tail_jsonl(DECISIONS_PATH, limit)):
        slots.append(
            {
                "slot_id": f"dec-{rec.get('decision_id') or i}",
                "kind": "execution_decision",
                "task_id": rec.get("task_id"),
                "summary": (rec.get("why") or rec.get("action_id") or "decision")[:120],
                "excerpt": json.dumps(rec, default=str)[:400],
                "path": str(DECISIONS_PATH),
                "producer": "B2",
                "source_plane": "B",
                "read_only": True,
            }
        )

    for i, rec in enumerate(_tail_jsonl(FEEDBACK_PATH, max(4, limit // 2))):
        slots.append(
            {
                "slot_id": f"fb-{i}",
                "kind": "feedback_signal",
                "summary": f"{rec.get('signal_type') or 'signal'}: {rec.get('target') or ''}"[:120],
                "excerpt": json.dumps(rec, default=str)[:400],
                "path": str(FEEDBACK_PATH),
                "producer": "B3",
                "source_plane": "B",
                "read_only": True,
            }
        )
    return slots


def collect_l5_history_slots(*, text: str, repo_root: str | None, limit: int = 6) -> list[dict]:
    try:
        from pre_llm.semantic_history.history_bridge import build_semantic_history  # noqa: WPS433

        hist = build_semantic_history(query_text=text, repo_root=repo_root, limit=limit)
    except Exception:
        return []
    slots: list[dict] = []
    for i, row in enumerate(hist.get("commits") or []):
        slots.append(
            {
                "slot_id": row.get("slot_id") or f"l5-{i}",
                "kind": "semantic_history",
                "summary": (row.get("summary") or "commit")[:120],
                "excerpt": f"{row.get('sha', '')[:12]} · {row.get('author', '')} · {row.get('timestamp', '')}",
                "path": row.get("path") or "",
                "producer": "L5",
                "source_plane": "L5",
                "read_only": True,
            }
        )
    return slots


def merge_slot_lists(*lists: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for group in lists:
        for slot in group:
            sid = str(slot.get("slot_id") or "")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            out.append(slot)
    return out
