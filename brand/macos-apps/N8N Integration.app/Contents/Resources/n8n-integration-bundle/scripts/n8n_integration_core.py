#!/usr/bin/env python3
"""N8N Integration — standalone founder app API router."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PORT = int(os.environ.get("N8N_INTEGRATION_PORT", "13026"))
VERSION = "1.8.3"
BRIEF_PATH = Path.home() / ".sina" / "n8n-intelligence" / "brief-latest.md"
RECEIPT_PATH = Path.home() / ".sina" / "n8n-integration-last-receipt.json"
HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))


def _fetch_cloud_workers_live(*, fast: bool = False) -> dict:
    """Pull queue head — disk cache first on fast path, then Hub HTTP."""
    phase_path = Path.home() / ".sina" / "phase-observed-v1.json"
    if fast and phase_path.is_file():
        try:
            phase = json.loads(phase_path.read_text(encoding="utf-8"))
            head = phase.get("cloud_forge_run_head") or phase.get("queue_head")
            last = phase.get("cloud_forge_run_last_completed") or phase.get("last_completed")
            if head:
                return {
                    "ok": True,
                    "source": "disk:phase-observed-v1.json",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "queue_head": head,
                    "last_completed": last,
                    "pipe": "LIVE",
                    "pending_count": None,
                    "event_count": None,
                    "auto_proceed_enabled": (Path.home() / ".sina" / "cloud-forge-run-auto-proceed-v1.flag").is_file(),
                    "hub_line": f"cloud head {head} · last {last or '—'} · disk sync",
                }
        except (OSError, json.JSONDecodeError):
            pass
    import urllib.request

    url = f"http://127.0.0.1:{HUB_PORT}/api/cloud-workers/v1"
    timeout = 6.0 if fast else 20.0
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SourceA-n8n-integration/1.7", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            cw = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "source": url}
    plans = cw.get("plans") or {}
    cloud_rows = plans.get("cloud_forge") or []
    sit = cw.get("situation") or {}
    head = sit.get("queue_head")
    auto = (cw.get("auto_runtime") or {}).get("auto_proceed_enabled")
    return {
        "ok": bool(cw.get("ok")),
        "source": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "queue_head": head,
        "last_completed": sit.get("last_completed"),
        "pipe": sit.get("pipe"),
        "pending_count": sum(1 for r in cloud_rows if r.get("status") in ("pending", "head")),
        "event_count": len(cw.get("events") or []),
        "auto_proceed_enabled": auto,
        "hub_line": f"cloud head {head or '—'} · last {sit.get('last_completed') or '—'} · autopilot {'ARMED' if auto else 'OFF'}",
    }


def _fetch_chain_live(*, fast: bool = False, max_age_s: int = 45) -> dict:
    """Use fresh receipt when available; full path runs light hub slice."""
    receipt = Path.home() / ".sina" / "living-system-chain-validate-receipt-v1.json"
    try:
        if receipt.is_file():
            row = json.loads(receipt.read_text(encoding="utf-8"))
            at = row.get("at") or ""
            if at:
                from datetime import datetime, timezone

                ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - ts).total_seconds()
                if row.get("chains") and (fast or age <= max_age_s):
                    return row
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    if fast:
        return {
            "ok": None,
            "summary_line": "Chain — tap Validate living chains",
            "stale": True,
        }
    try:
        from living_system_chain_validate_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


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


def _automation_24_7_status() -> dict:
    """24/7 Cloud Forge Run motors — CF cron, n8n backup, Mac auto-tick."""
    sina = Path.home() / ".sina"
    tick = {}
    hub = {}
    try:
        if (sina / "cloud-auto-runtime-tick-receipt-v1.json").is_file():
            tick = json.loads((sina / "cloud-auto-runtime-tick-receipt-v1.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    try:
        if (sina / "hub-cloud-forge-run-proceed-receipt-v1.json").is_file():
            hub = json.loads((sina / "hub-cloud-forge-run-proceed-receipt-v1.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    try:
        from cloud_workers_hub_v1 import auto_runtime_status  # noqa: WPS433

        ar = auto_runtime_status()
    except Exception as exc:
        ar = {"ok": False, "error": str(exc)[:120]}
    n8n_wf_active = None
    try:
        from n8n_automation import n8n_status_payload  # noqa: WPS433

        st = n8n_status_payload()
        n8n_wf_active = bool(st.get("n8n_running"))
    except Exception:
        pass
    decision = str(tick.get("decision") or "")
    blocker = None
    if decision == "rate_limited":
        blocker = (tick.get("for_founder") or {}).get("show_this") or "Mac auto-tick rate limited (15m) — CF cron still runs on Railway"
    elif decision == "observe_only":
        blocker = "Autopilot OFF — arm ~/.sina/cloud-forge-run-auto-proceed-v1.flag"
    elif hub.get("ok") is False:
        blocker = f"Last proceed FAIL · plan {hub.get('plan_id') or '—'}"
    armed = bool(ar.get("auto_proceed_enabled"))
    head = ar.get("head") or ""
    return {
        "ok": armed and not blocker,
        "schema": "automation-24-7-status-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "armed": armed,
        "queue_head": head,
        "last_proceed_at": hub.get("at"),
        "last_proceed_plan": hub.get("plan_id"),
        "last_proceed_ok": hub.get("ok"),
        "last_tick_at": tick.get("at"),
        "last_tick_decision": decision or "—",
        "blocker": blocker,
        "cron": ar.get("cron") or "*/15 * * * *",
        "motors": [
            {
                "id": "cf_cron",
                "label": "Cloudflare Worker (primary 24/7)",
                "url": "sourcea-cloud-auto-runtime-tick-v1.witness-bc.workers.dev",
                "schedule": "*/15 * * * *",
            },
            {
                "id": "n8n_cron",
                "label": "n8n wf-cloud-auto-runtime-v1 (Mac awake backup)",
                "active": n8n_wf_active,
                "schedule": "*/15 * * * *",
            },
            {
                "id": "mac_auto_tick",
                "label": "Mac auto-tick (backup when armed)",
                "armed": armed,
                "last_at": tick.get("at"),
                "decision": decision or "—",
            },
        ],
        "summary_line": (
            f"24/7 automation · head {head or '—'} · autopilot {'ARMED' if armed else 'OFF'}"
            + (f" · blocker: {blocker}" if blocker else " · motors LIVE")
        ),
        "for_founder": {
            "show_this": (
                f"Queue {head or '—'} · autopilot {'ARMED' if armed else 'OFF'} · "
                f"last proceed {hub.get('plan_id') or '—'} · CF+n8n cron */15"
                + (f" · {blocker}" if blocker else "")
            )
        },
    }


def build_report_fast() -> dict:
    """Sub-3s founder glance — no n8n auto-start, no intelligence capture."""
    from n8n_automation import FIXTURE_DIR, n8n_status_payload  # noqa: WPS433
    from n8n_intelligence import load_latest  # noqa: WPS433

    st = n8n_status_payload()
    manifest_path = FIXTURE_DIR / "workflow_manifest.json"
    wf_total = 0
    try:
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            wf_total = len(manifest.get("workflows") or manifest if isinstance(manifest, list) else [])
            if isinstance(manifest, dict) and not wf_total:
                wf_total = len(manifest.get("workflows") or [])
    except (OSError, json.JSONDecodeError):
        wf_total = 0
    latest = load_latest()
    intel = {"ok": False}
    if latest.get("ok"):
        snap = latest.get("snapshot") or {}
        intel = {
            "ok": True,
            "refreshed": False,
            "snapshot": snap,
            "analysis": snap.get("analysis"),
            "stack_score": (snap.get("analysis") or {}).get("stack_health_score"),
            "grade": (snap.get("analysis") or {}).get("grade"),
        }
    workflows: list = []
    ok_count = 0
    if latest.get("ok"):
        snap_checks = (((latest.get("snapshot") or {}).get("workflows") or {}).get("checks") or [])
        workflows = [{"id": c.get("id"), "name": c.get("name", c.get("id")), "ok": c.get("ok")} for c in snap_checks]
        ok_count = sum(1 for w in workflows if w.get("ok"))
        wf_total = max(wf_total, len(snap_checks))

    cloud = _fetch_cloud_workers_live(fast=True)
    chain = _fetch_chain_live(fast=True)
    automation = _automation_24_7_status()
    n8n_on = bool(st.get("n8n_running"))
    rt_on = bool(st.get("runtime_running"))

    report: dict = {
        "ok": True,
        "report_mode": "fast",
        "standalone": True,
        "version": VERSION,
        "app": "n8n-integration",
        "port": PORT,
        "status": st,
        "workflows": workflows,
        "intelligence": _enrich_intelligence(intel),
        "quality": {
            "workflow_ok_count": ok_count,
            "workflow_total": wf_total,
            "workflow_all_ok": ok_count == wf_total and wf_total > 0,
            "stack_score": intel.get("stack_score"),
            "grade": intel.get("grade"),
            "n8n_running": n8n_on,
        },
        "cloud_workers_live": cloud,
        "chain_live": chain,
        "automation_24_7": automation,
        "local_api": f"http://127.0.0.1:{PORT}/api/n8n-integration",
        "webhook_url": f"http://127.0.0.1:{PORT}/api/n8n-integration",
        "status_line": (
            cloud.get("hub_line")
            or f"n8n {'running' if n8n_on else 'stopped'} · runtime {'on' if rt_on else 'optional'} · hub {'up' if st.get('hub_running') else 'down'}"
        ),
        "loading_hint": "Live tiles loaded · full wire on Refresh or Capture intelligence",
        "brief_exists": BRIEF_PATH.is_file(),
        "brief_preview": "",
    }
    if report["brief_exists"]:
        try:
            report["brief_preview"] = BRIEF_PATH.read_text(encoding="utf-8")[:1200]
        except OSError:
            pass
    try:
        from validator_machine_v1 import hub_slice, terminal_tail  # noqa: WPS433

        vm = hub_slice(app_id="n8n_integration")
        tt = terminal_tail(lines=40)
        report["validator_machine"] = {
            **vm,
            "terminal_lines": tt.get("terminal_lines") or [],
            "terminal_running": tt.get("running"),
            "terminal_log": tt.get("log_path"),
        }
    except Exception as exc:
        report["validator_machine"] = {"ok": False, "error": str(exc)[:120]}
    return report


def build_report() -> dict:
    """Full wire report — never auto-starts n8n (use action start)."""
    import subprocess

    from n8n_automation import automation_payload  # noqa: WPS433

    report = automation_payload()
    st = report.get("status") or {}
    report["standalone"] = True
    report["report_mode"] = "full"
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
        from portfolio_mail_integration_wire_v1 import wire_status as pm_wire  # noqa: WPS433

        report["portfolio_mail_wire"] = pm_wire()
    except Exception as e:
        report["portfolio_mail_wire"] = {"wired": False, "error": str(e)}

    try:
        from ai_unify_api_v1 import status_payload  # noqa: WPS433

        report["ai_api"] = status_payload()
    except Exception as e:
        report["ai_api"] = {"ok": False, "error": str(e)}

    wfs = report.get("workflows") or []
    ok_count = sum(1 for w in wfs if w.get("ok"))
    wf_total = len(wfs)
    snapshot_checks = (((report.get("intelligence") or {}).get("snapshot") or {}).get("workflows") or {}).get("checks") or []
    if snapshot_checks:
        snap_ok = sum(1 for w in snapshot_checks if w.get("ok"))
        snap_total = len(snapshot_checks)
        # Use the best live view to avoid stale red tiles when disk snapshot is newer.
        if snap_ok >= ok_count:
            ok_count = snap_ok
            wf_total = max(wf_total, snap_total)
    analysis = report["intelligence"].get("analysis") or {}
    report["quality"] = {
        "workflow_ok_count": ok_count,
        "workflow_total": wf_total,
        "workflow_all_ok": ok_count == wf_total and wf_total > 0,
        "stack_score": report["intelligence"].get("stack_score"),
        "grade": report["intelligence"].get("grade"),
        "n8n_running": (report.get("status") or {}).get("n8n_running"),
    }
    st2 = report.get("status") or {}
    n8n_on = bool(st2.get("n8n_running"))
    rt_on = bool(st2.get("runtime_running"))
    report["status_line"] = (
        (report.get("cloud_workers_live") or {}).get("hub_line")
        or (
            f"n8n {'running' if n8n_on else 'stopped'} · runtime {'on' if rt_on else 'optional'} · hub up"
            if n8n_on
            else "n8n stopped — auto-start on refresh or bash scripts/n8n_wire_cloud_forge_run_v1.sh"
        )
    )
    report["runtime_optional"] = True
    report["cloud_workers_live"] = _fetch_cloud_workers_live()
    report["chain_live"] = _fetch_chain_live()
    try:
        from validator_machine_v1 import hub_slice as vm_hub  # noqa: WPS433

        report["validator_machine"] = vm_hub(app_id="n8n_integration")
    except Exception as exc:
        report["validator_machine"] = {"ok": False, "error": str(exc)[:120]}
    try:
        from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433

        report["ui_contract"] = build_ui_contract("n8n_integration", port=PORT)
    except Exception:
        report["ui_contract"] = {"ui_mode": "founder_glance", "version": VERSION}
    report["ok"] = True
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
        return build_report_fast()

    if action in ("report_full", "report_slow"):
        return build_report()

    if action == "validate_chain":
        from validator_machine_v1 import run_terminal_session  # noqa: WPS433

        tier = str(body.get("tier") or "probe")
        result = run_terminal_session(app_id="n8n_integration", tier=tier, include_chain=True)
        result["automation_24_7"] = _automation_24_7_status()
        result["cloud_workers_live"] = _fetch_cloud_workers_live(fast=True)
        chain_receipt = Path.home() / ".sina" / "living-system-chain-validate-receipt-v1.json"
        if chain_receipt.is_file():
            try:
                chain_doc = json.loads(chain_receipt.read_text(encoding="utf-8"))
                result["chains"] = chain_doc.get("chains") or []
                result["summary_line"] = chain_doc.get("summary_line")
            except (OSError, json.JSONDecodeError):
                pass
        _write_receipt(action, {"ok": result.get("ok"), "message": result.get("summary_line")})
        return result

    if action == "validator_run":
        from validator_machine_v1 import run_terminal_session, start_terminal_session_async  # noqa: WPS433

        tier = str(body.get("tier") or "probe")
        if body.get("async"):
            return start_terminal_session_async(app_id="n8n_integration", tier=tier, include_chain=True)
        return run_terminal_session(app_id="n8n_integration", tier=tier, include_chain=bool(body.get("chain", True)))

    if action == "force_auto_tick":
        from cloud_auto_runtime_v1 import run_auto_tick  # noqa: WPS433

        result = run_auto_tick(force=True, llm_provider=str(body.get("llm_provider") or "openrouter"))
        result["automation_24_7"] = _automation_24_7_status()
        _write_receipt(action, result)
        return result

    if action == "validator_terminal_tail":
        from validator_machine_v1 import terminal_tail  # noqa: WPS433

        return terminal_tail(lines=int(body.get("lines") or 80))

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

    if action == "wire_portfolio_mail":
        from portfolio_mail_integration_wire_v1 import wire_all as pm_wire  # noqa: WPS433

        result = pm_wire(import_cursor=bool(body.get("import_cursor", False)))
        _write_receipt(action, result)
        return result

    if action == "open_portfolio_mail":
        hub = int(os.environ.get("SINA_COMMAND_PORT", "13020"))
        return _open_url(f"http://127.0.0.1:{hub}/mail-hub/")

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
