#!/usr/bin/env python3
"""Fail hub build when locked source SSOT and founder UI drift apart."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
APP_JS = SOURCE_A / "agent-control-panel" / "assets" / "app.js"
COMMAND_DATA = SOURCE_A / "agent-control-panel" / "command-data.json"
sys.path.insert(0, str(SOURCE_A / "scripts"))

from hub_worker_mode_v1 import worker_hub_mode  # noqa: E402
from important_docs_index import _RAW_SECTIONS  # noqa: E402
from roadmaps_goals import roadmaps_goals_payload  # noqa: E402
from system_roadmap import (  # noqa: E402
    CURRENT_RUNTIME_STEP,
    CURRENT_STRATEGIC_STEP,
    RUNTIME_STACK_COMPLETE,
    _gate_is_enforce,
    _phase_d_complete,
    _pre_llm_shipped_count,
    HUB_UI_PROCEDURE_DOC,
    LAW_DOC,
    MAP_DOC,
    PAYLOAD_VERSION,
    STEP_CATALOG,
    STRATEGIC_BUILD_PHASES,
    _artifact_exists,
    _phase_d_step_ids,
    _phases_def,
    _strategic_build_step_count,
    system_roadmap_payload,
)

# Root locked docs that must reference the current MAP_DOC (not superseded paths).
MAP_POINTER_DOCS = [
    LAW_DOC,
    "SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md",
    "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md",
    "SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md",
    "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
    "brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md",
    "brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md",
    "AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md",
    "brain-os/law/GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md",
    "AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md",
]

APP_FORBIDDEN = [
    (r"build order — 12 steps", "hardcoded step count in app.js"),
    (r"Next build order — 12 steps", "hardcoded step count in app.js"),
    (r"WORLD_TARGET_MODEL_MAP_LOCKED_v2\.md", "stale map path in app.js"),
]

APP_REQUIRED = [
    "srStrategicStepCount",
    "ensureSystemRoadmap",
    "ui_contract",
    "renderSrDoNowBtn",
    "renderPacketReadinessPanel",
    "renderDecisionGovernance",
    "decision-governance",
    "metaReasoningPolicy",
    "sc-btn-now-live",
    "sc-packet-ready",
]


def _map_doc_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Version:\*\*\s*([\d.]+)", text)
    return m.group(1) if m else None


def _map_doc_step_ids(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return re.findall(
        r"\|\s*[\d.]+[b]?\s*\|\s*\*{0,2}([A][\d.]+[b]?)\*{0,2}\s*\|",
        text,
    )


def _important_docs_map_path() -> str | None:
    for _sec_id, _title, _aud, rows in _RAW_SECTIONS:
        for row in rows:
            if "World Target Model map" in row[1]:
                return row[0]
    return None


def _check_phase_s0_ssot_alignment_regression(errors: list[str]) -> None:
    """sa-0003..sa-0010 — inline validate-phase-s0-ssot-alignment-v1 (no subprocess)."""
    try:
        from strategic_synthesis_hub import (  # noqa: WPS433
            pendings,
            strategic_goals,
            strategic_synthesis_payload,
            this_week,
        )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"phase-s0 strategic_synthesis import: {exc}")
        return

    tw = this_week()
    if not any("spine" in (x.get("action") or "").lower() for x in tw):
        errors.append(f"this_week missing spine Action (sa-0078): {tw!r}")
    if not any("fleet" in (x.get("action") or "").lower() for x in tw):
        errors.append(f"this_week missing fleet auto-pass (sa-0078): {tw!r}")
    if not any(
        "g3" in (x.get("action") or "").lower() or "wire" in (x.get("who") or "").lower()
        for x in tw
    ):
        errors.append(f"this_week missing Wire G3 (sa-0078): {tw!r}")

    gdc = next((g for g in strategic_goals() if g.get("id") == "goal-dispatch-closure"), {})
    try:
        from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready

        exp_ready, _, _ = orchestrator_dispatch_ready()
        exp_status = "done" if exp_ready else "in_progress"
    except Exception:
        exp_status = "in_progress"
    if gdc.get("status") != exp_status:
        errors.append(f"goal-dispatch-closure status != {exp_status}: {gdc!r}")
    elif "spine" not in (gdc.get("blocker") or "").lower():
        errors.append(f"goal-dispatch-closure missing spine blocker: {gdc!r}")

    p2 = next((x for x in pendings() if x.get("id") == "P2"), {})
    if p2.get("status") != "partial":
        errors.append(f"P2 L0-full pendings must be partial not open (sa-0055): {p2!r}")

    p = strategic_synthesis_payload()
    gates = p.get("machine_gates") or {}
    if gates.get("eval_1b_gate_ok") and "eval_1b_gate_ok=true" not in (p.get("one_line") or ""):
        errors.append(f"synthesis one_line stale eval: {p.get('one_line')!r}")

    for rel in MAP_POINTER_DOCS:
        doc = SOURCE_A / rel
        if not doc.is_file():
            errors.append(f"MAP_POINTER doc missing: {rel}")
        elif MAP_DOC.split("/")[-1] not in doc.read_text(encoding="utf-8"):
            errors.append(f"MAP_POINTER doc {rel} missing {MAP_DOC}")


def _check_essentials_nav_regression(errors: list[str]) -> None:
    """sa-0013 — NAV_TABS must match app.js NAV ids (audit_essentials_nav)."""
    import subprocess

    script = SOURCE_A / "scripts" / "audit_essentials_nav.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(SOURCE_A / "scripts"),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        snippet = (proc.stdout or proc.stderr or "").strip()[:240]
        errors.append(f"audit_essentials_nav failed (sa-0013): {snippet}")


def _check_phase_d_complete_artifacts_regression(errors: list[str]) -> None:
    """sa-0012 — _phase_d_complete() must match D1–D16 in-repo artifacts."""
    ship = _pre_llm_shipped_count()
    pdc = _phase_d_complete()
    if pdc != (ship == 16):
        errors.append(
            f"_phase_d_complete={pdc} drifts from pre_llm_shipped={ship}/16 (sa-0012)"
        )
    if pdc and ship != 16:
        errors.append(
            f"_phase_d_complete true but only {ship}/16 D artifacts locally (sa-0012)"
        )


def _check_honest_score_not_here_regression(errors: list[str], payload: dict) -> None:
    """sa-0001 / sa-0076 — mirror validate-honest-score-not-here-v1 + drift guard."""
    wtm = payload.get("world_target_map") or {}
    here = (wtm.get("honest_score") or {}).get("here") or []
    built = (wtm.get("reality_alignment") or {}).get("built") or []
    if not any("Execution Spine" in str(x) for x in here):
        errors.append(f"honest_score.here must include Execution Spine: {here!r}")
    if "Execution Spine" not in built:
        errors.append(f"reality_alignment.built must include Execution Spine: {built!r}")
    not_here = (wtm.get("honest_score") or {}).get("not_here") or []
    report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
    if report_path.is_file():
        try:
            rep1b = json.loads(report_path.read_text(encoding="utf-8"))
            if rep1b.get("mode") == "live" and rep1b.get("live_ok", rep1b.get("ok")):
                for stale in (
                    "Eval-1b behavioral proof",
                    "Eval-1b live LLM A/B",
                    "Eval-1b below threshold",
                ):
                    if any(stale in str(line) for line in not_here):
                        errors.append(f"honest_score.not_here stale after live pass: {stale!r}")
        except json.JSONDecodeError:
            pass
    embed_path = SOURCE_A / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
    index_path = Path.home() / ".sina" / "vector_index_v1.json"
    if embed_path.is_file() and index_path.is_file() and any(
        "full L8 embeddings later" in str(line) for line in not_here
    ):
        errors.append(
            "honest_score.not_here stale (sa-0077): L8 hybrid shipped but still lists full embeddings later"
        )

    # sa-0011 — ENFORCE-only not_here must drop when ~/.sina/gate_mode_v1.txt is enforce
    import importlib
    import os

    import model_dispatch
    import system_roadmap

    _prev = os.environ.get("SINA_GATE_MODE")
    os.environ["SINA_GATE_MODE"] = "enforce"
    importlib.reload(model_dispatch)
    importlib.reload(system_roadmap)
    try:
        if not system_roadmap._gate_is_enforce():
            errors.append("honest_score enforce regression: SINA_GATE_MODE=enforce did not resolve")
        else:
            m_enf = system_roadmap._build_world_target_map()
            nh_enf = (m_enf.get("honest_score") or {}).get("not_here") or []
            tgt_enf = (m_enf.get("reality_alignment") or {}).get("target") or []
            for stale in (
                "ENFORCE gate in production (shadow today)",
                "ENFORCE gate flip",
            ):
                if any(stale in str(line) for line in nh_enf):
                    errors.append(
                        f"honest_score.not_here ENFORCE-only stale under enforce gate: {stale!r}"
                    )
                if any(stale in str(line) for line in tgt_enf):
                    errors.append(
                        f"reality_alignment.target ENFORCE-only stale under enforce gate: {stale!r}"
                    )
    finally:
        if _prev is None:
            os.environ.pop("SINA_GATE_MODE", None)
        else:
            os.environ["SINA_GATE_MODE"] = _prev
        importlib.reload(model_dispatch)
        importlib.reload(system_roadmap)


def _check_llm_context_packet_law_vs_builder_regression(errors: list[str]) -> None:
    """sa-0652 — mirror validate-llm-context-packet-law-vs-builder-v1."""
    law_path = SOURCE_A / "brain-os/law/LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md"
    try:
        from pre_llm.context_packet.schema import (  # noqa: WPS433
            FIELD_PRODUCERS,
            GATE_REQUIRED_SECTIONS,
            LAW_DOC,
            PACKET_VERSION,
            SCHEMA,
            empty_packet_template,
            schema_contract_payload,
        )
        from system_roadmap import LLM_PACKET_SCHEMA, _build_llm_packet_schema  # noqa: WPS433

        law_gate = (
            "intent",
            "code",
            "dependencies",
            "ranking",
            "plan",
            "compression",
            "compressed_context",
            "constraints",
            "provenance",
        )
        law_envelope = (
            "intent",
            "workspace",
            "code",
            "dependencies",
            "retrieval",
            "reasoning",
            "ranking",
            "plan",
            "tools",
            "validation",
            "diff",
            "compression",
            "memory",
            "constraints",
            "compressed_context",
            "provenance",
        )
        law_producers = {
            "intent": ["D4"],
            "workspace": ["L1", "hub"],
            "code": ["D1", "D2"],
            "dependencies": ["D3"],
            "retrieval": ["D5", "D6", "D7"],
            "reasoning": ["D8"],
            "ranking": ["D9"],
            "plan": ["D10"],
            "tools": ["D11"],
            "validation": ["D12"],
            "diff": ["D13"],
            "compression": ["D14"],
            "memory": ["D6", "D16"],
            "constraints": ["governance"],
            "compressed_context": ["D14"],
            "provenance": ["D15"],
        }

        if not law_path.is_file():
            errors.append(f"LLM_CONTEXT_PACKET_SCHEMA law missing: {law_path} (sa-0652)")
        else:
            law_text = law_path.read_text(encoding="utf-8")
            if LAW_DOC not in law_text:
                errors.append(f"law doc must cite {LAW_DOC} (sa-0652)")
            if "scripts/pre_llm/context_packet/schema.py" not in law_text:
                errors.append("law doc must cite schema.py module (sa-0652)")

        stub = empty_packet_template()
        for section in law_envelope:
            if section not in stub:
                errors.append(f"packet template missing law envelope section {section!r} (sa-0652)")

        if tuple(GATE_REQUIRED_SECTIONS) != law_gate:
            errors.append(
                f"GATE_REQUIRED_SECTIONS drift vs law: {GATE_REQUIRED_SECTIONS} (sa-0652)"
            )

        for section, expected in law_producers.items():
            got = FIELD_PRODUCERS.get(section)
            if got != expected:
                errors.append(
                    f"FIELD_PRODUCERS[{section!r}]={got} law expects {expected} (sa-0652)"
                )

        api = schema_contract_payload()
        if api.get("ok") is not True:
            errors.append(f"schema_contract_payload not ok: {api} (sa-0652)")
        elif api.get("schema") != SCHEMA:
            errors.append(f"schema_contract schema drift: {api.get('schema')} (sa-0652)")
        elif api.get("packet_version") != PACKET_VERSION:
            errors.append(f"packet_version drift: {api.get('packet_version')} (sa-0652)")
        elif api.get("law_doc") != LAW_DOC:
            errors.append(f"schema_contract law_doc drift: {api.get('law_doc')} (sa-0652)")
        elif api.get("field_producers") != FIELD_PRODUCERS:
            errors.append("schema_contract field_producers drift vs builder (sa-0652)")

        if LLM_PACKET_SCHEMA.get("law_doc") != LAW_DOC:
            errors.append(
                f"LLM_PACKET_SCHEMA law_doc drift: {LLM_PACKET_SCHEMA.get('law_doc')} (sa-0652)"
            )
        live = _build_llm_packet_schema()
        if live.get("law_doc") != LAW_DOC:
            errors.append(f"live llm_packet_schema law_doc drift: {live.get('law_doc')} (sa-0652)")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"llm context packet law vs builder check failed: {exc} (sa-0652)")


def _check_user_signals_record_hub_touch_on_build_regression(errors: list[str]) -> None:
    """sa-0653 — mirror validate-user-signals-record-hub-touch-on-build-v1."""
    build_path = SOURCE_A / "scripts" / "build-sina-command-panel.py"
    store_path = SOURCE_A / "scripts" / "pre_llm" / "user_signals" / "store.py"
    refresh_path = SOURCE_A / "scripts" / "hub_self_refresh_v1.py"
    try:
        if not build_path.is_file():
            errors.append(f"build-sina-command-panel.py missing (sa-0653)")
        else:
            build_text = build_path.read_text(encoding="utf-8")
            if "record_hub_touch" not in build_text:
                errors.append("build-sina-command-panel.py must call record_hub_touch (sa-0653)")
            elif 'source="hub_build"' not in build_text:
                errors.append("build-sina-command-panel.py record_hub_touch must use hub_build (sa-0653)")

        if not store_path.is_file():
            errors.append(f"user_signals store.py missing (sa-0653)")
        else:
            store_text = store_path.read_text(encoding="utf-8")
            if "hub_build" not in store_text or "_HUB_REFRESH_SOURCES" not in store_text:
                errors.append("user_signals store must list hub_build refresh source (sa-0653)")

        if not refresh_path.is_file():
            errors.append(f"hub_self_refresh_v1.py missing (sa-0653)")
        else:
            refresh_text = refresh_path.read_text(encoding="utf-8")
            if "record_hub_touch" not in refresh_text or "hub_self_refresh" not in refresh_text:
                errors.append("hub_self_refresh must call record_hub_touch with hub_self_refresh (sa-0653)")

        from pre_llm.user_signals.store import record_hub_touch  # noqa: WPS433

        out = record_hub_touch(hub_tab="audit", active_repo="SourceA", source="hub_build")
        sig = out.get("signals") or {}
        if not sig.get("last_refresh_at"):
            errors.append("record_hub_touch hub_build must set last_refresh_at (sa-0653)")
        signals = sig.get("signals") or []
        if not signals or signals[-1].get("source") != "hub_build":
            errors.append(f"record_hub_touch hub_build signal row missing (sa-0653): {signals[-1:] if signals else []}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"user_signals record_hub_touch on build check failed: {exc} (sa-0653)")


def _check_user_signals_v1_artifact_regression(errors: list[str]) -> None:
    """sa-0654 — mirror validate-user-signals-v1-artifact-v1."""
    try:
        from pre_llm.user_signals.store import SCHEMA, SIGNALS_PATH, hub_payload, load_signals  # noqa: WPS433
        from system_roadmap import _artifact_exists, system_roadmap_payload  # noqa: WPS433

        if not SIGNALS_PATH.is_file():
            errors.append(f"L0 artifact missing: {SIGNALS_PATH} (sa-0654)")
            return

        if not _artifact_exists("user_signals_v1.json"):
            errors.append("system_roadmap _artifact_exists user_signals_v1.json false (sa-0654)")

        sig = load_signals()
        if sig.get("schema") != SCHEMA:
            errors.append(f"user_signals schema drift: {sig.get('schema')} (sa-0654)")
        if not (sig.get("signals") or []):
            errors.append("user_signals_v1.json has no hub touch rows (sa-0654)")
        if not (sig.get("last_refresh_at") or sig.get("last_hub_tab")):
            errors.append("user_signals_v1.json missing last_refresh_at/last_hub_tab (sa-0654)")

        api = hub_payload()
        if api.get("ok") is not True:
            errors.append(f"user_signals hub_payload not ok: {api} (sa-0654)")
        elif api.get("l0_status") != "done":
            errors.append(f"user_signals l0_status={api.get('l0_status')} expected done (sa-0654)")
        elif int(api.get("signal_count") or 0) <= 0:
            errors.append(f"user_signals signal_count={api.get('signal_count')} (sa-0654)")

        sr = system_roadmap_payload()
        lc = {
            r["layer"]: r
            for r in (sr.get("world_target_map") or {}).get("layer_comparison") or []
        }
        if lc.get("L0", {}).get("your_status") != "done":
            errors.append(f"WTM L0 your_status={lc.get('L0', {}).get('your_status')} (sa-0654)")
        uws = sr.get("user_workspace_signals") or {}
        if uws.get("ok") is not True:
            errors.append(f"system_roadmap user_workspace_signals not ok (sa-0654)")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"user_signals_v1 artifact check failed: {exc} (sa-0654)")


def _check_l1_workspace_state_hub_post_regression(errors: list[str]) -> None:
    """sa-0655 — mirror validate-l1-workspace-state-hub-post-v1."""
    api_path = SOURCE_A / "scripts" / "pre_llm" / "user_signals" / "api.py"
    server_path = SOURCE_A / "scripts" / "sina-command-server.py"
    try:
        if not api_path.is_file():
            errors.append(f"user_signals api.py missing (sa-0655)")
        else:
            api_text = api_path.read_text(encoding="utf-8")
            if "user_workspace_signals_v1_payload" not in api_text:
                errors.append("api.py must define user_workspace_signals_v1_payload (sa-0655)")
            if '== "touch"' not in api_text:
                errors.append("api.py must handle action touch (sa-0655)")
            if '== "workspace"' not in api_text:
                errors.append("api.py must handle action workspace (sa-0655)")

        if not server_path.is_file():
            errors.append(f"sina-command-server.py missing (sa-0655)")
        else:
            srv = server_path.read_text(encoding="utf-8")
            if "/api/user-workspace-signals-v1" not in srv:
                errors.append("hub must expose /api/user-workspace-signals-v1 (sa-0655)")

        from pre_llm.user_signals.store import SCHEMA, WORKSPACE_PATH, load_workspace_state  # noqa: WPS433
        from pre_llm.user_signals.api import user_workspace_signals_v1_payload  # noqa: WPS433
        from system_roadmap import system_roadmap_payload  # noqa: WPS433

        out = user_workspace_signals_v1_payload(
            {
                "action": "touch",
                "hub_tab": "audit-l1",
                "active_repo": "SourceA",
                "source": "audit",
            }
        )
        if out.get("ok") is not True:
            errors.append(f"L1 touch payload not ok: {out} (sa-0655)")
        elif out.get("l1_status") not in ("done", "partial"):
            errors.append(f"L1 l1_status={out.get('l1_status')} after touch (sa-0655)")
        ws = out.get("workspace_state") or {}
        if not ws.get("hub_tab"):
            errors.append(f"workspace_state missing hub_tab after touch (sa-0655): {ws}")

        if not WORKSPACE_PATH.is_file():
            errors.append(f"workspace_state_v1.json missing: {WORKSPACE_PATH} (sa-0655)")
        else:
            disk = load_workspace_state()
            if disk.get("schema") != SCHEMA:
                errors.append(f"workspace_state schema drift: {disk.get('schema')} (sa-0655)")

        sr = system_roadmap_payload()
        lc = {
            r["layer"]: r
            for r in (sr.get("world_target_map") or {}).get("layer_comparison") or []
        }
        if lc.get("L1", {}).get("your_status") != "done":
            errors.append(f"WTM L1 your_status={lc.get('L1', {}).get('your_status')} (sa-0655)")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"L1 workspace hub POST check failed: {exc} (sa-0655)")


def _check_system_roadmap_phase_d_regression(
    payload: dict,
    phase_d_ids: list[str],
    errors: list[str],
) -> None:
    """sa-0651 — mirror validate-system-roadmap-phase-d-v1 when D16 shipped."""
    if not _phase_d_complete():
        return
    ph_d = next((p for p in payload.get("phases") or [] if p.get("id") == "D"), {})
    ui = (payload.get("ui_contract") or {}).get("phase_d") or {}
    fp = (payload.get("live") or {}).get("future_phase") or {}
    if ph_d.get("status") != "done":
        errors.append(
            f"system_roadmap phases[D].status={ph_d.get('status')!r} expected done (sa-0651)"
        )
    if ui.get("step_count") != 16:
        errors.append(
            f"system_roadmap ui_contract.phase_d.step_count="
            f"{ui.get('step_count')} expected 16 (sa-0651)"
        )
    if fp.get("status") != "done":
        errors.append(
            f"system_roadmap live.future_phase.status={fp.get('status')!r} expected done (sa-0651)"
        )
    if len(phase_d_ids) != 16:
        errors.append(
            f"system_roadmap phase D step ids count={len(phase_d_ids)} expected 16 (sa-0651)"
        )


def main() -> int:
    errors: list[str] = []
    payload = system_roadmap_payload()
    phases = _phases_def()
    phase_d_ids = _phase_d_step_ids(phases)
    strategic_ids = [
        s["roadmap_id"]
        for ph in STRATEGIC_BUILD_PHASES
        for s in ph.get("steps") or []
        if s.get("roadmap_id")
    ]

    if payload.get("version") != PAYLOAD_VERSION:
        errors.append(f"payload version mismatch: {payload.get('version')} != {PAYLOAD_VERSION}")

    map_path = SOURCE_A / MAP_DOC
    if not map_path.is_file():
        errors.append(f"missing canonical map at root: {MAP_DOC}")
    else:
        doc_ver = _map_doc_version(map_path)
        if doc_ver and doc_ver != PAYLOAD_VERSION:
            errors.append(f"MAP doc version {doc_ver} vs payload {PAYLOAD_VERSION}")
        map_table_ids = _map_doc_step_ids(map_path)
        if map_table_ids and map_table_ids != phase_d_ids:
            errors.append(
                f"MAP step table drift: doc={map_table_ids} payload={phase_d_ids}"
            )

    for ph in phases:
        ids: list[str] = []
        if ph.get("steps"):
            ids = [s["id"] for s in ph["steps"]]
        else:
            for sp in ph.get("subphases") or []:
                ids.extend(s["id"] for s in sp.get("steps") or [])
        for sid in ids:
            if not sid.upper().startswith(ph["id"]):
                errors.append(f"step {sid} in phase {ph['id']} breaks prefix law")

    for sid in phase_d_ids:
        if sid not in STEP_CATALOG:
            errors.append(f"phase D step {sid} missing from STEP_CATALOG")
    for sid in strategic_ids:
        if sid not in phase_d_ids:
            errors.append(f"strategic_build_phases id {sid} not in phase D")

    if _strategic_build_step_count() != len(phase_d_ids):
        errors.append(
            f"strategic step count {_strategic_build_step_count()} != phase D {len(phase_d_ids)}"
        )

    idx_map = _important_docs_map_path()
    if idx_map != MAP_DOC:
        errors.append(f"important_docs_index map {idx_map!r} != {MAP_DOC}")

    rg = roadmaps_goals_payload()
    wtm = rg.get("wtm_pointer") or {}
    if wtm.get("map_doc") != MAP_DOC:
        errors.append(f"roadmaps_goals map_doc {wtm.get('map_doc')!r} != {MAP_DOC}")

    proc = SOURCE_A / HUB_UI_PROCEDURE_DOC
    if not proc.is_file():
        errors.append(f"missing procedure doc: {HUB_UI_PROCEDURE_DOC}")

    for rel in MAP_POINTER_DOCS:
        p = SOURCE_A / rel
        if not p.is_file():
            errors.append(f"missing pointer doc: {rel}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if MAP_DOC not in text:
            errors.append(f"{rel} does not reference current {MAP_DOC}")

    for retired in ("WORLD_TARGET_MODEL_MAP_LOCKED_v1.md", "WORLD_TARGET_MODEL_MAP_LOCKED_v2.md"):
        if (SOURCE_A / retired).is_file():
            errors.append(f"superseded map still at root: {retired}")

    index_html = SOURCE_A / "agent-control-panel" / "index.html"
    if index_html.is_file():
        ih = index_html.read_text(encoding="utf-8", errors="replace")
        if "window.COMMAND_DATA = {" in ih:
            errors.append("index.html embeds full COMMAND_DATA — must use __COMMAND_DATA_LAZY (perf regression)")
        if index_html.stat().st_size > 50_000:
            errors.append(f"index.html too large ({index_html.stat().st_size} bytes) — lazy load broken")

    feedback_agg = SOURCE_A / "FEEDBACK_AGGREGATE.json"
    execution_truth = SOURCE_A / "EXECUTION_TRUTH.json"
    hub_built = str(payload.get("built_at") or "")
    if hub_built and feedback_agg.is_file():
        try:
            fa = json.loads(feedback_agg.read_text(encoding="utf-8"))
            if fa.get("hub_built_at") != hub_built:
                errors.append(
                    f"FEEDBACK_AGGREGATE hub_built_at drift vs hub payload (sa-0017): "
                    f"{fa.get('hub_built_at')!r} != {hub_built!r}"
                )
            et = fa.get("execution_truth") or {}
            if et.get("hub_built_at") != hub_built:
                errors.append("FEEDBACK_AGGREGATE.execution_truth hub_built_at drift (sa-0017)")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"FEEDBACK_AGGREGATE audit: {exc}")
    if hub_built and execution_truth.is_file():
        try:
            truth = json.loads(execution_truth.read_text(encoding="utf-8"))
            if truth.get("hub_built_at") != hub_built:
                errors.append(f"EXECUTION_TRUTH hub_built_at drift vs hub (sa-0017)")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"EXECUTION_TRUTH audit: {exc}")

    shell_json = SOURCE_A / "agent-control-panel" / "command-data-shell.json"
    if shell_json.is_file():
        try:
            from sina_command_lib import SHELL_MAX_BYTES  # noqa: WPS433

            shell_sz = shell_json.stat().st_size
            if shell_sz > SHELL_MAX_BYTES:
                errors.append(
                    f"command-data-shell.json {shell_sz} bytes > {SHELL_MAX_BYTES} — lazy shell cap (sa-0016)"
                )
            sh = json.loads(shell_json.read_text(encoding="utf-8"))
            if "fleet" in sh:
                errors.append("fleet leaked into command-data-shell.json (sa-0016)")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"command-data-shell.json audit: {exc}")

    if APP_JS.is_file():
        app_text = APP_JS.read_text(encoding="utf-8", errors="replace")
        for pattern, msg in APP_FORBIDDEN:
            if re.search(pattern, app_text, re.IGNORECASE):
                errors.append(f"app.js: {msg}")
        for needle in APP_REQUIRED:
            if needle not in app_text:
                errors.append(f"app.js missing required SSOT hook: {needle}")
    elif not worker_hub_mode():
        errors.append("missing app.js")

    ui = payload.get("ui_contract") or {}
    if ui.get("map_doc") != MAP_DOC:
        errors.append("ui_contract.map_doc drift")
    if ui.get("phase_d", {}).get("step_count") != len(phase_d_ids):
        errors.append("ui_contract.phase_d.step_count drift")
    _check_system_roadmap_phase_d_regression(payload, phase_d_ids, errors)
    _check_phase_d_complete_artifacts_regression(errors)
    _check_essentials_nav_regression(errors)
    _check_honest_score_not_here_regression(errors, payload)
    _check_phase_s0_ssot_alignment_regression(errors)
    _check_llm_context_packet_law_vs_builder_regression(errors)
    _check_user_signals_record_hub_touch_on_build_regression(errors)
    _check_user_signals_v1_artifact_regression(errors)
    _check_l1_workspace_state_hub_post_regression(errors)
    do_now = ui.get("do_now") or {}
    if RUNTIME_STACK_COMPLETE:
        primary_step = do_now.get("primary", {}).get("step")
        if _phase_d_complete():
            allowed = {"ENFORCE", "L0", "Eval-1", "L8", "STRATEGIC-SLICE"} if _gate_is_enforce() else {"ENFORCE"}
            if primary_step not in allowed:
                errors.append(
                    "ui_contract.do_now.primary must be ENFORCE or strategic slice "
                    "(L0/Eval-1/L8/STRATEGIC-SLICE when enforce live) when Phase D complete"
                )
        elif primary_step != CURRENT_STRATEGIC_STEP:
            errors.append("ui_contract.do_now.primary must be CURRENT_STRATEGIC_STEP when runtime stack complete")
        if do_now.get("parallel", {}).get("step") != CURRENT_RUNTIME_STEP:
            errors.append("ui_contract.do_now.parallel must be CURRENT_RUNTIME_STEP when runtime stack complete")
    else:
        if do_now.get("primary", {}).get("step") != CURRENT_RUNTIME_STEP:
            errors.append("ui_contract.do_now.primary must be CURRENT_RUNTIME_STEP (C track)")
        if do_now.get("parallel", {}).get("step") != CURRENT_STRATEGIC_STEP:
            errors.append("ui_contract.do_now.parallel must be CURRENT_STRATEGIC_STEP")

    live = payload.get("live") or {}
    phase_columns = live.get("phase_columns") or []
    if live.get("layout") != "abcd_four_column_v1":
        errors.append("live.layout must be abcd_four_column_v1 — one column per phase A B C D")
    if len(phase_columns) != 4:
        errors.append(f"live.phase_columns must have 4 phases, got {len(phase_columns)}")
    else:
        col_ids = [c.get("id") for c in phase_columns]
        if col_ids != ["A", "B", "C", "D"]:
            errors.append(f"live.phase_columns order must be A B C D, got {col_ids}")
        by_id = {c.get("id"): c for c in phase_columns}
        if len((by_id.get("A") or {}).get("steps") or []) != 4:
            errors.append("Phase A column must list 4 steps (A1–A4)")
        if len((by_id.get("B") or {}).get("steps") or []) != 6:
            errors.append("Phase B column must list 6 steps (B1–B6)")
        if len((by_id.get("C") or {}).get("steps") or []) != 7:
            errors.append("Phase C column must list 7 steps (C1–C7)")
        if len((by_id.get("D") or {}).get("steps") or []) != 16:
            errors.append("Phase D column must list all 16 steps in one column (no split D|D)")

    layer_by_id = {
        r.get("layer"): r
        for r in (payload.get("world_target_map") or {}).get("layer_comparison") or []
    }
    _layer_ssot_checks = [
        ("L3", "code_intelligence_v1.json", "Code Intelligence"),
        ("L14", "diff_intelligence_v1.json", "Diff Intelligence"),
        ("L15", "context_compression_v1.json", "Compression Engine"),
    ]
    for layer_id, ssot_name, label in _layer_ssot_checks:
        if not _artifact_exists(ssot_name):
            continue
        row = layer_by_id.get(layer_id) or {}
        status = str(row.get("your_status") or "").lower()
        if "missing" in status or status in ("", "not_built"):
            errors.append(
                f"layer_comparison {layer_id} stale: {ssot_name} exists but UI shows {row.get('your_status')!r}"
            )
    if _artifact_exists("llm_context_packet_v1.json"):
        row = layer_by_id.get("L16") or {}
        status = str(row.get("your_status") or "").lower()
        if status == "missing":
            errors.append("layer_comparison L16 stale: llm_context_packet_v1.json exists but status missing")
    embed_path = SOURCE_A / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
    if embed_path.is_file() and _artifact_exists("vector_index_v1.json"):
        row = layer_by_id.get("L8") or {}
        status = str(row.get("your_status") or "").lower()
        if status != "hybrid":
            errors.append(
                "layer_comparison L8 stale: embedding_provider + vector_index exist "
                f"but UI shows {row.get('your_status')!r} (expected hybrid)"
            )

    pr = payload.get("packet_readiness") or {}
    if not pr.get("ok"):
        errors.append("system_roadmap.packet_readiness missing or not ok — D15.2 hub surface")
    elif pr.get("readiness_pct") is None:
        errors.append("packet_readiness.readiness_pct missing")
    elif not (pr.get("section_rows") or []):
        errors.append("packet_readiness.section_rows empty")

    try:
        from meta_reasoning_policy import meta_reasoning_payload  # noqa: WPS433
        from runtime.dispatch_policy.policy_engine import (  # noqa: WPS433
            LAW_LAYER1_CLASSES,
            cross_check_law_policy_classes,
        )

        mr = meta_reasoning_payload()
        xc = mr.get("dispatch_policy_crosscheck") or {}
        if not xc.get("ok"):
            errors.append(f"meta_reasoning dispatch_policy_crosscheck not ok: {xc}")
        law_errors = cross_check_law_policy_classes()
        if law_errors:
            errors.append(f"dispatch Layer-1 law classes: {law_errors}")
        mr_classes = {x["class"] for x in mr.get("input_classes") or []}
        dp_classes = set(LAW_LAYER1_CLASSES)
        overlap = mr_classes & dp_classes
        if overlap:
            errors.append(
                f"meta_reasoning/dispatch namespace collision: {sorted(overlap)}"
            )
        if len(mr_classes) != 7:
            errors.append(f"meta_reasoning input_classes count != 7: {len(mr_classes)}")
        emap = mr.get("enforcement_map") or []
        if not any("dispatch" in (r.get("enforcement") or "").lower() for r in emap):
            errors.append("meta_reasoning enforcement_map missing dispatch_policy link")
        dp = payload.get("dispatch_policy") or {}
        align = (dp.get("alignment") or {}) if dp.get("ok") else {}
        if not dp.get("ok"):
            errors.append("system_roadmap.dispatch_policy missing or not ok")
        elif not (align.get("law_classes_ok") and align.get("mapping_ok")):
            errors.append(f"dispatch_policy alignment drift: {align}")
        auth = (payload.get("authorities") or {})
        if not (auth.get("meta_reasoning_stack") or []):
            errors.append("authorities.meta_reasoning_stack empty — decision governance hub drift")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"meta_reasoning dispatch crosscheck failed: {exc}")

    dispatch_doc = SOURCE_A / "brain-os" / "law" / "DISPATCH_POLICY_LOCKED_v1.md"
    try:
        import model_dispatch as md  # noqa: WPS433
        from runtime.dispatch_policy.policy_engine import dispatch_policy_payload  # noqa: WPS433

        if not dispatch_doc.is_file():
            errors.append("DISPATCH_POLICY_LOCKED_v1.md missing — SHADOW/ENFORCE doc drift")
        else:
            doc_text = dispatch_doc.read_text(encoding="utf-8")
            for needle in (
                "SHADOW",
                "ENFORCE",
                "gate_shadow_v1.jsonl",
                "gate_enforce_v1.jsonl",
                "gate_mode_v1.txt",
            ):
                if needle not in doc_text:
                    errors.append(f"dispatch policy doc missing gate-mode needle: {needle}")
        modes = md._VALID_GATE_MODES  # noqa: SLF001
        if modes != ("off", "shadow", "enforce"):
            errors.append(f"model_dispatch gate modes drift: {modes}")
        gate_status = md.gate_status_payload()
        if not gate_status.get("ok"):
            errors.append(f"model_dispatch gate_status not ok: {gate_status}")
        elif gate_status.get("current_mode") not in modes:
            errors.append(f"model_dispatch current_mode invalid: {gate_status.get('current_mode')}")
        dp_doc = dispatch_policy_payload()
        if dp_doc.get("ok") is False:
            errors.append(f"dispatch_policy_payload not ok: {dp_doc}")
        elif dp_doc.get("doc_path") != "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md":
            errors.append(f"dispatch_policy doc_path drift: {dp_doc.get('doc_path')!r}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"dispatch gate-modes SHADOW/ENFORCE check failed: {exc}")

    try:
        from pre_llm.tool_router.capability_catalog import _CATALOG  # noqa: WPS433
        from pre_llm.tool_router.router_engine import run_tool_router  # noqa: WPS433

        execute = _CATALOG.get("execute") or []
        report = _CATALOG.get("report") or []
        exec_hr = [c for c in execute if c.get("capability_id") == "hub_refresh"]
        rep_hr = [c for c in report if c.get("capability_id") == "hub_refresh"]
        if not exec_hr:
            errors.append("tool_router catalog: hub_refresh missing from execute")
        if not rep_hr:
            errors.append("tool_router catalog: hub_refresh missing from report")
        for row in exec_hr + rep_hr:
            if row.get("tool_id") != "hub/refresh":
                errors.append(f"tool_router hub_refresh tool_id drift: {row.get('tool_id')!r}")
            if row.get("permission") != "write":
                errors.append(f"tool_router hub_refresh permission drift: {row.get('permission')!r}")
        live = run_tool_router(
            text="hub refresh rebuild panel",
            task_id="audit-hub-refresh",
            force_refresh=True,
        )
        if not live.get("ok"):
            errors.append(f"tool_router hub_refresh live run not ok: {live}")
        else:
            sel = [
                s
                for s in (live.get("selection") or [])
                if s.get("capability_id") == "hub_refresh"
            ]
            if not sel:
                errors.append("tool_router hub_refresh not selected on hub refresh query")
            elif sel[0].get("tool_id") != "hub/refresh":
                errors.append(f"tool_router hub_refresh selection tool_id drift: {sel[0]!r}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"tool_router hub_refresh catalog check failed: {exc}")

    try:
        from pre_llm.vector_retrieval.embedding_provider import (  # noqa: WPS433
            hybrid_score,
            provider_payload,
        )
        from pre_llm.vector_retrieval.query_engine import search_chunks  # noqa: WPS433

        ep = provider_payload()
        if not ep.get("hybrid"):
            errors.append(f"vector_retrieval provider hybrid flag false: {ep}")
        score = hybrid_score(
            token_score=0.42,
            query="pre-LLM gate D5 vector retrieval",
            chunk_text="vector retrieval hybrid_score blends token overlap with hash embeddings",
        )
        if not (0.0 < score <= 1.0):
            errors.append(f"hybrid_score out of range: {score}")
        smoke_chunks = [
            {"chunk_id": "doc-1", "text": "D5 vector retrieval hybrid_score gate pre-LLM", "kind": "doc"},
            {"chunk_id": "doc-2", "text": "unrelated governance entry gate receipts", "kind": "doc"},
        ]
        hits = search_chunks(smoke_chunks, "hybrid_score vector gate D5", top_k=2, hybrid=True)
        if not hits:
            errors.append("search_chunks hybrid smoke returned no hits")
        elif hits[0].get("chunk_id") != "doc-1":
            errors.append(f"search_chunks hybrid smoke wrong top hit: {hits[0]!r}")
        elif float(hits[0].get("score") or 0) <= float(hits[-1].get("score") or 0):
            errors.append(f"search_chunks hybrid smoke ranking inverted: {hits}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"vector_retrieval hybrid_score smoke failed: {exc}")

    try:
        import inspect  # noqa: WPS433

        ranker_src = inspect.getsource(
            __import__("pre_llm.context_ranking.ranker", fromlist=["rank_evidence"]).rank_evidence
        )
        hybrid_src = inspect.getsource(
            __import__(
                "pre_llm.vector_retrieval.embedding_provider",
                fromlist=["hybrid_score"],
            ).hybrid_score
        )
        qe_src = (
            SOURCE_A / "scripts" / "pre_llm" / "vector_retrieval" / "query_engine.py"
        ).read_text(encoding="utf-8")
        d9 = {
            "intent": 0.26,
            "overlap": 0.22,
            "retrieval": 0.28,
            "graph": 0.12,
            "hybrid_sem": 0.12,
        }
        for w in d9.values():
            if f"{w}" not in ranker_src and f"{w:.2f}" not in ranker_src:
                errors.append(f"D9 blend weight {w} missing from ranker.py")
        if abs(sum(d9.values()) - 1.0) >= 0.001:
            errors.append(f"D9 blend weights must sum to 1.0: {d9}")
        if "hybrid_score" not in qe_src:
            errors.append("query_engine must call hybrid_score for hybrid mode")
        if not re.search(r"0\.55\s*\*\s*token_score\s*\+\s*0\.45\s*\*\s*sem", hybrid_src):
            errors.append("embedding_provider hybrid_score must use 0.55 token + 0.45 semantic")
        syn_path = SOURCE_A / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
        if not syn_path.is_file():
            errors.append("SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md missing — D9 blend doc drift")
        elif "D9 blend" not in syn_path.read_text(encoding="utf-8"):
            errors.append("synthesis doc missing D9 blend cross-reference")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"D9 blend weights doc/code check failed: {exc}")

    pre_llm = SOURCE_A / "scripts" / "pre_llm"
    authorized_modules = frozenset({
        "code_intelligence",
        "graph_fusion",
        "dependency_graph",
        "intent_engine",
        "vector_retrieval",
        "memory_git_bridge",
        "query_expansion",
        "graph_reasoning",
        "context_ranking",
        "planning_engine",
        "tool_router",
        "validation_layer",
        "diff_intelligence",
        "context_compression",
        "context_assembly",
        "packet_memory_merge",
        "context_packet",
        "packet_readiness",
        "user_signals",
        "semantic_history",
    })
    try:
        if not pre_llm.is_dir():
            errors.append("scripts/pre_llm missing — D-module guard cannot run")
        else:
            on_disk = {
                p.name
                for p in pre_llm.iterdir()
                if p.is_dir() and not p.name.startswith("__")
            }
            extra = sorted(on_disk - authorized_modules)
            missing = sorted(authorized_modules - on_disk)
            if extra:
                errors.append(f"unauthorized pre_llm modules: {extra}")
            if missing:
                errors.append(f"authorized pre_llm module missing locally: {missing}")
            syn_d = SOURCE_A / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
            if not syn_d.is_file():
                errors.append("synthesis doc missing — D1-D16 stack cross-ref drift")
            else:
                syn_text = syn_d.read_text(encoding="utf-8")
                if "D1–D16" not in syn_text and "D1-D16" not in syn_text:
                    errors.append("synthesis doc must document D1-D16 stack")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"D-module creation guard check failed: {exc}")

    try:
        import inspect  # noqa: WPS433

        from pre_llm.packet_memory_merge.memory_collector import (  # noqa: WPS433
            collect_b_layer_slots,
            collect_l5_history_slots,
        )

        mc_mod = __import__(
            "pre_llm.packet_memory_merge.memory_collector",
            fromlist=["collect_l5_history_slots"],
        )
        me_mod = __import__(
            "pre_llm.packet_memory_merge.merge_engine",
            fromlist=["run_memory_merge_writeback"],
        )
        mc_src = inspect.getsource(mc_mod)
        me_src = inspect.getsource(me_mod)
        for needle, msg in (
            ("build_semantic_history", "memory_collector must import L5 history_bridge"),
            ("semantic_history", "memory_collector must emit semantic_history slots"),
            ("feedback_signal", "memory_collector must emit feedback_signal slots"),
            ("execution_feedback_signals.jsonl", "B3 feedback path must be wired in memory_collector"),
        ):
            if needle not in mc_src:
                errors.append(msg)
        if "collect_l5_history_slots" not in me_src:
            errors.append("merge_engine must call collect_l5_history_slots")
        if "l5_slots" not in me_src:
            errors.append("merge_engine must merge l5_slots into D16 packet")
        hist_mod = inspect.getsource(
            __import__(
                "pre_llm.semantic_history.history_bridge",
                fromlist=["build_semantic_history"],
            ).build_semantic_history
        )
        if "read_git_commits" not in hist_mod:
            errors.append("L5 semantic_history must use git_reader for semantic history")
        l5 = collect_l5_history_slots(
            text="pre-LLM D16 memory merge semantic history",
            repo_root=str(SOURCE_A),
            limit=4,
        )
        if not isinstance(l5, list):
            errors.append(f"collect_l5_history_slots must return list: {type(l5)!r}")
        for row in l5[:2]:
            if row.get("kind") != "semantic_history":
                errors.append(f"L5 slot kind drift: {row!r}")
            if row.get("producer") != "L5":
                errors.append(f"L5 slot producer drift: {row!r}")
        if not isinstance(collect_b_layer_slots(limit=8), list):
            errors.append("collect_b_layer_slots must return list")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"semantic history L5→D16 path check failed: {exc}")

    synthesis_path = SOURCE_A / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
    try:
        from pre_llm.context_packet.schema import (  # noqa: WPS433
            FIELD_PRODUCERS,
            PACKET_VERSION,
            SCHEMA,
            SHIPPED_PRODUCERS,
            schema_contract_payload,
        )

        if not synthesis_path.is_file():
            errors.append("SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md missing — D16 shipped claim drift")
        else:
            synthesis = synthesis_path.read_text(encoding="utf-8")
            if "D16 shipped" not in synthesis and "**D16 shipped**" not in synthesis:
                errors.append("synthesis must record D16 shipped claim")
            if "D16 writeback is next" not in synthesis:
                errors.append("synthesis must cite stale Claude claim for contrast")
            report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
            if report_path.is_file():
                try:
                    from eval_report_capture import eval_synthesis_critic_drift_errors  # noqa: WPS433

                    rep_eval = json.loads(report_path.read_text(encoding="utf-8"))
                    errors.extend(eval_synthesis_critic_drift_errors(synthesis, rep_eval))
                except json.JSONDecodeError:
                    errors.append("eval_packet_v1b_report.json invalid — synthesis eval cross-check")
            try:
                import model_dispatch  # noqa: WPS433

                errors.extend(
                    model_dispatch.enforce_synthesis_critic_drift_errors(
                        synthesis, model_dispatch.current_gate_mode()
                    )
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(f"synthesis ENFORCE gate cross-check failed: {exc}")
        if "D16" not in SHIPPED_PRODUCERS:
            errors.append(f"SHIPPED_PRODUCERS must include D16: {SHIPPED_PRODUCERS}")
        if "D16" not in (FIELD_PRODUCERS.get("memory") or []):
            errors.append(f"FIELD_PRODUCERS memory must include D16: {FIELD_PRODUCERS.get('memory')}")
        api = schema_contract_payload()
        if api.get("ok") is not True:
            errors.append(f"schema_contract_payload not ok: {api}")
        elif api.get("schema") != SCHEMA:
            errors.append(f"schema_contract schema drift: {api.get('schema')} != {SCHEMA}")
        elif api.get("packet_version") != PACKET_VERSION:
            errors.append(f"packet_version drift: {api.get('packet_version')} != {PACKET_VERSION}")
        elif api.get("pre_llm_steps_shipped") != "16/16":
            errors.append(f"pre_llm_steps_shipped drift: {api.get('pre_llm_steps_shipped')}")
        elif "D16" not in (api.get("shipped_producers") or []):
            errors.append(f"shipped_producers must include D16: {api.get('shipped_producers')}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Claude D16 shipped vs packet schema check failed: {exc}")

    try:
        from eval_packet_v1b.grounding import (  # noqa: WPS433
            GOVERNANCE_RULES_PATHS,
            build_task_grounding,
            cross_check_governance_rules_grounding,
        )

        for err in cross_check_governance_rules_grounding():
            errors.append(f"governance-rules grounding: {err}")
        g = build_task_grounding(
            task_id="governance-rules",
            prompt="How does rules-in-charge loop load agent_rules scripts at session start?",
            keywords=["rules_in_charge", "agent_rules", "session", "orchestrator"],
        )
        paths = list(g.get("expected_paths") or [])
        if paths != list(GOVERNANCE_RULES_PATHS):
            errors.append(
                f"governance-rules expected_paths drift: {paths} != {list(GOVERNANCE_RULES_PATHS)}"
            )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"governance-rules grounding check failed: {exc}")

    critic_law = SOURCE_A / "brain-os" / "law" / "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
    critic_rule = SOURCE_A / ".cursor" / "rules" / "chatgpt-external-critic.mdc"
    critic_stub = SOURCE_A / "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
    try:
        from meta_reasoning_policy import meta_reasoning_payload  # noqa: WPS433
        from system_roadmap import SYSTEM_AUTHORITIES  # noqa: WPS433

        if not critic_law.is_file():
            errors.append("CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md missing")
        if not critic_rule.is_file():
            errors.append("chatgpt-external-critic.mdc missing")
        if not critic_stub.is_file():
            errors.append("CHATGPT_EXTERNAL_CRITIC_LAW stub missing")
        elif "brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md" not in critic_stub.read_text(
            encoding="utf-8"
        ):
            errors.append("critic law stub must point to brain-os/law canonical path")
        if critic_law.is_file():
            law_text = critic_law.read_text(encoding="utf-8").lower()
            if "never treat" not in law_text and "never obey" not in law_text:
                errors.append("critic law must forbid obeying critic")
            if "build order" not in law_text:
                errors.append("critic law must forbid critic reorder")
            if "steer" not in law_text:
                errors.append("critic law must mention steer prohibition")
        if critic_rule.is_file():
            rule_text = critic_rule.read_text(encoding="utf-8").lower()
            if "never" not in rule_text or "build order" not in rule_text:
                errors.append("chatgpt-external-critic.mdc must forbid critic build-order steer")
        auth = SYSTEM_AUTHORITIES
        if auth.get("critic_input_class") != "EXTERNAL_CRITIC":
            errors.append(f"critic_input_class drift: {auth.get('critic_input_class')}")
        if "never" not in str(auth.get("external_review_policy") or "").lower():
            errors.append("external_review_policy must say never steer critic")
        hier = {row.get("class"): row for row in (auth.get("authority_hierarchy") or [])}
        if "EXTERNAL_CRITIC" not in hier:
            errors.append("authority_hierarchy missing EXTERNAL_CRITIC")
        elif "compare" not in str(hier["EXTERNAL_CRITIC"].get("role") or "").lower():
            errors.append("EXTERNAL_CRITIC role must be compare-only")
        meta = meta_reasoning_payload()
        classes = {row.get("class"): row for row in (meta.get("input_classes") or [])}
        if "EXTERNAL_CRITIC" not in classes:
            errors.append("meta_reasoning input_classes missing EXTERNAL_CRITIC")
        elif "never steer" not in str(classes["EXTERNAL_CRITIC"].get("authority") or "").lower():
            errors.append("meta_reasoning EXTERNAL_CRITIC must say never steer")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"external critic law cross-check failed: {exc}")

    wtm_pre_llm = SOURCE_A / "brain-os" / "wtm" / "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md"
    try:
        from system_roadmap import _build_layer_comparison  # noqa: WPS433

        if not wtm_pre_llm.is_file():
            errors.append("SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md missing — L0-full gap drift")
        else:
            wtm_gap_text = wtm_pre_llm.read_text(encoding="utf-8")
            if "L0-full gap note" not in wtm_gap_text:
                errors.append("WTM must document L0-full gap note")
            wtm_lower = wtm_gap_text.lower()
            if "editor telemetry" not in wtm_lower and "editor open_files" not in wtm_lower:
                errors.append("WTM must document editor telemetry gap")
            if "partial" not in wtm_lower:
                errors.append("WTM must mark L0-full as partial")
        rows = {r["layer"]: r for r in _build_layer_comparison()}
        l0 = rows.get("L0") or {}
        if l0.get("your_status") not in ("done", "partial"):
            errors.append(f"L0 layer_comparison your_status drift: {l0.get('your_status')}")
        gap = str(l0.get("gap") or "").lower()
        if not any(k in gap for k in ("editor", "l0-full", "hub touch")):
            errors.append(f"L0 layer_comparison gap must cite editor/l0-full/hub touch: {l0.get('gap')}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"L0-full editor telemetry gap check failed: {exc}")

    embed_provider = SOURCE_A / "scripts" / "pre_llm" / "vector_retrieval" / "embedding_provider.py"
    try:
        reg = json.loads(
            (SOURCE_A / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json").read_text(
                encoding="utf-8"
            )
        )
        phases = {p.get("id") for p in (reg.get("phases") or [])}
        if "phase-s9-research-models" not in phases:
            errors.append("REGISTRY missing phase-s9-research-models — embeddings deferral drift")
        if not wtm_pre_llm.is_file():
            errors.append("SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md missing — deferral doc drift")
        else:
            wtm_text = wtm_pre_llm.read_text(encoding="utf-8")
            if "phase-s9-research-models" not in wtm_text:
                errors.append("WTM must cite phase-s9-research-models deferral for OpenRouter embeddings")
            if "phase-s6-wtm-pre-llm" not in wtm_text:
                errors.append("WTM must scope deferral away from phase-s6-wtm-pre-llm")
            if "sa-0620" not in wtm_text and "Embedding API deferral" not in wtm_text:
                errors.append("WTM missing Embedding API deferral documentation")
        if not embed_provider.is_file():
            errors.append("embedding_provider.py missing — D5 hybrid path drift")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"OpenRouter embeddings deferred-s9 check failed: {exc}")

    try:
        from pre_llm.context_packet.schema import (  # noqa: WPS433
            empty_packet_template,
            hydrate_from_disk_substrate,
            validate_packet,
        )

        hydrated = hydrate_from_disk_substrate(empty_packet_template())
        partial = validate_packet(hydrated)
        if partial.get("gate_eligible"):
            errors.append("hydrate_from_disk_substrate must stay gate_eligible=false on partial hydrate")
        missing_gate = partial.get("missing_for_gate") or []
        if "constraints" not in missing_gate:
            errors.append(
                f"partial hydrate missing_for_gate must include constraints: {missing_gate}"
            )
        code = hydrated.get("code") or {}
        deps = hydrated.get("dependencies") or {}
        if not code.get("files"):
            errors.append("hydrate_from_disk_substrate: D1 must populate code.files")
        if deps.get("impact_ready") is not True:
            errors.append("hydrate_from_disk_substrate: D3 must set dependencies.impact_ready")
        steps = (hydrated.get("provenance") or {}).get("producer_steps") or []
        for step in ("D1", "D2", "D3"):
            if step not in steps:
                errors.append(f"hydrate_from_disk_substrate: producer_steps missing {step}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"hydrate D1-D3 partial rule check failed: {exc}")

    eval_1b = payload.get("eval_packet_v1b") or {}
    if eval_1b.get("schema") == "eval-packet-v1b":
        if eval_1b.get("mode") == "scaffold" and eval_1b.get("live_ok") is True:
            errors.append(
                "eval-1b hub regression: system_roadmap eval_packet_v1b mode=scaffold while live_ok=true"
            )
    ci_mode_path = Path.home() / ".sina" / "eval_1b_ci_mode_v1.json"
    structural_ci = False
    if ci_mode_path.is_file():
        try:
            ci_row = json.loads(ci_mode_path.read_text(encoding="utf-8"))
            structural_ci = bool(ci_row.get("structural_fallback"))
        except json.JSONDecodeError:
            pass
    if eval_1b.get("schema") == "eval-packet-v1b":
        report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
        if report_path.is_file():
            try:
                rep = json.loads(report_path.read_text(encoding="utf-8"))
                if (
                    rep.get("mode") == "live"
                    and not rep.get("live_ok", rep.get("ok"))
                    and not structural_ci
                ):
                    errors.append(
                        f"eval-1b live report stale: live_ok={rep.get('live_ok')} "
                        f"wins={rep.get('live_pilot_wins')}/{rep.get('live_pilot_count')}"
                    )
                if (
                    rep.get("mode") == "live"
                    and int(rep.get("live_pilot_count") or 0) < 5
                    and not structural_ci
                ):
                    errors.append(
                        f"eval-1b live pilots {rep.get('live_pilot_count')} < 5 — expand tasks.json live_pilot"
                    )
                if structural_ci and rep.get("mode") == "live" and not rep.get("live_ok"):
                    errors.append(
                        "eval-1b structural CI active but report still mode=live — "
                        "re-run validate-eval-packet-v1b-live.sh to refresh scaffold report"
                    )
                try:
                    from eval_report_capture import eval_scaffold_live_regression_errors  # noqa: WPS433

                    errors.extend(eval_scaffold_live_regression_errors(rep, label="eval_packet_v1b_report"))
                except Exception:
                    if rep.get("mode") == "scaffold" and rep.get("live_ok") is True:
                        errors.append(
                            "eval-1b regression: mode=scaffold while live_ok=true logged report"
                        )
            except json.JSONDecodeError as e:
                errors.append(f"eval_packet_v1b_report.json invalid: {e}")

    eb = payload.get("event_bus") or {}
    if not eb.get("ok"):
        errors.append("system_roadmap.event_bus missing or not ok — Phase 5 fabric")

    gr = payload.get("gate_receipts") or {}
    if not gr.get("ok"):
        errors.append("system_roadmap.gate_receipts missing or not ok — ENFORCE bypass panel")
    elif gr.get("bypass_doc") != "brain-os/law/enforcement/law/enforcement/ENFORCE_BYPASS_MAP_LOCKED_v1.md":
        errors.append(f"gate_receipts.bypass_doc drift: {gr.get('bypass_doc')!r}")
    elif len(gr.get("bypass_routes") or []) != 8:
        errors.append(
            f"gate_receipts.bypass_routes count != 8: {len(gr.get('bypass_routes') or [])}"
        )
    bypass_doc = SOURCE_A / "brain-os/law/enforcement/law/enforcement/ENFORCE_BYPASS_MAP_LOCKED_v1.md"
    if not bypass_doc.is_file():
        errors.append("ENFORCE_BYPASS_MAP_LOCKED_v1.md missing locally")
    elif APP_JS.is_file() and not worker_hub_mode():
        js = APP_JS.read_text(encoding="utf-8")
        if "gate-receipts-panel" not in js or "renderGateReceiptsPanel" not in js:
            errors.append("app.js missing gate-receipts-panel / renderGateReceiptsPanel")
    if bypass_doc.is_file() and gr.get("ok"):
        try:
            from gate_receipts_hub import BYPASS_ROUTES  # noqa: WPS433

            hub_routes = {r["route"]: r for r in BYPASS_ROUTES}
            if len(hub_routes) != 8:
                errors.append(f"gate_receipts_hub.BYPASS_ROUTES count != 8: {len(hub_routes)}")
            elif sum(1 for r in BYPASS_ROUTES if r.get("enforce")) != 1:
                errors.append("gate_receipts_hub: expected exactly one enforce=true route")
            elif hub_routes.get("agent_loop planner", {}).get("enforce") is not True:
                errors.append("agent_loop planner must have enforce=true in BYPASS_ROUTES")
            else:
                section = bypass_doc.read_text(encoding="utf-8").split("## Receipt logs", 1)[0]
                doc_rows = 0
                for line in section.splitlines():
                    if not line.startswith("|") or line.startswith("| Route") or "---" in line:
                        continue
                    if len([c.strip() for c in line.strip("|").split("|")]) >= 2:
                        doc_rows += 1
                if doc_rows != 8:
                    errors.append(f"ENFORCE_BYPASS_MAP doc table rows != 8: {doc_rows}")
                payload_routes = {r.get("route") for r in (gr.get("bypass_routes") or [])}
                if payload_routes != set(hub_routes):
                    errors.append(
                        "system_roadmap.gate_receipts.bypass_routes drift vs gate_receipts_hub"
                    )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"gate_receipts route alignment check failed: {exc}")

    if COMMAND_DATA.is_file():
        try:
            embedded = json.loads(COMMAND_DATA.read_text(encoding="utf-8"))
            sr = embedded.get("system_roadmap") or {}
            if not sr.get("ok"):
                errors.append("command-data.json system_roadmap not ok — rebuild hub")
            elif sr.get("version") != PAYLOAD_VERSION:
                errors.append(
                    f"command-data.json stale: v{sr.get('version')} != {PAYLOAD_VERSION} — run build"
                )
            elif sr.get("map_doc") != MAP_DOC:
                errors.append(f"command-data.json map_doc {sr.get('map_doc')!r} != {MAP_DOC}")
            else:
                cd_gr = sr.get("gate_receipts") or {}
                if not cd_gr.get("ok") or len(cd_gr.get("bypass_routes") or []) != 8:
                    errors.append("command-data.json gate_receipts stale — rebuild hub")
        except json.JSONDecodeError as e:
            errors.append(f"command-data.json invalid JSON: {e}")

    if errors:
        print("HUB SOURCE/UI ALIGNMENT FAILED:")
        for e in errors:
            print(f"  - {e}")
        print(f"Fix: edit scripts/system_roadmap.py + {MAP_DOC}, then:")
        print("  python3 scripts/build-sina-command-panel.py")
        return 1

    print(
        f"OK: hub source/UI alignment · payload v{PAYLOAD_VERSION} · "
        f"{len(phase_d_ids)} Phase D steps · {MAP_DOC}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
