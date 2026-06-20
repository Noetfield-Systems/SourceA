#!/usr/bin/env python3
"""Better Loop v2 pulse — read-only probes for four auto loops + founder check card.

Law: docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md §2 v2
Receipt: ~/.sina/better-loop-pulse-receipt-v1.json
Check cart: ~/.sina/better-loop-checkcart-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"
CHECKCART = SINA / "better-loop-checkcart-v1.json"
RECEIPT = SINA / "better-loop-pulse-receipt-v1.json"
ROUTE_YAML = Path.home() / "Desktop" / "1 PAGER" / "portfolio-300-locked" / "STACK_MAP_BETTER_LOOP_ROUTE.yaml"
PY = sys.executable

MANDATORY_LOOPS = frozenset({"governance_pulse", "product_spine", "edge_deployed", "campus_readonly"})
OQG_BAR = 90

CHECK_CLASS: dict[str, str] = {
    "hub_next_steps": "product",
    "factory_now": "system",
    "run_inbox": "product",
    "w3_sends": "commercial",
    "w3_output_clean": "commercial",
    "w3_receiver_interest": "commercial",
    "w3_conversation_interest": "commercial",
    "w3_critic_circle": "commercial",
    "w3_rrl": "commercial",
    "w3_sina_read": "commercial",
    "oegcc_linter": "commercial",
    "oegcc_controller": "commercial",
    "edge_live": "system",
}


def _loop_auto_on() -> bool:
    cfg = SINA / "loop-specialist-config-v1.json"
    if not cfg.is_file():
        return False
    try:
        return bool(json.loads(cfg.read_text(encoding="utf-8")).get("loop_auto_dispatch_enabled"))
    except (OSError, json.JSONDecodeError):
        return False


def _founder_motion_line(*, goal1_idle: bool) -> str:
    sys.path.insert(0, str(SCRIPTS))
    from execution_path_vocabulary_v1 import founder_motion_line  # noqa: WPS433

    return founder_motion_line(goal1_idle=goal1_idle)


def _tag_checks(checks: list[dict]) -> list[dict]:
    out: list[dict] = []
    for c in checks:
        row = dict(c)
        cid = str(row.get("id") or "")
        row["class"] = CHECK_CLASS.get(cid, "system")
        out.append(row)
    return out


def _red_taxonomy(checks: list[dict]) -> dict[str, int]:
    tagged = _tag_checks(checks)
    return {
        "system_red_count": sum(1 for c in tagged if not c.get("ok") and c.get("class") == "system"),
        "commercial_red_count": sum(1 for c in tagged if not c.get("ok") and c.get("class") == "commercial"),
        "product_red_count": sum(1 for c in tagged if not c.get("ok") and c.get("class") == "product"),
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


def checkcart_template() -> dict:
    return {
        "schema": "better-loop-checkcart-v1",
        "at": _now(),
        "law": "docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md",
        "phase": "POST-DESIGN",
        "duty": "Operating loop cart BL1–BL11 — not law-ship W1–W11.",
        "mandatory_after_every_pulse": [
            {
                "id": "BL1",
                "step": "LOCK doctrine v2",
                "command": "python3 scripts/save_stack_map_better_loop_locked_v1.py",
                "pass": "doc datetime validator PASS · 3 mirrors synced",
                "owner": "executor",
            },
            {
                "id": "BL2",
                "step": "Check cart SSOT",
                "command": "test -f ~/.sina/better-loop-checkcart-v1.json",
                "pass": "JSON schema + BL1–BL11 rows",
                "owner": "executor",
            },
            {
                "id": "BL3",
                "step": "Pulse engine",
                "command": "python3 scripts/better_loop_pulse_v1.py --json",
                "pass": "ok true · steps for BL4–BL9 loops",
                "owner": "executor",
            },
            {
                "id": "BL4",
                "step": "Pulse receipt",
                "command": "test -f ~/.sina/better-loop-pulse-receipt-v1.json",
                "pass": "receipt ok when mandatory loops green",
                "owner": "executor",
            },
            {
                "id": "BL5",
                "step": "Live wire line",
                "command": "grep better_loop_line ~/.sina/agent-live-surfaces-v1.json",
                "pass": "better_loop_line on agent-live-surfaces",
                "owner": "executor",
            },
            {
                "id": "BL6",
                "step": "Session gate inject",
                "command": "python3 scripts/agent_session_gate_run_v1.py --role any --json",
                "pass": "gate receipt includes better_loop step",
                "owner": "executor",
            },
            {
                "id": "BL7",
                "step": "Hub founder card",
                "command": "python3 scripts/worker_hub_v1.py --json",
                "pass": "better_loop slice with checks + weekly_lever",
                "owner": "executor",
            },
            {
                "id": "BL8",
                "step": "Commercial loop wire",
                "command": "python3 scripts/better_loop_pulse_v1.py --json (commercial_flywheel)",
                "pass": "W3 approvals · approved_not_sent surfaced",
                "owner": "commercial",
            },
            {
                "id": "BL9",
                "step": "Factory loop wire",
                "command": "python3 scripts/better_loop_pulse_v1.py --json (factory_execution)",
                "pass": "FBE bundle + Fly receipt read-only",
                "owner": "worker",
            },
            {
                "id": "BL10",
                "step": "Validator + bundle",
                "command": "bash scripts/validate-better-loop-v1.sh",
                "pass": "receipt fresh (<24h)",
                "owner": "executor",
            },
            {
                "id": "BL11",
                "step": "Ship wire W1–W10",
                "command": "agent-law-wire-checkcart W1–W10 on v2 lock",
                "pass": "cross-refs + route YAML bump",
                "owner": "executor",
            },
            {
                "id": "BQ1",
                "step": "OQG score receipt",
                "command": "python3 scripts/best_loop_oqg_score_v1.py --json",
                "pass": "receipt + per-lane output_clean_pct",
                "owner": "executor",
            },
            {
                "id": "BQ2",
                "step": "W3 send OQG gate",
                "command": "python3 scripts/send_w3_canada_v1.py ocree --pack-only",
                "pass": "blocks <90 without waiver · stamps pack",
                "owner": "commercial",
            },
            {
                "id": "BQ3",
                "step": "Hub OQG + nerve slices",
                "command": "python3 scripts/worker_hub_v1.py --json",
                "pass": "nerve_system + best_loop_oqg fields present",
                "owner": "executor",
            },
            {
                "id": "BQ4",
                "step": "Trust mode 7d",
                "command": "python3 scripts/best_loop_oqg_score_v1.py --json",
                "pass": "fleet_output_clean_7d + trust_mode_7d on lanes",
                "owner": "executor",
            },
            {
                "id": "BQ5",
                "step": "Fleet OQG bar",
                "command": "python3 scripts/best_loop_oqg_score_v1.py --json",
                "pass": "fleet_output_clean_pct tracked · bar=90",
                "owner": "executor",
            },
            {
                "id": "NS1",
                "step": "Nerve pulse",
                "command": "python3 scripts/agent_nerve_system_v1.py --json",
                "pass": "queue_aligned + nerve_system_line",
                "owner": "executor",
            },
            {
                "id": "NS2",
                "step": "Nerve validator",
                "command": "bash scripts/validate-agent-nerve-system-v1.sh",
                "pass": "PASS",
                "owner": "executor",
            },
            {
                "id": "CC1",
                "step": "Factory output critic circle",
                "command": "python3 scripts/factory_output_critic_circle_v1.py --json",
                "pass": "verdict PASS or IMPROVE with next_action_only",
                "owner": "critic",
            },
            {
                "id": "CC2",
                "step": "Sina read bundle",
                "command": "python3 scripts/w3_founder_review_v1.py --show",
                "pass": "sina_read_score_pct on each artifact or PENDING flagged",
                "owner": "Sina",
            },
            {
                "id": "CC3",
                "step": "FEFS persuasion split",
                "command": "python3 scripts/best_loop_oqg_score_v1.py --w3-only --json",
                "pass": "structural_pct + persuasion_fefs_pct on W3",
                "owner": "executor",
            },
            {
                "id": "CC4",
                "step": "Critic learn log",
                "command": "test -f ~/.sina/factory-output-critic-incidents-v1.jsonl || true",
                "pass": "incidents append on IMPROVE turns",
                "owner": "critic",
            },
            {
                "id": "CC5",
                "step": "Critic loop law",
                "command": "test -f docs/SOURCEA_FACTORY_OUTPUT_CRITIC_LOOP_LOCKED_v1.md",
                "pass": "LOCKED doc datetime PASS",
                "owner": "executor",
            },
            {
                "id": "RIL1",
                "step": "Receiver interest loop",
                "command": "python3 scripts/receiver_interest_loop_v1.py --json",
                "pass": "receiver_interest_pct ≥90 per W3 artifact",
                "owner": "critic",
            },
            {
                "id": "RIL2",
                "step": "Interest asset SSOT",
                "command": "test -f data/w3-receiver-interest-assets-v1.json",
                "pass": "per-account demo/catalog URLs",
                "owner": "executor",
            },
            {
                "id": "RIL3",
                "step": "RIL loop law",
                "command": "test -f docs/SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md",
                "pass": "LOCKED doc datetime PASS",
                "owner": "executor",
            },
            {
                "id": "CIL1",
                "step": "Conversation interest loop",
                "command": "python3 scripts/conversation_interest_loop_v1.py --json",
                "pass": "conversation_interest_pct ≥92 per W3 artifact",
                "owner": "critic",
            },
            {
                "id": "OEGCC1",
                "step": "Outbound email linter (OEGCC step 1)",
                "command": "bash scripts/validate-outbound-email-linter-v1.sh",
                "pass": "structured failures · warn@100 · fail@140",
                "owner": "commercial",
            },
            {
                "id": "OEGCC2",
                "step": "Outbound email controller loop (OEGCC step 2–3)",
                "command": "bash scripts/validate-outbound-email-controller-loop-v1.sh",
                "pass": "bounded loop · oscillation · human_queue exit",
                "owner": "commercial",
            },
            {
                "id": "CIL2",
                "step": "Email translation SSOT",
                "command": "test -f data/factory-email-translation-v1.json",
                "pass": "hard fails + translation map logged",
                "owner": "executor",
            },
            {
                "id": "CIL3",
                "step": "Factory v2 spec + vocabulary",
                "command": "test -f data/founder-email-factory-v2-machine-v1.json && test -f data/sourcea-forge-vocabulary-disambiguation-v1.json",
                "pass": "machine SSOT mirrors LOCKED docs · Forge disambiguation logged",
                "owner": "executor",
            },
            {
                "id": "RRL1",
                "step": "Response Reality Layer",
                "command": "python3 scripts/response_reality_layer_v1.py --account ocree --json",
                "pass": "reaction D or E only",
                "owner": "critic",
            },
            {
                "id": "RRL2",
                "step": "RRL SSOT",
                "command": "test -f data/response-reality-layer-v1.json",
                "pass": "RRL law in repository",
                "owner": "executor",
            },
            {
                "id": "V1",
                "step": "Forge vocabulary disambiguation",
                "command": "bash scripts/validate-forge-vocabulary-disambiguation-v1.sh",
                "pass": "Forge = product only · no stale icp-forge paths",
                "owner": "executor",
            },
            {
                "id": "APC1",
                "step": "Advisor pre-call loop",
                "command": "python3 scripts/advisor_pre_call_email_loop_v1.py --json",
                "pass": "human_clarity_pct ≥90 on canonical example",
                "owner": "executor",
            },
            {
                "id": "APC2",
                "step": "Advisor pre-call SSOT",
                "command": "test -f data/advisor-pre-call-email-v1.json && test -f data/advisor-pre-call-examples/richard-alberta-v2.txt",
                "pass": "v2 rules + send-grade Richard compile",
                "owner": "executor",
            },
            {
                "id": "APC3",
                "step": "Advisor pre-call law",
                "command": "test -f docs/SOURCEA_ADVISOR_PRE_CALL_EMAIL_STANDARD_LOCKED_v1.md",
                "pass": "LOCKED doc datetime PASS",
                "owner": "executor",
            },
        ],
    }


def merge_checkcart_rows() -> None:
    """Append BQ/NS rows to live cart when template grows."""
    template = checkcart_template()
    tpl_ids = {r["id"] for r in template.get("mandatory_after_every_pulse") or []}
    if not CHECKCART.is_file():
        ensure_checkcart()
        return
    live = _read_json(CHECKCART)
    live_ids = {r.get("id") for r in live.get("mandatory_after_every_pulse") or []}
    missing = [r for r in template.get("mandatory_after_every_pulse") or [] if r["id"] not in live_ids]
    if missing:
        live.setdefault("mandatory_after_every_pulse", []).extend(missing)
        live["at"] = _now()
        live["phase"] = template.get("phase")
        CHECKCART.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")


def ensure_checkcart() -> Path:
    SINA.mkdir(parents=True, exist_ok=True)
    if not CHECKCART.is_file():
        CHECKCART.write_text(json.dumps(checkcart_template(), indent=2) + "\n", encoding="utf-8")
    else:
        merge_checkcart_rows()
    return CHECKCART


def _weekly_lever() -> str:
    if ROUTE_YAML.is_file():
        text = ROUTE_YAML.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("weekly_lever:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'") or "money"
    return "money"


def _probe_governance() -> dict:
    gate = _read_json(SINA / "agent_session_gate_receipt_v1.json")
    cart = _read_json(SINA / "governance-gate-cart-v1.json")
    surfaces = _read_json(SINA / "agent-live-surfaces-v1.json")
    zero = _read_json(SINA / "governance-zero-drift-live-wire-v1.json")
    # Core structural gates — exclude execution, commercial, optional pipelines (F050)
    _STRUCTURAL_OK = frozenset(
        {"brain_ssot", "cascade", "zero_drift", "sascip", "nerve", "zero_drift_wire"}
    )
    drift_items = zero.get("drift_items")
    drift_ok = drift_items in (0, "0", None) or (isinstance(drift_items, int) and drift_items == 0)
    zero_live_ok = bool(zero.get("ok")) and drift_ok
    cart_gates = cart.get("gates") or []
    if cart_gates:
        structural = [g for g in cart_gates if g.get("id") in _STRUCTURAL_OK and g.get("id") != "zero_drift"]
        gate_ok = bool(structural) and all(g.get("ok") for g in structural) and zero_live_ok
    else:
        gate_ok = gate.get("ok") is True and zero_live_ok
    queue_ok = True
    queue_detail = "cached"
    try:
        out = subprocess.check_output(
            [PY, str(SCRIPTS / "queue_ssot_unify_v1.py"), "--json"],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(ROOT),
            timeout=30,
        )
        q = json.loads(out[out.find("{") :])
        head_ok = bool(((q.get("steps") or {}).get("head") or {}).get("ok"))
        queue_ok = bool(q.get("ok")) and head_ok
        queue_detail = f"ok={q.get('ok')} head={head_ok}"
    except (subprocess.SubprocessError, json.JSONDecodeError, ValueError) as exc:
        queue_ok = False
        queue_detail = str(exc)[:120]
    ok = gate_ok and queue_ok and zero_live_ok
    return {
        "id": "governance_pulse",
        "loop": "governance",
        "ok": ok,
        "pass": ok,
        "detail": f"gate={gate_ok} queue={queue_detail} drift_items={drift_items}",
        "factory_now_line": (surfaces.get("factory_now_line") or "")[:96],
    }


def _probe_product() -> dict:
    fn = _read_json(SINA / "factory-now-v1.json")
    inbox = _read_json(SINA / "worker-prompt-inbox-v1.json")
    sa = str(fn.get("queue_sa") or (inbox.get("meta") or {}).get("sa_id") or "")
    valid = fn.get("valid_yes")
    backlog = fn.get("backlog")
    mode = str(fn.get("mode") or "")
    goal1_complete = (
        int(valid or 0) >= 1000
        and int(backlog if backlog is not None else 0) == 0
        and bool(fn.get("dual_proof_ok"))
    )
    ok = goal1_complete or (bool(sa) and sa not in ("—", "-", "unknown") and mode not in ("FREEZE",))
    if valid is not None and valid not in (True, "YES", "yes", 999) and not goal1_complete:
        ok = ok and bool(valid)
    return {
        "id": "product_spine",
        "loop": "product",
        "ok": ok,
        "pass": ok,
        "detail": f"queue_sa={sa or '?'} mode={mode} valid_yes={valid} backlog={backlog}",
        "queue_sa": sa,
    }


def _pipeline_slot_cleared(acct: dict) -> bool:
    slot = str(acct.get("pipeline_send_slot") or acct.get("hub_approve_slot") or "")
    return slot in ("cleared", "approved")


def _probe_commercial() -> dict:
    w3 = _read_json(ROOT / "data" / "commercial" / "w3-canada-send-approvals-v1.json")
    accounts = w3.get("accounts") or []
    pending = [
        a
        for a in accounts
        if _pipeline_slot_cleared(a)
        and not a.get("sent_at")
        and not a.get("sent")
    ]
    ids = [str(a.get("id") or a.get("company") or "?") for a in pending]
    # Commercial loop runs; W1 lever = sends still pending is expected red on founder card
    ok = w3.get("schema") == "w3-canada-send-approvals-v1" and bool(accounts)
    return {
        "id": "commercial_flywheel",
        "loop": "commercial",
        "ok": ok,
        "pass": ok,
        "detail": f"approved_not_sent={len(pending)} ids={','.join(ids) if ids else 'none'}",
        "approved_not_sent": ids,
        "approved_not_sent_count": len(pending),
    }


def _probe_factory() -> dict:
    bundle = _read_json(ROOT / "data" / "fbe_factory_builder_bundle_v1.json")
    fly = _read_json(SINA / "fbe-fly-deploy-receipt-v1.json")
    blocked = str(fly.get("blocked") or fly.get("status") or "")
    fly_ok = fly.get("ok") is True or fly.get("deployed") is True
    fly_pending_billing = "billing" in blocked.lower() or fly.get("blocked") == "fly_billing_required"
    bundle_ok = bundle.get("schema") in ("fbe-factory-builder-bundle-v1", None) or bool(bundle.get("wave"))
    ok = bundle_ok
    return {
        "id": "factory_execution",
        "loop": "factory",
        "ok": ok,
        "pass": ok,
        "detail": f"bundle={'yes' if bundle_ok else 'no'} fly={'live' if fly_ok else blocked or 'pending'}",
        "fly_pending_billing": fly_pending_billing,
        "fly_blocked": blocked or None,
    }


def _probe_edge() -> dict:
    proxy = Path.home() / "Desktop" / "Noetfield" / "Noetfield-All-Documents" / "Noetfield" / "infra" / "cf-www-proxy"
    aeg = SCRIPTS / "host_aeg_bundle_v1.py"
    proxy_ok = (proxy / "wrangler.toml").is_file() and (proxy / "src" / "worker.js").is_file()
    aeg_ok = aeg.is_file()
    ok = proxy_ok and aeg_ok
    return {
        "id": "edge_deployed",
        "loop": "edge",
        "ok": ok,
        "pass": ok,
        "detail": f"www_proxy={proxy_ok} aeg_script={aeg_ok}",
    }


def _probe_campus() -> dict:
    ok = True
    return {
        "id": "campus_readonly",
        "loop": "campus",
        "ok": ok,
        "pass": ok,
        "detail": "PLUS_ONE read-only import — Mac control plane only",
    }


def _probe_oqg() -> dict:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from best_loop_oqg_score_v1 import run_oqg  # noqa: WPS433

        return run_oqg(write=True)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "best-loop-oqg-receipt-v1"}


def _w3_ship_quality_checks() -> list[dict]:
    """Critic · CIL · RIL · Sina read — separate from machine OQG."""
    review = _read_json(SINA / "w3-founder-review-v1.json")
    critic = _read_json(SINA / "factory-output-critic-circle-receipt-v1.json")
    ril = _read_json(SINA / "receiver-interest-loop-receipt-v1.json")
    cil = _read_json(SINA / "conversation-interest-loop-receipt-v1.json")
    rrl = _read_json(SINA / "response-reality-layer-receipt-v1.json")
    arts = review.get("artifacts") or []

    def _artifact_sent(art: dict) -> bool:
        return str(art.get("status") or "") == "sent" or bool(art.get("confirm_sent_at") or art.get("sent_at"))

    active_arts = [a for a in arts if not _artifact_sent(a)]
    pending = [
        a
        for a in active_arts
        if (a.get("scores") or {}).get("sina_read_pending")
        or (a.get("scores") or {}).get("founder_score_pending")
    ]
    low_sina = [
        a
        for a in active_arts
        if (a.get("scores") or {}).get("sina_read_score_pct") is not None
        and int((a.get("scores") or {}).get("sina_read_score_pct") or 0) < 90
    ]
    if not low_sina:
        low_sina = [
            a
            for a in arts
            if (a.get("scores") or {}).get("founder_score_pct") is not None
            and int((a.get("scores") or {}).get("founder_score_pct") or 0) < 90
        ]
    w3_improve = [
        a
        for a in (critic.get("artifacts") or [])
        if a.get("lane") == "w3_commercial"
        and int(a.get("machine_oqg_pct") or 0) < OQG_BAR
    ]
    ril_improve = [a for a in (ril.get("artifacts") or []) if a.get("verdict") == "IMPROVE"]
    cil_improve = [a for a in (cil.get("artifacts") or []) if a.get("verdict") == "IMPROVE"]
    return [
        {
            "id": "w3_receiver_interest",
            "label": "W3 · receiver interest ≥90%",
            "ok": not ril_improve and ril.get("schema") == "receiver-interest-loop-receipt-v1",
            "detail": ril.get("next_action_only") or ril.get("receiver_interest_line") or "run receiver_interest_loop_v1.py",
        },
        {
            "id": "w3_conversation_interest",
            "label": "W3 · conversation interest ≥92%",
            "ok": not cil_improve and cil.get("schema") == "conversation-interest-loop-receipt-v1",
            "detail": cil.get("next_action_only") or cil.get("conversation_interest_line") or "run conversation_interest_loop_v1.py",
        },
        {
            "id": "w3_critic_circle",
            "label": "W3 · critic circle PASS",
            "ok": not w3_improve and critic.get("schema") == "factory-output-critic-circle-receipt-v1",
            "detail": critic.get("next_action_only") or critic.get("critic_circle_line") or "run factory_output_critic_circle_v1.py",
        },
        {
            "id": "w3_rrl",
            "label": "W3 · RRL reaction D/E",
            "ok": bool(rrl.get("ok")) and rrl.get("schema") == "response-reality-layer-receipt-v1",
            "detail": rrl.get("next_action_only") or rrl.get("rrl_line") or "run response_reality_layer_v1.py --account ocree --json",
        },
        {
            "id": "w3_sina_read",
            "label": "W3 · Sina read ≥90%",
            "ok": not pending and not low_sina,
            "detail": (
                f"pending={len(pending)} below90={len(low_sina)}"
                if (pending or low_sina)
                else "Sina read scores meet bar"
            ),
        },
    ]


def _w3_founder_send_loop_checks(*, quality: list[dict], w3_oqg: dict, comm: dict) -> list[dict]:
    """L3 founder-owned gates — Mail FROM + composite send-ready."""
    qmap = {c["id"]: c for c in quality}
    mail_from_ok = False
    mail_configured: list[str] = []
    try:
        from commercial_mail_draft_v1 import mail_configured_addresses  # noqa: WPS433

        mail_configured = mail_configured_addresses()
        need = {"hello@trustfield.ca", "operation@noetfield.com"}
        mail_from_ok = need.issubset({a.lower() for a in mail_configured})
    except Exception:
        pass
    pipeline_cleared = int(comm.get("approved_not_sent_count") or 0) == 0
    email_send_deferred = True
    email_defer_line = ""
    try:
        from commercial_email_send_defer_v1 import assess as email_defer_assess  # noqa: WPS433

        defer_row = email_defer_assess(write=False)
        email_send_deferred = bool(defer_row.get("defer_active"))
        email_defer_line = str(defer_row.get("email_send_defer_line") or "")
    except Exception:
        pass
    cloud_factories_online_ok = False
    cloud_factories_online_line = ""
    try:
        from cloud_factories_online_only_v1 import assess as cloud_online_assess  # noqa: WPS433

        cloud_row = cloud_online_assess(write=False)
        cloud_factories_online_ok = bool(cloud_row.get("ok"))
        cloud_factories_online_line = str(cloud_row.get("cloud_factories_online_line") or "")
    except Exception:
        pass
    from agent_nerve_system_v1 import _compute_w3_send_ready  # noqa: WPS433

    send_ready = _compute_w3_send_ready(
        w3_oqg_pass=bool(w3_oqg.get("oqg_pass")),
        w3_critic_pass=bool(qmap.get("w3_critic_circle", {}).get("ok")),
        w3_receiver_interest_pass=bool(qmap.get("w3_receiver_interest", {}).get("ok")),
        w3_conversation_interest_pass=bool(qmap.get("w3_conversation_interest", {}).get("ok")),
        w3_rrl_pass=bool(qmap.get("w3_rrl", {}).get("ok")),
        w3_sina_read_pass=bool(qmap.get("w3_sina_read", {}).get("ok")),
        mail_from_ok=mail_from_ok,
        pipeline_cleared_not_sent=pipeline_cleared,
        email_send_deferred=email_send_deferred,
    )
    return [
        {
            "id": "cloud_factories_online_only",
            "label": "Factories ONLINE cloud+API only — Mac never factory",
            "ok": cloud_factories_online_ok,
            "detail": cloud_factories_online_line or "cloud factory gate",
        },
        {
            "id": "w3_email_send_defer",
            "label": "W3 · email deferred until main cloud factories online",
            "ok": not email_send_deferred,
            "detail": email_defer_line or ("defer ON" if email_send_deferred else "defer lifted"),
        },
        {
            "id": "w3_mail_from",
            "label": "W3 · Mail FROM configured (founder)",
            "ok": mail_from_ok,
            "detail": ", ".join(mail_configured[:4]) if mail_configured else "configure Mail.app FROM accounts",
        },
        {
            "id": "w3_send_ready",
            "label": "W3 · send-ready composite",
            "ok": send_ready,
            "detail": "founder Mail FROM + Sina read + pipeline cleared" if send_ready else "founder send loop incomplete",
        },
    ]


def _probe_oegcc_linter() -> dict:
    """OEGCC step 1 — deterministic linter script + fixture smoke."""
    script = SCRIPTS / "outbound_email_linter_v1.py"
    fixture = SCRIPTS / "fixtures/outbound-email-linter/pass.txt"
    if not script.is_file() or not fixture.is_file():
        return {"ok": False, "detail": "missing linter script or fixture"}
    try:
        out = subprocess.check_output(
            [PY, str(script), "--body-file", str(fixture), "--json"],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(ROOT),
            timeout=20,
        )
        row = json.loads(out[out.find("{") :])
        ok = bool(row.get("ok"))
        failure_ids = sorted(
            str(f.get("id") or "")
            for f in row.get("failures") or []
            if f.get("id") and str(f.get("severity") or "fail") == "fail"
        )
        return {
            "ok": ok,
            "detail": row.get("line") or ("PASS" if ok else "FAIL"),
            "failures": len(row.get("failures") or []),
            "failure_ids": failure_ids,
        }
    except (subprocess.SubprocessError, json.JSONDecodeError, ValueError) as exc:
        return {"ok": False, "detail": str(exc)[:120], "failure_ids": []}


def _probe_oegcc_controller() -> dict:
    """OEGCC step 2–3 — controller receipt or simulate."""
    sys.path.insert(0, str(SCRIPTS))
    try:
        from oegcc_commercial_red_map_v1 import probe_oegcc_controller  # noqa: WPS433

        return probe_oegcc_controller(simulate=False)
    except Exception as exc:
        return {"ok": False, "detail": str(exc)[:120], "line": "oegcc-controller · probe error"}


def _ship_checks(loops: list[dict], *, oqg: dict | None = None) -> list[dict]:
    by_id = {r["id"]: r for r in loops}
    gov = by_id.get("governance_pulse") or {}
    prod = by_id.get("product_spine") or {}
    comm = by_id.get("commercial_flywheel") or {}
    edge = by_id.get("edge_deployed") or {}
    w3_oqg = {}
    if oqg:
        for lane in oqg.get("lanes") or []:
            if lane.get("lane") == "w3_commercial":
                w3_oqg = lane
                break
    next_steps = _read_json(SINA / "live-ongoing-prompts-next-10-v1.json")
    has_row = bool((next_steps.get("items") or next_steps.get("next") or [])[:1])
    fn_idle = _read_json(SINA / "factory-now-v1.json")
    goal1_idle = (
        int(fn_idle.get("valid_yes") or 0) >= 1000
        and int(fn_idle.get("backlog") or 0) == 0
        and bool(fn_idle.get("dual_proof_ok"))
        and not str(fn_idle.get("queue_sa") or "").strip()
    )
    sys.path.insert(0, str(SCRIPTS))
    from execution_path_vocabulary_v1 import run_inbox_check_label  # noqa: WPS433

    run_inbox_label = run_inbox_check_label()
    oegcc = _probe_oegcc_linter()
    oegcc_ctrl = _probe_oegcc_controller()
    quality = _w3_ship_quality_checks()
    founder = _w3_founder_send_loop_checks(quality=quality, w3_oqg=w3_oqg, comm=comm)
    checks = [
        {
            "id": "hub_next_steps",
            "label": "Worker Hub → Next steps",
            "ok": has_row or bool(prod.get("queue_sa")) or goal1_idle,
            "detail": "Goal 1 idle" if goal1_idle and not has_row else ("one clear row" if has_row else "queue_sa from factory-now"),
        },
        {
            "id": "factory_now",
            "label": "factory-now Valid YES · drift 0",
            "ok": bool(gov.get("ok")),
            "detail": gov.get("detail", ""),
        },
        {
            "id": "run_inbox",
            "label": run_inbox_label,
            "ok": bool(prod.get("ok")),
            "detail": prod.get("detail", ""),
        },
        {
            "id": "w3_sends",
            "label": "W3 · no stuck approved_not_sent",
            "ok": int(comm.get("approved_not_sent_count") or 0) == 0,
            "detail": comm.get("detail", ""),
        },
        {
            "id": "w3_output_clean",
            "label": "W3 · machine output_clean ≥90%",
            "ok": bool(w3_oqg.get("oqg_pass")),
            "detail": (
                f"output_clean={w3_oqg.get('output_clean_pct', '?')}% bar=90"
                if w3_oqg
                else "oqg not scored"
            ),
        },
        *quality,
        *founder,
        {
            "id": "oegcc_linter",
            "label": "OEGCC · outbound email linter smoke",
            "ok": bool(oegcc.get("ok")),
            "detail": oegcc.get("detail", ""),
            "failure_ids": oegcc.get("failure_ids") or [],
        },
        {
            "id": "oegcc_controller",
            "label": "OEGCC · controller loop receipt",
            "ok": bool(oegcc_ctrl.get("ok")),
            "detail": oegcc_ctrl.get("line") or oegcc_ctrl.get("detail", ""),
            "rule_histogram": oegcc_ctrl.get("rule_histogram") or {},
        },
        {
            "id": "edge_live",
            "label": "Edge · www proxy + AEG proof",
            "ok": bool(edge.get("ok")),
            "detail": edge.get("detail", ""),
        },
    ]
    return checks


def _better_loop_line(
    checks: list[dict],
    red: int,
    weekly: str,
    *,
    oqg: dict | None = None,
    goal1_idle: bool = False,
    taxonomy: dict | None = None,
) -> str:
    tax = taxonomy or _red_taxonomy(checks)
    sys_red = int(tax.get("system_red_count") or 0)
    comm_red = int(tax.get("commercial_red_count") or 0)
    if red == 0:
        status = "green"
    elif comm_red and not sys_red:
        status = f"{comm_red} commercial"
    elif sys_red or comm_red:
        status = f"{sys_red} sys · {comm_red} commercial"
    else:
        status = f"{red} red"
    w3_bit = ""
    if oqg:
        w3 = next(
            (l for l in (oqg.get("lanes") or []) if l.get("lane") == "w3_commercial"),
            {},
        )
        pct = w3.get("output_clean_pct")
        if pct is not None:
            w3_bit = f" · W3 clean={pct}%"
    action = _founder_motion_line(goal1_idle=goal1_idle)
    return f"better-loop · {status} · lever={weekly}{w3_bit} · {action}"


def run_pulse(*, write: bool = True) -> dict:
    ensure_checkcart()
    loops = [
        _probe_governance(),
        _probe_product(),
        _probe_commercial(),
        _probe_factory(),
        _probe_edge(),
        _probe_campus(),
    ]
    oqg = _probe_oqg()
    critic_row: dict = {}
    try:
        sys.path.insert(0, str(SCRIPTS))
        from factory_output_critic_circle_v1 import run_critic  # noqa: WPS433

        critic_row = run_critic(write=True)
    except Exception as exc:
        critic_row = {"ok": False, "error": str(exc), "schema": "factory-output-critic-circle-receipt-v1"}
    ril_row: dict = {}
    try:
        from receiver_interest_loop_v1 import run_ril  # noqa: WPS433

        ril_row = run_ril(write=True)
    except Exception as exc:
        ril_row = {"ok": False, "error": str(exc), "schema": "receiver-interest-loop-receipt-v1"}
    cil_row: dict = {}
    try:
        from conversation_interest_loop_v1 import run_cil  # noqa: WPS433

        cil_row = run_cil(write=True)
    except Exception as exc:
        cil_row = {"ok": False, "error": str(exc), "schema": "conversation-interest-loop-receipt-v1"}
    checks = _ship_checks(loops, oqg=oqg)
    checks = _tag_checks(checks)
    red = sum(1 for c in checks if not c.get("ok"))
    taxonomy = _red_taxonomy(checks)
    commercial_red_map: dict = {}
    try:
        from oegcc_commercial_red_map_v1 import map_commercial_reds  # noqa: WPS433

        oegcc_probe = next((c for c in checks if c.get("id") == "oegcc_linter"), {})
        ctrl_probe = next((c for c in checks if c.get("id") == "oegcc_controller"), {})
        commercial_red_map = map_commercial_reds(
            checks,
            oegcc_probe=oegcc_probe,
            controller_probe=ctrl_probe,
        )
    except Exception:
        commercial_red_map = {}
    weekly = _weekly_lever()
    fn_idle = _read_json(SINA / "factory-now-v1.json")
    goal1_idle = (
        int(fn_idle.get("valid_yes") or 0) >= 1000
        and int(fn_idle.get("backlog") or 0) == 0
        and bool(fn_idle.get("dual_proof_ok"))
        and not str(fn_idle.get("queue_sa") or "").strip()
    )
    mandatory_ok = all(r.get("ok") for r in loops if r["id"] in MANDATORY_LOOPS)
    row = {
        "schema": "better-loop-pulse-receipt-v1",
        "ok": mandatory_ok,
        "at": _now(),
        "version": "v2",
        "phase": "POST-DESIGN",
        "weekly_lever": weekly,
        "goal1_idle": goal1_idle,
        "loops": loops,
        "output_quality": oqg,
        "best_loop_oqg_line": oqg.get("best_loop_oqg_line", ""),
        "critic_circle": {
            "verdict": critic_row.get("verdict"),
            "critic_circle_line": critic_row.get("critic_circle_line"),
            "next_action_only": critic_row.get("next_action_only"),
            "summary": critic_row.get("summary"),
        },
        "receiver_interest": {
            "verdict": ril_row.get("verdict"),
            "receiver_interest_line": ril_row.get("receiver_interest_line"),
            "next_action_only": ril_row.get("next_action_only"),
            "receiver_interest_avg_pct": ril_row.get("receiver_interest_avg_pct"),
            "summary": ril_row.get("summary"),
        },
        "conversation_interest": {
            "verdict": cil_row.get("verdict"),
            "conversation_interest_line": cil_row.get("conversation_interest_line"),
            "next_action_only": cil_row.get("next_action_only"),
            "conversation_interest_avg_pct": cil_row.get("conversation_interest_avg_pct"),
            "summary": cil_row.get("summary"),
        },
        "ship_checks": checks,
        "founder_checks": checks,
        "commercial_red_map": commercial_red_map,
        "red_count": red,
        **taxonomy,
        "better_loop_line": _better_loop_line(
            checks, red, weekly, oqg=oqg, goal1_idle=goal1_idle, taxonomy=taxonomy
        ),
        "outbound_salvage": {
            "upgrade": "U085",
            "spec_path": "data/outbound-factory-salvage-spec-v1.json",
            "human_doc": "docs/SOURCEA_OUTBOUND_FACTORY_SALVAGE_SPEC_LOCKED_v1.md",
        },
        "checkcart": str(CHECKCART),
        "authority": "docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice(*, refresh: bool = False) -> dict:
    receipt = _read_json(RECEIPT)
    if refresh or not receipt or receipt.get("schema") != "better-loop-pulse-receipt-v1":
        receipt = run_pulse(write=True)
    checks = receipt.get("ship_checks") or receipt.get("founder_checks") or []
    oqg = receipt.get("output_quality") or {}
    return {
        "schema": "worker-hub-better-loop-v1",
        "ok": receipt.get("ok"),
        "at": receipt.get("at"),
        "red_count": receipt.get("red_count", 0),
        "system_red_count": receipt.get("system_red_count", 0),
        "commercial_red_count": receipt.get("commercial_red_count", 0),
        "product_red_count": receipt.get("product_red_count", 0),
        "weekly_lever": receipt.get("weekly_lever", "money"),
        "better_loop_line": receipt.get("better_loop_line", ""),
        "best_loop_oqg_line": receipt.get("best_loop_oqg_line") or oqg.get("best_loop_oqg_line", ""),
        "output_quality": oqg,
        "checks": checks,
        "loops": receipt.get("loops") or [],
        "law": "docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md",
        "oqg_law": "docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md",
        "pulse_command": "python3 scripts/better_loop_pulse_v1.py --json",
        "oqg_command": "python3 scripts/best_loop_oqg_score_v1.py --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Better Loop v2 pulse")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--init-cart", action="store_true", help="Write check cart SSOT only")
    ap.add_argument("--hub-slice", action="store_true", help="Hub JSON slice only")
    ap.add_argument("--refresh", action="store_true", help="Force re-probe")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.init_cart:
        path = ensure_checkcart()
        print(json.dumps({"ok": True, "path": str(path)}, indent=2))
        return 0
    if args.hub_slice:
        row = hub_slice(refresh=args.refresh)
        print(json.dumps(row, indent=2))
        return 0 if row.get("ok") else 1
    row = run_pulse(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"BETTER_LOOP ok={row['ok']} red={row['red_count']} line={row['better_loop_line']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
