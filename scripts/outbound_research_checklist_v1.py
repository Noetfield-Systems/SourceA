#!/usr/bin/env python3
"""Outbound research checklist — human-confirmed signals before ICP compile.

SSOT: data/outbound-research-checklist-v1.json
Law: data/outbound-factory-salvage-spec-v1.json
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "outbound-research-checklist-v1.json"
INGESTION_SCHEMA = ROOT / "data" / "outbound-ingestion-schema-v1.json"
SALVAGE_SPEC = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"
FILING_SSOT = ROOT / "data" / "canadian-issuer-filing-routes-v1.json"

RESEARCH_DEPTH_BULLET_IDS = (
    "target_identity",
    "filing_route",
    "financial_regulatory",
    "professional_dna",
    "technical_velocity",
)
RESEARCH_DEPTH_BULLET_COUNT = len(RESEARCH_DEPTH_BULLET_IDS)


def _default_research_depth_checklist() -> dict:
    labels = {
        "target_identity": "Company + executive identity verified against public record",
        "filing_route": "Filing route matches issuer country (no 10-K-only for CA)",
        "financial_regulatory": "Financial/regulatory signal reviewed with source or manual_only",
        "professional_dna": "Professional DNA confirmed — not scrape boilerplate",
        "technical_velocity": "Technical velocity reviewed or explicitly N/A",
    }
    return {
        "bullets": [
            {"id": bid, "label": labels[bid], "checked": False}
            for bid in RESEARCH_DEPTH_BULLET_IDS
        ],
        "human_signoff": {"all_checked": False, "signed_at": None},
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _validate_filing_route(meta: dict) -> tuple[bool, str]:
    country = str(meta.get("issuer_country") or "").upper()
    route = str(meta.get("filing_route") or "")
    if country == "CA" and route == "sec_10k":
        return False, "Canadian issuer cannot use sec_10k-only — use sedar_aif or sec_40f"
    if route not in ("sedar_aif", "sec_40f", "sec_10k", "manual_only"):
        return False, f"invalid filing_route: {route}"
    return True, "filing_route ok"


def validate_account(account_id: str, *, ssot: dict | None = None) -> dict:
    data = ssot or _read(SSOT)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {"ok": False, "account_id": account_id, "error": "unknown account"}

    meta = acct.get("target_metadata") or {}
    signals = acct.get("signals") or {}
    issues: list[str] = []

    for field in ("company_name", "executive_name", "executive_role", "issuer_country", "filing_route"):
        if not str(meta.get(field) or "").strip():
            issues.append(f"missing target_metadata.{field}")

    route_ok, route_note = _validate_filing_route(meta)
    if not route_ok:
        issues.append(route_note)

    unconfirmed = [
        k
        for k, v in signals.items()
        if isinstance(v, dict) and not v.get("human_confirmed")
    ]
    if unconfirmed:
        issues.append(f"signals not human_confirmed: {', '.join(unconfirmed)}")

    human = acct.get("human_tests_passed") or {}
    if not all(human.values()):
        issues.append("human_tests incomplete")

    ok = not issues
    return {
        "ok": ok,
        "account_id": account_id,
        "target_metadata": meta,
        "signals": signals,
        "human_tests_passed": human,
        "issues": issues,
        "ship_authority_note": data.get("ship_authority_note"),
        "compile_allowed": ok,
        "at": _now(),
    }


def preflight(account_id: str) -> dict:
    """Light preflight — metadata + filing route only (before human confirm)."""
    data = _read(SSOT)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {"ok": False, "error": "unknown account"}
    meta = acct.get("target_metadata") or {}
    route_ok, route_note = _validate_filing_route(meta)
    return {
        "ok": route_ok and bool(meta.get("company_name")),
        "account_id": account_id,
        "filing_route": meta.get("filing_route"),
        "route_note": route_note,
        "sina_read_required": True,
        "rrl_not_ship_authority": True,
    }


def validate_ingestion_schema_acceptance() -> dict:
    """U051 acceptance — target_metadata + signals SSOT aligned with salvage + checklist."""
    schema = _read(INGESTION_SCHEMA)
    salvage = _read(SALVAGE_SPEC)
    checklist = _read(SSOT)
    issues: list[str] = []

    if schema.get("schema") != "outbound-ingestion-schema-v1":
        issues.append("bad schema id")
    tm = schema.get("target_metadata") or {}
    sig = schema.get("signals") or {}
    salvage_ing = salvage.get("ingestion_schema") or {}
    required_meta = list(tm.get("required") or [])
    required_signals = list(sig.get("required_keys") or [])
    salvage_meta = list(salvage_ing.get("target_metadata") or [])
    salvage_signals = list(salvage_ing.get("signals") or [])

    if salvage_meta != required_meta:
        issues.append("target_metadata mismatch salvage")
    if salvage_signals != required_signals:
        issues.append("signals mismatch salvage")
    if not required_meta or not required_signals:
        issues.append("empty target_metadata or signals in schema")

    shape = sig.get("signal_shape") or {}
    if "human_confirmed" not in shape:
        issues.append("signals.signal_shape missing human_confirmed")

    account_rows: list[dict] = []
    for aid, acct in (checklist.get("accounts") or {}).items():
        meta = acct.get("target_metadata") or {}
        signals = acct.get("signals") or {}
        row_issues: list[str] = []
        for field in required_meta:
            if field not in meta:
                row_issues.append(f"missing target_metadata.{field}")
        for key in required_signals:
            if key not in signals:
                row_issues.append(f"missing signals.{key}")
            elif not isinstance(signals.get(key), dict):
                row_issues.append(f"signals.{key} must be object")
        account_rows.append(
            {
                "account_id": aid,
                "ok": not row_issues,
                "target_metadata_keys": sorted(meta.keys()),
                "signal_keys": sorted(signals.keys()),
                "issues": row_issues,
            }
        )
        issues.extend(f"{aid}:{i}" for i in row_issues)

    ok = not issues
    return {
        "ok": ok,
        "upgrade": "U051",
        "schema_path": str(INGESTION_SCHEMA),
        "target_metadata_required": required_meta,
        "signals_required": required_signals,
        "salvage_aligned": salvage_meta == required_meta and salvage_signals == required_signals,
        "accounts": account_rows,
        "acceptance": "target_metadata + signals",
        "check": "python3 scripts/outbound_research_checklist_v1.py --check-ingestion-schema --json",
    }


def check_human_confirm_before_compile(account_id: str, *, ssot: dict | None = None) -> dict:
    """U052 — block ICP compile until ingestion.human_confirmed_at is set on target."""
    data = ssot or _read(SSOT)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "human_confirmed_at": None,
            "reason": "unknown account",
            "compile_allowed": False,
            "upgrade": "U052",
        }
    confirmed_at = str(acct.get("human_confirmed_at") or "").strip()
    if not confirmed_at:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "human_confirmed_at": None,
            "reason": "missing human_confirmed_at",
            "compile_allowed": False,
            "upgrade": "U052",
        }
    unconfirmed = [
        k
        for k, v in (acct.get("signals") or {}).items()
        if isinstance(v, dict) and not v.get("human_confirmed")
    ]
    if unconfirmed:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "human_confirmed_at": confirmed_at,
            "reason": f"signals not human_confirmed: {', '.join(unconfirmed)}",
            "compile_allowed": False,
            "upgrade": "U052",
        }
    return {
        "ok": True,
        "blocked": False,
        "account_id": account_id,
        "human_confirmed_at": confirmed_at,
        "compile_allowed": True,
        "upgrade": "U052",
    }


def validate_human_confirm_compile_acceptance() -> dict:
    """U052 acceptance — no compile without human_confirmed_at on target."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from icp_output_compiler_v1 import run_compiler  # noqa: WPS433

    base = _read(SSOT)
    blocked_check = check_human_confirm_before_compile("fundmore", ssot=base)
    compile_row = run_compiler(account_id="fundmore", write=False)
    confirmed = copy.deepcopy(base)
    fm = (confirmed.get("accounts") or {}).get("fundmore") or {}
    fm["human_confirmed_at"] = _now()
    for sig in (fm.get("signals") or {}).values():
        if isinstance(sig, dict):
            sig["human_confirmed"] = True
    fm["human_tests_passed"] = {"ai_eraser": True, "curiosity_not_confusion": True}
    allowed_check = check_human_confirm_before_compile("fundmore", ssot=confirmed)
    ok = (
        blocked_check.get("blocked")
        and blocked_check.get("reason") == "missing human_confirmed_at"
        and not compile_row.get("ok")
        and compile_row.get("upgrade") == "U052"
        and compile_row.get("verdict") == "BLOCKED"
        and allowed_check.get("compile_allowed")
    )
    return {
        "ok": ok,
        "upgrade": "U052",
        "blocked_check": blocked_check,
        "compile_blocked": not compile_row.get("ok"),
        "compile_upgrade": compile_row.get("upgrade"),
        "compile_error": compile_row.get("error"),
        "allowed_check": allowed_check,
        "acceptance": "No compile without confirm",
        "check": "python3 scripts/outbound_research_checklist_v1.py --check-human-confirm-compile --json",
    }


