#!/usr/bin/env python3
"""Build per-repo + semi-separate Cursor agent notices + Prompt OS ready_to_paste files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
OUT_DIR = SOURCE_A / "founder" / "repo-agent-notices"
PROMPTOS_PASTE = Path.home() / "Desktop/SinaPromptOS/outputs/ready_to_paste"
MASTER = SOURCE_A / "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md"
SEMI_MASTER = SOURCE_A / "SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md"

sys.path.insert(0, str(SOURCE_A / "scripts"))

from sina_command_lib import REPOS_REGISTRY, parse_repo_plan, _repo_root  # noqa: E402

UPDATED = "2026-06-04"
MAINSTREAM_SKIP = frozenset({"sourcea", "promptos", "mergepack", "wire"})
SEMI_LANE_IDS = frozenset({"wire", "cursor_os_pro", "mergepack", "promptos", "noetfield_cloud"})

REPO_TASKS: dict[str, dict] = {
    "trustfield": {
        "thread": "THREAD-PORTFOLIO",
        "headline": "TrustField — delivery & infra truth",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md (general — Essentials + hub)",
            "GLOBAL_BLOCKERS / B-001 if touching payments or postgres",
        ],
        "updated_tasks": [
            "Resolve or document B-001 (postgres vs no-card) — cite GLOBAL_BLOCKERS.json path",
            "One verifiable infra or compliance step toward trustfield.ca / api.trustfield.ca (Actions for deploy checks)",
            "Use Sina Command Essentials → TrustField lane — do not edit SourceA",
            "Private agent page: Agent hub → TrustField — one loop round when ASF assigns",
        ],
        "forbidden": ["~/Desktop/SourceA", "Noetfield cloud ship repo"],
    },
    "mono": {
        "thread": "THREAD-SUPERBRAIN",
        "headline": "SinaaiMonoRepo — Layer A Personal Database (P0)",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md",
            "data/L0-meta/004-ingestion-pipeline.md",
        ],
        "updated_tasks": [
            "P0: support Layer A — valid frontmatter on data/*.md entries you touch",
            "Help founder use hub Personal DB tab: imports/raw → scan → promote draft to L2",
            "Do not replace Command hub with mono command-center for daily founder ops (hub :13020 is SSOT UI)",
            "Governance/registry changes only when THREAD-SUPERBRAIN is active in this chat",
        ],
        "forbidden": ["Random reads across 50 SourceA files — use Essentials read chain"],
    },
    "virlux": {
        "thread": "THREAD-PORTFOLIO",
        "headline": "VIRLUX — live site & DNS",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "Live products tab for VIRLUX URLs",
        ],
        "updated_tasks": [
            "One ship-proof step: DNS, Vercel smoke, or public URL check (founder uses Actions, not Terminal)",
            "Update os/plan.json next task when done — evidence path in reply",
            "GTM/media tasks stay scoped to VIRLUX repo only",
        ],
        "forbidden": ["~/Desktop/SourceA", "MergePack thread work in this chat"],
    },
    "noetfield": {
        "thread": "THREAD-PORTFOLIO",
        "headline": "Noetfield **local** documents — hierarchy SSOT (not cloud ship)",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "HIERARCHY_INDEX.md + source_of_truth_registry.json",
        ],
        "updated_tasks": [
            "Validate one L0–L3 doc or registry row — local disk only (Noetfield-All-Documents)",
            "Promote or archive one _under-analysis item with evidence",
            "Never edit ~/Desktop/Noetfield — use **noetfield_cloud** chat + SEMI_NOTICE_noetfield_cloud_v1.md",
        ],
        "forbidden": ["~/Desktop/Noetfield (cloud)", "~/Desktop/SourceA"],
    },
    "seven77": {
        "thread": "THREAD-PORTFOLIO",
        "headline": "The 777 Foundation — web ops & cohort",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "ops/gate0-week1-execution.md when doing outreach",
        ],
        "updated_tasks": [
            "One Gate 0 or web ops step with evidence (/api/health, deploy note, or ops doc update)",
            "Supabase/migration work only with founder-approved scope",
            "Ship lane proof via Actions when wired — no founder npm in Terminal",
        ],
        "forbidden": ["~/Desktop/SourceA"],
    },
    "hq": {
        "thread": "THREAD-ECOSYSTEM",
        "headline": "SinaaiDataBase HQ — Command maintainer only",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md",
            "AGENT_GOVERNANCE_INDEX_LOCKED_v1.md",
        ],
        "updated_tasks": [
            "Maintain hub only when ASF asks — rebuild panel, fix Actions, audit E2E",
            "Keep Essentials NAV in sync with app.js (build fails if drift)",
            "P0 RunReceipt factory thread — do not steal MergePack growth thread",
            "Personal DB + Essentials are live — verify ?tab=personal-db after hub changes",
            "Rebuild repo + semi notices: python3 scripts/build_repo_agent_notices.py",
        ],
        "forbidden": [],
    },
}

SEMI_TASKS: dict[str, dict] = {
    "wire": {
        "thread": "THREAD-WIRE",
        "headline": "AI Dev Bridge OS — wire orchestrator (phone ↔ Mac, M8)",
        "not_mainstream": "Not a portfolio IMPLEMENT lane — ROLE-WIRE reports to ASF directly.",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md",
            "SourceA/founder/ASF_WIRE_AND_PHONE.md",
            "SourceA/WIRE_LANE_PROGRESS.md",
            "config/locked_plan.json → chat_lanes.ai_dev_bridge",
        ],
        "updated_tasks": [
            "Close **full_m8 on iPhone** — RUN SYSTEM must not end at smoke-only; record with --lane full_m8",
            "Close **G3 Tailscale** — proof:g3 + record:g3 with real run-id from phone (never placeholder)",
            "Standardize artifacts: run.jsonl + summary.json + HTML pack (P0 RunReceipt alignment)",
            "Default desk lane: full_m8 — smoke is test-only",
        ],
        "forbidden": [
            "Cursor OS Pro mobile/ / App Store parity (other chat)",
            "~/Desktop/SourceA edits (HQ chat only)",
            "Portfolio os/plan.json tasks as primary work",
        ],
        "hub_actions": "Actions → Open wire progress doc · Essentials → wire-devbridge tile",
    },
    "cursor_os_pro": {
        "thread": "THREAD-CURSOR-OS-PRO",
        "headline": "Cursor OS Pro — App Store SKU (IDE For Cursor)",
        "not_mainstream": "Separate program — paying customers, not internal orchestra.",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md (hub law only)",
            "SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md",
            "docs/PARALLEL_LANE_BOUNDARIES.md",
            "docs/SINGLE-SOURCE-OF-TRUTH.md",
            "SourceA/investor/SEPARATE_PROGRAM_CURSOR_OS_PRO.md",
        ],
        "updated_tasks": [
            "P-R/G-R: npm run check green + device regression on real iPhone",
            "One outcome toward TestFlight / App Store — reference parity in mobile/ only",
            "If user asks wire/RUN SYSTEM → redirect to AI Dev Bridge OS chat",
        ],
        "forbidden": [
            "AI Dev Bridge OS agent/ scripts/ desk / RUN SYSTEM",
            "SinaPromptOS dispatch-day / m8-now in this chat",
            "Five portfolio repos + SourceA",
            "ready_to_paste portfolio prompts as primary task list",
        ],
        "hub_actions": "Do not use portfolio Repos lane brief as SSOT — use SEMI_NOTICE_cursor_os_pro",
    },
    "mergepack": {
        "thread": "THREAD-MERGEPACK",
        "headline": "MergePack — revenue & evidence factory",
        "not_mainstream": "Utility lane — not one of five portfolio delivery repos.",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md",
            "PROGRAM_PROGRESS.json milestones",
        ],
        "updated_tasks": [
            "MergePack revenue ≠ M8 wire automation — keep threads separate",
            "One ship step: Vercel deployment protection off + public /health verify (Actions)",
            "KPI / form-PDF only in this chat — not wire proof",
        ],
        "forbidden": ["~/Desktop/SourceA", "THREAD-WIRE work in this chat"],
        "hub_actions": "Products tab · MergePack KPI action",
    },
    "promptos": {
        "thread": "THREAD-PROMPTOS",
        "headline": "SinaPromptOS — dispatch & paste orchestration",
        "not_mainstream": "Meta lane — generates prompts; does not implement product repos.",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md",
            "SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md",
        ],
        "updated_tasks": [
            "Morning dispatch + ready_to_paste for five repos + semi lanes when ASF runs Actions",
            "M8 paste safety — SinaPromptOS/docs/M8_INCIDENT_* before any inject",
            "Rebuild notices after law change: build_repo_agent_notices.py",
        ],
        "forbidden": [
            "Implementing trustfield/mono/virlux/noetfield/777 code as primary session",
            "~/Desktop/SourceA unless maintainer thread",
        ],
        "hub_actions": "Actions · Prompt OS UI mini-app",
    },
    "noetfield_cloud": {
        "thread": "THREAD-PORTFOLIO",
        "headline": "Noetfield cloud — GitHub ship repo (TLE, governance console, :13080)",
        "not_mainstream": "Twin of noetfield **local** (All-Documents). This chat = **implementation SSOT** only.",
        "must_read": [
            "SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md",
            "SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md",
            "docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md",
            "docs/ops/AGENT_READ_LINKS_LOCKED_v1.md (in-repo mirror — cloud VM entry)",
            "os/plan.json + os/SHIP_NOW.md",
            "docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md",
        ],
        "updated_tasks": [
            "One ship step from os/plan.json lane_a_sprint_map or sprint-trust-ledger-v1.2.md",
            "Run verify: scripts/verify-local-dev.sh or tle-smoke — evidence in reply",
            "Sync ops/private/sourceA from hub when EXECUTION_TRUTH drifts (founder Actions)",
            "Never edit ~/Desktop/Noetfield-All-Documents from this workspace (noetfield_local chat)",
        ],
        "forbidden": [
            "~/Desktop/Noetfield-All-Documents (local docs archive)",
            "~/Desktop/SourceA edits (HQ maintainer only)",
            "TrustField/VIRLUX delivery scope in this chat",
        ],
        "hub_actions": "Agent hub → noetfield_cloud pack · Live products · Actions",
    },
}

CURSOR_OS_PRO_SPEC: dict = {
    "id": "cursor_os_pro",
    "name": "Cursor OS Pro",
    "root_key": "Cursor OS Pro",
    "plan_rel": None,
    "workspace": "Cursor OS Pro",
    "lane": "App Store",
    "thread": "THREAD-CURSOR-OS-PRO",
    "plane": "Commercial SKU",
    "semantic_key": "cursor_os_pro",
}

NOETFIELD_CLOUD_SPEC: dict = {
    "id": "noetfield_cloud",
    "name": "Noetfield (cloud / GitHub ship)",
    "root_key": "Noetfield",
    "plan_rel": "os/plan.json",
    "workspace": "Noetfield",
    "lane": "Noetfield ship",
    "thread": "THREAD-PORTFOLIO",
    "plane": "SHIP",
    "semantic_key": "noetfield_cloud",
}

SEMI_ONLY_SPECS: list[dict] = [CURSOR_OS_PRO_SPEC, NOETFIELD_CLOUD_SPEC]


def _spec_for_semi(lane_id: str) -> dict:
    for extra in SEMI_ONLY_SPECS:
        if extra["id"] == lane_id:
            return dict(extra)
    for spec in REPOS_REGISTRY:
        if spec["id"] == lane_id:
            return spec
    raise KeyError(lane_id)


def _render_repo_notice(repo_id: str, spec: dict, plan: dict) -> str:
    meta = REPO_TASKS.get(repo_id) or REPO_TASKS.get("hq", {})
    root = _repo_root(spec) if repo_id != "hq" else Path.home() / "Desktop/SinaaiDataBase"
    tasks = meta.get("updated_tasks") or []
    reads = meta.get("must_read") or []
    forb = meta.get("forbidden") or []
    nt = plan.get("next_tasks") or []
    plan_lines = []
    for t in nt[:5]:
        plan_lines.append(f"  • {t.get('text', t) if isinstance(t, dict) else t}")

    return f"""# Repo agent notice — {spec.get('name', repo_id)}

