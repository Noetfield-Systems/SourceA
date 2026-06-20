#!/usr/bin/env python3
"""Factory output critic circle — Observe · Analyze · Search · Learn · Improve.

Repeatable quality loop for ALL factory outputs (W3 email · FBE · CREED).
Better Loop = system running · Best Loop OQG = machine score · Critic Circle = improve until true ≥90%.

Law: docs/SOURCEA_FACTORY_OUTPUT_CRITIC_LOOP_LOCKED_v1.md
Receipt: ~/.sina/factory-output-critic-circle-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "factory-output-critic-circle-v1.json"
RECEIPT = SINA / "factory-output-critic-circle-receipt-v1.json"
INCIDENTS = SINA / "factory-output-critic-incidents-v1.jsonl"
OQG_BAR = 90


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _top_failures(checks: list[dict], *, limit: int = 5) -> list[str]:
    out: list[str] = []
    for chk in checks or []:
        issues = chk.get("issues") or []
        cid = str(chk.get("id") or "?")
        pts = chk.get("points")
        mx = chk.get("max")
        if issues:
            for iss in issues[:2]:
                out.append(f"{cid}:{iss}")
        elif mx and pts is not None and int(pts) < int(mx):
            out.append(f"{cid}:partial({pts}/{mx})")
        if len(out) >= limit:
            break
    return out


def _verdict(*, machine: int, founder: int | None, founder_required: bool) -> str:
    if machine < OQG_BAR:
        return "IMPROVE"
    if founder_required and founder is None:
        return "IMPROVE"
    if founder is not None and founder < OQG_BAR:
        return "IMPROVE"
    if machine >= OQG_BAR and (founder is None or founder >= OQG_BAR):
        if founder is None and founder_required:
            return "IMPROVE"
        return "PASS"
    return "IMPROVE"


def _next_action(*, lane: str, artifact_id: str, verdict: str, failures: list[str], founder: int | None) -> str:
    if verdict == "PASS":
        return "hold — re-run critic after any edit · ship only when all gates green"
    if founder is None and artifact_id:
        return f"sina_read {artifact_id} after full read — machine/advisor never ship authority"
    if any("fefs" in f for f in failures):
        return "rewrite per FEFS R1–R10 · one idea · pain-first · 90–140 words · re-pack · re-OQG"
    if any("url" in f for f in failures):
        return "fix URL or remove cold link · re-pack · re-OQG"
    if any("ril_" in f or "preview" in f or "no_url" in f for f in failures):
        return "add recipient-interest preview/demo link per RIL SSOT · re-pack · re-RIL"
    if lane == "fbe_sourcea":
        return "FBE bay harden — refinery+assembly verify · RunReceipt ZIP · re-OQG fleet"
    if lane == "creed_campus":
        return "CREED dealer 16-step + intake PASS on wired subset · re-OQG"
    return "one bounded fix · re-run factory_output_critic_circle_v1.py --json"


def _observe_w3() -> list[dict]:
    sys.path.insert(0, str(SCRIPTS))
    from w3_founder_review_v1 import build_review  # noqa: WPS433

    review = build_review(write=False)
    rows: list[dict] = []
    for art in review.get("artifacts") or []:
        status = str(art.get("status") or "")
        compile_gate = str(art.get("compile_gate") or "")
        if status == "compile_deferred" or compile_gate.startswith("blocked_until"):
            continue
        if not str(art.get("body_text") or "").strip():
            continue
        sc = art.get("scores") or {}
        machine = int(sc.get("machine_oqg_pct") or 0)
        founder = sc.get("sina_read_score_pct") or sc.get("founder_score_pct")
        founder_i = int(founder) if founder is not None else None
        checks = sc.get("machine_checks") or []
        failures = _top_failures(checks)
        v = _verdict(machine=machine, founder=founder_i, founder_required=True)
        rows.append(
            {
                "artifact_id": art.get("account_id"),
                "lane": "w3_commercial",
                "company": art.get("company"),
                "machine_oqg_pct": machine,
                "structural_pct": sc.get("machine_structural_pct"),
                "persuasion_fefs_pct": sc.get("machine_persuasion_fefs_pct"),
                "sina_read_score_pct": founder_i,
                "sina_read_pending": sc.get("sina_read_pending") or sc.get("founder_score_pending"),
                "founder_score_pct": founder_i,
                "founder_score_pending": sc.get("sina_read_pending") or sc.get("founder_score_pending"),
                "pipeline_send_slot": art.get("pipeline_send_slot"),
                "verdict": v,
                "failures": failures,
                "next_action": _next_action(
                    lane="w3_commercial",
                    artifact_id=str(art.get("account_id") or ""),
                    verdict=v,
                    failures=failures,
                    founder=founder_i,
                ),
            }
        )
    return rows


def _observe_fleet_lanes() -> list[dict]:
    oqg = _read_json(SINA / "best-loop-oqg-receipt-v1.json")
    rows: list[dict] = []
    for lane in oqg.get("lanes") or []:
        lid = str(lane.get("lane") or "")
        if lid == "w3_commercial":
            continue
        machine = int(lane.get("output_clean_now") or lane.get("output_clean_pct") or 0)
        v = _verdict(machine=machine, founder=None, founder_required=False)
        failures = _top_failures(lane.get("checks") or [])
        rows.append(
            {
                "artifact_id": lid,
                "lane": lid,
                "machine_oqg_pct": machine,
                "founder_score_pct": None,
                "verdict": v,
                "failures": failures,
                "next_action": _next_action(
                    lane=lid,
                    artifact_id=lid,
                    verdict=v,
                    failures=failures,
                    founder=None,
                ),
            }
        )
    return rows


def _append_incidents(artifacts: list[dict]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    with INCIDENTS.open("a", encoding="utf-8") as fh:
        for art in artifacts:
            if art.get("verdict") == "PASS":
                continue
            fh.write(
                json.dumps(
                    {
                        "at": _now(),
                        "artifact_id": art.get("artifact_id"),
                        "lane": art.get("lane"),
                        "machine_oqg_pct": art.get("machine_oqg_pct"),
                        "founder_score_pct": art.get("founder_score_pct"),
                        "failures": art.get("failures"),
                        "next_action": art.get("next_action"),
                    }
                )
                + "\n"
            )


def run_critic(*, write: bool = True, learn: bool = True) -> dict:
    cfg = _read_json(CONFIG)
    w3 = _observe_w3()
    fleet = _observe_fleet_lanes()
    artifacts = w3 + fleet

    improve_n = sum(1 for a in artifacts if a.get("verdict") == "IMPROVE")
    pass_n = sum(1 for a in artifacts if a.get("verdict") == "PASS")
    w3_pass = all(a.get("verdict") == "PASS" for a in w3) if w3 else False
    fleet_pass = all(a.get("verdict") == "PASS" for a in fleet) if fleet else False

    oqg = _read_json(SINA / "best-loop-oqg-receipt-v1.json")
    fleet_now = oqg.get("fleet_output_clean_now") or oqg.get("fleet_output_clean_pct")

    row = {
        "schema": "factory-output-critic-circle-receipt-v1",
        "at": _now(),
        "law": str(cfg.get("law") or "docs/SOURCEA_FACTORY_OUTPUT_CRITIC_LOOP_LOCKED_v1.md"),
        "ok": improve_n == 0 and w3_pass and fleet_pass,
        "verdict": "PASS" if (improve_n == 0 and w3_pass) else "IMPROVE",
        "quality_bar_pct": OQG_BAR,
        "fleet_output_clean_now": fleet_now,
        "summary": {
            "artifacts": len(artifacts),
            "pass": pass_n,
            "improve": improve_n,
            "w3_all_pass": w3_pass,
            "fleet_lanes_pass": fleet_pass,
        },
        "loop": cfg.get("loop") or {},
        "ship_gate": cfg.get("ship_gate") or {},
        "artifacts": artifacts,
        "critic_circle_line": _line(improve_n, pass_n, fleet_now, w3_pass),
        "next_action_only": _pick_one_action(artifacts),
        "command": "python3 scripts/factory_output_critic_circle_v1.py --json",
    }

    if learn and improve_n:
        _append_incidents(artifacts)

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _line(improve_n: int, pass_n: int, fleet: int | None, w3_pass: bool) -> str:
    fleet_s = f"fleet{fleet}%" if fleet is not None else "fleet?"
    w3_bit = "w3=ready" if w3_pass else f"w3=improve({improve_n})"
    return f"critic · {w3_bit} · pass={pass_n} · {fleet_s} · bar={OQG_BAR}"


def _pick_one_action(artifacts: list[dict]) -> str:
    for art in artifacts:
        if art.get("verdict") == "IMPROVE":
            return str(art.get("next_action") or "re-run critic after one fix")
    return "all artifacts PASS bar — ship gates may still block (Mail FROM · confirm-sent)"


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "factory-output-critic-circle-receipt-v1":
        row = run_critic(write=True)
    return {
        "schema": "worker-hub-factory-output-critic-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "verdict": row.get("verdict"),
        "critic_circle_line": row.get("critic_circle_line"),
        "next_action_only": row.get("next_action_only"),
        "summary": row.get("summary"),
        "artifacts": row.get("artifacts") or [],
        "law": row.get("law"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Factory output critic circle")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--no-learn", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    row = run_critic(write=not args.no_write, learn=not args.no_learn)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("critic_circle_line", ""))
        print(row.get("next_action_only", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
