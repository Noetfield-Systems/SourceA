#!/usr/bin/env python3
"""Forge Terminal Connect — full desktop server (Chat Unify machines + Forge IDE). Default :13029."""
from __future__ import annotations

import json
import mimetypes
import os
import socket
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

def _bundle_root_env() -> str:
    raw = os.environ.get("FORGE_TERMINAL_BUNDLE_ROOT", "").strip()
    if not raw:
        return ""
    root = Path(raw)
    if (root / "scripts" / "forge-terminal-server.py").is_file() or (
        root / "scripts" / "forge_terminal_connect_server_v1.py"
    ).is_file():
        return raw
    return ""


BUNDLE_ROOT = _bundle_root_env()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app" / "connect"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "apps" / "forge-terminal-connect-v1"
    if not APP_DIR.is_dir():
        APP_DIR = SOURCE_A / "scripts" / "chat-unify-standalone"
    SCRIPTS_DIR = SOURCE_A / "scripts"

PORT = int(os.environ.get("FORGE_TERMINAL_PORT", "13029"))
UI_VERSION = "4.0.0-alpha"
STANDALONE = os.environ.get("FORGE_TERMINAL_STANDALONE", "").strip() in ("1", "true", "yes")
CORS_ORIGIN = os.environ.get(
    "FORGE_TERMINAL_CORS_ORIGIN",
    f"http://127.0.0.1:{PORT}" if STANDALONE else "*",
)
UI_FEATURES = (
    "forge_ide",
    "living_chat",
    "desktop_mesh",
    "quality_engine",
    "founder_loop",
    "ord_loop",
    "prompt_forge",
    "proof_pack",
    "vocabulary_intelligence",
    "connect_hub",
    "integrations_api",
    "webhook_triggers",
    "unified_kernel",
    "truth_gate",
    "form_official",
    "forge_terminal",
    "chat_unify_machines",
)


def _resolve_source_a() -> Path:
    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (
        Path.home() / "Desktop" / "SourceA",
        Path(__file__).resolve().parents[1],
    ):
        if (candidate / "CHAT_EXTRACT_UNIFY_PROMPT.txt").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
FORGE_TERMINAL_LIVE = REAL_SA / "apps" / "forge-terminal-v1"
FORGE_TERMINAL_FALLBACK = APP_DIR / "terminal"


def _terminal_dir() -> Path:
    """Prefer live SourceA UI over stale .app bundle — hard refresh + dev parity."""
    use_live = os.environ.get("FORGE_TERMINAL_USE_LIVE_UI", "1").strip().lower() in ("1", "true", "yes")
    if use_live and (FORGE_TERMINAL_LIVE / "terminal.js").is_file():
        return FORGE_TERMINAL_LIVE
    if BUNDLE_ROOT:
        bundled = Path(BUNDLE_ROOT) / "app" / "terminal"
        if bundled.is_dir() and (bundled / "terminal.js").is_file():
            return bundled
    if FORGE_TERMINAL_FALLBACK.is_dir() and (FORGE_TERMINAL_FALLBACK / "terminal.js").is_file():
        return FORGE_TERMINAL_FALLBACK
    return FORGE_TERMINAL_LIVE if FORGE_TERMINAL_LIVE.is_dir() else FORGE_TERMINAL_FALLBACK


FORGE_TERMINAL_DIR = _terminal_dir()


os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("FORGE_TERMINAL_STANDALONE", "1")
os.environ.setdefault("FORGE_TERMINAL_PORT", str(PORT))
os.environ.setdefault("CHAT_UNIFY_PORT", str(PORT))

SHARED_DIR = REAL_SA / "agent-control-panel" / "shared"
FORM_DIR = REAL_SA / "agent-control-panel" / "form"
if BUNDLE_ROOT:
    _bundle = Path(BUNDLE_ROOT)
    if (_bundle / "form" / "index.html").is_file():
        FORM_DIR = _bundle / "form"
    if (_bundle / "shared" / "official-links-bar.js").is_file():
        SHARED_DIR = _bundle / "shared"

sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(REAL_SA / "scripts"))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, X-Forge-Token")


class ForgeTerminalConnectHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    address_family = socket.AF_INET


