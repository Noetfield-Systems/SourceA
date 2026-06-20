#!/usr/bin/env python3
"""Governance unification engine — batch intake, score, report (hub API)."""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
UNIFY_ROOT = SINA_HOME / "governance-unification"
REPORTS_PATH = UNIFY_ROOT / "reports.jsonl"
LAW_DOC = "brain-os/law/GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md"

VERDICTS = frozenset({"ADOPT", "MERGE", "ATTACH", "REJECT", "DEFER"})
INTAKE_CLASSES = frozenset({"ASF_ORDER", "GOVERNANCE_DRAFT", "EXTERNAL_CRITIC", "COMPANION", "DUPLICATE", "SUPERSEDE"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _known_locked_paths() -> set[str]:
    paths: set[str] = set()
    for p in SOURCE_A.glob("*_LOCKED*.md"):
        paths.add(p.name)
    try:
        from hub_essentials_index import READ_CHAIN  # noqa: WPS433

        for row in READ_CHAIN:
            paths.add(row.get("path", ""))
    except Exception:
        pass
    return {x for x in paths if x}


def _classify_item(text: str, source: str) -> str:
    src = (source or "").lower()
    if "gpt" in src or "chatgpt" in src or "critic" in src:
        return "EXTERNAL_CRITIC"
    if "order" in src or src == "asf":
        return "ASF_ORDER"
    if "supersede" in text.lower() or "replaces v" in text.lower():
        return "SUPERSEDE"
    return "GOVERNANCE_DRAFT"


def _score_item(title: str, body: str, known: set[str]) -> tuple[str, str, str]:
    text = f"{title}\n{body}".lower()
    for name in known:
        stem = name.replace("_LOCKED", "").replace(".md", "").lower()
        if stem and stem in text:
            return "MERGE", name, "Overlaps existing canonical doc"
    if any(w in text for w in ("chatgpt", "gpt said", "external critic")):
        return "ATTACH", "archive/attachments/", "External critic — compare only"
    if len(body.strip()) < 40:
        return "REJECT", "", "Too short — no actionable content"
    if "locked" in text and "v1" in text:
        return "ADOPT", f"NEW_{re.sub(r'[^A-Z0-9]+', '_', title.upper())[:40]}_LOCKED_v1.md", "New LOCKED candidate"
    return "DEFER", "", "Needs ASF clarify before file move"


def _append_report(row: dict) -> None:
    UNIFY_ROOT.mkdir(parents=True, exist_ok=True)
    with REPORTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_reports(limit: int = 20) -> list[dict]:
    if not REPORTS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in REPORTS_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def run_batch(items: list[dict], *, source: str = "ASF") -> dict:
    known = _known_locked_paths()
    manifest: list[dict] = []
    for i, raw in enumerate(items, start=1):
        title = (raw.get("title") or raw.get("id") or f"item-{i}").strip()[:200]
        body = (raw.get("body") or raw.get("content") or raw.get("text") or "").strip()
        src = (raw.get("source") or source).strip()
        intake_class = _classify_item(f"{title}\n{body}", src)
        verdict, target, reason = _score_item(title, body, known)
        manifest.append(
            {
                "n": i,
                "title": title,
                "intake_class": intake_class,
                "verdict": verdict,
                "target": target,
                "reason": reason,
                "chars": len(body),
            }
        )
    report_id = f"UNIFY-{uuid.uuid4().hex[:10]}"
    row = {
        "id": report_id,
        "at": _now(),
        "source": source,
        "item_count": len(manifest),
        "manifest": manifest,
        "law_doc": LAW_DOC,
        "pipeline": "INTAKE → INVENTORY → SCORE → MAP → MERGE → ARCHIVE → SYNC → VERIFY",
        "note": "Report generated — maintainer applies MERGE/ADOPT to root LOCKED files per law",
    }
    _append_report(row)
    return {"ok": True, "report": row, "recent_reports": _load_reports(5)}


def unification_payload() -> dict:
    return {
        "ok": True,
        "law_doc": LAW_DOC,
        "storage": str(UNIFY_ROOT),
        "reports_path": str(REPORTS_PATH),
        "recent_reports": _load_reports(10),
        "verdicts": sorted(VERDICTS),
        "intake_classes": sorted(INTAKE_CLASSES),
    }


def handle_unification_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    if action in ("list", ""):
        return unification_payload()
    if action == "run_batch":
        items = body.get("items") or []
        if not items and body.get("batch_text"):
            chunks = re.split(r"\n-{3,}\n|\n#{2,3}\s+", body.get("batch_text") or "")
            items = [{"title": c.split("\n", 1)[0][:120], "body": c} for c in chunks if c.strip()]
        if not items:
            return {"ok": False, "error": "items or batch_text required"}
        return run_batch(items, source=(body.get("source") or "ASF"))
    return {"ok": False, "error": f"unknown action: {action}"}
