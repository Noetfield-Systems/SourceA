"""D15.2 — founder-facing packet readiness (gate % + missing sections)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

HUB_SCHEMA = "packet-readiness-hub-v1"
API_PATH = "/api/packet-readiness-v1"
PROBE_TEXT = "Sina Command hub packet readiness probe"

SECTION_LABELS: dict[str, str] = {
    "intent": "Intent — goal classified before execution",
    "code": "Code intelligence — AST, symbols, fusion",
    "dependencies": "Dependency graph — impact paths ready",
    "ranking": "Context ranking — evidence scored pre-LLM",
    "plan": "Planning engine — semantic step graph",
    "compression": "Compression — token budget assigned",
    "compressed_context": "Compressed narrative — D14 output",
    "constraints": "Constraints — policy + safety refs",
    "provenance": "Provenance — producer steps + artifacts",
}

MISSING_HINTS: dict[str, str] = {
    "intent": "Assemble with task text so D4 intent engine runs",
    "code": "Build D1 code intelligence index",
    "dependencies": "Build D3 dependency graph",
    "ranking": "Run D9 context ranking for this task",
    "plan": "Run D10 planning engine for this task",
    "compression": "Run D14 context compression",
    "compressed_context": "D14 must produce a narrative under budget",
    "constraints": "D15 assembly must attach governance policy refs",
    "provenance": "D15 assembly must record producer steps",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _readiness_from_packet(packet: dict, validation: dict) -> dict[str, Any]:
    from pre_llm.context_packet.schema import FIELD_PRODUCERS, GATE_REQUIRED_SECTIONS  # noqa: WPS433

    score = float(validation.get("readiness_score") or 0.0)
    missing = list(validation.get("missing_for_gate") or [])
    populated = list(validation.get("populated_sections") or [])
    rows: list[dict[str, str]] = []
    for section in GATE_REQUIRED_SECTIONS:
        ok = section in populated
        rows.append(
            {
                "id": section,
                "label": SECTION_LABELS.get(section, section),
                "status": "done" if ok else "missing",
                "producer": ", ".join(FIELD_PRODUCERS.get(section, [])),
                "hint": "" if ok else MISSING_HINTS.get(section, "Section empty or not hydrated"),
            }
        )
    missing_plain = [SECTION_LABELS.get(s, s) for s in missing]
    eligible = bool(validation.get("gate_eligible"))
    if eligible:
        try:
            import model_dispatch as _md  # noqa: WPS433

            enforce_live = _md.current_gate_mode() == "enforce"
        except Exception:
            enforce_live = False
        if enforce_live:
            summary = "Think-before-model: packet passes structural gate — ENFORCE is live on planner dispatch."
        else:
            summary = "Think-before-model: packet passes structural gate — safe for ENFORCE when you flip mode."
    elif missing_plain:
        summary = f"Packet not gate-eligible — {len(missing_plain)} section(s) still missing."
    else:
        summary = "Packet not gate-eligible — run D15 assembly with task text."
    return {
        "readiness_score": score,
        "readiness_pct": int(round(score * 100)),
        "gate_eligible": eligible,
        "missing_sections": missing,
        "missing_plain": missing_plain,
        "populated_sections": populated,
        "section_rows": rows,
        "summary": summary,
        "task_id": packet.get("task_id") or "",
        "packet_generated_at": packet.get("generated_at") or "",
    }


def packet_readiness_hub_payload(
    *,
    task_id: str = "hub-readiness",
    repo_root: str = "",
    query_text: str = "",
) -> dict[str, Any]:
    """Hub SSOT for D15.2 — uses canonical packet on disk or fresh D15 assembly."""
    import model_dispatch  # noqa: WPS433
    from pre_llm.context_assembly.store import load_canonical  # noqa: WPS433
    from pre_llm.context_packet.schema import validate_packet  # noqa: WPS433

    text = (query_text or PROBE_TEXT).strip()
    packet = load_canonical()
    validation: dict[str, Any]
    source = "disk_ssot"

    if packet:
        validation = validate_packet(packet)
    else:
        prep = model_dispatch.prepare_packet(task_id=task_id, repo_root=repo_root, query_text=text)
        packet = prep.get("packet") or {}
        validation = prep.get("validation") or validate_packet(packet)
        source = "fresh_assembly"

    body = _readiness_from_packet(packet, validation)
    return {
        "ok": True,
        "schema": HUB_SCHEMA,
        "api": API_PATH,
        "producer": "D15.2",
        "generated_at": _now(),
        "source": source,
        "gate_mode": model_dispatch.current_gate_mode(),
        "probe_text": text,
        "shipped_producers": validation.get("shipped_producers") or [],
        **body,
    }
