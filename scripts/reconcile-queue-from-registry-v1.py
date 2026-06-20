#!/usr/bin/env python3
"""Align queue pointer to first sa not done in REGISTRY — receipt-safe reconcile."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"

sys.path.insert(0, str(SCRIPTS))
from healthy_queue_ssot_lib import load_healthy_queue, queue_items  # noqa: E402


def _current_pos() -> int:
    from healthy_queue_ssot_lib import healthy_queue_state_path  # noqa: WPS433

    path = healthy_queue_state_path()
    if path.is_file():
        try:
            return int(json.loads(path.read_text(encoding="utf-8")).get("next_pos") or 1)
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return 1


def reconcile(*, apply: bool = False, forward_only: bool = True) -> dict:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    status = {p["id"]: p.get("status") for p in reg.get("plans") or []}
    _, raw = load_healthy_queue()
    items = queue_items(raw)

    first_open = None
    skipped_done: list[dict] = []
    for idx, item in enumerate(items, start=1):
        pos = int(item.get("queue_pos") or idx)
        sid = item.get("sa_id") or ""
        st = status.get(sid, "MISSING")
        if st != "done" and first_open is None:
            first_open = pos
            break
        if st == "done":
            skipped_done.append({"pos": pos, "sa_id": sid, "role": item.get("queue_role")})

    if first_open is None:
        first_open = len(items) + 1

    cur_pos = _current_pos()
    target_pos = first_open
    rewind_blocked = False
    if forward_only and first_open < cur_pos:
        # Mid-slice progress (check→act→verify) — never rewind pointer backward.
        target_pos = cur_pos
        rewind_blocked = True

    out = {
        "ok": True,
        "first_open_pos": first_open,
        "current_pos": cur_pos,
        "target_pos": target_pos,
        "forward_only": forward_only,
        "rewind_blocked": rewind_blocked,
        "skipped_done_turns": len(skipped_done),
        "skipped_sample": skipped_done[:5],
        "queue_total": len(items),
    }

    if apply and not rewind_blocked and target_pos != cur_pos and target_pos <= len(items):
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "advance-healthy-queue-v1.py"),
                "--set-pos",
                str(target_pos),
                "--reason",
                "reconcile_registry_forward" if forward_only else "reconcile_registry",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        try:
            out["advance"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            out["advance"] = {"raw": proc.stdout, "stderr": proc.stderr}
        out["applied"] = proc.returncode == 0
    else:
        out["applied"] = False
        if rewind_blocked:
            out["hint"] = "forward_only: rewind blocked — pointer unchanged"
        elif target_pos == cur_pos:
            out["hint"] = "pointer already at target"
        else:
            out["hint"] = "pass --apply to write pointer"

    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = reconcile(apply=args.apply)
    print(json.dumps(row, indent=2) if args.json else json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
