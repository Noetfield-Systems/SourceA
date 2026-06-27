#!/usr/bin/env python3
"""Polish AgentGo case-study 6000 to v3 — thoughtful details · inventory receipt · bootstrap."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCEA_ROOT / "scripts"))

from lib.agentgo_polish_wisdom_v3 import wisdom_for  # noqa: E402
from lib.agentgo_smart_tasks_v2 import ANGLE_CTX, build_smart_task  # noqa: E402
from generate_agentgo_case_study_6000_plans_v1 import (  # noqa: E402
    ANGLES,
    PACK_BASE,
    SLICES_PER_CELL,
    THEMES,
    TIER_FOR_SLICE,
    WORKSTREAMS,
    phase_for_rank,
    receipt_gate_for,
)

POLISH_VERSION = 3
SA4 = Path.home() / "Desktop" / "YA5" / "SA4"
CASE_STUDY = SOURCEA_ROOT / "SourceA-landing/green-unified/case-studies/agentgo.html"
INVENTORY_PATH = SOURCEA_ROOT / "data/agentgo-sa4-inventory-receipt-v1.json"
RECEIPT_PATH = Path.home() / ".sina/agentgo-case-study-receipt-v1.json"


def _count_html(root: Path) -> int:
    if not root.is_dir():
        return 0
    try:
        out = subprocess.run(
            ["find", str(root), "-name", "*.html"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return len([ln for ln in out.stdout.splitlines() if ln.strip()])
    except (subprocess.TimeoutExpired, OSError):
        return 0


def _dir_count(root: Path) -> int:
    if not root.is_dir():
        return 0
    return sum(1 for p in root.iterdir() if p.is_dir())


def build_inventory_receipt(now: str) -> dict:
    trackers = list(SA4.glob("*-visibility-tracker")) + list(SA4.glob("*-tracker"))
    trackers = [p for p in trackers if p.is_dir()]
    inv = {
        "schema": "agentgo-sa4-inventory-receipt-v1",
        "version": "1.0.0",
        "generated_at": now,
        "sa4_root": str(SA4),
        "symlink": str(Path.home() / "Desktop/SA4"),
        "counts": {
            "html_pages": _count_html(SA4),
            "research_topics": _dir_count(SA4 / "research"),
            "compare_pages": _dir_count(SA4 / "compare"),
            "guide_topics": _dir_count(SA4 / "guides"),
            "tracker_landings": len(trackers),
            "blog_posts": _dir_count(SA4 / "blog"),
        },
        "tracker_samples": sorted(p.name for p in trackers)[:12],
        "ok": SA4.is_dir(),
    }
    INVENTORY_PATH.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "agentgo-case-study-receipt-v1",
        "version": "1.0.0",
        "saved_at": now,
        "case_study_html": str(CASE_STUDY),
        "case_study_shipped": CASE_STUDY.is_file(),
        "inventory": str(INVENTORY_PATH),
        "inventory_counts": inv["counts"],
        "polish_version": POLISH_VERSION,
        "ok": CASE_STUDY.is_file() and inv["ok"],
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return inv


def prompt_md_v3(
    *,
    plan_id: str,
    angle: dict,
    theme_id: str,
    theme_label: str,
    ws_id: str,
    ws_label: str,
    slice_n: int,
    tier: str,
    phase: str,
    title: str,
    task: str,
    receipt_gate: str,
    wisdom: str | None,
    seq: int,
) -> str:
    angle_key = angle["key"]
    verify = ANGLE_CTX[angle_key]["verify"]
    wisdom_block = f"\n## Polish wisdom (v3)\n\n{wisdom}\n" if wisdom else ""
    return f"""# {plan_id} — AgentGo SA4 case study plan (v3 polished)

**Version:** 3 · **Tier:** {tier} · **Phase:** {phase} · **Rank:** {seq}
**Angle:** {angle['angle_code']} · {angle['label']}
**Theme:** {theme_id} · {theme_label}
**Workstream:** {ws_id} · {ws_label}
**Slice:** {slice_n}/{SLICES_PER_CELL} · **Receipt gate:** {receipt_gate}
**SSOT:** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md`
**Inventory:** `data/agentgo-sa4-inventory-receipt-v1.json`

## Scope

{angle['story']}

## Task

{task}
{wisdom_block}
## Verify

```bash
{verify}
```

## Closeout

1. `status: done` in REGISTRY.json for `{plan_id}`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md` §AgentGo case study 6000
3. No cross-lane edits without EDIT ALLOWED
4. Keep AgentGo ≠ SourceA separation in all buyer-facing copy (angle C law)