def check_research_depth_signoff(account_id: str, *, ssot: dict | None = None) -> dict:
    """U058 — 5-bullet research depth checklist must be signed before FDG compile."""
    data = ssot or _read(SSOT)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "reason": "unknown account",
            "fdg_allowed": False,
            "upgrade": "U058",
        }
    checklist = acct.get("research_depth_checklist")
    if not isinstance(checklist, dict):
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "reason": "missing research_depth_checklist",
            "fdg_allowed": False,
            "upgrade": "U058",
        }
    bullets = checklist.get("bullets") or []
    if len(bullets) != RESEARCH_DEPTH_BULLET_COUNT:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "reason": f"expected {RESEARCH_DEPTH_BULLET_COUNT} checklist bullets",
            "bullet_count": len(bullets),
            "fdg_allowed": False,
            "upgrade": "U058",
        }
    unchecked = [str(b.get("id") or "") for b in bullets if not b.get("checked")]
    signoff = checklist.get("human_signoff") or {}
    if unchecked:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "reason": f"unchecked bullets: {', '.join(unchecked)}",
            "unchecked": unchecked,
            "fdg_allowed": False,
            "upgrade": "U058",
        }
    if not signoff.get("all_checked"):
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "reason": "human_signoff.all_checked required before FDG",
            "fdg_allowed": False,
            "upgrade": "U058",
        }
    return {
        "ok": True,
        "blocked": False,
        "account_id": account_id,
        "bullet_count": RESEARCH_DEPTH_BULLET_COUNT,
        "signed_at": signoff.get("signed_at"),
        "fdg_allowed": True,
        "upgrade": "U058",
    }


