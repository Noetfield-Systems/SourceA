#!/usr/bin/env python3
"""Judge Center L2 Counsel — settle alarms vs disk · draft form forks.

TRACE: SINA_JUDGE_STACK_DRAFT_v1.md L2 · Q-JUDGE-STACK-v1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JUDGE_DIR = Path.home() / ".sina/judge-center"
COUNSEL_DIR = JUDGE_DIR / "counsel"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_form() -> dict:
    raw = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--json"],
        text=True,
    )
    return json.loads(raw)


def _disk_truth(form: dict) -> dict:
    policy = str(form.get("hub_repair_policy") or "").upper()
    return {
        "open_questions_count": int(form.get("open_questions_count") or 0),
        "canvas_open_count": int(form.get("canvas_open_count") or 0),
        "awaiting_founder_picks": bool(form.get("awaiting_founder_picks")),
        "no_autorun": "NO CURSOR AUTO-RUN" in policy or "NO AUTO-RUN" in policy,
        "rt_live": "RT LIVE PASS" in policy,
    }


def _settle_alarm(alarm: dict, disk: dict, chat_id: str) -> dict:
    code = str(alarm.get("code") or "")
    tag = str(alarm.get("tag") or "")

    if code in ("false_sidebar_success", "scratch_canvas_path", "scratch_canvas_risk"):
        return {
            "outcome": "ESCALATE_INCIDENT",
            "class": "BAD",
            "resolution": "INCIDENT-029 class — chat claimed form UI without M1 Canvas proof",
            "form_action": "Q-M2-029 YES",
        }

    if code in ("incident_027_class", "incident_028_class"):
        inc = "027" if "027" in code else "028"
        return {
            "outcome": "ESCALATE_INCIDENT",
            "class": "BAD",
            "resolution": f"INCIDENT-{inc} conduct — hub/chat projection drift",
            "form_action": f"Q-M2-{inc} YES" if inc == "029" else "Q-M2-FORM-SYNC YES",
        }

    if code == "autorun_p0_stale" and disk["no_autorun"]:
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": "Chat AUTO-RUN hero is stale — form 2.03 A + Q-RT-LIVE YES + kill_flag win",
            "form_action": None,
        }

    if code == "governance_complete_stale" and disk["awaiting_founder_picks"]:
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": f"Governance not complete — {disk['open_questions_count']} form rows await Canvas PICK",
            "form_action": "Q-M2-FORM-SYNC YES",
        }

    if code == "tracker_as_ssot_stale":
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": "Master Tracker is map only — form JSON + founder_open win picks",
            "form_action": None,
        }

    if code == "rail_a_hero_stale" and disk["no_autorun"]:
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": "Rail A AUTO-RUN hero rejected — ENFORCE W1+W3 per 9.07 A",
            "form_action": None,
        }

    if code == "open_count_claim" and alarm.get("tag") == "STALE":
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": f"Chat count wrong — disk open_questions_count={disk['open_questions_count']}",
            "form_action": None,
        }

    if code == "open_count_match":
        return {
            "outcome": "SETTLED_ANSWERED",
            "class": "RIGHT",
            "resolution": "Open count matches form JSON",
            "form_action": None,
        }

    if tag == "UNPROVEN" and code == "no_alarm_match":
        return {
            "outcome": "ESCALATE_BENCH",
            "class": "UNPROVEN",
            "resolution": "No pattern hit — manual specialist audit or extend L1 patterns",
            "form_action": None,
        }

    if tag == "STALE":
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": alarm.get("excerpt", "stale vs disk")[:160],
            "form_action": None,
        }

    if tag == "BAD":
        return {
            "outcome": "ESCALATE_INCIDENT",
            "class": "BAD",
            "resolution": alarm.get("excerpt", "bad conduct")[:160],
            "form_action": "Q-M2-029 YES",
        }

    return {
        "outcome": "ESCALATE_BENCH",
        "class": tag or "UNPROVEN",
        "resolution": alarm.get("excerpt", "needs bench review")[:160],
        "form_action": None,
    }


def counsel_packet(packet: dict, form: dict, disk: dict) -> dict:
    settlements: list[dict] = []
    escalations: list[dict] = []
    for alarm in packet.get("alarms") or []:
        row = _settle_alarm(alarm, disk, str(packet.get("chat_id") or ""))
        row["alarm"] = alarm
        if row["outcome"].startswith("SETTLED"):
            settlements.append(row)
        else:
            escalations.append(row)

    tags = {s["class"] for s in settlements + escalations}
    settle_outcomes = {s["outcome"] for s in settlements}
    bad_codes = {
        str((e.get("alarm") or {}).get("code") or "")
        for e in escalations
        if e.get("outcome") == "ESCALATE_INCIDENT"
    }
    conduct_only = bad_codes.issubset({"incident_027_class", "incident_028_class", "scratch_canvas_path", "false_sidebar_success", "scratch_canvas_risk"})
    if "BAD" in tags and conduct_only and any(s.get("outcome") == "SETTLED_STALE" for s in settlements):
        overall = "STALE"
    elif "BAD" in tags:
        overall = "BAD"
    elif "STALE" in tags or "SETTLED_STALE" in settle_outcomes:
        overall = "STALE"
    elif settlements and not escalations:
        overall = "RIGHT"
    elif escalations and all(e["class"] == "UNPROVEN" for e in escalations):
        overall = "UNPROVEN"
    else:
        overall = "STALE" if settlements else "UNPROVEN"

    temporal = packet.get("temporal") or {}
    temporal_overall = str(temporal.get("overall") or "")
    if temporal_overall == "TRUSTED":
        overall = "RIGHT"
    elif temporal_overall == "PAST_STALE_ONLY":
        overall = "PAST_STALE_ONLY"  # trust recent; no remediation
    elif temporal_overall in ("ACTIVE_STALE", "REVERT"):
        overall = "ACTIVE_STALE"
    elif temporal_overall == "ACTIVE_BAD":
        overall = "BAD"

    keep_using: list[str] = []
    ignore: list[str] = []
    role = str(packet.get("role") or "")
    if "commercial" in role:
        keep_using = ["market comps", "W3 SKU", "honest $0", "three-layer v2"]
        ignore = ["Jun 8–9 AUTO-RUN hero", "tracker as pick SSOT"]
    elif "governance" in role:
        keep_using = ["entity/money firewall", "W3-CONTRACT-GATE", "authority map vault"]
        ignore = ["Jun 8–9 AUTO-RUN live proof thread"]

    return {
        "chat_id": packet.get("chat_id"),
        "role": role,
        "transcript": packet.get("transcript"),
        "audit_tag": packet.get("tag"),
        "archaeology_tag": packet.get("archaeology_tag"),
        "temporal": packet.get("temporal"),
        "overall": overall,
        "settlements": settlements,
        "escalations": escalations,
        "keep_using": keep_using,
        "ignore_stale": ignore,
    }


def build_counsel(audit: dict) -> dict:
    form = _load_form()
    disk = _disk_truth(form)
    briefs = [counsel_packet(p, form, disk) for p in audit.get("packets") or []]
    case_id = f"JC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    return {
        "schema": "judge-center-counsel-v1",
        "case_id": case_id,
        "counselled_at": _now(),
        "audit_ref": audit.get("audited_at"),
        "disk_truth": disk,
        "form_open_count": disk["open_questions_count"],
        "briefs": briefs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge Center L2 counsel")
    parser.add_argument("--packet", help="Path to audit JSON file")
    parser.add_argument("--latest", action="store_true", help="Use last line of cases.jsonl")
    parser.add_argument("--out", help="Write counsel brief path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.latest:
        cases_path = JUDGE_DIR / "cases.jsonl"
        if not cases_path.is_file():
            print("FAIL: no cases.jsonl", file=sys.stderr)
            return 1
        audit = json.loads(cases_path.read_text(encoding="utf-8").strip().splitlines()[-1])
    elif args.packet:
        audit = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    else:
        print("FAIL: --packet or --latest required", file=sys.stderr)
        return 1

    brief = build_counsel(audit)
    COUNSEL_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else COUNSEL_DIR / f"{brief['case_id']}.json"
    out_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (JUDGE_DIR / "latest-counsel-v1.json").write_text(
        json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if args.json:
        print(json.dumps(brief, indent=2))
    else:
        for b in brief["briefs"]:
            print(f"{b['chat_id']}: {b['overall']} ({b['role']})")
        print(f"WROTE {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