---
agent_tag: {angle['agent']}
trigger: PLAN WITH NO ASF
generator: polish_agentgo_case_study_v3.py v{POLISH_VERSION}
angle: {angle_key}
smart: pure-unique-smart-polished
"""


def should_bootstrap_done(plan: dict, *, case_study: bool, inventory: bool) -> bool:
    if plan.get("status") == "done":
        return False
    gate = plan.get("receipt_gate", "none")
    theme = plan.get("theme", "")
    if case_study and theme == "t02-landing-ship" and plan.get("workstream") == "w01-ship":
        if plan.get("slice", 99) <= 5:
            return True
    if case_study and theme == "t01-case-copy" and plan.get("workstream") == "w01-ship":
        if plan.get("slice", 99) <= 3:
            return True
    if inventory and theme == "t04-sa4-source" and plan.get("workstream") == "w02-prove":
        if plan.get("slice", 99) <= 2:
            return True
    if gate == "landing_ship" and case_study:
        return plan.get("slice", 99) <= 2 and theme == "t02-landing-ship"
    return False


def polish_angle(angle: dict, now: str, *, case_study: bool, inventory: bool) -> dict:
    pack = PACK_BASE / angle["key"]
    reg_path = pack / "REGISTRY.json"
    old_reg = json.loads(reg_path.read_text(encoding="utf-8"))
    old_by_id = {p["id"]: p for p in old_reg.get("plans", [])}

    entries: list[dict] = []
    phases: list[dict] = []
    seq = 0
    bootstrapped = 0

    for theme_id, theme_label in THEMES:
        phase_id = f"phase-{angle['prefix']}-{theme_id}"
        phases.append({"id": phase_id, "theme": theme_label, "description": f"{angle['label']} — {theme_label}"})
        for ws_id, ws_label in WORKSTREAMS:
            for slice_n in range(1, SLICES_PER_CELL + 1):
                seq += 1
                plan_id = f"{angle['prefix']}-{seq:04d}"
                tier = TIER_FOR_SLICE[slice_n - 1]
                phase = phase_for_rank(seq)
                receipt_gate = receipt_gate_for(angle["key"], theme_id, ws_id, slice_n)
                title, task = build_smart_task(
                    angle["key"], theme_id, theme_label, ws_id, ws_label, slice_n, tier, phase
                )
                wisdom = wisdom_for(angle["key"], seq)
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = pack / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    prompt_md_v3(
                        plan_id=plan_id,
                        angle=angle,
                        theme_id=theme_id,
                        theme_label=theme_label,
                        ws_id=ws_id,
                        ws_label=ws_label,
                        slice_n=slice_n,
                        tier=tier,
                        phase=phase,
                        title=title,
                        task=task,
                        receipt_gate=receipt_gate,
                        wisdom=wisdom,
                        seq=seq,
                    ),
                    encoding="utf-8",
                )
                prev = old_by_id.get(plan_id, {})
                entry = {
                    "id": plan_id,
                    "angle": angle["key"],
                    "angle_code": angle["angle_code"],
                    "angle_label": angle["label"],
                    "theme": theme_id,
                    "theme_label": theme_label,
                    "workstream": ws_id,
                    "workstream_label": ws_label,
                    "slice": slice_n,
                    "tier": tier,
                    "phase": phase,
                    "title": title,
                    "status": prev.get("status", "open"),
                    "receipt_gate": receipt_gate,
                    "priority_rank": seq,
                    "path": rel,
                    "lane": angle["lane"],
                    "agent_prompt": f"PLAN WITH NO ASF — {plan_id}: {title}",
                    "smart_version": POLISH_VERSION,
                    "polish_wisdom": wisdom,
                    "unique_key": f"{angle['key']}:{theme_id}:{ws_id}:{slice_n}",
                }
                if prev.get("closed_at"):
                    entry["closed_at"] = prev["closed_at"]
                if prev.get("close_reason"):
                    entry["close_reason"] = prev["close_reason"]
                if should_bootstrap_done(entry, case_study=case_study, inventory=inventory):
                    entry["status"] = "done"
                    entry["closed_at"] = now
                    entry["close_reason"] = "polish_v3_bootstrap"
                    bootstrapped += 1
                entries.append(entry)

    titles = [e["title"] for e in entries]
    if len(titles) != len(set(titles)):
        raise SystemExit(f"FAIL: {angle['key']} duplicate titles after polish")

    registry = {
        "schema": "agentgo-case-study-6000-registry-v1",
        "schema_version": POLISH_VERSION,
        "smart_tier": "pure-unique-smart-polished",
        "generated_at": old_reg.get("generated_at"),
        "upgraded_at": old_reg.get("upgraded_at"),
        "polished_at": now,
        "polish_script": "scripts/polish_agentgo_case_study_v3.py",
        "angle": angle["key"],
        "angle_label": angle["label"],
        "count": len(entries),
        "grid": "10 themes × 10 workstreams × 20 slices",
        "external_repo": angle["external_repo"],
        "inventory_receipt": "data/agentgo-sa4-inventory-receipt-v1.json",
        "phases": phases,
        "plans": entries,
    }
    reg_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"angle": angle["key"], "count": len(entries), "bootstrapped": bootstrapped}


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    inv = build_inventory_receipt(now)
    case_study = CASE_STUDY.is_file()
    inventory = inv.get("ok", False)

    results = []
    total_boot = 0
    for angle in ANGLES:
        r = polish_angle(angle, now, case_study=case_study, inventory=inventory)
        results.append(r)
        total_boot += r["bootstrapped"]

    master_path = SOURCEA_ROOT / "brain-os/plan-registry/AGENTGO_CASE_STUDY_6000_MASTER_v1.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    master["schema_version"] = "3.0.0"
    master["smart_tier"] = "pure-unique-smart-polished"
    master["polished_at"] = now
    master["polish_script"] = "scripts/polish_agentgo_case_study_v3.py"
    master["inventory_receipt"] = "data/agentgo-sa4-inventory-receipt-v1.json"
    master["inventory_counts"] = inv.get("counts", {})
    master_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    manifest_path = SOURCEA_ROOT / "data/agentgo-case-study-6000-manifest-v1.json"
    manifest_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "polished_at": now,
                "inventory": inv.get("counts"),
                "case_study_shipped": case_study,
                "bootstrapped": total_boot,
                "angles": results,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