def validate_research_depth_acceptance() -> dict:
    """U058 acceptance — checkbox before FDG on salvage stage 1 research."""
    base = _read(SSOT)
    stub_rows: list[dict] = []
    for aid in ("fundmore", "ocree"):
        row = check_research_depth_signoff(aid, ssot=base)
        stub_rows.append({"account_id": aid, **row})
    signed = copy.deepcopy(base)
    fm = (signed.get("accounts") or {}).get("fundmore") or {}
    checklist = fm.get("research_depth_checklist") or _default_research_depth_checklist()
    for bullet in checklist.get("bullets") or []:
        bullet["checked"] = True
    checklist["human_signoff"] = {"all_checked": True, "signed_at": _now()}
    fm["research_depth_checklist"] = checklist
    allowed = check_research_depth_signoff("fundmore", ssot=signed)
    ok = (
        all(not r.get("ok") and r.get("blocked") for r in stub_rows)
        and allowed.get("fdg_allowed")
        and allowed.get("bullet_count") == RESEARCH_DEPTH_BULLET_COUNT
    )
    return {
        "ok": ok,
        "upgrade": "U058",
        "stubs_blocked": stub_rows,
        "signed_off_ok": allowed,
        "acceptance": "Checkbox before FDG",
        "check": "python3 scripts/outbound_research_checklist_v1.py --check-research-depth --json",
    }


def _valid_source_url(url: object) -> bool:
    u = str(url or "").strip().lower()
    return u.startswith("http://") or u.startswith("https://")


def _signal_source_urls(sig: dict) -> list[str]:
    urls: list[str] = []
    if _valid_source_url(sig.get("source_url")):
        urls.append(str(sig.get("source_url")).strip())
    for raw in sig.get("source_urls") or []:
        if _valid_source_url(raw):
            urls.append(str(raw).strip())
    return urls


