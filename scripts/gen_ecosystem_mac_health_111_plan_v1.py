#!/usr/bin/env python3
"""Generate 111 ecosystem upgrade plans — Mac Health · control plane · founder progress.

Law: ~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md
     data/founder-execution-model-v1.json
Output: data/ecosystem-mac-health-111-upgrade-plan-v1.json
Human: docs/SOURCEA_ECOSYSTEM_MAC_HEALTH_111_UPGRADE_PLAN_LOCKED_v1.md
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ecosystem-mac-health-111-upgrade-plan-v1.json"
DOC = ROOT / "docs" / "SOURCEA_ECOSYSTEM_MAC_HEALTH_111_UPGRADE_PLAN_LOCKED_v1.md"

# (title, acceptance, receipt, wired_to, execution_plane, tier_override|None)
Spec = tuple[str, str, str, str, str, str | None]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _e01_mac_health_silent() -> list[Spec]:
    return [
        ("Mac Health founder_glance UI — tab_count=0 contract enforced on /health", "ui_contract.tab_count==0 · ui_mode=founder_glance", "mac-health-ui-contract-v1.json", "scripts/mac_health_founder_glance_ui_v1.py", "mac_control_panel", "P0"),
        ("Mac Health pulse side_effects=False by default — no sound on poll", "mac-health-guard-server pulse never calls _notify when quiet", "mac-health-quiet-pulse-receipt-v1.json", "scripts/mac-health-guard-server.py", "mac_control_panel", "P0"),
        ("Exception-only UI — Hub badge green hides Mac Health page requirement", "Hub shows health_grade when LIVE; no modal", "hub-health-badge-v1.json", "scripts/hub_health_badge_v1.py", "mac_control_panel", "P1"),
        ("Auto relieve on cursor_hot when RSS >6GB — one tap pre-applied", "prevention auto_apply cursor_busy without founder click", "mac-health-prevention-v1.json", "scripts/mac_health_prevention_v1.py", "mac_control_panel", "P0"),
        ("Cursor session relief wired to cpu_cool_down action", "POST cpu_cool_down invokes cursor_session_relief_v1", "cursor-session-relief-latest-v1.json", "scripts/mac_health_cpu_relief_v1.py", "mac_control_panel", "P0"),
        ("Mac Health never-again log cap 50MiB on hub command-server.log", "log shield truncates before agent cat bomb", "mac-health-log-shield-v1.json", "scripts/mac_health_log_shield_v1.py", "mac_control_panel", "P0"),
        ("Visual proof disabled — critic_boot in_gate skips screencapture", "visual_proof.enabled=false · zero screencapture pids", "config/visual_proof.json", "scripts/critic_boot_v1.py", "mac_control_panel", "P0"),
        ("Film render frozen flag enforced every pulse", "commercial-film-render-frozen-v1.flag present", "commercial-film-render-frozen-v1.flag", "scripts/mac_health_never_again_v1.py", "mac_control_panel", "P0"),
        ("e2e-latest-v1.json written every recipe — honest grade logged", "overall_ok field present after pulse", "mac-health/e2e-latest-v1.json", "scripts/run-mac-health-recipe-v1.sh", "mac_control_panel", "P1"),
        ("Mac Health Guard.app bundle parity with scripts SSOT", "validate-mac-health-bundle-parity-v1.sh PASS", "mac-health-bundle-parity-v1.json", "scripts/validate-mac-health-bundle-parity-v1.sh", "mac_control_panel", "P1"),
        ("Silent menu bar dot — LIVE without opening :13024", "Optional menubar shows grade only when yellow/red", "mac-health-menubar-grade-v1.json", "brand/macos-apps/Mac Health Guard.app", "mac_control_panel", "P2"),
    ]


def _e02_control_plane() -> list[Spec]:
    return [
        ("mac-control-plane-v1.flag default on founder boot", "enter-mac-control-plane-v1.sh creates flag", "mac-control-plane-v1.flag", "scripts/mac_control_plane_v1.py", "mac_control_panel", "P0"),
        ("factory_control drain_spawn blocked when control plane active", "spawn_blocked reason=mac_control_plane", "factory-mode-v1.json", "scripts/factory_control_v1.py", "mac_control_panel", "P0"),
        ("cli-disabled-v1.flag — no local CLI drain on Mac body", "autorun_dispatcher exits when cli-disabled", "cli-disabled-v1.flag", "scripts/autorun_dispatcher_v1.py", "mac_control_panel", "P0"),
        ("autorun-worker launchd booted out in control plane enter", "com.sourcea.autorun-worker not loaded", "mac-control-plane-receipt-v1.json", "scripts/mac_control_plane_v1.py", "mac_control_panel", "P0"),
        ("founder-mac-reset-v1.sh — soft and hard relief chain", "founder-mac-reset completes <60s soft", "mac-health/founder-reset-receipt-v1.json", "scripts/founder-mac-reset-v1.sh", "mac_control_panel", "P0"),
        ("Founder session pressure law in MAC_CONTROL_PLANE_LOCKED.md", "Doc contains Founder session pressure law section", "MAC_CONTROL_PLANE_LOCKED.md", "Desktop/MacLaw/", "mac_control_panel", "P0"),
        ("machine-execution-plane-registry mac_role=control_plane_only", "registry mac_role matches SSOT", "machine-execution-plane-registry-v1.json", "scripts/founder_execution_model_v1.py", "mac_control_panel", "P0"),
        ("api-disabled absent — cloud APIs callable from Mac cockpit", "paid_engine_gate allows API when founder-work-mode", "founder-work-mode-v1.flag", "scripts/paid_engine_gate_v1.py", "mac_control_panel", "P0"),
        ("Control plane validate script ship gate", "validate-mac-control-plane-v1.sh PASS", "mac-health/mac-control-plane-assess-v1.json", "scripts/validate-mac-control-plane-v1.sh", "mac_control_panel", "P0"),
        ("Wire FR-006 FR-009 into founder-execution-model founder_rules_live", "FR-006 FR-009 wired=true logged", "founder-execution-model-v1.json", "scripts/founder_execution_model_v1.py", "mac_control_panel", "P1"),
    ]


def _e03_hub_glance() -> list[Spec]:
    titles = [
        ("Hub home strip — Mac Health grade + Relieve deep-link to :13024", "worker-hub/v1 shows health_grade field", "hub-health-strip-v1.json"),
        ("Hub pressure badge — OK/HOT/STOP STACKING from ecosystem-pressure-v1", "Badge reads ~/.sina/ecosystem-pressure-v1.json", "ecosystem-pressure-v1.json"),
        ("Hub cloud factory heartbeat — last tick per main_cloud_factory", "Lists fbe_railway supabase video_ad status", "cloud-factory-heartbeat-v1.json"),
        ("Hub founder mandatory_next — not buried under architect tabs", "command_center shows single next_action", "command-data-canonical.json"),
        ("Hub form_pick primary — human fork on FORM_OFFICIAL not chat A/B/C", "form route reachable · agent-submit blocked", "form-official-wire-receipt-v1.json"),
        ("Hub /health truth — hub_online vs hub_health_ok separate", "health JSON distinguishes service vs log bomb", "hub-health-truth-v1.json"),
        ("Hub factory_now read-only when FREEZE — no spawn CTA", "factory_now mode FREEZE visible", "factory-now-v1.json"),
        ("Hub Auto Runtime specialist tick button — POST cloud dispatch only", "tick receipt execution_plane=cloud_api_worker", "loop-specialist-tick-receipt-v1.json"),
        ("Hub degrade Routing Panel link — optional not default home", "Hub hero links Mac Health before :8780", "hub-nav-priority-v1.json"),
        ("Hub session gate status — agent boot order visible", "session_gate row on worker-hub slice", "agent-session-gate-receipt-v1.json"),
        ("Hub PROGRAM_PROGRESS cloud migration row honest", "execution_plane not local_worker", "PROGRAM_PROGRESS.json"),
    ]
    return [
        (t, acc, r, "scripts/sina-command-server.py", "mac_control_panel", "P0" if i < 6 else "P1")
        for i, (t, acc, r) in enumerate(titles)
    ]


def _e04_validator_cloud() -> list[Spec]:
    deny = [
        "validate-all-e2e-v1.sh",
        "validate-mac-law-surfaces-e2e-v1.sh",
        "run-mac-health-recipe-v1.sh --build",
        "validate-e2e-fast-ladder-v1.sh",
        "validate-mcp-chain-e2e-v1.sh",
        "verify-mac-law-routing-panel-e2e.sh",
        "validate-hub-stabilization-e2e-light-v1.sh",
        "validate-form-official-e2e-v1.sh",
        "wbc-e2e.sh",
        "full-e2e-mono.sh",
    ]
    rows: list[Spec] = []
    for i, script in enumerate(deny):
        rows.append((
            f"Founder-session deny gate blocks {script} when control-plane flag set",
            f"Script exits 2 with message founder_session_no_heavy_gates",
            f"founder-session-gate-deny-{i+1:02d}-v1.json",
            f"scripts/{script.split('/')[-1]}",
            "cloud_api_worker" if i >= 5 else "mac_control_panel",
            "P0" if i < 5 else "P1",
        ))
    return rows


def _e05_cloud_heartbeat() -> list[Spec]:
    factories = [
        "fbe_railway", "supabase_edge", "video_ad_factory", "noetfield_freemium_bay",
        "trustfield_sandbox", "witnessbc_proof_lab", "fal_rendering_bridge", "openrouter_cloud",
    ]
    rows: list[Spec] = []
    for i, fid in enumerate(factories):
        rows.append((
            f"Cloud factory {fid} — public HTTPS health receipt logged",
            f"cloud-factories-online-only lists {fid} online=true with url",
            f"cloud-factory-{fid}-heartbeat-v1.json",
            "data/cloud-factories-online-only-v1.json",
            "cloud_api_worker",
            "P0" if i < 4 else "P1",
        ))
    rows.extend([
        ("Auto Runtime specialist Cloudflare cron POST hub tick when auto enabled", "Worker cron hits hub_api dispatch=true", "loop-specialist-cloud-cron-v1.json", "data/loop-specialist-cloud-contract-v1.json", "cloud_api_worker", "P0"),
        ("Brain phase0 work-order dispatch — never local Worker INBOX muscle", "brain_phase0 receipt cloud_stub=false", "brain-phase0-dispatch-receipt-v1.json", "scripts/brain_phase0_work_order_v1.py", "cloud_api_worker", "P0"),
        ("FBE cloud proxy Hub GET /api/fbe/cloud-proxy/v1 configured=true", "Railway URL in secrets not Mac motor", "hub-cloud-proxy-check-v1.json", "scripts/hub_cloud_proxy_v1.py", "cloud_api_worker", "P0"),
    ])
    return rows[:11]


def _e06_cursor_hygiene() -> list[Spec]:
    return [
        ("Cursor installed /Applications/Cursor.app not DMG volume", "cursor_session_relief reports Applications path", "cursor-session-relief-latest-v1.json", "scripts/cursor_session_relief_v1.py", "mac_control_panel", "P0"),
        ("cursor-day-relief-v1.sh --restart end-of-day ritual documented in Mac Law", "MAC_CONTROL_PLANE mentions hard reset", "cursor-day-relief-receipt-v1.json", "scripts/cursor-day-relief-v1.sh", "mac_control_panel", "P0"),
        ("Warn when renderer RSS >2800MB — banner in Mac Health", "cursor-hot-banner visible when threshold crossed", "mac-health-live-v1.json", "scripts/mac_health_live_v1.py", "mac_control_panel", "P0"),
        ("Cap extension-host count — recommend close windows at 4+", "probe reports extension_hosts>=4 recommendation", "cursor-session-relief-latest-v1.json", "scripts/cursor_session_relief_v1.py", "mac_control_panel", "P0"),
        ("Trim Cursor logs >100MB without restart", "cursor_session_relief --trim frees MB", "cursor-session-relief-latest-v1.json", "scripts/cursor_session_relief_v1.py", "mac_control_panel", "P1"),
        ("Kill DMG mount prompt in never-again probe", "cursor_dmg finding when /Volumes/Cursor Installer", "mac-health-never-again-v1.json", "scripts/mac_health_never_again_v1.py", "mac_control_panel", "P0"),
        ("One Cursor window policy in agent cursor rules", "mac-control-plane.mdc says one window target", ".cursor/rules/mac-control-plane.mdc", "Desktop/MacLaw/", "mac_control_panel", "P1"),
        ("founder-mac-reset --hard chains cursor restart", "hard flag triggers cursor-day-relief --restart", "founder-reset-receipt-v1.json", "scripts/founder-mac-reset-v1.sh", "mac_control_panel", "P0"),
        ("Mac Health cursor_hot mode does not play sound", "notifications_enabled false during cursor_hot", "mac-health-prevention-v1.json", "scripts/mac_health_settings_v1.py", "mac_control_panel", "P0"),
        ("Post-chat mandatory hard reset reminder on Hub after 4h session", "Hub shows cursor_reset_due when session long", "hub-cursor-session-nudge-v1.json", "scripts/sina-command-server.py", "mac_control_panel", "P2"),
    ]


def _e07_app_demotion() -> list[Spec]:
    apps = [
        ("Routing Panel :8780", "on_demand not RunAtLoad default", "com.sourcea.routing-panel"),
        ("Chat Unify :13023", "lazy start only when ASF opens lane", "chat-unify-server.py"),
        ("Apple Health :13025", "lazy start only when ASF opens lane", "apple-health-server.py"),
        ("N8N Integration :13026", "lazy start only when ASF opens lane", "n8n-integration-server.py"),
        ("goal1_lane_broker brain-poll", "pause when founder-work-mode unless ASF", "goal1_lane_broker.py"),
        ("Mac Law :8781", "keep minimal — no live architect poll", "mac-law-server.py"),
        ("Hub :13020", "always on — sole daily cockpit", "sina-command-server.py"),
        ("Mac Health :13024", "always on — silent pulse", "mac-health-guard-server.py"),
        ("Desktop 6-app sprawl doc — founder minimum 2 URLs", "MAC_CONTROL_PLANE lists daily minimum", "MAC_CONTROL_PLANE_LOCKED.md"),
        ("install-mac-law-desktop-all.sh — optional apps unchecked default", "install script documents lazy apps", "install-mac-law-desktop-all.sh"),
    ]
    return [
        (f"Demote/lazy: {name}", acc, f"app-demote-{i+1:02d}-v1.json", wired, "mac_control_panel", "P0" if i < 5 else "P1")
        for i, (name, acc, wired) in enumerate(apps)
    ]


def _e08_brain_dispatch() -> list[Spec]:
    return [
        ("Brain signs work orders — execution_plane cloud_api_worker only", "brain_outbound WO execution_plane set", "brain-outbound-work-order-active-v1.json", "scripts/brain_outbound_work_order_v1.py", "cloud_api_worker", "P0"),
        ("Brain session gate — no local ACT during founder-work-mode", "agent_session_gate blocks ACT spawn", "agent-session-gate-receipt-v1.json", "scripts/agent_session_gate_run_v1.py", "mac_control_panel", "P0"),
        ("Brain dual-mode — narrator default not executor on Mac", "BRAIN_CORE_EXECUTOR doc linked in plan", "brain-os/system/BRAIN_CORE_EXECUTOR_LOCKED_v1.md", "brain-os/system/", "cloud_api_worker", "P0"),
        ("next-execution-pointer synced — cloud handoff not INBOX rewind", "sync_next_execution_pointer_v1 PASS", "next-execution-pointer-v1.json", "scripts/sync_next_execution_pointer_v1.py", "cloud_api_worker", "P0"),
        ("loop_specialist observe_only default — dispatch only when graduated", "loop_auto_dispatch_enabled false default", "loop-specialist-config-v1.json", "scripts/loop_specialist_tick_v1.py", "mac_control_panel", "P0"),
        ("Brain cloud 1000-plan cross-ref M111 in cross_ref block", "brain-cloud-reasoning cross_ref ecosystem_111", "brain-cloud-reasoning-1000-upgrade-plan-v1.json", "scripts/gen_brain_cloud_reasoning_1000_plan_v1.py", "cloud_api_worker", "P1"),
        ("Brain live context mandatory_next points M111 head not form loop", "mandatory_next contains M111-001", "brain-live-context-v1.json", "scripts/brain_l1_brief_consequence_v1.py", "mac_control_panel", "P1"),
        ("Deny healthy-drain local spawn under control plane", "drain_spawn_allowed blocked", "healthy-drain-orchestrator-v1.json", "scripts/healthy_drain_orchestrator_v1.py", "mac_control_panel", "P0"),
        ("Brain phase0 cloud_stub=false gate before founder scale", "phase0 receipt bay_ok", "brain-phase0-dispatch-receipt-v1.json", "scripts/brain_phase0_work_order_v1.py", "cloud_api_worker", "P0"),
        ("Execution authority map L1 brain routes L3 workers build", "authority.yaml execution_authority true L1 only", "brain-os/system/authority.yaml", "brain-os/system/EXECUTION_AUTHORITY_MAP_LOCKED_v1.md", "cloud_api_worker", "P1"),
    ]


def _e09_founder_progress() -> list[Spec]:
    return [
        ("agent-live-surfaces founder_execution_model_line every wire-sync", "line contains Mac=control_plane_only", "agent-live-surfaces-v1.json", "scripts/founder_execution_model_v1.py", "mac_control_panel", "P0"),
        ("PROGRAM_PROGRESS row ecosystem_mac_health_111", "progress pct tracked for M111 plan", "PROGRAM_PROGRESS.json", "scripts/plans_unified_upgrade_v1.py", "mac_control_panel", "P0"),
        ("Hub command_center must_do_today max 3 items", "must_do_today length <=3", "command-data.json", "scripts/sina-command-server.py", "mac_control_panel", "P1"),
        ("Founder picks on FORM_OFFICIAL — chat does not hold A/B/C", "founder-picks-applied jsonl append on pick", "founder-picks-applied-v1.jsonl", "scripts/form_official_pick_v1.py", "mac_control_panel", "P0"),
        ("M111 critical path head visible on Hub H1", "cloud_111_line or ecosystem_111_head on hub", "worker-hub-cloud-slice-v1.json", "scripts/worker_hub_v1.py", "mac_control_panel", "P0"),
        ("plans_unified_upgrade syncs M111 progress counts", "plans-unified receipt lists ecosystem_111", "plans-unified-upgrade-receipt-v1.json", "scripts/plans_unified_upgrade_v1.py", "mac_control_panel", "P0"),
        ("Daily founder boot script single entry enter-mac-control-plane", "enter-founder-work-mode aliases control plane", "enter-mac-control-plane-v1.sh", "scripts/enter-mac-control-plane-v1.sh", "mac_control_panel", "P0"),
        ("Fail immediate — no fake-green on M111 done without receipt", "status=done requires execution_proof", "ecosystem-mac-health-111-upgrade-plan-v1.json", "scripts/plans_unified_upgrade_v1.py", "mac_control_panel", "P0"),
        ("Marketplace Card 1 progress linked from M111 E09 rows", "FR-003 referenced in goal_alignment market", "founder-execution-model-v1.json", "data/founder-execution-model-v1.json", "cloud_api_worker", "P1"),
        ("Founder zero-ui-drift flag respected on Hub projections", "founder-zero-ui-drift-v1.flag honored", "founder-zero-ui-drift-v1.flag", "scripts/hub_projection_sync_v1.py", "mac_control_panel", "P1"),
    ]


def _e10_agent_gates() -> list[Spec]:
    return [
        ("mac-health-agent-mandates enforced every pulse", "validate-mac-health-agent-mandates-v1.sh PASS", "agent-mandates-latest-v1.json", "scripts/mac_health_agent_mandates_v1.py", "mac_control_panel", "P0"),
        ("Cursor rule mac-control-plane alwaysApply", "MacLaw and SourceA .cursor/rules present", "mac-control-plane.mdc", "Desktop/MacLaw/.cursor/rules/", "mac_control_panel", "P0"),
        ("Agent boot order — Mac Law → control plane → health mandates", "MAC_AGENT_ENTRY_INDEX step 2-3", "MAC_AGENT_ENTRY_INDEX_LOCKED.md", "Desktop/MacLaw/", "mac_control_panel", "P0"),
        ("BAVT closeout — validate-mac-control-plane before Mac ship", "Agent checklist includes validate", "MAC_CONTROL_PLANE_LOCKED.md", "scripts/validate-mac-control-plane-v1.sh", "mac_control_panel", "P0"),
        ("Agent MUST NOT bootstrap autorun-worker during founder session", "mandates violation autorun_loaded", "agent-mandates-latest-v1.json", "scripts/mac_health_agent_mandates_v1.py", "mac_control_panel", "P0"),
        ("Agent MUST NOT run parallel validator loops", "Documented in founder session pressure law", "MAC_CONTROL_PLANE_LOCKED.md", "Desktop/MacLaw/", "mac_control_panel", "P0"),
        ("Agent MUST NOT re-enable visual_proof without ASF", "mandates visual_proof_enabled violation", "config/visual_proof.json", "scripts/mac_health_agent_mandates_v1.py", "mac_control_panel", "P0"),
        ("mac_law_mandatory_v1 enforce on session start", "validate-mac-law-mandatory-v1.sh PASS", "mac-law-mandatory-receipt-v1.json", "scripts/mac_law_mandatory_v1.py", "mac_control_panel", "P0"),
        ("paid_engine_gate respects founder-work-mode for API", "API not blocked when auto-run-disabled absent", "paid-engine-gate-receipt-v1.json", "scripts/paid_engine_gate_v1.py", "mac_control_panel", "P0"),
        ("Agent session gate pipelines_policy wired", "validate-founder-hospital-gate PASS", "agent-session-gate-receipt-v1.json", "scripts/validate-founder-hospital-gate-v1.sh", "mac_control_panel", "P1"),
    ]


def _e11_pressure_pulse() -> list[Spec]:
    return [
        ("ecosystem-pressure-v1.json written every Mac Health pulse", "pressure budget cursor/control/optional fields", "ecosystem-pressure-v1.json", "scripts/mac_health_live_v1.py", "mac_control_panel", "P0"),
        ("Pressure badge STOP STACKING when 2+ deny layers active", "Badge red when validators_running+chrome_debug", "ecosystem-pressure-v1.json", "scripts/ecosystem_pressure_v1.py", "mac_control_panel", "P0"),
        ("founder_session_gate_v1.py central deny list for heavy scripts", "Single module imported by validators", "founder-session-gate-v1.json", "scripts/founder_session_gate_v1.py", "mac_control_panel", "P0"),
        ("Cloud CI job validate-ship-gates — surfaces e2e off Mac", "Railway/GitHub workflow runs surfaces e2e", "cloud-ship-gates-ci-v1.json", ".github/workflows/", "cloud_api_worker", "P1"),
        ("M111 plan pulse script — progress line for Hub", "ecosystem_mac_health_111_plan_pulse_v1.py --json", "ecosystem-111-pulse-receipt-v1.json", "scripts/ecosystem_mac_health_111_plan_pulse_v1.py", "mac_control_panel", "P0"),
        ("Cross-link M111 to brain-cloud-practical-300 parent rows", "C300 wire rows cite M111 for Mac health", "brain-cloud-practical-300-plan-v1.json", "data/brain-cloud-practical-300-plan-v1.json", "mac_control_panel", "P1"),
        ("Unified plans orchestrator includes ecosystem_111", "plans_unified cross_ref ecosystem_mac_health_111", "plans-unified-upgrade-receipt-v1.json", "scripts/plans_unified_upgrade_v1.py", "mac_control_panel", "P0"),
        ("Gate M111-111 complete — ecosystem optimized for founder session", "111/111 done with receipts · critical path green", "ecosystem-111-complete-v1.json", "scripts/gen_ecosystem_mac_health_111_plan_v1.py", "mac_control_panel", "P0"),
    ]


EPICS: list[tuple[str, str, list[Spec]]] = [
    ("E01", "Mac Health silent auto heal", _e01_mac_health_silent()),
    ("E02", "Control plane pressure law", _e02_control_plane()),
    ("E03", "Hub founder glance merge", _e03_hub_glance()),
    ("E04", "Validator cloud relocation", _e04_validator_cloud()),
    ("E05", "Cloud factory heartbeat", _e05_cloud_heartbeat()),
    ("E06", "Cursor session hygiene", _e06_cursor_hygiene()),
    ("E07", "App sprawl demotion", _e07_app_demotion()),
    ("E08", "Brain dispatch cloud only", _e08_brain_dispatch()),
    ("E09", "Founder progress surfaces", _e09_founder_progress()),
    ("E10", "Agent obedience gates", _e10_agent_gates()),
    ("E11", "Pressure budget pulse wire", _e11_pressure_pulse()),
]


def _row(seq: int, epic_id: str, epic_label: str, spec: Spec) -> dict:
    title, acceptance, receipt, wired, plane, tier_override = spec
    tier = tier_override or ("P0" if seq <= 40 else ("P1" if seq <= 90 else "P2"))
    rid = f"M111-{seq:03d}"
    receipt_path = receipt if receipt.startswith("~") or "/" in receipt else f"~/.sina/{receipt}"
    return {
        "id": rid,
        "seq": seq,
        "epic": epic_id,
        "epic_label": epic_label,
        "tier": tier,
        "title": title,
        "goal_alignment": "mac_health_founder" if plane == "mac_control_panel" else "cloud_execute",
        "execution_plane": plane,
        "control_plane": "mac_hub",
        "wired_to": wired,
        "work_template": f"WORK: {rid} — {title[:120]}",
        "acceptance": acceptance,
        "receipt_path": receipt_path,
        "status": "planned",
        "cloud_proof_required": plane == "cloud_api_worker",
        "local_worker_allowed": False,
        "founder_session_safe": plane == "mac_control_panel" and "deny" not in title.lower()[:20],
    }


def _critical_path() -> list[str]:
    return ["M111-001", "M111-012", "M111-023", "M111-034", "M111-045", "M111-056", "M111-078", "M111-111"]


def generate() -> dict:
    upgrades: list[dict] = []
    seq = 0
    epic_counts: dict[str, int] = {}
    for epic_id, epic_label, specs in EPICS:
        epic_counts[epic_id] = len(specs)
        for spec in specs:
            seq += 1
            upgrades.append(_row(seq, epic_id, epic_label, spec))

    assert len(upgrades) == 111, f"expected 111 got {len(upgrades)}"

    p0 = sum(1 for u in upgrades if u["tier"] == "P0")
    p1 = sum(1 for u in upgrades if u["tier"] == "P1")
    p2 = sum(1 for u in upgrades if u["tier"] == "P2")

    return {
        "schema": "ecosystem-mac-health-111-upgrade-plan-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "law": "Mac = control panel · Mac Health = silent auto heal · validators/E2E on cloud · founder progress honest logged",
        "waves": {
            "W1": [
                f"M111-{i:03d}"
                for i in range(2, 38)
            ],
            "W1_label": "P0 wave 1 — Mac Health silent · Hub glance · validator deny · control plane",
            "W1_gate": "scripts/validate-m111-p0-wave1-v1.sh",
        },
        "human_doc": "docs/SOURCEA_ECOSYSTEM_MAC_HEALTH_111_UPGRADE_PLAN_LOCKED_v1.md",
        "parent_law": [
            "~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md",
            "data/founder-execution-model-v1.json",
            "data/machine-execution-plane-registry-v1.json",
        ],
        "generator": "scripts/gen_ecosystem_mac_health_111_plan_v1.py",
        "pulse_script": "scripts/ecosystem_mac_health_111_plan_pulse_v1.py",
        "validator": "scripts/validate-ecosystem-mac-health-111-plan-v1.sh",
        "orchestrator": "scripts/plans_unified_upgrade_v1.py",
        "cross_ref": {
            "brain_cloud_1000": "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
            "brain_cloud_practical_300": "data/brain-cloud-practical-300-plan-v1.json",
            "outbound_factory_100": "data/outbound-factory-100-upgrade-plan-v1.json",
            "founder_execution_model": "data/founder-execution-model-v1.json",
            "loop_specialist_cloud": "data/loop-specialist-cloud-contract-v1.json",
        },
        "tier_counts": {"P0": p0, "P1": p1, "P2": p2},
        "epic_counts": epic_counts,
        "critical_path": _critical_path(),
        "founder_rules_addressed": ["FR-001", "FR-002", "FR-006", "FR-008", "FR-009"],
        "progress": {"total": 111, "done": 0, "planned": 111, "pct": 0, "mac_proven": 0, "cloud_proven": 0},
        "upgrades": upgrades,
    }


def write_doc(plan: dict) -> None:
    lines = [
        "# SourceA Ecosystem Mac Health 111 Upgrade Plan — LOCKED (v1)",
        "",
        f"**Saved:** {plan['saved_at']} · **Generator:** `{plan['generator']}`",
        "",
        "## One sentence",
        "",
        f"> **{plan['law']}**",
        "",
        "## Critical path",
        "",
    ]
    for cid in plan["critical_path"]:
        row = next(u for u in plan["upgrades"] if u["id"] == cid)
        lines.append(f"- **{cid}** — {row['title']}")
    lines.extend([
        "",
        "## Epics",
        "",
        "| Epic | Count | Focus |",
        "|------|-------|-------|",
    ])
    for epic_id, label, _ in EPICS:
        lines.append(f"| {epic_id} | {plan['epic_counts'][epic_id]} | {label} |")
    lines.extend([
        "",
        "## Tiers",
        "",
        f"- **P0:** {plan['tier_counts']['P0']} — founder feel + pressure law",
        f"- **P1:** {plan['tier_counts']['P1']} — structural merge + cloud CI",
        f"- **P2:** {plan['tier_counts']['P2']} — polish",
        "",
        "## Commands",
        "",
        "```bash",
        "python3 scripts/gen_ecosystem_mac_health_111_plan_v1.py --write",
        "python3 scripts/ecosystem_mac_health_111_plan_pulse_v1.py --json",
        "bash scripts/validate-ecosystem-mac-health-111-plan-v1.sh",
        "python3 scripts/plans_unified_upgrade_v1.py --sync",
        "```",
        "",
        "**Parent:** `MAC_CONTROL_PLANE_LOCKED.md` · `founder-execution-model-v1.json`",
    ])
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write JSON + doc")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    plan = generate()
    if args.write or not args.json:
        OUT.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        write_doc(plan)
        print(f"Wrote {OUT} ({len(plan['upgrades'])} upgrades)")
        print(f"Wrote {DOC}")
    if args.json:
        print(json.dumps({"ok": True, "total": len(plan["upgrades"]), "critical_path": plan["critical_path"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
