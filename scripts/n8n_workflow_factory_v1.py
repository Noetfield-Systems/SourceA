#!/usr/bin/env python3
"""Generate n8n workflow JSON files for glue runner commands."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
OUT = SOURCE_A / "n8n/workflows"
MONO = Path.home() / "Desktop/SinaaiMonoRepo/n8n/workflows"
GLUE_URL = "http://127.0.0.1:13020/api/cloud-workers/v1"
PAYLOAD_CMDS = frozenset(
    {
        "signal-ingest",
        "cooldown-ingest",
        "founder-request",
        "semej-bookend",
        "chat-unify-merge",
        "film-ingest",
    }
)

SPECS = [
    ("wf-mac-health-cooldown-v1", "webhook", "mac-health-cooldown", "cooldown-ingest", None),
    ("wf-factory-queue-sweeper-v1", "cron", "0 * * * *", "queue-sweep", 60),
    ("wf-disk-live-wire-watchdog-v1", "cron", "*/30 * * * *", "disk-wire", 30),
    ("wf-n8n-self-pause-cpu-v1", "cron", "*/5 * * * *", "cpu-pause-check", 5),
    ("wf-governance-fast-15m-v1", "cron", "*/15 * * * *", "governance-fast", 15),
    ("wf-poison-track-reminder-v1", "cron", "0 9 * * *", "poison-track", 1440),
    ("wf-run-inbox-reminder-v1", "cron", "0 * * * *", "factory-stuck", 60),
    ("wf-judge-audit-batch-v1", "cron", "0 2 * * *", "judge-audit", 1440),
    ("wf-thread-scout-weekly-v1", "cron", "0 10 * * 0", "thread-scout", 10080),
    ("wf-openrouter-governance-hook-v1", "cron", "0 6 * * *", "openrouter-shadow", 1440),
    ("wf-agent-scoreboard-sync-v1", "cron", "0 * * * *", "scoreboard-sync", 60),
    ("wf-founder-request-registrar-v1", "webhook", "founder-request", "founder-request", None),
    ("wf-semej-session-bookend-v1", "webhook", "semej-bookend", "semej-bookend", None),
    ("wf-backup-receipt-archiver-v1", "cron", "0 3 * * 0", "backup-archive", 10080),
    ("wf-chat-unify-merge-receipt-v1", "webhook", "chat-unify-merge", "chat-unify-merge", None),
    ("wf-cloud-auto-runtime-v1", "cron", "*/10 * * * *", "cloud-auto-runtime-tick", 10),
]


def _glue_http_node(*, cmd: str, webhook_payload: bool) -> dict:
    if webhook_payload or cmd in PAYLOAD_CMDS:
        json_body = (
            f"={{{{ JSON.stringify({{ action: 'glue_run', command: '{cmd}', "
            f"payload: $json }}) }}}}"
        )
    else:
        json_body = json.dumps({"action": "glue_run", "command": cmd})
    return {
        "id": str(uuid.uuid4()),
        "name": "Hub glue",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "parameters": {
            "method": "POST",
            "url": GLUE_URL,
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json_body,
            "options": {
                "response": {
                    "response": {
                        "neverError": True,
                    }
                }
            },
        },
        "position": [280, 300],
    }


def _wf(name: str, trigger: str, trig_val: str, cmd: str) -> dict:
    nodes = []
    conns: dict = {}
    glue = _glue_http_node(cmd=cmd, webhook_payload=(trigger == "webhook"))
    if trigger == "webhook":
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "parameters": {"path": trig_val, "httpMethod": "POST", "options": {}},
            "position": [0, 300],
        })
        nodes.append(glue)
        conns = {"Webhook": {"main": [[{"node": "Hub glue", "type": "main", "index": 0}]]}}
    else:
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": "Schedule",
            "type": "n8n-nodes-base.cron",
            "typeVersion": 1,
            "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": trig_val}]}},
            "position": [0, 300],
        })
        nodes.append(glue)
        conns = {"Schedule": {"main": [[{"node": "Hub glue", "type": "main", "index": 0}]]}}
    return {
        "name": name,
        "nodes": nodes,
        "connections": conns,
        "active": False,
        "settings": {"executionOrder": "v1"},
        "meta": {"schema": "sina-n8n-glue-workflow-v1", "glue_command": cmd},
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    MONO.mkdir(parents=True, exist_ok=True)
    for name, trig, val, cmd, _mins in SPECS:
        wf = _wf(name, trig, val, cmd)
        path = OUT / f"{name}.json"
        path.write_text(json.dumps(wf, indent=2), encoding="utf-8")
        (MONO / f"{name}.json").write_text(json.dumps(wf, indent=2), encoding="utf-8")
    # stack health v2 copy
    src = OUT / "sinaai-stack-health-ping.json"
    if src.is_file():
        (MONO / "sinaai-stack-health-ping.json").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"ok": True, "written": len(SPECS) + 1, "dir": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
