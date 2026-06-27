"""FBE receipt helpers — read, write, federate paths."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def expand_path(rel: str) -> Path:
    p = Path(rel.replace("~", str(Path.home())))
    return p if p.is_absolute() else ROOT / p


def read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_dict(row: dict) -> str:
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


MOTOR_RECEIPT_PATHS: list[tuple[str, str]] = [
    ("session_gate", "~/.sina/agent-session-gate-receipt-v1.json"),
    ("sascip", "~/.sina/stranger-agent-safety-live-wire-v1.json"),
    ("zero_drift", "~/.sina/governance-zero-drift-live-wire-v1.json"),
    ("disk_live_wire", "~/.sina/disk-live-wire-receipt-v1.json"),
    ("vocabulary", "~/.sina/vocabulary-guard-v1.json"),
    ("tenant_isolation", "receipts/tenant-isolation-v1.json"),
    ("motor_registry", "~/.sina/fbe-motor-registry-v1.json"),
    ("motor_delegate", "~/.sina/fbe-motor-delegate-receipt-v1.json"),
    ("compile", "~/.sina/fbe-compile-receipt-v1.json"),
    ("factory_registry", "~/.sina/fbe-factory-registry-v1.json"),
    ("cloud_adapter", "~/.sina/fbe-cloud-adapter-receipt-v1.json"),
]


def collect_motor_receipts() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for key, rel in MOTOR_RECEIPT_PATHS:
        p = expand_path(rel)
        row = read_json(p)
        rows[key] = {
            "path": str(p),
            "exists": p.is_file(),
            "ok": bool(row.get("ok", p.is_file())),
            "schema": row.get("schema"),
            "sha256": sha256_file(p) if p.is_file() else "",
            "body": row if row else None,
        }
    return rows
