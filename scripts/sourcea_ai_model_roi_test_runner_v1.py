#!/usr/bin/env python3
"""SourceA AI model ROI test runner.

Default mode is dry-run: validate wiring and write receipts without calling
providers. Use --live during a cloud/ship window to score real model output.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/sourcea-ai-model-roi-test-matrix-v1.json"
EVAL_PATH = ROOT / "data/sourcea-ai-model-roi-eval-cases-v1.json"
BRAIN_CONFIG_PATH = ROOT / "sites/SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json"
RECEIPT_DIR = Path.home() / ".sina/sourcea-ai-model-roi-tests"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def model_matches_case(model: dict[str, Any], case: dict[str, Any]) -> bool:
    return case["surface"] in (model.get("surfaces") or []) and case["role"] in (model.get("roles") or [])


def pick_cases(cases: list[dict[str, Any]], surface: str = "", limit: int = 0) -> list[dict[str, Any]]:
    rows = [c for c in cases if not surface or c.get("surface") == surface]
    return rows[:limit] if limit else rows


def pick_models(models: list[dict[str, Any]], model_id: str = "", surface: str = "", limit: int = 0) -> list[dict[str, Any]]:
    rows = [
        m
        for m in models
        if m.get("status") != "candidate_future"
        and (not model_id or m.get("id") == model_id)
        and (not surface or surface in (m.get("surfaces") or []))
    ]
    return rows[:limit] if limit else rows


def score_output(text: str, case: dict[str, Any], *, model_used: str = "") -> tuple[int, list[dict[str, Any]]]:
    score = 20
    checks: list[dict[str, Any]] = []
    low = text.lower()

    includes = [str(x) for x in case.get("must_include_any") or []]
    if includes:
        ok = any(x.lower() in low for x in includes)
        checks.append({"id": "must_include_any", "ok": ok, "terms": includes})
        score += 20 if ok else 0

    forbidden = [str(x) for x in case.get("must_not_include_any") or []]
    if forbidden:
        hits = [x for x in forbidden if x.lower() in low]
        checks.append({"id": "must_not_include_any", "ok": not hits, "hits": hits})
        score += 30 if not hits else 0

    fmt = str(case.get("format") or "")
    if fmt == "terminal_four_sections":
        ok = all(x.lower() in low for x in ["bottom line", "business impact", "blockers", "next step"])
    elif fmt == "model_lock":
        ok = bool(model_used) and str(case.get("requested_model") or "") in model_used
    else:
        ok = len(text.strip()) >= 20
    checks.append({"id": "format", "ok": ok, "format": fmt})
    score += 20 if ok else 0

    if case.get("must_preserve_model_lock"):
        requested = str(case.get("requested_model") or "")
        ok = not requested or requested in model_used
        checks.append({"id": "model_lock", "ok": ok, "requested": requested, "model_used": model_used})
        score += 20 if ok else 0
    else:
        score += 20

    return min(score, 100), checks


def approval_for(score: int, model: dict[str, Any]) -> str:
    if score >= 90 and model.get("status") in {"current_default", "catalog_default"}:
        return "APPROVED_DEFAULT"
    if score >= 80:
        return "APPROVED_SELECTABLE"
    if model.get("cost_band") in {"$$$$"}:
        return "RESTRICTED"
    return "BLOCKED"


def call_brain_worker(model: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    config = load_json(BRAIN_CONFIG_PATH)
    url = str(config.get("api_worker_url") or "")
    body = {
        "message": case["prompt"],
        "model": model["api_model"],
        "product": "forge_terminal" if case["surface"] == "forge_terminal" else "brain",
    }
    data = json.dumps(body).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "SourceA-Model-ROI-Runner/1.0"},
        method="POST",
    )
    with urlopen(req, timeout=35) as resp:
        row = json.loads(resp.read().decode("utf-8"))
    return {
        "ok": bool(row.get("ok", True)),
        "text": str(row.get("reply") or row.get("message") or ""),
        "model_used": str(row.get("model") or model["api_model"]),
        "raw": row,
    }


def call_dispatch(model: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from ai_unify_api_v1 import dispatch_raw  # noqa: WPS433

    system = (
        "You are testing SourceA model ROI. Follow the case contract exactly. "
        "Do not expose internal paths, provider secrets, or implementation details."
    )
    if case.get("surface") == "forge_terminal":
        system += " Reply with sections: Bottom line, Business impact, Blockers, Next step."
    row = dispatch_raw(
        system=system,
        user=str(case["prompt"]),
        provider=str(model["provider"]),
        model=str(model["api_model"]),
        task_id=f"model-roi-{uuid.uuid4().hex[:8]}",
        source="sourcea-ai-model-roi-test-runner",
        light_gate=True,
    )
    return {
        "ok": bool(row.get("ok")),
        "text": str(row.get("text") or row.get("response") or row.get("content") or ""),
        "model_used": str(row.get("model") or model["api_model"]),
        "raw": row,
    }


def execute_case(model: dict[str, Any], case: dict[str, Any], *, live: bool) -> dict[str, Any]:
    started = time.perf_counter()
    if not live:
        return {
            "case_id": case["id"],
            "surface": case["surface"],
            "bucket": case["bucket"],
            "role": case["role"],
            "status": "NOT_EXECUTED",
            "dry_run": True,
            "score": None,
            "approval_status": "CANDIDATE_ONLY",
            "checks": [{"id": "dry_run_only", "ok": True, "detail": "Use --live to score real model output."}],
            "latency_ms": 0,
        }
    try:
        if case["surface"] == "brain_chat":
            out = call_brain_worker(model, case)
        else:
            out = call_dispatch(model, case)
        latency_ms = round((time.perf_counter() - started) * 1000)
        score, checks = score_output(out["text"], case, model_used=out["model_used"])
        return {
            "case_id": case["id"],
            "surface": case["surface"],
            "bucket": case["bucket"],
            "role": case["role"],
            "status": "EXECUTED",
            "dry_run": False,
            "ok": out["ok"],
            "score": score,
            "approval_status": approval_for(score, model),
            "checks": checks,
            "latency_ms": latency_ms,
            "model_used": out["model_used"],
            "sample": out["text"][:600],
        }
    except (OSError, URLError, TimeoutError, ValueError) as exc:
        return {
            "case_id": case["id"],
            "surface": case["surface"],
            "bucket": case["bucket"],
            "role": case["role"],
            "status": "ERROR",
            "dry_run": False,
            "ok": False,
            "score": 0,
            "approval_status": "BLOCKED",
            "checks": [{"id": "execution_error", "ok": False, "detail": str(exc)[:240]}],
            "latency_ms": round((time.perf_counter() - started) * 1000),
        }


def run(*, live: bool, surface: str = "", model_id: str = "", limit_models: int = 0, limit_cases: int = 0) -> dict[str, Any]:
    matrix = load_json(MATRIX_PATH)
    evals = load_json(EVAL_PATH)
    models = pick_models(matrix["models"], model_id=model_id, surface=surface, limit=limit_models)
    cases = pick_cases(evals["cases"], surface=surface, limit=limit_cases)
    run_id = f"model-roi-{uuid.uuid4().hex[:12]}"
    results: list[dict[str, Any]] = []
    for model in models:
        model_cases = [case for case in cases if model_matches_case(model, case)]
        case_results = [execute_case(model, case, live=live) for case in model_cases]
        executed = [r for r in case_results if isinstance(r.get("score"), int)]
        avg_score = round(sum(int(r["score"]) for r in executed) / len(executed), 1) if executed else None
        results.append(
            {
                "model_id": model["id"],
                "provider": model["provider"],
                "api_model": model["api_model"],
                "cost_band": model["cost_band"],
                "roles": model.get("roles") or [],
                "surfaces": model.get("surfaces") or [],
                "dry_run": not live,
                "case_count": len(case_results),
                "executed_count": len(executed),
                "avg_score": avg_score,
                "approval_status": "CANDIDATE_ONLY" if not live else approval_for(int(avg_score or 0), model),
                "cases": case_results,
            }
        )
    receipt = {
        "schema": "sourcea-ai-model-roi-test-receipt-v1",
        "version": "1.0.0",
        "run_id": run_id,
        "at": now(),
        "live": live,
        "surface_filter": surface or None,
        "model_filter": model_id or None,
        "matrix": str(MATRIX_PATH.relative_to(ROOT)),
        "eval_cases": str(EVAL_PATH.relative_to(ROOT)),
        "model_count": len(results),
        "case_count": len(cases),
        "results": results,
        "note": "Dry-run receipts prove wiring only. Live receipts are required for model approval." if not live else "Live run scored model output.",
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{run_id}.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Call providers and score real output.")
    parser.add_argument("--surface", choices=["brain_chat", "forge_terminal", "chat_unify"], default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--limit-models", type=int, default=0)
    parser.add_argument("--limit-cases", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = run(
        live=args.live,
        surface=args.surface,
        model_id=args.model,
        limit_models=args.limit_models,
        limit_cases=args.limit_cases,
    )
    if args.json:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        mode = "LIVE" if args.live else "DRY_RUN"
        print(f"{mode} {receipt['run_id']} models={receipt['model_count']} cases={receipt['case_count']}")
        print(receipt["receipt_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
