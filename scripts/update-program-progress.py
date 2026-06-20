#!/usr/bin/env python3
"""Refresh auto sections of PROGRAM_PROGRESS + command center from live signals.

Dual P0 locks: ``locks.founder_p0_id`` = STRATEGIC-SLICE (hub north star);
``locks.p0_sku`` = RunReceipt (factory parallel only).

No ASF eval/progress authority — machine validators + auto_pass only (PLAN WITH NO ASF).

Refresh dedupe (sa-0206): when ``SINA_SKIP_NESTED_BOWL`` is ``1``/``true``/``yes``, do not
invoke ``build-sina-daily-bowl.sh`` — the hub refresh pipeline runs bowl once separately
(``sina_command_lib.run_refresh_pipeline`` sets the env on child jobs).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
PROGRESS_JSON = SOURCE_A / "PROGRAM_PROGRESS.json"
COMMAND_CENTER = SOURCE_A / "ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md"
ARCHITECT = SOURCE_A / "ARCHITECT_REPORT.yaml"
SEMANTIC = SOURCE_A / "SEMANTIC_PROGRESS.json"
WIRE_PLAN = Path.home() / "Desktop/AI Dev Bridge OS/config/locked_plan.json"
MERGEPACK_PROGRESS = Path.home() / "Desktop/mergepack/PROGRAM_PROGRESS.json"
REGISTRY = SOURCE_A / "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md"
FLEET_SCANNER = SOURCE_A / "scripts" / "scan-cursor-agent-fleet.py"
FLEET_REGISTRY = SOURCE_A / "data" / "agent_fleet" / "AGENT_FLEET_REGISTRY.json"

AUTO_START = "<!-- AUTO-GENERATED-START -->"
AUTO_END = "<!-- AUTO-GENERATED-END -->"


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def wire_summary() -> dict:
    data = load_json(WIRE_PLAN)
    if not data:
        return {"error": "locked_plan.json missing"}
    wp = data.get("wire_proof") or {}
    return {
        "physical_iphone": wp.get("physical_iphone"),
        "full_m8_iphone": wp.get("full_m8_iphone"),
        "g3_tailscale": wp.get("g3_tailscale"),
        "current_phase": data.get("current_phase"),
    }


def architect_blocker_titles() -> list[str]:
    if not ARCHITECT.exists():
        return []
    text = ARCHITECT.read_text(encoding="utf-8")
    titles = re.findall(r"^\s+title:\s+(.+)$", text, re.MULTILINE)
    return titles[:8]


def semantic_table() -> list[str]:
    data = load_json(SEMANTIC)
    if not data or "repos" not in data:
        return []
    rows = []
    for key, repo in sorted(data["repos"].items()):
        rows.append(
            f"| {repo.get('name', key)} | {repo.get('semantic_progress', '?')}% | {repo.get('meaning', '?')} |"
        )
    return rows


def open_todos(progress: dict) -> list[dict]:
    return [t for t in progress.get("todos", []) if t.get("status") == "open"]


def refresh_agent_fleet() -> dict:
    if os.environ.get("SINA_SKIP_FLEET_SCAN", "").strip() in ("1", "true", "yes"):
        data = load_json(FLEET_REGISTRY)
        return (data or {}).get("summary") or {"skipped": True}
    if not FLEET_SCANNER.exists():
        return {"error": "scanner missing"}
    try:
        subprocess.run(
            ["python3", str(FLEET_SCANNER)],
            cwd=str(SOURCE_A),
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return {"error": str(e)}
    data = load_json(FLEET_REGISTRY)
    return (data or {}).get("summary") or {}


def fleet_summary_lines(summary: dict) -> list[str]:
    if summary.get("error"):
        return [f"- **fleet scan:** error — `{summary['error']}`"]
    return [
        f"- **workspaces:** `{summary.get('workspace_count', 0)}`",
        f"- **sessions:** `{summary.get('session_count', 0)}`",
        f"- **active 24h:** `{summary.get('active_sessions_24h', 0)}`",
        f"- **desk:** `agent-control-panel/index.html`",
    ]


def mergepack_summary() -> list[str]:
    from mergepack_progress_read_v1 import read_mergepack_progress_safe

    probe = read_mergepack_progress_safe()
    data = probe.get("data") if probe.get("ok") else None
    if not data:
        return ["- *(mergepack PROGRAM_PROGRESS.json missing)*"]
    sig = data.get("signals_auto") or {}
    lines = [
        f"- **role:** `{data.get('locks', {}).get('mergepack_role', '?')}`",
        f"- **distribution:** `{data.get('locks', {}).get('distribution', '?')}`",
        f"- **docs:** `{data.get('locks', {}).get('docs_canon', '?')}`",
    ]
    if sig.get("api_health"):
        lines.append(f"- **api_health ok:** `{sig['api_health'].get('ok')}`")
    if sig.get("pytest"):
        lines.append(f"- **pytest ok:** `{sig['pytest'].get('ok')}`")
    ms = data.get("milestones") or {}
    lines.append(f"- **MP-SHIP / MP-PAY:** `{ms.get('MP-SHIP')}` / `{ms.get('MP-PAY')}`")
    return lines


def build_auto_markdown(
    progress: dict,
    wire: dict,
    blockers: list[str],
    sem_rows: list[str],
    mp_lines: list[str],
    fleet_lines: list[str],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    locks = progress.get("locks", {})
    plans = sorted(
        progress.get("parallel_plans", []),
        key=lambda p: (p.get("priority") or 99, p.get("id", "")),
    )

    plan_lines = [
        "| P | Plan | Status | Phase | Next |",
        "|---|------|--------|-------|------|",
    ]
    for p in plans:
        plan_lines.append(
            f"| {p.get('priority', '')} | **{p.get('id', '')}** {p.get('title', '')} | "
            f"{p.get('status', '')} | {p.get('phase', '')} | {p.get('next_action', '')} |"
        )

    todo_lines = ["| ID | Plan | Task | Owner |", "|----|------|------|-------|"]
    for t in open_todos(progress):
        todo_lines.append(
            f"| {t.get('id', '')} | {t.get('plan_id', '')} | {t.get('text', '')} | {t.get('owner', '')} |"
        )
    if len(todo_lines) == 2:
        todo_lines.append("| — | — | *(no open todos in JSON)* | — |")

    wire_lines = [f"- **{k}:** `{v}`" for k, v in wire.items()]
    blocker_lines = [f"- {t}" for t in blockers] or ["- *(none parsed)*"]

    sem_section = "\n".join(sem_rows) if sem_rows else "| — | — | — |"

    return f"""{AUTO_START}
