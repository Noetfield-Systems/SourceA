#!/usr/bin/env python3
"""Mac–Cloud spine bridge (L16 W1–W4) — fresh-main, heartbeat, worker_inbox, truth_log dual-write.

Law: docs/GOVERNED_AUTORUN_LAWS_v3.md L16
Contract: data/mac-spine-bridge-contract-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FRESH_MAIN_RECEIPT = Path.home() / ".sina" / "mac-fresh-main-sync-receipt-v1.json"
HEARTBEAT_RECEIPT = Path.home() / ".sina" / "mac-spine-heartbeat-receipt-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
INBOX_JSON = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
FRESHNESS_MINUTES = 30


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(raw: str) -> datetime | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


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
    _load_secrets_file(Path.home() / ".sourcea-secrets" / "portfolio-spine.env")


def _supabase_cfg() -> dict[str, str]:
    ensure_env()
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    return {"url": url, "key": key}


def _git_run(args: list[str], *, timeout: int = 45) -> tuple[int, str]:
    try:
        out = subprocess.check_output(
            ["git", *args],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(ROOT),
            timeout=timeout,
        )
        return 0, out.strip()
    except subprocess.CalledProcessError as exc:
        return exc.returncode, (exc.output or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def _repo_git_state() -> dict[str, Any]:
    _, branch = _git_run(["rev-parse", "--abbrev-ref", "HEAD"])
    _, local_main = _git_run(["rev-parse", "main"])
    _, dirty_out = _git_run(["status", "--porcelain"])
    dirty_count = len([ln for ln in dirty_out.splitlines() if ln.strip()])
    remote = "origin"
    _, origin_main = _git_run(["rev-parse", f"{remote}/main"])
    return {
        "repo": str(ROOT),
        "branch": branch or "unknown",
        "local_main_sha": local_main[:40] if local_main else "",
        "origin_main_sha": origin_main[:40] if origin_main else "",
        "dirty_count": dirty_count,
        "remote": remote,
    }


def _post_rest(*, table: str, row: dict[str, Any], prefer: str = "return=representation") -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "table": table}
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{table}"
    req = urllib.request.Request(
        url,
        data=json.dumps(row).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": prefer,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            inserted: Any = json.loads(body) if body.strip() else {}
            if isinstance(inserted, list) and inserted:
                inserted = inserted[0]
            row_id = inserted.get("id") if isinstance(inserted, dict) else None
            return {"ok": bool(row_id), "id": row_id, "table": table}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "error": exc.read().decode("utf-8", errors="replace")[:400],
            "status": exc.code,
            "table": table,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "table": table}


def _get_rest(*, table: str, params: dict[str, str]) -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "rows": []}
    q = urllib.parse.urlencode(params)
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{table}?{q}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(body) if body.strip() else []
            if not isinstance(rows, list):
                rows = []
            return {"ok": True, "rows": rows}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "rows": []}


def dual_write_mac_truth(
    event: str,
    *,
    payload: dict[str, Any],
    receipt_id: str | None = None,
    deployment_id: str | None = None,
) -> dict[str, Any]:
    """W4 — proof-grade Mac receipt self-register to truth_log; disk stays mirror."""
    event = str(event or "").strip().upper()
    allowed = {
        "MAC_AGENT_HEARTBEAT",
        "MAC_FRESH_MAIN_SYNC",
        "MAC_RECEIPT_MIRROR",
        "MAC_SESSION_GATE",
        "AGENT_SESSION_COST",
        "TIER_ESCALATION",
    }
    if event not in allowed:
        return {"ok": False, "error": "invalid_mac_event", "event": event}
    row = {
        "source": "mac_agent",
        "event": event,
        "deployment_id": (deployment_id or payload.get("sha") or "")[:64] or None,
        "receipt_id": receipt_id or payload.get("receipt_id") or f"mac-{uuid.uuid4().hex[:12]}",
        "payload": payload,
    }
    result = _post_rest(table="truth_log", row=row)
    result["event"] = event
    result["source"] = "mac_agent"
    return result


def _write_mirror_receipt(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_mac_spine_fresh_main(*, agent_id: str = "cursor", skip_fetch: bool = False) -> dict[str, Any]:
    """W1 — fetch origin; block when local main != origin/main."""
    sync_id = f"MFS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    fetch_row: dict[str, Any] = {"skipped": True, "ok": True}
    if not skip_fetch:
        code, out = _git_run(["fetch", "origin", "main", "--quiet"])
        fetch_row = {"ok": code == 0, "exit": code, "output": out[:200]}

    state = _repo_git_state()
    local_sha = state.get("local_main_sha") or ""
    origin_sha = state.get("origin_main_sha") or ""
    fresh = bool(local_sha and origin_sha and local_sha == origin_sha)
    blocked = not fresh and bool(local_sha or origin_sha)

    receipt = {
        "schema": "mac-fresh-main-sync-receipt-v1",
        "sync_id": sync_id,
        "at": _now(),
        "agent_id": agent_id,
        "fetch": fetch_row,
        "local_main_sha": local_sha,
        "origin_main_sha": origin_sha,
        "dirty_count": state.get("dirty_count", 0),
        "repo": state.get("repo"),
        "fresh": fresh,
        "verdict": "PASS" if fresh else "BLOCKED_WITH_REASON",
        "reason": None if fresh else "stale_local_main",
        "action": "git fetch origin && git rebase origin/main" if blocked else None,
        "receipt_path": str(FRESH_MAIN_RECEIPT),
        "law": "L16 W1 — rebase before Mac agent writes",
    }
    _write_mirror_receipt(FRESH_MAIN_RECEIPT, receipt)

    spine = dual_write_mac_truth(
        "MAC_FRESH_MAIN_SYNC",
        payload=receipt,
        receipt_id=f"mac-fresh-main-{sync_id}",
        deployment_id=local_sha,
    )
    receipt["truth_log"] = spine
    _write_mirror_receipt(FRESH_MAIN_RECEIPT, receipt)

    return {
        "ok": fresh,
        "step": "mac_spine_fresh_main",
        "verdict": receipt["verdict"],
        "reason": receipt.get("reason"),
        "local_main_sha": local_sha,
        "origin_main_sha": origin_sha,
        "dirty_count": state.get("dirty_count", 0),
        "sync_id": sync_id,
        "receipt_path": str(FRESH_MAIN_RECEIPT),
        "truth_log": spine,
        "blocked": blocked,
    }


def build_mac_dashboard_row(*, agent_id: str) -> dict[str, Any]:
    """Dashboard row JSON — mac lane; STALE_DATA when last heartbeat >30m."""
    fetched = _get_rest(
        table="mac_agent_heartbeat",
        params={
            "select": "id,agent_id,repo,sha,dirty_count,at,recorded_at",
            "agent_id": f"eq.{agent_id}",
            "order": "at.desc",
            "limit": "1",
        },
    )
    rows = fetched.get("rows") or []
    row = rows[0] if rows else {}
    last_at = str(row.get("at") or row.get("recorded_at") or "")
    age_min: float | None = None
    stale = True
    parsed = _parse_ts(last_at)
    if parsed:
        age_min = (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds() / 60.0
        stale = age_min > FRESHNESS_MINUTES
    status = "STALE_DATA" if stale or not row else "OK"
    return {
        "lane": "mac",
        "workflow_id": "mac_agent_heartbeat",
        "agent_id": agent_id,
        "status": status,
        "freshness_window_min": FRESHNESS_MINUTES,
        "last_at": last_at or None,
        "age_minutes": round(age_min, 1) if age_min is not None else None,
        "sha": row.get("sha"),
        "dirty_count": row.get("dirty_count"),
        "repo": row.get("repo"),
        "spine_row_id": row.get("id"),
        "supabase_ok": fetched.get("ok", False),
    }


def run_mac_spine_heartbeat(*, agent_id: str = "cursor", role: str = "any") -> dict[str, Any]:
    """W2 — POST mac_agent_heartbeat to Supabase spine."""
    state = _repo_git_state()
    at = _now()
    hb_row = {
        "agent_id": agent_id,
        "repo": state.get("repo") or str(ROOT),
        "sha": state.get("local_main_sha") or "",
        "dirty_count": int(state.get("dirty_count") or 0),
        "at": at,
    }
    post = _post_rest(table="mac_agent_heartbeat", row=hb_row)
    dashboard = build_mac_dashboard_row(agent_id=agent_id)

    receipt = {
        "schema": "mac-spine-heartbeat-receipt-v1",
        "at": at,
        "agent_id": agent_id,
        "role": role,
        "heartbeat": hb_row,
        "spine_post": post,
        "dashboard_row": dashboard,
        "receipt_path": str(HEARTBEAT_RECEIPT),
        "law": "L16 W2 — session gate + Hub keepalive",
    }
    _write_mirror_receipt(HEARTBEAT_RECEIPT, receipt)

    truth = dual_write_mac_truth(
        "MAC_AGENT_HEARTBEAT",
        payload={**receipt, "dashboard_row": dashboard},
        receipt_id=f"mac-hb-{agent_id}-{at.replace(':', '').replace('-', '')[:15]}",
        deployment_id=hb_row.get("sha"),
    )
    receipt["truth_log"] = truth
    _write_mirror_receipt(HEARTBEAT_RECEIPT, receipt)

    cfg = _supabase_cfg()
    spine_ok = post.get("ok", False)
    degraded = not spine_ok and not cfg.get("url")

    return {
        "ok": spine_ok or degraded,
        "step": "mac_spine_heartbeat",
        "agent_id": agent_id,
        "spine_post": post,
        "dashboard_row": dashboard,
        "receipt_path": str(HEARTBEAT_RECEIPT),
        "truth_log": truth,
        "degraded": degraded,
    }


def spine_insert_worker_inbox(
    *,
    prompt: str,
    source: str,
    meta: dict[str, Any] | None = None,
    mark_pending: bool = True,
    founder_blocked: bool = False,
) -> dict[str, Any]:
    """W3 — insert worker_inbox spine row (Brain W-LBA routes by insert)."""
    meta = meta or {}
    sa_id = str(meta.get("sa_id") or "")
    op_key = str(meta.get("op_key") or f"inbox-{sa_id}-{uuid.uuid4().hex[:10]}")
    status = "founder_blocked" if founder_blocked else ("pending" if mark_pending else "delivered")
    row = {
        "status": status,
        "lane": "sourcea_worker",
        "source": source,
        "prompt": prompt or "",
        "meta": meta,
        "sa_id": sa_id or None,
        "queue_pos": meta.get("queue_pos"),
        "queue_total": meta.get("queue_total"),
        "queue_role": meta.get("queue_role"),
        "mission_id": meta.get("mission_id"),
        "founder_blocked": founder_blocked,
        "delivered_at": _now() if mark_pending else None,
        "op_key": op_key,
    }
    post = _post_rest(table="worker_inbox", row=row, prefer="return=representation,resolution=merge-duplicates")
    return {"ok": post.get("ok", False), "spine_row": row, "spine_post": post, "op_key": op_key}


def spine_read_worker_inbox_head(*, statuses: tuple[str, ...] = ("pending", "delivered")) -> dict[str, Any]:
    """Read pending head from spine for Mac Worker pickup."""
    status_filter = ",".join(statuses)
    fetched = _get_rest(
        table="worker_inbox",
        params={
            "select": "*",
            "status": f"in.({status_filter})",
            "order": "created_at.asc",
            "limit": "1",
        },
    )
    rows = fetched.get("rows") or []
    head = rows[0] if rows else {}
    return {"ok": fetched.get("ok", False), "head": head, "pending": bool(head)}


def mirror_inbox_to_disk(
    *,
    payload: dict[str, Any],
    spine_row_id: str | None = None,
    source: str = "hub",
) -> dict[str, Any]:
    """W3 — generate READ-ONLY disk mirror from spine payload."""
    meta = payload.get("meta") or {}
    pos = meta.get("queue_pos", "?")
    total = meta.get("queue_total", "?")
    role = meta.get("queue_role", "?")
    sa = meta.get("sa_id", "?")
    text = str(payload.get("prompt") or "")
    delivered_at = str(payload.get("delivered_at") or _now())

    md = f"""<!-- READ-ONLY MIRROR — SSOT: Supabase worker_inbox · do not edit -->
