#!/usr/bin/env python3
"""Agent nerve system — unified live-wire health · queue alignment · loop + OQG lines.

Collects L0.5→L2 receipts into one SSOT. Law: AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md
Receipt: ~/.sina/agent-nerve-system-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "agent-nerve-system-receipt-v1.json"

NERVE_PATHS: dict[str, Path] = {
    "surfaces": SINA / "agent-live-surfaces-v1.json",
    "anti_staleness": SINA / "anti-staleness-auto-wire-v1.json",
    "zero_drift": SINA / "governance-zero-drift-live-wire-v1.json",
    "better_loop": SINA / "better-loop-pulse-receipt-v1.json",
    "oqg": SINA / "best-loop-oqg-receipt-v1.json",
    "mirror": SINA / "agent-memory-mirror-v1.json",
    "worker_context": SINA / "worker-live-context-v1.json",
    "brain_context": SINA / "brain-live-context-v1.json",
    "truth_bundle": SINA / "last-truth-bundle-v1.json",
    "factory_now": SINA / "factory-now-v1.json",
    "disk_live_wire": SINA / "disk-live-wire-receipt-v1.json",
    "form_official": SINA / "form-official-wire-receipt-v1.json",
    "ui_upgrade_first_check": SINA / "ui-upgrade-first-check-receipt-v1.json",
    "research_index": SINA / "research-root" / "INDEX.yaml",
    "research_digest": SINA / "research-root" / "filtered" / "execution_core.digest.yaml",
    "worker_connected": SINA / "sourcea-worker-connected-receipt-v1.json",
    "outbound_coherence": SINA / "outbound-queue-coherence-receipt-v1.json",
    "orient_report": SINA / "orient-routing-report-v1.json",
    "orientation_receipt": SINA / "agent-orientation-receipt-v1.json",
    "hospital_receipt": SINA / "agent-hospital-receipt-v1.json",
    "maze_receipt": SINA / "agent-maze-receipt-v1.json",
    "ecosystem_connected": SINA / "sourcea-ecosystem-connected-receipt-v1.json",
    "step9_commercial": SINA / "worker-wire-step9-commercial-form-v1.json",
    "investigator_judge": SINA / "investigator-judge-unified-receipt-v1.json",
    "mac_law_universal": SINA / "mac-law-universal-wire-receipt-v1.json",
    "mac_law_machine": SINA / "mac-law-machine-enforce-receipt-v1.json",
    "mac_law_agent_lock": SINA / "mac-law-agent-execution-plane-lock-receipt-v1.json",
}


def _research_root_ok() -> dict:
    idx = NERVE_PATHS["research_index"]
    dig = NERVE_PATHS["research_digest"]
    reg = SINA / "research-root" / "registry.jsonl"
    ok = idx.is_file() and dig.is_file()
    rows = 0
    if reg.is_file():
        rows = sum(1 for line in reg.read_text(encoding="utf-8").splitlines() if line.strip())
    return {
        "ok": ok,
        "registry_rows": rows,
        "index": idx.is_file(),
        "execution_core_digest": dig.is_file(),
        "law": "UNIFIED_RESEARCH_ROOT_LOCKED_v1.md",
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _queue_from_row(row: dict, *, factory: dict | None = None) -> str:
    if not row:
        return ""
    if row.get("queue_exhausted"):
        return ""
    for key in ("queue_sa",):
        val = row.get(key)
        if val:
            return str(val)
    dual = row.get("dual_pick") or {}
    if dual.get("queue_sa"):
        return str(dual["queue_sa"])
    fn = row.get("factory_now") or factory or {}
    if fn.get("queue_exhausted"):
        return ""
    if fn.get("queue_sa"):
        return str(fn["queue_sa"])
    return ""


def _collect_nodes() -> list[dict]:
    nodes: list[dict] = []
    surfaces = _read_json(NERVE_PATHS["surfaces"])
    anti = _read_json(NERVE_PATHS["anti_staleness"])
    zd = _read_json(NERVE_PATHS["zero_drift"])
    bl = _read_json(NERVE_PATHS["better_loop"])
    oqg = _read_json(NERVE_PATHS["oqg"])
    mirror = _read_json(NERVE_PATHS["mirror"])
    worker = _read_json(NERVE_PATHS["worker_context"])
    brain = _read_json(NERVE_PATHS["brain_context"])
    truth = _read_json(NERVE_PATHS["truth_bundle"])
    factory = _read_json(NERVE_PATHS["factory_now"])
    form_wire = _read_json(NERVE_PATHS["form_official"])
    ui_fc = _read_json(NERVE_PATHS["ui_upgrade_first_check"])

    ls = (mirror.get("inject") or {}).get("live_surfaces") or {}

    specs = [
        ("surfaces", surfaces, surfaces.get("synced_at"), bool(surfaces.get("factory_now_line"))),
        ("anti_staleness", anti, anti.get("at"), anti.get("ok")),
        ("zero_drift", zd, zd.get("at"), zd.get("ok")),
        ("better_loop", bl, bl.get("at"), bl.get("ok")),
        ("oqg", oqg, oqg.get("at"), oqg.get("metric") == "output_clean_pct"),
        ("form_official", form_wire, form_wire.get("wired_at"), bool(form_wire.get("ok"))),
        ("ui_upgrade_first_check", ui_fc, ui_fc.get("saved_at"), bool(ui_fc.get("wire_ok"))),
        ("mirror_inject", ls, ls.get("synced_at"), bool(ls.get("factory_now_line"))),
        ("worker_context", worker, worker.get("at"), bool(worker.get("text_block"))),
        ("brain_context", brain, brain.get("at"), bool(brain.get("text_block"))),
        ("truth_bundle", truth, truth.get("at"), truth.get("schema") == "agent-truth-bundle-v1"),
        (
            "factory_now",
            factory,
            factory.get("at"),
            bool(factory.get("queue_sa")) or _lawful_registry_idle(factory),
        ),
    ]
    behavior = _read_json(SINA / "agent-behavior-settings-receipt-v1.json")
    mirror_detail = (mirror.get("inject") or {}).get("founder_intent_first_detail") or {}
    specs.append(
        (
            "founder_intent_behavior",
            behavior,
            behavior.get("at"),
            bool(behavior.get("ok")) and bool(mirror_detail.get("one_law")),
        )
    )
    cost_intel = _read_json(SINA / "factory-cost-intelligence-receipt-v1.json")
    cost_detail = (mirror.get("inject") or {}).get("factory_cost_intelligence_detail") or {}
    specs.append(
        (
            "factory_cost_intelligence",
            cost_intel,
            cost_intel.get("at"),
            bool(cost_intel.get("ok")) and int(cost_detail.get("registry_count") or 0) >= 100,
        )
    )
    for node_id, row, at, pass_hint in specs:
        nodes.append(
            {
                "id": node_id,
                "present": bool(row),
                "ok": bool(pass_hint) if row else False,
                "at": at,
                "queue_sa": _queue_from_row(row, factory=factory)
                if node_id != "factory_now"
                else str(factory.get("queue_sa") or ""),
            }
        )
    ml_u = _read_json(NERVE_PATHS["mac_law_universal"])
    ml_m = _read_json(NERVE_PATHS["mac_law_machine"])
    ml_l = _read_json(NERVE_PATHS["mac_law_agent_lock"])
    for node_id, row, at_key in (
        ("mac_law_universal_wire", ml_u, "saved_at"),
        ("mac_law_machine_enforce", ml_m, "saved_at"),
        ("mac_law_agent_lock", ml_l, "saved_at"),
    ):
        nodes.append(
            {
                "id": node_id,
                "present": bool(row),
                "ok": bool(row.get("ok")) if row else False,
                "at": row.get(at_key),
                "queue_sa": "",
            }
        )
    return nodes


def _lawful_registry_idle(factory: dict) -> bool:
    return (
        int(factory.get("backlog") or 0) == 0
        and int(factory.get("valid_yes") or 0) >= 1000
        and bool(factory.get("dual_proof_ok"))
        and not str(factory.get("queue_sa") or "").strip()
    )


def _alignment_issues(*, canonical: str, nodes: list[dict], lawful_idle: bool = False) -> list[str]:
    if lawful_idle:
        return []
    if not canonical:
        return ["queue_sa_missing"]
    issues: list[str] = []
    for node in nodes:
        nid = node.get("id")
        q = str(node.get("queue_sa") or "")
        if not node.get("present"):
            issues.append(f"{nid}:missing")
            continue
        if q and q != canonical:
            issues.append(f"{nid}:queue_mismatch({q}!={canonical})")
    return issues


def _compute_w3_send_ready(
    *,
    w3_oqg_pass: bool,
    w3_critic_pass: bool,
    w3_receiver_interest_pass: bool,
    w3_conversation_interest_pass: bool,
    w3_rrl_pass: bool,
    w3_sina_read_pass: bool,
    mail_from_ok: bool,
    pipeline_cleared_not_sent: bool,
    email_send_deferred: bool = False,
) -> bool:
    """U040 — composite send gate; RRL pass alone never sufficient without Sina read."""
    if email_send_deferred:
        return False
    return (
        w3_oqg_pass
        and w3_critic_pass
        and w3_receiver_interest_pass
        and w3_conversation_interest_pass
        and w3_rrl_pass
        and w3_sina_read_pass
        and mail_from_ok
        and pipeline_cleared_not_sent
    )


def validate_rrl_not_ship_ready(*, bl: dict | None = None, oqg: dict | None = None) -> dict:
    """U040 acceptance — w3_rrl_pass ≠ w3_send_ready (RRL alone never ship-ready)."""
    bl = bl or _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    oqg = oqg or _read_json(SINA / "best-loop-oqg-receipt-v1.json")
    ship = _ship_gates(bl=bl, oqg=oqg)
    rrl = bool(ship.get("w3_rrl_pass"))
    sina = bool(ship.get("w3_sina_read_pass"))
    send = bool(ship.get("w3_send_ready"))
    live_ok = not (send and not sina)
    rrl_only_ne_send = (rrl and not sina and not send) if rrl else True
    synthetic_send = _compute_w3_send_ready(
        w3_oqg_pass=True,
        w3_critic_pass=True,
        w3_receiver_interest_pass=True,
        w3_conversation_interest_pass=True,
        w3_rrl_pass=True,
        w3_sina_read_pass=False,
        mail_from_ok=True,
        pipeline_cleared_not_sent=True,
    )
    return {
        "ok": live_ok and rrl_only_ne_send and synthetic_send is False,
        "w3_rrl_pass": rrl,
        "w3_sina_read_pass": sina,
        "w3_send_ready": send,
        "live_send_without_sina_blocked": live_ok,
        "rrl_only_ne_send_ready": rrl_only_ne_send,
        "synthetic_rrl_only_send_ready": synthetic_send,
        "acceptance": "w3_rrl_pass ≠ w3_send_ready",
        "upgrade": "U040",
        "check": "python3 scripts/agent_nerve_system_v1.py --check-rrl-ship-gate --json",
    }


def _ship_gates(*, bl: dict, oqg: dict) -> dict:
    """BQ2 ship readiness — W3 OQG + Mail FROM + approved-not-sent."""
    sys.path.insert(0, str(SCRIPTS))
    w3_oqg_pass = True
    w3_artifacts: list[dict] = []
    waiver_n = int(oqg.get("active_waiver_count") or 0)
    try:
        from best_loop_oqg_score_v1 import score_w3_lane, active_waiver_count  # noqa: WPS433

        w3 = score_w3_lane()
        w3_oqg_pass = bool(w3.get("oqg_pass"))
        w3_artifacts = w3.get("artifacts") or []
        waiver_n = active_waiver_count()
    except Exception:
        w3_lane = next(
            (l for l in (oqg.get("lanes") or []) if l.get("lane") == "w3_commercial"),
            {},
        )
        w3_oqg_pass = bool(w3_lane.get("oqg_pass"))

    approved_not_sent = 0
    for chk in bl.get("ship_checks") or bl.get("founder_checks") or bl.get("checks") or []:
        cid = str(chk.get("id") or "")
        if cid in ("w3_sends", "w3_output_clean") and not chk.get("ok"):
            approved_not_sent = max(approved_not_sent, int(chk.get("count") or 2))
    if not approved_not_sent:
        loops = bl.get("loops") or {}
        loop_items = loops if isinstance(loops, list) else loops.values()
        for step in loop_items:
            if isinstance(step, dict) and step.get("id") == "commercial_flywheel":
                raw = step.get("approved_not_sent_count")
                if raw is None:
                    raw = step.get("approved_not_sent")
                if isinstance(raw, list):
                    approved_not_sent = len(raw)
                else:
                    approved_not_sent = int(raw or 0)

    mail_from_ok = False
    mail_configured: list[str] = []
    try:
        from commercial_mail_draft_v1 import mail_configured_addresses  # noqa: WPS433

        mail_configured = mail_configured_addresses()
        need = {"hello@trustfield.ca", "operation@noetfield.com"}
        mail_from_ok = need.issubset({a.lower() for a in mail_configured})
    except Exception:
        pass

    checks = bl.get("ship_checks") or bl.get("founder_checks") or bl.get("checks") or []
    chk_by_id = {str(c.get("id") or ""): c for c in checks}
    w3_critic_pass = bool(chk_by_id.get("w3_critic_circle", {}).get("ok"))
    w3_sina_read_pass = bool(chk_by_id.get("w3_sina_read", {}).get("ok")) or bool(
        chk_by_id.get("w3_founder_score", {}).get("ok")
    )
    w3_receiver_interest_pass = bool(chk_by_id.get("w3_receiver_interest", {}).get("ok"))
    w3_conversation_interest_pass = bool(chk_by_id.get("w3_conversation_interest", {}).get("ok"))
    w3_rrl_pass = bool(chk_by_id.get("w3_rrl", {}).get("ok"))
    w3_sends_chk = chk_by_id.get("w3_sends") or {}
    pipeline_cleared_not_sent = not bool(w3_sends_chk.get("ok", True))
    if pipeline_cleared_not_sent:
        approved_not_sent = max(approved_not_sent, int(w3_sends_chk.get("count") or 2))

    email_send_deferred = False
    email_defer_line = ""
    try:
        from commercial_email_send_defer_v1 import assess as email_defer_assess  # noqa: WPS433

        defer_row = email_defer_assess(write=False)
        email_send_deferred = bool(defer_row.get("defer_active"))
        email_defer_line = str(defer_row.get("email_send_defer_line") or "")
    except Exception:
        email_send_deferred = True

    w3_send_ready = _compute_w3_send_ready(
        w3_oqg_pass=w3_oqg_pass,
        w3_critic_pass=w3_critic_pass,
        w3_receiver_interest_pass=w3_receiver_interest_pass,
        w3_conversation_interest_pass=w3_conversation_interest_pass,
        w3_rrl_pass=w3_rrl_pass,
        w3_sina_read_pass=w3_sina_read_pass,
        mail_from_ok=mail_from_ok,
        pipeline_cleared_not_sent=pipeline_cleared_not_sent,
        email_send_deferred=email_send_deferred,
    )

    return {
        "w3_oqg_pass": w3_oqg_pass,
        "w3_critic_pass": w3_critic_pass,
        "w3_receiver_interest_pass": w3_receiver_interest_pass,
        "w3_conversation_interest_pass": w3_conversation_interest_pass,
        "w3_rrl_pass": w3_rrl_pass,
        "w3_sina_read_pass": w3_sina_read_pass,
        "w3_founder_score_pass": w3_sina_read_pass,
        "w3_rrl_not_ship_authority": True,
        "w3_send_ready_requires_sina_read": True,
        "w3_rrl_alone_never_send_ready": bool(w3_rrl_pass and not w3_sina_read_pass and not w3_send_ready),
        "upgrade_u040": "U040",
        "w3_artifacts": w3_artifacts,
        "w3_approved_not_sent_count": approved_not_sent,
        "w3_pipeline_cleared_not_sent": pipeline_cleared_not_sent,
        "w3_mail_from_configured": mail_from_ok,
        "w3_mail_accounts": mail_configured,
        "w3_email_send_deferred": email_send_deferred,
        "email_send_defer_line": email_defer_line,
        "w3_send_ready": w3_send_ready,
        "active_waiver_count": waiver_n,
    }


def _nerve_line(
    *,
    queue_sa: str,
    aligned: bool,
    drift_score: int | None,
    red_count: int,
    fleet_clean: int | None,
    anti_ok: bool,
    waiver_n: int = 0,
    send_ready: bool = False,
    system_red_count: int = 0,
    commercial_red_count: int = 0,
    commercial_rule_ids: list[str] | None = None,
    research_ok: bool = False,
    ui_fc_ok: bool = False,
) -> str:
    align = "aligned" if aligned else "drift"
    drift = drift_score if drift_score is not None else "?"
    fleet_tag = f"fleet{fleet_clean}%" if fleet_clean is not None else "oqg?"
    if fleet_clean is not None and fleet_clean >= 90:
        fleet_tag = f"fleet90+"
    as_bit = "AS=ok" if anti_ok else "AS=review"
    w_bit = f" · waiver={waiver_n}" if waiver_n else ""
    ship = " · send-ready" if send_ready else ""
    if commercial_red_count and not system_red_count:
        loop_bit = f"loop={commercial_red_count}commercial"
    elif system_red_count or commercial_red_count:
        loop_bit = f"loop={system_red_count}sys·{commercial_red_count}comm"
    else:
        loop_bit = f"loop={red_count}red"
    rules_bit = ""
    if commercial_red_count and commercial_rule_ids:
        shown = ",".join(commercial_rule_ids[:4])
        if len(commercial_rule_ids) > 4:
            shown += f"+{len(commercial_rule_ids) - 4}"
        rules_bit = f" · rules={shown}"
    ui_bit = "ui_fc=mandatory" if ui_fc_ok else "ui_fc=BLOCK"
    return (
        f"nerve · queue={queue_sa or 'idle'} · {align} · drift={drift} · "
        f"{loop_bit}{rules_bit} · {fleet_tag}{w_bit}{ship} · research={'YES' if research_ok else 'NO'} · {as_bit} · {ui_bit}"
    )


def _outbound_ship_gates() -> dict:
    """Worker full wire gates — nerve must enforce, not only mirror."""
    sys.path.insert(0, str(SCRIPTS))
    row: dict = {}
    try:
        from validate_sourcea_worker_connected_v1 import assess_connected  # noqa: WPS433

        wc = assess_connected(hub_check=False, write_receipt=False)
        row["worker_connected"] = bool(wc.get("ok"))
        row["worker_connected_line"] = wc.get("line") or ""
        row["outbound_progress_line"] = wc.get("outbound_progress_line") or ""
        row["execution_honesty_line"] = wc.get("execution_honesty_line") or ""
    except Exception as exc:
        row["worker_connected"] = False
        row["error"] = str(exc)

    try:
        from outbound_queue_coherence_v1 import assess_queue_coherence  # noqa: WPS433

        coh = assess_queue_coherence()
        row["outbound_coherence"] = bool(coh.get("ok"))
        row["outbound_head"] = coh.get("head") or {}
    except Exception as exc:
        row["outbound_coherence"] = False
        row["coherence_error"] = str(exc)

    try:
        from execution_plane_honesty_v1 import assess_execution_plane  # noqa: WPS433

        ep = assess_execution_plane()
        checks = ep.get("checks") or {}
        honest_n = sum(1 for v in checks.values() if v)
        total_n = len(checks) or 12
        row["execution_honesty_12of12"] = bool(ep.get("ok"))
        row["execution_honesty_score"] = f"{honest_n}/{total_n}"
    except Exception as exc:
        row["execution_honesty_12of12"] = False
        row["honesty_error"] = str(exc)

    try:
        from worker_wire_step9_commercial_form_v1 import assess_step9  # noqa: WPS433

        s9 = assess_step9()
        row["commercial_l3_pct"] = (s9.get("commercial") or {}).get("ready_pct")
        row["commercial_l3_ok"] = int((s9.get("commercial") or {}).get("ready_pct") or 0) >= 100
        row["form_open_picks"] = (s9.get("form") or {}).get("open_picks")
    except Exception as exc:
        row["commercial_l3_ok"] = False
        row["step9_error"] = str(exc)

    ij = _read_json(NERVE_PATHS["investigator_judge"])
    row["investigator_judge_ok"] = bool(ij.get("ok")) if ij else None

    orient = _read_json(NERVE_PATHS["orient_report"])
    row["orient_fresh"] = bool(orient.get("ok")) if orient else None

    return row


def run_nerve_pulse(*, write: bool = True, refresh_loops: bool = False) -> dict:
    if refresh_loops:
        sys.path.insert(0, str(SCRIPTS))
        try:
            from better_loop_pulse_v1 import run_pulse  # noqa: WPS433
            from best_loop_oqg_score_v1 import run_oqg  # noqa: WPS433

            run_pulse(write=True)
            run_oqg(write=True)
        except Exception:
            pass

    try:
        from investigator_judge_unified_receipt_v1 import build_unified_receipt  # noqa: WPS433

        build_unified_receipt(write=True)
    except Exception:
        pass

    surfaces = _read_json(NERVE_PATHS["surfaces"])
    anti = _read_json(NERVE_PATHS["anti_staleness"])
    zd = _read_json(NERVE_PATHS["zero_drift"])
    bl = _read_json(NERVE_PATHS["better_loop"])
    oqg = _read_json(NERVE_PATHS["oqg"])
    factory = _read_json(NERVE_PATHS["factory_now"])
    truth = _read_json(NERVE_PATHS["truth_bundle"])
    form_wire = _read_json(NERVE_PATHS["form_official"])
    ui_fc = _read_json(NERVE_PATHS["ui_upgrade_first_check"])
    truth_q = (truth.get("run_inbox_truth") or {}).get("queue") or {}

    canonical = (
        str(surfaces.get("queue_sa") or "")
        or str(factory.get("queue_sa") or "")
        or str(anti.get("queue_sa") or "")
        or _queue_from_row(truth)
    )
    lawful_idle = _lawful_registry_idle(factory) and bool(
        truth_q.get("queue_exhausted") or not canonical
    )
    if lawful_idle:
        canonical = ""

    nodes = _collect_nodes()
    align_issues = _alignment_issues(canonical=canonical, nodes=nodes, lawful_idle=lawful_idle)
    aligned = not any("mismatch" in i for i in align_issues)

    lines = {
        "factory_now_line": surfaces.get("factory_now_line") or factory.get("line") or "",
        "zero_drift_line": surfaces.get("zero_drift_line") or zd.get("zero_drift_line") or "",
        "sascip_safety_line": surfaces.get("sascip_safety_line") or surfaces.get("sascip_line") or "",
        "better_loop_line": surfaces.get("better_loop_line") or bl.get("better_loop_line") or "",
        "best_loop_oqg_line": surfaces.get("best_loop_oqg_line") or oqg.get("best_loop_oqg_line") or "",
        "form_official_line": surfaces.get("form_official_line") or form_wire.get("form_official_line") or "",
        "critic_circle_line": (
            surfaces.get("critic_circle_line")
            or (bl.get("critic_circle") or {}).get("critic_circle_line")
            or ""
        ),
    }

    drift_score = zd.get("drift_score")
    if drift_score is None:
        try:
            drift_score = int(str(surfaces.get("zero_drift_line") or "").split("score=")[1].split()[0])
        except (IndexError, ValueError):
            drift_score = None

    ship = _ship_gates(bl=bl, oqg=oqg)
    try:
        from commercial_email_send_defer_v1 import assess as email_defer_assess  # noqa: WPS433

        defer_row = email_defer_assess(write=True)
        if defer_row.get("email_send_defer_line"):
            lines["email_send_defer_line"] = defer_row["email_send_defer_line"]
            ship["w3_email_send_deferred"] = bool(defer_row.get("defer_active"))
            ship["email_send_defer_line"] = defer_row["email_send_defer_line"]
    except Exception:
        pass
    try:
        fem = _read_json(SINA / "founder-execution-model-receipt-v1.json")
        if fem.get("line"):
            lines["founder_execution_model_line"] = fem["line"]
            ship["founder_execution_model"] = bool(fem.get("ok"))
            ship["founder_execution_model_line"] = fem["line"]
    except Exception:
        pass
    try:
        mlm = _read_json(SINA / "mac-law-mandatory-receipt-v1.json")
        if mlm.get("line"):
            lines["mac_law_mandatory_line"] = mlm["line"]
            ship["mac_law_mandatory"] = bool(mlm.get("ok"))
            ship["mac_law_mandatory_line"] = mlm["line"]
    except Exception:
        pass
    try:
        mlw = _read_json(NERVE_PATHS["mac_law_universal"])
        if mlw.get("line"):
            lines["mac_law_universal_line"] = mlw["line"]
            ship["mac_law_universal_wire"] = bool(mlw.get("ok"))
            ship["mac_law_universal_line"] = mlw["line"]
    except Exception:
        pass
    try:
        mle = _read_json(NERVE_PATHS["mac_law_machine"])
        if mle.get("line"):
            lines["mac_law_machine_line"] = mle["line"]
            ship["mac_law_machine_enforce"] = bool(mle.get("ok"))
            ship["mac_law_machine_line"] = mle["line"]
    except Exception:
        pass
    try:
        mla = _read_json(NERVE_PATHS["mac_law_agent_lock"])
        if mla.get("line"):
            lines["mac_law_agent_lock_line"] = mla["line"]
            ship["mac_law_agent_no_factory_on_mac"] = bool(mla.get("ok"))
            ship["mac_law_agent_lock_line"] = mla["line"]
        elif not NERVE_PATHS["mac_law_agent_lock"].is_file():
            sys.path.insert(0, str(SCRIPTS))
            from mac_law_agent_execution_plane_lock_v1 import sync_receipt  # noqa: WPS433

            mla = sync_receipt(enforce=False)
            lines["mac_law_agent_lock_line"] = mla.get("line") or ""
            ship["mac_law_agent_no_factory_on_mac"] = bool(mla.get("ok"))
            ship["mac_law_agent_lock_line"] = mla.get("line") or ""
    except Exception:
        ship["mac_law_agent_no_factory_on_mac"] = False
    try:
        from cloud_factories_online_only_v1 import assess as cloud_online_assess  # noqa: WPS433

        cloud_row = cloud_online_assess(write=True)
        if cloud_row.get("cloud_factories_online_line"):
            lines["cloud_factories_online_line"] = cloud_row["cloud_factories_online_line"]
            ship["cloud_factories_online_only"] = bool(cloud_row.get("ok"))
            ship["cloud_factories_online_line"] = cloud_row["cloud_factories_online_line"]
    except Exception:
        pass
    outbound_gates = _outbound_ship_gates()
    ship["worker_connected"] = outbound_gates.get("worker_connected")
    ship["outbound_coherence"] = outbound_gates.get("outbound_coherence")
    ship["execution_honesty_12of12"] = outbound_gates.get("execution_honesty_12of12")
    ship["commercial_l3_ok"] = outbound_gates.get("commercial_l3_ok")
    ship["outbound_progress_line"] = outbound_gates.get("outbound_progress_line") or ""
    ship["execution_honesty_line"] = outbound_gates.get("execution_honesty_line") or ""

    if outbound_gates.get("outbound_progress_line"):
        lines["outbound_progress_line"] = outbound_gates["outbound_progress_line"]
    if outbound_gates.get("execution_honesty_line"):
        lines["execution_honesty_line"] = outbound_gates["execution_honesty_line"]

    research = _research_root_ok()
    fleet_clean = oqg.get("fleet_output_clean_now") or oqg.get("fleet_output_clean_pct")
    waiver_n = int(ship.get("active_waiver_count") or oqg.get("active_waiver_count") or 0)

    worker_wire_ok = bool(outbound_gates.get("worker_connected"))
    coherence_ok = bool(outbound_gates.get("outbound_coherence"))
    honesty_ok = bool(outbound_gates.get("execution_honesty_12of12"))

    commercial_red_map = bl.get("commercial_red_map") or {}
    if not commercial_red_map:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from oegcc_commercial_red_map_v1 import map_commercial_reds  # noqa: WPS433

            checks = bl.get("ship_checks") or bl.get("founder_checks") or []
            commercial_red_map = map_commercial_reds(checks)
        except Exception:
            commercial_red_map = {}
    commercial_rule_ids = list(commercial_red_map.get("rule_ids") or [])

    row = {
        "schema": "agent-nerve-system-receipt-v1",
        "at": _now(),
        "law": "AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md",
        "ok": (aligned or lawful_idle)
        and bool(lines.get("factory_now_line"))
        and bool(lines.get("best_loop_oqg_line"))
        and worker_wire_ok
        and coherence_ok
        and honesty_ok
        and bool(ui_fc.get("wire_ok")),
        "worker_connected": worker_wire_ok,
        "outbound_coherence": coherence_ok,
        "execution_honesty_ok": honesty_ok,
        "queue_sa": canonical,
        "queue_exhausted": lawful_idle,
        "queue_aligned": aligned or lawful_idle,
        "alignment_issues": align_issues,
        "nerve_system_line": _nerve_line(
            queue_sa=canonical,
            aligned=aligned,
            drift_score=drift_score if isinstance(drift_score, int) else None,
            red_count=int(bl.get("red_count") or 0),
            fleet_clean=fleet_clean if isinstance(fleet_clean, int) else None,
            anti_ok=bool(anti.get("ok")),
            waiver_n=waiver_n,
            send_ready=bool(ship.get("w3_send_ready")),
            system_red_count=int(bl.get("system_red_count") or 0),
            commercial_red_count=int(bl.get("commercial_red_count") or 0),
            commercial_rule_ids=commercial_rule_ids,
            research_ok=bool(research.get("ok")),
            ui_fc_ok=bool(ui_fc.get("wire_ok")),
        )
        + (
            f" · maclaw={'PASS' if ship.get('mac_law_agent_no_factory_on_mac') else 'RED'}"
            f" · worker={'PASS' if worker_wire_ok else 'BLOCK'}"
            + (f" · {outbound_gates.get('outbound_progress_line', '')[:48]}" if outbound_gates.get("outbound_progress_line") else "")
        ),
        "research_root": research,
        "lines": lines,
        "nodes": nodes,
        "ship_gates": ship,
        "outbound_gates": outbound_gates,
        "commercial_red_map": commercial_red_map,
        "commercial_rule_ids": commercial_rule_ids,
        "better_loop": {
            "ok": bl.get("ok"),
            "red_count": bl.get("red_count"),
            "system_red_count": bl.get("system_red_count"),
            "commercial_red_count": bl.get("commercial_red_count"),
            "product_red_count": bl.get("product_red_count"),
            "weekly_lever": bl.get("weekly_lever"),
            "ship_checks": bl.get("ship_checks") or bl.get("founder_checks") or [],
            "founder_checks": bl.get("ship_checks") or bl.get("founder_checks") or [],
            "commercial_red_map": commercial_red_map,
            "critic_circle": bl.get("critic_circle") or {},
        },
        "output_quality": {
            "fleet_output_clean_pct": oqg.get("fleet_output_clean_pct"),
            "fleet_output_clean_now": oqg.get("fleet_output_clean_now"),
            "fleet_output_clean_7d": oqg.get("fleet_output_clean_7d"),
            "fleet_trust_mode": oqg.get("fleet_trust_mode"),
            "trust_mode_7d": oqg.get("fleet_trust_mode"),
            "active_waiver_count": waiver_n,
            "lanes": oqg.get("lanes") or [],
        },
        "paths": {k: str(v) for k, v in NERVE_PATHS.items()},
        "command": "python3 scripts/agent_nerve_system_v1.py --json",
    }

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "agent-nerve-system-receipt-v1":
        row = run_nerve_pulse(write=True)
    return {
        "schema": "worker-hub-nerve-system-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "nerve_system_line": row.get("nerve_system_line"),
        "queue_sa": row.get("queue_sa"),
        "queue_aligned": row.get("queue_aligned"),
        "lines": row.get("lines") or {},
        "better_loop": row.get("better_loop") or {},
        "output_quality": row.get("output_quality") or {},
        "ship_gates": row.get("ship_gates") or {},
        "alignment_issues": row.get("alignment_issues") or [],
        "law": row.get("law"),
        "command": row.get("command"),
    }


def patch_surfaces(*, row: dict | None = None) -> dict:
    """Write nerve_system_line onto agent-live-surfaces (read-only merge)."""
    surf_path = NERVE_PATHS["surfaces"]
    if row is None:
        row = run_nerve_pulse(write=True)
    surf = _read_json(surf_path)
    if not surf:
        return {"ok": False, "error": "missing surfaces"}
    surf["nerve_system_line"] = row.get("nerve_system_line")
    if row.get("lines", {}).get("email_send_defer_line"):
        surf["email_send_defer_line"] = row["lines"]["email_send_defer_line"]
    surf["nerve_system"] = {
        "receipt": str(RECEIPT),
        "law": "scripts/agent_nerve_system_v1.py",
        "queue_aligned": row.get("queue_aligned"),
        "at": row.get("at"),
    }
    for key, val in (row.get("lines") or {}).items():
        if val and not surf.get(key):
            surf[key] = val
    surf_path.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(surf_path), "nerve_system_line": row.get("nerve_system_line")}


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent nerve system unified pulse")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--patch-surfaces", action="store_true")
    ap.add_argument("--refresh-loops", action="store_true", help="Re-run better_loop pulse before nerve check")
    ap.add_argument("--check-rrl-ship-gate", action="store_true", help="U040 — w3_rrl_pass alone must not set w3_send_ready")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.check_rrl_ship_gate:
        row = validate_rrl_not_ship_ready()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_rrl_ship_gate:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    row = run_nerve_pulse(write=not args.no_write, refresh_loops=args.refresh_loops)
    if args.patch_surfaces:
        patch_surfaces(row=row)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("nerve_system_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
