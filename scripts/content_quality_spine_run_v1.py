#!/usr/bin/env python3
"""Run shared content-quality spine proof — pre-generation/pre-send firewall only.

Usage:
  python3 scripts/content_quality_spine_run_v1.py --proof --json
  python3 scripts/content_quality_spine_run_v1.py --artifact ivr_receptionist --file draft.md --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SPINE = ROOT / "data" / "content-quality-spine"
SINA = Path.home() / ".sina"
RUNTIME_RECEIPT = SPINE / "CONTENT_QUALITY_RUNTIME_RECEIPT_v1.json"

sys.path.insert(0, str(SCRIPTS))
from content_quality_spine_core_v1 import run_spine  # noqa: E402

PROOF_FIXTURES = {
    "ivr_receptionist_good": {
        "artifact_type": "ivr_receptionist",
        "domain_pack": "automotive",
        "evidence": {
            "capability_state": "LOOKUP_AND_REQUEST",
            "terminal_outcome": "appointment_requested",
            "calendar_lookup": True,
        },
        "draft": """**Receptionist:** Parkside Auto Care. How can I help?

**Caller:** My brakes are making a grinding noise.

**Receptionist:** Understood. What vehicle is it?

**Caller:** A 2019 Ford Escape.

**Receptionist:** Has the braking performance changed, or are you mainly hearing the noise?

**Caller:** Mainly the noise.

**Receptionist:** What time would work best for you?

**Caller:** Tomorrow morning.

**Receptionist:** I'll ask the shop to confirm the earliest morning opening. May I have your name and number?

**Caller:** Kevin Walsh — six oh four, eight one seven, two two nine oh.

**Receptionist:** Thanks, Kevin. The shop will call or text with availability. If the braking changes or feels unsafe, avoid driving until it has been assessed.

**Receptionist:** You're welcome. Goodbye.""",
    },
    "commercial_film_good": {
        "artifact_type": "commercial_film",
        "domain_pack": "general_SMB",
        "evidence": {},
        "draft": """VO: Your agents execute right now. Who stops the one that goes too far?

VO: SourceA puts policy, BLOCK, and receipt on every loop — before spend, send, or deploy.

VO: Book a fifteen-minute proof. See the gate logged, not in a slide deck.""",
    },
    "email_good": {
        "artifact_type": "email",
        "domain_pack": "general_SMB",
        "lane": "w3_canada",
        "evidence": {},
        "draft": """Subject: Ocree — one question on controlled agent loops

Hi Sarah,

Teams like yours are shipping faster with agent loops — and one bad send can erase the win.

We built a checker that blocks architecture jargon and unsupported claims before anything leaves draft.

Would a 15-minute walkthrough of the receipt trail be useful this week?

Sina
Reply **stop** to opt out.""",
    },
    "landing_copy_good": {
        "artifact_type": "landing_page",
        "domain_pack": "general_SMB",
        "evidence": {},
        "draft": """Controlled agentic automation for teams that cannot afford a bad send.

Policy runs before spend. Every loop leaves a receipt you can audit.

Book a 15-minute proof — see BLOCK logged, not in a deck.""",
    },
}

CANARY_BAD = {
    "ivr_drive_safe_after_brakes": {
        "artifact_type": "ivr_receptionist",
        "domain_pack": "automotive",
        "evidence": {},
        "draft": """**Receptionist:** Auto shop. How can I help?
**Caller:** Grinding brakes when I stop.
**Receptionist:** Drive safe and we'll call you back.""",
    },
    "email_invented_personalization": {
        "artifact_type": "email",
        "domain_pack": "general_SMB",
        "lane": "w3_canada",
        "evidence": {},
        "draft": """Subject: Following up on your Q3 board review

Hi Jordan,

I loved your keynote at Acme Summit last week about neural orchestration meshes.

We've been spending time with teams like yours who need receipt-native governance at scale.

Would you be open to a 30-minute architecture deep dive plus a demo of our Supabase edge pipeline?

Also book here, schedule here, and reply with your budget.

Best,
Sina""",
    },
}


def _write_runtime_receipt(payload: dict) -> None:
    SPINE.mkdir(parents=True, exist_ok=True)
    RUNTIME_RECEIPT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Content quality spine runner")
    ap.add_argument("--proof", action="store_true", help="Run four-artifact proof bundle")
    ap.add_argument("--canaries", action="store_true", help="Run calibration bad-pattern canaries")
    ap.add_argument("--artifact", help="Artifact adapter key")
    ap.add_argument("--file", help="Draft text file")
    ap.add_argument("--domain", default="general_SMB")
    ap.add_argument("--lane", default="w3_canada")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results: dict = {"runs": [], "canaries": []}

    if args.proof or (not args.artifact and not args.file):
        for name, fix in PROOF_FIXTURES.items():
            row = run_spine(
                artifact_type=fix["artifact_type"],
                draft=fix["draft"],
                domain_pack=fix.get("domain_pack", "general_SMB"),
                evidence=fix.get("evidence"),
                lane=fix.get("lane", "w3_canada"),
                metadata={"fixture": name, "proof": True},
            )
            results["runs"].append({"fixture": name, "result": row})

    if args.canaries or args.proof:
        for name, fix in CANARY_BAD.items():
            row = run_spine(
                artifact_type=fix["artifact_type"],
                draft=fix["draft"],
                domain_pack=fix.get("domain_pack", "general_SMB"),
                evidence=fix.get("evidence"),
                lane=fix.get("lane", "w3_canada"),
                metadata={"canary": name},
            )
            results["canaries"].append(
                {
                    "canary": name,
                    "expected": "QUARANTINED",
                    "got": row["final_artifact"]["status"],
                    "passed": row["final_artifact"]["status"] == "QUARANTINED",
                    "result": row,
                }
            )

    if args.artifact and args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        row = run_spine(
            artifact_type=args.artifact,
            draft=text,
            domain_pack=args.domain,
            lane=args.lane,
        )
        results["runs"].append({"fixture": args.file, "result": row})

    proof_ok = all(r["result"]["final_artifact"]["status"] == "APPROVED" for r in results.get("runs", []))
    canary_ok = all(c["passed"] for c in results.get("canaries", []))
    results["summary"] = {
        "audited_head_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "proof_artifacts": len(results.get("runs", [])),
        "proof_all_approved": proof_ok,
        "canaries_run": len(results.get("canaries", [])),
        "canaries_caught_bad": canary_ok,
        "status": "SHARED_QUALITY_SPINE_PROVEN" if proof_ok and canary_ok else "SHARED_QUALITY_SPINE_PARTIAL",
    }

    _write_runtime_receipt(results)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(results["summary"]["status"])
    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
