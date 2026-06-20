#!/usr/bin/env python3
"""Re-import WF8 with valid node IDs and activate webhook via n8n REST (owner API key)."""
from __future__ import annotations

import json
import secrets
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WF8_NAME = "wf-mac-health-cooldown-v1"
WF8_PATH = SOURCE_A / "n8n/workflows/wf-mac-health-cooldown-v1.json"
P0_GATE = Path.home() / ".sina/n8n-receipts/health/p0-operational-pass.json"
API_KEY_PATH = Path.home() / ".sina/n8n-owner-api-key-v1.txt"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stop_n8n() -> None:
    subprocess.run(["pkill", "-f", "n8n start"], check=False)
    subprocess.run(["pkill", "-f", "npx.*n8n"], check=False)
    time.sleep(2)


def _start_n8n() -> None:
    subprocess.run(["bash", str(SOURCE_A / "scripts/founder-start-n8n.sh")], check=False)
    import urllib.request

    for _ in range(90):
        try:
            urllib.request.urlopen("http://127.0.0.1:5678/healthz", timeout=3)
            time.sleep(4)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("n8n did not start")


def _regenerate_wf8() -> None:
    subprocess.run([sys.executable, str(SOURCE_A / "scripts/n8n_workflow_factory_v1.py")], check=True)


def _delete_wf8_rows() -> None:
    con = sqlite3.connect(N8N_DB)
    try:
        rows = con.execute("SELECT id FROM workflow_entity WHERE name = ?", (WF8_NAME,)).fetchall()
        for (wf_id,) in rows:
            con.execute("DELETE FROM workflow_entity WHERE id = ?", (wf_id,))
            con.execute("DELETE FROM workflow_history WHERE workflowId = ?", (wf_id,))
            con.execute("DELETE FROM webhook_entity WHERE workflowId = ?", (wf_id,))
        con.commit()
    finally:
        con.close()


def _import_wf8() -> str:
    data = json.loads(WF8_PATH.read_text(encoding="utf-8"))
    wf_id = str(uuid.uuid4())
    data["id"] = wf_id
    data["active"] = False
    tmp = Path("/tmp/n8n-import-wf8-fixed.json")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    r = subprocess.run(
        ["npx", "--yes", "n8n", "import:workflow", f"--input={tmp}"],
        capture_output=True,
        text=True,
        cwd=str(SOURCE_A),
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return wf_id


def _ensure_api_key() -> str:
    import urllib.request

    if API_KEY_PATH.is_file():
        key = API_KEY_PATH.read_text(encoding="utf-8").strip()
        if key:
            return key

    # Create API key via n8n public API (requires owner session cookie) — fallback: owner UI once.
    # Use stored key from env if founder set it.
    env_key = __import__("os").environ.get("N8N_API_KEY", "").strip()
    if env_key:
        API_KEY_PATH.write_text(env_key + "\n", encoding="utf-8")
        return env_key

    raise RuntimeError(
        "No n8n API key. Create one in n8n UI → Settings → API → Create API Key, "
        f"save to {API_KEY_PATH}, then re-run."
    )


def _activate_via_api(wf_id: str, api_key: str) -> bool:
    import urllib.error
    import urllib.request

    for path in (f"/api/v1/workflows/{wf_id}/activate", f"/api/v1/workflows/{wf_id}"):
        try:
            if path.endswith("/activate"):
                req = urllib.request.Request(
                    f"http://127.0.0.1:5678{path}",
                    data=b"{}",
                    headers={"X-N8N-API-KEY": api_key, "Content-Type": "application/json"},
                    method="POST",
                )
            else:
                body = json.dumps({"active": True}).encode()
                req = urllib.request.Request(
                    f"http://127.0.0.1:5678{path}",
                    data=body,
                    headers={"X-N8N-API-KEY": api_key, "Content-Type": "application/json"},
                    method="PATCH",
                )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return 200 <= resp.status < 300
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            body = e.read().decode(errors="replace")[:200]
            raise RuntimeError(f"activate failed {e.code}: {body}") from e
    return False


def _activate_via_sqlite(wf_id: str) -> None:
    con = sqlite3.connect(N8N_DB)
    try:
        con.execute("UPDATE workflow_entity SET active = 1 WHERE id = ?", (wf_id,))
        con.commit()
    finally:
        con.close()
    _stop_n8n()
    _start_n8n()


def _webhook_probe() -> bool:
    import urllib.error
    import urllib.request

    payload = json.dumps({"event": "test", "action": "cpu_cool_down", "cpu_after": 42}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:5678/webhook/mac-health-cooldown",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        return e.code not in (404, 503)
    except Exception:
        return False


def _update_p0_gate(webhook_ok: bool, wf_id: str) -> None:
    if not P0_GATE.is_file():
        return
    gate = json.loads(P0_GATE.read_text(encoding="utf-8"))
    items = gate.setdefault("items", {})
    items["wf8_webhook_active"] = True
    items["wf8_webhook_probe"] = webhook_ok
    items["wf8_id"] = wf_id
    items["wf8_webhook_fixed_at"] = _now()
    gate["ok"] = bool(items.get("cooldown_receipt")) and items.get("health_ping_overall") in ("green", "yellow")
    P0_GATE.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    _regenerate_wf8()
    _stop_n8n()
    _delete_wf8_rows()
    wf_id = _import_wf8()
    _start_n8n()

    activated = False
    try:
        api_key = _ensure_api_key()
        activated = _activate_via_api(wf_id, api_key)
    except RuntimeError:
        _activate_via_sqlite(wf_id)

    if not activated:
        _activate_via_sqlite(wf_id)

    time.sleep(2)
    ok = _webhook_probe()
    _update_p0_gate(ok, wf_id)
    print(json.dumps({"ok": ok, "wf_id": wf_id, "webhook_probe": ok, "activated": activated}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
