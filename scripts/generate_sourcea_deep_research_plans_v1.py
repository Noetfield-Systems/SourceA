#!/usr/bin/env python3
"""Generate plans + client-proof recipes from SourceA deep research report.

Source: external deep research (PRODUCT BETA · P0/P1 fix list).
Law: data/cloud-forge-run-realistic-motor-law-v1.json — one recipe per row · one row per tick.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PLAN_OUT = ROOT / "data" / "sourcea-deep-research-upgrade-plan-v1.json"
QUEUE_OUT = ROOT / "data" / "client-proof-recipe-queue-v1.json"
ACTIVE_POINTER = ROOT / "data" / "cloud-forge-run-queue-active-v1.json"
CONTROL_PLANE = ROOT / "data" / "cloud-workers-control-plane-v1.json"
INBOX_JSON = SINA / "worker-prompt-inbox-v1.json"
INBOX_MD = ROOT / ".sina-loop" / "INBOX.md"
RECEIPT = SINA / "sourcea-deep-research-plans-receipt-v1.json"
RESEARCH_DOC = Path.home() / "Downloads" / "sourcea_deep_research_report.md"
PLAN_REGISTRY_DIR = ROOT / "brain-os" / "plan-registry" / "sourcea-deep-research-v1"
VERIFY_SCRIPT = "scripts/verify_client_proof_artifact_v1.py"
SUPABASE_VERIFY = (
    "cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count"
)


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
    parts = [
        "cd ~/Desktop/SourceA",
        f"python3 {VERIFY_SCRIPT} --url {url}",
    ]
    for marker in markers:
        parts.append(f"--marker {json.dumps(marker)}")
    parts.append(SUPABASE_VERIFY)
    return " && ".join(parts)


def _cmd_verify(*cmds: str) -> str:
    return " && ".join(["cd ~/Desktop/SourceA", *cmds, SUPABASE_VERIFY])


def deep_research_plans() -> list[dict[str, Any]]:
    """P0/P1 fixes from deep research §9 — one shippable unit each."""
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
                f"python3 {VERIFY_SCRIPT} --url https://sourcea.app/eval --marker sourcea-boot",
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
                "curl -fsS https://sourcea.app/sourcea/proof/live | python3 -c \"import json,sys; d=json.load(sys.stdin); assert d.get('ok') or d.get('verdict')\"",
                f"python3 {VERIFY_SCRIPT} --url https://sourcea.app/proof --marker What this proves",
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
                f"python3 {VERIFY_SCRIPT} --url https://sourcea.app/ --marker og:title",
            ),
            "proof_artifact": "https://sourcea.app/",
            "client_demo": "LinkedIn post inspector shows correct preview",
            "lane": "sourcea-site",
            "work_path": "SourceA-landing/green-unified/index.html",
            "status": "open",
        },
    ]


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
            "client_proof_queue": "data/client-proof-recipe-queue-v1.json",
            "site_score_registry": "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
            "full_stack_fix": "data/sourcea-full-stack-100-fix-plan-v1.json",
            "generator": "scripts/generate_sourcea_deep_research_plans_v1.py",
        },
    }


def _recipe_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_id": plan["id"],
        "title": plan["title"],
        "goal": plan["goal"],
        "done_when": plan["done_when"],
        "verify": plan["verify"],
        "proof_artifact": plan["proof_artifact"],
        "client_demo": plan["client_demo"],
        "client_problem": plan.get("tier", "P1") + "-deep-research",
        "tier": "T0" if plan.get("tier") == "P0" else "T1",
        "lane": plan.get("lane", "sourcea-site"),
        "status": "backlog",
        "source_registry": "data/sourcea-deep-research-upgrade-plan-v1.json",
        "prompt_path": plan.get("work_path"),
        "proven": False,
        "realistic": True,
        "recipe_class": "deep_research",
        "human_review_before_buyer_call": plan.get("tier") == "P0",
    }


def build_queue(*, include_proven: bool = True) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_client_proof_recipe_queue_v1 import PROVEN_LIVE_RECIPES  # noqa: WPS433

    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for plan in deep_research_plans():
        pid = plan["id"]
        if pid not in seen:
            items.append(_recipe_from_plan(plan))
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
        "version": "1.1.0",
        "generated_at": _now(),
        "rubric": "data/client-proof-recipe-rubric-v1.json",
        "total": len(items),
        "deep_research_count": sum(1 for x in items if x.get("recipe_class") == "deep_research"),
        "proven_live_count": sum(1 for x in items if x.get("recipe_class") == "proven_live"),
        "one_law": "One row = one client-demo recipe (GOAL · DONE · VERIFY · Supabase proof). One tick = one row.",
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
    plans = [p for p in deep_research_plans() if p.get("status") == "open"][:window]
    start_sa = _existing_sa_floor()
    queue = []
    for idx, plan in enumerate(plans, start=1):
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
            }
        )
    head = queue[0] if queue else {}
    prompt = head.get("instruction", "")
    payload = {
        "schema": "worker-prompt-inbox-v1",
        "pending": True,
        "delivered_at": _now(),
        "source": "deep_research_plans_v1",
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
            "phase": "phase-deep-research-v1",
            "queue_exhausted": False,
        },
        "sa_id": head.get("sa_id"),
        "deep_research_queue": queue,
        "pickup": {
            "founder_line": "RUN INBOX — deep research P0/P1 queue logged",
            "inbox_json": str(INBOX_JSON),
            "inbox_md": str(INBOX_MD),
        },
    }
    _write(INBOX_JSON, payload)
    md = f"""<!-- WORKER_INBOX pending=1 source=deep_research queue=1/{len(queue)} sa={head.get('sa_id')} -->
