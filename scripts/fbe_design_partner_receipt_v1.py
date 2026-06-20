#!/usr/bin/env python3
"""FBE design partner receipt pack — buyer ZIP for Wil AI + TrustField."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _proof_for_tenant(*, tenant: str, job: dict) -> dict:
    if tenant == "trustfield":
        exchange_v = _read_json(SINA / "fbe-exchange-verify-receipt-v1.json")
        return {
            "proof_source": "exchange_verify",
            "tier_achieved": job.get("tier_achieved") or exchange_v.get("tier_achieved"),
            "exchange_proof": exchange_v.get("proof"),
            "market_ready_proof": None,
            "assembly_proof": None,
        }
    market = _read_json(SINA / "fbe-market-ready-verify-receipt-v1.json")
    assembly_v = _read_json(SINA / "fbe-assembly-verify-receipt-v1.json")
    return {
        "proof_source": "market_ready_assembly",
        "tier_achieved": job.get("tier_achieved") or market.get("tier_achieved"),
        "market_ready_proof": market.get("proof"),
        "assembly_proof": assembly_v.get("proof"),
        "exchange_proof": None,
    }


def build_partner_pack(*, tenant: str = "trustfield", bay_slug: str = "trustfield-bay") -> dict:
    pack_dir = ROOT / "receipts" / "partners" / tenant
    pack_dir.mkdir(parents=True, exist_ok=True)
    zip_path = pack_dir / "design-partner-receipt-v1.zip"
    manifest: list[dict] = []

    job = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    billing = _read_json(SINA / "fbe-billing-meter-receipt-v1.json")
    proof = _proof_for_tenant(tenant=tenant, job=job)

    summary = {
        "schema": "fbe-design-partner-summary-v1",
        "at": _now(),
        "tenant": tenant,
        "bay_slug": bay_slug,
        "template_id": job.get("template_id") or ("exchange-factory-v1" if tenant == "trustfield" else "web-product-factory-v1"),
        "tier_achieved": proof.get("tier_achieved"),
        "billing_total_usd": billing.get("total_usd"),
        "proof_source": proof.get("proof_source"),
        "market_ready_proof": proof.get("market_ready_proof"),
        "assembly_proof": proof.get("assembly_proof"),
        "exchange_proof": proof.get("exchange_proof"),
        "deliveryMode": "prove_only",
    }
    summary_path = pack_dir / "partner-summary-v1.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    candidates = [
        summary_path,
        ROOT / "receipts" / "federated-run-v1.json",
        SINA / "fbe-federated-receipt-v1.json",
        SINA / "fbe-run-job-receipt-v1.json",
        SINA / "fbe-billing-meter-receipt-v1.json",
        ROOT / "receipts" / "tenant-isolation-v1.json",
        ROOT / "receipts" / "packs" / bay_slug / "run-receipt-v1.zip",
    ]
    if tenant == "trustfield":
        candidates.append(SINA / "fbe-exchange-verify-receipt-v1.json")
    else:
        candidates.extend([
            SINA / "fbe-market-ready-verify-receipt-v1.json",
            SINA / "fbe-assembly-verify-receipt-v1.json",
            SINA / "fbe-assembly-run-receipt-v1.json",
        ])

    bay = ROOT / "receipts" / "bays" / bay_slug
    if bay.is_dir():
        for p in bay.rglob("*.json"):
            candidates.append(p)
        for p in bay.rglob("*.jsonl"):
            candidates.append(p)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        seen: set[str] = set()
        for path in candidates:
            if not path.is_file():
                continue
            try:
                arc = str(path.relative_to(ROOT))
            except ValueError:
                arc = path.name
            if arc in seen:
                continue
            seen.add(arc)
            zf.write(path, arcname=arc)
            manifest.append({"path": arc, "sha256": _sha256_file(path)})
        zf.writestr(
            "partner-manifest-v1.json",
            json.dumps({"schema": "fbe-partner-manifest-v1", "at": _now(), "files": manifest}, indent=2),
        )

    row = {
        "schema": "fbe-design-partner-receipt-v1",
        "ok": True,
        "at": _now(),
        "tenant": tenant,
        "bay_slug": bay_slug,
        "artifact_uri": str(zip_path.relative_to(ROOT)),
        "receipt_pack_uri": str(zip_path.relative_to(ROOT)),
        "file_count": len(manifest),
        "summary": summary,
    }
    (pack_dir / "pack-receipt-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", default="trustfield")
    ap.add_argument("--bay", default="trustfield-bay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = build_partner_pack(tenant=args.tenant, bay_slug=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
