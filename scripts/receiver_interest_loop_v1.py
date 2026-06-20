#!/usr/bin/env python3
"""Receiver Interest Loop (RIL) — score outbound from recipient POV.

Separate from machine OQG / FEFS: asks what is interesting enough to click,
know more, or reply — preview · catalog · demo link tied to their world.

Law: docs/SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md
Receipt: ~/.sina/receiver-interest-loop-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "w3-receiver-interest-assets-v1.json"
EMAILS_JSON = ROOT / "data" / "commercial" / "canada-priority-a-emails-v1.json"
W3_PACK_ROOT = SINA / "outbound"
RECEIPT = SINA / "receiver-interest-loop-receipt-v1.json"
BAR = 90
RIL_URL_TIMEOUT_S = 2.0
RIL_URL_RETRIES = 2
SOURCEA_PROBE_URL = "https://sourcea.com"
COMMERCIAL_PREVIEW_ACCOUNTS = ("fundmore", "ocree", "sourcea-factory")
_GENERIC_PREVIEW_PROMISES = frozenset({"five-minute preview", "preview", "demo", "walkthrough"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _probe_url_head(url: str, *, timeout: float = RIL_URL_TIMEOUT_S) -> tuple[bool, float]:
    """Single HEAD probe — returns (ok, elapsed_ms)."""
    if not url or not url.startswith("http"):
        return False, 0.0
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ok = 200 <= resp.status < 400
            return ok, (time.perf_counter() - t0) * 1000
    except (urllib.error.URLError, OSError, ValueError):
        return False, (time.perf_counter() - t0) * 1000


def _url_ok_ril(url: str, *, timeout: float = RIL_URL_TIMEOUT_S, retries: int = RIL_URL_RETRIES) -> dict:
    """U045 — RIL2 reachability via HEAD retry only (no GET fallback)."""
    last_ms = 0.0
    for attempt in range(1, retries + 1):
        ok, elapsed_ms = _probe_url_head(url, timeout=timeout)
        last_ms = elapsed_ms
        if ok:
            return {
                "ok": True,
                "method": "HEAD",
                "attempts": attempt,
                "elapsed_ms": round(elapsed_ms, 1),
                "upgrade": "U045",
            }
    return {
        "ok": False,
        "method": "HEAD",
        "attempts": retries,
        "elapsed_ms": round(last_ms, 1),
        "upgrade": "U045",
    }


def check_ril2_url_reachable(*, urls_in_body: list[str], has_url: bool | None = None) -> dict:
    """U045 — RIL2 interest URL reachable via HEAD retry."""
    has_url = bool(urls_in_body) if has_url is None else has_url
    probes: list[dict] = []
    reachable = False
    for u in urls_in_body[:3]:
        row = _url_ok_ril(u)
        probes.append({**row, "url": u})
        if row.get("ok"):
            reachable = True
            break
    ril2 = 15 if reachable else (8 if has_url else 0)
    issues_r2: list[str] = []
    if has_url and not reachable:
        issues_r2.append("interest_url_unreachable")
    elif not has_url:
        issues_r2.append("no_url_to_verify")
    return {
        "id": "ril_url_reachable",
        "points": ril2,
        "max": 15,
        "issues": issues_r2,
        "reachable": reachable,
        "probes": probes,
        "upgrade": "U045",
    }


def validate_ril2_url_reachable_acceptance() -> dict:
    """U045 acceptance — RIL HEAD-only retry with faster probe budget than legacy GET fallback."""
    retry_row = _url_ok_ril(SOURCEA_PROBE_URL)
    ril_budget_s = RIL_URL_TIMEOUT_S * RIL_URL_RETRIES
    legacy_budget_s = 8.0  # legacy HEAD 4s + GET 4s fallback
    live_rows: list[dict] = []
    for aid in ("ocree", "fundmore"):
        body, _ = _body_for(aid)
        pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
        urls = [u.rstrip(".,)") for u in re.findall(r"https?://[^\s\])<>]+", pre_sig)]
        live_rows.append(check_ril2_url_reachable(urls_in_body=urls))
    ok = (
        retry_row.get("method") == "HEAD"
        and int(retry_row.get("attempts") or 0) >= 1
        and RIL_URL_TIMEOUT_S <= 2.0
        and ril_budget_s <= legacy_budget_s
        and all(r.get("points") == 15 for r in live_rows)
    )
    return {
        "ok": ok,
        "upgrade": "U045",
        "sourcea_probe": SOURCEA_PROBE_URL,
        "ril_budget_s": ril_budget_s,
        "legacy_budget_s": legacy_budget_s,
        "head_only_no_get": retry_row.get("method") == "HEAD",
        "retry": retry_row,
        "live_w3": [{"account_id": aid, "points": r.get("points"), "reachable": r.get("reachable")} for aid, r in zip(("ocree", "fundmore"), live_rows)],
    }


def _url_ok(url: str) -> bool:
    """Legacy wrapper — prefer _url_ok_ril for RIL2."""
    return bool(_url_ok_ril(url).get("ok"))


def _brand_urls_from_config(cfg: dict | None = None) -> list[str]:
    cfg = cfg or _read_json(CONFIG)
    urls: list[str] = []
    for brand_block in (cfg.get("brands") or {}).values():
        urls.extend(str(v) for v in brand_block.values() if isinstance(v, str) and v.startswith("http"))
    return urls


def check_ril5_interest_url(
    *,
    urls_in_body: list[str],
    expected_urls: list[str],
    brand_urls: list[str] | None = None,
    has_url: bool | None = None,
) -> dict:
    """U042 — RIL5 canonical URL must match account interest_urls SSOT.

    Wrong demo URL on same brand = -5 pts (10/15). Off-brand URL = 5/15.
    """
    expected = [str(u) for u in expected_urls]
    brand_urls = brand_urls if brand_urls is not None else _brand_urls_from_config()
    has_url = bool(urls_in_body) if has_url is None else has_url
    matched_expected = any(any(e.rstrip("/") in u.rstrip("/") for e in expected) for u in urls_in_body)
    on_brand = any(any(b.rstrip("/") in u.rstrip("/") for b in brand_urls) for u in urls_in_body)
    if matched_expected:
        ril5 = 15
        issues_r5: list[str] = []
    elif on_brand:
        ril5 = 10
        issues_r5 = ["url_not_canonical_demo"]
    elif has_url:
        ril5 = 5
        issues_r5 = ["off_brand_or_wrong_preview"]
    else:
        ril5 = 0
        issues_r5 = ["missing_catalog_demo_link"]
    return {
        "id": "ril_catalog_demo_match",
        "points": ril5,
        "max": 15,
        "deduct_from_max": 15 - ril5,
        "issues": issues_r5,
        "expected_urls": expected,
        "urls_found": urls_in_body,
        "upgrade": "U042",
    }


def validate_ril5_interest_url_acceptance() -> dict:
    """U042 acceptance — wrong demo URL deducts exactly 5 points on RIL5."""
    cfg = _read_json(CONFIG)
    ocree = (cfg.get("accounts") or {}).get("ocree") or {}
    expected = [str(u) for u in (ocree.get("interest_urls") or [])]
    canonical = check_ril5_interest_url(
        urls_in_body=["https://www.trustfield.ca/demo"],
        expected_urls=expected,
    )
    wrong_demo = check_ril5_interest_url(
        urls_in_body=["https://www.trustfield.ca/pilot"],
        expected_urls=expected,
    )
    off_brand = check_ril5_interest_url(
        urls_in_body=["https://evil.example/demo"],
        expected_urls=expected,
    )
    live_rows: list[dict] = []
    for aid in ("ocree", "fundmore"):
        row_cfg = (cfg.get("accounts") or {}).get(aid) or {}
        body, _ = _body_for(aid)
        pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
        urls = [u.rstrip(".,)") for u in re.findall(r"https?://[^\s\])<>]+", pre_sig)]
        live_rows.append(
            check_ril5_interest_url(
                urls_in_body=urls,
                expected_urls=[str(u) for u in (row_cfg.get("interest_urls") or [])],
            )
        )
    ok = (
        canonical.get("points") == 15
        and wrong_demo.get("points") == 10
        and wrong_demo.get("deduct_from_max") == 5
        and off_brand.get("points") == 5
        and all(r.get("points") == 15 for r in live_rows)
    )
    return {
        "ok": ok,
        "upgrade": "U042",
        "canonical_pts": canonical.get("points"),
        "wrong_demo_pts": wrong_demo.get("points"),
        "wrong_demo_deduct": wrong_demo.get("deduct_from_max"),
        "off_brand_pts": off_brand.get("points"),
        "live_w3": [{"account_id": aid, "points": r.get("points")} for aid, r in zip(("ocree", "fundmore"), live_rows)],
        "ssot": str(CONFIG),
    }


def load_interest_asset_row(account_id: str, cfg: dict | None = None) -> dict:
    """U048 — per-account interest asset row from w3-receiver-interest-assets SSOT."""
    data = cfg if cfg is not None else _read_json(CONFIG)
    return dict((data.get("accounts") or {}).get(account_id) or {})


def check_preview_promise_ssot_row(account_id: str, row_cfg: dict) -> dict:
    """U048 — preview_promise + interest_urls must exist per commercial account row."""
    promise = str(row_cfg.get("preview_promise") or "").strip()
    urls = [str(u) for u in (row_cfg.get("interest_urls") or []) if str(u).startswith("http")]
    issues: list[str] = []
    if not promise:
        issues.append("missing_preview_promise")
    elif len(promise) < 8:
        issues.append("preview_promise_too_short")
    elif promise.lower() in _GENERIC_PREVIEW_PROMISES:
        issues.append("generic_preview_promise")
    if not urls:
        issues.append("missing_interest_urls")
    if not row_cfg.get("company"):
        issues.append("missing_company")
    if not row_cfg.get("brand"):
        issues.append("missing_brand")
    return {
        "account_id": account_id,
        "ok": not issues,
        "preview_promise": promise or None,
        "interest_urls": urls,
        "catalog_label": row_cfg.get("catalog_label"),
        "issues": issues,
        "upgrade": "U048",
    }


def validate_preview_promise_ssot_acceptance() -> dict:
    """U048 acceptance — fundmore/ocree/sourcea-factory rows in interest-assets SSOT."""
    cfg = _read_json(CONFIG)
    accounts = cfg.get("accounts") or {}
    rows = [check_preview_promise_ssot_row(aid, accounts.get(aid) or {}) for aid in COMMERCIAL_PREVIEW_ACCOUNTS]
    promises = [str(r.get("preview_promise") or "").lower() for r in rows if r.get("preview_promise")]
    distinct = len(set(promises)) == len(COMMERCIAL_PREVIEW_ACCOUNTS)
    ok = all(r.get("ok") for r in rows) and distinct
    return {
        "ok": ok,
        "upgrade": "U048",
        "accounts": rows,
        "distinct_promises": distinct,
        "acceptance": "fundmore/ocree/sourcea rows",
        "ssot": str(CONFIG),
        "check": "python3 scripts/receiver_interest_loop_v1.py --check-preview-promise-ssot --json",
    }


_EMPTY_PREVIEW_PATTERNS = (
    r"I(?:'d|\s+would)?\s+be\s+happy\s+to\s+show",
    r"I\s+can\s+walk\s+through",
    r"walk\s+you\s+through",
    r"walk\s*through",
    r"happy\s+to\s+(?:walk|show)",
    r"(?:walk through|show a|happy to show|five-minute demo)\??\s*$",
    r"(?:five|5)[-\s]?minute\s+(?:demo|walkthrough|replay|preview)",
    r"(?:quick|short)\s+(?:demo|walkthrough|preview)",
)


def _empty_preview_offer(pre_sig: str, *, has_url: bool) -> bool:
    """U043 — walkthrough/demo offer without clickable link."""
    if has_url:
        return False
    return any(re.search(p, pre_sig, re.I | re.M) for p in _EMPTY_PREVIEW_PATTERNS)


def check_ril4_preview_promise(
    *,
    pre_sig: str,
    low: str,
    has_url: bool,
    preview_promise: str = "",
) -> dict:
    """U043 — concrete preview promise; empty walkthrough without link = 0."""
    promise = str(preview_promise or "").lower()
    empty_offer = _empty_preview_offer(pre_sig, has_url=has_url)
    promise_words = ("replay", "demo", "preview", "minute", "no signup", "screen-share", "live")
    has_promise = any(p in low for p in promise_words) or (promise and promise.split()[0] in low)
    if empty_offer:
        ril4 = 0
        issues_r4 = ["empty_preview_promise_no_link"]
    elif has_promise and has_url:
        ril4 = 20
        issues_r4 = []
    elif has_promise:
        ril4 = 12
        issues_r4 = ["promise_without_link"]
    else:
        ril4 = 5
        issues_r4 = ["no_concrete_preview"]
    return {
        "id": "ril_preview_promise",
        "points": ril4,
        "max": 20,
        "issues": issues_r4,
        "empty_offer": empty_offer,
        "upgrade": "U043",
    }


def validate_ril4_preview_promise_acceptance() -> dict:
    """U043 acceptance — walkthrough without link scores 0 on RIL4."""
    cfg = _read_json(CONFIG)
    ocree = (cfg.get("accounts") or {}).get("ocree") or {}
    promise = str(ocree.get("preview_promise") or "")
    walk_no_link = check_ril4_preview_promise(
        pre_sig="Hi Anne, curious about issuance. Happy to walk you through a short demo.",
        low="hi anne, curious about issuance. happy to walk you through a short demo.",
        has_url=False,
        preview_promise=promise,
    )
    with_link = check_ril4_preview_promise(
        pre_sig="Curious?\n\nIf relevant — five-minute replay:\n\nhttps://www.trustfield.ca/demo",
        low="curious?\n\nif relevant — five-minute replay:\n\nhttps://www.trustfield.ca/demo",
        has_url=True,
        preview_promise=promise,
    )
    live_rows: list[dict] = []
    for aid in ("ocree", "fundmore"):
        body, _ = _body_for(aid)
        row_cfg = (cfg.get("accounts") or {}).get(aid) or {}
        pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
        urls = [u.rstrip(".,)") for u in re.findall(r"https?://[^\s\])<>]+", pre_sig)]
        live_rows.append(
            check_ril4_preview_promise(
                pre_sig=pre_sig,
                low=pre_sig.lower(),
                has_url=bool(urls),
                preview_promise=str(row_cfg.get("preview_promise") or ""),
            )
        )
    ok = (
        walk_no_link.get("points") == 0
        and with_link.get("points") == 20
        and all(r.get("points") == 20 for r in live_rows)
    )
    return {
        "ok": ok,
        "upgrade": "U043",
        "walkthrough_no_link_pts": walk_no_link.get("points"),
        "with_link_pts": with_link.get("points"),
        "live_w3": [{"account_id": aid, "points": r.get("points")} for aid, r in zip(("ocree", "fundmore"), live_rows)],
    }


MODE_A = "A_curiosity_first"
MODE_B = "B_interest_asset"


def resolve_ril_bar_policy(*, declared_mode: str | None, detected_mode: str) -> dict:
    """U046 — RIL bar is Mode B only; skip only when compose_mode A is explicit."""
    declared = str(declared_mode or "").strip()
    if declared == MODE_A:
        return {
            "ril_bar_applied": False,
            "ril_bar_skipped": True,
            "ril_skip_explicit": True,
            "ril_skip_reason": "compose_mode_A_curiosity_first_explicit",
            "detected_mode": detected_mode,
            "declared_mode": declared,
            "upgrade": "U046",
        }
    return {
        "ril_bar_applied": True,
        "ril_bar_skipped": False,
        "ril_skip_explicit": False,
        "ril_skip_reason": None,
        "detected_mode": detected_mode,
        "declared_mode": declared or None,
        "upgrade": "U046",
    }


def validate_ril_mode_b_bar_acceptance() -> dict:
    """U046 acceptance — no silent RIL skip; Mode B always scored."""
    cfg = _read_json(CONFIG)
    ocree = (cfg.get("accounts") or {}).get("ocree") or {}
    body_a = "Hi Anne,\n\nCurious whether issuance proof is on your radar yet?\nReply **stop**"
    body_b = (
        "Hi Anne,\n\nCurious?\n\nIf useful — replay:\n\nhttps://www.trustfield.ca/demo\nReply **stop**"
    )
    explicit_a = score_receiver_interest(
        account_id="accept-a",
        body=body_a,
        cfg_row=ocree,
        declared_mode=MODE_A,
    )
    explicit_b = score_receiver_interest(
        account_id="accept-b",
        body=body_b,
        cfg_row=ocree,
        declared_mode=MODE_B,
    )
    undeclared_b = score_receiver_interest(
        account_id="accept-undeclared",
        body=body_b,
        cfg_row=ocree,
        declared_mode=None,
    )
    compile_dir = ROOT / "data" / "icp-compile"
    live_rows: list[dict] = []
    for aid in ("ocree", "fundmore"):
        forge = _read_json(compile_dir / f"{aid}-v1.json")
        body, _ = _body_for(aid)
        row_cfg = (cfg.get("accounts") or {}).get(aid) or {}
        scored = score_receiver_interest(
            account_id=aid,
            body=body,
            cfg_row=row_cfg,
            declared_mode=str(forge.get("compose_mode") or "") or None,
        )
        live_rows.append(scored)
    silent_skip = any(
        a.get("ril_bar_skipped") and not a.get("ril_skip_explicit")
        for a in [explicit_a, explicit_b, undeclared_b, *live_rows]
    )
    ok = (
        explicit_a.get("ril_bar_skipped")
        and explicit_a.get("ril_skip_explicit")
        and explicit_a.get("ril_skip_reason")
        and explicit_b.get("ril_bar_applied")
        and not explicit_b.get("ril_bar_skipped")
        and undeclared_b.get("ril_bar_applied")
        and not silent_skip
        and all(r.get("ril_bar_applied") and not r.get("ril_bar_skipped") for r in live_rows)
    )
    return {
        "ok": ok,
        "upgrade": "U046",
        "explicit_a_skipped": explicit_a.get("ril_bar_skipped"),
        "explicit_b_applied": explicit_b.get("ril_bar_applied"),
        "undeclared_b_applied": undeclared_b.get("ril_bar_applied"),
        "silent_skip": silent_skip,
        "live_w3": [
            {
                "account_id": aid,
                "declared_mode": r.get("compose_mode_declared"),
                "ril_bar_applied": r.get("ril_bar_applied"),
                "ril_bar_skipped": r.get("ril_bar_skipped"),
            }
            for aid, r in zip(("ocree", "fundmore"), live_rows)
        ],
    }


def detect_compose_mode(body: str) -> str:
    """U014 — Mode A vs B auto-detect from body (demo/replay words)."""
    low = body.lower()
    if re.search(r"\b(demo|preview|replay|walk through|walkthrough|pilot)\b", low):
        return "B_interest_asset"
    return "A_curiosity_first"


def _body_for(account_id: str) -> tuple[str, Path | None]:
    pack_dir = W3_PACK_ROOT / f"w3-canada-{account_id}"
    body_path = pack_dir / "body.txt"
    if body_path.is_file():
        return body_path.read_text(encoding="utf-8"), body_path
    data = _read_json(EMAILS_JSON)
    for row in data.get("accounts") or []:
        if row.get("id") == account_id:
            return str(row.get("body_full") or row.get("body") or ""), None
    return "", None


def score_receiver_interest(
    *,
    account_id: str,
    body: str,
    cfg_row: dict,
    declared_mode: str | None = None,
) -> dict:
    """Score 0–100 from recipient POV — separate bar from OQG."""
    checks: list[dict] = []
    total = 0
    low = body.lower()
    pre_sig = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
    detected_mode = detect_compose_mode(body)
    declared = str(declared_mode or "").strip()
    mode_ok = not declared or detected_mode == declared
    checks.append(
        {
            "id": "ril_compose_mode",
            "points": 0 if mode_ok else 0,
            "max": 0,
            "detected": detected_mode,
            "declared": declared or None,
            "issues": [] if mode_ok else [f"mode_mismatch:{declared}!={detected_mode}"],
            "upgrade": "U014",
        }
    )
    if not mode_ok:
        return {
            "account_id": account_id,
            "company": cfg_row.get("company"),
            "brand": cfg_row.get("brand"),
            "receiver_interest_pct": min(89, BAR - 1),
            "ril_pass": False,
            "compose_mode_detected": detected_mode,
            "compose_mode_declared": declared or None,
            "checks": checks,
            "urls_found": [],
            "expected_urls": [str(u) for u in (cfg_row.get("interest_urls") or [])],
            "preview_promise": cfg_row.get("preview_promise"),
            "catalog_label": cfg_row.get("catalog_label"),
        }

    bar_policy = resolve_ril_bar_policy(declared_mode=declared, detected_mode=detected_mode)
    checks.append({"id": "ril_bar_policy", "max": 0, "points": 0, "issues": [], **bar_policy})
    if bar_policy.get("ril_bar_skipped"):
        return {
            "account_id": account_id,
            "company": cfg_row.get("company"),
            "brand": cfg_row.get("brand"),
            "receiver_interest_pct": None,
            "ril_pass": True,
            "ril_bar_applied": False,
            **bar_policy,
            "compose_mode_detected": detected_mode,
            "compose_mode_declared": declared or None,
            "checks": checks,
            "urls_found": [],
            "expected_urls": [str(u) for u in (cfg_row.get("interest_urls") or [])],
            "preview_promise": cfg_row.get("preview_promise"),
            "catalog_label": cfg_row.get("catalog_label"),
        }

    urls_in_body = re.findall(r"https?://[^\s\])<>]+", pre_sig)
    urls_in_body = [u.rstrip(".,)") for u in urls_in_body]
    expected = [str(u) for u in (cfg_row.get("interest_urls") or [])]

    # RIL1 — clickable interest asset present (25)
    has_url = bool(urls_in_body)
    ril1 = 25 if has_url else 0
    total += ril1
    checks.append(
        {
            "id": "ril_clickable_asset",
            "points": ril1,
            "max": 25,
            "issues": [] if has_url else ["no_preview_or_demo_url"],
        }
    )

    # RIL2 — URL reachable (15) — U045 HEAD retry, no GET fallback
    ril2_row = check_ril2_url_reachable(urls_in_body=urls_in_body, has_url=has_url)
    ril2 = int(ril2_row["points"])
    total += ril2
    checks.append(ril2_row)

    # RIL3 — recipient-specific world (25)
    signals = [str(s).lower() for s in (cfg_row.get("must_signal") or [])]
    world = [str(w).lower() for w in (cfg_row.get("receiver_world") or [])]
    hit_signal = sum(1 for s in signals if s in low)
    hit_world = sum(1 for w in world if w in low)
    spec_score = min(25, hit_signal * 8 + min(9, hit_world * 3))
    ril3 = spec_score
    total += ril3
    checks.append(
        {
            "id": "ril_recipient_specific",
            "points": ril3,
            "max": 25,
            "issues": [] if ril3 >= 18 else ["weak_recipient_hook"],
        }
    )

    # RIL4 — concrete preview promise, not empty offer (20) — U043 refinement
    ril4_row = check_ril4_preview_promise(
        pre_sig=pre_sig,
        low=low,
        has_url=has_url,
        preview_promise=str(cfg_row.get("preview_promise") or ""),
    )
    ril4 = int(ril4_row["points"])
    total += ril4
    checks.append(ril4_row)

    # RIL5 — expected brand URL or catalog path (15) — U042 interest_urls SSOT
    ril5_row = check_ril5_interest_url(
        urls_in_body=urls_in_body,
        expected_urls=expected,
        has_url=has_url,
    )
    ril5 = int(ril5_row["points"])
    issues_r5 = list(ril5_row.get("issues") or [])
    total += ril5
    checks.append({**ril5_row, "issues": issues_r5})

    pct = min(100, max(0, total))
    return {
        "account_id": account_id,
        "company": cfg_row.get("company"),
        "brand": cfg_row.get("brand"),
        "receiver_interest_pct": pct,
        "ril_pass": pct >= BAR and mode_ok,
        "ril_bar_applied": True,
        "ril_bar_skipped": False,
        "ril_skip_explicit": False,
        "ril_skip_reason": None,
        "compose_mode_detected": detected_mode,
        "compose_mode_declared": declared or None,
        "checks": checks,
        "urls_found": urls_in_body,
        "expected_urls": expected,
        "preview_promise": cfg_row.get("preview_promise"),
        "catalog_label": cfg_row.get("catalog_label"),
    }


def run_ril(*, write: bool = True, account_ids: list[str] | None = None) -> dict:
    cfg = _read_json(CONFIG)
    accounts_cfg = cfg.get("accounts") or {}
    compile_dir = ROOT / "data" / "icp-compile"
    ids = account_ids or list(accounts_cfg.keys())
    artifacts: list[dict] = []
    for aid in ids:
        row_cfg = accounts_cfg.get(aid) or {}
        forge = _read_json(compile_dir / f"{aid}-v1.json")
        body, body_path = _body_for(aid)
        if not body.strip():
            artifacts.append(
                {
                    "account_id": aid,
                    "receiver_interest_pct": 0,
                    "ril_pass": False,
                    "verdict": "IMPROVE",
                    "next_action": f"prepare pack for {aid} — missing body",
                    "checks": [{"id": "ril_missing_body", "issues": ["no_body"]}],
                }
            )
            continue
        scored = score_receiver_interest(
            account_id=aid,
            body=body,
            cfg_row=row_cfg,
            declared_mode=str(forge.get("compose_mode") or "") or None,
        )
        failures = []
        for chk in scored.get("checks") or []:
            for iss in chk.get("issues") or []:
                failures.append(f"{chk.get('id')}:{iss}")
        verdict = "PASS" if scored["ril_pass"] else "IMPROVE"
        next_action = _next_action(aid, scored, failures)
        artifacts.append(
            {
                **scored,
                "body_path": str(body_path) if body_path else "",
                "verdict": verdict,
                "failures": failures,
                "next_action": next_action,
            }
        )

    improve_n = sum(1 for a in artifacts if a.get("verdict") == "IMPROVE")
    pass_n = sum(1 for a in artifacts if a.get("verdict") == "PASS")
    w3_pass = all(a.get("ril_pass") for a in artifacts) if artifacts else False
    avg = round(sum(a.get("receiver_interest_pct") or 0 for a in artifacts) / len(artifacts)) if artifacts else 0

    row = {
        "schema": "receiver-interest-loop-receipt-v1",
        "at": _now(),
        "law": str(cfg.get("law") or "docs/SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md"),
        "ok": w3_pass,
        "verdict": "PASS" if w3_pass else "IMPROVE",
        "quality_bar_pct": BAR,
        "receiver_interest_avg_pct": avg,
        "summary": {"artifacts": len(artifacts), "pass": pass_n, "improve": improve_n, "w3_all_pass": w3_pass},
        "artifacts": artifacts,
        "receiver_interest_line": _line(improve_n, pass_n, avg, w3_pass),
        "next_action_only": _pick_one(artifacts),
        "command": "python3 scripts/receiver_interest_loop_v1.py --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _next_action(aid: str, scored: dict, failures: list[str]) -> str:
    if scored.get("ril_pass"):
        return "hold — receiver sees clear preview path"
    if any("no_preview" in f or "no_url" in f or "empty_preview" in f for f in failures):
        cfg = (_read_json(CONFIG).get("accounts") or {}).get(aid) or {}
        url = (cfg.get("interest_urls") or ["https://www.trustfield.ca/demo"])[0]
        label = cfg.get("preview_promise") or "five-minute preview"
        return f"add recipient interest link — {label}: {url} · re-pack · re-RIL"
    if any("weak_recipient" in f for f in failures):
        return f"sharpen hook for {aid} receiver world — mention their lane · re-pack · re-RIL"
    if any("unreachable" in f for f in failures):
        return "fix or swap interest URL to reachable demo/catalog · re-pack · re-RIL"
    return "one bounded receiver-interest fix · re-run receiver_interest_loop_v1.py --json"


def _line(improve_n: int, pass_n: int, avg: int, w3_pass: bool) -> str:
    bit = "w3=ready" if w3_pass else f"w3=improve({improve_n})"
    return f"receiver-interest · {bit} · avg={avg}% · pass={pass_n} · bar={BAR}"


def _pick_one(artifacts: list[dict]) -> str:
    for art in artifacts:
        if art.get("verdict") == "IMPROVE":
            return str(art.get("next_action") or "re-run RIL after fix")
    return "all W3 artifacts pass receiver-interest bar"


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "receiver-interest-loop-receipt-v1":
        row = run_ril(write=True)
    return {
        "schema": "worker-hub-receiver-interest-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "verdict": row.get("verdict"),
        "receiver_interest_line": row.get("receiver_interest_line"),
        "next_action_only": row.get("next_action_only"),
        "receiver_interest_avg_pct": row.get("receiver_interest_avg_pct"),
        "summary": row.get("summary"),
        "artifacts": row.get("artifacts") or [],
        "law": row.get("law"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Receiver Interest Loop — recipient POV quality")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--check-interest-urls", action="store_true", help="U042 — RIL5 interest_urls SSOT acceptance")
    ap.add_argument("--check-preview-promise", action="store_true", help="U043 — empty walkthrough without link = 0")
    ap.add_argument("--check-preview-promise-ssot", action="store_true", help="U048 — preview_promise per account in w3-receiver-interest-assets")
    ap.add_argument("--check-url-reachable", action="store_true", help="U045 — RIL2 HEAD retry faster than GET on sourcea.com")
    ap.add_argument("--check-ril-bar-skip", action="store_true", help="U046 — Mode B RIL bar; skip only when Mode A explicit")
    ap.add_argument("--account", action="append", dest="accounts")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    if args.check_interest_urls:
        row = validate_ril5_interest_url_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_interest_urls:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_preview_promise:
        row = validate_ril4_preview_promise_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_preview_promise:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_preview_promise_ssot:
        row = validate_preview_promise_ssot_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_preview_promise_ssot:", "PASS" if row.get("ok") else row.get("accounts"))
        return 0 if row.get("ok") else 1
    if args.check_url_reachable:
        row = validate_ril2_url_reachable_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_url_reachable:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    if args.check_ril_bar_skip:
        row = validate_ril_mode_b_bar_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_ril_bar_skip:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    row = run_ril(write=not args.no_write, account_ids=args.accounts)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("receiver_interest_line", ""))
        print(row.get("next_action_only", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
