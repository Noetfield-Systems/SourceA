#!/usr/bin/env python3
"""Wire n8n ↔ Chat Unify ↔ Cursor — merge webhooks, transcript import, glue config."""
from __future__ import annotations

import json
import subprocess
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WF_NAME = "wf-chat-unify-merge-receipt-v1"
WF_PATH = SOURCE_A / "n8n/workflows/wf-chat-unify-merge-receipt-v1.json"
WIRE_RECEIPT = SINA / "n8n-chat-unify-wire-v1.json"
CHAT_UNIFY_PORT = int(__import__("os").environ.get("CHAT_UNIFY_PORT", "13023"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _http_json(url: str, *, method: str = "GET", body: dict | None = None, timeout: float = 8.0) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": resp.status, "body": json.loads(raw) if raw.strip() else {}}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw[:400]}
        return {"ok": False, "status": e.code, "body": parsed, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e), "url": url}


def _probe_health(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def _glue_urls() -> dict[str, str]:
    from n8n_glue_config_v1 import load_config  # noqa: WPS433

    cfg = load_config()
    urls = dict(cfg.get("urls") or {})
    webhooks = dict(cfg.get("webhooks") or {})
    urls.setdefault("chat_unify", f"http://127.0.0.1:{CHAT_UNIFY_PORT}")
    webhooks.setdefault("chat_unify_merge", "http://127.0.0.1:5678/webhook/chat-unify-merge")
    return {"urls": urls, "webhooks": webhooks}


def ensure_chat_unify_up() -> dict[str, Any]:
    base = f"http://127.0.0.1:{CHAT_UNIFY_PORT}"
    if _probe_health(f"{base}/health"):
        return {"ok": True, "already_up": True, "url": base}
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts/serve-chat-unify.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=90,
    )
    import time

    for _ in range(40):
        if _probe_health(f"{base}/health"):
            return {"ok": True, "started": True, "url": base}
        time.sleep(0.25)
    return {"ok": False, "error": "chat_unify_start_timeout", "url": base}


def ensure_n8n_up() -> dict[str, Any]:
    if _probe_health("http://127.0.0.1:5678/healthz"):
        return {"ok": True, "already_up": True}
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts/founder-start-n8n.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=120,
    )
    import time

    for _ in range(60):
        if _probe_health("http://127.0.0.1:5678/healthz"):
            return {"ok": True, "started": True}
        time.sleep(2)
    return {"ok": False, "error": "n8n_start_timeout"}


def _wf_row() -> tuple[str, int] | None:
    if not N8N_DB.is_file():
        return None
    try:
        con = sqlite3.connect(N8N_DB)
        row = con.execute(
            "SELECT id, active FROM workflow_entity WHERE name = ? ORDER BY updatedAt DESC LIMIT 1",
            (WF_NAME,),
        ).fetchone()
        con.close()
        return (str(row[0]), int(row[1])) if row else None
    except sqlite3.Error:
        return None


def _merge_receipt_exists() -> bool:
    p = SINA / "n8n-receipts/intelligence/chat-unify-merge.jsonl"
    return p.is_file() and p.stat().st_size > 0


def _webhook_registered() -> bool:
    if not N8N_DB.is_file():
        return False
    try:
        con = sqlite3.connect(N8N_DB)
        row = con.execute(
            "SELECT 1 FROM webhook_entity WHERE webhookPath = ?",
            ("chat-unify-merge",),
        ).fetchone()
        con.close()
        return bool(row)
    except sqlite3.Error:
        return False


def _restart_n8n() -> dict[str, Any]:
    subprocess.run(["pkill", "-f", "n8n start"], check=False)
    subprocess.run(["pkill", "-f", "npx.*n8n"], check=False)
    import time

    time.sleep(2)
    return ensure_n8n_up()


def import_merge_workflow(*, active: bool = True) -> dict[str, Any]:
    if not WF_PATH.is_file():
        return {"ok": False, "error": "workflow_missing", "path": str(WF_PATH)}
    import uuid

    if N8N_DB.is_file():
        try:
            con = sqlite3.connect(N8N_DB)
            rows = con.execute("SELECT id FROM workflow_entity WHERE name = ?", (WF_NAME,)).fetchall()
            for (wf_id,) in rows:
                con.execute("DELETE FROM workflow_entity WHERE id = ?", (wf_id,))
                con.execute("DELETE FROM workflow_history WHERE workflowId = ?", (wf_id,))
                con.execute("DELETE FROM webhook_entity WHERE workflowId = ?", (wf_id,))
            con.commit()
            con.close()
        except sqlite3.Error:
            pass

    data = json.loads(WF_PATH.read_text(encoding="utf-8"))
    wf_id = str(uuid.uuid4())
    data["id"] = wf_id
    data["active"] = active
    tmp = SINA / "n8n-import-chat-unify-merge.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    proc = subprocess.run(
        ["npx", "--yes", "n8n", "import:workflow", f"--input={tmp}"],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        return {"ok": False, "error": "import_failed", "tail": (proc.stderr or proc.stdout or "")[-500:]}
    restart = _restart_n8n()
    import time

    time.sleep(4)
    return {
        "ok": bool(restart.get("ok")),
        "wf_id": wf_id,
        "imported": True,
        "active": active,
        "webhook_registered": _webhook_registered(),
        "n8n_restart": restart,
    }


