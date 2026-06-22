#!/usr/bin/env python3
"""Forge-v0.1 deterministic engine — cloud plane (Railway FBE worker).

Mirrors labs/forge-v0.1/forge_v01_engine.ts · no Mac disk writes.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCORING_PATH = ROOT / "data" / "forge-scoring-ssot-v01.json"
BLUEPRINTS_PATH = ROOT / "data" / "forge-real-blueprints-v01.json"


def forge_output_path(root: Path | None = None) -> Path:
    base = root or ROOT
    return base / "receipts" / "forge_v0.1_output.json"

DEDUP_SIMILARITY_THRESHOLD = 85


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def load_scoring_config(path: Path | None = None) -> dict[str, Any]:
    return _read_json(path or SCORING_PATH)


def load_real_blueprints(path: Path | None = None) -> list[dict[str, Any]]:
    doc = _read_json(path or BLUEPRINTS_PATH)
    return list(doc.get("blueprints") or [])


def stable_stringify(value: Any) -> str:
    if value is None or not isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, list):
        return "[" + ",".join(stable_stringify(v) for v in value) + "]"
    obj = value
    keys = sorted(obj.keys())
    return "{" + ",".join(json.dumps(k) + ":" + stable_stringify(obj[k]) for k in keys) + "}"


def signature_hash(blueprint: dict[str, Any]) -> str:
    return stable_stringify({"inputs": blueprint.get("inputs"), "outputs": blueprint.get("outputs")})


def io_similarity_percent(a: dict[str, Any], b: dict[str, Any]) -> float:
    ha = signature_hash(a)
    hb = signature_hash(b)
    if ha == hb:
        return 100.0
    ta = set(re.findall(r"[a-z0-9]{2,}", ha.lower()))
    tb = set(re.findall(r"[a-z0-9]{2,}", hb.lower()))
    if not ta and not tb:
        return 100.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return (inter / union * 100.0) if union else 0.0


def is_valid_blueprint(raw: Any) -> bool:
    if not isinstance(raw, dict):
        return False
    for key in ("id", "schema_version", "destination_repo", "validation_rule"):
        val = raw.get(key)
        if not isinstance(val, str) or not val.strip():
            return False
    if raw.get("inputs") is None or raw.get("outputs") is None:
        return False
    if not isinstance(raw["inputs"], (dict, list)):
        return False
    if not isinstance(raw["outputs"], (dict, list)):
        return False
    return True


def stage_validate(raw_blueprints: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    valid: list[dict[str, Any]] = []
    malformed_ids: list[str] = []
    for raw in raw_blueprints:
        if is_valid_blueprint(raw):
            valid.append(raw)
        else:
            pid = raw.get("id") if isinstance(raw, dict) else "(unknown)"
            malformed_ids.append(str(pid))
    return valid, malformed_ids


def _matches_already_implemented(blueprint: dict[str, Any], scoring: dict[str, Any]) -> bool:
    pid = str(blueprint.get("id") or "")
    if pid in (scoring.get("already_implemented_plan_ids") or []):
        return True
    blob = stable_stringify(blueprint)
    for sig in scoring.get("already_implemented_signatures") or []:
        if sig in blob:
            return True
    impl_sig = (blueprint.get("inputs") or {}).get("implementation_signature")
    if impl_sig and impl_sig in (scoring.get("already_implemented_signatures") or []):
        return True
    return False


def stage_dedup(
    valid: list[dict[str, Any]], scoring: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    unique: list[dict[str, Any]] = []
    duplicate_ids: list[str] = []
    already_have_ids: list[str] = []
    threshold = float(scoring.get("dedup_similarity_threshold") or DEDUP_SIMILARITY_THRESHOLD)

    for blueprint in valid:
        if _matches_already_implemented(blueprint, scoring):
            already_have_ids.append(str(blueprint.get("id") or ""))
            continue
        is_dupe = False
        for kept in unique:
            if kept.get("destination_repo") != blueprint.get("destination_repo"):
                continue
            if signature_hash(kept) == signature_hash(blueprint):
                is_dupe = True
                break
            if io_similarity_percent(kept, blueprint) >= threshold:
                is_dupe = True
                break
        if is_dupe:
            duplicate_ids.append(str(blueprint.get("id") or ""))
        else:
            unique.append(blueprint)
    return unique, duplicate_ids, already_have_ids


def _blob(blueprint: dict[str, Any]) -> str:
    return stable_stringify(blueprint)


def _has_vague(blueprint: dict[str, Any], scoring: dict[str, Any]) -> bool:
    blob = _blob(blueprint).lower()
    for pat in scoring.get("vague_keyword_patterns") or []:
        if pat.lower() in blob:
            return True
    return False


def _pattern_adjustment(text: str, scoring: dict[str, Any]) -> int:
    t = text.lower()
    adj = 0
    for row in scoring.get("score_boost_patterns") or []:
        if str(row.get("pattern") or "").lower() in t:
            adj += int(row.get("points") or 0)
    for row in scoring.get("score_penalty_patterns") or []:
        if str(row.get("pattern") or "").lower() in t:
            adj -= int(row.get("points") or 0)
    return adj


def _tier_adjustment(blueprint: dict[str, Any], scoring: dict[str, Any]) -> int:
    tier = str((blueprint.get("inputs") or {}).get("tier") or "")
    tier_map = scoring.get("tier_score") or {}
    return int(tier_map.get(tier) or 0)


def score_blueprint(blueprint: dict[str, Any], scoring: dict[str, Any]) -> dict[str, Any]:
    score = 0
    caps = set(scoring.get("core_capabilities") or [])
    probs = set(scoring.get("client_problems") or [])
    blob = _blob(blueprint)
    action = str((blueprint.get("inputs") or {}).get("action") or blueprint.get("notes") or "")

    core_cap = str(blueprint.get("core_capability") or "") in caps or any(c in blob for c in caps)
    client_prob = str(blueprint.get("client_problem") or "") in probs or any(p in blob for p in probs)
    minimal_deps = len(blueprint.get("dependencies") or []) <= 1
    vague = _has_vague(blueprint, scoring)
    already = _matches_already_implemented(blueprint, scoring)
    pattern_adj = _pattern_adjustment(action, scoring)
    tier_adj = _tier_adjustment(blueprint, scoring)

    if core_cap:
        score += 10
    if client_prob:
        score += 10
    if minimal_deps:
        score += 10
    if vague:
        score -= 15
    if already:
        score -= 15
    score += pattern_adj + tier_adj

    out = dict(blueprint)
    out["score"] = score
    out["score_breakdown"] = {
        "core_capability": core_cap,
        "client_problem": client_prob,
        "minimal_dependencies": minimal_deps,
        "vague_keywords": vague,
        "already_implemented": already,
        "pattern_adjustment": pattern_adj,
        "tier_adjustment": tier_adj,
    }
    return out


def stage_rank(scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(scored, key=lambda r: (-int(r.get("score") or 0), str(r.get("id") or "")))


def stage_route(ranked: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    routed: dict[str, list[dict[str, Any]]] = {}
    for row in ranked:
        repo = str(row.get("destination_repo") or "unknown")
        routed.setdefault(repo, []).append(row)
    return routed


def _human_line(row: dict[str, Any]) -> str:
    inputs = row.get("inputs") or {}
    action = inputs.get("action") or row.get("notes") or ""
    return (
        f"{row.get('id')} score={row.get('score')} "
        f"[{inputs.get('workstream')}|{inputs.get('competitor') or 'mac'}] "
        f"{str(action)[:100]}"
    )


def format_forge_run_summary(funnel: dict[str, int]) -> str:
    return (
        f"Forge Run Summary: {funnel['totalIn']} in -> {funnel['dupesDropped']} dupes dropped -> "
        f"{funnel['malformedDropped']} malformed dropped -> {funnel['alreadyHaveDropped']} already-have dropped -> "
        f"{funnel['validRemaining']} valid remaining -> Top 10 ranked & routed."
    )


def run_forge_v01_engine(
    raw_blueprints: list[Any],
    *,
    scoring: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if len(raw_blueprints) != 100:
        raise ValueError(f"Forge-v0.1 requires exactly 100 blueprints, received {len(raw_blueprints)}")

    cfg = scoring or load_scoring_config()
    valid, malformed_ids = stage_validate(raw_blueprints)
    unique, duplicate_ids, already_have_ids = stage_dedup(valid, cfg)
    scored = [score_blueprint(b, cfg) for b in unique]
    ranked = stage_rank(scored)
    routed = stage_route(ranked)

    funnel = {
        "totalIn": len(raw_blueprints),
        "dupesDropped": len(duplicate_ids),
        "malformedDropped": len(malformed_ids),
        "alreadyHaveDropped": len(already_have_ids),
        "validRemaining": len(unique),
    }

    top_10 = ranked[:10]
    return {
        "schema": "forge-v0.1-output",
        "at": _now(),
        "architecture": "A",
        "target_repo": cfg.get("target_repo"),
        "funnel": funnel,
        "summary_line": format_forge_run_summary(funnel),
        "win_test_question": "Are these the 10 you would have picked by hand, or better?",
        "win_test_card": [_human_line(r) for r in top_10],
        "top_10": top_10,
        "routed": routed,
        "all_ranked": ranked,
        "dropped_malformed_ids": malformed_ids,
        "dropped_duplicate_ids": duplicate_ids,
        "dropped_already_have_ids": already_have_ids,
    }


def run_forge_from_disk(*, write_output: bool = True, root: Path | None = None) -> dict[str, Any]:
    base = root or ROOT
    cfg = load_scoring_config(base / "data" / "forge-scoring-ssot-v01.json")
    cfg = _merge_live_receipts(cfg, base)
    blueprints = load_real_blueprints(base / "data" / "forge-real-blueprints-v01.json")
    result = run_forge_v01_engine(blueprints, scoring=cfg)
    if write_output:
        _write_json(forge_output_path(base), result)
    return result


def _merge_live_receipts(cfg: dict[str, Any], root: Path) -> dict[str, Any]:
    """Upgrade: extend already-have set from live cloud receipt index (Architecture A)."""
    idx_path = root / "receipts" / "index.json"
    if not idx_path.is_file():
        return cfg
    idx = _read_json(idx_path)
    merged = dict(cfg)
    ids = list(merged.get("already_implemented_plan_ids") or [])
    seen = set(ids)
    for row in idx.get("receipts") or []:
        pid = str(row.get("plan_id") or "")
        if not pid.startswith("CLOUD-SEC-"):
            continue
        if row.get("status") != "PASS":
            continue
        action = ""
        for bp in load_real_blueprints(root / "data" / "forge-real-blueprints-v01.json"):
            if bp.get("id") == pid:
                action = str((bp.get("inputs") or {}).get("action") or "").lower()
                break
        if action.startswith("fetch ") or action.startswith("capture ") or action.startswith("document "):
            if pid not in seen:
                ids.append(pid)
                seen.add(pid)
    merged["already_implemented_plan_ids"] = ids
    return merged


def run_win_test(result: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    funnel = result.get("funnel") or {}
    top_10 = result.get("top_10") or []
    all_ranked = result.get("all_ranked") or []

    accounted = (
        int(funnel.get("validRemaining") or 0)
        + int(funnel.get("malformedDropped") or 0)
        + int(funnel.get("dupesDropped") or 0)
        + int(funnel.get("alreadyHaveDropped") or 0)
    )
    if accounted != int(funnel.get("totalIn") or 0):
        errors.append(f"Funnel arithmetic failed: {accounted} != {funnel.get('totalIn')}")

    if len(top_10) != 10:
        errors.append(f"Expected top_10 length 10, got {len(top_10)}")

    if top_10 and len(all_ranked) > 10:
        min_top = min(int(r.get("score") or 0) for r in top_10)
        max_rest = max(int(r.get("score") or 0) for r in all_ranked[10:])
        if min_top < max_rest:
            errors.append(f"min top-10 score {min_top} < max lower-ranked {max_rest}")

    return {"ok": not errors, "errors": errors}
