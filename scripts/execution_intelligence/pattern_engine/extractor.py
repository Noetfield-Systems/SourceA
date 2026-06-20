"""Pattern mining — success, failure, repetition, fix (observe + structure only)."""
from __future__ import annotations

import hashlib
from collections import defaultdict

from execution_intelligence.pattern_engine.classifier import classify_records, group_by_action
from execution_intelligence.pattern_engine.clustering import cluster_by_error, cluster_records
from execution_intelligence.pattern_engine.signatures import (
    action_key,
    command_signature,
    error_fingerprint,
    output_fingerprint,
    record_fingerprint,
)

PatternType = str  # success | failure | repetition | fix


def _pattern_id(ptype: PatternType, signature: str, input_pattern: str) -> str:
    raw = f"{ptype}|{signature}|{input_pattern}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _confidence(frequency: int, sample: int) -> float:
    if sample <= 0:
        return 0.0
    base = min(1.0, frequency / max(sample, 1))
    return round(min(0.99, 0.35 + base * 0.55 + min(frequency, 10) * 0.02), 3)


def _pattern(
    *,
    ptype: PatternType,
    frequency: int,
    signature: str,
    related_task_ids: list[str],
    input_pattern: str,
    output_pattern: str,
    sample: int,
) -> dict:
    return {
        "pattern_id": _pattern_id(ptype, signature, input_pattern),
        "type": ptype,
        "frequency": frequency,
        "signature": signature,
        "related_task_ids": related_task_ids[-30:],
        "input_pattern": input_pattern,
        "output_pattern": output_pattern,
        "confidence": _confidence(frequency, sample),
    }


def build_success_patterns(records: list[dict]) -> list[dict]:
    classified = classify_records(records)
    success = classified["success"]
    if not success:
        return []
    by_action = group_by_action(success)
    clusters = cluster_records(success)
    patterns: list[dict] = []

    for action, recs in by_action.items():
        cmd_counts: dict[str, int] = defaultdict(int)
        out_counts: dict[str, int] = defaultdict(int)
        tids: list[str] = []
        for r in recs:
            cmd_counts[r.get("input_command") or ""] += 1
            out_counts[output_fingerprint(r.get("stdout") or "")] += 1
            if r.get("task_id"):
                tids.append(r["task_id"])
        top_cmd = max(cmd_counts, key=cmd_counts.get)
        top_out = max(out_counts, key=out_counts.get)
        sig = command_signature(top_cmd)
        patterns.append(
            _pattern(
                ptype="success",
                frequency=len(recs),
                signature=sig,
                related_task_ids=tids,
                input_pattern=f"action:{action}|{top_cmd[:200]}",
                output_pattern=top_out,
                sample=len(records),
            )
        )

    # Stable multi-run command clusters
    for fp, recs in clusters.items():
        if len(recs) < 2:
            continue
        tids = [r.get("task_id", "") for r in recs if r.get("task_id")]
        patterns.append(
            _pattern(
                ptype="success",
                frequency=len(recs),
                signature=fp,
                related_task_ids=tids,
                input_pattern=recs[0].get("input_command") or "",
                output_pattern=output_fingerprint(recs[-1].get("stdout") or ""),
                sample=len(records),
            )
        )

    return _dedupe(patterns)


def build_failure_patterns(records: list[dict]) -> list[dict]:
    classified = classify_records(records)
    failure = classified["failure"]
    if not failure:
        return []
    err_clusters = cluster_by_error(failure)
    patterns: list[dict] = []

    for err_sig, recs in err_clusters.items():
        tids = [r.get("task_id", "") for r in recs if r.get("task_id")]
        actions = sorted({action_key(r) for r in recs})
        patterns.append(
            _pattern(
                ptype="failure",
                frequency=len(recs),
                signature=err_sig,
                related_task_ids=tids,
                input_pattern=f"actions:{','.join(actions[:5])}",
                output_pattern=err_sig,
                sample=len(records),
            )
        )

    return _dedupe(patterns)


def build_repetition_patterns(records: list[dict]) -> list[dict]:
    by_action = group_by_action(records)
    patterns: list[dict] = []

    for action, recs in by_action.items():
        if len(recs) < 2:
            continue
        fps = [record_fingerprint(r) for r in recs]
        unique_fps = len(set(fps))
        variation = unique_fps / len(recs)
        tids = [r.get("task_id", "") for r in recs if r.get("task_id")]
        patterns.append(
            _pattern(
                ptype="repetition",
                frequency=len(recs),
                signature=f"repeat:{action}",
                related_task_ids=tids,
                input_pattern=f"action:{action}|runs:{len(recs)}|variants:{unique_fps}",
                output_pattern=f"variation_ratio:{round(variation, 2)}",
                sample=len(records),
            )
        )

    return patterns


def build_fix_patterns(records: list[dict]) -> list[dict]:
    """failure → success transition on same action."""
    sorted_recs = sorted(records, key=lambda r: r.get("timestamp") or "")
    by_action = group_by_action(sorted_recs)
    patterns: list[dict] = []

    for action, recs in by_action.items():
        saw_fail = False
        fail_sig = ""
        fail_tid = ""
        for r in recs:
            if r.get("status") != "success":
                saw_fail = True
                fail_sig = error_fingerprint(
                    r.get("stderr") or "",
                    int(r.get("exit_code") or 1),
                    r.get("error_signature") or "",
                )
                fail_tid = r.get("task_id") or ""
            elif saw_fail:
                success_tid = r.get("task_id") or ""
                patterns.append(
                    _pattern(
                        ptype="fix",
                        frequency=1,
                        signature=f"fix:{action}:{fail_sig}",
                        related_task_ids=[t for t in (fail_tid, success_tid) if t],
                        input_pattern=f"action:{action}|failed_with:{fail_sig}",
                        output_pattern=f"recovered:{command_signature(r.get('input_command') or '')}",
                        sample=len(records),
                    )
                )
                saw_fail = False

    # Merge duplicate fix paths
    merged: dict[str, dict] = {}
    for p in patterns:
        pid = p["pattern_id"]
        if pid in merged:
            merged[pid]["frequency"] += 1
            merged[pid]["related_task_ids"].extend(p["related_task_ids"])
        else:
            merged[pid] = p
    return list(merged.values())


def extract_all_patterns(records: list[dict]) -> list[dict]:
    if not records:
        return []
    patterns: list[dict] = []
    patterns.extend(build_success_patterns(records))
    patterns.extend(build_failure_patterns(records))
    patterns.extend(build_repetition_patterns(records))
    patterns.extend(build_fix_patterns(records))
    patterns.sort(key=lambda p: (-p["frequency"], p["type"], p["signature"]))
    return patterns


def _dedupe(patterns: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for p in patterns:
        if p["pattern_id"] in seen:
            continue
        seen.add(p["pattern_id"])
        out.append(p)
    return out
