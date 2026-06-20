#!/usr/bin/env python3
"""P0 commercial film ship gate — ingest → critic → unfreeze → publish allow/deny.

Founder path after Screen Studio recording:
  1. Export master to Desktop (see lane candidates below)
  2. bash sourcea-commercial-film-ship.sh   OR   bash witnessbc-commercial-film-ship.sh

Receipt: ~/.sina/enforcement/commercial-film-ship-gate-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "enforcement" / "commercial-film-ship-gate-receipt-v1.json"
FREEZE_FLAG = SINA / "commercial-film-render-frozen-v1.flag"

sys.path.insert(0, str(ROOT / "scripts"))

from commercial_film_critic_circle_v1 import run as critic_run  # noqa: E402
from sourcea_commercial_film_ingest_master_v1 import (  # noqa: E402
    CANDIDATES as SOURCEA_CANDIDATES,
    find_master as sourcea_find_master,
    ingest as sourcea_ingest,
)
from witnessbc_commercial_film_ingest_master_v1 import (  # noqa: E402
    CANDIDATES as WITNESSBC_CANDIDATES,
    find_master as witnessbc_find_master,
    ingest as witnessbc_ingest,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _preflight_lane(lane: str, *, source: Path | None) -> dict[str, Any]:
    if lane == "sourcea":
        src, tier = sourcea_find_master(source)
        return {"ok": True, "lane": lane, "master": str(src), "tier": tier}
    if lane == "witnessbc":
        src, tier = witnessbc_find_master(source)
        return {"ok": True, "lane": lane, "master": str(src), "tier": tier}
    raise SystemExit(f"FAIL: unknown lane {lane}")


def _master_hint(lane: str) -> str:
    if lane == "sourcea":
        paths = "\n".join(f"    {p}" for p in SOURCEA_CANDIDATES)
        return f"SourceA Screen Studio master required:\n{paths}"
    paths = "\n".join(f"    {p}" for p in WITNESSBC_CANDIDATES)
    return f"WitnessBC Screen Studio master required:\n{paths}"


def run_ship_gate(
    *,
    lane: str,
    source: Path | None = None,
    skip_ingest: bool = False,
    skip_deploy: bool = False,
    critic_only: bool = False,
) -> dict[str, Any]:
    lane = lane.strip().lower()
    if lane not in ("sourcea", "witnessbc"):
        raise SystemExit("FAIL: lane must be sourcea or witnessbc")

    receipt: dict[str, Any] = {
        "schema": "commercial-film-ship-gate-receipt-v1",
        "at": _now(),
        "lane": lane,
        "steps": [],
        "publish_allowed": False,
    }

    if not critic_only:
        try:
            pre = _preflight_lane(lane, source=source)
            receipt["steps"].append({"step": "preflight_master", **pre})
        except SystemExit as exc:
            receipt["steps"].append({"step": "preflight_master", "ok": False, "error": str(exc)})
            receipt["hint"] = _master_hint(lane)
            receipt["publish_allowed"] = False
            RECEIPT.parent.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            raise SystemExit(str(exc)) from exc

        if not skip_ingest:
            if lane == "sourcea":
                ingest_receipt = sourcea_ingest(source=source, deploy=not skip_deploy)
            else:
                ingest_receipt = witnessbc_ingest(source=source)
            receipt["steps"].append(
                {
                    "step": "ingest_screen_studio",
                    "ok": True,
                    "grade": ingest_receipt.get("grade"),
                    "resolution": ingest_receipt.get("resolution"),
                    "duration_seconds": ingest_receipt.get("duration_seconds"),
                    "published": ingest_receipt.get("published"),
                    "deploy_ok": ingest_receipt.get("deploy_ok"),
                }
            )
        else:
            receipt["steps"].append({"step": "ingest_screen_studio", "skipped": True})

    critic = critic_run(write_freeze=True, lane=lane)
    receipt["steps"].append(
        {
            "step": "critic_circle",
            "ok": critic.get("ok"),
            "verdict": critic.get("verdict"),
            "freeze_cleared": critic.get("freeze_cleared", False),
            "judgments": [
                {
                    "label": j.get("label"),
                    "verdict": j.get("verdict"),
                    "tier": j.get("tier"),
                    "capture_method": j.get("capture_method"),
                    "failures": j.get("failures"),
                }
                for j in critic.get("judgments", [])
            ],
        }
    )

    publish_allowed = critic.get("verdict") == "PASS" and bool(critic.get("ok"))
    receipt["publish_allowed"] = publish_allowed
    receipt["render_frozen"] = FREEZE_FLAG.is_file()
    receipt["critic_receipt"] = str(SINA / "enforcement/commercial-film-critic-circle-receipt-v1.json")
    receipt["next_action"] = (
        f"Public embed OK for {lane} — ship hero"
        if publish_allowed
        else critic.get("next_action_only") or "Fix capture tier or re-record Screen Studio master"
    )
    receipt["factory_now_line"] = (
        f"ship-gate · {lane} · critic={critic.get('verdict')} · publish={'YES' if publish_allowed else 'NO'}"
    )

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="P0 ship gate: Screen Studio ingest → critic → unfreeze")
    ap.add_argument("--lane", required=True, choices=("sourcea", "witnessbc"))
    ap.add_argument("--source", type=Path, default=None, help="Explicit Screen Studio master file")
    ap.add_argument("--skip-ingest", action="store_true", help="Critic only on current site/desktop assets")
    ap.add_argument("--no-deploy", action="store_true", help="SourceA: skip run-recipe deploy after ingest")
    ap.add_argument("--critic-only", action="store_true", help="Alias for --skip-ingest")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    skip_ingest = args.skip_ingest or args.critic_only
    try:
        receipt = run_ship_gate(
            lane=args.lane,
            source=args.source,
            skip_ingest=skip_ingest,
            skip_deploy=args.no_deploy,
            critic_only=skip_ingest,
        )
    except SystemExit:
        return 1

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(receipt.get("factory_now_line", "ship-gate done"))
        print(f"publish_allowed={receipt.get('publish_allowed')}")
        print(f"render_frozen={receipt.get('render_frozen')}")
        print(f"NEXT: {receipt.get('next_action')}")
        print(f"RECEIPT={RECEIPT}")

    return 0 if receipt.get("publish_allowed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
