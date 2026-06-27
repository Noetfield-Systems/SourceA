#!/usr/bin/env python3
"""Execution path vocabulary SSOT — Brain work-order vs legacy Worker INBOX.

Law: docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md · brain-cloud-reasoning B0501
All founder-facing execution lines should import from here (not duplicate).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SINA = Path.home() / ".sina"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def loop_auto_on() -> bool:
    return bool(_read(SINA / "loop-specialist-config-v1.json").get("loop_auto_dispatch_enabled"))


def post_outbound_complete() -> bool:
    try:
        import sys
        from pathlib import Path as P

        root = P(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from outbound_factory_phase_complete_v1 import outbound_plan_progress  # noqa: WPS433

        return bool(outbound_plan_progress().get("complete"))
    except Exception:
        return False


def post_outbound_smart_loop_active() -> bool:
    return loop_auto_on() and post_outbound_complete()


def _research_depth_block() -> str | None:
    """U058 — surface research checklist block without founder tap."""
    try:
        import sys
        from pathlib import Path as P

        root = P(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from outbound_research_checklist_v1 import check_research_depth_signoff  # noqa: WPS433

        blocked = [a for a in ("fundmore", "ocree") if check_research_depth_signoff(a).get("blocked")]
        if blocked:
            return f"U058:{','.join(blocked)}"
    except Exception:
        pass
    return None


def commercial_l3_blocker_summary() -> str:
    """Short L3 blocker line from commercial-command-pulse SSOT."""
    pulse = _read(SINA / "commercial-command-pulse-v1.json")
    if not pulse:
        return "L3 ?"
    pct = int(pulse.get("l3_ready_pct") or 0)
    if pct >= 100 and not _research_depth_block():
        return "L3 100% ready"
    parts: list[str] = []
    for acct in pulse.get("accounts") or []:
        blockers = acct.get("blockers") or []
        if blockers:
            aid = str(acct.get("id") or "?")
            parts.append(f"{aid}:{','.join(blockers[:2])}")
    u058 = _research_depth_block()
    if u058:
        parts.append(u058)
    line = f"L3 {pct}%"
    if parts:
        line += " · " + " · ".join(parts[:4])
    return line


def commercial_smart_loop_line() -> str:
    base = "Auto Runtime ON · commercial smart loop owns L3 prep · Hub glance only"
    if post_outbound_smart_loop_active():
        block = commercial_l3_blocker_summary()
        if block and not block.endswith("100% ready"):
            return f"{base} · {block}"
    return base


def brain_work_order_primary() -> bool:
    if not loop_auto_on():
        return False
    hq = _read(SINA / "healthy-queue-30-active.json")
    phase = str(hq.get("phase") or "")
    product = str(hq.get("product") or "")
    thread = str(hq.get("thread") or "")
    outbound = (
        "outbound-factory" in phase
        or product.startswith("Outbound Factory")
        or thread == "OUTBOUND-FACTORY"
    )
    if not outbound:
        return False
    active = _read(SINA / "brain-outbound-work-order-active-v1.json")
    if active.get("execution_mode") == "brain_work_order":
        return True
    try:
        import sys
        from pathlib import Path as P

        root = P(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from brain_outbound_work_order_v1 import brain_work_order_enabled  # noqa: WPS433

        return bool(brain_work_order_enabled())
    except Exception:
        return outbound


def _forge_factory_era() -> bool:
    try:
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from factory_control_v1 import _load_factory_era  # noqa: WPS433

        return (_load_factory_era().get("current_era") or "") == "forge_factory_cycle2"
    except Exception:
        return False


def founder_daily_ops_line() -> str:
    if _forge_factory_era():
        return "FORGE FACTORY cycle2 · Auto Runtime · cloud execute · Hub glance only"
    if post_outbound_smart_loop_active():
        return commercial_smart_loop_line()
    if loop_auto_on():
        if brain_work_order_primary():
            return "Auto Runtime · Brain work-order dispatch · Hub glance only"
        return "Auto Runtime specialist · Brain work-order · Hub glance only"
    return "Auto Runtime specialist tick on Hub · ASF resume Cloud Forge Run if FREEZE"


def factory_motion_line() -> str:
    if brain_work_order_primary():
        return "Auto Runtime specialist · Brain work-order dispatch when pending"
    if loop_auto_on():
        return "Auto Runtime specialist · Auto Runtime dispatch when pending"
    return "Brain routes · Worker implements bounded disk work"


def execute_line() -> str:
    if post_outbound_smart_loop_active():
        return commercial_smart_loop_line()
    if brain_work_order_primary():
        return "Auto Runtime ON · Brain work-order dispatch · Hub glance only"
    if loop_auto_on():
        return "Auto Runtime ON · Auto Runtime specialist dispatch when pending"
    return "Auto Runtime specialist delivers · ASF resume Cloud Forge Run if FREEZE"


def live_disk_header() -> str:
    if brain_work_order_primary():
        return "LIVE DISK (wins over old chat — Brain work-order primary)"
    return "LIVE DISK (wins over old chat — bounded Worker turn when routed)"


def run_inbox_check_label() -> str:
    if brain_work_order_primary():
        return "Auto Runtime · Brain work-order dispatch"
    if loop_auto_on():
        return "Auto Runtime · Auto Runtime specialist dispatch"
    return "Worker bounded turn · one sa/turn"


def founder_motion_line(*, goal1_idle: bool = False) -> str:
    if _forge_factory_era():
        return "FORGE FACTORY cycle2 · Auto Runtime · Hub glance · commercial P0 parallel"
    if goal1_idle and post_outbound_smart_loop_active():
        return commercial_smart_loop_line()
    if goal1_idle:
        return "Goal 1 idle · Hub glance · commercial P0"
    if brain_work_order_primary():
        return "Auto Runtime · Brain work-order · Hub glance"
    if loop_auto_on():
        return "Auto Runtime · Auto Runtime specialist · Hub glance"
    return "Auto Runtime specialist tick · Hub glance"


def inject_execution_path() -> str:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from fbe.lib.hub_cloud_proxy_v1 import execution_mode  # noqa: WPS433

        if execution_mode() == "CLOUD_ONLY":
            ongoing = _read(SINA / "live-ongoing-prompts-next-10-v1.json")
            if ongoing.get("execution_surface") == "cloud_forge":
                head = (ongoing.get("cloud_forge_glance") or {}).get("head") or "Railway"
                return f"cloud_forge CF cron */10 · head {head} · Mac observes only"
    except Exception:
        pass
    if _forge_factory_era():
        return "FORGE FACTORY cycle2 · healthy-queue-30-active.json · brain work-order + Auto Runtime"
    if brain_work_order_primary():
        return "brain work-order dispatch + Auto Runtime"
    return "run inbox + live-ongoing-prompts-next-10-v1.json"


def founder_close_line() -> str:
    return founder_daily_ops_line().rstrip(".") + "."


def queue_founder_line(*, sa: str, role: str, pos: int, total: int, inbox_pending: bool = False) -> str:
    base = f"{sa} · {role.upper()} · {pos}/{total}"
    if brain_work_order_primary():
        if inbox_pending:
            return f"INBOX stale · {base} · Brain work-order dispatch"
        active = _read(SINA / "brain-outbound-work-order-active-v1.json")
        ref = active.get("upgrade_ref") or "?"
        return f"{base} · Auto Runtime · Brain work-order · head={ref}"
    if loop_auto_on():
        return f"{base} · Auto Runtime · Auto Runtime specialist dispatch"
    return f"{base} · Worker bounded turn when Brain routes"
