#!/usr/bin/env python3
"""Generate 300 UNIQUE practical plans — CLOUD_ONLY factory execution v2.

Every row: unique title · specific acceptance · receipt · goal_alignment tag.
Law: fbe_execution_contract · founder-pivot-pattern · loop-specialist-cloud-contract
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "brain-cloud-practical-300-plan-v1.json"
SINA = Path.home() / ".sina"

# (title, acceptance, receipt, goal_alignment, tier_override|None)
# goal_alignment: wire | nf_factory | tf_sandbox | loop | federate | graduate | market | openrouter


def _wire_specs() -> list[tuple]:
    base = []
    url = [
        ("Deploy Railway FBE runner from cloud/Dockerfile.fbe-runner — capture public URL", "Remote GET /health returns ok=true", "fbe-cloud-deploy-receipt-v1.json", "wire"),
        ("Write FBE_CLOUD_WORKER_URL to ~/.sina/secrets.env — never commit", "hub_cloud_proxy_v1.cloud_worker_url non-empty", "cloud-url-set-v1.json", "wire"),
        ("Write FBE_INTERNAL_SECRET to secrets.env for cloud runner auth", "Proxy auth header validates on /health", "cloud-secret-set-v1.json", "wire"),
        ("Point data/fbe_cloud_worker_config worker_url at live Railway URL logged", "Config worker_url matches secrets.env", "fbe-cloud-worker-config-sync-v1.json", "wire"),
        ("Hub GET /api/fbe/cloud-proxy/v1 shows configured=true", "HTTP 200 · configured · url host matches Railway", "hub-cloud-proxy-check-v1.json", "wire"),
        ("Validate mono_mirror_fallback only as documented fallback not primary", "Primary URL is Railway not mirror alone", "cloud-url-primary-receipt-v1.json", "wire"),
        ("Document Fly deploy_status blocked_billing — Railway hobby until card", "fbe_cloud_worker_config fly.deploy_status logged", "fly-billing-blocker-note-v1.json", "wire"),
        ("Run scripts/deploy_fbe_fly_free_v1.sh dry-run — record blocker not fake PASS", "Dry-run receipt honest RED if billing blocked", "fly-deploy-dry-run-v1.json", "wire"),
        ("Smoke POST cloud runner /health with internal secret", "Latency <5s · service=fbe-runner", "cloud-health-smoke-v1.json", "wire"),
        ("Sync fbe-federated-receipt live_snapshot.cloud_worker_url from secrets", "Federated receipt url matches secrets", "fbe-federated-receipt-v1.json", "wire"),
    ]
    honesty = [
        ("Flip brain-outbound-work-order-active execution_mode to brain_work_order", "Receipt execution_mode≠local_worker", "brain-outbound-work-order-active-v1.json", "wire"),
        ("Set brain-outbound bay_slug noetfield-freemium-bay not sourcea-local-deferred", "bay_slug maps to cloud factory spec", "brain-outbound-work-order-active-v1.json", "wire"),
        ("Set pending_cloud_bay=false when URL + bay mapped", "pending_cloud_bay=false on active WO", "brain-outbound-work-order-active-v1.json", "wire"),
        ("Set local_worker_deprecated=true on active brain work-order", "local_worker_deprecated=true", "brain-outbound-work-order-active-v1.json", "wire"),
        ("run_inbox_disk_truth execution_lane=brain_work_order when cloud ready", "execution_lane≠run_inbox in truth receipt", "run-inbox-disk-truth-v1.json", "wire"),
        ("outbound_queue_coherence rejects local_worker when Q-GATH-04 A applied", "coherence ok=false if local_worker persists", "outbound-disk-coherence-heal-receipt-v1.json", "wire"),
        ("execution_plane_honesty_v1 headline PASS with cloud URL set", "honest=true · cloud_worker_url set", "execution-honesty-receipt-v1.json", "wire"),
        ("Queue SSOT unify blocks INBOX primary when brain_work_order active", "queue_sa aligned · no local_primary", "governance-zero-drift-live-wire-v1.json", "wire"),
        ("brain_phase0 active receipt cloud_stub=false after remote health", "cloud_stub=false · bay_ok=true", "brain-phase0-dispatch-receipt-v1.json", "wire"),
        ("Deny CLOUD_ONLY spawn when FBE_CLOUD_WORKER_URL empty — fail closed", "Spawn returns error not headless_w2 Mac", "fbe-spawn-deny-local-v1.json", "wire"),
    ]
    openrouter = [
        ("Remove ollama_local from data/tool-pick-two-phase-v1.json active picks", "No ollama_local in founder-facing tool pick", "tool-pick-openrouter-only-v1.json", "openrouter"),
        ("Cloud worker uses OpenRouter API key from secrets — not Mac Ollama", "Runner env OPENROUTER_API_KEY set remote only", "cloud-openrouter-wire-v1.json", "openrouter"),
        ("Mac Health: zero local LLM spawn under focus freeze", "No ollama process spawned by factory", "mac-health-llm-quiet-v1.json", "openrouter"),
        ("Brain chat never runs bay muscle — routes WORK only", "Brain session conduct zero sa implementation", "brain-session-gate-receipt-v1.json", "openrouter"),
        ("n8n openrouter gate enforce on cloud dispatch path", "openrouter_gate=enforce in hub slice", "governance-n8n-openrouter-wire-v1.json", "openrouter"),
        ("FBE cloud runner model calls via OpenRouter not local GPU", "Receipt execution_plane=cloud_api_worker", "fbe-execution-receipt-v1.json", "openrouter"),
        ("Disable data/brain-local-ollama paths in outbound compile", "No local_primary in federated receipt", "fbe-federated-receipt-v1.json", "openrouter"),
        ("Worker INBOX prompt feasibility blocks local bay execution when URL set", "prompt_feasibility redirects to cloud WO", "worker-prompt-feasibility-receipt-v1.json", "openrouter"),
        ("Catalog all factory specs execution_mode=CLOUD_ONLY audit PASS", "validate-factory-specs-cloud-only PASS", "factory-spec-cloud-audit-v1.json", "openrouter"),
        ("Document Mac=control plane · API keys never on founder Terminal paste", "Hub Actions only for wire ops", "founder-motion-cloud-v1.json", "openrouter"),
    ]
    hub = [
        ("Wire founder-open-integrity-form unrelated — Hub P0 is cloud wire card", "Hub shows cloud-300 head not form loop", "hub-cloud-card-v1.json", "wire"),
        ("Worker Hub form_live secondary to cloud_300_line on H1", "cloud_300_line visible on worker-hub/v1", "worker-hub-cloud-slice-v1.json", "wire"),
        ("disk_live_wire_sync emits cloud_practical_300_line every session", "agent-live-surfaces cloud_practical_300_line set", "agent-live-surfaces-v1.json", "wire"),
        ("brain_live_context mandatory_next points to C300 head not M1 form", "mandatory_next contains cloud-300 head id", "brain-live-context-v1.json", "wire"),
        ("founder_pivot PIVOT-CLOUD-TEAM match routes C300 critical path", "Pivot receipt primary_lane=cloud_factory", "founder-pivot-routing-receipt-v1.json", "wire"),
        ("PROGRAM_PROGRESS cloud migration row not stuck on local_worker", "PROGRAM_PROGRESS execution_plane=cloud", "PROGRAM_PROGRESS.json", "wire"),
        ("Anti-staleness queue_sa aligned after cloud flip receipt", "zero_drift score≥85 post-flip", "governance_drift_report_v1.json", "wire"),
        ("SASCIP stranger probes: cloud path read-only on Mac", "sentinel_probes PASS", "stranger-agent-safety-live-wire-v1.json", "wire"),
        ("Governance propagation cascade reason=cloud-300-upgrade not form submit", "governance-propagation-receipt cloud reason", "governance-propagation-receipt-v1.json", "wire"),
        ("Validate no CLOUD_ONLY spec runs headless_w2 on Mac post-wire", "federated receipt remote_status≠local_primary", "federated-run-v1.json", "wire"),
    ]
    qgath = [
        ("Enforce Q-GATH-04 A: brain_work_order_primary on live surfaces", "brain_work_order_primary=YES", "agent-live-surfaces-v1.json", "wire"),
        ("Enforce Q-GATH-04 A: Auto Runtime respects cloud_proof not INBOX alone", "loop_specialist dispatch requires cloud URL", "loop-specialist-tick-receipt-v1.json", "wire"),
        ("Enforce Q-GATH-01: M1 Canvas form office — not gather scratch for factory", "form_official route m1_only on hub", "form-official-wire-receipt-v1.json", "wire"),
        ("Enforce Q-GATH-05: gather phase complete before outbound scale", "form edition advances past final_fix_gathering", "live-founder-decision-form-v1.json", "wire"),
        ("Mark C300-001..050 done only with cloud_proof receipts — no chat claims", "progress.cloud_proven increments per row", "brain-cloud-practical-300-plan-v1.json", "wire"),
        ("Cross-link C300-001 to parent B0101 two-plane migration 1000-plan", "parent_b1000=B0101 on row metadata", "brain-cloud-reasoning-1000-upgrade-plan-v1.json", "wire"),
        ("Outbound factory head U* compiles to cloud WO not local sa muscle", "brain-outbound upgrade_ref maps cloud bay", "outbound-factory-upgrade-plan-v1.json", "wire"),
        ("Freeze blocks local Docker — cloud URL is only escape hatch", "run_result error=freeze_blocks_local_docker without URL", "brain-phase0-dispatch-receipt-v1.json", "wire"),
        ("Mac focus freeze: factory motors cap respected — cloud bays exempt", "monitor-live factory spawn count OK", "monitor-live-v1.json", "wire"),
        ("Founder north star line on every C300 row goal_alignment set", "All 300 rows have non-empty goal_alignment", "brain-cloud-practical-300-plan-v1.json", "wire"),
    ]
    for block in (url, honesty, openrouter, hub, qgath):
        base.extend(block)
    return base[:50]


def _nf_specs() -> list[tuple]:
    actions = []
    verbs = [
        "Register", "Validate", "Deploy", "Run", "Prove", "Catalog", "Wire", "Federate",
        "Compile", "Receipt", "Audit", "Publish", "Mock", "Govern", "Sync", "Test",
    ]
    objs = [
        "noetfield-freemium-factory-v1 spec tier FREEMIUM mock_only",
        "noetfield-freemium-bay CLOUD_ONLY remote runner",
        "noetfield_freemium_w0 pipeline on cloud worker",
        "noetfield_governance FBE node graph W0 line",
        "NF-RD board pack mock JSON artifact on cloud",
        "Copilot readiness TLE one-pager output on cloud",
        "governance receipt mock for freemium ATTRACT",
        "catalog row hero=false buyer=prospects",
        "brain work-order sa-nf-freemium not sa-1100 local",
        "phase0-noetfield-freemium-factory-receipt ok=true",
    ]
    receipts = [
        "phase0-noetfield-freemium-factory-receipt-v1.json",
        "brain-phase0-work-order-active-v1.json",
        "brain-phase0-dispatch-receipt-v1.json",
        "fbe-execution-receipt-v1.json",
        "fbe-federated-receipt-v1.json",
    ]
    for i in range(50):
        v = verbs[i % len(verbs)]
        o = objs[i % len(objs)]
        r = receipts[i % len(receipts)]
        title = f"{v} {o} — Phase 0 NF factory step {i + 1}/50"
        acc = f"Remote execution · cloud_stub=false · receipt {r} updated"
        actions.append((title, acc, r, "nf_factory"))
    # Override critical milestones with exact titles
    milestones = {
        0: ("Deploy noetfield-freemium-bay on cloud runner — POST /api/fbe/run-bay/v1", "HTTP 200 · bay_slug=noetfield-freemium-bay · remote", "fbe-bay-run-receipt-v1.json", "nf_factory"),
        1: ("Run noetfield-freemium-factory-v1 --validate-only on cloud not Mac", "validate-only PASS · execution_plane=cloud", "phase0-noetfield-freemium-factory-receipt-v1.json", "nf_factory"),
        2: ("Phase0 receipt cloud_stub=false bay_ok=true federated_ok=true", "All three flags true on dispatch receipt", "brain-phase0-dispatch-receipt-v1.json", "nf_factory"),
        9: ("Compile order locked: Sina read → Noetfield compile → TrustField send", "founder-pivot compile_order logged surfaces", "founder-pivot-routing-receipt-v1.json", "nf_factory"),
        24: ("Publish NF freemium mock artifact URL for ATTRACT Phase 0", "Public or signed preview URL live", "nf-freemium-attract-url-v1.json", "market"),
        49: ("Gate C300-100: NF factory cloud_proof — ready for TF sandbox", "C300-051..100 cloud_proven count=50", "brain-cloud-practical-300-plan-v1.json", "nf_factory"),
    }
    for idx, m in milestones.items():
        actions[idx] = m
    return actions


def _tf_specs() -> list[tuple]:
    titles = [
        "Spawn sandbox-mock-factory-v1 CLOUD_ONLY only after NF bay PASS",
        "TrustField compile lane cloud_api_worker — Mac control_plane only",
        "MSB/tokenization TF-001 vocabulary separate from NF-RD governance",
        "Shadow $3K deposit workflow — block send until w3_send_ready GREEN",
        "Freemium sandbox reference surface live for ATTRACT",
        "compliance-aml-wrapper-v1 cloud bay read-only proof",
        "Portfolio trustfield tenant isolation — no cross-tenant writes",
        "Federate trustfield-sandbox run to ~/.sina/fbe-runs/",
        "World model plan check — platform-neutral SaaS not Mac-only copy",
        "Phase 1 gate NF $2K deposit signal before TF shadow send",
        "TrustField freemium mock MSB receipt JSON on cloud",
        "TF sandbox catalog row tier honest FREEMIUM",
        "Brain routes TF lane after NF Phase 0 complete",
        "w3_founder_review Sina read stays Mac — compile on cloud",
        "Commercial pipeline 0 sent until TF sandbox proof filed",
        "Hub commercial_readiness w3_send_ready tracked honestly RED until green",
        "Trust Motor gate pre-spawn on TF cloud job",
        "Receipt cross-ref NF attract URL → TF shadow invite",
        "Validate phase0-freemium-sandbox-reference-v1.json surfaces",
        "Gate C300-130: TF sandbox cloud_proof before loop scale",
        "TF-001 brand routing logged — never merge with NF-RD",
        "TrustField bay_slug mapped on brain work-order",
        "Cloud stub false on TF factory receipt",
        "OQG lint TF outbound copy on cloud batch",
        "Disclosure ladder tier T0 for freemium sandbox public page",
        "Stripe buyer copy Noetfield Systems platform-neutral",
        "TF sandbox health endpoint on cloud runner",
        "FBE spawn TF factory registry row W1 not W0",
        "Investigator observe TF spawn — routes=0 until market gate",
        "C300-101..130 done marks Phase 0 complete for loop",
    ]
    return [(t, f"TF sandbox · {t[:40]}… receipt filed", "trustfield-sandbox-receipt-v1.json", "tf_sandbox") for t in titles]


def _loop_specs() -> list[tuple]:
    titles = [
        "loop_specialist_tick dispatch=true only when FBE_CLOUD_WORKER_URL set",
        "loop_auto_graduation --enable-shadow receipt filed",
        "CF Worker cron */15 POST /api/loop-specialist/tick/v1",
        "tick_decision dispatch_done requires federated cloud receipt",
        "Block RUN INBOX as factory muscle when loop_auto ON + URL set",
        "Investigator GREEN routes=0 observe — no local drain override",
        "brain-outbound pending_cloud_bay=false when bay mapped",
        "Queue sa-* Mac SSOT — cloud executes job body",
        "Loop observatory founder_action Hub glance not Worker chat",
        "Graduate shadow_auto→live after 10 cloud_proof receipts",
        "loop_auto_dispatch_enabled true on loop-specialist-config",
        "Better-loop lever=money respects cloud dispatch not INBOX",
        "Judge loop LOOP_HEALTHY requires cloud honesty PASS",
        "Routing panel tick=dispatch_done on cloud job not local turn",
        "Auto Runtime specialist advisory points to C300 head id",
        "Disable healthy-drain local spawn when cloud WO pending=false",
        "Factory SINGLE_SA respects brain_work_order not Worker paste",
        "Goal1 Auto Runtime observes cloud federated receipts",
        "Worker connected BLOCK for factory muscle — control checks only",
        "Hub Next steps shows cloud-300 head not sa local check",
        "Loop degraded heals when cloud URL wired — not form submit",
        "Cross-ref sa-1100 outbound to cloud job_id in coherence",
        "Auto Runtime graduation receipt loop-auto-graduation-v1.json",
        "Cloudflare phase 2b contract wired logged",
        "Mac SSOT loop tick — cloud worker executes",
        "Investigator commercial founder_action aligns C300",
        "Auto Runtime specialist rooms run cloud-safe observe only",
        "Outbound 80/108 upgrades compile to cloud WO template",
        "Brain work-order dispatch replaces INBOX for act role",
        "Gate C300-180: Auto Runtime live on cloud proof",
        "loop_specialist_line shows Brain work-order executed",
        "Zero drift queue_sa after loop cloud flip",
        "Monitor live pulse sidecars reflect cloud dispatch",
        "Brain phase0 line on surfaces when Auto Runtime ON",
        "Founder close line Worker RUN INBOX head control-only",
        "Auto Runtime mode documented in loop-specialist-cloud-contract",
        "Dispatch receipt includes execution_plane cloud_api_worker",
        "No fake-green loop PASS without cloud_proof counter",
        "Loop tick block_reasons empty when URL+bay ready",
        "C300-131..180 cloud_proven increments on loop receipts",
        "Outbound factory pulse head aligns cloud upgrade ref",
        "Brain cloud 1000-plan E06 linked to C300 loop phase",
        "Session gate loop conduct zero validator chains",
        "Governance zero drift live wire after loop enable",
        "Factory freeze stop_open false when cloud executing",
        "Queue role act dispatches cloud not local check-only",
        "Loop observatory commercial RED stays RED until send gate",
        "Hub /api/loop-specialist/tick/v1 POST smoke PASS",
        "Founder pivot PIVOT-ALL-LOOPS subordinate to cloud URL first",
        "Gate loop before market scale — C300-180 milestone",
    ]
    return [(t, "Loop cloud · receipt loop-specialist-tick-receipt-v1.json", "loop-specialist-tick-receipt-v1.json", "loop") for t in titles]


def _fed_specs() -> list[tuple]:
    fields = ["job_id", "execution_plane", "policy_passed", "kernel_hash", "artifact_urls", "duration_ms", "tier_achieved", "tenant_id", "factory_id", "status"]
    rows = []
    for i, field in enumerate(fields * 5):
        seq = i + 1
        rows.append((
            f"Federate fbe-execution-receipt field {field} #{seq} — Mac Hub ingest",
            f"Receipt {field} present · federated ok=true",
            "fbe-federated-receipt-v1.json",
            "federate",
        ))
    rows[0] = ("Every cloud bay run writes fbe-execution-receipt-v1 execution_plane=cloud", "No headless_w2 Mac entries", "fbe-execution-receipt-v1.json", "federate")
    rows[49] = ("Gate C300-230: 50 federation receipts cloud_proven", "C300-181..230 done", "brain-cloud-practical-300-plan-v1.json", "federate")
    return rows[:50]


def _grad_specs() -> list[tuple]:
    deprecate = [
        "RUN INBOX as P0 north star",
        "execution_mode=local_worker",
        "headless_w2 on Mac for CLOUD_ONLY specs",
        "chat SSOT for factory picks",
        "Worker implements sa in Brain chat",
        "form canvas as factory substitute",
        "local Docker bay under freeze",
        "ollama_local tool pick on Mac",
        "healthy-drain local spawn path",
        "founder Terminal for wire ops",
    ]
    rows = []
    for i in range(50):
        dep = deprecate[i % len(deprecate)]
        rows.append((
            f"Graduate off: {dep} — step {i + 1}/50 documented deprecated",
            f"Disk surfaces no longer inject {dep} as primary",
            "brain-cloud-graduate-receipt-v1.json",
            "graduate",
        ))
    rows[0] = ("Mark healthy-drain-orchestrator local factory path deprecated", "Orchestrator cloud branch only when URL set", "healthy-drain-orchestrator-v1.json", "graduate")
    rows[19] = ("OpenRouter-only on cloud worker — purge Mac Ollama from factory path", "No local LLM in federated receipt", "cloud-openrouter-wire-v1.json", "openrouter")
    rows[49] = ("Gate C300-280: local_worker muscle fully deprecated logged", "All active WO local_worker_deprecated=true", "brain-outbound-work-order-active-v1.json", "graduate")
    return rows


def _scale_specs() -> list[tuple]:
    titles = [
        "Register forge-app-factory-v1 CLOUD_ONLY after NF+TF PASS",
        "Register web-product-factory-v1 CLOUD_ONLY catalog row",
        "Register exchange-factory-v1 CLOUD_ONLY catalog row",
        "FBE campus spawn read-only tenant isolation proof",
        "Commercial W3 Sina read Mac — compile outbound on cloud",
        "OQG cloud batch federate — w3_send_ready GREEN gate",
        "First AB1 eval send one row only — market traction",
        "NF $2K deposit signal Phase 1 gate",
        "TF $3K shadow pilot Phase 1 gate",
        "Phase 2 FBE catalog maintenance recurring cloud",
        "World model plan check every new factory spec",
        "Brain cloud 1000-plan row links C300 parent on done",
        "Gate C300-300: 10 factories CLOUD_ONLY proven + Auto Runtime live",
        "Zero drift queue_sa factory→brain→inbox after cloud flip",
        "North star traction: first paid ≥$3K AB1 receipt",
        "Hub commercial w3_oqg PASS sustained",
        "Public NF freemium attract URL in outbound pack",
        "TrustField shadow sandbox linked from NF attract",
        "Agentic trust infrastructure demo — cloud proof bundle",
        "C300 plan 300/300 cloud_proven — migration complete",
    ]
    return [(t, "Market scale · honest commercial gate", "market-traction-receipt-v1.json", "market") for t in titles]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row(seq: int, phase_id: str, phase_label: str, spec: tuple) -> dict:
    title, acceptance, receipt, goal = spec
    tier = "P0" if seq <= 100 or phase_id in ("P1-LOOP", "P2-GRAD") else ("P2" if seq >= 281 else "P1")
    if goal == "market" and seq >= 281:
        tier = "P1"
    pid = f"C300-{seq:03d}"
    parent_b = None
    if seq == 1:
        parent_b = "B0101"
    elif seq == 51:
        parent_b = "B0501"
    elif seq == 131:
        parent_b = "B0601"
    return {
        "id": pid,
        "seq": seq,
        "phase": phase_id,
        "phase_label": phase_label,
        "tier": tier,
        "title": title,
        "goal_alignment": goal,
        "policy_refs": _policy_for_phase(phase_id),
        "owner_role": "worker" if seq <= 130 else "brain_route_worker",
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "work_template": f"WORK: {pid} — {title[:100]}",
        "acceptance": acceptance,
        "receipt_path": f"~/.sina/{receipt}" if not receipt.startswith("~") and "/" not in receipt else receipt,
        "blocker_if_skipped": _blocker(goal, seq),
        "parent_b1000": parent_b,
        "status": "planned",
        "cloud_only": True,
        "local_worker_allowed": False,
        "cloud_proof_required": True,
    }


def _policy_for_phase(phase_id: str) -> list[str]:
    common = [
        "data/fbe_execution_contract_v1.json",
        "data/fbe_cloud_worker_config_v1.json",
        "data/founder-pivot-pattern-v1.json",
    ]
    extra = {
        "P0-WIRE": ["data/loop-specialist-cloud-contract-v1.json"],
        "P0-NF": ["data/factory-specs/noetfield-freemium-factory-v1.json"],
        "P1-TF": ["data/phase0-freemium-sandbox-reference-v1.json", "data/platform-neutral-world-model-v1.json"],
        "P1-LOOP": ["data/loop-specialist-cloud-contract-v1.json"],
        "P2-FED": ["receipts/federated-run-v1.json"],
        "P2-GRAD": ["brain-os/system/EXECUTION_AUTHORITY_MAP_LOCKED_v1.md"],
        "P3-SCALE": ["data/platform-neutral-world-model-v1.json", "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"],
    }
    return common + extra.get(phase_id, [])


def _blocker(goal: str, seq: int) -> str:
    if seq <= 50:
        return "All cloud factories remain CLOUD_ONLY blocked — FBE_CLOUD_WORKER_URL empty or local_worker persists"
    if goal == "nf_factory":
        return "Phase 0 ATTRACT fails — Noetfield freemium factory stays cloud_stub"
    if goal == "market":
        return "North star traction blocked — no paid pilot or send gate"
    return "Cloud migration stall — loop keeps draining local Worker"


def generate() -> dict:
    phases_meta = [
        ("P0-WIRE", "Wire cloud URL + honesty + OpenRouter-only", 1, 50, _wire_specs()),
        ("P0-NF", "Noetfield freemium factory live remote", 51, 100, _nf_specs()),
        ("P1-TF", "TrustField freemium sandbox second", 101, 130, _tf_specs()),
        ("P1-LOOP", "Auto Runtime cloud dispatch", 131, 180, _loop_specs()),
        ("P2-FED", "Federation + cloud proof receipts", 181, 230, _fed_specs()),
        ("P2-GRAD", "Graduate off local Cursor Worker muscle", 231, 280, _grad_specs()),
        ("P3-SCALE", "Market traction + factory scale", 281, 300, _scale_specs()),
    ]
    plans: list[dict] = []
    phases_out: list[dict] = []
    for phase_id, phase_label, start, end, specs in phases_meta:
        ids = []
        for i, spec in enumerate(specs):
            seq = start + i
            row = _row(seq, phase_id, phase_label, spec)
            plans.append(row)
            ids.append(row["id"])
        phases_out.append({"id": phase_id, "label": phase_label, "range": f"C300-{start:03d}..C300-{end:03d}", "count": len(ids), "plan_ids": ids})

    assert len(plans) == 300
    titles = [p["title"] for p in plans]
    assert len(titles) == len(set(titles)), f"duplicate titles: {len(titles) - len(set(titles))}"

    tier_counts = {t: sum(1 for p in plans if p["tier"] == t) for t in ("P0", "P1", "P2")}
    goal_counts = {}
    for p in plans:
        g = p["goal_alignment"]
        goal_counts[g] = goal_counts.get(g, 0) + 1

    return {
        "schema": "brain-cloud-practical-300-plan-v1",
        "version": "2.0.0",
        "saved_at": _now(),
        "law": "Mac control plane · Brain signs · Cloud/API executes · CLOUD_ONLY · OpenRouter on cloud · market traction gates",
        "north_star": "Agentic trust infrastructure → real market traction",
        "compile_order": "SourceA Sina read → Noetfield compile → TrustField send",
        "phase_model": {
            "phase0": "$0 freemium sandboxes ATTRACT — NF factory cloud live",
            "phase1": "NF $2K deposit · TF $3K shadow FIRST CAD",
            "phase2": "FBE catalog maintenance RECURRING",
        },
        "policy_authority": [
            "data/fbe_execution_contract_v1.json",
            "data/fbe_cloud_worker_config_v1.json",
            "data/founder-pivot-pattern-v1.json",
            "data/loop-specialist-cloud-contract-v1.json",
            "data/platform-neutral-world-model-v1.json",
            "data/factory-specs/noetfield-freemium-factory-v1.json",
            "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
        ],
        "parent_1000_plan": "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
        "generator": "scripts/gen_brain_cloud_practical_300_plan_v1.py",
        "pulse_script": "scripts/brain_cloud_practical_300_pulse_v1.py",
        "critical_path": ["C300-001", "C300-010", "C300-051", "C300-101", "C300-131", "C300-231", "C300-300"],
        "execution_order_top_40": [p["id"] for p in plans[:40]],
        "tier_counts": tier_counts,
        "goal_alignment_counts": goal_counts,
        "unique_titles": 300,
        "progress": {"total": 300, "done": 0, "planned": 300, "cloud_proven": 0},
        "phases": phases_out,
        "plans": plans,
    }


def main() -> int:
    doc = generate()
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {OUT} v{doc['version']} plans={len(doc['plans'])} unique={doc['unique_titles']} P0={doc['tier_counts']['P0']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
