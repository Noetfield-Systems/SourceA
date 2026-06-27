#!/usr/bin/env python3
"""Landing commercial copy gate — mandatory pre-ship PASS/BLOCK for public pages.

SSOT: data/landing-commercial-copy-audience-v1.json
Receipt: ~/.sina/enforcement/landing-commercial-copy-gate-receipt-v1.json
Law: docs/SOURCEA_TERMINOLOGY_AND_COMMERCIAL_TUNE_2026_LOCKED_v1.md

Suggests client-facing rewrites — does NOT auto-edit HTML or publish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "landing-commercial-copy-audience-v1.json"
GREEN = ROOT / "SourceA-landing" / "green-unified"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "enforcement" / "landing-commercial-copy-gate-receipt-v1.json"
LOG_PATH = SINA / "e2e-logs" / "validate-landing-commercial-copy-v1.log"

TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.I | re.S)
STRIP_TAGS = re.compile(r"<[^>]+>")
METRIC_NUM = re.compile(
    r"(\$\d+[KkMm]?|\b\d{1,3}%|\d{3,4}/\d{3,4})",
    re.I,
)
PRICE_LINE = re.compile(r"ar-price|sa-price|From \$|\$3[–-]10K|one-time|/mo", re.I)
CSS_PERCENT = re.compile(
    r"style=[^>]*%|--n[xy]:|linearGradient|offset=\"\d+%\"|viewBox|xmlns|stop-color",
    re.I,
)
POLICY_CLAIM = re.compile(r"100%\s*policy|policy at dispatch", re.I)
ILLUSTRATIVE = re.compile(r"\b(illustrative|sample metrics|for demo)\b", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _checksum(row: dict[str, Any]) -> str:
    body = {k: v for k, v in row.items() if k != "receipt_checksum"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]


def _write_receipt(row: dict[str, Any]) -> dict[str, Any]:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = dict(row)
    row.pop("receipt_checksum", None)
    row["receipt_checksum"] = _checksum(row)
    text = json.dumps(row, indent=2, ensure_ascii=False) + "\n"
    RECEIPT.write_text(text, encoding="utf-8")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(text)
    return row


def _extract_main_html(html: str) -> str:
    m = re.search(r"<main[^>]*>(.*)</main>", html, re.I | re.S)
    chunk = m.group(1) if m else html
    chunk = TAG_RE.sub(" ", chunk)
    chunk = STRIP_TAGS.sub(" ", chunk)
    chunk = unescape(re.sub(r"\s+", " ", chunk)).strip()
    return chunk


def _line_hits(html: str, pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for i, line in enumerate(html.splitlines(), start=1):
        if pattern.search(line):
            excerpt = line.strip()[:240]
            hits.append({"line": i, "excerpt": excerpt})
    return hits


def _suggest(finding_id: str, excerpt: str, audience: str) -> str:
    suggestions = {
        "wrong_you_founder_ops": (
            "Speak to the prospect, not founder ops — e.g. "
            "'Show prospects a governed proof demo' or 'Fixed builds with weekly exports for client stakeholders.'"
        ),
        "wrong_you_meta_buyer": (
            "Address the visitor directly — replace 'your buyer' with 'prospects', 'stakeholders', or 'clients'."
        ),
        "founder_confessional": (
            "Remove internal factory confession — sell the outcome: "
            "'Production-grade governance on every plan — replay demo stakeholders can verify.'"
        ),
        "founder_cost_leak": (
            "Remove internal run-cost — use buyer-facing bands only (e.g. 'Platform runtime from $2K/mo')."
        ),
        "stripe_secrets_leak": (
            "Remove Stripe/secrets operator note — link to pricing or hello@sourcea.app for procurement."
        ),
        "internal_account_leak": (
            "Remove 'SourceA account only' — use 'your deployment' or 'your environment'."
        ),
        "raw_founder_phrase": (
            "Rewrite in pro client-facing tone — outcome + proof + one action; not verbatim founder phrasing."
        ),
        "recipe_leak": (
            "Remove internal ports/routing/kernel references from public copy — keep mechanism in docs, not buyer pages."
        ),
        "fake_metric": (
            "Mark as illustrative ('sample metrics for demo') or cite a receipt-backed public JSON "
            "(boot-proof.json, trust-signals.json, phase1-proof-pack-public-v1.json)."
        ),
        "explain_not_sell": (
            "Lead with buyer outcome + proof + price/CTA — e.g. "
            "'Book a 15-minute proof call — fixed $3–10K build, replay on disk.'"
        ),
        "missing_commercial_shape": (
            "Add one clear outcome line, a price or plan anchor, and a single CTA (Book proof demo / hello@sourcea.app)."
        ),
        "audience_ambiguous": (
            "Set audience in data/landing-commercial-copy-audience-v1.json — founder vs agency vs platform."
        ),
    }
    base = suggestions.get(finding_id, "Rewrite for client-facing commercial tone.")
    if audience == "agency_reseller":
        return base + " (Agency page: 'your MRR' / 'your clients' is OK when the agency is the reader.)"
    return base


def _trust_backed_metrics() -> set[str]:
    backed: set[str] = set()
    trust = GREEN / "data" / "trust-signals.json"
    if trust.is_file():
        try:
            row = json.loads(trust.read_text(encoding="utf-8"))
            for key in ("valid_yes", "receipts_signed_today"):
                val = row.get(key)
                if val is not None:
                    backed.add(str(val))
        except (OSError, json.JSONDecodeError):
            pass
    pack = GREEN / "data" / "phase1-proof-pack-public-v1.json"
    if pack.is_file():
        try:
            row = json.loads(pack.read_text(encoding="utf-8"))
            score = row.get("score") or row.get("valid_yes")
            if score is not None:
                backed.add(str(score))
        except (OSError, json.JSONDecodeError):
            pass
    return backed


def scan_page(
    rel_path: str,
    html: str,
    *,
    cfg: dict[str, Any],
    backed_metrics: set[str],
) -> list[dict[str, Any]]:
    pages = cfg.get("pages") or {}
    page_cfg = pages.get(rel_path)
    findings: list[dict[str, Any]] = []

    if not page_cfg:
        findings.append(
            {
                "id": "audience_ambiguous",
                "page": rel_path,
                "line": 1,
                "excerpt": "(page not in audience registry)",
                "suggestion": _suggest("audience_ambiguous", "", "ambiguous"),
            }
        )
        return findings

    audience = str(page_cfg.get("audience") or "ambiguous")
    if audience == "founder_internal" or not page_cfg.get("commercial", True):
        return findings
    if audience == "ambiguous":
        findings.append(
            {
                "id": "audience_ambiguous",
                "page": rel_path,
                "line": 1,
                "excerpt": rel_path,
                "suggestion": _suggest("audience_ambiguous", rel_path, audience),
            }
        )
        return findings

    wrong_you_patterns = (cfg.get("wrong_you") or {}).get(audience, [])
    for pat in wrong_you_patterns:
        rx = re.compile(pat, re.I)
        for hit in _line_hits(html, rx):
            findings.append(
                {
                    "id": "wrong_you_founder_ops" if "buyer" not in pat else "wrong_you_meta_buyer",
                    "page": rel_path,
                    **hit,
                    "suggestion": _suggest(
                        "wrong_you_meta_buyer" if "buyer" in pat else "wrong_you_founder_ops",
                        hit["excerpt"],
                        audience,
                    ),
                }
            )

    for phrase in cfg.get("founder_voice_forbidden") or []:
        if phrase.lower() in html.lower():
            for hit in _line_hits(html, re.compile(re.escape(phrase), re.I)):
                fid = "stripe_secrets_leak" if "stripe" in phrase.lower() else "raw_founder_phrase"
                if "factory" in phrase.lower() and "run" in phrase.lower():
                    fid = "founder_confessional"
                if phrase.startswith("~$"):
                    fid = "founder_cost_leak"
                if "account only" in phrase.lower():
                    fid = "internal_account_leak"
                findings.append(
                    {
                        "id": fid,
                        "page": rel_path,
                        **hit,
                        "suggestion": _suggest(fid, hit["excerpt"], audience),
                    }
                )

    for pat in cfg.get("recipe_leak_patterns") or []:
        rx = re.compile(pat, re.I)
        for hit in _line_hits(html, rx):
            findings.append(
                {
                    "id": "recipe_leak",
                    "page": rel_path,
                    **hit,
                    "suggestion": _suggest("recipe_leak", hit["excerpt"], audience),
                }
            )

    illustrative_on_page = bool(ILLUSTRATIVE.search(html))
    for hit in _line_hits(html, METRIC_NUM):
        excerpt = hit["excerpt"]
        if CSS_PERCENT.search(excerpt):
            continue
        if POLICY_CLAIM.search(excerpt):
            continue
        if PRICE_LINE.search(excerpt):
            continue
        nums = METRIC_NUM.findall(excerpt)
        for num in nums:
            bare = re.sub(r"[^\d]", "", num)
            if illustrative_on_page:
                continue
            if bare and bare in backed_metrics:
                continue
            if "$" in num or "%" in num or "/" in num:
                findings.append(
                    {
                        "id": "fake_metric",
                        "page": rel_path,
                        **hit,
                        "metric": num,
                        "suggestion": _suggest("fake_metric", excerpt, audience),
                    }
                )
                break

    if page_cfg.get("commercial", True) and audience != "founder_internal":
        text = _extract_main_html(html).lower()
        reqs = cfg.get("commercial_requires") or {}
        has_outcome = any(s in text for s in reqs.get("outcome_signals") or [])
        has_price = any(s.lower() in text for s in reqs.get("price_signals") or [])
        has_cta = any(s.lower() in html.lower() for s in reqs.get("cta_signals") or [])
        if not (has_outcome and has_cta):
            findings.append(
                {
                    "id": "missing_commercial_shape",
                    "page": rel_path,
                    "line": 1,
                    "excerpt": f"outcome={has_outcome} price={has_price} cta={has_cta}",
                    "suggestion": _suggest("missing_commercial_shape", "", audience),
                }
            )

        operator_hits = 0
        for pat in cfg.get("operator_explain_patterns") or []:
            operator_hits += len(re.findall(pat, html, re.I))
        hero = html[:4000]
        hero_outcome = any(s in hero.lower() for s in ("proof", "book", "close", "$", "retainer", "demo"))
        if operator_hits >= 4 and not hero_outcome and audience in ("platform_buyer", "agency_and_platform"):
            findings.append(
                {
                    "id": "explain_not_sell",
                    "page": rel_path,
                    "line": 1,
                    "excerpt": f"{operator_hits} operator-role lines in hero without outcome/price/CTA",
                    "suggestion": _suggest("explain_not_sell", "", audience),
                }
            )

    # de-dupe by id+line+excerpt
    seen: set[tuple[str, int, str]] = set()
    unique: list[dict[str, Any]] = []
    for f in findings:
        key = (f.get("id", ""), int(f.get("line") or 0), f.get("excerpt", "")[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique


def scan_text_fixture(text: str, *, rel_path: str = "fixture.html") -> dict[str, Any]:
    cfg = _read(SSOT)
    findings = scan_page(rel_path, text, cfg=cfg, backed_metrics=_trust_backed_metrics())
    return {
        "schema": "landing-commercial-copy-gate-v1",
        "at": _now(),
        "verdict": "PASS" if not findings else "BLOCK",
        "ok": not findings,
        "publish_allowed": not findings,
        "pages_scanned": 1,
        "finding_count": len(findings),
        "findings": findings,
        "fixture": rel_path,
    }


def run_gate(
    *,
    landing_root: Path | None = None,
    pages: list[str] | None = None,
    all_commercial: bool = False,
) -> dict[str, Any]:
    cfg = _read(SSOT)
    if not cfg:
        raise SystemExit(f"FAIL: missing SSOT {SSOT}")

    root = landing_root or GREEN
    if not root.is_dir():
        raise SystemExit(f"FAIL: landing root missing: {root}")

    page_map = cfg.get("pages") or {}
    ship_pages = cfg.get("commercial_ship_pages")
    if pages:
        targets = pages
    elif all_commercial:
        targets = [p for p, meta in page_map.items() if meta.get("commercial", True)]
    elif ship_pages:
        targets = [p for p in ship_pages if (page_map.get(p) or {}).get("commercial", True)]
    else:
        targets = [p for p, meta in page_map.items() if meta.get("commercial", True)]
    backed = _trust_backed_metrics()
    all_findings: list[dict[str, Any]] = []
    scanned: list[str] = []

    for rel in sorted(targets):
        path = root / rel
        if not path.is_file():
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        scanned.append(rel)
        all_findings.extend(scan_page(rel, html, cfg=cfg, backed_metrics=backed))

    ok = len(all_findings) == 0
    row: dict[str, Any] = {
        "schema": "landing-commercial-copy-gate-v1",
        "at": _now(),
        "verdict": "PASS" if ok else "BLOCK",
        "ok": ok,
        "publish_allowed": ok,
        "pages_scanned": len(scanned),
        "pages": scanned,
        "finding_count": len(all_findings),
        "findings": all_findings,
        "ssot": str(SSOT.relative_to(ROOT)),
        "landing_root": str(root),
        "factory_now_line": (
            f"landing-copy-gate · {'PASS' if ok else 'BLOCK'} · "
            f"{len(scanned)} pages · {len(all_findings)} findings"
        ),
        "next_action": (
            "Ship allowed — commercial copy gate PASS"
            if ok
            else "Fix findings on disk (gate suggests rewrites — founder approves edits) — do not publish"
        ),
    }
    return _write_receipt(row)


def main() -> int:
    ap = argparse.ArgumentParser(description="Landing commercial copy gate v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--landing-root", type=Path, default=None)
    ap.add_argument("--page", action="append", default=[], help="Single page relative path (repeatable)")
    ap.add_argument(
        "--all-commercial",
        action="store_true",
        help="Scan every commercial page in audience registry (audit — not default ship bundle)",
    )
    ap.add_argument(
        "--fixture",
        choices=("bad-pricing",),
        help="Self-test fixture — BLOCK expected",
    )
    args = ap.parse_args()

    if args.fixture == "bad-pricing":
        bad = """
        <main>
          <p class="ar-lead">Your MRR grows when your agents book your calls — we run on our own factory.</p>
          <p>Stripe v1 — set Payment Link in secrets. ~$200/mo to run the factory.</p>
          <p>Brain orchestrates. Outreach books. Prove closes. Guard blocks. Expand compounds.</p>
          <span>13027</span><span>cloud_forge_run</span>
          <p>$24K pipeline · 34% proof-to-close</p>
        </main>
        """
        row = scan_text_fixture(bad, rel_path="pricing.html")
        row["fixture"] = "bad-pricing"
        row["factory_now_line"] = (
            f"landing-copy-gate · {row['verdict']} · fixture bad-pricing · {row['finding_count']} findings"
        )
        _write_receipt(row)
        if args.json:
            print(json.dumps(row, indent=2, ensure_ascii=False))
        else:
            print(row["factory_now_line"])
            for f in row.get("findings") or []:
                print(f"  BLOCK {f['page']}:{f.get('line')} [{f['id']}] {f.get('excerpt','')[:100]}")
                print(f"    → {f.get('suggestion','')[:160]}")
        return 1 if not row.get("ok") else 0

    pages = args.page or None
    row = run_gate(
        landing_root=args.landing_root,
        pages=pages,
        all_commercial=args.all_commercial,
    )
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("factory_now_line", "landing-copy-gate done"))
        if not row.get("ok"):
            for f in row.get("findings") or []:
                print(f"  BLOCK {f['page']}:{f.get('line')} [{f['id']}]")
                print(f"    line: {f.get('excerpt','')[:120]}")
                print(f"    suggest: {f.get('suggestion','')[:200]}")
        print(f"RECEIPT={RECEIPT}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
