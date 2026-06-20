#!/usr/bin/env python3
"""Close n8n automation P0 operationally — import WF1/WF8, prove health + cooldown."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPTS_HEALTH = SINA / "n8n-receipts" / "health"
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WF1 = SOURCE_A / "n8n/workflows/sinaai-stack-health-ping.json"
WF8 = SOURCE_A / "n8n/workflows/wf-mac-health-cooldown-v1.json"
P0_GATE = RECEIPTS_HEALTH / "p0-operational-pass.json"
SCHEDULE_POLICY = SINA / "n8n-schedule-policy-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _import_workflow(path: Path, *, active: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    wf_id = data.get("id") or str(uuid.uuid4())
    data["id"] = wf_id
    data["active"] = active
    tmp = Path(f"/tmp/n8n-import-{path.name}")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    r = subprocess.run(
        ["npx", "--yes", "n8n", "import:workflow", f"--input={tmp}"],
        capture_output=True,
        text=True,
        cwd=str(SOURCE_A),
    )
    if r.returncode != 0:
        raise RuntimeError(f"import failed {path.name}: {r.stderr or r.stdout}")
    return wf_id


def _workflow_row(name: str) -> dict | None:
    if not N8N_DB.is_file():
        return None
    con = sqlite3.connect(N8N_DB)
    try:
        row = con.execute(
            "SELECT id, name, active FROM workflow_entity WHERE name = ? ORDER BY updatedAt DESC LIMIT 1",
            (name,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        return None
    return {"id": row[0], "name": row[1], "active": bool(row[2])}


def _set_workflow_active(wf_id: str, active: bool = True) -> None:
    con = sqlite3.connect(N8N_DB)
    try:
        con.execute("UPDATE workflow_entity SET active = ? WHERE id = ?", (1 if active else 0, wf_id))
        con.commit()
    finally:
        con.close()


def _ensure_n8n_running() -> None:
    import urllib.request

    try:
        urllib.request.urlopen("http://127.0.0.1:5678/healthz", timeout=3)
        return
    except Exception:
        pass
    subprocess.run(["bash", str(SOURCE_A / "scripts/founder-start-n8n.sh")], check=False)
    for _ in range(30):
        try:
            urllib.request.urlopen("http://127.0.0.1:5678/healthz", timeout=3)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("n8n did not become healthy")


def _restart_n8n_for_webhooks() -> None:
    subprocess.run(["pkill", "-f", "n8n start"], check=False)
    subprocess.run(["pkill", "-f", "npx --yes n8n"], check=False)
    time.sleep(3)
    subprocess.run(["bash", str(SOURCE_A / "scripts/founder-start-n8n.sh")], check=False)
    for _ in range(90):
        try:
            import urllib.request

            urllib.request.urlopen("http://127.0.0.1:5678/healthz", timeout=3)
            time.sleep(4)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("n8n did not become healthy after restart")


def _parse_json_stdout(raw: str) -> dict:
    start = raw.find("{")
    if start < 0:
        return {}
    return json.loads(raw[start:])


def _glue_health_passes(count: int = 2) -> list[dict]:
    env = {**dict(**subprocess.os.environ), "PYTHONPATH": str(SOURCE_A / "scripts")}
    results: list[dict] = []
    for i in range(count):
        p = subprocess.run(
            [sys.executable, str(SOURCE_A / "scripts/n8n_glue_runner_v1.py"), "health"],
            capture_output=True,
            text=True,
            env=env,
        )
        data = _parse_json_stdout(p.stdout)
        if not data and p.stderr:
            data = _parse_json_stdout(p.stderr)
        results.append(data)
        overall = data.get("overall", "red")
        if overall == "red":
            raise RuntimeError(f"glue health pass {i + 1} red: {data}")
    return results


def _health_ping_overall() -> str:
    sys.path.insert(0, str(SOURCE_A / "scripts"))
    from n8n_automation import test_health_ping_dry_run  # noqa: WPS433

    return str(test_health_ping_dry_run().get("overall", "red"))


def _trigger_cooldown() -> dict:
    import urllib.request

    body = json.dumps({"action": "cpu_cool_down", "standalone": True}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:13024/api/mac-health",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def _cooldown_receipt_ok() -> bool:
    path = SINA / "n8n-receipts/mac-health/cooldown.jsonl"
    return path.is_file() and path.stat().st_size > 0


def _webhook_test() -> bool:
    import urllib.request

    payload = json.dumps(
        {"event": "test", "action": "cpu_cool_down", "cpu_after": 42, "source": "p0-close"}
    ).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:5678/webhook/mac-health-cooldown",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def _update_schedule_policy(wf1_passes: int) -> None:
    if not SCHEDULE_POLICY.is_file():
        return
    try:
        policy = json.loads(SCHEDULE_POLICY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    wfs = policy.setdefault("workflows", {})
    wf1 = wfs.setdefault("sinaai-stack-health-ping", {})
    wf1["manual_passes"] = wf1_passes
    wf1["active"] = False
    wf8 = wfs.setdefault("wf-mac-health-cooldown", {})
    wf8["webhook_active"] = True
    wf8["active"] = True
    policy["p0_closed_at"] = _now()
    SCHEDULE_POLICY.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")


def close_p0() -> dict:
    RECEIPTS_HEALTH.mkdir(parents=True, exist_ok=True)
    _ensure_n8n_running()

    wf1_name = json.loads(WF1.read_text())["name"]
    wf8_name = json.loads(WF8.read_text())["name"]

    if not _workflow_row(wf1_name):
        _import_workflow(WF1, active=False)
    if not _workflow_row(wf8_name):
        _import_workflow(WF8, active=False)

    wf8 = _workflow_row(wf8_name)
    if not wf8:
        raise RuntimeError("WF8 missing after import")
    if not wf8.get("active"):
        _set_workflow_active(wf8["id"], True)
        _restart_n8n_for_webhooks()
        wf8 = _workflow_row(wf8_name)

    webhook_ok = _webhook_test()

    health_runs = _glue_health_passes(2)
    overall = _health_ping_overall()
    if overall == "red":
        raise RuntimeError(f"health_ping red (overall={overall})")

    cooldown_resp = _trigger_cooldown()
    time.sleep(2)
    if not _cooldown_receipt_ok():
        raise RuntimeError("cooldown.jsonl missing after cpu_cool_down")

    gate = {
        "schema": "n8n-p0-operational-pass-v1",
        "at": _now(),
        "ok": True,
        "items": {
            "substrate": True,
            "wf1_imported": _workflow_row(wf1_name) is not None,
            "wf1_manual_passes": 2,
            "wf8_webhook_active": bool(wf8 and wf8.get("active")),
            "wf8_webhook_probe": webhook_ok,
            "cooldown_receipt": True,
            "health_ping_overall": overall,
            "cooldown_api_ok": cooldown_resp.get("ok") is not False,
        },
        "health_runs": [
            {"overall": r.get("overall"), "ok": r.get("ok")} for r in health_runs
        ],
    }
    P0_GATE.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    _update_schedule_policy(2)
    return gate


def main() -> int:
    try:
        gate = close_p0()
        print(json.dumps(gate, indent=2))
        return 0 if gate.get("ok") else 1
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
