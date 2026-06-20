#!/usr/bin/env python3
"""Publish Card 1 — SourceA Forge Governance Cursor plugin bundle."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "cursor-plugin/sourcea-forge-governance"
PKG = ROOT / "packages/mcp-sourcea-verify"
ARTIFACTS = ROOT / "data/publish-artifacts"
RECEIPT = ROOT / "receipts/card-1-sourcea-forge-governance-publish-v1.json"
PUBLISH_SSOT = ROOT / "data/mcp-chain-publish-receipt-v1.json"

REQUIRED = [
    PLUGIN_ROOT / ".cursor-plugin/plugin.json",
    PLUGIN_ROOT / ".mcp.json",
    PLUGIN_ROOT / "README.md",
    PLUGIN_ROOT / "plugin-v1.json",
    PLUGIN_ROOT / "skills/verify-after-mcp/SKILL.md",
    PLUGIN_ROOT / "skills/governance-receipt-recovery/SKILL.md",
    PLUGIN_ROOT / "rules/receipt-native-governance.mdc",
    PLUGIN_ROOT / "assets/logo.svg",
    PKG / "dist/index.js",
    PKG / "registry/server-v1.json",
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_bundle() -> list[str]:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.is_file()]
    return missing


def npm_pack() -> dict:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["npm", "pack", "--pack-destination", str(ARTIFACTS)],
        cwd=PKG,
        capture_output=True,
        text=True,
    )
    tgz = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.endswith(".tgz"):
            tgz = line
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "tgz": tgz,
        "artifact_path": str(ARTIFACTS / tgz) if tgz else None,
        "stderr": proc.stderr[-500:] if proc.stderr else "",
    }


def tar_plugin_bundle() -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ARTIFACTS / f"sourcea-forge-governance-card1-{stamp}.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        for path in PLUGIN_ROOT.rglob("*"):
            if path.is_file() and ".DS_Store" not in path.name:
                tar.add(path, arcname=str(path.relative_to(PLUGIN_ROOT.parent)))
    return out


def update_publish_ssot(receipt_path: str, plugin_tar: str, npm_info: dict) -> None:
    if not PUBLISH_SSOT.is_file():
        return
    data = json.loads(PUBLISH_SSOT.read_text())
    data["saved_at"] = _utc()
    data["card_1"] = {
        "id": "sourcea-forge-governance",
        "card": 1,
        "status": "bundle_published_disk",
        "plugin_tar": plugin_tar,
        "npm_pack": npm_info.get("artifact_path"),
        "receipt": receipt_path,
        "honest_label": "P1 stdio — Cursor marketplace submit + npm publish remain founder taps",
    }
    data["next_founder_tap"] = (
        "npm publish @sourcea/mcp-verify --access public · "
        "submit cursor-plugin/sourcea-forge-governance to Cursor marketplace · "
        "registry.modelcontextprotocol.io metadata"
    )
    PUBLISH_SSOT.write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish Card 1 — SourceA Forge Governance")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-npm-pack", action="store_true")
    args = parser.parse_args()

    missing = validate_bundle()
    if missing:
        out = {"ok": False, "missing": missing, "saved_at": _utc()}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print("FAIL: missing bundle files:")
            for m in missing:
                print(f"  - {m}")
        sys.exit(1)

    npm_info: dict = {"ok": True, "skipped": True}
    if not args.skip_npm_pack:
        npm_info = npm_pack()

    plugin_tar = tar_plugin_bundle()
    receipt = {
        "schema": "sourcea-forge-governance-card1-publish-v1",
        "card": 1,
        "id": "sourcea-forge-governance",
        "verdict": "PASS",
        "saved_at": _utc(),
        "bundle_root": str(PLUGIN_ROOT.relative_to(ROOT)),
        "artifacts": {
            "plugin_tar": str(plugin_tar.relative_to(ROOT)),
            "npm_pack": npm_info.get("artifact_path"),
        },
        "mcp_package": "@sourcea/mcp-verify",
        "registry_name": "io.github.sinakazemnezhad/sourcea-verify",
        "categories": ["Agent Orchestration", "Infrastructure"],
        "partner_line": "We don't replace your MCP — we prove what your MCP did.",
        "honest_label": "P1 disk bundle ready — MOCK_ONLY stdio tier · cloud SSE P2",
        "next_founder_tap": [
            "npm publish --access public -w packages/mcp-sourcea-verify",
            "Submit cursor-plugin/sourcea-forge-governance via Cursor marketplace",
            "Submit registry/server-v1.json to registry.modelcontextprotocol.io",
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    update_publish_ssot(str(RECEIPT.relative_to(ROOT)), str(plugin_tar.relative_to(ROOT)), npm_info)

    proc = subprocess.run(
        ["bash", "scripts/validate-mcp-chain-motor-v1.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    out = {
        "ok": proc.returncode == 0 and npm_info.get("ok", True),
        "card": 1,
        "saved_at": receipt["saved_at"],
        "plugin_tar": str(plugin_tar.relative_to(ROOT)),
        "npm_pack": npm_info,
        "receipt": str(RECEIPT.relative_to(ROOT)),
        "validate_mcp_chain": proc.returncode == 0,
        "validate_log": proc.stdout.strip(),
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"OK: Card 1 published to disk · {plugin_tar.name}")
        print(f"Receipt: {RECEIPT.relative_to(ROOT)}")
        if npm_info.get("artifact_path"):
            print(f"npm pack: {npm_info['artifact_path']}")
    sys.exit(0 if out["ok"] else 1)


if __name__ == "__main__":
    main()
