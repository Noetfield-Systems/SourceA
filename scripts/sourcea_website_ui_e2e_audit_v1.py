#!/usr/bin/env python3
"""Strict live UI E2E audit v2 — sourcea.app (live-discovered paths).

Law: discover from live link BFS + sitemap; diff vs dist; no splat URLs;
SPA-fallback rows REJECTED from pass math; receipts under reports/ only.
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
from collections import deque
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

STALE_WARN = (
    "powered by Forge",
    "Business Acquisition Systems — proof-backed engines",
    "verify on a call",
    "We show real work on a call",
    "15-minute demo script",
)

STALE_FAIL = ("Book proof demo",)

BUYER_FUNNEL = (
    "/",
    "/start",
    "/pricing",
    "/sourcea/pricing",
    "/proof",
    "/sourcea/proof",
    "/offer",
    "/sourcea/offer",
    "/eval",
    "/forge/terminal",
    "/sourcea/forge/terminal",
    "/security",
    "/sourcea/security",
)

CONTACT_MARKERS = (
    "hello@sourcea.app",
    "forge@sourcea.app",
    "contract@sourcea.app",
    "contract@sourcea.ca",
    "contract@sourcea.uk",
)

SKU_PATHS = frozenset(
    {
        "/ai-value-governance",
        "/enterprise-ai-control-plane",
        "/operating-brain-install",
        "/sourcea/ai-value-governance",
        "/sourcea/enterprise-ai-control-plane",
        "/sourcea/operating-brain-install",
    }
)

HREF_RE = re.compile(r"""href\s*=\s*["']([^"'#]+)""")


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
    return [str(i.get("pattern") or "").strip() for i in row.get("forbidden_primary_phrases") or [] if i.get("pattern")]


def _load_regex_checks() -> list[dict[str, Any]]:
    return list(_load_gate().get("regex_checks") or [])


def _normalize_for_deploy_hash(body: str) -> str:
    """Strip edge-injected analytics so live vs dist compares deploy artifact only."""
    text = re.sub(
        r"<script[^>]*cloudflareinsights\.com/beacon\.min\.js[^>]*>.*?</script>",
        "",
        body,
        flags=re.I | re.S,
    )
    lines = [ln.rstrip() for ln in text.splitlines()]
    compact: list[str] = []
    prev_blank = False
    for ln in lines:
        blank = ln == ""
        if blank and prev_blank:
            continue
        compact.append(ln)
        prev_blank = blank
    text = "\n".join(compact).strip()
    text = re.sub(r"\n\s*\n(\s*</body>)", r"\n\1", text, flags=re.I)
    return text


def _body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _deploy_body_sha256(body: str) -> str:
    return _body_sha256(_normalize_for_deploy_hash(body))


def _dist_html_for_path(path: str) -> Path | None:
    """Map public path to shipped dist HTML file (deploy truth)."""
    path = _normalize_path(path)
    if path == "/":
        for cand in (DIST / "index.html", DIST / "sourcea" / "founder-home.html"):
            if cand.is_file():
                return cand
        return None
    if path.endswith(".html"):
        bare = path[: -len(".html")]
    else:
        bare = path
    candidates = [
        DIST / f"{bare.lstrip('/')}.html",
        DIST / bare.lstrip("/") / "index.html",
        DIST / f"sourcea{bare}.html" if bare.startswith("/sourcea") else None,
    ]
    if bare.startswith("/sourcea/"):
        rel = bare[len("/sourcea/") :]
        candidates.extend(
            [
                DIST / "sourcea" / f"{rel}.html",
                DIST / "sourcea" / rel / "index.html",
            ]
        )
    elif not bare.startswith("/sourcea"):
        candidates.append(DIST / "sourcea" / f"{bare.lstrip('/')}.html")
    for cand in candidates:
        if cand is not None and cand.is_file():
            return cand
    return None


def _fetch_with_headers(url: str) -> tuple[int, str, str, dict[str, str]]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "sourcea-website-ui-e2e-audit/2.0", "Cache-Control": "no-cache"},
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return int(resp.status), resp.geturl(), body, headers


def _fetch_raw(url: str) -> tuple[int, str, str]:
    status, final, body, _ = _fetch_with_headers(url)
    return status, final, body


