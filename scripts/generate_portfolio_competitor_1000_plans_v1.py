#!/usr/bin/env python3
"""Generate + validate 1000 competitor-derived plans per portfolio stack (v2 upgraded).

SSOT: docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md
Grid: 20 competitors × 5 workstreams × 10 tasks = 1000 plans per repo
Upgrade v2: full competitor fields · stack-specific surfaces · non-repetitive tasks
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
COMP_DOC = SOURCEA_ROOT / "docs" / "PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md"
GENERATOR_VERSION = 2

WORKSTREAMS = [
    ("ws-ux", "Buyer-visible UX"),
    ("ws-pricing", "Pricing & packaging"),
    ("ws-run", "Run history & proof"),
    ("ws-onboard", "Onboarding & PLG"),
    ("ws-integrate", "Integrations & API"),
]

TIER_FOR_SLOT = ["T0", "T0", "T1", "T1", "T2", "T2", "T2", "T3", "T3", "T3"]
PRIORITY = {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}

STACK_SURFACES = {
    "sourcea": {
        "primary": "Worker Hub Next steps + factory-now line",
        "run": "Worker job run detail page (pass/fail/steps/logs/retry)",
        "pricing": "SourceA agency + Buyer-1 pricing narrative",
        "onboard": "Hub Actions + RUN INBOX first-run path",
        "integrate": "scripts/ queue + cloud dispatch APIs",
        "scope_note": "Controlled agent orchestration motor — not MSB product",
    },
    "witnessbc": {
        "primary": "witnessbc.com pricing + toolkits hub",
        "run": "Witness AI Flow install replay demo + 6 receipt types",
        "pricing": "Free toolkits → Pro packs → Flow install → Ops retainer",
        "onboard": "Founding cohort shadow parallel install SOW",
        "integrate": "Policy packs mapped to agent receipt gates",
        "scope_note": "AI policy + first agentic install — site independence law",
    },
    "noetfield": {
        "primary": "Noetfield NW1 Copilot governance + board pack",
        "run": "TLE evaluate + drift export + copilot pilot e2e",
        "pricing": "CAD $2K shadow pilot → annual design partner",
        "onboard": "Procurement pack + demo-to-SOW path",
        "integrate": "M365/Google evidence connectors",
        "scope_note": "Copilot audit vocabulary — not SourceA motor wording",
    },
    "trustfield": {
        "primary": "trustfield.ca MSB program + compliance export",
        "run": "FINTRAC evidence bundle + investigation timeline",
        "pricing": "Fixed-scope CAD SKUs (registration, policies, CCO)",
        "onboard": "MSB registration → bank onboarding package path",
        "integrate": "KYC/KYB/AML API orchestration stubs",
        "scope_note": "FINTRAC/MSB lane lives here — not VIRLUX",
    },
    "virlux": {
        "primary": "/dashboard/factory Build Factory catalog",
        "run": "Sandbox bay run detail + MCP verify PASS/FAIL receipt",
        "pricing": "mock_only → freemium_cap → paid bay tier ladder",
        "onboard": "30s sandbox demo → upgrade gate",
        "integrate": "@virlux/mcp-verify-factory + catalog REGISTRY.json",
        "scope_note": "Agentic factory SaaS only — payments/FINTRAC OUT",
    },
}

# 10 tasks per workstream — slot index 0..9 (tiers mapped via TIER_FOR_SLOT)
WORKSTREAM_TASKS: dict[str, list[str]] = {
    "ws-ux": [
        "Open {link} — screenshot or quote the exact buyer-facing {ws_label} sentence {comp} uses; paste into plan evidence (vendor says: {what_they_sell})",
        "Write one-line UX spec: `{comp} {ws_label}` → buyer sees X → we show on `{surface_primary}` (lesson: {lesson})",
        "Add `{surface_primary}` UI field or copy block implementing smallest slice of `{lesson}`; preserve honest tier label",
        "E2E or glance check: founder can see `{ws_label}` outcome without Terminal; receipt timestamp logged",
        "Diff our public copy vs {comp} pricing/product page — list 3 concrete gaps; fix highest P0 gap only",
        "Add `{surface_run}` mock row labeled mock_only until live — match {comp} run/history metaphor not invented name",
        "Document who buys ({who_buys}) vs our ICP one sentence on `{priority_md}` row for {comp}",
        "Reject abstract rename — keep market words buyers know from {comp} ({product})",
        "Ship summary in PRIORITY: preserved · changed · achieved vs {comp} {ws_label}",
        "Mark {plan_id} done in REGISTRY with evidence path + {link} after verify PASS",
    ],
    "ws-pricing": [
        "Capture {comp} public pricing evidence: {pricing} — save link or quoted range in plan receipt",
        "Map {comp} revenue model ({revenue_model}) to our `{surface_pricing}` tier names — no hidden fees theater",
        "Add or update one public price card on `{surface_primary}` inspired by {comp} packaging motion",
        "Label free vs paid honestly ({scope_note}); never claim production without receipt",
        "Compare {comp} PLG motion ({gtm}) vs our onboarding — one adoption fix on `{surface_onboard}`",
        "Document why buyers pay per {comp}: {why_pay} — tie to our offer in plain English",
        "Add upgrade CTA path: sandbox/free → paid bay matching {comp} upgrade pattern where applicable",
        "Validator: public copy contains no stale price; tier badge matches REGISTRY honesty label",
        "Write competitor row evidence: {comp} pricing → our SKU → defer/shipped with path",
        "Close {plan_id}: PRIORITY row + verify PASS + link {link}",
    ],
    "ws-run": [
        "From {link} document {comp} run/history UX: {how_runs} — map to `{surface_run}`",
        "Spec run detail fields: status · steps · failure class · retry · timestamp (from lesson: {lesson})",
        "Implement smallest `{surface_run}` slice — PASS/FAIL + one step log; mock_only ok with label",
        "Wire orchestrator/factory receipt emit on run complete — no chat-only done",
        "Add retention note: how long run history kept vs {comp} ({pricing} tier hints)",
        "Surface run id + link in Hub/factory glance for founder audit",
        "Attribute infra vs agent failure class on failed run (Anthropic noise pattern)",
        "Export last run JSON/md bundle for diligence — one-click",
        "Regression: rerun verify after run UI change",
        "Mark {plan_id} done with run page screenshot or receipt path",
    ],
    "ws-onboard": [
        "Document {comp} onboarding path ({gtm}): who runs ({who_runs}) → first value moment",
        "Define ≤30s-to-value step on `{surface_onboard}` copied from {comp} motion",
        "Add checklist or wizard step on `{surface_primary}` — no Terminal required",
        "Freemium cap or trial label visible before first run ({scope_note})",
        "Pair onboarding step with `{surface_run}` receipt so buyer sees proof immediately",
        "Write founder-facing SOW snippet if {comp} uses services-led motion — Witness/TrustField lanes",
        "Measure drop-off: list one friction point vs {comp} and fix",
        "Integrate `{surface_integrate}` hook needed for onboarding (API key, MCP, connector)",
        "Docs: onboarding section cites {comp} as market analog with {link}",
        "Close {plan_id} with onboarding evidence + verify PASS",
    ],
    "ws-integrate": [
        "List {comp} integrations/APIs from {link} or docs — pick one we can wire this quarter",
        "Spec `{surface_integrate}` contract: input → policy gate → output + receipt",
        "Implement stub or live adapter with honest mock_only label if not production",
        "Add signed webhook/event/async pattern — no cross-project DB joins",
        "Log every external call on run timeline (`{surface_run}`)",
        "Document secrets path ~/.sourcea-secrets — never workspace .env",
        "Rate-limit + retry policy copied from {comp} operating model ({how_runs})",
        "Validate adapter with one fixture test or validator script",
        "Update catalog/registry row for integration — {comp} row {competitor_row}",
        "Close {plan_id}: integration receipt + verify PASS + {link}",
    ],
}

STACKS = [
    {
        "stack": "SourceA",
        "stack_key": "sourcea",
        "row_start": 1,
        "row_end": 20,
        "prefix": "sa-mkt",
        "lane": "sourcea",
        "repo": "SourceA",
        "library": "sourcea-competitor-1000",
        "pack_root": SOURCEA_ROOT / "brain-os" / "plan-registry" / "sourcea-competitor-1000",
        "verify": "cd ~/Desktop/SourceA/scripts && bash worker_verify_fast_v1.sh",
        "agent": "AGENT-AUTO-SOURCEA",
        "priority_md": "brain-os/plan-registry/SOURCEA-PRIORITY.md",
    },
    {
        "stack": "WitnessBC",
        "stack_key": "witnessbc",
        "row_start": 21,
        "row_end": 40,
        "prefix": "wb-mkt",
        "lane": "witnessbc",
        "repo": "witnessbc-site",
        "library": "witnessbc-competitor-1000",
        "pack_root": SOURCEA_ROOT / "witnessbc-site" / "os" / "plan-library" / "witnessbc-competitor-1000",
        "verify": "bash ~/Desktop/SourceA/scripts/validate-witnessbc-competitor-1000-v1.sh",
        "agent": "AGENT-AUTO-WITNESSBC",
        "priority_md": "witnessbc-site/content/pricing.html",
    },
    {
        "stack": "Noetfield",
        "stack_key": "noetfield",
        "row_start": 41,
        "row_end": 60,
        "prefix": "nf-mkt",
        "lane": "noetfield",
        "repo": "Noetfield",
        "library": "noetfield-competitor-1000",
        "pack_root": Path.home()
        / "Desktop"
        / "Noetfield"
        / "Noetfield-All-Documents"
        / "Noetfield"
        / "os"
        / "plan-library"
        / "noetfield-competitor-1000",
        "verify": "cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-gtm",
        "agent": "AGENT-AUTO-NOETFIELD",
        "priority_md": "os/plan-library/NOETFIELD-PRIORITY.md",
    },
    {
        "stack": "TrustField",
        "stack_key": "trustfield",
        "row_start": 61,
        "row_end": 80,
        "prefix": "tf-mkt",
        "lane": "trustfield",
        "repo": "TrustField Technologies",
        "library": "trustfield-competitor-1000",
        "pack_root": Path.home() / "Desktop" / "TrustField Technologies" / "os" / "plan-library" / "trustfield-competitor-1000",
        "verify": "cd ~/Desktop/TrustField\\ Technologies && npm test",
        "agent": "AGENT-AUTO-TRUSTFIELD",
        "priority_md": "prompts/future-plans-1000.json",
    },
    {
        "stack": "VIRLUX",
        "stack_key": "virlux",
        "row_start": 81,
        "row_end": 100,
        "prefix": "vx-mkt",
        "lane": "virlux",
        "repo": "VIRLUX",
        "library": "virlux-competitor-1000",
        "pack_root": Path.home() / "Desktop" / "VIRLUX" / "os" / "plan-library" / "virlux-competitor-1000",
        "verify": "cd ~/Desktop/VIRLUX && npm run verify:live",
        "agent": "Auto-VIRLUX-Delivery",
        "priority_md": "os/plan-library/VIRLUX-PRIORITY.md",
    },
]


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s[:48] or "vendor"


def _cell(block: str, key: str) -> str:
    for line in block.splitlines():
        if line.startswith(f"| {key} |"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                return parts[2]
    return ""


def parse_competitors(doc: Path) -> list[dict]:
    text = doc.read_text(encoding="utf-8")
    out: list[dict] = []
    pattern = re.compile(
        r"### (\d+)\. ([^\n]+)\n\n\*\*Stack:\*\* ([^\n·]+)",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        row_num = int(m.group(1))
        name = m.group(2).strip()
        stack = m.group(3).strip()
        start = m.end()
        next_m = pattern.search(text, start)
        block = text[start : next_m.start() if next_m else len(text)]
        product_m = re.search(r"\*\*Product / service:\*\* (.+)", block)
        product = product_m.group(1).strip() if product_m else ""
        out.append(
            {
                "row": row_num,
                "name": name,
                "stack": stack,
                "product": product,
                "what_they_sell": _cell(block, "What they sell") or product,
                "who_runs": _cell(block, "Who runs it"),
                "how_runs": _cell(block, "How it runs"),
                "who_buys": _cell(block, "Who buys"),
                "pricing": _cell(block, "Pricing / cost"),
                "revenue_model": _cell(block, "Revenue model"),
                "why_pay": _cell(block, "Why buyers pay"),
                "gtm": _cell(block, "How they reached market"),
                "links": _cell(block, "Source links") or "see PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md",
                "lesson": _cell(block, "Portfolio lesson") or product,
                "slug": slugify(name),
            }
        )
    out.sort(key=lambda x: x["row"])
    return out


def format_task(template: str, *, comp: dict, cfg: dict, ws_label: str, plan_id: str) -> str:
    surf = STACK_SURFACES[cfg["stack_key"]]
    return template.format(
        comp=comp["name"],
        product=comp["product"],
        ws_label=ws_label,
        lesson=comp["lesson"],
        link=comp["links"],
        plan_id=plan_id,
        competitor_row=comp["row"],
        what_they_sell=comp["what_they_sell"],
        who_runs=comp["who_runs"],
        how_runs=comp["how_runs"],
        who_buys=comp["who_buys"],
        pricing=comp["pricing"],
        revenue_model=comp["revenue_model"],
        why_pay=comp["why_pay"],
        gtm=comp["gtm"],
        priority_md=cfg["priority_md"],
        surface_primary=surf["primary"],
        surface_run=surf["run"],
        surface_pricing=surf["pricing"],
        surface_onboard=surf["onboard"],
        surface_integrate=surf["integrate"],
        scope_note=surf["scope_note"],
    )


def prompt_body(
    *,
    plan_id: str,
    stack: str,
    comp: dict,
    phase: str,
    ws_id: str,
    ws_label: str,
    tier: str,
    task: str,
    verify: str,
    agent: str,
    tier_depth: str,
) -> str:
    return f"""# {plan_id} — {comp["name"]} · {ws_label}

