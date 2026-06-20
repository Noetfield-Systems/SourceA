#!/usr/bin/env python3
"""One-sentence prompt — narrate with mandatory per-step timing caps."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-narrate-loop-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from brain_intent_gate_v1 import clear_narrate_lock, set_narrate_lock  # noqa: E402
from brain_timing_enforce_v1 import BRAIN_REPLY_LIMIT_SEC, TOTAL_LIMIT_SEC  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phrase", default="Run the loop step-by-step, narrating each action until we have a final answer.")
    args = p.parse_args()
    t0 = time.monotonic()
    set_narrate_lock()
    try:
        return _run(args, t0)
    finally:
        clear_narrate_lock()


def _run(args, t0: float) -> int:
    spec = importlib.util.spec_from_file_location("bw", ROOT / "scripts" / "brain_watch_loop_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    watch = mod.watch_loop(founder_phrase=args.phrase)
    timing = watch.get("timing_enforcement") or {}

    narration: list[str] = []
    for s in watch.get("steps") or []:
        narration.append(
            f"Step {s.get('n')} [{s.get('gate')}] {s.get('decision')} "
            f"({s.get('elapsed_sec')}s/{s.get('limit_sec')}s): {s.get('reason')}"
        )

    activate = next((s for s in watch.get("steps") or [] if s.get("gate") == "ACTIVATE"), {})
    act_dec = activate.get("decision")
    bugs = watch.get("bugs_suspected") or []
    violations = timing.get("violations") or []

    if violations:
        final = f"TIMING VIOLATION — {len(violations)} step(s) over cap. Brain must STOP."
    elif bugs:
        final = f"Trace complete — {len(bugs)} bug(s); activate={act_dec}."
    elif act_dec == "RUNNING":
        final = "Loop already running — narrate done; do not spawn."
    elif act_dec == "READY":
        final = "Gates green — say 'activate loop' to spawn (not this prompt)."
    else:
        final = f"Trace complete — activate={act_dec}."

    elapsed = round(time.monotonic() - t0, 1)
    out = {
        "status": "BRAIN_NARRATE_LOOP",
        "at": _now(),
        "elapsed_sec": elapsed,
        "timing_enforcement": timing,
        "founder_prompt": args.phrase,
        "narration": narration,
        "final_answer": final,
        "chain": watch.get("chain"),
        "bugs_suspected": bugs,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    SINA.joinpath("brain-loop-watch-v1.json").write_text(json.dumps(watch, indent=2) + "\n", encoding="utf-8")

    print(f"status: {out['status']}")
    print(f"elapsed_sec: {elapsed}")
    print(f"timing: {timing.get('timing')} (total_limit={TOTAL_LIMIT_SEC}s reply_limit={BRAIN_REPLY_LIMIT_SEC}s)")
    print("narration:")
    for line in narration:
        print(f"  - {line}")
    print(f"final_answer: {final}")
    if violations:
        print("timing_violations:")
        for v in violations:
            print(f"  - {v.get('gate')}: {v.get('elapsed_sec')}s > {v.get('limit_sec')}s")
    if bugs:
        print("bugs_suspected:")
        for b in bugs:
            print(f"  - {b.get('id')}: {b.get('symptom')}")

    bad = (
        elapsed > BRAIN_REPLY_LIMIT_SEC
        or timing.get("timing") == "VIOLATION"
        or bool(violations)
    )
    return 1 if bad else 0


def _run_entry() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phrase", default="Run the loop step-by-step, narrating each action until we have a final answer.")
    return _run(p.parse_args(), time.monotonic())


if __name__ == "__main__":
    raise SystemExit(main())
