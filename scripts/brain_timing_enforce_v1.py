#!/usr/bin/env python3
"""Mandatory per-step + total time budgets for Brain narrate/watch — no blocking."""
from __future__ import annotations

import subprocess
import time
from typing import Any, Callable

# Per-gate hard limits (seconds). Brain chat must not exceed these per step.
STEP_LIMIT_SEC: dict[str, int] = {
    "SYNC": 12,
    "FEASIBILITY": 5,
    "ORCHESTRATOR": 4,
    "INJECT": 4,
    "VALIDATE": 10,
    "ONE_SA": 4,
    "ACTIVATE": 15,
    "PROOF": 3,
    "CHAIN": 10,
}

TOTAL_LIMIT_SEC = 60
BRAIN_REPLY_LIMIT_SEC = 75  # script + paste to founder


class TimingBudget:
    def __init__(self) -> None:
        self._t0 = time.monotonic()
        self.violations: list[dict] = []

    def elapsed_total(self) -> float:
        return time.monotonic() - self._t0

    def remaining_total(self) -> float:
        return max(0.0, TOTAL_LIMIT_SEC - self.elapsed_total())

    def timing_block(self, gate: str, elapsed: float, *, timed_out: bool = False) -> dict:
        limit = STEP_LIMIT_SEC.get(gate, 10)
        ok = (not timed_out) and elapsed <= limit
        row = {
            "limit_sec": limit,
            "elapsed_sec": round(elapsed, 2),
            "timing": "PASS" if ok else "VIOLATION",
            "timed_out": timed_out,
        }
        if not ok:
            self.violations.append(
                {
                    "gate": gate,
                    "limit_sec": limit,
                    "elapsed_sec": row["elapsed_sec"],
                    "timed_out": timed_out,
                    "rule": "BRAIN_UNIFIED_RULES_LOCKED_v1.md",
                }
            )
        return row

    def run(self, gate: str, fn: Callable[[], Any]) -> tuple[Any, dict]:
        if self.remaining_total() <= 0:
            tb = self.timing_block(gate, 0.0, timed_out=True)
            tb["skip"] = True
            tb["reason"] = "TOTAL_BUDGET_EXCEEDED"
            self.violations.append(
                {
                    "gate": gate,
                    "limit_sec": STEP_LIMIT_SEC.get(gate, 10),
                    "elapsed_sec": 0,
                    "timed_out": True,
                    "rule": "TOTAL_BUDGET_EXCEEDED",
                }
            )
            return None, tb
        limit = STEP_LIMIT_SEC.get(gate, 10)
        cap = min(limit, self.remaining_total())
        t0 = time.monotonic()
        try:
            out = fn()
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - t0
            return None, self.timing_block(gate, elapsed, timed_out=True)
        elapsed = time.monotonic() - t0
        if elapsed > cap:
            return out, self.timing_block(gate, elapsed, timed_out=True)
        return out, self.timing_block(gate, elapsed)

    def run_subprocess(
        self,
        gate: str,
        cmd: list[str],
        *,
        cwd: str,
        timeout: int | None = None,
    ) -> dict:
        limit = STEP_LIMIT_SEC.get(gate, 10)
        cap = int(min(limit if timeout is None else timeout, self.remaining_total()))
        if cap <= 0:
            tb = self.timing_block(gate, 0.0, timed_out=True)
            tb["skip"] = True
            return {"ok": False, "timed_out": True, "timing": tb}

        t0 = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=cap)
            elapsed = time.monotonic() - t0
            tb = self.timing_block(gate, elapsed, timed_out=elapsed > limit)
            return {
                "ok": proc.returncode == 0 and not tb.get("timed_out"),
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "timing": tb,
            }
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - t0
            tb = self.timing_block(gate, elapsed, timed_out=True)
            return {
                "ok": False,
                "timed_out": True,
                "stdout": (exc.stdout or b"").decode("utf-8", errors="replace")[:1500] if exc.stdout else "",
                "stderr": (exc.stderr or b"").decode("utf-8", errors="replace")[:400] if exc.stderr else "",
                "timing": tb,
            }

    def summary(self) -> dict:
        total = round(self.elapsed_total(), 2)
        return {
            "total_limit_sec": TOTAL_LIMIT_SEC,
            "brain_reply_limit_sec": BRAIN_REPLY_LIMIT_SEC,
            "elapsed_sec": total,
            "timing": "PASS" if total <= TOTAL_LIMIT_SEC and not self.violations else "VIOLATION",
            "violations": self.violations,
            "step_limits_sec": STEP_LIMIT_SEC,
        }