def check_signal_source_citations(account_id: str, *, ssot: dict | None = None) -> dict:
    """U059 — hallucination guard: non-empty signal text must cite source_url or source_urls[]."""
    data = ssot or _read(SSOT)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {
            "ok": False,
            "compile_warn": False,
            "account_id": account_id,
            "reason": "unknown account",
            "upgrade": "U059",
        }
    signals = acct.get("signals") or {}
    uncited: list[str] = []
    cited: list[str] = []
    for key, sig in signals.items():
        if not isinstance(sig, dict):
            continue
        text = str(sig.get("text") or "").strip()
        if not text:
            continue
        if _signal_source_urls(sig):
            cited.append(str(key))
        else:
            uncited.append(str(key))
    compile_warn = bool(uncited)
    return {
        "ok": not compile_warn,
        "compile_warn": compile_warn,
        "account_id": account_id,
        "uncited_signals": uncited,
        "cited_signals": cited,
        "upgrade": "U059",
    }


def validate_hallucination_guard_acceptance() -> dict:
    """U059 acceptance — uncited claim = compile warn; source_urls[] clears warn."""
    base = _read(SSOT)
    ocree_uncited = check_signal_source_citations("ocree", ssot=base)
    fundmore_ok = check_signal_source_citations("fundmore", ssot=base)
    cited = copy.deepcopy(base)
    ocree_sig = (cited.get("accounts") or {}).get("ocree", {}).get("signals", {}).get(
        "financial_regulatory"
    )
    if isinstance(ocree_sig, dict):
        ocree_sig["source_urls"] = ["https://www.securities-administrators.ca/"]
    ocree_cited = check_signal_source_citations("ocree", ssot=cited)
    ok = (
        ocree_uncited.get("compile_warn")
        and "financial_regulatory" in (ocree_uncited.get("uncited_signals") or [])
        and fundmore_ok.get("ok")
        and not fundmore_ok.get("compile_warn")
        and ocree_cited.get("ok")
        and not ocree_cited.get("compile_warn")
    )
    return {
        "ok": ok,
        "upgrade": "U059",
        "ocree_uncited": ocree_uncited,
        "fundmore_cited": fundmore_ok,
        "ocree_after_source_urls": ocree_cited,
        "acceptance": "Uncited claim = compile warn",
        "check": "python3 scripts/outbound_research_checklist_v1.py --check-hallucination-guard --json",
    }


INGEST_COMPOSE_FORBIDDEN_KEYS = (
    "body",
    "subject",
    "email_body",
    "composed_email",
    "compose_mode",
    "auto_compose",
    "compose_on_ingest",
)


def run_ingest_profile(
    account_id: str,
    *,
    ssot: dict | None = None,
    auto_compose: bool = False,
) -> dict:
    """U060 — ingest ends at JSON profile; compile is a separate step."""
    if auto_compose:
        return {
            "ok": False,
            "blocked": True,
            "account_id": account_id,
            "reason": "auto_compose forbidden on ingest",
            "compose_called": False,
            "upgrade": "U060",
        }
    data = ssot or _read(SSOT)
    acct = (data.get("accounts") or {}).get(account_id)
    if not acct:
        return {
            "ok": False,
            "account_id": account_id,
            "error": "unknown account",
            "upgrade": "U060",
        }
    for key in INGEST_COMPOSE_FORBIDDEN_KEYS:
        if key in acct and acct.get(key):
            return {
                "ok": False,
                "blocked": True,
                "account_id": account_id,
                "reason": f"ingest must not include {key}",
                "compose_called": False,
                "upgrade": "U060",
            }
    profile = {
        "schema": "outbound-ingest-profile-v1",
        "account_id": account_id,
        "target_metadata": acct.get("target_metadata") or {},
        "signals": acct.get("signals") or {},
        "human_tests_passed": acct.get("human_tests_passed") or {},
        "ingest_complete": True,
        "compose_called": False,
        "compile_separate": True,
        "next_step": f"python3 scripts/icp_output_compiler_v1.py --account {account_id}",
    }
    if acct.get("research_depth_checklist"):
        profile["research_depth_checklist"] = acct.get("research_depth_checklist")
    if acct.get("human_confirmed_at"):
        profile["human_confirmed_at"] = acct.get("human_confirmed_at")
    return {
        "ok": True,
        "account_id": account_id,
        "profile": profile,
        "ingest_output": "json_profile",
        "auto_compose": False,
        "at": _now(),
        "upgrade": "U060",
    }


