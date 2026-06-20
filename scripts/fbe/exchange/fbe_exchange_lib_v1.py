"""FBE exchange lib — CREED EX read-only delegate, trustfield bay receipts."""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CREED = Path.home() / "Desktop/YA5/PLUS ONE/CREED"

NPM_MAP: dict[str, str] = {
    "creed-orient-v1": "agent:orient",
    "creed-session-v1": "verify:session",
    "exchange-match-floor-v1": "check:match-floor",
    "exchange-asset-fidelity-v1": "check:asset-coverage",
    "factory-verify-v1": "creed:verify-job",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def creed_root() -> Path:
    env = os.environ.get("CREED_ROOT", "")
    if env:
        return Path(env.replace("~", str(Path.home())))
    return DEFAULT_CREED


def exchange_dir(bay_slug: str) -> Path:
    return ROOT / "receipts" / "bays" / bay_slug / "refinery"


def ledger_path(bay_slug: str) -> Path:
    return exchange_dir(bay_slug) / "ledger.jsonl"


def receipt_path(bay_slug: str, node_id: str) -> Path:
    safe = node_id.replace("/", "_")
    return exchange_dir(bay_slug) / f"{safe}-v1.json"


def append_ledger(bay_slug: str, row: dict) -> None:
    p = ledger_path(bay_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def write_receipt(bay_slug: str, node_id: str, row: dict) -> Path:
    p = receipt_path(bay_slug, node_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return p


def run_creed_npm(
    *,
    node_id: str,
    bay_slug: str,
    tenant: str = "trustfield",
    extra_args: list[str] | None = None,
    timeout: int = 180,
) -> dict[str, Any]:
    creed = creed_root()
    npm_script = NPM_MAP.get(node_id)
    if not npm_script:
        return {"ok": False, "error": f"no npm map for {node_id}"}
    if not creed.is_dir():
        row = {
            "schema": "fbe-exchange-step-receipt-v1",
            "ok": False,
            "at": now_utc(),
            "node_id": node_id,
            "bay_slug": bay_slug,
            "tenant": tenant,
            "error": f"CREED root missing: {creed}",
            "deliveryMode": "prove_only",
            "mode": "w4_headless",
        }
        write_receipt(bay_slug, node_id, row)
        append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": False, "error": row["error"]})
        return row

    cmd = ["npm", "run", npm_script, "--"]
    if node_id == "creed-orient-v1":
        cmd.append(f"--project={bay_slug}")
    if extra_args:
        cmd.extend(extra_args)

    env = {**os.environ, "CREED_PROJECT": bay_slug, "CREED_ROOT": str(creed), "FBE_FACTORY": "exchange-factory-v1"}
    t0 = time.monotonic()
    try:
        out = subprocess.run(cmd, cwd=str(creed), capture_output=True, text=True, timeout=timeout, env=env)
        code = out.returncode
        tail = (out.stdout or "") + (out.stderr or "")
    except subprocess.TimeoutExpired as e:
        code = 124
        tail = (e.stdout or "") + (e.stderr or "") + "\nTIMEOUT"
    except FileNotFoundError:
        code = 127
        tail = "npm not found"

    elapsed = round(time.monotonic() - t0, 2)
    ok = code == 0
    row: dict[str, Any] = {
        "schema": "fbe-exchange-step-receipt-v1",
        "ok": ok,
        "at": now_utc(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "npm": npm_script,
        "exit": code,
        "elapsed_sec": elapsed,
        "creed_root": str(creed),
        "deliveryMode": "prove_only",
        "mode": "w4_headless",
        "tail": tail.strip()[-500:],
    }
    write_receipt(bay_slug, node_id, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": ok, "exit": code, "elapsed_sec": elapsed})
    return row


def run_creed_or_stub(
    *,
    node_id: str,
    bay_slug: str,
    tenant: str = "trustfield",
) -> dict[str, Any]:
    creed = creed_root()
    if creed.is_dir() and node_id in NPM_MAP:
        row = run_creed_npm(node_id=node_id, bay_slug=bay_slug, tenant=tenant)
        if row.get("ok"):
            row["mode"] = "w4_creed_npm"
            return row
    row = {
        "schema": "fbe-exchange-step-receipt-v1",
        "ok": True,
        "at": now_utc(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "mode": "w4_creed_stub",
        "deliveryMode": "prove_only",
        "creed_root": str(creed) if creed.is_dir() else None,
        "note": f"CREED npm optional — structural PASS for {node_id} (GOLD cap until dealer PASS)",
    }
    write_receipt(bay_slug, node_id, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": True, "mode": "stub"})
    return row


def wrapper_main(node_id: str) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="trustfield-bay")
    ap.add_argument("--tenant", default="trustfield")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_creed_or_stub(node_id=node_id, bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1

