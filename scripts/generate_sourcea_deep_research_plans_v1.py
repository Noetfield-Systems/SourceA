#!/usr/bin/env python3
"""Generate plans + client-proof recipes from SourceA deep research report.

Source: external deep research (PRODUCT BETA · P0/P1 fix list).
Law: data/cloud-forge-run-realistic-motor-law-v1.json — one recipe per row · one row per tick.

Outputs:
  - 12 child sdr-* plans (granular)
  - 10 UP-DR upgrade workstreams (§9 fix list)
  - client-proof queue · batch chain · Worker INBOX
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PLAN_OUT = ROOT / "data" / "sourcea-deep-research-upgrade-plan-v1.json"
UPGRADE_10_OUT = ROOT / "data" / "sourcea-deep-research-10-upgrade-plan-v1.json"
QUEUE_OUT = ROOT / "data" / "client-proof-recipe-queue-v1.json"
ACTIVE_POINTER = ROOT / "data" / "cloud-forge-run-queue-active-v1.json"
CONTROL_PLANE = ROOT / "data" / "cloud-workers-control-plane-v1.json"
INBOX_JSON = SINA / "worker-prompt-inbox-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
RECEIPT = SINA / "sourcea-deep-research-plans-receipt-v1.json"
RESEARCH_DOC = Path.home() / "Downloads" / "sourcea_deep_research_report.md"
PLAN_REGISTRY_DIR = ROOT / "brain-os" / "plan-registry" / "sourcea-deep-research-v1"
PROMPTS_DIR = PLAN_REGISTRY_DIR / "prompts"
VERIFY_SCRIPT = "scripts/verify_client_proof_artifact_v1.py"
SUPABASE_VERIFY = (
    "cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count"
)
PULSE_SCRIPT = "scripts/sourcea_deep_research_10_pulse_v1.py"
VALIDATOR_SCRIPT = "scripts/validate-sourcea-deep-research-10-v1.sh"


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


def _write(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _url_verify(url: str, *markers: str) -> str:
    marker_flags = " ".join(f"--marker {json.dumps(marker)}" for marker in markers)
    cmd = f"python3 {VERIFY_SCRIPT} --url {url} {marker_flags}".strip()
    return " && ".join(["cd ~/Desktop/SourceA", cmd, SUPABASE_VERIFY])


def _cmd_verify(*cmds: str) -> str:
    return " && ".join(["cd ~/Desktop/SourceA", *cmds, SUPABASE_VERIFY])


def deep_research_plans() -> list[dict[str, Any]]:
    """P0/P1/P2 child plans — granular sdr-* rows."""
    return [
        {
            "id": "sdr-p0-001",
            "tier": "P0",
            "title": "Fix public install/package claim vs PyPI reality",
            "problem": "Homepage/eval references pip install sourcea-boot; package must resolve or copy must say GitHub-only.",
            "goal": "Eval page and PyPI probe agree — no false install promise",
            "done_when": "probe_sourcea_boot_pypi_v1.py ok OR eval copy says GitHub clone pending",
            "verify": _cmd_verify(
                "python3 scripts/probe_sourcea_boot_pypi_v1.py --json",
                f'python3 {VERIFY_SCRIPT} --url https://sourcea.app/eval --marker "sourcea-boot"',
            ),
            "proof_artifact": "https://sourcea.app/eval",
            "client_demo": "Open /eval — show install line matches live PyPI or honest GitHub fallback",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/eval.html",
            "status": "open",
        },
        {
            "id": "sdr-p0-002",
            "tier": "P0",
            "title": "Forge Terminal: fix Connecting… or show honest offline state",
            "problem": "Public demo stuck on Connecting damages conversion.",
            "goal": "Terminal shows online send path OR clear offline + forge@sourcea.app fallback",
            "done_when": "Terminal page markers present; health/send path returns ok or offline banner",
            "verify": _url_verify(
                "https://sourcea.app/sourcea/forge/terminal",
                "Forge Terminal",
                "data-sa-proof-cta",
            ),
            "proof_artifact": "https://sourcea.app/sourcea/forge/terminal",
            "client_demo": "Send one prompt on terminal — response or explicit offline state",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/sourcea/forge/terminal.html",
            "status": "open",
        },
        {
            "id": "sdr-p0-003",
            "tier": "P0",
            "title": "Verify intake submit: store lead + confirmation + notification",
            "problem": "Lead capture is P0 commercial path; submit not externally verified.",
            "goal": "Start/intake POST stores row in Supabase and shows success reference",
            "done_when": "mvp-intake-config exposes worker URL; verify_mvp_intake_proof_v1 PASS",
            "verify": _cmd_verify("python3 scripts/verify_mvp_intake_proof_v1.py --json"),
            "proof_artifact": "supabase://mvp_intake_leads",
            "client_demo": "Submit test lead on /start — show confirmation ID + Supabase row",
            "lane": "sourcea-site",
            "work_path": "cloud/workers/sourcea-mvp-intake-v1/",
            "status": "open",
        },
        {
            "id": "sdr-p1-001",
            "tier": "P1",
            "title": "One primary CTA: Request a 48-hour build",
            "problem": "Too many CTAs fragment buyer path.",
            "goal": "Homepage hero primary CTA = Request a 48-hour build; secondary See proof",
            "done_when": "Homepage has data-sa-primary-cta marker linking to /start or /offer",
            "verify": _url_verify(
                "https://sourcea.app/",
                "Request a 48-hour build",
                "See proof",
            ),
            "proof_artifact": "https://sourcea.app/",
            "client_demo": "10-second test: visitor names paid path without reading nav",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/index.html",
            "status": "open",
        },
        {
            "id": "sdr-p1-002",
            "tier": "P1",
            "title": "Canonical pricing ladder across Offer/Start/Pricing",
            "problem": "Price bands inconsistent across pages.",
            "goal": "One ladder: 48h $1.5K–$5K · custom $3K–$10K · support from $2K/mo",
            "done_when": "pricing.html offer.html start.html share same tier copy hash",
            "verify": " && ".join(
                [
                    _url_verify("https://sourcea.app/pricing", "$1,500", "$5,000"),
                    _url_verify("https://sourcea.app/offer", "48-hour", "$1,500"),
                ]
            ),
            "proof_artifact": "https://sourcea.app/pricing",
            "client_demo": "Tab three pages — pricing matches",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/pricing.html",
            "status": "open",
        },
        {
            "id": "sdr-p1-003",
            "tier": "P1",
            "title": "Privacy/data note visible before intake Submit",
            "problem": "Form collects email/project; privacy assurance missing.",
            "goal": "Intake form shows no-resale privacy note above Submit",
            "done_when": "Start page has data-sa-privacy-note marker before submit button",
            "verify": _url_verify(
                "https://sourcea.app/start",
                "no resale",
                "data-sa-privacy-note",
            ),
            "proof_artifact": "https://sourcea.app/start",
            "client_demo": "Scroll intake — privacy visible before Submit",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/start.html",
            "status": "open",
        },
        {
            "id": "sdr-p1-004",
            "tier": "P1",
            "title": "Simplify product taxonomy box on homepage",
            "problem": "Forge/Brain/Chat Unify/Cloud Workers confuse first-time buyers.",
            "goal": "One box: SourceA=product · Forge=engine · components named once",
            "done_when": "Homepage has data-sa-taxonomy box with three-line explainer",
            "verify": _url_verify(
                "https://sourcea.app/",
                "data-sa-taxonomy",
                "Forge is the execution engine",
            ),
            "proof_artifact": "https://sourcea.app/",
            "client_demo": "Read taxonomy box aloud — under 15 seconds",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/index.html",
            "status": "open",
        },
        {
            "id": "sdr-p1-005",
            "tier": "P1",
            "title": "Buyer-readable proof: What this proves under live receipt",
            "problem": "Technical receipts need commercial interpretation.",
            "goal": "Live receipt page adds plain-English what-this-proves strip",
            "done_when": "GET /sourcea/proof/live JSON + human strip on proof page",
            "verify": _cmd_verify(
                'curl -fsS https://sourcea.app/sourcea/proof/live | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get(\'ok\') or d.get(\'verdict\')"',
                f'python3 {VERIFY_SCRIPT} --url https://sourcea.app/proof --marker "What this proves"',
            ),
            "proof_artifact": "https://sourcea.app/sourcea/proof/live",
            "client_demo": "Open receipt — non-technical line explains delivery proof",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/proof.html",
            "status": "open",
        },
        {
            "id": "sdr-p1-006",
            "tier": "P1",
            "title": "Homepage copy upgrade: proof-backed MVPs headline",
            "problem": "Hero still dense; research recommends clearer commercial headline.",
            "goal": "Hero matches research §10 headline + subheadline",
            "done_when": "Homepage contains Proof-backed MVPs and acquisition systems, shipped fast",
            "verify": _url_verify(
                "https://sourcea.app/",
                "Proof-backed MVPs",
                "acquisition systems",
            ),
            "proof_artifact": "https://sourcea.app/",
            "client_demo": "Read hero — ICP clear in one breath",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/index.html",
            "status": "open",
        },
        {
            "id": "sdr-p1-007",
            "tier": "P1",
            "title": "Pricing page route reliability (200 + linked from nav)",
            "problem": "Pricing route partially confirmed during external review.",
            "goal": "/pricing returns 200 and nav Pricing link resolves",
            "done_when": "curl 200 on /pricing and validate-sourcea-contract-pages or link check PASS",
            "verify": _cmd_verify(
                "curl -fsS -o /dev/null -w '%{http_code}' https://sourcea.app/pricing | grep -q 200",
            ),
            "proof_artifact": "https://sourcea.app/pricing",
            "client_demo": "Click nav Pricing — page loads",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/pricing.html",
            "status": "open",
        },
        {
            "id": "sdr-p2-001",
            "tier": "P2",
            "title": "Footer relation map: SourceA · Noetfield · TrustField · Gateway",
            "problem": "TrustField/Gateway relationship not visible.",
            "goal": "Footer or about shows one-line relation map",
            "done_when": "Footer contains data-sa-relation-map with four entities",
            "verify": _url_verify(
                "https://sourcea.app/",
                "data-sa-relation-map",
                "Noetfield",
            ),
            "proof_artifact": "https://sourcea.app/",
            "client_demo": "Footer answers who-owns-what in 10s",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/index.html",
            "status": "open",
        },
        {
            "id": "sdr-p2-002",
            "tier": "P2",
            "title": "OpenGraph / LinkedIn share card",
            "problem": "Social preview not verified.",
            "goal": "og:title and og:description match research §9 P2 copy",
            "done_when": "index.html head has og:title Proof-backed AI execution systems",
            "verify": _cmd_verify(
                f'python3 {VERIFY_SCRIPT} --url https://sourcea.app/ --marker "og:title"',
            ),
            "proof_artifact": "https://sourcea.app/",
            "client_demo": "LinkedIn post inspector shows correct preview",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/index.html",
            "status": "open",
        },
    ]


def _sdr_index() -> dict[str, dict[str, Any]]:
    return {p["id"]: p for p in deep_research_plans()}


def build_up_dr_plans() -> list[dict[str, Any]]:
    """10 upgrade workstreams — deep research §9 fix list."""
    sdr = _sdr_index()

    def _step(child_id: str) -> dict[str, Any]:
        c = sdr[child_id]
        return {
            "sdr_id": child_id,
            "title": c["title"],
            "acceptance": f"{child_id} verify PASS",
            "status": c.get("status", "open"),
        }

    specs: list[dict[str, Any]] = [
        {
            "id": "UP-DR-01",
            "tier": "P0",
            "theme": "claim-hygiene",
            "title": "Claim hygiene — install/PyPI",
            "child_ids": ["sdr-p0-001"],
            "work_path": "SourceA-landing/green-unified/eval.html",
        },
        {
            "id": "UP-DR-02",
            "tier": "P0",
            "theme": "live-demo",
            "title": "Live demo — Forge Terminal",
            "child_ids": ["sdr-p0-002"],
            "work_path": "SourceA-landing/green-unified/sourcea/forge/terminal.html",
        },
        {
            "id": "UP-DR-03",
            "tier": "P0",
            "theme": "lead-capture",
            "title": "Lead capture — intake submit",
            "child_ids": ["sdr-p0-003"],
            "work_path": "cloud/workers/sourcea-mvp-intake-v1/",
        },
        {
            "id": "UP-DR-04",
            "tier": "P1",
            "theme": "buyer-path",
            "title": "Buyer path — primary CTA + hero",
            "child_ids": ["sdr-p1-001", "sdr-p1-006"],
            "work_path": "SourceA-landing/green-unified/index.html",
        },
        {
            "id": "UP-DR-05",
            "tier": "P1",
            "theme": "commercial-ladder",
            "title": "Commercial ladder — pricing",
            "child_ids": ["sdr-p1-002", "sdr-p1-007"],
            "work_path": "SourceA-landing/green-unified/pricing.html",
        },
        {
            "id": "UP-DR-06",
            "tier": "P1",
            "theme": "intake-trust",
            "title": "Intake trust — privacy note",
            "child_ids": ["sdr-p1-003"],
            "work_path": "SourceA-landing/green-unified/start.html",
        },
        {
            "id": "UP-DR-07",
            "tier": "P1",
            "theme": "product-taxonomy",
            "title": "Product taxonomy",
            "child_ids": ["sdr-p1-004"],
            "work_path": "SourceA-landing/green-unified/index.html",
        },
        {
            "id": "UP-DR-08",
            "tier": "P1",
            "theme": "proof-readability",
            "title": "Proof readability",
            "child_ids": ["sdr-p1-005"],
            "work_path": "SourceA-landing/green-unified/proof.html",
        },
        {
            "id": "UP-DR-09",
            "tier": "P2",
            "theme": "ecosystem-map",
            "title": "Ecosystem map",
            "child_ids": ["sdr-p2-001"],
            "work_path": "SourceA-landing/green-unified/index.html",
        },
        {
            "id": "UP-DR-10",
            "tier": "P2",
            "theme": "share-gate",
            "title": "Shareability + ship gate",
            "child_ids": ["sdr-p2-002"],
            "work_path": "SourceA-landing/green-unified/index.html",
        },
    ]

    rows: list[dict[str, Any]] = []
    for spec in specs:
        children = [sdr[cid] for cid in spec["child_ids"]]
        goals = " · ".join(c["goal"] for c in children)
        done = " · ".join(c["done_when"] for c in children)
        verify_parts = [c["verify"] for c in children]
        if spec["id"] == "UP-DR-10":
            verify_parts.append(f"bash {VALIDATOR_SCRIPT}")
        verify = " && ".join(verify_parts)
        rows.append(
            {
                "id": spec["id"],
                "wave": "W1",
                "tier": spec["tier"],
                "theme": spec["theme"],
                "title": spec["title"],
                "goal": goals,
                "done_when": done,
                "verify": verify,
                "proof_artifact": children[0]["proof_artifact"],
                "client_demo": " · ".join(c["client_demo"] for c in children),
                "lane": "sourcea-site",
                "work_path": spec["work_path"],
                "status": "open",
                "steps": [_step(cid) for cid in spec["child_ids"]],
                "prompt_path": f"brain-os/plan-registry/sourcea-deep-research-v1/prompts/{spec['id'].lower()}-{spec['theme']}.md",
            }
        )
    return rows


def _plan_doc(plans: list[dict[str, Any]]) -> dict[str, Any]:
    p0 = sum(1 for p in plans if p.get("tier") == "P0")
    p1 = sum(1 for p in plans if p.get("tier") == "P1")
    p2 = sum(1 for p in plans if p.get("tier") == "P2")
    return {
        "schema": "sourcea-deep-research-upgrade-plan-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "source": str(RESEARCH_DOC),
        "verdict": "PRODUCT_BETA",
        "commercial_framing": "Proof-backed 48-hour acquisition systems for founders, agencies, and service businesses",
        "one_law": "One plan = one shippable recipe row · one Auto Runtime tick = one row · Supabase proof required",
        "motor_law": "data/cloud-forge-run-realistic-motor-law-v1.json",
        "tier_counts": {"P0": p0, "P1": p1, "P2": p2, "total": len(plans)},
        "plans": plans,
        "cross_ref": {
            "upgrade_10": "data/sourcea-deep-research-10-upgrade-plan-v1.json",
            "client_proof_queue": "data/client-proof-recipe-queue-v1.json",
            "site_score_registry": "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
            "generator": "scripts/generate_sourcea_deep_research_plans_v1.py",
        },
    }


def upgrade_10_doc(up_plans: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "sourcea-deep-research-10-upgrade-plan-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "source": str(RESEARCH_DOC),
        "wave": "W1",
        "gate_plan": "UP-DR-10",
        "baseline": "PRODUCT_BETA",
        "target": "WARM_COMMERCIAL_READY",
        "critical_path": ["UP-DR-01", "UP-DR-02", "UP-DR-03", "UP-DR-10"],
        "one_law": "One UP-DR plan = one CLOUD-SEC row · one CF tick = one row · Supabase proof gate",
        "motor_law": "data/cloud-forge-run-realistic-motor-law-v1.json",
        "pulse_script": PULSE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
        "human_doc": "docs/SOURCEA_DEEP_RESEARCH_10_UPGRADE_PLANS_LOCKED_v1.md",
        "upgrade_plans": up_plans,
        "cross_ref": {
            "child_plans": "data/sourcea-deep-research-upgrade-plan-v1.json",
            "registry": "brain-os/plan-registry/sourcea-deep-research-v1/REGISTRY.json",
            "client_proof_queue": "data/client-proof-recipe-queue-v1.json",
            "generator": "scripts/generate_sourcea_deep_research_plans_v1.py",
        },
    }


def _recipe_from_up(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": plan["id"],
        "title": plan["title"],
        "goal": plan["goal"],
        "done_when": plan["done_when"],
        "verify": plan["verify"],
        "proof_artifact": plan["proof_artifact"],
        "client_demo": plan["client_demo"],
        "client_problem": f"{plan.get('tier')}-deep-research-upgrade",
        "tier": "T0" if plan.get("tier") == "P0" else "T1",
        "lane": plan.get("lane", "sourcea-site"),
        "status": "backlog",
        "source_registry": "data/sourcea-deep-research-10-upgrade-plan-v1.json",
        "prompt_path": plan.get("prompt_path"),
        "proven": False,
        "realistic": True,
        "recipe_class": "deep_research_upgrade",
        "human_review_before_buyer_call": plan.get("tier") == "P0",
    }


def build_queue(*, include_proven: bool = True) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_client_proof_recipe_queue_v1 import PROVEN_LIVE_RECIPES  # noqa: WPS433

    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for plan in build_up_dr_plans():
        pid = plan["id"]
        if pid not in seen:
            items.append(_recipe_from_up(plan))
            seen.add(pid)
    if include_proven:
        for row in PROVEN_LIVE_RECIPES:
            pid = str(row.get("plan_id") or "")
            if pid and pid not in seen:
                items.append({**row, "status": "backlog", "realistic": True, "recipe_class": "proven_live"})
                seen.add(pid)
    for idx, row in enumerate(items, start=1):
        row["backlog_index"] = idx
    return {
        "schema": "client-proof-recipe-queue-v1",
        "version": "1.2.0",
        "generated_at": _now(),
        "rubric": "data/client-proof-recipe-rubric-v1.json",
        "total": len(items),
        "up_dr_count": sum(1 for x in items if x.get("recipe_class") == "deep_research_upgrade"),
        "proven_live_count": sum(1 for x in items if x.get("recipe_class") == "proven_live"),
        "one_law": "One row = one UP-DR recipe (GOAL · DONE · VERIFY · Supabase proof). One tick = one row.",
        "items": items,
    }


def _existing_sa_floor() -> int:
    max_seen = 9000
    pat = re.compile(r"\bsa-(\d{4,})\b", re.I)
    for path in (
        SINA / "healthy-queue-30-active.json",
        ROOT / "data" / "plans-unified-worker-queue-v1.json",
    ):
        if not path.is_file():
            continue
        for match in pat.finditer(path.read_text(encoding="utf-8", errors="replace")):
            max_seen = max(max_seen, int(match.group(1)))
    return max_seen + 1


def fill_inbox(*, window: int = 10) -> dict[str, Any]:
    """Fill Worker INBOX — all 10 UP-DR plans; head = first P0."""
    up_plans = build_up_dr_plans()
    p0 = [p for p in up_plans if p.get("tier") == "P0"]
    rest = [p for p in up_plans if p.get("tier") != "P0"]
    ordered = (p0 + rest)[:window]
    start_sa = _existing_sa_floor()
    queue = []
    for idx, plan in enumerate(ordered, start=1):
        sa = f"sa-{start_sa + idx - 1:04d}"
        instruction = (
            f"WORK: {plan['id']} — {plan['title']}\n"
            f"Path: {plan.get('work_path')}\n"
            f"Goal: {plan['goal']}\n"
            f"Done when: {plan['done_when']}\n"
            f"Verify: {plan['verify']}\n"
            f"Proof: {plan['proof_artifact']}\n"
            "One bounded turn · receipt + Supabase row · WORKER_ROUND_REPORT · STOP."
        )
        queue.append(
            {
                "queue_pos": idx,
                "sa_id": sa,
                "plan_id": plan["id"],
                "title": plan["title"],
                "tier": plan["tier"],
                "instruction": instruction,
                "queue_role": "act",
                "phase": "phase-deep-research-w1-v1",
            }
        )
    head = queue[0] if queue else {}
    prompt = head.get("instruction", "")
    payload = {
        "schema": "worker-prompt-inbox-v1",
        "pending": True,
        "delivered_at": _now(),
        "source": "deep_research_up_dr_v1",
        "lane": "sourcea_worker",
        "workspace": str(ROOT),
        "chars": len(prompt),
        "prompt": f"WORK: {head.get('sa_id')} — {head.get('title')}\n\n{prompt}",
        "meta": {
            "sa_id": head.get("sa_id"),
            "plan_id": head.get("plan_id"),
            "queue_role": "act",
            "queue_pos": 1,
            "queue_total": len(queue),
            "phase": "phase-deep-research-w1-v1",
            "queue_exhausted": False,
        },
        "sa_id": head.get("sa_id"),
        "deep_research_queue": queue,
        "pickup": {
            "founder_line": "RUN INBOX — UP-DR-01..10 deep research upgrade queue",
            "inbox_json": str(INBOX_JSON),
            "inbox_md": str(INBOX_MD),
        },
    }
    _write(INBOX_JSON, payload)
    md = f"""<!-- WORKER_INBOX pending=1 source=deep_research_up_dr queue=1/{len(queue)} sa={head.get('sa_id')} -->
