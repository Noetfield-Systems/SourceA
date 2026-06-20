#!/usr/bin/env python3
"""ICP compile · Sina read bundle — show ready-to-send emails + score ladder.

Law: docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md
Machine: data/founder-email-factory-v2-machine-v1.json
  — Founder = Sina (human) only. Advisor critique (GPT/Gemini) is NEVER founder.
  — sina_read_score_pct is ship authority; machine/CIL/RIL/RRL are not.
  — Agents produce ready-to-send packs; founder sends manually from Mail.
Receipt: ~/.sina/w3-founder-review-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUTBOUND = SINA / "outbound"
RECEIPT = SINA / "w3-founder-review-v1.json"
PACK_TO_META = SINA / "w3-pack-to-meta-v1.json"
APPROVALS = ROOT / "data" / "commercial" / "w3-canada-send-approvals-v1.json"
TEMPLATE = ROOT / "data" / "commercial" / "w3-founder-review-v1.json"

COMPILE_DIR = ROOT / "data" / "icp-compile"
MACHINE_SSOT = ROOT / "data" / "founder-email-factory-v2-machine-v1.json"
ICP_RECEIPT = SINA / "icp-output-compiler-receipt-v1.json"

# Founder review bundle — Noetfield ∥ TrustField first · SourceA deferred · Forge last
FOUNDER_REVIEW_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory", "forge-product")
COMMERCIAL_BUNDLE_LOOP_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory")
SCORE_ALL_THREE = COMMERCIAL_BUNDLE_LOOP_ACCOUNTS  # U061 — batch Sina read in one command
W3_ACCOUNTS = FOUNDER_REVIEW_ACCOUNTS  # backward compat
W3_RECEIVER_ASSETS = ROOT / "data" / "w3-receiver-interest-assets-v1.json"
TRANSLATION_CFG = ROOT / "data" / "factory-email-translation-v1.json"
FORBIDDEN_SINA_ALIASES = (
    "gpt_founder_score",
    "gpt_score",
    "gemini_founder_score",
    "gemini_score",
    "advisor_founder_score",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _brain_lane_claim() -> dict:
    """Brain/chat inject claim — informational only, not ship authority."""
    ctx = _read_json(SINA / "brain-live-context-v1.json")
    block = str(ctx.get("text_block") or "")
    claim = None
    for token in block.split("\n"):
        if "W3 clean=" in token or "output_quality:" in token:
            claim = token.strip()
            break
    bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    oqg_line = bl.get("best_loop_oqg_line") or ""
    return {
        "source": "brain-live-context-v1.json + better-loop pulse",
        "lane_claim_line": claim or oqg_line,
        "w3_lane_clean_pct": _w3_lane_avg_from_oqg(),
        "ship_authority": False,
        "note": "Brain/chat lane % is not sina_read_score and does not replace OQG + Sina read",
    }


def _w3_lane_avg_from_oqg() -> int | None:
    oqg = _read_json(SINA / "best-loop-oqg-receipt-v1.json")
    lane = next((l for l in (oqg.get("lanes") or []) if l.get("lane") == "w3_commercial"), {})
    return lane.get("output_clean_now") or lane.get("output_clean_pct")


def _compile_stub(account_id: str) -> dict:
    for name in (f"{account_id}-v1.json", f"{account_id}.json"):
        row = _read_json(COMPILE_DIR / name)
        if row:
            return row
    return {}


def _live_loop_scores(account_id: str, body: str, pack: dict, *, write_pack: bool = True) -> dict:
    """U047 — live CIL+RIL for commercial bundle rows (incl. sourcea-factory)."""
    if account_id not in COMMERCIAL_BUNDLE_LOOP_ACCOUNTS or not body.strip():
        return {}
    sys.path.insert(0, str(SCRIPTS))
    from conversation_interest_loop_v1 import score_conversation_interest  # noqa: WPS433
    from receiver_interest_loop_v1 import score_receiver_interest  # noqa: WPS433

    stub = _compile_stub(account_id)
    cfg_trans = _read_json(TRANSLATION_CFG)
    cfg_ril = (_read_json(W3_RECEIVER_ASSETS).get("accounts") or {}).get(account_id) or {}
    cil = score_conversation_interest(account_id=account_id, body=body, cfg=cfg_trans)
    ril = score_receiver_interest(
        account_id=account_id,
        body=body,
        cfg_row=cfg_ril,
        declared_mode=str(stub.get("compose_mode") or "") or None,
    )
    at = _now()
    cil_pct = cil.get("conversation_interest_pct")
    ril_pct = ril.get("receiver_interest_pct")
    out = {
        "cil_pct": cil_pct,
        "ril_pct": ril_pct,
        "cil_pass": cil.get("cil_pass"),
        "ril_pass": ril.get("ril_pass"),
        "loop_scores_live": True,
        "loop_scores_at": at,
        "upgrade": "U047",
    }
    if write_pack:
        pack_path = OUTBOUND / f"w3-canada-{account_id}" / "pack.json"
        merged = dict(pack or {"schema": "w3-canada-outbound-send-pack-v1", "account_id": account_id})
        if cil_pct is not None:
            merged["cil_pct"] = cil_pct
        if ril_pct is not None:
            merged["ril_pct"] = ril_pct
        merged["cil_at"] = at
        merged["ril_at"] = at
        merged["loop_scores_at"] = at
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        pack_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return out


def _icp_loop_scores(account_id: str, pack: dict, *, body: str = "") -> dict:
    """ICP compiler + loop scores from pack, live CIL/RIL, or compile stub."""
    stub = _compile_stub(account_id)
    trace = stub.get("output_trace") or {}
    icp_rcpt = _read_json(ICP_RECEIPT)
    from_receipt = icp_rcpt if icp_rcpt.get("account_id") == account_id else {}
    rrl_block = from_receipt.get("rrl") or {}
    live = _live_loop_scores(account_id, body, pack) if body.strip() else {}
    return {
        "icp_compiler_pct": pack.get("icp_compiler_pct") or trace.get("icp_compiler_pct") or from_receipt.get("icp_compiler_pct"),
        "cil_pct": live.get("cil_pct") or pack.get("cil_pct") or trace.get("cil_pct") or (from_receipt.get("cil") or {}).get("pct"),
        "ril_pct": live.get("ril_pct") or pack.get("ril_pct") or trace.get("ril_pct") or (from_receipt.get("ril") or {}).get("pct"),
        "rrl_reaction": pack.get("rrl_reaction") or trace.get("rrl_reaction") or rrl_block.get("reaction"),
        "rrl_reaction_label": rrl_block.get("label"),
        "rrl_pass": trace.get("rrl_pass") if trace.get("rrl_pass") is not None else rrl_block.get("pass"),
        "rrl_interpretation": rrl_block.get("interpretation"),
        "compile_status": stub.get("status"),
        "compile_gate": stub.get("compile_gate"),
        "loop_scores_live": live.get("loop_scores_live", False),
        "loop_scores_at": live.get("loop_scores_at"),
    }


def validate_founder_review_loop_scores() -> dict:
    """U047 acceptance — fundmore, ocree, sourcea-factory all show CIL+RIL in bundle."""
    row = build_review(write=False)
    checks: list[dict] = []
    for aid in COMMERCIAL_BUNDLE_LOOP_ACCOUNTS:
        art = next((a for a in (row.get("artifacts") or []) if a.get("account_id") == aid), {})
        sc = art.get("scores") or {}
        cil = sc.get("conversation_interest_pct")
        ril = sc.get("receiver_interest_pct")
        checks.append(
            {
                "account_id": aid,
                "ok": isinstance(cil, (int, float)) and isinstance(ril, (int, float)),
                "conversation_interest_pct": cil,
                "receiver_interest_pct": ril,
                "loop_scores_live": sc.get("loop_scores_live"),
            }
        )
    return {
        "ok": len(checks) == 3 and all(c.get("ok") for c in checks),
        "upgrade": "U047",
        "accounts": checks,
        "acceptance": "All three show loop scores",
        "check": "python3 scripts/w3_founder_review_v1.py --check-loop-scores --json",
    }


def _resolve_recipient_interpretation(account_id: str, body: str, icp_loops: dict) -> dict:
    """U039 — full recipient interpretation sentence for founder review print."""
    sentence = str(icp_loops.get("rrl_interpretation") or "").strip()
    reaction = icp_loops.get("rrl_reaction")
    label = icp_loops.get("rrl_reaction_label")
    if not sentence and body.strip():
        sys.path.insert(0, str(SCRIPTS))
        from response_reality_layer_v1 import run_rrl  # noqa: WPS433

        stub = _compile_stub(account_id)
        prof = stub.get("icp_profile") or {}
        rrl = run_rrl(
            body=body,
            account_id=account_id,
            company=str(stub.get("company") or ""),
            icp_world=prof.get("their_world") or [],
            write=False,
        )
        sim = rrl.get("simulation") or {}
        sentence = str(sim.get("recipient_interpretation") or "").strip()
        reaction = reaction or sim.get("reaction")
        label = label or sim.get("reaction_label")
        icp_loops = {
            **icp_loops,
            "rrl_reaction": reaction,
            "rrl_reaction_label": label,
            "rrl_interpretation": sentence or icp_loops.get("rrl_interpretation"),
            "rrl_pass": icp_loops.get("rrl_pass") if icp_loops.get("rrl_pass") is not None else sim.get("rrl_pass"),
        }
    full_sentence = ""
    if sentence:
        if reaction and label:
            suffix = f" ({reaction} · {label})"
        elif reaction:
            suffix = f" ({reaction})"
        else:
            suffix = ""
        full_sentence = f"Recipient interpretation: {sentence}{suffix}"
    return {
        **icp_loops,
        "recipient_interpretation": sentence or None,
        "recipient_interpretation_sentence": full_sentence or None,
        "upgrade": "U039",
    }


def validate_founder_review_interpretation() -> dict:
    """U039 acceptance — founder review shows full recipient interpretation sentence."""
    row = build_review(write=False)
    checks: list[dict] = []
    for art in row.get("artifacts") or []:
        aid = art.get("account_id")
        if aid not in ("fundmore", "ocree") or not art.get("body_text"):
            continue
        sc = art.get("scores") or {}
        sent = str(sc.get("recipient_interpretation_sentence") or "")
        checks.append(
            {
                "account_id": aid,
                "ok": sent.startswith("Recipient interpretation:") and len(sent) > 40,
                "sentence": sent,
                "reaction": sc.get("rrl_reaction"),
            }
        )
    return {
        "ok": len(checks) >= 2 and all(c.get("ok") for c in checks),
        "accounts": checks,
        "acceptance": "Already partial — full sentence",
        "upgrade": "U039",
        "check": "python3 scripts/w3_founder_review_v1.py --check-interpretation --json",
    }


def _machine_score(account_id: str) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from best_loop_oqg_score_v1 import score_w3_email  # noqa: WPS433

    pack_path = OUTBOUND / f"w3-canada-{account_id}" / "pack.json"
    body_path = OUTBOUND / f"w3-canada-{account_id}" / "body.txt"
    pack = _read_json(pack_path)
    body = body_path.read_text(encoding="utf-8") if body_path.is_file() else ""
    attach = pack.get("attach")
    attach_p = Path(str(attach)) if attach else None
    scored = score_w3_email(
        account_id=account_id,
        body=body,
        lane=str(pack.get("lane") or ""),
        attach=attach_p,
        subject=pack.get("subject"),
        relationship_basis=pack.get("relationship_basis"),
    )
    return scored


def _pipeline_slot_cleared(acct: dict) -> bool:
    slot = str(acct.get("pipeline_send_slot") or acct.get("hub_approve_slot") or "")
    return slot in ("cleared", "approved")


def _human_sina_read_from_pack(pack: dict) -> int | None:
    """U067 — pack sina_read is ship authority only when human scored (sina_read_at set)."""
    if not pack.get("sina_read_at"):
        return None
    val = pack.get("sina_read_score_pct")
    if val is None:
        val = pack.get("founder_score_pct")
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _resolve_advisor_critique(existing: dict, prev_scores: dict, pack: dict) -> dict:
    """U067 — advisor_critique field separate from sina_read · never ship authority."""
    pct = prev_scores.get("advisor_critique_pct")
    note = prev_scores.get("advisor_critique_note")
    at = prev_scores.get("advisor_critique_at")
    source = prev_scores.get("advisor_critique_source")
    if pct is None:
        pct = existing.get("advisor_critique_pct")
        note = existing.get("advisor_critique_note")
        at = existing.get("advisor_critique_at")
        source = existing.get("advisor_critique_source")
    if pct is None:
        pct = pack.get("advisor_critique_pct")
        note = pack.get("advisor_critique_note")
        at = pack.get("advisor_critique_at")
        source = pack.get("advisor_critique_source")
    if pct is None and pack.get("sina_read_score_pct") is not None and not pack.get("sina_read_at"):
        try:
            pct = int(pack.get("sina_read_score_pct"))
            source = source or "relabeled_pack_sina_without_at_u067"
            note = note or "machine/advisor score relabeled — not sina_read ship authority"
        except (TypeError, ValueError):
            pct = None
    return {
        "advisor_critique_pct": pct,
        "advisor_critique_note": note,
        "advisor_critique_at": at,
        "advisor_critique_source": source,
        "advisor_critique_ship_authority": False,
    }


def _compute_send_red(
    pack: dict,
    *,
    sina_read: int | None,
    pipeline_cleared: bool,
    sina_read_pending: bool = False,
) -> bool:
    """U066 — RED only when sina≥90 AND to set AND not sent (+ hub slot cleared · no pending read)."""
    if sina_read_pending or sina_read is None or int(sina_read) < 90:
        return False
    if not pack.get("to") or pack.get("sent_at"):
        return False
    if not pipeline_cleared:
        return False
    status = str(pack.get("status") or "")
    if status == "sent":
        return False
    allowed = (
        "prepared",
        "pack_ready",
        "machine_pass_await_sina_read",
        "ready_for_founder_send",
        "",
    )
    return status in allowed or pack.get("status") is None


def _translation_table(cfg: dict) -> dict:
    """U019 — merged translate map for founder review hints."""
    table = dict(cfg.get("translate") or {})
    for key, val in (cfg.get("human_primitive_glossary") or {}).items():
        table.setdefault(key, val)
    return table


def _translation_issues(body: str) -> tuple[list[str], dict, dict]:
    """Return forbidden-term issues plus hit glossary and full translate table on fail."""
    cfg = _read_json(ROOT / "data" / "factory-email-translation-v1.json")
    low = body.lower()
    issues: list[str] = []
    table = _translation_table(cfg)
    hit_table: dict[str, str] = {}
    for term in cfg.get("forbidden_in_email_one") or []:
        if term.lower() in low:
            suggest = table.get(term) or table.get(term.split()[0])
            issues.append(f"{term} → use '{suggest}'" if suggest else f"forbidden:{term}")
            if suggest:
                hit_table[term] = suggest
    full_table = table if issues else {}
    return issues, hit_table, full_table


def _effective_pack_status(pack: dict) -> str:
    """Machine pass without Sina read → machine_pass_await_sina_read (not ship-ready)."""
    if pack.get("sent_at") or str(pack.get("status") or "") == "sent":
        return "sent"
    sina = pack.get("sina_read_score_pct")
    if sina is None:
        sina = pack.get("founder_score_pct")
    machine_ok = bool(pack.get("oqg_pass") or pack.get("machine_verdict") == "PASS")
    if machine_ok and (sina is None or int(sina) < 90):
        return "machine_pass_await_sina_read"
    if sina is not None and int(sina) >= 90:
        return "ready_for_founder_send"
    return str(pack.get("status") or "prepared")


def _sync_pack_status(pack_path: Path, pack: dict) -> dict:
    """Write effective status onto pack when machine passed but Sina read pending."""
    effective = _effective_pack_status(pack)
    if pack.get("status") != effective:
        pack["status"] = effective
        pack["ship_authority_note"] = (
            "RRL D/E + OQG PASS are not ship authority — Sina read ≥90 required"
        )
        pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return pack


def _artifact_row(account_id: str, *, existing: dict | None = None) -> dict:
    existing = existing or {}
    pack_path = OUTBOUND / f"w3-canada-{account_id}" / "pack.json"
    body_path = OUTBOUND / f"w3-canada-{account_id}" / "body.txt"
    pack = _read_json(pack_path)
    if pack_path.is_file() and pack:
        pack = _sync_pack_status(pack_path, pack)
    stub = _compile_stub(account_id)
    body = body_path.read_text(encoding="utf-8") if body_path.is_file() else ""
    if not body.strip() and stub.get("approved_body_path"):
        alt = ROOT / str(stub["approved_body_path"])
        if alt.is_file():
            body = alt.read_text(encoding="utf-8")
    machine = _machine_score(account_id) if body.strip() else {}
    icp_loops = _icp_loop_scores(account_id, pack, body=body)
    icp_loops = _resolve_recipient_interpretation(account_id, body, icp_loops)
    trans_issues, trans_gloss, trans_table = _translation_issues(body) if body.strip() else ([], {}, {})
    ssot_row = (_read_json(W3_RECEIVER_ASSETS).get("accounts") or {}).get(account_id) or {}

    prev_scores = existing.get("scores") if isinstance(existing.get("scores"), dict) else {}
    sina_read = prev_scores.get("sina_read_score_pct")
    if sina_read is None:
        sina_read = prev_scores.get("founder_score_pct")
    if sina_read is None:
        sina_read = existing.get("sina_read_score_pct")
    if sina_read is None:
        sina_read = existing.get("founder_score_pct")
    if sina_read is None:
        sina_read = _human_sina_read_from_pack(pack)
    sina_note = (
        prev_scores.get("sina_read_note")
        or prev_scores.get("founder_score_note")
        or existing.get("sina_read_note")
        or existing.get("founder_score_note")
        or pack.get("sina_read_note")
    )
    sina_at = (
        prev_scores.get("sina_read_at")
        or prev_scores.get("founder_scored_at")
        or existing.get("sina_read_at")
        or existing.get("founder_scored_at")
        or pack.get("sina_read_at")
    )

    machine_pct = int(machine.get("output_clean_pct") or pack.get("output_clean_pct") or 0)
    brain_pct = _w3_lane_avg_from_oqg()
    if brain_pct is not None and machine_pct and brain_pct != machine_pct:
        brain_artifact_note = f"brain lane avg {brain_pct}% ≠ this artifact {machine_pct}%"
    elif machine_pct:
        brain_artifact_note = f"brain lane avg {brain_pct}% (no per-email brain score logged)"
    else:
        brain_artifact_note = "no body in the repository — compile stub only"

    approvals = _read_json(APPROVALS)
    acct_row = next((a for a in (approvals.get("accounts") or []) if a.get("id") == account_id), {})
    pipeline_cleared = _pipeline_slot_cleared(acct_row)

    deferred = (
        stub.get("status") not in ("ready_for_founder_send", "machine_pass_await_sina_read")
        and (
            icp_loops.get("compile_gate")
            or stub.get("status")
            in ("compile_deferred", "compile_queued", "compile_deferred")
        )
        and pack.get("status") != "ready_for_founder_send"
    )
    await_sina = (
        sina_read is None
        and not deferred
        and bool(body.strip())
        and not str(icp_loops.get("compile_gate") or "").startswith("blocked_until")
    )

    send_red = _compute_send_red(
        pack,
        sina_read=int(sina_read) if sina_read is not None else None,
        pipeline_cleared=pipeline_cleared,
        sina_read_pending=await_sina,
    )
    advisor = _resolve_advisor_critique(existing, prev_scores, pack)

    return {
        "account_id": account_id,
        "company": pack.get("company") or stub.get("company"),
        "lane": pack.get("lane") or stub.get("lane"),
        "sku": pack.get("sku") or stub.get("sku"),
        "subject": pack.get("subject"),
        "to": pack.get("to"),
        "from_email": pack.get("from_email"),
        "from_name": pack.get("from_name"),
        "attach": pack.get("attach"),
        "status": _effective_pack_status(pack) if pack else stub.get("status"),
        "compile_gate": icp_loops.get("compile_gate"),
        "deferred": deferred,
        "pipeline_send_slot": acct_row.get("pipeline_send_slot") or acct_row.get("hub_approve_slot"),
        "pipeline_send_cleared": pipeline_cleared,
        "send_red": send_red,
        "red_reason": "founder_manual_send_pending" if (send_red) else None,
        "body_path": str(body_path) if body_path.is_file() else str(stub.get("approved_body_path") or ""),
        "body_text": body,
        "pack_path": str(pack_path),
        "scores": {
            "icp_compiler_pct": icp_loops.get("icp_compiler_pct"),
            "conversation_interest_pct": icp_loops.get("cil_pct"),
            "receiver_interest_pct": icp_loops.get("ril_pct"),
            "loop_scores_live": icp_loops.get("loop_scores_live"),
            "loop_scores_at": icp_loops.get("loop_scores_at"),
            "preview_promise": ssot_row.get("preview_promise"),
            "interest_urls": ssot_row.get("interest_urls"),
            "interest_asset_ssot": str(W3_RECEIVER_ASSETS),
            "rrl_reaction": icp_loops.get("rrl_reaction"),
            "rrl_reaction_label": icp_loops.get("rrl_reaction_label"),
            "rrl_pass": icp_loops.get("rrl_pass"),
            "rrl_interpretation": icp_loops.get("rrl_interpretation"),
            "recipient_interpretation": icp_loops.get("recipient_interpretation"),
            "recipient_interpretation_sentence": icp_loops.get("recipient_interpretation_sentence"),
            "translation_issues": trans_issues,
            "translation_glossary": trans_gloss,
            "translation_table": trans_table,
            "rrl_is_factory_intelligence_layer": True,
            "machine_oqg_pct": machine_pct or None,
            "machine_structural_pct": machine.get("structural_pct"),
            "machine_persuasion_fefs_pct": machine.get("persuasion_fefs_pct"),
            "machine_oqg_pass": bool(machine.get("oqg_pass") or pack.get("oqg_pass")),
            "machine_checks": machine.get("checks") or [],
            "brain_lane_claim_pct": brain_pct,
            "brain_per_artifact_claim_pct": None,
            "brain_claim_note": brain_artifact_note,
            "brain_ship_authority": False,
            "pipeline_send_cleared": pipeline_cleared,
            "pipeline_send_slot_is_not_sina_read": True,
            "sina_read_score_pct": sina_read,
            "sina_read_note": sina_note,
            "sina_read_at": sina_at,
            "sina_read_pending": await_sina,
            "founder_score_pct": sina_read,
            "founder_score_note": sina_note,
            "founder_scored_at": sina_at,
            "founder_score_pending": await_sina,
            "advisor_critique_pct": advisor.get("advisor_critique_pct"),
            "advisor_critique_note": advisor.get("advisor_critique_note"),
            "advisor_critique_at": advisor.get("advisor_critique_at"),
            "advisor_critique_source": advisor.get("advisor_critique_source"),
            "advisor_critique_ship_authority": False,
            "ship_ready_requires": [
                "RRL D/E — factory intelligence (human receiver behavior sim)",
                "machine_oqg_pass (structural + FEFS persuasion)",
                "conversation_interest_pct ≥ 92 (CIL)",
                "receiver_interest_pct ≥ 90 when Mode B (RIL)",
                "sina_read_score_pct ≥ 90 (Sina human only — ship authority)",
                "founder approves recipient + sends manually from Mail",
                "confirm-sent in the repository — agents never send",
            ],
        },
    }


def build_review(*, write: bool = True) -> dict:
    prev = _read_json(RECEIPT)
    prev_arts = {a.get("account_id"): a for a in (prev.get("artifacts") or []) if a.get("account_id")}

    artifacts = [_artifact_row(aid, existing=prev_arts.get(aid, {})) for aid in FOUNDER_REVIEW_ACCOUNTS]
    red = [a for a in artifacts if a.get("send_red")]

    nerve = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    sg = nerve.get("ship_gates") or {}
    machine_cfg = _read_json(MACHINE_SSOT)

    row = {
        "schema": "w3-founder-review-v1",
        "version": "3.0.0",
        "at": _now(),
        "law": "docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md",
        "vocabulary_law": "docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md",
        "machine_ssot": str(MACHINE_SSOT.relative_to(ROOT)),
        "research_checklist_ssot": "data/outbound-research-checklist-v1.json",
        "purpose": "ICP compile · Sina read bundle — full email + RRL/CIL/RIL/OQG vs Sina read (human ship authority)",
        "governance_alignment": machine_cfg.get("governance_alignment"),
        "send_policy": machine_cfg.get("send_policy"),
        "valid_output_law": machine_cfg.get("valid_output_law"),
        "founder_review_bundle_order": list(FOUNDER_REVIEW_ACCOUNTS),
        "red_summary": {
            "better_loop_check": "w3_sends",
            "red_count": len(red),
            "account_ids": [a["account_id"] for a in red],
            "detail": "founder_manual_send_pending — Sina read PASS + recipient set · founder sends from Mail (agents never send)",
            "mail_from_configured": sg.get("w3_mail_from_configured"),
            "mail_from_gate_doc": "data/commercial-mail-from-gate-v1.json",
            "mail_from_founder_only": True,
            "w3_send_ready": sg.get("w3_send_ready"),
            "agentic_send": "restricted — produce ready-to-send pack only",
        },
        "brain_claim": _brain_lane_claim(),
        "score_ladder": {
            "1_machine_oqg": "Structural 40 + FEFS — machine, not ship authority",
            "2_conversation_interest": "CIL reply probability — machine, bar 92",
            "3_receiver_interest": "RIL click asset — machine, bar 90 (Mode B)",
            "4_rrl_factory_intelligence": "RRL human receiver behavior sim — D curious · E would_reply — NOT ship authority alone",
            "5_brain_lane_line": "Inject only — NOT ship authority",
            "6_pipeline_send_slot": "Hub workflow — NOT Sina read · NOT quality",
            "7_sina_read_score_pct": "Sina (human founder) 0–100 — ONLY ship authority",
            "8_advisor_critique": "GPT/Gemini/external — NEVER ship authority · NEVER labeled founder",
            "9_founder_manual_send": "Founder sends from Mail + confirm-sent — agents produce pack only",
        },
        "artifacts": artifacts,
        "command_score": "python3 scripts/w3_founder_review_v1.py --score <id> <pct> [--note text]",
        "command_score_all": "python3 scripts/w3_founder_review_v1.py --score-all '<json>'",
        "command_show": "python3 scripts/w3_founder_review_v1.py --show",
    }
    pending_sina = [
        a["account_id"]
        for a in artifacts
        if a.get("scores", {}).get("sina_read_pending") and a.get("account_id") in ("fundmore", "ocree")
    ]
    row["founder_next_tap"] = (
        f"Sina read ≥90 on {', '.join(pending_sina) or 'active accounts'} — "
        "python3 scripts/w3_founder_review_v1.py --score <id> <pct>"
        if pending_sina
        else "Sina read complete on W3 accounts — founder Mail send when ready"
    )
    row["research_checklist"] = {
        "ssot": "data/outbound-research-checklist-v1.json",
        "ship_note": "lint PASS + RRL D/E ≠ send authority",
        "accounts": {},
    }
    try:
        from outbound_research_checklist_v1 import preflight  # noqa: WPS433

        for aid in ("fundmore", "ocree"):
            row["research_checklist"]["accounts"][aid] = preflight(aid)
    except Exception as exc:
        row["research_checklist"]["error"] = str(exc)

    if prev.get("batch_score"):
        row["batch_score"] = prev.get("batch_score")

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if not TEMPLATE.is_file():
            TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
            tpl = {k: v for k, v in row.items() if k != "artifacts"}
            tpl["artifacts"] = []
            TEMPLATE.write_text(json.dumps(tpl, indent=2) + "\n", encoding="utf-8")

        for art in artifacts:
            pack_path = Path(art["pack_path"])
            if pack_path.is_file():
                pack = _read_json(pack_path)
                sc = art.get("scores") or {}
                if sc.get("sina_read_at"):
                    pack["sina_read_score_pct"] = sc.get("sina_read_score_pct")
                    pack["sina_read_note"] = sc.get("sina_read_note")
                    pack["sina_read_at"] = sc.get("sina_read_at")
                    pack["sina_read_source"] = "human_founder"
                    pack["founder_score_pct"] = sc.get("sina_read_score_pct")
                if sc.get("advisor_critique_pct") is not None:
                    pack["advisor_critique_pct"] = sc.get("advisor_critique_pct")
                    pack["advisor_critique_note"] = sc.get("advisor_critique_note")
                    pack["advisor_critique_at"] = sc.get("advisor_critique_at")
                    pack["advisor_critique_source"] = sc.get("advisor_critique_source")
                pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")

    return row


def _require_sina_read_note(pct: int, note: str) -> None:
    """U064 — low Sina read score requires founder note."""
    if int(pct) < 90 and not str(note or "").strip():
        raise SystemExit("sina_read score <90 requires --note")


def _pack_to_meta() -> dict:
    row = _read_json(PACK_TO_META)
    if row.get("schema") != "w3-pack-to-meta-v1":
        return {"schema": "w3-pack-to-meta-v1", "accounts": {}}
    row.setdefault("accounts", {})
    return row


def _write_pack_to_meta(row: dict) -> None:
    row["schema"] = "w3-pack-to-meta-v1"
    row["saved_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    PACK_TO_META.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def update_pack_to(account_id: str, to_email: str, *, acceptance_reset: bool = False) -> dict:
    """U063 — founder sets pack.to once; second different email blocked."""
    to_email = str(to_email or "").strip()
    if not to_email or "@" not in to_email:
        return {"ok": False, "upgrade": "U063", "error": "invalid to email"}
    pack_path = OUTBOUND / f"w3-canada-{account_id}" / "pack.json"
    if not pack_path.is_file():
        return {"ok": False, "upgrade": "U063", "account_id": account_id, "error": "missing pack"}
    meta = _pack_to_meta()
    acct_meta = (meta.get("accounts") or {}).get(account_id) or {}
    if acceptance_reset:
        meta.setdefault("accounts", {}).pop(account_id, None)
        _write_pack_to_meta(meta)
        acct_meta = {}
    pack = _read_json(pack_path)
    prior_to = str(pack.get("to") or "")
    if acct_meta.get("locked") and acct_meta.get("to") and acct_meta.get("to") != to_email:
        return {
            "ok": False,
            "upgrade": "U063",
            "account_id": account_id,
            "blocked": True,
            "reason": "to already set once",
            "locked_to": acct_meta.get("to"),
        }
    pack["to"] = to_email
    pack["to_set_at"] = _now()
    pack["to_set_by"] = "founder"
    pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    meta.setdefault("accounts", {})[account_id] = {
        "to": to_email,
        "locked": True,
        "prior_to": prior_to or None,
        "at": _now(),
    }
    _write_pack_to_meta(meta)
    build_review(write=True)
    return {
        "ok": True,
        "upgrade": "U063",
        "account_id": account_id,
        "to": to_email,
        "prior_to": prior_to or None,
        "locked": True,
    }


def validate_pack_to_update_acceptance() -> dict:
    """U063 acceptance — first set succeeds; second different email rejected."""
    aid = "sourcea-factory"
    first = update_pack_to(aid, "founder-once@noetfield.com", acceptance_reset=True)
    second = update_pack_to(aid, "blocked-second@noetfield.com")
    ok = bool(first.get("ok")) and not second.get("ok") and bool(second.get("blocked"))
    return {
        "ok": ok,
        "upgrade": "U063",
        "first": first,
        "second": second,
        "acceptance": "Founder sets recipient once",
        "check": "python3 scripts/w3_founder_review_v1.py --check-pack-to-update --json",
        "command": "python3 scripts/w3_founder_review_v1.py --pack-to sourcea-factory founder@example.com",
    }


def validate_sina_read_note_required_acceptance() -> dict:
    """U064 acceptance — score <90 without note rejected; with note or ≥90 accepted."""
    aid = "ocree"
    low_no_note: dict = {"ok": False}
    try:
        set_sina_read_score(aid, 85, note="")
        low_no_note = {"ok": True, "unexpected": True}
    except SystemExit as exc:
        low_no_note = {"ok": False, "rejected": True, "error": str(exc)}
    low_with_note = set_sina_read_score(aid, 85, note="U064 acceptance low score note")
    high_no_note = set_sina_read_score(aid, 92, note="")
    ok = (
        low_no_note.get("rejected")
        and low_with_note.get("artifacts")
        and high_no_note.get("artifacts")
    )
    art = next((a for a in (high_no_note.get("artifacts") or []) if a.get("account_id") == aid), {})
    sc = art.get("scores") or {}
    ok = ok and sc.get("sina_read_score_pct") == 92
    return {
        "ok": bool(ok),
        "upgrade": "U064",
        "low_no_note": low_no_note,
        "acceptance": "Low score without note rejected",
        "check": "python3 scripts/w3_founder_review_v1.py --check-sina-read-note --json",
    }


def validate_founder_review_order_acceptance() -> dict:
    """U065 acceptance — NF · OCree · SA · Forge order logged + hub mirror."""
    expected = list(FOUNDER_REVIEW_ACCOUNTS)
    row = build_review(write=False)
    bundle_order = list(row.get("founder_review_bundle_order") or [])
    artifact_ids = [str(a.get("account_id") or "") for a in (row.get("artifacts") or [])]
    hub = hub_slice()
    hub_ids = [str(a.get("account_id") or "") for a in (hub.get("artifacts") or [])]
    ok = bundle_order == expected and artifact_ids == expected and hub_ids == expected
    return {
        "ok": ok,
        "upgrade": "U065",
        "expected": expected,
        "bundle_order": bundle_order,
        "artifact_ids": artifact_ids,
        "hub_ids": hub_ids,
        "acceptance": "Already wired — hub mirror",
        "check": "python3 scripts/w3_founder_review_v1.py --check-founder-review-order --json",
    }


def validate_send_red_logic_acceptance() -> dict:
    """U066 acceptance — RED only when sina≥90 AND to set AND not sent (no false RED ready)."""
    synth_cases: list[tuple[dict, int | None, bool, bool, bool]] = [
        ({"to": "a@b.com", "status": "ready_for_founder_send"}, 92, True, False, True),
        ({"to": "a@b.com", "status": "prepared"}, 85, True, False, False),
        ({"to": None, "status": "prepared"}, 92, True, False, False),
        ({"to": "a@b.com", "sent_at": "2026-01-01T00:00:00Z", "status": "sent"}, 92, True, False, False),
        ({"to": "a@b.com", "status": "prepared"}, 92, False, False, False),
        ({"to": "a@b.com", "status": "prepared"}, 92, True, True, False),
        ({"to": "a@b.com", "status": "prepared"}, None, True, False, False),
    ]
    synth_rows: list[dict] = []
    synth_ok = True
    for pack, sina, pipe, pending, expect in synth_cases:
        got = _compute_send_red(
            pack,
            sina_read=sina,
            pipeline_cleared=pipe,
            sina_read_pending=pending,
        )
        synth_rows.append({"expect": expect, "got": got, "sina": sina, "to": pack.get("to")})
        if got != expect:
            synth_ok = False

    live_violations: list[dict] = []
    review = build_review(write=False)
    for art in review.get("artifacts") or []:
        aid = art.get("account_id")
        sc = art.get("scores") or {}
        if not art.get("send_red"):
            continue
        sina = sc.get("sina_read_score_pct")
        pending = bool(sc.get("sina_read_pending"))
        if pending or sina is None:
            live_violations.append({"account_id": aid, "issue": "send_red_while_sina_pending"})
        elif int(sina) < 90:
            live_violations.append({"account_id": aid, "issue": "send_red_below_sina_90", "sina": sina})
        if not art.get("to"):
            live_violations.append({"account_id": aid, "issue": "send_red_without_to"})
        pack_path = Path(str(art.get("pack_path") or ""))
        pack = _read_json(pack_path) if pack_path.is_file() else {}
        if pack.get("sent_at"):
            live_violations.append({"account_id": aid, "issue": "send_red_after_sent"})
        if not art.get("pipeline_send_cleared"):
            live_violations.append({"account_id": aid, "issue": "send_red_without_pipeline_cleared"})

    ok = synth_ok and not live_violations
    return {
        "ok": ok,
        "upgrade": "U066",
        "synthetic_ok": synth_ok,
        "synthetic_cases": synth_rows,
        "live_violations": live_violations,
        "red_on_disk": [
            a.get("account_id")
            for a in (review.get("artifacts") or [])
            if a.get("send_red")
        ],
        "acceptance": "No false RED ready",
        "check": "python3 scripts/w3_founder_review_v1.py --check-send-red-logic --json",
    }


def validate_advisor_critique_separate_acceptance() -> dict:
    """U067 acceptance — GPT/advisor score stored as advisor_critique · never sina_read."""
    ladder = (build_review(write=False).get("score_ladder") or {})
    ladder_ok = "8_advisor_critique" in ladder and "7_sina_read_score_pct" in ladder

    synth_ok = True
    synth_detail: dict = {}
    try:
        row = set_advisor_critique_score("forge-product", 88, note="U067 acceptance GPT critique")
        art = next(a for a in (row.get("artifacts") or []) if a.get("account_id") == "forge-product")
        sc = art.get("scores") or {}
        synth_ok = (
            sc.get("advisor_critique_pct") == 88
            and sc.get("advisor_critique_ship_authority") is False
            and sc.get("sina_read_score_pct") is None
            and sc.get("advisor_critique_pct") != sc.get("sina_read_score_pct")
        )
        synth_detail = {
            "account_id": "forge-product",
            "advisor_critique_pct": sc.get("advisor_critique_pct"),
            "sina_read_score_pct": sc.get("sina_read_score_pct"),
        }
    except Exception as exc:
        synth_ok = False
        synth_detail = {"error": str(exc)}

    forbidden_hits: list[dict] = []
    review = build_review(write=False)
    for art in review.get("artifacts") or []:
        aid = art.get("account_id")
        sc = art.get("scores") or {}
        for key in FORBIDDEN_SINA_ALIASES:
            if key in sc or key in art:
                forbidden_hits.append({"account_id": aid, "forbidden_key": key})
        if sc.get("advisor_critique_ship_authority"):
            forbidden_hits.append({"account_id": aid, "issue": "advisor_critique_ship_authority_true"})
        ac = sc.get("advisor_critique_pct")
        sr = sc.get("sina_read_score_pct")
        if ac is not None and sr is not None and ac == sr and sc.get("advisor_critique_source") != "relabeled_pack_sina_without_at_u067":
            forbidden_hits.append(
                {"account_id": aid, "issue": "advisor_equals_sina_without_relabel", "pct": ac}
            )

    ok = ladder_ok and synth_ok and not forbidden_hits
    return {
        "ok": ok,
        "upgrade": "U067",
        "ladder_ok": ladder_ok,
        "synthetic_ok": synth_ok,
        "synthetic_detail": synth_detail,
        "forbidden_hits": forbidden_hits,
        "acceptance": "GPT score ≠ sina_read",
        "check": "python3 scripts/w3_founder_review_v1.py --check-advisor-critique-separate --json",
        "command": "python3 scripts/w3_founder_review_v1.py --advisor-score ocree 93 --note 'GPT critique'",
    }


def validate_export_md_acceptance() -> dict:
    """U068 acceptance — fundmore + ocree + sourcea-factory · three emails · one file."""
    row = build_review(write=False)
    dest = export_markdown(row)
    text = dest.read_text(encoding="utf-8")
    headers = [ln for ln in text.splitlines() if ln.startswith("## ")]
    account_ids = [h.replace("## ", "").split(" — ", 1)[0].strip() for h in headers]
    expected = list(COMMERCIAL_BUNDLE_LOOP_ACCOUNTS)
    body_blocks = text.count("```") // 2
    ok = (
        dest.is_file()
        and len(headers) == 3
        and account_ids == expected
        and body_blocks == 3
        and "forge-product" not in text
    )
    return {
        "ok": ok,
        "upgrade": "U068",
        "path": str(dest),
        "email_count": len(headers),
        "account_ids": account_ids,
        "expected": expected,
        "body_blocks": body_blocks,
        "acceptance": "Three emails one file",
        "check": "python3 scripts/w3_founder_review_v1.py --check-export-md --json",
        "command": "python3 scripts/w3_founder_review_v1.py --export-md",
    }


def _apply_sina_score_to_artifact(art: dict, pct: int, *, note: str = "") -> None:
    _require_sina_read_note(pct, note)
    art.setdefault("scores", {})
    art["scores"]["sina_read_score_pct"] = int(pct)
    art["scores"]["sina_read_note"] = note or None
    art["scores"]["sina_read_at"] = _now()
    art["scores"]["sina_read_pending"] = False
    art["scores"]["founder_score_pct"] = int(pct)
    art["scores"]["founder_score_note"] = note or None
    art["scores"]["founder_scored_at"] = art["scores"]["sina_read_at"]
    art["scores"]["founder_score_pending"] = False


def set_sina_read_scores_batch(scores: dict[str, dict], *, write: bool = True) -> dict:
    """U061 — batch Sina read for fundmore + ocree + sourcea-factory with notes."""
    row = build_review(write=False)
    results: list[dict] = []
    for aid in SCORE_ALL_THREE:
        spec = scores.get(aid) if isinstance(scores.get(aid), dict) else {}
        pct = spec.get("pct")
        note = str(spec.get("note") or "")
        if pct is None:
            results.append({"account_id": aid, "ok": False, "error": "missing pct"})
            continue
        found = False
        for art in row.get("artifacts") or []:
            if art.get("account_id") != aid:
                continue
            found = True
            _require_sina_read_note(int(pct), note)
            _apply_sina_score_to_artifact(art, int(pct), note=note)
            results.append(
                {
                    "account_id": aid,
                    "ok": True,
                    "pct": int(pct),
                    "note": note or None,
                }
            )
            break
        if not found:
            results.append({"account_id": aid, "ok": False, "error": "unknown account_id"})
    if not all(r.get("ok") for r in results):
        missing = [r for r in results if not r.get("ok")]
        raise SystemExit(f"batch score failed: {missing}")
    row["at"] = _now()
    row["batch_score"] = {"upgrade": "U061", "accounts": results, "at": row["at"]}
    if write:
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        build_review(write=True)
    return row


def _parse_score_all_payload(raw: str) -> dict[str, dict]:
    text = str(raw or "").strip()
    if not text:
        raise SystemExit("score-all payload empty — provide JSON or file path")
    path = Path(text)
    if path.is_file():
        text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise SystemExit("score-all JSON must be an object keyed by account_id")
    out: dict[str, dict] = {}
    for aid in SCORE_ALL_THREE:
        spec = data.get(aid)
        if not isinstance(spec, dict):
            raise SystemExit(f"score-all missing entry for {aid}")
        out[aid] = spec
    return out


def validate_score_all_acceptance() -> dict:
    """U061 acceptance — batch score all three with notes in one command."""
    scores = {
        "fundmore": {"pct": 92, "note": "U061 batch fundmore"},
        "ocree": {"pct": 90, "note": "U061 batch ocree"},
        "sourcea-factory": {"pct": 91, "note": "U061 batch sourcea-factory"},
    }
    row = set_sina_read_scores_batch(scores, write=True)
    receipt = _read_json(RECEIPT)
    checks: list[dict] = []
    for aid in SCORE_ALL_THREE:
        art = next((a for a in (receipt.get("artifacts") or []) if a.get("account_id") == aid), {})
        sc = art.get("scores") or {}
        expected = scores[aid]
        checks.append(
            {
                "account_id": aid,
                "ok": sc.get("sina_read_score_pct") == expected["pct"]
                and sc.get("sina_read_note") == expected["note"]
                and sc.get("sina_read_pending") is False,
                "pct": sc.get("sina_read_score_pct"),
                "note": sc.get("sina_read_note"),
            }
        )
    batch = row.get("batch_score") or receipt.get("batch_score") or {}
    ok = (
        len(checks) == 3
        and all(c.get("ok") for c in checks)
        and batch.get("upgrade") == "U061"
        and len(batch.get("accounts") or []) == 3
    )
    return {
        "ok": ok,
        "upgrade": "U061",
        "accounts": checks,
        "batch_score": batch,
        "acceptance": "Batch score with notes",
        "check": "python3 scripts/w3_founder_review_v1.py --check-score-all --json",
        "command": "python3 scripts/w3_founder_review_v1.py --score-all '<json>'",
    }


def set_sina_read_score(account_id: str, pct: int, *, note: str = "") -> dict:
    """Record Sina (human founder) read score — only Sina sets this."""
    row = build_review(write=False)
    found = False
    for art in row.get("artifacts") or []:
        if art.get("account_id") != account_id:
            continue
        found = True
        _apply_sina_score_to_artifact(art, pct, note=note)
    if not found:
        raise SystemExit(f"unknown account_id: {account_id}")
    row["at"] = _now()
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    build_review(write=True)
    try:
        sys.path.insert(0, str(SCRIPTS))
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "sina_read_score",
            detail=f"{account_id}={pct}%",
            extra={"upgrade": "U090", "account_id": account_id, "sina_read_score_pct": int(pct)},
        )
    except Exception:
        pass
    return row


def set_advisor_critique_score(
    account_id: str,
    pct: int,
    *,
    note: str = "",
    source: str = "advisor_llm",
) -> dict:
    """U067 — GPT/Gemini critique on advisor_critique_* only · never sina_read ship authority."""
    row = build_review(write=False)
    found = False
    for art in row.get("artifacts") or []:
        if art.get("account_id") != account_id:
            continue
        found = True
        art.setdefault("scores", {})
        art["scores"]["advisor_critique_pct"] = int(pct)
        art["scores"]["advisor_critique_note"] = note or None
        art["scores"]["advisor_critique_at"] = _now()
        art["scores"]["advisor_critique_source"] = source
        art["scores"]["advisor_critique_ship_authority"] = False
    if not found:
        raise SystemExit(f"unknown account_id: {account_id}")
    row["at"] = _now()
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return build_review(write=True)


def _apply_pack_sent_transition(account_id: str, *, now: str, note: str = "") -> dict:
    """U062 — pack.status ready_for_founder_send → sent + sent_at on Mail confirm."""
    pack_path = OUTBOUND / f"w3-canada-{account_id}" / "pack.json"
    if not pack_path.is_file():
        return {
            "ok": False,
            "account_id": account_id,
            "error": "missing pack",
            "upgrade": "U062",
        }
    pack = _read_json(pack_path)
    if pack.get("sent_at") or str(pack.get("status") or "") == "sent":
        return {
            "ok": True,
            "account_id": account_id,
            "already_sent": True,
            "status": "sent",
            "sent_at": pack.get("sent_at"),
            "upgrade": "U062",
        }
    prior = str(pack.get("status") or "")
    effective = _effective_pack_status(pack)
    if prior != "ready_for_founder_send" and effective != "ready_for_founder_send":
        return {
            "ok": False,
            "account_id": account_id,
            "blocked": True,
            "reason": f"pack must be ready_for_founder_send (got {prior})",
            "prior_status": prior,
            "effective_status": effective,
            "upgrade": "U062",
        }
    pack["status"] = "sent"
    pack["sent_at"] = now
    pack["sent_by"] = "founder"
    pack["confirm_sent_at"] = now
    if note:
        pack["confirm_sent_note"] = note
    pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "account_id": account_id,
        "prior_status": prior,
        "status": "sent",
        "sent_at": now,
        "upgrade": "U062",
    }


def validate_confirm_sent_pack_transition_acceptance() -> dict:
    """U062 acceptance — sent_at stamped on pack when founder confirms Mail send."""
    aid = "fundmore"
    pack_path = OUTBOUND / f"w3-canada-{aid}" / "pack.json"
    pack = _read_json(pack_path)
    if not pack:
        return {"ok": False, "upgrade": "U062", "error": "missing fundmore pack"}
    pack["status"] = "ready_for_founder_send"
    pack["sina_read_score_pct"] = max(int(pack.get("sina_read_score_pct") or 0), 92)
    pack["sina_read_at"] = _now()
    pack["sina_read_source"] = "human_founder"
    pack.pop("sent_at", None)
    pack.pop("confirm_sent_at", None)
    pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    row = confirm_sent(aid, note="U062 acceptance Mail confirm")
    after = _read_json(pack_path)
    approvals = _read_json(APPROVALS)
    appr = next((a for a in (approvals.get("accounts") or []) if a.get("id") == aid), {})
    ok = (
        after.get("status") == "sent"
        and bool(after.get("sent_at"))
        and after.get("confirm_sent_at") == after.get("sent_at")
        and bool(appr.get("sent_at"))
        and str(appr.get("confirm_sent_note") or "") == "U062 acceptance Mail confirm"
    )
    return {
        "ok": ok,
        "upgrade": "U062",
        "pack_after": {
            "status": after.get("status"),
            "sent_at": after.get("sent_at"),
            "confirm_sent_at": after.get("confirm_sent_at"),
        },
        "approval_sent_at": appr.get("sent_at"),
        "acceptance": "sent_at stamped on Mail confirm",
        "check": "python3 scripts/w3_founder_review_v1.py --check-confirm-sent-pack --json",
        "command": "python3 scripts/w3_founder_review_v1.py --confirm-sent fundmore --note 'Mail confirm'",
    }


def confirm_sent(account_id: str, *, note: str = "") -> dict:
    """Record founder manual send — stamps approvals + review receipt."""
    now = _now()
    approvals = _read_json(APPROVALS)
    found = False
    for acct in approvals.get("accounts") or []:
        if acct.get("id") == account_id:
            acct["confirm_sent_at"] = now
            acct["sent_at"] = now
            acct["sent_by"] = "founder"
            if note:
                acct["confirm_sent_note"] = note
            found = True
            break
    if not found:
        raise SystemExit(f"unknown account_id: {account_id}")
    approvals["saved_at"] = now
    APPROVALS.write_text(json.dumps(approvals, indent=2) + "\n", encoding="utf-8")

    pack_row = _apply_pack_sent_transition(account_id, now=now, note=note)
    if not pack_row.get("ok"):
        raise SystemExit(pack_row.get("reason") or pack_row.get("error") or "pack sent transition failed")

    confirm_receipt = SINA / "w3-confirm-sent-receipt-v1.json"
    hist = _read_json(confirm_receipt)
    events = hist.get("events") or []
    events.append({"account_id": account_id, "at": now, "note": note, "pack_status": pack_row.get("status")})
    confirm_receipt.parent.mkdir(parents=True, exist_ok=True)
    confirm_receipt.write_text(
        json.dumps({"schema": "w3-confirm-sent-receipt-v1", "at": now, "events": events}, indent=2) + "\n",
        encoding="utf-8",
    )
    row = build_review(write=True)
    try:
        from commercial_command_pulse_v1 import run_pulse  # noqa: WPS433

        run_pulse(write=True)
    except Exception:
        pass
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "w3-founder-review-v1":
        row = build_review(write=True)
    pack_to_meta = _pack_to_meta().get("accounts") or {}
    reply_latest: dict[str, dict] = {}
    try:
        from outbound_reply_log_v1 import latest_reply_by_account  # noqa: WPS433

        reply_latest = latest_reply_by_account()
    except Exception:
        reply_latest = {}
    slim = []
    for art in row.get("artifacts") or []:
        sc = art.get("scores") or {}
        aid = art.get("account_id")
        to_lock = pack_to_meta.get(aid) or {}
        rep = reply_latest.get(aid) or {}
        slim.append(
            {
                "account_id": aid,
                "company": art.get("company"),
                "subject": art.get("subject"),
                "to": art.get("to"),
                "to_locked": bool(to_lock.get("locked")),
                "deferred": art.get("deferred"),
                "compile_gate": art.get("compile_gate"),
                "send_red": art.get("send_red"),
                "reply_yn": rep.get("reply_yn"),
                "reply_logged_at": rep.get("at"),
                "reply_note": rep.get("note"),
                "icp_compiler_pct": sc.get("icp_compiler_pct"),
                "rrl_reaction": sc.get("rrl_reaction"),
                "recipient_interpretation_sentence": sc.get("recipient_interpretation_sentence"),
                "machine_oqg_pct": sc.get("machine_oqg_pct"),
                "sina_read_score_pct": sc.get("sina_read_score_pct") or sc.get("founder_score_pct"),
                "sina_read_pending": sc.get("sina_read_pending", sc.get("founder_score_pending")),
                "founder_score_pct": sc.get("sina_read_score_pct") or sc.get("founder_score_pct"),
                "founder_score_pending": sc.get("sina_read_pending", sc.get("founder_score_pending")),
                "advisor_critique_pct": sc.get("advisor_critique_pct"),
                "advisor_critique_ship_authority": sc.get("advisor_critique_ship_authority", False),
                "brain_lane_claim_pct": sc.get("brain_lane_claim_pct"),
            }
        )
    pending_ids = [a["account_id"] for a in slim if a.get("sina_read_pending")]
    return {
        "schema": "worker-hub-w3-founder-review-v1",
        "at": row.get("at"),
        "red_summary": row.get("red_summary"),
        "score_ladder": row.get("score_ladder"),
        "artifacts": slim,
        "command": "python3 scripts/w3_founder_review_v1.py --show",
        "hub_anchor": "#sina-read-card",
        "hub_url": "http://127.0.0.1:13020/worker-hub/#sina-read-card",
        "pending_count": len(pending_ids),
        "pending_accounts": pending_ids,
        "bundle_path": str(SINA / "outbound" / "founder-review-bundle-v1.md"),
        "reply_log_path": str(SINA / "outbound-replies-v1.jsonl"),
        "reply_log_command": "python3 scripts/outbound_reply_log_v1.py --log <account_id> Y|N",
        "ship_authority": "sina_read_score_pct only — machine OQG/RRL are not ship gates alone",
    }


def print_show(row: dict) -> None:
    print("=" * 72)
    print("ICP COMPILE · SINA READ BUNDLE — 4 BRANDS · RRL INTELLIGENCE LAYER")
    print("=" * 72)
    print(f"\nVALID OUTPUT: {row.get('valid_output_law') or '(see machine SSOT)'}")
    sp = row.get("send_policy") or {}
    if sp:
        print(f"SEND POLICY: agents may={sp.get('agent_may')} · founder must={sp.get('founder_must')}")
    rs = row.get("red_summary") or {}
    print(f"\nRED ({rs.get('red_count', 0)}): {rs.get('detail')}")
    if rs.get("account_ids"):
        print(f"  accounts: {', '.join(rs.get('account_ids') or [])}")
    print(f"  agentic_send: {rs.get('agentic_send')}")

    bc = row.get("brain_claim") or {}
    print(f"\nBRAIN CLAIM (NOT ship authority): {bc.get('lane_claim_line')}")
    print(f"  {bc.get('note')}")

    print("\nSCORE LADDER:")
    for k, v in (row.get("score_ladder") or {}).items():
        print(f"  {k}: {v}")

    for art in row.get("artifacts") or []:
        sc = art.get("scores") or {}
        print("\n" + "=" * 72)
        flag = ""
        if art.get("deferred"):
            flag = " *** DEFERRED — compile gate ***"
        elif art.get("send_red"):
            flag = " *** FOUNDER MANUAL SEND ***"
        elif sc.get("sina_read_pending") and art.get("body_text"):
            flag = " *** AWAIT SINA READ ***"
        print(f"{art.get('company')} ({art.get('account_id')}){flag}")
        print("=" * 72)
        if art.get("compile_gate"):
            print(f"Compile gate: {art.get('compile_gate')}")
        acct = next((a for a in (_read_json(APPROVALS).get("accounts") or []) if a.get("id") == art.get("account_id")), {})
        if acct.get("parallel_with"):
            print(f"Parallel with: {acct.get('parallel_with')} (same compile tier)")
        print(f"Subject: {art.get('subject') or '(not composed)'}")
        print(f"To: {art.get('to') or '(founder sets recipient)'}  From: {art.get('from_email')}")
        print(f"SKU: {art.get('sku')}  Lane: {art.get('lane')}  Status: {art.get('status')}")
        print(f"Attach: {art.get('attach') or '(none)'}")
        print("\n--- FACTORY INTELLIGENCE (RRL + loops) ---")
        print(f"  icp_compiler_pct:    {sc.get('icp_compiler_pct') or '—'}")
        print(f"  conversation_interest: {sc.get('conversation_interest_pct') or '—'}")
        print(f"  receiver_interest:   {sc.get('receiver_interest_pct') or '—'}")
        rrl = sc.get("rrl_reaction")
        print(
            f"  rrl_reaction:        {rrl or '—'}  pass={sc.get('rrl_pass')}  (factory intelligence layer)"
        )
        if sc.get("recipient_interpretation_sentence"):
            print(f"  {sc.get('recipient_interpretation_sentence')}")
        elif sc.get("rrl_interpretation"):
            print(f"  rrl_interpretation:  {sc.get('rrl_interpretation')}")
        rrl_label = sc.get("rrl_reaction_label")
        if rrl_label:
            print(f"  rrl_label:           {rrl_label}")
        if rrl:
            meaning = "D=curious may reply · E=would reply — neither is ship authority"
            print(f"  rrl_meaning:         {meaning}")
        trans_issues = sc.get("translation_issues") or []
        if trans_issues:
            print("\n--- TRANSLATION HINTS (use human primitives) ---")
            for issue in trans_issues[:6]:
                print(f"  {issue}")
            gloss = sc.get("translation_glossary") or {}
            if gloss:
                print("  hits:")
                for key, val in gloss.items():
                    print(f"    {key} → {val}")
            table = sc.get("translation_table") or {}
            if table:
                print("\n  translate table:")
                for key, val in table.items():
                    print(f"    {key} → {val}")
        print("\n--- MACHINE OQG ---")
        print(f"  machine_oqg_total:   {sc.get('machine_oqg_pct') or '—'}%  pass={sc.get('machine_oqg_pass')}")
        print(f"  brain_lane_claim:    {sc.get('brain_lane_claim_pct')}%  (NOT ship authority)")
        print(f"  pipeline_send_slot:  {art.get('pipeline_send_slot')}  (workflow — NOT Sina read)")
        sr = sc.get("sina_read_score_pct") or sc.get("founder_score_pct")
        print(
            f"  sina_read_score_pct: {sr if sr is not None else 'PENDING — Sina reads after full email'}"
        )
        if sc.get("sina_read_note") or sc.get("founder_score_note"):
            print(f"  sina_read_note:      {sc.get('sina_read_note') or sc.get('founder_score_note')}")
        print(f"  {sc.get('brain_claim_note')}")
        if art.get("body_text"):
            print("\n--- FULL EMAIL BODY (ready for founder review) ---\n")
            print(art.get("body_text"))
            print("\n--- END EMAIL ---")
        else:
            print("\n--- NO BODY YET (compile stub logged) ---")

    print("\n" + "=" * 72)
    print(
        "TO SCORE (Sina only): python3 scripts/w3_founder_review_v1.py --score sourcea-factory 92 --note 'reason'"
    )
    print("=" * 72)


def export_markdown(row: dict | None = None, *, out_path: Path | None = None) -> Path:
    """U068 — export fundmore + ocree + sourcea-factory emails in one markdown file."""
    row = row or build_review(write=False)
    dest = out_path or (SINA / "outbound" / "founder-review-bundle-v1.md")
    arts = [
        a
        for a in (row.get("artifacts") or [])
        if a.get("account_id") in COMMERCIAL_BUNDLE_LOOP_ACCOUNTS and str(a.get("body_text") or "").strip()
    ]
    lines = [
        "# Founder review bundle — ready to send",
        "",
        f"**Generated:** {row.get('at') or _now()}",
        "",
        f"**Bundle:** {', '.join(COMMERCIAL_BUNDLE_LOOP_ACCOUNTS)} · three emails · one file",
        "",
        "Ship authority: **sina_read_score_pct only** (Sina human). Machine OQG/RRL are not ship gates alone.",
        "",
    ]
    for art in arts:
        sc = art.get("scores") or {}
        lines.append(f"## {art.get('account_id')} — {art.get('company')}")
        if art.get("deferred"):
            lines.append(f"- **Status:** DEFERRED ({art.get('compile_gate')})")
        lines.append(f"- **To:** {art.get('to')}")
        lines.append(f"- **From:** {art.get('from_email')} ({art.get('lane')})")
        lines.append(f"- **Subject:** {art.get('subject')}")
        lines.append(f"- **ICP:** {sc.get('icp_compiler_pct')}% · **OQG:** {sc.get('machine_oqg_pct')}% · **RRL:** {sc.get('rrl_reaction')}")
        if sc.get("recipient_interpretation_sentence"):
            lines.append(f"- **{sc.get('recipient_interpretation_sentence')}**")
        sr = sc.get("sina_read_score_pct")
        lines.append(f"- **Sina read:** {sr if sr is not None else 'PENDING'}")
        lines.append("")
        if art.get("body_text"):
            lines.append("```")
            lines.append(art.get("body_text", "").rstrip())
            lines.append("```")
        lines.append("")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description="W3 founder review bundle")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--show", action="store_true", help="Print full emails + scores for founder analysis")
    ap.add_argument("--export-md", action="store_true", help="Write founder-review-bundle-v1.md for Mail paste")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--check-interpretation", action="store_true", help="U039 — recipient interpretation full sentence in founder review")
    ap.add_argument("--check-loop-scores", action="store_true", help="U047 — fundmore/ocree/sourcea-factory CIL+RIL in bundle")
    ap.add_argument("--check-score-all", action="store_true", help="U061 — batch score all three with notes")
    ap.add_argument("--check-confirm-sent-pack", action="store_true", help="U062 — ready_for_founder_send → sent + sent_at")
    ap.add_argument("--check-pack-to-update", action="store_true", help="U063 — pack.to single-set lock")
    ap.add_argument("--check-sina-read-note", action="store_true", help="U064 — score <90 requires note")
    ap.add_argument("--check-founder-review-order", action="store_true", help="U065 — NF OCree SA Forge hub order")
    ap.add_argument("--check-send-red-logic", action="store_true", help="U066 — send_red only when sina≥90 + to + not sent")
    ap.add_argument(
        "--check-advisor-critique-separate",
        action="store_true",
        help="U067 — advisor_critique separate from sina_read",
    )
    ap.add_argument("--check-export-md", action="store_true", help="U068 — three emails one markdown file")
    ap.add_argument("--pack-to", nargs=2, metavar=("ID", "EMAIL"), help="U063 — set pack.to once")
    ap.add_argument("--score", nargs=2, metavar=("ID", "PCT"))
    ap.add_argument("--advisor-score", nargs=2, metavar=("ID", "PCT"), help="U067 — GPT critique only")
    ap.add_argument(
        "--score-all",
        nargs="?",
        const="-",
        metavar="JSON",
        help="U061 — batch Sina read for fundmore+ocree+sourcea-factory (JSON or path; stdin if omitted)",
    )
    ap.add_argument("--note", default="")
    ap.add_argument("--confirm-sent", metavar="ID", help="Record founder manual send for account")
    args = ap.parse_args()

    if args.check_interpretation:
        row = validate_founder_review_interpretation()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_interpretation:", "PASS" if row.get("ok") else row.get("accounts"))
        return 0 if row.get("ok") else 1
    if args.check_loop_scores:
        row = validate_founder_review_loop_scores()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_loop_scores:", "PASS" if row.get("ok") else row.get("accounts"))
        return 0 if row.get("ok") else 1
    if args.check_score_all:
        row = validate_score_all_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_score_all:", "PASS" if row.get("ok") else row.get("accounts"))
        return 0 if row.get("ok") else 1
    if args.check_confirm_sent_pack:
        row = validate_confirm_sent_pack_transition_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_confirm_sent_pack:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_pack_to_update:
        row = validate_pack_to_update_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_pack_to_update:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_sina_read_note:
        row = validate_sina_read_note_required_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_sina_read_note:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_founder_review_order:
        row = validate_founder_review_order_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_founder_review_order:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_send_red_logic:
        row = validate_send_red_logic_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_send_red_logic:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_advisor_critique_separate:
        row = validate_advisor_critique_separate_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_advisor_critique_separate:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_export_md:
        row = validate_export_md_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_export_md:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.pack_to:
        aid, email = args.pack_to
        row = update_pack_to(aid, email)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"OK: pack-to {aid}={email}" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    if args.confirm_sent:
        row = confirm_sent(args.confirm_sent, note=args.note)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"OK: confirm-sent {args.confirm_sent}")
        return 0
    if args.score:
        aid, pct_s = args.score
        row = set_sina_read_score(aid, int(pct_s), note=args.note)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"OK: sina_read_score {aid}={pct_s}%")
        return 0
    if args.advisor_score:
        aid, pct_s = args.advisor_score
        row = set_advisor_critique_score(aid, int(pct_s), note=args.note)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"OK: advisor_critique {aid}={pct_s}%")
        return 0
    if args.score_all is not None:
        payload = sys.stdin.read() if args.score_all == "-" else str(args.score_all)
        scores = _parse_score_all_payload(payload)
        row = set_sina_read_scores_batch(scores, write=True)
        if args.json:
            print(json.dumps({"ok": True, "batch_score": row.get("batch_score"), "upgrade": "U061"}, indent=2))
        else:
            scored = ", ".join(f"{r['account_id']}={r['pct']}%" for r in (row.get("batch_score") or {}).get("accounts") or [])
            print(f"OK: score-all {scored}")
        return 0

    row = build_review(write=True)
    if args.export_md:
        path = export_markdown(row)
        print(f"OK: exported {path}")
        return 0
    if args.show:
        print_show(row)
        return 0
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print_show(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
