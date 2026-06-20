#!/usr/bin/env python3
"""Thin cloud plan dispatch — Mac Hub proxies here on Railway; no FBE motor on Mac."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PLANS_PATH = ROOT / "data" / "secondary-cloud-drain-next-100-v1.json"
RECEIPTS_ROOT = ROOT / "receipts"
RECEIPTS_DIR = RECEIPTS_ROOT / "cloud-dispatch"
INDEX_PATH = RECEIPTS_ROOT / "index.json"
SUMMARY_PATH = RECEIPTS_ROOT / "summary.json"

WORKSTREAM_AREA: dict[str, str] = {
    "ws-ux": "ux",
    "ws-pricing": "pricing",
    "ws-run": "run",
    "ws-onboard": "onboard",
    "ws-integrate": "integrate",
}

TIER_SCORE: dict[str, int] = {"T0": 400, "T1": 300, "T2": 200, "T3": 100}
AREA_SCORE: dict[str, int] = {"run": 30, "pricing": 25, "onboard": 20, "integrate": 15, "ux": 10}

_URLS: dict[str, dict[str, str]] = {
    "Trigger.dev": {
        "ws-ux": "https://trigger.dev/docs/tasks/overview",
        "ws-pricing": "https://trigger.dev/pricing",
        "ws-run": "https://trigger.dev/docs/runs",
        "ws-onboard": "https://trigger.dev/docs/quick-start",
        "ws-integrate": "https://trigger.dev/docs/triggering",
    },
    "Inngest": {
        "ws-ux": "https://www.inngest.com",
        "ws-pricing": "https://www.inngest.com/pricing",
        "ws-run": "https://www.inngest.com/docs/platform/monitor/insights",
        "ws-onboard": "https://www.inngest.com/docs/getting-started/nextjs-quick-start",
        "ws-integrate": "https://www.inngest.com/docs/events",
    },
}

SNIPPET_BLOCKLIST = re.compile(
    r"(pricing\s+how\s+it\s+works|roadmap|uptime\s+status|terms\s+of\s+service|"
    r"github|linkedin|contact\s+sales|sign\s+up|documentation\s+examples\s+patterns|"
    r"contact\s+careers|privacy\s+terms|faqs\s+uptime)",
    re.I,
)

WORKSTREAM_KEYWORDS: dict[str, re.Pattern[str]] = {
    "ws-run": re.compile(r"\b(retry|retried|step|status|attempt|run|timeline|persisted)\b", re.I),
    "ws-onboard": re.compile(r"\b(quick\s+start|install|deploy|get\s+started|onboard|setup)\b", re.I),
    "ws-integrate": re.compile(r"\b(webhook|api|event|trigger|integrat)\b", re.I),
    "ws-pricing": re.compile(r"(\$\d|free\b|tier|credit|month)", re.I),
    "ws-ux": re.compile(r"\b(task|workflow|dashboard|overview|ui)\b", re.I),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def load_plan(plan_id: str) -> dict[str, Any] | None:
    doc = _read_json(PLANS_PATH)
    pid = str(plan_id or "").strip()
    for row in doc.get("plans") or []:
        if str(row.get("id") or "") == pid:
            return row
    if pid.startswith("W-CLOUD-"):
        for row in doc.get("plans") or []:
            if str(row.get("bind") or "") == pid:
                return row
    return None


def list_cloud_plans(*, start: int = 1, end: int = 90) -> list[dict[str, Any]]:
    doc = _read_json(PLANS_PATH)
    out: list[dict[str, Any]] = []
    for row in doc.get("plans") or []:
        pid = str(row.get("id") or "")
        if not pid.startswith("CLOUD-SEC-"):
            continue
        try:
            n = int(pid.split("-")[-1])
        except ValueError:
            continue
        if start <= n <= end:
            out.append(row)
    out.sort(key=lambda r: int(str(r.get("id", "")).split("-")[-1]))
    return out


def _fetch_url(url: str, *, timeout_s: int = 30) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": "SourceA-CloudWorker/1.0"})
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            body = resp.read(500_000).decode("utf-8", errors="replace")
            return {"status": resp.status, "url": url, "body": body, "bytes": len(body.encode("utf-8"))}
    except Exception as exc:
        status = getattr(exc, "code", 0) or 0
        return {"status": status, "url": url, "body": "", "bytes": 0, "error": str(exc)[:200]}


def _html_visible_text(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_title_h1(html: str) -> list[str]:
    out: list[str] = []
    title_m = re.search(r"<title[^>]*>([^<]+)</title>", html, flags=re.I | re.S)
    if title_m:
        title = re.sub(r"\s+", " ", title_m.group(1)).strip()
        title = re.sub(r"\s*-\s*Trigger\.dev\s*$", "", title, flags=re.I).strip()
        title = re.sub(r"\s*-\s*Inngest\s*(Documentation)?\s*$", "", title, flags=re.I).strip()
        if title:
            out.append(title[:220])
    og_m = re.search(r'property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', html, flags=re.I)
    if og_m:
        og = re.sub(r"\s+", " ", og_m.group(1)).strip()
        og = re.sub(r"\s*-\s*Trigger\.dev\s*$", "", og, flags=re.I).strip()
        og = re.sub(r"\s*-\s*Inngest\s*(Documentation)?\s*$", "", og, flags=re.I).strip()
        if og and og not in out:
            out.append(og[:220])
    h1_m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, flags=re.I | re.S)
    if h1_m:
        h1 = re.sub(r"\s+", " ", h1_m.group(1)).strip()
        if h1 and h1 not in out:
            out.append(h1[:220])
    return out


_SIDEBAR_MARKERS = (
    "Dashboard Run tests",
    "React hooks Backend CLI",
    "Introduction Commands",
    "Run tests Alerts",
    "Troubleshooting Common problems",
    "Observabilit",
)


def _is_code_junk_snippet(text: str) -> bool:
    t = str(text or "")
    return bool(re.search(r"(_jsx|CodeGroup|CodeBlock|&quot;|\\n\s*\}\))", t))


def _is_boilerplate_snippet(text: str, *, primary: bool = False) -> bool:
    t = str(text or "").strip()
    if not t:
        return True
    if not primary and len(t) < 8:
        return True
    if SNIPPET_BLOCKLIST.search(t):
        return True
    if _is_code_junk_snippet(t):
        return True
    if any(m in t for m in _SIDEBAR_MARKERS):
        return True
    nav_hits = sum(1 for w in ("Pricing", "Roadmap", "Careers", "Contact", "FAQs", "Uptime") if w.lower() in t.lower())
    return nav_hits >= 3


def _snippet_quality_score(text: str, *, workstream: str, primary: bool = False) -> int:
    t = str(text or "").strip()
    if not t or _is_boilerplate_snippet(t, primary=primary):
        return -100
    score = 100 if primary else 0
    score += min(len(t) // 8, 25)
    kw = WORKSTREAM_KEYWORDS.get(workstream)
    if kw and kw.search(t):
        score += 40
    if re.search(r"\$\d", t):
        score += 15
    return score


def _extract_snippets(html: str, *, workstream: str) -> list[str]:
    primary = _extract_title_h1(html)
    primary_set = set(primary)
    candidates: list[str] = []
    candidates.extend(primary)
    text = _html_visible_text(html)
    patterns = [r"\$\d[\d,]*(?:\.\d{2})?(?:\s*/\s*\w+)?", r"\bfree\b[^.]{0,80}", r"\bpricing\b[^.]{0,120}"]
    if workstream == "ws-run":
        patterns.extend([r"\brun\b[^.]{0,80}", r"\bretry\b[^.]{0,80}", r"\bstep\b[^.]{0,80}", r"\bpersisted\b[^.]{0,80}"])
    elif workstream == "ws-onboard":
        patterns.extend([r"\bget started\b[^.]{0,80}", r"\bonboard\b[^.]{0,80}", r"\bquick\s+start\b[^.]{0,80}", r"\binstall\b[^.]{0,80}"])
    elif workstream == "ws-integrate":
        patterns.extend([r"\bapi\b[^.]{0,80}", r"\bwebhook\b[^.]{0,80}", r"\bintegrat\b[^.]{0,80}", r"\bevent\b[^.]{0,80}"])
    else:
        patterns.extend([r"\bdashboard\b[^.]{0,80}", r"\bworkflow\b[^.]{0,80}", r"\btask\b[^.]{0,80}"])
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.I):
            snippet = m.group(0).strip()
            if snippet and snippet not in candidates:
                candidates.append(snippet[:160])
    filtered = [
        s
        for s in candidates
        if not _is_boilerplate_snippet(s, primary=s in primary_set)
    ]
    ranked = sorted(
        filtered,
        key=lambda s: _snippet_quality_score(s, workstream=workstream, primary=s in primary_set),
        reverse=True,
    )
    hits = ranked[:10]
    if not hits and text:
        fallback = text[:200]
        if not _is_boilerplate_snippet(fallback):
            hits.append(fallback)
        elif primary:
            hits.extend(primary[:2])
        elif candidates:
            hits.append(candidates[0][:200])
    return hits


def _source_url(plan: dict[str, Any]) -> str:
     = str(plan.get("") or "")
    workstream = str(plan.get("workstream") or "ws-ux")
    urls = _URLS.get() or {}
    return urls.get(workstream) or urls.get("ws-ux") or "https://trigger.dev"


def _update_index(entry: dict[str, Any]) -> dict[str, Any]:
    doc = _read_json(INDEX_PATH)
    if doc.get("schema") != "cloud-dispatch-index-v1":
        doc = {"schema": "cloud-dispatch-index-v1", "receipts": []}
    receipts = [r for r in doc.get("receipts") or [] if r.get("plan_id") != entry.get("plan_id")]
    receipts.append(entry)
    receipts.sort(key=lambda r: str(r.get("plan_id") or ""))
    passed = sum(1 for r in receipts if r.get("status") == "PASS")
    failed = sum(1 for r in receipts if r.get("status") == "FAIL")
    doc["updated_at"] = _now()
    doc["receipts"] = receipts
    doc["summary"] = {"pass": passed, "fail": failed, "total": len(receipts)}
    _write_json(INDEX_PATH, doc)
    return doc


def _run_cloud_plan(plan: dict[str, Any]) -> dict[str, Any]:
    url = _source_url(plan)
    fetched = _fetch_url(url)
    snippets = _extract_snippets(fetched.get("body") or "", workstream=str(plan.get("workstream") or ""))
    receipt_id = f"cloud-dispatch-{uuid.uuid4().hex[:12]}"
    ok = fetched.get("status") == 200 and bool(snippets) and int(fetched.get("bytes") or 0) > 500
    receipt = {
        "schema": "cloud-dispatch-receipt-v1",
        "receipt_id": receipt_id,
        "plan_id": plan.get("id"),
        "maps_registry": plan.get("maps_registry"),
        "": plan.get(""),
        "workstream": plan.get("workstream"),
        "tier": plan.get("tier"),
        "cloud_action": plan.get("cloud_action"),
        "at": _now(),
        "execution_plane": "cloud_forge",
        "source_url": url,
        "http_status": fetched.get("status"),
        "bytes_fetched": fetched.get("bytes"),
        "evidence_snippets": snippets,
        "ok": ok,
        "status": "PASS" if ok else "FAIL",
    }
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPTS_DIR / f"{receipt_id}.json"
    receipt_url = f"/receipts/cloud-dispatch/{receipt_id}.json"
    receipt["receipt_path"] = str(receipt_path)
    receipt["receipt_url"] = receipt_url
    _write_json(receipt_path, receipt)
    _update_index(
        {
            "plan_id": plan.get("id"),
            "": plan.get(""),
            "workstream": plan.get("workstream"),
            "status": receipt["status"],
            "receipt_url": receipt_url,
            "receipt_id": receipt_id,
            "at": receipt["at"],
        }
    )
    show = (
        f"{plan.get('id')} · {plan.get('')} · {plan.get('workstream')} — "
        f"{receipt['status']} · {len(snippets)} snippets · {receipt_id}"
    )
    receipt["for_founder"] = {"show_this": show, "receipt_url": receipt_url}
    return receipt


def dispatch(*, plan_id: str, dry_run: bool = False) -> dict[str, Any]:
    plan = load_plan(plan_id)
    if not plan:
        return {"ok": False, "error": "plan_not_found", "plan_id": plan_id}
    plane = str(plan.get("plane") or "")
    if plane == "mac_control":
        return {
            "ok": True,
            "schema": "cloud-worker-dispatch-v1",
            "plan_id": plan_id,
            "plane": plane,
            "mac_executes_plan_body": False,
            "for_founder": {
                "show_this": f"{plan_id} is Mac control only — glance + confirm, no factory body on Mac.",
                "title": plan.get("title"),
            },
        }
    if dry_run:
        return {
            "ok": True,
            "schema": "cloud-worker-dispatch-v1",
            "plan_id": plan_id,
            "plane": plane,
            "dry_run": True,
            "cloud_action": plan.get("cloud_action"),
            "for_founder": {"show_this": f"DRY-RUN · would cloud-run {plan_id}: {plan.get('cloud_action')}"},
        }
    row = _run_cloud_plan(plan)
    row["schema"] = "cloud-worker-dispatch-v1"
    return row


def dispatch_batch(*, start: int = 1, end: int = 90) -> dict[str, Any]:
    plans = list_cloud_plans(start=start, end=end)
    results: list[dict[str, Any]] = []
    passed = 0
    failed = 0
    for plan in plans:
        pid = str(plan.get("id") or "")
        try:
            row = _run_cloud_plan(plan)
            ok = bool(row.get("ok"))
        except Exception as exc:
            row = {"plan_id": pid, "ok": False, "status": "FAIL", "error": str(exc)[:200]}
            ok = False
        if ok:
            passed += 1
        else:
            failed += 1
        results.append(
            {
                "plan_id": pid,
                "status": row.get("status") or ("PASS" if ok else "FAIL"),
                "receipt_url": row.get("receipt_url"),
                "ok": ok,
            }
        )
    index = _read_json(INDEX_PATH)
    return {
        "ok": failed == 0,
        "schema": "cloud-worker-dispatch-batch-v1",
        "at": _now(),
        "start": start,
        "end": end,
        "total": len(plans),
        "passed": passed,
        "failed": failed,
        "index_url": "/receipts/index.json",
        "results": results,
        "summary": index.get("summary") or {"pass": passed, "fail": failed, "total": len(plans)},
    }


def _area(workstream: str) -> str:
    return WORKSTREAM_AREA.get(workstream, workstream.replace("ws-", ""))


def _best_snippet(receipt: dict[str, Any]) -> str:
    snippets = receipt.get("evidence_snippets") or receipt.get("pricing_snippets") or []
    workstream = str(receipt.get("workstream") or "")
    if not snippets:
        return ""
    ranked = sorted(
        (str(s).strip() for s in snippets if str(s).strip()),
        key=lambda s: _snippet_quality_score(s, workstream=workstream),
        reverse=True,
    )
    for s in ranked:
        if not _is_boilerplate_snippet(s):
            return s[:220]
    return ranked[0][:220] if ranked else ""


def _gap_score(receipt: dict[str, Any]) -> int:
    tier = str(receipt.get("tier") or "T3")
    area = _area(str(receipt.get("workstream") or ""))
    workstream = str(receipt.get("workstream") or "")
    snippet = _best_snippet(receipt)
    quality = _snippet_quality_score(snippet, workstream=workstream)
    base = TIER_SCORE.get(tier, 50) + AREA_SCORE.get(area, 0)
    if quality < 0:
        return base - 50
    return base + quality


def _gap_line(receipt: dict[str, Any]) -> str:
     = str(receipt.get("") or "")
    area = _area(str(receipt.get("workstream") or ""))
    action = str(receipt.get("cloud_action") or "")
    snippet = _best_snippet(receipt)
    if snippet:
        return f"{} {area}: {action} —  evidence: {snippet}"
    return f"{} {area}: {action}"


def build_summary() -> dict[str, Any]:
    index = _read_json(INDEX_PATH)
    entries = index.get("receipts") or []
    receipts: list[dict[str, Any]] = []
    for entry in entries:
        rel = str(entry.get("receipt_url") or "").lstrip("/")
        if rel.startswith("receipts/"):
            rel = rel[len("receipts/") :]
        path = RECEIPTS_ROOT / rel
        row = _read_json(path)
        if row:
            receipts.append(row)

    findings: dict[str, dict[str, Any]] = {
        "Trigger.dev": {a: {"plans": [], "evidence": [], "actions": []} for a in WORKSTREAM_AREA.values()},
        "Inngest": {a: {"plans": [], "evidence": [], "actions": []} for a in WORKSTREAM_AREA.values()},
    }
    gap_candidates: list[dict[str, Any]] = []

    for receipt in receipts:
        if receipt.get("status") != "PASS" and not receipt.get("ok"):
            continue
         = str(receipt.get("") or "")
        if  not in findings:
            findings[] = {a: {"plans": [], "evidence": [], "actions": []} for a in WORKSTREAM_AREA.values()}
        area = _area(str(receipt.get("workstream") or ""))
        bucket = findings[].setdefault(area, {"plans": [], "evidence": [], "actions": []})
        pid = str(receipt.get("plan_id") or "")
        bucket["plans"].append(pid)
        action = str(receipt.get("cloud_action") or "")
        if action and action not in bucket["actions"]:
            bucket["actions"].append(action)
        for snip in (receipt.get("evidence_snippets") or receipt.get("pricing_snippets") or [])[:5]:
            text = str(snip).strip()
            if text and text not in bucket["evidence"] and not _is_boilerplate_snippet(text):
                bucket["evidence"].append(text[:180])
        gap_candidates.append(
            {
                "score": _gap_score(receipt),
                "gap": _gap_line(receipt),
                "plan_id": pid,
                "receipt_id": receipt.get("receipt_id"),
                "receipt_url": receipt.get("receipt_url"),
                "": ,
                "area": area,
                "workstream": receipt.get("workstream"),
                "tier": receipt.get("tier"),
                "source_url": receipt.get("source_url"),
            }
        )

    gap_candidates.sort(key=lambda g: g["score"], reverse=True)
    top_gaps: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cand in gap_candidates:
        key = f"{cand.get('')}:{cand.get('area')}:{cand.get('gap')[:80]}"
        if key in seen:
            continue
        seen.add(key)
        top_gaps.append(cand)
        if len(top_gaps) >= 10:
            break
    for i, row in enumerate(top_gaps, start=1):
        row["rank"] = i

    summary = {
        "schema": "cloud-dispatch-summary-v1",
        "at": _now(),
        "receipts_read": len(receipts),
        "index_url": "/receipts/index.json",
        "summary_url": "/receipts/summary.json",
        "findings_by_": findings,
        "top_10_gaps": [
            {
                "rank": g["rank"],
                "gap": g["gap"],
                "plan_id": g["plan_id"],
                "receipt_url": g["receipt_url"],
                "": g[""],
                "area": g["area"],
            }
            for g in top_gaps
        ],
        "ok": len(receipts) >= 90 and len(top_gaps) == 10,
    }
    _write_json(SUMMARY_PATH, summary)
    return summary


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--build-summary", action="store_true")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=90)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.batch:
        row = dispatch_batch(start=args.start, end=args.end)
    elif args.build_summary:
        row = build_summary()
    else:
        row = dispatch(plan_id=args.plan_id, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print((row.get("for_founder") or {}).get("show_this") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
