#!/usr/bin/env python3
"""HMAC-chained receipt audit — TrustField tamper detection (MACHINE_LOOPS §5)."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF_DIR = ROOT / "receipts" / "proof"
CHAIN_STATE = PROOF_DIR / "receipt-chain-state-v1.json"
RECEIPT = PROOF_DIR / "receipt-chain-audit-latest-v1.json"
CANON_VERSION = "FOUNDER_CANON_v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hmac_key() -> bytes:
    env = os.environ.get("RECEIPT_CHAIN_HMAC_KEY", "").strip()
    if env:
        return env.encode()
    secret = Path.home() / ".sourcea-secrets" / "receipt-chain-hmac.key"
    if secret.is_file():
        return secret.read_text(encoding="utf-8").strip().encode()
    # Dev fallback — deterministic per repo; production should set RECEIPT_CHAIN_HMAC_KEY
    seed = hashlib.sha256(str(ROOT).encode()).hexdigest()
    return f"sourcea-receipt-chain-dev:{seed[:32]}".encode()


def _canonical(row: dict[str, Any]) -> bytes:
    return json.dumps(row, sort_keys=True, separators=(",", ":")).encode()


def _link_hash(prev: str, body_hash: str, at: str) -> str:
    msg = f"{prev}|{body_hash}|{at}".encode()
    return hmac.new(_hmac_key(), msg, hashlib.sha256).hexdigest()


def audit(*, write_state: bool = True) -> dict[str, Any]:
    state = {}
    if CHAIN_STATE.is_file():
        try:
            state = json.loads(CHAIN_STATE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            state = {}

    links: dict[str, str] = state.get("links") if isinstance(state.get("links"), dict) else {}
    prev_global = str(state.get("head") or "GENESIS")
    broken: list[dict[str, str]] = []
    updated = 0

    files = sorted(PROOF_DIR.glob("*-latest-v1.json"))
    for path in files:
        if path.name == RECEIPT.name:
            continue
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            broken.append({"file": path.name, "reason": "unreadable"})
            continue

        body_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        at = str(row.get("at") or _now())
        expected_prev = links.get(path.name, prev_global if path.name not in links else links.get(path.name))
        stored_link = links.get(f"{path.name}#link")

        if stored_link:
            recomputed = _link_hash(prev_global, body_hash, at)
            if stored_link != recomputed:
                broken.append({"file": path.name, "reason": "hmac_mismatch"})
        else:
            updated += 1

        link = _link_hash(prev_global, body_hash, at)
        links[path.name] = prev_global
        links[f"{path.name}#link"] = link
        links[f"{path.name}#body_hash"] = body_hash
        prev_global = link

    ok = len(broken) == 0
    doc = {
        "schema": "receipt-chain-audit-v1",
        "version": "1.0.0",
        "canon_version": CANON_VERSION,
        "at": _now(),
        "ok": ok,
        "files_audited": len(files),
        "links_updated": updated,
        "broken_links": broken,
        "head": prev_global,
        "report_line": (
            f"receipt_chain PASS · {len(files)} files · head={prev_global[:12]}"
            if ok
            else f"receipt_chain FAIL · {len(broken)} broken links"
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    if write_state:
        CHAIN_STATE.write_text(
            json.dumps(
                {"schema": "receipt-chain-state-v1", "at": _now(), "head": prev_global, "links": links},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = audit()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
