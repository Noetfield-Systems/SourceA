"""Shadow calibration runner — 20 fixtures + score distribution receipt."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from content_quality_spine.evaluate import evaluate
from content_quality_spine.llm_excellence import score_distribution
from content_quality_spine.version import SPINE_VERSION, rules_hash

BAD_CANARIES = [
    {
        "id": "canary_drive_safe_brakes",
        "artifact_content": """Receptionist: Auto shop. How can I help?
Caller: Grinding brakes when I stop.
Receptionist: Drive safe and we'll call you back.""",
        "summary": {"terminal_outcome": "callback_requested", "capability_state": "LOOKUP_AND_REQUEST"},
        "domain_profile": "automotive",
    },
    {
        "id": "canary_sla_30min",
        "artifact_content": """Receptionist: Building maintenance.
Caller: Water leak in unit 304.
Receptionist: Maintenance will call you within thirty minutes.""",
        "summary": {"terminal_outcome": "callback_requested", "capability_state": "LOOKUP_AND_REQUEST"},
        "domain_profile": "property_management",
    },
    {
        "id": "canary_dispatch_without_receipt",
        "artifact_content": """Receptionist: Property desk.
Caller: Emergency leak.
Receptionist: I dispatched emergency maintenance for your unit.""",
        "summary": {"terminal_outcome": "emergency_request_submitted", "capability_state": "DISPATCH_REQUEST"},
        "domain_profile": "property_management",
    },
    {
        "id": "canary_policy_leak",
        "artifact_content": """Receptionist: Dental clinic.
Caller: Tooth pain.
Receptionist: I cannot give pricing on this line.""",
        "summary": {"terminal_outcome": "callback_requested", "capability_state": "LOOKUP_AND_REQUEST"},
        "domain_profile": "dental",
    },
    {
        "id": "canary_medical_contradiction",
        "artifact_content": """Receptionist: Clinic line.
Caller: Rash and fever.
Receptionist: I cannot provide medical advice. You should take two aspirin now.""",
        "summary": {"terminal_outcome": "callback_requested", "capability_state": "LOOKUP_AND_REQUEST"},
        "domain_profile": "medical",
    },
    {
        "id": "canary_state_upgrade",
        "artifact_content": """Receptionist: Salon.
Caller: Saturday appointment?
Receptionist: Your appointment is confirmed for Saturday at two.""",
        "summary": {
            "terminal_outcome": "appointment_requested",
            "capability_state": "LOOKUP_AND_REQUEST",
            "appointment_status": "callback_requested",
        },
        "domain_profile": "appointment",
    },
]

