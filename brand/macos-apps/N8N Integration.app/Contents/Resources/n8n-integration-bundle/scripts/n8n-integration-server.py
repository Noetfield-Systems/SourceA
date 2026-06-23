#!/usr/bin/env python3
"""N8N Integration — standalone server (UI + API). Default :13026. No Sina Command hub."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

DEBUG_LOG = Path(__file__).resolve().parents[1] / ".cursor" / "debug-e9f1f5.log"


def _dbg(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # #region agent log
    try:
        row = {
            "sessionId": "e9f1f5",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        }
        DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass
    # #endregion


def _bundle_root_env() -> str:
    raw = os.environ.get("N8N_INTEGRATION_BUNDLE_ROOT", "").strip()
    if not raw:
        return ""
    root = Path(raw)
    if (root / "scripts" / "n8n-integration-server.py").is_file() and (root / "app" / "index.html").is_file():
        return raw
    return ""


BUNDLE_ROOT = _bundle_root_env()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "scripts" / "n8n-standalone"
    SCRIPTS_DIR = SOURCE_A / "scripts"

PORT = int(os.environ.get("N8N_INTEGRATION_PORT", "13026"))


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
        if (candidate / "brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("N8N_INTEGRATION_STANDALONE", "1")
os.environ.setdefault("N8N_INTEGRATION_PORT", str(PORT))
# Prefer live SourceA UI when repo is on disk (avoids stale bundled v1.1 HTML).
LIVE_APP = REAL_SA / "scripts" / "n8n-standalone"
if LIVE_APP.is_dir() and (LIVE_APP / "index.html").is_file():
    APP_DIR = LIVE_APP
_path = os.environ.get("PATH", "")
if "/opt/homebrew/bin" not in _path:
    os.environ["PATH"] = (
        "/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:" + _path
    )

sys.path.insert(0, str(SCRIPTS_DIR))
if str(REAL_SA / "scripts") not in sys.path:
    sys.path.insert(0, str(REAL_SA / "scripts"))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class N8nIntegrationHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class N8nIntegrationHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433
            from n8n_integration_core import VERSION  # noqa: WPS433

            self._json(
                200,
                {
                    "ok": True,
                    "service": "n8n-integration",
                    "port": PORT,
                    "standalone": True,
                    "version": VERSION,
                    "ui_contract": build_ui_contract("n8n_integration", port=PORT),
                },
            )
            return
        if path == "/api/n8n-integration":
            try:
                from n8n_integration_core import build_report, build_report_fast  # noqa: WPS433

                qs = parse_qs(urlparse(self.path).query)
                if qs.get("full"):
                    payload = build_report()
                else:
                    payload = build_report_fast()
                self._json(200, payload)
            except Exception as exc:
                self._json(500, {"ok": False, "error": str(exc)[:200]})
            return
        if path == "/api/validator-terminal/v1":
            from validator_machine_v1 import terminal_tail, run_terminal_session, start_terminal_session_async  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if qs.get("run"):
                tier = (qs.get("tier") or ["probe"])[0]
                app_id = (qs.get("app") or ["n8n_integration"])[0]
                if qs.get("async"):
                    self._json(200, start_terminal_session_async(app_id=app_id, tier=tier, include_chain=True))
                    return
                self._json(200, run_terminal_session(app_id=app_id, tier=tier, include_chain=True))
                return
            lines = int((qs.get("lines") or ["80"])[0])
            self._json(200, terminal_tail(lines=lines))
            return
        if path == "/api/validator-machine/v1":
            from validator_machine_v1 import hub_slice, run_all  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if qs.get("run"):
                tier = (qs.get("tier") or ["probe"])[0]
                self._json(200, run_all(tier=tier))
                return
            app_id = (qs.get("app") or [None])[0]
            self._json(200, hub_slice(app_id=app_id))
            return
        if path == "/api/api-station/terminal/v1":
            from api_station_v1 import handle_terminal_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            lines = int((qs.get("lines") or ["120"])[0])
            self._json(200, handle_terminal_get(lines=lines))
            return
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["n8n-integration"])[0]
            self._json(200, handle_get(app_id=app_id))
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import payload as hub_pro_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["n8n_integration"])[0]
            if app_id == "n8n-integration":
                app_id = "n8n_integration"
            self._json(200, hub_pro_payload(app_id=app_id))
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_post  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["n8n-integration"])[0]
            result = handle_post(app_id=app_id, body=body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import append_entry  # noqa: WPS433

            action = str(body.get("action") or "").strip().lower()
            if action == "append":
                app_id = str(body.get("app_id") or "n8n_integration")
                if app_id == "n8n-integration":
                    app_id = "n8n_integration"
                result = append_entry(
                    app_id=app_id,
                    agent=str(body.get("agent") or "founder-ui"),
                    summary=str(body.get("summary") or ""),
                    obstacles=body.get("obstacles"),
                    fixes=body.get("fixes"),
                    golden_tips=body.get("golden_tips"),
                    paths=body.get("paths"),
                )
                self._json(200 if result.get("ok") else 400, result)
                return
            from hub_pro_skills_v1 import payload as hub_pro_payload  # noqa: WPS433

            app_id = str(body.get("app_id") or "n8n_integration")
            if app_id == "n8n-integration":
                app_id = "n8n_integration"
            self._json(200, hub_pro_payload(app_id=app_id))
            return
        if path != "/api/n8n-integration":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        from n8n_integration_core import handle_action  # noqa: WPS433

        try:
            result = handle_action(body)
        except Exception as exc:
            result = {
                "ok": False,
                "error": "execution_failed",
                "message": str(exc)[:500],
                "action": body.get("action"),
            }
        err = (result.get("error") or "").strip().lower()
        if err.startswith("unknown") or err == "not_found":
            self._json(400, result)
        else:
            self._json(200, result)

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
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
        if str(file_path).endswith(".html"):
            self.send_header("Cache-Control", "no-cache")
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
    boot_log = Path.home() / ".sina" / "n8n-integration-boot.log"
    try:
        boot_log.parent.mkdir(parents=True, exist_ok=True)
        boot_log.write_text(
            f"{datetime.now(timezone.utc).isoformat()} starting port={PORT} app_dir={APP_DIR}\n",
            encoding="utf-8",
        )
    except OSError:
        pass
    if not APP_DIR.is_dir():
        print(f"Missing app dir: {APP_DIR}", file=sys.stderr)
        sys.exit(1)
    try:
        server = N8nIntegrationHTTPServer(("127.0.0.1", PORT), N8nIntegrationHandler)
        try:
            boot_log.write_text(
                boot_log.read_text(encoding="utf-8") + f"bound ok fd={getattr(server.socket, 'fileno', lambda: '?')()}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
    except OSError as exc:
        try:
            boot_log.write_text(
                boot_log.read_text(encoding="utf-8") + f"bind failed: {exc}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        print(f"Bind failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"N8N Integration standalone → http://127.0.0.1:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
