"""Governance constraints for assembled packet — gate section filler."""
from __future__ import annotations

from typing import Any

POLICY_REFS: list[str] = [
    "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md",
    "LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md",
    "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md",
]


def build_constraints(*, d11: dict[str, Any] | None = None, d12: dict[str, Any] | None = None) -> dict[str, Any]:
    safety: list[dict[str, str]] = [
        {"id": "pre_llm_gate", "rule": "No hub model call unless validate_packet gate_eligible"},
        {"id": "compress_before_assemble", "rule": "D14 compression must precede D15 assembly"},
        {"id": "no_execute_pre_enforce", "rule": "Tool execute blocked until gate ENFORCE receipt"},
    ]
    if d12 and d12.get("validation_ready"):
        safety.append(
            {
                "id": "d12_validation",
                "rule": "D12 dry-run validation pass required",
                "status": "pass",
            }
        )
    if d11 and d11.get("router_ready"):
        blocked = [
            s for s in (d11.get("selection") or [])
            if s.get("permission") == "execute" and not s.get("allowed")
        ]
        if blocked:
            safety.append(
                {
                    "id": "d11_policy",
                    "rule": f"execute tools gated ({len(blocked)} blocked selections)",
                    "status": "advisory",
                }
            )
    return {
        "policy_refs": POLICY_REFS,
        "safety": safety,
        "producer": "governance",
    }
