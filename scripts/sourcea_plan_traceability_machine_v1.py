#!/usr/bin/env python3
"""SourceA plan traceability machine.

Builds an evidence-backed plan matrix from disk SSOTs, local git scope, receipts,
and optional live website probes. Chat memory is never an input.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-plan-traceability-machine-receipt-v1.json"
REPORT = SINA / "sourcea-plan-traceability-report-v1.md"
SOURCEA_SITE = "https://sourcea.app/"

PLAN_JSON_SOURCES = [
    {
        "source_id": "program_progress_parallel",
        "path": "PROGRAM_PROGRESS.json",
        "item_key": "parallel_plans",
        "id_field": "id",
        "title_field": "title",
        "argument_fields": ["phase", "next_action", "hook"],
    },
    {
        "source_id": "program_progress_todos",
        "path": "PROGRAM_PROGRESS.json",
        "item_key": "todos",
        "id_field": "id",
        "title_field": "text",
        "argument_fields": ["plan_id", "owner", "hook", "evidence"],
    },
    {
        "source_id": "full_stack_100",
        "path": "data/sourcea-full-stack-100-fix-plan-v1.json",
        "item_key": "fixes",
        "id_field": "id",
        "title_field": "title",
        "argument_fields": ["lane", "tier", "why", "verify", "evidence"],
    },
    {
        "source_id": "outbound_100",
        "path": "data/outbound-factory-100-upgrade-plan-v1.json",
        "item_key": "upgrades",
        "id_field": "id",
        "title_field": "title",
        "argument_fields": ["lane", "tier", "why", "verify", "evidence"],
    },
    {
        "source_id": "brain_cloud_1000",
        "path": "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json",
        "item_key": "upgrades",
        "id_field": "id",
        "title_field": "title",
        "argument_fields": ["lane", "tier", "why", "verify", "evidence"],
    },
    {
        "source_id": "ecosystem_m111",
        "path": "data/ecosystem-mac-health-111-upgrade-plan-v1.json",
        "item_key": "upgrades",
        "id_field": "id",
        "title_field": "title",
        "argument_fields": ["lane", "tier", "why", "verify", "evidence"],
    },
]

REGISTRY_SOURCES = [
    "brain-os/plan-registry/sourcea-1000/REGISTRY.json",
    "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
    "brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json",
    "brain-os/plan-registry/sourcea-upgrade-path-7500/REGISTRY.json",
]

LIVE_MARKERS = (
    "SourceA",
    "Execution Proof",
    "RunReceipt",
    "hello@sourcea.app",
    "sourcea.app",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(v) for v in value if _text(v))
    if isinstance(value, dict):
        return "; ".join(f"{k}={_text(v)}" for k, v in value.items() if _text(v))
    return str(value)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _git(args: list[str]) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL, text=True, timeout=8)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def git_scope() -> dict[str, Any]:
    porcelain = _git(["status", "--porcelain"])
    diff_names = _git(["diff", "--name-only"])
    staged_names = _git(["diff", "--cached", "--name-only"])
    shortstat = _git(["diff", "--shortstat"])
    changed = []
    for line in porcelain.splitlines():
        if not line:
            continue
        changed.append({"status": line[:2].strip(), "path": line[3:].strip()})
    return {
        "dirty": bool(changed),
        "changed_count": len(changed),
        "changed_files": changed[:200],
        "unstaged_diff_files": [x for x in diff_names.splitlines() if x],
        "staged_diff_files": [x for x in staged_names.splitlines() if x],
        "shortstat": shortstat,
    }


def receipt_index() -> dict[str, str]:
    out: dict[str, str] = {}
    rec_dir = ROOT / "receipts"
    if rec_dir.is_dir():
        for path in rec_dir.glob("sa-*-receipt.json"):
            out[path.stem.replace("-receipt", "")] = _rel(path)
    for path in SINA.glob("*receipt*.json"):
        out[path.stem] = str(path)
    return out


def _argument(row: dict[str, Any], fields: list[str]) -> str:
    parts = []
    for field in fields:
        val = _text(row.get(field))
        if val:
            parts.append(f"{field}: {val}")
    return " | ".join(parts)[:500]


def _row_from_item(source: dict[str, Any], item: dict[str, Any], source_path: str) -> dict[str, Any]:
    plan_id = _text(item.get(source.get("id_field", "id")) or item.get("plan_id") or item.get("id")).strip()
    title = _text(item.get(source.get("title_field", "title")) or item.get("title") or item.get("text")).strip()
    status = _text(item.get("status") or "unknown").strip() or "unknown"
    evidence = _text(item.get("evidence") or item.get("receipt") or item.get("completed_at") or "")
    return {
        "plan_id": plan_id,
        "title": title,
        "status": status,
        "tier": _text(item.get("tier") or item.get("priority")),
        "lane": _text(item.get("lane") or item.get("thread") or item.get("plan_id")),
        "argument": _argument(item, source.get("argument_fields", [])),
        "source": source["source_id"],
        "source_path": source_path,
        "prompt_path": _text(item.get("prompt_path")),
        "verify": _text(item.get("verify")),
        "evidence": evidence,
    }


def collect_json_plan_rows(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in PLAN_JSON_SOURCES:
        path = ROOT / source["path"]
        data = _read_json(path)
        items = data.get(source["item_key"])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                rows.append(_row_from_item(source, item, source["path"]))
            if len(rows) >= limit:
                return rows
    return rows


def collect_registry_rows(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in REGISTRY_SOURCES:
        data = _read_json(ROOT / rel)
        plans = data.get("plans")
        if not isinstance(plans, list):
            continue
        for item in plans:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "plan_id": _text(item.get("id") or item.get("plan_id")),
                    "title": _text(item.get("title")),
                    "status": _text(item.get("status") or "unknown"),
                    "tier": _text(item.get("tier")),
                    "lane": _text(item.get("lane")),
                    "argument": _argument(item, ["agent_prompt", "verify", "phase", "workstream"]),
                    "source": _text(data.get("library") or Path(rel).parent.name),
                    "source_path": rel,
                    "prompt_path": _text(item.get("prompt_path")),
                    "verify": _text(item.get("verify")),
                    "evidence": _text(item.get("evidence") or item.get("receipt")),
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def live_probe(enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {"enabled": False, "ok": False, "skipped": True}
    try:
        req = urllib.request.Request(SOURCEA_SITE, headers={"User-Agent": "SourceA-TraceabilityMachine/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read(250_000).decode("utf-8", errors="replace")
            found = [m for m in LIVE_MARKERS if m.lower() in raw.lower()]
            title_match = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
            footer_match = re.search(r"<footer[^>]*>(.*?)</footer>", raw, re.I | re.S)
            footer = re.sub(r"\s+", " ", footer_match.group(1)).strip()[:300] if footer_match else ""
            return {
                "enabled": True,
                "ok": 200 <= resp.status < 300 and bool(found),
                "status": resp.status,
                "url": SOURCEA_SITE,
                "markers_found": found,
                "title": re.sub(r"\s+", " ", title_match.group(1)).strip()[:160] if title_match else "",
                "footer_excerpt": footer,
            }
    except urllib.error.HTTPError as exc:
        return {"enabled": True, "ok": False, "status": exc.code, "url": SOURCEA_SITE, "error": str(exc)[:180]}
    except Exception as exc:
        return {"enabled": True, "ok": False, "status": 0, "url": SOURCEA_SITE, "error": str(exc)[:180]}


def classify_row(row: dict[str, Any], *, receipts: dict[str, str], git: dict[str, Any], live: dict[str, Any]) -> dict[str, Any]:
    plan_id = row.get("plan_id") or ""
    status = str(row.get("status") or "unknown").lower()
    evidence = str(row.get("evidence") or "")
    receipt_path = receipts.get(plan_id, "")
    source_path = str(row.get("source_path") or "")
    changed_paths = [x.get("path", "") for x in git.get("changed_files", []) if isinstance(x, dict)]
    local_hits = [p for p in changed_paths if p == source_path or plan_id and plan_id in p]
    is_done = status in {"done", "complete", "completed", "shipped"}
    is_live_related = live.get("ok") and any(
        token
        for token in (plan_id, row.get("title", ""), row.get("lane", ""))
        if token and str(token).lower() in json.dumps(live).lower()
    )
    has_proof = bool(receipt_path or evidence)
    trace_state = "proven_done" if is_done and has_proof else ("planned" if not is_done else "done_unproven")
    follow_up_reason = ""
    if trace_state == "done_unproven":
        follow_up_reason = "status is done but no receipt/evidence was found logged"
    elif trace_state == "planned":
        follow_up_reason = row.get("verify") or row.get("argument") or "status is not closed"

    row["what_changed_locally"] = ", ".join(local_hits) if local_hits else "no local diff tied to this row"
    row["live_on_website"] = "matched live probe" if is_live_related else ("site reachable; no row-specific marker" if live.get("ok") else "not proven live")
    row["receipt_path"] = receipt_path or evidence
    row["remaining_planned"] = "none found" if trace_state == "proven_done" else follow_up_reason
    row["trace_state"] = trace_state
    row["needs_follow_up"] = trace_state != "proven_done"
    row["follow_up_reason"] = follow_up_reason
    row["evidence_quality"] = {
        "has_receipt_file": bool(receipt_path),
        "has_inline_evidence": bool(evidence),
        "has_local_diff_match": bool(local_hits),
        "has_live_match": bool(is_live_related),
    }
    return row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "total": len(rows),
        "proven_done": 0,
        "done_unproven": 0,
        "planned": 0,
        "rows_needing_follow_up": 0,
        "threads_needing_follow_up": 0,
        "follow_up_threads": [],
    }
    follow_up_threads: set[str] = set()
    for row in rows:
        state = row.get("trace_state")
        if state in out:
            out[state] += 1
        if row.get("needs_follow_up"):
            out["rows_needing_follow_up"] += 1
            thread = str(row.get("lane") or row.get("source") or "unknown").strip() or "unknown"
            follow_up_threads.add(thread)
    out["follow_up_threads"] = sorted(follow_up_threads)
    out["threads_needing_follow_up"] = len(follow_up_threads)
    return out


def build_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# SourceA Plan Traceability Report v1",
        "",
        f"Generated: {receipt['at']}",
        "",
        "## Evidence Sources",
        "",
        f"- Local git dirty: {receipt['git_scope']['dirty']} ({receipt['git_scope']['changed_count']} paths)",
        f"- Live website: {receipt['live_probe'].get('url', SOURCEA_SITE)} ok={receipt['live_probe'].get('ok')}",
        f"- Receipts indexed: {receipt['receipt_count']}",
        "",
        "## Summary",
        "",
        f"- Total rows sampled: {receipt['summary']['total']}",
        f"- Proven done: {receipt['summary']['proven_done']}",
        f"- Done but unproven: {receipt['summary']['done_unproven']}",
        f"- Planned / open: {receipt['summary']['planned']}",
        f"- Rows needing follow-up: {receipt['summary']['rows_needing_follow_up']}",
        f"- Threads needing follow-up: {receipt['summary']['threads_needing_follow_up']}",
        "",
        "## Plan Matrix",
        "",
        "| Plan | Argument | Status | Follow-up | Local Change | Live Website | Remaining | Evidence |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in receipt["rows"]:
        cells = [
            f"{row.get('plan_id', '')}: {row.get('title', '')}",
            row.get("argument", ""),
            row.get("trace_state", row.get("status", "")),
            row.get("follow_up_reason", ""),
            row.get("what_changed_locally", ""),
            row.get("live_on_website", ""),
            row.get("remaining_planned", ""),
            row.get("receipt_path", ""),
        ]
        safe = [str(c).replace("\n", " ").replace("|", "/")[:220] for c in cells]
        lines.append("| " + " | ".join(safe) + " |")
    lines.append("")
    return "\n".join(lines)


def run(*, limit: int = 120, include_live: bool = True, write: bool = False) -> dict[str, Any]:
    git = git_scope()
    receipts = receipt_index()
    live = live_probe(include_live)
    rows = collect_json_plan_rows(limit)
    if len(rows) < limit:
        rows.extend(collect_registry_rows(limit - len(rows)))
    rows = [classify_row(row, receipts=receipts, git=git, live=live) for row in rows[:limit]]
    row = {
        "schema": "sourcea-plan-traceability-machine-receipt-v1",
        "ok": True,
        "at": _now(),
        "input_contract": "disk plan SSOTs + git diff scope + receipt index + optional live sourcea.app probe",
        "receipt_path": str(RECEIPT),
        "report_path": str(REPORT),
        "source_count": len(PLAN_JSON_SOURCES) + len(REGISTRY_SOURCES),
        "receipt_count": len(receipts),
        "git_scope": git,
        "live_probe": live,
        "summary": summarize(rows),
        "rows": rows,
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        REPORT.write_text(build_markdown(row), encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--no-live", action="store_true")
    ap.add_argument("--limit", type=int, default=120)
    args = ap.parse_args()
    row = run(limit=max(1, min(args.limit, 500)), include_live=not args.no_live, write=args.write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        s = row["summary"]
        print(
            "traceability "
            f"ok={row['ok']} total={s['total']} proven_done={s['proven_done']} "
            f"done_unproven={s['done_unproven']} planned={s['planned']} "
            f"threads_follow_up={s['threads_needing_follow_up']} report={row['report_path']}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
