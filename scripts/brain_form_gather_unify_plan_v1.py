#!/usr/bin/env python3
"""Brain FORM_OFFICIAL post-gather — unify · plan · route (fail-closed).

Reads: ~/.sina/live-founder-decision-form-extraction-v1.json
Writes: data/brain-form-gather-unify-routing-plan-v1.json
        ~/.sina/brain-form-gather-unify-routing-plan-v1.json
Law: SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md · BRAIN_UNIFIED_RULES
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
EXTRACTION = SINA / "live-founder-decision-form-extraction-v1.json"
OUT_DATA = ROOT / "data/brain-form-gather-unify-routing-plan-v1.json"
OUT_SINA = SINA / "brain-form-gather-unify-routing-plan-v1.json"

FAIL_POLICY = "FAIL_IMMEDIATE_NO_TEMPER"
BUNDLE_PATH = ROOT / "data" / "sourcea_agentic_unified_bundle_v1.json"
IDENTITY_APEX = "SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md"

ROUTING_LANES = {
    "founder": "Hub FORM_OFFICIAL M1 Canvas · ASF FIVE-STEP PICK",
    "brain": "SourceA Brain — sign work order · route · no Worker paste",
    "worker": "SourceA Worker — RUN INBOX · bounded WORK only",
    "maintainer": "Maintainer — validators · hub wire · anti-staleness",
    "fbe_cloud": "FBE execution plane — cloud headless · receipts federate Mac",
    "portfolio": "TrustField · VIRLUX · Noetfield · PLUS ONE read-only patterns",
}

WAVE_SPECS: list[dict] = [
    {
        "id": "WAVE-0",
        "title": "Language + chat forks (never chat-only)",
        "tier": "P0_final_fix",
        "question_ids": [
            "Q-CHAT-LANG-01",
            "Q-CHAT-PLUSONE-01",
            "Q-CHAT-NEXT-P0-01",
            "Q-CHAT-CLOUD-01",
            "Q-CHAT-PUBLISH-01",
        ],
        "executor_after_pick": "brain",
        "plan": "Founder picks lock agent voice + P0 sequencing. Brain applies to vocabulary inject + daily routing.",
        "proof": "canvas_form_apply_picks_v1.py · vocabulary_guard_v1.py --tooling",
    },
    {
        "id": "WAVE-1",
        "title": "Authorize UNIFY phase (meta already picked)",
        "tier": "P0_meta",
        "question_ids": ["Q-FINAL-05", "Q-GATH-05"],
        "executor_after_pick": "brain",
        "plan": "Founder confirms gather complete → Brain runs unify organize prioritize on 84 rows.",
        "proof": "brain_form_gather_unify_plan_v1.py --json",
    },
    {
        "id": "WAVE-2",
        "title": "Strategic spine after FBE (north star)",
        "tier": "P0_final_fix",
        "question_ids": [
            "Q-FINAL-01",
            "Q-FINAL-02",
            "Q-FINAL-03",
            "Q-FINAL-04",
            "Q-FINAL-06",
            "Q-FINAL-07",
        ],
        "executor_after_pick": "brain",
        "plan": "Locks STRATEGIC-SLICE vs outbound vs FBE catalog · U031 bay · Mono never_sync · vocabulary · disk-first Brain law · Auto Runtime safety.",
        "proof": "brain_outbound_work_order_v1.py --json · queue_ssot_unify_v1.py",
    },
    {
        "id": "WAVE-3",
        "title": "Paradox conflicts — execution honesty",
        "tier": "P0_conflict",
        "question_ids": [
            "Q-CONF-B0503-CONSUMER",
            "Q-CONF-CREED-36V14",
            "Q-CONF-F002-BROKER",
            "Q-CONF-FALSE-DONE-GUARD",
            "Q-CONF-MCP-PHASE2",
            "Q-CONF-PLUSONE-MOTOR",
        ],
        "executor_after_pick": "maintainer",
        "plan": "Each pick wires validator or blocks false-done. FAIL immediate on honesty breach.",
        "proof": "validate-form-official-e2e-v1.sh · debug_e2e_governance_chain_v1.py",
    },
    {
        "id": "WAVE-4",
        "title": "Brain cloud execution plane (pre-LLM dispatch)",
        "tier": "P0_brain_cloud",
        "question_ids": [f"Q-BC-{i:02d}" for i in range(1, 11)],
        "executor_after_pick": "brain",
        "plan": "Defines who executes outbound · cloud honesty · compiler path · INBOX vs work-order · bay mapping.",
        "proof": "brain_outbound_work_order_v1.py · fbe_run_job_v1.py --dry-run",
    },
    {
        "id": "WAVE-5",
        "title": "Prior picks — receipt sync only (56 rows)",
        "tier": "picked",
        "question_ids": [],
        "executor_after_pick": "maintainer",
        "plan": "Do not re-ask. Maintainer syncs Canvas cards · hub projection · cascade receipt.",
        "proof": "form_official_wire_e2e_v1.py --sync-surfaces",
    },
    {
        "id": "WAVE-6",
        "title": "Integrity + enforcement + commercial (picked tiers)",
        "tier": "P1_P4_picked",
        "question_ids": [],
        "executor_after_pick": "worker",
        "plan": "Execute per locked §ANSWERED picks via RUN INBOX sa-* — not chat re-poll.",
        "proof": "validate-all-e2e-v1.sh",
    },
    {
        "id": "WAVE-7",
        "title": "Architect + gather no-lost (session 2026-06-19)",
        "tier": "P0_meta",
        "question_ids": [
            "Q-SESSION-GATHER-NO-LOST",
            "Q-SESSION-ARCH-REFSTD",
            "Q-SESSION-ARCH-PILLAR",
            "Q-SESSION-ARCH-UNIFY-PLAN",
            "Q-SESSION-ARCH-SCAFFOLD",
            "Q-SESSION-ARCH-GEMINI-WS",
        ],
        "executor_after_pick": "brain",
        "plan": "Locks chat→form law · SourceA reference standard · strategic pillar WORK routing · Brain unify SSOT · Gemini gap closes without fork.",
        "proof": "form_official_gather_extraction_v1.py --wire · brain_form_gather_unify_plan_v1.py",
    },
    {
        "id": "WAVE-8",
        "title": "Marketplace + multi-factory thread (Gemini · cloud cockpit)",
        "tier": "P0_final_fix",
        "question_ids": [
            "Q-MF-01",
            "Q-MF-02",
            "Q-MF-03",
            "Q-MF-04",
            "Q-MF-05",
            "Q-MF-06",
            "Q-MF-07",
            "Q-MF-08",
            "Q-MF-09",
            "Q-MF-10",
            "Q-MF-11",
            "Q-THREAD-DEPLOY-01",
            "Q-THREAD-10STEP-01",
        ],
        "executor_after_pick": "brain",
        "plan": (
            "Mac cockpit · Card1 npm · Proof tagline · billing→orchestration→Fal · "
            "Supabase edge · scripts vs apps · HUMAN_APPROVAL · blueprint SSOT · no fork · "
            "E2E deploy · 10-step scope"
        ),
        "proof": "docs/SOURCEA_MULTI_FACTORY_ENTERPRISE_BLUEPRINT_LOCKED_v1.md · validate-video-ad-factory-chain-v1.sh",
    },
    {
        "id": "WAVE-9",
        "title": "Session build + form cap (dedupe Q-MF-12 ↔ Q-GATH-06)",
        "tier": "P0_meta",
        "question_ids": [
            "Q-GATH-06",
            "Q-MF-12",
            "Q-SESSION-INBOX-NEXT",
            "Q-SESSION-FORM-BUILD",
            "Q-SESSION-TUNNEL-DEMO",
            "Q-SESSION-UNIFY-GO",
            "Q-SESSION-PHASE0-SPOT",
            "Q-SESSION-CLOUD-CF06",
            "Q-SESSION-WBC-SUMMARY",
        ],
        "executor_after_pick": "worker",
        "plan": "100 cap minder · parallel form+INBOX · defer tunnel · spot-check phase0 · local before CF06 federated.",
        "proof": "form_official_unify_open_picks_v1.py · phase0-freemium-sandbox-reference-v1.json",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_extraction() -> dict:
    if not EXTRACTION.is_file():
        raise SystemExit(f"FAIL: missing {EXTRACTION}")
    return json.loads(EXTRACTION.read_text(encoding="utf-8"))


def _row_index(rows: list[dict]) -> dict[str, dict]:
    return {str(r["id"]): r for r in rows if r.get("id")}


def build_plan() -> dict:
    ext = _load_extraction()
    rows = list(ext.get("rows") or [])
    by_id = _row_index(rows)
    fresh = [r["id"] for r in rows if not r.get("prior_pick")]

    waves_out: list[dict] = []
    for spec in WAVE_SPECS:
        qids = list(spec.get("question_ids") or [])
        if spec["id"] == "WAVE-5":
            qids = [r["id"] for r in rows if r.get("prior_pick")]
        if spec["id"] == "WAVE-6":
            qids = [
                r["id"]
                for r in rows
                if r.get("prior_pick")
                and str(r.get("gather_tier", "")).startswith(("P1", "P2", "P3", "P4"))
            ]
        wave_rows = [by_id[q] for q in qids if q in by_id]
        waves_out.append(
            {
                **spec,
                "question_count": len(wave_rows),
                "fresh_count": sum(1 for r in wave_rows if not r.get("prior_pick")),
                "questions": [
                    {
                        "id": r["id"],
                        "title": r.get("title"),
                        "recommended": r.get("recommended"),
                        "prior_pick": r.get("prior_pick"),
                        "reply_template": r.get("reply_template"),
                        "gather_tier": r.get("gather_tier"),
                    }
                    for r in wave_rows
                ],
                "route_lane": ROUTING_LANES.get(str(spec["executor_after_pick"]), spec["executor_after_pick"]),
                "fail_gate": FAIL_POLICY,
            }
        )

    dispatch_chain = [
        {"step": 1, "gate": "agent_session_gate_run_v1.py", "fail": "STOP — no advise"},
        {"step": 2, "gate": "live-founder-decision-form-v1.json", "fail": "STOP — no invent picks"},
        {"step": 3, "gate": "founder FIVE-STEP PICK on FORM_OFFICIAL", "fail": "STOP — no Worker dispatch"},
        {"step": 4, "gate": "brain_outbound_work_order sign", "fail": "STOP — no cloud spawn"},
        {"step": 5, "gate": "pre_write_guard_v1.py", "fail": "STOP — no disk write"},
        {"step": 6, "gate": "validate-* proof for lane", "fail": "STOP — FAIL immediate"},
        {"step": 7, "act": "Worker RUN INBOX or FBE cloud job", "fail": "receipt RED"},
    ]

    return {
        "ok": True,
        "schema": "brain-form-gather-unify-routing-plan-v1",
        "saved_at": _now(),
        "phase": "unify_plan_route",
        "source_a_identity_ssot": IDENTITY_APEX,
        "source_a_identity_bundle": str(BUNDLE_PATH),
        "source_a_identity_note": (
            "Runs and sells controlled agentic automation — pointer only; "
            "full prose lives in portfolio SSOT §0–§2b"
        ),
        "fail_policy": FAIL_POLICY,
        "fail_policy_note": "No tempering · validator FAIL = immediate STOP · chat cannot override disk",
        "extraction": {
            "path": str(EXTRACTION),
            "gathered_at": ext.get("gathered_at"),
            "total_count": ext.get("total_count"),
            "fresh_count": ext.get("fresh_count"),
            "prior_pick_count": ext.get("prior_pick_count"),
            "tier_counts": ext.get("tier_counts"),
        },
        "fresh_question_ids": fresh,
        "routing_lanes": ROUTING_LANES,
        "dispatch_chain": dispatch_chain,
        "waves": waves_out,
        "brain_next_actions": [
            "Form rows STAY on M1 until founder PICK — do not re-ask in chat",
            "Under cap 100: Brain builds (WAVE plans · RUN INBOX · validators)",
            "At cap 100: URGENT founder remind — pause new gathers",
            "Founder fills when ready — not blocking all build work",
        ],
        "form_minder": {
            "script": "scripts/form_official_minder_v1.py",
            "cap": 100,
            "warn_at": 90,
            "receipt": "~/.sina/form-official-minder-v1.json",
        },
        "proof_commands": [
            "python3 scripts/brain_form_gather_unify_plan_v1.py --json",
            "bash scripts/validate-form-official-e2e-v1.sh",
            "bash scripts/validate-all-e2e-v1.sh",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Brain post-gather unify plan + routing")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", default=True)
    args = ap.parse_args()
    plan = build_plan()
    if args.write:
        OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
        OUT_DATA.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        SINA.mkdir(parents=True, exist_ok=True)
        OUT_SINA.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        plan["paths"] = {"data": str(OUT_DATA), "sina": str(OUT_SINA)}
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(
            f"OK: brain-form-gather-unify · waves={len(plan['waves'])} "
            f"fresh={plan['extraction']['fresh_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