def _normalize_path(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub(r"/+", "/", path)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path


def _extract_hrefs(base: str, body: str) -> set[str]:
    out: set[str] = set()
    base_p = urllib.parse.urlparse(base)
    for href in HREF_RE.findall(body):
        href = href.strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        full = urllib.parse.urljoin(base, href)
        p = urllib.parse.urlparse(full)
        if p.netloc and p.netloc not in (base_p.netloc, f"www.{base_p.netloc}", base_p.netloc.removeprefix("www.")):
            continue
        path = _normalize_path(p.path or "/")
        if "*" in path or not _is_page_path(path):
            continue
        out.add(path)
    return out


NON_PAGE_SUFFIXES = (".dmg", ".json", ".js", ".css", ".svg", ".webp", ".png", ".jpg", ".jpeg", ".mp4")


def _is_page_path(path: str) -> bool:
    return not any(path.lower().endswith(s) for s in NON_PAGE_SUFFIXES)


def _discover_live_bfs(base: str, *, max_pages: int = 120) -> set[str]:
    seen: set[str] = set()
    queue: deque[str] = deque(["/"])
    while queue and len(seen) < max_pages:
        path = queue.popleft()
        if path in seen or "*" in path:
            continue
        seen.add(path)
        url = base.rstrip("/") + path
        try:
            status, final, body = _fetch_raw(url)
        except Exception:  # noqa: BLE001
            continue
        if status != 200 or "text/html" not in body[:500].lower() and "<html" not in body.lower():
            continue
        for link in _extract_hrefs(final, body):
            if link not in seen and len(seen) + len(queue) < max_pages + 20:
                queue.append(link)
    for path in ("/sitemap.xml", "/robots.txt"):
        try:
            status, _, body = _fetch_raw(base.rstrip("/") + path)
            if status == 200 and path == "/sitemap.xml":
                for loc in re.findall(r"<loc>([^<]+)</loc>", body):
                    p = urllib.parse.urlparse(loc.strip())
                    if p.path and "*" not in p.path:
                        seen.add(_normalize_path(p.path))
        except Exception:  # noqa: BLE001
            pass
    return seen


def _discover_dist_paths() -> set[str]:
    paths: set[str] = {"/"}
    redirects = DIST / "_redirects"
    if redirects.is_file():
        for line in redirects.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 2:
                src = parts[0].strip()
                if src and "*" not in src:
                    paths.add(_normalize_path(src))
    if DIST.is_dir():
        for html in DIST.rglob("*.html"):
            rel = html.relative_to(DIST).as_posix()
            if rel == "index.html":
                paths.add("/")
            elif rel in ("eval.html", "platform.html"):
                paths.add(f"/{rel.replace('.html', '')}")
            elif rel.startswith("sourcea/"):
                clean = "/" + rel.replace(".html", "")
                if clean.endswith("/index"):
                    clean = clean[: -len("/index")] or "/sourcea/"
                paths.add(_normalize_path(clean))
            elif rel.startswith(("unify/", "unify-demo/", "downloads/")):
                paths.add(_normalize_path("/" + rel.replace(".html", "").replace("/index", "")))
    return {p for p in paths if "*" not in p}


def _dedupe_paths(paths: set[str]) -> list[str]:
    """Drop .html twins when extensionless path exists."""
    norm = {_normalize_path(p) for p in paths}
    drop: set[str] = set()
    for p in norm:
        if p.endswith(".html"):
            bare = p[: -len(".html")]
            if bare in norm or f"{bare}/" in norm:
                drop.add(p)
    return sorted(norm - drop)


def _has_contact(body: str) -> bool:
    return any(m in body for m in CONTACT_MARKERS) or "sourcea-chatbot.js" in body


def _visible_html(body: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.I | re.S)
    return re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.I | re.S)