# SourceA Worker — UP-DR deep research W1

**Updated:** {payload['delivered_at']}

---

{payload['prompt']}

---

**Worker:** one UP-DR plan · proof on disk · STOP.
"""
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(md, encoding="utf-8")
    hq = {
        "schema": "healthy-queue-30-active.v1",
        "product": "Deep research UP-DR-01..10 — Worker mirror",
        "thread": "DEEP-RESEARCH-W1",
        "count": len(queue),
        "queue": queue,
        "head_sa": head.get("sa_id"),
        "rhythm": "one sa per Worker turn · mirrors Cloud Forge Run UP-DR recipes",
        "saved_at": _now(),
    }
    for path in (
        SINA / "healthy-queue-30-active.json",
        ROOT / "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json",
    ):
        _write(path, hq)
    return {"ok": True, "inbox": str(INBOX_JSON), "head_sa": head.get("sa_id"), "queue_len": len(queue)}


def write_plan_markdowns(plans: list[dict[str, Any]]) -> dict[str, Any]:
    """Child sdr-* markdown files."""
    PLAN_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for plan in plans:
        pid = plan["id"]
        slug = pid.replace("sdr-", "deep-research-")
        path = PLAN_REGISTRY_DIR / f"{slug}.md"
        body = f"""# {plan['title']}

