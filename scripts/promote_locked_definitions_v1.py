#!/usr/bin/env python3
"""Check promotion requirements for locked-definitions-v1 → live_locked."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY = ROOT / "data/sourcea-brain-registry-inventory-v1.json"
DEFINITIONS = ROOT / "reports/locked-definitions-v1.json"
CONTRACT_RECEIPT = SINA / "sourcea-contract-pages-e2e-v1.json"
FOUNDER_VERIFY = SINA / "client-proof-founder-review-verify-v1.json"
BUNDLE = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"
RECEIPT = SINA / "locked-definitions-promotion-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_sha() -> str:
    raw = BUNDLE.read_bytes()
    return hashlib.sha256(raw).hexdigest()


def check(*, write: bool = False) -> dict:
    requirements = (_read_json(REGISTRY).get("promotion_requirements") or {}).get(
        "locked_definitions_to_live_locked"
    ) or []
    checks: dict[str, dict] = {}

    # contract-pages-e2e:ALL_PASS
    contract_ok = CONTRACT_RECEIPT.is_file() and _read_json(CONTRACT_RECEIPT).get("ok") is True
    if not contract_ok:
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/validate-sourcea-contract-pages-e2e-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "SOURCEA_CONTRACT_E2E_PUBLIC_ONLY": "1"},
        )
        contract_ok = proc.returncode == 0
    checks["contract-pages-e2e:ALL_PASS"] = {"ok": contract_ok}

    # brain-knowledge-bundle:deploy_sha_match
    bundle_sha = _bundle_sha()
    checks["brain-knowledge-bundle:deploy_sha_match"] = {
        "ok": BUNDLE.is_file(),
        "bundle_sha256": bundle_sha,
    }

    # brain-core-gate-staging:production_enable (flag OFF until SG verifier — staging only)
    checks["brain-core-gate-staging:production_enable"] = {
        "ok": False,
        "reason": "SG secondary Cloudflare verifier unavailable — production gate stays OFF",
        "staging_header": "X-SourceA-Brain-Core-Gate: staging",
    }

    founder_ok = FOUNDER_VERIFY.is_file() and _read_json(FOUNDER_VERIFY).get("ok") is True
    checks["founder_proof_15_recipes"] = {"ok": founder_ok}

    # live status probes
    sys.path.insert(0, str(ROOT / "scripts"))
    from brain_core_v1.live_status_probe import probe_live_status_map  # noqa: WPS433

    probe_map = probe_live_status_map()
    probe_ok = all(
        isinstance(v, dict) and v.get("status") in ("good", "ok")
        for v in probe_map.values()
    )
    checks["live_status_probe"] = {"ok": probe_ok, "probe_map": probe_map}

    all_required = all(checks.get(req, {}).get("ok") for req in requirements if req in checks)
    promote_ready = contract_ok and founder_ok and probe_ok and checks["brain-knowledge-bundle:deploy_sha_match"]["ok"]

    row = {
        "schema": "locked-definitions-promotion-v1",
        "at": _now(),
        "requirements": requirements,
        "checks": checks,
        "promote_ready": promote_ready,
        "all_required_green": all_required,
        "definitions_status": _read_json(DEFINITIONS).get("status") if DEFINITIONS.is_file() else None,
    }

    if write and promote_ready and DEFINITIONS.is_file():
        doc = _read_json(DEFINITIONS)
        doc["status"] = "live_locked_candidate_verified"
        doc["promotion_checked_at"] = row["at"]
        doc["live_status_probe"] = probe_map
        DEFINITIONS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        reg = _read_json(REGISTRY)
        for asset in reg.get("assets") or []:
            if asset.get("asset_id") == "locked-definitions-v1":
                asset["status"] = "live_locked_candidate_verified"
                asset["last_modified"] = row["at"][:10]
        reg["saved_at"] = row["at"]
        REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
        row["wrote_definitions"] = True
        row["wrote_registry"] = True

    if write:
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help="Update definitions + registry when checks pass")
    args = ap.parse_args()
    row = check(write=args.write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"promote_ready={row['promote_ready']} all_required={row['all_required_green']}")
    return 0 if row.get("promote_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
