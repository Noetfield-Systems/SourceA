#!/usr/bin/env python3
"""Build + reset + autodrain healthy packs until queue exhausted or max packs."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BUILD = Path.home() / ".sina/build-achievable-healthy-queue.py"
AUTODRAIN = SCRIPTS / "worker_healthy_pack_autodrain_v1.py"
RECEIPTS_DIR = Path.home() / ".sina/pack-drain-receipts"
CHECKPOINTS = (580, 650, 750)

sys.path.insert(0, str(SCRIPTS))
from healthy_pack_bind_lib_v1 import heal_bind_mismatch, sync_active_now  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(ROOT),
        env={**dict(__import__("os").environ), "PYTHONUNBUFFERED": "1"},
    )
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def _progress() -> int:
    code, out = _run([sys.executable, str(SCRIPTS / "goal-progress-v1.py")], timeout=30)
    for line in out.splitlines():
        if line.startswith("GOAL_1:"):
            try:
                return int(line.split()[1].split("/")[0])
            except (IndexError, ValueError):
                pass
    return -1


def _write_receipt(pack_num: int, payload: dict) -> Path:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS_DIR / f"pack-{pack_num:02d}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _reset_pack() -> None:
    state = {
        "next_pos": 1,
        "last_advanced_at": _now(),
        "last_completed_pos": 0,
        "skip_sa_slice": False,
        "skipped_positions": 0,
    }
    for p in (
        Path.home() / ".sina/healthy-queue-state-v1.json",
        ROOT / "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-state-v1.json",
    ):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    _run([sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "reset"])
    sync_active_now()


def _run_autodrain(*, max_turns: int = 30) -> tuple[int, str]:
    return _run([sys.executable, str(AUTODRAIN), "--max-turns", str(max_turns)], timeout=900)


def _checkpoint_if_needed(after: int) -> dict | None:
    if after not in CHECKPOINTS:
        return None
    bundle = {}
    for v in (
        "validate-registry-honest-gate-v1.sh",
        "validate-monitor-honesty-v1.sh",
        "validate-healthy-pack-bind-v1.sh",
    ):
        code, out = _run(["bash", str(SCRIPTS / v)], timeout=120)
        bundle[v] = {"ok": code == 0, "tail": out.splitlines()[-1] if out else ""}
    _run([sys.executable, str(SCRIPTS / "brain_sync_lib_v1.py"), "--mode", "full"], timeout=120)
    _run([sys.executable, str(SCRIPTS / "hub_self_refresh_v1.py"), "--json"], timeout=120)
    return {"checkpoint": after, "validators": bundle}


def _one_pack(pack_num: int, *, retry: bool = False) -> dict:
    before = _progress()
    code, out = _run([sys.executable, str(BUILD)], timeout=60)
    if code != 0:
        return {"ok": False, "pack": pack_num, "step": "build", "error": out[:500]}
    try:
        start = out.rfind("{")
        built = json.loads(out[start:] if start >= 0 else out)
        sa_range = built.get("sa_range", [])
        pick_floor = built.get("pick_floor")
    except json.JSONDecodeError:
        sa_range = []
        pick_floor = None

    _reset_pack()
    bind_heal = heal_bind_mismatch(force_deliver=True)
    _run(["bash", str(SCRIPTS / "validate-healthy-pack-bind-v1.sh")], timeout=60)

    code, out = _run_autodrain()
    partial = False
    if code != 0 and not retry:
        heal_bind_mismatch(force_deliver=True)
        code, out = _run_autodrain()

    _run([sys.executable, str(SCRIPTS / "brain_sync_lib_v1.py"), "--mode", "light"], timeout=60)
    after = _progress()
    delta = (after - before) if after >= 0 and before >= 0 else None
    if delta is not None and 0 < delta < 8:
        partial = True

    receipt = {
        "pack": pack_num,
        "at": _now(),
        "sa_range": sa_range,
        "pick_floor": pick_floor,
        "before": before,
        "after": after,
        "delta": delta,
        "ok": code == 0,
        "partial": partial,
        "retry": retry,
        "bind_heal": bind_heal,
        "autodrain_exit": code,
        "tail": out.splitlines()[-8:] if out else [],
    }
    ck = _checkpoint_if_needed(after) if after >= 0 else None
    if ck:
        receipt["checkpoint"] = ck
    receipt["receipt_path"] = str(_write_receipt(pack_num, receipt))

    return {
        "ok": code == 0,
        "pack": pack_num,
        "sa_range": sa_range,
        "before": before,
        "after": after,
        "delta": delta,
        "partial": partial,
        "autodrain_exit": code,
        "tail": receipt["tail"],
        "receipt_path": receipt["receipt_path"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max-packs", type=int, default=79, help="Pack 5..N (default drain all achievable)")
    p.add_argument("--start-pack", type=int, default=5)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    from factory_spawn_gate_v1 import exit_if_spawn_blocked  # noqa: WPS433

    exit_if_spawn_blocked("worker_healthy_pack_loop", json_mode=args.json)
    results = []
    for n in range(args.start_pack, args.start_pack + args.max_packs):
        r = _one_pack(n)
        results.append(r)
        after = r.get("after") or 0
        if r.get("delta") == 0:
            heal_bind_mismatch(force_deliver=True)
            retry_r = _one_pack(n, retry=True)
            results[-1] = {**r, "first_attempt": r, "retry": retry_r}
            r = retry_r
            if r.get("delta") == 0:
                break
        if not r.get("ok") and (r.get("delta") or 0) <= 0:
            break
        if after >= 750:
            break
    summary = {
        "packs_run": len(results),
        "start_progress": results[0].get("before") if results else None,
        "end_progress": results[-1].get("after") if results else None,
        "results": results,
    }
    _write_receipt(0, {"schema": "pack-loop-summary-v1", "at": _now(), **summary})
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for r in results:
            tag = " PARTIAL" if r.get("partial") else ""
            print(
                f"pack {r.get('pack')} range={r.get('sa_range')} "
                f"{r.get('before')}->{r.get('after')} ok={r.get('ok')}{tag}"
            )
    return 0 if results and results[-1].get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
