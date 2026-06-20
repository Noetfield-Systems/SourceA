#!/usr/bin/env python3
"""Unify queue head across factory-now · monitor-live · run-inbox · brain · inbox meta.

Single writer: healthy-queue-state next_pos + healthy-queue-30-active.
Law: RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md · INCIDENT split-brain routing.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
INBOX_JSON = SINA / "worker-prompt-inbox-v1.json"
HYGIENE_PASS = SINA / "last-hygiene-pass-v1.json"
BRAIN_FRESH_SEC = 120

sys.path.insert(0, str(SCRIPTS))
from healthy_queue_ssot_lib import (  # noqa: E402
    healthy_queue_path,
    healthy_queue_state_path,
    load_healthy_queue,
    queue_items,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def queue_head() -> dict:
    """Canonical queue cursor — one sa_id + role for all surfaces."""
    _, q = load_healthy_queue()
    items = queue_items(q)
    total = len(items)
    if q.get("queue_exhausted") or q.get("phase_strict_complete") or not items:
        return {
            "ok": True,
            "sa_id": "",
            "role": "",
            "pos": 1,
            "total": total,
            "phase": None,
            "queue_exhausted": True,
        }
    pos = 1
    state_path = healthy_queue_state_path()
    if state_path.is_file():
        try:
            st = json.loads(state_path.read_text(encoding="utf-8"))
            if st.get("queue_exhausted"):
                return {
                    "ok": True,
                    "sa_id": "",
                    "role": "",
                    "pos": int(st.get("next_pos") or 1),
                    "total": total,
                    "phase": None,
                    "queue_exhausted": True,
                }
            pos = int(st.get("next_pos") or 1)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pos = 1
    try:
        from healthy_queue_ssot_lib import first_open_queue_pos, sa_closeout_complete  # noqa: WPS433

        pos = first_open_queue_pos()
    except Exception:
        pass
    exhausted = bool(total and pos > total)
    if exhausted:
        return {
            "ok": True,
            "sa_id": "",
            "role": "",
            "pos": pos,
            "total": total,
            "phase": None,
            "queue_exhausted": True,
        }
    item = items[pos - 1] if items and 1 <= pos <= len(items) else {}
    sa_id = str(item.get("sa_id") or "")
    role = str(item.get("queue_role") or "")
    if sa_id and sa_closeout_complete(sa_id):
        return {
            "ok": True,
            "sa_id": "",
            "role": "",
            "pos": pos,
            "total": total,
            "phase": item.get("phase"),
            "queue_exhausted": True,
            "poison_skipped": sa_id,
        }
    return {
        "ok": bool(sa_id),
        "sa_id": sa_id,
        "role": role,
        "pos": pos,
        "total": total,
        "phase": item.get("phase"),
        "upgrade_id": str(item.get("upgrade_id") or ""),
        "queue_exhausted": exhausted,
    }


def heal_stale_inbox_meta() -> dict:
    """When INBOX cleared, meta must match queue head (not prior pack tail)."""
    head = queue_head()
    if head.get("queue_exhausted") and not head.get("sa_id"):
        from worker_inject_lib import clear_idle_turn_artifacts  # noqa: WPS433

        cleared = clear_idle_turn_artifacts()
        if INBOX_JSON.is_file():
            try:
                data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
                directive_stub = ""
                try:
                    from founder_directive_ssot_v1 import truth_block_lines  # noqa: WPS433

                    lines = truth_block_lines()
                    if lines:
                        directive_stub = "\n".join(lines) + "\n"
                except Exception:
                    pass
                stub = (
                    "INBOX cleared · pending=false · Goal 1 complete · queue idle\n"
                    f"{directive_stub}"
                )
                # #region agent log
                try:
                    import time

                    with open(
                        ROOT / ".cursor" / "debug-baabac.log",
                        "a",
                        encoding="utf-8",
                    ) as _df:
                        _df.write(
                            json.dumps(
                                {
                                    "sessionId": "baabac",
                                    "runId": "post-fix",
                                    "hypothesisId": "H1",
                                    "location": "queue_ssot_unify_v1.py:heal_stale_inbox_meta",
                                    "message": "lawful_queue_exhausted stub",
                                    "data": {
                                        "has_founder_directive": "FOUNDER DIRECTIVE" in stub,
                                        "directive_lines": len(directive_stub.splitlines()),
                                    },
                                    "timestamp": int(time.time() * 1000),
                                }
                            )
                            + "\n"
                        )
                except OSError:
                    pass
                # #endregion
                data["pending"] = False
                data["meta"] = {
                    "sa_id": "",
                    "queue_role": "",
                    "queue_pos": 0,
                    "queue_total": 0,
                    "queue_exhausted": True,
                    "healed_at": _now(),
                    "heal_reason": "lawful_queue_exhausted",
                }
                data["sa_id"] = ""
                data["prompt"] = stub
                data["chars"] = len(stub)
                INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            except (OSError, json.JSONDecodeError):
                pass
        return {"ok": True, "healed": True, "reason": "lawful_queue_exhausted", "head": head, "cleared": cleared}
    if not head.get("sa_id"):
        return {"ok": False, "error": "empty_queue_head", "head": head}
    if not INBOX_JSON.is_file():
        from worker_inject_lib import ensure_inbox_shell  # noqa: WPS433

        shell = ensure_inbox_shell(reason="queue_ssot_missing_inbox")
        if not shell.get("ok"):
            return shell
        return {"ok": True, "healed": bool(shell.get("created")), "reason": "created_inbox_shell", "head": head}
    try:
        data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}

    meta = data.get("meta") or {}
    pending = bool(data.get("pending"))
    sa = str(meta.get("sa_id") or data.get("sa_id") or "")
    pos = int(meta.get("queue_pos") or 0)
    role = str(meta.get("queue_role") or "")
    head_uid = str(head.get("upgrade_id") or "")
    inbox_uid = str(meta.get("upgrade_id") or "")

    if pending and head_uid and inbox_uid != head_uid:
        meta = {
            **meta,
            "sa_id": head["sa_id"],
            "queue_role": head["role"],
            "queue_pos": head["pos"],
            "queue_total": head["total"],
            "phase": head.get("phase"),
            "upgrade_id": head_uid,
            "healed_at": _now(),
            "heal_reason": "upgrade_id_latch",
        }
        data["meta"] = meta
        data["sa_id"] = head["sa_id"]
        INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return {
            "ok": True,
            "healed": True,
            "reason": "upgrade_id_latch",
            "was": {"upgrade_id": inbox_uid or None},
            "head": head,
        }

    need = (
        not pending
        and (
            sa != head["sa_id"]
            or pos != head["pos"]
            or role != head["role"]
            or "FOUNDER DIRECTIVE" not in (data.get("prompt") or "")
        )
    )
    if not need:
        return {"ok": True, "healed": False, "reason": "already_aligned", "head": head}

    data["meta"] = {
        "sa_id": head["sa_id"],
        "queue_role": head["role"],
        "queue_pos": head["pos"],
        "queue_total": head["total"],
        "phase": head.get("phase"),
        "upgrade_id": head_uid or None,
        "healed_at": _now(),
        "heal_reason": "queue_ssot_unify",
    }
    data["sa_id"] = head["sa_id"]
    stub = (
        f"INBOX cleared · pending=false · next head {head['sa_id']} "
        f"{head['role']} {head['pos']}/{head['total']}\n"
    )
    if "FOUNDER DIRECTIVE" not in (data.get("prompt") or ""):
        try:
            from founder_directive_ssot_v1 import truth_block_lines  # noqa: WPS433

            lines = truth_block_lines()
            if lines:
                stub = stub + "\n".join(lines) + "\n"
        except Exception:
            pass
    data["prompt"] = stub
    data["chars"] = len(stub)
    INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "healed": True, "was": {"sa_id": sa, "pos": pos, "role": role}, "head": head}


def heal_local_worker_inbox_latch(head: dict) -> dict:
    """Local Worker work orders require pending inbox latched to queue head upgrade."""
    head_uid = str(head.get("upgrade_id") or "")
    head_sa = str(head.get("sa_id") or "")
    if not head_uid or not head_sa:
        return {"ok": True, "skipped": True, "reason": "empty_head"}

    wo_path = SINA / "brain-outbound-work-order-active-v1.json"
    if not wo_path.is_file():
        return {"ok": True, "skipped": True, "reason": "no_work_order"}
    try:
        wo = json.loads(wo_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}

    if wo.get("execution_mode") != "local_worker":
        return {"ok": True, "skipped": True, "reason": "not_local_worker"}
    if str(wo.get("upgrade_ref") or "") != head_uid:
        return {"ok": True, "skipped": True, "reason": "upgrade_ref_mismatch", "work_order": wo.get("upgrade_ref")}

    inbox: dict = {}
    if INBOX_JSON.is_file():
        try:
            inbox = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            inbox = {}
    meta = inbox.get("meta") or {}
    if bool(inbox.get("pending")) and str(meta.get("upgrade_id") or "") == head_uid:
        return {"ok": True, "healed": False, "reason": "already_latched", "head": head}

    try:
        from outbound_factory_queue_assign_v1 import build_assignment, deliver_head  # noqa: WPS433

        bundle = build_assignment()
        deliver = deliver_head(bundle)
        return {
            "ok": bool(deliver.get("ok")),
            "healed": bool(deliver.get("ok")),
            "reason": "local_worker_deliver",
            "deliver": deliver,
            "head": head,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "head": head}


def _brain_sync_skippable_fast() -> bool:
    """Skip expensive brain_sync when hygiene receipt is fresh and dual proof holds."""
    if not HYGIENE_PASS.is_file():
        return False
    try:
        age = datetime.now(timezone.utc).timestamp() - HYGIENE_PASS.stat().st_mtime
        if age > BRAIN_FRESH_SEC:
            return False
        data = json.loads(HYGIENE_PASS.read_text(encoding="utf-8"))
        dual = data.get("dual_proof") or {}
        return bool(data.get("ok")) and bool(dual.get("dual_proof_ok"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return False


def unify_queue_ssot(*, write_brain: bool = True, rebuild_factory: bool = True, fast: bool = False) -> dict:
    """Heal inbox meta · sync orchestrator · rebuild factory-now · run-inbox truth · brain receipt."""
    head = queue_head()
    steps: dict = {"head": head}

    steps["inbox_meta"] = heal_stale_inbox_meta()
    steps["local_worker_latch"] = heal_local_worker_inbox_latch(head)

    try:
        from worker_stuck_recovery_v1 import sync_orchestrator_from_queue  # noqa: WPS433

        steps["orchestrator"] = sync_orchestrator_from_queue()
    except Exception as exc:
        steps["orchestrator"] = {"ok": False, "error": str(exc)}

    factory_row: dict = {}
    if rebuild_factory:
        try:
            from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

            factory_row = rebuild_factory_now(caller="queue_ssot_unify", force=True)
        except Exception as exc:
            factory_row = {"ok": False, "error": str(exc)}
    steps["factory_now"] = factory_row

    truth: dict = {}
    try:
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        truth = write_truth(sync=False)
    except Exception as exc:
        truth = {"ok": False, "error": str(exc)}
    steps["run_inbox_truth"] = truth

    # Cross-check
    fn_sa = str((factory_row or {}).get("queue_sa") or "")
    fn_in = str((factory_row or {}).get("inbox_sa") or "")
    tq = (truth.get("queue") or {}) if isinstance(truth, dict) else {}
    t_sa = str(tq.get("sa_id") or "")
    t_match = (truth.get("inbox") or {}).get("truth_match") if isinstance(truth, dict) else None
    aligned = bool(head.get("queue_exhausted")) or bool(head.get("sa_id") and head["sa_id"] == t_sa and fn_sa == head["sa_id"])
    if head.get("queue_exhausted") and not head.get("sa_id"):
        aligned = bool(tq.get("queue_exhausted") or t_match is not False)
    if not pending_inbox() and head.get("sa_id"):
        aligned = aligned and fn_in == head["sa_id"]
    steps["aligned"] = aligned
    steps["truth_match"] = t_match

    if write_brain:
        try:
            from brain_validate_goal1_v1 import validate_goal1  # noqa: WPS433

            bv = validate_goal1()
            bv_path = SINA / "brain-goal1-validation-v1.json"
            bv_path.write_text(json.dumps(bv, indent=2) + "\n", encoding="utf-8")
            steps["brain_validation"] = {
                "ok": bool(bv.get("ok")),
                "queue_head": bv.get("queue_head"),
                "path": str(bv_path),
            }
        except Exception as exc:
            steps["brain_validation"] = {"ok": False, "error": str(exc)}
        if fast and _brain_sync_skippable_fast():
            steps["brain"] = {"ok": True, "skipped": "fast_fresh", "caller": "queue_ssot_unify"}
        else:
            try:
                from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

                steps["brain"] = sync_brain_snapshot(mode="light", caller="queue_ssot_unify")
            except Exception as exc:
                steps["brain"] = {"ok": False, "error": str(exc)}

    return {
        "ok": aligned and t_match is not False,
        "schema": "queue-ssot-unify-v1",
        "at": _now(),
        "steps": steps,
        "founder_line": (
            f"Next: {head.get('sa_id')} {str(head.get('role') or '').upper()} "
            f"({head.get('pos')}/{head.get('total')}) · Worker chat → RUN INBOX"
            if head.get("sa_id")
            else (
                "Goal 1 complete · queue idle · Worker Hub → Next steps · commercial P0"
                if head.get("queue_exhausted")
                else "Queue head unknown — Maintainer heal"
            )
        ),
    }


def pending_inbox() -> bool:
    if not INBOX_JSON.is_file():
        return False
    try:
        return bool(json.loads(INBOX_JSON.read_text(encoding="utf-8")).get("pending"))
    except (OSError, json.JSONDecodeError):
        return False


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Unify queue SSOT across disk surfaces")
    p.add_argument("--json", action="store_true")
    p.add_argument("--head-only", action="store_true")
    p.add_argument("--fast", action="store_true", help="Skip brain_sync when hygiene receipt fresh")
    args = p.parse_args()
    if args.head_only:
        row = queue_head()
    else:
        row = unify_queue_ssot(fast=args.fast)
    if args.json or not args.head_only:
        print(json.dumps(row, indent=2))
    else:
        h = row
        print(f"{h.get('sa_id')} {h.get('role')} {h.get('pos')}/{h.get('total')}")
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
