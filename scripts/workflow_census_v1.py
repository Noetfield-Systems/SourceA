#!/usr/bin/env python3
"""WORKFLOW_CENSUS_v1 — crawl loops, classify value, upsert Supabase, run audit rules.

Crawls (disk + Supabase loop_registry):
  - Cloudflare workers + crons (wrangler.toml)
  - Railway FBE scheduled routes (loop-specialist dispatch)
  - GitHub workflows (.github/workflows)
  - Supabase loop_registry liveness rows

Weekly cron: CF → Railway /api/fbe/workflow-census/weekly/v1
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data/workflow-census-loop-map-v1.json"
TRAFFIC_PATH = ROOT / "data/workflow-census-traffic-override-v1.json"
DISPATCH_PATH = ROOT / "data/loop-specialist-cron-dispatch-v1.json"
TRIGGER_PATH = ROOT / "data/trigger-registry-v1.json"
TABLE = "workflow_census"
SOURCE = "workflow_census_v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("WC-%Y%m%d")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _supabase_cfg() -> tuple[str, str] | tuple[None, None]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return None, None
    return url, key


def cron_invocations_per_day(expression: str | None) -> float:
    expr = (expression or "").strip()
    if not expr:
        return 0.0
    if expr == "event":
        return 2.0
    if expr == "manual":
        return 0.5
    if expr == "piggyback":
        return 0.0
    if expr == "0 * * * *":
        return 24.0
    if expr == "0 0 * * *":
        return 1.0
    if expr == "0 3 * * *":
        return 1.0
    if expr == "0 7 * * *":
        return 1.0
    if expr == "0 8 * * *":
        return 1.0
    if expr == "0 9 * * 0":
        return 1.0 / 7.0
    if expr == "0 10 * * 0":
        return 1.0 / 7.0
    if expr == "0 14 * * *":
        return 1.0
    if expr == "30 */6 * * *":
        return 4.0
    m = re.fullmatch(r"\*/(\d+)\s+\*\s+\*\s+\*\s+\*", expr)
    if m:
        mins = int(m.group(1))
        if mins > 0:
            return round(1440.0 / mins, 4)
    return 1.0


def _wrangler_crons(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    crons: list[str] = []
    in_triggers = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[triggers]"):
            in_triggers = True
            continue
        if in_triggers and s.startswith("["):
            break
        if in_triggers and s.startswith("crons"):
            m = re.search(r"\[(.*)\]", line.split("=", 1)[-1])
            if m:
                crons.extend(re.findall(r'"([^"]+)"', m.group(1)))
    return crons


def _worker_name(wrangler: Path) -> str:
    text = wrangler.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'name\s*=\s*"([^"]+)"', text)
    return m.group(1) if m else wrangler.parent.name


def crawl_cloudflare() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    workers = ROOT / "cloud" / "workers"
    for wrangler in sorted(workers.glob("*/wrangler.toml")):
        name = _worker_name(wrangler)
        crons = _wrangler_crons(wrangler)
        if not crons:
            rows.append(
                {
                    "loop_key": f"cf:{name}",
                    "name": name,
                    "trigger_host": "cloudflare",
                    "schedule_cron": None,
                    "invocations_per_day": 50.0,
                    "metadata": {"wrangler": str(wrangler.relative_to(ROOT)), "kind": "http_worker"},
                }
            )
            continue
        for cron in crons:
            rows.append(
                {
                    "loop_key": f"cf:{name}:{cron}",
                    "name": name,
                    "trigger_host": "cloudflare",
                    "schedule_cron": cron,
                    "invocations_per_day": cron_invocations_per_day(cron),
                    "metadata": {"wrangler": str(wrangler.relative_to(ROOT))},
                }
            )
    return rows


def crawl_railway() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    dispatch = _load_json(DISPATCH_PATH)
    seen: set[str] = set()
    for block in dispatch.get("crons") or []:
        cron = block.get("cron")
        for job in block.get("jobs") or []:
            if job.get("kind") != "railway":
                continue
            path = str(job.get("path") or "")
            jid = str(job.get("id") or path)
            key = f"railway:{jid}"
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "loop_key": key,
                    "name": jid,
                    "trigger_host": "railway",
                    "schedule_cron": cron,
                    "invocations_per_day": cron_invocations_per_day(str(cron or "")),
                    "metadata": {"fbe_path": path, "trigger_id": block.get("trigger_id")},
                }
            )
    rows.append(
        {
            "loop_key": "railway:sourcea-fbe-runner",
            "name": "sourcea-fbe-runner",
            "trigger_host": "railway",
            "schedule_cron": "*/10 * * * *",
            "invocations_per_day": cron_invocations_per_day("*/10 * * * *"),
            "metadata": {"service": "sourcea-fbe-runner", "role": "cloud_forge_motor"},
        }
    )
    return rows


def crawl_github() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    wf_dir = ROOT / ".github" / "workflows"
    for wf in sorted(wf_dir.glob("*.yml")):
        text = wf.read_text(encoding="utf-8", errors="replace")
        stem = wf.stem
        if re.search(r"^\s*schedule\s*:", text, re.M):
            sched_m = re.search(r"cron:\s*['\"]([^'\"]+)['\"]", text)
            cron = sched_m.group(1) if sched_m else "schedule"
            rows.append(
                {
                    "loop_key": f"gha:{stem}",
                    "name": stem,
                    "trigger_host": "github_actions",
                    "schedule_cron": cron,
                    "invocations_per_day": cron_invocations_per_day(cron),
                    "metadata": {"path": str(wf.relative_to(ROOT)), "kind": "schedule_forbidden_backup"},
                }
            )
            continue
        kind = "event" if re.search(r"^\s*push\s*:|^\s*pull_request\s*:|workflow_run", text, re.M) else "manual"
        rows.append(
            {
                "loop_key": f"gha:{stem}",
                "name": stem,
                "trigger_host": "github_actions",
                "schedule_cron": kind,
                "invocations_per_day": cron_invocations_per_day(kind),
                "metadata": {"path": str(wf.relative_to(ROOT)), "kind": kind},
            }
        )
    return rows


def fetch_loop_registry() -> list[dict[str, Any]]:
    url, key = _supabase_cfg()
    if not url or not key:
        return []
    req = urllib.request.Request(
        f"{url}/rest/v1/loop_registry?select=*&order=last_fired_at.desc.nullslast",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            return body if isinstance(body, list) else []
    except (urllib.error.URLError, json.JSONDecodeError):
        return []


def crawl_supabase_registry(existing: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for reg in fetch_loop_registry():
        loop_id = str(reg.get("loop_id") or "")
        if not loop_id:
            continue
        key = f"supabase:{loop_id}"
        last_fired = reg.get("last_fired_at")
        receipt = reg.get("last_receipt") if isinstance(reg.get("last_receipt"), dict) else {}
        row = existing.get(key) or {
            "loop_key": key,
            "name": loop_id,
            "trigger_host": str(reg.get("trigger_host") or "supabase"),
            "schedule_cron": reg.get("schedule_cron"),
            "invocations_per_day": cron_invocations_per_day(str(reg.get("schedule_cron") or "")),
            "metadata": {"source": "loop_registry"},
        }
        row["last_receipt_at"] = last_fired
        row["last_receipt_kind"] = str(receipt.get("kind") or receipt.get("schema") or "loop_liveness")
        row["last_receipt_ref"] = receipt
        rows.append(row)
    return rows


def _classify(name: str, loop_map: dict[str, Any]) -> tuple[str, str, bool]:
    hay = name.lower()
    for rule in loop_map.get("rules") or []:
        for pat in rule.get("match") or []:
            if str(pat).lower() in hay:
                vc = str(rule.get("value_class") or "META")
                rk = str(rule.get("receipt_kind") or "named_receipt")
                return vc, rk, True
    default = str(loop_map.get("default_value_class") or "META")
    return default, "ops_receipt", default != "NONE"


def _estimate_cost(host: str, invocations: float, loop_map: dict[str, Any]) -> float:
    est = loop_map.get("cost_estimates_usd_monthly") or {}
    h = host.lower()
    if h == "cloudflare":
        base = float(est.get("cloudflare_worker") or 0.35)
        slot = float(est.get("cloudflare_cron_slot") or 0.15)
        return round(base + slot * max(1.0, invocations / 100.0), 4)
    if h == "railway":
        shared = float(est.get("railway_fbe_shared") or 18.0)
        job = float(est.get("railway_job_amortized") or 0.25)
        return round(shared / 30.0 + job * max(1.0, invocations / 10.0), 4)
    if h == "github_actions":
        return float(est.get("github_actions_event") or 0.02) * max(1.0, invocations)
    return float(est.get("supabase_row") or 0.01)


def _intake_stats() -> dict[str, Any]:
    url, key = _supabase_cfg()
    out: dict[str, Any] = {"intake_24h": 0, "intake_7d": 0, "probe_7d": 0}
    if not url or not key:
        return out
    since_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    since_24h = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    for label, since, probe in (
        ("intake_7d", since_7d, "false"),
        ("intake_24h", since_24h, "false"),
        ("probe_7d", since_7d, "true"),
    ):
        q = (
            f"{url}/rest/v1/nf_intake_submissions"
            f"?select=id&recorded_at=gte.{since}&probe=eq.{probe}&limit=1"
        )
        req = urllib.request.Request(
            q,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Prefer": "count=exact",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                cr = resp.headers.get("Content-Range", "")
                if "/" in cr:
                    out[label] = int(cr.split("/")[-1])
        except (urllib.error.URLError, ValueError):
            pass
    return out


def traffic_intake_row(loop_map: dict[str, Any]) -> dict[str, Any]:
    traffic = _load_json(TRAFFIC_PATH)
    intake = _intake_stats()
    visits = int(os.environ.get("WORKFLOW_CENSUS_WEB_VISITS_24H") or traffic.get("web_visits_24h") or 0)
    leads_24h = int(intake.get("intake_24h") or 0)
    rate = round((leads_24h / visits) * 100.0, 4) if visits > 0 else 0.0
    return {
        "loop_key": "metric:traffic-intake-conversion",
        "name": "www traffic → intake conversion",
        "trigger_host": "cloudflare_analytics",
        "schedule_cron": "0 10 * * 0",
        "invocations_per_day": 1.0 / 7.0,
        "cost_usd_monthly": 0.0,
        "last_receipt_at": _now(),
        "last_receipt_kind": "conversion_rate",
        "last_receipt_ref": {
            "web_visits_24h": visits,
            "intake_leads_24h": leads_24h,
            "conversion_pct_24h": rate,
            "intake_7d": intake.get("intake_7d"),
            "probe_7d": intake.get("probe_7d"),
            "traffic_source": traffic.get("source") or "override_json",
        },
        "value_class": "REVENUE",
        "receipt_named": True,
        "audit_flags": [],
        "metadata": {"domain": traffic.get("domain") or "www.sourcea.app"},
    }


def merge_census_rows() -> list[dict[str, Any]]:
    loop_map = _load_json(MAP_PATH)
    merged: dict[str, dict[str, Any]] = {}
    for row in crawl_cloudflare() + crawl_railway() + crawl_github():
        merged[row["loop_key"]] = row
    for row in crawl_supabase_registry(merged):
        merged[row["loop_key"]] = {**merged.get(row["loop_key"], {}), **row}

    run_id = _run_id()
    at = _now()
    out: list[dict[str, Any]] = []
    for row in merged.values():
        name = str(row.get("name") or "")
        host = str(row.get("trigger_host") or "")
        inv = float(row.get("invocations_per_day") or 0.0)
        vc, receipt_kind, named = _classify(name, loop_map)
        last_at = row.get("last_receipt_at")
        if not last_at and row.get("loop_key", "").startswith("cf:"):
            last_at = None
        flags: list[str] = []
        if not named and not row.get("last_receipt_ref"):
            flags.append("unnamed_receipt")
        out.append(
            {
                "loop_key": row["loop_key"],
                "name": name,
                "trigger_host": host,
                "schedule_cron": row.get("schedule_cron"),
                "invocations_per_day": inv,
                "cost_usd_monthly": _estimate_cost(host, inv, loop_map),
                "last_receipt_at": last_at,
                "last_receipt_kind": row.get("last_receipt_kind") or receipt_kind,
                "last_receipt_ref": row.get("last_receipt_ref") or {},
                "value_class": vc,
                "receipt_named": bool(named or row.get("last_receipt_ref")),
                "audit_flags": flags,
                "census_run_id": run_id,
                "census_at": at,
                "updated_at": at,
                "metadata": row.get("metadata") or {},
            }
        )
    out.append(traffic_intake_row(loop_map))
    return out


def upsert_census(rows: list[dict[str, Any]]) -> dict[str, Any]:
    url, key = _supabase_cfg()
    if not url or not key:
        return {"ok": False, "error": "supabase_not_configured", "upserted": 0, "at": _now()}

    sys.path.insert(0, str(ROOT / "scripts"))
    from ensure_truth_log_schema_v1 import apply_migrations  # noqa: WPS433

    sql_014 = ROOT / "infra/supabase/portfolio-spine/migrations/014_workflow_census_v1.sql"
    probe_req = urllib.request.Request(
        f"{url}/rest/v1/{TABLE}?select=loop_key&limit=1",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(probe_req, timeout=15):
            pass
    except urllib.error.HTTPError:
        mig = apply_migrations(files=(sql_014,))
        if not mig.get("ok"):
            return {"ok": False, "error": "migration_failed", "migration": mig, "upserted": 0, "at": _now()}

    payload = []
    for row in rows:
        payload.append(
            {
                "loop_key": row["loop_key"],
                "name": row["name"],
                "trigger_host": row["trigger_host"],
                "schedule_cron": row.get("schedule_cron"),
                "invocations_per_day": row.get("invocations_per_day"),
                "cost_usd_monthly": row.get("cost_usd_monthly"),
                "last_receipt_at": row.get("last_receipt_at"),
                "last_receipt_kind": row.get("last_receipt_kind"),
                "last_receipt_ref": row.get("last_receipt_ref") or {},
                "value_class": row["value_class"],
                "receipt_named": bool(row.get("receipt_named")),
                "audit_flags": row.get("audit_flags") or [],
                "census_run_id": row["census_run_id"],
                "census_at": row["census_at"],
                "updated_at": row["updated_at"],
                "metadata": row.get("metadata") or {},
            }
        )

    req = urllib.request.Request(
        f"{url}/rest/v1/{TABLE}?on_conflict=loop_key",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            inserted = body if isinstance(body, list) else [body]
            return {
                "ok": True,
                "upserted": len(inserted),
                "census_run_id": rows[0]["census_run_id"] if rows else _run_id(),
                "at": _now(),
            }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        return {"ok": False, "status": exc.code, "error": detail, "upserted": 0, "at": _now()}


def apply_audit_rules(rows: list[dict[str, Any]], *, insert: bool = True) -> dict[str, Any]:
    """Four deterministic weekly audit rules → improvement_queue."""
    from workflow_census_audit_v1 import findings_from_census  # noqa: WPS433

    findings = findings_from_census(rows)
    result: dict[str, Any] = {
        "ok": True,
        "findings": len(findings),
        "rules_triggered": [f.get("rule") for f in findings],
        "at": _now(),
    }
    if not insert or not findings:
        result["inserted"] = 0
        return result

    from improvement_queue_insert_v1 import insert_findings  # noqa: WPS433

    ins = insert_findings(findings)
    result["inserted"] = ins.get("inserted", 0)
    result["queue_ok"] = ins.get("ok")
    return result


def run_census(*, write: bool = True, audit: bool = True) -> dict[str, Any]:
    rows = merge_census_rows()
    summary = {
        "REVENUE": 0,
        "GUARD": 0,
        "META": 0,
        "NONE": 0,
    }
    cost = {k: 0.0 for k in summary}
    for row in rows:
        vc = str(row.get("value_class") or "META")
        summary[vc] = summary.get(vc, 0) + 1
        cost[vc] = cost.get(vc, 0.0) + float(row.get("cost_usd_monthly") or 0.0)

    out: dict[str, Any] = {
        "schema": "workflow-census-run-v1",
        "ok": True,
        "at": _now(),
        "loop_count": len(rows),
        "census_run_id": rows[0]["census_run_id"] if rows else _run_id(),
        "summary_by_value_class": summary,
        "cost_usd_monthly_by_class": {k: round(v, 2) for k, v in cost.items()},
        "meta_vs_guard_revenue": {
            "meta_cost": round(cost.get("META", 0.0), 2),
            "guard_plus_revenue": round(cost.get("GUARD", 0.0) + cost.get("REVENUE", 0.0), 2),
            "red_flag": cost.get("META", 0.0) > (cost.get("GUARD", 0.0) + cost.get("REVENUE", 0.0)),
        },
        "revenue_lane_empty": summary.get("REVENUE", 0) == 0,
    }

    if write:
        out["supabase"] = upsert_census(rows)
        out["ok"] = out["ok"] and bool(out["supabase"].get("ok"))
    if audit:
        out["audit"] = apply_audit_rules(rows, insert=write)

    receipt_path = Path.home() / ".sina" / "workflow-census-last-run-v1.json"
    try:
        receipt_path.write_text(json.dumps({**out, "rows_sample": rows[:5]}, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    out["report_line"] = (
        f"workflow_census · loops={len(rows)} · "
        f"REV={summary.get('REVENUE',0)} GUARD={summary.get('GUARD',0)} "
        f"META={summary.get('META',0)} · meta_red={out['meta_vs_guard_revenue']['red_flag']}"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="No Supabase write or queue insert")
    ap.add_argument("--no-audit", action="store_true")
    args = ap.parse_args()
    row = run_census(write=not args.dry_run, audit=not args.no_audit)
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
