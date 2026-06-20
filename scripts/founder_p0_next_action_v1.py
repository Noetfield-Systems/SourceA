#!/usr/bin/env python3
"""SSOT: founder Hub p0.next_action — no Cursor AUTO-RUN promotion (INCIDENT-022 / AS-01)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

FORBIDDEN_PATTERNS = (
    r"auto-run",
    r"auto run",
    r"start auto",
    r"goal 1 auto-run",
    r"▶\s*start",
    r"kill\s*#6",
    r"hub\s+track",
    r"refresh\s+hub\s+track",
)

# INCIDENT-027 — drain headline on hub hero when form filled + RT LIVE gate open
DRAIN_HEADLINE_PATTERNS = (
    r"worker inbox",
    r"valid yes \d+/\d+",
    r"queue \d+/\d+",
    r"resume drain",
    r"bounded resume",
    r"check · sa-",
    r"pick sa-\d{4}",
)

RT_LIVE_GATE_OPEN_COPY = (
    "Hub repair-only · RT LIVE gate OPEN · FR-003 wired · "
    "Safety guard active · factory background only"
)
RT_LIVE_GATE_PASS_COPY = (
    "ENFORCEMENT W1 film · W3 NF outreach (9.07 A) · FR-003 wired · Phase 3 resume — "
    "RT LIVE PASS · Safety guard active · factory background only"
)


def _scripts_path() -> None:
    p = str(SCRIPTS)
    if p not in sys.path:
        sys.path.insert(0, p)


def _forbidden(text: str) -> bool:
    low = (text or "").lower()
    return any(re.search(pat, low, re.I) for pat in FORBIDDEN_PATTERNS)


def _drain_headline(text: str) -> bool:
    low = (text or "").lower()
    return any(re.search(pat, low, re.I) for pat in DRAIN_HEADLINE_PATTERNS)


def rt_live_gate_active() -> bool:
    """Form v2 filled + hub repair until RT LIVE (Q-RT-LIVE YES) — INCIDENT-027 latch."""
    try:
        from live_founder_decision_form_v1 import payload  # noqa: WPS433

        form = payload()
    except Exception:
        return False
    if not (form.get("v2_answers") or {}).get("filled"):
        return False
    if int(form.get("open_questions_count") or 0) > 0:
        return False
    policy = str(form.get("hub_repair_policy") or "").upper()
    headline = str(form.get("form_headline") or "").upper()
    return "RT LIVE" in policy or "RT LIVE" in headline


def build_founder_p0_next_action(
    *,
    queue_brief: str | None = None,
    live_pick_id: str | None = None,
    live_pick_title: str | None = None,
) -> str:
    """Single builder for command_center.founder.p0.next_action."""
    _scripts_path()

    try:
        from live_founder_decision_form_v1 import payload  # noqa: WPS433

        form = payload()
    except Exception:
        form = {}

    oq = int(form.get("open_questions_count") or 0)
    if oq > 0:
        headline = str(
            form.get("form_headline")
            or f"{oq} open PICKs · FORM on disk · INCIDENT-037 block ON"
        ).strip()
        out = f"{headline} · Safety guard"
        if _forbidden(out) or _drain_headline(out):
            out = f"{oq} OPEN QUESTIONS — M1 Canvas Pending confirmations · Safety check"
        return out

    # Law beats projection — form filled → RT LIVE owns hub hero (INCIDENT-027)
    if rt_live_gate_active():
        try:
            from rt_live_gate_v1 import sync_gate_state  # noqa: WPS433

            sync_gate_state()
        except Exception:
            pass
        try:
            from rt_live_gate_v1 import receipt_pass  # noqa: WPS433

            out = RT_LIVE_GATE_PASS_COPY if receipt_pass() else RT_LIVE_GATE_OPEN_COPY
        except Exception:
            out = RT_LIVE_GATE_OPEN_COPY
        if _forbidden(out):
            raise ValueError(f"founder_p0_next_action produced forbidden copy: {out[:120]!r}")
        if _drain_headline(out):
            raise ValueError(f"founder_p0_next_action RT LIVE path leaked drain: {out[:120]!r}")
        return out

    from factory_control_v1 import load_factory_now  # noqa: WPS433

    fn = load_factory_now()
    valid_yes = int(fn.get("valid_yes") or 0)
    total = 1000
    freeze = bool(fn.get("kill_flag")) or str(fn.get("mode") or "FREEZE") == "FREEZE"
    brief = (queue_brief or "").strip()
    if not brief and fn.get("queue_sa"):
        brief = f"sa-{fn.get('queue_sa')}" if not str(fn.get("queue_sa")).startswith("sa-") else str(fn.get("queue_sa"))

    if freeze:
        parts = [f"FREEZE · Valid YES {valid_yes}/{total}"]
        if brief:
            parts.append(brief)
        parts.append("Safety guard active · bounded resume on ASF order only")
        out = " · ".join(parts)
    elif brief:
        out = (
            f"Factory: RUN INBOX when Brain routes · {brief} · "
            f"Safety guard active · Brain sync if red"
        )
    elif live_pick_id:
        title = (live_pick_title or "See SOURCEA-PRIORITY.md")[:72]
        out = (
            f"Live pick: {live_pick_id} — {title} · "
            f"Hub Actions only · Cursor automation rejected"
        )
    else:
        out = (
            f"Valid YES {valid_yes}/{total} · Safety guard active · Brain sync · "
            f"Cursor AUTO-RUN rejected"
        )

    queue_sa = str(fn.get("queue_sa") or "").strip()
    if queue_sa and not queue_sa.startswith("sa-"):
        queue_sa = f"sa-{queue_sa}"
    pick = queue_sa or str(live_pick_id or "").strip()
    if pick.startswith("sa-") and pick not in out:
        out = f"{out} · pick {pick}"

    if _forbidden(out):
        raise ValueError(f"founder_p0_next_action produced forbidden copy: {out[:120]!r}")
    return out


def _open_questions_headline_active() -> bool:
    try:
        from live_founder_decision_form_v1 import payload  # noqa: WPS433

        return int(payload().get("open_questions_count") or 0) > 0
    except Exception:
        return False


def validate_next_action(text: str) -> tuple[bool, str]:
    """Machine check for validators."""
    na = str(text or "").strip()
    if not na:
        return False, "empty next_action"
    if _forbidden(na):
        return False, f"forbidden AUTO-RUN pattern in: {na[:96]!r}"
    if _open_questions_headline_active():
        upper = na.upper()
        if _drain_headline(na) or re.search(r"sa-\d{4}", na, re.I):
            return False, f"open questions active but drain/sa headline present: {na[:96]!r}"
        if not any(tok in upper for tok in ("OPEN QUESTIONS", "QUESTIONS · FORM", "M1 CANVAS", "PENDING CONFIRMATIONS")):
            return False, f"open questions active but missing form/Canvas headline: {na[:96]!r}"
        return True, "ok"
    if rt_live_gate_active():
        if "RT LIVE" not in na.upper():
            return False, f"RT LIVE gate open but next_action missing RT LIVE: {na[:96]!r}"
        if _drain_headline(na) or re.search(r"sa-\d{4}", na, re.I):
            return False, f"RT LIVE gate open but drain/sa headline present: {na[:96]!r}"
        if "SAFETY" not in na.upper():
            return False, f"RT LIVE gate open but missing Safety: {na[:96]!r}"
        try:
            from rt_live_gate_v1 import receipt_pass  # noqa: WPS433

            if receipt_pass() and re.search(r"prove\s+cascade", na, re.I):
                return False, f"RT LIVE receipt PASS but hero still says prove cascade: {na[:96]!r}"
        except Exception:
            pass
        return True, "ok"
    if not any(
        tok in na.upper()
        for tok in ("FREEZE", "RUN INBOX", "VALID YES", "LIVE PICK", "SAFETY", "CURSOR AUTO-RUN REJECTED")
    ):
        return False, f"missing required founder signal tokens: {na[:96]!r}"
    return True, "ok"


def main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="Build or validate founder P0 next_action")
    p.add_argument("--queue-brief", default="")
    p.add_argument("--live-pick-id", default="")
    p.add_argument("--live-pick-title", default="")
    p.add_argument("--validate", default="", help="Validate existing string instead of build")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.validate:
        ok, msg = validate_next_action(args.validate)
        out = {"ok": ok, "message": msg, "text": args.validate}
    else:
        text = build_founder_p0_next_action(
            queue_brief=args.queue_brief or None,
            live_pick_id=args.live_pick_id or None,
            live_pick_title=args.live_pick_title or None,
        )
        ok, msg = validate_next_action(text)
        out = {"ok": ok, "message": msg, "next_action": text}

    if args.json or True:
        print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
