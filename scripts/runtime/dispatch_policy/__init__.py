"""Dispatch policy — task-class registry + Eval-1b gate (Phase 2 law-safe)."""

from runtime.dispatch_policy.allowlist import TASK_CLASS_REGISTRY
from runtime.dispatch_policy.policy_engine import evaluate, evaluate_action

__all__ = ["TASK_CLASS_REGISTRY", "evaluate", "evaluate_action"]