**Last updated:** {UPDATED} · **Repo id:** `{repo_id}` · **Thread:** `{meta.get('thread', spec.get('thread', '—'))}`

> Paste this at the **start** of this Cursor chat after the general system update.  
> Master notice: `SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md`

---

## Headline

{meta.get('headline', spec.get('name', ''))}

**Workspace:** `{spec.get('workspace') or 'SinaaiDataBase'}`  
**Root:** `{root}`  
**Plane:** {spec.get('plane', '—')}

---

## Must read (this repo chat)

{chr(10).join(f'- {r}' for r in reads)}

---

## Updated tasks — do this week (repo-specific)

{chr(10).join(f'{i + 1}. {t}' for i, t in enumerate(tasks))}

---

## Live plan.json next tasks (verify logged)

{chr(10).join(plan_lines) if plan_lines else '  • (refresh hub Repos tab or run plan sync)'}

**Active focus:** {plan.get('active_focus') or '—'}

---

## Forbidden in this chat

{chr(10).join(f'- `{f}`' for f in forb) if forb else '- (see governance index)'}

---

## Hub shortcuts (founder)

| Tab | Use |
|-----|-----|
| Essentials | Full map — no duplicates |
| Track | Open commitments for this program |
| Repos | Copy lane brief (includes this notice) |
| Agent hub | Private agent loop for `{repo_id}` if configured |

