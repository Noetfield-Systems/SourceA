#!/usr/bin/env python3
"""Validate Cloud Factory 10 Steps receipts — CHECK ALL."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
PLAN = ROOT / "data" / "brain-cloud-practical-300-plan-v1.json"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _health(url: str) -> bool:
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=8) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        return bool(row.get("ok")) and str(row.get("service", "")).startswith("fbe")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return False


def run_check() -> dict:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from cloud_factory_10_steps_v1 import _patch_federated_honesty  # noqa: WPS433

        _patch_federated_honesty()
    except Exception:
        pass
    checks: list[dict] = []
    cfg = _read(CONFIG)
    url = str(cfg.get("worker_url") or "")
    secrets = (SINA / "secrets.env").read_text(encoding="utf-8") if (SINA / "secrets.env").is_file() else ""

    def add(step: str, ok: bool, detail: str, *, warn: bool = False) -> None:
        checks.append({"step": step, "ok": ok, "warn": warn, "detail": detail})

    add("step1_health", _health(url) if url else False, f"worker_url={url or 'empty'}")
    dep = _read(SINA / "fbe-cloud-deploy-receipt-v1.json")
    add("step1_receipt", bool(dep.get("ok")), str(dep.get("deployment") or dep.get("error")))
    railway_pending = dep.get("railway_pending") or {}
    local_health_ok = _health(url) if url else False
    if url.startswith("https://") and local_health_ok:
        add("step1_railway", True, f"Railway public URL live · {url[:72]}")
    elif dep.get("ok") and str(dep.get("worker_url") or "").startswith("https://") and _health(str(dep.get("worker_url"))):
        add("step1_railway", True, f"Railway public URL live · {str(dep.get('worker_url'))[:72]}")
    elif url.startswith("http://127.") and railway_pending.get("documented") and local_health_ok:
        founder_gate = railway_pending.get("founder_gate") or {}
        action = str(railway_pending.get("founder_action") or "scripts/deploy_fbe_railway_v1.py")
        detail = (
            f"local control-plane proxy ok · need public fbe-cloud-worker HTTPS · run {action}"
        )
        if founder_gate.get("documented"):
            detail += f" · blocker={founder_gate.get('blocker', 'pending')}"
        add("step1_railway", False, detail, warn=True)
    elif url.startswith("http://127."):
        add("step1_railway", False, "local FBE HTTP — Mac/local proxy does NOT count as cloud factory online")

    add("step2_secrets", "FBE_CLOUD_WORKER_URL" in secrets and bool(url), "secrets.env + config synced")
    add("step2_config", cfg.get("worker_url") == url, "fbe_cloud_worker_config worker_url")

    hub = _read(SINA / "hub-cloud-proxy-check-v1.json")
    add("step3_hub", bool(hub.get("ok")), str(hub.get("surfaces", ""))[:80])
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    line = str(surfaces.get("cloud_practical_300_line") or "")
    add("step3_surfaces", "300/300" in line and "head=C300-300" in line, line[:90])

    wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    add(
        "step4_wo",
        wo.get("execution_mode") == "brain_work_order"
        and wo.get("bay_slug") == "noetfield-freemium-bay"
        and bool(wo.get("local_worker_deprecated")),
        f"{wo.get('execution_mode')} · {wo.get('bay_slug')}",
    )

    bay = _read(SINA / "fbe-bay-run-receipt-v1.json")
    add("step5_nf", bool(bay.get("ok")), bay.get("bay_slug", ""))

    p0 = _read(SINA / "brain-phase0-dispatch-receipt-v1.json")
    add(
        "step6_cloud_proof",
        p0.get("cloud_stub") is False and bool(p0.get("bay_ok") or (p0.get("bay") or {}).get("ok")),
        f"cloud_stub={p0.get('cloud_stub')} bay_ok={p0.get('bay_ok')}",
    )
    fed = _read(SINA / "fbe-federated-receipt-v1.json")
    add(
        "step6_federated",
        fed.get("remote_status") == "cloud_api_worker",
        f"remote_status={fed.get('remote_status')}",
    )

    loop = _read(SINA / "loop-specialist-config-v1.json")
    add("step7_loop", bool(loop.get("loop_auto_dispatch_enabled")), str(loop.get("loop_auto_mode")))

    tf = _read(SINA / "trustfield-sandbox-receipt-v1.json")
    add("step8_tf", bool(tf.get("ok")), tf.get("factory_id", ""))

    grad = _read(SINA / "brain-cloud-graduate-receipt-v1.json")
    add("step9_graduate", bool(grad.get("ok")), "local_worker_deprecated")

    mkt = _read(SINA / "market-traction-receipt-v1.json")
    w3_block = mkt.get("w3_send_ready") or {}
    w3 = w3_block.get("status")
    founder_gate = w3_block.get("founder_gate") or {}
    add("step10_market", bool(mkt.get("ok")), f"w3_send={w3}")
    if w3 == "GREEN":
        add("step10_w3_send", True, "w3_send_ready GREEN")
    elif w3 == "RED" and founder_gate.get("documented"):
        add(
            "step10_w3_send",
            True,
            "w3_send_ready RED · founder gate documented — agents never send",
        )
    elif w3 == "RED":
        add("step10_w3_send", False, "w3_send_ready RED — send blocked until founder gate", warn=True)

    plan = _read(PLAN)
    prog = plan.get("progress") or {}
    add("plan_300", prog.get("done") == 300 and prog.get("cloud_proven") == 300, str(prog))

    master = _read(SINA / "cloud-factory-10-steps-receipt-v1.json")
    add("master_receipt", bool(master.get("ok")), master.get("at", ""))

    hard_fail = [c for c in checks if not c["ok"] and not c.get("warn")]
    warn = [c for c in checks if not c["ok"] and c.get("warn")]
    return {
        "ok": len(hard_fail) == 0,
        "schema": "cloud-factory-10-steps-check-v1",
        "hard_fail_count": len(hard_fail),
        "warn_count": len(warn),
        "checks": checks,
        "hard_fails": hard_fail,
        "warnings": warn,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_check()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        for c in row["checks"]:
            tag = "WARN" if c.get("warn") and not c["ok"] else ("PASS" if c["ok"] else "FAIL")
            print(f"{tag} {c['step']}: {c['detail']}")
        print(f"SUMMARY ok={row['ok']} hard_fail={row['hard_fail_count']} warn={row['warn_count']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