def _audit_page(url: str, *, home_hash: str | None, dist_path: Path | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"url": url, "ok": False, "findings": []}
    try:
        status, final, body, headers = _fetch_with_headers(url)
        row["status"] = status
        row["final_url"] = final
        row["content_type"] = headers.get("content-type", "")
        row["cf_cache_status"] = headers.get("cf-cache-status", "")
        row["x_sourcea_pages_path"] = headers.get("x-sourcea-pages-path", "")
        row["bytes"] = len(body.encode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        row["status"] = int(exc.code)
        row["final_url"] = url
        row["content_type"] = exc.headers.get("Content-Type", "") if exc.headers else ""
        row["bytes"] = len(body.encode()) if body else 0
        row["findings"].append({"id": "http_error", "severity": "FAIL", "detail": f"HTTP {exc.code}"})
        return row
    except Exception as exc:  # noqa: BLE001
        row["status"] = 0
        row["error"] = str(exc)
        row["findings"].append({"id": "fetch_error", "severity": "FAIL", "detail": str(exc)})
        return row

    title_m = re.search(r"<title[^>]*>([^<]+)</title>", body, re.I)
    row["title"] = unescape(title_m.group(1).strip()) if title_m else ""
    row["body_sha256"] = _body_sha256(body)
    row["deploy_body_sha256"] = _deploy_body_sha256(body)
    if dist_path and dist_path.is_file():
        dist_body = dist_path.read_text(encoding="utf-8", errors="replace")
        row["dist_path"] = dist_path.relative_to(ROOT).as_posix()
        row["dist_sha256"] = _body_sha256(dist_body)
        row["dist_deploy_sha256"] = _deploy_body_sha256(dist_body)
        row["dist_live_match"] = row["dist_deploy_sha256"] == row["deploy_body_sha256"]
        if not row["dist_live_match"]:
            row["findings"].append(
                {
                    "id": "deploy_drift",
                    "severity": "FAIL",
                    "detail": f"live deploy hash != dist ({row['dist_path']})",
                }
            )
    visible = _visible_html(body)
    path = _normalize_path(urllib.parse.urlparse(url).path or "/")

    if row.get("status") not in (200, 301, 302):
        row["findings"].append({"id": "bad_status", "severity": "FAIL", "detail": f"status={row.get('status')}"})

    is_html = row.get("status") == 200 and (
        "text/html" in str(row.get("content_type", "")).lower() or "<html" in body.lower()[:2000]
    )

    if row.get("status") == 200 and row["bytes"] < 200 and is_html:
        row["findings"].append({"id": "tiny_body", "severity": "FAIL", "detail": "body < 200 bytes"})

    if is_html:
        if not row["title"]:
            row["findings"].append({"id": "missing_title", "severity": "FAIL", "detail": "no <title>"})

    if not is_html:
        row["ok"] = row.get("status") == 200
        row["skipped_non_html"] = True
        return row

    for needle in FORBIDDEN_PATH_LEAKS:
        if needle in visible:
            row["findings"].append({"id": "path_leak", "severity": "FAIL", "detail": f"contains {needle!r}"})

    for phrase in STALE_FAIL:
        if phrase.lower() in visible.lower():
            row["findings"].append({"id": "stale_phrase_fail", "severity": "FAIL", "detail": f"stale: {phrase!r}"})

    for phrase in STALE_WARN:
        if phrase.lower() in visible.lower():
            row["findings"].append({"id": "stale_phrase", "severity": "WARN", "detail": f"stale: {phrase!r}"})

    for phrase in _load_forbidden_from_gate():
        if phrase and phrase.lower() in visible.lower():
            row["findings"].append(
                {"id": "forbidden_primary", "severity": "FAIL", "detail": f"forbidden: {phrase!r}"}
            )

    for item in _load_regex_checks():
        pattern = str(item.get("regex") or "")
        if pattern and re.search(pattern, visible, re.I):
            row["findings"].append(
                {
                    "id": str(item.get("id") or "regex_check"),
                    "severity": str(item.get("severity") or "FAIL"),
                    "detail": str(item.get("suggestion") or "regex check failed"),
                }
            )

    if "{ENTITY}" in visible:
        row["findings"].append({"id": "entity_consistency", "severity": "FAIL", "detail": "unrendered {ENTITY}"})

    commercial = path in BUYER_FUNNEL or path in SKU_PATHS or path.startswith(
        ("/sourcea/pricing", "/sourcea/offer", "/sourcea/start", "/sourcea/proof")
    )
    if row.get("status") == 200 and commercial and not _has_contact(body):
        sev = "FAIL" if path in SKU_PATHS else "WARN"
        row["findings"].append({"id": "no_contact_surface", "severity": sev, "detail": "missing contact/chatbot"})

    if path in ("/", "") and row.get("status") == 200:
        if re.search(r"data-trust-receipts-lifetime[^>]*>—<", visible):
            row["findings"].append(
                {
                    "id": "trust_placeholder_ssr",
                    "severity": "WARN",
                    "detail": "SSR trust counters show em-dash — hydrated client-side from trust-signals.json",
                }
            )

    if home_hash and path not in ("/", "") and row.get("status") == 200:
        if row.get("body_sha256") == home_hash:
            row["spa_fallback"] = True
            row["findings"].append(
                {"id": "spa_fallback_detect", "severity": "REJECT_ROW", "detail": "homepage body hash match"}
            )

    row["ok"] = not any(f["severity"] == "FAIL" for f in row["findings"])
    row["rejected"] = any(f["severity"] == "REJECT_ROW" for f in row["findings"])
    return row


def _audit(*, base: str, workers: int) -> dict[str, Any]:
    live_paths = _discover_live_bfs(base)
    dist_paths = _discover_dist_paths()
    paths = _dedupe_paths(live_paths | dist_paths)
    paths = [p for p in paths if _is_page_path(p)]
    urls = [base.rstrip("/") + p for p in paths]

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_fetch_raw, base.rstrip("/") + "/") for _ in range(1)]
        try:
            _, _, home_body = futs[0].result()
            home_hash = _body_sha256(home_body)
        except Exception:  # noqa: BLE001
            home_hash = None

        futs = {
            pool.submit(
                _audit_page,
                u,
                home_hash=home_hash,
                dist_path=_dist_html_for_path(_normalize_path(urllib.parse.urlparse(u).path or "/")),
            ): u
            for u in urls
        }
        for fut in as_completed(futs):
            results.append(fut.result())

    results.sort(key=lambda r: r["url"])
    counted = [r for r in results if not r.get("rejected")]
    fail_pages = [r for r in counted if not r.get("ok")]
    warn_pages = [r for r in counted if r.get("ok") and any(f["severity"] == "WARN" for f in r.get("findings", []))]
    rejected = [r for r in results if r.get("rejected")]

    buyer_results = []
    for bf in BUYER_FUNNEL:
        url = base.rstrip("/") + bf
        match = next((r for r in results if r["url"] == url), None)
        if match:
            buyer_results.append(
                {
                    "path": bf,
                    "url": url,
                    "ok": match.get("ok"),
                    "rejected": match.get("rejected"),
                    "body_sha256": match.get("deploy_body_sha256"),
                    "dist_sha256": match.get("dist_deploy_sha256"),
                    "dist_live_match": match.get("dist_live_match"),
                    "cf_cache_status": match.get("cf_cache_status"),
                    "title": match.get("title"),
                    "findings": [f for f in match.get("findings", []) if f["severity"] in ("FAIL", "WARN")],
                }
            )

    buyer_fail = [b for b in buyer_results if not b.get("ok") and not b.get("rejected")]
    live_only = sorted(live_paths - dist_paths)
    dist_only = sorted(dist_paths - live_paths)

    verdict = "PASS"
    if fail_pages or buyer_fail:
        verdict = "FAIL"
    elif warn_pages:
        verdict = "PASS_WITH_WARNINGS"

    deploy_drift = [
        {
            "url": r["url"],
            "dist_path": r.get("dist_path"),
            "live_sha256": r.get("deploy_body_sha256"),
            "dist_sha256": r.get("dist_deploy_sha256"),
            "match": r.get("dist_live_match"),
        }
        for r in results
        if r.get("dist_path") and r.get("dist_live_match") is False
    ]

    return {
        "schema": "sourcea-website-ui-e2e-audit-v2",
        "at": _now(),
        "base": base,
        "verdict": verdict,
        "summary": {
            "paths_live_bfs": len(live_paths),
            "paths_dist": len(dist_paths),
            "paths_audited_unique": len(paths),
            "pages_fetched": len(results),
            "pages_counted": len(counted),
            "pass": sum(1 for r in counted if r.get("ok")),
            "fail": len(fail_pages),
            "warn_only": len(warn_pages),
            "rejected_spa_fallback": len(rejected),
            "buyer_funnel_fail": len(buyer_fail),
            "live_only_count": len(live_only),
            "dist_only_count": len(dist_only),
        },
        "buyer_funnel": buyer_results,
        "deploy_drift": deploy_drift,
        "count_math": {
            "unique_audited": len(paths),
            "rejected_spa_fallback": len(rejected),
            "counted_non_rejected": len(counted),
            "formula": "counted = unique_audited - rejected_spa_fallback",
        },
        "drift": {"live_only": live_only[:40], "dist_only": dist_only[:40]},
        "failures": [
            {"url": r["url"], "status": r.get("status"), "title": r.get("title"), "findings": r.get("findings")}
            for r in fail_pages
        ],
        "warnings": [
            {"url": r["url"], "findings": [f for f in r.get("findings", []) if f["severity"] == "WARN"]}
            for r in warn_pages
        ],
        "rejected_rows": [{"url": r["url"], "reason": "spa_fallback_detect"} for r in rejected],
        "results": results,
    }


