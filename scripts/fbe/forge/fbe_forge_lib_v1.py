"""FBE forge lib — FORGE app scaffold delegates, forge-bay receipts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
INBOX_PATH = SINA / "worker-prompt-inbox-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def refinery_dir(bay_slug: str) -> Path:
    return ROOT / "receipts" / "bays" / bay_slug / "refinery"


def assembly_dir(bay_slug: str) -> Path:
    return ROOT / "receipts" / "bays" / bay_slug / "assembly"


def receipt_path(bay_slug: str, node_id: str, *, line: str = "refinery") -> Path:
    base = refinery_dir(bay_slug) if line == "refinery" else assembly_dir(bay_slug)
    safe = node_id.replace("/", "_")
    return base / f"{safe}-v1.json"


def ledger_path(bay_slug: str, *, line: str = "refinery") -> Path:
    base = refinery_dir(bay_slug) if line == "refinery" else assembly_dir(bay_slug)
    return base / "ledger.jsonl"


def trace_dir(bay_slug: str) -> Path:
    return ROOT / "receipts" / "bays" / bay_slug / "trace"


def trace_file(bay_slug: str, kind: str) -> Path:
    name = "cost.jsonl" if kind == "cost" else "eval.jsonl"
    return trace_dir(bay_slug) / name


def append_trace(bay_slug: str, kind: str, row: dict[str, Any]) -> None:
    p = trace_file(bay_slug, kind)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = {"at": now_utc(), **row}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, separators=(",", ":")) + "\n")


def append_ledger(bay_slug: str, row: dict, *, line: str = "refinery") -> None:
    p = ledger_path(bay_slug, line=line)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def write_receipt(bay_slug: str, node_id: str, row: dict, *, line: str = "refinery") -> Path:
    p = receipt_path(bay_slug, node_id, line=line)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return p


def read_inbox_head() -> dict[str, Any]:
    if INBOX_PATH.is_file():
        try:
            data = json.loads(INBOX_PATH.read_text(encoding="utf-8"))
            head = (data.get("queue") or data.get("items") or [])
            if isinstance(head, list) and head:
                first = head[0] if isinstance(head[0], dict) else {"raw": str(head[0])[:200]}
            else:
                first = {"sa_id": data.get("bound_sa") or data.get("sa_id")}
            return {"ok": True, "path": str(INBOX_PATH), "head": first}
        except (OSError, json.JSONDecodeError) as exc:
            return {"ok": True, "path": str(INBOX_PATH), "head": {"note": "inbox file present"}, "parse_error": str(exc)}
    if INBOX_MD.is_file():
        try:
            head_line = INBOX_MD.read_text(encoding="utf-8").splitlines()[0][:200]
        except OSError:
            head_line = ""
        return {"ok": True, "path": str(INBOX_MD), "head": {"inbox_md": head_line}, "mode": "inbox_md_fallback"}
    return {"ok": False, "error": "inbox missing", "path": str(INBOX_PATH)}


def run_stub_step(
    *,
    node_id: str,
    bay_slug: str,
    tenant: str,
    line: str,
    mode: str,
    extra: dict | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema": "fbe-forge-step-receipt-v1",
        "ok": True,
        "at": now_utc(),
        "node_id": node_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "line": line,
        "mode": mode,
        "deliveryMode": "prove_only",
        "factory": "forge-app-factory-v1",
        "proof_class": "G0-G3",
    }
    if extra:
        row.update(extra)
    write_receipt(bay_slug, node_id, row, line=line)
    append_ledger(
        bay_slug,
        {"at": row["at"], "node_id": node_id, "ok": True, "line": line, "mode": mode},
        line=line,
    )
    return row


def wrapper_main(fn) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="forge-bay")
    ap.add_argument("--tenant", default="forge")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = fn(bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1
