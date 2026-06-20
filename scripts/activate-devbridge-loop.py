#!/usr/bin/env python3
"""Activate AI Dev Bridge OS seed pack (100 catalog · 10 UI rows) and optionally start 10-round loop."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))

# Back-compat wrapper — use activate-portfolio-loop.py --pack ai_dev_bridge_os
from loop_seeds import activate_devbridge_seed_pack, _load_pack_file  # noqa: E402


def _load_devbridge_pack():
    return _load_pack_file("ai_dev_bridge_os")


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
    ap = argparse.ArgumentParser(description="Activate Dev Bridge loop pack (legacy archive)")
    ap.add_argument("--start", action="store_true", help="Start 10-round loop after activating pack")
    ap.add_argument("--force", action="store_true", help="Stop active loop before --start")
    ap.add_argument("--max-rounds", type=int, default=10)
    args = ap.parse_args()

    act = activate_devbridge_seed_pack(sync_ui_file=True)
    if not act.get("ok"):
        print(act.get("error", "activate failed"))
        return 1
    print(act.get("message"), f"· UI rows={act.get('count')} · catalog={act.get('catalog_size')}")

    pack = _load_devbridge_pack() or {}
    goal = pack.get("goal_default") or act.get("goal_default") or ""
    print("Goal preset:", goal[:200], "…" if len(goal) > 200 else "")

    st = _loop_state()
    if st.get("active"):
        print(f"Note: loop already active (round {st.get('round')}/{st.get('max_rounds')}).")
        print("Pack is active for seeds UI. Legacy loop archived — use RUN INBOX in Worker chat.")
        if not args.start:
            return 0

    if args.start:
        if st.get("active") and not args.force:
            print("Refusing --start while loop active. Pass --force to stop first.")
            return 2
        if st.get("active") and args.force:
            cancel = _api_post("/api/agent-loop", {"action": "cancel"})
            print(cancel.get("message", cancel))
        try:
            out = _api_post(
                "/api/agent-loop",
                {
                    "action": "start",
                    "goal": goal,
                    "trigger_source": "devbridge_pack",
                    "max_rounds": min(10, max(1, args.max_rounds)),
                },
            )
        except Exception as e:
            print("API failed — Worker chat RUN INBOX or legacy /legacy/ agent loop if ASF enables", e)
            return 3
        print(out.get("message", out.get("error", out)))
        return 0 if out.get("ok") else 4

    print("Next: RUN INBOX in Worker chat — or legacy /legacy/ agent loop if ASF enables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
