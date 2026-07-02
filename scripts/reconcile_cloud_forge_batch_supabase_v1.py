#!/usr/bin/env python3
"""Reconcile batch CLOUD-SEC IDs vs Supabase rows — classify lag and write artifact."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLOUD_RE = re.compile(r"CLOUD-SEC-(\d+)")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cloud_num(plan_id: str) -> int | None:
    m = CLOUD_RE.search(str(plan_id or ""))
    return int(m.group(1)) if m else None


def _load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _supabase_cfg() -> dict[str, str]:
    env = _load_env(Path.home() / ".sourcea-secrets/portfolio-spine.env")
    return {
        "url": env.get("SUPABASE_URL", "").strip(),
        "key": env.get("SUPABASE_SERVICE_ROLE_KEY", "").strip(),
        "table": "cloud_forge_run_rows",
    }


def fetch_plan_ids(cfg: dict[str, str], plan_ids: list[str]) -> dict[str, dict]:
    if not cfg["url"] or not cfg["key"] or not plan_ids:
        return {}
    quoted = ",".join(f'"{pid}"' for pid in plan_ids)
    params = urllib.parse.urlencode(
        {
            "select": "plan_id,status,proof_tier,sellable,shipped_at,batch_id,artifact_path",
            "plan_id": f"in.({quoted})",
        }
    )
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            return {str(r["plan_id"]): r for r in rows if r.get("plan_id")}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        return {"__error__": {"error": str(exc)[:200]}}


def classify_missing(plan_id: str, batch_doc: dict) -> str:
    plans = {str(p.get("id")): p for p in batch_doc.get("plans") or []}
    plan = plans.get(plan_id) or {}
    proof = str(plan.get("proof_tier") or plan.get("artifact", {}).get("proof_tier") or "")
    if proof in ("receipt_only", "local_receipt"):
        return "receipt_only_no_supabase_sink"
    if plan.get("skip_supabase"):
        return "processed_no_row_by_design"
    return "failed_or_delayed_write"


def reconcile(*, batch_path: Path) -> dict[str, Any]:
    doc = json.loads(batch_path.read_text(encoding="utf-8"))
    cloud_plans = [str(p.get("id")) for p in doc.get("plans") or [] if _cloud_num(str(p.get("id") or ""))]
    cloud_plans = sorted(set(cloud_plans), key=lambda x: _cloud_num(x) or 0)
    cfg = _supabase_cfg()
    found = fetch_plan_ids(cfg, cloud_plans)
    err = found.pop("__error__", None)
    present = set(found)
    missing = [pid for pid in cloud_plans if pid not in present]
    classified = {pid: classify_missing(pid, doc) for pid in missing}
    by_class: dict[str, list[str]] = {}
    for pid, cls in classified.items():
        by_class.setdefault(cls, []).append(pid)
    summary = doc.get("summary") or {}
    return {
        "schema": "cloud-forge-batch-supabase-reconcile-v1",
        "at": _now(),
        "batch_id": summary.get("batch_id"),
        "batch_path": str(batch_path),
        "claimed_range": summary.get("cloud_sec_range"),
        "expected_cloud_ids": len(cloud_plans),
        "supabase_present": len(present),
        "supabase_missing": len(missing),
        "missing_ids": missing,
        "classification": classified,
        "by_class": by_class,
        "supabase_query_error": err,
        "invariant": (
            "Supabase cloud_forge_run_rows is a post-ship sink — not 1:1 guaranteed per Railway tick. "
            "Rows appear only when persist_shipped_row runs with ok=true and proof_tier=verified_fetch sellable path."
        ),
        "backfill_recommended": [pid for pid, cls in classified.items() if cls == "failed_or_delayed_write"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-id", type=int, default=77)
    ap.add_argument("--batch-json", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    batch_path = args.batch_json or ROOT / "data" / f"secondary-cloud-forge-run-batch-{args.batch_id}-locked-v1.json"
    if not batch_path.is_file():
        print(f"FAIL: missing {batch_path}", file=sys.stderr)
        return 2
    row = reconcile(batch_path=batch_path)
    out = args.out or ROOT / "data" / f"cloud-forge-batch-{args.batch_id}-supabase-reconcile-v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["artifact_path"] = str(out)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"OK reconcile batch {row.get('batch_id')}: "
            f"{row['supabase_present']}/{row['expected_cloud_ids']} present · "
            f"{row['supabase_missing']} missing → {out}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