def activate_merge_workflow() -> dict[str, Any]:
    row = _wf_row()
    if row and row[1] and _webhook_registered():
        return {"ok": True, "wf_id": row[0], "already_active": True, "webhook_registered": True}
    if not row:
        imported = import_merge_workflow(active=True)
        if not imported.get("ok"):
            return imported
        row = _wf_row()
    if not row:
        return {"ok": False, "error": "workflow_not_in_db"}
    wf_id = row[0]
    if not _publish_workflow(wf_id):
        return {"ok": False, "error": "publish_failed", "wf_id": wf_id}
    restart = _restart_n8n()
    import time

    time.sleep(6)
    registered = _webhook_registered()
    return {
        "ok": bool(restart.get("ok")),
        "wf_id": wf_id,
        "activated": True,
        "webhook_registered": registered,
        "n8n_restart": restart,
        "note": "If webhook 404, merge still flows via direct glue runner",
    }


def _publish_workflow(wf_id: str) -> bool:
    proc = subprocess.run(
        ["n8n", "publish:workflow", f"--id={wf_id}"],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=90,
    )
    return proc.returncode == 0


def _direct_merge_ingest(payload: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        [
            __import__("sys").executable,
            str(SOURCE_A / "scripts/n8n_glue_runner_v1.py"),
            "chat-unify-merge",
            "--payload",
            json.dumps(payload),
        ],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        body = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        body = {"raw": (proc.stdout or proc.stderr or "")[-500:]}
    return {
        "ok": proc.returncode == 0 and bool(body.get("ok", True)),
        "mode": "direct_glue",
        "exit": proc.returncode,
        "body": body,
    }


def post_merge_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    glue = _glue_urls()
    url = glue["webhooks"].get("chat_unify_merge") or "http://127.0.0.1:5678/webhook/chat-unify-merge"
    body = {
        "source": "chat-unify",
        "event": "merge_receipt",
        "at": _now(),
        **payload,
    }
    result = _http_json(url, method="POST", body=body, timeout=20)
    result["webhook_url"] = url
    if result.get("ok"):
        result["mode"] = "webhook"
        return result
    direct = _direct_merge_ingest(body)
    result["ok"] = bool(direct.get("ok"))
    result["mode"] = "direct_glue"
    result["fallback"] = direct
    return result


def notify_merge(payload: dict[str, Any]) -> dict[str, Any]:
    """Called from Chat Unify after merge — best-effort n8n webhook + intelligence ingest."""
    row = _wf_row()
    if not row or not row[1]:
        activate_merge_workflow()
    wh = post_merge_webhook(payload)
    intel: dict[str, Any] = {"ok": False, "skipped": True}
    if wh.get("ok"):
        try:
            from n8n_intelligence import handle_intelligence_action  # noqa: WPS433

            intel = handle_intelligence_action(
                {
                    "action": "ingest",
                    "source": "chat-unify",
                    "event": "merge_receipt",
                    "data": {
                        "extract_count": payload.get("extract_count"),
                        "contradiction_count": payload.get("contradiction_count"),
                        "brief_chars": payload.get("brief_chars"),
                        "receipt_path": payload.get("receipt_path"),
                    },
                }
            )
        except Exception as e:
            intel = {"ok": False, "error": str(e)}
    out = {
        "ok": bool(wh.get("ok")),
        "webhook": wh,
        "intelligence": intel,
        "at": _now(),
    }
    return out


def sync_cursor_transcripts(*, limit: int = 3) -> dict[str, Any]:
    """Import latest Cursor agent transcripts into Chat Unify via local API."""
    cu = ensure_chat_unify_up()
    if not cu.get("ok"):
        return cu
    base = cu.get("url") or f"http://127.0.0.1:{CHAT_UNIFY_PORT}"
    report = _http_json(f"{base}/api/chat-unify", method="POST", body={"action": "report"})
    if not report.get("ok"):
        return {"ok": False, "error": "chat_unify_report_failed", **report}
    candidates = (report.get("body") or {}).get("transcript_candidates") or []
    imported: list[dict] = []
    skipped: list[dict] = []
    for cand in candidates[: max(1, limit)]:
        path = cand.get("path") or ""
        if not path:
            continue
        r = _http_json(
            f"{base}/api/chat-unify",
            method="POST",
            body={
                "action": "import_transcript",
                "path": path,
                "label": cand.get("name") or "Cursor transcript",
                "tags": ["CURSOR", "THREAD-CHAT-CONSOLIDATION"],
            },
            timeout=60,
        )
        body = r.get("body") or {}
        if body.get("ok"):
            if body.get("skipped"):
                skipped.append({"path": path, "extract": body.get("extract")})
            else:
                imported.append({"path": path, "extract": body.get("extract")})
        else:
            skipped.append({"path": path, "error": body.get("error") or r.get("error")})
    return {
        "ok": True,
        "imported_count": len(imported),
        "skipped_count": len(skipped),
        "imported": imported,
        "skipped": skipped,
        "cursor_roots": ["~/.cursor/projects/**/agent-transcripts"],
        "chat_unify_url": base,
    }


def wire_status() -> dict[str, Any]:
    glue = _glue_urls()
    chat_url = glue["urls"].get("chat_unify", f"http://127.0.0.1:{CHAT_UNIFY_PORT}")
    wf = _wf_row()
    status = {
        "schema": "n8n-chat-unify-wire-v1",
        "at": _now(),
        "chat_unify_up": _probe_health(f"{chat_url}/health"),
        "chat_unify_url": chat_url,
        "n8n_up": _probe_health("http://127.0.0.1:5678/healthz"),
        "n8n_integration_up": _probe_health("http://127.0.0.1:13026/health"),
        "merge_workflow": WF_NAME,
        "merge_workflow_active": bool(wf and wf[1]),
        "merge_workflow_id": wf[0] if wf else None,
        "webhook_url": glue["webhooks"].get("chat_unify_merge"),
        "cursor_transcript_glob": "~/.cursor/projects/**/agent-transcripts/*.jsonl",
        "wired": False,
    }
    status["wired"] = bool(
        status["chat_unify_up"]
        and status["n8n_up"]
        and (status["merge_workflow_active"] or _merge_receipt_exists())
    )
    status["webhook_registered"] = _webhook_registered()
    status["glue_fallback"] = not status["webhook_registered"]
    return status


def wire_all(*, import_cursor: bool = True, cursor_limit: int = 2) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    from n8n_glue_config_v1 import load_config, save_config  # noqa: WPS433

    cfg = load_config()
    cfg.setdefault("urls", {})["chat_unify"] = f"http://127.0.0.1:{CHAT_UNIFY_PORT}"
    cfg.setdefault("webhooks", {})["chat_unify_merge"] = "http://127.0.0.1:5678/webhook/chat-unify-merge"
    cfg["chat_unify_wired_at"] = _now()
    save_config(cfg)
    steps.append({"step": "glue_config", "ok": True})

    n8n = ensure_n8n_up()
    steps.append({"step": "n8n_up", **n8n})
    cu = ensure_chat_unify_up()
    steps.append({"step": "chat_unify_up", **cu})
    act = activate_merge_workflow()
    steps.append({"step": "activate_merge_wf", **act})
    if not act.get("ok") and act.get("already_active"):
        pass
    elif not act.get("ok") and _wf_row() and _wf_row()[1]:
        act = {"ok": True, "wf_id": _wf_row()[0], "already_active": True}
        steps[-1] = {"step": "activate_merge_wf", **act}

    if not _probe_health("http://127.0.0.1:5678/healthz"):
        n8n_retry = ensure_n8n_up()
        steps.append({"step": "n8n_recover", **n8n_retry})

    probe = post_merge_webhook({"event": "wire_test", "extract_count": 0, "test": True})
    steps.append({"step": "webhook_probe", "ok": bool(probe.get("ok")), "status": probe.get("status")})

    cursor_sync: dict[str, Any] = {"ok": True, "skipped": True}
    if import_cursor:
        cursor_sync = sync_cursor_transcripts(limit=cursor_limit)
        steps.append({"step": "cursor_import", "ok": bool(cursor_sync.get("ok")), "imported": cursor_sync.get("imported_count", 0)})

    status = wire_status()
    ok = bool(
        n8n.get("ok")
        and cu.get("ok")
        and act.get("ok")
        and probe.get("ok")
        and status.get("wired")
    )
    receipt = {
        "ok": ok,
        "schema": "n8n-chat-unify-wire-v1",
        "at": _now(),
        "status": status,
        "steps": steps,
        "cursor_sync": cursor_sync,
        "founder_line": (
            "n8n ↔ Chat Unify ↔ Cursor wired — merge fires webhook; transcripts import from ~/.cursor"
            if ok
            else "Wire incomplete — check steps"
        ),
        "next_founder": (
            "Chat Unify → Merge all → n8n logs receipt · N8N Integration → Wire Chat Unify to refresh"
            if ok
            else "N8N Integration → Wire Chat Unify · activate wf-chat-unify-merge-receipt-v1"
        ),
    }
    WIRE_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="n8n ↔ Chat Unify ↔ Cursor wire")
    ap.add_argument("--wire", action="store_true", help="Full connect sequence")
    ap.add_argument("--status", action="store_true", help="Wire status only")
    ap.add_argument("--sync-cursor", action="store_true", help="Import Cursor transcripts to Chat Unify")
    ap.add_argument("--limit", type=int, default=2)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.wire:
        result = wire_all(import_cursor=True, cursor_limit=args.limit)
    elif args.sync_cursor:
        result = sync_cursor_transcripts(limit=args.limit)
    else:
        result = wire_status()
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