# SourceA Worker — deep research P0/P1

**Updated:** {payload['delivered_at']}

---

{payload['prompt']}

---

**Worker:** one plan · verification built in · STOP.
"""
    INBOX_MD.parent.mkdir(parents=True, exist_ok=True)
    INBOX_MD.write_text(md, encoding="utf-8")
    hq = {
        "schema": "healthy-queue-30-active.v1",
        "product": "Deep research P0/P1 — Worker mirror",
        "thread": "DEEP-RESEARCH",
        "count": len(queue),
        "queue": queue,
        "head_sa": head.get("sa_id"),
        "rhythm": "one sa per Worker turn · mirrors Cloud Forge Run recipes",
        "saved_at": _now(),
    }
    for path in (
        SINA / "healthy-queue-30-active.json",
        ROOT / "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json",
    ):
        _write(path, hq)
    return {"ok": True, "inbox": str(INBOX_JSON), "head_sa": head.get("sa_id"), "queue_len": len(queue)}


def write_plan_markdowns(plans: list[dict[str, Any]]) -> dict[str, Any]:
    """One markdown plan file per deep-research row — Worker + Cloud Forge Run mirror."""
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
*One row per Auto Runtime tick · Supabase proof required · INCIDENT-045*
"""
        path.write_text(body, encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))
    index = {
        "schema": "sourcea-deep-research-plan-registry-v1",
        "saved_at": _now(),
        "source": str(RESEARCH_DOC),
        "count": len(written),
        "plans": [p["id"] for p in plans],
        "motor_law": "data/cloud-forge-run-realistic-motor-law-v1.json",
        "one_law": "One plan = one CLOUD-SEC row · one tick = one row · */10 CF cron",
    }
    _write(PLAN_REGISTRY_DIR / "REGISTRY.json", index)
    return {"ok": True, "written": len(written), "registry": str(PLAN_REGISTRY_DIR.relative_to(ROOT))}


def arm_next_batch(*, batch_id: int = 82, batch_only: bool = False) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_client_proof_cloud_batch_v1 import generate  # noqa: WPS433

    row = generate(batch_id=batch_id, offset=0, write=True, activate=not batch_only)
    ptr = _read(ACTIVE_POINTER)
    summary_rng = row.get("cloud_sec_range", "")
    ptr["next_batch"] = {
        "batch_id": batch_id,
        "status": "ready_locked",
        "queue_path": f"data/secondary-cloud-forge-run-batch-{batch_id}-locked-v1.json",
        "cloud_sec_range": summary_rng,
        "library": "client-proof-recipe",
        "tasks_per_row": 1,
        "source": "deep_research_v1",
    }
    ptr["registry_exhausted"] = False
    ptr["saved_at"] = _now()
    _write(ACTIVE_POINTER, ptr)
    cp = _read(CONTROL_PLANE)
    cp["ready_batch"] = ptr["next_batch"]
    cp["saved_at"] = _now()
    _write(CONTROL_PLANE, cp)
    return {**row, "next_batch_armed": True, "batch_only": batch_only}


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
        "· one recipe per CLOUD-SEC row · Supabase proof gate"
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
    plans = deep_research_plans()
    plan_doc = _plan_doc(plans)
    queue_doc = build_queue()
    receipt: dict[str, Any] = {
        "schema": "sourcea-deep-research-plans-receipt-v1",
        "ok": True,
        "at": _now(),
        "plans": len(plans),
        "queue_total": queue_doc["total"],
        "deep_research_recipes": queue_doc["deep_research_count"],
    }
    if write:
        _write(PLAN_OUT, plan_doc)
        _write(QUEUE_OUT, queue_doc)
        receipt["plans_md"] = write_plan_markdowns(plans)
        receipt["motor"] = patch_motor_ssot(max_advance=1)
        receipt["inbox"] = fill_inbox(window=10)
        receipt["batch"] = arm_next_batch(batch_id=82)
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
        doc = _plan_doc(deep_research_plans())
        if not args.no_write:
            _write(PLAN_OUT, doc)
        row = {"ok": True, "plans": len(doc["plans"])}
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
