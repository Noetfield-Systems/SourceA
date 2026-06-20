#!/usr/bin/env python3
"""Build Sina Daily Bowl — one unified morning read for ASF + agents."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
BOWL_DIR = SOURCE_A / "sina-bowl"
PROGRESS = SOURCE_A / "PROGRAM_PROGRESS.json"
MERGEPACK_PROGRESS = Path.home() / "Desktop/mergepack/PROGRAM_PROGRESS.json"
FLEET = SOURCE_A / "data/agent_fleet/AGENT_FLEET_REGISTRY.json"
ARCHITECT = SOURCE_A / "ARCHITECT_REPORT.yaml"
SCANNER = SOURCE_A / "scripts/scan-cursor-agent-fleet.py"


def load_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def architect_blockers(limit: int = 3) -> list[dict]:
    if not ARCHITECT.is_file():
        return []
    text = ARCHITECT.read_text(encoding="utf-8")
    blocks = []
    current = {}
    for line in text.splitlines():
        if line.strip().startswith("- id:"):
            if current.get("title"):
                blocks.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif "title:" in line and current:
            current["title"] = line.split(":", 1)[1].strip()
        elif "severity:" in line and current:
            current["severity"] = line.split(":", 1)[1].strip()
    if current.get("title"):
        blocks.append(current)
    return blocks[:limit]


def detect_drift(progress: dict, mp: dict | None) -> list[dict]:
    drift = []
    locks = progress.get("locks") or {}
    mp_plan = None
    for p in progress.get("parallel_plans") or []:
        if (p.get("id") or "").startswith("MERGEPACK"):
            mp_plan = p
            break
    if mp:
        mp_locks = mp.get("locks") or {}
        if locks.get("mergepack", "").startswith("parked"):
            drift.append(
                {
                    "id": "D-MP-1",
                    "severity": "high",
                    "title": "MergePack lock still says parked — use active_parallel",
                    "action": "ASF: locks.mergepack → active_parallel_l1_evidence_factory",
                }
            )
        if mp_plan and mp_plan.get("status") == "parked":
            drift.append(
                {
                    "id": "D-MP-2",
                    "severity": "high",
                    "title": "MERGEPACK plan status still parked",
                    "action": "ASF: plan status → active_parallel in PROGRAM_PROGRESS.json",
                }
            )
        if mp.get("version") == "1.3" and mp_plan and mp_plan.get("status") not in (
            "active_parallel",
            "active",
        ):
            drift.append(
                {
                    "id": "D-MP-3",
                    "severity": "medium",
                    "title": "mergepack repo v1.3 but SourceA plan not active_parallel",
                    "action": "Align parallel_plans MERGEPACK-L1",
                }
            )
    mp_plan_status = (mp_plan or {}).get("status") or ""
    mp_lock = locks.get("mergepack", "")
    mergepack_registry_lag = mp_plan and (
        mp_plan_status not in ("active_parallel", "active")
        or not str(mp_lock).startswith("active_parallel")
    )
    if mergepack_registry_lag:
        drift.append(
            {
                "id": "D-REG-1",
                "severity": "low",
                "title": "Thread registry may lag command center",
                "action": "Sync THREAD-MERGEPACK status in ASF_PROGRAM_THREADS_REGISTRY",
            }
        )
    return drift


def refresh_fleet() -> dict:
    if os.environ.get("SINA_SKIP_FLEET_SCAN", "").strip() in ("1", "true", "yes"):
        return load_json(FLEET) or {}
    if SCANNER.is_file():
        try:
            subprocess.run(
                ["python3", str(SCANNER)],
                cwd=str(SOURCE_A),
                check=False,
                capture_output=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            pass
    return load_json(FLEET) or {}


def build_state(progress: dict, fleet: dict, drift: list[dict], blockers: list[dict]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    locks = progress.get("locks") or {}
    plans = sorted(progress.get("parallel_plans") or [], key=lambda p: p.get("priority", 99))
    todos = [t for t in progress.get("todos", []) if t.get("status") == "open"]
    p0 = next((p for p in plans if p.get("priority") == 1), None)

    p0_hint = f"Confirm P0: {locks.get('p0_sku', '?')} — thread {locks.get('p0_thread', '?')}"
    fn: dict = {}
    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now() or {}
        line = str(fn.get("line") or "")
        if fn.get("kill_flag") or str(fn.get("mode")) == "FREEZE":
            p0_hint = f"FREEZE · tap Safety · {line}" if line else "FREEZE · tap Safety · bounded resume on ASF order"
        elif line:
            p0_hint = f"RUN INBOX when Brain routes · {line}"
    except Exception:
        pass

    asf_duties = [
        "Pick one active THREAD per Cursor chat today",
        "Resolve drift items below (you are the only law editor)",
        p0_hint,
        "Optional: 5 min — Worker Hub glance / read DAILY_BOWL.md",
        "If scope unclear: ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md",
    ]
    if any(d["severity"] == "high" for d in drift):
        asf_duties.insert(0, "Fix high drift before new features")

    roles = [
        {"id": "ASF", "line": "Final law, P0, registry — supervises all"},
        {"id": "ROLE-CURSOR-HQ", "line": "SinaaiDataBase chat — bowl, Source A, fleet, cross-repo locks"},
        {"id": "ROLE-ARCHITECT", "line": "Read-only blockers — run-architect.sh"},
        {"id": "ROLE-ORCHESTRATOR", "line": "SinaPromptOS — rank + dispatch five lanes"},
        {"id": "LANE-1..5", "line": "TrustField · Mono · VIRLUX · Noetfield · 777 — one task each"},
        {"id": "ROLE-WIRE", "line": "DevBridge — phone → Mac automation (M8)"},
        {"id": "PAIOS-4", "line": "Analyst · Brain · CoS · Operator — Super Brain"},
        {"id": "RUNTIME", "line": "Telegram workers on :8000 — not Cursor"},
    ]

    tier1 = [
        {"label": "Bowl spec", "path": "brain-os/law/SINA_DAILY_BOWL_LOCKED_v1.md"},
        {"label": "Command vision", "path": "SINA_COMMAND_CENTER_VISION_LOCKED_v1.md"},
        {"label": "Understanding roles", "path": "brain-os/law/UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md"},
        {"label": "Command center", "path": "ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md"},
        {"label": "Thread registry", "path": "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md"},
        {"label": "Source A start", "path": "brain-os/law/entry/README_SOURCE_A.md"},
        {"label": "Mono blueprint", "path": "../SinaaiMonoRepo/SinaaiDataBase/data/L0-meta/005-project-blueprint.md"},
        {"label": "Agent desk", "path": "agent-control-panel/index.html"},
    ]

    founder_p0 = "STRATEGIC-SLICE"
    try:
        cmd_path = SOURCE_A / "agent-control-panel" / "command-data.json"
        if cmd_path.is_file():
            cmd = load_json(cmd_path) or {}
            founder_p0 = (
                ((cmd.get("command_center") or {}).get("founder") or {}).get("p0") or {}
            ).get("id") or founder_p0
    except Exception:
        pass
    if fn.get("kill_flag") or str(fn.get("mode")) == "FREEZE":
        p0_brief = f"FREEZE · {founder_p0} · factory parallel {locks.get('p0_sku', '?')}"
    else:
        p0_brief = f"{founder_p0} · factory parallel {locks.get('p0_sku', '?')}"

    brief_lines = [
        f"Sina daily brief. Today P zero is {p0_brief}.",
        f"{len(drift)} drift alerts.",
        f"{len(blockers)} architect blockers.",
        f"{fleet.get('summary', {}).get('workspace_count', 0)} agent workspaces;",
        f"{fleet.get('summary', {}).get('active_sessions_24h', 0)} active in the last day.",
        "Worker Hub http://127.0.0.1:13020/ for optional queue glance.",
    ]

    return {
        "schema_version": 1,
        "generated_at": now,
        "p0": p0,
        "locks": locks,
        "parallel_plans": plans,
        "open_todos": todos,
        "drift": drift,
        "blockers": blockers,
        "fleet_summary": fleet.get("summary") or {},
        "fleet_workspaces": (fleet.get("workspaces") or [])[:8],
        "asf_duties": asf_duties,
        "roles_glance": roles,
        "tier1_links": tier1,
        "brief_text": " ".join(brief_lines),
        "brief_fa": build_farsi_brief(
            locks=locks,
            drift=drift,
            blockers=blockers,
            fleet_summary=fleet.get("summary") or {},
        ),
    }


# Persian-only audio brief — never mix Latin/English in this string (LOCKED for Sina).
P0_FA_LABELS: dict[str, str] = {
    "RunReceipt": "رسید اجرای عامل",
    "P0-RUNRECEIPT": "رسید اجرای عامل",
    "P0": "اولویت صفر",
}


def _fa_digits(n: int) -> str:
    return "".join("۰۱۲۳۴۵۶۷۸۹"[int(d)] for d in str(n))


def build_farsi_brief(
    *,
    locks: dict,
    drift: list,
    blockers: list,
    fleet_summary: dict,
) -> str:
    p0_key = str(locks.get("p0_sku") or "RunReceipt")
    p0_fa = P0_FA_LABELS.get(p0_key, "اولویت اصلی امروز")
    drift_n = len(drift)
    block_n = len(blockers)
    ws = int(fleet_summary.get("workspace_count") or 0)
    active = int(fleet_summary.get("active_sessions_24h") or 0)

    drift_clause = (
        f"{_fa_digits(drift_n)} هشدار انحراف برنامه."
        if drift_n
        else "بدون هشدار انحراف برنامه."
    )
    block_clause = (
        f"{_fa_digits(block_n)} مانع معماری."
        if block_n
        else "بدون مانع معماری."
    )

    lines = [
        "خلاصه روزانه سینا.",
        f"اولویت امروز: {p0_fa}.",
        drift_clause,
        block_clause,
        f"{_fa_digits(ws)} فضای کاری عامل؛ {_fa_digits(active)} مورد فعال در شبانه‌روز گذشته.",
        "برای جزئیات کامل، پنل فرمان سینا را روی لپتاپ باز کنید.",
    ]
    text = " ".join(lines)
    import re

    if re.search(r"[A-Za-z]", text):
        raise ValueError(f"Farsi brief must not contain English/Latin: {text!r}")
    return text


def render_markdown(state: dict) -> str:
    locks = state["locks"]
    lines = [
        "# Sina Daily Bowl",
        "",
        f"*Generated {state['generated_at']} — read this first every day.*",
        "",
        "## ASF today",
        "",
    ]
    for d in state["asf_duties"]:
        lines.append(f"- {d}")
    lines.extend(
        [
            "",
            "## P0 & locks",
            "",
            f"- **Founder P0:** {locks.get('founder_p0_id', 'STRATEGIC-SLICE')} · **Factory parallel:** {locks.get('p0_sku', '?')}",
            f"- **P0 thread:** {locks.get('p0_thread', '?')}",
            f"- **MergePack lock:** {locks.get('mergepack', '?')}",
            f"- **M8 meaning:** {locks.get('m8_meaning', '?')}",
            "",
            "## Drift (fix or ack)",
            "",
        ]
    )
    if state["drift"]:
        for d in state["drift"]:
            lines.append(f"- **[{d['severity']}]** {d['title']} → {d['action']}")
    else:
        lines.append("- *(none detected)*")
    lines.extend(["", "## Architect blockers (top 3)", ""])
    for b in state["blockers"]:
        lines.append(f"- **{b.get('id', '?')}** ({b.get('severity', '?')}): {b.get('title', '?')}")
    if not state["blockers"]:
        lines.append("- *(none parsed)*")
    lines.extend(["", "## Parallel plans", "", "| P | Plan | Status | Next |", "|---|------|--------|------|"])
    for p in state["parallel_plans"]:
        lines.append(
            f"| {p.get('priority', '')} | {p.get('id', '')} | {p.get('status', '')} | {p.get('next_action', '')[:60]} |"
        )
    lines.extend(["", "## Open todos", ""])
    for t in state["open_todos"][:12]:
        lines.append(f"- **{t.get('id')}** ({t.get('owner', '?')}): {t.get('text', '')}")
    if not state["open_todos"]:
        lines.append("- *(none)*")
    fs = state["fleet_summary"]
    lines.extend(
        [
            "",
            "## Fleet pulse",
            "",
            f"- Workspaces: **{fs.get('workspace_count', 0)}** · Sessions: **{fs.get('session_count', 0)}** · Active 24h: **{fs.get('active_sessions_24h', 0)}**",
            "",
            "## Roles at a glance",
            "",
        ]
    )
    for r in state["roles_glance"]:
        lines.append(f"- **{r['id']}:** {r['line']}")
    lines.extend(["", "## Tier-1 links (only if bowl is not enough)", ""])
    for link in state["tier1_links"]:
        lines.append(f"- {link['label']}: `{link['path']}`")
    lines.extend(["", "---", "", "*Full vision: `SINA_COMMAND_CENTER_VISION_LOCKED_v1.md`*", ""])
    return "\n".join(lines) + "\n"


def main() -> None:
    BOWL_DIR.mkdir(parents=True, exist_ok=True)
    progress = load_json(PROGRESS) or {}
    from mergepack_progress_read_v1 import read_mergepack_progress_safe

    mp_probe = read_mergepack_progress_safe()
    mp = mp_probe.get("data") if mp_probe.get("ok") else None
    fleet = refresh_fleet()
    drift = detect_drift(progress, mp)
    blockers = architect_blockers()
    state = build_state(progress, fleet, drift, blockers)
    (BOWL_DIR / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    (BOWL_DIR / "DRIFT.json").write_text(json.dumps(drift, indent=2), encoding="utf-8")
    (BOWL_DIR / "DAILY_BOWL.md").write_text(render_markdown(state), encoding="utf-8")
    (BOWL_DIR / "brief.txt").write_text(state["brief_text"], encoding="utf-8")
    fa_brief = state["brief_fa"]
    (BOWL_DIR / "brief.fa.txt").write_text(fa_brief, encoding="utf-8")
    print(f"OK: {BOWL_DIR}/DAILY_BOWL.md")
    print(f"Drift items: {len(drift)}")
    export_orders = SOURCE_A / "scripts/export-master-orders-json.py"
    if export_orders.is_file():
        subprocess.run(["python3", str(export_orders)], check=False, cwd=SOURCE_A)
    if os.environ.get("SINA_SKIP_PANEL_BUILD", "").strip() not in ("1", "true", "yes"):
        panel = SOURCE_A / "scripts/build-sina-command-panel.py"
        if panel.is_file():
            subprocess.run(["python3", str(panel)], check=False, cwd=SOURCE_A)
    else:
        print("OK: skip nested panel build — SINA_SKIP_PANEL_BUILD=1 (sa-0222)")


if __name__ == "__main__":
    main()
