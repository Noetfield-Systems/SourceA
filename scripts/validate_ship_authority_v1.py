#!/usr/bin/env python3
"""Ship authority pack auditor — sina_read >= 90 before ready_for_founder_send.

Law: data/anti-theater-validator-loop-v1.json ship_authority block
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUTBOUND = SINA / "outbound"
REVIEW = SINA / "w3-founder-review-v1.json"
LAW = "scripts/validate_ship_authority_v1.py"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sina_score(pack: dict) -> int | None:
    val = pack.get("sina_read_score_pct")
    if val is None:
        val = pack.get("founder_score_pct")
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def validate(*, include_review: bool = True) -> dict:
    pack_violations: list[dict] = []
    scanned = 0
    sina_pending = 0

    if OUTBOUND.is_dir():
        for pack_path in sorted(OUTBOUND.glob("**/pack.json")):
            scanned += 1
            pack = _read(pack_path)
            status = str(pack.get("status") or "")
            sina = _sina_score(pack)
            acct = pack.get("account_id") or pack_path.parent.name.replace("w3-canada-", "")
            if sina is None or sina < 90:
                if status == "ready_for_founder_send":
                    pack_violations.append(
                        {
                            "account_id": acct,
                            "path": str(pack_path),
                            "status": status,
                            "sina_read_score_pct": sina,
                            "issue": "ship_ready_without_sina_90",
                        }
                    )
                elif status == "machine_pass_await_sina_read":
                    sina_pending += 1
            elif status == "machine_pass_await_sina_read":
                pack_violations.append(
                    {
                        "account_id": acct,
                        "status": status,
                        "sina_read_score_pct": sina,
                        "issue": "sina_90_but_status_still_await",
                    }
                )

    review_violations: list[dict] = []
    if include_review:
        review = _read(REVIEW)
        for art in review.get("artifacts") or []:
            scores = art.get("scores") or {}
            if art.get("send_red") and scores.get("sina_read_pending"):
                review_violations.append(
                    {
                        "account_id": art.get("account_id"),
                        "issue": "send_red_true_while_sina_pending",
                    }
                )
            if art.get("send_red"):
                sina = scores.get("sina_read_score_pct")
                if sina is None or int(sina) < 90:
                    review_violations.append(
                        {
                            "account_id": art.get("account_id"),
                            "issue": "send_red_without_sina_90",
                            "sina_read_score_pct": sina,
                        }
                    )
                if not art.get("to"):
                    review_violations.append(
                        {
                            "account_id": art.get("account_id"),
                            "issue": "send_red_without_to",
                        }
                    )

    violations = pack_violations + review_violations
    ok = len(violations) == 0
    return {
        "ok": ok,
        "law": LAW,
        "scanned_packs": scanned,
        "sina_pending": sina_pending,
        "violation_count": len(violations),
        "violations": violations,
        "ship_authority": "sina_read_score_pct >= 90 only",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Ship authority pack auditor")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = validate()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row['ok']} violations={row['violation_count']} sina_pending={row['sina_pending']}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