**Plan ID:** `{pid}` · **Tier:** {plan.get('tier')} · **Updated:** {_now()}

## Problem
{plan.get('problem', '')}

## Goal
{plan['goal']}

## Done when
{plan['done_when']}

## Verify
```
{plan['verify']}
```

## Proof artifact
{plan.get('proof_artifact', '')}

## Client demo
{plan.get('client_demo', '')}

## Work path
`{plan.get('work_path', '')}`

---
*Child plan · rolled into UP-DR upgrade wave*
"""
        path.write_text(body, encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))
    return {"ok": True, "written": len(written), "kind": "sdr_child"}


def write_up_dr_markdowns(up_plans: list[dict[str, Any]]) -> dict[str, Any]:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for plan in up_plans:
        slug = f"{plan['id'].lower()}-{plan['theme']}"
        path = PROMPTS_DIR / f"{slug}.md"
        steps = plan.get("steps") or []
        steps_md = "\n".join(
            f"- **{s['sdr_id']}** — {s['title']} ({s['status']})" for s in steps
        )
        body = f"""# {plan['title']}

**Plan ID:** `{plan['id']}` · **Tier:** {plan.get('tier')} · **Wave:** W1

## Goal
{plan['goal']}

## Done when
{plan['done_when']}

## Child steps
{steps_md}

