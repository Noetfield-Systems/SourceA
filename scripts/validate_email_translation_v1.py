#!/usr/bin/env python3
"""Validate factory email translation SSOT — U018.

Fails if forbidden engineering terms appear in outbound bodies without translation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
TRANSLATION = ROOT / "data" / "factory-email-translation-v1.json"
SALVAGE = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"
SALVAGE_REL = "data/outbound-factory-salvage-spec-v1.json"
TRANSLATION_REL = "data/factory-email-translation-v1.json"
OUTBOUND = SINA / "outbound"
SAVED_AT_JSON_RE = re.compile(
    r'"saved_at"\s*:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"'
)
MIN_TRANSLATION_VERSION = (1, 1, 0)


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_version(version: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", str(version or "1.0.0").strip())
    if not match:
        return (1, 0, 0)
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def bump_translation_version(current: str) -> str:
    """U020 — patch bump on any translation SSOT edit."""
    major, minor, patch = _parse_version(current)
    return f"{major}.{minor}.{patch + 1}"


def check_translation_saved_at(path: Path | None = None) -> dict:
    """U020 — saved_at discipline: exact UTC timestamp in JSON header."""
    path = path or TRANSLATION
    if not path.is_file():
        return {"ok": False, "error": "missing_translation_ssot", "upgrade": "U020"}
    head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    match = SAVED_AT_JSON_RE.search(head)
    if not match:
        return {
            "ok": False,
            "path": str(path),
            "reason": "missing_or_invalid_saved_at",
            "upgrade": "U020",
            "fix": 'Add "saved_at": "YYYY-MM-DDTHH:MM:SSZ" in first 12 lines',
        }
    cfg = _read_json(path)
    version = _parse_version(str(cfg.get("version") or "0.0.0"))
    if version < MIN_TRANSLATION_VERSION:
        return {
            "ok": False,
            "path": str(path),
            "reason": "version_below_1_1_0",
            "version": cfg.get("version"),
            "upgrade": "U020",
        }
    return {
        "ok": True,
        "path": str(path),
        "saved_at": match.group(1),
        "version": cfg.get("version"),
        "upgrade": "U020",
    }


def write_translation_ssot(trans: dict, *, upgrade: str = "") -> dict:
    """U020 — bump version + saved_at on any translation JSON write."""
    trans["version"] = bump_translation_version(str(trans.get("version") or "1.0.0"))
    trans["saved_at"] = _now()
    trans["version_discipline"] = {
        "upgrade": "U020",
        "at": trans["saved_at"],
        "rule": "bump patch + saved_at on any edit",
        "validator": "scripts/validate_email_translation_v1.py --check-saved-at",
        "last_edit": upgrade or "translation_ssot_write",
    }
    TRANSLATION.write_text(json.dumps(trans, indent=2) + "\n", encoding="utf-8")
    saved = check_translation_saved_at()
    return {
        "ok": saved.get("ok"),
        "version": trans["version"],
        "saved_at": trans["saved_at"],
        "saved_check": saved,
    }


def sync_salvage_hard_fails(*, write: bool = True) -> dict:
    """U011 — sync salvage hard_fail_openers into translation SSOT."""
    salvage = _read_json(SALVAGE)
    trans = _read_json(TRANSLATION)
    if not salvage:
        return {"ok": False, "error": "missing_salvage_spec"}
    if not trans:
        return {"ok": False, "error": "missing_translation_ssot"}
    openers = list(salvage.get("hard_fail_openers") or [])
    patterns = list(salvage.get("hard_fail_patterns") or [])
    trans["hard_fail_openers"] = openers
    trans["salvage_hard_fail_patterns"] = patterns
    trans["salvage_sync"] = {
        "upgrade": "U011",
        "at": _now(),
        "salvage_spec": str(SALVAGE.relative_to(ROOT)),
    }
    if write:
        write_translation_ssot(trans, upgrade="U011")
    return {
        "ok": True,
        "hard_fail_openers": openers,
        "salvage_hard_fail_patterns": patterns,
        "openers_match": openers == list(salvage.get("hard_fail_openers") or []),
    }


def salvage_openers_match(cfg: dict | None = None, salvage: dict | None = None) -> bool:
    """Acceptance — salvage openers = translation hard_fail_openers."""
    cfg = cfg if cfg is not None else _read_json(TRANSLATION)
    salvage = salvage if salvage is not None else _read_json(SALVAGE)
    return list(salvage.get("hard_fail_openers") or []) == list(cfg.get("hard_fail_openers") or [])


def check_salvage_law_crosslink(
    cfg: dict | None = None,
    salvage: dict | None = None,
) -> dict:
    """U017 — translation law field must cite salvage human doc + machine spec."""
    cfg = cfg if cfg is not None else _read_json(TRANSLATION)
    salvage = salvage if salvage is not None else _read_json(SALVAGE)
    if not cfg:
        return {"ok": False, "error": "missing_translation_ssot", "upgrade": "U017"}
    if not salvage:
        return {"ok": False, "error": "missing_salvage_spec", "upgrade": "U017"}

    human_doc = str(salvage.get("human_doc") or "docs/SOURCEA_OUTBOUND_FACTORY_SALVAGE_SPEC_LOCKED_v1.md")
    law = str(cfg.get("law") or "")
    salvage_spec = str(cfg.get("salvage_spec") or "")
    translation_ssot = str(salvage.get("translation_ssot") or "")
    issues: list[str] = []

    if SALVAGE_REL not in law:
        issues.append(f"law_missing:{SALVAGE_REL}")
    if human_doc not in law:
        issues.append(f"law_missing:{human_doc}")
    if salvage_spec != SALVAGE_REL:
        issues.append(f"salvage_spec_mismatch:{salvage_spec}")
    if translation_ssot != TRANSLATION_REL:
        issues.append(f"salvage_translation_ssot_mismatch:{translation_ssot}")

    return {
        "ok": not issues,
        "issues": issues,
        "law": law,
        "salvage_spec": salvage_spec,
        "human_doc": human_doc,
        "translation_ssot": translation_ssot,
        "upgrade": "U017",
    }


def wire_salvage_law_crosslink(*, write: bool = True) -> dict:
    """U017 — normalize law pointer + bidirectional cross-link metadata."""
    salvage = _read_json(SALVAGE)
    trans = _read_json(TRANSLATION)
    if not salvage or not trans:
        return {"ok": False, "error": "missing_ssot"}

    human_doc = str(salvage.get("human_doc") or "docs/SOURCEA_OUTBOUND_FACTORY_SALVAGE_SPEC_LOCKED_v1.md")
    canonical_law = f"{human_doc} · {SALVAGE_REL}"
    trans["law"] = canonical_law
    trans["salvage_spec"] = SALVAGE_REL
    trans["salvage_law_crosslink"] = {
        "upgrade": "U017",
        "at": _now(),
        "human_doc": human_doc,
        "salvage_spec": SALVAGE_REL,
        "script": "scripts/validate_email_translation_v1.py --check-law-crosslink",
    }

    salvage["translation_ssot"] = TRANSLATION_REL
    salvage["translation_law_field"] = f"{TRANSLATION_REL}#law"
    salvage["translation_law_crosslink"] = {
        "upgrade": "U017",
        "at": _now(),
        "cites": [human_doc, SALVAGE_REL],
    }

    if write:
        row = write_translation_ssot(trans, upgrade="U017")
        stamp = row.get("saved_at") or _now()
        salvage["saved_at"] = stamp
        salvage["translation_law_crosslink"]["at"] = stamp
        SALVAGE.write_text(json.dumps(salvage, indent=2) + "\n", encoding="utf-8")

    check = check_salvage_law_crosslink(trans, salvage)
    return {"ok": check.get("ok"), "check": check, "law": canonical_law}


def _body_words(text: str) -> str:
    pre = text.split("Reply **stop**")[0] if "Reply **stop**" in text else text
    return pre.lower()


def check_body(body: str, cfg: dict) -> list[str]:
    return compose_lint(body, cfg).get("issues") or []


def compose_lint(body: str, cfg: dict | None = None, *, region: str = "canada", lane: str = "") -> dict:
    """U013 — compose lint with auto-suggest from translate map."""
    cfg = cfg or _read_json(TRANSLATION)
    low = _body_words(body)
    translate = cfg.get("translate") or {}
    glossary = cfg.get("human_primitive_glossary") or {}
    issues: list[str] = []
    messages: list[str] = []
    regional = check_regional_vocabulary(body, region, cfg)
    issues.extend(regional.get("issues") or [])
    for msg in regional.get("routing_messages") or []:
        messages.append(msg)
    if lane:
        lane_check = check_lane_forbidden(body, lane, cfg)
        if lane_check.get("hard_fail"):
            issues.extend(lane_check.get("issues") or [])
            for hit in lane_check.get("hits") or []:
                messages.append(f"lane_forbidden:{hit} — hard fail on TrustField email")
    for term in cfg.get("forbidden_in_email_one") or []:
        if term.lower() in low:
            issues.append(f"forbidden_term:{term}")
            suggest = translate.get(term) or glossary.get(term)
            if suggest:
                messages.append(f"{term} → use '{suggest}'")
            else:
                messages.append(f"forbidden:{term}")
    for opener in cfg.get("hard_fail_openers") or []:
        if low.lstrip().startswith(opener.lower()):
            issues.append(f"hard_fail_opener:{opener}")
            messages.append(f"opener:{opener} — rewrite opening")
    return {
        "ok": not issues,
        "issues": issues,
        "compose_lint_messages": messages,
        "regional_vocabulary": regional,
        "lane_forbidden": check_lane_forbidden(body, lane, cfg) if lane else None,
        "upgrade": "U013",
    }


def check_lane_forbidden(body: str, lane: str, cfg: dict | None = None) -> dict:
    """U016 — TF-specific forbidden phrases (inspectable proof) hard fail."""
    cfg = cfg or _read_json(TRANSLATION)
    lane_key = str(lane or "").lower()
    forbidden_map = cfg.get("lane_forbidden") or {}
    low = _body_words(body)
    hits: list[str] = []
    for phrase in forbidden_map.get(lane_key) or []:
        if phrase.lower() in low:
            hits.append(phrase)
    return {
        "ok": not hits,
        "lane": lane_key,
        "hits": hits,
        "issues": [f"lane_forbidden:{p}" for p in hits],
        "hard_fail": bool(hits),
        "upgrade": "U016",
    }


def check_regional_vocabulary(body: str, region: str, cfg: dict | None = None) -> dict:
    """U015 — route OSFI vs SEC terms via translation regional_overlay."""
    cfg = cfg or _read_json(TRANSLATION)
    overlay = (cfg.get("regional_overlay") or {}).get(str(region or "canada").lower()) or {}
    low = _body_words(body)
    issues: list[str] = []
    routing_messages: list[str] = []
    prefer_hits = [term for term in (overlay.get("prefer") or []) if term.lower() in low]
    for term in overlay.get("forbid_mismatch") or []:
        if term.lower() in low:
            issues.append(f"regional_forbid:{term}")
            routing_messages.append(f"{term} — wrong region ({region}); use {overlay.get('prefer', [])[:2]}")
    region_key = str(region or "canada").lower()
    if region_key == "canada":
        if re.search(r"\bsec\b", low) and "sec 10-k" not in low:
            if not any(t.lower() in low for t in ("osfi", "osc", "csa", "sedar", "fintrac")):
                issues.append("regional_mismatch:SEC_without_canadian_regulator")
                routing_messages.append("SEC framing in Canada pack — route to OSFI/CSA/OSC terms")
        if prefer_hits:
            routing_messages.append(f"canadian terms ok: {', '.join(prefer_hits[:3])}")
    elif region_key == "us":
        if "osfi" in low and "canada" not in low:
            issues.append("regional_mismatch:OSFI_without_canada_context")
            routing_messages.append("OSFI in US pack — use SEC/FINRA/FDIC unless Canada context is explicit")
        if re.search(r"\bsec\b", low) or "finra" in low:
            routing_messages.append("US regulatory terms routed ok")
    return {
        "ok": not issues,
        "region": region_key,
        "issues": issues,
        "prefer_hits": prefer_hits,
        "routing_messages": routing_messages,
        "upgrade": "U015",
    }


def _account_lane(account_id: str) -> str:
    pack = _read_json(OUTBOUND / f"w3-canada-{account_id}" / "pack.json")
    lane = str(pack.get("lane") or "").lower()
    if lane == "trustfield":
        return "trustfield"
    if lane == "noetfield":
        return "noetfield"
    return lane


def check_account(account_id: str, cfg: dict, *, region: str = "canada") -> dict:
    body_path = OUTBOUND / f"w3-canada-{account_id}" / "body.txt"
    if not body_path.is_file():
        return {"account_id": account_id, "ok": False, "issues": ["missing_body"]}
    row = lint_body_file(body_path, cfg, region=region, lane=_account_lane(account_id))
    return {
        "account_id": account_id,
        "ok": row.get("ok"),
        "issues": row.get("issues") or [],
        "compose_lint_messages": row.get("compose_lint_messages") or [],
        "regional_vocabulary": row.get("regional_vocabulary") or {},
    }


def lint_body_file(
    body_path: Path | str,
    cfg: dict | None = None,
    *,
    region: str = "canada",
    lane: str = "",
) -> dict:
    """U018 — lint outbound body file; exit 1 on forbidden noun."""
    path = Path(body_path).expanduser()
    if not path.is_file():
        return {"ok": False, "error": "missing_body_file", "path": str(path), "upgrade": "U018"}
    body = path.read_text(encoding="utf-8")
    detected_lane = lane
    if not detected_lane:
        match = re.search(r"w3-canada-([^/]+)", str(path))
        if match:
            detected_lane = _account_lane(match.group(1))
    cfg = cfg or _read_json(TRANSLATION)
    lint = compose_lint(body, cfg, region=region, lane=detected_lane)
    return {
        **lint,
        "path": str(path),
        "lane": detected_lane or None,
        "upgrade": "U018",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate email translation SSOT")
    ap.add_argument("--account", default="")
    ap.add_argument("--sync-salvage", action="store_true", help="U011 — sync salvage hard fails into translation SSOT")
    ap.add_argument(
        "--check-law-crosslink",
        action="store_true",
        help="U017 — verify translation law field cites salvage doc",
    )
    ap.add_argument(
        "--wire-law-crosslink",
        action="store_true",
        help="U017 — normalize law pointer + cross-link metadata",
    )
    ap.add_argument(
        "--check-saved-at",
        action="store_true",
        help="U020 — validate translation JSON saved_at + version ≥1.1.0",
    )
    ap.add_argument("--compose-lint", default="", help="U013 — lint body text and emit auto-suggest messages")
    ap.add_argument(
        "--body-file",
        default="",
        help="U018 — lint body file path; exit 1 on forbidden noun",
    )
    ap.add_argument("--region", default="canada", help="U015 — canada|us regional vocabulary routing")
    ap.add_argument("--lane", default="", help="U016 — trustfield|noetfield lane forbidden check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.body_file:
        row = lint_body_file(args.body_file, region=args.region, lane=args.lane)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            if row.get("error"):
                print(row["error"], file=sys.stderr)
            else:
                for msg in row.get("compose_lint_messages") or row.get("issues") or []:
                    print(msg)
        return 0 if row.get("ok") else 1
    if args.compose_lint:
        cfg = _read_json(TRANSLATION)
        row = compose_lint(args.compose_lint, cfg, region=args.region, lane=args.lane)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            for msg in row.get("compose_lint_messages") or []:
                print(msg)
        return 0 if row.get("ok") else 1
    if args.sync_salvage:
        row = sync_salvage_hard_fails(write=True)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("sync_salvage:", "PASS" if row.get("ok") else row.get("error"))
        return 0 if row.get("ok") else 1
    if args.check_law_crosslink:
        row = check_salvage_law_crosslink()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_law_crosslink:", "PASS" if row.get("ok") else row.get("issues"))
        return 0 if row.get("ok") else 1
    if args.wire_law_crosslink:
        row = wire_salvage_law_crosslink(write=True)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("wire_law_crosslink:", "PASS" if row.get("ok") else row.get("error"))
        return 0 if row.get("ok") else 1
    if args.check_saved_at:
        row = check_translation_saved_at()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_saved_at:", "PASS" if row.get("ok") else row.get("reason"))
        return 0 if row.get("ok") else 1
    cfg = _read_json(TRANSLATION)
    if not cfg:
        print("FAIL: missing translation SSOT", file=sys.stderr)
        return 1
    accounts = [args.account] if args.account else []
    if not accounts:
        bundle = _read_json(OUTBOUND / "icp-ready-to-send-bundle-v1.json")
        accounts = [a.get("account_id") for a in (bundle.get("accounts") or []) if a.get("account_id")]
        if not accounts:
            accounts = ["fundmore", "ocree", "sourcea-factory"]
    rows = [check_account(aid, cfg) for aid in accounts]
    ok = all(r.get("ok") for r in rows)
    out = {"schema": "validate-email-translation-v1", "ok": ok, "accounts": rows}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for r in rows:
            status = "PASS" if r.get("ok") else "FAIL"
            print(f"{r.get('account_id')}: {status} {r.get('issues') or ''}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
