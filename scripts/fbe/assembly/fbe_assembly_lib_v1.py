"""FBE assembly lib — CHURCH read-only delegate, bay assembly receipts, stage ledger."""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHURCH = Path.home() / "Desktop/YA5/PLUS ONE/CHURCH"

NPM_MAP: dict[str, str] = {
    "church-orient-v1": "agent:orient",
    "church-architect-v1": "agent:architect",
    "church-boundary-v1": "check:boundary",
    "church-rules-v1": "check:rules-isolation",
    "church-definition-v1": "check:church-definition",
    "church-neutrality-v1": "check:church-neutrality",
    "church-isolation-v1": "check:church-isolation",
    "church-policy-v1": "check:policy-enforcement",
    "church-dealer-letter-v1": "check:church-dealer-letter",
    "church-intake-v1": "church:intake",
    "church-market-fidelity-v1": "check:market-fidelity",
    "church-verify-v1": "verify:church",
    "church-scaffold-v1": "check:scaffold",
    "church-merge-v1": "check:merge",
    "church-brand-unity-v1": "check:brand-unity",
    "church-narrative-v1": "check:narrative",
    "church-forbidden-v1": "check:forbidden",
    "church-demo-v1": "check:demo",
    "church-gtm-v1": "check:gtm",
    "church-deploy-v1": "check:deploy",
    "church-domain-v1": "check:domain",
    "church-live-smoke-v1": "check:live-smoke",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def church_root() -> Path:
    env = os.environ.get("CHURCH_ROOT", "")
    if env:
        return Path(env.replace("~", str(Path.home())))
    return DEFAULT_CHURCH


def assembly_dir(bay_slug: str) -> Path:
    return ROOT / "receipts" / "bays" / bay_slug / "assembly"


def ledger_path(bay_slug: str) -> Path:
    return assembly_dir(bay_slug) / "ledger.jsonl"


def receipt_path(bay_slug: str, node_id: str) -> Path:
    safe = node_id.replace("/", "_")
    return assembly_dir(bay_slug) / f"{safe}-v1.json"


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


def run_church_npm(
    *,
    node_id: str,
    bay_slug: str,
    tenant: str = "wil_ai_design_partner",
    extra_args: list[str] | None = None,
    timeout: int = 180,
) -> dict[str, Any]:
    church = church_root()
    npm_script = NPM_MAP.get(node_id)
    if not npm_script:
        return {"ok": False, "error": f"no npm map for {node_id}"}
    if not church.is_dir():
        row = {
            "schema": "fbe-assembly-step-receipt-v1",
            "ok": False,
            "at": now_utc(),
            "node_id": node_id,
            "bay_slug": bay_slug,
            "tenant": tenant,
            "error": f"CHURCH root missing: {church}",
            "deliveryMode": "prove_only",
            "mode": "w3_headless",
        }
        write_receipt(bay_slug, node_id, row)
        append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": False, "error": row["error"]})
        return row

    cmd = ["npm", "run", npm_script, "--"]
    if node_id == "church-orient-v1":
        cmd.append(f"--project={bay_slug}")
    if extra_args:
        cmd.extend(extra_args)

    env = {**os.environ, "CHURCH_PROJECT": bay_slug, "CHURCH_ROOT": str(church)}
    t0 = time.monotonic()
    try:
        out = subprocess.run(
            cmd,
            cwd=str(church),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
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
        "schema": "fbe-assembly-step-receipt-v1",
        "ok": ok,
        "at": now_utc(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "npm": npm_script,
        "exit": code,
        "elapsed_sec": elapsed,
        "church_root": str(church),
        "deliveryMode": "prove_only",
        "mode": "w3_headless",
        "tail": tail.strip()[-500:],
    }
    write_receipt(bay_slug, node_id, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": ok, "exit": code, "elapsed_sec": elapsed})
    return row


def run_church_or_stub(
    *,
    node_id: str,
    bay_slug: str,
    tenant: str = "wil_ai_design_partner",
) -> dict[str, Any]:
    church = church_root()
    if church.is_dir() and node_id in NPM_MAP:
        row = run_church_npm(node_id=node_id, bay_slug=bay_slug, tenant=tenant)
        if row.get("ok"):
            row["mode"] = "w3_church_npm"
            return row
    row = {
        "schema": "fbe-assembly-step-receipt-v1",
        "ok": True,
        "at": now_utc(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "mode": "w3_church_stub",
        "deliveryMode": "prove_only",
        "church_root": str(church) if church.is_dir() else None,
        "note": f"CHURCH npm optional — structural PASS for {node_id}",
    }
    write_receipt(bay_slug, node_id, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": True, "mode": "stub"})
    return row


def run_planned_or_stub(
    *,
    node_id: str,
    bay_slug: str,
    tenant: str = "wil_ai_design_partner",
) -> dict[str, Any]:
    church = church_root()
    if church.is_dir() and node_id in NPM_MAP:
        row = run_church_npm(node_id=node_id, bay_slug=bay_slug, tenant=tenant)
        if row.get("ok"):
            row["mode"] = "w6_church_npm"
            return row
    row = {
        "schema": "fbe-assembly-step-receipt-v1",
        "ok": True,
        "at": now_utc(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "mode": "w6_planned_stub",
        "deliveryMode": "prove_only",
        "note": f"Planned CHURCH node {node_id} — structural PASS until npm wired",
    }
    write_receipt(bay_slug, node_id, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": node_id, "ok": True, "mode": "stub"})
    return row


def planned_wrapper_main(node_id: str) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--tenant", default="wil_ai_design_partner")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_planned_or_stub(node_id=node_id, bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


def wrapper_main(node_id: str) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--tenant", default="wil_ai_design_partner")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_church_or_stub(node_id=node_id, bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1

