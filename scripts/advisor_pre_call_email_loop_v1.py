#!/usr/bin/env python3
"""Advisor pre-call email loop v2 — human clarity for business-not-AI audience.

Lane: advisor_pre_call (scheduled call brief — NOT W3 commercial).
SSOT: data/advisor-pre-call-email-v1.json
Receipt: ~/.sina/advisor-pre-call-email-loop-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "advisor-pre-call-email-v1.json"
EXAMPLES = ROOT / "data" / "advisor-pre-call-examples"
RECEIPT = SINA / "advisor-pre-call-email-loop-receipt-v1.json"
BAR = 90
DEFAULT_EXAMPLE = "richard-alberta-v2"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _word_count(text: str) -> int:
    pre = text.split("SourceA-Commercial")[0] if "SourceA-Commercial" in text else text
    pre = pre.split("Reply **stop**")[0] if "Reply **stop**" in pre else pre
    return len(re.findall(r"[A-Za-z0-9']+", pre))


def _bullet_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if re.match(r"^\s*[-•*]\s+", line))


def score_advisor_pre_call(body: str, *, cfg: dict | None = None) -> dict:
    cfg = cfg or _read_json(CONFIG)
    checks: list[dict] = []
    total = 0
    low = body.lower()
    wc = _word_count(body)
    hard_fails: list[str] = []

    wmin = int((cfg.get("word_count") or {}).get("min") or 80)
    wmax = int((cfg.get("word_count") or {}).get("max") or 220)

    for term in cfg.get("forbidden_jargon") or []:
        if term.lower() in low:
            hard_fails.append(f"forbidden:{term}")

    for term in cfg.get("forbidden_stack_hero") or []:
        if term.lower() in low:
            hard_fails.append(f"stack_hero:{term}")

    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from disclosure_ladder_v1 import check_outbound_body  # noqa: WPS433

        disc = check_outbound_body(body, lane="advisor_pre_call", context="advisor_pre_call")
        for hit in disc.get("forbidden_hits") or []:
            hard_fails.append(f"disclosure:{hit}")
        checks.append(
            {
                "id": "disclosure_tier_advisor",
                "points": 0 if disc.get("forbidden_hits") else 10,
                "max": 10,
                "tier": disc.get("tier"),
                "issues": disc.get("forbidden_hits") or [],
            }
        )
    except Exception:
        pass

    bullets = _bullet_lines(body)
    if bullets >= 3:
        hard_fails.append(f"architecture_bullets:{bullets}")

    theme_ok = any(p.lower() in low for p in (cfg.get("required_theme_phrases_any") or []))
    if not theme_ok:
        hard_fails.append("missing_one_theme")

    worldview_ok = any(p.lower() in low for p in (cfg.get("required_worldview_any") or []))
    if not worldview_ok:
        hard_fails.append("missing_worldview_shift")

    struct = cfg.get("structure") or {}

    # APC1 frame (15)
    frame_any = (struct.get("APC1_frame") or {}).get("required_phrases_any") or []
    apc1 = 15 if any(p.lower() in low for p in frame_any) else 0
    total += apc1
    checks.append({"id": "apc1_call_frame", "points": apc1, "max": 15, "issues": [] if apc1 else ["missing_call_frame"]})

    # APC2 one theme before products (25)
    theme_pos = min((low.find(p.lower()) for p in (cfg.get("required_theme_phrases_any") or []) if p.lower() in low), default=999)
    tf_pos = low.find("trustfield")
    apc2 = 25 if theme_ok and (tf_pos == -1 or theme_pos < tf_pos) else (10 if theme_ok else 0)
    total += apc2
    checks.append({"id": "apc2_one_theme_first", "points": apc2, "max": 25, "issues": [] if apc2 >= 20 else ["theme_missing_or_after_products"]})

    # APC3 light products (15)
    product_names = sum(1 for n in ("trustfield", "noetfield", "777") if n in low)
    apc3 = 15 if bullets == 0 and product_names <= 3 else max(0, 10 - bullets * 3)
    total += apc3
    checks.append({"id": "apc3_light_products", "points": apc3, "max": 15, "issues": [] if apc3 >= 12 else ["product_dump"]})

    # APC4 worldview (20)
    apc4 = 20 if worldview_ok else 0
    total += apc4
    checks.append({"id": "apc4_worldview_shift", "points": apc4, "max": 20, "issues": [] if apc4 else ["missing_why_care"]})

    # APC5 URLs (10)
    urls = re.findall(r"https?://[^\s\])<>]+", body)
    umin = int((cfg.get("url_count") or {}).get("min") or 1)
    umax = int((cfg.get("url_count") or {}).get("max") or 3)
    apc5 = 10 if umin <= len(urls) <= umax else (5 if urls else 0)
    total += apc5
    checks.append({"id": "apc5_live_urls", "points": apc5, "max": 10, "issues": [] if apc5 >= 8 else ["url_count"]})

    # APC6 not pitch (10)
    np_any = (struct.get("APC6_not_pitch") or struct.get("APC5_not_pitch") or {}).get("required_phrases_any") or []
    apc6 = 10 if any(p.lower() in low for p in np_any) else 0
    total += apc6
    checks.append({"id": "apc6_not_pitch", "points": apc6, "max": 10, "issues": [] if apc6 else ["missing_not_pitch"]})

    # APC7 no system layer (5) — hard fail already; bonus if clean
    apc7 = 5 if not any("forbidden:" in f or "stack_hero:" in f for f in hard_fails) else 0
    total += apc7
    checks.append({"id": "apc7_no_system_layer", "points": apc7, "max": 5, "issues": [f for f in hard_fails if f.startswith("forbidden:") or f.startswith("stack_hero:")]})

    if wc > wmax:
        hard_fails.append(f"word_count>{wmax}")
    if wc < wmin:
        hard_fails.append(f"word_count<{wmin}")

    pct = 0 if hard_fails else min(100, total)
    one_sentence = _one_sentence_summary(cfg, body)
    return {
        "lane": "advisor_pre_call",
        "schema_version": cfg.get("version", "2.0.0"),
        "human_clarity_pct": pct,
        "apc_pass": pct >= BAR and not hard_fails,
        "word_count": wc,
        "url_count": len(urls),
        "bullet_lines": bullets,
        "product_mentions": product_names,
        "one_theme_present": theme_ok,
        "worldview_present": worldview_ok,
        "one_sentence_test": one_sentence,
        "hard_fails": hard_fails,
        "checks": checks,
        "urls_found": urls,
    }


def _one_sentence_summary(cfg: dict, body: str) -> str:
    for ex in cfg.get("canonical_examples") or []:
        if ex.get("id") == DEFAULT_EXAMPLE and ex.get("one_sentence_summary"):
            return str(ex["one_sentence_summary"])
    return "Reader should restate: proof-of-what-happened theme + pre-call purpose"


def run_loop(*, body: str | None = None, example_id: str | None = None, write: bool = True) -> dict:
    cfg = _read_json(CONFIG)
    ex_id = example_id or DEFAULT_EXAMPLE
    if body is None:
        for ex in cfg.get("canonical_examples") or []:
            if ex.get("id") == ex_id and ex.get("status") != "deprecated":
                body = (ROOT / ex["path"]).read_text(encoding="utf-8")
                break
        if body is None:
            p = EXAMPLES / f"{ex_id}.txt"
            body = p.read_text(encoding="utf-8") if p.is_file() else ""

    scored = score_advisor_pre_call(body or "", cfg=cfg)
    verdict = "PASS" if scored["apc_pass"] else "IMPROVE"
    next_action = "hold — Sina read is ship authority" if scored["apc_pass"] else _next_action(scored)

    row = {
        "schema": "advisor-pre-call-email-loop-receipt-v1",
        "at": _now(),
        "law": str(cfg.get("law") or "docs/SOURCEA_ADVISOR_PRE_CALL_EMAIL_STANDARD_LOCKED_v1.md"),
        "ssot_version": cfg.get("version"),
        "ok": scored["apc_pass"],
        "verdict": verdict,
        "quality_bar_pct": BAR,
        "human_clarity_pct": scored["human_clarity_pct"],
        "example_id": ex_id,
        "scored": scored,
        "advisor_pre_call_line": f"advisor-pre-call · {verdict.lower()} · clarity={scored['human_clarity_pct']}% · bar={BAR}",
        "next_action_only": next_action,
        "command": "python3 scripts/advisor_pre_call_email_loop_v1.py --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _next_action(scored: dict) -> str:
    fails = scored.get("hard_fails") or []
    if any("missing_one_theme" in f for f in fails):
        return "add ONE unifying theme before any product name · re-run loop"
    if any("missing_worldview" in f for f in fails):
        return "add why-care sentence — reconstruct after the fact · re-run loop"
    if any(f.startswith("forbidden:") or f.startswith("stack_hero:") for f in fails):
        return "delete system/backend layer entirely · narrative only · re-run loop"
    if any("architecture_bullets" in f for f in fails):
        return "collapse to prose paragraphs · re-run loop"
    return "one bounded APC v2 fix · re-run advisor_pre_call_email_loop_v1.py --json"


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "advisor-pre-call-email-loop-receipt-v1":
        row = run_loop(write=True)
    return {
        "schema": "worker-hub-advisor-pre-call-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "advisor_pre_call_line": row.get("advisor_pre_call_line"),
        "human_clarity_pct": row.get("human_clarity_pct"),
        "next_action_only": row.get("next_action_only"),
        "law": row.get("law"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Advisor pre-call email loop v2")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--body-file", help="Path to email body to score")
    ap.add_argument("--example", default=DEFAULT_EXAMPLE)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    body = None
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    row = run_loop(body=body, example_id=None if args.body_file else args.example, write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("advisor_pre_call_line", ""))
        print(row.get("next_action_only", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
