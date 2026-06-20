#!/usr/bin/env python3
"""Mac Health Guard — standalone server (UI + API). Default :13024. No Sina Command hub."""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

BUNDLE_ROOT = os.environ.get("MAC_HEALTH_BUNDLE_ROOT", "").strip()
if BUNDLE_ROOT:
    SOURCE_A = Path(BUNDLE_ROOT)
    APP_DIR = SOURCE_A / "app"
    SCRIPTS_DIR = SOURCE_A / "scripts"
else:
    SOURCE_A = Path(__file__).resolve().parents[1]
    APP_DIR = SOURCE_A / "scripts" / "mac-health-standalone"
    SCRIPTS_DIR = SOURCE_A / "scripts"
PORT = int(os.environ.get("MAC_HEALTH_PORT", "13024"))

sys.path.insert(0, str(SCRIPTS_DIR))
os.environ.setdefault("MAC_HEALTH_STANDALONE", "1")

from mac_health_version_v1 import MAC_HEALTH_VERSION  # noqa: E402
from mac_health_debug_bab1ff_v1 import dbg  # noqa: E402


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class MacHealthHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        import time as _time

        path = urlparse(self.path).path
        t0 = _time.monotonic()
        # #region agent log
        dbg(
            hypothesis_id="D",
            location="mac-health-guard-server.py:do_GET",
            message="request_start",
            data={"path": path, "app_dir": str(APP_DIR)},
        )
        # #endregion
        if path == "/health":
            from mac_health_founder_glance_ui_v1 import build_ui_contract  # noqa: WPS433
            from mac_health_cloud_glance_v1 import probe as cloud_glance_probe  # noqa: WPS433

            ui_contract = build_ui_contract(port=PORT)
            try:
                cg = cloud_glance_probe(write_receipt=False)
                ui_contract["cloud_glance"] = {
                    "founder_line": cg.get("founder_line"),
                    "railway_ok": cg.get("railway_ok"),
                    "last_plan_id": cg.get("last_plan_id"),
                }
            except Exception:
                pass
            self._json(
                200,
                {
                    "ok": True,
                    "service": "mac-health-guard",
                    "port": PORT,
                    "standalone": True,
                    "version": MAC_HEALTH_VERSION,
                    "ui_contract": ui_contract,
                },
            )
            return
        if path == "/api/mac-health/cloud-glance/v1":
            from mac_health_cloud_glance_v1 import probe as cloud_glance_probe  # noqa: WPS433

            row = cloud_glance_probe(write_receipt=True)
            self._json(200 if row.get("ok") or row.get("last_plan_id") else 207, row)
            return
        if path == "/api/mac-health/live":
            from mac_health_live_v1 import get_live_api_row  # noqa: WPS433

            live_t0 = _time.monotonic()
            row = get_live_api_row(sync_h1=False)
            # #region agent log
            dbg(
                hypothesis_id="B",
                location="mac-health-guard-server.py:live",
                message="live_api_done",
                data={
                    "ms": round((_time.monotonic() - live_t0) * 1000, 1),
                    "live_status": row.get("live_status"),
                    "ok": row.get("ok"),
                },
            )
            # #endregion
            self._json(200, row)
            return
        if path == "/api/mac-health/panic":
            from mac_health_emergency_stop_v1 import run_mac_health_emergency_stop  # noqa: WPS433

            row = run_mac_health_emergency_stop(trigger="api-get", fast=True, notify=True)
            self._json(200, {"ok": True, "emergency_stop": row, "summary": row.get("summary")})
            return
        if path == "/api/mac-health":
            from mac_health_guard import build_report  # noqa: WPS433

            self._json(200, build_report(rescan=False, standalone=True))
            return
        self._serve_static(path)
        # #region agent log
        dbg(
            hypothesis_id="D",
            location="mac-health-guard-server.py:do_GET",
            message="request_end",
            data={"path": path, "ms": round((_time.monotonic() - t0) * 1000, 1)},
        )
        # #endregion

    def do_POST(self):
        import time as _time

        path = urlparse(self.path).path
        post_t0 = _time.monotonic()
        # #region agent log
        dbg(
            hypothesis_id="C",
            location="mac-health-guard-server.py:do_POST",
            message="post_start",
            data={"path": path},
        )
        # #endregion
        if path == "/api/mac-health/panic":
            from mac_health_emergency_stop_v1 import run_mac_health_emergency_stop  # noqa: WPS433

            row = run_mac_health_emergency_stop(trigger="ui", fast=False, notify=True)
            self._json(200, {"ok": True, "emergency_stop": row, "summary": row.get("summary")})
            return
        if path == "/api/mac-health/panic/full":
            from mac_health_emergency_stop_v1 import run_mac_health_emergency_stop  # noqa: WPS433

            row = run_mac_health_emergency_stop(trigger="full_stop", fast=False, notify=True)
            self._json(200, {"ok": True, "emergency_stop": row, "summary": row.get("summary")})
            return
        if path == "/debug/agent-log":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                payload = {}
            dbg(
                hypothesis_id=str(payload.get("hypothesisId") or "?"),
                location=str(payload.get("location") or "client"),
                message=str(payload.get("message") or "client_log"),
                data=payload.get("data") if isinstance(payload.get("data"), dict) else {},
            )
            self._json(204, {"ok": True})
            return
        if path != "/api/mac-health":
            self._json(404, {"ok": False, "error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
        body["standalone"] = True
        from mac_health_guard import handle_action  # noqa: WPS433

        result = handle_action(body)
        ok = bool(result.get("ok")) or bool(result.get("cpu_relief")) or bool(result.get("ram_purge"))
        # #region agent log
        dbg(
            hypothesis_id="C",
            location="mac-health-guard-server.py:do_POST",
            message="post_done",
            data={
                "action": body.get("action"),
                "ms": round((_time.monotonic() - post_t0) * 1000, 1),
                "ok": ok,
                "error": result.get("error"),
            },
        )
        # #endregion
        self._json(200 if ok else 400, result)

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
        snippet = data[:4096].decode("utf-8", errors="replace")
        # #region agent log
        dbg(
            hypothesis_id="A",
            location="mac-health-guard-server.py:_serve_static",
            message="static_served",
            data={
                "file": str(file_path),
                "bytes": len(data),
                "has_seg_nav": "mhg-seg-nav" in snippet,
                "has_founder_glance": "mhg-founder-glance" in snippet,
                "css_ver": "3.2.2" if "3.2.2" in snippet else ("3.3.0" if "3.3.0" in snippet else "?"),
            },
        )
        # #endregion
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if str(file_path).endswith((".html", ".js", ".css")):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
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
    import threading
    import time

    if not APP_DIR.is_dir():
        print(f"Missing app dir: {APP_DIR}", file=sys.stderr)
        sys.exit(1)

    # #region agent log
    dbg(
        hypothesis_id="E",
        location="mac-health-guard-server.py:main",
        message="server_start",
        data={"port": PORT, "app_dir": str(APP_DIR), "version": MAC_HEALTH_VERSION},
    )
    # #endregion

    def _pulse_loop() -> None:
        log_path = Path.home() / ".sina" / "mac-health-guard-server.log"
        while True:
            interval = 8
            try:
                from mac_health_ram_pressure_v1 import pulse_interval_sec  # noqa: WPS433

                interval = pulse_interval_sec()
            except Exception:
                pass
            try:
                from mac_health_live_v1 import build_live_snapshot  # noqa: WPS433

                row = build_live_snapshot(sync_h1=False, side_effects=not __import__(
                    "mac_health_ram_pressure_v1", fromlist=["is_cursor_ultra_light"]
                ).is_cursor_ultra_light())
                try:
                    from mac_health_live_v1 import write_h1_bridge  # noqa: WPS433

                    write_h1_bridge(row)
                except Exception:
                    pass
            except Exception as exc:
                try:
                    import traceback

                    with log_path.open("a", encoding="utf-8") as fh:
                        fh.write(f"pulse error: {exc}\n{traceback.format_exc()}\n")
                except OSError:
                    pass
            time.sleep(interval)

    threading.Thread(target=_pulse_loop, daemon=True, name="mac-health-pulse").start()

    class ReuseHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True

    try:
        server = ReuseHTTPServer(("127.0.0.1", PORT), MacHealthHandler)
    except OSError as exc:
        # #region agent log
        dbg(
            hypothesis_id="E",
            location="mac-health-guard-server.py:main",
            message="bind_failed",
            data={"port": PORT, "errno": getattr(exc, "errno", None), "error": str(exc)},
        )
        # #endregion
        raise
    # #region agent log
    dbg(
        hypothesis_id="E",
        location="mac-health-guard-server.py:main",
        message="bind_ok",
        data={"port": PORT},
    )
    # #endregion
    print(f"Mac Health Guard standalone → http://127.0.0.1:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