def validate_ingest_no_auto_compose_acceptance() -> dict:
    """U060 acceptance — ingest ends at JSON profile; no auto-compose on ingest path."""
    base = _read(SSOT)
    ingest = run_ingest_profile("fundmore", ssot=base)
    blocked = run_ingest_profile("fundmore", ssot=base, auto_compose=True)
    bad = copy.deepcopy(base)
    (bad.get("accounts") or {}).setdefault("fundmore", {})["composed_email"] = "must not ingest compose"
    bad_row = run_ingest_profile("fundmore", ssot=bad)
    sys.path.insert(0, str(ROOT / "scripts"))
    from exa_velocity_fetch_v1 import fetch_technical_velocity  # noqa: WPS433

    exa = fetch_technical_velocity(account_id="fundmore", live=False)
    profile = ingest.get("profile") or {}
    ok = (
        ingest.get("ok")
        and profile.get("schema") == "outbound-ingest-profile-v1"
        and profile.get("compose_called") is False
        and profile.get("ingest_complete") is True
        and "target_metadata" in profile
        and "signals" in profile
        and "body" not in profile
        and blocked.get("blocked")
        and bad_row.get("blocked")
        and exa.get("ok")
        and exa.get("raw_html") is False
        and "structured_notes" in exa
        and "body" not in exa
    )
    return {
        "ok": ok,
        "upgrade": "U060",
        "ingest_profile": ingest,
        "auto_compose_blocked": blocked,
        "compose_field_blocked": bad_row,
        "exa_ingest_only": {
            "ok": exa.get("ok"),
            "has_structured_notes": bool(exa.get("structured_notes")),
            "no_body_key": "body" not in exa,
        },
        "acceptance": "Ingest ends at JSON profile",
        "check": "python3 scripts/outbound_research_checklist_v1.py --check-ingest-pipeline --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound research checklist validator")
    ap.add_argument("--account", required=False)
    ap.add_argument("--preflight", action="store_true", help="Metadata + filing route only")
    ap.add_argument("--check-ingestion-schema", action="store_true", help="U051 — target_metadata + signals SSOT")
    ap.add_argument("--check-human-confirm-compile", action="store_true", help="U052 — no compile without human_confirmed_at")
    ap.add_argument("--check-research-depth", action="store_true", help="U058 — 5-bullet checklist before FDG")
    ap.add_argument("--check-hallucination-guard", action="store_true", help="U059 — cite source URL per signal")
    ap.add_argument("--check-ingest-pipeline", action="store_true", help="U060 — ingest ends at JSON profile")
    ap.add_argument("--ingest-profile", action="store_true", help="U060 — emit JSON ingest profile for --account")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.check_ingestion_schema:
        row = validate_ingestion_schema_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_ingestion_schema:", "PASS" if row.get("ok") else row.get("issues", row))
        return 0 if row.get("ok") else 1
    if args.check_human_confirm_compile:
        row = validate_human_confirm_compile_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_human_confirm_compile:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_research_depth:
        row = validate_research_depth_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_research_depth:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_hallucination_guard:
        row = validate_hallucination_guard_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_hallucination_guard:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_ingest_pipeline:
        row = validate_ingest_no_auto_compose_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_ingest_pipeline:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.ingest_profile:
        if not args.account:
            ap.error("--account required with --ingest-profile")
        row = run_ingest_profile(args.account)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("ingest_profile:", row.get("ok"), row.get("account_id"))
        return 0 if row.get("ok") else 1
    if not args.account:
        ap.error(
            "--account required unless --check-ingestion-schema, "
            "--check-human-confirm-compile, --check-research-depth, "
            "--check-hallucination-guard, or --check-ingest-pipeline"
        )
    row = preflight(args.account) if args.preflight else validate_account(args.account)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} account={args.account} issues={row.get('issues', row.get('route_note'))}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
