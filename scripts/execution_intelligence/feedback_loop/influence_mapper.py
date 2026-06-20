"""Map raw signals into consolidated per-action influence records."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def map_influence(signals: list[dict]) -> list[dict]:
    """
    Merge signals sharing action_id + signal_type.
    Weight = max of cluster; reason = strongest-weight reason kept.
    """
    buckets: dict[tuple[str, str], list[dict]] = {}
    for sig in signals:
        key = (sig.get("action_id") or "", sig.get("signal_type") or "")
        if not key[0] or not key[1]:
            continue
        buckets.setdefault(key, []).append(sig)

    mapped: list[dict] = []
    for (action_id, signal_type), cluster in buckets.items():
        cluster.sort(key=lambda s: -float(s.get("weight") or 0))
        lead = cluster[0]
        weight = max(float(s.get("weight") or 0) for s in cluster)
        pattern_ids = sorted({s.get("source_pattern_id") or "" for s in cluster if s.get("source_pattern_id")})
        decision_ids = sorted({s.get("source_decision_id") or "" for s in cluster if s.get("source_decision_id")})
        mapped.append(
            {
                "signal_id": str(uuid.uuid4()),
                "signal_type": signal_type,
                "action_id": action_id,
                "weight": round(min(1.0, weight), 3),
                "reason": lead.get("reason") or "",
                "source_pattern_id": pattern_ids[0] if pattern_ids else "",
                "source_decision_id": decision_ids[0] if decision_ids else "",
                "created_at": _now(),
                "source_count": len(cluster),
                "source_pattern_ids": pattern_ids[:5],
                "source_decision_ids": decision_ids[:5],
            }
        )

    mapped.sort(key=lambda s: (-float(s.get("weight") or 0), s.get("action_id") or ""))
    return mapped