<!-- spine_row={spine_row_id or 'local'} source={source} queue={pos}/{total} role={role} sa={sa} -->
# SourceA Worker — prompt ready (INBOX delivery)

**READ-ONLY.** Spine SSOT: `public.worker_inbox`. Edit on disk is ignored on next sync.

**Lane:** SourceA Worker only — if you are Brain, ignore this file.

**Updated:** {delivered_at}

---

{text}

---

**Worker:** read spine head · execute fully · `WORKER_ROUND_REPORT` · STOP  
**Founder:** stay in Brain or Hub — open Worker chat when ready; no Terminal
"""
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(md, encoding="utf-8")

    disk_payload = dict(payload)
    disk_payload["spine_row_id"] = spine_row_id
    disk_payload["mirror_mode"] = "read_only"
    disk_payload["spine_ssot"] = "public.worker_inbox"
    INBOX_JSON.parent.mkdir(parents=True, exist_ok=True)
    INBOX_JSON.write_text(json.dumps(disk_payload, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "inbox_md": str(INBOX_MD),
        "inbox_json": str(INBOX_JSON),
        "mirror_mode": "read_only",
        "spine_row_id": spine_row_id,
    }


def mirror_mac_receipt_to_truth(
    *,
    receipt_path: Path,
    event: str = "MAC_RECEIPT_MIRROR",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """W4 — dual-write any proof-grade ~/.sina receipt to truth_log."""
    if not receipt_path.is_file():
        return {"ok": False, "error": "receipt_missing", "path": str(receipt_path)}
    try:
        doc = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:120], "path": str(receipt_path)}
    payload = {**doc, **(extra or {}), "mirror_path": str(receipt_path)}
    rid = str(doc.get("gate_id") or doc.get("sync_id") or receipt_path.stem)
    return dual_write_mac_truth(event, payload=payload, receipt_id=f"mac-mirror-{rid}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "command",
        choices=[
            "fresh_main",
            "heartbeat",
            "dashboard_row",
            "inbox_head",
            "mirror_receipt",
        ],
    )
    ap.add_argument("--agent-id", default="cursor")
    ap.add_argument("--role", default="any")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--receipt", default="")
    ap.add_argument("--event", default="MAC_RECEIPT_MIRROR")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.command == "fresh_main":
        row = run_mac_spine_fresh_main(agent_id=args.agent_id, skip_fetch=args.skip_fetch)
    elif args.command == "heartbeat":
        row = run_mac_spine_heartbeat(agent_id=args.agent_id, role=args.role)
    elif args.command == "dashboard_row":
        row = build_mac_dashboard_row(agent_id=args.agent_id)
    elif args.command == "inbox_head":
        row = spine_read_worker_inbox_head()
    elif args.command == "mirror_receipt":
        path = Path(args.receipt).expanduser() if args.receipt else FRESH_MAIN_RECEIPT
        row = mirror_mac_receipt_to_truth(receipt_path=path, event=args.event)
    else:
        row = {"ok": False, "error": "unsupported"}

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
