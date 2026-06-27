"""Hub model dispatch — single OpenRouter choke point (D15.1)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
ROI_MATRIX_PATH = ROOT / "data" / "forge-model-roi-matrix-v1.json"

GATE_MODE_PREF_PATH = Path.home() / ".sina" / "gate_mode_v1.txt"
SHADOW_LOG = Path.home() / ".sina" / "gate_shadow_v1.jsonl"
ENFORCE_LOG = Path.home() / ".sina" / "gate_enforce_v1.jsonl"
GATE_SSOT_PATH = Path.home() / ".sina" / "model_dispatch_gate_v1.json"
GATE_SCHEMA = "model-dispatch-gate-v1"
_VALID_GATE_MODES = ("off", "shadow", "enforce")

# Forge Terminal — Master Model Matrix (UI id = catalog key; api_model = provider endpoint).
FORGE_MODEL_MATRIX: list[dict[str, Any]] = [
    {
        "id": "gemini-1.5-flash",
        "label": "Gemini 1.5 Flash",
        "subtitle": "Fast verify loop · $",
        "group": "Google",
        "provider": "gemini_direct",
        "api_model": "gemini-2.5-flash",
        "tier_hint": "T1_fast",
        "use_roles": ["check", "bulk"],
        "cost_band": "$",
    },
    {
        "id": "gemini-1.5-pro",
        "label": "Gemini 1.5 Pro",
        "subtitle": "2M context · architecture · $$$",
        "group": "Google",
        "provider": "gemini_direct",
        "api_model": "gemini-2.5-pro",
        "tier_hint": "T3_heavy",
        "use_roles": ["build", "reason", "critical"],
        "cost_band": "$$$",
    },
    {
        "id": "deepseek-v4",
        "label": "DeepSeek V4",
        "subtitle": "OpenRouter · Logic & JSON · $",
        "group": "OpenRouter",
        "provider": "openrouter",
        "api_model": "deepseek/deepseek-chat-v3-0324",
        "tier_hint": "T1_fast",
        "use_roles": ["bulk", "check"],
        "cost_band": "$",
    },
    {
        "id": "deepseek-r1-or",
        "label": "DeepSeek R1",
        "subtitle": "OpenRouter · Reasoning · $$",
        "group": "OpenRouter",
        "provider": "openrouter",
        "api_model": "deepseek/deepseek-r1-0528",
        "tier_hint": "T3_heavy",
        "use_roles": ["reason"],
        "cost_band": "$$",
    },
    {
        "id": "claude-haiku-4-direct",
        "label": "Claude Haiku 4.5",
        "subtitle": "Anthropic direct · Check & bulk · $",
        "group": "Anthropic",
        "provider": "anthropic_direct",
        "api_model": "claude-haiku-4-5-20251001",
        "tier_hint": "T1_fast",
        "use_roles": ["bulk", "check"],
        "cost_band": "$",
        "requires_key": "anthropic",
    },
    {
        "id": "claude-sonnet-4-direct",
        "label": "Claude Sonnet 4.6",
        "subtitle": "Anthropic direct · Build & act · $$$",
        "group": "Anthropic",
        "provider": "anthropic_direct",
        "api_model": "claude-sonnet-4-6",
        "tier_hint": "T2_medium",
        "use_roles": ["build", "act", "critical"],
        "cost_band": "$$$",
        "requires_key": "anthropic",
    },
    {
        "id": "claude-3.5-sonnet",
        "label": "Claude 3.5 Sonnet",
        "subtitle": "OpenRouter · Agentic coding · $$$",
        "group": "OpenRouter",
        "provider": "openrouter",
        "api_model": "anthropic/claude-3.5-sonnet",
        "tier_hint": "T2_medium",
        "use_roles": ["build", "act"],
        "cost_band": "$$$",
    },
    {
        "id": "claude-opus-4-or",
        "label": "Claude Opus 4",
        "subtitle": "OpenRouter · Critical · $$$$",
        "group": "OpenRouter",
        "provider": "openrouter",
        "api_model": "anthropic/claude-opus-4",
        "tier_hint": "T4_marathon",
        "use_roles": ["critical", "reason"],
        "cost_band": "$$$$",
    },
    {
        "id": "gpt-4o-mini-or",
        "label": "GPT-4o mini",
        "subtitle": "OpenRouter · Cheap control · $",
        "group": "OpenRouter",
        "provider": "openrouter",
        "api_model": "openai/gpt-4o-mini",
        "tier_hint": "T1_fast",
        "use_roles": ["check", "bulk"],
        "cost_band": "$",
    },
    {
        "id": "gpt-4o",
        "label": "GPT-4o",
        "subtitle": "OpenAI · Build & act · $$$",
        "group": "OpenAI",
        "provider": "openai",
        "api_model": "gpt-4o",
        "tier_hint": "T2_medium",
        "use_roles": ["build", "act"],
        "cost_band": "$$$",
        "requires_key": "openai",
    },
    {
        "id": "openai-o1",
        "label": "OpenAI o1",
        "subtitle": "Deep reasoning · Critical · $$$$",
        "group": "OpenAI",
        "provider": "openai",
        "api_model": "o1",
        "tier_hint": "T4_marathon",
        "use_roles": ["reason", "critical"],
        "cost_band": "$$$$",
        "requires_key": "openai",
    },
]

FORGE_MODEL_CATALOG: dict[str, dict[str, Any]] = {m["id"]: m for m in FORGE_MODEL_MATRIX}
FORGE_MODEL_GROUPS: tuple[str, ...] = ("Google", "Anthropic", "OpenRouter", "OpenAI")
FORGE_DEFAULT_MODEL = "gpt-4o"
FORGE_DEFAULT_ROLE = "bulk"
# Retired from auto-routing — high-demand 503s; OpenAI default when keyed.
FORGE_DISABLED_MODELS = frozenset({"gemini-3.1-flash-lite"})

_PROVIDER_KEY_MAP = {
    "gemini_direct": "gemini",
    "openrouter": "openrouter",
    "openai": "openai",
    "anthropic_direct": "anthropic",
}


def _load_roi_matrix() -> dict[str, Any]:
    if ROI_MATRIX_PATH.is_file():
        try:
            row = json.loads(ROI_MATRIX_PATH.read_text(encoding="utf-8"))
            if row.get("roles"):
                return row
        except (OSError, json.JSONDecodeError):
            pass
    return {"roles": {}}


def provider_key_ready(provider: str, keys: dict[str, str] | None = None) -> bool:
    """Whether secrets support this provider (optional pre-loaded keys dict)."""
    if keys is None:
        try:
            import sys

            sys.path.insert(0, str(ROOT / "scripts"))
            from ai_unify_api_v1 import load_keys  # noqa: WPS433

            keys = load_keys()
        except Exception:
            keys = {}
    p = (provider or "").strip()
    if p == "gemini_direct":
        return bool(keys.get("GEMINI_API_KEY"))
    if p == "openrouter":
        or_key = keys.get("OPENROUTER_API_KEY") or keys.get("OPENROUTER_API_KEY_FORGE", "")
        return bool(or_key) and str(or_key).startswith("sk-or-v1-")
    if p == "openai":
        return bool(keys.get("OPENAI_API_KEY"))
    if p == "anthropic_direct":
        return bool(keys.get("ANTHROPIC_API_KEY"))
    return False


def model_available(model_id: str, keys: dict[str, str] | None = None) -> bool:
    if model_id in FORGE_DISABLED_MODELS:
        return False
    entry = FORGE_MODEL_CATALOG.get(model_id)
    if not entry:
        return False
    return provider_key_ready(entry.get("provider") or "", keys)


def pick_forge_default_model(keys: dict[str, str] | None = None) -> str:
    """Prefer OpenAI when keyed; never auto-pick retired Gemini Flash-Lite."""
    for mid in (
        "gpt-4o",
        "gpt-4o-mini-or",
        "claude-sonnet-4-direct",
        "deepseek-v4",
        "gemini-1.5-flash",
    ):
        if model_available(mid, keys):
            return mid
    return FORGE_DEFAULT_MODEL


def pick_roi_model(role: str, keys: dict[str, str] | None = None) -> str:
    """Pick highest-ROI model for role among keys currently on disk."""
    role_id = (role or FORGE_DEFAULT_ROLE).strip().lower()
    matrix = _load_roi_matrix()
    roles = matrix.get("roles") or {}
    spec = roles.get(role_id) or roles.get(FORGE_DEFAULT_ROLE) or {}
    for mid in spec.get("priority") or []:
        if model_available(mid, keys):
            return mid
    for entry in FORGE_MODEL_MATRIX:
        if role_id in (entry.get("use_roles") or []) and model_available(entry["id"], keys):
            return entry["id"]
    for entry in FORGE_MODEL_MATRIX:
        if model_available(entry["id"], keys):
            return entry["id"]
    return pick_forge_default_model(keys)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_gate_mode(raw: str) -> str:
    m = (raw or "").strip().lower()
    if m not in _VALID_GATE_MODES:
        return "shadow"
    return m


def read_gate_mode_pref() -> str:
    """Founder SSOT: env SINA_GATE_MODE overrides ~/.sina/gate_mode_v1.txt."""
    env = os.environ.get("SINA_GATE_MODE", "").strip()
    if env:
        return _normalize_gate_mode(env)
    if GATE_MODE_PREF_PATH.is_file():
        return _normalize_gate_mode(GATE_MODE_PREF_PATH.read_text(encoding="utf-8"))
    return "shadow"


def persist_gate_mode_pref(mode: str) -> None:
    m = _normalize_gate_mode(mode)
    GATE_MODE_PREF_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_MODE_PREF_PATH.write_text(m + "\n", encoding="utf-8")


def current_gate_mode() -> str:
    return read_gate_mode_pref()


def enforce_synthesis_critic_drift_errors(
    synthesis_text: str,
    gate_mode: str | None = None,
    *,
    label: str = "SINA_GPT_CLAUDE_WTM_SYNTHESIS",
) -> list[str]:
    """sa-0020 — critic ENFORCE claims must match ~/.sina/gate_mode_v1.txt + dispatch-policy API."""
    mode = _normalize_gate_mode(gate_mode or current_gate_mode())
    errors: list[str] = []
    if mode == "shadow":
        if "| Gate mode | **enforce** |" in synthesis_text:
            errors.append(f"{label}: Live results Gate mode stale — disk={mode!r}")
        if "gate_mode_v1.txt` = enforce" in synthesis_text:
            errors.append(f"{label}: Claude table claims enforce current — disk={mode!r}")
        head = synthesis_text[:900]
        if "ENFORCE is live" in head and "shadow" not in head:
            errors.append(f"{label}: verdict claims ENFORCE live — disk={mode!r}")
    elif mode == "enforce":
        if "| Gate mode | **shadow** |" in synthesis_text:
            errors.append(f"{label}: Live results Gate mode stale — disk={mode!r}")
    if f"**{mode}**" not in synthesis_text and f"= {mode}" not in synthesis_text:
        errors.append(f"{label}: missing current gate_mode {mode!r} in synthesis")
    return errors


def _append_log(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_gate_ssot(*, row: dict, validation: dict) -> None:
    GATE_SSOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": GATE_SCHEMA,
        "generated_at": _now(),
        "path": str(GATE_SSOT_PATH),
        "latest": {
            **row,
            "readiness_score": validation.get("readiness_score"),
            "gate_eligible": validation.get("gate_eligible"),
            "missing_for_gate": validation.get("missing_for_gate"),
            "modes": ["off", "shadow", "enforce"],
            "current_mode": current_gate_mode(),
            "shadow_log": str(SHADOW_LOG),
            "enforce_log": str(ENFORCE_LOG),
            "choke_law": "assemble → validate_packet → dispatch (agent_loop planner first)",
        },
    }
    GATE_SSOT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def prepare_packet(*, task_id: str, repo_root: str = "", query_text: str = "") -> dict[str, Any]:
    from pre_llm.context_packet.schema import empty_packet_template, hydrate_from_disk_substrate, validate_packet  # noqa: WPS433

    if query_text.strip():
        try:
            from pre_llm.context_assembly.assembly_engine import run_context_assembly  # noqa: WPS433

            assembled = run_context_assembly(
                text=query_text,
                repo_root=repo_root or None,
                task_id=task_id or "dispatch-stub",
                force_refresh=False,
            )
            if assembled.get("ok") and assembled.get("packet"):
                pkt = assembled["packet"]
                check = assembled.get("validation") or validate_packet(pkt)
                pkt["readiness"] = {
                    **(pkt.get("readiness") or {}),
                    "score": check.get("readiness_score"),
                    "gate_eligible": check.get("gate_eligible"),
                    "missing_for_gate": check.get("missing_for_gate"),
                }
                return {"packet": pkt, "validation": check}
        except Exception:
            pass

    pkt = empty_packet_template(task_id=task_id or "dispatch-stub", repo_root=repo_root)
    pkt = hydrate_from_disk_substrate(pkt)
    check = validate_packet(pkt)
    pkt["readiness"] = {
        **(pkt.get("readiness") or {}),
        "score": check.get("readiness_score"),
        "gate_eligible": check.get("gate_eligible"),
        "missing_for_gate": check.get("missing_for_gate"),
    }
    return {"packet": pkt, "validation": check}


def gate_decision(validation: dict) -> dict[str, Any]:
    mode = current_gate_mode()
    eligible = bool(validation.get("gate_eligible"))
    if mode == "off":
        return {"allowed": True, "mode": mode, "reason": "gate_off", "gate_eligible": eligible}
    if mode == "shadow":
        return {"allowed": True, "mode": mode, "reason": "shadow_log_only", "gate_eligible": eligible}
    if mode == "enforce" and not eligible:
        return {
            "allowed": False,
            "mode": mode,
            "reason": "gate_eligible_false",
            "gate_eligible": eligible,
            "missing_for_gate": validation.get("missing_for_gate") or [],
        }
    return {"allowed": True, "mode": mode, "reason": "gate_pass", "gate_eligible": eligible}


def infer_provider_for_model(model_id: str) -> str:
    mid = (model_id or "").strip()
    if not mid:
        return ""
    if mid in FORGE_MODEL_CATALOG:
        return FORGE_MODEL_CATALOG[mid]["provider"]
    if mid.startswith("gpt-") or mid.startswith("openai-") or mid.startswith("o1"):
        return "openai"
    if mid.startswith("claude-"):
        return "anthropic_direct"
    if "/" in mid:
        return "openrouter"
    return "gemini_direct"


def resolve_explicit_model(model_id: str) -> dict[str, Any]:
    """Lock execution to a UI-selected model — bypasses T0–T4 cost intelligence routing."""
    mid = (model_id or "").strip()
    if mid in FORGE_DISABLED_MODELS:
        mid = FORGE_DEFAULT_MODEL
    if not mid:
        return {
            "explicit": False,
            "forge_model_id": "",
            "model_id": "",
            "api_model": "",
            "provider": "",
            "bypass_tier_routing": False,
        }
    entry = FORGE_MODEL_CATALOG.get(mid, {})
    provider = entry.get("provider") or infer_provider_for_model(mid)
    api_model = entry.get("api_model") or mid
    return {
        "explicit": True,
        "forge_model_id": mid,
        "model_id": mid,
        "api_model": api_model,
        "provider": provider,
        "label": entry.get("label") or mid,
        "subtitle": entry.get("subtitle") or "",
        "group": entry.get("group") or "",
        "tier_hint": entry.get("tier_hint") or "",
        "bypass_tier_routing": True,
        "tier_routing": "bypassed",
    }


def forge_models_payload(*, keys: dict[str, str] | None = None) -> dict[str, Any]:
    if keys is None:
        try:
            import sys

            sys.path.insert(0, str(ROOT / "scripts"))
            from ai_unify_api_v1 import load_keys  # noqa: WPS433

            keys = load_keys()
        except Exception:
            keys = {}

    models = []
    for m in FORGE_MODEL_MATRIX:
        prov = m["provider"]
        avail = model_available(m["id"], keys)
        models.append(
            {
                "id": m["id"],
                "label": m["label"],
                "subtitle": m.get("subtitle") or "",
                "group": m.get("group") or "",
                "provider": prov,
                "api_model": m.get("api_model") or m["id"],
                "tier_hint": m.get("tier_hint") or "",
                "use_roles": m.get("use_roles") or [],
                "cost_band": m.get("cost_band") or "",
                "available": avail,
            }
        )
    groups = [
        {
            "name": group,
            "models": [row for row in models if row["group"] == group],
        }
        for group in FORGE_MODEL_GROUPS
    ]
    matrix = _load_roi_matrix()
    roles_out = []
    for role_id, spec in (matrix.get("roles") or {}).items():
        pick = pick_roi_model(role_id, keys)
        roles_out.append(
            {
                "id": role_id,
                "label": spec.get("label") or role_id,
                "hint": spec.get("hint") or "",
                "default_model": pick,
                "available": model_available(pick, keys),
            }
        )
    return {
        "schema": "forge-terminal-models-v2",
        "models": models,
        "groups": groups,
        "roles": roles_out,
        "default_model": pick_forge_default_model(keys),
        "default_role": FORGE_DEFAULT_ROLE,
        "roi_matrix_path": str(ROI_MATRIX_PATH),
        "keys_ready": {
            "gemini": provider_key_ready("gemini_direct", keys),
            "openrouter": provider_key_ready("openrouter", keys),
            "openai": provider_key_ready("openai", keys),
            "anthropic": provider_key_ready("anthropic_direct", keys),
        },
    }


def gate_status_payload(*, task_id: str = "", repo_root: str = "", query_text: str = "") -> dict[str, Any]:
    prep = prepare_packet(task_id=task_id or "gate-status", repo_root=repo_root, query_text=query_text)
    val = prep["validation"]
    decision = gate_decision(val)
    return {
        "ok": True,
        "schema": GATE_SCHEMA,
        "api": "/api/model-dispatch-gate-v1",
        "path": str(GATE_SSOT_PATH),
        "producer": "D15.1",
        "current_mode": current_gate_mode(),
        "decision": decision,
        "validation": val,
        "packet_readiness": prep["packet"].get("readiness"),
    }


def dispatch_chat(
    *,
    system: str,
    user: str,
    chat_fn: Callable[[str, str], tuple[bool, str]],
    task_id: str = "",
    repo_root: str = "",
    source: str = "hub",
    model_id: str = "",
    explicit_model: bool = False,
) -> dict[str, Any]:
    """Shadow/enforce wrapper around a chat completion callable."""
    locked = resolve_explicit_model(model_id) if explicit_model and model_id else {"explicit": False}
    if locked.get("explicit"):
        decision = {
            "allowed": True,
            "mode": current_gate_mode(),
            "reason": "explicit_model_lock",
            "gate_eligible": True,
            "bypass_tier_routing": True,
            "model_id": locked["forge_model_id"],
            "api_model": locked.get("api_model") or locked["forge_model_id"],
            "provider": locked["provider"],
        }
        val: dict[str, Any] = {
            "readiness_score": 1.0,
            "gate_eligible": True,
            "missing_for_gate": [],
            "explicit_model": True,
            "tier_routing": "bypassed",
        }
        row = {
            "at": _now(),
            "source": source,
            "task_id": task_id,
            "readiness_score": val.get("readiness_score"),
            "gate_eligible": True,
            "missing_for_gate": [],
            "mode": decision.get("mode"),
            "allowed": True,
            "reason": decision.get("reason"),
            "model_id": locked["forge_model_id"],
            "api_model": locked.get("api_model"),
        }
        _append_log(SHADOW_LOG, row)
        _write_gate_ssot(row=row, validation=val)
        ok, raw = chat_fn(system, user)
        return {
            "ok": ok,
            "blocked": False,
            "gate": decision,
            "validation": val,
            "response": raw,
            "model": locked["forge_model_id"],
            "api_model": locked.get("api_model"),
            "provider": locked["provider"],
        }

    prep = prepare_packet(task_id=task_id, repo_root=repo_root, query_text=user)
    val = prep["validation"]
    decision = gate_decision(val)
    row = {
        "at": _now(),
        "source": source,
        "task_id": task_id,
        "readiness_score": val.get("readiness_score"),
        "gate_eligible": val.get("gate_eligible"),
        "missing_for_gate": val.get("missing_for_gate"),
        "mode": decision.get("mode"),
        "allowed": decision.get("allowed"),
        "reason": decision.get("reason"),
    }
    if decision.get("mode") == "shadow":
        _append_log(SHADOW_LOG, row)
    if decision.get("mode") == "enforce" and not decision.get("allowed"):
        _append_log(ENFORCE_LOG, row)
    _write_gate_ssot(row=row, validation=val)

    if not decision.get("allowed"):
        return {
            "ok": False,
            "blocked": True,
            "gate": decision,
            "validation": val,
            "message": "Model call blocked — packet not gate-eligible",
        }

    ok, raw = chat_fn(system, user)
    return {
        "ok": ok,
        "blocked": False,
        "gate": decision,
        "validation": val,
        "response": raw,
    }
