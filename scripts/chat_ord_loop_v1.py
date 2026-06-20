#!/usr/bin/env python3
"""Chat Unify — ORD Loop (Output Reverse Debugger).

Reverse Forge: parse AI output → classify → check → attribute source → simplify → flag → report.

Stages: parse · classify · consistency · attribution · simplify · redflags · report
Receipt: ~/.sina/chat-unify-ord-loop-v1.json
Progress: ~/.sina/chat-unify-ord-loop-progress-v1.json
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
RECEIPT = SINA / "chat-unify-ord-loop-v1.json"
PROGRESS_PATH = SINA / "chat-unify-ord-loop-progress-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
EVAL_1B = SINA / "eval_packet_v1b_report.json"
LOOP_VERSION = "0.6.0"

STAGE_ORDER = (
    "parse",
    "classify",
    "consistency",
    "attribution",
    "simplify",
    "redflags",
    "report",
)

STAGE_DEPENDS: dict[str, str | None] = {
    "parse": None,
    "classify": "parse",
    "consistency": "classify",
    "attribution": "consistency",
    "simplify": "attribution",
    "redflags": "simplify",
    "report": "redflags",
}

SIMPLIFY_SYSTEM = """You reverse-debug AI agent output for a founder.

Given parsed claims and issues, write a SHORT plain-English summary (max 100 words).

Structure:
What the AI said (one sentence)
What is probably true
What needs checking

