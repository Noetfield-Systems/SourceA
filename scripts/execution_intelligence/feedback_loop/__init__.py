"""Feedback Loop v1 — patterns + decisions → behavioral influence signals."""
from execution_intelligence.feedback_loop.api import feedback_v1_payload
from execution_intelligence.feedback_loop.loop_engine import (
    load_patterns_readonly,
    read_signals,
    run_feedback_loop,
)


def load_patterns() -> list[dict]:
    """Backward-compatible pattern load for planner consumers."""
    from execution_intelligence.pattern_engine.api import load_patterns_v1  # noqa: WPS433

    return load_patterns_v1()


__all__ = [
    "feedback_v1_payload",
    "load_patterns",
    "load_patterns_readonly",
    "read_signals",
    "run_feedback_loop",
]
