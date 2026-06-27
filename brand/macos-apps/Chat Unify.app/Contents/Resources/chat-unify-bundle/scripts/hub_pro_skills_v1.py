#!/usr/bin/env python3
"""Hub Pro skills — manifest, per-app experience log, agent append."""
from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data/hub-pro-skills-index-v1.json"
LOG_PATH = ROOT / "data/hub-pro-app-experience-log-v1.json"
SKILLS_ROOT = ROOT / ".cursor/skills"

GENERAL_TECHNICAL_CHECKLIST: list[dict[str, str]] = [
    {"id": "UP-0", "step": "Classify surface — ui_upgrade_path_classifier_v1.py --path"},
    {"id": "UP-1", "step": "FIRST CHECK ack — ui_upgrade_first_check_v1.py --surface <id> --ack"},
    {"id": "UP-2", "step": "Read per-app ledger MD — frozen inventory"},
    {"id": "UP-3", "step": "Inventory DOM/routes/CTAs vs frozen"},
    {"id": "UP-4", "step": "Edit additive only — no silent removals"},
    {"id": "UP-5", "step": "Verify — surface verify script from registry"},
    {"id": "UP-6", "step": "E2E — surface e2e (cloud CI if heavy on Mac founder session)"},
    {"id": "UP-7", "step": "Append ledger entry + hub_pro_skills experience log"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["saved_at"] = _now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _split_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in re.split(r"[,\n]", raw) if p.strip()]


def load_index() -> dict:
    return _load_json(INDEX_PATH)


def load_log() -> dict:
    row = _load_json(LOG_PATH)
    if not row:
        row = {
            "schema": "hub-pro-app-experience-log-v1",
            "version": "1.0.0",
            "entries": [],
        }
    return row


def entries_for_app(app_id: str, *, limit: int = 20) -> list[dict]:
    log = load_log()
    rows = [e for e in log.get("entries") or [] if e.get("app_id") == app_id]
    rows.sort(key=lambda r: r.get("at") or "", reverse=True)
    return rows[:limit]


def skill_bodies() -> list[dict]:
    index = load_index()
    out: list[dict] = []
    for sk in index.get("skills") or []:
        rel = sk.get("path") or ""
        path = ROOT / rel
        body = ""
        if path.is_file():
            body = path.read_text(encoding="utf-8", errors="replace")
        out.append({**sk, "exists": path.is_file(), "body_preview": body[:1200]})
    return out


def upgrade_ledger_for_app(app_meta: dict) -> dict | None:
    surface_id = (app_meta or {}).get("surface_id")
    if not surface_id:
        return None
    try:
        from ui_upgrade_ledger_v1 import show  # noqa: WPS433

        return show(surface_id)
    except SystemExit:
        return {"ok": False, "surface_id": surface_id, "error": "ledger_not_found"}
    except Exception as exc:
        return {"ok": False, "surface_id": surface_id, "error": str(exc)[:200]}


def payload(*, app_id: str | None = None) -> dict:
    index = load_index()
    apps = index.get("apps") or {}
    app_key = app_id or "worker_hub"
    app_meta = apps.get(app_key) or apps.get("worker_hub") or {}
    log = load_log()
    ledger = upgrade_ledger_for_app(app_meta)
    return {
        "ok": True,
        "schema": "hub-pro-skills-payload-v1",
        "at": _now(),
        "app_id": app_key,
        "app": app_meta,
        "index": {
            "label": index.get("label"),
            "version": index.get("version"),
            "one_law": index.get("one_law"),
            "skills": index.get("skills") or [],
            "related_law": index.get("related_law") or [],
        },
        "skills": skill_bodies(),
        "technical_checklist": GENERAL_TECHNICAL_CHECKLIST,
        "upgrade_ledger": ledger,
        "experience": {
            "path": str(LOG_PATH.relative_to(ROOT)),
            "entries_for_app": entries_for_app(app_key),
            "recent_all": (log.get("entries") or [])[-8:][::-1],
        },
        "append_hint": "python3 scripts/hub_pro_skills_v1.py --append --app <id> --agent <id> --summary '...'",
    }


def append_entry(
    *,
    app_id: str,
    agent: str,
    summary: str,
    obstacles: list[str] | None = None,
    fixes: list[str] | None = None,
    golden_tips: list[str] | None = None,
    paths: list[str] | None = None,
) -> dict:
    log = load_log()
    entries = list(log.get("entries") or [])
    stamp = _now()[:10].replace("-", "")
    seq = len(entries) + 1
    entry = {
        "id": f"HPL-{stamp}-{seq:03d}",
        "at": _now(),
        "app_id": app_id,
        "agent": agent,
        "summary": summary.strip(),
        "obstacles": obstacles or [],
        "fixes": fixes or [],
        "golden_tips": golden_tips or [],
        "paths": paths or [],
    }
    entries.append(entry)
    log["entries"] = entries
    _save_json(LOG_PATH, log)
    receipt = Path.home() / ".sina/hub-pro-skills-append-receipt-v1.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({"ok": True, "entry": entry}, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "entry": entry, "receipt_path": str(receipt)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Hub Pro skills manifest + experience log")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--app", default="", help="App id filter")
    ap.add_argument("--list-apps", action="store_true")
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--agent", default="agent")
    ap.add_argument("--summary", default="")
    ap.add_argument("--obstacles", default="")
    ap.add_argument("--fixes", default="")
    ap.add_argument("--tips", default="", help="golden_tips csv")
    ap.add_argument("--paths", default="")
    args = ap.parse_args()

    if args.append:
        if not args.app or not args.summary:
            row = {"ok": False, "error": "app and summary required"}
        else:
            row = append_entry(
                app_id=args.app,
                agent=args.agent,
                summary=args.summary,
                obstacles=_split_csv(args.obstacles),
                fixes=_split_csv(args.fixes),
                golden_tips=_split_csv(args.tips),
                paths=_split_csv(args.paths),
            )
    elif args.list_apps:
        index = load_index()
        row = {"ok": True, "apps": index.get("apps") or {}}
    else:
        row = payload(app_id=args.app or None)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
