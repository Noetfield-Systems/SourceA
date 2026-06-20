#!/usr/bin/env python3
"""EXECUTOR/CI ONLY — founders use Worker chat RUN INBOX (no Terminal).

Activate loop seed pack: ai_dev_bridge_os | trustfield | virlux | noetfield_local — optional start loop via API.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))

from loop_pack_registry import PACKS, list_pack_ids  # noqa: E402
from loop_seeds import activate_seed_pack, _load_pack_file  # noqa: E402


def _loop_state() -> dict:
    p = Path.home() / ".sina/agent-loop.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _api_post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:13020" + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def main() -> int:
    ap = argparse.ArgumentParser(description="Activate portfolio loop prompt pack (legacy archive)")
    ap.add_argument(
        "--pack",
        choices=list_pack_ids(),
        default="ai_dev_bridge_os",
        help="Which repo pack to activate (default: ai_dev_bridge_os)",
    )
    ap.add_argument("--start", action="store_true", help="Start 10-round loop after activating pack")
    ap.add_argument("--force", action="store_true", help="Stop active loop before --start")
    ap.add_argument("--max-rounds", type=int, default=10)
    args = ap.parse_args()

    act = activate_seed_pack(args.pack, sync_ui_file=True)
    if not act.get("ok"):
        print(act.get("error", "activate failed"))
        return 1
    print(act.get("message"), f"· rows={act.get('count')} · catalog={act.get('catalog_size')}")

    pack = _load_pack_file(args.pack) or {}
    goal = pack.get("goal_default") or act.get("goal_default") or ""
    spec = PACKS[args.pack]
    print("Pack:", spec["label"])
    print("Goal:", goal[:240], "…" if len(goal) > 240 else "")
    if spec.get("workspace_rule"):
        print("Workspace:", spec.get("root"))
        print("Forbidden:", spec.get("workspace_forbidden", ""))

    st = _loop_state()
    if st.get("active"):
        print(f"Note: loop already active (round {st.get('round')}/{st.get('max_rounds')}).")
        print("Legacy loop archived. Stop via API first, or use --start --force.")
        if not args.start:
            return 0

    if args.start:
        if st.get("active") and not args.force:
            print("Refusing --start while loop active. Pass --force to stop first.")
            return 2
        if st.get("active") and args.force:
            print(_api_post("/api/agent-loop", {"action": "cancel"}).get("message", "cancelled"))
        try:
            out = _api_post(
                "/api/agent-loop",
                {
                    "action": "start",
                    "goal": goal,
                    "trigger_source": f"pack:{args.pack}",
                    "max_rounds": min(10, max(1, args.max_rounds)),
                },
            )
        except Exception as e:
            print("API failed — RUN INBOX in Worker chat or legacy /legacy/ agent loop", e)
            return 3
        print(out.get("message", out.get("error", out)))
        return 0 if out.get("ok") else 4

    print("Next: RUN INBOX in Worker chat — legacy /legacy/ agent loop if ASF enables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
