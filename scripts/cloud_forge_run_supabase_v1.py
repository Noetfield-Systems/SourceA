#!/usr/bin/env python3
"""Cloud Forge Run → Supabase — per-plan row on ship (Railway motor)."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infra/supabase/portfolio-spine/migrations/003_cloud_forge_run_rows_v1.sql"
MIGRATION_ORIGIN = ROOT / "infra/supabase/portfolio-spine/migrations/004_cloud_forge_run_rows_origin_v1.sql"
STORE = "receipts/forge-seed"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_headless() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return True
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return Path("/app/receipts").is_dir()


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    table = os.environ.get("CLOUD_FORGE_RUN_SUPABASE_TABLE", "cloud_forge_run_rows").strip()
    return {"url": url, "key": key, "table": table or "cloud_forge_run_rows"}


def _load_secrets_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and val and not os.environ.get(key):
            os.environ[key] = val


def ensure_env() -> None:
    """Load portfolio-spine secrets when not already in env."""
    if os.environ.get("SUPABASE_URL") and (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    ):
        for extra in (
            Path.home() / ".sourcea-secrets/portfolio-spine-db.env",
            Path.home() / ".sourcea-secrets/portfolio-spine.env",
        ):
            _load_secrets_file(extra)
        return
    for candidate in (
        Path.home() / ".sourcea-secrets/portfolio-spine.env",
        Path.home() / ".sourcea-secrets/portfolio-spine-db.env",
        Path.home() / ".sina/portfolio-spine.env",
    ):
        _load_secrets_file(candidate)


def table_probe(*, cfg: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = cfg or _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "exists": False}
    params = urllib.parse.urlencode({"select": "plan_id", "limit": "1"})
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
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(body) if body.strip() else []
            return {"ok": True, "exists": True, "status": resp.status, "sample_count": len(rows)}
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        missing = exc.code == 404 or "PGRST205" in err or "42P01" in err or "does not exist" in err.lower()
        return {
            "ok": not missing,
            "exists": not missing,
            "status": exc.code,
            "error": err[:300],
        }
    except Exception as exc:
        return {"ok": False, "exists": False, "error": str(exc)[:200]}


def apply_origin_migration() -> dict[str, Any]:
    """Apply origin column migration (004) if SQL file present."""
    ensure_env()
    if not MIGRATION_ORIGIN.is_file():
        return {"ok": False, "error": "origin_migration_missing"}
    sql = MIGRATION_ORIGIN.read_text(encoding="utf-8")
    mgmt = _apply_via_management_api(sql)
    if mgmt.get("ok"):
        return {**mgmt, "migration": "004_cloud_forge_run_rows_origin_v1"}
    db_url = (
        os.environ.get("SUPABASE_DB_URL", "").strip()
        or os.environ.get("DATABASE_URL", "").strip()
        or os.environ.get("POSTGRES_URL", "").strip()
    )
    if db_url:
        try:
            proc = subprocess.run(
                ["psql", db_url, "-v", "ON_ERROR_STOP=1", "-f", str(MIGRATION_ORIGIN)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode == 0:
                return {"ok": True, "applied": True, "method": "psql", "migration": "004"}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    pg = _apply_via_psycopg(sql)
    if pg.get("ok"):
        return {**pg, "migration": "004"}
    return {"ok": False, "error": "origin_migration_not_applied", "management": mgmt, "psycopg": pg}


def apply_migration_if_missing() -> dict[str, Any]:
    ensure_env()
    cfg = _supabase_cfg()
    probe = table_probe(cfg=cfg)
    if probe.get("exists"):
        return {"ok": True, "skipped": True, "reason": "table_exists", "table": cfg["table"]}
    if not MIGRATION.is_file():
        return {"ok": False, "error": "migration_missing", "path": str(MIGRATION)}

    sql = MIGRATION.read_text(encoding="utf-8")
    mgmt = _apply_via_management_api(sql)
    if mgmt.get("ok"):
        return {**mgmt, "table": cfg["table"]}

    db_url = (
        os.environ.get("SUPABASE_DB_URL", "").strip()
        or os.environ.get("DATABASE_URL", "").strip()
        or os.environ.get("POSTGRES_URL", "").strip()
    )
    if db_url:
        try:
            proc = subprocess.run(
                ["psql", db_url, "-v", "ON_ERROR_STOP=1", "-f", str(MIGRATION)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode == 0:
                return {"ok": True, "applied": True, "method": "psql", "table": cfg["table"]}
            return {
                "ok": False,
                "error": "psql_failed",
                "stderr": (proc.stderr or proc.stdout or "")[:400],
            }
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "psql_timeout"}

    pg = _apply_via_psycopg(sql)
    if pg.get("ok"):
        return {**pg, "table": cfg["table"]}

    return {
        "ok": False,
        "error": "migration_not_applied",
        "hint": (
            "Add SUPABASE_DB_PASSWORD to ~/.sourcea-secrets/portfolio-spine.env "
            "or SUPABASE_ACCESS_TOKEN, or paste SQL in Supabase dashboard"
        ),
        "dashboard_sql": f"https://supabase.com/dashboard/project/{os.environ.get('SUPABASE_PROJECT_ID', '')}/sql/new",
        "migration_path": str(MIGRATION),
        "probe": probe,
        "management": mgmt,
        "psycopg": pg,
    }


def _apply_via_management_api(sql: str) -> dict[str, Any]:
    token = (
        os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
        or os.environ.get("SUPABASE_PAT", "").strip()
    )
    if not token:
        for path in (
            Path.home() / ".config/supabase/access-token",
            Path.home() / ".supabase/access-token",
        ):
            if path.is_file():
                token = path.read_text(encoding="utf-8").strip()
                break
    ref = os.environ.get("SUPABASE_PROJECT_ID", "").strip()
    if not token or not ref:
        return {"ok": False, "skipped": True, "error": "management_token_or_project_missing"}
    url = f"https://api.supabase.com/v1/projects/{ref}/database/query"
    req = urllib.request.Request(
        url,
        data=json.dumps({"query": sql}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"ok": 200 <= resp.status < 300, "applied": True, "method": "management_api", "body": body[:200]}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
            "status": exc.code,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _resolve_ipv4(host: str) -> str | None:
    try:
        infos = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)
        return infos[0][4][0] if infos else None
    except OSError:
        return None


def _pooler_region() -> str:
    return os.environ.get("SUPABASE_REGION", "us-west-1").strip() or "us-west-1"


def _psycopg_connect_attempts(ref: str) -> list[dict[str, Any]]:
    """Valid Supabase host/port/user triples — avoid pooler+postgres (ENOIDENTIFIER)."""
    region = _pooler_region()
    pooler = os.environ.get("SUPABASE_POOLER_HOST", f"aws-0-{region}.pooler.supabase.com").strip()
    direct_host = f"db.{ref}.supabase.co"
    attempts: list[dict[str, Any]] = [
        {
            "host": direct_host,
            "hostaddr": _resolve_ipv4(direct_host),
            "port": 5432,
            "user": "postgres",
            "options": None,
        },
        {
            "host": pooler,
            "hostaddr": _resolve_ipv4(pooler),
            "port": 6543,
            "user": f"postgres.{ref}",
            "options": f"project={ref}",
        },
        {
            "host": pooler,
            "hostaddr": _resolve_ipv4(pooler),
            "port": 5432,
            "user": f"postgres.{ref}",
            "options": f"project={ref}",
        },
    ]
    return attempts


def _exec_psycopg_sql(
    psycopg2: Any,
    *,
    connect_target: str,
    connect_kwargs: dict[str, Any],
    sql: str,
) -> dict[str, Any]:
    conn = psycopg2.connect(**connect_kwargs, connect_timeout=12)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.close()
    return {
        "ok": True,
        "applied": True,
        "method": "psycopg",
        "connect_target": connect_target,
        "host": connect_kwargs.get("host"),
        "port": connect_kwargs.get("port"),
        "user": connect_kwargs.get("user"),
    }


def _apply_via_psycopg(sql: str) -> dict[str, Any]:
    password = (
        os.environ.get("SUPABASE_DB_PASSWORD", "").strip()
        or os.environ.get("POSTGRES_PASSWORD", "").strip()
    )
    ref = os.environ.get("SUPABASE_PROJECT_ID", "").strip()
    db_url = (
        os.environ.get("SUPABASE_DB_URL", "").strip()
        or os.environ.get("DATABASE_URL", "").strip()
    )
    if not ref and not db_url:
        return {"ok": False, "skipped": True, "error": "db_ref_or_url_missing"}
    if not password and not db_url:
        return {"ok": False, "skipped": True, "error": "db_password_missing"}
    try:
        import psycopg2  # noqa: WPS433
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"],
            check=False,
            timeout=120,
        )
        try:
            import psycopg2  # noqa: WPS433
        except ImportError:
            return {"ok": False, "error": "psycopg2_missing"}

    attempts_log: list[dict[str, Any]] = []
    last_err = ""

    if db_url:
        try:
            return _exec_psycopg_sql(
                psycopg2,
                connect_target="SUPABASE_DB_URL",
                connect_kwargs={"dsn": db_url},
                sql=sql,
            )
        except Exception as exc:
            last_err = str(exc)[:200]
            attempts_log.append({"target": "SUPABASE_DB_URL", "error": last_err})

    if password and ref:
        enc = urllib.parse.quote(password, safe="")
        direct_host = f"db.{ref}.supabase.co"
        direct_ipv4 = _resolve_ipv4(direct_host)
        built = f"postgresql://postgres:{enc}@{direct_host}:5432/postgres?sslmode=require"
        if direct_ipv4:
            built += f"&hostaddr={direct_ipv4}"
        try:
            return _exec_psycopg_sql(
                psycopg2,
                connect_target="direct_built_url",
                connect_kwargs={"dsn": built},
                sql=sql,
            )
        except Exception as exc:
            last_err = str(exc)[:200]
            attempts_log.append({"target": "direct_built_url", "error": last_err})

        for attempt in _psycopg_connect_attempts(ref):
            kwargs: dict[str, Any] = {
                "host": attempt["host"],
                "port": attempt["port"],
                "user": attempt["user"],
                "password": password,
                "dbname": "postgres",
                "sslmode": "require",
            }
            if attempt.get("hostaddr"):
                kwargs["hostaddr"] = attempt["hostaddr"]
            if attempt.get("options"):
                kwargs["options"] = f"-c {attempt['options']}"
            target = f"{attempt['host']}:{attempt['port']} user={attempt['user']}"
            try:
                row = _exec_psycopg_sql(
                    psycopg2,
                    connect_target=target,
                    connect_kwargs=kwargs,
                    sql=sql,
                )
                return row
            except Exception as exc:
                last_err = str(exc)[:200]
                attempts_log.append({"target": target, "error": last_err})

    return {
        "ok": False,
        "error": last_err or "psycopg_connect_failed",
        "attempts": attempts_log[-5:],
    }


def _sellable(proof_tier: str) -> bool:
    return proof_tier == "verified_fetch"


def row_from_ship(
    *,
    plan_id: str,
    cycle_row: dict[str, Any],
    plan: dict[str, Any] | None,
    artifact_doc: dict[str, Any],
    trigger_source: str | None = None,
) -> dict[str, Any]:
    plan = plan or {}
    proof_tier = str(artifact_doc.get("proof_tier") or "")
    shipped_at = str(cycle_row.get("at") or artifact_doc.get("at") or _now())
    status = "PASS" if cycle_row.get("ok") else "FAIL"
    batch_id: int | None = None
    try:
        from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

        obs = read_head().get("observed") if isinstance(read_head().get("observed"), dict) else {}
        if obs.get("batch_id") is not None:
            batch_id = int(obs["batch_id"])
    except Exception:
        pass

    dispatch = cycle_row.get("cloud_dispatch") if isinstance(cycle_row.get("cloud_dispatch"), dict) else {}
    return {
        "plan_id": plan_id,
        "status": status,
        "validator_result": str(cycle_row.get("validator_result") or ""),
        "evidence_source": str(artifact_doc.get("evidence_source") or dispatch.get("evidence_source") or ""),
        "proof_tier": proof_tier,
        "sellable": _sellable(proof_tier),
        "maps_registry": str(plan.get("maps_registry") or artifact_doc.get("maps_registry") or ""),
        "workstream": str(plan.get("workstream") or artifact_doc.get("workstream") or ""),
        "competitor": str(plan.get("competitor") or artifact_doc.get("competitor") or ""),
        "source_url": str(artifact_doc.get("source_url") or dispatch.get("source_url") or ""),
        "http_status": artifact_doc.get("http_status") if artifact_doc.get("http_status") is not None else dispatch.get("http_status"),
        "artifact_path": str(cycle_row.get("artifact_path") or ""),
        "dispatch_receipt_url": str(dispatch.get("receipt_url") or dispatch.get("receipt_path") or ""),
        "evidence_snippets": artifact_doc.get("evidence_snippets") or [],
        "artifact": artifact_doc,
        "shipped_at": shipped_at,
        "batch_id": batch_id,
        "trigger_source": trigger_source or os.environ.get("CLOUD_FORGE_RUN_TRIGGER_SOURCE"),
        "origin": str(cycle_row.get("origin") or artifact_doc.get("origin") or plan.get("origin") or ""),
        "updated_at": _now(),
    }


def upsert_row(row: dict[str, Any], *, cfg: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = cfg or _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "skipped": True, "error": "supabase_not_configured"}
    if not _is_headless() and not os.environ.get("CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC"):
        return {"ok": False, "skipped": True, "error": "mac_writes_blocked"}

    params = urllib.parse.urlencode({"on_conflict": "plan_id"})
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{params}"
    req = urllib.request.Request(
        url,
        data=json.dumps(row).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return {"ok": 200 <= resp.status < 300, "status": resp.status, "plan_id": row.get("plan_id")}
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        if "42P01" in err or "does not exist" in err.lower():
            applied = apply_migration_if_missing()
            if applied.get("ok") and applied.get("applied"):
                return upsert_row(row, cfg=cfg)
        cause = "rate_limit" if exc.code == 429 else "http_error"
        return {
            "ok": False,
            "status": exc.code,
            "error": err[:300],
            "cause": cause,
            "plan_id": row.get("plan_id"),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "cause": "transport_error", "plan_id": row.get("plan_id")}


def upsert_row_with_retry(
    row: dict[str, Any],
    *,
    cfg: dict[str, str] | None = None,
    max_attempts: int = 5,
) -> dict[str, Any]:
    """Retry until PostgREST ack or hard fail — no silent sink drops."""
    last: dict[str, Any] = {"ok": False, "error": "no_attempt"}
    for attempt in range(1, max_attempts + 1):
        last = upsert_row(row, cfg=cfg)
        if last.get("ok") or last.get("skipped"):
            last["attempts"] = attempt
            return last
        if attempt < max_attempts:
            time.sleep(min(2 ** (attempt - 1), 8))
    last["attempts"] = max_attempts
    last["failure_class"] = "supabase_sink_not_acked"
    return last


def persist_shipped_row(
    cycle_row: dict[str, Any],
    *,
    plan: dict[str, Any] | None = None,
    artifact_doc: dict[str, Any] | None = None,
    trigger_source: str | None = None,
) -> dict[str, Any]:
    if not cycle_row.get("ok"):
        return {"ok": False, "skipped": True, "reason": "not_pass"}
    plan_id = str(cycle_row.get("plan_id") or "")
    artifact_doc = artifact_doc or cycle_row.get("forge_seed_artifact") or {}
    if not plan_id:
        return {"ok": False, "skipped": True, "reason": "missing_plan_id"}
    row = row_from_ship(
        plan_id=plan_id,
        cycle_row=cycle_row,
        plan=plan,
        artifact_doc=artifact_doc if isinstance(artifact_doc, dict) else {},
        trigger_source=trigger_source,
    )
    return upsert_row_with_retry(row)


def batch_plan_ids_from_doc(doc: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(p.get("id") or "")
            for p in doc.get("plans") or []
            if str(p.get("id") or "").startswith("CLOUD-SEC-")
        },
        key=lambda x: int(x.rsplit("-", 1)[-1]),
    )


def count_batch_in_supabase(*, plan_ids: list[str], cfg: dict[str, str] | None = None) -> dict[str, Any]:
    ensure_env()
    cfg = cfg or _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "present": [], "missing": plan_ids}
    quoted = ",".join(f'"{pid}"' for pid in plan_ids)
    params = urllib.parse.urlencode({"select": "plan_id", "plan_id": f"in.({quoted})"})
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{params}"
    req = urllib.request.Request(
        url,
        headers={"apikey": cfg["key"], "Authorization": f"Bearer {cfg['key']}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            present = sorted({str(r["plan_id"]) for r in rows if r.get("plan_id")})
            missing = [pid for pid in plan_ids if pid not in present]
            return {
                "ok": True,
                "expected": len(plan_ids),
                "supabase_count": len(present),
                "present": present,
                "missing": missing,
            }
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "error": err[:300], "status": exc.code, "missing": plan_ids}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "missing": plan_ids}


def count_batch_on_railway(
    *,
    plan_ids: list[str],
    base_url: str = "https://sourcea-fbe-runner-production.up.railway.app",
) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    base = base_url.rstrip("/")

    def _has_artifact(pid: str) -> bool:
        detail_url = f"{base}/api/cloud-forge-run/evidence-audit/v1?plan_id={urllib.parse.quote(pid)}"
        req = urllib.request.Request(detail_url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                detail = json.loads(resp.read().decode("utf-8", errors="replace"))
            return bool(detail.get("ok") and detail.get("artifact"))
        except Exception:
            return False

    for pid in plan_ids:
        if _has_artifact(pid):
            present.append(pid)
        else:
            missing.append(pid)
    if missing:
        retry_present: list[str] = []
        retry_missing: list[str] = []
        for pid in missing:
            if _has_artifact(pid):
                retry_present.append(pid)
            else:
                retry_missing.append(pid)
        if retry_present:
            present.extend(retry_present)
            missing = retry_missing
    return {
        "ok": True,
        "expected": len(plan_ids),
        "railway_count": len(present),
        "present": present,
        "missing": missing,
        "source": base,
    }


def count_batch_origin_in_supabase(
    *,
    plan_ids: list[str],
    origin: str = "mac_replay",
    cfg: dict[str, str] | None = None,
) -> dict[str, Any]:
    ensure_env()
    cfg = cfg or _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "mac_replay_count": 0}
    quoted = ",".join(f'"{pid}"' for pid in plan_ids)
    params = urllib.parse.urlencode(
        {
            "select": "plan_id,origin",
            "plan_id": f"in.({quoted})",
            "origin": f"eq.{origin}",
        }
    )
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{params}"
    req = urllib.request.Request(
        url,
        headers={"apikey": cfg["key"], "Authorization": f"Bearer {cfg['key']}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            present = sorted({str(r["plan_id"]) for r in rows if r.get("plan_id")})
            return {
                "ok": True,
                "origin": origin,
                "mac_replay_count": len(present),
                "present": present,
            }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "mac_replay_count": 0}


def batch_sink_invariant(
    *,
    batch_id: int,
    batch_path: Path | None = None,
    railway_url: str = "https://sourcea-fbe-runner-production.up.railway.app",
) -> dict[str, Any]:
    path = batch_path or ROOT / f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json"
    if not path.is_file():
        return {"ok": False, "error": "batch_file_missing", "path": str(path)}
    doc = json.loads(path.read_text(encoding="utf-8"))
    plan_ids = batch_plan_ids_from_doc(doc)
    sb = count_batch_in_supabase(plan_ids=plan_ids)
    rw = count_batch_on_railway(plan_ids=plan_ids, base_url=railway_url)
    mac = count_batch_origin_in_supabase(plan_ids=plan_ids, origin="mac_replay")
    mac_count = int(mac.get("mac_replay_count") or 0)
    rw_count = int(rw.get("railway_count") or 0)
    sb_count = int(sb.get("supabase_count") or 0)
    covered = set(rw.get("present") or []) | set(mac.get("present") or [])
    ok = (
        sb.get("ok")
        and rw.get("ok")
        and sb_count == len(plan_ids)
        and len(covered) == sb_count
        and (rw_count + mac_count) == sb_count
    )
    reason = None
    if not ok:
        reason = (
            f"supabase_count={sb_count} railway_count={rw_count} mac_replay_count={mac_count} "
            f"expected={len(plan_ids)}"
        )
    return {
        "ok": ok,
        "schema": "cloud-forge-batch-sink-invariant-v1",
        "at": _now(),
        "batch_id": batch_id,
        "expected": len(plan_ids),
        "supabase_count": sb_count,
        "railway_count": rw_count,
        "mac_replay_count": mac_count,
        "supabase_missing": sb.get("missing") or [],
        "railway_missing": rw.get("missing") or [],
        "mac_replay_ids": mac.get("present") or [],
        "blocked_reason": reason,
        "verdict": "PASS" if ok else "BLOCKED_WITH_REASON",
        "law": "railway_count + mac_replay_count == supabase_count",
    }


def query_rows(*, limit: int = 20, proof_tier: str | None = None) -> dict[str, Any]:
    ensure_env()
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "rows": []}
    params: dict[str, str] = {
        "select": "plan_id,status,proof_tier,sellable,maps_registry,artifact_path,shipped_at,evidence_source,http_status",
        "order": "shipped_at.desc",
        "limit": str(max(1, min(limit, 500))),
    }
    if proof_tier:
        params["proof_tier"] = f"eq.{proof_tier}"
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Accept": "application/json",
            "Prefer": "count=exact",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(body) if body.strip() else []
            count_hdr = resp.headers.get("Content-Range", "")
            total: int | None = None
            if "/" in count_hdr:
                try:
                    total = int(count_hdr.split("/")[-1])
                except ValueError:
                    total = None
            return {"ok": True, "rows": rows, "count": len(rows), "total": total, "table": cfg["table"]}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
            "rows": [],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "rows": []}


def count_rows() -> dict[str, Any]:
    ensure_env()
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured"}
    params = urllib.parse.urlencode({"select": "plan_id", "limit": "1"})
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "count=exact",
        },
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            count_hdr = resp.headers.get("Content-Range", "")
            total = 0
            if "/" in count_hdr:
                try:
                    total = int(count_hdr.split("/")[-1])
                except ValueError:
                    pass
            return {"ok": True, "total": total, "table": cfg["table"]}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def ensure_schema(*, allow_mac: bool = False) -> dict[str, Any]:
    if allow_mac:
        os.environ["CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC"] = "1"
    return apply_migration_if_missing()


def _artifact_root(*, root: Path | None = None) -> Path:
    if root is not None:
        return root / STORE
    if _is_headless() and Path("/app/receipts/forge-seed").is_dir():
        return Path("/app/receipts/forge-seed")
    return ROOT / STORE


def backfill_from_artifacts(*, root: Path | None = None, limit: int = 0) -> dict[str, Any]:
    os.environ.setdefault("CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC", "1")
    ensure_env()
    applied = apply_migration_if_missing()
    art_root = _artifact_root(root=root)
    if not art_root.is_dir():
        return {"ok": False, "error": "artifact_dir_missing", "path": str(art_root), "migration": applied}

    upserted = 0
    failed = 0
    errors: list[str] = []
    paths = sorted(art_root.glob("CLOUD-SEC-*/artifact-v1.json"))
    if not paths:
        paths = sorted(art_root.glob("*/artifact-v1.json"))
    if limit > 0:
        paths = paths[:limit]
    for ap in paths:
        try:
            doc = json.loads(ap.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            failed += 1
            continue
        plan_id = str(doc.get("plan_id") or ap.parent.name)
        rel_base = Path("/app") if str(art_root).startswith("/app") else ROOT
        try:
            artifact_rel = str(ap.relative_to(rel_base))
        except ValueError:
            artifact_rel = str(ap)
        cycle_row = {
            "ok": True,
            "plan_id": plan_id,
            "at": doc.get("at") or _now(),
            "validator_result": "PASS",
            "artifact_path": artifact_rel,
            "forge_seed_artifact": doc,
        }
        result = upsert_row(row_from_ship(plan_id=plan_id, cycle_row=cycle_row, plan=None, artifact_doc=doc))
        if result.get("ok"):
            upserted += 1
        else:
            failed += 1
            if len(errors) < 5:
                errors.append(f"{plan_id}: {result.get('error', result.get('status'))}")
    return {
        "ok": failed == 0 or upserted > 0,
        "upserted": upserted,
        "failed": failed,
        "scanned": len(paths),
        "errors": errors,
        "migration": applied,
    }


def backfill_from_railway(
    *,
    base_url: str = "https://sourcea-fbe-runner-production.up.railway.app",
    page_size: int = 100,
    max_rows: int = 0,
) -> dict[str, Any]:
    """Pull shipped rows from Railway evidence-audit → Supabase (Mac/CI backfill)."""
    os.environ.setdefault("CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC", "1")
    ensure_env()
    applied = apply_migration_if_missing()
    if not applied.get("ok") and not applied.get("skipped"):
        return {"ok": False, "error": "migration_required", "migration": applied}

    upserted = 0
    failed = 0
    scanned = 0
    errors: list[str] = []
    offset = 0
    base = base_url.rstrip("/")

    while True:
        if max_rows and scanned >= max_rows:
            break
        limit = min(page_size, max_rows - scanned) if max_rows else page_size
        params = urllib.parse.urlencode({"limit": str(limit), "offset": str(offset)})
        list_url = f"{base}/api/cloud-forge-run/evidence-audit/v1?{params}"
        req = urllib.request.Request(list_url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as exc:
            return {
                "ok": False,
                "error": f"railway_fetch_failed: {exc}",
                "upserted": upserted,
                "scanned": scanned,
                "migration": applied,
            }

        rows = payload.get("rows") or []
        if not rows:
            break

        for r in rows:
            if max_rows and scanned >= max_rows:
                break
            scanned += 1
            plan_id = str(r.get("plan_id") or "")
            if not plan_id or not r.get("has_artifact"):
                failed += 1
                continue
            artifact_doc: dict[str, Any] = {}
            detail_url = f"{base}/api/cloud-forge-run/evidence-audit/v1?plan_id={urllib.parse.quote(plan_id)}"
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(detail_url, headers={"Accept": "application/json"}),
                    timeout=45,
                ) as dresp:
                    detail = json.loads(dresp.read().decode("utf-8", errors="replace"))
                    artifact_doc = detail.get("artifact") if isinstance(detail.get("artifact"), dict) else {}
            except Exception:
                artifact_doc = {}

            if not artifact_doc:
                artifact_doc = {
                    "plan_id": plan_id,
                    "at": r.get("at"),
                    "evidence_source": r.get("evidence_source"),
                    "proof_tier": r.get("proof_tier"),
                    "source_url": r.get("source_url"),
                    "http_status": r.get("http_status"),
                    "evidence_snippets": [],
                    "maps_registry": r.get("maps_registry"),
                    "competitor": r.get("competitor"),
                }

            cycle_row = {
                "ok": r.get("validator_result") == "PASS",
                "plan_id": plan_id,
                "at": r.get("at") or artifact_doc.get("at") or _now(),
                "validator_result": r.get("validator_result"),
                "artifact_path": r.get("artifact_path"),
                "forge_seed_artifact": artifact_doc,
            }
            result = upsert_row(row_from_ship(plan_id=plan_id, cycle_row=cycle_row, plan=None, artifact_doc=artifact_doc))
            if result.get("ok"):
                upserted += 1
            else:
                failed += 1
                if len(errors) < 5:
                    errors.append(f"{plan_id}: {result.get('error', result.get('status'))}")

        if len(rows) < limit:
            break
        offset += len(rows)

    return {
        "ok": upserted > 0,
        "upserted": upserted,
        "failed": failed,
        "scanned": scanned,
        "errors": errors,
        "migration": applied,
        "source": base,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Cloud Forge Run Supabase wire")
    ap.add_argument("--apply-migration", action="store_true")
    ap.add_argument("--query", action="store_true", help="Query recent rows")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--backfill-railway", action="store_true")
    ap.add_argument("--railway-url", default="https://sourcea-fbe-runner-production.up.railway.app")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ensure_env()
    if args.apply_migration:
        row = apply_migration_if_missing()
    elif args.count:
        row = count_rows()
    elif args.backfill:
        row = backfill_from_artifacts(limit=args.limit if args.limit != 20 else 0)
    elif args.backfill_railway:
        row = backfill_from_railway(base_url=args.railway_url, max_rows=args.limit if args.limit != 20 else 0)
    elif args.query:
        row = query_rows(limit=args.limit)
    else:
        row = {"probe": table_probe(), "cfg_table": _supabase_cfg().get("table")}

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row)
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