## Verify
```
{plan['verify']}
```

## Proof artifact
{plan.get('proof_artifact', '')}

## Client demo
{plan.get('client_demo', '')}

## Work path
`{plan.get('work_path', '')}`

---
*One CLOUD-SEC row per Auto Runtime tick · Supabase proof · INCIDENT-045*
"""
        path.write_text(body, encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))
    return {"ok": True, "written": len(written), "kind": "up_dr"}


def write_registry(up_plans: list[dict[str, Any]], sdr_plans: list[dict[str, Any]]) -> dict[str, Any]:
    w1_execution = {
        "wave": "W1",
        "label": "Deep research §9 — 10 upgrade workstreams",
        "gate_plan": "UP-DR-10",
        "total_steps": 10,
        "critical_path": ["UP-DR-01", "UP-DR-02", "UP-DR-03", "UP-DR-10"],
        "pulse_script": PULSE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
        "upgrade_plans": [
            {
                "id": p["id"],
                "wave": p.get("wave", "W1"),
                "theme": p["theme"],
                "title": p["title"],
                "tier": p["tier"],
                "status": p.get("status", "open"),
                "prompt_path": p.get("prompt_path"),
                "steps": p.get("steps", []),
            }
            for p in up_plans
        ],
    }
    index = {
        "schema": "sourcea-deep-research-plan-registry-v1",
        "version": "2.0.0",
        "saved_at": _now(),
        "source": str(RESEARCH_DOC),
        "child_count": len(sdr_plans),
        "upgrade_count": len(up_plans),
        "child_plans": [p["id"] for p in sdr_plans],
        "upgrade_plans": [p["id"] for p in up_plans],
        "motor_law": "data/cloud-forge-run-realistic-motor-law-v1.json",
        "one_law": "One UP-DR plan = one CLOUD-SEC row · one tick = one row · */10 CF cron",
        "w1_execution": w1_execution,
    }
    _write(PLAN_REGISTRY_DIR / "REGISTRY.json", index)
    return {"ok": True, "registry": str(PLAN_REGISTRY_DIR.relative_to(ROOT)), "w1_execution": True}


def arm_batch_chain(*, batch_id: int = 83) -> dict[str, Any]:
    """Generate batch file; chain after existing next_batch without clobbering."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_client_proof_cloud_batch_v1 import generate  # noqa: WPS433

    row = generate(batch_id=batch_id, offset=0, write=True, activate=False)
    ptr = _read(ACTIVE_POINTER)
    cp = _read(CONTROL_PLANE)
    batch_meta = {
        "batch_id": batch_id,
        "status": "ready_locked",
        "queue_path": f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json",
        "cloud_sec_range": row.get("cloud_sec_range"),
        "library": "client-proof-recipe",
        "tasks_per_row": 1,
        "source": "deep_research_up_dr_v1",
    }
    nxt_id = int((ptr.get("next_batch") or {}).get("batch_id") or 0)
    active_id = int(ptr.get("batch_id") or 0)
    if nxt_id == batch_id:
        pass
    elif nxt_id == batch_id - 1 or (nxt_id == 0 and active_id < batch_id):
        ptr["next_batch"] = batch_meta
        ptr["registry_exhausted"] = False
        ptr["saved_at"] = _now()
        _write(ACTIVE_POINTER, ptr)
        cp["ready_batch"] = batch_meta
    else:
        cp["queued_batch_chain"] = {**(cp.get("queued_batch_chain") or {}), str(batch_id): batch_meta}
    cp["saved_at"] = _now()
    _write(CONTROL_PLANE, cp)
    return {**row, "batch_chained": True, "next_batch_preserved": nxt_id if nxt_id != batch_id else None}


