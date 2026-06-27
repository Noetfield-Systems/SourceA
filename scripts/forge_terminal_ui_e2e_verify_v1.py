#!/usr/bin/env python3
"""Forge Terminal UI E2E — HTTP API checks simulating desktop UI contract."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
APP_VERSION = "4.11.8-buttons-e2e"
E2E_MODEL = "gpt-4o"


def _health(port: int) -> dict:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as r:
        return json.loads(r.read().decode())


def _port() -> tuple[int, str]:
    for p in (13029,):
        try:
            row = _health(p)
            if row.get("service") == "forge-terminal":
                return p, str(row.get("forge_local_token") or "")
        except Exception:
            continue
    raise SystemExit("Forge Terminal not running on :13029 — open Forge Terminal.app first")


def _post(port: int, body: dict, token: str = "", timeout: float = 90) -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Forge-Token"] = token
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/forge-terminal/v1",
        data=data,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _get_ui(port: int) -> str:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/terminal/index.html", timeout=5) as r:
        return r.read().decode("utf-8", errors="replace")


def main() -> int:
    port, token = _port()
    checks: list[tuple[str, bool, str]] = []
    html = _get_ui(port)
    checks.append(("terminal html", 'id="chat-thread"' in html and 'id="mesh-list"' in html, ""))
    checks.append(("terminal version", APP_VERSION in html, ""))
    checks.append(("advisor mode pills", 'id="forge-mode-pills"' in html, ""))
    checks.append(("settings panel", 'id="settings-panel"' in html and 'id="btn-forge-settings"' in html, ""))
    checks.append(("model select", 'id="model-select"' in html, ""))
    checks.append(("toolbar clear", 'id="btn-clear-chat-toolbar"' in html, ""))
    checks.append(("no gemini31 html", "gemini-3.1-flash-lite" not in html, ""))
    checks.append(("gpt4o default option", 'value="gpt-4o" selected' in html, ""))
    checks.append(("model options", html.count("<option") >= 10, str(html.count("<option"))))
    css = urllib.request.urlopen(f"http://127.0.0.1:{port}/terminal/terminal.css", timeout=5).read().decode("utf-8", errors="replace")
    checks.append(("quality chip css", "forge-chat-quality-chip" in css, ""))
    try:
        connect_html = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8", errors="replace")
        checks.append(("connect shell", "forge-quality-bridge.js" in connect_html and "forge-ide-frame" in connect_html, ""))
    except Exception as exc:
        checks.append(("connect shell", False, str(exc)[:80]))

    checks.append(("composer arena", 'id="forge-composer"' in html and "forge-composer-arena" in html, ""))
    checks.append(("big composer", 'rows="7"' in html or 'rows="5"' in html, ""))
    checks.append(("send composer btn", 'id="btn-run-composer"' in html, ""))
    checks.append(("no chat pointer lock", "forge-chat-column.is-locked" not in css or "pointer-events: none" not in css, ""))
    checks.append(("founder sections css", "forge-founder-sections" in css, ""))

    td = Path(tempfile.mkdtemp(prefix="forge-ui-e2e-"))
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from forge_workspace_open_v1 import open_folder  # noqa: WPS433

        (td / "README.md").write_text("# ui e2e\n", encoding="utf-8")
        open_folder(str(td), auto_init=True)
        ws = str(td)

        mesh = _post(port, {"action": "desktop_mesh_status"}, token=token)
        checks.append(("desktop mesh", bool(mesh.get("peers")), str(mesh.get("live_peers"))))

        status_get = urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/forge-terminal/v1?status=1&light=1", timeout=5
        )
        status_row = json.loads(status_get.read().decode())
        model_count = len(status_row.get("models") or [])
        checks.append(("status models", model_count >= 10, str(model_count)))
        checks.append(("default model gpt4o", status_row.get("default_model") == E2E_MODEL, str(status_row.get("default_model"))))
        checks.append(("model roles", len(status_row.get("model_roles") or []) >= 4, ""))

        models_json = urllib.request.urlopen(
            f"http://127.0.0.1:{port}/terminal/data/forge-terminal-models-public-v1.json", timeout=5
        )
        pub = json.loads(models_json.read().decode())
        checks.append(("public models json", len(pub.get("models") or []) >= 10, ""))

        thread = _post(port, {"action": "chat_thread", "workspace_path": ws}, token=token)
        checks.append(("chat thread api", thread.get("ok") is True, str(len(thread.get("turns") or []))))

        global_chat = _post(
            port,
            {
                "action": "chat_turn",
                "text": "E2E global living chat ping",
                "full_llm": False,
                "fast": True,
                "model": E2E_MODEL,
            },
            token=token,
        )
        checks.append(("chat_turn no workspace", global_chat.get("ok") is True, global_chat.get("error") or ""))

        settings = _post(port, {"action": "chat_settings_get"}, token=token)
        checks.append(("chat settings api", settings.get("ok") is True and bool(settings.get("settings")), ""))

        run = _post(
            port,
            {
                "action": "run",
                "text": "List project files in this workspace README",
                "full_llm": True,
                "fast": True,
                "model": E2E_MODEL,
                "workspace_path": ws,
            },
            token=token,
        )
        card = run.get("decision_card") or {}
        qg = card.get("quality_gate") or run.get("quality_gate") or {}
        layers = qg.get("layers") or []
        checks.append(("run ok", bool(run.get("ok")), run.get("error") or ""))
        disp = str(run.get("display_response") or "")
        checks.append(("display_response", bool(disp) and not disp.strip().startswith("{"), disp[:60]))
        checks.append(("quality 11 layers", len(layers) == 11, str(len(layers))))
        checks.append(
            ("execution_allowed field",
             "execution_allowed" in qg,
             str(qg.get("verdict")))
        )

        run_id = str(run.get("run_id") or "")
        if run_id and not qg.get("execution_allowed"):
            blocked = _post(port, {"action": "send_cloud", "run_id": run_id, "dry_run": True}, token=token)
            checks.append(
                ("cloud blocked when fail", blocked.get("error") == "quality_gate_blocked", blocked.get("error") or "")
            )

        if run_id and qg.get("execution_allowed"):
            _post(port, {"action": "decide", "run_id": run_id, "decision": "approved"}, token=token)
            cloud = _post(port, {"action": "send_cloud", "run_id": run_id, "dry_run": True}, token=token)
            checks.append(("cloud dry when pass", cloud.get("ok") is True, cloud.get("error") or ""))

        if run_id:
            rerun = _post(
                port,
                {
                    "action": "quality_rerun",
                    "run_id": run_id,
                    "text": "List project files in this workspace README",
                    "full_llm": False,
                },
                token=token,
            )
            checks.append(("quality_rerun", rerun.get("ok") is True, ""))

        if token:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/forge-terminal/v1?auth=1", timeout=5) as r:
                    auth_row = json.loads(r.read().decode())
                checks.append(("auth GET", bool(auth_row.get("forge_local_token")), ""))
            except Exception as exc:
                checks.append(("auth GET", False, str(exc)[:80]))
            try:
                _post(port, {"action": "status_light"}, token="bad-token")
                checks.append(("auth negative", False, "expected 401"))
            except urllib.error.HTTPError as e:
                checks.append(("auth negative", e.code == 401, str(e.code)))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    passed = sum(1 for _, ok, _ in checks if ok)
    print(f"Forge UI E2E on :{port}\n")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" ({detail})" if detail else ""))
    print(f"\n{passed}/{len(checks)} passed")
    receipt = {
        "schema": "forge-terminal-ui-e2e-v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "port": port,
        "passed": passed,
        "total": len(checks),
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "forge-terminal-ui-e2e-v1.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