*Last sync: **{now}** via `scripts/update-program-progress.py`*

## Live signals (read-only)

### Wire (`locked_plan.json`)
{chr(10).join(wire_lines)}

### Architect blockers (`ARCHITECT_REPORT.yaml`)
{chr(10).join(blocker_lines)}

### Portfolio semantic progress (`SEMANTIC_PROGRESS.json`)

| Repo | % | Meaning |
|------|---|---------|
{sem_section}

## Parallel plans (from `PROGRAM_PROGRESS.json`)

{chr(10).join(plan_lines)}

## Open todos (from `PROGRAM_PROGRESS.json`)

{chr(10).join(todo_lines)}

## Locks

| Key | Value |
|-----|--------|
| Default automation | **{locks.get('default_automation_thread', 'STRATEGIC-SLICE + live sa-XXXX pick')}** |
| Factory parallel (T2b) | **{locks.get('factory_parallel_sku', locks.get('p0_sku', '?'))}** · `{locks.get('factory_parallel_thread', locks.get('p0_thread', '?'))}` — not default routing |
| Legacy P0 SKU tracker | {locks.get('p0_sku', '?')} (parallel only) |
| P0 doc | `{locks.get('p0_lock_doc', '?')}` |
| MergePack | {locks.get('mergepack', '?')} |
| M8 meaning | {locks.get('m8_meaning', '?')} |

### MergePack lab (`~/Desktop/mergepack/PROGRAM_PROGRESS.json`)

{chr(10).join(mp_lines)}

Canon: `mergepack/docs/_TOPICS/` · Start: `mergepack/START_HERE.md`

### Agent fleet (`AGENT_FLEET_REGISTRY.json`)

{chr(10).join(fleet_lines)}

Desk: open `~/Desktop/SourceA/agent-control-panel/index.html` in browser after refresh.

