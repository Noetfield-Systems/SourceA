#!/usr/bin/env python3
"""H2 maintainer slice — ENFORCE/shadow gate display cross-check (sa-0823)."""
from __future__ import annotations

from typing import Any

SLICE_SCHEMA = "h2-maintainer-enforce-slice-v1"
PROBE_TASK = "h2-maintainer-enforce-slice"


def maintainer_enforce_slice_payload(*, query_text: str = "") -> dict[str, Any]:
    """Build H2-only maintainer ENFORCE/shadow display — cross-checks packet readiness SSOT."""
    import model_dispatch  # noqa: WPS433
    from pre_llm.packet_readiness.hub_surface import (  # noqa: WPS433
        PROBE_TEXT,
        packet_readiness_hub_payload,
    )

    mode = model_dispatch.current_gate_mode()
    text = (query_text or PROBE_TEXT).strip()
    pr = packet_readiness_hub_payload(task_id=PROBE_TASK, query_text=text)
    pr_mode = str(pr.get("gate_mode") or mode)
    pct = int(pr.get("readiness_pct") or 0)
    eligible = bool(pr.get("gate_eligible"))

    if mode == "enforce":
        display_line = (
            f"ENFORCE live on planner · packet {pct}% · "
            f"eligible={'yes' if eligible else 'no'}"
        )
        shadow_note = "Blocks planner dispatch when gate_eligible is false"
    elif mode == "shadow":
        display_line = (
            f"SHADOW active — log-only gate · packet {pct}% · "
            f"eligible={'yes' if eligible else 'no'}"
        )
        shadow_note = "Model runs; decisions logged to gate_shadow_v1.jsonl"
    else:
        display_line = f"Gate OFF · packet {pct}% · eligible={'yes' if eligible else 'no'}"
        shadow_note = "No planner gate logging"

    return {
        "ok": True,
        "schema": SLICE_SCHEMA,
        "hub": "H2",
        "slice": "maintainer_ship",
        "gate_mode": mode,
        "packet_gate_mode": pr_mode,
        "gate_is_enforce": mode == "enforce",
        "gate_is_shadow": mode == "shadow",
        "display_line": display_line,
        "shadow_note": shadow_note,
        "packet_readiness_pct": pct,
        "packet_gate_eligible": eligible,
        "packet_summary": str(pr.get("summary") or ""),
        "pref_path": str(model_dispatch.GATE_MODE_PREF_PATH),
        "cross_check_ok": mode == pr_mode,
        "h1_forbidden": "Legacy monolith packet panel — H2 maintainer slice only",
        "law": "archive/attachments/2026-06-15/sa-0823-h2-enforce-shadow-maintainer-slice_LOCKED_v1.md",
    }
