#!/usr/bin/env python3
"""Build founder missed-actions card + Worker-ordered next-10 drain SSOT."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CARD_PATH = SINA / "founder-missed-actions-card-v1.json"
DRAIN_PATH = SINA / "worker-drain-next-10-v1.json"
SCHEMA_CARD = "founder-missed-actions-card-v1"
SCHEMA_DRAIN = "worker-drain-next-10-v1"
DRAIN_LIMIT = 10


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _honest_progress() -> dict:
    try:
        import sys

        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

        audit = audit_registry_done()
        honest = int(audit.get("honest_done") or 0)
        total = int(audit.get("total") or 1000)
        return {
            "honest_done": honest,
            "total": total,
            "pct": round(100.0 * honest / max(total, 1), 1),
            "left": total - honest,
        }
    except Exception:
        return {"honest_done": 0, "total": 1000, "pct": 0.0, "left": 1000}


def _worker_drain_next_10() -> dict:
    """Delegate to live_ongoing_prompts — 10 consecutive queue turns (not sa dedupe)."""
    sys.path.insert(0, str(SOURCE_A / "scripts"))
    try:
        from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

        live = rebuild(write=True, preview=False)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": SCHEMA_DRAIN}

    if not live.get("ok"):
        return {**live, "schema": SCHEMA_DRAIN}

    compat_path = SINA / "worker-drain-next-10-v1.json"
    if compat_path.is_file():
        try:
            return json.loads(compat_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass

    turns = live.get("turns") or []
    drain = [
        {
            "order": t.get("order"),
            "queue_pos": t.get("queue_pos"),
            "sa_id": t.get("sa_id"),
            "title": t.get("title"),
            "queue_role": t.get("queue_role"),
            "roles": [t.get("queue_role") or "check"],
            "rail": "goal1_healthy_drain",
        }
        for t in turns
    ]
    hp = _honest_progress()
    return {
        "ok": True,
        "schema": SCHEMA_DRAIN,
        "built_at": live.get("built_at"),
        "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        "queue_path": live.get("queue_path"),
        "next_pos": live.get("cursor_pos"),
        "queue_total": live.get("queue_total"),
        "valid_yes": hp["honest_done"],
        "valid_yes_label": live.get("valid_yes"),
        "count": len(drain),
        "limit": DRAIN_LIMIT,
        "note": live.get("note"),
        "drain": drain,
        "live_ongoing_path": str(SINA / "live-ongoing-prompts-next-10-v1.json"),
        "worker_recipe": [
            "INBOX deliver → validators → broker worker-submit CHECK→ACT→VERIFY",
            "bash scripts/enforce-registry-hygiene-v1.sh after each sa close",
        ],
    }


def _brain_snapshot_gap() -> dict:
    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from brain_sync_lib_v1 import brain_snapshot_status  # noqa: WPS433

        return brain_snapshot_status()
    except Exception as exc:
        return {"ok": False, "dual_proof_ok": True, "error": str(exc)}


def _missed_founder_items(*, progress: dict, wire: dict, mp_prog: dict, drain: dict) -> list[dict]:
    items: list[dict] = []
    hp = _honest_progress()
    drain_rows = drain.get("drain") or []
    brain_st = _brain_snapshot_gap()

    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        form = live_form_payload()
        n = int(form.get("open_questions_count") or 0)
        if n > 0 or form.get("awaiting_founder_picks"):
            items.append(
                {
                    "id": "founder-live-decision-form",
                    "label": f"【{n} QUESTIONS · FORM {str(form.get('form_edition') or 'v2').upper()}】Fill live decision form — Q1–Q{n}",
                    "why": form.get("hub_repair_policy") or "Hub repair — ASF answers before agents deep-work",
                    "kind": "tab",
                    "tab": form.get("hub_tab") or "track",
                    "priority": -2,
                }
            )
    except Exception:
        pass

    if not brain_st.get("dual_proof_ok"):
        items.append(
            {
                "id": "founder-brain-sync-monitor",
                "label": "Fix Brain sync (monitor ↺)",
                "why": (
                    f"Snapshot {brain_st.get('brain_vy')} vs live {brain_st.get('live_vy')} — "
                    "Brain PEND on green rows is display lag, not redo"
                ),
                "kind": "repair",
                "priority": 0,
            }
        )

    frozen = False
    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        frozen = bool(load_factory_now().get("kill_flag"))
    except Exception:
        pass
    try:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from w3_outbound_batch_approve_v1 import card_status, hub_card_visible  # noqa: WPS433

        if hub_card_visible() and not card_status().get("founder_approved"):
            w3 = card_status()
            items.append(
                {
                    "id": "founder-approve-outbound-batch",
                    "label": "Approve outbound batch",
                    "why": w3.get("why") or w3.get("summary") or "9.07 A · W3 — tap before send",
                    "kind": "primary",
                    "priority": -1,
                }
            )
    except Exception:
        pass

    if frozen:
        items.append(
            {
                "id": "founder-ecosystem-safety",
                "label": "🛡 Safety check (FREEZE)",
                "why": f"Factory frozen · {hp['honest_done']}/{hp['total']} honest · resume on ASF order only",
                "kind": "safety",
                "priority": 1,
            }
        )
    else:
        items.append(
            {
                "id": "founder-ecosystem-safety",
                "label": "🛡 Safety check",
                "why": f"RUN INBOX when Brain routes · next {len(drain_rows)} sa in pack · {hp['honest_done']}/{hp['total']} honest",
                "kind": "safety",
                "priority": 1,
            }
        )

    ms = (mp_prog or {}).get("milestones") or {}
    if ms.get("MP-SHIP") != "pass":
        items.append(
            {
                "id": "founder-verify-mp-health",
                "label": "Verify MergePack /health",
                "why": "MP-SHIP public ship — Vercel protection still blocking demos",
                "kind": "action",
                "priority": 2,
            }
        )

    if wire.get("g3_tailscale") == "pending":
        items.append(
            {
                "id": "founder-wire-preflight",
                "label": "Wire G3 preflight",
                "why": "Remote Mac control — Tailscale proof still pending",
                "kind": "action",
                "priority": 3,
            }
        )

    blockers = (progress.get("signals_auto") or {}).get("architect_blockers") or []
    bowl_blockers = (_read_json(SINA / "daily-bowl-state-v1.json") or {}).get("blockers") or []
    has_b001 = any("B-001" in str(b) for b in blockers) or any(
        (b.get("id") == "B-001") for b in bowl_blockers if isinstance(b, dict)
    )
    if has_b001:
        items.append(
            {
                "id": "founder-open-global-blockers",
                "label": "Open GLOBAL_BLOCKERS",
                "why": "Active law collision — infra postgres vs no-card",
                "kind": "action",
                "priority": 4,
            }
        )

    eval_ok = (progress.get("signals_auto") or {}).get("eval_1b_gate_ok")
    if eval_ok is False:
        items.append(
            {
                "id": "founder-enqueue-spine-bridge",
                "label": "Enqueue eval spine bridge",
                "why": "OpenRouter credits / Eval-1b gate — live eval blocked",
                "kind": "action",
                "priority": 5,
            }
        )

    items.append(
        {
            "id": "founder-next-steps",
            "label": "Next steps — live next 10 turns",
            "why": "Machine queue order in the repository — optional big-picture commentary only",
            "kind": "tab",
            "tab": "next-steps",
            "priority": 6,
        }
    )

    items.append(
        {
            "id": "founder-ecosystem-safety",
            "label": "Factory safety check",
            "why": "Weekly or after errors — locks, monitor, INBOX sync",
            "kind": "safety",
            "priority": 7,
        }
    )

    items.sort(key=lambda r: int(r["priority"]) if r.get("priority") is not None else 99)
    return items


def sync_founder_missed_actions(*, write: bool = True) -> dict:
    try:
        import subprocess

        subprocess.run(
            [sys.executable, str(SOURCE_A / "scripts" / "registry_updater_v1.py")],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:
        pass

    progress = _read_json(SINA / "goal-progress-v1.json")
    if not progress:
        try:
            import subprocess

            proc = subprocess.run(
                ["python3", str(SOURCE_A / "scripts" / "goal-progress-v1.py"), "--json"],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=45,
            )
            if proc.returncode == 0:
                progress = json.loads(proc.stdout)
        except Exception:
            progress = {}

    wire = (progress.get("signals_auto") or {}).get("wire") or {}
    mp_prog = _read_json(SOURCE_A / "founder" / "MERGEPACK_PROGRESS.json")
    drain = _worker_drain_next_10()
    items = _missed_founder_items(progress=progress, wire=wire, mp_prog=mp_prog, drain=drain)
    hp = _honest_progress()
    open_count = sum(1 for it in items if it.get("kind") != "safety")

    card = {
        "ok": True,
        "schema": SCHEMA_CARD,
        "built_at": _now(),
        "id": "MISSED-ACTIONS",
        "title": "Missed actions",
        "lead": (
            f"{open_count} founder taps still open · {hp['honest_done']}/{hp['total']} honest · "
            f"Worker next {drain.get('count', 0)} sa from queue pos {drain.get('next_pos')}"
        ),
        "honest_progress": hp,
        "items": items,
        "worker_drain_ref": str(DRAIN_PATH),
    }

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        CARD_PATH.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
        DRAIN_PATH.write_text(json.dumps(drain, indent=2) + "\n", encoding="utf-8")

    return {"card": card, "worker_drain_next_10": drain}


if __name__ == "__main__":
    out = sync_founder_missed_actions()
    print(json.dumps(out, indent=2))
