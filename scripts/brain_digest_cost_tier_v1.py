#!/usr/bin/env python3
"""Brain digest slice — weekly spend-by-tier + cost-per-merged-change trend (L17)."""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "brain-digest-cost-tier-latest-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() and v.strip() and not os.environ.get(k.strip()):
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def _fetch_session_costs(*, days: int = 7) -> list[dict[str, Any]]:
    _load_secrets(Path.home() / ".sourcea-secrets" / "portfolio-spine.env")
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    if not url or not key:
        return []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = urllib.parse.urlencode(
        {
            "select": "id,recorded_at,event,payload",
            "event": "eq.AGENT_SESSION_COST",
            "recorded_at": f"gte.{since}",
            "order": "recorded_at.desc",
            "limit": "500",
        }
    )
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/truth_log?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace"))
            return rows if isinstance(rows, list) else []
    except Exception:
        return []


def build_digest(*, days: int = 7) -> dict[str, Any]:
    rows = _fetch_session_costs(days=days)
    marginal_by_tier: dict[str, float] = defaultdict(float)
    list_by_tier: dict[str, float] = defaultdict(float)
    by_tier_count: dict[str, int] = defaultdict(int)
    total_marginal = 0.0
    total_list = 0.0
    for row in rows:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        tier = str(payload.get("tier") or "T2")
        marginal = float(
            payload.get("usd_marginal")
            if payload.get("usd_marginal") is not None
            else payload.get("usd_est")
            or 0
        )
        list_equiv = float(
            payload.get("usd_list_equiv")
            if payload.get("usd_list_equiv") is not None
            else marginal
        )
        marginal_by_tier[tier] += marginal
        list_by_tier[tier] += list_equiv
        by_tier_count[tier] += 1
        total_marginal += marginal
        total_list += list_equiv

    merge_rows = _fetch_merges(days=days)
    merge_count = len(merge_rows)
    cost_per_merge_marginal = round(total_marginal / merge_count, 4) if merge_count else None
    cost_per_merge_list = round(total_list / merge_count, 4) if merge_count else None

    digest = {
        "schema": "brain-digest-cost-tier-v1",
        "at": _now(),
        "window_days": days,
        "spend_by_tier_marginal": {k: round(v, 4) for k, v in sorted(marginal_by_tier.items())},
        "spend_by_tier_list_equiv": {k: round(v, 4) for k, v in sorted(list_by_tier.items())},
        "spend_by_tier": {k: round(v, 4) for k, v in sorted(marginal_by_tier.items())},
        "sessions_by_tier": dict(sorted(by_tier_count.items())),
        "total_usd_marginal": round(total_marginal, 4),
        "total_usd_list_equiv": round(total_list, 4),
        "total_usd_est": round(total_marginal, 4),
        "merged_changes": merge_count,
        "cost_per_merged_change_usd_marginal": cost_per_merge_marginal,
        "cost_per_merged_change_usd_list_equiv": cost_per_merge_list,
        "cost_per_merged_change_usd_est": cost_per_merge_marginal,
        "trend_note": "cost_per_merged_change = total session cost / EXTERNAL_VERIFY_PASS count in window",
        "source_rows": len(rows),
        "law": "L17 — Brain digest weekly spend-by-tier (marginal + list_equiv)",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(digest, indent=2) + "\n", encoding="utf-8")
    return digest


def _fetch_merges(*, days: int) -> list[dict[str, Any]]:
    """Proxy: EXTERNAL_VERIFY_PASS rows as merged-change signal."""
    _load_secrets(Path.home() / ".sourcea-secrets" / "portfolio-spine.env")
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    if not url or not key:
        return []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = urllib.parse.urlencode(
        {
            "select": "id,recorded_at",
            "event": "eq.EXTERNAL_VERIFY_PASS",
            "recorded_at": f"gte.{since}",
            "limit": "200",
        }
    )
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/truth_log?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace"))
            return rows if isinstance(rows, list) else []
    except Exception:
        return []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_digest(days=args.days)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
