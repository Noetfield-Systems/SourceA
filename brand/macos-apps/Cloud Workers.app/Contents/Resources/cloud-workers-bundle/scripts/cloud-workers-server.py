#!/usr/bin/env python3
"""Cloud Workers Command Center — standalone server (UI + API). Default :13027."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))


def _bundle_root_env() -> str:
    raw = os.environ.get("CLOUD_WORKERS_BUNDLE_ROOT", "").strip()
    if not raw:
        return ""
    root = Path(raw)
    if (root / "scripts" / "cloud-workers-server.py").is_file() and (root / "app" / "index.html").is_file():
        return raw
    return ""


BUNDLE_ROOT = _bundle_root_env()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app"
    SHARED_DIR = SOURCE_A / "shared"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "scripts" / "cloud-workers-standalone"
    SHARED_DIR = SOURCE_A / "agent-control-panel" / "shared"
    SCRIPTS_DIR = SOURCE_A / "scripts"

PORT = int(os.environ.get("CLOUD_WORKERS_PORT", "13027"))
UI_VERSION = "1.1.0"

MUTATING_ACTIONS = frozenset(
    {
        "skip_head",
        "skip_to_next_real",
        "auto_tick",
        "dispatch",
        "proceed",
    }
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
        if (candidate / "data/cloud-workers-control-plane-v1.json").is_file():
            return candidate
    return Path(__file__).resolve().parents[1]


REAL_SA = _resolve_source_a()
os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("CLOUD_WORKERS_STANDALONE", "1")
os.environ.setdefault("CLOUD_WORKERS_PORT", str(PORT))
# Prefer live workspace scripts over bundled copies so UI/API always
# reflect current disk + cloud truth after upgrades.
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(REAL_SA / "scripts"))


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


def _hub_up() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{HUB_PORT}/health", timeout=2.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _proxy_hub_json(path: str, *, method: str = "GET", body: dict | None = None, timeout: float = 180.0) -> dict:
    url = f"http://127.0.0.1:{HUB_PORT}{path}"
    data = json.dumps(body or {}).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw.strip() else {}
            return {"ok": True, "status": resp.status, **parsed} if isinstance(parsed, dict) else {"ok": True, "body": parsed}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw[:500]}
        if isinstance(parsed, dict):
            parsed.setdefault("ok", False)
            parsed["status"] = exc.code
            return parsed
        return {"ok": False, "status": exc.code, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "hub_required": True, "hint": f"Start Worker Hub on :{HUB_PORT}"}


class CloudWorkersHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class CloudWorkersHandler(BaseHTTPRequestHandler):
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

            self._json(
                200,
                {
                    "ok": True,
                    "service": "cloud-workers",
                    "port": PORT,
                    "standalone": True,
                    "version": UI_VERSION,
                    "hub_port": HUB_PORT,
                    "hub_live": _hub_up(),
                    "ui_contract": build_ui_contract("cloud_workers", port=PORT),
                },
            )
            return
        if path == "/api/cloud-workers/v1":
            hub_live = _hub_up()
            if hub_live:
                row = _proxy_hub_json("/api/cloud-workers/v1", method="GET", timeout=180.0)
                code = int(row.pop("status", 200) or 200)
                row["hub_live"] = True
                self._json(code, row)
                return
            from cloud_workers_hub_v1 import payload  # noqa: WPS433

            row = payload()
            row["hub_live"] = False
            row["fallback_mode"] = "local_payload"
            self._json(200, row)
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import payload as hub_pro_payload  # noqa: WPS433

            qs = urlparse(self.path).query
            app_id = "cloud_workers"
            if "app=" in qs:
                app_id = qs.split("app=")[1].split("&")[0]
            self._json(200, hub_pro_payload(app_id=app_id))
            return
        if path == "/api/api-station/terminal/v1":
            from api_station_v1 import handle_terminal_get  # noqa: WPS433

            qs = urlparse(self.path).query
            lines = 120
            if "lines=" in qs:
                try:
                    lines = int(qs.split("lines=")[1].split("&")[0])
                except ValueError:
                    lines = 120
            self._json(200, handle_terminal_get(lines=lines))
            return
        if path.startswith("/api/api-station/v1"):
            from api_station_v1 import handle_get  # noqa: WPS433

            qs = urlparse(self.path).query
            app_id = "cloud-workers"
            if "app=" in qs:
                app_id = qs.split("app=")[1].split("&")[0]
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
        if path == "/api/cloud-workers/v1":
            action = str(body.get("action") or "").strip().lower()
            standalone = os.environ.get("CLOUD_WORKERS_STANDALONE") == "1"
            if standalone and action in MUTATING_ACTIONS and _hub_up():
                result = _proxy_hub_json("/api/cloud-workers/v1", method="POST", body=body, timeout=180.0)
                code = int(result.pop("status", 200) or 200)
                if result.get("ok", True) or result.get("error") != "execution_failed":
                    self._json(code, result)
                    return
            from cloud_workers_hub_v1 import handle_action  # noqa: WPS433

            try:
                result = handle_action(body)
            except Exception as exc:
                result = {"ok": False, "error": "execution_failed", "message": str(exc)[:500]}
                if standalone and _hub_up() and action in MUTATING_ACTIONS:
                    result = _proxy_hub_json("/api/cloud-workers/v1", method="POST", body=body, timeout=180.0)
                    code = int(result.pop("status", 200) or 200)
                    self._json(code, result)
                    return
            self._json(200 if result.get("ok", True) else 400, result)
            return
        if path == "/api/cloud-drain/proceed/v1":
            if not _hub_up():
                self._json(
                    503,
                    {
                        "ok": False,
                        "error": "hub_down",
                        "for_founder": {
                            "show_this": f"Worker Hub :{HUB_PORT} must be running for Proceed — open Worker Hub.app first.",
                        },
                    },
                )
                return
            result = _proxy_hub_json(path, method="POST", body=body, timeout=180.0)
            code = int(result.pop("status", 200) or 200)
            self._json(code, result)
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import append_entry  # noqa: WPS433

            if body.get("action") == "append":
                row = append_entry(
                    app_id=str(body.get("app_id") or "cloud_workers"),
                    agent=str(body.get("agent") or "founder-ui"),
                    summary=str(body.get("summary") or ""),
                )
                self._json(200 if row.get("ok") else 400, row)
                return
            self._json(400, {"ok": False, "error": "unknown action"})
            return
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_post  # noqa: WPS433

            app_id = str(body.get("app") or "cloud-workers")
            result = handle_post(app_id=app_id, body=body)
            self._json(200 if result.get("ok") else 400, result)
            return
        self._json(404, {"ok": False, "error": "not_found"})

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        if path.startswith("/shared/"):
            rel = unquote(path[len("/shared/") :])
            file_path = (SHARED_DIR / rel).resolve()
            root = SHARED_DIR.resolve()
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


def main() -> int:
    boot_log = Path.home() / ".sina" / "cloud-workers-boot.log"
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
        return 1
    try:
        server = CloudWorkersHTTPServer(("127.0.0.1", PORT), CloudWorkersHandler)
    except OSError as exc:
        print(f"Bind failed: {exc}", file=sys.stderr)
        return 1
    print(f"Cloud Workers Command Center → http://127.0.0.1:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
