#!/usr/bin/env python3
"""Bootstrap Tier 0 n8n glue substrate on disk."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from n8n_glue_config_v1 import DEFAULT_CONFIG, RECEIPTS_ROOT, SINA, detect_hub_mode, save_config

SOURCE_A = Path(__file__).resolve().parents[1]
MONO = Path.home() / "Desktop/SinaaiMonoRepo"
MANIFEST = SOURCE_A / "scripts/fixtures/n8n/workflow_manifest.json"

WORKFLOW_CATALOG = [
    ("sinaai-stack-health-ping", "health", "production", 1, "A"),
    ("wf-mac-health-cooldown", "health", "production", 1, "A"),
    ("wf-factory-queue-sweeper", "health", "production", 2, "A"),
    ("wf-disk-live-wire-watchdog", "health", "production", 2, "A"),
    ("wf-n8n-self-pause-cpu", "health", "production", 2, "A"),
    ("wf-governance-fast-15m", "governance", "stub", 3, "B"),
    ("wf-poison-track-reminder", "governance", "production", 3, "B"),
    ("wf-run-inbox-reminder", "factory", "production", 3, "B"),
    ("wf-judge-audit-batch", "governance", "stub", 5, "B"),
    ("wf-thread-scout-weekly", "governance", "stub", 5, "B"),
    ("wf-openrouter-governance-hook", "governance", "stub", 5, "B"),
    ("sinaai-product-signal-webhook", "intelligence", "production", 4, "C"),
    ("sinaai-intelligence-pipeline", "intelligence", "production", 4, "C"),
    ("wf-chat-unify-merge-receipt", "intelligence", "production", 6, "D"),
    ("wf-agent-scoreboard-sync", "governance", "production", 6, "D"),
    ("wf-founder-request-registrar", "archive", "production", 6, "D"),
    ("wf-semej-session-bookend", "archive", "production", 6, "D"),
    ("wf-backup-receipt-archiver", "archive", "production", 6, "D"),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_path(wf_id: str) -> str | None:
    candidates = [
        MONO / "n8n/workflows" / f"{wf_id}.json",
        MONO / "n8n/workflows" / f"{wf_id}.stub.json",
        SOURCE_A / "n8n/workflows" / f"{wf_id}.json",
        SOURCE_A / "n8n/workflows" / f"{wf_id}.stub.json",
        SOURCE_A / "n8n/workflows" / f"{wf_id}-v1.json",
    ]
    if wf_id == "sinaai-stack-health-ping":
        candidates.insert(0, MONO / "n8n/workflows/sinaai-stack-health-ping.json")
    for p in candidates:
        if p.is_file():
            return str(p)
    return None


def bootstrap() -> dict:
    tracks = ("health", "governance", "factory", "intelligence", "archive")
    for t in tracks:
        (RECEIPTS_ROOT / t).mkdir(parents=True, exist_ok=True)
    readme = RECEIPTS_ROOT / "README.txt"
    readme.write_text(
        "health/ — stack ping, mac health cooldown, queue sweep, disk wire, cpu pause\n"
        "governance/ — fast 15m, poison track, judge, thread scout, openrouter\n"
        "factory/ — run inbox reminder, queue sweeper\n"
        "intelligence/ — product signals, brief pipeline\n"
        "archive/ — backups, founder requests, semej bookends\n",
        encoding="utf-8",
    )

    cfg = dict(DEFAULT_CONFIG)
    cfg["hub_mode"] = detect_hub_mode()
    cfg["bootstrapped_at"] = _now()
    save_config(cfg)

    rows = []
    for wf_id, track, status, tier, parallel in WORKFLOW_CATALOG:
        rows.append(
            {
                "id": wf_id,
                "track": track,
                "tier": tier,
                "parallel_track": parallel,
                "status": status,
                "on_disk": _resolve_path(wf_id),
            }
        )
    inventory = {
        "schema": "n8n-workflow-inventory-v2",
        "at": _now(),
        "hub_mode": cfg["hub_mode"],
        "workflows": rows,
        "deferred": ["sinaai-telegram-agents", "wf-form-change-cascade", "wf-health-sweep-15m"],
        "manifest_path": str(MANIFEST),
    }
    inv_path = SINA / "n8n-workflow-inventory-v2.json"
    inv_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")

    listener = {
        "schema": "n8n-listener-state-v1",
        "at": _now(),
        "active_listener": "runtime",
        "n8n_telegram_workflow": "off",
        "runtime_telegram_bot": "default_on_when_runtime_up",
        "law": "one listener only — never enable sinaai-telegram-agents while Runtime bot active",
    }
    (SINA / "n8n-listener-state-v1.json").write_text(json.dumps(listener, indent=2), encoding="utf-8")

    schedule = {
        "schema": "n8n-schedule-policy-v1",
        "at": _now(),
        "rule": "founder enables cron only after 2 manual PASS per workflow",
        "default_active": False,
        "workflows": {r["id"]: {"cron": None, "active": False} for r in rows},
    }
    (SINA / "n8n-schedule-policy-v1.json").write_text(json.dumps(schedule, indent=2), encoding="utf-8")

    return {"ok": True, "config": str(SINA / "n8n-glue-config-v1.json"), "inventory": str(inv_path), "hub_mode": cfg["hub_mode"]}


if __name__ == "__main__":
    import sys

    print(json.dumps(bootstrap(), indent=2))
    raise SystemExit(0)
