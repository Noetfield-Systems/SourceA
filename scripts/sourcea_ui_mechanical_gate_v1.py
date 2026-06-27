#!/usr/bin/env python3
"""SourceA UI mechanical gate v1 — BLOCK broken UI regressions before ship.

Grades Part A only (docs/SOURCEA_UI_STANDARD_RUBRIC_LOCKED_v1.md).
Does NOT grade desire, taste, or willingness to pay.

SSOT: data/sourcea-ui-mechanical-gate-v1.json
Receipt: ~/.sina/enforcement/sourcea-ui-mechanical-gate-receipt-v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "sourcea-ui-mechanical-gate-v1.json"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "enforcement" / "sourcea-ui-mechanical-gate-receipt-v1.json"
LOG_PATH = SINA / "e2e-logs" / "validate-sourcea-ui-mechanical-v1.log"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
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


def _line_hits(text: str, pattern: str, *, flags: int = re.I) -> list[dict[str, Any]]:
    rx = re.compile(pattern, flags)
    hits: list[dict[str, Any]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if rx.search(line):
            hits.append({"line": i, "excerpt": line.strip()[:240]})
    return hits


def _scan_positioning_ssot(cfg: dict[str, Any], landing: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    rel = str(cfg.get("positioning_ssot") or "")
    path = ROOT / rel if rel else landing / "data/sourcea-positioning-v1.json"
    row = _read_json(path)
    if row.get("schema") != "sourcea-positioning-v1":
        findings.append(
            {
                "id": "positioning_ssot",
                "page": rel or "data/sourcea-positioning-v1.json",
                "line": 1,
                "excerpt": f"schema={row.get('schema')!r}",
                "suggestion": "Missing or invalid sourcea-positioning-v1.json — lock one-liner first.",
            }
        )
    elif not (row.get("one_line") or "").strip():
        findings.append(
            {
                "id": "positioning_ssot",
                "page": rel,
                "line": 1,
                "excerpt": "one_line empty",
                "suggestion": "Set one_line in sourcea-positioning-v1.json.",
            }
        )
    return findings


def _scan_phrase_list(
    text: str,
    rel_path: str,
    items: list[dict[str, Any]],
    *,
    finding_id: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in items:
        pattern = str(item.get("pattern") or "")
        if not pattern:
            continue
        for hit in _line_hits(text, pattern):
            excerpt = hit.get("excerpt") or ""
            if finding_id == "poison" and "retired poison" in excerpt.lower():
                continue
            findings.append(
                {
                    "id": finding_id,
                    "rule_id": item.get("id"),
                    "page": rel_path,
                    **hit,
                    "suggestion": str(item.get("suggestion") or "Remove or replace forbidden copy."),
                }
            )
    return findings


def _scan_placeholders(text: str, rel_path: str, patterns: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for raw in patterns:
        for hit in _line_hits(text, raw, flags=0):
            findings.append(
                {
                    "id": "placeholder",
                    "page": rel_path,
                    **hit,
                    "suggestion": "Replace unreplaced placeholder or TODO before ship.",
                }
            )
    return findings


def _scan_json_file(path: Path, rel_path: str) -> list[dict[str, Any]]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return []
    except (OSError, json.JSONDecodeError) as exc:
        return [
            {
                "id": "json_parse",
                "page": rel_path,
                "line": 1,
                "excerpt": str(exc)[:200],
                "suggestion": "Fix JSON syntax before publish.",
            }
        ]


def _scan_chatbot(cfg: dict[str, Any], landing: Path) -> list[dict[str, Any]]:
    path = landing / "sourcea-chatbot.js"
    if not path.is_file():
        return [
            {
                "id": "missing_asset",
                "page": "sourcea-chatbot.js",
                "line": 1,
                "excerpt": "file missing",
                "suggestion": "sourcea-chatbot.js must exist logged.",
            }
        ]
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict[str, Any]] = []
    for item in cfg.get("chatbot_required") or []:
        target = landing / str(item.get("file") or "sourcea-chatbot.js")
        body = target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""
        if not re.search(str(item.get("pattern") or ""), body, re.I):
            findings.append(
                {
                    "id": "chatbot_required",
                    "rule_id": item.get("id"),
                    "page": str(target.relative_to(landing)),
                    "line": 1,
                    "excerpt": f"missing pattern: {item.get('pattern')}",
                    "suggestion": str(item.get("suggestion") or "Required chatbot invariant missing."),
                }
            )
    findings.extend(_scan_phrase_list(text, "sourcea-chatbot.js", cfg.get("chatbot_forbidden") or [], finding_id="chatbot_forbidden"))
    if 'offlineBanner.setAttribute("aria-hidden"' not in text:
        findings.append(
            {
                "id": "chatbot_a11y",
                "page": "sourcea-chatbot.js",
                "line": 1,
                "excerpt": "syncOfflineBanner aria-hidden missing",
                "suggestion": "Offline banner must set aria-hidden when hidden (a11y).",
            }
        )
    return findings


def _scan_css_invariants(cfg: dict[str, Any], landing: Path) -> list[dict[str, Any]]:
    path = landing / "sourcea.css"
    if not path.is_file():
        return [
            {
                "id": "missing_asset",
                "page": "sourcea.css",
                "line": 1,
                "excerpt": "file missing",
                "suggestion": "sourcea.css must exist logged.",
            }
        ]
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict[str, Any]] = []
    for item in cfg.get("css_brain_mobile_invariants") or []:
        pattern = str(item.get("pattern") or "")
        if not re.search(pattern, text, re.I):
            findings.append(
                {
                    "id": "css_invariant",
                    "rule_id": item.get("id"),
                    "page": "sourcea.css",
                    "line": 1,
                    "excerpt": f"missing invariant: {item.get('id')}",
                    "suggestion": str(item.get("suggestion") or "CSS brain mobile invariant missing."),
                }
            )
    return findings


def scan_landing(*, landing_root: Path | None = None, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = cfg or _read_json(SSOT)
    landing = landing_root or ROOT / str(cfg.get("landing_root") or "SourceA-landing/green-unified")
    findings: list[dict[str, Any]] = []
    scanned: list[str] = []

    findings.extend(_scan_positioning_ssot(cfg, landing))

    for rel in cfg.get("scan_pages") or []:
        path = landing / rel
        scanned.append(rel)
        if not path.is_file():
            findings.append(
                {
                    "id": "missing_page",
                    "page": rel,
                    "line": 1,
                    "excerpt": "file missing",
                    "suggestion": "Expected commercial page missing from landing root.",
                }
            )
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        findings.extend(_scan_phrase_list(text, rel, cfg.get("forbidden_primary_phrases") or [], finding_id="positioning"))
        findings.extend(_scan_phrase_list(text, rel, cfg.get("forbidden_poison") or [], finding_id="poison"))
        findings.extend(_scan_placeholders(text, rel, cfg.get("placeholder_patterns") or []))

    for rel in cfg.get("scan_assets") or []:
        path = landing / rel
        scanned.append(rel)
        if not path.is_file():
            findings.append(
                {
                    "id": "missing_asset",
                    "page": rel,
                    "line": 1,
                    "excerpt": "file missing",
                    "suggestion": "Required landing asset missing.",
                }
            )
            continue
        if path.suffix.lower() == ".json":
            findings.extend(_scan_json_file(path, rel))
        elif path.suffix.lower() == ".html":
            text = path.read_text(encoding="utf-8", errors="replace")
            findings.extend(_scan_placeholders(text, rel, cfg.get("placeholder_patterns") or []))

    findings.extend(_scan_chatbot(cfg, landing))
    findings.extend(_scan_css_invariants(cfg, landing))

    # Dist mirror — warn only if dist exists and contradicts (optional)
    dist = landing / "dist" / "sourcea"
    dist_chat = dist / "sourcea-chatbot.js"
    if dist_chat.is_file():
        src = (landing / "sourcea-chatbot.js").read_text(encoding="utf-8", errors="replace")
        dst = dist_chat.read_text(encoding="utf-8", errors="replace")
        if src != dst:
            findings.append(
                {
                    "id": "dist_stale",
                    "page": "dist/sourcea/sourcea-chatbot.js",
                    "line": 1,
                    "excerpt": "dist chatbot differs from green-unified source",
                    "suggestion": "Run python3 scripts/build_sourcea_vercel_output_v1.py before publish.",
                }
            )

    unique = {(f.get("id"), f.get("page"), f.get("line"), f.get("excerpt")): f for f in findings}
    findings = list(unique.values())
    ok = len(findings) == 0
    row = {
        "schema": "sourcea-ui-mechanical-gate-v1",
        "at": _now(),
        "verdict": "PASS" if ok else "BLOCK",
        "ok": ok,
        "publish_allowed": ok,
        "pages_scanned": len(scanned),
        "pages": scanned,
        "finding_count": len(findings),
        "findings": findings,
        "ssot": str(SSOT.relative_to(ROOT)),
        "landing_root": str(landing),
        "factory_now_line": (
            f"ui-mechanical · {'PASS' if ok else 'BLOCK'} · {len(scanned)} assets · {len(findings)} findings"
        ),
        "next_action": (
            "Ship allowed — UI mechanical gate PASS"
            if ok
            else "Fix mechanical UI findings in the repository — do not publish"
        ),
    }
    return _write_receipt(row)


def scan_fixture_bad_footer() -> dict[str, Any]:
    cfg = _read_json(SSOT)
    html = """
    <main><h1>Welcome</h1></main>
    <footer><p>SourceA helps teams ship AI work clients can verify.</p></footer>
    """
    findings = _scan_phrase_list(html, "fixture/bad-footer.html", cfg.get("forbidden_primary_phrases") or [], finding_id="positioning")
    ok = len(findings) > 0
    row = {
        "schema": "sourcea-ui-mechanical-gate-v1",
        "at": _now(),
        "verdict": "BLOCK" if ok else "PASS",
        "ok": not ok,
        "publish_allowed": not ok,
        "pages_scanned": 1,
        "finding_count": len(findings),
        "findings": findings,
        "fixture": "bad-positioning-footer",
        "factory_now_line": f"ui-mechanical · {'BLOCK' if ok else 'PASS'} · fixture bad-positioning-footer",
    }
    return _write_receipt(row)


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA UI mechanical gate v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--landing-root", type=Path, default=None)
    ap.add_argument("--fixture", choices=("bad-positioning-footer",), help="Self-test — BLOCK expected")
    args = ap.parse_args()

    if args.fixture == "bad-positioning-footer":
        row = scan_fixture_bad_footer()
        if args.json:
            print(json.dumps(row, indent=2, ensure_ascii=False))
        else:
            print(row["factory_now_line"])
        return 1 if not row.get("ok") else 0

    row = scan_landing(landing_root=args.landing_root)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("factory_now_line", "ui-mechanical done"))
        if not row.get("ok"):
            for f in row.get("findings") or []:
                print(f"  BLOCK {f.get('page')}:{f.get('line')} [{f.get('id')}]")
                print(f"    {f.get('excerpt', '')[:120]}")
                print(f"    → {f.get('suggestion', '')[:200]}")
        print(f"RECEIPT={RECEIPT}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