def _markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# SourceA Website UI E2E Audit (v2)",
        "",
        f"**At:** {report['at']}  ",
        f"**Base:** {report['base']}  ",
        f"**Verdict:** `{report['verdict']}`  ",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Live BFS paths | {s['paths_live_bfs']} |",
        f"| Dist paths | {s['paths_dist']} |",
        f"| Unique audited | {s['paths_audited_unique']} |",
        f"| Counted (non-rejected) | {s['pages_counted']} |",
        f"| PASS | {s['pass']} |",
        f"| FAIL | {s['fail']} |",
        f"| Buyer funnel FAIL | {s['buyer_funnel_fail']} |",
        f"| SPA fallback rejected | {s['rejected_spa_fallback']} |",
        f"| Count math | {report.get('count_math', {}).get('formula', '')} |",
        "",
        "## Deploy drift (live sha256 vs dist)",
        "",
    ]
    drift = report.get("deploy_drift") or []
    if drift:
        for d in drift[:20]:
            lines.append(
                f"- `{d['url']}` dist=`{d.get('dist_path')}` live={d.get('live_sha256','')[:12]}… dist={d.get('dist_sha256','')[:12]}…"
            )
    else:
        lines.append("- **None** — all mapped dist files match live body sha256")
    lines += ["", "## Buyer funnel", ""]
    for b in report.get("buyer_funnel") or []:
        status = "PASS" if b.get("ok") else ("REJECT" if b.get("rejected") else "FAIL")
        hash_note = ""
        if b.get("body_sha256"):
            hash_note = f" · sha256 `{b['body_sha256'][:12]}…`"
            if b.get("dist_live_match") is True:
                hash_note += " · **dist match**"
            elif b.get("dist_live_match") is False:
                hash_note += " · **DIST DRIFT**"
        lines.append(f"- `{b['path']}` — **{status}**{hash_note}")
        for f in b.get("findings") or []:
            lines.append(f"  - {f['severity']} `{f['id']}`: {f['detail']}")
    lines.append("")
    if report.get("failures"):
        lines += ["## Failures", ""]
        for f in report["failures"][:30]:
            lines.append(f"### {f['url']}")
            for finding in f.get("findings") or []:
                if finding["severity"] == "FAIL":
                    lines.append(f"- `{finding['id']}`: {finding['detail']}")
            lines.append("")
    lines += [
        "## Checks",
        "",
        "- Live BFS + sitemap discovery (not splat URLs)",
        "- Dist vs live body sha256 (deploy drift FAIL)",
        "- Path leaks, {ENTITY}, forbidden phrases, regex v2",
        "- SPA fallback rejection",
        "- Buyer funnel explicit bucket",
        "- Contact: hello@ / forge@ / contract@sourcea.*",
        "",
        "`scripts/sourcea_website_ui_e2e_audit_v1.py` · gate `data/sourcea-ui-mechanical-gate-v1.json`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Strict sourcea.app UI E2E audit v2")
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
        s = report["summary"]
        print(
            f"{report['verdict']}: {s['pass']}/{s['pages_counted']} pass "
            f"(audited {s['paths_audited_unique']} unique · buyer_fail {s['buyer_funnel_fail']}) "
            f"· {json_path.relative_to(ROOT)}"
        )
    return 0 if report["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
