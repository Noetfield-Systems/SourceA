"""Execution intelligence layer — types (extends spine, does not modify it)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

PatternType = Literal["success", "failure"]

STATE_DIR_NAME = ".sina"
MEMORY_FILENAME = "execution_memory.jsonl"
PATTERNS_FILENAME = "execution_patterns.json"
DECISIONS_FILENAME = "execution_decisions.jsonl"
INTEL_STATE_FILENAME = "execution-intelligence-state.json"


@dataclass
class ExecutionPattern:
    pattern_id: str
    type: PatternType
    frequency: int
    related_tasks: list[str] = field(default_factory=list)
    resolution_strategy: str = ""
    action_id: str = ""
    error_signature: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionRecord:
    decision_id: str
    task_id: str
    timestamp: str
    action_id: str
    outcome: str
    why: str
    fix_applied: str = ""
    error_signature: str = ""
    pattern_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