def patch_motor_ssot(*, max_advance: int = 1) -> dict[str, Any]:
    paths_updated = []
    pairs = [
        (ROOT / "data/cloud-auto-runtime-v1.json", ("max_advance_per_tick", "rows_per_turn_cap")),
        (ROOT / "data/cloud-forge-run-full-pack-pattern-v1.json", None),
        (ROOT / "data/cloud-forge-run-realistic-motor-law-v1.json", ("max_advance_per_tick", "rows_per_turn_cap")),
    ]
    for path, keys in pairs:
        doc = _read(path)
        if not doc:
            continue
        if keys:
            for k in keys:
                doc[k] = max_advance
        motor = doc.get("motor")
        if isinstance(motor, dict):
            motor["max_advance_per_tick"] = max_advance
            motor["rows_per_turn_cap"] = max_advance
        pattern = doc.get("pattern")
        if isinstance(pattern, dict):
            pattern["max_advance_per_tick"] = max_advance
        for trig in doc.get("triggers") or []:
            body = trig.get("body")
            if isinstance(body, dict) and "max_advance" in body:
                body["max_advance"] = max_advance
        doc["one_law"] = (
            f"CF cron (~10 min) → one Railway POST → {max_advance} doable task(s) "
            "(one recipe per row). Proof gate + Supabase before advance."
        )
        doc["saved_at"] = _now()
        _write(path, doc)
        paths_updated.append(str(path.relative_to(ROOT)))
    cp = _read(CONTROL_PLANE)
    cp["one_law"] = (
        f"Cloud Workers cockpit · Auto Runtime */10 · max_advance={max_advance} "
        "· one UP-DR recipe per CLOUD-SEC row · Supabase proof gate"
    )
    cp["hub_api"]["proceed"] = (
        f'POST http://127.0.0.1:13027/api/cloud-workers/v1 {{"action":"proceed","full_pack":true,"max_advance":{max_advance}}}'
    )
    if isinstance(cp.get("active_batch"), dict):
        cp["active_batch"]["tasks_per_row"] = 1
        cp["active_batch"]["rows_per_turn"] = max_advance
    cp["saved_at"] = _now()
    _write(CONTROL_PLANE, cp)
    return {"ok": True, "max_advance": max_advance, "updated": paths_updated}


