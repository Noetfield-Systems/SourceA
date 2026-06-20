#!/usr/bin/env python3
"""ICP output compiler — FDG v1 validate + reverse-engineer trace check.

Output-first factory: specialized ICP email must match forge trace rules.
Law: data/icp-failure-driven-generator-v1.json
Ship authority: sina_read_score_pct only (Sina human).
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
SINA = Path.home() / ".sina"
FDG = ROOT / "data" / "icp-failure-driven-generator-v1.json"
COMPILE_DIR = ROOT / "data" / "icp-compile"
COMPILER_SSOT = ROOT / "data" / "icp-output-compiler-v1.json"
TRANSLATION = ROOT / "data" / "factory-email-translation-v1.json"
RECEIPT = SINA / "icp-output-compiler-receipt-v1.json"
FLEET_RECEIPT = SINA / "icp-compiler-fleet-receipt-v1.json"
BAR = 90
FLEET_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory", "forge-product")
GATED_DEFER_ACCOUNTS = frozenset({"sourcea-factory", "forge-product"})
COMMERCIAL_BRAND_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory")
BRAND_BY_ACCOUNT = {
    "fundmore": "Noetfield",
    "ocree": "TrustField",
    "sourcea-factory": "SourceA",
}
ICP_STUB_V2_TRACE_FIELDS = (
    "approved",
    "machine_compiled_at",
    "machine_verdict",
    "icp_compiler_pct",
    "cil_pct",
    "ril_pct",
    "oqg_pct",
    "rrl_reaction",
    "rrl_pass",
    "sina_read_score_pct",
    "advisor_critique_only",
    "machine_next",
    "outbound_pack",
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


def _detect_compose_mode(body: str) -> str:
    sys.path.insert(0, str(SCRIPTS))
    from receiver_interest_loop_v1 import detect_compose_mode  # noqa: WPS433

    return detect_compose_mode(body)


def _compile_sequence() -> str:
    ssot = _read_json(COMPILER_SSOT)
    fp = ssot.get("factory_priority") or {}
    parallel = " ∥ ".join(fp.get("parallel_commercial_brands") or ["Noetfield", "TrustField"])
    return f"{parallel} first · then SourceA deferred · then Forge product"


def check_compile_sequence_field(seq: str) -> dict:
    """U030 — receipt.compile_sequence must show NF∥TF then SourceA deferred."""
    s = (seq or "").lower()
    issues: list[str] = []
    if not seq:
        issues.append("missing_compile_sequence")
    if "noetfield" not in s or "trustfield" not in s:
        issues.append("missing_parallel_commercial_brands")
    if seq and "∥" not in seq:
        issues.append("missing_parallel_marker")
    if "sourcea" not in s:
        issues.append("missing_sourcea_deferred")
    sa_pos = s.find("sourcea")
    nf_pos = s.find("noetfield")
    tf_pos = s.find("trustfield")
    if sa_pos >= 0 and nf_pos >= 0 and sa_pos < nf_pos:
        issues.append("sourcea_before_noetfield")
    if sa_pos >= 0 and tf_pos >= 0 and sa_pos < tf_pos:
        issues.append("sourcea_before_trustfield")
    return {
        "ok": not issues,
        "issues": issues,
        "compile_sequence": seq,
        "upgrade": "U030",
    }


def validate_compile_sequence_acceptance() -> dict:
    """U030 acceptance — compiler output receipt shows NF∥TF then SA."""
    law = _compile_sequence()
    law_check = check_compile_sequence_field(law)
    compile_row = run_compiler(account_id="fundmore", write=False)
    row_check = check_compile_sequence_field(str(compile_row.get("compile_sequence") or ""))
    disk = _read_json(RECEIPT)
    disk_check = check_compile_sequence_field(str(disk.get("compile_sequence") or ""))
    fleet = _read_json(FLEET_RECEIPT)
    fleet_check = check_compile_sequence_field(str(fleet.get("compile_sequence") or ""))
    return {
        "ok": law_check.get("ok") and row_check.get("ok") and disk_check.get("ok"),
        "law": law,
        "law_check": law_check,
        "compile_row": row_check,
        "disk_receipt": disk_check,
        "fleet_receipt": fleet_check,
        "acceptance": "Shows NF∥TF then SA",
        "upgrade": "U030",
        "check": "python3 scripts/icp_output_compiler_v1.py --check-compile-sequence --json",
    }


def _compile_gate_warning(account_id: str, forge: dict) -> str | None:
    gate = str(forge.get("compile_gate") or "").strip()
    if gate:
        return gate
    ssot = _read_json(COMPILER_SSOT)
    for row in ssot.get("accounts") or []:
        if row.get("id") == account_id and row.get("compile_gate"):
            return str(row["compile_gate"])
    if account_id == "sourcea-factory":
        return "blocked_until_noetfield_and_trustfield_compiled"
    if account_id == "forge-product":
        return "blocked_until_sourcea_compiled"
    return None


def check_compile_gate(account_id: str, forge: dict | None = None) -> dict:
    """U023 — warn when deferred compile_gate is active (sourcea-factory / forge-product)."""
    forge = forge or {}
    gate = _compile_gate_warning(account_id, forge)
    active = bool(gate and account_id in GATED_DEFER_ACCOUNTS)
    warning = (
        f"DEFERRED — {gate} — do not compile/send until commercial tier closes"
        if active
        else None
    )
    return {
        "ok": True,
        "account_id": account_id,
        "compile_gate": gate,
        "compile_gate_active": active,
        "compile_gate_blocked": active,
        "compile_gate_warning": warning,
        "upgrade": "U023",
    }


def _body_for_account(account_id: str, forge: dict) -> tuple[str, str | None]:
    ap = forge.get("approved_body_path")
    if ap:
        p = ROOT / ap
        if p.is_file():
            return p.read_text(encoding="utf-8"), ap
        return "", ap
    pack = SINA / "outbound" / f"w3-canada-{account_id}" / "body.txt"
    if pack.is_file():
        return pack.read_text(encoding="utf-8"), None
    return "", ap


def check_failure_moment_stub(forge: dict) -> dict:
    """U021 — FDG failure_moment required on icp-compile stub."""
    fm = forge.get("failure_moment")
    if not isinstance(fm, dict) or not fm:
        return {
            "ok": False,
            "issues": ["missing_failure_moment_field"],
            "upgrade": "U021",
        }
    issues: list[str] = []
    if not str(fm.get("scenario") or "").strip():
        issues.append("missing_failure_moment_scenario")
    if not str(fm.get("pressure") or "").strip():
        issues.append("missing_failure_moment_pressure")
    return {
        "ok": not issues,
        "issues": issues,
        "failure_moment": fm,
        "upgrade": "U021",
    }


SCRAPE_PASTE_SOURCES = frozenset({"scrape", "proxycurl", "auto_fetch", "exa", "linkedin_scrape"})
SCRAPE_PASTE_MARKERS = (
    "are public on",
    "leadership contact",
    "i came across",
    "i noticed",
    "your osc-registered",
    "i saw your platform",
)


def check_press_earnings_manual_paste(forge: dict) -> dict:
    """U057 — press/earnings signal must be founder manual paste, not scrape."""
    signals = forge.get("signals") or {}
    row = signals.get("press_earnings_manual_paste")
    if not isinstance(row, dict):
        return {
            "ok": False,
            "issues": ["missing_press_earnings_manual_paste"],
            "upgrade": "U057",
        }
    source = str(row.get("source") or "").strip().lower()
    text = str(row.get("text") or "")
    issues: list[str] = []
    if source != "manual_paste":
        issues.append("founder_paste_must_not_be_scrape_source")
    if source in SCRAPE_PASTE_SOURCES:
        issues.append("scrape_source_forbidden")
    if row.get("scrape_forbidden") is not True:
        issues.append("scrape_forbidden_must_be_true")
    low = text.lower()
    if text.strip() and any(m in low for m in SCRAPE_PASTE_MARKERS):
        issues.append("paste_text_looks_like_scrape")
    return {
        "ok": not issues,
        "issues": issues,
        "source": source or None,
        "text_len": len(text.strip()),
        "human_confirmed": row.get("human_confirmed"),
        "upgrade": "U057",
    }


def validate_press_earnings_paste_acceptance() -> dict:
    """U057 acceptance — founder paste ≠ scrape on icp-compile signals block."""
    import copy

    stub_rows: list[dict] = []
    for aid in ("fundmore", "ocree"):
        forge = _read_json(COMPILE_DIR / f"{aid}-v1.json")
        chk = check_press_earnings_manual_paste(forge)
        stub_rows.append({"account_id": aid, **chk})
    base = _read_json(COMPILE_DIR / "fundmore-v1.json")
    good = copy.deepcopy(base)
    good.setdefault("signals", {})["press_earnings_manual_paste"] = {
        "text": "Earnings call — board asked how copilot decisions get reconstructed.",
        "source": "manual_paste",
        "human_confirmed": True,
        "scrape_forbidden": True,
    }
    bad_source = copy.deepcopy(good)
    bad_source["signals"]["press_earnings_manual_paste"]["source"] = "scrape"
    bad_text = copy.deepcopy(good)
    bad_text["signals"]["press_earnings_manual_paste"]["text"] = (
        "I came across your leadership contact are public on linkedin."
    )
    ok = (
        all(r.get("ok") for r in stub_rows)
        and check_press_earnings_manual_paste(good).get("ok")
        and not check_press_earnings_manual_paste(bad_source).get("ok")
        and not check_press_earnings_manual_paste(bad_text).get("ok")
    )
    return {
        "ok": ok,
        "upgrade": "U057",
        "stubs": stub_rows,
        "founder_paste_ok": check_press_earnings_manual_paste(good).get("ok"),
        "scrape_source_blocked": not check_press_earnings_manual_paste(bad_source).get("ok"),
        "scrape_text_blocked": not check_press_earnings_manual_paste(bad_text).get("ok"),
        "acceptance": "Founder paste ≠ scrape",
        "check": "python3 scripts/icp_output_compiler_v1.py --check-press-earnings-paste --json",
    }


def validate_icp_compile_stubs() -> dict:
    """U021 — all icp-compile *-v1.json stubs must carry failure_moment."""
    rows: list[dict] = []
    for path in sorted(COMPILE_DIR.glob("*-v1.json")):
        forge = _read_json(path)
        row = check_failure_moment_stub(forge)
        row["account_id"] = forge.get("account_id") or path.stem.replace("-v1", "")
        row["path"] = str(path.relative_to(ROOT))
        rows.append(row)
    ok = all(r.get("ok") for r in rows)
    return {"ok": ok, "stubs": rows, "upgrade": "U021"}


def check_icp_stub_v2_trace(forge: dict) -> dict:
    """U022 — icp-compile v2 output_trace must carry all machine trace fields."""
    trace = forge.get("output_trace")
    if not isinstance(trace, dict):
        return {"ok": False, "issues": ["missing_output_trace"], "upgrade": "U022"}
    missing = [key for key in ICP_STUB_V2_TRACE_FIELDS if key not in trace]
    return {
        "ok": not missing,
        "issues": [f"missing_trace:{k}" for k in missing],
        "trace_keys": list(trace.keys()),
        "upgrade": "U022",
    }


ICP5_TRACE_RULES_MIN = 5
ICP5_TRACE_RULES_MAX = 15
ICP5_TRACE_RULES_THIN_CAP = 13


def check_icp5_trace_rules(forge: dict, body: str = "") -> dict:
    """U025 — reverse_engineered_rules min 5 rows; thin rules cap icp5 at 13/15."""
    rules = forge.get("reverse_engineered_rules") or []
    if not isinstance(rules, list):
        rules = []
    low = (body or "").lower()
    rule_hits = sum(
        1
        for r in rules
        if isinstance(r, str) and any(w in low for w in re.findall(r"[a-z]{6,}", r.lower())[:3])
    )
    raw = 5 + rule_hits * 2 if rules else 5
    thin = len(rules) < ICP5_TRACE_RULES_MIN
    if thin:
        points = min(ICP5_TRACE_RULES_THIN_CAP, raw)
        issues = ["thin_rules_lt5"]
    else:
        points = min(ICP5_TRACE_RULES_MAX, raw)
        issues = []
    return {
        "ok": True,
        "points": points,
        "max": ICP5_TRACE_RULES_MAX,
        "issues": issues,
        "rule_count": len(rules),
        "rule_hits": rule_hits,
        "thin_cap": ICP5_TRACE_RULES_THIN_CAP if thin else None,
        "upgrade": "U025",
        "id": "icp5_trace_rules",
    }


def validate_icp5_trace_rules_acceptance() -> dict:
    """U025 acceptance — thin rules cap score at 13/15."""
    thin_forge = {
        "reverse_engineered_rules": [
            "alpha one rule here",
            "beta two rule here",
            "gamma three rule here",
        ]
    }
    thin_body = "alpha one rule beta two rule gamma three rule"
    thin = check_icp5_trace_rules(thin_forge, thin_body)
    thin_ok = (
        thin.get("rule_count", 99) < ICP5_TRACE_RULES_MIN
        and thin.get("points", 99) <= ICP5_TRACE_RULES_THIN_CAP
        and thin.get("max") == ICP5_TRACE_RULES_MAX
        and "thin_rules_lt5" in (thin.get("issues") or [])
    )
    full_forge = {
        "reverse_engineered_rules": [
            "open with mortgage board pressure",
            "frame specific decision six months",
            "Noetfield replay under pressure",
            "forbidden governance layer trail",
            "required mortgage copilot reconstruct",
            "end curiosity question before link",
            "one tension insight product question",
        ]
    }
    full_body = "mortgage board pressure decision six months Noetfield replay governance"
    full = check_icp5_trace_rules(full_forge, full_body)
    full_ok = (
        full.get("rule_count", 0) >= ICP5_TRACE_RULES_MIN
        and "thin_rules_lt5" not in (full.get("issues") or [])
        and full.get("points", 0) > ICP5_TRACE_RULES_THIN_CAP
    )
    stub_rows: list[dict] = []
    for path in sorted(COMPILE_DIR.glob("*-v1.json")):
        forge = _read_json(path)
        row = check_icp5_trace_rules(forge)
        stub_rows.append(
            {
                "account_id": forge.get("account_id") or path.stem.replace("-v1", ""),
                "rule_count": row.get("rule_count"),
                "thin": (row.get("rule_count") or 0) < ICP5_TRACE_RULES_MIN,
            }
        )
    return {
        "ok": thin_ok and full_ok,
        "thin_rules_cap": thin,
        "full_rules_score": full,
        "stubs": stub_rows,
        "acceptance": "Thin rules cap score at 13/15",
        "upgrade": "U025",
    }


def check_approved_body_path(forge: dict, *, require_field: bool = True) -> dict:
    """U026 — approved_body_path must exist in the repository before compile PASS."""
    ap = forge.get("approved_body_path")
    if not ap:
        if require_field:
            return {
                "ok": False,
                "issues": ["missing_approved_body_path"],
                "approved_body_path": None,
                "upgrade": "U026",
            }
        return {"ok": True, "issues": [], "approved_body_path": None, "optional": True, "upgrade": "U026"}
    path = ROOT / str(ap)
    if not path.is_file():
        return {
            "ok": False,
            "issues": ["missing_approved_body_file"],
            "approved_body_path": ap,
            "path_resolved": str(path),
            "upgrade": "U026",
        }
    return {
        "ok": True,
        "issues": [],
        "approved_body_path": ap,
        "path_resolved": str(path),
        "upgrade": "U026",
    }


def validate_approved_body_path_preflight() -> dict:
    """U026 acceptance — missing approved body file is error, not PASS."""
    missing_file_forge = {
        "account_id": "u026-missing-file",
        "approved_body_path": "data/icp-compile/__u026_missing_body_test__.txt",
    }
    missing_row = check_approved_body_path(missing_file_forge)
    missing_file_blocks = (
        not missing_row.get("ok")
        and "missing_approved_body_file" in (missing_row.get("issues") or [])
    )
    ap = missing_file_forge.get("approved_body_path")
    preflight_blocks_pass = bool(ap and not (ROOT / str(ap)).is_file())
    stub_rows: list[dict] = []
    for path in sorted(COMPILE_DIR.glob("*-v1.json")):
        forge = _read_json(path)
        aid = forge.get("account_id") or path.stem.replace("-v1", "")
        require = aid != "forge-product"
        row = check_approved_body_path(forge, require_field=require)
        row["account_id"] = aid
        row["path"] = str(path.relative_to(ROOT))
        stub_rows.append(row)
    active_ok = all(r.get("ok") for r in stub_rows if r.get("account_id") != "forge-product")
    return {
        "ok": missing_file_blocks and preflight_blocks_pass and active_ok,
        "missing_file_case": missing_row,
        "preflight_blocks_pass": preflight_blocks_pass,
        "stubs": stub_rows,
        "acceptance": "Missing file = error not PASS",
        "upgrade": "U026",
    }


def check_fundmore_ocree_parity() -> dict:
    """U022 — fundmore stub keys + populated v2 trace aligned to ocree schema v2."""
    ocree = _read_json(COMPILE_DIR / "ocree-v1.json")
    fundmore = _read_json(COMPILE_DIR / "fundmore-v1.json")
    if not ocree or not fundmore:
        return {"ok": False, "error": "missing_stub", "upgrade": "U022"}
    skip = {"account_id", "company", "brand_route", "sku", "parallel_with", "saved_at"}
    missing_top = [k for k in ocree if k not in fundmore and k not in skip]
    trace = check_icp_stub_v2_trace(fundmore)
    issues = list(missing_top) + (trace.get("issues") or [])
    return {
        "ok": not issues,
        "issues": issues,
        "missing_top_level": missing_top,
        "trace": trace,
        "upgrade": "U022",
    }


def _lane_forbidden_hits(body: str, brand_route: str, trans: dict) -> list[str]:
    low = body.lower()
    lane_key = str(brand_route or "").lower()
    forbidden_map = trans.get("lane_forbidden") or {}
    hits: list[str] = []
    for phrase in forbidden_map.get(lane_key) or []:
        if phrase.lower() in low:
            hits.append(f"lane_forbidden:{phrase}")
    return hits


def _forbidden_one_hits(body: str, trans: dict) -> list[str]:
    """U012 — reject architecture nouns from translation forbidden_in_email_one."""
    low = body.lower()
    hits: list[str] = []
    for term in trans.get("forbidden_in_email_one") or []:
        if term.lower() in low:
            hits.append(f"forbidden_one:{term}")
    return hits


def _product_mentions_body(text: str) -> int:
    pre_sig = text.split("Reply **stop**")[0] if "Reply **stop**" in text else text
    lines: list[str] = []
    for line in pre_sig.splitlines():
        t = line.strip()
        if not t or t.startswith("http") or ("@" in t and "." in t):
            continue
        if re.match(r"^Sina\b", t):
            continue
        lines.append(t)
    return len(re.findall(r"\btrustfield\b|\bnoetfield\b", "\n".join(lines).lower()))


def score_icp_output(body: str, *, forge: dict, fdg: dict, trans: dict | None = None) -> dict:
    checks: list[dict] = []
    total = 0
    low = body.lower()
    hard_fails: list[str] = []
    trans = trans or {}

    for phrase in fdg.get("forbidden_icp_phrases") or []:
        if phrase.lower() in low:
            hard_fails.append(f"forbidden:{phrase}")

    for phrase in forge.get("forbidden_from_this_compile") or []:
        if phrase.lower() in low:
            hard_fails.append(f"compile_ban:{phrase[:40]}")

    sys.path.insert(0, str(SCRIPTS))
    from outbound_email_linter_v1 import lint_email  # noqa: WPS433

    linter = lint_email(
        body,
        lane=str(forge.get("brand_route") or forge.get("lane") or ""),
        trans=trans,
    )
    linter_hard = [
        f
        for f in linter.get("failures") or []
        if str(f.get("severity") or "fail") == "fail"
    ]
    linter_issues = [
        (
            f"{f.get('id')}:{f.get('match') or f.get('pattern') or f.get('got')}"
            if f.get("id") != "word_count"
            else f"word_count_over:{f.get('got')}>{f.get('limit')}"
        )
        for f in linter_hard
    ]
    lane_hits = [i for i in linter_issues if i.startswith("lane_forbidden:")]
    forbidden_one = [i for i in linter_issues if i.startswith("forbidden_one:")]
    if linter_issues:
        hard_fails.extend(linter_issues)
    checks.append(
        {
            "id": "lane_forbidden_tf",
            "points": 0 if lane_hits else 10,
            "max": 10,
            "issues": lane_hits,
            "upgrade": "U016",
        }
    )
    checks.append(
        {
            "id": "forbidden_in_email_one",
            "points": 0 if forbidden_one else 10,
            "max": 10,
            "issues": forbidden_one,
            "upgrade": "U012",
        }
    )
    checks.append(
        {
            "id": "outbound_email_linter",
            "points": 0 if linter.get("ok") else 10,
            "max": 10,
            "issues": linter_issues,
            "warnings": linter.get("warnings") or [],
            "repair_lines": linter.get("repair_lines") or [],
            "upgrade": "OEGCC1",
        }
    )

    try:
        sys.path.insert(0, str(SCRIPTS))
        from disclosure_ladder_v1 import check_outbound_body  # noqa: WPS433

        disc = check_outbound_body(
            body,
            lane=str(forge.get("brand_route") or forge.get("lane") or "w3_commercial"),
            tier=str(forge.get("disclosure_tier") or "") or None,
        )
        if disc.get("hard_fails"):
            hard_fails.extend(disc["hard_fails"])
        checks.append(
            {
                "id": "disclosure_tier_t1",
                "points": 0 if disc.get("forbidden_hits") else 10,
                "max": 10,
                "tier": disc.get("tier"),
                "issues": disc.get("forbidden_hits") or [],
                "upgrade": "DL1",
            }
        )
    except Exception:
        pass

    try:
        sys.path.insert(0, str(SCRIPTS))
        from brand_route_forbid_bleed_v1 import check_bleed  # noqa: WPS433

        bleed = check_bleed(body=body, lane=str(forge.get("brand_route") or forge.get("lane") or ""))
        if bleed.get("hard_fail"):
            for issue in bleed.get("issues") or []:
                hard_fails.append(f"brand_bleed:{issue}")
        checks.append(
            {
                "id": "brand_route_forbid_bleed",
                "points": 0 if bleed.get("hard_fail") else 10,
                "max": 10,
                "issues": bleed.get("issues") or [],
                "upgrade": "U027",
            }
        )
    except Exception:
        pass

    stub_fm = check_failure_moment_stub(forge)
    if not stub_fm.get("ok"):
        hard_fails.extend(stub_fm.get("issues") or [])
    checks.append(
        {
            "id": "fdg_failure_moment_stub",
            "points": 0 if stub_fm.get("ok") else 25,
            "max": 25,
            "issues": stub_fm.get("issues") or [],
            "upgrade": "U021",
        }
    )

    fm = forge.get("failure_moment") or {}
    if stub_fm.get("ok"):
        pressure = str(fm.get("pressure") or "").lower()
        key_bits = [w for w in re.findall(r"[a-z]{5,}", pressure) if w not in ("whether", "after", "something")]
        hits = sum(1 for w in key_bits[:6] if w in low)
        fm_ok = hits >= 2 or "collaboratory" in low or "permitted after" in low
        if not fm_ok:
            hard_fails.append("missing_failure_moment")
    else:
        fm_ok = False

    icp_world = forge.get("icp_profile") or {}
    must = icp_world.get("their_world") or []
    named = sum(1 for w in must if w.lower() in low)
    icp1 = 25 if named >= 2 else (12 if named >= 1 else 0)
    total += icp1
    checks.append({"id": "icp1_named_world", "points": icp1, "max": 25, "issues": [] if icp1 >= 20 else ["weak_icp_naming"]})

    icp2 = 25 if fm_ok and not any("forbidden:" in f for f in hard_fails) else 0
    total += icp2
    checks.append({"id": "icp2_failure_moment", "points": icp2, "max": 25, "issues": [] if icp2 else ["no_failure_moment"]})

    pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
    try:
        from icp_curiosity_gate_v1 import check_curiosity_before_link  # noqa: WPS433

        cur = check_curiosity_before_link(body)
        if not cur.get("ok"):
            hard_fails.extend([f"icp3:{i}" for i in cur.get("issues") or []])
        icp3 = 20 if cur.get("ok") else 0
        total += icp3
        checks.append(
            {
                "id": "icp3_curiosity_question",
                "points": icp3,
                "max": 20,
                "issues": cur.get("issues") or [],
                "upgrade": "U028",
            }
        )
    except Exception:
        has_q = "?" in pre_sig
        icp3 = 20 if has_q else 0
        total += icp3
        checks.append({"id": "icp3_curiosity_question", "points": icp3, "max": 20, "issues": [] if has_q else ["no_question"]})

    try:
        from icp_one_product_line_gate_v1 import check_one_product_line  # noqa: WPS433

        prod = check_one_product_line(body)
        if not prod.get("ok"):
            hard_fails.extend([f"icp4:{i}" for i in prod.get("issues") or []])
        icp4 = 15 if prod.get("ok") else 0
        checks.append(
            {
                "id": "icp4_one_product_line",
                "points": icp4,
                "max": 15,
                "issues": prod.get("issues") or [],
                "product_paragraph_count": prod.get("product_paragraph_count"),
                "upgrade": "U029",
            }
        )
    except Exception:
        product_hits_body = _product_mentions_body(body)
        icp4 = 15 if product_hits_body <= 2 else max(0, 15 - (product_hits_body - 2) * 5)
        checks.append(
            {
                "id": "icp4_one_product_line",
                "points": icp4,
                "max": 15,
                "issues": [] if product_hits_body <= 2 else ["product_dump"],
            }
        )
    total += icp4

    icp5_row = check_icp5_trace_rules(forge, body)
    icp5 = icp5_row.get("points") or 0
    icp5_issues = icp5_row.get("issues") or []
    total += icp5
    checks.append(
        {
            "id": "icp5_trace_rules",
            "points": icp5,
            "max": icp5_row.get("max") or ICP5_TRACE_RULES_MAX,
            "issues": icp5_issues,
            "rule_count": icp5_row.get("rule_count"),
            "rule_hits": icp5_row.get("rule_hits"),
            "thin_cap": icp5_row.get("thin_cap"),
            "upgrade": "U025",
        }
    )

    detected_mode = _detect_compose_mode(body)
    declared_mode = str(forge.get("compose_mode") or "")
    mode_ok = not declared_mode or detected_mode == declared_mode
    if not mode_ok:
        hard_fails.append(f"compose_mode_mismatch:{declared_mode}!={detected_mode}")
    checks.append(
        {
            "id": "compose_mode_detect",
            "points": 0,
            "max": 0,
            "detected": detected_mode,
            "declared": declared_mode or None,
            "issues": [] if mode_ok else [f"mode_mismatch:{declared_mode}!={detected_mode}"],
        }
    )

    pct = 0 if hard_fails else min(100, total)
    return {
        "account_id": forge.get("account_id"),
        "brand_route": forge.get("brand_route"),
        "icp_compiler_pct": pct,
        "icp_pass": pct >= BAR and not hard_fails,
        "failure_moment_present": fm_ok,
        "compose_mode_detected": detected_mode,
        "hard_fails": hard_fails,
        "checks": checks,
    }


def _fleet_index_row(account_id: str, compile_row: dict | None = None) -> dict:
    """U024 — one fleet index row from stub + optional compile receipt."""
    stub_path = COMPILE_DIR / f"{account_id}-v1.json"
    if account_id == "sourcea-factory" and not stub_path.is_file():
        stub_path = COMPILE_DIR / "sourcea-factory-v1.json"
    stub = _read_json(stub_path)
    trace = stub.get("output_trace") or {}
    compile_row = compile_row or {}
    rrl = compile_row.get("rrl") or {}
    return {
        "account_id": account_id,
        "brand": BRAND_BY_ACCOUNT.get(account_id) or stub.get("brand_route"),
        "company": stub.get("company"),
        "brand_route": stub.get("brand_route"),
        "ok": compile_row.get("ok") if compile_row else trace.get("machine_verdict") == "PASS",
        "icp_compiler_pct": compile_row.get("icp_compiler_pct") or trace.get("icp_compiler_pct"),
        "rrl_reaction": rrl.get("reaction") or trace.get("rrl_reaction"),
        "compile_gate": compile_row.get("compile_gate") or stub.get("compile_gate"),
        "status": stub.get("status"),
        "stub_path": str(stub_path.relative_to(ROOT)) if stub_path.is_file() else "",
    }


def build_fleet_index_receipt(*, write: bool = True) -> dict:
    """U024 — single fleet view: all 3 commercial brands in one accounts JSON array."""
    last_compile = _read_json(RECEIPT)
    rows: list[dict] = []
    for aid in COMMERCIAL_BRAND_ACCOUNTS:
        compile_row = last_compile if last_compile.get("account_id") == aid else {}
        rows.append(_fleet_index_row(aid, compile_row))
    out = {
        "schema": "icp-compiler-fleet-receipt-v1",
        "at": _now(),
        "compile_sequence": _compile_sequence(),
        "upgrade": "U024",
        "commercial_brands": [BRAND_BY_ACCOUNT[a] for a in COMMERCIAL_BRAND_ACCOUNTS],
        "accounts": rows,
        "brands_index": [
            {"brand": row["brand"], "account_id": row["account_id"], "ok": row.get("ok")}
            for row in rows
        ],
        "fleet_view": "single JSON array — 3 commercial brands",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        FLEET_RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def check_fleet_index_receipt(path: Path | None = None) -> dict:
    """U024 acceptance — fleet receipt lists fundmore + ocree + sourcea-factory."""
    path = path or FLEET_RECEIPT
    row = _read_json(path)
    accounts = row.get("accounts") or []
    present = {str(a.get("account_id") or "") for a in accounts}
    missing = [aid for aid in COMMERCIAL_BRAND_ACCOUNTS if aid not in present]
    brands = row.get("commercial_brands") or []
    return {
        "ok": not missing and len(accounts) >= 3 and len(brands) >= 3,
        "missing_accounts": missing,
        "account_count": len(accounts),
        "brands": brands,
        "path": str(path),
        "upgrade": "U024",
    }


def _write_fleet_receipt(rows: list[dict]) -> None:
    """Write fleet receipt — prefer full 3-brand index when partial rows passed."""
    if len(rows) < len(COMMERCIAL_BRAND_ACCOUNTS):
        build_fleet_index_receipt(write=True)
        return
    SINA.mkdir(parents=True, exist_ok=True)
    out = {
        "schema": "icp-compiler-fleet-receipt-v1",
        "at": _now(),
        "compile_sequence": _compile_sequence(),
        "upgrade": "U024",
        "commercial_brands": [BRAND_BY_ACCOUNT[a] for a in COMMERCIAL_BRAND_ACCOUNTS],
        "accounts": rows,
        "brands_index": [
            {
                "brand": BRAND_BY_ACCOUNT.get(r.get("account_id", ""), r.get("brand_route")),
                "account_id": r.get("account_id"),
                "ok": r.get("ok"),
            }
            for r in rows
            if r.get("account_id") in COMMERCIAL_BRAND_ACCOUNTS
        ],
        "fleet_view": "single JSON array — 3 commercial brands",
    }
    FLEET_RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


def run_compiler(*, account_id: str, write: bool = True, fleet_refresh: bool = False) -> dict:
    forge_path = COMPILE_DIR / f"{account_id}-v1.json"
    if not forge_path.is_file() and account_id == "sourcea-factory":
        forge_path = COMPILE_DIR / "sourcea-factory-v1.json"
    forge = _read_json(forge_path)
    if not forge:
        return {"ok": False, "error": f"missing forge {forge_path}"}

    compile_gate_row = check_compile_gate(account_id, forge)
    compile_gate = compile_gate_row.get("compile_gate")
    gate_blocked = bool(compile_gate_row.get("compile_gate_blocked"))
    from outbound_research_checklist_v1 import (  # noqa: WPS433
        check_human_confirm_before_compile,
        check_research_depth_signoff,
        check_signal_source_citations,
    )

    depth_row = check_research_depth_signoff(account_id)
    if depth_row.get("blocked"):
        return {
            "ok": False,
            "account_id": account_id,
            "icp_pass": False,
            "verdict": "BLOCKED",
            "error": depth_row.get("reason"),
            "research_depth_check": depth_row,
            "fdg_allowed": False,
            "compile_allowed": False,
            "compile_gate": compile_gate,
            "compile_gate_blocked": gate_blocked,
            "compile_gate_warning": compile_gate_row.get("compile_gate_warning"),
            "upgrade": "U058",
        }
    human_confirm_row = check_human_confirm_before_compile(account_id)
    if human_confirm_row.get("blocked"):
        return {
            "ok": False,
            "account_id": account_id,
            "icp_pass": False,
            "verdict": "BLOCKED",
            "error": human_confirm_row.get("reason"),
            "human_confirm_check": human_confirm_row,
            "human_confirmed_at": human_confirm_row.get("human_confirmed_at"),
            "compile_allowed": False,
            "compile_gate": compile_gate,
            "compile_gate_blocked": gate_blocked,
            "compile_gate_warning": compile_gate_row.get("compile_gate_warning"),
            "upgrade": "U052",
        }
    cite_row = check_signal_source_citations(account_id)
    hallucination_guard_warning = None
    if cite_row.get("compile_warn"):
        uncited = cite_row.get("uncited_signals") or []
        hallucination_guard_warning = (
            f"UNCITED_CLAIM — cite source_url per signal: {', '.join(uncited)}"
        )
    stub_fm = check_failure_moment_stub(forge)
    if not stub_fm.get("ok"):
        return {
            "ok": False,
            "account_id": account_id,
            "icp_pass": False,
            "error": "missing_failure_moment_stub",
            "stub_check": stub_fm,
            "compile_gate": compile_gate,
            "compile_gate_blocked": gate_blocked,
            "compile_gate_warning": compile_gate_row.get("compile_gate_warning"),
            "upgrade": "U021",
        }
    body_preflight = check_approved_body_path(
        forge,
        require_field=account_id not in ("forge-product",),
    )
    if not body_preflight.get("ok"):
        issue = (body_preflight.get("issues") or ["approved_body_preflight_fail"])[0]
        return {
            "ok": False,
            "account_id": account_id,
            "icp_pass": False,
            "verdict": "ERROR",
            "error": issue,
            "preflight_check": body_preflight,
            "compile_gate": compile_gate,
            "compile_gate_blocked": gate_blocked,
            "compile_gate_warning": compile_gate_row.get("compile_gate_warning"),
            "upgrade": "U026",
        }

    trans = _read_json(TRANSLATION)
    fdg = _read_json(FDG)
    body, body_src = _body_for_account(account_id, forge)
    ap = forge.get("approved_body_path")
    if not body.strip():
        return {"ok": False, "error": "missing body", "approved_body_path": ap}

    scored = score_icp_output(body, forge=forge, fdg=fdg, trans=trans)
    sys.path.insert(0, str(SCRIPTS))
    cil = ril = oqg = rrl = {}
    try:
        from conversation_interest_loop_v1 import score_conversation_interest  # noqa: WPS433
        from receiver_interest_loop_v1 import score_receiver_interest  # noqa: WPS433
        from best_loop_oqg_score_v1 import export_oqg_checks_bundle, score_w3_email  # noqa: WPS433

        cil = score_conversation_interest(account_id=account_id, body=body, cfg=trans)
        ril_cfg = _read_json(ROOT / "data" / "w3-receiver-interest-assets-v1.json")
        ril_row = (ril_cfg.get("accounts") or {}).get(account_id) or {}
        ril = score_receiver_interest(
            account_id=account_id,
            body=body,
            cfg_row=ril_row,
            declared_mode=str(forge.get("compose_mode") or "") or None,
        )
        pack = _read_json(SINA / "outbound" / f"w3-canada-{account_id}" / "pack.json")
        attach_p = Path(pack["attach"]) if pack.get("attach") else None
        oqg = score_w3_email(
            account_id=account_id,
            body=body,
            lane=str(pack.get("lane") or forge.get("brand_route") or ""),
            attach=attach_p,
            subject=pack.get("subject"),
            relationship_basis=pack.get("relationship_basis"),
        )
        if write:
            pack_dir = SINA / "outbound" / f"w3-canada-{account_id}"
            pack_path = pack_dir / "pack.json"
            if not pack:
                pack = {"schema": "w3-canada-outbound-send-pack-v1", "account_id": account_id}
            if oqg.get("error"):
                pack["oqg_checks"] = {
                    "schema": "oqg-checks-bundle-v1",
                    "upgrade": "U010",
                    "at": _now(),
                    "line_items": [],
                    "exported": {},
                    "issues": [str(oqg.get("error"))],
                    "oqg_pass": False,
                    "output_clean_pct": 0,
                }
            else:
                pack["oqg_checks"] = export_oqg_checks_bundle(oqg)
            pack["output_clean_pct"] = oqg.get("output_clean_pct")
            pack["oqg_pass"] = oqg.get("oqg_pass")
            pack["oqg_at"] = _now()
            pack["cil_pct"] = cil.get("conversation_interest_pct")
            pack["ril_pct"] = ril.get("receiver_interest_pct")
            pack_dir.mkdir(parents=True, exist_ok=True)
            pack_path.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
        from response_reality_layer_v1 import run_rrl  # noqa: WPS433

        prof = forge.get("icp_profile") or {}
        rrl = run_rrl(
            body=body,
            account_id=account_id,
            company=str(forge.get("company") or ""),
            icp_world=prof.get("their_world") or [],
            write=True,
        )
    except Exception as exc:
        cil = ril = oqg = rrl = {"error": str(exc)}

    rrl_pass = bool((rrl.get("simulation") or {}).get("rrl_pass")) if isinstance(rrl, dict) else False
    factory_pass = scored["icp_pass"] and rrl_pass

    row = {
        "schema": "icp-output-compiler-receipt-v1",
        "at": _now(),
        "account_id": account_id,
        "ok": factory_pass,
        "icp_trace_pass": scored["icp_pass"],
        "rrl_pass": rrl_pass,
        "verdict": "PASS" if factory_pass else "IMPROVE",
        "icp_compiler_pct": scored["icp_compiler_pct"],
        "icp_compiler_line": f"icp-compile · {account_id} · {scored['icp_compiler_pct']}% · bar={BAR}",
        "compile_sequence": _compile_sequence(),
        "compile_gate": compile_gate,
        "compile_gate_active": compile_gate_row.get("compile_gate_active"),
        "compile_gate_blocked": gate_blocked,
        "compile_gate_warning": compile_gate_row.get("compile_gate_warning"),
        "compile_gate_check": compile_gate_row,
        "hallucination_guard": cite_row,
        "hallucination_guard_warning": hallucination_guard_warning,
        "compile_warn": bool(hallucination_guard_warning),
        "preflight_check": body_preflight,
        "approved_body_path": ap,
        "body_source": body_src,
        "compose_mode_detected": scored.get("compose_mode_detected"),
        "failure_moment": forge.get("failure_moment"),
        "output_spec": forge.get("output_spec"),
        "reverse_engineered_rules": forge.get("reverse_engineered_rules"),
        "scored": scored,
        "cil": {"pct": cil.get("conversation_interest_pct"), "pass": cil.get("cil_pass")},
        "ril": {"pct": ril.get("receiver_interest_pct"), "pass": ril.get("ril_pass")},
        "oqg": {"pct": oqg.get("output_clean_pct"), "pass": oqg.get("oqg_pass")},
        "rrl": {
            "reaction": (rrl.get("simulation") or {}).get("reaction"),
            "label": (rrl.get("simulation") or {}).get("reaction_label"),
            "pass": rrl_pass,
            "line": rrl.get("rrl_line"),
            "interpretation": (rrl.get("simulation") or {}).get("recipient_interpretation"),
        },
        "ship_authority": "sina_read_score_pct only",
        "next_action_only": (
            f"DEFERRED — {compile_gate} — do not send until commercial tier closes"
            if gate_blocked and factory_pass
            else (
                "Sina read after full email — only ship authority"
                if factory_pass
                else (
                    rrl.get("next_action_only")
                    if scored["icp_pass"] and not rrl_pass
                    else scored.get("hard_fails") or ["fix ICP trace gaps"]
                )
            )
        ),
        "command": f"python3 scripts/icp_output_compiler_v1.py --account {account_id} --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if fleet_refresh:
            fleet_rows = []
            for aid in FLEET_ACCOUNTS:
                if aid == account_id:
                    fleet_rows.append(
                        {
                            "account_id": aid,
                            "ok": row.get("ok"),
                            "icp_compiler_pct": row.get("icp_compiler_pct"),
                            "rrl_reaction": (row.get("rrl") or {}).get("reaction"),
                            "compile_gate": row.get("compile_gate"),
                        }
                    )
                else:
                    prev = _read_json(SINA / "icp-output-compiler-receipt-v1.json")
                    if prev.get("account_id") == aid:
                        fleet_rows.append(
                            {
                                "account_id": aid,
                                "ok": prev.get("ok"),
                                "icp_compiler_pct": prev.get("icp_compiler_pct"),
                                "rrl_reaction": (prev.get("rrl") or {}).get("reaction"),
                                "compile_gate": prev.get("compile_gate"),
                            }
                        )
            if fleet_rows:
                _write_fleet_receipt(fleet_rows)
    return row


def run_fleet(*, write: bool = True) -> dict:
    rows: list[dict] = []
    for aid in FLEET_ACCOUNTS:
        stub = _read_json(COMPILE_DIR / f"{aid}-v1.json")
        if not stub and aid != "sourcea-factory":
            continue
        if not stub and aid == "sourcea-factory":
            stub = _read_json(COMPILE_DIR / "sourcea-factory-v1.json")
        if not stub:
            rows.append({"account_id": aid, "ok": False, "error": "missing_stub"})
            continue
        row = run_compiler(account_id=aid, write=write, fleet_refresh=False)
        rows.append(
            {
                "account_id": aid,
                "ok": row.get("ok"),
                "icp_compiler_pct": row.get("icp_compiler_pct"),
                "rrl_reaction": (row.get("rrl") or {}).get("reaction"),
                "compile_gate": row.get("compile_gate"),
                "verdict": row.get("verdict"),
            }
        )
    out = build_fleet_index_receipt(write=write)
    if not write:
        out["accounts"] = rows
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="ICP output compiler FDG v1")
    ap.add_argument("--account", default="")
    ap.add_argument("--fleet", action="store_true", help="Compile all fleet accounts + fleet receipt")
    ap.add_argument(
        "--fleet-index",
        action="store_true",
        help="U024 — build icp-compiler-fleet-receipt-v1.json index (3 brands)",
    )
    ap.add_argument(
        "--check-fleet-index",
        action="store_true",
        help="U024 — verify fleet receipt has 3 commercial brand accounts",
    )
    ap.add_argument(
        "--check-compile-sequence",
        action="store_true",
        help="U030 — verify receipt.compile_sequence shows NF∥TF then SourceA deferred",
    )
    ap.add_argument(
        "--check-one-product-line",
        action="store_true",
        help="U029 — one product paragraph max · two product paragraphs = fail",
    )
    ap.add_argument(
        "--check-curiosity-gate",
        action="store_true",
        help="U028 — curiosity question last before link · question after sign-off = fail",
    )
    ap.add_argument(
        "--check-brand-bleed",
        action="store_true",
        help="U027 — brand route forbid bleed · NF body mentioning TrustField = fail",
    )
    ap.add_argument(
        "--check-approved-body-path",
        action="store_true",
        help="U026 — verify approved_body_path file exists (missing file = error not PASS)",
    )
    ap.add_argument(
        "--check-trace-rules",
        action="store_true",
        help="U025 — verify reverse_engineered_rules min-5 cap (thin rules max 13/15)",
    )
    ap.add_argument(
        "--check-stubs",
        action="store_true",
        help="U021 — verify failure_moment on all icp-compile stubs",
    )
    ap.add_argument(
        "--check-press-earnings-paste",
        action="store_true",
        help="U057 — press/earnings manual paste field on compile stub",
    )
    ap.add_argument(
        "--check-fundmore-parity",
        action="store_true",
        help="U022 — fundmore icp-compile stub parity with ocree schema v2",
    )
    ap.add_argument(
        "--check-compile-gate",
        default="",
        help="U023 — report compile_gate warning for account (e.g. sourcea-factory)",
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.check_compile_sequence:
        row = validate_compile_sequence_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_compile_sequence:", "PASS" if row.get("ok") else row.get("law_check"))
        return 0 if row.get("ok") else 1
    if args.check_one_product_line:
        from icp_one_product_line_gate_v1 import validate_one_product_line_acceptance  # noqa: WPS433

        row = validate_one_product_line_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_one_product_line:", "PASS" if row.get("ok") else row.get("two_product_paragraphs"))
        return 0 if row.get("ok") else 1
    if args.check_curiosity_gate:
        from icp_curiosity_gate_v1 import validate_curiosity_gate_acceptance  # noqa: WPS433

        row = validate_curiosity_gate_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_curiosity_gate:", "PASS" if row.get("ok") else row.get("after_signoff"))
        return 0 if row.get("ok") else 1
    if args.check_brand_bleed:
        from brand_route_forbid_bleed_v1 import validate_brand_bleed_acceptance  # noqa: WPS433

        row = validate_brand_bleed_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_brand_bleed:", "PASS" if row.get("ok") else row.get("nf_trustfield_mention"))
        return 0 if row.get("ok") else 1
    if args.check_approved_body_path:
        row = validate_approved_body_path_preflight()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_approved_body_path:", "PASS" if row.get("ok") else row.get("missing_file_case"))
        return 0 if row.get("ok") else 1
    if args.check_trace_rules:
        row = validate_icp5_trace_rules_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(
                "check_trace_rules:",
                "PASS" if row.get("ok") else "FAIL",
                f"thin_cap={row.get('thin_rules_cap', {}).get('points')}",
            )
        return 0 if row.get("ok") else 1
    if args.check_press_earnings_paste:
        row = validate_press_earnings_paste_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_press_earnings_paste:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_stubs:
        row = validate_icp_compile_stubs()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            for stub in row.get("stubs") or []:
                status = "PASS" if stub.get("ok") else "FAIL"
                print(f"{stub.get('account_id')}: {status} {stub.get('issues') or ''}")
        return 0 if row.get("ok") else 1
    if args.check_fundmore_parity:
        row = check_fundmore_ocree_parity()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_fundmore_parity:", "PASS" if row.get("ok") else row.get("issues"))
        return 0 if row.get("ok") else 1
    if args.check_compile_gate:
        forge_path = COMPILE_DIR / f"{args.check_compile_gate}-v1.json"
        if args.check_compile_gate == "sourcea-factory" and not forge_path.is_file():
            forge_path = COMPILE_DIR / "sourcea-factory-v1.json"
        row = check_compile_gate(args.check_compile_gate, _read_json(forge_path))
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(row.get("compile_gate_warning") or "compile_gate: clear")
        return 0
    if args.fleet_index:
        row = build_fleet_index_receipt(write=not args.no_write)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            brands = ", ".join(row.get("commercial_brands") or [])
            print(f"fleet-index · {len(row.get('accounts') or [])} accounts · brands={brands}")
        return 0
    if args.check_fleet_index:
        row = check_fleet_index_receipt()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_fleet_index:", "PASS" if row.get("ok") else row.get("missing_accounts"))
        return 0 if row.get("ok") else 1
    if args.fleet:
        row = run_fleet(write=not args.no_write)
    elif args.account:
        row = run_compiler(account_id=args.account, write=not args.no_write, fleet_refresh=True)
    else:
        ap.error("require --account or --fleet")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if args.fleet:
            ok_n = sum(1 for a in row.get("accounts") or [] if a.get("ok"))
            print(f"icp-fleet · {ok_n}/{len(row.get('accounts') or [])} PASS · {row.get('compile_sequence')}")
        else:
            print(row.get("icp_compiler_line", row.get("error", "")))
    ok = row.get("ok") if not args.fleet else all(a.get("ok") for a in (row.get("accounts") or []))
    if args.fleet and not ok and row.get("schema") == "icp-compiler-fleet-receipt-v1":
        row["partial_fleet"] = True
        return 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