Rules: no jargon · no bash · no validator names · bullet-free prose."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _ai_call(*, system: str, user: str, timeout_sec: int = 20) -> tuple[str, str]:
    try:
        from ai_unify_api_v1 import dispatch_raw, pick_provider  # noqa: WPS433
    except ImportError:
        return "", "none"
    if pick_provider("auto") == "none":
        return "", "none"

    def _run() -> dict:
        return dispatch_raw(
            system=system,
            user=user[:12000],
            provider="auto",
            light_gate=True,
            source="chat-ord-loop",
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            row = pool.submit(_run).result(timeout=timeout_sec)
    except (FutTimeout, Exception):
        return "", "timeout"
    if row.get("ok") and (row.get("response") or "").strip():
        return (row.get("response") or "").strip(), row.get("provider") or "ai"
    return "", "failed"


def _split_code_blocks(text: str) -> tuple[list[str], str]:
    blocks: list[str] = []
    rest_parts: list[str] = []
    pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
    last = 0
    for m in pattern.finditer(text):
        rest_parts.append(text[last : m.start()])
        blocks.append(m.group(1).strip())
        last = m.end()
    rest_parts.append(text[last:])
    return blocks, "\n".join(rest_parts)


def _extract_table_blocks(text: str) -> tuple[list[str], list[str]]:
    """Split tab-table blocks from prose lines — tables become single FACT segments."""
    table_facts: list[str] = []
    prose_lines: list[str] = []
    block: list[str] = []
    in_table = False

    def _flush_table() -> None:
        nonlocal in_table, block
        if len(block) >= 2:
            header = block[0].replace("\t", " | ")
            rows = [r.replace("\t", " | ") for r in block[1:6]]
            table_facts.append(f"Table: {header} — " + "; ".join(rows))
        elif block:
            prose_lines.extend(block)
        block = []
        in_table = False

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if in_table:
                _flush_table()
            continue
        is_tab_row = "\t" in line and len(line.split("\t")) >= 2
        if is_tab_row:
            if not in_table:
                in_table = True
                block = []
            block.append(line.strip())
            continue
        if in_table:
            _flush_table()
        if line.strip().startswith("#"):
            prose_lines.append(line.lstrip("#").strip())
        elif re.match(r"^[-*•]\s+", line.strip()):
            prose_lines.append(re.sub(r"^[-*•]\s+", "", line.strip()))
        elif re.match(r"^\d+[.)]\s+", line.strip()):
            prose_lines.append(re.sub(r"^\d+[.)]\s+", "", line.strip()))
        elif len(line.strip()) > 12:
            prose_lines.append(line.strip())
    if in_table:
        _flush_table()
    return table_facts, prose_lines[:80]


def _lines_of_interest(text: str) -> list[str]:
    _, prose = _extract_table_blocks(text)
    return prose


def _stage_parse(*, draft: str) -> dict:
    code_blocks, prose = _split_code_blocks(draft)
    table_facts, lines = _extract_table_blocks(prose)
    claims: list[str] = []
    actions: list[str] = []
    assumptions: list[str] = []
    decisions: list[str] = []

    action_re = re.compile(
        r"\b(run|execute|deploy|fix|add|create|build|ship|merge|delete|move|restart|curl|bash)\b",
        re.I,
    )
    assume_re = re.compile(r"\b(probably|likely|should|assume|if .+ then|might|may)\b", re.I)
    decide_re = re.compile(r"\b(pick|choose|decide|recommend|option [a-d]|approve|defer)\b", re.I)
    claim_re = re.compile(
        r"\b(pass|fail|wired|complete|done|ready|fixed|verified|zero drift|ssot|manifest)\b",
        re.I,
    )

    for tf in table_facts:
        claims.append(tf[:400])

    for line in lines:
        try:
            from chat_ord_claim_rules_v1 import is_table_noise_line  # noqa: WPS433

            if is_table_noise_line(line):
                continue
        except ImportError:
            pass
        low = line.lower()
        if action_re.search(low):
            actions.append(line[:200])
        elif assume_re.search(low):
            assumptions.append(line[:200])
        elif decide_re.search(low):
            decisions.append(line[:200])
        elif claim_re.search(low) or line.endswith(".") and len(line) > 20:
            claims.append(line[:200])

    claim_lines = [f"· {c}" for c in claims[:4]] or ["· (none detected)"]
    action_lines = [f"· {a}" for a in actions[:4]] or ["· (none detected)"]
    assume_lines = [f"· {a}" for a in assumptions[:4]] or ["· (none detected)"]

    text = "\n".join(
        [
            "Parsed segments",
            f"· claims: {len(claims)}",
            f"· actions: {len(actions)}",
            f"· assumptions: {len(assumptions)}",
            f"· decisions: {len(decisions)}",
            f"· code blocks: {len(code_blocks)}",
            f"· table blocks: {len(table_facts)}",
            "",
            "Sample claims",
            *claim_lines,
            "",
            "Sample actions",
            *action_lines,
            "",
            "Sample assumptions",
            *assume_lines,
        ]
    )
    return {
        "ok": True,
        "text": text,
        "method": "rules",
        "parsed": {
            "claims": claims,
            "actions": actions,
            "assumptions": assumptions,
            "decisions": decisions,
            "code_blocks": code_blocks,
            "table_facts": table_facts,
            "line_count": len(lines),
        },
    }


def _classify_line(line: str) -> str:
    low = line.lower()
    if re.search(r"\b(you must|run |execute |deploy |fix |add |create |build |ship )\b", low):
        return "INSTRUCTION"
    if re.search(r"\b(probably|likely|assume|might|may|if .+ then)\b", low):
        return "ASSUMPTION"
    if re.search(r"\b(pass|fail|wired|verified|complete|done|ready|fixed|exists in the repository)\b", low):
        return "CLAIM"
    if re.search(r"\b(is |are |was |has |have |will |can )\b", low) and not re.search(r"\?", low):
        return "FACT"
    if len(line) < 18 or re.search(r"^(thanks|note:|tip:|see also)", low):
        return "NOISE"
    return "CLAIM"


def _stage_classify(*, parsed: dict) -> dict:
    buckets: dict[str, list[str]] = {
        "FACT": [],
        "CLAIM": [],
        "ASSUMPTION": [],
        "INSTRUCTION": [],
        "NOISE": [],
    }
    all_lines = (
        parsed.get("claims", [])
        + parsed.get("actions", [])
        + parsed.get("assumptions", [])
        + parsed.get("decisions", [])
    )
    for line in all_lines:
        kind = _classify_line(line)
        buckets[kind].append(line[:160])

    text = "\n".join(
        [
            "Line types",
            *(f"· {k}: {len(v)}" for k, v in buckets.items()),
            "",
            "Examples",
            *(f"[{k}] {v[0]}" for k, v in buckets.items() if v),
        ]
    )
    return {"ok": True, "text": text, "method": "rules", "buckets": buckets}


def _disk_hints() -> dict:
    snap: dict = {"paths_checked": []}
    manifest = ROOT / "infra" / "cleanup" / "cleanup-manifest.md"
    if manifest.is_file():
        body = manifest.read_text(encoding="utf-8", errors="replace")
        snap["batch_4_frozen"] = "Batch 4 FROZEN" in body or "FROZEN — Batch 4" in body
        snap["batch_4_approved"] = (
            re.search(r"Batch 4[^\n]*APPROVED|Status:\s*APPROVED", body, re.I) is not None
            and not snap["batch_4_frozen"]
        )
        snap["paths_checked"].append(str(manifest))
    surfaces = _read_json(SURFACES)
    if surfaces.get("factory_now_line"):
        snap["factory_now"] = str(surfaces["factory_now_line"])[:180]
        snap["paths_checked"].append(str(SURFACES))
    eval_row = _read_json(EVAL_1B)
    if eval_row.get("schema") == "eval-packet-v1b":
        snap["eval_1b"] = {
            "mode": eval_row.get("mode"),
            "ok": eval_row.get("ok"),
            "live_ok": eval_row.get("live_ok"),
        }
        snap["paths_checked"].append(str(EVAL_1B))
    return snap


def _stage_consistency(
    *,
    draft: str,
    parsed: dict,
    buckets: dict,
    issues: list[str] | None = None,
    disk: dict | None = None,
) -> dict:
    from chat_ord_claim_rules_v1 import enrich_disk_hints  # noqa: WPS433

    snap = enrich_disk_hints(draft=draft, snap=disk or _disk_hints())
    issue_list = list(issues or [])
    issue_lines = [f"· {i}" for i in issue_list] or ["· Rules scan pending atom verify."]
    path_lines = [f"· {p}" for p in snap.get("paths_checked", [])[:5]]
    draft_paths = snap.get("draft_paths") or []
    if draft_paths:
        path_lines.extend(f"· draft: {p}" for p in draft_paths[:4])

    text = "\n".join(
        [
            f"Checks run: {len(issue_list)} issue(s)",
            "",
            *issue_lines,
            "",
            "Disk peek (rules v1)",
            f"· paths: {len(snap.get('paths_checked', []))}",
            *path_lines,
        ]
    )
    return {"ok": True, "text": text, "method": "rules", "issues": issue_list, "disk": snap}


def _stage_attribution(*, draft: str, issues: list[str], use_ai: bool) -> dict:
    tags: list[str] = []
    low = draft.lower()

    if re.search(r"\b(wired|ssot|zero drift|gate pass|validator pass)\b", low):
        tags.append("AGENT — governance theater words without line-by-line disk proof")
    if re.search(r"\b(api/[a-z0-9_/-]+)\b", low) and "404" not in low:
        tags.append("MODEL — API paths may be hallucinated if not grep-verified")
    if any("DISK:" in i for i in issues):
        tags.append("DISK — agent prose disagrees with manifest or receipts")
    if re.search(r"\b(openrouter|claude|gpt|gemini|model)\b", low):
        tags.append("ROUTER — reply mentions model routing; check if right tier was used")
    if re.search(r"\b(i (fixed|updated|changed|committed))\b", low):
        tags.append("AGENT — first-person execution claims need file/receipt proof")
    if not tags:
        tags.append("AGENT — default: treat as agent draft until disk-bound")

    if use_ai:
        user = f"Issues:\n{chr(10).join(issues[:12])}\n\nDraft excerpt:\n{draft[:4000]}"
        ai_text, prov = _ai_call(system="Tag each issue: MODEL | AGENT | DISK | ROUTER. Max 80 words.", user=user)
        if ai_text:
            return {"ok": True, "text": ai_text, "method": prov, "tags": tags}

    text = "\n".join(["Likely source", "", *(f"· {t}" for t in tags)])
    return {"ok": True, "text": text, "method": "rules", "tags": tags}


def _stage_simplify(
    *,
    draft: str,
    parsed: dict,
    issues: list[str],
    use_ai: bool,
    atoms: list[dict] | None = None,
    stats: dict | None = None,
    decision: dict | None = None,
) -> dict:
    from chat_ord_claim_rules_v1 import simplify_from_atoms  # noqa: WPS433

    rules_text = simplify_from_atoms(
        atoms=atoms or [],
        issues=issues,
        stats=stats or {},
        decision=decision,
    )
    if not (atoms or []):
        sample_claim = (parsed.get("claims") or ["(no clear claim)"])[0][:120]
        rules_text = "\n".join(
            [
                "Plain read",
                "",
                "Original vibe",
                f'"{sample_claim}…"',
                "",
                "In human words",
                "The AI gave a long answer mixing plans, claims, and instructions.",
                f"It raised {len(issues)} consistency flag(s) on a quick scan.",
                "Treat green/success words as claims until you see disk paths or receipts.",
            ]
        )
    if use_ai:
        user = f"Claims: {len(atoms or [])}\nIssues: {issues[:6]}\n\nDraft:\n{draft[:5000]}"
        ai_text, prov = _ai_call(system=SIMPLIFY_SYSTEM, user=user)
        if ai_text:
            return {"ok": True, "text": ai_text, "method": prov}
    return {"ok": True, "text": rules_text, "method": "rules"}


def _stage_redflags(*, draft: str, issues: list[str], tags: list[str], stats: dict | None = None) -> dict:
    flags: list[str] = []
    low = draft.lower()
    st = stats or {}
    if st.get("contradictions", 0) > 0:
        flags.append(f"Graph — {st['contradictions']} contradiction edge(s) in claim graph")
    if st.get("disk_mismatch", 0) > 0:
        flags.append(f"Disk — {st['disk_mismatch']} atom(s) disagree with disk")
    if st.get("unverified", 0) > 3:
        flags.append(f"Unverified — {st['unverified']} claims lack disk binding")
    if re.search(r"\b(multi-?agent|orchestrat|dag|routing layer|microservice)\b", low):
        flags.append("Over-complexity — architecture words without one bounded next step")
    if len(draft) > 8000:
        flags.append("Length — very long reply; high risk of mixed truth and filler")
    if re.search(r"\b(guarantee|certainly|definitely|always works)\b", low):
        flags.append("Hallucination risk — absolute certainty language")
    if re.search(r"\b(layers?|pipelines?|tiers?)\b", low) and low.count("layer") + low.count("pipeline") > 4:
        flags.append("Fake layering — many stack words, unclear single action")
    if any("MODEL" in t for t in tags):
        flags.append("Model hallucination risk — verify APIs and file paths")
    if any("DISK" in t for t in tags):
        flags.append("Disk mismatch risk — read receipts before acting")
    if not flags:
        flags.append("Low flag count — still verify any execution claim logged")

    text = "\n".join(["Red flags", "", *(f"· {f}" for f in flags)])
    return {"ok": True, "text": text, "method": "rules", "flags": flags}


def _confidence(*, issues: list[str], flags: list[str], disk: dict) -> int:
    score = 72
    score -= min(30, len(issues) * 6)
    score -= min(20, len(flags) * 4)
    if disk.get("paths_checked"):
        score += 8
    if any("DISK" in str(i) for i in issues):
        score -= 12
    return max(5, min(95, score))


def _stage_report(
    *,
    simplify: str,
    issues: list[str],
    tags: list[str],
    flags: list[str],
    disk: dict,
    stats: dict | None = None,
    atoms: list[dict] | None = None,
) -> dict:
    from chat_ord_claim_rules_v1 import top_verify_actions  # noqa: WPS433

    st = stats or {}
    verify_actions = top_verify_actions(atoms or [], limit=5)
    conf = _confidence(issues=issues, flags=flags, disk=disk)
    if st.get("contradictions"):
        conf = max(5, conf - st["contradictions"] * 8)
    if st.get("disk_mismatch"):
        conf = max(5, conf - st["disk_mismatch"] * 10)
    if st.get("verified"):
        conf = min(95, conf + min(8, st["verified"] * 2))

    issue_lines = [f"· {i}" for i in issues[:6]]
    if not issue_lines and st.get("unverified", 0) > 0:
        issue_lines = [f"· {st['unverified']} checkable claim(s) unverified logged"]
    if not issue_lines:
        issue_lines = ["· none from rules scan"]

    tag_lines = [f"· {t}" for t in tags[:4]]
    flag_lines = [f"· {f}" for f in flags[:5]]
    action_lines = [f"· {a}" for a in verify_actions] or ["· (none — all checkable bound or opinion)"]

    text = "\n".join(
        [
            "ORD report",
            "",
            "Truth counts (rules v1.2)",
            f"· atoms: {st.get('atom_count', 0)} · checkable: {st.get('checkable_count', 0)}",
            f"· verified: {st.get('verified', 0)} · unverified: {st.get('unverified', 0)}",
            f"· mismatch: {st.get('disk_mismatch', 0)} · opinion: {st.get('opinion_count', 0)}",
            f"· skipped fragments: {st.get('skipped_fragments', 0)}",
            f"· graph contradictions: {st.get('contradictions', 0)}",
            "",
            "Simple explanation",
            simplify.split("\n\n")[-1][:400] if simplify else "—",
            "",
            "Detected issues",
            *issue_lines,
            "",
            "Next verify actions",
            *action_lines,
            "",
            "Error source (per-atom tags)",
            *tag_lines,
            "",
            "Red flags",
            *flag_lines,
            "",
            f"Report confidence (heuristic): {conf}/100",
            "Truth gate score (weighted) appears after report stage — not the same number.",
        ]
    )
    return {
        "ok": True,
        "text": text,
        "method": "rules+graph",
        "confidence": conf,
        "issue_count": len(issues),
        "flag_count": len(flags),
        "stats": st,
        "verify_actions": verify_actions,
    }


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
        "schema": "chat-unify-ord-loop-progress-v1",
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


def read_ord_progress() -> dict:
    row = _read_json(PROGRESS_PATH)
    if row.get("schema") != "chat-unify-ord-loop-progress-v1":
        return {"ok": True, "running": False, "stages": {}, "completed_stages": []}
    row["ok"] = True
    return row


def run_ord_loop(
    *,
    draft: str,
    founder_message: str = "",
    use_ai: bool = False,
    write_receipt: bool = True,
    write_progress: bool = True,
) -> dict:
    if not (draft or "").strip():
        return {"ok": False, "error": "empty_text", "message": "Paste AI output first."}

    want = list(STAGE_ORDER)
    out_stages: dict = {}
    completed: list[str] = []

    def _next(after: str | None) -> str | None:
        if after is None:
            return want[0]
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

    _progress(want[0])

    parsed: dict = {}
    buckets: dict = {}
    issues: list[str] = []
    tags: list[str] = []
    flags: list[str] = []
    disk: dict = {}
    simplify_text = ""

    _progress("parse")
    out_stages["parse"] = _stage_parse(draft=draft)
    parsed = out_stages["parse"].get("parsed") or {}
    completed.append("parse")
    _progress(_next("parse"))

    _progress("classify")
    out_stages["classify"] = _stage_classify(parsed=parsed)
    buckets = out_stages["classify"].get("buckets") or {}
    from chat_ord_atoms_v1 import build_atoms_rules, verify_atoms_on_disk, build_claim_graph, atom_stats  # noqa: WPS433
    from chat_ord_claim_rules_v1 import enrich_disk_hints, load_rules, run_consistency_rules  # noqa: WPS433

    atoms = build_atoms_rules(parsed=parsed, buckets=buckets)
    completed.append("classify")
    _progress(_next("classify"))

    _progress("consistency")
    snap = enrich_disk_hints(draft=draft, snap=_disk_hints())
    atoms = verify_atoms_on_disk(atoms=atoms, disk=snap)
    from chat_unify_live_http_verify_v1 import apply_live_http_results, verify_atoms_live_http  # noqa: WPS433

    dv = load_rules().get("deploy_verify") or {}
    if any(a.get("claim_type") == "LIVE_HTTP" for a in atoms):
        http_results = verify_atoms_live_http(
            atoms,
            base_url=str(dv.get("live_http_base_url") or "https://www.noetfield.com"),
            max_requests=int(dv.get("live_http_max_per_run") or 3),
        )
        atoms = apply_live_http_results(
            atoms, http_results, base_url=str(dv.get("live_http_base_url") or "https://www.noetfield.com")
        )
    pre_stats = atom_stats(atoms, {"nodes": [], "edges": []})
    issues = run_consistency_rules(
        draft=draft, parsed=parsed, atoms=atoms, disk=snap, stats=pre_stats
    )
    graph = build_claim_graph(atoms=atoms, issues=issues, draft=draft)
    ord_stats = atom_stats(atoms, graph)
    out_stages["consistency"] = _stage_consistency(
        draft=draft, parsed=parsed, buckets=buckets, issues=issues, disk=snap
    )
    disk = snap
    completed.append("consistency")
    _progress(_next("consistency"))

    _progress("attribution")
    out_stages["attribution"] = _stage_attribution(draft=draft, issues=issues, use_ai=use_ai)
    tags = out_stages["attribution"].get("tags") or []
    completed.append("attribution")
    _progress(_next("attribution"))

    _progress("simplify")
    out_stages["simplify"] = _stage_simplify(
        draft=draft,
        parsed=parsed,
        issues=issues,
        use_ai=use_ai,
        atoms=atoms,
        stats=ord_stats,
        decision=None,
    )
    simplify_text = out_stages["simplify"].get("text") or ""
    completed.append("simplify")
    _progress(_next("simplify"))

    _progress("redflags")
    out_stages["redflags"] = _stage_redflags(draft=draft, issues=issues, tags=tags, stats=ord_stats)
    flags = out_stages["redflags"].get("flags") or []
    completed.append("redflags")
    _progress(_next("redflags"))

    _progress("report")
    out_stages["report"] = _stage_report(
        simplify=simplify_text,
        issues=issues,
        tags=tags,
        flags=flags,
        disk=disk,
        stats=ord_stats,
        atoms=atoms,
    )
    completed.append("report")

    if write_progress:
        _flush_progress(
            running=False,
            current=None,
            completed=completed,
            stages=out_stages,
            stage_order=want,
        )

    report = out_stages.get("report") or {}
    result = {
        "ok": True,
        "schema": "chat-unify-ord-loop-v1",
        "version": LOOP_VERSION,
        "loop": "ord",
        "id": f"ord-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "founder_message": founder_message,
        "use_ai": use_ai,
        "stages": out_stages,
        "stage_order": want,
        "confidence": report.get("confidence"),
        "issue_count": report.get("issue_count"),
        "flag_count": report.get("flag_count"),
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def _apply_truth_gate_to_report(
    *,
    report_stage: dict,
    issues: list[str],
    tags: list[str],
    disk: dict,
    kernel: dict,
    graph: dict | None = None,
    stats: dict | None = None,
    use_ai: bool = False,
    draft: str = "",
) -> dict:
    from chat_ord_claim_rules_v1 import enrich_stats_for_gate  # noqa: WPS433
    from chat_unify_truth_gate_v1 import evaluate_truth_gate, format_decision_block, write_latest_receipt  # noqa: WPS433
    from chat_unify_kernel_v1 import set_decision, save_kernel  # noqa: WPS433

    disk_mismatch = any("DISK:" in str(i) for i in issues) or bool((stats or {}).get("disk_mismatch"))
    atoms = kernel.get("atoms") or []
    gate_stats = enrich_stats_for_gate(atoms, stats or report_stage.get("stats") or {})
    decision = evaluate_truth_gate(
        confidence=report_stage.get("confidence"),
        issue_count=report_stage.get("issue_count") or len(issues),
        flag_count=report_stage.get("flag_count") or 0,
        issues=issues,
        tags=tags,
        disk_mismatch=disk_mismatch,
        stats=gate_stats,
        graph=graph or kernel.get("graph"),
        use_ai=use_ai,
        draft_excerpt=draft,
    )
    report_stage = dict(report_stage)
    report_stage["stats"] = gate_stats
    set_decision(kernel, decision)
    write_latest_receipt(decision, run_id=kernel.get("run_id"))
    gate_text = format_decision_block(decision)
    report_stage = dict(report_stage)
    report_stage["text"] = (report_stage.get("text") or "") + "\n\n" + gate_text
    report_stage["decision"] = decision
    report_stage["truth_gate"] = decision
    kernel["stages"]["report"] = report_stage
    save_kernel(kernel)
    return report_stage, decision


def run_ord_stage(
    stage: str,
    *,
    draft: str,
    founder_message: str = "",
    use_ai: bool = False,
    kernel: dict | None = None,
    run_id: str | None = None,
    write_receipt: bool = True,
) -> dict:
    """Run exactly ONE ORD stage — dependency enforced via persisted kernel."""
    from chat_unify_kernel_v1 import (  # noqa: WPS433
        append_stage_log,
        bind_disk_snapshots,
        ensure_kernel,
        kernel_summary,
        merge_stage_output,
        record_model,
        save_kernel,
        set_atoms,
        set_graph,
    )
    from chat_ord_atoms_v1 import (  # noqa: WPS433
        atom_stats,
        build_atoms_rules,
        build_claim_graph,
        enrich_atoms_ai,
        format_atoms_summary,
        format_graph_summary,
        tag_atom_sources,
        verify_atoms_on_disk,
    )

    sid = (stage or "").strip().lower()
    if sid not in STAGE_ORDER:
        return {"ok": False, "error": "unknown_stage", "message": f"Unknown stage: {stage}"}
    if not (draft or "").strip():
        return {"ok": False, "error": "empty_text", "message": "Paste AI output first."}

    k = ensure_kernel(
        loop="ord",
        draft=draft,
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
            "kernel": k,
            "run_id": k.get("run_id"),
        }

    parsed = (out_stages.get("parse") or {}).get("parsed") or {}
    buckets = (out_stages.get("classify") or {}).get("buckets") or {}
    issues = (out_stages.get("consistency") or {}).get("issues") or []
    tags = (out_stages.get("attribution") or {}).get("tags") or []
    flags = (out_stages.get("redflags") or {}).get("flags") or []
    disk = (out_stages.get("consistency") or {}).get("disk") or {}
    simplify_text = (out_stages.get("simplify") or {}).get("text") or ""
    atoms: list = list(k.get("atoms") or [])
    graph: dict = dict(k.get("graph") or {"nodes": [], "edges": []})
    stats: dict = atom_stats(atoms, graph) if atoms else {}

    if sid == "parse":
        out_stages["parse"] = _stage_parse(draft=draft)
        parsed = out_stages["parse"].get("parsed") or {}
    elif sid == "classify":
        if not parsed:
            parsed = _stage_parse(draft=draft).get("parsed") or {}
        out_stages["classify"] = _stage_classify(parsed=parsed)
        buckets = out_stages["classify"].get("buckets") or {}
        atoms = build_atoms_rules(parsed=parsed, buckets=buckets)
        atoms, atom_method = enrich_atoms_ai(draft=draft, atoms=atoms, use_ai=use_ai)
        set_atoms(k, atoms)
        stats = atom_stats(atoms, graph)
        out_stages["classify"]["atoms"] = atoms
        out_stages["classify"]["atom_count"] = len(atoms)
        out_stages["classify"]["text"] = (
            (out_stages["classify"].get("text") or "")
            + "\n\n"
            + format_atoms_summary(atoms, stats)
        )
        if atom_method != "rules":
            out_stages["classify"]["method"] = atom_method
    elif sid == "consistency":
        from chat_ord_claim_rules_v1 import enrich_disk_hints, run_consistency_rules  # noqa: WPS433

        if not parsed:
            parsed = _stage_parse(draft=draft).get("parsed") or {}
        if not buckets:
            buckets = _stage_classify(parsed=parsed).get("buckets") or {}
        if not atoms:
            atoms = build_atoms_rules(parsed=parsed, buckets=buckets)
        snap = enrich_disk_hints(draft=draft, snap=_disk_hints())
        atoms = verify_atoms_on_disk(atoms=atoms, disk=snap)
        from chat_ord_claim_rules_v1 import load_rules  # noqa: WPS433
        from chat_unify_live_http_verify_v1 import (  # noqa: WPS433
            apply_live_http_results,
            verify_atoms_live_http,
        )

        dv = load_rules().get("deploy_verify") or {}
        base_url = str(dv.get("live_http_base_url") or "https://www.noetfield.com")
        max_http = int(dv.get("live_http_max_per_run") or 3)
        if any(a.get("claim_type") == "LIVE_HTTP" for a in atoms):
            http_results = verify_atoms_live_http(atoms, base_url=base_url, max_requests=max_http)
            atoms = apply_live_http_results(atoms, http_results, base_url=base_url)
            snap["live_http_verify"] = http_results
        stats = atom_stats(atoms, {"nodes": [], "edges": []})
        issues = run_consistency_rules(
            draft=draft, parsed=parsed, atoms=atoms, disk=snap, stats=stats
        )
        graph = build_claim_graph(atoms=atoms, issues=issues, draft=draft)
        stats = atom_stats(atoms, graph)
        out_stages["consistency"] = _stage_consistency(
            draft=draft, parsed=parsed, buckets=buckets, issues=issues, disk=snap
        )
        disk = snap
        set_atoms(k, atoms)
        set_graph(k, graph)
        out_stages["consistency"]["graph"] = graph
        out_stages["consistency"]["stats"] = stats
        out_stages["consistency"]["text"] = (
            (out_stages["consistency"].get("text") or "")
            + "\n\n"
            + format_graph_summary(graph, stats)
        )
    elif sid == "attribution":
        if not atoms:
            atoms = list(k.get("atoms") or [])
        atoms = tag_atom_sources(atoms=atoms, draft=draft, issues=issues)
        set_atoms(k, atoms)
        tag_lines = [f"· [{a['id']}] {a.get('source_tag')} — {a['text'][:80]}" for a in atoms[:8]]
        tag_text = "\n".join(["Per-atom source tags", ""] + (tag_lines or ["· (none)"]))
        base = _stage_attribution(draft=draft, issues=issues, use_ai=use_ai)
        out_stages["attribution"] = base
        out_stages["attribution"]["text"] = tag_text + "\n\n" + (base.get("text") or "")
        tags = [f"{a.get('source_tag')} — {a['text'][:60]}" for a in atoms[:6]]
        out_stages["attribution"]["tags"] = tags
        out_stages["attribution"]["atoms"] = atoms
    elif sid == "simplify":
        stats = atom_stats(atoms, graph) if atoms else stats
        out_stages["simplify"] = _stage_simplify(
            draft=draft,
            parsed=parsed,
            issues=issues,
            use_ai=use_ai,
            atoms=atoms,
            stats=stats,
            decision=k.get("decision"),
        )
        simplify_text = out_stages["simplify"].get("text") or ""
    elif sid == "redflags":
        stats = atom_stats(atoms, graph) if atoms else stats
        out_stages["redflags"] = _stage_redflags(draft=draft, issues=issues, tags=tags, stats=stats)
        flags = out_stages["redflags"].get("flags") or []
    elif sid == "report":
        stats = atom_stats(atoms, graph) if atoms else stats
        out_stages["report"] = _stage_report(
            simplify=simplify_text,
            issues=issues,
            tags=tags,
            flags=flags,
            disk=disk,
            stats=stats,
            atoms=atoms,
        )
        merge_stage_output(k, out_stages)
        out_stages["report"], _decision = _apply_truth_gate_to_report(
            report_stage=out_stages["report"],
            issues=issues,
            tags=tags,
            disk=disk,
            kernel=k,
            graph=graph,
            stats=stats,
            use_ai=use_ai,
            draft=draft,
        )

    merge_stage_output(k, out_stages)
    if sid == "consistency":
        bind_disk_snapshots(k, disk)

    stage_ok = bool(out_stages.get(sid, {}).get("ok", True))
    method = (out_stages.get(sid) or {}).get("method")
    if use_ai and method and ("ai" in str(method) or method == "openrouter"):
        record_model(k, provider="openrouter", method=str(method))
    append_stage_log(k, stage=sid, depends_on=dep, ok=stage_ok, method=method)
    save_kernel(k)

    idx = STAGE_ORDER.index(sid)
    next_stage = STAGE_ORDER[idx + 1] if idx + 1 < len(STAGE_ORDER) else None
    report = out_stages.get("report") or {}
    decision = k.get("decision") or report.get("decision")

    result: dict = {
        "ok": stage_ok,
        "schema": "chat-unify-ord-loop-stage-v1",
        "version": LOOP_VERSION,
        "execution_mode": "sequential_single_stage",
        "loop": "ord",
        "stage": sid,
        "next_stage": next_stage,
        "depends_on": dep,
        "stages": out_stages,
        "kernel": k,
        "run_id": k.get("run_id"),
        "kernel_summary": kernel_summary(k),
        "atoms": k.get("atoms"),
        "graph": k.get("graph"),
        "stats": stats if sid == "report" else atom_stats(atoms, graph) if atoms else None,
        "use_ai": use_ai,
    }

    if sid == "report":
        result["confidence"] = report.get("confidence")
        result["issue_count"] = report.get("issue_count")
        result["flag_count"] = report.get("flag_count")
        result["decision"] = decision
        result["truth_gate"] = decision
        result["stats"] = report.get("stats") or stats
        if write_receipt:
            full = {
                "ok": True,
                "schema": "chat-unify-ord-loop-v1",
                "version": LOOP_VERSION,
                "loop": "ord",
                "id": f"ord-{uuid.uuid4().hex[:10]}",
                "at": _now(),
                "founder_message": founder_message,
                "use_ai": use_ai,
                "stages": out_stages,
                "stage_order": list(STAGE_ORDER),
                "confidence": report.get("confidence"),
                "issue_count": report.get("issue_count"),
                "flag_count": report.get("flag_count"),
                "decision": decision,
                "run_id": k.get("run_id"),
            }
            SINA.mkdir(parents=True, exist_ok=True)
            RECEIPT.write_text(json.dumps(full, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return result


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="ORD loop v0.1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--ai", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_ord_loop(
        draft=args.text,
        founder_message=args.founder_message,
        use_ai=args.ai,
        write_receipt=True,
        write_progress=True,
    )
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        for sid in row.get("stage_order") or []:
            st = row.get("stages", {}).get(sid) or {}
            print(f"\n=== {sid.upper()} ===\n{st.get('text', '')[:500]}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
