"""sourcea-sdk CLI — sign · replay · spine-tail."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sourcea_sdk.receipt import load_latest_receipt, sign_receipt, verify_receipt
from sourcea_sdk.spine import append_spine_event, tail_spine


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sourcea-sdk", description="Governance receipt spine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sign = sub.add_parser("sign", help="Sign intent → receipt (+ optional spine bind)")
    sign.add_argument("--intent", required=True, help="JSON intent body or path to JSON file")
    sign.add_argument("--out", default="", help="Ignored — writes .sourcea/receipts/latest.json")
    sign.add_argument("--bind-spine", action="store_true")

    replay = sub.add_parser("replay", help="Verify latest or named receipt")
    replay.add_argument("--file", default="", help="Receipt path (default: .sourcea/receipts/latest.json)")
    replay.add_argument("--last", action="store_true")

    tail = sub.add_parser("spine-tail", help="Show last N spine events")
    tail.add_argument("--n", type=int, default=5)

    args = ap.parse_args(argv)

    if args.cmd == "sign":
        raw = args.intent.strip()
        if raw.startswith("{") or raw.startswith("["):
            intent = json.loads(raw)
        else:
            intent = json.loads(Path(raw).read_text(encoding="utf-8"))
        spine_event = None
        if args.bind_spine:
            spine_event = append_spine_event(
                event_type="WORKER_ROUND",
                object_id=str(intent.get("object_id") or intent.get("intent_id") or "sdk-sign"),
                object_kind="task",
                payload={"intent_id": intent.get("intent_id"), "sdk": True},
            )
            if not spine_event.get("ok"):
                print(json.dumps(spine_event, indent=2))
                return 1
        receipt = sign_receipt(intent=intent, bind_spine=args.bind_spine, spine_event=spine_event)
        print(json.dumps({"ok": True, "receipt": receipt}, indent=2))
        return 0

    if args.cmd == "replay":
        if args.file:
            receipt = json.loads(Path(args.file).read_text(encoding="utf-8"))
        else:
            receipt = load_latest_receipt()
        if not receipt:
            print(json.dumps({"ok": False, "error": "no receipt found"}, indent=2))
            return 1
        ok, reason = verify_receipt(receipt)
        print(json.dumps({"ok": ok, "reason": reason, "receipt_id": receipt.get("receipt_id")}, indent=2))
        return 0 if ok else 1

    if args.cmd == "spine-tail":
        rows = tail_spine(n=max(1, args.n))
        print(json.dumps({"ok": True, "count": len(rows), "rows": rows}, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
