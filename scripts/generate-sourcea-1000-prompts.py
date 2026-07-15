#!/usr/bin/env python3
"""Generate 1000 concrete SourceA hub prompts (10 phases × 4 tiers × 25). LOCKED NO-ASF pack."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "os" / "plan-library" / "sourcea-1000"
PROMPTS = PACK / "prompts"
AGENT = "AGENT-AUTO-SOURCEA"
TAG = "AGENT-AUTO-SOURCEA"

PHASES = [
    ("phase-s0-ssot-alignment", "SSOT drift, GPT/Claude synthesis, honest_score, strategic hub"),
    ("phase-s1-eval-dispatch", "Eval-1b live CI, dispatch policy, grounding, gate receipts"),
    ("phase-s2-hub-build-ci", "strict build, validators, find_critical_bugs, backend E2E"),
    ("phase-s3-scoreboard-fleet", "auto-green scoreboard, essay discourse, governance fleet"),
    ("phase-s4-spine-loop", "spine bridge, graph executor, event bus, execution memory"),
    ("phase-s5-commercial-lanes", "RunReceipt, verify:wire, TrustField, Wire G3, PROGRAM_PROGRESS"),
    ("phase-s6-wtm-pre-llm", "D1–D16 packet, L0–L16 layers, ENFORCE, context assembly"),
    ("phase-s7-council-governance", "Council room, rules-in-charge, mind share, unification engine"),
    ("phase-s8-hub-ui-ux", "Hub 2 Machine Hub /machines/ — pending registry, scheduled receipts, sibling surface (not Sina Command archive)"),
    ("phase-s9-research-models", "World-model research, critic compare, deferred OpenRouter/L0-full"),
]

TIERS = [
    ("T0", "Critical — machine verify without founder"),
    ("T1", "High — next maintainer sprint"),
    ("T2", "Medium — quarterly hardening"),
    ("T3", "Low — research / polish"),
]

TIER_DEPTH = {
    "T0": "Do now. Minimal diff. Run verify gate before close.",
    "T1": "Next sprint. Evidence in SOURCEA-PRIORITY.md or REPO_EXECUTION_LOGS.",
    "T2": "Quarterly hardening. No new D-modules unless plan says so.",
    "T3": "Research spike. Document only unless verify stays green.",
}

VERIFY = {
    "T0": "cd scripts && bash worker_verify_fast_v1.sh",
    "T1": "cd scripts && bash worker_verify_fast_v1.sh && bash validate-eval-packet-v1b-live.sh",
    "T2": "cd scripts && bash worker_verify_fast_v1.sh",
    "T3": "cd scripts && bash worker_verify_fast_v1.sh",
}

# v6 maintainer prompts already shipped — mark done on regen
DONE_IDS = {
    f"sa-{i:04d}"
    for i in range(1, 76)  # phases s0–s3 core v6 work + first tranche s2/s3
}

PINNED_DONE = [
    "pinned-sourcea-v6-ssot-honest",
    "pinned-sourcea-eval-5-5-live",
    "pinned-sourcea-no-asf-scoreboard",
    "pinned-sourcea-strict-build-ci",
    "pinned-sourcea-fr-tracker-sync",
    "pinned-sourcea-refresh-dedupe",
    "pinned-sourcea-1000-pack-locked",
]

PINNED_FOUNDER = [
    ("pinned-sourcea-spine-bridge-action", "Founder: Actions → Enqueue eval spine bridge → Refresh"),
    ("pinned-sourcea-fleet-6-auto-green", "Founder/lanes: 6 scoreboard reports + essays (auto-green)"),
    ("pinned-sourcea-wire-g3-attest", "Wire lane: G3 on WIRE_LANE_PROGRESS + vault"),
    ("pinned-sourcea-trustfield-pilot", "TrustField: pilot vault note + outreach"),
]

PHASE_TASKS: list[list[str]] = [
    [  # s0 SSOT
        "Run python3 audit_hub_source_alignment.py strict; fix honest_score not_here drift",
        "Skip L8 embeddings-later in not_here when embedding_provider.py + vector_index exist",
        "Update strategic_synthesis_hub this_week: spine Action + fleet auto-pass + Wire G3",
        "Set goal-dispatch-closure status in_progress with spine bridge blocker note",
        "Set P2 L0-full pendings status partial not open",
        "Sync SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md Eval line to 5/5 · 100% live",
        "Add audit regression: fail if live eval ok but Eval-1b still in not_here",
        "Validate MAP_POINTER_DOCS reference WORLD_TARGET_MODEL_MAP_LOCKED_v5.md only",
        "Run bash validate-governance-drift-v1.sh; drift items must be 0",
        "Cross-check STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md vs /api/strategic-synthesis-v1",
        "Fix ENFORCE-only not_here when ~/.sina/gate_mode_v1.txt is enforce",
        "Verify _phase_d_complete() matches D1–D16 in-repo artifacts",
        "Run python3 audit_essentials_nav.py — 42 sidebar tabs match app.js",
        "Grep app.js for WORLD_TARGET_MODEL_MAP_LOCKED_v2 — must be zero hits",
        "Ensure PROGRAM_PROGRESS signals_auto synced_at updates on build",
        "Validate index.html has __COMMAND_DATA_LAZY and shell payload under 500KB",
        "Sync FEEDBACK_AGGREGATE execution truth with hub built_at",
        "Reject unconditional L8 line in honest_score when hybrid shipped",
        "Compare ChatGPT critic Eval claim to ~/.sina/eval_packet_v1b_report.json",
        "Compare Claude ENFORCE stale claims to dispatch-policy API live",
        "Document SSOT trust order in COUNCIL_BRIEF one bullet",
        "Grep scripts for dispatch_ready=true global set — reject",
        "Validate strategic_synthesis bottleneck mentions dispatch_ready false",
        "Strict build runs validate-eval-packet-v1b-live without SINA_EVAL_1B_LIVE=1",
        "Append SOURCEA-PRIORITY row: SSOT alignment PASS with timestamp",
    ],
    [  # s1 eval dispatch
        "Run bash validate-eval-packet-v1b-live.sh; sustain 5/5 pilots ≥80%",
        "Wire validate-eval-packet-v1b-live into strict build default chain",
        "Strengthen eval_packet_v1b/grounding.py bugfix-gate paths model_dispatch gate_receipts",
        "Verify dispatch_policy eval_1b_gate_ok true in /api/dispatch-policy-v1",
        "Ensure dispatch_ready stays false until founder spine Action — no code bypass",
        "Run eval live with SINA_AUDIT_STRICT=1; capture report to ~/.sina",
        "Add validate-governance-fleet-v1.sh to find_critical_bugs.py checks list",
        "Cross-check DISPATCH_POLICY_LOCKED_v1.md classes vs policy_engine.py",
        "Validate graph-executor pos-dispatch suggest not auto dispatch globally",
        "Run python3 eval_packet_v1b/runner.py live smoke — write_report true",
        "Harden scorer.py path citation checks for plan-eval-1b task",
        "Add retrieve-dispatch grounding paths orchestrator + planner_engine",
        "Validate factory-runreceipt grounding includes RUNRECEIPT schema doc",
        "Validate l8-hybrid grounding cites embedding_provider.py",
        "Run bash validate-eval-packet-v1b.sh scaffold arm after live pass",
        "Compare Eval-1 structural vs Eval-1b behavioral in council brief",
        "Document eval CI in build-sina-command-panel.py header comment",
        "Reject ASF as eval authority in scoreboard or progress scripts grep",
        "Validate eval packet win_pct in command-data matches live report",
        "Run council_strategic_brief eval validator strings vs disk scripts",
        "Add eval regression to audit if mode=scaffold while live_ok",
        "Cross-check runtime/dispatch_policy/classifier.py task ids",
        "Ensure model_dispatch.py gate receipts integrate with hub panel",
        "Run validate-governance-drift after eval script touch",
        "Append SOURCEA-PRIORITY eval sustain row with pilot count",
    ],
    [  # s2 hub build CI
        "Fix build-sina-command-panel _run_audit to invoke .sh via bash not python3",
        "Run SINA_AUDIT_STRICT=1 build; all audits must pass",
        "Run python3 find_critical_bugs.py — critical must be 0 with hub up",
        "Run python3 audit_backend_e2e.py including POST /refresh timeout 360s",
        "Dedupe refresh: SINA_SKIP_NESTED_BOWL + SINA_SKIP_PANEL_BUILD in pipeline",
        "Skip nested bowl.sh in update-program-progress when env skip set",
        "Add fleet scan timeout 120s in build-sina-daily-bowl refresh_fleet",
        "Log fleet snapshot nudges auto-green report gaps on build complete",
        "Run bash validate-verify-wire-v1.sh on build; bump P0-RUNRECEIPT 100%",
        "Run bash validate-spine-bridge-founder-v1.sh after graph executor seed",
        "Run python3 audit_agent_governance_e2e.py v6 eight agents",
        "Run audit_personal_db_layer_a.py non-strict on build",
        "Validate governance-fleet in strict build after eval live",
        "Ensure hub serve-sina-command.sh health on :13020 before E2E",
        "Cross-check find_critical_bugs hub_health curl :13020",
        "Harden audit_backend_e2e refresh intelligence_circle chat_messages check",
        "Document refresh ~230s expected in SOURCEA-PRIORITY perf note",
        "Run seed_council_strategic_slice_v1 on build without flake",
        "Run import_founder_directives_v1 on build when jsonl rows exist",
        "Validate command-data.json and shell.json written atomically",
        "Compare build log fleet snapshot to scoreboard_payload live",
        "Reject duplicate panel build inside bowl during hub refresh",
        "Run validate-governance-drift-v1.sh in find_critical_bugs chain",
        "Add WTM future column guard in find_critical_bugs when hub up",
        "Append REPO_EXECUTION_LOGS/sourcea latest.yaml on CI pass",
    ],
    [  # s3 scoreboard fleet
        "Implement agent_scoreboard _auto_verify on auto_pass verified_by auto",
        "Expose fleet_auto_green_count in scoreboard_payload",
        "Backfill auto_verify in scoreboard_row when auto_pass and report exists",
        "Set scoreboard tagline auto-checks green not ASF verify",
        "Update app.js renderAgentScoreboard hero auto-green copy and gap banners",
        "Replace Verify Force buttons with Auto green pill when auto_pass",
        "Show essayNudgeBanner on Today tab and Council room from essay_discourse",
        "Inject planner_bridge_ready first_action_id note in renderGraphExecutorPanel",
        "Run bash validate-governance-fleet-v1.sh — nudges and verify_gap SSOT",
        "Sync FR-007/010/011 shipped via founder_request_tracker sync_shipped_from_disk",
        "Mark FR-008 in_progress until nudge_count <= 2",
        "Mark FR-009 shipped when auto_pass_count >= 6 not ASF verify count",
        "Remove ASF verified copy from workspace mirror scoreboard block",
        "Validate fleet_report_gap banner lists missing agent ids",
        "Validate fleet_verify_gap lists agents with report but no auto_pass",
        "Run agent_essay_discourse essay_nudges payload for council",
        "Ensure 6 essay nudges visible until lanes post governance-drift essays",
        "Cross-check AGENT_SCOREBOARD_LOCKED_v1.md law vs UI behavior",
        "Reject manual verify as progress authority in hub primary UI grep",
        "Run scoreboard session report POST E2E via audit_backend minimal",
        "Validate auto_checks council_read vault_used paths in scoreboard",
        "Document fleet targets reported>=6 auto_pass>=6 nudges<=2 in PRIORITY",
        "Compare MergePack exclusion in scoreboard agent count 8",
        "Run governance fleet validator after essay or scoreboard code change",
        "Append SOURCEA-PRIORITY fleet auto-green count evidence row",
    ],
    [  # s4 spine loop
        "Validate graph-executor spine_bridge_ready field in hub payload",
        "Ensure planner_bridge_note explains pos-dispatch suggest state",
        "Run validate-spine-bridge-founder-v1.sh — proof event or smoke echo",
        "Founder-only: document Actions enqueue eval spine bridge steps in FOUNDER guide",
        "Verify runtime/event_bus/bus_v1.py API /api/event-bus-v1 returns topics",
        "Check execution_memory.jsonl appends on spine success only",
        "Validate graph_executor run_graph_executor on build without exception",
        "Cross-check spine_bridge.py planner_bridge_ready logic vs branches_registry",
        "Ensure no spine.bridge event fabricated without founder Action",
        "Run dispatch policy classifier for spine-bridge-founder task id",
        "Document loop closure proof in STRATEGIC synthesis bottleneck",
        "Compare D16 writeback vs loop closure in GPT synthesis doc",
        "Validate pos-dispatch stays suggest until council amends policy",
        "Add hub Actions panel entry for spine bridge if missing from founder_actions",
        "Run audit for graph-executor policy_class in GET /api/graph-executor-v1",
        "Harden spine smoke echo test idempotency",
        "Cross-check EXECUTION_TRUTH last_spine_success in PROGRAM_PROGRESS",
        "Validate event bus panel in app.js renders tail topics",
        "Document founder Refresh-only law for spine — no Terminal",
        "Reject dispatch_ready true promotion in planner without eval+founder",
        "Compare Claude loop-closure critique to live event bus tail",
        "Add spine bridge row to council strategic brief if drift",
        "Run find_critical_bugs after spine_bridge.py touch",
        "Validate execution_spine progress_sync does not fake G3",
        "Append SOURCEA-PRIORITY spine proof row when bridge event exists",
    ],
    [  # s5 commercial
        "Validate P0-RUNRECEIPT progress_pct 100 when verify:wire passes",
        "Run bash validate-verify-wire-v1.sh — RunReceipt artifact schema",
        "Cross-check TRUST_LEDGER_SCHEMA_LOCKED_v1.md FR-007 shipped signal",
        "Document Wire G3 attest as founder/lane step in this_week",
        "Validate product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md hub link",
        "Compare TrustField pilot vault note requirement vs workspace-vault API",
        "Run founder_request_tracker sync on build for commercial FR rows",
        "Validate PROGRAM_PROGRESS parallel_plans P0 next_action honest",
        "Cross-check MergePack KPI trio in command center payload",
        "Document lane P0 revenue bottleneck in strategic one_line",
        "Reject fabricated G3 or Track PASS in any script grep",
        "Validate wire lane progress md exists logged for Wire agent",
        "Compare ChatGPT commercial critique to PROGRAM_PROGRESS locks",
        "Ensure RunReceipt factory hook in command center P0 card",
        "Run update-program-progress wire_summary from locked_plan.json",
        "Validate acquisition stack docs indexed in important-docs",
        "Cross-check PRODUCT_FACTORY roadmap vs hub progress signals",
        "Document TrustField outreach P10 pending in strategic pendings",
        "Validate evidence flywheel doc linked from hub essentials",
        "Compare best-in-world GTM moat notes to governance scoreboard law",
        "Run commercial attests checklist in SOURCEA-PRIORITY founder section",
        "Harden verify:wire to fail on missing run receipt artifact",
        "Validate mergepack progress json read without blocking build",
        "Document two-clock slice parallel lane P0 in synthesis lessons",
        "Append commercial lane evidence when G3 visible in vault",
    ],
    [  # s6 WTM pre-LLM
        "Validate system_roadmap payload v5.2 Phase D 16 steps count",
        "Cross-check LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1 vs packet builder",
        "Run pre_llm user_signals store record_hub_touch on build",
        "Validate L0 MVP user_signals_v1.json artifact when hub touched",
        "Validate L1 workspace state from hub tab POST signals",
        "Cross-check L8 hybrid row in WTM layer map not partial false",
        "Validate ENFORCE_BYPASS_MAP_LOCKED_v1 hub panel surfaces",
        "Run gate_receipts_hub.py routes vs ENFORCE bypass map",
        "Validate context_packet hydrate_from_disk D1-D3 partial rules",
        "Cross-check META_REASONING_POLICY_STACK vs dispatch classes",
        "Document SHADOW vs ENFORCE modes in dispatch policy doc",
        "Validate tool_router capability_catalog hub_refresh entry",
        "Run vector_retrieval query_engine hybrid_score smoke",
        "Compare D9 blend weights doc to query_engine implementation",
        "Reject new D-module creation grep in scripts unless plan authorizes",
        "Validate semantic history L5 feedback to D16 path exists",
        "Cross-check WORLD_TARGET_MODEL step catalog vs app.js srStrategicStepCount",
        "Run audit hub ui_contract renderPacketReadinessPanel present",
        "Validate pre_llm packet_memory_merge collector D6 slots",
        "Document deferred OpenRouter real embeddings in phase s9 only",
        "Compare Claude D16 shipped claim to packet schema version",
        "Validate honest_score built list includes Execution Spine",
        "Run eval grounding governance-rules paths agent_rules scripts",
        "Cross-check CHATGPT_EXTERNAL_CRITIC_LAW — compare never steer",
        "Append WTM layer gap note when L0-full editor telemetry partial",
    ],
    [  # s7 council governance
        "Validate council room essay discourse form POST path in audit E2E",
        "Run agent_rules_in_charge.py payload — gold highlight in charge now",
        "Validate governance unification engine batch form in app.js",
        "Cross-check AGENT_MIND_SHARE_LOCKED law vs mind share feed render",
        "Validate conflict room API GET returns schema ok",
        "Run agent_governance_events log on session report scoreboard",
        "Validate essay topic governance-drift-detection default subject",
        "Cross-check AGENT_ESSAY_DISCOURSE_LOCKED vs essay_nudges payload",
        "Validate rules loop orchestrator charges vs council rules list",
        "Run validate-governance-drift after rules_in_charge change",
        "Document governance moat 50% product in synthesis lessons",
        "Validate paradox detection mind share kind paradox cards",
        "Cross-check unification policy doc link in council hero",
        "Validate advisory votes council topics POST creates row",
        "Run important_docs_index governance section completeness",
        "Compare GPT governance drift essay requirement to nudge_count",
        "Validate blueprint navigator inclusive vs exclusive scopes",
        "Cross-check sprint consolidation locked doc vs hub pendings",
        "Validate agent workspace vault log_activity on essay post",
        "Document ASF assigns subject law — founder role not verify role",
        "Run council strategic slice seed on build",
        "Validate TASK_ORDERS_OPEN_REGISTER sync with hub todos",
        "Cross-check order guardian judgments vs pendings statuses",
        "Harden essay mark-best POST without ASF as sole actor",
        "Append council governance evidence row after fleet essay wave",
    ],
    [  # s8 Hub 2 Machine Hub (not Sina Command archive — SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md)
        "Validate machine-hub/v1 payload size under 16KB — no Sina Command embed",
        "Validate h2-pending-registry-v1.json honest pending_total counter",
        "Validate machines/index.html health pill and live poll parity with H1",
        "Run validate-machine-hub-v1.sh — sibling hub copy and staleness gate",
        "Cross-check H2 pending buckets vs SOURCEA_SUPER_FAST_HUB section 2a taxonomy",
        "Validate form_open mirror links to M1 Canvas PICK rows",
        "Validate next_phase bucket rows vs PROGRAM_PROGRESS founder_open",
        "Validate deferred bucket excludes scheduled_cadence rows from pending_total",
        "Validate thread_room summary from latest-curation-v1.json on H2 only",
        "Validate judge alarm strip one-line receipt — full batch on H2 weekly only",
        "Run hub_dual_heal_v1 — H2 sync after H1 light refresh",
        "Cross-check machine_hub_staleness_v1 auto-heal recommended path",
        "Validate h2_pending_registry_reconcile_v1 closed maintainer_ship rows",
        "Document H2 weekly machine receipt bundle regen cadence in integration-fabric",
        "Validate hub_surface_v1 tab slices load without command-data.json hero",
        "Cross-check THREE_ZONE_HUB_SPINE — H2 not nested under H1 navigation law",
        "Validate H2 light refresh does not trigger build-sina-command-panel",
        "Run validate-h2-pending-honest-count-v1.sh after registry sync",
        "Cross-check Thread Room second-hop law vs SINA_THREAD_ROOM_LOCKED_v1",
        "Validate machines banner sibling-hub copy — not sub-page wording",
        "Document ops_blocker bucket MP-SHIP WIRE-G3 B-001 row contracts",
        "Validate scheduled_cadence UP-01 through UP-06 excluded from pending_total",
        "Cross-check ENFORCE shadow mode display on H2 maintainer slice only",
        "Append H2 machine hub evidence row after weekly SHIP pass",
        "Compare Sina Command /legacy/ quarantine banner vs Hub 2 bookmark law",
    ],
    [  # s9 research models
        "Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only",
        "Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates",
        "Compare RAGAS eval CI to Eval-1b live packet approach — internal note",
        "Research OpenRouter real embeddings cost model — defer implementation",
        "Research L0-full Cursor MCP editor telemetry — defer per phase 6",
        "Document pos-dispatch policy promotion criteria — founder council vote",
        "Compare best world model agent OS patterns to Sina D-layer stack",
        "Analyze critic law effectiveness — external chat wrong rate table",
        "Research fleet 8-agent scoreboard at scale — auto-check taxonomy",
        "Document no-ASF verify authority pattern for other repos mono noetfield",
        "Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts",
        "Research hub refresh parallelize progress+bowl — perf note only",
        "Spike: eval live pilot expansion beyond 5 tasks — tasks.json design",
        "Document TrustField vs RunReceipt vs MergePack positioning matrix",
        "Research event bus topic taxonomy for spine learning loop",
        "Compare ENFORCE IDE bypass gap to industry gate patterns",
        "Document two-speed clocks strategic slice vs lane P0 case study",
        "Research governance fleet validator extensions for lazy-load FR rows",
        "Spike: semantic diff L14 integration with packet assembly",
        "Document world model v5 vs v4 migration lessons locked",
        "Research agent essay discourse as fleet compliance moat",
        "Compare founder hub-only law to terminal-first agent products",
        "Document validate-spine-bridge-founder proof types matrix",
        "Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents",
        "Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography",
    ],
]


def prompt_body(
    pid: str,
    phase: str,
    phase_desc: str,
    tier: str,
    task: str,
    slot: int,
    today: str,
) -> str:
    priority = {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier]
    agent_prompt = (
        f"PLAN WITH NO ASF — SourceA prompt {pid}. "
        f"{task} ({TIER_DEPTH[tier]}). "
        f"Pre-flight: read SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md + brain-os/plan-registry/SOURCEA-PRIORITY.md. "
        f"Founder law: hub Refresh/Actions/tabs only — no Terminal. "
        f"No ASF as verify/progress authority — machine validators + auto_pass. "
        f"Post-flight: verify gate + mark prompt done + SOURCEA-PRIORITY evidence row."
    )
    return f"""---