---

## Session end

1. Line 1: `Active thread: {meta.get('thread', 'THREAD-???')}`  
2. Evidence paths + commands run  
3. VERIFY block per agent output contract  
4. Ingest YAML if delivery work shipped  

**Do not ask founder to use Terminal.**
"""


def _render_semi_notice(lane_id: str, spec: dict, plan: dict) -> str:
    meta = SEMI_TASKS[lane_id]
    root = _repo_root(spec)
    tasks = meta.get("updated_tasks") or []
    reads = meta.get("must_read") or []
    forb = meta.get("forbidden") or []
    nt = plan.get("next_tasks") or []
    plan_lines = [f"  • {t.get('text', t) if isinstance(t, dict) else t}" for t in nt[:5]]

    return f"""# Semi-separate lane notice — {spec.get('name', lane_id)}

**Last updated:** {UPDATED} · **Lane id:** `{lane_id}` · **Thread:** `{meta.get('thread', '—')}`  
**Kind:** Semi-separate (not one of five portfolio delivery lanes)

> Paste at the **start** of this Cursor chat.  
> Read first: `SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md` + `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md`

---

## Headline

{meta.get('headline', '')}

{meta.get('not_mainstream', '')}

**Workspace:** `{spec.get('workspace') or lane_id}`  
**Root:** `{root}`  
**Plane:** {spec.get('plane', '—')}

