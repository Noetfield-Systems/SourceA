#!/usr/bin/env python3
"""Landing copy depth gate — BLOCK shallow, repetitive, padded public copy before ship.

Separate from landing_commercial_copy_gate_v1.py (voice/tone).
SSOT: data/landing-copy-depth-gate-v1.json
Receipt: ~/.sina/enforcement/landing-copy-depth-gate-receipt-v1.json

Suggests cut/tighten — does NOT auto-edit HTML or publish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "landing-copy-depth-gate-v1.json"
GREEN = ROOT / "SourceA-landing" / "green-unified"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "enforcement" / "landing-copy-depth-gate-receipt-v1.json"
LOG_PATH = SINA / "e2e-logs" / "validate-landing-copy-depth-v1.log"

TAG_RE = re.compile(r"<(script|style|nav|footer)[^>]*>.*?</\1>", re.I | re.S)
MAIN_RE = re.compile(r"<main[^>]*>(.*)</main>", re.I | re.S)
STRIP_TAGS = re.compile(r"<[^>]+>")


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


def _main_html(html: str) -> str:
    m = MAIN_RE.search(html)
    return m.group(1) if m else html


def _plain_text(chunk: str) -> str:
    chunk = TAG_RE.sub(" ", chunk)
    chunk = STRIP_TAGS.sub(" ", chunk)
    return unescape(re.sub(r"\s+", " ", chunk)).strip()


def _line_hits(html: str, pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for i, line in enumerate(html.splitlines(), start=1):
        if pattern.search(line):
            hits.append({"line": i, "excerpt": line.strip()[:240]})
    return hits


def _beat_counts(html: str, pattern: str) -> tuple[int, list[dict[str, Any]]]:
    rx = re.compile(pattern, re.I)
    hits = _line_hits(html, rx)
    return len(hits), hits


def scan_page(rel_path: str, html: str, *, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    main = _main_html(html)
    plain = _plain_text(main)

    for beat in cfg.get("beats") or []:
        count, hits = _beat_counts(main, str(beat["pattern"]))
        max_per = int(beat.get("max_per_page") or 1)
        if count > max_per:
            for hit in hits[max_per:]:
                findings.append(
                    {
                        "id": "repetition",
                        "beat_id": beat["id"],
                        "page": rel_path,
                        **hit,
                        "suggestion": f"CUT — repeated beat '{beat.get('label', beat['id'])}' ({count}× on page). "
                        + str(beat.get("suggestion") or "Say it once."),
                    }
                )

    for filler in cfg.get("filler_phrases") or []:
        rx = re.compile(str(filler["pattern"]), re.I | re.S)
        for hit in _line_hits(main, rx):
            findings.append(
                {
                    "id": "filler",
                    "page": rel_path,
                    **hit,
                    "suggestion": f"CUT — filler. {filler.get('suggestion', 'Delete this line.')}",
                }
            )

    lexemes = cfg.get("proof_lexemes") or []
    proof_count = sum(len(re.findall(rf"\b{re.escape(w)}\b", plain, re.I)) for w in lexemes)
    anchors = cfg.get("artifact_anchors") or []
    artifact_hits = sum(1 for a in anchors if a.lower() in html.lower())
    if proof_count >= 10 and artifact_hits == 0:
        findings.append(
            {
                "id": "hollow_proof",
                "page": rel_path,
                "line": 1,
                "excerpt": f"{proof_count} proof/controlled tokens · 0 artifact anchors",
                "suggestion": "CUT hollow proof lines — add one real anchor (sourcea-boot, boot-proof.json, /sourcea/proof) or delete claims.",
            }
        )
    elif plain.lower().count("receipt logged") >= 3 and artifact_hits < 1:
        findings.append(
            {
                "id": "hollow_proof",
                "page": rel_path,
                "line": 1,
                "excerpt": "receipt logged repeated without artifact link",
                "suggestion": "CUT repeats — one receipt claim + link to sourcea-boot or live proof page.",
            }
        )

    padding = cfg.get("padding") or {}
    section_count = len(re.findall(r"<section\b", main, re.I))
    max_sections = int(padding.get("max_sections_per_page") or 7)
    if section_count > max_sections:
        findings.append(
            {
                "id": "padding",
                "page": rel_path,
                "line": 1,
                "excerpt": f"{section_count} sections in <main> (max {max_sections})",
                "suggestion": "CUT whole sections — merge flywheel + win stories + revenue math into one decision block.",
            }
        )

    explore_class = str(padding.get("explore_section_class") or "sa-explore")
    if explore_class in main:
        card_count = len(re.findall(r"sa-explore-card", main, re.I))
        max_cards = int(padding.get("max_explore_cards") or 12)
        if card_count >= max_cards and section_count > max_sections:
            for hit in _line_hits(main, re.compile(r"sa-explore", re.I))[:1]:
                findings.append(
                    {
                        "id": "padding",
                        "page": rel_path,
                        **hit,
                        "excerpt": hit["excerpt"][:120],
                        "suggestion": "CUT sa-explore grid — 12-link chapter nav is site chrome; keep footer nav only.",
                    }
                )

    cta_bands = len(re.findall(r"sa-cta-band", main, re.I))
    if cta_bands >= 2:
        findings.append(
            {
                "id": "padding",
                "page": rel_path,
                "line": 1,
                "excerpt": f"{cta_bands} CTA bands on one page",
                "suggestion": "CUT duplicate CTA band — one closing call to action is enough.",
            }
        )

    return findings


def scan_cross_page(page_html: dict[str, str], *, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    beat_totals: dict[str, int] = defaultdict(int)
    beat_pages: dict[str, set[str]] = defaultdict(set)

    for rel, html in page_html.items():
        main = _main_html(html)
        for beat in cfg.get("beats") or []:
            count, _ = _beat_counts(main, str(beat["pattern"]))
            if count:
                beat_totals[beat["id"]] += count
                beat_pages[beat["id"]].add(rel)

    min_pages = int(cfg.get("cross_page_beat_min_pages") or 3)
    min_total = int(cfg.get("cross_page_beat_min_total") or 6)
    beat_map = {b["id"]: b for b in (cfg.get("beats") or [])}

    for beat_id, total in beat_totals.items():
        pages = beat_pages[beat_id]
        if len(pages) >= min_pages and total >= min_total:
            beat = beat_map.get(beat_id, {})
            findings.append(
                {
                    "id": "cross_page_repetition",
                    "beat_id": beat_id,
                    "page": "(cross-page)",
                    "line": 0,
                    "excerpt": f"'{beat.get('label', beat_id)}' ×{total} across {len(pages)} pages: {', '.join(sorted(pages))}",
                    "suggestion": f"CUT sitewide echo — keep '{beat.get('label', beat_id)}' on proof.html only. "
                    + str(beat.get("suggestion") or "Say it once site-wide."),
                }
            )
    return findings


def run_gate(
    *,
    landing_root: Path | None = None,
    pages: list[str] | None = None,
    audit_all: bool = False,
) -> dict[str, Any]:
    cfg = _read(SSOT)
    if not cfg:
        raise SystemExit(f"FAIL: missing SSOT {SSOT}")

    root = landing_root or GREEN
    if pages:
        targets = pages
    elif audit_all:
        targets = list(dict.fromkeys((cfg.get("depth_ship_pages") or []) + (cfg.get("depth_audit_pages") or [])))
    else:
        targets = list(cfg.get("depth_ship_pages") or [])

    page_html: dict[str, str] = {}
    all_findings: list[dict[str, Any]] = []
    for rel in sorted(targets):
        path = root / rel
        if not path.is_file():
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        page_html[rel] = html
        all_findings.extend(scan_page(rel, html, cfg=cfg))

    if len(page_html) >= 2:
        all_findings.extend(scan_cross_page(page_html, cfg=cfg))

    seen: set[tuple[str, str, int, str]] = set()
    unique: list[dict[str, Any]] = []
    for f in all_findings:
        key = (f.get("id", ""), f.get("page", ""), int(f.get("line") or 0), (f.get("excerpt") or "")[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)

    ok = len(unique) == 0
    row: dict[str, Any] = {
        "schema": "landing-copy-depth-gate-v1",
        "at": _now(),
        "verdict": "PASS" if ok else "BLOCK",
        "ok": ok,
        "publish_allowed": ok,
        "pages_scanned": len(page_html),
        "pages": sorted(page_html.keys()),
        "finding_count": len(unique),
        "findings": unique,
        "ssot": str(SSOT.relative_to(ROOT)),
        "landing_root": str(root),
        "factory_now_line": (
            f"landing-copy-depth · {'PASS' if ok else 'BLOCK'} · "
            f"{len(page_html)} pages · {len(unique)} findings"
        ),
        "next_action": (
            "Ship allowed — copy depth gate PASS"
            if ok
            else "CUT or tighten flagged lines logged (founder approves) — do not publish"
        ),
    }
    return _write_receipt(row)


def scan_text_fixture(text: str, *, rel_path: str = "growth.html") -> dict[str, Any]:
    cfg = _read(SSOT)
    findings = scan_page(rel_path, text, cfg=cfg)
    ok = len(findings) == 0
    return {
        "schema": "landing-copy-depth-gate-v1",
        "at": _now(),
        "verdict": "PASS" if ok else "BLOCK",
        "ok": ok,
        "publish_allowed": ok,
        "pages_scanned": 1,
        "finding_count": len(findings),
        "findings": findings,
        "fixture": rel_path,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Landing copy depth gate v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--landing-root", type=Path, default=None)
    ap.add_argument("--page", action="append", default=[], help="Scan specific page(s)")
    ap.add_argument("--audit-all", action="store_true", help="Ship bundle + audit pages + cross-page beats")
    ap.add_argument(
        "--fixture",
        choices=("bad-padded-growth",),
        help="Self-test fixture — BLOCK expected",
    )
    args = ap.parse_args()

    if args.fixture == "bad-padded-growth":
        bad = """
        <main>
          <section><p class="ar-section-copy">Every stage runs on the same spine — policy before action, receipt logged. That is what prospects remember — not another orchestration slide.</p></section>
          <section><p>15-minute screen-share — ALLOW, BLOCK, replay.</p><p>Book 15 minutes. Screen-share ALLOW, BLOCK, and replay.</p><p>Proof deck on every invite. Live ALLOW and BLOCK.</p></section>
          <section><p>Weekly proof export. Trust compounds into MRR.</p><p>SourceA flips the script — prospects watch governance.</p></section>
          <section class="sa-explore"><div class="sa-explore-grid"><a class="sa-explore-card">01</a></div></section>
          <section></section><section></section><section></section><section></section><section></section><section></section>
        </main>
        """
        row = scan_text_fixture(bad, rel_path="growth.html")
        row["fixture"] = "bad-padded-growth"
        row["factory_now_line"] = (
            f"landing-copy-depth · {row['verdict']} · fixture bad-padded-growth · {row['finding_count']} findings"
        )
        _write_receipt(row)
        if args.json:
            print(json.dumps(row, indent=2, ensure_ascii=False))
        else:
            print(row["factory_now_line"])
            for f in row.get("findings") or []:
                print(f"  BLOCK {f['page']}:{f.get('line')} [{f['id']}]")
                print(f"    → {f.get('suggestion', '')[:160]}")
        return 1 if not row.get("ok") else 0

    pages = args.page or None
    row = run_gate(landing_root=args.landing_root, pages=pages, audit_all=args.audit_all)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("factory_now_line", "landing-copy-depth done"))
        if not row.get("ok"):
            for f in row.get("findings") or []:
                print(f"  BLOCK {f['page']}:{f.get('line')} [{f['id']}]")
                print(f"    {f.get('excerpt', '')[:120]}")
                print(f"    → {f.get('suggestion', '')[:200]}")
        print(f"RECEIPT={RECEIPT}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
