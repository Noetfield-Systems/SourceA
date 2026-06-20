"""Execution intelligence v2 — predictive layer types."""
from __future__ import annotations

from typing import Any, Literal

RiskType = Literal["low", "medium", "high"]

DEFAULT_CANDIDATE_ACTIONS = [
    "pos-dispatch",
    "pos-execute",
    "pos-decide",
    "pos-run",
    "pos-status",
]
