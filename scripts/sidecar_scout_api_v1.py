#!/usr/bin/env python3
"""Lane B — API scout. Lookahead CHECK items only. Never advances boss queue."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = Path.home() / ".sina" / "sidecar" / "api-scout"
LOG = Path.home() / ".sina" / "sidecar-scout-api-v1.jsonl"

sys.path.insert(0, str(SCRIPTS))
from healthy_queue_ssot_lib import (  # noqa: E402
    healthy_queue_state_path,
    load_healthy_queue,
    queue_items,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _current_pos() -> int:
    st = healthy_queue_state_path()
    if st.is_file():
        try:
            return int(json.loads(st.read_text()).get("next_pos") or 1)
        except (ValueError, json.JSONDecodeError):
            pass
    return 1


def _lookahead_checks(*, ahead: int = 3) -> list[dict]:
    _, raw = load_healthy_queue()
    items = queue_items(raw)
    pos = _current_pos()
    picks: list[dict] = []
    for i in range(pos, min(len(items), pos + ahead - 1) + 1):
        item = items[i - 1]
        role = (item.get("queue_role") or "").lower()
        if role == "check":
            picks.append({**item, "_lookahead_pos": i})
    return picks


def _resolve_sa_file(sa_path: str) -> Path | None:
    if not sa_path:
        return None
    for base in (ROOT, ROOT / "brain-os/plan-registry/sourcea-1000"):
        p = base / sa_path
        if p.is_file():
            return p
    return None


def _scout_usable(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 200:
        return False
    body = path.read_text(encoding="utf-8", errors="replace").lower()
    junk = ("don't have access", "cannot retrieve", "paste the content", "provide the task")
    return not any(j in body for j in junk)


def _scout_one(item: dict, *, dry_run: bool) -> dict:
    sa_id = item.get("sa_id", "unknown")
    out = OUT / f"{sa_id}-scout.md"
    if _scout_usable(out):
        return {"ok": True, "sa_id": sa_id, "skipped": "fresh_scout_exists", "path": str(out)}

    sa_path = item.get("sa_path") or ""
    sa_text = ""
    full = _resolve_sa_file(sa_path)
    if full:
        sa_text = full.read_text(encoding="utf-8", errors="replace")[:12000]

    prompt = (
        f"SCOUT LANE ONLY — {sa_id} CHECK lookahead pos {item.get('_lookahead_pos')}.\n"
        "Read task context. List gaps vs verify criteria. NO implement. NO queue advance.\n"
        f"Task path: {sa_path}\n\n{sa_text}"
    )

    if dry_run:
        _log({"event": "dry_run", "sa_id": sa_id})
        return {"ok": True, "dry_run": True, "sa_id": sa_id}

    sys.path.insert(0, str(SCRIPTS))
    from paid_engine_gate_v1 import block_paid  # noqa: WPS433

    gate = block_paid(engine="api", caller="sidecar_scout_api")
    if gate:
        _log({"event": "scout_blocked", "sa_id": sa_id, **gate})
        return {"ok": True, "sa_id": sa_id, "skipped": gate.get("reason"), "cost_usd": 0}

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"ok": False, "error": "ANTHROPIC_API_KEY not set"}

    try:
        import anthropic  # noqa: WPS433
    except ImportError:
        return {"ok": False, "error": "pip install anthropic"}

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    body = msg.content[0].text if msg.content else ""
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"# API scout — {sa_id}\n\n**At:** {_now()}\n**Lane:** B (no queue touch)\n\n{body}\n",
        encoding="utf-8",
    )
    _log({"event": "scout_written", "sa_id": sa_id, "path": str(out)})
    return {"ok": True, "sa_id": sa_id, "path": str(out)}


def main() -> int:
    p = argparse.ArgumentParser(description="Lane B — API scout (lookahead CHECK only)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--ahead", type=int, default=3)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    picks = _lookahead_checks(ahead=args.ahead)
    results = [_scout_one(it, dry_run=args.dry_run) for it in picks]
    row = {"ok": all(r.get("ok") for r in results), "lane": "B", "scouts": results}
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        for r in results:
            print(r)
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