**Version:** 2 · **Tier:** {tier} · **Workstream:** {ws_id}
**Stack:** {stack} · **Competitor row:** {comp["row"]} · **Phase:** {phase}
**Market SSOT:** `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`

## Competitor evidence

| Field | Value |
|-------|-------|
| Company | {comp["name"]} |
| Product | {comp["product"]} |
| What they sell | {comp["what_they_sell"]} |
| Who buys | {comp["who_buys"]} |
| Pricing | {comp["pricing"]} |
| How it runs | {comp["how_runs"]} |
| Source links | {comp["links"]} |
| Portfolio lesson | {comp["lesson"]} |

## Task ({tier_depth})

{task}

## Implementation extraction

`{comp["name"]} · {ws_label}` → what buyer sees at vendor → what we ship logged with receipt.

## Verify

```bash
{verify}
```

## Closeout

1. `status: done` in REGISTRY.json for `{plan_id}`
2. Evidence row in `{agent}` PRIORITY/AUDIT with `{comp["name"]}` link
3. No abstract rename — concrete behavior only

---
agent_tag: {agent}
trigger: PLAN WITH NO ASF
generator: generate_portfolio_competitor_1000_plans_v1.py v{GENERATOR_VERSION}
"""


TIER_DEPTH = {
    "T0": "Critical — smallest shippable slice with receipt",
    "T1": "High — next sprint parity with competitor",
    "T2": "Medium — hardening, validator, docs",
    "T3": "Low — research, defer note, or compare-only",
}


def generate_stack(cfg: dict, all_competitors: list[dict], now: str) -> dict:
    comps = [c for c in all_competitors if cfg["row_start"] <= c["row"] <= cfg["row_end"]]
    if len(comps) != 20:
        raise SystemExit(f"{cfg['stack']}: expected 20 competitors, got {len(comps)}")

    pack = cfg["pack_root"]
    entries: list[dict] = []
    phases = []
    seq = 0

    for c_idx, comp in enumerate(comps):
        phase_id = f"phase-c{c_idx + 1:02d}-{comp['slug']}"
        phases.append(
            {
                "id": phase_id,
                "competitor": comp["name"],
                "competitor_row": comp["row"],
                "description": f"Implement from {comp['name']}: {comp['lesson'][:160]}",
            }
        )
        for ws_id, ws_label in WORKSTREAMS:
            tasks = WORKSTREAM_TASKS[ws_id]
            for slot, stem in enumerate(tasks):
                seq += 1
                tier = TIER_FOR_SLOT[slot]
                plan_id = f"{cfg['prefix']}-{seq:04d}"
                task = format_task(stem, comp=comp, cfg=cfg, ws_label=ws_label, plan_id=plan_id)
                rel = f"prompts/{phase_id}/{ws_id}/{plan_id}.md"
                path = pack / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    prompt_body(
                        plan_id=plan_id,
                        stack=cfg["stack"],
                        comp=comp,
                        phase=phase_id,
                        ws_id=ws_id,
                        ws_label=ws_label,
                        tier=tier,
                        task=task,
                        verify=cfg["verify"],
                        agent=cfg["agent"],
                        tier_depth=TIER_DEPTH[tier],
                    ),
                    encoding="utf-8",
                )
                entries.append(
                    {
                        "id": plan_id,
                        "phase": phase_id,
                        "workstream": ws_id,
                        "tier": tier,
                        "priority": PRIORITY[tier],
                        "lane": cfg["lane"],
                        "slot": slot,
                        "competitor": comp["name"],
                        "competitor_row": comp["row"],
                        "competitor_slug": comp["slug"],
                        "title": task[:200],
                        "path": rel,
                        "status": "backlog",
                        "verify": cfg["verify"],
                        "market_ssot": "docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md",
                        "portfolio_lesson": comp["lesson"],
                        "source_links": comp["links"],
                        "implementation": f"{comp['name']} {ws_label} -> buyer-visible proof -> {STACK_SURFACES[cfg['stack_key']]['primary']}",
                        "agent_tag": cfg["agent"],
                        "agent_prompt": f"PLAN WITH NO ASF — {plan_id}: {task[:120]}",
                    }
                )

    registry = {
        "schema_version": GENERATOR_VERSION,
        "library": f"{cfg['library']}-locked",
        "locked": True,
        "count": len(entries),
        "generated_at": now,
        "upgraded_at": now,
        "agent": cfg["agent"],
        "repo": cfg["repo"],
        "stack": cfg["stack"],
        "grid": "20 competitors × 5 workstreams × 10 tasks = 1000",
        "trigger": "PLAN WITH NO ASF",
        "execution_plane": "cloud_forge",
        "pick_script": f"scripts/pick-{cfg['stack_key']}-competitor-mkt-plan.py",
        "run_script": f"bash scripts/plan-competitor-mkt-run.sh pick {cfg['stack_key']} 1",
        "forge_dispatch": "python3 scripts/portfolio_competitor_forge_dispatch_v1.py",
        "market_ssot": str(COMP_DOC.relative_to(SOURCEA_ROOT)),
        "generator": "scripts/generate_portfolio_competitor_1000_plans_v1.py",
        "generator_version": GENERATOR_VERSION,
        "phases": phases,
        "workstreams": [{"id": w[0], "label": w[1]} for w in WORKSTREAMS],
        "stack_surfaces": STACK_SURFACES[cfg["stack_key"]],
        "tiers": [
            {"id": "T0", "description": TIER_DEPTH["T0"]},
            {"id": "T1", "description": TIER_DEPTH["T1"]},
            {"id": "T2", "description": TIER_DEPTH["T2"]},
            {"id": "T3", "description": TIER_DEPTH["T3"]},
        ],
        "plans": entries,
    }

    pack.mkdir(parents=True, exist_ok=True)
    (pack / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    lock_path = pack.parent / f"{cfg['stack_key'].upper()}-COMPETITOR-1000-LOCK.md"
    lock_path.write_text(
        f"""# {cfg['stack']} Competitor 1000 — LOCKED v2

