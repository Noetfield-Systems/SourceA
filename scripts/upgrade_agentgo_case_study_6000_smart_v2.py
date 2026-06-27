#!/usr/bin/env python3
"""Upgrade AgentGo case-study 6000 to v2 — pure · unique · smart tasks (preserves status)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCEA_ROOT / "scripts"))

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

UPGRADE_VERSION = 2


def prompt_md_v2(
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
) -> str:
    angle_key = angle["key"]
    verify = ANGLE_CTX[angle_key]["verify"]
    return f"""# {plan_id} — AgentGo SA4 case study plan (v2 smart)

**Version:** 2 · **Tier:** {tier} · **Phase:** {phase}
**Angle:** {angle['angle_code']} · {angle['label']}
**Theme:** {theme_id} · {theme_label}
**Workstream:** {ws_id} · {ws_label}
**Slice:** {slice_n}/{SLICES_PER_CELL} · **Receipt gate:** {receipt_gate}
**SSOT:** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md`

## Scope

{angle['story']}

## Task

{task}

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
generator: upgrade_agentgo_case_study_6000_smart_v2.py v{UPGRADE_VERSION}
angle: {angle_key}
smart: pure-unique-smart
"""


def upgrade_angle(angle: dict, now: str) -> dict:
    pack = PACK_BASE / angle["key"]
    reg_path = pack / "REGISTRY.json"
    if not reg_path.is_file():
        raise SystemExit(f"Missing {reg_path}")

    old_reg = json.loads(reg_path.read_text(encoding="utf-8"))
    old_by_id = {p["id"]: p for p in old_reg.get("plans", [])}

    entries: list[dict] = []
    phases: list[dict] = []
    seq = 0

    for theme_id, theme_label in THEMES:
        phase_id = f"phase-{angle['prefix']}-{theme_id}"
        phases.append(
            {
                "id": phase_id,
                "theme": theme_label,
                "description": f"{angle['label']} — {theme_label}",
            }
        )
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
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = pack / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    prompt_md_v2(
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
                    ),
                    encoding="utf-8",
                )
                prev = old_by_id.get(plan_id, {})
                entries.append(
                    {
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
                        "smart_version": UPGRADE_VERSION,
                        "unique_key": f"{angle['key']}:{theme_id}:{ws_id}:{slice_n}",
                    }
                )
                if prev.get("closed_at"):
                    entries[-1]["closed_at"] = prev["closed_at"]
                if prev.get("close_reason"):
                    entries[-1]["close_reason"] = prev["close_reason"]

    titles = [e["title"] for e in entries]
    if len(titles) != len(set(titles)):
        dupes = len(titles) - len(set(titles))
        raise SystemExit(f"FAIL: {angle['key']} has {dupes} duplicate titles")

    registry = {
        "schema": "agentgo-case-study-6000-registry-v1",
        "schema_version": UPGRADE_VERSION,
        "smart_tier": "pure-unique-smart",
        "generated_at": now,
        "upgraded_at": now,
        "upgrade_script": "scripts/upgrade_agentgo_case_study_6000_smart_v2.py",
        "angle": angle["key"],
        "angle_label": angle["label"],
        "count": len(entries),
        "grid": "10 themes × 10 workstreams × 20 slices",
        "external_repo": angle["external_repo"],
        "phases": phases,
        "plans": entries,
    }
    reg_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"angle": angle["key"], "count": len(entries), "unique_titles": len(set(titles))}


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    for angle in ANGLES:
        results.append(upgrade_angle(angle, now))

    master_path = SOURCEA_ROOT / "brain-os" / "plan-registry" / "AGENTGO_CASE_STUDY_6000_MASTER_v1.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    master["schema_version"] = "2.0.0"
    master["smart_tier"] = "pure-unique-smart"
    master["upgraded_at"] = now
    master["upgrade_script"] = "scripts/upgrade_agentgo_case_study_6000_smart_v2.py"
    master_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    manifest_path = SOURCEA_ROOT / "data" / "agentgo-case-study-6000-manifest-v1.json"
    manifest_path.write_text(json.dumps(master, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "upgraded_at": now, "angles": results, "plan_count": 6000}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
