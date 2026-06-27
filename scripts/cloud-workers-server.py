#!/usr/bin/env python3
"""Cloud Workers Command Center — standalone server (UI + API). Default :13027.

Law: Cloud Workers is the founder cockpit for Railway + CF cron — NOT Worker Hub :13020.
Proceed / probe / dispatch go direct to FBE cloud worker URL. Hub is optional glance only.
"""
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

# Legacy hub port — optional only; never required for Proceed.
HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))
PROCEED_LOG = Path.home() / ".sina" / "cloud-workers-proceed-log-v1.jsonl"


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
UI_VERSION = "1.3.0"


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
# Live UI + SSOT from repo — .app bundle is fallback when Desktop/SourceA is missing.
if (REAL_SA / "agent-control-panel" / "shared" / "cloud-workers-panel.js").is_file():
    SHARED_DIR = REAL_SA / "agent-control-panel" / "shared"
if (REAL_SA / "scripts" / "cloud-workers-standalone" / "index.html").is_file():
    APP_DIR = REAL_SA / "scripts" / "cloud-workers-standalone"
DEBUG_LOG = REAL_SA / ".cursor" / "debug-23242e.log"
os.environ.setdefault("SINA_SOURCE_A", str(REAL_SA))
os.environ.setdefault("CLOUD_WORKERS_STANDALONE", "1")
os.environ.setdefault("CLOUD_WORKERS_PORT", str(PORT))
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(REAL_SA / "scripts"))


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


def _hub_up() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{HUB_PORT}/health", timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def _railway_up() -> bool:
    deploy_path = Path.home() / ".sina" / "fbe-cloud-deploy-receipt-v1.json"
    try:
        deploy = json.loads(deploy_path.read_text(encoding="utf-8"))
        health = deploy.get("health") if isinstance(deploy.get("health"), dict) else {}
        return bool(deploy.get("ok")) and bool(health.get("ok"))
    except (OSError, json.JSONDecodeError):
        return False


def _dbg(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "23242e",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        }
        DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass
    # #endregion


def _append_proceed_log(row: dict) -> None:
    try:
        PROCEED_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ok": row.get("ok"),
            "plan_id": row.get("plan_id"),
            "error": row.get("error"),
            "decision": row.get("decision"),
            "pack_advanced": (row.get("pack") or {}).get("advanced"),
            "show_this": (row.get("for_founder") or {}).get("show_this"),
            "cloud_url": row.get("cloud_worker_url"),
        }
        with PROCEED_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _proceed_direct_cloud(body: dict | None) -> dict:
    """Full-pack proceed — Railway only, no Worker Hub."""
    _dbg("H1", "cloud-workers-server:_proceed_direct_cloud", "proceed start", {"full_pack": (body or {}).get("full_pack")})
    try:
        from hub_cloud_forge_run_proceed_v1 import proceed_from_hub  # noqa: WPS433
        from fbe.lib.hub_cloud_proxy_v1 import cloud_worker_url  # noqa: WPS433

        payload = dict(body or {})
        payload.setdefault("full_pack", True)
        payload.setdefault("max_advance", 100)
        payload.setdefault("full_motor", True)
        payload.setdefault("trigger_source", "hub_proceed_pack")
        payload.setdefault("force_reset_gate", True)
        row = proceed_from_hub(payload)
        if row.get("decision") in ("drain_complete", "batch_complete"):
            row["ok"] = True
        if row.get("error") == "mac_observe_only":
            ssot = _read_json(REAL_SA / "data/cloud-auto-runtime-v1.json")
            cf = (ssot.get("cloudflare_worker") or {}).get("url") or ""
            cf = str(cf).rstrip("/")
            row = {
                **row,
                "ok": True,
                "decision": "use_cf_cron",
                "redirect": "browser_cf_tick",
                "cf_tick_url": f"{cf}/tick" if cf else None,
                "for_founder": {
                    "show_this": (
                        "Mac observe only — use Trigger CF full-pack button (browser→CF→Railway). "
                        "CF cron */10 runs automatically."
                    ),
                },
            }
        cloud = row.get("cloud") if isinstance(row.get("cloud"), dict) else {}
        if cloud.get("pack"):
            row["pack"] = cloud.get("pack")
        row["execution_plane"] = "cloud_workers_standalone"
        row["cloud_worker_url"] = cloud_worker_url() or None
        row["hub_required"] = False
        _append_proceed_log(row)
        try:
            from cloud_workers_hub_v1 import append_event  # noqa: WPS433

            append_event(
                "proceed",
                {
                    "ok": bool(row.get("ok")),
                    "plan_id": row.get("plan_id"),
                    "line": row.get("hub_proceed_line") or (row.get("for_founder") or {}).get("show_this"),
                    "pack_advanced": (row.get("pack") or {}).get("advanced"),
                    "source": "cloud_workers_standalone",
                },
            )
        except Exception:
            pass
        _dbg("H1", "cloud-workers-server:_proceed_direct_cloud", "proceed done", {"ok": row.get("ok"), "plan_id": row.get("plan_id")})
        return row
    except Exception as exc:
        _dbg("H1", "cloud-workers-server:_proceed_direct_cloud", "proceed exception", {"error": str(exc)[:300]})
        return {
            "ok": False,
            "error": "proceed_failed",
            "message": str(exc)[:500],
            "for_founder": {"show_this": f"Proceed failed: {str(exc)[:200]}"},
        }


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
            from fbe.lib.hub_cloud_proxy_v1 import cloud_worker_url  # noqa: WPS433

            self._json(
                200,
                {
                    "ok": True,
                    "service": "cloud-workers",
                    "port": PORT,
                    "standalone": True,
                    "version": UI_VERSION,
                    "ui_version": UI_VERSION,
                    "shared_dir": str(SHARED_DIR),
                    "app_dir": str(APP_DIR),
                    "railway_live": _railway_up(),
                    "railway_url": cloud_worker_url() or None,
                    "legacy_hub_port": HUB_PORT,
                    "legacy_hub_live": _hub_up(),
                    "hub_required_for_proceed": False,
                    "ui_contract": build_ui_contract("cloud_workers", port=PORT),
                },
            )
            return
        if path == "/api/cloud-workers/v1":
            from cloud_workers_hub_v1 import payload  # noqa: WPS433

            row = payload()
            row["hub_live"] = _railway_up()
            row["railway_live"] = row["hub_live"]
            row["legacy_hub_live"] = _hub_up()
            row["standalone_mode"] = True
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
            if action == "proceed":
                result = _proceed_direct_cloud(body)
                code = 200 if result.get("ok") else 422
                self._json(code, result)
                return
            from cloud_workers_hub_v1 import handle_action  # noqa: WPS433

            try:
                result = handle_action(body)
            except Exception as exc:
                result = {"ok": False, "error": "execution_failed", "message": str(exc)[:500]}
            self._json(200 if result.get("ok", True) else 400, result)
            return
        if path == "/api/cloud-forge-run/proceed/v1":
            result = _proceed_direct_cloud(body)
            code = 200 if result.get("ok") else 422
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
