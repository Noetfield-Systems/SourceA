#!/usr/bin/env python3
"""One-shot generator for sourcea-full-stack-100-fix-plan-v1.json"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sourcea-full-stack-100-fix-plan-v1.json"

OWNER_BY_LANE = {
    "execution_inbox": "worker",
    "session_gate": "system",
    "commercial_w3": "founder",
    "research_l1": "brain",
    "research_l2": "brain",
    "mcp_stack": "founder",
    "vocabulary": "system",
    "governance": "system",
    "cloud_factory": "system",
    "fdg_icp": "worker",
    "linter_oqg": "worker",
    "translation": "worker",
    "rrl_intelligence": "worker",
    "cil_ril": "worker",
    "sina_founder": "founder",
    "telemetry": "system",
    "anti_template": "worker",
    "research_ingest": "brain",
    "deferred_volume": "founder",
}

VALIDATOR_BY_LANE = {
    "execution_inbox": "scripts/execution_plane_honesty_v1.py",
    "session_gate": "scripts/agent_session_gate_run_v1.py",
    "commercial_w3": "scripts/execution_plane_honesty_v1.py",
    "mcp_stack": "scripts/validate-mcp-stack-free-tier-v1.sh",
    "governance": "scripts/governance_gate_cart_v1.py",
    "vocabulary": "scripts/validate-anti-staleness-vocabulary-gate-v1.sh",
    "research_l2": "scripts/validate-brain-l2-wire-v1.sh",
}


def add(
    plans: list,
    wave: str,
    tier: str,
    lane: str,
    lane_label: str,
    title: str,
    wired_to: str,
    acceptance: str,
    deps: list | None = None,
    *,
    outbound_ref: str = "",
    validator_hook: str = "",
) -> str:
    n = len(plans) + 1
    fid = f"F{n:03d}"
    plans.append(
        {
            "id": fid,
            "tier": tier,
            "wave": wave,
            "lane": lane,
            "lane_label": lane_label,
            "title": title,
            "wired_to": wired_to,
            "acceptance": acceptance,
            "status": "planned",
            "owner_role": OWNER_BY_LANE.get(lane, "worker"),
            "outbound_ref": outbound_ref,
            "validator_hook": validator_hook or VALIDATOR_BY_LANE.get(lane, ""),
            "priority": n,
            "deps": deps or [],
            "parent_spec": "data/sourcea-full-stack-100-fix-plan-v1.json",
            "human_doc": "docs/SOURCEA_FULL_STACK_100_FIX_PLAN_LOCKED_v1.md",
            "pulse": "scripts/full_stack_fix_plan_pulse_v1.py",
        }
    )
    return fid


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    plans: list[dict] = []

    w1_items = [
        ("P0", "execution_inbox", "Worker INBOX turn", "Execute U029 One product line max", "Worker chat disk INBOX", "receipt U029; plan done; inbox pending=false"),
        ("P0", "execution_inbox", "Broker round-trip", "Broker submit after U029", "goal1-lane-broker-v1.py", "last_worker_report fresh"),
        ("P0", "execution_inbox", "Plan mark honesty", "Mark U029 done with execution_proof", "outbound-factory-100-upgrade-plan-v1.json", "worker proof not bulk_wiring"),
        ("P0", "execution_inbox", "Heal chain post-turn", "Run outbound_disk_coherence_heal", "outbound_disk_coherence_heal_v1.py", "heal_ok true"),
        ("P0", "execution_inbox", "Auto Runtime specialist clear", "Tick after U029 clears inbox", "loop_specialist_tick_v1.py", "execute_pending or observe"),
        ("P0", "execution_inbox", "INBOX truth patch", "Refresh disk truth block", "run_inbox_disk_truth_v1.py", "truth_match true"),
        ("P1", "execution_inbox", "U030 worker proof", "Re-verify U030 compile_sequence receipt", "icp_output_compiler_v1.py", "NF|TF then SA in receipt"),
        ("P1", "execution_inbox", "Queue drain U031", "Execute U031 RRL per-account history", "Worker INBOX", "U031 done + receipt"),
        ("P1", "execution_inbox", "Advisory circle pin", "Honor CL10 queue_head_pin", "future_loop_prompt_advisory_circle_v1.py", "head matches plan order"),
        ("P1", "execution_inbox", "Execution honesty UI", "Expose bulk vs worker counts", "execution_plane_honesty_v1.py", "worker_proven counter on Hub"),
        ("P1", "execution_inbox", "Orchestrator latch", "Clear last_completed_sa ghost", "worker_stuck_recovery_v1.py", "no stale sa on new unit"),
        ("P1", "execution_inbox", "Drain orchestrator align", "Align pos/total with plan head", "healthy-drain-orchestrator", "queue_pos matches U0xx"),
    ]
    for row in w1_items:
        add(plans, "W1", *row)
    if plans and plans[0].get("id") == "F001":
        plans[0]["outbound_ref"] = "U029"

    outbound = [
        ("U032", "fdg_icp", "ICP4 single CTA block enforcement", "icp4_single_cta", "Two CTAs = fail"),
        ("U033", "anti_template", "Salvage opener rotation per account", "salvage_opener_rotation", "No repeat opener 30d"),
        ("U034", "linter_oqg", "RIL bar structural fail on missing proof", "ril_structural", "Missing proof = hard fail"),
        ("U035", "translation", "Regional compliance footer auto-select", "regional_footer", "OSFI vs SEC correct"),
        ("U036", "rrl_intelligence", "RRL sim receipt append-only", "rrl_history_jsonl", "10 sims per account"),
        ("U037", "cil_ril", "CIL curiosity references prior touch", "cil_curiosity_link", "Generic curiosity = fail"),
        ("U038", "sina_founder", "Sina read gate blocks auto-send", "commercial_mail_draft_v1.py", "send_ready false until founder"),
        ("U039", "telemetry", "Pulse maturity honest label", "outbound_factory_upgrade_pulse_v1.py", "verified_done = worker only"),
        ("U040", "linter_oqg", "Brand bleed cross-check", "brand_route_checker", "Cross-brand = fail"),
        ("U041", "fdg_icp", "Product line count lint", "icp4_one_product_line", "Two paragraphs = fail"),
        ("U042", "translation", "Forbidden architecture noun block", "forbidden_in_email_one", "Brain-os term = fail"),
        ("U043", "rrl_intelligence", "Receiver interest sim freshness", "w3_receiver_interest", "Stale sim = review"),
        ("U044", "cil_ril", "Link block order law", "icp_curiosity_gate_v1.py", "Curiosity last before links"),
        ("U045", "anti_template", "Template hash dedup per wave", "template_hash_gate", "Duplicate hash = fail"),
        ("U046", "sina_founder", "Founder score receipt on read", "w3_founder_score", "Score on Sina read"),
        ("U047", "telemetry", "Plan dual counter bulk vs worker", "outbound plan meta", "bulk_done vs worker_proven"),
        ("U048", "linter_oqg", "OQG fleet artifact clean bar", "best_loop_oqg_score_v1.py", "w3 100% maintained"),
        ("U049", "fdg_icp", "Compile mode receipt stamp", "icp_output_compiler", "compose_mode in receipt"),
        ("U050", "translation", "Auto-suggest lint in compose", "translate block", "Suggests fix phrase"),
        ("U051", "rrl_intelligence", "Conversation interest trend", "w3_conversation_interest", "Down-trend flags review"),
        ("U052", "rrl_intelligence", "RRL history not overwrite", "response-reality-layer-history", "U031 full impl"),
        ("U053", "research_ingest", "Research digest refresh", "research_root_sync.py sync", "digest <24h"),
        ("U054", "sina_founder", "Mail FROM config verify", "commercial_mail_draft_v1.py", "hello@ + operation@ ok"),
        ("U055", "telemetry", "sa-1100 multi-unit receipt chain", "receipts/", "Each U0xx receipt row"),
        ("U056", "linter_oqg", "Pack basis field required", "pack.json validator", "Missing basis fail"),
        ("U057", "anti_template", "Buzzword subject hard fail", "OQG subject fluff", "synergy = 0"),
        ("U058", "fdg_icp", "Compile order receipt field", "receipt.compile_sequence", "U030 regression guard"),
        ("U059", "translation", "Hard fail openers from salvage", "factory-email-translation-v1.json", "Salvage opener fail"),
        ("U060", "rrl_intelligence", "RIL/OQG shared URL cache", "RIL/OQG cache", "Stale URL once"),
        ("U061", "cil_ril", "Attach URL broken path gate", "attach_urls block", "Broken attach fail"),
        ("U062", "sina_founder", "Approved-not-sent zero", "commercial_flywheel", "count=0 at send"),
        ("U063", "telemetry", "Queue exhausted signal", "healthy-queue-30-active.json", "exhausted at 67/67"),
        ("U064", "linter_oqg", "Word-count sweet spot hold", "fefs_word_count", "90-110 bonus"),
        ("U065", "anti_template", "Duplicate 4-gram hold", "fefs_buzzword_duplicate", "No double penalty"),
        ("U066", "fdg_icp", "Regional overlay OSFI/SEC", "translation regional", "Terms routed"),
        ("U067", "deferred_volume", "Volume defer until L3 100%", "commercial readiness", "send_ready first"),
    ]
    for uid, lane, title, wired, acc in outbound:
        add(
            plans,
            "W2",
            "P1",
            lane,
            f"Outbound {uid}",
            f"Worker execute {uid}: {title}",
            wired,
            acc,
            ["F001"] if uid == "U032" else [],
            outbound_ref=uid,
        )

    w3_items = [
        ("P0", "session_gate", "C4 crawl honesty", "C4 ok when execution 6/6 or labeled BLOCK", "sourcea_crawl_mirror_pipeline_v1.py", "C4 not silent fail"),
        ("P0", "session_gate", "Better loop governance_pulse", "governance_pulse ok when cart honest", "better_loop_pulse_v1.py", "governance_pulse pass"),
        ("P1", "session_gate", "Session gate aggregate", "ok true when sub-steps pass", "agent_session_gate_run_v1.py", "session gate ok true"),
        ("P1", "session_gate", "Crawl prove stage", "prove PASS after execution fix", "sourcea_crawl_mirror_pipeline_v1.py", "prove ok"),
        ("P1", "session_gate", "Governance center fast", "governance_center gate pass", "governance_center_run_v1.py", "center ok"),
        ("P1", "session_gate", "Gate cart 17/17", "cart ok when execution+commercial founder done", "governance_gate_cart_v1.py", "17/17 or documented founder block"),
        ("P2", "session_gate", "Loop observatory freeze", "freeze truth with override", "loop_observatory_report_v1.py", "freeze honest"),
        ("P2", "session_gate", "Auto Runtime graduation", "shadow_auto to full auto", "loop_auto_graduation_v1.py", "graduation when validators pass"),
        ("P2", "session_gate", "Anti-staleness vocab pair", "both keys PASS", "validate-anti-staleness-vocabulary-gate-v1.sh", "paired PASS"),
        ("P2", "session_gate", "Disk live wire chain", "all steps including nerve research", "disk_live_wire_sync_v1.py", "full chain ok"),
    ]
    for row in w3_items:
        add(plans, "W3", *row)

    w4_items = [
        ("P0", "commercial_w3", "Founder Sina read", "Human read session", "founder workflow", "w3_sina_read PASS"),
        ("P0", "commercial_w3", "Mail FROM setup", "Configure hello@ and operation@", "commercial_mail_draft_v1.py", "w3_mail_from PASS"),
        ("P0", "commercial_w3", "Send ready composite", "All ship gates true", "nerve ship_gates", "w3_send_ready PASS"),
        ("P1", "commercial_w3", "Commercial 100%", "L3 ready_pct 100", "assess_commercial_readiness", "ready true"),
        ("P1", "commercial_w3", "W3 OQG maintain", "oqg_pass holds", "best_loop_oqg_score_v1.py", "w3 100%"),
        ("P1", "commercial_w3", "Critic circle", "w3_critic pass", "critic_circle", "critic PASS"),
        ("P1", "commercial_w3", "Receiver interest", "sim fresh", "w3_receiver_interest", "PASS"),
        ("P1", "commercial_w3", "RRL gate", "rrl pass", "w3_rrl", "PASS"),
        ("P2", "commercial_w3", "Pipeline not sent", "approved_not_sent handled", "w3_sends", "cleared"),
        ("P2", "commercial_w3", "Disclosure outbound", "No T0 MCP in email", "disclosure_ladder_v1.py", "T0 clean"),
    ]
    for row in w4_items:
        add(plans, "W4", *row)

    w5_items = [
        ("P1", "research_l2", "Research sync refresh", "sync filtered digests", "research_root_sync.py sync", "digest fresh"),
        ("P1", "research_l2", "L2 register briefs", "registry matches vault", "research_root_sync.py register", "rows aligned"),
        ("P1", "research_l1", "L1 brief schema", "YAML per GOAL_SPECIALIST §4", "research-acquisitor/briefs/", "schema valid"),
        ("P1", "research_l2", "Orientation research reads", "add O-stations", "agent_orientation_pipeline_v1.py", "research paths in pack"),
        ("P1", "research_l2", "Brain L2 wire", "researcher_l2 in wire", "validate-brain-l2-wire-v1.sh", "PASS"),
        ("P2", "research_l2", "Nerve research pulse", "research=YES line", "agent_nerve_system_v1.py", "research ok"),
        ("P2", "research_l2", "Filtered 4-pack", "all yaml present", "research-root/filtered/", "4/4"),
        ("P2", "research_l1", "L1→L2 handoff receipt", "brief in registry", "research_root_sync receipt", "handoff ok"),
        ("P2", "research_l2", "Brain digest-only read", "execution_core.digest only", "MANDATORY_READ_BY_ROLE", "law obeyed"),
        ("P2", "research_l2", "Research outbound tie", "U053 cross-ref", "outbound + research", "ingest lane wired"),
    ]
    for row in w5_items:
        add(plans, "W5", *row)

    w6_items = [
        ("P0", "mcp_stack", "GitHub MCP P0", "Enable per manifest", "cursor-mcp-free-tier-manifest-v1.json", "github active"),
        ("P1", "mcp_stack", "MCP validator", "validate PASS", "validate-mcp-stack-free-tier-v1.sh", "PASS"),
        ("P1", "mcp_stack", "Hub MCP tick", "API + card", "POST /api/mcp-stack/tick/v1", "slice live"),
        ("P1", "mcp_stack", "Browser pilot verify", "Hub UI smoke", "cursor-ide-browser", "UI verified"),
        ("P1", "mcp_stack", "Linear GTM mirror", "optional issue mirror", "plugin-linear-linear", "issues linked"),
        ("P2", "mcp_stack", "Supabase read", "TrustField proof queries", "plugin-supabase-supabase", "read-only"),
        ("P2", "mcp_stack", "Notion adjunct", "research capture auth", "plugin-notion-workspace", "not SSOT"),
        ("P2", "mcp_stack", "Figma review", "design lane auth", "plugin-figma-figma", "no outbound paste"),
        ("P2", "mcp_stack", "Disclosure audit", "T0 violations 0", "mcp_stack_free_tier_v1.py", "audit ok"),
        ("P2", "mcp_stack", "Defer paid MCP", "no Datadog yet", "mcp-stack tier C", "deferred"),
    ]
    for row in w6_items:
        add(plans, "W6", *row)

    w7_items = [
        ("P1", "vocabulary", "Duty card taps", "Hub glance not RUN INBOX only", "agent-executor-daily-duty-card-v1.json", "inject aligned"),
        ("P1", "vocabulary", "Session gate inject", "match surfaces", "agent_session_gate_run_v1.py", "no split-brain"),
        ("P1", "vocabulary", "GATE_TREE daily_ops", "Auto Runtime disk INBOX", "agent_three_pipelines_lib_v1.py", "text fixed"),
        ("P1", "vocabulary", "MCP one_law", "assist not replace", "mcp-stack-free-tier-v1.json", "wording fixed"),
        ("P2", "vocabulary", "Better loop motion", "Auto Runtime line", "better_loop_pulse_v1.py", "aligned"),
        ("P2", "vocabulary", "Stack map sync", "cross_ref aligned", "stack-map-routing-v1.json", "aligned"),
    ]
    for row in w7_items:
        add(plans, "W7", *row)

    w8_items = [
        ("P1", "governance", "Cart execution green", "6/6 execution gates", "governance_gate_cart_v1.py", "execution gates PASS"),
        ("P1", "governance", "Bulk vs worker UI", "pulse dual counter", "outbound_factory_upgrade_pulse_v1.py", "honest label"),
        ("P1", "governance", "Cascade latch restore", "post proof test", "validate-founder-input-cascade-v1.sh", "latch ok"),
        ("P1", "governance", "Honesty on surfaces", "execution_honesty_line", "agent-live-surfaces-v1.json", "always visible"),
    ]
    for row in w8_items:
        add(plans, "W8", *row)

    w9_items = [
        ("P2", "cloud_factory", "Loop cloud phase 2b", "cron when live", "loop-specialist-cloud-contract-v1.json", "cloud receipt"),
        ("P2", "cloud_factory", "FBE W1 spawn stub", "registry only", "fbe_factory_builder_bundle_v1.json", "Mac control plane"),
    ]
    for row in w9_items:
        add(plans, "W9", *row)

    if len(plans) != 100:
        raise SystemExit(f"expected 100 plans got {len(plans)}")

    waves = []
    for wid, label, desc in [
        ("W1", "P0 Execution unblock", "U029 inbox · broker · heal · honesty"),
        ("W2", "P1 Outbound drain", "Worker-proven U032-U067"),
        ("W3", "Session gate green", "C4 · better_loop · cart"),
        ("W4", "Commercial L3 100%", "Sina read · mail · send"),
        ("W5", "Research L1/L2", "sync · orientation · nerve"),
        ("W6", "MCP free-tier", "GitHub P0 · leverage lanes"),
        ("W7", "Vocabulary unify", "Auto Runtime inject"),
        ("W8", "Governance honesty", "cart · bulk vs worker"),
        ("W9", "Cloud defer", "phase 2b · FBE"),
    ]:
        waves.append(
            {
                "id": wid,
                "label": label,
                "description": desc,
                "plan_ids": [p["id"] for p in plans if p["wave"] == wid],
                "status": "pending",
            }
        )

    doc = {
        "schema": "sourcea-full-stack-100-fix-plan-v2",
        "version": "2.1.0",
        "saved_at": now,
        "law": "100 fix plans v2.1 — pulse wired · outbound cross · gate cart · C4 decoupled",
        "parent_audit": "Brain chat full honest audit 2026-06-18",
        "human_doc": "docs/SOURCEA_FULL_STACK_100_FIX_PLAN_LOCKED_v1.md",
        "pulse_script": "scripts/full_stack_fix_plan_pulse_v1.py",
        "pulse_receipt": "~/.sina/full-stack-fix-plan-pulse-v1.json",
        "validator": "scripts/validate-full-stack-100-fix-plan-v1.sh",
        "critical_path": ["F001", "F002", "F003", "F004", "F049", "F050", "F054"],
        "cross_ref": {
            "outbound_plan": "data/outbound-factory-100-upgrade-plan-v1.json",
            "mcp_ssot": "data/mcp-stack-free-tier-v1.json",
            "execution_honesty": "scripts/execution_plane_honesty_v1.py",
            "heal_chain": "scripts/outbound_disk_coherence_heal_v1.py",
            "gate_cart": "scripts/governance_gate_cart_v1.py",
        },
        "tier_counts": {
            "P0": sum(1 for p in plans if p["tier"] == "P0"),
            "P1": sum(1 for p in plans if p["tier"] == "P1"),
            "P2": sum(1 for p in plans if p["tier"] == "P2"),
        },
        "lanes": sorted({p["lane"] for p in plans}),
        "progress": {
            "total": 100,
            "done": 0,
            "in_progress": 0,
            "planned": 100,
            "blocked": 0,
            "worker_proven": 0,
            "founder_gates": 10,
        },
        "waves": waves,
        "fixes": plans,
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {OUT} fixes={len(plans)} P0={doc['tier_counts']['P0']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
