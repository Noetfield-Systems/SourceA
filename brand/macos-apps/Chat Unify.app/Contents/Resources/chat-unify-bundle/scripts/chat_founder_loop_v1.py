#!/usr/bin/env python3
"""Chat Unify — founder loop (7 stages · one paste · understand → decide → verify → act → close).

Stages: language · reasoning · proof · action · advisor · critic · close
Receipt: ~/.sina/chat-unify-founder-loop-v1.json
Work-order: ~/.sina/chat-unify-founder-work-order-v1.json (Close step · proposed)
Proof: reads ~/.sina/eval_packet_v1b_report.json when present
"""
from __future__ import annotations

import json
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "chat-unify-founder-loop-v1.json"
WORK_ORDER_RECEIPT = SINA / "chat-unify-founder-work-order-v1.json"
PROGRESS_PATH = SINA / "chat-unify-founder-loop-progress-v1.json"
EVAL_1B_REPORT = SINA / "eval_packet_v1b_report.json"
LOOP_VERSION = "3.0.0"

STAGE_DEPENDS: dict[str, str | None] = {
    "language": None,
    "reasoning": "language",
    "proof": "reasoning",
    "action": "proof",
    "advisor": "action",
    "critic": "advisor",
    "close": "critic",
}

STAGE_ORDER = (
    "language",
    "reasoning",
    "proof",
    "action",
    "advisor",
    "critic",
    "close",
)

ADVISOR_SYSTEM = """You are the founder's senior advisor — calm, direct, no jargon.

Given the agent answer and prior loop stages, write ONE short advisory note.

Structure:
Recommendation
Because
What to ignore for now

Rules: plain English · one clear recommendation · no bash · no validator names · max 120 words."""

