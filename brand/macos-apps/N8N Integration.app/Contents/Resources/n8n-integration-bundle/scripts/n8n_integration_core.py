#!/usr/bin/env python3
"""N8N Integration — standalone founder app API router."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PORT = int(os.environ.get("N8N_INTEGRATION_PORT", "13026"))
VERSION = "1.6.0"
BRIEF_PATH = Path.home() / ".sina" / "n8n-intelligence" / "brief-latest.md"
RECEIPT_PATH = Path.home() / ".sina" / "n8n-integration-last-receipt.json"


def _enrich_intelligence(intel: dict) -> dict:
    if not isinstance(intel, dict):
        return {"ok": False, "error": "invalid intelligence payload"}
    analysis = intel.get("analysis") or {}
    if not analysis and intel.get("snapshot"):
        analysis = (intel.get("snapshot") or {}).get("analysis") or {}
    intel["stack_score"] = analysis.get("stack_health_score")
    intel["grade"] = analysis.get("grade")
    intel["webhook_url"] = f"http://127.0.0.1:{PORT}/api/n8n-integration"
    intel["webhook_ingest_hint"] = 'POST {"action":"ingest","source":"n8n","event":"...","data":{}}'
    return intel


def build_report() -> dict:
    from n8n_automation import automation_payload  # noqa: WPS433

    report = automation_payload()
    report["standalone"] = True
    report["version"] = VERSION
    report["app"] = "n8n-integration"
    report["port"] = PORT
    report["local_api"] = f"http://127.0.0.1:{PORT}/api/n8n-integration"
    report["webhook_url"] = report["local_api"]
    report["webhook_action"] = "ingest"
    report["state_dir"] = str(Path.home() / ".sina" / "n8n-intelligence")
    report["brief_path"] = str(BRIEF_PATH)
    report["brief_exists"] = BRIEF_PATH.is_file()
    if report["brief_exists"]:
        try:
            report["brief_preview"] = BRIEF_PATH.read_text(encoding="utf-8")[:4000]
        except OSError:
            report["brief_preview"] = ""
    else:
        report["brief_preview"] = ""

    report["intelligence"] = _enrich_intelligence(report.get("intelligence") or {})

    try:
        from n8n_chat_unify_wire_v1 import wire_status  # noqa: WPS433

        report["chat_unify_wire"] = wire_status()
    except Exception as e:
        report["chat_unify_wire"] = {"wired": False, "error": str(e)}

    try:
        from ai_unify_api_v1 import status_payload  # noqa: WPS433

        report["ai_api"] = status_payload()
    except Exception as e:
        report["ai_api"] = {"ok": False, "error": str(e)}

    wfs = report.get("workflows") or []
    ok_count = sum(1 for w in wfs if w.get("ok"))
    analysis = report["intelligence"].get("analysis") or {}
    report["quality"] = {
        "workflow_ok_count": ok_count,
        "workflow_total": len(wfs),
        "workflow_all_ok": ok_count == len(wfs) and len(wfs) > 0,
        "stack_score": report["intelligence"].get("stack_score"),
        "grade": report["intelligence"].get("grade"),
        "n8n_running": (report.get("status") or {}).get("n8n_running"),
    }
    try:
        from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433

        report["ui_contract"] = build_ui_contract("n8n_integration", port=PORT)
    except Exception:
        report["ui_contract"] = {"ui_mode": "founder_glance", "version": VERSION}
    return report


def _write_receipt(action: str, result: dict) -> None:
    try:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(
            json.dumps(
                {
                    "action": action,
                    "at": datetime.now(timezone.utc).isoformat(),
                    "ok": result.get("ok", True),
                    "version": VERSION,
                    "result": {k: result[k] for k in ("message", "ok_count", "total", "grade", "stack_score") if k in result},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass


def _open_url(url: str) -> dict:
    try:
        subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"ok": True, "opened": url}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "url": url}


def handle_action(body: dict | None = None) -> dict:
    body = body or {}
    action = (body.get("action") or "report").strip().lower()

    if action == "report":
        return build_report()

    if action == "export_receipt":
        report = build_report()
        receipt = {
            "ok": True,
            "version": VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "quality": report.get("quality"),
            "status": report.get("status"),
            "workflow_ok": report.get("quality", {}).get("workflow_ok_count"),
            "workflow_total": report.get("quality", {}).get("workflow_total"),
        }
        out = Path.home() / ".sina" / "n8n-integration-export-receipt.json"
        try:
            out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
            receipt["path"] = str(out)
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        return receipt

    if action == "commercial_grade":
        from n8n_commercial_grade_v1 import assess_commercial_ready, upgrade_workflow_files  # noqa: WPS433

        upgrade_workflow_files()
        result = assess_commercial_ready()
        _write_receipt(action, result)
        return result

    if action == "export_commercial_pack":
        from n8n_commercial_grade_v1 import build_sales_pack, upgrade_workflow_files  # noqa: WPS433

        upgrade_workflow_files()
        pack = build_sales_pack()
        pack["ok"] = True
        _write_receipt(action, pack)
        return pack

    if action == "upgrade_all":
        from n8n_commercial_grade_v1 import run_upgrade_all  # noqa: WPS433

        result = run_upgrade_all()
        result["ok"] = bool(result.get("ok"))
        _write_receipt(action, result)
        return result

    if action == "commercial_all":
        from n8n_commercial_grade_v1 import run_finish_all  # noqa: WPS433

        closeout = run_finish_all()
        closeout["ok"] = bool(closeout.get("ok"))
        _write_receipt(action, closeout)
        return closeout

    if action == "open_brief":
        if not BRIEF_PATH.is_file():
            return {"ok": False, "error": "brief_missing", "path": str(BRIEF_PATH)}
        try:
            text = BRIEF_PATH.read_text(encoding="utf-8")
            subprocess.Popen(["open", str(BRIEF_PATH)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"ok": True, "path": str(BRIEF_PATH), "chars": len(text), "brief": text[:12000]}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}

    if action == "open_n8n":
        from n8n_automation import N8N_URL  # noqa: WPS433

        return _open_url(N8N_URL)

    if action == "open_chat_unify":
        port = int(os.environ.get("CHAT_UNIFY_PORT", "13023"))
        return _open_url(f"http://127.0.0.1:{port}/")

    if action == "wire_chat_unify":
        from n8n_chat_unify_wire_v1 import wire_all  # noqa: WPS433

        result = wire_all(
            import_cursor=bool(body.get("import_cursor", True)),
            cursor_limit=int(body.get("limit") or 2),
        )
        _write_receipt(action, result)
        return result

    if action == "sync_cursor_transcripts":
        from n8n_chat_unify_wire_v1 import sync_cursor_transcripts  # noqa: WPS433

        result = sync_cursor_transcripts(limit=int(body.get("limit") or 3))
        _write_receipt(action, result)
        return result

    if action in ("ai_status", "ai_api_status"):
        from ai_unify_api_v1 import status_payload  # noqa: WPS433

        row = status_payload()
        row["ok"] = True
        _write_receipt(action, row)
        return row

    if action == "ai_chat":
        from ai_unify_api_v1 import handle_action as ai_handle  # noqa: WPS433

        result = ai_handle(
            {
                "action": "chat",
                "user": body.get("user") or body.get("text") or body.get("prompt") or "",
                "system": body.get("system") or "",
                "provider": body.get("provider") or "auto",
                "model": body.get("model"),
                "source": "n8n-integration",
            }
        )
        _write_receipt(action, result)
        return result

    if action == "ai_polish":
        from ai_unify_api_v1 import polish_brief  # noqa: WPS433

        result = polish_brief(
            body.get("text") or body.get("brief") or "",
            provider=body.get("provider") or "auto",
            model=body.get("model"),
        )
        _write_receipt(action, result)
        return result

    if action == "ai_critique":
        from ai_unify_api_v1 import critique_brief  # noqa: WPS433

        result = critique_brief(
            body.get("text") or body.get("brief") or "",
            provider=body.get("provider") or "auto",
            model=body.get("model"),
        )
        _write_receipt(action, result)
        return result

    if action == "open_wf8_activate":
        import sqlite3

        wf_id = None
        db = Path.home() / ".n8n" / "database.sqlite"
        if db.is_file():
            try:
                con = sqlite3.connect(db)
                row = con.execute(
                    "SELECT id FROM workflow_entity WHERE name = ? ORDER BY updatedAt DESC LIMIT 1",
                    ("wf-mac-health-cooldown-v1",),
                ).fetchone()
                con.close()
                if row:
                    wf_id = row[0]
            except sqlite3.Error:
                wf_id = None
        url = f"http://127.0.0.1:5678/workflow/{wf_id}" if wf_id else "http://127.0.0.1:5678/workflows"
        opened = _open_url(url)
        opened["message"] = (
            "Toggle Active ON (top-right) for wf-mac-health-cooldown-v1 — registers Cool Down webhook."
        )
        opened["wf8_id"] = wf_id
        return opened

    if action == "open_law":
        from n8n_automation import LAW_PATH  # noqa: WPS433

        if LAW_PATH.is_file():
            return _open_url(f"file://{LAW_PATH}")
        return {"ok": False, "error": "law_missing", "path": str(LAW_PATH)}

    if action == "governance_wire":
        from governance_n8n_openrouter_wire_v1 import wire_all  # noqa: WPS433

        result = wire_all(run_fast=body.get("run_fast", True))
        _write_receipt(action, result)
        return result

    if action in (
        "film_ingest",
        "film_status",
        "film_critic",
        "film_compile",
        "film_ship_gate",
        "film_ship",
        "film_run_and_judge",
    ):
        from n8n_film_factory_wire_v1 import handle_film_action  # noqa: WPS433

        body = dict(body)
        if action == "film_ingest":
            body["action"] = "film_ship_gate"
        else:
            body["action"] = action
        result = handle_film_action(body)
        _write_receipt(action, result)
        return result

    if action == "ingest":
        from n8n_intelligence import handle_intelligence_action  # noqa: WPS433

        result = handle_intelligence_action(body)
        _write_receipt(action, result)
        return result

    if action in ("capture", "refresh", "analyze", "get", "intelligence"):
        from n8n_intelligence import handle_intelligence_action  # noqa: WPS433

        result = handle_intelligence_action(body)
        result = _enrich_intelligence(result)
        _write_receipt(action, result)
        return result

    from n8n_automation import handle_n8n_action  # noqa: WPS433

    result = handle_n8n_action(action)
    if action in ("capture_intelligence", "intelligence"):
        result = _enrich_intelligence(result)
    _write_receipt(action, result)
    return result
