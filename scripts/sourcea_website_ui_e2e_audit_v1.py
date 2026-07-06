#!/usr/bin/env python3
"""Strict live UI E2E audit — sourcea.app all pages + subpages.

Fetches public HTTPS only (not local dist). Writes JSON + Markdown report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "SourceA-landing" / "green-unified" / "dist"
REPORTS = ROOT / "reports"
GATE = ROOT / "data" / "sourcea-ui-mechanical-gate-v1.json"

FORBIDDEN_PATH_LEAKS = ("/Users/", "sinakazemnezhad", "Desktop/SourceA", "Desktop/agentrun")

STALE_PHRASES = (
    "powered by Forge",
    "Business Acquisition Systems — proof-backed engines",
    "verify on a call",
    "Book proof demo",
    "We show real work on a call",
    "15-minute demo script",
)

COMMERCIAL_HINTS = (
    "/sourcea/pricing",
    "/sourcea/offer",
    "/sourcea/start",
    "/sourcea/proof",
    "/",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_gate() -> dict[str, Any]:
    if not GATE.is_file():
        return {}
    try:
        return json.loads(GATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_forbidden_from_gate() -> list[str]:
    row = _load_gate()
    out: list[str] = []
    for item in row.get("forbidden_primary_phrases") or []:
        pat = str(item.get("pattern") or "").strip()
        if pat:
            out.append(pat)
    return out


def _load_regex_checks() -> list[dict[str, Any]]:
    return list(_load_gate().get("regex_checks") or [])


def _reclassify_finding_ids() -> dict[str, str]:
    out: dict[str, str] = {}
    for item in _load_gate().get("reclassify") or []:
        fid = str(item.get("finding_id") or "")
        sev = str(item.get("severity") or "FAIL")
        if not fid:
            continue
        for page in item.get("pages") or []:
            out[str(page)] = sev
    return out


def _body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _entity_from_body(body: str) -> str | None:
    m = re.search(r"Noetfield Systems Inc\.|{ENTITY}", body)
    return m.group(0) if m else None


def _discover_paths() -> list[str]:
    paths: set[str] = {"/"}

    redirects = DIST / "_redirects"
    if redirects.is_file():
        for line in redirects.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                src = parts[0].strip()
                if "*" in src:
                    continue
                if src and not src.startswith(":"):
                    paths.add(src if src.startswith("/") else f"/{src}")

    if DIST.is_dir():
        for html in DIST.rglob("*.html"):
            rel = html.relative_to(DIST).as_posix()
            if rel == "index.html":
                paths.add("/")
                continue
            if rel in ("eval.html", "platform.html"):
                paths.add(f"/{rel.replace('.html', '')}")
                paths.add(f"/{rel}")
            if rel.startswith("sourcea/"):
                clean = "/" + rel.replace(".html", "").replace("/index", "/")
                if clean.endswith("/index"):
                    clean = clean[: -len("index")]
                paths.add(clean)
                paths.add("/" + rel)
            elif rel.startswith(("unify/", "unify-demo/", "downloads/")):
                paths.add("/" + rel.replace(".html", ""))
                paths.add("/" + rel)

    # High-value short aliases
    for short in (
        "/eval",
        "/platform",
        "/start",
        "/pricing",
        "/proof",
        "/forge/terminal",
        "/operating-brain-install",
        "/ai-value-governance",
        "/enterprise-ai-control-plane",
    ):
        paths.add(short)

    return sorted(p for p in paths if "*" not in p)


def _fetch(url: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "sourcea-website-ui-e2e-audit/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    ctx = ssl.create_default_context()
    row: dict[str, Any] = {"url": url, "ok": False, "findings": []}
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            raw = resp.read()
            body = raw.decode("utf-8", errors="replace")
            row["status"] = int(resp.status)
            row["final_url"] = resp.geturl()
            row["content_type"] = resp.headers.get("Content-Type", "")
            row["bytes"] = len(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        row["status"] = int(exc.code)
        row["final_url"] = url
        row["content_type"] = exc.headers.get("Content-Type", "") if exc.headers else ""
        row["bytes"] = len(body.encode("utf-8")) if body else 0
        row["findings"].append({"id": "http_error", "severity": "FAIL", "detail": f"HTTP {exc.code}"})
    except Exception as exc:  # noqa: BLE001
        row["status"] = 0
        row["final_url"] = url
        row["error"] = str(exc)
        row["findings"].append({"id": "fetch_error", "severity": "FAIL", "detail": str(exc)})
        return row

    title_m = re.search(r"<title[^>]*>([^<]+)</title>", body, re.I)
    row["title"] = unescape(title_m.group(1).strip()) if title_m else ""
    row["body_sha256"] = _body_sha256(body)
    row["entity"] = _entity_from_body(body)

    if row.get("status") not in (200, 301, 302):
        row["findings"].append(
            {"id": "bad_status", "severity": "FAIL", "detail": f"status={row.get('status')}"}
        )

    if row.get("status") == 200 and row["bytes"] < 200:
        row["findings"].append({"id": "tiny_body", "severity": "FAIL", "detail": "body < 200 bytes"})

    if row.get("status") == 200 and "text/html" in str(row.get("content_type", "")):
        if not row["title"]:
            row["findings"].append({"id": "missing_title", "severity": "FAIL", "detail": "no <title>"})
        if "<html" not in body.lower():
            row["findings"].append({"id": "not_html", "severity": "FAIL", "detail": "missing <html>"})

    for needle in FORBIDDEN_PATH_LEAKS:
        if needle in body:
            row["findings"].append(
                {"id": "path_leak", "severity": "FAIL", "detail": f"contains {needle!r}"}
            )

    for phrase in STALE_PHRASES:
        if phrase.lower() in body.lower():
            row["findings"].append(
                {"id": "stale_phrase", "severity": "WARN", "detail": f"stale copy: {phrase!r}"}
            )

    for phrase in _load_forbidden_from_gate():
        if phrase.lower() in body.lower():
            row["findings"].append(
                {"id": "forbidden_primary", "severity": "FAIL", "detail": f"forbidden: {phrase!r}"}
            )

    for item in _load_regex_checks():
        pattern = str(item.get("regex") or "")
        if not pattern:
            continue
        rx = re.compile(pattern, re.I)
        if rx.search(body):
            row["findings"].append(
                {
                    "id": str(item.get("id") or "regex_check"),
                    "severity": str(item.get("severity") or "FAIL"),
                    "detail": str(item.get("suggestion") or item.get("why") or "regex check failed"),
                }
            )

    if row.get("status") == 200 and "text/html" in str(row.get("content_type", "")):
        path = urllib.parse.urlparse(url).path
        reclassify = _reclassify_finding_ids()
        contact_severity = "WARN"
        for page_key, sev in reclassify.items():
            if path == page_key or path.rstrip("/") == page_key.rstrip("/"):
                contact_severity = sev
                break
        if any(h in path for h in COMMERCIAL_HINTS) or path in ("/", "/sourcea/", "/sourcea"):
            if "hello@sourcea.app" not in body and "forge@sourcea.app" not in body:
                if "sourcea-chatbot.js" not in body and path not in ("/sourcea/forge/terminal",):
                    row["findings"].append(
                        {
                            "id": "no_contact_surface",
                            "severity": contact_severity,
                            "detail": "commercial page missing hello@/forge@ and chatbot",
                        }
                    )
        if row.get("entity") == "{ENTITY}":
            row["findings"].append(
                {"id": "entity_consistency", "severity": "FAIL", "detail": "unrendered {ENTITY} in body"}
            )

    row["ok"] = not any(f["severity"] == "FAIL" for f in row["findings"])
    return row


def _audit(*, base: str, workers: int) -> dict[str, Any]:
    paths = _discover_paths()
    urls = [base.rstrip("/") + (p if p.startswith("/") else f"/{p}") for p in paths if "*" not in p]
    results: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(_fetch, u): u for u in urls}
        for fut in as_completed(futs):
            results.append(fut.result())

    results.sort(key=lambda r: r["url"])
    home = next((r for r in results if urllib.parse.urlparse(r["url"]).path in ("/", "")), None)
    home_hash = home.get("body_sha256") if home else None
    if home_hash:
        for row in results:
            path = urllib.parse.urlparse(row["url"]).path
            if path in ("/", "") or row.get("status") != 200:
                continue
            if row.get("body_sha256") == home_hash:
                row["spa_fallback"] = True
                row["findings"].append(
                    {
                        "id": "spa_fallback_detect",
                        "severity": "REJECT_ROW",
                        "detail": "body sha256 matches homepage — SPA fallback",
                    }
                )
                rejected.append({"url": row["url"], "id": "spa_fallback_detect"})
                row["ok"] = not any(f["severity"] == "FAIL" for f in row["findings"])

    fail_pages = [r for r in results if not r.get("ok")]
    warn_pages = [r for r in results if r.get("ok") and any(f["severity"] == "WARN" for f in r.get("findings", []))]

    verdict = "PASS"
    if fail_pages:
        verdict = "FAIL"
    elif warn_pages:
        verdict = "PASS_WITH_WARNINGS"

    return {
        "schema": "sourcea-website-ui-e2e-audit-v1",
        "at": _now(),
        "base": base,
        "verdict": verdict,
        "summary": {
            "paths_discovered": len(paths),
            "pages_fetched": len(results),
            "pass": sum(1 for r in results if r.get("ok")),
            "fail": len(fail_pages),
            "warn_only": len(warn_pages),
            "rejected_rows": len(rejected),
        },
        "rejected_rows": rejected,
        "failures": [
            {
                "url": r["url"],
                "status": r.get("status"),
                "title": r.get("title"),
                "findings": r.get("findings"),
            }
            for r in fail_pages
        ],
        "warnings": [
            {
                "url": r["url"],
                "findings": [f for f in r.get("findings", []) if f["severity"] == "WARN"],
            }
            for r in warn_pages
        ],
        "results": results,
    }


def _markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# SourceA Website UI E2E Audit",
        "",
        f"**At:** {report['at']}  ",
        f"**Base:** {report['base']}  ",
        f"**Verdict:** `{report['verdict']}`  ",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Paths discovered | {s['paths_discovered']} |",
        f"| Pages fetched | {s['pages_fetched']} |",
        f"| PASS | {s['pass']} |",
        f"| FAIL | {s['fail']} |",
        f"| WARN only | {s['warn_only']} |",
        "",
    ]

    if report["failures"]:
        lines += ["## Failures (BLOCK)", ""]
        for f in report["failures"][:50]:
            lines.append(f"### {f['url']}")
            lines.append(f"- HTTP {f.get('status')} · `{f.get('title', '')[:80]}`")
            for finding in f.get("findings") or []:
                lines.append(f"- **{finding['severity']}** `{finding['id']}`: {finding['detail']}")
            lines.append("")

    if report["warnings"]:
        lines += ["## Warnings (review)", ""]
        for w in report["warnings"][:40]:
            lines.append(f"- **{w['url']}**")
            for finding in w.get("findings") or []:
                lines.append(f"  - `{finding['id']}`: {finding['detail']}")
        lines.append("")

    lines += [
        "## Checks applied",
        "",
        "- Live HTTPS fetch (public hostname only)",
        "- HTTP status + title + HTML shell",
        "- Path leaks (`/Users/`, local desktop paths)",
        "- Stale positioning (`powered by Forge`, call-first copy)",
        "- Mechanical gate forbidden primary phrases + v2 regex checks",
        "- Commercial contact/chatbot surface (FAIL on SKU landers per reclassify)",
        "- SPA fallback detect (homepage body hash match)",
        "- Splat URL guard (skip `*` paths)",
        "- Receipt hygiene (reports/ only; no path leaks in receipt body)",
        "",
        f"**Gate SSOT:** `data/sourcea-ui-mechanical-gate-v1.json`",
        f"**Machine:** `scripts/sourcea_website_ui_e2e_audit_v1.py`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Strict sourcea.app UI E2E audit")
    ap.add_argument("--base", default="https://sourcea.app")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = _audit(base=args.base.rstrip("/"), workers=args.workers)

    REPORTS.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS / "sourcea-website-ui-e2e-audit-v1.json"
    md_path = REPORTS / "sourcea-website-ui-e2e-audit-v1.md"

    json_text = json.dumps(report, indent=2) + "\n"
    for needle in FORBIDDEN_PATH_LEAKS:
        if needle in json_text:
            report["verdict"] = "FAIL"
            report.setdefault("receipt_hygiene", []).append(
                {"id": "receipt_hygiene", "severity": "FAIL", "detail": f"receipt contains {needle!r}"}
            )
            json_text = json.dumps(report, indent=2) + "\n"
            break

    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"{report['verdict']}: {report['summary']['pass']}/{report['summary']['pages_fetched']} pass "
            f"· report {json_path}"
        )
    return 0 if report["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
