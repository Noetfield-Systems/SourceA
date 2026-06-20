"""Task-class allowlist — SAFE_AUTO / BEHAVIORAL / CONFIRM tiers."""
from __future__ import annotations

ALLOWLIST_VERSION = "v1"

TASK_CLASS_REGISTRY: dict[str, str] = {
    # SAFE_AUTO — read-only / validate-only; no file writes, network, or shell side effects
    "validate-only": "SAFE_AUTO",
    "hub-rebuild": "SAFE_AUTO",
    "ssot-read": "SAFE_AUTO",
    "packet-assemble": "SAFE_AUTO",
    "eval-run": "SAFE_AUTO",
    "index-read": "SAFE_AUTO",
    # BEHAVIORAL — writes or external APIs; requires behavioral_pass or founder_override
    "file-write": "BEHAVIORAL",
    "shell-script": "BEHAVIORAL",
    "git-commit": "BEHAVIORAL",
    "api-call-external": "BEHAVIORAL",
    "index-write": "BEHAVIORAL",
    # CONFIRM — high-consequence; always requires founder confirm
    "deploy": "CONFIRM",
    "database-migrate": "CONFIRM",
    "delete-files": "CONFIRM",
    "send-external": "CONFIRM",
    "agent-loop-start": "CONFIRM",
}

ALLOWLIST: dict[str, str] = TASK_CLASS_REGISTRY

TIER_SAFE_AUTO = "SAFE_AUTO"
TIER_BEHAVIORAL = "BEHAVIORAL"
TIER_CONFIRM = "CONFIRM"

# Layer-1 action_id → Layer-2 task_class (see DISPATCH_POLICY_LOCKED_v1.md Phase 2a)
ACTION_TO_TASK_CLASS: dict[str, str] = {
    "spine-smoke-echo": "validate-only",
    "validate-eval-packet-v1": "validate-only",
    "validate-eval-packet-v1b": "validate-only",
    "validate-gate-receipts-v1": "validate-only",
    "pos-dispatch": "packet-assemble",
    "pos-decide": "packet-assemble",
    "pos-run": "packet-assemble",
}

_TASK_CLASS_PREFIXES: tuple[tuple[str, str], ...] = (
    ("validate-", "validate-only"),
    ("audit-", "validate-only"),
    ("read-", "ssot-read"),
    ("pos-", "packet-assemble"),
    ("plan-", "packet-assemble"),
    ("repair-", "packet-assemble"),
)


def infer_task_class(action_id: str) -> str:
    """Map spine action_id to task_class for evaluate() / orchestrator shadow."""
    aid = (action_id or "").strip()
    if not aid:
        return "packet-assemble"
    if aid in ACTION_TO_TASK_CLASS:
        return ACTION_TO_TASK_CLASS[aid]
    for prefix, task_class in _TASK_CLASS_PREFIXES:
        if aid.startswith(prefix):
            return task_class
    return "packet-assemble"
