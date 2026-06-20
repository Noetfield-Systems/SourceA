#!/usr/bin/env python3
"""Live pack validator — hard gate before auto-deliver (founder confirm not required).

Law: SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md
Receipt: ~/.sina/live-pack-validator-receipt-v1.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "live-pack-validator-receipt-v1.json"
BLOCKED = SINA / "live-pack-blocked-v1.json"

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_bash(script: str) -> tuple[bool, str]:
    proc = subprocess.run(
        ["bash", str(SCRIPTS / script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out.strip()[:500]


def validate(*, write_receipt: bool = True) -> dict:
    checks: list[dict] = []
    ok = True

    # 1) Feasibility
    try:
        from prompt_feasibility_gate import check_session  # noqa: WPS433

        feas = check_session(role="worker")
        c_ok = feas.get("action") == "PROCEED" and not feas.get("pick_mismatch")
        checks.append(
            {
                "id": "prompt_feasibility",
                "ok": c_ok,
                "detail": feas.get("action"),
                "pick_mismatch": feas.get("pick_mismatch"),
            }
        )
        ok = ok and c_ok
    except Exception as exc:
        checks.append({"id": "prompt_feasibility", "ok": False, "error": str(exc)})
        ok = False

    # 2) Run inbox disk truth
    try:
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        truth = write_truth(sync=True)
        inbox = truth.get("inbox") or {}
        c_ok = bool(truth.get("truth_match") or inbox.get("truth_match"))
        pre_deliver_gap = False
        # Post-broker window: inbox cleared after submit; deliver injects next — not a truth violation.
        if not c_ok and not inbox.get("pending"):
            try:
                from worker_turn_lib import turn_open_block  # noqa: WPS433

                if not turn_open_block():
                    c_ok = True
                    pre_deliver_gap = True
            except Exception:
                pass
        checks.append(
            {
                "id": "run_inbox_truth",
                "ok": c_ok,
                "detail": truth.get("queue", {}).get("sa_id"),
                "inbox_pending": inbox.get("pending"),
                "pre_deliver_gap": pre_deliver_gap,
            }
        )
        ok = ok and c_ok
    except Exception as exc:
        checks.append({"id": "run_inbox_truth", "ok": False, "error": str(exc)})
        ok = False

    # 3) Pack bind
    bind_ok, bind_out = _run_bash("validate-healthy-pack-bind-v1.sh")
    checks.append({"id": "healthy_pack_bind", "ok": bind_ok, "detail": bind_out[:200]})
    ok = ok and bind_ok

    # 4) FREEZE — CHECK only when kill_flag
    try:
        from factory_control_v1 import rebuild_factory_now  # noqa: WPS433
        from healthy_queue_ssot_lib import healthy_queue_path, healthy_queue_state_path  # noqa: WPS433

        factory = rebuild_factory_now(caller="validate_pack_live", force=False)
        kill = bool(factory.get("kill_flag"))
        q = json.loads(healthy_queue_path().read_text(encoding="utf-8"))
        items = q.get("queue") or []
        pos = int(json.loads(healthy_queue_state_path().read_text()).get("next_pos") or 1)
        role = ""
        if 1 <= pos <= len(items):
            role = (items[pos - 1].get("queue_role") or "check").lower()
        if kill and role not in ("check",):
            from worker_inject_lib import inbox_status  # noqa: WPS433

            ib = inbox_status()
            if not ib.get("pending"):
                checks.append(
                    {
                        "id": "freeze_role",
                        "ok": True,
                        "detail": f"FREEZE blocks {role} deliver — inbox clear OK",
                    }
                )
            else:
                c_ok = False
                checks.append({"id": "freeze_role", "ok": False, "detail": f"FREEZE blocks {role} — CHECK only"})
                ok = False
        else:
            checks.append({"id": "freeze_role", "ok": True, "detail": f"mode={factory.get('mode')} role={role}"})
    except Exception as exc:
        checks.append({"id": "freeze_role", "ok": False, "error": str(exc)})
        ok = False

    # 5) Rules in charge
    ric_ok, ric_out = _run_bash("validate-agent-rules-in-charge-v1.sh")
    checks.append({"id": "rules_in_charge", "ok": ric_ok, "detail": ric_out[:120]})
    ok = ok and ric_ok

    # 6) Mandatory read paths
    mand_ok, mand_out = _run_bash("validate-mandatory-read-paths-v1.sh")
    checks.append({"id": "mandatory_reads", "ok": mand_ok, "detail": mand_out[:120]})
    ok = ok and mand_ok

    # 7) Dual-pick
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "_ecosystem_safety_dual_pick_check_v1.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        dp_ok = proc.returncode == 0
        checks.append({"id": "dual_pick", "ok": dp_ok, "detail": (proc.stdout or proc.stderr or "")[:200]})
        ok = ok and dp_ok
    except Exception as exc:
        checks.append({"id": "dual_pick", "ok": False, "error": str(exc)})
        ok = False

    # 8) Live ongoing slice
    try:
        from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

        live = rebuild(write=True, preview=False)
        turns = live.get("turns") or []
        c_ok = live.get("ok") and turns and turns[0].get("queue_pos") == live.get("cursor_pos")
        if turns and not turns[0].get("feasible"):
            c_ok = False
            checks.append(
                {
                    "id": "live_ongoing_feasible",
                    "ok": False,
                    "detail": turns[0].get("feasibility_reasons"),
                }
            )
            ok = False
        else:
            checks.append(
                {
                    "id": "live_ongoing_align",
                    "ok": c_ok,
                    "detail": f"cursor={live.get('cursor_pos')} head={turns[0].get('sa_id') if turns else None}",
                }
            )
            ok = ok and c_ok
    except Exception as exc:
        checks.append({"id": "live_ongoing", "ok": False, "error": str(exc)})
        ok = False

    row = {
        "ok": ok,
        "schema": "live-pack-validator-receipt-v1",
        "at": _now(),
        "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        "checks": checks,
        "failed": [c["id"] for c in checks if not c.get("ok")],
    }

    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if ok:
            if BLOCKED.is_file():
                BLOCKED.unlink()
        else:
            BLOCKED.write_text(json.dumps({**row, "blocked": True}, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = validate()
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print("PASS" if out.get("ok") else f"FAIL: {out.get('failed')}")
    if args.strict and not out.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
