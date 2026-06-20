#!/usr/bin/env python3
"""Audit enforcement-1000 pack vs disk — categorize, mark done, write report."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os" / "plan-registry" / "enforcement-1000"
REG = PACK / "REGISTRY.json"
REPORT = PACK / "AUDIT_REPORT_v1.json"
INDEX = ROOT / "brain-os" / "plan-registry" / "ENFORCEMENT-1000-CATEGORY-INDEX.md"

PHASE_TO_CATEGORY = {
    "phase-e0-commit-gate": "W2_KERNEL",
    "phase-e1-receipt-integrity": "W2_KERNEL",
    "phase-e2-validator-tamper": "W2_KERNEL",
    "phase-e3-demo-live": "W1_DEMO",
    "phase-e4-commercial-w3": "W3_MONEY",
    "phase-e5-bypass-chaos": "CHAOS_HARDEN",
    "phase-e6-investor-pipeline": "NARRATIVE",
    "phase-e7-regulated-wedge": "W3_MONEY",
    "phase-e8-kernel-harden": "W2_KERNEL",
    "phase-e9-dec-closeout": "CLOSEOUT",
}

PHASE_TO_OWNER = {
    "phase-e0-commit-gate": "worker",
    "phase-e1-receipt-integrity": "worker",
    "phase-e2-validator-tamper": "worker",
    "phase-e3-demo-live": "worker",
    "phase-e4-commercial-w3": "commercial",
    "phase-e5-bypass-chaos": "worker",
    "phase-e6-investor-pipeline": "commercial",
    "phase-e7-regulated-wedge": "commercial",
    "phase-e8-kernel-harden": "worker",
    "phase-e9-dec-closeout": "brain",
}

PHASE_TO_MONTH = {
    "phase-e0-commit-gate": "2026-06",
    "phase-e1-receipt-integrity": "2026-06",
    "phase-e2-validator-tamper": "2026-07",
    "phase-e3-demo-live": "2026-07",
    "phase-e4-commercial-w3": "2026-06",
    "phase-e5-bypass-chaos": "2026-08",
    "phase-e6-investor-pipeline": "2026-09",
    "phase-e7-regulated-wedge": "2026-08",
    "phase-e8-kernel-harden": "2026-10",
    "phase-e9-dec-closeout": "2026-12",
}

SLICE_BY_PHASE_SLOT: dict[str, dict[int, str]] = {
    "phase-e0-commit-gate": {0: "DEMO-ENF-S9", 2: "DEMO-ENF-S2", 3: "DEMO-ENF-S2", 4: "DEMO-ENF-S2", 5: "DEMO-ENF-S3"},
    "phase-e1-receipt-integrity": {0: "DEMO-ENF-S3", 2: "DEMO-ENF-S4", 5: "DEMO-ENF-S4"},
    "phase-e2-validator-tamper": {0: "DEMO-ENF-S5", 1: "DEMO-ENF-S5", 2: "DEMO-ENF-S5"},
    "phase-e3-demo-live": {0: "DEMO-ENF-S7", 2: "DEMO-ENF-S7", 5: "DEMO-ENF-S8", 6: "DEMO-ENF-S8"},
    "phase-e4-commercial-w3": {9: "DEMO-ENF-W3", 17: "DEMO-ENF-W3"},
}


def _exists(rel: str) -> bool:
    return (ROOT / rel).is_file()


def _validator_ok(script: str, extra: list[str] | None = None) -> bool:
    cmd = ["bash", str(ROOT / "scripts" / script)] + (extra or [])
    try:
        return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, timeout=120).returncode == 0
    except Exception:
        return False


def disk_done_t0_slots() -> set[tuple[str, int]]:
    """(phase, slot) pairs proven in the repository — T0 only."""
    done: set[tuple[str, int]] = set()
    demo_ok = _validator_ok("validate-demo-enforcement-v1.sh")
    tamper_ok = demo_ok and _validator_ok("validate-demo-enforcement-v1.sh", ["--tamper-test"])
    universe_ok = _validator_ok("validate-universe-invariants-v1.sh")

    if _exists("brain-os/demo/governance_demo_policy_v1.json") and _exists(
        "brain-os/demo/governance_demo_intents_v1.json"
    ):
        done.add(("phase-e0-commit-gate", 4))
        done.add(("phase-e0-commit-gate", 5))
    if _exists("scripts/commit_intent_v1.py"):
        done.add(("phase-e0-commit-gate", 2))
    if _exists("scripts/sourcea_execute_v1.py"):
        done.add(("phase-e0-commit-gate", 3))
    if _exists("brain-os/demo/DEMO_BYPASS_AUDIT_v1.md"):
        done.add(("phase-e0-commit-gate", 0))
    if _exists("scripts/governance_demo_gate_v1.py"):
        done.add(("phase-e0-commit-gate", 10))
    if demo_ok:
        for s in range(0, 15):
            done.add(("phase-e2-validator-tamper", s))
        done.add(("phase-e1-receipt-integrity", 0))
        done.add(("phase-e1-receipt-integrity", 5))
    if tamper_ok:
        done.add(("phase-e2-validator-tamper", 0))
        done.add(("phase-e2-validator-tamper", 9))
    if universe_ok:
        done.add(("phase-e2-validator-tamper", 3))
    if _exists("scripts/demo-enforcement-5min-v1.sh"):
        done.add(("phase-e3-demo-live", 4))
        done.add(("phase-e3-demo-live", 5))
    if _exists("investor/ENFORCEMENT_DEMO_5MIN.md"):
        done.add(("phase-e3-demo-live", 0))
    if _exists("brain-os/demo/INVESTOR_DEMO_RUNBOOK_v1.md"):
        done.add(("phase-e3-demo-live", 15))
    if _exists("investor/ENFORCEMENT_3SLIDE_DECK_v1.md"):
        done.add(("phase-e4-commercial-w3", 5))
    if _exists("investor/ENFORCEMENT_OUTREACH_v1.md"):
        done.add(("phase-e4-commercial-w3", 6))
    return done


def plan_id_for(phase: str, tier: str, slot: int, phases: list[str], tiers: list[str]) -> str:
    p_idx = phases.index(phase)
    t_idx = tiers.index(tier)
    seq = p_idx * 100 + t_idx * 25 + slot + 1
    return f"enf-{seq:04d}"


def main() -> int:
    if not REG.is_file():
        print("Missing REGISTRY — run generate-enforcement-1000-prompts.py first")
        return 1

    data = json.loads(REG.read_text(encoding="utf-8"))
    plans = data.get("plans") or []
    phases = [p["id"] for p in data.get("phases") or []]
    tiers = [t["id"] for t in data.get("tiers") or []]
    if not phases:
        phases = list(PHASE_TO_CATEGORY.keys())
    if not tiers:
        tiers = ["T0", "T1", "T2", "T3"]

    t0_done_slots = disk_done_t0_slots()
    marked = 0
    for pl in plans:
        phase = pl.get("phase", "")
        tier = pl.get("tier", "")
        slot = int(pl.get("slot") or 0)
        pl["category"] = PHASE_TO_CATEGORY.get(phase, "UNKNOWN")
        pl["owner"] = PHASE_TO_OWNER.get(phase, "worker")
        pl["month"] = PHASE_TO_MONTH.get(phase, "2026-12")
        pl["slice_ref"] = SLICE_BY_PHASE_SLOT.get(phase, {}).get(slot, "")
        pl["win"] = {"W2_KERNEL": "W2", "W1_DEMO": "W1", "W3_MONEY": "W3"}.get(
            pl["category"], pl["category"]
        )

        should_done = tier == "T0" and (phase, slot) in t0_done_slots
        if should_done and pl.get("status") != "done":
            pl["status"] = "done"
            pl["disk_proven"] = True
            marked += 1
            pid = pl["id"]
            path = PACK / pl["path"]
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                if "status: backlog" in text:
                    path.write_text(text.replace("status: backlog", "status: done", 1), encoding="utf-8")

    by_cat = Counter(p.get("category") for p in plans)
    by_owner = Counter(p.get("owner") for p in plans)
    by_status = Counter(p.get("status") for p in plans)
    by_month = Counter(p.get("month") for p in plans)
    by_tier = Counter(p.get("tier") for p in plans)

    unique_titles = len({p.get("title") for p in plans})
    data["plans"] = plans
    data["audited_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["categories"] = {
        cat: {"count": by_cat[cat], "owner": PHASE_TO_OWNER.get(
            next((ph for ph, c in PHASE_TO_CATEGORY.items() if c == cat), ""), "mixed"
        )}
        for cat in sorted(by_cat)
    }
    data["audit_summary"] = {
        "unique_titles": unique_titles,
        "done": by_status.get("done", 0),
        "backlog": by_status.get("backlog", 0),
        "disk_marked_this_run": marked,
        "validators": {
            "demo": _validator_ok("validate-demo-enforcement-v1.sh"),
            "tamper": _validator_ok("validate-demo-enforcement-v1.sh", ["--tamper-test"]),
            "universe": _validator_ok("validate-universe-invariants-v1.sh"),
        },
    }
    REG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    report = {
        "audited_at": data["audited_at"],
        "by_category": dict(by_cat),
        "by_owner": dict(by_owner),
        "by_status": dict(by_status),
        "by_month": dict(by_month),
        "by_tier": dict(by_tier),
        "unique_titles": unique_titles,
        "disk_t0_done_slots": [f"{a}:{b}" for a, b in sorted(t0_done_slots)],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# ENFORCEMENT-1000 — Category index (audited)",
        "",
        f"**Audited:** {data['audited_at']}",
        f"**Unique titles:** {unique_titles} / 1000",
        f"**Done:** {by_status.get('done', 0)} · **Backlog:** {by_status.get('backlog', 0)}",
        "",
        "## Win buckets",
        "",
        "| Category | Count | Owner | Win | Months |",
        "|----------|-------|-------|-----|--------|",
    ]
    cat_months: dict[str, set[str]] = defaultdict(set)
    for pl in plans:
        cat_months[pl.get("category", "")].add(pl.get("month", ""))
    for cat in sorted(by_cat):
        sample_phase = next(ph for ph, c in PHASE_TO_CATEGORY.items() if c == cat)
        win = {"W2_KERNEL": "W2", "W1_DEMO": "W1", "W3_MONEY": "W3"}.get(cat, cat)
        months = ", ".join(sorted(cat_months[cat]))
        lines.append(
            f"| `{cat}` | {by_cat[cat]} | {PHASE_TO_OWNER.get(sample_phase, '')} | {win} | {months} |"
        )

    lines += [
        "",
        "## Tier depth (all 1000)",
        "",
        "| Tier | Count | Role |",
        "|------|-------|------|",
    ]
    tier_role = {
        "T0": "Ship — demo blocker",
        "T1": "CI + evidence",
        "T2": "Chaos / stress",
        "T3": "Polish or DELETE",
    }
    for t in ["T0", "T1", "T2", "T3"]:
        lines.append(f"| `{t}` | {by_tier[t]} | {tier_role[t]} |")

    lines += [
        "",
        "## Phase map",
        "",
        "| Phase | IDs | Category |",
        "|-------|-----|----------|",
    ]
    for i, ph in enumerate(phases):
        start = i * 100 + 1
        end = start + 99
        lines.append(
            f"| `{ph}` | enf-{start:04d}…enf-{end:04d} | {PHASE_TO_CATEGORY.get(ph, '')} |"
        )

    v = data["audit_summary"]["validators"]
    lines += [
        "",
        "## Disk validators",
        "",
        f"- validate-demo-enforcement: **{'PASS' if v['demo'] else 'FAIL'}**",
    ]
    lines.append(f"- tamper test: **{'PASS' if v['tamper'] else 'FAIL'}**")
    lines.append(f"- universe invariants: **{'PASS' if v['universe'] else 'FAIL'}**")
    lines += [
        "",
        "## Pick next",
        "",
        "```bash",
        "python3 scripts/pick-enforcement-no-asf-plan.py --any-tier --limit 3 --prompt",
        "```",
        "",
        "Regenerate: `python3 scripts/generate-enforcement-1000-prompts.py`",
        "Re-audit: `python3 scripts/audit-enforcement-1000-v1.py`",
    ]
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"OK: audit-enforcement-1000 — done={by_status.get('done',0)} backlog={by_status.get('backlog',0)}")
    print(f"    unique_titles={unique_titles} disk_marked={marked}")
    print(f"    report → {REPORT}")
    print(f"    index  → {INDEX}")
    for cat, n in sorted(by_cat.items()):
        print(f"    {cat}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
