#!/usr/bin/env python3
"""Generate n8n workflow JSON files for glue runner commands."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
OUT = SOURCE_A / "n8n/workflows"
MONO = Path.home() / "Desktop/SinaaiMonoRepo/n8n/workflows"
GLUE = "cd ~/Desktop/SourceA/scripts && python3 n8n_glue_runner_v1.py"

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
    ("wf-chat-unify-merge-receipt-v1", "webhook", "chat-unify-merge", "signal-ingest", None),
]


def _wf(name: str, trigger: str, trig_val: str, cmd: str) -> dict:
    nodes = []
    conns: dict = {}
    if trigger == "webhook":
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "parameters": {"path": trig_val, "httpMethod": "POST", "options": {}},
            "position": [0, 300],
        })
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": "Glue runner",
            "type": "n8n-nodes-base.executeCommand",
            "typeVersion": 1,
            "parameters": {"command": f"{GLUE} {cmd} --payload '{{{{ JSON.stringify($json) }}}}'"},
            "position": [280, 300],
        })
        conns = {"Webhook": {"main": [[{"node": "Glue runner", "type": "main", "index": 0}]]}}
    else:
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": "Schedule",
            "type": "n8n-nodes-base.cron",
            "typeVersion": 1,
            "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": trig_val}]}},
            "position": [0, 300],
        })
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": "Glue runner",
            "type": "n8n-nodes-base.executeCommand",
            "typeVersion": 1,
            "parameters": {"command": f"{GLUE} {cmd}"},
            "position": [280, 300],
        })
        conns = {"Schedule": {"main": [[{"node": "Glue runner", "type": "main", "index": 0}]]}}
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
