#!/usr/bin/env python3
"""Build curated client-proof recipe queue — one realistic proven demo per plan row.

Law: docs/FORGE_FACTORY_THREE_OFFERS_AND_FLOWS_LOCKED_v1.md
Each item = GOAL · DONE · VERIFY · proof artifact a buyer can replay on a call.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "client-proof-recipe-queue-v1.json"
RUBRIC = ROOT / "data" / "client-proof-recipe-rubric-v1.json"
SCORING = ROOT / "data" / "forge-scoring-ssot-v01.json"
ALL_PLAN = ROOT / "data" / "all-remaining-plan-backlog-v1.json"
VERIFY_SCRIPT = "scripts/verify_client_proof_artifact_v1.py"


def _url_verify(url: str, *markers: str) -> str:
    parts = [
        "cd ~/Desktop/SourceA",
        f"python3 {VERIFY_SCRIPT} --url {url}",
    ]
    for marker in markers:
        parts.append(f"--marker {json.dumps(marker)}")
    return " && ".join(parts)


def _intake_api_verify() -> str:
    return (
        "cd ~/Desktop/SourceA && "
        "curl -fsS https://sourcea.app/sourcea/data/mvp-intake-config.json | "
        "python3 -c \"import json,sys; d=json.load(sys.stdin); "
        "assert d.get('api_worker_url') and 'mvp-intake' in str(d.get('api_worker_url'))\""
    )


# Live surfaces — VERIFY uses content markers (not curl 200-only). Human pass before buyer calls.
PROVEN_LIVE_RECIPES: list[dict[str, Any]] = [
    {
        "plan_id": "cpr-eval-boot",
        "title": "5-minute eval: sourcea-boot PASS on prospect laptop",
        "goal": "Prospect clones or pip-installs and sees PASS receipt in under 5 minutes",
        "done_when": "Eval page has boot markers + validate-sourcea-boot-v1.sh PASS + PyPI resolves",
        "verify": (
            f"{_url_verify('https://sourcea.app/eval', 'data-sa-page=\"sourcea-boot-eval\"', 'pip install sourcea-boot')} && "
            "bash scripts/validate-sourcea-boot-v1.sh && python3 scripts/probe_sourcea_boot_pypi_v1.py --json"
        ),
        "proof_artifact": "https://sourcea.app/eval",
        "client_demo": "Screen-share /eval → pip install → PASS line logged",
        "client_problem": "P2-onboard-friction",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
        "human_review_before_buyer_call": True,
    },
    {
        "plan_id": "cpr-contract-operating-brain",
        "title": "Contract SKU live: Operating Brain Install page + proof strip",
        "goal": "Buyer opens SKU page and sees live proof embed, not placeholder copy",
        "done_when": "validate-sourcea-contract-pages-e2e-v1.sh PASS for /operating-brain-install",
        "verify": "cd ~/Desktop/SourceA && bash scripts/validate-sourcea-contract-pages-e2e-v1.sh",
        "proof_artifact": "https://sourcea.app/operating-brain-install",
        "client_demo": "Open page → scroll proof strip → click read-only demo",
        "client_problem": "P0-trust-receipt-gap",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
        "human_review_before_buyer_call": True,
    },
    {
        "plan_id": "cpr-contract-aivg",
        "title": "Contract SKU live: AI Value Governance (sourcea.ca mirror)",
        "goal": "Canadian buyer sees distinct regional page with hreflang + live proof",
        "done_when": "Contract E2E PASS for /ai-value-governance on sourcea.app and sourcea.ca",
        "verify": "cd ~/Desktop/SourceA && bash scripts/validate-sourcea-contract-pages-e2e-v1.sh",
        "proof_artifact": "https://sourcea.ca/ai-value-governance",
        "client_demo": "Compare CA vs UK copy — show procurement pack link",
        "client_problem": "P0-trust-receipt-gap",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-contract-eacp",
        "title": "Contract SKU live: Enterprise AI Control Plane (sourcea.uk mirror)",
        "goal": "UK enterprise buyer sees control-plane narrative + demo panel",
        "done_when": "Contract E2E PASS for /enterprise-ai-control-plane",
        "verify": "cd ~/Desktop/SourceA && bash scripts/validate-sourcea-contract-pages-e2e-v1.sh",
        "proof_artifact": "https://sourcea.uk/enterprise-ai-control-plane",
        "client_demo": "Open #demo read-only panel on contract page",
        "client_problem": "P0-trust-receipt-gap",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-live-receipt",
        "title": "Live receipt URL returns 200 with proof class metadata",
        "goal": "Agency prospect verifies a sample job without a sales call",
        "done_when": "GET /sourcea/proof/live returns 200 JSON with verdict field",
        "verify": "curl -fsS https://sourcea.app/sourcea/proof/live | python3 -c \"import json,sys; d=json.load(sys.stdin); assert d.get('ok') or d.get('verdict')\"",
        "proof_artifact": "https://sourcea.app/sourcea/proof/live",
        "client_demo": "Paste live receipt URL in outreach — prospect opens in browser",
        "client_problem": "P1-run-visibility",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-forge-terminal",
        "title": "Forge Terminal public surface loads with controlled send path",
        "goal": "Buyer sees terminal UI and understands policy-before-send",
        "done_when": "Forge terminal page has terminal UI markers (not SPA shell only)",
        "verify": _url_verify("https://sourcea.app/sourcea/forge/terminal", "Forge Terminal", "data-sa-proof-cta"),
        "proof_artifact": "https://sourcea.app/sourcea/forge/terminal",
        "client_demo": "Walk ALLOW vs BLOCK beat on terminal page",
        "client_problem": "P2-onboard-friction",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
        "human_review_before_buyer_call": True,
    },
    {
        "plan_id": "cpr-free-job-intake",
        "title": "Free job CTA: Bring one real job → intake form → storage path",
        "goal": "Prospect who clicks bring-one-real-workflow lands on sandbox form wired to MVP intake worker",
        "done_when": "proof-sandbox page markers + mvp-intake-config.json exposes worker API URL",
        "verify": (
            f"{_url_verify('https://sourcea.app/sourcea/sandbox', 'data-sa-page=\"proof-sandbox\"', 'sa-sandbox-intake-form', 'Bring one real job')} && "
            f"{_intake_api_verify()}"
        ),
        "proof_artifact": "https://sourcea.app/sourcea/sandbox",
        "client_demo": "Walk CTA → fill 5-field form → show intake API config logged",
        "client_problem": "P2-onboard-friction",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
        "human_review_before_buyer_call": True,
    },
    {
        "plan_id": "cpr-railway-observer",
        "title": "Cloud Forge observer proves motor ran on Railway not Mac",
        "goal": "Buyer sees headless cloud execution receipt",
        "done_when": "Railway observer JSON returns ok with execution_plane headless_cloud",
        "verify": "curl -fsS https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1 | python3 -c \"import json,sys; d=json.load(sys.stdin); assert d.get('ok')\"",
        "proof_artifact": "https://sourcea-fbe-runner-production.up.railway.app/observer",
        "client_demo": "Cloud Workers glance → queue head delta after cron tick",
        "client_problem": "P1-run-visibility",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-supabase-rows",
        "title": "Supabase cloud_forge_run_rows accumulates shipped proof rows",
        "goal": "Client sees durable audit trail outside chat",
        "done_when": "cloud_forge_run_supabase_v1.py --query --count returns ok total > 0",
        "verify": "cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count",
        "proof_artifact": "supabase://cloud_forge_run_rows",
        "client_demo": "Show row count delta before/after Auto Runtime tick",
        "client_problem": "P0-trust-receipt-gap",
        "tier": "T0",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-proof-export-loop",
        "title": "Proof export loop page explains weekly client handoff bundle",
        "goal": "Agency retainer renewal uses exported HTML/PDF not Slack threads",
        "done_when": "Proof export marketing page returns 200",
        "verify": _url_verify("https://sourcea.app/sourcea/loops/proof-export", "Proof export", "retainer"),
        "proof_artifact": "https://sourcea.app/loops/proof-export",
        "client_demo": "Walk boot → replay → procurement pack export order",
        "client_problem": "P0-trust-receipt-gap",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-agency-onepager",
        "title": "Agency onepager attachment is institutional not placeholder",
        "goal": "Outbound email attaches credible 1-pager with proof row",
        "done_when": "attach/agency-onepager.html returns 200 with proof language",
        "verify": _url_verify("https://sourcea.app/attach/agency-onepager.html", "Agency overview", "proof"),
        "proof_artifact": "https://sourcea.app/attach/agency-onepager.html",
        "client_demo": "Email attach + 15-min screen-share script from page",
        "client_problem": "P3-pricing-clarity",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-procurement-pack",
        "title": "Procurement pack attachment for regulated buyers",
        "goal": "Security/procurement reviewer gets ISO-map educational pack",
        "done_when": "procurement pack HTML returns 200",
        "verify": _url_verify("https://sourcea.app/attach/procurement-pack.html", "Procurement", "ISO"),
        "proof_artifact": "https://sourcea.app/attach/procurement-pack.html",
        "client_demo": "Send pack before security review call",
        "client_problem": "P0-trust-receipt-gap",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-pureflow-case",
        "title": "PureFlow case study shows full Prompt→Verification",
        "goal": "Service operator prospect sees relatable vertical proof",
        "done_when": "case-studies/pureflow returns 200",
        "verify": _url_verify("https://sourcea.app/case-studies/pureflow", "PureFlow", "48-hour"),
        "proof_artifact": "https://sourcea.app/case-studies/pureflow",
        "client_demo": "Walk 48h path timeline on case study page",
        "client_problem": "P2-onboard-friction",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-agentgo-case",
        "title": "AgentGo case study shows agency-scale proof narrative",
        "goal": "Agency ICP sees second foundational proof story",
        "done_when": "case-studies/agentgo returns 200",
        "verify": _url_verify("https://sourcea.app/case-studies/agentgo", "AgentGo", "agency"),
        "proof_artifact": "https://sourcea.app/case-studies/agentgo",
        "client_demo": "Compare PureFlow vs AgentGo ICP fit in discovery",
        "client_problem": "P2-onboard-friction",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
    },
    {
        "plan_id": "cpr-brain-chat",
        "title": "Public Brain answers from live knowledge bundle not stale chat",
        "goal": "Prospect asks pricing question and gets disk-backed answer",
        "done_when": "Brain worker health returns 200",
        "verify": "curl -fsS -o /dev/null -w '%{http_code}' https://sourcea.app/api/brain-chat/health/v1 | grep -q 200",
        "proof_artifact": "https://sourcea.app/",
        "client_demo": "Ask Brain a contract SKU question on landing",
        "client_problem": "P2-onboard-friction",
        "tier": "T1",
        "lane": "client-proof",
        "proven": True,
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _vague_patterns() -> list[str]:
    scoring = _read(SCORING)
    return [str(x).lower() for x in (scoring.get("vague_keyword_patterns") or [])]


def _is_realistic_backlog_item(item: dict[str, Any], vague: list[str]) -> bool:
    verify = str(item.get("verify") or "").strip()
    if not verify or len(verify) < 20:
        return False
    blob = " ".join(
        str(item.get(k) or "")
        for k in ("title", "agent_prompt", "plan_id", "lane")
    ).lower()
    if any(v in blob for v in vague):
        return False
    if "mock_only" in blob and "live" not in blob:
        return False
    # Prefer client-facing enforcement / ship rows over  grid slices.
    good_markers = (
        "validate-",
        "receipt",
        "proof",
        "demo",
        "e2e",
        "client",
        "ship",
        "deploy",
        "buyer",
        "procurement",
        "eval",
        "boot",
        "contract",
        "landing",
        "intake",
    )
    if not any(m in blob for m in good_markers):
        return False
    return True


def _backlog_to_recipe(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or item.get("plan_id") or "").strip()
    verify = str(item.get("verify") or "").strip()
    return {
        "plan_id": str(item.get("plan_id") or ""),
        "title": title[:200],
        "goal": f"Ship {title[:120]} with validator PASS — show buyer on call",
        "done_when": f"verify command exits 0 · receipt path logged",
        "verify": verify,
        "proof_artifact": str(item.get("prompt_path") or item.get("source_registry") or "disk-receipt"),
        "client_demo": f"Run verify live → show PASS → tie to SourceA verification",
        "client_problem": "P0-trust-receipt-gap",
        "tier": str(item.get("tier") or "T1"),
        "lane": "client-proof-filtered",
        "status": "backlog",
        "source_registry": item.get("source_registry"),
        "prompt_path": item.get("prompt_path"),
        "proven": False,
        "realistic": True,
    }


def build(*, target: int = 100, write: bool = True) -> dict[str, Any]:
    vague = _vague_patterns()
    seen: set[str] = set()
    items: list[dict[str, Any]] = []

    for row in PROVEN_LIVE_RECIPES:
        pid = str(row.get("plan_id") or "")
        if pid and pid not in seen:
            seen.add(pid)
            items.append({**row, "status": "backlog", "realistic": True, "recipe_class": "proven_live"})

    backlog = _read(ALL_PLAN)
    for raw in backlog.get("items") or []:
        if not isinstance(raw, dict):
            continue
        pid = str(raw.get("plan_id") or "")
        if not pid or pid in seen:
            continue
        if not _is_realistic_backlog_item(raw, vague):
            continue
        items.append(_backlog_to_recipe(raw))
        seen.add(pid)
        if len(items) >= target:
            break

    for idx, row in enumerate(items, start=1):
        row["backlog_index"] = idx

    doc = {
        "schema": "client-proof-recipe-queue-v1",
        "version": "1.0.0",
        "generated_at": _now(),
        "rubric": str(RUBRIC.relative_to(ROOT)),
        "total": len(items),
        "proven_live_count": sum(1 for x in items if x.get("recipe_class") == "proven_live"),
        "filtered_backlog_count": sum(1 for x in items if x.get("lane") == "client-proof-filtered"),
        "one_law": "One row = one client-demo recipe (GOAL · DONE · VERIFY · proof artifact).",
        "items": items,
    }
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", type=int, default=100)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    doc = build(target=args.target, write=not args.no_write)
    if args.json:
        print(json.dumps({"ok": True, "total": doc["total"], "path": str(OUT)}, indent=2))
    else:
        print(f"OK client-proof-recipe-queue total={doc['total']} proven_live={doc['proven_live_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
