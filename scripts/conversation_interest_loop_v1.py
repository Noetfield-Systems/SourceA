#!/usr/bin/env python3
"""Conversation Interest Loop (CIL) — reply probability from recipient POV.

Scores whether email earns a thoughtful reply — not product explanation.
Separate from OQG, RIL, and Sina read (human founder only).

Law: docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md
Receipt: ~/.sina/conversation-interest-loop-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from best_loop_oqg_score_v1 import SCRAPE_OPEN_RE, check_scrape_open  # noqa: E402

SINA = Path.home() / ".sina"
TRANSLATION = ROOT / "data" / "factory-email-translation-v1.json"
EMAILS_JSON = ROOT / "data" / "commercial" / "canada-priority-a-emails-v1.json"
W3_PACK_ROOT = SINA / "outbound"
RECEIPT = SINA / "conversation-interest-loop-receipt-v1.json"
FLEET_RECEIPT = SINA / "cil-fleet-receipt-v1.json"
BAR = 92
W3_ACCOUNTS = ("ocree", "fundmore")
FLEET_ACCOUNTS = W3_ACCOUNTS


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _pack_dir(account_id: str) -> Path:
    return W3_PACK_ROOT / f"w3-canada-{account_id}"


def _pack_path(account_id: str) -> Path:
    return _pack_dir(account_id) / "pack.json"


def sync_cil_to_pack(*, account_id: str, scored: dict, write: bool = True) -> dict:
    """U041 — wire conversation_interest_pct onto w3 pack as cil_pct."""
    pack_path = _pack_path(account_id)
    pack = _read_json(pack_path)
    if not pack:
        return {"ok": False, "account_id": account_id, "reason": "missing_pack", "path": str(pack_path)}
    pct = scored.get("conversation_interest_pct")
    if pct is None:
        return {"ok": False, "account_id": account_id, "reason": "missing_score"}
    pack["cil_pct"] = pct
    pack["cil_pass"] = bool(scored.get("cil_pass"))
    pack["cil_at"] = _now()
    if write:
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "account_id": account_id, "cil_pct": pct, "cil_pass": pack["cil_pass"], "path": str(pack_path)}


def _body_for(account_id: str) -> str:
    pack = _pack_dir(account_id) / "body.txt"
    if pack.is_file():
        return pack.read_text(encoding="utf-8")
    data = _read_json(EMAILS_JSON)
    for row in data.get("accounts") or []:
        if row.get("id") == account_id:
            return str(row.get("body_full") or row.get("body") or "")
    return ""


def _word_count(text: str) -> int:
    pre = text.split("Reply **stop**")[0] if "Reply **stop**" in text else text
    return len(re.findall(r"[A-Za-z0-9']+", pre))


def _mode(body: str) -> str:
    low = body.lower()
    if re.search(r"\b(demo|preview|replay|walk through|walkthrough)\b", low):
        return "B_interest_asset"
    return "A_curiosity_first"


def _narrative_before_link(pre_sig: str) -> str:
    """Narrative portion before link / If relevant block."""
    hits: list[int] = []
    for pat in (r"https?://", r"^\s*if relevant", r"^\s*if useful"):
        m = re.search(pat, pre_sig, re.I | re.M)
        if m:
            hits.append(m.start())
    if hits:
        return pre_sig[: min(hits)].rstrip()
    return pre_sig.rstrip()


def check_cil_curiosity_end_weight(pre_sig: str) -> dict:
    """U044 — curiosity question in last 30% of narrative earns full CIL1 bonus."""
    narrative = _narrative_before_link(pre_sig)
    pre_no_url = re.sub(r"https?://[^\s]+", "", pre_sig)
    has_q = "?" in narrative
    q_idx = narrative.rfind("?")
    threshold = int(len(narrative) * 0.7) if narrative else 0
    end_weight = has_q and q_idx >= threshold
    no_hard_close = not re.search(r"\b(book|schedule|15 minutes)\b", pre_no_url[-200:].lower())
    if end_weight and no_hard_close:
        points = 25
        issues: list[str] = []
    elif has_q:
        points = 10
        issues = ["question_not_in_last_30pct"] if not end_weight else ["hard_close_after_question"]
    else:
        points = 0
        issues = ["weak_curiosity_close"]
    return {
        "id": "cil_curiosity_close",
        "points": points,
        "max": 25,
        "issues": issues,
        "end_weight": end_weight,
        "question_in_last_30pct": end_weight,
        "narrative_chars": len(narrative),
        "upgrade": "U044",
    }


def validate_cil_curiosity_end_weight_acceptance() -> dict:
    """U044 acceptance — question in last 30% of narrative earns full bonus."""
    end_q = check_cil_curiosity_end_weight(
        "Hi Chris,\n\n"
        "Boards ask for evidence after AI decisions in mortgage ops.\n\n"
        "Curious whether your team is preparing for that audit question yet?"
    )
    early_q = check_cil_curiosity_end_weight(
        "Still too early for audit replay?\n\n"
        "Boards ask for evidence after AI decisions in mortgage ops.\n\n"
        "We focus on copilot replay at Noetfield."
    )
    live_rows: list[dict] = []
    for aid in W3_ACCOUNTS:
        body = _body_for(aid)
        pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
        live_rows.append(check_cil_curiosity_end_weight(pre_sig))
    ok = (
        end_q.get("points") == 25
        and end_q.get("end_weight") is True
        and early_q.get("points") == 10
        and all(r.get("points") == 25 for r in live_rows)
    )
    return {
        "ok": ok,
        "upgrade": "U044",
        "end_question_pts": end_q.get("points"),
        "early_question_pts": early_q.get("points"),
        "live_w3": [{"account_id": aid, "points": r.get("points"), "end_weight": r.get("end_weight")} for aid, r in zip(W3_ACCOUNTS, live_rows)],
    }


def validate_opener_ssot_acceptance() -> dict:
    """U049 acceptance — CIL and OQG share single SCRAPE_OPEN_RE import."""
    from best_loop_oqg_score_v1 import _score_fefs_persuasion  # noqa: WPS433

    scrape_body = (
        "Hi Anne,\n\nYour OSC-registered profile and leadership contact are public on trustfield.ca.\n\n"
        "Curious whether issuance proof is on your roadmap?"
    )
    cfg = _read_json(TRANSLATION)
    cil_scrape = score_conversation_interest(account_id="ocree", body=scrape_body, cfg=cfg)
    _, fefs_checks = _score_fefs_persuasion(scrape_body)
    r1 = next(c for c in fefs_checks if c.get("id") == "fefs_human_opening")
    prefix_body = "I came across your platform and wanted to reach out.\n\nCurious?"
    cil_prefix = score_conversation_interest(account_id="ocree", body=prefix_body, cfg=cfg)
    clean_body = _body_for("fundmore")
    cil_clean = score_conversation_interest(account_id="fundmore", body=clean_body, cfg=cfg)
    scrape_fail = check_scrape_open(scrape_body)
    ok = (
        scrape_fail["hard_fail"]
        and "scrape_open" in (r1.get("issues") or [])
        and any("scrape_open" in f for f in cil_scrape.get("hard_fails") or [])
        and cil_scrape.get("conversation_interest_pct") == 0
        and any("hard_fail_opener" in f for f in cil_prefix.get("hard_fails") or [])
        and not cil_clean.get("hard_fails")
        and cil_clean.get("conversation_interest_pct", 0) >= BAR
    )
    return {
        "ok": ok,
        "upgrade": "U049",
        "shared_scrape_open_re": True,
        "scrape_pattern": scrape_fail.get("matched"),
        "cil_scrape_hard_fail": any("scrape_open" in f for f in cil_scrape.get("hard_fails") or []),
        "oqg_scrape_fail": "scrape_open" in (r1.get("issues") or []),
        "prefix_opener_still_fails": any("hard_fail_opener" in f for f in cil_prefix.get("hard_fails") or []),
        "clean_w3_no_hard_fail": not cil_clean.get("hard_fails"),
        "acceptance": "One opener list SSOT",
        "check": "python3 scripts/conversation_interest_loop_v1.py --check-opener-ssot --json",
    }


def score_conversation_interest(*, account_id: str, body: str, cfg: dict) -> dict:
    checks: list[dict] = []
    total = 0
    pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
    low = pre_sig.lower()
    wc = _word_count(body)
    mode = _mode(body)

    hard_fails: list[str] = []
    for opener in cfg.get("hard_fail_openers") or []:
        if low.lstrip().startswith(opener):
            hard_fails.append(f"hard_fail_opener:{opener}")
    if check_scrape_open(pre_sig)["hard_fail"]:
        hard_fails.append("hard_fail_opener:scrape_open")
    for term in cfg.get("forbidden_in_email_one") or []:
        if term.lower() in low:
            hard_fails.append(f"forbidden_term:{term}")
    if wc > 150:
        hard_fails.append("hard_fail_word_count>150")
    if re.search(r"\b(not custody|advisory only|not payment)\b.*\b(not custody|advisory only|not payment)\b", low):
        hard_fails.append("disclaimer_stack")
    if re.search(r"\brefund\b|\bCAD \$|\bpilot.*\$", low):
        hard_fails.append("cold_pricing_refund")

    # CIL1 curiosity close (25) — U044 end-weight: question in last 30% narrative
    cil1_row = check_cil_curiosity_end_weight(pre_sig)
    cil1 = int(cil1_row["points"])
    total += cil1
    checks.append(cil1_row)

    # CIL2 human tone — no brochure (20)
    brochure = sum(1 for b in ("our platform", "we're building", "we are building", "delivers", "solution") if b in low)
    cil2 = max(0, 20 - brochure * 8)
    total += cil2
    checks.append({"id": "cil_human_tone", "points": cil2, "max": 20, "issues": [f"brochure:{brochure}"] if brochure else []})

    # CIL3 insight before pitch (20)
    product_markers = ("trustfield", "noetfield", "we build", "that's what we're")
    first_product = min((low.find(m) for m in product_markers if m in low), default=999)
    pain_cues = ("question", "harder", "boards", "prove", "evidence", "gap", "curious", "pattern")
    first_pain = min((low.find(p) for p in pain_cues if p in low), default=999)
    cil3 = 20 if first_pain < first_product else (8 if first_pain < 999 else 0)
    total += cil3
    checks.append({"id": "cil_insight_before_pitch", "points": cil3, "max": 20, "issues": [] if cil3 >= 18 else ["pitch_before_insight"]})

    # CIL4 density — one idea (15)
    paras = [p for p in re.split(r"\n\s*\n", pre_sig) if p.strip()]
    cil4 = 15 if len(paras) <= 5 else max(0, 15 - (len(paras) - 5) * 3)
    total += cil4
    checks.append({"id": "cil_density", "points": cil4, "max": 15, "issues": [] if cil4 >= 12 else ["too_many_blocks"]})

    # CIL5 brevity (10)
    modes = cfg.get("modes") or {}
    max_w = int((modes.get("B_interest_asset") or {}).get("max_words") or 140)
    if mode.startswith("A"):
        max_w = int((modes.get("A_curiosity_first") or {}).get("max_words") or 120)
    cil5 = 10 if wc <= max_w else max(0, 10 - (wc - max_w) // 10)
    total += cil5
    checks.append({"id": "cil_brevity", "points": cil5, "max": 10, "issues": [] if wc <= max_w else [f"word_count:{wc}>{max_w}"]})

    # CIL6 reply test (10)
    has_q = "?" in pre_sig
    cil2_pts = next((c.get("points") or 0 for c in checks if c.get("id") == "cil_human_tone"), 0)
    reply_ok = has_q and cil2_pts >= 12 and not hard_fails
    cil6 = 10 if reply_ok else 0
    total += cil6
    checks.append({"id": "cil_reply_test", "points": cil6, "max": 10, "issues": hard_fails or ([] if reply_ok else ["unlikely_reply"])})

    pct = 0 if hard_fails else min(100, max(0, total))
    return {
        "account_id": account_id,
        "compose_mode": mode,
        "conversation_interest_pct": pct,
        "cil_pass": pct >= BAR and not hard_fails,
        "word_count": wc,
        "hard_fails": hard_fails,
        "checks": checks,
    }


def run_cil(*, write: bool = True, account_ids: list[str] | None = None) -> dict:
    cfg = _read_json(TRANSLATION)
    ids = account_ids or list(W3_ACCOUNTS)
    artifacts: list[dict] = []
    for aid in ids:
        body = _body_for(aid)
        if not body.strip():
            artifacts.append({"account_id": aid, "conversation_interest_pct": 0, "cil_pass": False, "verdict": "IMPROVE", "next_action": f"prepare body for {aid}"})
            continue
        scored = score_conversation_interest(account_id=aid, body=body, cfg=cfg)
        verdict = "PASS" if scored["cil_pass"] else "IMPROVE"
        failures = list(scored.get("hard_fails") or [])
        for chk in scored.get("checks") or []:
            failures.extend(chk.get("issues") or [])
        next_action = _next_action(aid, scored, failures)
        artifacts.append({**scored, "verdict": verdict, "failures": failures, "next_action": next_action})

    improve_n = sum(1 for a in artifacts if a.get("verdict") == "IMPROVE")
    pass_n = sum(1 for a in artifacts if a.get("verdict") == "PASS")
    avg = round(sum(a.get("conversation_interest_pct") or 0 for a in artifacts) / len(artifacts)) if artifacts else 0
    all_pass = all(a.get("cil_pass") for a in artifacts) if artifacts else False

    row = {
        "schema": "conversation-interest-loop-receipt-v1",
        "at": _now(),
        "law": "docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md",
        "ok": all_pass,
        "verdict": "PASS" if all_pass else "IMPROVE",
        "quality_bar_pct": BAR,
        "conversation_interest_avg_pct": avg,
        "summary": {"artifacts": len(artifacts), "pass": pass_n, "improve": improve_n},
        "artifacts": artifacts,
        "conversation_interest_line": f"conversation · w3={'ready' if all_pass else f'improve({improve_n})'} · avg={avg}% · bar={BAR}",
        "next_action_only": next((a["next_action"] for a in artifacts if a.get("verdict") == "IMPROVE"), "all PASS conversation bar"),
        "command": "python3 scripts/conversation_interest_loop_v1.py --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def build_fleet_cil_receipt(*, write: bool = True) -> dict:
    """U041 — fleet receipt with per-account CIL at bar 92; sync cil_pct onto packs."""
    cfg = _read_json(TRANSLATION)
    accounts: list[dict] = []
    for aid in FLEET_ACCOUNTS:
        body = _body_for(aid)
        if not body.strip():
            row = {
                "account_id": aid,
                "conversation_interest_pct": 0,
                "cil_pass": False,
                "cil_pct": None,
                "pack_sync": {"ok": False, "reason": "missing_body"},
            }
            accounts.append(row)
            continue
        scored = score_conversation_interest(account_id=aid, body=body, cfg=cfg)
        sync = sync_cil_to_pack(account_id=aid, scored=scored, write=write)
        accounts.append(
            {
                "account_id": aid,
                "conversation_interest_pct": scored.get("conversation_interest_pct"),
                "cil_pass": scored.get("cil_pass"),
                "cil_pct": sync.get("cil_pct"),
                "quality_bar_pct": BAR,
                "pack_sync": sync,
            }
        )
    all_pass = all(a.get("cil_pass") for a in accounts) if accounts else False
    avg = round(sum(a.get("conversation_interest_pct") or 0 for a in accounts) / len(accounts)) if accounts else 0
    out = {
        "schema": "cil-fleet-receipt-v1",
        "at": _now(),
        "upgrade": "U041",
        "ok": all_pass,
        "quality_bar_pct": BAR,
        "conversation_interest_avg_pct": avg,
        "accounts": accounts,
        "fleet_view": "per-account CIL on pack — fundmore + ocree",
        "cil_fleet_line": f"cil-fleet · avg={avg}% · bar={BAR} · {'PASS' if all_pass else 'IMPROVE'}",
        "command": "python3 scripts/conversation_interest_loop_v1.py --fleet --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        FLEET_RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        run_cil(write=True, account_ids=list(FLEET_ACCOUNTS))
    return out


def check_cil_fleet_pack(path: Path | None = None) -> dict:
    """U041 acceptance — fundmore/ocree CIL on pack + fleet receipt per account."""
    path = path or FLEET_RECEIPT
    fleet = _read_json(path)
    fleet_accounts = fleet.get("accounts") or []
    fleet_ids = {str(a.get("account_id") or "") for a in fleet_accounts}
    missing_fleet = [aid for aid in FLEET_ACCOUNTS if aid not in fleet_ids]
    pack_rows: list[dict] = []
    missing_pack: list[str] = []
    for aid in FLEET_ACCOUNTS:
        pack = _read_json(_pack_path(aid))
        cil_pct = pack.get("cil_pct")
        if cil_pct is None:
            missing_pack.append(aid)
        pack_rows.append({"account_id": aid, "cil_pct": cil_pct, "pack_path": str(_pack_path(aid))})
    per_account = all(
        isinstance(a.get("conversation_interest_pct"), (int, float)) and a.get("quality_bar_pct") == BAR
        for a in fleet_accounts
        if str(a.get("account_id") or "") in FLEET_ACCOUNTS
    )
    return {
        "ok": not missing_fleet and not missing_pack and per_account and fleet.get("schema") == "cil-fleet-receipt-v1",
        "upgrade": "U041",
        "missing_fleet_accounts": missing_fleet,
        "missing_pack_cil": missing_pack,
        "pack_rows": pack_rows,
        "fleet_path": str(path),
        "quality_bar_pct": BAR,
        "per_account_bar": per_account,
    }


def validate_cil_fleet_surfaces_acceptance() -> dict:
    """U050 acceptance — cil_fleet_pct quoted on agent-live-surfaces."""
    fleet = build_fleet_cil_receipt(write=True)
    avg = fleet.get("conversation_interest_avg_pct")
    from disk_live_wire_sync_v1 import sync_disk_live_wire  # noqa: WPS433

    sync_disk_live_wire(role="worker", skip_factory=True)
    surfaces = _read_json(SINA / "agent-live-surfaces-v1.json")
    quoted_pct = surfaces.get("cil_fleet_pct")
    quoted_line = str(surfaces.get("cil_fleet_line") or "")
    ok = (
        quoted_pct == avg
        and quoted_line == fleet.get("cil_fleet_line")
        and f"avg={avg}%" in quoted_line
    )
    return {
        "ok": ok,
        "upgrade": "U050",
        "fleet_avg_pct": avg,
        "surfaces_cil_fleet_pct": quoted_pct,
        "surfaces_cil_fleet_line": quoted_line,
        "acceptance": "cil_fleet_pct quoted",
        "surfaces_path": str(SINA / "agent-live-surfaces-v1.json"),
        "check": "python3 scripts/conversation_interest_loop_v1.py --check-cil-fleet-surfaces --json",
    }


def _next_action(aid: str, scored: dict, failures: list[str]) -> str:
    if scored.get("cil_pass"):
        return "hold — re-run CIL after any edit"
    if any("hard_fail_opener" in f for f in failures):
        return f"remove banned opener · rewrite curiosity-first · re-pack · re-CIL"
    if any("forbidden_term" in f for f in failures):
        return f"translate engineering terms per factory-email-translation-v1.json · re-CIL"
    return "one bounded conversation fix · re-run conversation_interest_loop_v1.py --json"


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "conversation-interest-loop-receipt-v1":
        row = run_cil(write=True)
    return {
        "schema": "worker-hub-conversation-interest-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "verdict": row.get("verdict"),
        "conversation_interest_line": row.get("conversation_interest_line"),
        "next_action_only": row.get("next_action_only"),
        "conversation_interest_avg_pct": row.get("conversation_interest_avg_pct"),
        "summary": row.get("summary"),
        "artifacts": row.get("artifacts") or [],
        "law": row.get("law"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Conversation Interest Loop")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--fleet", action="store_true", help="U041 — fleet receipt + sync cil_pct to packs")
    ap.add_argument("--check-fleet-pack", action="store_true", help="U041 acceptance — fundmore/ocree CIL on pack")
    ap.add_argument("--check-curiosity-end-weight", action="store_true", help="U044 — question in last 30% narrative bonus")
    ap.add_argument("--check-opener-ssot", action="store_true", help="U049 — CIL hard-fail openers share SCRAPE_OPEN_RE with OQG")
    ap.add_argument("--check-cil-fleet-surfaces", action="store_true", help="U050 — cil_fleet_pct quoted on agent-live-surfaces")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    if args.check_fleet_pack:
        row = check_cil_fleet_pack()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_fleet_pack:", "PASS" if row.get("ok") else row.get("missing_pack_cil") or row.get("missing_fleet_accounts"))
        return 0 if row.get("ok") else 1
    if args.check_curiosity_end_weight:
        row = validate_cil_curiosity_end_weight_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_curiosity_end_weight:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_opener_ssot:
        row = validate_opener_ssot_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_opener_ssot:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_cil_fleet_surfaces:
        row = validate_cil_fleet_surfaces_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_cil_fleet_surfaces:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.fleet:
        row = build_fleet_cil_receipt(write=not args.no_write)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(row.get("cil_fleet_line", ""))
        return 0 if row.get("ok") else 1
    row = run_cil(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("conversation_interest_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
