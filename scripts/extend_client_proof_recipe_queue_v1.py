#!/usr/bin/env python3
"""Fail-closed queue extension — append only rows passing client-proof-recipe-rubric-v1."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "client-proof-recipe-queue-v1.json"
RUBRIC_PATH = ROOT / "data" / "client-proof-recipe-rubric-v1.json"
BACKLOG = ROOT / "data" / "all-remaining-plan-backlog-v1.json"
FOUNDER_VERIFY = Path.home() / ".sina" / "client-proof-founder-review-verify-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from build_client_proof_recipe_queue_v1 import (  # noqa: E402
    _backlog_to_recipe,
    _is_realistic_backlog_item,
    _read,
    _vague_patterns,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _passes_rubric(row: dict[str, Any], rubric: dict[str, Any]) -> bool:
    for field in rubric.get("required_fields") or []:
        if not str(row.get(field) or "").strip():
            return False
    verify = str(row.get("verify") or "")
    if rubric.get("quality_gates", {}).get("must_have_verify_command") and len(verify) < 20:
        return False
    artifact = str(row.get("proof_artifact") or "")
    if rubric.get("quality_gates", {}).get("must_have_proof_artifact_url_or_path"):
        if artifact in ("disk-receipt", ""):
            return False
        if not (artifact.startswith("http") or artifact.startswith("supabase://")):
            return False
    if "curl -fsS" in verify and "200" in verify and "assert" not in verify and "verify_client_proof" not in verify:
        return False
    return True


def _founder_pack_passed() -> tuple[bool, str]:
    if not FOUNDER_VERIFY.is_file():
        return False, "missing founder verify receipt"
    try:
        doc = json.loads(FOUNDER_VERIFY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, str(exc)[:80]
    if not doc.get("ok"):
        return False, "founder verify ok=false"
    passed = int(doc.get("passed") or 0)
    total = int(doc.get("total") or 15)
    if passed < total:
        return False, f"founder verify {passed}/{total}"
    return True, "founder pack PASS"


def extend(*, write: bool = False) -> dict[str, Any]:
    pack_ok, pack_reason = _founder_pack_passed()
    if not pack_ok:
        return {
            "ok": False,
            "fail_closed": True,
            "gate": "founder_review_pack",
            "reason": pack_reason,
            "before_total": 0,
            "after_total": 0,
            "new_rows_admitted": 0,
            "queue_exhausted": True,
        }

    rubric = _read(RUBRIC_PATH)
    current = _read(QUEUE)
    existing = current.get("items") or []
    seen = {str(r.get("plan_id") or "") for r in existing}
    before = len(existing)

    vague = _vague_patterns()
    new_rows: list[dict[str, Any]] = []
    for raw in (_read(BACKLOG).get("items") or []):
        if not isinstance(raw, dict):
            continue
        pid = str(raw.get("plan_id") or "")
        if not pid or pid in seen:
            continue
        if not _is_realistic_backlog_item(raw, vague):
            continue
        candidate = _backlog_to_recipe(raw)
        if not _passes_rubric(candidate, rubric):
            continue
        new_rows.append(candidate)
        seen.add(pid)

    after = before + len(new_rows)
    result = {
        "ok": True,
        "before_total": before,
        "after_total": after,
        "new_rows_admitted": len(new_rows),
        "queue_exhausted": len(new_rows) == 0,
        "rubric": str(RUBRIC_PATH.relative_to(ROOT)),
        "fail_closed": True,
    }

    if write and new_rows:
        merged = list(existing) + new_rows
        for idx, row in enumerate(merged, start=1):
            row["backlog_index"] = idx
        doc = {
            **current,
            "generated_at": _now(),
            "total": len(merged),
            "proven_live_count": sum(1 for x in merged if x.get("proven")),
            "filtered_backlog_count": sum(
                1 for x in merged if x.get("lane") == "client-proof-filtered"
            ),
            "items": merged,
            "extension": result,
        }
        QUEUE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="Write queue only when new_rows > 0")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = extend(write=args.write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"OK extend before={row['before_total']} new={row['new_rows_admitted']} "
            f"exhausted={row['queue_exhausted']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
