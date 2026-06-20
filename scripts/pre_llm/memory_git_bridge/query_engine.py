"""Filter D6 memory slots by query text."""
from __future__ import annotations


def filter_slots(slots: list[dict], text: str, *, top_k: int = 12) -> list[dict]:
    q = (text or "").strip().lower()
    if not q:
        return slots[:top_k]

    scored: list[tuple[float, dict]] = []
    tokens = [t for t in q.split() if len(t) > 2]

    for slot in slots:
        hay = " ".join(
            str(slot.get(k) or "")
            for k in ("summary", "excerpt", "action_id", "kind", "sha", "path")
        ).lower()
        if q in hay:
            score = 2.0
        else:
            score = sum(1.0 for t in tokens if t in hay) / max(len(tokens), 1)
        if score > 0:
            scored.append((score, {**slot, "score": round(score, 3)}))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:top_k]]