**Saved:** {now} · **Authority:** ASF · **Count:** 1000 · **Generator:** v{GENERATOR_VERSION}
**SSOT:** `{COMP_DOC.name}` · **Grid:** 20 competitors × 50 plans (5 workstreams × 10 tasks)
**Registry:** `{pack.name}/REGISTRY.json`

## Upgrade v2

- Full competitor table fields in every prompt
- Stack-specific surfaces (not generic PRIORITY theater)
- 10 distinct tasks per workstream (not repeated stems)

## Pick + FORGE cloud (Mac observes only)

```bash
bash ~/Desktop/SourceA/scripts/plan-competitor-mkt-run.sh pick {cfg['stack_key']} 1
bash ~/Desktop/SourceA/scripts/plan-competitor-mkt-run.sh dispatch-forge {cfg['stack_key']} --dry-run
python3 ~/Desktop/SourceA/scripts/pick-{cfg['stack_key']}-competitor-mkt-plan.py --any-tier --limit 3 --prompt
```

Regenerate + validate:

```bash
python3 ~/Desktop/SourceA/scripts/generate_portfolio_competitor_1000_plans_v1.py
python3 ~/Desktop/SourceA/scripts/validate_portfolio_competitor_1000_v1.py
```
""",
        encoding="utf-8",
    )
    return {"stack": cfg["stack"], "count": len(entries), "pack": str(pack), "version": GENERATOR_VERSION}


def validate_pack(pack: Path) -> list[str]:
    errors: list[str] = []
    reg_path = pack / "REGISTRY.json"
    if not reg_path.is_file():
        return [f"Missing {reg_path}"]
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    if reg.get("schema_version") != GENERATOR_VERSION:
        errors.append(f"{pack.name}: schema_version != {GENERATOR_VERSION}")
    if reg.get("count") != 1000 or len(reg.get("plans", [])) != 1000:
        errors.append(f"{pack.name}: count != 1000")
    if len(reg.get("phases", [])) != 20:
        errors.append(f"{pack.name}: phases != 20")
    ids = [p["id"] for p in reg["plans"]]
    if len(ids) != len(set(ids)):
        errors.append(f"{pack.name}: duplicate plan ids")
    for p in reg["plans"]:
        md = pack / p["path"]
        if not md.is_file():
            errors.append(f"Missing prompt {p['path']}")
            continue
        body = md.read_text(encoding="utf-8")
        if "**Version:** 2" not in body:
            errors.append(f"{p['id']}: missing v2 header")
        if p["competitor"] not in body:
            errors.append(f"{p['id']}: competitor name missing in md")
        if "Implementation extraction" not in body:
            errors.append(f"{p['id']}: missing implementation section")
    return errors


def main() -> None:
    if not COMP_DOC.is_file():
        raise SystemExit(f"Missing {COMP_DOC}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    competitors = parse_competitors(COMP_DOC)
    if len(competitors) != 100:
        raise SystemExit(f"Expected 100 competitors in doc, parsed {len(competitors)}")

    results = []
    all_errors: list[str] = []
    for cfg in STACKS:
        results.append(generate_stack(cfg, competitors, now))
        all_errors.extend(validate_pack(cfg["pack_root"]))

    summary_path = SOURCEA_ROOT / "data" / "portfolio-competitor-1000-manifest-v1.json"
    summary_path.write_text(
        json.dumps(
            {
                "schema": "portfolio-competitor-1000-manifest-v1",
                "generator_version": GENERATOR_VERSION,
                "generated_at": now,
                "market_ssot": "docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md",
                "stacks": results,
                "validation_errors": all_errors,
                "ok": len(all_errors) == 0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    out = {"ok": len(all_errors) == 0, "generated_at": now, "version": GENERATOR_VERSION, "stacks": results}
    if all_errors:
        out["errors"] = all_errors[:20]
        out["error_count"] = len(all_errors)
    print(json.dumps(out, indent=2))
    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
