"""Group similar executions by fingerprint (exact-match clusters)."""
from __future__ import annotations

from collections import defaultdict

from execution_intelligence.pattern_engine.signatures import record_fingerprint


def cluster_records(records: list[dict]) -> dict[str, list[dict]]:
    clusters: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        key = record_fingerprint(rec)
        clusters[key].append(rec)
    return dict(clusters)


def cluster_by_error(records: list[dict]) -> dict[str, list[dict]]:
    from execution_intelligence.pattern_engine.signatures import error_fingerprint

    clusters: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        if rec.get("status") == "success":
            continue
        key = error_fingerprint(
            rec.get("stderr") or "",
            int(rec.get("exit_code") or 1),
            rec.get("error_signature") or "",
        )
        clusters[key].append(rec)
    return dict(clusters)
