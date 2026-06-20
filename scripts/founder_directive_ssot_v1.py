#!/usr/bin/env python3
"""Founder directive SSOT — one read for every machine layer (ASF order > stale templates)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
LATCH = SINA / "worker-asf-directive-latch-v1.json"
ROUTING = SINA / "run-inbox-routing-v1.json"

HUB_PHASES = frozenset({"phase-s8-hub-ui-ux", "phase-s2-hub-build-ci"})
HUB_SA_MIN = 851
HUB_SA_MAX = 900


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_latch() -> dict:
    if not LATCH.is_file():
        return {}
    try:
        return json.loads(LATCH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def is_no_hub() -> bool:
    return bool(read_latch().get("no_hub"))


def is_plan_only() -> bool:
    return bool(read_latch().get("plan_only"))


def hub2_drain_allowed() -> bool:
    return bool(read_latch().get("hub2_drain_allowed"))


def command_retired_forever() -> bool:
    return bool(read_latch().get("command_retired_forever"))


def hub_closed() -> bool:
    """Sina Command archive closed — Hub 2 machine drain may still be allowed."""
    lat = read_latch()
    if hub2_drain_allowed():
        return bool(lat.get("no_hub_rebuild") or lat.get("no_hub_archive"))
    return bool(lat.get("no_hub") or lat.get("no_hub_rebuild") or lat.get("no_hub_archive"))


def execution_rail_line() -> str:
    if command_retired_forever() and hub2_drain_allowed():
        return "Hub only (H1/H2) · Sina Command RETIRED · factory drain phase-s8"
    if hub2_drain_allowed():
        return "Hub 2 machine drain (phase-s8) · Command DELETED · factory drain"
    if hub_closed():
        return "s7 → s9 research · Sina Command ARCHIVED (ASF closed — not open)"
    return "s7 → s9 (legacy s8 skipped)"


def is_hub_sa(sa_id: str, *, phase: str = "") -> bool:
    sid = (sa_id or "").strip().lower()
    if phase in HUB_PHASES:
        return True
    if sid.startswith("sa-"):
        try:
            n = int(sid.split("-", 1)[1])
            if HUB_SA_MIN <= n <= HUB_SA_MAX:
                return True
        except (ValueError, IndexError):
            pass
    return False


def _resolve_item_phase(sa_id: str, phase: str) -> str:
    """Fill missing phase from queue head when inject meta drifted (INCIDENT-031 hub2 drain)."""
    if phase:
        return phase
    try:
        from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

        qh = queue_head()
        if str(qh.get("sa_id") or "") == sa_id:
            return str(qh.get("phase") or "")
    except Exception:
        pass
    return ""


def block_hub_item(item: dict) -> tuple[bool, str]:
    sa = str(item.get("sa_id") or "")
    phase = _resolve_item_phase(sa, str(item.get("phase") or ""))
    if phase == "phase-s8-hub-ui-ux" and hub2_drain_allowed():
        return False, ""
    if not hub_closed() and not read_latch().get("no_hub"):
        return False, ""
    if is_hub_sa(sa, phase=phase):
        if phase == "phase-s8-hub-ui-ux":
            return True, f"sina_command_quarantine blocks {sa} — use Hub 2 drain latch"
        reason = f"hub_closed_latch blocks {sa} ({phase or 'hub range'})"
        return True, reason
    return False, ""


def _outbound_queue_active() -> bool:
    hq_path = SINA / "healthy-queue-30-active.json"
    if not hq_path.is_file():
        return False
    try:
        hq = json.loads(hq_path.read_text(encoding="utf-8"))
        phase = str(hq.get("phase") or "")
        product = str(hq.get("product") or "")
        thread = str(hq.get("thread") or "")
        return (
            "outbound-factory" in phase
            or product.startswith("Outbound Factory")
            or thread == "OUTBOUND-FACTORY"
        )
    except (OSError, json.JSONDecodeError):
        return False


def outbound_directive_note() -> str:
    hq_path = SINA / "healthy-queue-30-active.json"
    if not hq_path.is_file():
        return ""
    try:
        hq = json.loads(hq_path.read_text(encoding="utf-8"))
        queue = hq.get("queue") or []
        head = queue[0] if queue else {}
        uid = head.get("upgrade_id") or head.get("hp_id") or "?"
        sa = head.get("sa_id") or "?"
        cfg_path = SINA / "loop-specialist-config-v1.json"
        auto = False
        if cfg_path.is_file():
            try:
                auto = bool(json.loads(cfg_path.read_text(encoding="utf-8")).get("loop_auto_dispatch_enabled"))
            except (OSError, json.JSONDecodeError):
                auto = False
        if auto:
            return f"OUTBOUND FACTORY · {uid} · {sa} · LOOP AUTO · Brain work-order dispatch"
        return f"OUTBOUND FACTORY · {uid} · {sa} · Loop specialist deliver · ASF resume if FREEZE"
    except (OSError, json.JSONDecodeError):
        return ""


def directive_payload() -> dict:
    lat = read_latch()
    note = lat.get("note") or lat.get("plan_note") or ""
    if _outbound_queue_active():
        ob_note = outbound_directive_note()
        if ob_note:
            note = ob_note
    return {
        "schema": "founder-directive-ssot-v1",
        "at": _now(),
        "no_hub": bool(lat.get("no_hub")),
        "no_hub_rebuild": bool(lat.get("no_hub_rebuild")),
        "no_hub_archive": bool(lat.get("no_hub_archive")),
        "plan_only": bool(lat.get("plan_only")),
        "chat_first": bool(lat.get("chat_first")),
        "hub2_drain_allowed": bool(lat.get("hub2_drain_allowed")),
        "command_retired_forever": bool(lat.get("command_retired_forever")),
        "hub_status": (
            "COMMAND_RETIRED_FOREVER"
            if lat.get("command_retired_forever")
            else (
                "HUB2_DRAIN_ACTIVE"
                if lat.get("hub2_drain_allowed")
                else ("SINA_COMMAND_QUARANTINE" if hub_closed() else "unknown")
            )
        ),
        "execution_rail": execution_rail_line(),
        "note": note,
        "set_at": lat.get("set_at") or "",
        "incident": lat.get("incident") or "INCIDENT-031",
        "law": "ASF order propagates to every layer — not chat-only",
    }


def truth_block_lines() -> list[str]:
    d = directive_payload()
    if not (d.get("no_hub") or d.get("plan_only")):
        return []
    lines = ["═ FOUNDER DIRECTIVE (disk SSOT — every layer) ═"]
    if d.get("no_hub"):
        if d.get("command_retired_forever"):
            lines.append("Command: RETIRED FOREVER · Hub only (/) + (/machines/) · /legacy/ must not serve")
        elif d.get("hub2_drain_allowed"):
            lines.append("Sina Command: QUARANTINE · Hub 2 machine drain ACTIVE (phase-s8)")
        else:
            lines.append("Sina Command: ARCHIVED · CLOSED · not open · not rebuild · not refresh · zero hub sa")
    if d.get("plan_only"):
        lines.append("MODE: plan_only — answer founder before run inbox")
    lines.append(f"Rail: {d.get('execution_rail')}")
    if d.get("note"):
        lines.append(f"ASF: {d['note'][:160]}")
    lines.append("═ END FOUNDER DIRECTIVE ═")
    return lines


def heal_latch_outbound_note() -> dict:
    """Restore outbound SSOT note on latch — stop cascade validator ghost text."""
    if not _outbound_queue_active():
        return {"ok": True, "skipped": True, "reason": "not_outbound"}
    note = outbound_directive_note()
    if not note:
        return {"ok": False, "error": "no_outbound_note"}
    lat = read_latch()
    lat["note"] = note
    lat["outbound_healed_at"] = _now()
    LATCH.parent.mkdir(parents=True, exist_ok=True)
    LATCH.write_text(json.dumps(lat, indent=2) + "\n", encoding="utf-8")
    sync = sync_all_layers(stairlift=True)
    return {"ok": True, "note": note, "sync": sync}


def sync_routing_file() -> dict:
    """Rewrite run-inbox-routing order line when hub closed."""
    row = _read_json(ROUTING) if ROUTING.is_file() else {"schema": "run-inbox-routing-v1", "enabled": True}
    row["order"] = execution_rail_line()
    row["resume_sa"] = str((_read_json(SINA / "factory-now-v1.json")).get("queue_sa") or row.get("resume_sa") or "")
    row["hub_status"] = "ARCHIVED_CLOSED" if hub_closed() else row.get("hub_status")
    row["founder_directive_at"] = _now()
    ROUTING.parent.mkdir(parents=True, exist_ok=True)
    ROUTING.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def sync_all_layers(*, stairlift: bool = True) -> dict:
    """Push founder directive to routing · truth · stairlift payload."""
    routing = sync_routing_file()
    truth: dict = {}
    stair: dict = {"skipped": True}
    try:
        import sys
        from pathlib import Path as P

        scripts = P(__file__).resolve().parent
        sys.path.insert(0, str(scripts))
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        truth = write_truth(sync=True)
    except Exception as exc:
        truth = {"ok": False, "error": str(exc)}
    if stairlift:
        try:
            import subprocess
            import sys

            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parent / "governance_stairlift_sync_v1.py"), "--force", "--tier", "hot", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            stair = {"ok": proc.returncode == 0}
        except Exception as exc:
            stair = {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "schema": "founder-directive-sync-v1",
        "at": _now(),
        "directive": directive_payload(),
        "routing": routing,
        "truth": {"ok": bool(truth.get("at") or truth.get("queue"))},
        "stairlift": stair,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sync-all", action="store_true")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()
    if args.sync_all:
        row = sync_all_layers()
    else:
        row = directive_payload()
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
