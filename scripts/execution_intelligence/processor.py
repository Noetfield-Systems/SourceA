"""Extract success/failure patterns from execution memory."""
from __future__ import annotations

import hashlib
from collections import defaultdict

from execution_intelligence.types import ExecutionPattern, PatternType


def _pattern_id(kind: PatternType, action_id: str, signature: str = "") -> str:
    raw = f"{kind}|{action_id}|{signature}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _norm_action(record: dict) -> str:
    return (record.get("action_id") or record.get("producer") or "unknown").strip()


def extract_patterns(records: list[dict]) -> list[ExecutionPattern]:
    if not records:
        return []

    success_buckets: dict[str, list[dict]] = defaultdict(list)
    failure_buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    sig_only: dict[str, list[dict]] = defaultdict(list)

    for rec in records:
        action = _norm_action(rec)
        tid = rec.get("task_id") or ""
        status = rec.get("status") or ""
        sig = (rec.get("error_signature") or "").strip()

        if status == "success":
            success_buckets[action].append(rec)
        else:
            failure_buckets[(action, sig or "unknown_error")].append(rec)
            if sig:
                sig_only[sig].append(rec)

    # Detect fixes: action failed then later succeeded
    action_timeline: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for rec in sorted(records, key=lambda r: r.get("timestamp") or ""):
        action = _norm_action(rec)
        action_timeline[action].append((rec.get("timestamp") or "", rec.get("status") or ""))

    fix_map: dict[str, str] = {}
    for action, events in action_timeline.items():
        saw_fail = False
        for _ts, st in events:
            if st != "success":
                saw_fail = True
            elif saw_fail:
                fix_map[action] = f"Action '{action}' succeeded after prior failure(s) — reuse last working command path."
                break

    patterns: list[ExecutionPattern] = []

    for action, recs in success_buckets.items():
        pid = _pattern_id("success", action)
        patterns.append(
            ExecutionPattern(
                pattern_id=pid,
                type="success",
                frequency=len(recs),
                related_tasks=[r.get("task_id", "") for r in recs if r.get("task_id")][-20:],
                resolution_strategy=f"Prefer '{action}' — {len(recs)} successful run(s).",
                action_id=action,
            )
        )

    for (action, sig), recs in failure_buckets.items():
        pid = _pattern_id("failure", action, sig)
        strategy = fix_map.get(action) or f"Avoid '{action}' until fixed — signature: {sig or 'unknown'}."
        patterns.append(
            ExecutionPattern(
                pattern_id=pid,
                type="failure",
                frequency=len(recs),
                related_tasks=[r.get("task_id", "") for r in recs if r.get("task_id")][-20:],
                resolution_strategy=strategy,
                action_id=action,
                error_signature=sig,
            )
        )

    for sig, recs in sig_only.items():
        if len(recs) < 2:
            continue
        actions = sorted({_norm_action(r) for r in recs})
        pid = _pattern_id("failure", "cross_action", sig)
        patterns.append(
            ExecutionPattern(
                pattern_id=pid,
                type="failure",
                frequency=len(recs),
                related_tasks=[r.get("task_id", "") for r in recs if r.get("task_id")][-20:],
                resolution_strategy=f"Repeated error across {', '.join(actions[:5])} — investigate root cause.",
                action_id="*",
                error_signature=sig,
            )
        )

    patterns.sort(key=lambda p: (-p.frequency, p.type, p.action_id))
    return patterns


def repeated_error_signatures(records: list[dict], *, min_count: int = 2) -> list[dict]:
    counts: dict[str, int] = defaultdict(int)
    tasks: dict[str, list[str]] = defaultdict(list)
    for rec in records:
        if rec.get("status") == "success":
            continue
        sig = (rec.get("error_signature") or "unknown_error").strip()
        counts[sig] += 1
        tid = rec.get("task_id")
        if tid:
            tasks[sig].append(tid)
    out = []
    for sig, n in sorted(counts.items(), key=lambda x: -x[1]):
        if n >= min_count:
            out.append({"error_signature": sig, "frequency": n, "related_tasks": tasks[sig][-15:]})
    return out
