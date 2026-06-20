#!/usr/bin/env python3
"""Export structured master orders for Sina Command panel."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
OUT = SOURCE_A / "sina-bowl" / "MASTER_ORDERS.json"

SECTIONS = [
    {
        "id": "S1",
        "title": "Personal Database",
        "items": [
            {"id": "1.1", "text": "Personal DB = SSOT for agent copy/train", "status": "active"},
            {"id": "1.2", "text": "Layered L0–L4, access-controlled", "status": "active"},
            {"id": "1.5", "text": "Sina AI Personal Database — Command on top", "status": "locked"},
        ],
    },
    {
        "id": "S2",
        "title": "Evidence flywheel",
        "items": [
            {"id": "2.1", "text": "MergePack = Evidence Factory (events)", "status": "locked"},
            {"id": "2.2", "text": "KPI trio: pay · referral-pay · organic", "status": "active"},
            {"id": "2.5", "text": "M8 = wire/automation only", "status": "locked"},
        ],
    },
    {
        "id": "S3",
        "title": "MergePack growth vs factory",
        "items": [
            {"id": "3.1", "text": "No-ads = 30-idea scoring only", "status": "locked"},
            {"id": "3.2", "text": "10K blitz + SEO + paid NOT parked", "status": "locked"},
            {"id": "3.3", "text": "Upgrade SSOT when blockers clear", "status": "locked"},
        ],
    },
    {
        "id": "S4",
        "title": "Participation (strategy)",
        "items": [
            {"id": "4.3", "text": "No full Participation OS at 0 users", "status": "locked"},
            {"id": "4.4", "text": "V0 lanes: User · Earner · Connector", "status": "planned"},
            {"id": "4.7", "text": "Hooks now in MergePack", "status": "shipped"},
        ],
    },
    {
        "id": "S5",
        "title": "Command center & bowl",
        "items": [
            {"id": "5.1", "text": "Chic local control panel on laptop", "status": "in_progress"},
            {"id": "5.4", "text": "Daily bowl — unified read", "status": "done"},
            {"id": "5.5", "text": "Earphones morning brief", "status": "done"},
            {"id": "5.6", "text": "Read whole ecosystem, not last line", "status": "process"},
            {"id": "5.10", "text": "Organize all orders (registry)", "status": "done"},
        ],
    },
]

FLYWHEEL = [
    "Traffic",
    "Usage Events",
    "Evidence",
    "Revenue",
    "Trust",
    "Distribution",
    "Participation",
    "TrustField",
    "Noetfield",
]

LAYERS = [
    {"layer": "L1", "sku": "MergePack", "role": "Evidence Factory", "status": "active_parallel"},
    {"layer": "L2", "sku": "RunReceipt", "role": "Monetized events", "status": "factory_p0"},
    {"layer": "L3", "sku": "Participation HQ", "role": "Role system (later)", "status": "hooks_only"},
    {"layer": "L4", "sku": "TrustField", "role": "Governance", "status": "lane_1"},
    {"layer": "L5", "sku": "Noetfield", "role": "Trust analysis", "status": "lane_4"},
]

HQ_SUPERVISION = [
    {"node": "ASF", "kind": "human", "line": "Final law, P0, registry"},
    {"node": "Architect", "kind": "observe", "line": "ARCHITECT_REPORT.yaml"},
    {"node": "Prompt OS", "kind": "dispatch", "line": "5 repo pastes + Lane 0"},
    {"node": "Sina Command", "kind": "observe", "line": "Fleet + bowl + orders"},
    {"node": "Lane 1–5", "kind": "delivery", "line": "TrustField · Mono · VIRLUX · Noetfield · 777"},
    {"node": "Wire", "kind": "automation", "line": "DevBridge M8"},
    {"node": "MergePack", "kind": "utility", "line": "Evidence + growth when ASF activates"},
    {"node": "Runtime PAIOS", "kind": "telegram", "line": ":8000 workers — not Cursor"},
]

HQ_CREATED = [
    "Evidence flywheel + acquisition locks",
    "MergePack v1.3 evidence API",
    "Sina Command + bowl builders",
    "Fleet scanner",
    "Participation hooks spec",
]

PARTICIPATION_LANES_FUTURE = [
    "user", "earner", "connector", "developer", "investor",
    "dropshipping", "airdrop", "shareholder_path", "points_dashboard",
]


def main() -> None:
    payload = {
        "schema_version": 1,
        "doc": "ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md",
        "sections": SECTIONS,
        "flywheel": FLYWHEEL,
        "layers": LAYERS,
        "hq_supervision": HQ_SUPERVISION,
        "hq_created": HQ_CREATED,
        "participation_lanes_future": PARTICIPATION_LANES_FUTURE,
        "equation": "Utilities → Events → Evidence → Revenue → Trust → Distribution → Noetfield",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"OK: {OUT}")


if __name__ == "__main__":
    main()
