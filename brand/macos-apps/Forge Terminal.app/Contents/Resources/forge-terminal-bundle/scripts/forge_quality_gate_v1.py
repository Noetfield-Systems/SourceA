#!/usr/bin/env python3
"""Forge Terminal Quality Engine — 10-layer gate before any execution.

Receipt: ~/.sina/forge-terminal-quality/<run_id>.json
Law: FAIL or REVISE → block send_to_cloud / send_to_cursor / execute until PASS on re-run.

Verdict rules (v1.1):
  - Any CRITICAL_LAYERS fail → REJECT
  - passed_layers >= 9 → PASS (execution_allowed=True)
  - passed_layers >= 7 → REVISE
  - else → REJECT

CRITICAL_LAYERS: functional, model_appropriate, decision_card_valid, user_intent_match, founder_language
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "forge-quality-gate-v1"
QUALITY_ENGINE_VERSION = "1.1"
SINA = Path.home() / ".sina"
QUALITY_DIR = SINA / "forge-terminal-quality"

LAYER_ORDER = (
    "functional",
    "founder_language",
    "consistency",
    "cost",
    "model_appropriate",
    "workspace_context_fit",
    "determinism",
    "reproducibility",
    "compression_score",
    "decision_card_valid",
    "user_intent_match",
)

LAYER_LABELS = {
    "functional": "Functional output",
    "founder_language": "Founder-readable prose",
    "consistency": "Internal consistency",
    "cost": "Cost bounds",
    "model_appropriate": "Model appropriateness",
    "workspace_context_fit": "Workspace context fit",
    "determinism": "Deterministic run identity",
    "reproducibility": "Reproducible metadata",
    "compression_score": "Compression score",
    "decision_card_valid": "Decision card validity",
    "user_intent_match": "User intent match",
}

CRITICAL_LAYERS = frozenset({
    "functional",
    "founder_language",
    "model_appropriate",
    "decision_card_valid",
    "user_intent_match",
})

_STOP = frozenset(
    "a an the and or to in on for of is it this that with from be by at as".split()
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9][a-z0-9_-]{2,}", (text or "").lower())
    return {w for w in words if w not in _STOP}


def _layer(
    layer_id: str,
    *,
    ok: bool,
    score: int,
    note: str = "",
) -> dict[str, Any]:
    score = max(0, min(100, int(score)))
    return {
        "id": layer_id,
        "name": LAYER_LABELS.get(layer_id, layer_id),
        "ok": bool(ok),
        "score": score,
        "verdict": "PASS" if ok else "FAIL",
        "note": (note or "")[:240],
    }


def _check_functional(*, doc: dict, card: dict, full_llm: bool) -> dict[str, Any]:
    response = str(doc.get("response") or card.get("summary") or "").strip()
    llm = doc.get("llm") or {}
    if full_llm and not llm.get("ok") and not llm.get("skipped"):
        return _layer("functional", ok=False, score=0, note="LLM call failed")
    if len(response) < 8:
        return _layer("functional", ok=False, score=20, note="Response too short")
    if response.lower() in ("ok", "n/a", "none", "error"):
        return _layer("functional", ok=False, score=40, note="Placeholder response")
    return _layer("functional", ok=True, score=100, note="Non-empty actionable response")


def _looks_like_json_blob(text: str) -> bool:
    s = (text or "").strip()
    if not s or s[0] not in "{[":
        return False
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def _check_founder_language(*, response: str) -> dict[str, Any]:
    text = (response or "").strip()
    if not text:
        return _layer("founder_language", ok=False, score=0, note="Empty response")
    if _looks_like_json_blob(text):
        return _layer("founder_language", ok=False, score=25, note="Raw JSON — use founder prose")
    if len(text) > 120 and "." not in text and "\n" not in text:
        return _layer("founder_language", ok=False, score=40, note="No sentence structure")
    return _layer("founder_language", ok=True, score=100, note="Founder-readable prose")


def response_for_display(*, response: str, card: dict) -> str:
    """Prefer summary over raw JSON for UI."""
    summary = str(card.get("summary") or "").strip()
    if _looks_like_json_blob(response) and summary and not _looks_like_json_blob(summary):
        return summary
    if _looks_like_json_blob(response):
        goal = str(card.get("goal") or "").strip()
        if goal:
            return goal
    return response


def _check_consistency(*, founder: str, card: dict, response: str) -> dict[str, Any]:
    blob = f"{founder}\n{response}\n{card.get('goal') or ''}".lower()
    neg = bool(re.search(r"\b(cannot|impossible|unable to|won't work|no way)\b", response.lower()))
    pos_ask = bool(re.search(r"\b(create|build|add|fix|implement|design|list|show)\b", founder.lower()))
    if neg and pos_ask and len(response) < 200:
        return _layer("consistency", ok=False, score=35, note="Response contradicts build intent")
    if card.get("risk") == "high" and "payment" not in blob and "secret" not in blob:
        return _layer("consistency", ok=False, score=50, note="High risk without signal in text")
    return _layer("consistency", ok=True, score=92, note="Goal and response aligned")


def _check_cost(*, card: dict, full_llm: bool) -> dict[str, Any]:
    cost = float(card.get("cost_usd") or 0)
    if not full_llm:
        return _layer("cost", ok=True, score=100, note="No live LLM — cost N/A")
    if cost <= 0:
        return _layer("cost", ok=False, score=30, note="Zero cost with live LLM")
    if cost > 5.0:
        return _layer("cost", ok=False, score=40, note="Cost estimate above $5 cap")
    return _layer("cost", ok=True, score=95, note=f"${cost:.2f} within bounds")


def _check_model(*, llm: dict, full_llm: bool) -> dict[str, Any]:
    if not full_llm:
        return _layer("model_appropriate", ok=True, score=100, note="Forge-only path")
    provider = str(llm.get("provider") or "").lower()
    model = str(llm.get("model") or "")
    if provider in ("", "forge_only", "none"):
        return _layer("model_appropriate", ok=False, score=0, note="No live model provider")
    if llm.get("blocked"):
        return _layer("model_appropriate", ok=False, score=20, note="Model dispatch blocked")
    if not model:
        return _layer("model_appropriate", ok=False, score=50, note="Model id missing")
    return _layer("model_appropriate", ok=True, score=100, note=f"{provider}/{model}")


def _check_workspace(*, doc: dict, workspace_path: str | None) -> dict[str, Any]:
    forge = doc.get("forge") or {}
    ws = (workspace_path or forge.get("workspace") or "").strip()
    if not ws:
        return _layer("workspace_context_fit", ok=False, score=0, note="No workspace bound")
    combined = str(doc.get("response") or "") + str((doc.get("decision_card") or {}).get("cursor_prompt") or "")
    outside = []
    for m in re.finditer(r"(/(?:Users|home|tmp)[^\s`\"']+)", combined):
        p = m.group(1)
        if ws and not p.startswith(ws.rstrip("/")):
            outside.append(p[:60])
    if outside:
        return _layer(
            "workspace_context_fit",
            ok=False,
            score=45,
            note=f"Paths outside workspace: {outside[0]}",
        )
    return _layer("workspace_context_fit", ok=True, score=96, note="Scoped to open folder")


def _check_determinism(*, doc: dict, run_id: str) -> dict[str, Any]:
    rid = run_id or str(doc.get("run_id") or "")
    if not re.match(r"^ft-[a-f0-9]{8,16}$", rid):
        return _layer("determinism", ok=False, score=0, note="Invalid run_id")
    if doc.get("schema") != "forge-terminal-run-v1":
        return _layer("determinism", ok=False, score=40, note="Run schema missing")
    if not doc.get("at"):
        return _layer("determinism", ok=False, score=50, note="Timestamp missing")
    return _layer("determinism", ok=True, score=100, note=rid)


def _check_reproducibility(*, doc: dict) -> dict[str, Any]:
    llm = doc.get("llm") or {}
    forge = doc.get("forge") or {}
    score = 0
    notes = []
    if doc.get("founder_input"):
        score += 25
    else:
        notes.append("no founder_input")
    if llm.get("provider") is not None or llm.get("skipped"):
        score += 25
    else:
        notes.append("no llm meta")
    if forge.get("workspace"):
        score += 25
    else:
        notes.append("no workspace")
    if doc.get("decision_card"):
        score += 25
    else:
        notes.append("no card")
    ok = score >= 75
    return _layer(
        "reproducibility",
        ok=ok,
        score=score,
        note="; ".join(notes) if notes else "Full run metadata",
    )


def _check_compression(*, founder: str, response: str) -> dict[str, Any]:
    fi, fo = max(len(founder), 1), len(response or "")
    ratio = fo / fi
    if fi < 40 and fo > 8000:
        return _layer("compression_score", ok=False, score=30, note="Bloated vs short mission")
    if ratio > 25 and fo > 4000:
        return _layer("compression_score", ok=False, score=45, note=f"Ratio {ratio:.1f}x too high")
    if fo < 20:
        return _layer("compression_score", ok=False, score=35, note="Over-compressed / empty")
    score = 100 if ratio <= 12 else max(60, 100 - int((ratio - 12) * 3))
    return _layer("compression_score", ok=score >= 60, score=score, note=f"{ratio:.1f}x vs input")


def _check_card(*, card: dict) -> dict[str, Any]:
    required = ("goal", "risk", "cursor_prompt", "summary", "decision")
    missing = [k for k in required if not str(card.get(k) or "").strip()]
    if missing:
        return _layer("decision_card_valid", ok=False, score=0, note=f"Missing: {', '.join(missing)}")
    if len(str(card.get("cursor_prompt") or "")) < 8:
        return _layer("decision_card_valid", ok=False, score=40, note="cursor_prompt too short")
    return _layer("decision_card_valid", ok=True, score=100, note="All required fields present")


def _check_intent(*, founder: str, card: dict, response: str) -> dict[str, Any]:
    ft = _tokens(founder)
    rt = _tokens(f"{card.get('goal') or ''} {card.get('summary') or ''} {response}")
    if len(founder.strip()) < 12:
        return _layer("user_intent_match", ok=True, score=90, note="Short mission — auto pass")
    overlap = ft & rt
    if not ft:
        return _layer("user_intent_match", ok=True, score=80, note="No token extract")
    pct = int(100 * len(overlap) / max(len(ft), 1))
    ok = len(overlap) >= 1 or pct >= 25
    return _layer(
        "user_intent_match",
        ok=ok,
        score=max(pct, 55 if ok else pct),
        note=f"{len(overlap)} keyword overlap" if overlap else "No keyword overlap with founder",
    )


def evaluate_quality_gate(
    *,
    run_id: str,
    doc: dict[str, Any],
    workspace_path: str | None = None,
    full_llm: bool = True,
    eval_shadow: bool = False,
) -> dict[str, Any]:
    card = doc.get("decision_card") or {}
    founder = str(doc.get("founder_input") or card.get("founder_input") or "")
    response = str(doc.get("response") or card.get("summary") or "")
    llm = doc.get("llm") or {}

    layers = [
        _check_functional(doc=doc, card=card, full_llm=full_llm),
        _check_founder_language(response=response),
        _check_consistency(founder=founder, card=card, response=response),
        _check_cost(card=card, full_llm=full_llm),
        _check_model(llm=llm, full_llm=full_llm),
        _check_workspace(doc=doc, workspace_path=workspace_path),
        _check_determinism(doc=doc, run_id=run_id),
        _check_reproducibility(doc=doc),
        _check_compression(founder=founder, response=response),
        _check_card(card=card),
        _check_intent(founder=founder, card=card, response=response),
    ]

    layer_ids = [ly["id"] for ly in layers]
    if layer_ids != list(LAYER_ORDER):
        raise ValueError(f"layer order drift: {layer_ids} != {list(LAYER_ORDER)}")

    passed = sum(1 for ly in layers if ly.get("ok"))
    total = len(layers)
    avg_score = int(sum(int(ly.get("score") or 0) for ly in layers) / max(total, 1))
    critical_fail = [ly["id"] for ly in layers if ly["id"] in CRITICAL_LAYERS and not ly.get("ok")]

    if critical_fail:
        verdict = "REJECT"
    elif passed >= 9:
        verdict = "PASS"
    elif passed >= 7:
        verdict = "REVISE"
    else:
        verdict = "REJECT"

    shadow = None
    if eval_shadow and full_llm and founder.strip():
        shadow = _eval_shadow_critic(founder=founder, response=response, card=card)

    out = {
        "schema": SCHEMA,
        "engine_version": QUALITY_ENGINE_VERSION,
        "run_id": run_id,
        "at": _now(),
        "verdict": verdict,
        "passed_layers": passed,
        "total_layers": total,
        "score": avg_score,
        "critical_failures": critical_fail,
        "execution_allowed": verdict == "PASS",
        "layers": layers,
    }
    if shadow:
        out["eval_shadow"] = shadow
    return out


def _eval_shadow_critic(*, founder: str, response: str, card: dict) -> dict[str, Any]:
    """Advisory only — OpenRouter Eval key; never blocks execution."""
    try:
        from ai_unify_api_v1 import chat_openrouter  # noqa: WPS433

        ok, text = chat_openrouter(
            system="You are a quality critic. Reply PASS or REVISE plus one short reason.",
            user=f"Founder mission:\n{founder[:800]}\n\nResponse:\n{response[:1200]}\n\nGoal: {card.get('goal') or ''}",
            model="google/gemini-2.5-flash-lite",
            key_slot="eval",
        )
        verdict = "PASS" if ok and "pass" in text.lower()[:40] else "ADVISORY"
        return {
            "schema": "forge-quality-eval-shadow-v1",
            "ok": ok,
            "verdict": verdict,
            "note": (text or "")[:240],
            "blocks_execution": False,
            "key_slot": "eval",
        }
    except Exception as exc:
        return {
            "schema": "forge-quality-eval-shadow-v1",
            "ok": False,
            "verdict": "SKIP",
            "note": str(exc)[:120],
            "blocks_execution": False,
            "key_slot": "eval",
        }


def quality_receipt_path(run_id: str) -> Path:
    safe = "".join(c for c in run_id if c.isalnum() or c in "-_")
    return QUALITY_DIR / f"{safe}.json"


def write_quality_receipt(result: dict[str, Any]) -> Path:
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    path = quality_receipt_path(str(result.get("run_id") or ""))
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_quality_receipt(run_id: str) -> dict[str, Any]:
    path = quality_receipt_path(run_id)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def execution_allowed(doc: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    gate = doc.get("quality_gate") or load_quality_receipt(str(doc.get("run_id") or ""))
    if not gate:
        return False, {"error": "quality_gate_missing", "hint": "Re-run mission to evaluate quality gate."}
    if not gate.get("execution_allowed"):
        return False, {
            "error": "quality_gate_blocked",
            "verdict": gate.get("verdict"),
            "passed_layers": gate.get("passed_layers"),
            "critical_failures": gate.get("critical_failures"),
            "hint": "Fix mission and re-run, or address failed quality layers.",
            "quality_gate": gate,
        }
    return True, gate


def apply_gate_to_decision_card(card: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    card = dict(card)
    card["quality_gate"] = {
        "verdict": gate.get("verdict"),
        "passed_layers": gate.get("passed_layers"),
        "total_layers": gate.get("total_layers"),
        "score": gate.get("score"),
        "execution_allowed": gate.get("execution_allowed"),
        "layers": gate.get("layers"),
        "eval_shadow": gate.get("eval_shadow"),
    }
    verdict = str(gate.get("verdict") or "")
    if verdict == "REJECT" and card.get("decision") == "pending":
        card["decision"] = "revise"
        card["quality_note"] = "Quality gate REJECT — revise before approve/execute."
    elif verdict == "REVISE" and card.get("decision") == "pending":
        card["decision"] = "revise"
        card["quality_note"] = "Quality gate REVISE — tighten mission or response."
    return card


def validate_receipt_schema(gate: dict[str, Any]) -> tuple[bool, str]:
    """Assert receipt fields for E2E."""
    required = ("schema", "verdict", "execution_allowed", "layers", "passed_layers", "total_layers")
    for key in required:
        if key not in gate:
            return False, f"missing:{key}"
    if gate.get("schema") != SCHEMA:
        return False, "bad_schema"
    layers = gate.get("layers") or []
    if len(layers) != len(LAYER_ORDER):
        return False, f"layer_count:{len(layers)}"
    ids = [ly.get("id") for ly in layers]
    if ids != list(LAYER_ORDER):
        return False, f"layer_ids:{ids}"
    return True, ""