def run_all(*, write: bool = True) -> dict[str, Any]:
    sdr_plans = deep_research_plans()
    up_plans = build_up_dr_plans()
    plan_doc = _plan_doc(sdr_plans)
    upgrade_doc = upgrade_10_doc(up_plans)
    queue_doc = build_queue()
    receipt: dict[str, Any] = {
        "schema": "sourcea-deep-research-plans-receipt-v1",
        "ok": True,
        "at": _now(),
        "sdr_plans": len(sdr_plans),
        "up_dr_plans": len(up_plans),
        "queue_total": queue_doc["total"],
        "up_dr_recipes": queue_doc["up_dr_count"],
    }
    if write:
        _write(PLAN_OUT, plan_doc)
        _write(UPGRADE_10_OUT, upgrade_doc)
        _write(QUEUE_OUT, queue_doc)
        receipt["sdr_md"] = write_plan_markdowns(sdr_plans)
        receipt["up_dr_md"] = write_up_dr_markdowns(up_plans)
        receipt["registry"] = write_registry(up_plans, sdr_plans)
        receipt["motor"] = patch_motor_ssot(max_advance=1)
        receipt["inbox"] = fill_inbox(window=10)
        receipt["batch"] = arm_batch_chain(batch_id=83)
    _write(RECEIPT, receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--plans-only", action="store_true")
    ap.add_argument("--inbox-only", action="store_true")
    ap.add_argument("--motor-only", action="store_true")
    args = ap.parse_args()
    if args.plans_only:
        sdr = deep_research_plans()
        up = build_up_dr_plans()
        if not args.no_write:
            _write(PLAN_OUT, _plan_doc(sdr))
            _write(UPGRADE_10_OUT, upgrade_10_doc(up))
            write_registry(up, sdr)
            write_up_dr_markdowns(up)
        row = {"ok": True, "sdr": len(sdr), "up_dr": len(up)}
    elif args.inbox_only:
        row = fill_inbox()
    elif args.motor_only:
        row = patch_motor_ssot(max_advance=1)
    else:
        row = run_all(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row, indent=2)[:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
