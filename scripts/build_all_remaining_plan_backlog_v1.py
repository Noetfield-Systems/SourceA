#!/usr/bin/env python3
"""Build one deduped backlog from all non-done plan registries."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "all-remaining-plan-backlog-v1.json"

DONE_STATUSES = {
    "done",
    "complete",
    "completed",
    "closed",
    "archived",
    "retired",
    "superseded",
    "shipped",
}

SOURCE_GLOBS = (
    "brain-os/plan-registry/**/REGISTRY.json",
    "witnessbc-site/os/plan-library/**/REGISTRY.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _registry_paths() -> list[Path]:
    paths: set[Path] = set()
    for glob in SOURCE_GLOBS:
        paths.update(ROOT.glob(glob))
    return sorted(paths)


def _status(row: dict[str, Any]) -> str:
    return str(row.get("status") or row.get("state") or "").strip().lower()


def _skip_reason(row: dict[str, Any]) -> str:
    status = _status(row)
    if status in DONE_STATUSES:
        return f"status:{status}"
    if row.get("archived") is True:
        return "archived:true"
    if row.get("retired") is True:
        return "retired:true"
    if row.get("superseded") is True or row.get("superseded_by"):
        return "superseded"
    return ""


def _tier_rank(tier: str) -> int:
    t = str(tier or "").upper()
    if t.startswith("T") and t[1:].isdigit():
        return int(t[1:])
    if t.startswith("P") and t[1:].isdigit():
        return int(t[1:])
    return 9


def _priority_rank(row: dict[str, Any]) -> int:
    for key in ("priority_rank", "rank", "position", "slot", "slice"):
        try:
            return int(row.get(key))
        except (TypeError, ValueError):
            pass
    return 999_999


def _plan_id(row: dict[str, Any], *, registry_rel: str, idx: int) -> str:
    pid = str(row.get("id") or row.get("plan_id") or row.get("sa_id") or "").strip()
    if pid:
        return pid
    stem = registry_rel.replace("/", "-").replace("REGISTRY.json", "").strip("-")
    return f"{stem}-{idx:04d}"


def _title(row: dict[str, Any], pid: str) -> str:
    title = str(row.get("title") or row.get("name") or row.get("description") or "").strip()
    return title or f"Execute {pid}"


def _extract(registry_path: Path, registry: dict[str, Any]) -> tuple[list[dict[str, Any]], Counter[str]]:
    registry_rel = str(registry_path.relative_to(ROOT))
    plans = registry.get("plans")
    if not isinstance(plans, list):
        return [], Counter({"no_plans_array": 1})

    skipped: Counter[str] = Counter()
    out: list[dict[str, Any]] = []
    for idx, raw in enumerate(plans, start=1):
        if not isinstance(raw, dict):
            skipped["non_object"] += 1
            continue
        reason = _skip_reason(raw)
        if reason:
            skipped[reason] += 1
            continue
        pid = _plan_id(raw, registry_rel=registry_rel, idx=idx)
        tier = str(raw.get("tier") or raw.get("priority") or "").strip()
        lane = str(raw.get("lane") or raw.get("repo") or registry.get("repo") or registry.get("stack") or "").strip()
        prompt_path = str(raw.get("path") or raw.get("prompt_path") or "").strip()
        out.append(
            {
                "plan_id": pid,
                "title": _title(raw, pid),
                "status": _status(raw) or "open",
                "tier": tier,
                "lane": lane or "sourcea",
                "phase": raw.get("phase"),
                "workstream": raw.get("workstream"),
                "priority": raw.get("priority"),
                "priority_rank": raw.get("priority_rank"),
                "source_registry": registry_rel,
                "source_schema": registry.get("schema") or registry.get("library") or registry.get("schema_version"),
                "prompt_path": prompt_path,
                "agent_prompt": raw.get("agent_prompt") or raw.get("prompt"),
                "verify": raw.get("verify"),
                "raw_ref": {
                    "registry": registry_rel,
                    "index": idx,
                    "id": pid,
                },
                "_sort": [
                    _tier_rank(tier or str(raw.get("priority") or "")),
                    _priority_rank(raw),
                    registry_rel,
                    idx,
                ],
            }
        )
    return out, skipped


def build_backlog(*, write: bool = True) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    skipped_by_source: dict[str, dict[str, int]] = {}
    source_counts: Counter[str] = Counter()
    skipped_total: Counter[str] = Counter()
    duplicates: list[dict[str, str]] = []
    seen: dict[str, str] = {}

    for path in _registry_paths():
        reg = _read_json(path)
        rel = str(path.relative_to(ROOT))
        extracted, skipped = _extract(path, reg)
        skipped_by_source[rel] = dict(skipped)
        skipped_total.update(skipped)
        for row in extracted:
            key = str(row.get("plan_id") or "").lower()
            if key in seen:
                duplicates.append({"plan_id": row["plan_id"], "kept": seen[key], "skipped": rel})
                continue
            seen[key] = rel
            source_counts[rel] += 1
            rows.append(row)

    rows.sort(key=lambda r: (r["_sort"], str(r["plan_id"])))
    for idx, row in enumerate(rows, start=1):
        row["backlog_index"] = idx
        row.pop("_sort", None)

    doc = {
        "schema": "all-remaining-plan-backlog-v1",
        "version": "1.0.0",
        "generated_at": _now(),
        "ok": True,
        "source_globs": list(SOURCE_GLOBS),
        "total_remaining": len(rows),
        "dedupe": {
            "duplicates_skipped": len(duplicates),
            "sample": duplicates[:25],
        },
        "skipped_total": dict(skipped_total),
        "source_counts": dict(sorted(source_counts.items())),
        "skipped_by_source": skipped_by_source,
        "items": rows,
    }
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    doc = build_backlog(write=not args.no_write)
    if args.json:
        print(json.dumps({k: doc[k] for k in ("schema", "ok", "generated_at", "total_remaining", "dedupe", "skipped_total")}, indent=2))
    else:
        print(f"ALL_PLAN_BACKLOG total={doc['total_remaining']} path={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
