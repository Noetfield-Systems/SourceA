#!/usr/bin/env python3
"""Live-prompt lane score only — 8 checks, 90% gate. No anti-staleness / dual-pick dims."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "live-prompt-lane-score-v1.json"
RECEIPT = SINA / "live-prompt-lane-receipt-v1.json"
LIVE = SINA / "live-ongoing-prompts-next-10-v1.json"
OVERRIDES = SINA / "live-prompt-overrides-v1.json"
RECEIPT_MAX_AGE_SEC = 300
WALL_SEC_DEFAULT = 120


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 120) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0, (proc.stdout or proc.stderr or "")[-500:]
    except Exception as exc:
        return False, str(exc)


def _load_hdr():
    spec = importlib.util.spec_from_file_location("hdr", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _smoke_quarantine_skip() -> dict:
    try:
        hdr = _load_hdr()
        qi = hdr.queue_item()
        if not qi.get("ok"):
            return {"ok": False, "detail": "no queue item"}
        pos = int(qi.get("pos") or 0)
        backup = OVERRIDES.read_text(encoding="utf-8") if OVERRIDES.is_file() else None
        sys.path.insert(0, str(SCRIPTS))
        from healthy_queue_ssot_lib import healthy_queue_state_path  # noqa: WPS433

        state_path = healthy_queue_state_path()
        state_backup = state_path.read_text(encoding="utf-8")
        OVERRIDES.parent.mkdir(parents=True, exist_ok=True)
        OVERRIDES.write_text(
            json.dumps(
                {
                    "schema": "live-prompt-overrides-v1",
                    "edits": {},
                    "quarantine": [pos],
                    "excluded": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        st = hdr.orchestrator_state()
        out = hdr._skip_override_turn(qi=qi, reason="quarantine", st=st)
        ok = bool(out.get("skipped")) and out.get("skip_reason") == "quarantine"
        # restore
        if backup is None:
            OVERRIDES.unlink(missing_ok=True)
        else:
            OVERRIDES.write_text(backup, encoding="utf-8")
        subprocess.run(
            [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py"), "--set-pos", str(pos), "--reason", "lane-score-restore"],
            cwd=str(ROOT),
            capture_output=True,
        )
        state_path.write_text(state_backup, encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPTS / "live_ongoing_prompts_v1.py"), "--rebuild"], cwd=str(ROOT), capture_output=True)
        return {"ok": ok, "detail": out.get("skip_reason") or "fail"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


def _smoke_edit_roundtrip() -> dict:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from live_prompt_overrides_v1 import handle_action  # noqa: WPS433
        from live_ongoing_prompts_v1 import load_overrides, rebuild  # noqa: WPS433

        hdr = _load_hdr()
        qi = hdr.queue_item()
        pos = int((qi.get("pos") or 1))
        backup = OVERRIDES.read_text(encoding="utf-8") if OVERRIDES.is_file() else None
        res = handle_action({"action": "edit", "queue_pos": pos, "instruction": "lane-score smoke edit"})
        ok = bool(res.get("ok"))
        ov = load_overrides()
        ok = ok and str(pos) in (ov.get("edits") or {})
        rebuild(write=True)
        if backup is None:
            OVERRIDES.unlink(missing_ok=True)
        else:
            OVERRIDES.write_text(backup, encoding="utf-8")
            rebuild(write=True)
        return {"ok": ok, "detail": "edit round-trip"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


def _receipt_age_sec() -> float | None:
    if not RECEIPT.is_file():
        return None
    try:
        data = json.loads(RECEIPT.read_text(encoding="utf-8"))
        at = data.get("at") or ""
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return None


def _receipt_fresh(*, max_age: int = RECEIPT_MAX_AGE_SEC) -> bool:
    age = _receipt_age_sec()
    if age is None:
        return False
    try:
        data = json.loads(RECEIPT.read_text(encoding="utf-8"))
        return age < max_age and bool(data.get("ok"))
    except (OSError, json.JSONDecodeError):
        return False


def _e2e_ok_from_receipt() -> bool:
    try:
        data = json.loads(RECEIPT.read_text(encoding="utf-8"))
        for c in data.get("checks") or []:
            if c.get("id") == "e2e":
                return bool(c.get("ok"))
    except (OSError, json.JSONDecodeError):
        pass
    return False


def _smoke_freeze_act() -> dict:
    try:
        hdr = _load_hdr()
        qi = hdr.queue_item()
        item = qi.get("item") or {}
        role = str(item.get("queue_role") or "check")
        blocked = hdr._freeze_blocks_role("act")
        check_ok = not hdr._freeze_blocks_role("check")
        if role == "check":
            return {"ok": check_ok, "detail": f"cursor CHECK freeze_act={blocked}"}
        return {"ok": blocked, "detail": f"cursor {role} freeze_act_blocks={blocked}"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


def _cached_score_fresh(*, max_age: int = RECEIPT_MAX_AGE_SEC) -> dict | None:
    if not OUT.is_file():
        return None
    try:
        row = json.loads(OUT.read_text(encoding="utf-8"))
        at = row.get("at") or ""
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        if age < max_age and bool(row.get("ok")):
            row["from_cache"] = True
            return row
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        pass
    return None


def score(*, write: bool = True, use_receipt: bool = False, wall_sec: int = WALL_SEC_DEFAULT) -> dict:
    started = datetime.now(timezone.utc)
    if use_receipt:
        cached = _cached_score_fresh()
        if cached is not None:
            return cached
    weights = {
        "validate_live_ongoing": 15,
        "validate_pack_live": 15,
        "built_at_fresh": 10,
        "cursor_align": 15,
        "overrides_schema": 10,
        "quarantine_skip": 15,
        "edit_roundtrip": 10,
        "e2e": 10,
    }
    checks: dict[str, dict] = {}

    ok1, _ = _run(["bash", str(SCRIPTS / "validate-live-ongoing-prompts-v1.sh")])
    checks["validate_live_ongoing"] = {"ok": ok1, "weight": weights["validate_live_ongoing"]}

    ok2, _ = _run([sys.executable, str(SCRIPTS / "validate-next-prompt-pack-live-v1.py"), "--strict"])
    checks["validate_pack_live"] = {"ok": ok2, "weight": weights["validate_pack_live"]}

    fresh = False
    cursor_align = False
    if LIVE.is_file():
        live = json.loads(LIVE.read_text(encoding="utf-8"))
        built = live.get("built_at") or ""
        try:
            dt = datetime.fromisoformat(built.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - dt).total_seconds()
            fresh = age < 30
        except Exception:
            fresh = False
        sys.path.insert(0, str(SCRIPTS))
        from healthy_queue_ssot_lib import healthy_queue_state_path  # noqa: WPS433

        state = json.loads(healthy_queue_state_path().read_text(encoding="utf-8"))
        cursor = int(state.get("next_pos") or 1)
        turns = live.get("turns") or []
        cursor_align = bool(turns) and int(turns[0].get("queue_pos") or 0) == cursor
    checks["built_at_fresh"] = {"ok": fresh, "weight": weights["built_at_fresh"]}
    checks["cursor_align"] = {"ok": cursor_align, "weight": weights["cursor_align"]}

    ov_ok = False
    if OVERRIDES.is_file():
        try:
            ov = json.loads(OVERRIDES.read_text(encoding="utf-8"))
            ov_ok = ov.get("schema") == "live-prompt-overrides-v1"
        except Exception:
            ov_ok = False
    else:
        ov_ok = True
    checks["overrides_schema"] = {"ok": ov_ok, "weight": weights["overrides_schema"]}

    q = _smoke_quarantine_skip()
    checks["quarantine_skip"] = {"ok": q["ok"], "weight": weights["quarantine_skip"], "detail": q.get("detail")}

    e = _smoke_edit_roundtrip()
    checks["edit_roundtrip"] = {"ok": e["ok"], "weight": weights["edit_roundtrip"], "detail": e.get("detail")}

    if use_receipt and _receipt_fresh():
        ok8 = _e2e_ok_from_receipt()
        checks["e2e"] = {"ok": ok8, "weight": weights["e2e"], "source": "receipt"}
    else:
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        budget = max(10, wall_sec - int(elapsed))
        ok8, _ = _run(
            ["bash", str(SCRIPTS / "validate-live-prompt-feed-e2e-v1.sh")],
            timeout=min(180, budget),
        )
        checks["e2e"] = {"ok": ok8, "weight": weights["e2e"], "source": "live"}

    earned = sum(c["weight"] for c in checks.values() if c.get("ok"))
    total = sum(weights.values())
    pct = round(100.0 * earned / total, 1)
    freeze_smoke = _smoke_freeze_act()

    wall_elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    partial = wall_elapsed >= wall_sec and pct < 90.0
    row = {
        "ok": pct >= 90.0 and not partial,
        "schema": "live-prompt-lane-score-v1",
        "at": _now(),
        "score_pct": pct,
        "earned": earned,
        "total": total,
        "checks": checks,
        "freeze_act_smoke": freeze_smoke,
        "gate": "LIVE_PACK_VALIDATOR_BLOCKED" if pct < 90.0 else None,
        "use_receipt": use_receipt,
        "wall_sec": wall_sec,
        "partial": partial,
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--use-receipt", action="store_true", help="Reuse fresh live-prompt-lane-receipt for E2E check")
    p.add_argument("--wall-sec", type=int, default=WALL_SEC_DEFAULT)
    args = p.parse_args()
    use_receipt = args.use_receipt or _receipt_fresh()
    row = score(use_receipt=use_receipt, wall_sec=args.wall_sec)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"score={row['score_pct']}% {'PASS' if row['ok'] else 'FAIL'}")
    if args.strict and not row.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
