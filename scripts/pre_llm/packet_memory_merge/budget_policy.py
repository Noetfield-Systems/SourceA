"""Memory slot budget for D16 writeback — no re-compression."""
from __future__ import annotations

DEFAULT_MAX_SLOTS = 16
DEFAULT_CHAR_BUDGET = 6000
_MEMORY_FRACTION = 0.18


def resolve_memory_budget(*, packet: dict, explicit_slots: int | None = None) -> tuple[int, int]:
    """Return (max_slots, char_budget)."""
    if explicit_slots and explicit_slots > 0:
        max_slots = int(explicit_slots)
    else:
        max_slots = DEFAULT_MAX_SLOTS

    comp = packet.get("compression") or {}
    budget = comp.get("budget") or {}
    token_limit = int(budget.get("token_limit") or 0)
    if token_limit > 0:
        char_budget = max(1200, int(token_limit * 4 * _MEMORY_FRACTION))
    else:
        char_budget = DEFAULT_CHAR_BUDGET
    return max_slots, char_budget


def prune_slots(slots: list[dict], *, max_slots: int, char_budget: int) -> list[dict]:
    out: list[dict] = []
    used = 0
    for slot in slots:
        if len(out) >= max_slots:
            break
        excerpt = str(slot.get("excerpt") or slot.get("summary") or "")
        cost = min(len(excerpt), 400) + 80
        if used + cost > char_budget and out:
            break
        trimmed = dict(slot)
        if excerpt:
            trimmed["excerpt"] = excerpt[:400]
        out.append(trimmed)
        used += cost
    return out
