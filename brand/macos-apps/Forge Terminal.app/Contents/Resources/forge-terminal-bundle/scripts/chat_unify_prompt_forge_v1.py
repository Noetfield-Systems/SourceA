#!/usr/bin/env python3
"""Chat Unify — Prompt Forge machine (#3): founder language → SSOT Cursor mission.

Stages: lint · extract · compile · emit
Receipt: ~/.sina/prompt-forge-receipts/prompt-forge-<stamp>-v1.json
         ~/.sina/chat-unify-prompt-forge-v1.json (latest)
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
LATEST_RECEIPT = SINA / "chat-unify-prompt-forge-v1.json"
RECEIPT_DIR = SINA / "prompt-forge-receipts"
MACHINE_VERSION = "1.0.0"

STAGE_ORDER = ("lint", "extract", "compile", "emit")
STAGE_DEPENDS: dict[str, str | None] = {
    "lint": None,
    "extract": "lint",
    "compile": "extract",
    "emit": "compile",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _findings_text(findings: list) -> str:
    if not findings:
        return "No lint warnings — input looks scoped."
    lines = []
    for f in findings:
        level = getattr(f, "level", f.get("level") if isinstance(f, dict) else "note")
        msg = getattr(f, "message", f.get("message") if isinstance(f, dict) else str(f))
        lines.append(f"[{str(level).upper()}] {msg}")
    return "\n".join(lines)


def _stage_lint(text: str) -> dict:
    from prompt_forge_pipeline_v1 import lint  # noqa: WPS433

    findings = lint(text)
    return {
        "ok": True,
        "method": "policy_lint",
        "findings": [
            {"level": f.level, "code": f.code, "message": f.message} for f in findings
        ],
        "finding_count": len(findings),
        "text": _findings_text(findings),
    }


def _stage_extract(text: str) -> dict:
    from prompt_forge_pipeline_v1 import detect_mode, extract_facts  # noqa: WPS433

    mode = detect_mode(text)
    facts = extract_facts(text)
    summary = [
        f"Mode: {mode}",
        f"Systems: {', '.join(facts.get('systems') or []) or '—'}",
        f"URLs: {len(facts.get('urls') or [])}",
        f"Already-done hints: {len(facts.get('already_done') or [])}",
    ]
    return {
        "ok": True,
        "method": "policy_extract",
        "mode": mode,
        "facts": facts,
        "text": "\n".join(summary),
    }


def _stage_compile(text: str, *, use_ai: bool) -> dict:
    from prompt_forge_pipeline_v1 import PromptForge  # noqa: WPS433

    forge = PromptForge()
    result = forge.run(text, use_llm=use_ai if use_ai else None)
    return {
        "ok": bool(result.prompt),
        "method": "openrouter" if result.used_llm else "deterministic",
        "mode": result.mode,
        "used_llm": result.used_llm,
        "prompt": result.prompt,
        "findings": [
            {"level": f.level, "code": f.code, "message": f.message} for f in result.findings
        ],
        "text": result.prompt,
        "forge_version": result.version,
    }


def _write_receipt(payload: dict) -> str | None:
    try:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = RECEIPT_DIR / f"prompt-forge-{stamp}-v1.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        LATEST_RECEIPT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return str(path)
    except OSError:
        return None


def _stage_emit(*, compile_stage: dict, founder_text: str, run_id: str) -> dict:
    prompt = (compile_stage.get("prompt") or compile_stage.get("text") or "").strip()
    if not prompt:
        return {"ok": False, "error": "empty_prompt", "text": "Compile stage produced no prompt."}
    payload = {
        "schema": "chat-unify-prompt-forge-v1",
        "ok": True,
        "at": _now(),
        "run_id": run_id,
        "pipeline": "prompt_forge",
        "machine_version": MACHINE_VERSION,
        "founder_text_preview": founder_text[:400],
        "mode": compile_stage.get("mode"),
        "used_llm": compile_stage.get("used_llm"),
        "method": compile_stage.get("method"),
        "prompt": prompt,
        "prompt_chars": len(prompt),
        "contact": "forge@sourcea.app",
    }
    receipt_path = _write_receipt(payload)
    return {
        "ok": True,
        "method": "disk_emit",
        "receipt_path": receipt_path,
        "prompt": prompt,
        "text": f"Receipt: {receipt_path or 'memory only'}\n\n--- COPY TO CURSOR ---\n\n{prompt}",
    }


def run_prompt_forge_loop(
    *,
    founder_text: str = "",
    use_ai: bool = False,
    write_receipt: bool = True,
) -> dict:
    text = (founder_text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_text", "message": "Paste founder language first."}
    run_id = f"pf-{uuid.uuid4().hex[:12]}"
    kernel: dict | None = None
    stages: dict[str, Any] = {}
    for sid in STAGE_ORDER:
        row = run_prompt_forge_stage(
            sid,
            founder_text=text,
            use_ai=use_ai,
            kernel=kernel,
            run_id=run_id,
            write_receipt=write_receipt and sid == "emit",
        )
        if not row.get("ok"):
            return row
        kernel = row.get("kernel") if isinstance(row.get("kernel"), dict) else kernel
        stages = row.get("stages") or stages
    compile_st = stages.get("compile") or {}
    emit_st = stages.get("emit") or {}
    return {
        "ok": True,
        "run_id": run_id,
        "pipeline": "prompt_forge",
        "machine_version": MACHINE_VERSION,
        "stages": stages,
        "prompt": compile_st.get("prompt") or emit_st.get("prompt"),
        "receipt_path": emit_st.get("receipt_path"),
        "mode": compile_st.get("mode"),
        "used_llm": compile_st.get("used_llm"),
    }


def run_prompt_forge_stage(
    stage: str,
    *,
    founder_text: str = "",
    use_ai: bool = False,
    kernel: dict | None = None,
    run_id: str | None = None,
    write_receipt: bool = True,
) -> dict:
    from chat_unify_kernel_v1 import ensure_kernel, merge_stage_output, save_kernel  # noqa: WPS433

    sid = (stage or "").strip().lower()
    if sid not in STAGE_ORDER:
        return {"ok": False, "error": "unknown_stage", "message": f"Unknown stage: {stage}"}

    text = (founder_text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_text", "message": "Paste founder language first."}

    k = ensure_kernel(
        loop="prompt_forge",
        draft=text,
        founder_message="",
        run_id=run_id,
        kernel=kernel,
    )
    out_stages: dict = dict(k.get("stages") or {})
    dep = STAGE_DEPENDS.get(sid)
    if dep and dep not in out_stages:
        return {
            "ok": False,
            "error": "dependency_blocked",
            "blocked_by": dep,
            "stage": sid,
            "message": f"{sid} blocked — complete {dep} first.",
            "stages": out_stages,
            "run_id": k.get("run_id"),
        }

    rid = k.get("run_id") or run_id or f"pf-{uuid.uuid4().hex[:12]}"
    k["run_id"] = rid

    if sid == "lint":
        out_stages["lint"] = _stage_lint(text)
        stage_ok = bool(out_stages["lint"].get("ok"))
    elif sid == "extract":
        out_stages["extract"] = _stage_extract(text)
        stage_ok = bool(out_stages["extract"].get("ok"))
    elif sid == "compile":
        out_stages["compile"] = _stage_compile(text, use_ai=use_ai)
        stage_ok = bool(out_stages["compile"].get("ok"))
    elif sid == "emit":
        compile_st = out_stages.get("compile") or _stage_compile(text, use_ai=use_ai)
        out_stages["compile"] = compile_st
        if not compile_st.get("ok"):
            return {
                "ok": False,
                "error": "compile_blocked",
                "message": "Emit blocked — compile failed.",
                "stages": out_stages,
                "run_id": rid,
            }
        out_stages["emit"] = _stage_emit(
            compile_stage=compile_st,
            founder_text=text,
            run_id=rid,
        ) if write_receipt else {
            "ok": True,
            "method": "preview",
            "prompt": compile_st.get("prompt"),
            "text": compile_st.get("prompt") or "",
        }
        stage_ok = bool(out_stages["emit"].get("ok"))
    else:
        stage_ok = False

    merge_stage_output(k, out_stages)
    save_kernel(k)

    compile_st = out_stages.get("compile") or {}
    emit_st = out_stages.get("emit") or {}
    return {
        "ok": stage_ok,
        "stage": sid,
        "stages": out_stages,
        "run_id": rid,
        "pipeline": "prompt_forge",
        "machine_version": MACHINE_VERSION,
        "prompt": compile_st.get("prompt") or emit_st.get("prompt"),
        "receipt_path": emit_st.get("receipt_path"),
        "mode": compile_st.get("mode") or out_stages.get("extract", {}).get("mode"),
        "used_llm": compile_st.get("used_llm"),
        "kernel": k,
    }