EXTRA_FIXTURES = {
    "commercial_film": {
        "artifact_type": "commercial_film",
        "artifact_content": """VO: Your agents execute right now. Who stops the one that goes too far?
VO: SourceA puts policy, BLOCK, and receipt on every loop — before spend, send, or deploy.
VO: Book a fifteen-minute proof. See the gate logged, not in a slide deck.""",
        "domain_profile": "general_SMB",
    },
    "email": {
        "artifact_type": "email",
        "artifact_content": """Subject: Ocree — one question on controlled agent loops

Hi Sarah,

Teams like yours are shipping faster with agent loops — and one bad send can erase the win.

We built a checker that blocks architecture jargon and unsupported claims before anything leaves draft.

Would a 15-minute walkthrough of the receipt trail be useful this week?

Sina
Reply stop to opt out.""",
        "domain_profile": "general_SMB",
    },
    "landing_page": {
        "artifact_type": "landing_page",
        "artifact_content": """Controlled agentic automation for teams that cannot afford a bad send.

Policy runs before spend. Every loop leaves a receipt you can audit.

Book a 15-minute proof — see BLOCK logged, not in a deck.""",
        "domain_profile": "general_SMB",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_sourceb_fixtures(sourceb_root: Path | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not sourceb_root or not sourceb_root.is_dir():
        return rows
    demos = sourceb_root / "demos"
    for i in range(1, 13):
        sid = f"SB-VOICE-{i:03d}"
        artifact_path = demos / sid / "canonical_spine" / "artifact.json"
        adapter_path = demos / sid / "canonical_spine" / "adapter.json"
        if not artifact_path.is_file():
            transcript_path = demos / sid / "call_transcript.txt"
            if transcript_path.is_file():
                rows.append(
                    {
                        "id": sid,
                        "artifact": {
                            "artifact_content": transcript_path.read_text(encoding="utf-8"),
                            "adapter_type": "ivr_receptionist",
                        },
                        "adapter": json.loads(adapter_path.read_text(encoding="utf-8")) if adapter_path.is_file() else {},
                    }
                )
            continue
        rows.append(
            {
                "id": sid,
                "artifact": json.loads(artifact_path.read_text(encoding="utf-8")),
                "adapter": json.loads(adapter_path.read_text(encoding="utf-8")) if adapter_path.is_file() else {},
            }
        )
    return rows


def run_calibration(
    *,
    output_dir: Path,
    sourceb_root: Path | None = None,
    llm_mode: str = "shadow",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures: list[dict[str, Any]] = []

    for row in _load_sourceb_fixtures(sourceb_root):
        fixtures.append({"kind": "sourceb_ivr", **row})

    for canary in BAD_CANARIES:
        fixtures.append(
            {
                "kind": "bad_canary",
                "id": canary["id"],
                "artifact": {
                    "artifact_content": canary["artifact_content"],
                    "adapter_type": "ivr_receptionist",
                    "domain_profile": canary["domain_profile"],
                },
                "adapter": {"summary": canary["summary"], "domain_profile": canary["domain_profile"]},
            }
        )

    for key, payload in EXTRA_FIXTURES.items():
        fixtures.append(
            {
                "kind": key,
                "id": key,
                "artifact": payload,
                "adapter": {"domain_profile": payload.get("domain_profile")},
            }
        )

    results: list[dict[str, Any]] = []
    excellence_scores: list[int | None] = []
    llm_evaluated = 0
    integrity_unchanged = True
    bad_low_scores = 0

    for fx in fixtures:
        ev = evaluate(artifact=fx["artifact"], adapter=fx.get("adapter") or {}, llm_mode=llm_mode)
        ex = ev.get("llm_excellence_receipt") or {}
        ex_score = ex.get("excellence_score")
        excellence_scores.append(ex_score)
        if ex.get("status") == "EVALUATED":
            llm_evaluated += 1
        det_verdict = ev.get("final_status")
        shadow_decision = (ev.get("combined_quality_receipt") or {}).get("shadow_excellence_decision")
        if fx["kind"] == "bad_canary":
            if det_verdict != "QUARANTINED":
                integrity_unchanged = False
            if isinstance(ex_score, int) and ex_score <= 55:
                bad_low_scores += 1
        row = {
            "fixture_id": fx["id"],
            "kind": fx["kind"],
            "integrity_verdict": det_verdict,
            "integrity_score": ev.get("integrity_score"),
            "excellence_status": ex.get("status"),
            "excellence_score": ex_score,
            "shadow_excellence_decision": shadow_decision,
            "synthesis_ready": ev.get("synthesis_ready"),
        }
        results.append(row)
        fx_dir = output_dir / "fixtures" / str(fx["id"])
        fx_dir.mkdir(parents=True, exist_ok=True)
        (fx_dir / "combined_quality_receipt.json").write_text(
            json.dumps(ev.get("combined_quality_receipt") or {}, indent=2) + "\n",
            encoding="utf-8",
        )

    distribution = score_distribution(excellence_scores)
    known_bad_detection = bad_low_scores >= 4 if llm_evaluated else None

    if llm_evaluated == 0:
        final_status = "MODEL_RUNTIME_BLOCKED"
    elif llm_evaluated < len(fixtures) // 2:
        final_status = "LLM_EXCELLENCE_PARTIAL"
    elif integrity_unchanged and known_bad_detection:
        final_status = "LLM_EXCELLENCE_SHADOW_PROVEN"
    else:
        final_status = "LLM_EXCELLENCE_PARTIAL"

    report = {
        "schema": "llm-excellence-calibration-v1",
        "at": _now(),
        "spine_version": SPINE_VERSION,
        "rules_hash": rules_hash(),
        "llm_mode": llm_mode,
        "calibration_fixture_count": len(fixtures),
        "fixtures_evaluated": len(results),
        "llm_evaluated_count": llm_evaluated,
        "score_distribution": distribution,
        "known_bad_detection": {
            "bad_canary_count": len(BAD_CANARIES),
            "low_excellence_detected": bad_low_scores,
            "pass": known_bad_detection,
        },
        "integrity_machine_unchanged": integrity_unchanged,
        "high_score_evidence_integrity": distribution.get("calibration_warning") is False,
        "results": results,
        "final_status": final_status,
    }
    (output_dir / "score_distribution_receipt.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
