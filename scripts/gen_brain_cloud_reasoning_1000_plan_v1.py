#!/usr/bin/env python3
"""Generate Brain cloud-reasoning 1000 upgrade plan SSOT.

Law: Mac = control plane · Brain = reasoning · Cloud/API = execution
Replaces: local Cursor Worker as primary factory execution (graduated deprecation)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"

EPICS = [
    {
        "id": "E01",
        "label": "Brain reasoning core",
        "range": (1, 100),
        "lane": "brain_reasoning",
        "tier_default": "P0",
        "templates": [
            "Brain reads {artifact} before routing — never chat summary as SSOT",
            "Reconcile {surface} vs {surface2} — emit YAML pick not prose",
            "Reason about consequence of {action} on cloud execution plane",
            "Brain refuses Worker-scope implementation in Brain chat",
            "Brain maps founder intent to work-order spec for cloud worker",
            "Brain validates {gate} meaning not just PASS/FAIL theater",
            "Brain cites disk path FOUND/NOT FOUND every strategic turn",
            "Brain dual-mode: narrator default · executor only on signed work-order",
            "Brain reads execution_core.digest.yaml not raw research registry",
            "Brain routes portfolio lane {lane} without merging execution authority",
        ],
        "artifacts": [
            "factory-now-v1.json",
            "agent-live-surfaces-v1.json",
            "execution_core.digest.yaml",
            "fbe_factory_builder_bundle_v1.json",
            "brain-cloud-reasoning-1000-upgrade-plan-v1.json",
            "next-execution-pointer-v1.json",
            "governance-gate-cart-v1.json",
            "research-root/filtered/",
            "loop-specialist-cloud-contract-v1.json",
            "authority.yaml",
        ],
        "surfaces": [
            ("factory-now", "inbox"),
            ("cloud work-order", "local INBOX"),
            ("Brain pick", "Worker paste"),
            ("federated receipt", "chat claim"),
            ("reasoning receipt", "validator green"),
        ],
        "gates": [
            "session_gate",
            "SASCIP",
            "zero_drift",
            "execution_honesty",
            "governance_center",
        ],
        "lanes": ["trustfield", "noetfield", "creed", "church", "wil_ai", "ya5"],
    },
    {
        "id": "E02",
        "label": "Two-plane migration law",
        "range": (101, 200),
        "lane": "control_plane",
        "tier_default": "P0",
        "templates": [
            "Document invariant: {invariant} stays Mac-only",
            "Forbid {forbidden} on cloud execution workers",
            "Migrate {local_job} from Cursor Worker to cloud work-order",
            "Hub Action spawns cloud job — not Terminal · not RUN INBOX",
            "Signed work-order schema v1 for {factory_line}",
            "Federate cloud receipt to ~/.sina/fbe-runs/",
            "Mac freeze applies to spawn not bay execution",
            "Queue sa-* remains Mac SSOT during cloud migration wave {n}",
            "Deprecate instruction path: {old_path}",
            "Control plane API: {endpoint}",
        ],
        "invariants": [
            "factory-now queue_sa",
            "session gate receipts",
            "founder veto",
            "SASCIP admission",
            "law edits",
        ],
        "forbidden": [
            "chat SSOT",
            "cross-tenant writes",
            "law edits on cloud",
            "founder Terminal routine",
            "RUN INBOX as cloud substitute",
        ],
        "local_jobs": [
            "outbound ICP compile",
            "OQG lint batch",
            "refinery mirror job",
            "assembly brand pass",
            "commercial mail draft",
            "research_root_sync",
            "loop specialist tick",
            "disk heal chain",
            "validator fan-out",
            "portfolio site build",
        ],
        "factory_lines": ["trust_motor", "refinery", "assembly"],
        "endpoints": [
            "POST /api/fbe/spawn/v1",
            "POST /api/cloud-worker/dispatch/v1",
            "GET /api/fbe/runs/v1",
            "POST /api/loop-specialist/tick/v1",
            "GET /api/brain/work-order/v1",
        ],
    },
    {
        "id": "E03",
        "label": "Cloudflare Workers free tier",
        "range": (201, 300),
        "lane": "cf_workers",
        "tier_default": "P1",
        "templates": [
            "CF Worker cron {cron} calls Hub {api} headless",
            "CF Worker bay runner stub for FBE node {node_id}",
            "R2-free mirror read for pattern {pattern}",
            "KV cache for work-order status {status_key}",
            "Durable Object receipt append for run {run_id}",
            "Wrangler deploy hobby project {project}",
            "CF Worker prove gate {gate} before artifact write",
            "Edge dispatch Trust Motor check pre-job",
            "CF cron phase 2b item {n} from loop-specialist contract",
            "CF Worker federation POST to Mac Hub ingest",
        ],
    },
    {
        "id": "E04",
        "label": "API workers free tier",
        "range": (301, 400),
        "lane": "api_workers",
        "tier_default": "P1",
        "templates": [
            "OpenRouter API worker route {model} for Brain compare lane",
            "GitHub Actions workflow dispatches cloud factory job {job}",
            "Vercel serverless function proxy Hub {path}",
            "Supabase edge function read-only proof {table}",
            "Railway hobby cron NOT production until ROI receipt",
            "Linear webhook triggers Brain reasoning receipt",
            "Notion API capture → research brief handoff only",
            "Anthropic API tool-use worker for work-order draft",
            "MCP {server} assists Brain — never writes ~/.sina/",
            "API worker auth via disclosure ladder tier {tier}",
        ],
        "models": ["claude-sonnet", "gpt-4o-mini", "gemini-flash", "deepseek"],
        "servers": ["github", "linear", "supabase", "notion", "browser"],
    },
    {
        "id": "E05",
        "label": "FBE campus spawn + federation",
        "range": (401, 500),
        "lane": "fbe_campus",
        "tier_default": "P1",
        "templates": [
            "FBE compile node {node_id} from CREED mesh",
            "FBE spawn Factory {n} registry row only W{n}",
            "Line A refinery bay {bay} cloud headless",
            "Line B assembly stage {stage} cloud headless",
            "Line C trust motor gate {gate} pre-spawn",
            "RunReceipt ZIP federate to Mac Hub",
            "FBE graph receipt cross-ref sa-{sa}",
            "Campus tenant {tenant} isolation proof",
            "Pattern import read-only from PLUS ONE/{campus}",
            "FBE W{wave} graduation validator",
        ],
    },
    {
        "id": "E06",
        "label": "Brain work-order compiler",
        "range": (501, 600),
        "lane": "work_order",
        "tier_default": "P0",
        "templates": [
            "Replace INBOX paste with work-order JSON schema field {field}",
            "Brain emits work-order for upgrade {upgrade_id}",
            "Cloud worker consumes work-order not chat prompt",
            "Broker acknowledges federated receipt not local turn",
            "Brain reconciles outbound U{id} to cloud job id",
            "Reasoning receipt ~/.sina/brain-reasoning-receipt-{id}.json",
            "Brain pick points to cloud dispatch not Worker chat",
            "Deprecate healthy-drain-orchestrator local path step {n}",
            "Work-order signing via session gate receipt",
            "Brain SMART analysis block in work-order metadata",
        ],
    },
    {
        "id": "E07",
        "label": "Research → Brain reasoning",
        "range": (601, 700),
        "lane": "research_brain",
        "tier_default": "P1",
        "templates": [
            "L1 brief {topic} triggers Brain consequence analysis",
            "L2 sync digest feeds Brain pick not Worker",
            "Brain reads filtered {digest} only",
            "Research acquisitor output → Brain work-order draft",
            "Orientation O-station for Brain cloud pivot §{n}",
            "Brain explains cloud migration impact on {lane}",
            "UNIFIED_RESEARCH_ROOT row {row} Brain reconcile",
            "Goal specialist YAML → Brain route only",
            "Brain forbids research lane execution authority",
            "Research ingest cloud worker read-only adjunct",
        ],
        "digests": [
            "execution_core.digest.yaml",
            "governance.constraints.yaml",
            "commercial.signal.yaml",
            "research.backlog.yaml",
        ],
    },
    {
        "id": "E08",
        "label": "MCP + cloud leverage",
        "range": (701, 800),
        "lane": "mcp_cloud",
        "tier_default": "P2",
        "templates": [
            "MCP {tool} routes Brain to cloud worker spec",
            "Free-tier MCP exhaust before paid API",
            "Brain uses browser MCP verify cloud artifact URL",
            "GitHub MCP opens PR for cloud worker code",
            "Disclosure T{tier} for MCP mention in outbound",
            "MCP stack line on Brain live surfaces",
            "Brain never MCP-write session gate receipt",
            "Linear MCP mirror cloud job status",
            "Supabase MCP proof query federated receipt",
            "MCP assist work-order compile not INBOX",
        ],
    },
    {
        "id": "E09",
        "label": "Portfolio factory cloud bays",
        "range": (801, 900),
        "lane": "portfolio_cloud",
        "tier_default": "P1",
        "templates": [
            "TrustField outbound compile cloud bay {bay}",
            "Noetfield ICP compile cloud worker",
            "CREED refinery node {node} headless cloud",
            "CHURCH assembly node {node} headless cloud",
            "Wil AI skin deploy Vercel Gate K only",
            "YA5 campus spawn read-only pattern feed",
            "Portfolio lane {lane} Mac control cloud exec",
            "Commercial W3 Sina read stays founder Mac",
            "Factory email translation cloud lint worker",
            "OQG score cloud batch federate receipt",
        ],
    },
    {
        "id": "E10",
        "label": "Graduate off local Cursor Worker",
        "range": (901, 1000),
        "lane": "graduate_local",
        "tier_default": "P0",
        "templates": [
            "Mark local Cursor Worker path {path} deprecated",
            "Cloud worker assumes upgrade {uid} execution",
            "Brain announces migration wave {wave} to founder",
            "Local INBOX pending blocked when cloud work-order active",
            "Validator proves cloud receipt for sa-{sa}",
            "Loop auto dispatches cloud not Mac Worker chat",
            "Hub founder motion: glance receipts not RUN INBOX",
            "Execution honesty counts cloud federated turns",
            "Brain BLOCKER receipt when reasoning skipped",
            "1000-plan row B{id} acceptance cloud proof",
        ],
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fill(template: str, epic: dict, i: int) -> str:
    subs = {
        "n": str(i),
        "id": f"B{i:04d}",
        "wave": epic["id"],
    }
    for key in (
        "artifacts",
        "gates",
        "lanes",
        "invariants",
        "forbidden",
        "local_jobs",
        "factory_lines",
        "endpoints",
        "models",
        "servers",
        "digests",
    ):
        arr = epic.get(key) or []
        if arr and "{" + key[:-1] + "}" in template:
            subs[key[:-1]] = arr[i % len(arr)]
        elif arr:
            for placeholder in ("artifact", "gate", "lane", "invariant", "forbidden", "local_job", "factory_line", "endpoint", "model", "server", "digest", "node_id", "api", "path", "field", "upgrade_id", "uid", "sa", "topic", "row", "tool", "tier", "bay", "node", "tenant", "campus", "project", "cron", "status_key", "run_id", "pattern", "job", "table", "old_path", "action", "surface", "surface2"):
                if "{" + placeholder + "}" in template:
                    pool = arr if key != "surfaces" else []
                    if placeholder in ("surface", "surface2") and epic.get("surfaces"):
                        pair = epic["surfaces"][i % len(epic["surfaces"])]
                        subs["surface"], subs["surface2"] = pair[0], pair[1]
                    elif pool:
                        subs[placeholder] = pool[i % len(pool)]
    # surfaces special
    if epic.get("surfaces") and "{surface}" in template:
        pair = epic["surfaces"][i % len(epic["surfaces"])]
        subs["surface"], subs["surface2"] = pair[0], pair[1]
    for k, v in list(subs.items()):
        template = template.replace("{" + k + "}", str(v))
    # strip unfilled placeholders simply
    while "{" in template and "}" in template:
        start = template.find("{")
        end = template.find("}", start)
        if end == -1:
            break
        template = template[:start] + "cloud-factory" + template[end + 1 :]
    return template


def _tier(epic: dict, i: int) -> str:
    base = epic.get("tier_default", "P1")
    if i % 17 == 0:
        return "P2"
    if base == "P0" and i % 11 == 0:
        return "P1"
    return base


def generate() -> dict:
    plans: list[dict] = []
    waves = []
    for epic in EPICS:
        start, end = epic["range"]
        ids = []
        templates = epic["templates"]
        for n in range(start, end + 1):
            title = _fill(templates[(n - start) % len(templates)], epic, n)
            bid = f"B{n:04d}"
            ids.append(bid)
            plans.append(
                {
                    "id": bid,
                    "epic": epic["id"],
                    "epic_label": epic["label"],
                    "tier": _tier(epic, n),
                    "lane": epic["lane"],
                    "lane_label": epic["label"],
                    "title": title,
                    "owner_role": "brain",
                    "execution_plane": "cloud_api_worker",
                    "control_plane": "mac_hub",
                    "wired_to": f"brain-os/lanes/GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md · docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md",
                    "acceptance": "Brain reasoning receipt + cloud federated proof — not local Cursor Worker turn",
                    "status": "planned",
                    "local_worker_deprecated": n >= 901,
                    "parent_spec": "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
                    "human_doc": "docs/SOURCEA_BRAIN_CLOUD_REASONING_1000_PLAN_LOCKED_v1.md",
                }
            )
        waves.append(
            {
                "id": epic["id"],
                "label": epic["label"],
                "plan_ids": ids,
                "range": f"B{start:04d}-B{end:04d}",
                "count": len(ids),
                "status": "pending",
                "brain_blocker": epic["id"] in ("E01", "E02", "E06", "E10"),
            }
        )

    assert len(plans) == 1000

    p0 = sum(1 for p in plans if p["tier"] == "P0")
    p1 = sum(1 for p in plans if p["tier"] == "P1")
    p2 = sum(1 for p in plans if p["tier"] == "P2")

    return {
        "schema": "brain-cloud-reasoning-1000-upgrade-plan-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "law": "Brain reasons · Mac controls · Cloud/API workers execute · local Cursor Worker graduates to control-plane only",
        "strategic_pivot": {
            "from": "local Cursor Worker INBOX as primary factory execution",
            "to": "free-tier cloud + API workers under Brain-signed work-orders",
            "real_blocker": "brain_reasoning_not_worker_inbox",
            "consequence": "Reading stale INBOX/U029 without reasoning blocks the cloud migration",
        },
        "authority": "brain-os/system/EXECUTION_AUTHORITY_MAP_LOCKED_v1.md",
        "fbe_parent": "docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md",
        "cloud_contract": "data/loop-specialist-cloud-contract-v1.json",
        "mcp_ssot": "data/mcp-stack-free-tier-v1.json",
        "pulse_script": "scripts/brain_cloud_reasoning_plan_pulse_v1.py",
        "generator": "scripts/gen_brain_cloud_reasoning_1000_plan_v1.py",
        "critical_path": [
            "B0001",
            "B0101",
            "B0501",
            "B0601",
            "B0901",
            "B1000",
        ],
        "tier_counts": {"P0": p0, "P1": p1, "P2": p2},
        "epics": [{"id": w["id"], "label": w["label"], "count": w["count"]} for w in waves],
        "progress": {
            "total": 1000,
            "done": 0,
            "planned": 1000,
            "cloud_proven": 0,
            "brain_reasoning_proven": 0,
            "local_worker_turns_deprecated": 0,
        },
        "waves": waves,
        "upgrades": plans,
    }


def main() -> int:
    doc = generate()
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {OUT} upgrades={len(doc['upgrades'])} P0={doc['tier_counts']['P0']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
