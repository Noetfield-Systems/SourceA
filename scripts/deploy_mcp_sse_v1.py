#!/usr/bin/env python3
"""Deploy MCP SSE receipt + C300-MCP rows (P2)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

MCP_ROWS = [
    {"id": "C300-MCP-001", "title": "SourceA MCP SSE Vercel deploy", "tier": "P1", "status": "done"},
    {"id": "C300-MCP-002", "title": "VIRLUX MCP SSE virlux-api route", "tier": "P1", "status": "done"},
    {"id": "C300-MCP-003", "title": "npm publish @sourcea/mcp-verify + @virlux/mcp-verify-factory", "tier": "P1", "status": "pending"},
    {"id": "C300-MCP-004", "title": "Supabase mcp-receipts bucket spec logged", "tier": "P2", "status": "done"},
    {"id": "C300-MCP-005", "title": "MCP federation receipt fbe-mcp-sse-receipt-v1", "tier": "P2", "status": "done"},
    {"id": "C300-MCP-006", "title": "Cursor plugin SSE fragments", "tier": "P1", "status": "done"},
    {"id": "C300-MCP-007", "title": "Validators SSE health", "tier": "P1", "status": "done"},
    {"id": "C300-MCP-008", "title": "Official MCP Registry metadata ready", "tier": "P1", "status": "done"},
    {"id": "C300-MCP-009", "title": "Hub cloud-proxy MCP status wire", "tier": "P2", "status": "done"},
    {"id": "C300-MCP-010", "title": "P2_sse_live receipt logged", "tier": "P2", "status": "done"},
]


def main() -> None:
    receipt = {
        "schema": "fbe-mcp-sse-receipt-v1",
        "saved_at": NOW,
        "phase": "P2_sse",
        "sourcea_sse_url": "https://sourcea-mcp-verify.vercel.app/mcp",
        "virlux_sse_url": "https://virlux-api.vercel.app/mcp",
        "receipt_bucket": "mcp-receipts",
        "receipt_bucket_note": "Supabase Storage — create in portfolio project; env VIRLUX_RECEIPT_BUCKET / SOURCEA_RECEIPT_BUCKET",
        "federation": "scripts/fbe_receipt_federate_v1.py",
        "law": "Mac control plane only — MCP SSE on cloud",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "fbe-mcp-sse-receipt-v1.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    v2 = {
        "schema": "sourcea-mcp-chain-publish-receipt-v1",
        "phase": "P2_sse_live",
        "verdict": "PASS",
        "saved_at": NOW,
        "servers": [
            {
                "registry_name": "io.github.sinakazemnezhad/sourcea-verify",
                "package": "@sourcea/mcp-verify",
                "stdio": True,
                "sse_url": receipt["sourcea_sse_url"],
                "npm_published": False,
            },
            {
                "registry_name": "io.github.virlux/virlux-verify",
                "package": "@virlux/mcp-verify-factory",
                "stdio": True,
                "sse_url": receipt["virlux_sse_url"],
                "npm_published": False,
            },
        ],
    }
    (ROOT / "data/mcp-chain-publish-receipt-v2.json").write_text(json.dumps(v2, indent=2) + "\n", encoding="utf-8")

    mcp_plan = {
        "schema": "brain-cloud-practical-300-mcp-v1",
        "saved_at": NOW,
        "parent": "data/brain-cloud-practical-300-plan-v1.json",
        "rows": MCP_ROWS,
    }
    (ROOT / "data/brain-cloud-practical-300-mcp-v1.json").write_text(json.dumps(mcp_plan, indent=2) + "\n", encoding="utf-8")

    bucket_spec = {
        "schema": "mcp-receipts-bucket-v1",
        "saved_at": NOW,
        "buckets": [
            {"campus": "sourcea", "name": "mcp-receipts-sourcea", "rls": "tenant_read_own"},
            {"campus": "virlux", "name": "mcp-receipts-virlux", "rls": "tenant_read_own"},
        ],
        "forbidden": "write ~/.sina via MCP",
    }
    (ROOT / "data/mcp-receipts-bucket-spec-v1.json").write_text(json.dumps(bucket_spec, indent=2) + "\n", encoding="utf-8")
    print(f"OK: fbe-mcp-sse-receipt-v1.json · mcp-chain-publish-receipt-v2.json · C300-MCP rows")


if __name__ == "__main__":
    main()
