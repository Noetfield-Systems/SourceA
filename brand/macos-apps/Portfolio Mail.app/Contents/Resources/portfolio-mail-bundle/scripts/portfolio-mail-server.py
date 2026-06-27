#!/usr/bin/env python3
"""Portfolio Mail — standalone server. Default :13028. No Worker Hub required."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

PORT = int(os.environ.get("PORTFOLIO_MAIL_PORT", "13028"))


def _resolve_source_a() -> Path:
    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for candidate in (Path.home() / "Desktop" / "SourceA", Path(__file__).resolve().parents[1]):
        if (candidate / "data" / "portfolio-vault-email-tags-v1.json").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
SCRIPTS_DIR = REAL_SA / "scripts"
MAIL_DIR = REAL_SA / "agent-control-panel" / "mail-hub"
SHARED_DIR = REAL_SA / "agent-control-panel" / "shared"

sys.path.insert(0, str(SCRIPTS_DIR))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class PortfolioMailHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class PortfolioMailHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._json(
                200,
                {
                    "ok": True,
                    "service": "portfolio-mail",
                    "port": PORT,
                    "standalone": True,
                    "worker_hub_required": False,
                    "mail_hub": f"http://127.0.0.1:{PORT}/mail-hub/",
                },
            )
            return
        if path == "/api/portfolio-mail/v1/integration":
            from portfolio_mail_hub_v1 import integration_status  # noqa: WPS433

            self._json(200, integration_status())
            return
        if path == "/api/portfolio-mail/v1":
            from portfolio_mail_hub_v1 import handle_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            self._json(200, handle_get(qs))
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["portfolio_mail"])[0]
            self._json(200, payload(app_id=app_id))
            return
        if path.startswith("/api/api-station/v1"):
            from api_station_v1 import handle_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["portfolio-mail"])[0]
            self._json(200, handle_get(app_id=app_id))
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
        if path == "/api/portfolio-mail/v1/integration":
            from portfolio_mail_hub_v1 import integration_wire  # noqa: WPS433

            row = integration_wire(import_cursor=bool(body.get("import_cursor")))
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/portfolio-mail/v1/send":
            import asyncio

            from portfolio_mail_hub_v1 import handle_post  # noqa: WPS433

            row = asyncio.run(handle_post(body))
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import append_entry  # noqa: WPS433

            if str(body.get("action") or "").strip().lower() != "append":
                self._json(400, {"ok": False, "error": "action_required"})
                return
            row = append_entry(
                app_id=str(body.get("app_id") or "portfolio_mail"),
                agent=str(body.get("agent") or "founder-ui"),
                summary=str(body.get("summary") or ""),
            )
            self._json(200 if row.get("ok") else 500, row)
            return
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_post  # noqa: WPS433

            row = handle_post(app_id=str(body.get("app") or "portfolio-mail"), body=body)
            self._json(200 if row.get("ok") else 207, row)
            return
        self._json(404, {"ok": False, "error": "not_found"})

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/mail-hub/"
        if path.startswith("/shared/"):
            rel = unquote(path[len("/shared/") :])
            file_path = (SHARED_DIR / rel).resolve()
            root = SHARED_DIR.resolve()
        elif path.startswith("/mail-hub/") or path == "/mail-hub":
            rel = unquote(path[len("/mail-hub/") :]) if path.startswith("/mail-hub/") else ""
            if not rel or rel.endswith("/"):
                rel = (rel.rstrip("/") + "/index.html") if rel else "index.html"
            file_path = (MAIL_DIR / rel).resolve()
            root = MAIL_DIR.resolve()
        else:
            self.send_error(404)
            return
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
            self.send_header("Cache-Control", "no-store")
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


def main() -> int:
    boot_log = Path.home() / ".sina" / "portfolio-mail-boot.log"
    try:
        boot_log.write_text(
            f"{datetime.now(timezone.utc).isoformat()} starting port={PORT}\n",
            encoding="utf-8",
        )
    except OSError:
        pass
    server = PortfolioMailHTTPServer(("127.0.0.1", PORT), PortfolioMailHandler)
    print(f"portfolio-mail http://127.0.0.1:{PORT}/mail-hub/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