def _bind_address(port: int) -> tuple[str, int]:
    bind = os.environ.get("FORGE_TERMINAL_BIND", "local").strip().lower()
    if bind in ("all", "::", "0.0.0.0"):
        ForgeTerminalConnectHTTPServer.address_family = socket.AF_INET6

        def _v6_bind(p: int) -> tuple[str, int]:
            return ("::", p)

        return _v6_bind(port)
    return ("127.0.0.1", port)


class ForgeTerminalConnectHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        query = urlparse(self.path).query
        if path in ("", "/") and "ui=" not in query:
            from urllib.parse import urlencode

            bust = urlencode({"ui": UI_VERSION, "t": int(datetime.now(timezone.utc).timestamp())})
            self.send_response(302)
            self.send_header("Location", f"/?{bust}")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if path == "/health":
            from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433

            ai_row: dict = {}
            auth_row: dict = {}
            try:
                from ai_unify_api_v1 import status_payload  # noqa: WPS433

                ai_row = status_payload()
            except Exception:
                ai_row = {}
            try:
                from forge_terminal_local_auth_v1 import health_auth_payload  # noqa: WPS433

                auth_row = health_auth_payload()
            except Exception:
                auth_row = {}
            self._json(
                200,
                {
                    "ok": True,
                    "service": "forge-terminal",
                    "port": PORT,
                    "standalone": STANDALONE,
                    "version": UI_VERSION,
                    "ui_version": UI_VERSION,
                    "execution_mode": "sequential_single_stage",
                    "features": list(UI_FEATURES),
                    "app_dir": str(APP_DIR),
                    "terminal_dir": str(_terminal_dir()),
                    "terminal_live_ui": str(FORGE_TERMINAL_LIVE) if _terminal_dir() == FORGE_TERMINAL_LIVE else "",
                    "use_live_ui": _terminal_dir() == FORGE_TERMINAL_LIVE,
                    "openrouter_ready": bool(ai_row.get("openrouter_ready")),
                    "ai_provider": ai_row.get("auto_provider") or "none",
                    "ui_contract": build_ui_contract("forge_terminal", port=PORT),
                    **auth_row,
                },
            )
            return
        if path == "/api/chat-unify":
            from chat_unify_merge import build_report  # noqa: WPS433

            self._json(200, build_report())
            return
        if path == "/api/api-station/terminal/v1":
            from api_station_v1 import handle_terminal_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            lines = int((qs.get("lines") or ["120"])[0])
            self._json(200, handle_terminal_get(lines=lines))
            return
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_get  # noqa: WPS433

            self._json(200, handle_get(app_id="forge-terminal"))
            return
        if path == "/api/ai-unify":
            from ai_unify_api_v1 import status_payload  # noqa: WPS433

            row = status_payload()
            row["ok"] = True
            self._json(200, row)
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import payload as hub_pro_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["forge_terminal"])[0]
            self._json(200, hub_pro_payload(app_id=app_id))
            return
        if path == "/api/form-official-canvas-route-v1":
            from form_official_canvas_route_v1 import hub_canvas_target  # noqa: WPS433

            row = hub_canvas_target()
            self._json(200, {"ok": True, **row})
            return
        if path == "/api/live-founder-decision-form-v1":
            from live_founder_decision_form_v1 import founder_readable_cards, payload as live_form_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if "index" in qs:
                try:
                    idx = int(qs["index"][0])
                except (TypeError, ValueError):
                    self._json(400, {"ok": False, "error": "index must be integer"})
                    return
                cards = founder_readable_cards()
                if idx < 0 or idx >= len(cards):
                    self._json(404, {"ok": False, "error": "index out of range", "total": len(cards)})
                    return
                self._json(
                    200,
                    {
                        "ok": True,
                        "index": idx,
                        "total": len(cards),
                        "card": cards[idx],
                    },
                )
                return
            self._json(200, live_form_payload())
            return
        if path == "/api/platform-catalog/v1":
            from chat_unify_platform_catalog_v1 import catalog_payload  # noqa: WPS433

            self._json(200, catalog_payload(port=PORT))
            return
        if path == "/api/chat-unify-update/v1":
            from chat_unify_update_check_v1 import update_check_payload  # noqa: WPS433

            self._json(200, update_check_payload(current_version=UI_VERSION))
            return
        if path == "/api/integrations/v1":
            from chat_unify_integrations_v1 import integrations_live_payload  # noqa: WPS433

            self._json(200, integrations_live_payload(port=PORT))
            return
        if path in ("/terminal", "/terminal/", "/forge-terminal", "/forge-terminal/"):
            self.send_response(302)
            self.send_header("Location", "/terminal/index.html")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if path == "/api/forge-terminal/v1":
            from forge_terminal_v1 import get_run, status_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if qs.get("status") or qs.get("action") == ["status"]:
                ws_path = (qs.get("workspace_path") or qs.get("folder") or [""])[0]
                light = (qs.get("light") or ["0"])[0] in ("1", "true", "yes")
                if light:
                    from forge_terminal_v1 import status_light  # noqa: WPS433

                    self._json(200, status_light(workspace_path=ws_path or None))
                else:
                    self._json(200, status_payload(workspace_path=ws_path or None))
                return
            if (qs.get("auth") or ["0"])[0] in ("1", "true", "yes"):
                from forge_terminal_local_auth_v1 import health_auth_payload  # noqa: WPS433

                self._json(200, {"ok": True, **health_auth_payload()})
                return
            rid = (qs.get("run_id") or [""])[0]
            row = get_run(run_id=rid) if rid else get_run()
            self._json(200 if row.get("ok", True) else 404, row)
            return
        if path == "/api/integrations/v1/manifest":
            from chat_unify_integrations_v1 import load_catalog, load_plugin_manifest  # noqa: WPS433

            self._json(
                200,
                {
                    "ok": True,
                    "manifest": load_plugin_manifest(),
                    "catalog": load_catalog(),
                },
            )
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/ai-unify":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            from ai_unify_api_v1 import handle_action  # noqa: WPS433

            result = handle_action(body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/live-founder-decision-form-v1":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            action = (body.get("action") or "").strip().lower()
            if action == "submit":
                if not body.get("founder_submit"):
                    self._json(
                        403,
                        {
                            "ok": False,
                            "error": "FOUNDER_SUBMIT_REQUIRED",
                            "law": "INCIDENT-037 — only founder Submit with founder_submit:true",
                        },
                    )
                    return
                from hub_form_submit_v1 import submit_founder_picks  # noqa: WPS433

                overrides = body.get("picks") if isinstance(body.get("picks"), dict) else None
                comments = body.get("founder_comments") or body.get("comments")
                if not isinstance(comments, dict):
                    comments = None
                partial = bool(body.get("partial_batch") or body.get("batch_submit"))
                try:
                    result = submit_founder_picks(
                        overrides=overrides,
                        comments=comments,
                        cascade_hub=False,
                        partial_batch=partial,
                        actor="founder",
                        channel="chat_unify_browser",
                        background_wire=False,
                    )
                except Exception as exc:
                    self._json(
                        500,
                        {
                            "ok": False,
                            "error": "FORM_SUBMIT_EXCEPTION",
                            "detail": str(exc)[:240],
                        },
                    )
                    return
                code = 200 if result.get("ok") else 500
                result["cascade"] = result.get("cascade") or "disk_now·wire_background"
                self._json(code, result)

                def _form_post_response_wire() -> None:
                    try:
                        from hub_form_submit_v1 import _background_form_wire  # noqa: WPS433

                        _background_form_wire(reason="chat-unify-form-submit")
                    except Exception:
                        pass

                threading.Thread(target=_form_post_response_wire, daemon=True, name="cu-form-post-wire").start()
                return
            self._json(400, {"ok": False, "error": "action required: submit"})
            return
        if path == "/api/hub-pro-skills/v1":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            from hub_pro_skills_v1 import append_entry  # noqa: WPS433

            if str(body.get("action") or "").strip().lower() != "append":
                self._json(400, {"ok": False, "error": "action_required"})
                return
            row = append_entry(
                app_id=str(body.get("app_id") or "chat_unify"),
                agent=str(body.get("agent") or "founder-ui"),
                summary=str(body.get("summary") or ""),
            )
            self._json(200 if row.get("ok") else 500, row)
            return
        if path == "/api/api-station/v1":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            from api_station_v1 import handle_post  # noqa: WPS433

            result = handle_post(app_id="forge-terminal", body=body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/forge-terminal/v1":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            try:
                from forge_terminal_local_auth_v1 import verify_request  # noqa: WPS433

                headers = {k: v for k, v in self.headers.items()}
                ok_auth, auth_err = verify_request(headers)
                if not ok_auth:
                    self._json(401, {"ok": False, "error": auth_err, "message": "Missing X-Forge-Token"})
                    return
            except Exception:
                pass
            from forge_terminal_v1 import handle_post  # noqa: WPS433

            result = handle_post(body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/integrations/v1/hook":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            from chat_unify_integrations_v1 import handle_webhook_hook  # noqa: WPS433
            from chat_unify_merge import handle_action  # noqa: WPS433

            result = handle_webhook_hook(body, run_chat_unify=handle_action)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/integrations/v1":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}
            from chat_unify_integrations_v1 import handle_integration_action  # noqa: WPS433

            result = handle_integration_action(body, port=PORT)
            self._json(200 if result.get("ok", True) else 400, result)
            return
        if path != "/api/chat-unify":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        from chat_unify_merge import handle_action  # noqa: WPS433

        result = handle_action(body)
        self._json(200 if result.get("ok", True) else 400, result)

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        if path.startswith("/shared/"):
            rel = unquote(path[len("/shared/") :])
            file_path = (SHARED_DIR / rel).resolve()
            root = SHARED_DIR.resolve()
        elif path.startswith("/form/") or path == "/form":
            rel = unquote(path[len("/form/") :]) if path.startswith("/form/") else ""
            if not rel or rel.endswith("/"):
                rel = (rel.rstrip("/") + "/index.html") if rel else "index.html"
            file_path = (FORM_DIR / rel).resolve()
            root = FORM_DIR.resolve()
        elif path.startswith("/terminal/"):
            rel = unquote(path[len("/terminal/") :]) or "index.html"
            tdir = _terminal_dir()
            file_path = (tdir / rel).resolve()
            root = tdir.resolve()
        else:
            rel = unquote(path.lstrip("/"))
            file_path = (APP_DIR / rel).resolve()
            root = APP_DIR.resolve()
        if root != file_path and root not in file_path.parents:
            self.send_error(403)
            return
        if file_path.is_dir():
            file_path = file_path / "index.html"
        if not file_path.is_file():
            self.send_error(404)
            return
        ctype, _ = mimetypes.guess_type(str(file_path))
        if not ctype:
            ctype = "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if str(file_path).endswith((".html", ".js", ".css")):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        cors_headers(self)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main() -> None:
    boot_log = Path.home() / ".sina" / "forge-terminal-boot.log"
    try:
        boot_log.parent.mkdir(parents=True, exist_ok=True)
        boot_log.write_text(
            f"{datetime.now(timezone.utc).isoformat()} starting port={PORT} app={APP_DIR} terminal={_terminal_dir()}\n",
            encoding="utf-8",
        )
    except OSError:
        pass
    try:
        from ai_unify_api_v1 import bootstrap_secrets_env  # noqa: WPS433

        bootstrap_secrets_env(force=True, log=False)
    except Exception:
        pass
    try:
        from forge_terminal_local_auth_v1 import ensure_token  # noqa: WPS433

        if STANDALONE:
            ensure_token()
    except Exception:
        pass
    try:
        import threading

        from forge_terminal_v1 import warm_status_light_cache  # noqa: WPS433

        threading.Thread(target=warm_status_light_cache, daemon=True).start()
    except Exception:
        pass
    if not APP_DIR.is_dir():
        print(f"Missing app dir: {APP_DIR}", file=sys.stderr)
        sys.exit(1)
    try:
        server = ForgeTerminalConnectHTTPServer(_bind_address(PORT), ForgeTerminalConnectHandler)
    except OSError as exc:
        try:
            boot_log.write_text(
                boot_log.read_text(encoding="utf-8") + f"bind failed ({exc}); fallback 127.0.0.1\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        ForgeTerminalConnectHTTPServer.address_family = socket.AF_INET
        server = ForgeTerminalConnectHTTPServer(("127.0.0.1", PORT), ForgeTerminalConnectHandler)
    print(f"Forge Terminal Connect → http://127.0.0.1:{PORT}/ (IDE: /terminal/)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