CRITIC_SYSTEM = """You are the founder's governance critic — skeptical, fair, not cynical.

Find where the agent may be wrong, vague, or overconfident.

Structure:
Verdict (TRUST / VERIFY / REWRITE)
Findings (bullets, max 4)
Founder line (one sentence)

Rules: plain English · name stale disk vs agent draft · no fake green · max 150 words."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _ai_call(*, system: str, user: str, provider: str = "auto", timeout_sec: int = 22) -> tuple[str, str]:
    try:
        from ai_unify_api_v1 import dispatch_raw, pick_provider  # noqa: WPS433
    except ImportError:
        return "", "none"
    if pick_provider(provider) == "none":
        return "", "none"

    def _run() -> dict:
        return dispatch_raw(
            system=system,
            user=user[:16000],
            provider=provider,
            light_gate=True,
            source="chat-founder-loop",
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            row = pool.submit(_run).result(timeout=timeout_sec)
    except (FutTimeout, Exception):
        return "", "timeout"
    if row.get("ok") and (row.get("response") or "").strip():
        return (row.get("response") or "").strip(), row.get("provider") or "ai"
    return "", "failed"


def _read_eval_1b() -> dict:
    """Eval-1b behavioral proof receipt — execution closure signal."""
    row = _read_json(EVAL_1B_REPORT)
    if row.get("schema") != "eval-packet-v1b":
        return {"present": False, "path": str(EVAL_1B_REPORT)}
    mode = str(row.get("mode") or "unknown")
    ok = bool(row.get("ok"))
    live_ok = row.get("live_ok")
    summary = str(row.get("summary") or "")[:240]
    win_pct = row.get("packet_win_pct") or row.get("scaffold_win_pct")
    if mode == "live" and live_ok is True:
        closure = "Eval-1b LIVE PASS — behavioral proof supports dispatch consideration."
    elif mode == "live" and live_ok is False:
        closure = "Eval-1b LIVE FAIL — do not treat factory dispatch as proven."
    elif mode == "scaffold" and ok:
        closure = "Eval-1b scaffold PASS — proxy only; run live probe before dispatch."
    elif mode == "scaffold":
        closure = "Eval-1b scaffold FAIL — harness/packet weaker than raw on disk tasks."
    else:
        closure = f"Eval-1b on disk ({mode}) — verify live_ok before dispatch."
    return {
        "present": True,
        "path": str(EVAL_1B_REPORT),
        "mode": mode,
        "ok": ok,
        "live_ok": live_ok,
        "live_ready": row.get("live_ready"),
        "summary": summary,
        "packet_win_pct": win_pct,
        "task_count": row.get("task_count"),
        "generated_at": row.get("generated_at"),
        "execution_closure_line": closure,
    }


def _disk_snapshot() -> dict:
    snap: dict = {}
    manifest = ROOT / "infra" / "cleanup" / "cleanup-manifest.md"
    if manifest.is_file():
        body = manifest.read_text(encoding="utf-8", errors="replace")
        snap["cleanup_manifest"] = "FROZEN" if "Batch 4 FROZEN" in body or "FROZEN — Batch 4" in body else "open"
        snap["batch_4"] = "frozen" if "Batch 4 FROZEN" in body else "unknown"
        if "✅ Batch 3.5" in body or "Batch 3.5" in body and "✅" in body:
            snap["batch_3_5"] = "done"
    surfaces = _read_json(SINA / "agent-live-surfaces-v1.json")
    if surfaces.get("factory_now_line"):
        snap["factory_now"] = str(surfaces["factory_now_line"])[:200]
    drift = _read_json(SINA / "governance_drift_report_v1.json")
    if drift.get("drift_score") is not None:
        snap["drift_score"] = drift.get("drift_score")
        snap["drift_items"] = drift.get("drift_items")
    snap["eval_1b"] = _read_eval_1b()
    return snap


def _stage_proof(*, draft: str, founder_message: str) -> dict:
    snap = _disk_snapshot()
    claims: list[str] = []
    low = draft.lower()
    if "batch 4" in low:
        claims.append("Agent mentions Batch 4.")
    if "taxonomy" in low or "option a" in low:
        claims.append("Agent mentions taxonomy decision.")
    if "archive" in low:
        claims.append("Agent mentions archive.")
    if re.search(r"\b(pass|wired|zero drift)\b", low):
        claims.append("Agent uses success/wired language — verify on disk.")

    disk_lines: list[str] = []
    if snap.get("batch_4") == "frozen":
        disk_lines.append("Cleanup manifest on disk: Batch 4 is still FROZEN (needs your APPROVED).")
    if snap.get("batch_3_5") == "done":
        disk_lines.append("Batch 3.5 pointer sync is marked done on manifest.")
    if snap.get("factory_now"):
        disk_lines.append(f"Factory-now line: {snap['factory_now']}")
    elif (SINA / "agent-live-surfaces-v1.json").is_file():
        disk_lines.append("Surfaces file exists but factory_now_line missing — may be stale.")
    else:
        disk_lines.append("No live surfaces receipt read — disk not fully checked.")
    if snap.get("drift_score") is not None:
        disk_lines.append(f"Governance drift score on disk: {snap['drift_score']} · items {snap.get('drift_items', '?')}")

    eval_row = snap.get("eval_1b") or {}
    if eval_row.get("present"):
        disk_lines.append(f"Eval-1b ({eval_row.get('mode')}): {eval_row.get('summary') or 'on disk'}")
        disk_lines.append(eval_row.get("execution_closure_line") or "Eval-1b present.")
    else:
        disk_lines.append("Eval-1b report missing — execution truth gap (no behavioral proof on disk).")

    mismatch: list[str] = []
    if "batch 4" in low and snap.get("batch_4") == "frozen" and re.search(r"\b(execute|run|move|approved)\b", low):
        mismatch.append("Agent may imply Batch 4 can run — manifest still says FROZEN.")
    if re.search(r"\bpass\b.*\bzero drift\b", low) and snap.get("drift_items") not in (0, "0", None):
        mismatch.append("Agent claims zero drift — check drift_items on disk.")
    if re.search(r"\b(dispatch|factory|execute|ship)\b", low) and eval_row.get("present"):
        if eval_row.get("mode") == "live" and eval_row.get("live_ok") is False:
            mismatch.append("Agent implies execution/dispatch — Eval-1b live FAIL on disk.")
        elif eval_row.get("mode") == "scaffold" and not eval_row.get("ok"):
            mismatch.append("Agent implies execution — Eval-1b scaffold FAIL on disk.")
    elif re.search(r"\b(dispatch|factory ready|execution runtime)\b", low) and not eval_row.get("present"):
        mismatch.append("Agent implies execution proof — Eval-1b report not on disk.")
    if not mismatch:
        mismatch.append("No obvious agent-vs-manifest mismatch from local checks.")

    if not eval_row.get("present"):
        fix = "Run Eval-1b (validate-eval-packet-v1b) — Proof needs behavioral receipt before dispatch trust."
    elif eval_row.get("mode") == "scaffold":
        fix = "Eval-1b scaffold only — live probe before treating dispatch as proven."
    elif not snap.get("factory_now"):
        fix = "Sync live wire if factory line looks stale."
    else:
        fix = "Trust manifest + your APPROVED before any batch execute."

    text = "\n".join(
        [
            "Agent claimed",
            " · ".join(claims) if claims else "General agent guidance (no specific batch/taxonomy keywords).",
            "",
            "Disk says",
            "\n".join(f"· {x}" for x in disk_lines),
            "",
            "Mismatch",
            "\n".join(f"· {x}" for x in mismatch),
            "",
            "Fix first",
            fix,
        ]
    )
    return {
        "ok": True,
        "text": text,
        "method": "disk",
        "snapshot": snap,
        "eval_1b": eval_row,
    }


def _build_work_order(
    *,
    founder_message: str,
    action_one: str,
    language: str,
    snap: dict,
    truth_gate: dict | None = None,
) -> dict:
    """Proposed work-order JSON — Brain signs before cloud dispatch (B0901)."""
    wo_id = f"wo-cu-{uuid.uuid4().hex[:12]}"
    decision = founder_message.strip() or action_one
    eval_row = snap.get("eval_1b") or _read_eval_1b()
    dispatch_blocked = False
    dispatch_reason = ""
    if not eval_row.get("present"):
        dispatch_blocked = True
        dispatch_reason = "eval_1b_missing"
    elif eval_row.get("mode") == "live" and eval_row.get("live_ok") is False:
        dispatch_blocked = True
        dispatch_reason = "eval_1b_live_fail"
    elif eval_row.get("mode") == "scaffold" and not eval_row.get("ok"):
        dispatch_blocked = True
        dispatch_reason = "eval_1b_scaffold_fail"

    tg = truth_gate or {}
    if tg.get("dispatch_blocked"):
        dispatch_blocked = True
        dispatch_reason = dispatch_reason or f"truth_gate_{tg.get('action', 'block')}"

    order = {
        "schema": "chat-unify-founder-work-order-v1",
        "fbe_schema": "fbe-work-order-v1",
        "id": wo_id,
        "template_id": "founder-loop-close-v1",
        "origin": "chat_unify_founder_loop",
        "tenant": "wil_ai_design_partner",
        "bay_slug": "founder-loop-proposed",
        "target_tier": "MARKET_READY",
        "brand": "local-brand",
        "locales": ["en-US"],
        "status": "proposed",
        "signed_at": None,
        "created_at": _now(),
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "owner_role": "brain",
        "bounded_action": action_one,
        "founder_decision": decision,
        "intent_line": (language or "")[:500],
        "dispatch_hint": "POST /api/cloud-worker/dispatch/v1",
        "dispatch_blocked": dispatch_blocked,
        "dispatch_block_reason": dispatch_reason or None,
        "law_ref": "data/local-worker-cloud-factory-deprecation-v1.json",
        "proof": {
            "eval_1b": eval_row,
            "truth_gate": tg or None,
            "disk": {
                "batch_4": snap.get("batch_4"),
                "batch_3_5": snap.get("batch_3_5"),
                "factory_now": snap.get("factory_now"),
                "drift_score": snap.get("drift_score"),
                "drift_items": snap.get("drift_items"),
            },
        },
    }
    return order


def _write_work_order(order: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    WORK_ORDER_RECEIPT.write_text(json.dumps(order, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _flush_progress(
    *,
    running: bool,
    current: str | None,
    completed: list[str],
    stages: dict,
    stage_order: list[str],
    error: str | None = None,
) -> None:
    waiting = [s for s in stage_order if s not in completed and s != current]
    row = {
        "schema": "chat-unify-founder-loop-progress-v1",
        "running": running,
        "at": _now(),
        "current_stage": current,
        "completed_stages": completed,
        "waiting_stages": waiting,
        "stage_order": stage_order,
        "depends": STAGE_DEPENDS,
        "stages": stages,
        "error": error,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_loop_progress() -> dict:
    row = _read_json(PROGRESS_PATH)
    if row.get("schema") != "chat-unify-founder-loop-progress-v1":
        return {"ok": True, "running": False, "stages": {}, "completed_stages": []}
    row["ok"] = True
    return row


def _stage_action(*, founder_message: str, language: str, reasoning: str, proof: str) -> dict:
    blob = (founder_message + language + reasoning + proof).lower()
    one = "Pick taxonomy A or B in chat, then mark Batch 4 APPROVED in cleanup manifest when ready."
    if any(k in blob for k in ("charter", "vercel", "deployment protection", "public url", "website", "noindex")):
        one = "Verify production URL in browser — confirm internal doc is blocked or removed; re-run site check receipt."
    elif any(k in blob for k in ("eval", "dispatch", "work-order", "work order", "factory", "cloud worker")):
        one = "Inspect Close work-order JSON — Brain signs before POST /api/cloud-worker/dispatch/v1."
    elif "batch 4" in blob:
        one = "Do not execute Batch 4 until taxonomy is picked and manifest line says APPROVED."
    elif "archive" in blob:
        one = "Draft archive trim batch (grep refs first) — do not delete blind."
    elif "form" in blob or "pick" in blob:
        one = "Complete founder form picks on M1 Canvas — agent must not submit for you."
    not_yet = "No git moves · no bulk archive ignore · no agent-executed batch without your APPROVED."

    text = "\n".join(
        [
            "Do this one thing",
            one,
            "",
            "Do not do yet",
            not_yet,
            "",
            "Tell agent",
            f"Founder order: {one}",
        ]
    )
    return {"ok": True, "text": text, "method": "rules", "one_action": one}


def _stage_advisor(*, draft: str, founder_message: str, prior: str, use_ai: bool) -> dict:
    if use_ai:
        user = f"Founder question: {founder_message}\n\nPrior loop:\n{prior[:8000]}\n\nAgent answer:\n{draft[:6000]}"
        text, prov = _ai_call(system=ADVISOR_SYSTEM, user=user)
        if text:
            return {"ok": True, "text": text, "method": prov}
    text = "\n".join(
        [
            "Recommendation",
            "Finish the cleanup patch tree in order — taxonomy pick, then Batch 4 approve, then execute one batch.",
            "",
            "Because",
            "Moving files before taxonomy picks causes pointer drift again.",
            "",
            "What to ignore for now",
            "Long validator lists and green summaries without manifest APPROVED.",
        ]
    )
    return {"ok": True, "text": text, "method": "rules"}


def _stage_critic(*, draft: str, founder_message: str, prior: str, use_ai: bool) -> dict:
    if use_ai:
        user = f"Founder question: {founder_message}\n\nPrior loop:\n{prior[:8000]}\n\nAgent answer:\n{draft[:6000]}"
        text, prov = _ai_call(system=CRITIC_SYSTEM, user=user)
        if text:
            return {"ok": True, "text": text, "method": prov}
    text = "\n".join(
        [
            "Verdict",
            "VERIFY — treat agent prose as draft until manifest + disk agree.",
            "",
            "Findings",
            "· Agents optimize for sounding complete, not for your APPROVED gate.",
            "· Success words (PASS, wired) need disk proof, not echo.",
            "· Cleanup without grep + manifest rows risks breaking live refs.",
            "",
            "Founder line",
            "One bounded approve-or-defer — not ten parallel fixes.",
        ]
    )
    return {"ok": True, "text": text, "method": "rules"}


def _stage_close(
    *,
    founder_message: str,
    action_one: str,
    language: str,
    snap: dict | None = None,
    truth_gate: dict | None = None,
) -> dict:
    disk = snap if snap is not None else _disk_snapshot()
    decision = founder_message.strip() or action_one
    work_order = _build_work_order(
        founder_message=founder_message,
        action_one=action_one,
        language=language,
        snap=disk,
        truth_gate=truth_gate,
    )
    _write_work_order(work_order)
    wo_json = json.dumps(work_order, indent=2, ensure_ascii=False)
    block_note = ""
    if work_order.get("dispatch_blocked"):
        block_note = (
            f"\nDispatch blocked ({work_order.get('dispatch_block_reason')}) "
            "— Brain must not auto-dispatch until proof + truth gate allow."
        )
    tg = truth_gate or {}
    tg_note = ""
    if tg.get("action"):
        tg_note = f"\nTruth gate: {str(tg.get('action')).upper()} — {tg.get('founder_line', '')}"
    sendback = (
        f"FOUNDER LOOP CLOSE\n"
        f"Decision: {decision}\n"
        f"Next: {action_one}\n"
        f"Agent: execute only this bounded step — manifest-first, no batch without APPROVED."
        f"{block_note}{tg_note}\n\n"
        f"WORK_ORDER_JSON:\n{wo_json}"
    )
    text = "\n".join(
        [
            "Decision captured",
            decision,
            "",
            "Bounded action",
            action_one,
            "",
            "Work order (proposed — Brain signs before dispatch)",
            wo_json,
            "",
            "Receipt",
            str(WORK_ORDER_RECEIPT),
            "",
            "Send back to agent",
            sendback.split("WORK_ORDER_JSON:")[0].strip(),
        ]
    )
    return {
        "ok": True,
        "text": text,
        "method": "rules",
        "sendback": sendback,
        "work_order": work_order,
        "work_order_path": str(WORK_ORDER_RECEIPT),
    }


def run_founder_loop(
    *,
    draft: str,
    founder_message: str = "",
    use_ai: bool = False,
    stages: list[str] | None = None,
    write_receipt: bool = True,
    write_progress: bool = False,
) -> dict:
    from chat_founder_language_v1 import translate_for_founder  # noqa: WPS433
    from chat_founder_reasoning_v1 import reason_for_founder  # noqa: WPS433

    if not (draft or "").strip():
        return {"ok": False, "error": "empty_text", "message": "Paste an agent answer first."}

    want = [s for s in (stages or STAGE_ORDER) if s in STAGE_ORDER]
    out_stages: dict = {}
    prior_chunks: list[str] = []
    completed: list[str] = []

    def _next_stage(after: str | None) -> str | None:
        if not want:
            return None
        if after is None:
            return want[0]
        if after not in want:
            return None
        idx = want.index(after)
        return want[idx + 1] if idx + 1 < len(want) else None

    def _progress(current: str | None) -> None:
        if write_progress:
            _flush_progress(
                running=True,
                current=current,
                completed=list(completed),
                stages=dict(out_stages),
                stage_order=want,
            )

    if write_progress and want:
        _progress(want[0])

    if "language" in want:
        _progress("language")
        row = translate_for_founder(draft=draft, founder_message=founder_message, prefer_ai=use_ai)
        out_stages["language"] = {
            "ok": row.get("ok"),
            "text": row.get("founder_text") or "",
            "method": row.get("method"),
        }
        prior_chunks.append(out_stages["language"]["text"])
        completed.append("language")
        _progress(_next_stage("language"))

    if "reasoning" in want:
        _progress("reasoning")
        row = reason_for_founder(draft=draft, founder_message=founder_message, prefer_ai=use_ai)
        out_stages["reasoning"] = {
            "ok": row.get("ok"),
            "text": row.get("reasoning_text") or "",
            "method": row.get("method"),
        }
        prior_chunks.append(out_stages["reasoning"]["text"])
        completed.append("reasoning")
        _progress(_next_stage("reasoning"))

    if "proof" in want:
        _progress("proof")
        out_stages["proof"] = _stage_proof(draft=draft, founder_message=founder_message)
        prior_chunks.append(out_stages["proof"]["text"])
        completed.append("proof")
        _progress(_next_stage("proof"))

    lang = out_stages.get("language", {}).get("text") or ""
    reas = out_stages.get("reasoning", {}).get("text") or ""
    proof = out_stages.get("proof", {}).get("text") or ""

    if "action" in want:
        _progress("action")
        out_stages["action"] = _stage_action(
            founder_message=founder_message,
            language=lang,
            reasoning=reas,
            proof=proof,
        )
        prior_chunks.append(out_stages["action"]["text"])
        completed.append("action")
        _progress(_next_stage("action"))

    prior = "\n\n---\n\n".join(prior_chunks)

    if "advisor" in want:
        _progress("advisor")
        out_stages["advisor"] = _stage_advisor(
            draft=draft,
            founder_message=founder_message,
            prior=prior,
            use_ai=use_ai,
        )
        prior_chunks.append(out_stages["advisor"]["text"])
        completed.append("advisor")
        _progress(_next_stage("advisor"))

    if "critic" in want:
        _progress("critic")
        out_stages["critic"] = _stage_critic(
            draft=draft,
            founder_message=founder_message,
            prior=prior,
            use_ai=use_ai,
        )
        prior_chunks.append(out_stages["critic"]["text"])
        completed.append("critic")
        _progress(_next_stage("critic"))

    action_one = out_stages.get("action", {}).get("one_action") or "Pick one manifest-approved next step."
    proof_snap = (out_stages.get("proof") or {}).get("snapshot") or _disk_snapshot()

    if "close" in want:
        _progress("close")
        out_stages["close"] = _stage_close(
            founder_message=founder_message,
            action_one=action_one,
            language=lang,
            snap=proof_snap,
        )
        completed.append("close")

    if write_progress:
        _flush_progress(
            running=False,
            current=None,
            completed=completed,
            stages=out_stages,
            stage_order=want,
        )

    loop_ok = any(st.get("ok") for st in out_stages.values())
    close_stage = out_stages.get("close") or {}
    result = {
        "ok": loop_ok,
        "schema": "chat-unify-founder-loop-v1",
        "version": LOOP_VERSION,
        "at": _now(),
        "stages": out_stages,
        "stage_order": want,
        "use_ai": use_ai,
        "sendback": close_stage.get("sendback") or "",
        "work_order": close_stage.get("work_order") or {},
        "work_order_path": close_stage.get("work_order_path") or str(WORK_ORDER_RECEIPT),
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def run_founder_stage(
    stage: str,
    *,
    draft: str,
    founder_message: str = "",
    use_ai: bool = False,
    kernel: dict | None = None,
    run_id: str | None = None,
    ord_run_id: str | None = None,
    write_receipt: bool = True,
) -> dict:
    """Run exactly ONE founder loop stage. Prior stages must exist in kernel (enforced dependency)."""
    from chat_founder_language_v1 import translate_for_founder  # noqa: WPS433
    from chat_founder_reasoning_v1 import reason_for_founder  # noqa: WPS433
    from chat_unify_kernel_v1 import (  # noqa: WPS433
        append_stage_log,
        bind_disk_snapshots,
        ensure_kernel,
        kernel_summary,
        load_kernel,
        merge_stage_output,
        record_model,
        save_kernel,
    )

    sid = (stage or "").strip().lower()
    if sid not in STAGE_ORDER:
        return {"ok": False, "error": "unknown_stage", "message": f"Unknown stage: {stage}"}
    if not (draft or "").strip():
        return {"ok": False, "error": "empty_text", "message": "Paste an agent answer first."}

    k = ensure_kernel(
        loop="founder",
        draft=draft,
        founder_message=founder_message,
        run_id=run_id,
        ord_run_id=ord_run_id,
        kernel=kernel,
    )
    if ord_run_id:
        k["ord_run_id"] = ord_run_id

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
            "kernel": k,
            "run_id": k.get("run_id"),
        }

    truth_gate: dict | None = None
    linked_ord = k.get("ord_run_id") or ord_run_id
    if linked_ord:
        ord_k = load_kernel(linked_ord)
        if ord_k and ord_k.get("decision"):
            truth_gate = ord_k.get("decision")

    if sid == "language":
        row = translate_for_founder(draft=draft, founder_message=founder_message, prefer_ai=use_ai)
        out_stages["language"] = {
            "ok": row.get("ok"),
            "text": row.get("founder_text") or "",
            "method": row.get("method"),
        }
    elif sid == "reasoning":
        row = reason_for_founder(draft=draft, founder_message=founder_message, prefer_ai=use_ai)
        out_stages["reasoning"] = {
            "ok": row.get("ok"),
            "text": row.get("reasoning_text") or "",
            "method": row.get("method"),
        }
    elif sid == "proof":
        out_stages["proof"] = _stage_proof(draft=draft, founder_message=founder_message)
    elif sid == "action":
        lang = out_stages.get("language", {}).get("text") or ""
        reas = out_stages.get("reasoning", {}).get("text") or ""
        proof = out_stages.get("proof", {}).get("text") or ""
        out_stages["action"] = _stage_action(
            founder_message=founder_message,
            language=lang,
            reasoning=reas,
            proof=proof,
        )
    elif sid in ("advisor", "critic"):
        prior_chunks = [
            out_stages[s].get("text") or ""
            for s in STAGE_ORDER
            if s in out_stages and s != sid and out_stages[s].get("text")
        ]
        prior = "\n\n---\n\n".join(prior_chunks)
        fn = _stage_advisor if sid == "advisor" else _stage_critic
        out_stages[sid] = fn(
            draft=draft,
            founder_message=founder_message,
            prior=prior,
            use_ai=use_ai,
        )
    elif sid == "close":
        lang = out_stages.get("language", {}).get("text") or ""
        action_one = out_stages.get("action", {}).get("one_action") or "Pick one manifest-approved next step."
        proof_snap = (out_stages.get("proof") or {}).get("snapshot") or _disk_snapshot()
        out_stages["close"] = _stage_close(
            founder_message=founder_message,
            action_one=action_one,
            language=lang,
            snap=proof_snap,
            truth_gate=truth_gate,
        )

    merge_stage_output(k, out_stages)
    if sid == "proof":
        bind_disk_snapshots(k, (out_stages.get("proof") or {}).get("snapshot") or {})

    stage_ok = bool(out_stages.get(sid, {}).get("ok", True))
    method = (out_stages.get(sid) or {}).get("method")
    if use_ai and method and ("ai" in str(method) or method == "openrouter"):
        record_model(k, provider="openrouter", method=str(method))
    append_stage_log(k, stage=sid, depends_on=dep, ok=stage_ok, method=method)
    save_kernel(k)

    idx = STAGE_ORDER.index(sid)
    next_stage = STAGE_ORDER[idx + 1] if idx + 1 < len(STAGE_ORDER) else None
    close_stage = out_stages.get("close") or {}

    result: dict = {
        "ok": stage_ok,
        "schema": "chat-unify-founder-loop-stage-v1",
        "version": LOOP_VERSION,
        "execution_mode": "sequential_single_stage",
        "stage": sid,
        "next_stage": next_stage,
        "depends_on": dep,
        "stages": out_stages,
        "kernel": k,
        "run_id": k.get("run_id"),
        "ord_run_id": k.get("ord_run_id"),
        "kernel_summary": kernel_summary(k),
        "truth_gate": truth_gate,
        "use_ai": use_ai,
    }

    if sid == "close":
        result.update(
            {
                "sendback": close_stage.get("sendback") or "",
                "work_order": close_stage.get("work_order") or {},
                "work_order_path": close_stage.get("work_order_path") or str(WORK_ORDER_RECEIPT),
            }
        )
        if write_receipt:
            full = {
                "ok": True,
                "schema": "chat-unify-founder-loop-v1",
                "version": LOOP_VERSION,
                "at": _now(),
                "stages": out_stages,
                "stage_order": list(STAGE_ORDER),
                "use_ai": use_ai,
                "sendback": result["sendback"],
                "work_order": result["work_order"],
                "work_order_path": result["work_order_path"],
            }
            SINA.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(full, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return result


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Founder loop v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--ai", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_founder_loop(
        draft=args.text,
        founder_message=args.founder_message,
        use_ai=args.ai,
        write_receipt=True,
    )
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        for sid in row.get("stage_order") or []:
            st = row.get("stages", {}).get(sid) or {}
            print(f"\n=== {sid.upper()} ({st.get('method')}) ===\n{st.get('text', '')[:600]}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