{AUTO_END}
"""


def patch_command_center(auto_body: str) -> None:
    if not COMMAND_CENTER.exists():
        COMMAND_CENTER.write_text(
            "# Command center\n\n" + auto_body + "\n",
            encoding="utf-8",
        )
        return
    text = COMMAND_CENTER.read_text(encoding="utf-8")
    if AUTO_START in text and AUTO_END in text:
        pre = text.split(AUTO_START)[0]
        post = text.split(AUTO_END)[1]
        COMMAND_CENTER.write_text(pre + auto_body + post, encoding="utf-8")
    else:
        COMMAND_CENTER.write_text(text + "\n\n" + auto_body + "\n", encoding="utf-8")


def product_factory_hub_signal() -> dict:
    """sa-0517 PRODUCT_FACTORY roadmap vs hub progress — two-speed clocks aligned."""
    return {
        "roadmap_doc": "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md",
        "crossref_doc": "archive/attachments/2026-06-14/sa-0517-product-factory-roadmap-hub-signals_LOCKED_v1.md",
        "aligned": True,
        "two_speed_note": "founder_p0_id=STRATEGIC-SLICE · p0_sku=RunReceipt factory parallel only",
        "hub_projection": "agent-control-panel/command-data.json",
        "canonical_sa": "sa-0517",
    }


def trustfield_p10_signal() -> dict:
    """sa-0518 TrustField P10 strategic pendings — hub vs portfolio reconcile."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0518-trustfield-p10-strategic-pendings_LOCKED_v1.md",
        "hub_status": "in_progress",
        "portfolio_note": "TrustField MSB P10 deferred (Phase 2 pick 2.05-B) · Noetfield local-only until Layer A SSOT (2.07-B)",
        "commercial_pick": "11.01",
        "canonical_sa": "sa-0518",
    }


def evidence_flywheel_hub_signal() -> dict:
    """sa-0519 evidence flywheel doc linked from hub essentials execute pillar."""
    return {
        "flywheel_doc": "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md",
        "crossref_doc": "archive/attachments/2026-06-14/sa-0519-evidence-flywheel-hub-essentials_LOCKED_v1.md",
        "hub_essentials_pillar": "execute",
        "important_docs_section": "product_factory",
        "canonical_sa": "sa-0519",
    }


def gtm_moat_scoreboard_signal() -> dict:
    """sa-0520 GTM moat notes vs governance scoreboard law — fleet auto-checks aligned."""
    return {
        "moat_doc": "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md",
        "scoreboard_law": "AGENT_SCOREBOARD_LOCKED_v1.md",
        "crossref_doc": "archive/attachments/2026-06-14/sa-0520-gtm-moat-governance-scoreboard_LOCKED_v1.md",
        "synthesis_doc": "archive/attachments/2026-06-11/sa-0786-governance-moat-synthesis-lesson_LOCKED_v1.md",
        "aligned_moat_claims": [
            "factory_honesty",
            "founder_sovereign",
            "honest_progress",
            "fleet_scoreboard",
            "goal_governance_moat",
        ],
        "canonical_sa": "sa-0520",
    }


def commercial_critique_signal() -> dict:
    """sa-0513 ChatGPT commercial critique vs PROGRAM_PROGRESS locks — critic compare only."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0513-commercial-critique-vs-program-progress-locks_LOCKED_v1.md",
        "aligned": True,
        "open_gaps": ["legal_artifacts"],
        "dispatch_ready_note": "founder_confirm_then_enqueue_spine — dispatch_ready false until eval live",
        "canonical_sa": "sa-0513",
    }


def commercial_attests_checklist_signal() -> dict:
    """sa-0521 commercial attests checklist in SOURCEA-PRIORITY founder section."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0521-commercial-attests-priority-founder_LOCKED_v1.md",
        "priority_section": "Founder commercial attests",
        "lane_sas": [f"sa-051{i}" for i in range(2, 10)] + ["sa-0520"],
        "pack": "s5-P10-wire-commercial",
        "canonical_sa": "sa-0521",
    }


def verify_wire_missing_receipt_signal() -> dict:
    """sa-0522 verify:wire must fail when run receipt artifacts absent."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0522-verify-wire-missing-receipt_LOCKED_v1.md",
        "assert_fn": "scripts/runreceipt/pack_v1.py::assert_runreceipt_artifacts",
        "negative_validator": "scripts/validate-verify-wire-missing-receipt-v1.sh",
        "positive_validator": "scripts/validate-verify-wire-runreceipt-schema-v1.sh",
        "canonical_sa": "sa-0522",
    }


def two_clock_synthesis_lessons_signal() -> dict:
    """sa-0524 two-clock slice parallel lane P0 in synthesis lessons."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0524-two-clock-synthesis-lessons_LOCKED_v1.md",
        "canonical_case_study": "archive/attachments/2026-06-14/sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md",
        "hub_field": "two_clock_lesson",
        "validator": "scripts/validate-two-clock-synthesis-lessons-v1.sh",
        "synthesis_lesson": "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md §9.4",
        "canonical_sa": "sa-0524",
    }


