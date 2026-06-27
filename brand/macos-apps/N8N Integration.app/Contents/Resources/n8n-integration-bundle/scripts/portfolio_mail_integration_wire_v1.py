#!/usr/bin/env python3
"""Portfolio Mail ↔ Chat Unify ↔ N8N Integration — three-app glue wire."""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
WIRE_RECEIPT = SINA / "portfolio-mail-integration-wire-v1.json"
MAIL_PORT = int(os.environ.get("PORTFOLIO_MAIL_PORT", "13028"))
CHAT_UNIFY_PORT = int(os.environ.get("CHAT_UNIFY_PORT", "13023"))
N8N_INTEGRATION_PORT = int(os.environ.get("N8N_INTEGRATION_PORT", "13026"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _probe(url: str, *, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def _http_json(url: str, *, method: str = "GET", body: dict | None = None, timeout: float = 12.0) -> dict[str, Any]:
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
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw[:400]}
        return {"ok": False, "status": exc.code, "body": parsed, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "url": url}


def _urls() -> dict[str, str]:
    mail = f"http://127.0.0.1:{MAIL_PORT}"
    return {
        "hub": mail,
        "portfolio_mail": f"{mail}/mail-hub/",
        "portfolio_mail_api": f"{mail}/api/portfolio-mail/v1",
        "portfolio_mail_integration_api": f"{mail}/api/portfolio-mail/v1/integration",
        "chat_unify": f"http://127.0.0.1:{CHAT_UNIFY_PORT}",
        "chat_unify_api": f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/chat-unify",
        "n8n_integration": f"http://127.0.0.1:{N8N_INTEGRATION_PORT}",
        "n8n_integration_api": f"http://127.0.0.1:{N8N_INTEGRATION_PORT}/api/n8n-integration",
        "mac_law": "http://127.0.0.1:8781/",
        "mac_law_api": "http://127.0.0.1:8781/api/mac-law/health",
    }


def ensure_hub_up() -> dict[str, Any]:
    """Legacy name — starts standalone portfolio mail server (:13028), not Worker Hub."""
    base = f"http://127.0.0.1:{MAIL_PORT}"
    if _probe(f"{base}/health"):
        return {"ok": True, "already_up": True, "url": base}
    subprocess.Popen(
        ["python3", str(SOURCE_A / "scripts/portfolio-mail-server.py")],
        cwd=str(SOURCE_A),
        env={**os.environ, "PORTFOLIO_MAIL_PORT": str(MAIL_PORT), "SINA_SOURCE_A": str(SOURCE_A)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import time

    for _ in range(40):
        if _probe(f"{base}/health"):
            return {"ok": True, "started": True, "url": base}
        time.sleep(0.25)
    return {"ok": False, "error": "mail_start_timeout", "url": base}


def ensure_chat_unify_up() -> dict[str, Any]:
    from n8n_chat_unify_wire_v1 import ensure_chat_unify_up as _cu  # noqa: WPS433

    return _cu()


def ensure_n8n_integration_up() -> dict[str, Any]:
    base = f"http://127.0.0.1:{N8N_INTEGRATION_PORT}"
    if _probe(f"{base}/health"):
        return {"ok": True, "already_up": True, "url": base}
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts/serve-n8n-integration.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=90,
    )
    import time

    for _ in range(40):
        if _probe(f"{base}/health"):
            return {"ok": True, "started": True, "url": base}
        time.sleep(0.25)
    return {"ok": False, "error": "n8n_integration_start_timeout", "url": base}


def _save_glue_config() -> dict[str, Any]:
    from n8n_glue_config_v1 import load_config, save_config  # noqa: WPS433

    urls = _urls()
    cfg = load_config()
    cfg.setdefault("urls", {})
    cfg["urls"]["portfolio_mail"] = urls["portfolio_mail"]
    cfg["urls"]["portfolio_mail_api"] = urls["portfolio_mail_api"]
    cfg["urls"]["hub"] = urls["hub"]
    cfg["urls"]["chat_unify"] = urls["chat_unify"]
    cfg["urls"]["n8n_integration"] = urls["n8n_integration"]
    cfg["urls"]["mac_law"] = urls["mac_law"]
    cfg.setdefault("webhooks", {})
    cfg["webhooks"]["portfolio_mail_send"] = (
        cfg["webhooks"].get("portfolio_mail_send") or "http://127.0.0.1:5678/webhook/portfolio-mail-send"
    )
    cfg["portfolio_mail_wired_at"] = _now()
    save_config(cfg)
    return {"ok": True, "config_path": str(SINA / "n8n-glue-config-v1.json")}


def wire_status() -> dict[str, Any]:
    urls = _urls()
    mail_api = _http_json(urls["portfolio_mail_api"] + "?limit=1")
    mail_summary = (mail_api.get("body") or {}).get("summary") or {}
    chat_up = _probe(f"{urls['chat_unify']}/health")
    n8n_int_up = _probe(f"{urls['n8n_integration']}/health")
    mac_law_up = _probe(urls["mac_law_api"])
    hub_up = _probe(f"{urls['hub']}/health")

    chat_unify_wire: dict[str, Any] = {"wired": False}
    try:
        from n8n_chat_unify_wire_v1 import wire_status as cu_wire  # noqa: WPS433

        chat_unify_wire = cu_wire()
    except Exception as exc:
        chat_unify_wire = {"wired": False, "error": str(exc)}

    wired = bool(
        hub_up
        and mail_api.get("ok")
        and chat_up
        and n8n_int_up
        and int(mail_summary.get("ok") or 0) >= 1
    )
    return {
        "schema": "portfolio-mail-integration-wire-v1",
        "at": _now(),
        "wired": wired,
        "urls": urls,
        "hub_up": hub_up,
        "portfolio_mail_up": hub_up and mail_api.get("ok"),
        "portfolio_mail_live_count": int(mail_summary.get("ok") or 0),
        "chat_unify_up": chat_up,
        "n8n_integration_up": n8n_int_up,
        "mac_law_up": mac_law_up,
        "chat_unify_wire": chat_unify_wire,
        "receipt_path": str(WIRE_RECEIPT),
    }


def wire_all(*, import_cursor: bool = False, cursor_limit: int = 2) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    glue = _save_glue_config()
    steps.append({"step": "glue_config", **glue})

    hub = ensure_hub_up()
    steps.append({"step": "hub_up", **hub})
    cu = ensure_chat_unify_up()
    steps.append({"step": "chat_unify_up", **cu})
    n8 = ensure_n8n_integration_up()
    steps.append({"step": "n8n_integration_up", **n8})

    chat_wire: dict[str, Any] = {"ok": True, "skipped": True}
    if import_cursor:
        try:
            from n8n_chat_unify_wire_v1 import wire_all as cu_wire_all  # noqa: WPS433

            chat_wire = cu_wire_all(import_cursor=True, cursor_limit=cursor_limit)
        except Exception as exc:
            chat_wire = {"ok": False, "error": str(exc)}
    else:
        try:
            from n8n_chat_unify_wire_v1 import wire_status as cu_status  # noqa: WPS433

            st = cu_status()
            if not st.get("chat_unify_up"):
                cu2 = ensure_chat_unify_up()
                steps.append({"step": "chat_unify_recover", **cu2})
        except Exception:
            pass
    steps.append({"step": "chat_unify_wire", "ok": bool(chat_wire.get("ok", True))})

    urls = _urls()
    probe = _http_json(
        urls["n8n_integration_api"],
        method="POST",
        body={"action": "report"},
    )
    steps.append({"step": "n8n_integration_probe", "ok": bool(probe.get("ok"))})

    mail_probe = _http_json(urls["portfolio_mail_api"] + "?limit=1")
    steps.append({"step": "portfolio_mail_probe", "ok": bool(mail_probe.get("ok"))})

    mac_law_probe = _probe(urls["mac_law_api"])
    if not mac_law_probe:
        try:
            subprocess.run(
                ["bash", str(SOURCE_A / "scripts/mac_law_surfaces_boot_v1.sh")],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=90,
            )
            mac_law_probe = _probe(urls["mac_law_api"])
        except Exception:
            mac_law_probe = False
    steps.append({"step": "mac_law_probe", "ok": bool(mac_law_probe)})

    status = wire_status()
    ok = bool(
        hub.get("ok")
        and cu.get("ok")
        and n8.get("ok")
        and mail_probe.get("ok")
        and status.get("wired")
    )
    receipt = {
        "ok": ok,
        "schema": "portfolio-mail-integration-wire-v1",
        "at": _now(),
        "status": status,
        "steps": steps,
        "founder_line": (
            "Portfolio Mail · Chat Unify · N8N Integration wired — send mail logs to automation spine"
            if ok
            else "Integration incomplete — run Wire all from Portfolio Mail"
        ),
    }
    WIRE_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    WIRE_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def notify_mail_sent(payload: dict[str, Any]) -> dict[str, Any]:
    """Best-effort fan-out after outbound send — n8n intelligence + chat unify tag."""
    body = {
        "source": "portfolio-mail",
        "event": "mail_sent",
        "at": _now(),
        **payload,
    }
    urls = _urls()
    results: dict[str, Any] = {"ok": True, "at": _now()}

    intel: dict[str, Any] = {"ok": False, "skipped": True}
    try:
        from n8n_intelligence import handle_intelligence_action  # noqa: WPS433

        intel = handle_intelligence_action(
            {
                "action": "ingest",
                "source": "portfolio-mail",
                "event": "mail_sent",
                "data": {
                    "from": payload.get("from"),
                    "to": payload.get("to"),
                    "subject": payload.get("subject"),
                    "dispatch_ref": payload.get("dispatch_ref"),
                },
            }
        )
    except Exception as exc:
        intel = {"ok": False, "error": str(exc)}
    results["intelligence"] = intel

    n8n_post = _http_json(
        urls["n8n_integration_api"],
        method="POST",
        body={"action": "ingest", "source": "portfolio-mail", "event": "mail_sent", "data": body},
        timeout=8,
    )
    results["n8n_integration"] = n8n_post

    cu_post = _http_json(
        urls["chat_unify_api"],
        method="POST",
        body={
            "action": "save_extract",
            "label": f"Mail · {payload.get('subject') or 'sent'}",
            "text": (
                f"Outbound mail\nFrom: {payload.get('from')}\n"
                f"To: {payload.get('to')}\nSubject: {payload.get('subject')}\n"
                f"Ref: {payload.get('dispatch_ref')}"
            ),
            "tags": ["PORTFOLIO-MAIL", "OUTBOUND"],
        },
        timeout=8,
    )
    results["chat_unify"] = cu_post
    results["ok"] = bool(intel.get("ok") or n8n_post.get("ok") or cu_post.get("ok"))
    return results


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Portfolio Mail + Chat Unify + N8N Integration wire")
    ap.add_argument("--wire", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--import-cursor", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.wire:
        result = wire_all(import_cursor=args.import_cursor)
    else:
        result = wire_status()
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