id: {pid}
phase: {phase}
tier: {tier}
priority: {priority}
status: backlog
lane: sourcea
library: sourcea-1000-locked
agent: {AGENT}
agent_tag: {TAG}
written_at: {today}
slot: {slot}
generator: scripts/generate-sourcea-1000-prompts.py
locked: true
---

# [{TAG}@{today}] {pid} — {task}

**Phase:** `{phase}` — {phase_desc}  
**Tier:** `{tier}` — {TIER_DEPTH[tier]}

## Agent prompt (copy to chat)

```
{agent_prompt}
```

## Task

{task}

## Sources (read first)

- `SINA_OS_SSOT_LOCKED.md` · `SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md`
- `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` · `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`
- `brain-os/plan-registry/SOURCEA-PRIORITY.md` · `brain-os/plan-registry/sourcea-1000/REGISTRY.json`
- `scripts/system_roadmap.py` · `scripts/strategic_synthesis_hub.py`
- `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` (compare only)
- Global: `~/.cursor/plans/no-asf-library/REGISTRY.json` (lane sourcea)
- Machine: `~/.sina/eval_packet_v1b_report.json` · hub `http://127.0.0.1:13020/`

## Verify

```bash
{VERIFY[tier]}
```

## Closeout

1. Set `status: done` in this file front matter when complete
2. Append `REPO_EXECUTION_LOGS/sourcea/` YAML with verify_passed true
3. Update `brain-os/plan-registry/SOURCEA-PRIORITY.md` evidence row
4. Re-run `bash scripts/validate-sourcea-1000-pack.sh`
"""


def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries: list[dict] = []
    seq = 0

    for p_idx, (phase, phase_desc) in enumerate(PHASES):
        tasks = PHASE_TASKS[p_idx]
        for tier, _tier_desc in TIERS:
            tier_dir = PROMPTS / phase / tier
            tier_dir.mkdir(parents=True, exist_ok=True)
            for slot in range(25):
                seq += 1
                pid = f"sa-{seq:04d}"
                task = tasks[slot]
                rel = f"prompts/{phase}/{tier}/{pid}.md"
                path = PACK / rel
                status = "done" if pid in DONE_IDS else "backlog"
                body = prompt_body(pid, phase, phase_desc, tier, task, slot, today)
                if status == "done":
                    body = body.replace("status: backlog", "status: done", 1)
                path.write_text(body, encoding="utf-8")
                entries.append(
                    {
                        "id": pid,
                        "phase": phase,
                        "tier": tier,
                        "priority": {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier],
                        "lane": "sourcea",
                        "slot": slot,
                        "title": task[:120],
                        "path": rel,
                        "status": status,
                        "verify": VERIFY[tier],
                        "agent_tag": TAG,
                        "agent_prompt": f"PLAN WITH NO ASF — {pid}: {task}",
                    }
                )

    pinned = [{"id": pin, "lane": "sourcea", "tier": "T0", "status": "done"} for pin in PINNED_DONE]
    for pin, title in PINNED_FOUNDER:
        pinned.append(
            {
                "id": pin,
                "lane": "sourcea",
                "tier": "T0",
                "status": "backlog",
                "title": title,
                "founder_only": True,
            }
        )

    registry = {
        "schema_version": 1,
        "library": "sourcea-1000-locked",
        "locked": True,
        "count": len(entries),
        "generated_at": now,
        "agent": AGENT,
        "agent_tag": TAG,
        "repo": "SourceA",
        "grid": "10 phases × 4 tiers × 25 prompts = 1000",
        "trigger": "PLAN WITH NO ASF",
        "pick_script": "scripts/pick-sourcea-no-asf-plan.py",
        "run_script": "scripts/plan-no-asf-run.sh",
        "validate_script": "scripts/validate-sourcea-1000-pack.sh",
        "global_pack": str(Path.home() / ".cursor/plans/no-asf-library"),
        "mono_pack_ref": str(Path.home() / "Desktop/SinaaiMonoRepo/brain-os/plan-registry/mono-1000"),
        "noetfield_pack_ref": str(Path.home() / "Desktop/Noetfield/brain-os/plan-registry/noetfield-1000"),
        "sources": [
            "SINA_OS_SSOT_LOCKED.md",
            "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md",
            "brain-os/law/STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md",
            "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md",
            "execute_v6_no_asf plan (maintainer phases 0/2/5)",
            "brain-os/plan-registry/SOURCEA-PRIORITY.md",
            "PROGRAM_PROGRESS.json",
            "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
            "~/.cursor/plans/no-asf-library/REGISTRY.json",
        ],
        "phases": [{"id": p, "description": d} for p, d in PHASES],
        "tiers": [{"id": t, "description": d} for t, d in TIERS],
        "pinned": pinned,
        "plans": entries,
        "verdicts": {
            "gpt": "Right on gaps (L0/L8/Eval); wrong on live ENFORCE/dispatch state — trust ~/.sina",
            "claude": "Right on milestone; stale on ENFORCE/D15.2/D16 — fixed in synthesis doc",
            "cursor": "SSOT projection drift + hub perf + no-ASF auto-green pattern",
            "v6_maintainer": "Phases 0/2/5 shipped; founder P1/P3/P4 remain hub-only",
            "world_model_compare": "D-layer packet path  vs raw-agent; weak on IDE ENFORCE + live fleet proof",
        },
        "success_criteria": {
            "ssot_honest": "audit_hub_source_alignment OK",
            "no_asf_verify": "scoreboard auto_pass not manual verify",
            "eval_sustain": "5/5 live on strict build",
            "fleet_target": "auto_pass>=6 nudges<=2",
            "spine_loop": "spine.bridge after founder Action",
        },
    }

    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    assert len(entries) == 1000, f"expected 1000 got {len(entries)}"
    print(f"LOCKED {len(entries)} SourceA prompts → {PACK / 'REGISTRY.json'}")


if __name__ == "__main__":
    main()