---

## Must read (this chat only)

{chr(10).join(f'- {r}' for r in reads)}

---

## Updated tasks — do this week (lane-specific)

{chr(10).join(f'{i + 1}. {t}' for i, t in enumerate(tasks))}

---

## Live plan / wire_proof (verify logged)

{chr(10).join(plan_lines) if plan_lines else '  • (refresh hub Repos or wire:preflight)'}

**Active focus:** {plan.get('active_focus') or '—'}

---

## Forbidden in this chat

{chr(10).join(f'- `{f}`' for f in forb)}

---

## Hub (founder — not daily SSOT for this lane)

{meta.get('hub_actions', 'Essentials for ecosystem awareness only.')}

---

## Session end

1. Line 1: `Active thread: {meta.get('thread', 'THREAD-???')}`  
2. Evidence paths + commands run  
3. VERIFY block per agent output contract  
4. **Do not** import five-repo portfolio tasks as your primary outcome  

**Do not ask founder to use Terminal.**
"""


def _write_paste(*, lane_id: str, spec: dict, body: str, kind: str, write_promptos: bool) -> str | None:
    sk = spec.get("semantic_key") or lane_id
    paste_name = f"ready_to_paste_{sk}.txt"
    header = [
        f"══ SINA COMMAND — {kind.upper()} NOTICE ══",
        f"Last updated: {UPDATED}",
        f"Lane: {spec.get('name', lane_id)} · Thread: "
        f"{REPO_TASKS.get(lane_id, SEMI_TASKS.get(lane_id, {})).get('thread', spec.get('thread', '—'))}",
        "Read fully. Line 1 = Active thread. Line 2 = one outcome this session.",
        "",
        body,
        "",
        "══ END NOTICE ══",
        "",
    ]
    full = "\n".join(header)
    if write_promptos:
        PROMPTOS_PASTE.mkdir(parents=True, exist_ok=True)
        (PROMPTOS_PASTE / paste_name).write_text(full, encoding="utf-8")
        return str(PROMPTOS_PASTE / paste_name)
    return None


def build_all(*, write_promptos: bool = True) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    mainstream: list[dict] = []
    semi: list[dict] = []

    targets = list(REPOS_REGISTRY)
    if not any(r["id"] == "hq" for r in targets):
        targets.append(
            {
                "id": "hq",
                "name": "SinaaiDataBase HQ",
                "workspace": "SinaaiDataBase",
                "thread": "THREAD-ECOSYSTEM",
                "plane": "HQ steward",
                "semantic_key": None,
                "plan_rel": None,
                "root_key": "SinaaiDataBase",
            }
        )

    for spec in targets:
        rid = spec["id"]
        if rid in MAINSTREAM_SKIP:
            continue
        plan = parse_repo_plan(spec) if spec.get("plan_rel") else {}
        body = _render_repo_notice(rid, spec, plan)
        path = OUT_DIR / f"REPO_NOTICE_{rid}_v1.md"
        path.write_text(body, encoding="utf-8")
        paste_file = _write_paste(
            lane_id=rid, spec=spec, body=body, kind="mainstream", write_promptos=write_promptos
        )
        mainstream.append(
            {
                "repo_id": rid,
                "name": spec.get("name"),
                "notice_path": str(path.relative_to(SOURCE_A)),
                "paste_file": paste_file,
                "thread": REPO_TASKS.get(rid, {}).get("thread"),
                "kind": "mainstream",
            }
        )

    for lane_id in sorted(SEMI_LANE_IDS):
        spec = _spec_for_semi(lane_id)
        plan = parse_repo_plan(spec) if spec.get("plan_rel") else {}
        body = _render_semi_notice(lane_id, spec, plan)
        path = OUT_DIR / f"SEMI_NOTICE_{lane_id}_v1.md"
        path.write_text(body, encoding="utf-8")
        paste_file = _write_paste(
            lane_id=lane_id, spec=spec, body=body, kind="semi-separate", write_promptos=write_promptos
        )
        semi.append(
            {
                "lane_id": lane_id,
                "name": spec.get("name"),
                "notice_path": str(path.relative_to(SOURCE_A)),
                "paste_file": paste_file,
                "thread": SEMI_TASKS[lane_id].get("thread"),
                "kind": "semi_separate",
            }
        )

    index = {
        "ok": True,
        "updated": UPDATED,
        "master_notice": str(MASTER.relative_to(SOURCE_A)),
        "semi_master_notice": str(SEMI_MASTER.relative_to(SOURCE_A)),
        "repos": mainstream,
        "semi_separate": semi,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index


def main() -> int:
    write_promptos = "--no-promptos" not in sys.argv
    result = build_all(write_promptos=write_promptos)
    print(f"OK: {len(result['repos'])} mainstream notices → {OUT_DIR}")
    print(f"OK: {len(result['semi_separate'])} semi-separate notices (wire · Cursor OS Pro · Noetfield cloud · …)")
    if write_promptos:
        print(f"OK: ready_to_paste → {PROMPTOS_PASTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
