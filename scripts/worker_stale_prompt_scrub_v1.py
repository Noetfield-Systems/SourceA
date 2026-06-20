#!/usr/bin/env python3
"""Scrub stale Prompt feed / command-data steer from Worker disk caches (INCIDENT-034).

Targets: broker cache · session gate · truth bundle · run-inbox truth · inbox prompt · execution lane.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
NEXT_STEPS = (
    "Worker Hub http://127.0.0.1:13020/ · UI tab Next steps · "
    "disk ~/.sina/live-ongoing-prompts-next-10-v1.json"
)
STALE = re.compile(
    r"Prompt\s+feed|prompt-feed|prompt_feed|Sina\s+Command|Confirm\s+auto-send|AUTO-RUN\s+P0",
    re.I,
)

WIRE_FILES = (
    "brain-wire-v1.json",
    "governance-brain-wire-v1.json",
    "l1-brain-pipeline-wire-v1.json",
    "l1-agent-pipeline-wire-v1.json",
    "monitor-live-v1.json",
    "run-inbox-disk-truth-v1.json",
    "governance-stairlift-v1.json",
    "governance-propagation-receipt-v1.json",
    "phase-strict-drain-v1.json",
)


def _fresh_directive_suffix() -> str:
    try:
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from founder_directive_ssot_v1 import execution_rail_line, truth_block_lines  # noqa: WPS433

        lines = truth_block_lines()
        if lines:
            return "\n".join(lines) + "\n"
        return f"Rail: {execution_rail_line()}\n"
    except Exception:
        return ""


def _rewrite_prompt(prompt: str) -> str | None:
    if not STALE.search(prompt):
        return None
    head = prompt.split("═ FOUNDER DIRECTIVE", 1)[0].rstrip()
    if not head.endswith("\n"):
        head += "\n"
    suffix = _fresh_directive_suffix()
    return head + (suffix or "INBOX cleared · stale brand scrubbed\n")


def _scrub_wire_file(path: Path, *, write: bool) -> list[dict]:
    actions: list[dict] = []
    if not path.is_file():
        return actions
    try:
        import sys
        from pathlib import Path as P

        sys.path.insert(0, str(P(__file__).resolve().parent))
        from founder_directive_ssot_v1 import execution_rail_line  # noqa: WPS433

        rail = execution_rail_line()
        raw = path.read_text(encoding="utf-8")
        if not STALE.search(raw):
            return actions
        data = json.loads(raw)
        changed = False

        def walk(obj):
            nonlocal changed
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    if k in ("phase_strict_order", "order", "phase_strict", "execution_rail", "note", "law") and isinstance(v, str) and STALE.search(v):
                        if k == "law" and "quarantine" in v.lower():
                            obj[k] = "cycle-3: Hub 2 machine drain — phase-s8 · legacy hub offline"
                        elif k == "note":
                            obj[k] = "ASF: Hub 2 machine drain — legacy hub offline · RUN INBOX only"
                        else:
                            obj[k] = rail
                        changed = True
                    elif k == "bind" and isinstance(v, str) and STALE.search(v):
                        obj[k] = "RUN INBOX only · legacy hub offline"
                        changed = True
                    else:
                        walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)
        if changed and write:
            data["stale_wire_scrub_at"] = _now()
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            actions.append({"file": str(path), "action": "scrubbed_wire_fields"})
    except (OSError, json.JSONDecodeError) as exc:
        actions.append({"file": str(path), "error": str(exc)})
    return actions


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fix_inject(inj: dict) -> tuple[dict, list[str]]:
    actions: list[str] = []
    if not isinstance(inj, dict):
        return inj, actions
    if inj.pop("forbidden_daily", None):
        actions.append("removed_forbidden_daily")
    if "prompt-feed" in str(inj.get("next_steps") or ""):
        inj["next_steps"] = NEXT_STEPS
        actions.append("fixed_next_steps")
    inj.setdefault(
        "daily_positive",
        [
            "RUN INBOX one sa/turn",
            "Worker Hub Next steps optional glance",
            "Quote factory_now_line from truth bundle",
        ],
    )
    return inj, actions


def scrub_worker_stale_disk(*, write: bool = True) -> dict:
    actions: list[dict] = []

    broker_path = SINA / "goal1-lane-broker-v1.json"
    if broker_path.is_file():
        try:
            data = json.loads(broker_path.read_text(encoding="utf-8"))
            changed = False
            for key in ("inbox_after_ack", "last_deliver", "last_pickup", "last_submit", "inbox_after"):
                block = data.get(key)
                if not isinstance(block, dict):
                    continue
                prompt = str(block.get("prompt") or "")
                if not prompt:
                    continue
                new_prompt = _rewrite_prompt(prompt)
                if new_prompt:
                    block["prompt"] = new_prompt
                    block["preview"] = new_prompt[:200]
                    block["chars"] = len(new_prompt)
                    data[key] = block
                    changed = True
                    actions.append({"file": str(broker_path), "field": key, "action": "rewrote_stale_prompt"})
            inbox = (data.get("last_auto_deliver") or {}).get("inbox")
            if isinstance(inbox, dict):
                prompt = str(inbox.get("prompt") or "")
                new_prompt = _rewrite_prompt(prompt)
                if new_prompt:
                    inbox["prompt"] = new_prompt
                    inbox["preview"] = new_prompt[:200]
                    inbox["chars"] = len(new_prompt)
                    data["last_auto_deliver"]["inbox"] = inbox
                    changed = True
                    actions.append({"file": str(broker_path), "field": "last_auto_deliver.inbox", "action": "rewrote_stale_prompt"})
            if changed and write:
                data["stale_prompt_scrub_at"] = _now()
                broker_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError) as exc:
            actions.append({"file": str(broker_path), "error": str(exc)})

    for rel in (
        "agent_session_gate_receipt_v1.json",
        "last-truth-bundle-v1.json",
    ):
        path = SINA / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            changed = False
            inj, acts = _fix_inject(data.get("inject") or {})
            if acts:
                data["inject"] = inj
                changed = True
                for a in acts:
                    actions.append({"file": str(path), "action": a})
            rit = data.get("run_inbox_truth")
            if isinstance(rit, dict) and rit.pop("prompt_feed_lane", None):
                rit["next_steps_lane"] = rit.get("next_steps_lane") or "advisory_only"
                data["run_inbox_truth"] = rit
                changed = True
                actions.append({"file": str(path), "action": "renamed_prompt_feed_lane"})
            if changed and write:
                path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    truth_path = SINA / "run-inbox-disk-truth-v1.json"
    if truth_path.is_file():
        try:
            data = json.loads(truth_path.read_text(encoding="utf-8"))
            from worker_steer_guard_v1 import heal_truth_row  # noqa: WPS433

            data, changed = heal_truth_row(data)
            if changed:
                actions.append({"file": str(truth_path), "action": "healed_prompt_feed_lane_key"})
            if changed and write:
                truth_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    inbox_path = SINA / "worker-prompt-inbox-v1.json"
    if inbox_path.is_file():
        try:
            data = json.loads(inbox_path.read_text(encoding="utf-8"))
            prompt = str(data.get("prompt") or "")
            new_prompt = _rewrite_prompt(prompt)
            if new_prompt:
                data["prompt"] = new_prompt
                data["chars"] = len(new_prompt)
                data["stale_scrub_at"] = _now()
                if write:
                    inbox_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                actions.append({"file": str(inbox_path), "action": "rewrote_stale_prompt"})
        except (OSError, json.JSONDecodeError):
            pass

    exec_path = SINA / "execution-lane-v1.json"
    if exec_path.is_file():
        try:
            from worker_steer_guard_v1 import heal_execution_lane_row  # noqa: WPS433

            data = json.loads(exec_path.read_text(encoding="utf-8"))
            data, changed = heal_execution_lane_row(data)
            if changed:
                data["scrubbed_at"] = _now()
                if write:
                    exec_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                actions.append({"file": str(exec_path), "action": "advisory_live_next10_mirror"})
        except (OSError, json.JSONDecodeError):
            pass

    ongoing = SINA / "live-ongoing-prompts-next-10-v1.json"
    if ongoing.is_file():
        try:
            data = json.loads(ongoing.read_text(encoding="utf-8"))
            changed = False
            for turn in data.get("turns") or []:
                if not isinstance(turn, dict):
                    continue
                preview = str(turn.get("preview") or turn.get("prompt_preview") or "")
                if STALE.search(preview):
                    turn.pop("preview", None)
                    turn.pop("prompt_preview", None)
                    changed = True
            if changed and write:
                data["stale_scrub_at"] = _now()
                ongoing.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                actions.append({"file": str(ongoing), "action": "scrubbed_turn_previews"})
        except (OSError, json.JSONDecodeError):
            pass

    for name in WIRE_FILES:
        actions.extend(_scrub_wire_file(SINA / name, write=write))

    surfaces = SINA / "agent-live-surfaces-v1.json"
    if surfaces.is_file():
        try:
            data = json.loads(surfaces.read_text(encoding="utf-8"))
            changed = False
            if data.pop("founder_museum", None) is not None:
                changed = True
            if changed and write:
                surfaces.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                actions.append({"file": str(surfaces), "action": "removed_founder_museum_surface"})
        except (OSError, json.JSONDecodeError):
            pass

    missed = SINA / "founder-missed-actions-card-v1.json"
    if missed.is_file():
        try:
            data = json.loads(missed.read_text(encoding="utf-8"))
            changed = False
            for row in data.get("actions") or data.get("cards") or data.get("items") or []:
                if not isinstance(row, dict):
                    continue
                if row.get("id") in ("founder-prompt-feed", "founder-next-steps"):
                    if row.get("id") == "founder-prompt-feed":
                        row["id"] = "founder-next-steps"
                        changed = True
                    if row.get("tab") == "prompt-feed":
                        row["tab"] = "next-steps"
                        changed = True
                    row["label"] = row.get("label") or "Next steps"
                    row["title"] = row.get("title") or "Next steps"
            if changed and write:
                missed.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                actions.append({"file": str(missed), "action": "renamed_founder_next_steps"})
        except (OSError, json.JSONDecodeError):
            pass

    return {"ok": True, "at": _now(), "actions": actions, "count": len(actions)}


def main() -> int:
    p = argparse.ArgumentParser(description="Scrub stale Prompt feed from Worker disk caches")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = scrub_worker_stale_disk()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"WORKER_STALE_SCRUB actions={row.get('count')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
