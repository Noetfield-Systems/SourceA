#!/usr/bin/env python3
"""Founder execution model — Mac control panel · Cloud factories · auto-upgrade disk + machines.

Law: data/founder-execution-model-v1.json
Receipt: ~/.sina/founder-execution-model-receipt-v1.json

Run after every new founder rule:
  python3 scripts/founder_execution_model_v1.py --wire-sync --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "founder-execution-model-v1.json"
MACHINE_REG = ROOT / "data" / "machine-execution-plane-registry-v1.json"
RECEIPT = SINA / "founder-execution-model-receipt-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _run(cmd: list[str], *, timeout: float = 90.0) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout, cwd=str(ROOT))
        return 0, out[:800]
    except subprocess.CalledProcessError as exc:
        return int(exc.returncode or 1), (exc.output or str(exc))[:800]
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def load_ssot() -> dict:
    return _read(SSOT)


def build_machine_registry(ssot: dict) -> dict:
    mac = ssot.get("mac_role") or {}
    cloud = ssot.get("cloud_role") or {}
    main_ids = list(cloud.get("main_cloud_factories") or [])
    deferred = list(cloud.get("deferred_lanes") or [])

    def _factory_row(spec: dict, *, tier: str, priority: int) -> dict:
        row = dict(spec)
        row["tier"] = tier
        row["priority"] = priority
        return row

    main_specs = [
        {"id": "fbe_railway", "execution_plane": "cloud_api_worker", "host": "railway", "script": "scripts/fbe_runner_v1.py"},
        {"id": "supabase_edge", "execution_plane": "cloud_api_worker", "host": "supabase", "migration": "data/supabase-migration-001-campaign-automations-v1.sql"},
        {"id": "video_ad_factory", "execution_plane": "cloud", "orchestrate": "scripts/video_ad_factory_orchestrate_v1.py", "render": "scripts/video_ad_rendering_bridge_v1.py"},
        {"id": "noetfield_freemium_bay", "execution_plane": "cloud_api_worker", "work_order": "U094"},
        {"id": "trustfield_sandbox", "execution_plane": "cloud_api_worker", "receipt": "~/.sina/trustfield-sandbox-receipt-v1.json"},
        {"id": "witnessbc_proof_lab", "execution_plane": "cloud_api_worker", "receipt": "~/.sina/witnessbc-proof-lab-publish-receipt-v1.json", "site": "https://witnessbc.com", "orchestrate": "scripts/witnessbc_proof_lab_publish_v1.py"},
        {"id": "fal_rendering_bridge", "execution_plane": "cloud", "env": "FAL_KEY"},
        {"id": "openrouter_cloud", "execution_plane": "cloud", "note": "LLM on cloud — not Mac body"},
    ]
    main_by_id = {s["id"]: s for s in main_specs}
    main_cloud = [
        _factory_row(main_by_id[fid], tier="main", priority=i + 1)
        for i, fid in enumerate(main_ids)
        if fid in main_by_id
    ]
    deferred_cloud = [
        _factory_row(
            {
                "id": str(d.get("id") or "commercial_email_cloud"),
                "execution_plane": "cloud",
                "defer_ssot": d.get("defer_ssot") or "data/commercial-email-send-defer-v1.json",
                "label": d.get("label"),
                "runs_after": d.get("runs_after"),
            },
            tier="deferred",
            priority=int(d.get("priority") or 99),
        )
        for d in deferred
    ]
    return {
        "schema": "machine-execution-plane-registry-v1",
        "version": "1.1.0",
        "saved_at": _now(),
        "ssot": "data/founder-execution-model-v1.json",
        "one_law": ssot.get("one_law"),
        "factory_priority_law": cloud.get("factory_priority_law"),
        "mac_role": mac.get("canonical"),
        "mac_role_aliases": mac.get("aliases") or [],
        "cloud_role": cloud.get("canonical"),
        "main_cloud_factories": main_ids,
        "deferred_lanes": [d.get("id") for d in deferred],
        "control_plane_only": [
            {
                "id": "worker_hub",
                "role": "cockpit",
                "url": "http://127.0.0.1:13020/",
                "runs": ["form_pick", "gate", "approve", "monitor", "factory_now"],
                "execution_plane": "mac_control_panel",
            },
            {
                "id": "mac_health_guard",
                "role": "cockpit_health",
                "url": "http://127.0.0.1:13024/",
                "runs": ["body_monitor", "cooldown_pulse"],
                "execution_plane": "mac_control_panel",
                "note": "NOT a factory — health shield only",
            },
            {
                "id": "session_gate",
                "role": "gate",
                "script": "scripts/agent_session_gate_run_v1.py",
                "execution_plane": "mac_control_panel",
            },
            {
                "id": "form_official",
                "role": "human_fork_intake",
                "url": "http://127.0.0.1:13020/form/",
                "execution_plane": "mac_control_panel",
            },
        ],
        "cloud_factories": main_cloud + deferred_cloud,
        "forbidden_on_mac": mac.get("forbidden_as_factory") or [],
        "factory_online_law": ssot.get("cloud_factories_online_ssot") or "data/cloud-factories-online-only-v1.json",
        "factory_online_one_law": "Factories ONLINE on cloud + public API only — Mac = control panel never factory body",
        "founder_rules_count": len(ssot.get("founder_rules_live") or []),
    }


def sync_ledgers(ssot: dict) -> list[dict]:
    steps: list[dict] = []
    mac_canonical = (ssot.get("mac_role") or {}).get("canonical") or "control_plane_only"
    cloud_canonical = (ssot.get("cloud_role") or {}).get("canonical") or "execution_plane_headless"
    aliases = (ssot.get("mac_role") or {}).get("aliases") or []
    ts = _now()

    desired_contracts = {
        "mac_role": mac_canonical,
        "cloud_role": cloud_canonical,
        "founder_execution_model": "data/founder-execution-model-v1.json",
        "mac_role_aliases": aliases,
    }

    for rel in ("data/architecture-ledger-v1.json", "data/cursor-bootstrap-ledger-v1.json", "docs/architecture_ledger.json"):
        path = ROOT / rel
        if not path.is_file():
            steps.append({"target": rel, "ok": False, "detail": "missing"})
            continue
        data = _read(path)
        contracts = data.setdefault("core_contracts", {})
        changed = False
        for key, val in desired_contracts.items():
            if contracts.get(key) != val:
                contracts[key] = val
                changed = True
        if data.get("founder_execution_model_ssot") != "data/founder-execution-model-v1.json":
            data["founder_execution_model_ssot"] = "data/founder-execution-model-v1.json"
            changed = True
        if changed:
            data["saved_at"] = ts
            if rel.startswith("data/") and data.get("schema") in (
                "architecture-ledger-v1",
                "cursor-bootstrap-ledger-v1",
            ):
                data["epoch"] = int(data.get("epoch") or 0) + 1
        _write(path, data)
        steps.append({
            "target": rel,
            "ok": True,
            "changed": changed,
            "epoch": data.get("epoch"),
            "mac_role": mac_canonical,
        })

    wtm = ROOT / "data" / "platform-neutral-world-model-v1.json"
    if wtm.is_file():
        wm = _read(wtm)
        if wm.get("schema") != "platform-neutral-world-model-v1":
            steps.append({
                "target": str(wtm.relative_to(ROOT)),
                "ok": False,
                "detail": "platform-neutral-world-model schema missing — restore SSOT before wire-sync",
            })
        else:
            wm["founder_execution_model"] = "data/founder-execution-model-v1.json"
            wm["execution_split"] = {
                "mac": mac_canonical,
                "cloud": cloud_canonical,
                "one_law": ssot.get("one_law"),
                "factory_online_law": ssot.get("cloud_factories_online_ssot") or "data/cloud-factories-online-only-v1.json",
                "governance": "anti_staleness · zero_drift · zero_fragmentation",
            }
            wm["saved_at"] = ts
            _write(wtm, wm)
            steps.append({"target": str(wtm.relative_to(ROOT)), "ok": True})

    reg = build_machine_registry(ssot)
    _write(MACHINE_REG, reg)
    steps.append({"target": str(MACHINE_REG.relative_to(ROOT)), "ok": True, "cloud_factories": len(reg["cloud_factories"])})

    return steps


def assess() -> dict:
    ssot = load_ssot()
    issues: list[str] = []
    if not ssot:
        issues.append("missing SSOT")
    mac = (ssot.get("mac_role") or {}).get("canonical")
    cloud = (ssot.get("cloud_role") or {}).get("canonical")
    if mac != "control_plane_only":
        issues.append(f"mac_role expected control_plane_only got {mac}")
    if cloud != "execution_plane_headless":
        issues.append(f"cloud_role expected execution_plane_headless got {cloud}")

    boot = _read(ROOT / "data" / "cursor-bootstrap-ledger-v1.json")
    bc = boot.get("core_contracts") or {}
    if bc.get("mac_role") != mac:
        issues.append("cursor-bootstrap mac_role drift")
    if bc.get("cloud_role") != cloud:
        issues.append("cursor-bootstrap cloud_role drift")
    if not (ROOT / "data" / "machine-execution-plane-registry-v1.json").is_file():
        issues.append("machine registry missing — run --wire-sync")

    return {
        "ok": not issues,
        "issues": issues,
        "mac_role": mac,
        "cloud_role": cloud,
        "founder_rules": len(ssot.get("founder_rules_live") or []),
        "one_law": ssot.get("one_law"),
    }


def pulse_receipt(*, write: bool = True) -> dict:
    """Registry pulse — ledgers + machine registry only (no recursive wire-sync)."""
    row = wire_sync(skip_chain=True)
    line = str(row.get("line") or "")
    return {
        **row,
        "ok": bool(row.get("ok")),
        "at": row.get("saved_at") or _now(),
        "founder_execution_model_line": line,
    }


def wire_sync(*, skip_chain: bool = False) -> dict:
    t0 = time.monotonic()
    ssot = load_ssot()
    if not ssot:
        return {"ok": False, "error": "missing SSOT"}

    ledger_steps = sync_ledgers(ssot)
    chain_steps: list[dict] = []

    if not skip_chain:
        for cmd, label in (
            ([PY, str(ROOT / "scripts" / "h2_pending_registry_sync_v1.py")], "h2_registry"),
            ([PY, str(ROOT / "scripts" / "agent_rule_live_wire_v1.py"), "--wire-sync", "--json"], "agent_rule_live_wire"),
        ):
            code, out = _run(cmd, timeout=120)
            chain_steps.append({"step": label, "ok": code == 0, "exit": code, "preview": out[:200]})

    assess_row = assess()
    elapsed = round(time.monotonic() - t0, 2)
    line = (
        f"FOUNDER_EXEC · Mac={assess_row.get('mac_role')} · Cloud={assess_row.get('cloud_role')} · "
        f"rules={assess_row.get('founder_rules')} · ok={'YES' if assess_row.get('ok') else 'NO'}"
    )

    surfaces = SINA / "agent-live-surfaces-v1.json"
    if surfaces.is_file():
        surf = _read(surfaces)
        surf["founder_execution_model_line"] = line
        surf["founder_execution_model_ssot"] = "data/founder-execution-model-v1.json"
        _write(surfaces, surf)

    receipt = {
        "schema": "founder-execution-model-receipt-v1",
        "saved_at": _now(),
        "ok": assess_row.get("ok") and all(s.get("ok") for s in ledger_steps),
        "line": line,
        "ledger_steps": ledger_steps,
        "chain_steps": chain_steps,
        "assess": assess_row,
        "elapsed_s": elapsed,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    _write(RECEIPT, receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder execution model — disk + machine upgrade")
    ap.add_argument("--assess", action="store_true", help="Assess alignment only")
    ap.add_argument("--wire-sync", action="store_true", help="Sync ledgers + machine registry + chain")
    ap.add_argument("--skip-chain", action="store_true", help="Skip h2 + agent_rule wire (ledger only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.wire_sync:
        row = wire_sync(skip_chain=args.skip_chain)
    elif args.assess:
        row = assess()
    else:
        row = assess()
        if not row.get("ok"):
            row = wire_sync(skip_chain=args.skip_chain)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
