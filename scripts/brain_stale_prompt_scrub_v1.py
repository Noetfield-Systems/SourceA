#!/usr/bin/env python3
"""Scrub stale Prompt feed / Sina Command steer from Brain disk caches (INCIDENT-034)."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
STALE = re.compile(
    r"Prompt\s+feed|prompt-feed|prompt_feed|Sina\s+Command\s*→\s*Prompt|Confirm\s+auto-send",
    re.I,
)
POSITIVE_CLOSE = (
    "Worker chat: RUN INBOX one sa/turn. Optional: Worker Hub http://127.0.0.1:13020/ "
    "→ Form · Safety · H2 machines. Quote factory_now_line from truth bundle."
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _heal_strings(obj, path: str = "") -> tuple[object, list[str]]:
    actions: list[str] = []
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("founder_line", "founder_surface", "mandatory_next", "founder_message") and isinstance(
                v, str
            ):
                if STALE.search(v):
                    if k == "mandatory_next" and obj.get("queue_head"):
                        qh = obj.get("queue_head") or {}
                        sa = qh.get("sa_id") or "?"
                        role = str(qh.get("role") or "check").upper()
                        out[k] = f"Worker chat → RUN INBOX — {sa} {role}"
                    else:
                        out[k] = POSITIVE_CLOSE
                    actions.append(f"{path}.{k}")
                else:
                    out[k] = v
            else:
                fixed, acts = _heal_strings(v, f"{path}.{k}" if path else k)
                out[k] = fixed
                actions.extend(acts)
        return out, actions
    if isinstance(obj, list):
        out_list = []
        for i, v in enumerate(obj):
            fixed, acts = _heal_strings(v, f"{path}[{i}]")
            out_list.append(fixed)
            actions.extend(acts)
        return out_list, actions
    if isinstance(obj, str) and STALE.search(obj):
        return POSITIVE_CLOSE, [path or "string"]
    return obj, actions


def scrub_brain_stale_disk(*, write: bool = True) -> dict:
    actions: list[dict] = []
    for rel in (
        "brain-current-action-v1.json",
        "brain-fast-startup-v1.json",
        "brain-goal1-validation-v1.json",
        "brain-self-heal-startup-v1.json",
        "agent_session_gate_receipt_v1.json",
        "last-truth-bundle-v1.json",
    ):
        path = SINA / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if rel == "agent_session_gate_receipt_v1.json" and data.get("role") != "brain":
                continue
            healed, acts = _heal_strings(data)
            if acts:
                if write:
                    healed["brain_stale_scrub_at"] = _now()
                    path.write_text(json.dumps(healed, indent=2) + "\n", encoding="utf-8")
                for a in acts:
                    actions.append({"file": str(path), "field": a, "action": "healed_stale_steer"})
        except (OSError, json.JSONDecodeError) as exc:
            actions.append({"file": str(path), "error": str(exc)})

    try:
        from brain_live_context_v1 import build_brain_live_context  # noqa: WPS433

        ctx = build_brain_live_context()
        if write:
            (SINA / "brain-live-context-v1.json").write_text(json.dumps(ctx, indent=2) + "\n", encoding="utf-8")
        actions.append({"file": str(SINA / "brain-live-context-v1.json"), "action": "rebuilt_brain_live_context"})
    except Exception as exc:
        actions.append({"action": "brain_live_context", "error": str(exc)})

    return {"ok": True, "at": _now(), "actions": actions, "count": len(actions)}


def main() -> int:
    p = argparse.ArgumentParser(description="Scrub stale Prompt feed from Brain disk caches")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = scrub_brain_stale_disk()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"BRAIN_STALE_SCRUB actions={row.get('count')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