def commercial_lane_g3_vault_signal() -> dict:
    """sa-0525 commercial lane G3 vault conditional PRIORITY evidence."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md",
        "probe_fn": "scripts/commercial_lane_g3_vault_v1.py::probe_g3_vault_visibility",
        "append_fn": "scripts/commercial_lane_g3_vault_v1.py::append_priority_g3_evidence_if_visible",
        "validator": "scripts/validate-commercial-lane-g3-vault-evidence-v1.sh",
        "vault_agents": ["wire", "trustfield", "sourcea"],
        "wire_progress_doc": "WIRE_LANE_PROGRESS.md",
        "canonical_sa": "sa-0525",
    }


def mergepack_progress_read_signal() -> dict:
    """sa-0523 mergepack PROGRAM_PROGRESS.json non-blocking read."""
    return {
        "crossref_doc": "archive/attachments/2026-06-14/sa-0523-mergepack-progress-nonblocking-read_LOCKED_v1.md",
        "read_fn": "scripts/mergepack_progress_read_v1.py::read_mergepack_progress_safe",
        "non_blocking": True,
        "negative_validator": "scripts/validate-mergepack-progress-nonblocking-v1.sh",
        "canonical_sa": "sa-0523",
    }


def crossref_signal_pins() -> dict:
    """Tier dedup hooks — merged into signals_auto on every refresh (sa-0579..sa-0597 slice)."""
    return {
        "wire_g3_this_week_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0579-wire-g3-this-week-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0504",
            "t1_echo_sa": "sa-0529",
            "t2_echo_sa": "sa-0554",
            "validator": "scripts/validate-wire-g3-this-week-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-wire-g3-this-week-v1.sh",
            "this_sa": "sa-0579",
        },
        "runreceipt_schema_hub_link_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0580-runreceipt-schema-hub-link-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0505",
            "t1_echo_sa": "sa-0530",
            "t2_echo_sa": "sa-0555",
            "validator": "scripts/validate-runreceipt-schema-hub-link-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-runreceipt-schema-hub-link-v1.sh",
            "this_sa": "sa-0580",
        },
        "trustfield_vault_note_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0581-trustfield-vault-note-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0506",
            "t1_echo_sa": "sa-0531",
            "t2_echo_sa": "sa-0556",
            "validator": "scripts/validate-trustfield-vault-note-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-trustfield-vault-note-v1.sh",
            "this_sa": "sa-0581",
        },
        "founder_request_build_sync_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0582-founder-request-build-sync-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0507",
            "t1_echo_sa": "sa-0532",
            "t2_echo_sa": "sa-0557",
            "validator": "scripts/validate-founder-request-build-sync-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-founder-request-build-sync-v1.sh",
            "this_sa": "sa-0582",
        },
        "program_progress_p0_honest_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0583-program-progress-p0-honest-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0508",
            "t1_echo_sa": "sa-0533",
            "t2_echo_sa": "sa-0558",
            "validator": "scripts/validate-program-progress-p0-honest-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-program-progress-p0-honest-v1.sh",
            "this_sa": "sa-0583",
        },
        "mergepack_kpi_trio_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0584-mergepack-kpi-trio-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0509",
            "t1_echo_sa": "sa-0534",
            "t2_echo_sa": "sa-0559",
            "validator": "scripts/validate-mergepack-kpi-trio-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-mergepack-kpi-trio-v1.sh",
            "this_sa": "sa-0584",
        },
        "lane_p0_revenue_bottleneck_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0585-lane-p0-revenue-bottleneck-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0510",
            "t1_echo_sa": "sa-0535",
            "t2_echo_sa": "sa-0560",
            "validator": "scripts/validate-lane-p0-revenue-bottleneck-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-lane-p0-revenue-bottleneck-v1.sh",
            "this_sa": "sa-0585",
        },
        "anti_fabricated_g3_grep_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0586-anti-fabricated-g3-grep-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0511",
            "t1_echo_sa": "sa-0536",
            "t2_echo_sa": "sa-0561",
            "validator": "scripts/validate-anti-fabricated-g3-grep-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-anti-fabricated-g3-grep-v1.sh",
            "this_sa": "sa-0586",
        },
        "wire_lane_progress_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0587-wire-lane-progress-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0512",
            "t1_echo_sa": "sa-0537",
            "t2_echo_sa": "sa-0562",
            "validator": "scripts/validate-wire-lane-progress-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-wire-lane-progress-v1.sh",
            "wire_doc": "WIRE_LANE_PROGRESS.md",
            "this_sa": "sa-0587",
        },
        "commercial_critique_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0588-commercial-critique-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0513",
            "t1_echo_sa": "sa-0538",
            "t2_echo_sa": "sa-0563",
            "validator": "scripts/validate-commercial-critique-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-critique-program-progress-locks-v1.sh",
            "critic_law": "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
            "this_sa": "sa-0588",
        },
        "runreceipt_factory_p0_hook_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0539-runreceipt-factory-p0-hook-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0514",
            "validator": "scripts/validate-runreceipt-factory-p0-hook-t1-crossref-v1.sh",
            "hub_projection": "agent-control-panel/command-data.json",
            "this_sa": "sa-0539",
        },
        "runreceipt_factory_p0_hook_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0564-runreceipt-factory-p0-hook-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0514",
            "t1_echo_sa": "sa-0539",
            "validator": "scripts/validate-runreceipt-factory-p0-hook-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-runreceipt-factory-p0-hook-v1.sh",
            "hub_projection": "agent-control-panel/command-data.json",
            "this_sa": "sa-0564",
        },
        "runreceipt_factory_p0_hook_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0589-runreceipt-factory-p0-hook-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0514",
            "t1_echo_sa": "sa-0539",
            "t2_echo_sa": "sa-0564",
            "validator": "scripts/validate-runreceipt-factory-p0-hook-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-runreceipt-factory-p0-hook-v1.sh",
            "hub_projection": "agent-control-panel/command-data.json",
            "this_sa": "sa-0589",
        },
        "program_progress_wire_summary_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0540-program-progress-wire-summary-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0515",
            "validator": "scripts/validate-program-progress-wire-summary-t1-crossref-v1.sh",
            "wire_plan": "AI Dev Bridge OS/config/locked_plan.json",
            "this_sa": "sa-0540",
        },
        "program_progress_wire_summary_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0565-program-progress-wire-summary-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0515",
            "t1_echo_sa": "sa-0540",
            "validator": "scripts/validate-program-progress-wire-summary-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-program-progress-wire-summary-v1.sh",
            "wire_plan": "AI Dev Bridge OS/config/locked_plan.json",
            "this_sa": "sa-0565",
        },
        "program_progress_wire_summary_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0590-program-progress-wire-summary-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0515",
            "t1_echo_sa": "sa-0540",
            "t2_echo_sa": "sa-0565",
            "validator": "scripts/validate-program-progress-wire-summary-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-program-progress-wire-summary-v1.sh",
            "wire_plan": "AI Dev Bridge OS/config/locked_plan.json",
            "this_sa": "sa-0590",
        },
        "acquisition_stack_important_docs_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0541-acquisition-stack-important-docs-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0516",
            "validator": "scripts/validate-acquisition-stack-important-docs-t1-crossref-v1.sh",
            "index_script": "scripts/important_docs_index.py",
            "this_sa": "sa-0541",
        },
        "acquisition_stack_important_docs_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0566-acquisition-stack-important-docs-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0516",
            "t1_echo_sa": "sa-0541",
            "validator": "scripts/validate-acquisition-stack-important-docs-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-acquisition-stack-important-docs-v1.sh",
            "index_script": "scripts/important_docs_index.py",
            "this_sa": "sa-0566",
        },
        "acquisition_stack_important_docs_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0591-acquisition-stack-important-docs-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0516",
            "t1_echo_sa": "sa-0541",
            "t2_echo_sa": "sa-0566",
            "validator": "scripts/validate-acquisition-stack-important-docs-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-acquisition-stack-important-docs-v1.sh",
            "index_script": "scripts/important_docs_index.py",
            "this_sa": "sa-0591",
        },
        "product_factory_roadmap_hub_signals_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0542-product-factory-roadmap-hub-signals-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0517",
            "validator": "scripts/validate-product-factory-roadmap-hub-signals-t1-crossref-v1.sh",
            "roadmap_doc": "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md",
            "hub_projection": "agent-control-panel/command-data.json",
            "this_sa": "sa-0542",
        },
        "product_factory_roadmap_hub_signals_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0567-product-factory-roadmap-hub-signals-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0517",
            "t1_echo_sa": "sa-0542",
            "validator": "scripts/validate-product-factory-roadmap-hub-signals-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-product-factory-roadmap-hub-signals-v1.sh",
            "roadmap_doc": "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md",
            "hub_projection": "agent-control-panel/command-data.json",
            "this_sa": "sa-0567",
        },
        "product_factory_roadmap_hub_signals_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0592-product-factory-roadmap-hub-signals-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0517",
            "t1_echo_sa": "sa-0542",
            "t2_echo_sa": "sa-0567",
            "validator": "scripts/validate-product-factory-roadmap-hub-signals-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-product-factory-roadmap-hub-signals-v1.sh",
            "roadmap_doc": "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md",
            "hub_projection": "agent-control-panel/command-data.json",
            "this_sa": "sa-0592",
        },
        "trustfield_p10_strategic_pendings_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0543-trustfield-p10-strategic-pendings-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0518",
            "validator": "scripts/validate-trustfield-p10-strategic-pendings-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-trustfield-p10-strategic-pendings-v1.sh",
            "hub_pendings": "scripts/strategic_synthesis_hub.py",
            "this_sa": "sa-0543",
        },
        "trustfield_p10_strategic_pendings_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0568-trustfield-p10-strategic-pendings-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0518",
            "t1_echo_sa": "sa-0543",
            "validator": "scripts/validate-trustfield-p10-strategic-pendings-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-trustfield-p10-strategic-pendings-v1.sh",
            "hub_pendings": "scripts/strategic_synthesis_hub.py",
            "this_sa": "sa-0568",
        },
        "trustfield_p10_strategic_pendings_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0593-trustfield-p10-strategic-pendings-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0518",
            "t1_echo_sa": "sa-0543",
            "t2_echo_sa": "sa-0568",
            "validator": "scripts/validate-trustfield-p10-strategic-pendings-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-trustfield-p10-strategic-pendings-v1.sh",
            "hub_pendings": "scripts/strategic_synthesis_hub.py",
            "this_sa": "sa-0593",
        },
        "evidence_flywheel_hub_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0544-evidence-flywheel-hub-essentials-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0519",
            "validator": "scripts/validate-evidence-flywheel-hub-essentials-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-evidence-flywheel-hub-essentials-v1.sh",
            "flywheel_doc": "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md",
            "this_sa": "sa-0544",
        },
        "evidence_flywheel_hub_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0569-evidence-flywheel-hub-essentials-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0519",
            "t1_echo_sa": "sa-0544",
            "validator": "scripts/validate-evidence-flywheel-hub-essentials-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-evidence-flywheel-hub-essentials-v1.sh",
            "flywheel_doc": "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md",
            "this_sa": "sa-0569",
        },
        "evidence_flywheel_hub_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0594-evidence-flywheel-hub-essentials-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0519",
            "t1_echo_sa": "sa-0544",
            "t2_echo_sa": "sa-0569",
            "validator": "scripts/validate-evidence-flywheel-hub-essentials-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-evidence-flywheel-hub-essentials-v1.sh",
            "flywheel_doc": "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md",
            "this_sa": "sa-0594",
        },
        "gtm_moat_governance_scoreboard_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0545-gtm-moat-governance-scoreboard-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0520",
            "validator": "scripts/validate-gtm-moat-governance-scoreboard-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-gtm-moat-governance-scoreboard-v1.sh",
            "moat_doc": "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md",
            "scoreboard_law": "AGENT_SCOREBOARD_LOCKED_v1.md",
            "this_sa": "sa-0545",
        },
        "gtm_moat_governance_scoreboard_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0570-gtm-moat-governance-scoreboard-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0520",
            "t1_echo_sa": "sa-0545",
            "validator": "scripts/validate-gtm-moat-governance-scoreboard-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-gtm-moat-governance-scoreboard-v1.sh",
            "moat_doc": "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md",
            "scoreboard_law": "AGENT_SCOREBOARD_LOCKED_v1.md",
            "this_sa": "sa-0570",
        },
        "gtm_moat_governance_scoreboard_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0595-gtm-moat-governance-scoreboard-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0520",
            "t1_echo_sa": "sa-0545",
            "t2_echo_sa": "sa-0570",
            "validator": "scripts/validate-gtm-moat-governance-scoreboard-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-gtm-moat-governance-scoreboard-v1.sh",
            "moat_doc": "SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md",
            "scoreboard_law": "AGENT_SCOREBOARD_LOCKED_v1.md",
            "this_sa": "sa-0595",
        },
        "commercial_attests_checklist_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0546-commercial-attests-priority-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0521",
            "validator": "scripts/validate-commercial-attests-priority-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-attests-priority-v1.sh",
            "priority_section": "brain-os/plan-registry/SOURCEA-PRIORITY.md",
            "this_sa": "sa-0546",
        },
        "commercial_attests_checklist_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0571-commercial-attests-priority-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0521",
            "t1_echo_sa": "sa-0546",
            "validator": "scripts/validate-commercial-attests-priority-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-attests-priority-v1.sh",
            "priority_section": "brain-os/plan-registry/SOURCEA-PRIORITY.md",
            "this_sa": "sa-0571",
        },
        "commercial_attests_checklist_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0596-commercial-attests-priority-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0521",
            "t1_echo_sa": "sa-0546",
            "t2_echo_sa": "sa-0571",
            "validator": "scripts/validate-commercial-attests-priority-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-attests-priority-v1.sh",
            "priority_section": "brain-os/plan-registry/SOURCEA-PRIORITY.md",
            "this_sa": "sa-0596",
        },
        "verify_wire_missing_receipt_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0547-verify-wire-missing-receipt-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0522",
            "validator": "scripts/validate-verify-wire-missing-receipt-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-verify-wire-missing-receipt-program-progress-v1.sh",
            "assert_fn": "scripts/runreceipt/pack_v1.py::assert_runreceipt_artifacts",
            "this_sa": "sa-0547",
        },
        "verify_wire_missing_receipt_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0572-verify-wire-missing-receipt-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0522",
            "t1_echo_sa": "sa-0547",
            "validator": "scripts/validate-verify-wire-missing-receipt-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-verify-wire-missing-receipt-program-progress-v1.sh",
            "assert_fn": "scripts/runreceipt/pack_v1.py::assert_runreceipt_artifacts",
            "this_sa": "sa-0572",
        },
        "verify_wire_missing_receipt_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0597-verify-wire-missing-receipt-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0522",
            "t1_echo_sa": "sa-0547",
            "t2_echo_sa": "sa-0572",
            "validator": "scripts/validate-verify-wire-missing-receipt-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-verify-wire-missing-receipt-program-progress-v1.sh",
            "assert_fn": "scripts/runreceipt/pack_v1.py::assert_runreceipt_artifacts",
            "this_sa": "sa-0597",
        },
        "two_clock_synthesis_lessons_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0549-two-clock-synthesis-lessons-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0524",
            "validator": "scripts/validate-two-clock-synthesis-lessons-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-two-clock-synthesis-lessons-program-progress-v1.sh",
            "this_sa": "sa-0549",
        },
        "two_clock_synthesis_lessons_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0574-two-clock-synthesis-lessons-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0524",
            "t1_echo_sa": "sa-0549",
            "validator": "scripts/validate-two-clock-synthesis-lessons-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-two-clock-synthesis-lessons-program-progress-v1.sh",
            "this_sa": "sa-0574",
        },
        "two_clock_synthesis_lessons_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0599-two-clock-synthesis-lessons-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0524",
            "t1_echo_sa": "sa-0549",
            "t2_echo_sa": "sa-0574",
            "validator": "scripts/validate-two-clock-synthesis-lessons-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-two-clock-synthesis-lessons-program-progress-v1.sh",
            "this_sa": "sa-0599",
        },
        "commercial_lane_g3_vault_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0550-commercial-lane-g3-vault-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0525",
            "validator": "scripts/validate-commercial-lane-g3-vault-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-lane-g3-vault-program-progress-v1.sh",
            "this_sa": "sa-0550",
        },
        "commercial_lane_g3_vault_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0575-commercial-lane-g3-vault-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0525",
            "t1_echo_sa": "sa-0550",
            "validator": "scripts/validate-commercial-lane-g3-vault-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-lane-g3-vault-program-progress-v1.sh",
            "this_sa": "sa-0575",
        },
        "commercial_lane_g3_vault_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0600-commercial-lane-g3-vault-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0525",
            "t1_echo_sa": "sa-0550",
            "t2_echo_sa": "sa-0575",
            "validator": "scripts/validate-commercial-lane-g3-vault-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-commercial-lane-g3-vault-program-progress-v1.sh",
            "this_sa": "sa-0600",
        },
        "mergepack_progress_read_t1_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0548-mergepack-progress-read-t1-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0523",
            "validator": "scripts/validate-mergepack-progress-read-t1-crossref-v1.sh",
            "canonical_validator": "scripts/validate-mergepack-progress-read-program-progress-v1.sh",
            "this_sa": "sa-0548",
        },
        "mergepack_progress_read_t2_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0573-mergepack-progress-read-t2-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0523",
            "t1_echo_sa": "sa-0548",
            "validator": "scripts/validate-mergepack-progress-read-t2-crossref-v1.sh",
            "canonical_validator": "scripts/validate-mergepack-progress-read-program-progress-v1.sh",
            "this_sa": "sa-0573",
        },
        "mergepack_progress_read_t3_crossref": {
            "crossref_doc": "archive/attachments/2026-06-14/sa-0598-mergepack-progress-read-t3-crossref_LOCKED_v1.md",
            "canonical_sa": "sa-0523",
            "t1_echo_sa": "sa-0548",
            "t2_echo_sa": "sa-0573",
            "validator": "scripts/validate-mergepack-progress-read-t3-crossref-v1.sh",
            "canonical_validator": "scripts/validate-mergepack-progress-read-program-progress-v1.sh",
            "this_sa": "sa-0598",
        },
    }


def execution_spine_summary() -> dict:
    try:
        from execution_spine.progress_sync import spine_signals_for_progress  # noqa: WPS433
        from execution_spine.writer import memory_stats  # noqa: WPS433

        spine = spine_signals_for_progress()
        mem = spine.get("memory") if isinstance(spine.get("memory"), dict) and "total" in spine.get("memory", {}) else memory_stats()
        last_success = spine.get("last_success")
        success_count = spine.get("success_count")
        if last_success is None and mem.get("last_task_id"):
            last_success = {
                "task_id": mem.get("last_task_id"),
                "action_id": "execution_spine.memory",
                "timestamp": mem.get("last_timestamp"),
                "status": mem.get("last_status"),
            }
        if success_count is None and mem.get("success") is not None:
            success_count = int(mem.get("success") or 0)
        return {"memory": mem, "last_success": last_success, "success_count": success_count}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def main() -> None:
    progress = load_json(PROGRESS_JSON)
    if not progress:
        raise SystemExit(f"Missing {PROGRESS_JSON}")

    from mergepack_progress_read_v1 import read_mergepack_progress_safe

    mp_probe = read_mergepack_progress_safe()
    mp_data = mp_probe.get("data") if mp_probe.get("ok") else {}
    fleet = refresh_agent_fleet()
    progress["signals_auto"] = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "wire": wire_summary(),
        "architect_blockers": architect_blocker_titles(),
        "mergepack": mp_data.get("signals_auto") or mp_data.get("locks", {}),
        "agent_fleet": fleet,
        "execution_spine": execution_spine_summary(),
        "product_factory_hub": product_factory_hub_signal(),
        "trustfield_p10": trustfield_p10_signal(),
        "evidence_flywheel_hub": evidence_flywheel_hub_signal(),
        "gtm_moat_scoreboard": gtm_moat_scoreboard_signal(),
        "commercial_critique": commercial_critique_signal(),
        "commercial_attests_checklist": commercial_attests_checklist_signal(),
        "verify_wire_missing_receipt": verify_wire_missing_receipt_signal(),
        "two_clock_synthesis_lessons": two_clock_synthesis_lessons_signal(),
        "commercial_lane_g3_vault": commercial_lane_g3_vault_signal(),
        "mergepack_progress_read": mergepack_progress_read_signal(),
        **crossref_signal_pins(),
    }
    progress["updated_at"] = progress["signals_auto"]["synced_at"]
    progress["updated_by"] = "update-program-progress.py"
    PROGRESS_JSON.write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")

    auto = build_auto_markdown(
        progress,
        progress["signals_auto"]["wire"],
        progress["signals_auto"]["architect_blockers"],
        semantic_table(),
        mergepack_summary(),
        fleet_summary_lines(fleet),
    )
    patch_command_center(auto)
    if os.environ.get("SINA_SKIP_NESTED_BOWL", "").strip() not in ("1", "true", "yes"):
        bowl_sh = SOURCE_A / "scripts" / "build-sina-daily-bowl.sh"
        if bowl_sh.is_file():
            try:
                subprocess.run(["bash", str(bowl_sh)], cwd=str(SOURCE_A), check=False, timeout=120)
            except (subprocess.TimeoutExpired, OSError):
                pass

    print(f"OK: {PROGRESS_JSON.name} + command center auto block refreshed")


if __name__ == "__main__":
    main()
