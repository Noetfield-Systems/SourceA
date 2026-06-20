#!/usr/bin/env python3
"""Response Reality Layer (RRL) — simulate recipient reaction in <10s read.

Machine simulation only — NOT ship authority. Sina read remains final.
Pass: reaction D (curious) or E (would_reply) only.

Law: data/response-reality-layer-v1.json
Receipt: ~/.sina/response-reality-layer-receipt-v1.json
History: ~/.sina/response-reality-layer-history-v1.jsonl (append-only · last 10 per account)
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "response-reality-layer-v1.json"
RECEIPT = SINA / "response-reality-layer-receipt-v1.json"
HISTORY = SINA / "response-reality-layer-history-v1.jsonl"
CIL_RECEIPT = SINA / "conversation-interest-loop-receipt-v1.json"
PASS_REACTIONS = frozenset({"D", "E"})
MAX_HISTORY_PER_ACCOUNT = 10


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _read_body(body: str | None, account_id: str | None) -> str:
    if body:
        return body
    if account_id:
        pack = SINA / "outbound" / f"w3-canada-{account_id}" / "body.txt"
        if pack.is_file():
            return pack.read_text(encoding="utf-8")
        ap = ROOT / "data" / "icp-compile" / f"{account_id}-approved-v1.txt"
        if ap.is_file():
            return ap.read_text(encoding="utf-8")
    return ""


def _read_history_lines() -> list[dict]:
    if not HISTORY.is_file():
        return []
    rows: list[dict] = []
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _write_history_lines(rows: list[dict]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text("\n".join(json.dumps(r, separators=(",", ":")) for r in rows) + "\n", encoding="utf-8")


def append_history(entry: dict) -> dict:
    """Append sim entry; retain last MAX_HISTORY_PER_ACCOUNT per account_id."""
    account_id = str(entry.get("account_id") or "unknown")
    rows = _read_history_lines()
    rows.append(entry)
    by_acct: dict[str, list[dict]] = {}
    for r in rows:
        aid = str(r.get("account_id") or "unknown")
        by_acct.setdefault(aid, []).append(r)
    trimmed: list[dict] = []
    for aid, items in by_acct.items():
        trimmed.extend(items[-MAX_HISTORY_PER_ACCOUNT:])
    trimmed.sort(key=lambda x: x.get("at") or "")
    _write_history_lines(trimmed)
    acct_rows = [r for r in trimmed if str(r.get("account_id") or "unknown") == account_id]
    return {
        "history_path": str(HISTORY),
        "account_id": account_id,
        "count": len(acct_rows),
        "last_10": acct_rows[-MAX_HISTORY_PER_ACCOUNT:],
    }


def history_for_account(account_id: str) -> list[dict]:
    aid = str(account_id)
    return [r for r in _read_history_lines() if str(r.get("account_id") or "") == aid][-MAX_HISTORY_PER_ACCOUNT:]


def _suggest_c_fix(signals: list[str]) -> str:
    if "vendor_paragraph" in signals:
        return "Cut the vendor paragraph — lead with their constraint, not TrustField producing."
    if any(s.startswith("skeptical:") for s in signals):
        return "Remove compliance pitch phrasing — one concrete scenario question instead."
    if "mass_outreach_opener" in signals:
        return "Replace mass opener with a named scenario from their world."
    if "no_icp_anchor" in signals:
        return "Name at least three anchors from their world in the first 300 chars."
    return "Shorten to one scenario + one curious question — drop vendor framing."


def _cil_disagreement(rrl_reaction: str) -> dict | None:
    cil = _read_json(CIL_RECEIPT)
    if not cil or cil.get("schema") != "conversation-interest-loop-receipt-v1":
        return None
    cil_score = float(cil.get("interest_score") or cil.get("score") or 0)
    cil_high = cil_score >= 70 or str(cil.get("verdict") or "").upper() == "HIGH"
    if cil_high and rrl_reaction in ("A", "B", "C"):
        return {
            "alert": True,
            "reason": "cil_high_rrl_skeptical",
            "cil_score": cil_score,
            "rrl_reaction": rrl_reaction,
            "line": f"CIL/RRL disagree · CIL high · RRL {rrl_reaction} — over-optimistic conversation interest",
        }
    return {"alert": False, "cil_score": cil_score, "rrl_reaction": rrl_reaction}


def simulate_reaction(
    body: str,
    *,
    cfg: dict | None = None,
    company: str = "",
    icp_world: list[str] | None = None,
) -> dict:
    """Classify A/B/C/D/E from recipient POV heuristics."""
    cfg = cfg or _read_json(CONFIG)
    weights = cfg.get("scoring_weights") or {}
    vendor_penalty = int(weights.get("vendor_paragraph_penalty") or 3)
    icp_min_pass = int(weights.get("icp_anchors_min_pass") or 3)
    read_time_sec = int((cfg.get("simulation") or {}).get("read_time_seconds") or 10)
    words_per_sec = float(weights.get("words_per_sec") or 15.0)

    pre = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
    low = pre.lower()
    words = len(re.findall(r"[A-Za-z0-9']+", pre))

    signals: list[str] = []
    scores = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}

    if not any(p in low for p in (cfg.get("curious_phrases") or [])) and "?" not in pre:
        scores["A"] += 3
        signals.append("no_curiosity_hook")
    company_l = (company or "").lower()
    icp = [w.lower() for w in (icp_world or [])]
    named = sum(1 for w in icp if w in low) + (1 if company_l and company_l.split()[0] in low else 0)
    if named == 0 and not re.search(r"\b(winnipeg|polymorph|polymesh|mortgage|fundmore|ocree)\b", low):
        scores["A"] += 2
        signals.append("no_icp_anchor")
    if re.search(r"\bi came across\b|\bhope you.re well\b", low):
        scores["A"] += 4
        signals.append("mass_outreach_opener")

    for phrase in cfg.get("confusion_phrases") or []:
        if phrase.lower() in low:
            scores["B"] += 2
            signals.append(f"confusion:{phrase}")
    if words > 160:
        scores["B"] += 1
        signals.append("too_long_10s_read")

    max_words = int(read_time_sec * words_per_sec)
    if words > max_words:
        scores["B"] += 2
        signals.append(f"read_time_mismatch:{words}w>{max_words}w@{read_time_sec}s")

    for phrase in cfg.get("skeptical_phrases") or []:
        if phrase.lower() in low:
            scores["C"] += 2
            signals.append(f"skeptical:{phrase}")
    if re.search(r"\btrustfield\b.*\bproducing\b|\bwe.ve been focusing\b", low):
        scores["C"] += vendor_penalty
        signals.append("vendor_paragraph")

    if "?" in pre:
        scores["D"] += 2
    if any(p in low for p in (cfg.get("curious_phrases") or [])):
        scores["D"] += 2
    if named >= 2 or re.search(r"\b(collaboratory|winnipeg|polymesh|mortgage|copilot)\b", low):
        scores["D"] += 2
        signals.append("specific_scenario")
    if re.search(r"\bafter the fact\b|\breconstruct\b|\bwhat actually happened\b", low):
        scores["D"] += 1

    if scores["D"] >= 4 and scores["C"] <= 2 and scores["A"] <= 2:
        scores["E"] += 2
    if "?" in pre and named >= 1 and scores["C"] <= 3:
        scores["E"] += 2
    if words <= 120 and scores["C"] <= 2:
        scores["E"] += 1

    order = ["C", "A", "B", "D", "E"]
    reaction = max(order, key=lambda k: (scores[k], -order.index(k)))
    if scores["E"] >= scores["D"] + 2 and scores["C"] <= 2:
        reaction = "E"
    elif scores["D"] >= max(scores["A"], scores["B"], scores["C"]) + 1:
        reaction = "D" if scores["E"] < scores["D"] + 2 else "E"
    elif scores["C"] >= 3:
        reaction = "C"
    elif scores["A"] >= 3:
        reaction = "A"
    elif scores["B"] >= 3:
        reaction = "B"

    if named < icp_min_pass and reaction in ("D", "E"):
        reaction = "C"
        signals.append(f"icp_anchors_below_min:{named}<{icp_min_pass}")

    reactions = cfg.get("reactions") or {}
    meta = reactions.get(reaction) or {}
    rrl_pass = reaction in PASS_REACTIONS

    interpretation = {
        "A": "Skim → archive. Feels like outreach.",
        "B": "Re-read once → still unclear → delete.",
        "C": "Reads as compliance/vendor pitch → low trust.",
        "D": "Pauses — interesting constraint — might reply if time.",
        "E": "Likely short reply or calendar ask.",
    }
    e_vs_d = (cfg.get("reaction_ladder") or {}).get(
        "E_vs_D",
        "E = would_reply (stronger) · D = curious pause only — both pass · E preferred for send",
    )

    return {
        "reaction": reaction,
        "reaction_label": meta.get("label", reaction),
        "rrl_pass": rrl_pass,
        "read_time_target_sec": read_time_sec,
        "word_count": words,
        "read_time_word_cap": max_words,
        "read_time_flag": words > max_words,
        "icp_anchors": named,
        "icp_anchors_min_pass": icp_min_pass,
        "recipient_interpretation": interpretation.get(reaction, ""),
        "reaction_ladder_note": e_vs_d,
        "signals": signals[:12],
        "scores": scores,
        "pass_reactions": sorted(PASS_REACTIONS),
        "c_fix_one_line": _suggest_c_fix(signals) if reaction == "C" else "",
    }


def run_rrl(
    *,
    body: str | None = None,
    account_id: str | None = None,
    company: str = "",
    icp_world: list[str] | None = None,
    brand: str = "",
    write: bool = True,
) -> dict:
    cfg = _read_json(CONFIG)
    text = _read_body(body, account_id)
    if not text.strip():
        return {"ok": False, "error": "missing body"}

    if account_id and not icp_world:
        forge = _read_json(ROOT / "data" / "icp-compile" / f"{account_id}-v1.json")
        prof = forge.get("icp_profile") or {}
        company = company or str(prof.get("company") or forge.get("company") or "")
        icp_world = prof.get("their_world") or []
        brand = brand or str(forge.get("brand_route") or forge.get("brand") or "")

    sim = simulate_reaction(text, cfg=cfg, company=company, icp_world=icp_world)
    cil_alert = _cil_disagreement(sim["reaction"])

    if sim["rrl_pass"]:
        next_action = "hold — RRL D/E · await Sina read"
    elif sim["reaction"] == "C":
        next_action = sim.get("c_fix_one_line") or "rewrite — skeptical tone"
    else:
        next_action = f"rewrite for curious/reply reaction — currently {sim['reaction']} ({sim['reaction_label']})"

    row = {
        "schema": "response-reality-layer-receipt-v1",
        "at": _now(),
        "account_id": account_id,
        "brand": brand,
        "ok": sim["rrl_pass"],
        "verdict": "PASS" if sim["rrl_pass"] else "REJECT",
        "rrl_line": f"rrl · {sim['reaction']}({sim['reaction_label']}) · pass={sim['rrl_pass']}",
        "simulation": sim,
        "cil_disagreement": cil_alert,
        "ship_authority": "sina_read_score_pct only — RRL is machine reaction sim",
        "next_action_only": next_action,
        "command": "python3 scripts/response_reality_layer_v1.py --account <id> --json",
    }

    if write and account_id:
        hist_entry = {
            "at": row["at"],
            "account_id": account_id,
            "brand": brand,
            "reaction": sim["reaction"],
            "rrl_pass": sim["rrl_pass"],
            "word_count": sim["word_count"],
            "icp_anchors": sim["icp_anchors"],
        }
        row["history"] = append_history(hist_entry)

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    rec = _read_json(RECEIPT)
    hist_count = len(_read_history_lines())
    fleet: dict = {}
    try:
        from rrl_fleet_glance_v1 import fleet_glance  # noqa: WPS433

        fleet = fleet_glance()
    except Exception as exc:
        fleet = {"ok": False, "error": str(exc)}
    return {
        "schema": "worker-hub-rrl-v1",
        "ok": bool(rec),
        "rrl_line": rec.get("rrl_line", "rrl — run response_reality_layer_v1.py"),
        "reaction_ladder_note": (rec.get("simulation") or {}).get("reaction_ladder_note"),
        "next_action_only": rec.get("next_action_only"),
        "cil_disagreement": rec.get("cil_disagreement"),
        "history_count": hist_count,
        "fleet": fleet,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Response Reality Layer")
    ap.add_argument("--account")
    ap.add_argument("--body-file")
    ap.add_argument("--brand")
    ap.add_argument("--history", action="store_true", help="Print history for --account")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    if args.history:
        rows = history_for_account(args.account or "")
        out = {"account_id": args.account, "count": len(rows), "history": rows}
        print(json.dumps(out, indent=2))
        return 0
    body = None
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    row = run_rrl(
        body=body,
        account_id=args.account,
        brand=args.brand or "",
        write=not args.no_write,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("rrl_line", row.get("error", "")))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
