#!/usr/bin/env python3
"""Chat Unify — Vocabulary Intelligence Machine (6 stages).

Stages: goal → scan → classify → suggest → review → emit
Sources: repo profiles · live URL · paste · local file
Scanner: scripts/vocabulary_intelligence_scan_v1.py
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
VIM_DIR = SINA / "chat-unify" / "vocabulary-intelligence"
SCAN_CACHE_DIR = VIM_DIR / "scans"
LATEST_RECEIPT = SINA / "chat-unify-vocabulary-intelligence-v1.json"
PROGRESS_PATH = SINA / "chat-unify-vocabulary-intelligence-progress-v1.json"
REGISTRY_PATH = ROOT / "data" / "vocabulary-intelligence-registry-v1.json"
UNIFIED_INDEX_PATH = ROOT / "data" / "sourcea-vocabulary-unified-index-v1.json"

STAGE_ORDER = ("goal", "scan", "classify", "suggest", "review", "emit")
STAGE_DEPENDS: dict[str, str | None] = {
    "goal": None,
    "scan": "goal",
    "classify": "scan",
    "suggest": "classify",
    "review": "suggest",
    "emit": "review",
}
MACHINE_VERSION = "1.2.0"
DEFAULT_CAMPAIGN = "motor-rename-v1"
DEFAULT_PROFILES = ["sourcea_repo"]
SOURCE_TYPES = ("repo", "url", "paste", "file")
_URL_INLINE = re.compile(r"https?://[^\s<>\"']+", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _detect_source_from_text(text: str) -> tuple[str, str]:
    """If founder pasted a bare URL, treat as url source."""
    t = (text or "").strip()
    m = _URL_INLINE.match(t)
    if m and len(t.split()) == 1:
        return "url", m.group(0).rstrip(".,;:")
    return "paste", t


def _parse_config(
    *,
    founder_text: str = "",
    founder_message: str = "",
    url: str = "",
    file_path: str = "",
    source_type: str = "",
) -> dict[str, Any]:
    cfg: dict[str, Any] = {}
    raw = (founder_message or "").strip()
    if raw.startswith("{"):
        try:
            cfg = json.loads(raw)
        except json.JSONDecodeError:
            cfg = {}

    campaign = (cfg.get("campaign_id") or cfg.get("campaign") or DEFAULT_CAMPAIGN).strip()
    profiles = cfg.get("profiles") or DEFAULT_PROFILES
    if isinstance(profiles, str):
        profiles = [p.strip() for p in profiles.split(",") if p.strip()]
    if not profiles:
        profiles = list(DEFAULT_PROFILES)

    st = (source_type or cfg.get("source_type") or "repo").strip().lower()
    if st not in SOURCE_TYPES:
        st = "repo"

    paste = (cfg.get("paste") or founder_text or cfg.get("note") or "").strip()
    url_val = (url or cfg.get("url") or "").strip()
    file_val = (file_path or cfg.get("file_path") or cfg.get("file") or "").strip()

    if st == "repo" and paste and not file_val and not url_val:
        detected, payload = _detect_source_from_text(paste)
        if detected == "url":
            st = "url"
            url_val = payload
            paste = ""
        elif payload:
            st = "paste"

    use_ai = bool(cfg.get("use_ai"))

    return {
        "campaign_id": campaign,
        "profiles": profiles,
        "source_type": st,
        "url": url_val,
        "paste": paste,
        "file_path": file_val,
        "note": paste if st == "paste" else (url_val if st == "url" else file_val),
        "use_ai": use_ai,
    }


def _scan_cache_path(run_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in run_id)
    return SCAN_CACHE_DIR / f"{safe}.json"


def _slim_scan_stage(stage: dict[str, Any]) -> dict[str, Any]:
    slim = {k: v for k, v in stage.items() if k != "scan"}
    scan = stage.get("scan") or {}
    if scan:
        slim["scan_cached"] = True
        slim["source_type"] = scan.get("source_type")
        slim["source_label"] = scan.get("source_label")
        slim["files_scanned"] = scan.get("files_scanned")
        slim["hits_total"] = scan.get("hits_total")
        slim["hits_patch"] = scan.get("hits_patch")
        slim["hits_by_tier"] = scan.get("hits_by_tier")
        if scan.get("fetch"):
            slim["fetch"] = scan["fetch"]
    return slim


def _stage_goal(*, config: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    campaigns = registry.get("campaigns") or {}
    cid = config["campaign_id"]
    if cid not in campaigns:
        return {
            "ok": False,
            "method": "registry",
            "text": f"Unknown campaign: {cid}",
            "campaign_id": cid,
            "known_campaigns": list(campaigns.keys()),
        }
    camp = campaigns[cid]
    goal = camp.get("goal") or ""
    unified = _read_json(UNIFIED_INDEX_PATH)
    unified_law = (unified.get("one_law") or "")[:160]
    st = config["source_type"]
    lines = [
        f"Campaign · {cid}",
        f"Goal · {goal}",
        f"Spine · data/sourcea-vocabulary-unified-index-v1.json",
        f"Source · {st}",
    ]
    if st == "repo":
        lines.append(f"Profiles · {', '.join(config['profiles'])}")
    elif st == "url":
        lines.append(f"URL · {config.get('url') or '(missing — paste link in input)'}")
    elif st == "paste":
        preview = (config.get("paste") or "")[:120]
        lines.append(f"Paste · {len(config.get('paste') or '')} chars")
        if preview:
            lines.append(f"Preview · {preview}{'…' if len(config.get('paste') or '') > 120 else ''}")
    elif st == "file":
        lines.append(f"File · {config.get('file_path') or '(missing path)'}")
    if unified_law:
        lines.extend(["", f"Unified law · {unified_law}…"])
    return {
        "ok": True,
        "method": "registry",
        "text": "\n".join(lines),
        "campaign_id": cid,
        "goal": goal,
        "source_type": st,
        "profiles": config.get("profiles"),
        "url": config.get("url"),
        "paste": config.get("paste"),
        "file_path": config.get("file_path"),
    }


def _stage_scan(*, config: dict[str, Any]) -> dict[str, Any]:
    from vocabulary_intelligence_scan_v1 import run_scan_source  # noqa: WPS433

    st = config["source_type"]
    if st == "url" and not config.get("url"):
        return {"ok": False, "method": "scan", "text": "URL required — paste a page link."}
    if st == "paste" and not config.get("paste"):
        return {"ok": False, "method": "scan", "text": "Paste text required."}
    if st == "file" and not config.get("file_path"):
        return {"ok": False, "method": "scan", "text": "Local file path required."}

    result = run_scan_source(
        campaign_id=config["campaign_id"],
        source_type=st,
        profiles=list(config.get("profiles") or DEFAULT_PROFILES),
        url=config.get("url") or "",
        paste=config.get("paste") or "",
        file_path=config.get("file_path") or "",
        registry=_read_json(REGISTRY_PATH),
    )
    if not result.get("ok"):
        return {
            "ok": False,
            "method": "scan",
            "text": result.get("message") or result.get("error") or "Scan failed",
            "scan": result,
        }

    src = result.get("source_type") or st
    label = result.get("source_label") or src
    fetch = result.get("fetch") or {}
    fetch_line = ""
    if fetch.get("url"):
        fetch_line = f" · fetched HTTP {fetch.get('status')}"
    summary = (
        f"{src.upper()} · {label}{fetch_line}\n"
        f"Scanned {result.get('files_scanned', 0)} unit(s) · "
        f"{result.get('hits_total', 0)} hits · "
        f"{result.get('hits_patch', 0)} patch queue"
    )
    return {
        "ok": True,
        "method": "url_fetch" if src == "url" else "scan",
        "text": summary,
        "scan": result,
        "source_type": src,
        "source_label": label,
        "files_scanned": result.get("files_scanned"),
        "hits_total": result.get("hits_total"),
        "hits_patch": result.get("hits_patch"),
        "hits_by_tier": result.get("hits_by_tier"),
    }


def _load_scan_from_stages(stages: dict[str, Any], *, run_id: str) -> dict[str, Any] | None:
    scan_st = stages.get("scan") or {}
    if scan_st.get("scan"):
        return scan_st["scan"]
    cached = _read_json(_scan_cache_path(run_id))
    if cached.get("ok"):
        return cached
    return None


def _stage_classify(*, scan: dict[str, Any]) -> dict[str, Any]:
    by_tier = scan.get("hits_by_tier") or {}
    hits = scan.get("hits") or []
    by_subject: dict[str, int] = {}
    for h in hits:
        subj = str(h.get("subject") or "unknown")
        by_subject[subj] = by_subject.get(subj, 0) + 1
    top_subjects = sorted(by_subject.items(), key=lambda x: -x[1])[:8]
    src = scan.get("source_type") or "repo"
    lines = [
        f"Source · {src} · {scan.get('source_label') or '—'}",
        f"Tier 1 founder-facing · {by_tier.get('1', 0)}",
        f"Tier 2 ops display · {by_tier.get('2', 0)}",
        f"Tier 3 frozen machine · {by_tier.get('3', 0)}",
        "",
        "Subjects:",
    ]
    for name, count in top_subjects:
        lines.append(f"  {name} · {count}")
    if not top_subjects:
        lines.append("  (none)")
    return {
        "ok": True,
        "method": "classify",
        "text": "\n".join(lines),
        "hits_by_tier": by_tier,
        "hits_by_subject": dict(top_subjects),
    }


def _stage_suggest(*, scan: dict[str, Any], use_ai: bool = False, limit: int = 12) -> dict[str, Any]:
    patch = scan.get("patch_queue") or []
    if not patch:
        patch = [h for h in (scan.get("hits") or []) if h.get("action") == "patch"]
    sample = patch[:limit]
    lines: list[str] = []
    for h in sample:
        sug = h.get("suggestion") or "—"
        match = h.get("match") or ""
        lines.append(f"{h.get('file')}:{h.get('line')} · {match!r} → {sug}")

    llm_note = ""
    method = "rules"
    if use_ai and sample:
        llm_note = _llm_suggest_review(scan=scan, samples=sample)
        if llm_note:
            method = "rules+llm"
            lines.extend(["", "LLM review:", llm_note])

    if len(patch) > limit:
        lines.append(f"… +{len(patch) - limit} more in patch queue")
    if not lines:
        lines.append("No patch suggestions — scan clean or all tier-3 / skipped subjects.")
    return {
        "ok": True,
        "method": method,
        "text": "\n".join(lines),
        "sample_count": len(sample),
        "patch_total": len(patch),
        "samples": sample,
        "llm_review": llm_note or None,
        "used_llm": bool(llm_note),
    }


def _llm_suggest_review(*, scan: dict[str, Any], samples: list[dict[str, Any]]) -> str:
    try:
        from ai_unify_api_v1 import chat_openrouter, pick_provider  # noqa: WPS433
    except ImportError:
        return ""
    if pick_provider() == "none":
        return ""

    rows = []
    for h in samples[:8]:
        rows.append(
            f"- {h.get('match')} in `{h.get('file')}` line {h.get('line')}: "
            f"suggest `{h.get('suggestion')}` ({h.get('reason')})"
        )
    user = (
        f"Campaign goal: {scan.get('goal')}\n"
        f"Source: {scan.get('source_type')} {scan.get('source_label')}\n\n"
        "Hits:\n" + "\n".join(rows) + "\n\n"
        "Reply in 3-6 short bullets: validate each suggestion, flag any poison-as-motor mistake, "
        "and one founder-facing summary line. Plain English only."
    )
    system = (
        "You are Vocabulary Intelligence for SourceA. Cloud motor display names: "
        "Cloud Forge Run (not drain), Auto Runtime (not Auto Runtime). "
        "Poison/anti-poison is governance-only — never a motor name."
    )
    ok, text = chat_openrouter(system=system, user=user)
    return text.strip()[:2000] if ok else ""


def _stage_review(*, scan: dict[str, Any]) -> dict[str, Any]:
    patch = scan.get("patch_queue") or []
    t1 = sum(1 for h in patch if h.get("tier") == 1)
    t2 = sum(1 for h in patch if h.get("tier") == 2)
    files: dict[str, int] = {}
    for h in patch:
        f = str(h.get("file") or "")
        files[f] = files.get(f, 0) + 1
    top_files = sorted(files.items(), key=lambda x: -x[1])[:10]
    lines = [
        f"Source · {scan.get('source_type') or 'repo'}",
        f"Patch queue · {len(patch)} total",
        f"  Tier 1 ready · {t1}",
        f"  Tier 2 ops copy · {t2}",
        "",
        "Top locations:",
    ]
    for path, count in top_files:
        lines.append(f"  {path} · {count} hit(s)")
    if not top_files:
        lines.append("  (none)")
    lines.extend(["", "Policy · tier 3 frozen · product_loop + chat_unify_loop skipped"])
    return {
        "ok": True,
        "method": "review",
        "text": "\n".join(lines),
        "patch_total": len(patch),
        "tier1": t1,
        "tier2": t2,
        "top_files": top_files,
        "ready_to_apply": t1 + t2,
    }


def _stage_emit(
    *,
    scan: dict[str, Any],
    stages: dict[str, Any],
    config: dict[str, Any],
    run_id: str,
    write_receipt: bool,
) -> dict[str, Any]:
    src = scan.get("source_type") or config.get("source_type") or "repo"
    receipt = {
        "ok": True,
        "schema": "chat-unify-vocabulary-intelligence-v1",
        "version": MACHINE_VERSION,
        "at": _now(),
        "run_id": run_id,
        "campaign_id": config["campaign_id"],
        "source_type": src,
        "source_label": scan.get("source_label"),
        "profiles": config.get("profiles"),
        "url": config.get("url"),
        "file_path": config.get("file_path"),
        "goal": scan.get("goal"),
        "files_scanned": scan.get("files_scanned"),
        "hits_total": scan.get("hits_total"),
        "hits_patch": scan.get("hits_patch"),
        "hits_by_tier": scan.get("hits_by_tier"),
        "patch_queue_count": len(scan.get("patch_queue") or []),
        "used_llm": bool((stages.get("suggest") or {}).get("used_llm")),
        "scan_receipt": str(SINA / "vocabulary-intelligence-scan-receipt-v1.json"),
        "stages": {
            k: {"ok": v.get("ok"), "text": v.get("text"), "method": v.get("method")}
            for k, v in stages.items()
            if isinstance(v, dict)
        },
        "founder_line": (
            f"Vocabulary · {src} · {scan.get('hits_patch', 0)} patches · "
            f"T1={scan.get('hits_by_tier', {}).get('1', 0)} "
            f"T2={scan.get('hits_by_tier', {}).get('2', 0)} · "
            f"{config['campaign_id']}"
        ),
    }
    receipt_path = LATEST_RECEIPT
    run_receipt = VIM_DIR / "runs" / f"{run_id}.json"
    if write_receipt:
        _write_json(receipt_path, receipt)
        _write_json(run_receipt, {**receipt, "scan": scan})
        scan_receipt = dict(scan)
        scan_receipt["chat_unify_run_id"] = run_id
        _write_json(SINA / "vocabulary-intelligence-scan-receipt-v1.json", scan_receipt)
    return {
        "ok": True,
        "method": "disk",
        "text": f"Receipt · {receipt_path}\nRun · {run_receipt}\n{receipt['founder_line']}",
        "receipt_path": str(receipt_path),
        "run_receipt_path": str(run_receipt),
        "founder_line": receipt["founder_line"],
        "receipt": receipt,
    }


def _flush_progress(
    *,
    running: bool,
    current: str | None,
    completed: list[str],
    stages: dict[str, Any],
    error: str | None = None,
) -> None:
    _write_json(
        PROGRESS_PATH,
        {
            "schema": "chat-unify-vocabulary-intelligence-progress-v1",
            "at": _now(),
            "running": running,
            "current": current,
            "completed": completed,
            "stages": stages,
            "error": error,
        },
    )


def read_vocabulary_intelligence_progress() -> dict[str, Any]:
    data = _read_json(PROGRESS_PATH)
    if not data:
        return {"ok": True, "running": False, "completed": [], "stages": {}}
    return {"ok": True, **data}


def run_vocabulary_intelligence_ingest(
    *,
    founder_text: str = "",
    founder_message: str = "",
    url: str = "",
    file_path: str = "",
    source_type: str = "",
    use_ai: bool = False,
    write_receipt: bool = True,
) -> dict[str, Any]:
    """API-friendly one-shot — same as full loop."""
    return run_vocabulary_intelligence_loop(
        founder_text=founder_text,
        founder_message=founder_message,
        url=url,
        file_path=file_path,
        source_type=source_type,
        use_ai=use_ai,
        write_receipt=write_receipt,
    )


def run_vocabulary_intelligence_loop(
    *,
    founder_text: str = "",
    founder_message: str = "",
    url: str = "",
    file_path: str = "",
    source_type: str = "",
    use_ai: bool = False,
    write_receipt: bool = True,
    write_progress: bool = True,
) -> dict[str, Any]:
    config = _parse_config(
        founder_text=founder_text,
        founder_message=founder_message,
        url=url,
        file_path=file_path,
        source_type=source_type,
    )
    if use_ai:
        config["use_ai"] = True
    registry = _read_json(REGISTRY_PATH)
    run_id = f"vim-{uuid.uuid4().hex[:12]}"
    out_stages: dict[str, Any] = {}
    completed: list[str] = []

    def _progress(current: str | None) -> None:
        if write_progress:
            _flush_progress(running=True, current=current, completed=list(completed), stages=dict(out_stages))

    _progress("goal")
    out_stages["goal"] = _stage_goal(config=config, registry=registry)
    if not out_stages["goal"].get("ok"):
        _flush_progress(running=False, current=None, completed=completed, stages=out_stages, error="goal_failed")
        return {"ok": False, "stages": out_stages, "message": out_stages["goal"].get("text")}
    completed.append("goal")

    _progress("scan")
    out_stages["scan"] = _stage_scan(config=config)
    if not out_stages["scan"].get("ok"):
        _flush_progress(running=False, current=None, completed=completed, stages=out_stages, error="scan_failed")
        return {"ok": False, "stages": out_stages, "message": out_stages["scan"].get("text")}
    scan = out_stages["scan"]["scan"]
    _write_json(_scan_cache_path(run_id), scan)
    completed.append("scan")

    _progress("classify")
    out_stages["classify"] = _stage_classify(scan=scan)
    completed.append("classify")

    _progress("suggest")
    out_stages["suggest"] = _stage_suggest(scan=scan, use_ai=config.get("use_ai", False))
    completed.append("suggest")

    _progress("review")
    out_stages["review"] = _stage_review(scan=scan)
    completed.append("review")

    _progress("emit")
    out_stages["emit"] = _stage_emit(
        scan=scan,
        stages=out_stages,
        config=config,
        run_id=run_id,
        write_receipt=write_receipt,
    )
    completed.append("emit")

    result = {
        "ok": True,
        "schema": "chat-unify-vocabulary-intelligence-v1",
        "version": MACHINE_VERSION,
        "at": _now(),
        "run_id": run_id,
        "campaign_id": config["campaign_id"],
        "source_type": config["source_type"],
        "profiles": config.get("profiles"),
        "founder_line": out_stages["emit"].get("founder_line"),
        "receipt_path": out_stages["emit"].get("receipt_path"),
        "used_llm": bool(out_stages["suggest"].get("used_llm")),
        "stages": out_stages,
        "stage_order": list(STAGE_ORDER),
    }
    if write_receipt:
        _write_json(LATEST_RECEIPT, result)
    _flush_progress(running=False, current=None, completed=completed, stages=out_stages)
    return result


def run_vocabulary_intelligence_stage(
    stage: str,
    *,
    founder_text: str = "",
    founder_message: str = "",
    url: str = "",
    file_path: str = "",
    source_type: str = "",
    use_ai: bool = False,
    kernel: dict | None = None,
    run_id: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    from chat_unify_kernel_v1 import ensure_kernel, merge_stage_output, save_kernel  # noqa: WPS433

    sid = (stage or "").strip().lower()
    if sid not in STAGE_ORDER:
        return {"ok": False, "error": "unknown_stage", "message": f"Unknown stage: {stage}"}

    config = _parse_config(
        founder_text=founder_text,
        founder_message=founder_message,
        url=url,
        file_path=file_path,
        source_type=source_type,
    )
    if use_ai:
        config["use_ai"] = True
    registry = _read_json(REGISTRY_PATH)

    k = ensure_kernel(
        loop="vocabulary_intelligence",
        draft=founder_text or config.get("note") or config["campaign_id"],
        founder_message=founder_message,
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

    rid = k.get("run_id") or run_id or f"vim-{uuid.uuid4().hex[:12]}"
    k["run_id"] = rid
    stage_ok = False
    stage_payload: dict[str, Any] = {}

    if sid == "goal":
        stage_payload = _stage_goal(config=config, registry=registry)
        stage_ok = bool(stage_payload.get("ok"))
    elif sid == "scan":
        stage_payload = _stage_scan(config=config)
        stage_ok = bool(stage_payload.get("ok"))
        if stage_ok and stage_payload.get("scan"):
            _write_json(_scan_cache_path(rid), stage_payload["scan"])
            out_stages["scan"] = _slim_scan_stage(stage_payload)
            merge_stage_output(k, out_stages)
            save_kernel(k)
            emit_st = out_stages.get("emit") or {}
            return {
                "ok": stage_ok,
                "schema": "chat-unify-vocabulary-intelligence-v1",
                "version": MACHINE_VERSION,
                "stage": sid,
                "run_id": rid,
                "campaign_id": config["campaign_id"],
                "source_type": config["source_type"],
                "profiles": config.get("profiles"),
                "founder_line": emit_st.get("founder_line"),
                "receipt_path": emit_st.get("receipt_path"),
                "stages": {**out_stages, "scan": stage_payload},
                "stage_order": list(STAGE_ORDER),
                "message": stage_payload.get("text") if not stage_ok else "",
            }
    elif sid == "classify":
        scan = _load_scan_from_stages(out_stages, run_id=rid)
        if not scan:
            return {
                "ok": False,
                "error": "scan_missing",
                "message": "Classify blocked — run scan first.",
                "stages": out_stages,
                "run_id": rid,
            }
        stage_payload = _stage_classify(scan=scan)
        stage_ok = bool(stage_payload.get("ok"))
    elif sid == "suggest":
        scan = _load_scan_from_stages(out_stages, run_id=rid)
        if not scan:
            return {
                "ok": False,
                "error": "scan_missing",
                "message": "Suggest blocked — run scan first.",
                "stages": out_stages,
                "run_id": rid,
            }
        stage_payload = _stage_suggest(scan=scan, use_ai=config.get("use_ai", False))
        stage_ok = bool(stage_payload.get("ok"))
    elif sid == "review":
        scan = _load_scan_from_stages(out_stages, run_id=rid)
        if not scan:
            return {
                "ok": False,
                "error": "scan_missing",
                "message": "Review blocked — run scan first.",
                "stages": out_stages,
                "run_id": rid,
            }
        stage_payload = _stage_review(scan=scan)
        stage_ok = bool(stage_payload.get("ok"))
    elif sid == "emit":
        scan = _load_scan_from_stages(out_stages, run_id=rid)
        if not scan:
            return {
                "ok": False,
                "error": "scan_missing",
                "message": "Emit blocked — run scan first.",
                "stages": out_stages,
                "run_id": rid,
            }
        stage_payload = _stage_emit(
            scan=scan,
            stages={**out_stages, "emit": {}},
            config=config,
            run_id=rid,
            write_receipt=write_receipt,
        )
        stage_ok = bool(stage_payload.get("ok"))

    out_stages[sid] = stage_payload
    merge_stage_output(k, out_stages)
    save_kernel(k)

    emit_st = out_stages.get("emit") or {}
    return {
        "ok": stage_ok,
        "schema": "chat-unify-vocabulary-intelligence-v1",
        "version": MACHINE_VERSION,
        "stage": sid,
        "run_id": rid,
        "campaign_id": config["campaign_id"],
        "source_type": config["source_type"],
        "profiles": config.get("profiles"),
        "founder_line": emit_st.get("founder_line") or stage_payload.get("founder_line"),
        "receipt_path": emit_st.get("receipt_path") or stage_payload.get("receipt_path"),
        "used_llm": bool((out_stages.get("suggest") or {}).get("used_llm")),
        "stages": out_stages,
        "stage_order": list(STAGE_ORDER),
        "message": stage_payload.get("text") if not stage_ok else "",
    }
