#!/usr/bin/env python3
"""Cloud comprehension pipeline loop — C1→C7 + output analyst (disk vs agent vs machines).

Every agent answer is OUTPUT. Analyst diagnoses root cause → ACCEPT · RETURN_TO_AGENT · FIX_DISK · FIX_MACHINES.

SSOT: data/cloud-comprehension-pipeline-loop-v1.json
Receipt: ~/.sina/cloud-comprehension-pipeline-loop-receipt-v1.json
Log: ~/.sina/agent-output-quality-log-v1.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/cloud-comprehension-pipeline-loop-v1.json"
RECEIPT = SINA / "cloud-comprehension-pipeline-loop-receipt-v1.json"
LOG = SINA / "agent-output-quality-log-v1.jsonl"

INTENT_VERB = re.compile(
    r"\b(why|what|how|understand|explain|mean|block|defer|email|form|cloud|problem|bug)\b",
    re.I,
)
FOUNDER_ASKS = re.compile(r"\b(why|what|how|explain|understand|mean|analyze|quality)\b", re.I)
BENEFIT_HINT = re.compile(
    r"\b(you|your|for you|means|because|so |which means|blocked|ready|helps|matters)\b",
    re.I,
)
PROOF_HINT = re.compile(r"(\.json|\.md|receipts/|data/|~/.sina/)", re.I)
MEANING_MIN = 65


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _append_log(row: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    slim = {
        "at": row.get("at"),
        "output_verdict": row.get("output_verdict"),
        "root_cause": row.get("root_cause"),
        "meaning_score": row.get("meaning_score"),
        "attempt": row.get("attempt"),
        "return_reasons": row.get("return_package", {}).get("return_reasons") or [],
    }
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(slim, ensure_ascii=False) + "\n")


def _attempt_count() -> int:
    if not LOG.is_file():
        return 0
    try:
        lines = [ln for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return len(lines)
    except OSError:
        return 0


def _circle_understand(founder_message: str) -> dict:
    msg = (founder_message or "").strip()
    if not msg:
        return {
            "id": "C1",
            "name": "understand",
            "ok": True,
            "intent_line": "Founder message not provided — infer from latest turn.",
            "keywords": [],
        }
    keys = [
        w.lower()
        for w in re.findall(r"[a-zA-Z']{4,}", msg)
        if w.lower() not in {"that", "this", "with", "from", "have", "your", "this", "every", "agent"}
    ]
    intent = msg[:200]
    low = msg.lower()
    if "why" in low:
        intent = "Founder wants to understand why something is blocked or how it works."
    elif "main problem" in low or "north star" in low:
        intent = "Founder wants the real priority — not a status report."
    elif any(w in low for w in ("comprehension", "buzzword", "quality", "analyze", "output")):
        intent = "Founder wants agent answers analyzed for quality — plain language, accept or send back for rewrite."
    return {
        "id": "C1",
        "name": "understand",
        "ok": bool(msg),
        "intent_line": intent,
        "keywords": keys[:12],
    }


def scan_disk_bug_signals() -> list[dict]:
    """C5 — plain-English issues from live disk for gradual system debugging."""
    signals: list[dict] = []
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    portfolio = str(surfaces.get("portfolio_line") or "")
    if "RED" in portfolio.upper() or "FAIL" in portfolio.upper():
        signals.append(
            {
                "id": "portfolio_site",
                "plain": "At least one public product site still fails its live check — outbound email may stay blocked.",
                "disk": "portfolio_line",
            }
        )
    defer_r = _read(SINA / "commercial-email-send-defer-receipt-v1.json")
    if defer_r.get("defer_active") or defer_r.get("send_ready") is False:
        signals.append(
            {
                "id": "email_defer",
                "plain": "Outbound email send is still blocked until all product sites pass checks.",
                "disk": "commercial-email-send-defer-receipt-v1.json",
            }
        )
    gate = _read(SINA / "agent_session_gate_receipt_v1.json")
    if gate and gate.get("ok") is False:
        failed = [str(s.get("step")) for s in (gate.get("steps") or []) if not s.get("ok")]
        if failed:
            signals.append(
                {
                    "id": "session_gate",
                    "plain": f"Some automatic session checks are failing ({', '.join(failed[:4])}) — disk layers may need sync.",
                    "disk": "agent_session_gate_receipt_v1.json",
                }
            )
    drift = _read(SINA / "governance_drift_report_v1.json")
    score = drift.get("drift_score")
    if isinstance(score, (int, float)) and score < 85:
        signals.append(
            {
                "id": "governance_drift",
                "plain": f"Governance drift score is {score} (target ≥85) — queue or mirror may be out of sync.",
                "disk": "governance_drift_report_v1.json",
            }
        )
    mp = _read(SINA / "main-problem-trigger-receipt-v1.json")
    if mp.get("mode") == "PREPARE_NOT_REPORT" and mp.get("next_action"):
        na = mp["next_action"]
        signals.append(
            {
                "id": "main_problem_next",
                "plain": f"North-star next action logged: {na.get('because') or na.get('action')}.",
                "disk": "main-problem-trigger-receipt-v1.json",
            }
        )
    return signals[:8]


POISON_MARKERS = re.compile(
    r"\b(never say|do not inject|prohibition table|never inject|forbidden inject)\b",
    re.I,
)
STALE_MINUTES = 45


def _iso_age_minutes(iso: str) -> float | None:
    if not iso:
        return None
    try:
        raw = iso.replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 60.0
    except (ValueError, TypeError):
        return None


def run_output_analyst(*, draft: str, issue_signals: list[dict]) -> dict:
    """C6 analyst — root cause: agent draft vs disk stale/wrong/poison vs machines."""
    ssot = _read(SSOT)
    fix_map = (ssot.get("output_analyst") or {}).get("fix_commands") or {}
    findings: list[dict] = []
    root = "AGENT_DRAFT"
    priority = 0

    anti = _read(SINA / "anti-staleness-auto-wire-v1.json")
    surfaces = _read(SINA / "agent-live-surfaces-v1.json")
    mirror = _read(SINA / "agent-memory-mirror-v1.json")
    gate = _read(SINA / "agent_session_gate_receipt_v1.json")
    drift = _read(SINA / "governance_drift_report_v1.json")
    vocab = _read(SINA / "vocabulary-guard-receipt-v1.json")

    for label, path, age_limit in (
        ("anti_staleness", anti.get("at"), STALE_MINUTES),
        ("live_surfaces", surfaces.get("synced_at"), STALE_MINUTES),
        ("session_gate", gate.get("at"), STALE_MINUTES * 2),
    ):
        age = _iso_age_minutes(str(path or ""))
        if age is not None and age > age_limit:
            findings.append(
                {
                    "id": "disk_stale",
                    "plain": f"{label} receipt is {int(age)} minutes old — agent may parrot stale inject.",
                    "disk": label,
                }
            )
            if priority < 3:
                root, priority = "DISK_STALE", 3

    if anti.get("ok") is False:
        findings.append(
            {
                "id": "anti_staleness_fail",
                "plain": "Anti-staleness wire failed — disk truth may not match what agents read.",
                "disk": "anti-staleness-auto-wire-v1.json",
            }
        )
        root, priority = "DISK_STALE", max(priority, 3)

    inject_blob = json.dumps(mirror.get("inject") or {}, ensure_ascii=False)[:8000]
    if POISON_MARKERS.search(inject_blob):
        findings.append(
            {
                "id": "inject_poison",
                "plain": "Agent mirror inject contains prohibition/poison vocabulary — answers echo meaningless labels.",
                "disk": "agent-memory-mirror-v1.json",
            }
        )
        root, priority = "DISK_POISON", max(priority, 4)

    if vocab.get("ok") is False:
        findings.append(
            {
                "id": "vocabulary_fail",
                "plain": "Vocabulary guard failed — what agents read may be stale or forbidden phrasing.",
                "disk": "vocabulary-guard-receipt-v1.json",
            }
        )
        root, priority = "DISK_POISON", max(priority, 4)

    q_surf = str(surfaces.get("queue_sa") or "")
    q_anti = str(anti.get("queue_sa") or "")
    if q_surf and q_anti and q_surf != q_anti:
        findings.append(
            {
                "id": "queue_mismatch",
                "plain": f"Queue mismatch locally (surfaces={q_surf} vs anti-staleness={q_anti}) — agent cites wrong task.",
                "disk": "queue_sa",
            }
        )
        root, priority = "DISK_WRONG", max(priority, 4)

    drift_score = drift.get("drift_score")
    if isinstance(drift_score, (int, float)) and drift_score < 85:
        findings.append(
            {
                "id": "governance_drift",
                "plain": f"Governance drift score {drift_score} — machine layers out of sync.",
                "disk": "governance_drift_report_v1.json",
            }
        )
        root, priority = "MACHINE_STALE", max(priority, 3)

    if gate.get("ok") is False:
        machine_steps = [
            s.get("step")
            for s in (gate.get("steps") or [])
            if not s.get("ok")
            and str(s.get("step") or "") in ("governance_zero_drift", "anti_staleness", "disk_live_wire")
        ]
        if machine_steps:
            findings.append(
                {
                    "id": "machine_gate_fail",
                    "plain": f"Session machine checks failing: {', '.join(machine_steps[:3])}.",
                    "disk": "agent_session_gate_receipt_v1.json",
                }
            )
            root, priority = "MACHINE_STALE", max(priority, 3)

    if len(issue_signals) >= 3 and not quality_draft_only(draft):
        findings.append(
            {
                "id": "many_disk_signals",
                "plain": "Multiple live disk issues — bad output may be symptom of disk not agent alone.",
                "disk": "comprehension C5",
            }
        )
        if priority < 2:
            root, priority = "DISK_STALE", 2

    fix_commands = list(fix_map.get(root) or [])
    analyst_line = (
        f"analyst · root={root} · findings={len(findings)} · "
        + (findings[0]["plain"][:72] if findings else "disk inject looks current")
    )
    return {
        "id": "C6",
        "name": "output_analyst",
        "ok": root == "AGENT_DRAFT" or not findings,
        "root_cause": root,
        "findings": findings[:8],
        "fix_commands": fix_commands,
        "analyst_line": analyst_line,
        "disk_ok": len(findings) == 0,
    }


def quality_draft_only(draft: str) -> bool:
    return len((draft or "").split()) < 20


def _analyze_output(
    *,
    draft: str,
    founder_message: str,
    c1: dict,
    c2: dict,
    c3: dict,
    quality: dict,
    lang: dict,
    analyst: dict,
) -> dict:
    """C7 output gate — ACCEPT · RETURN_TO_AGENT · FIX_DISK · FIX_MACHINES."""
    return_reasons: list[str] = []
    score = quality.get("meaning_score")
    draft_bad = False
    if score is not None and score < MEANING_MIN:
        return_reasons.append(f"Meaning score {score} below {MEANING_MIN} — not helpful for founder")
        draft_bad = True
    if not quality.get("ok"):
        return_reasons.append(f"Quality loop verdict: {quality.get('verdict') or 'REJECT'}")
        draft_bad = True
    if not c2.get("ok"):
        draft_bad = True
        for hit in c2.get("language_hits") or []:
            return_reasons.append(hit.get("label") or hit.get("id") or "language hit")
    founder_asked = bool(FOUNDER_ASKS.search(founder_message or ""))
    long_reply = len((draft or "").split()) > 40
    if founder_asked and long_reply and not c3.get("ok"):
        return_reasons.append("Founder asked for understanding — missing benefit (what it means for you)")
        draft_bad = True

    rewrite_hints = list(quality.get("rewrite_hints") or [])
    rewrite_order = [
        "If analyst says FIX_DISK — run fix_commands · sync mirror · then rewrite",
        "C1 — Restate what the founder needs in one plain sentence",
        "C2 — Explain in normal English · because / so · translate buzzwords once",
        "C3 — Say what it means for the founder (blocked · ready · matters)",
        "C4 — Add disk proof after explanation — not instead of it",
        "Re-run output analysis until ACCEPT",
    ]

    root = analyst.get("root_cause") or "AGENT_DRAFT"
    findings = analyst.get("findings") or []
    fix_commands = analyst.get("fix_commands") or []

    if not draft_bad and quality.get("ok") and c2.get("ok"):
        verdict = "ACCEPT"
        accepted = quality.get("founder_text") or draft.strip()
        agent_line = "Output ACCEPT — ship accepted_founder_text to founder."
    elif root == "DISK_POISON" and findings:
        verdict = "FIX_DISK"
        accepted = ""
        agent_line = "Analyst: inject poison/stale vocabulary in the repository — scrub mirror before blaming agent."
        return_reasons = [f["plain"] for f in findings[:4]] + return_reasons[:2]
    elif root in ("DISK_STALE", "DISK_WRONG") and findings and draft_bad:
        verdict = "FIX_DISK"
        accepted = ""
        agent_line = (
            "Analyst: disk/inject stale or wrong — sync live wire + mirror, then rewrite answer."
        )
        return_reasons = [f["plain"] for f in findings[:4]] + return_reasons[:2]
    elif root == "MACHINE_STALE" and findings:
        verdict = "FIX_MACHINES"
        accepted = ""
        agent_line = "Analyst: governance/factory machines drift — heal tier session before rewrite."
        return_reasons = [f["plain"] for f in findings[:4]] + return_reasons[:2]
    elif draft_bad:
        verdict = "RETURN_TO_AGENT"
        accepted = ""
        agent_line = (
            "Analyst: disk OK — agent draft problem. Rewrite before founder sees this. "
            + (return_reasons[0] if return_reasons else "Not plain enough")
        )
    else:
        verdict = "ACCEPT"
        accepted = quality.get("founder_text") or draft.strip()
        agent_line = "Output ACCEPT — ship accepted_founder_text to founder."

    return {
        "id": "C7",
        "name": "output_quality_gate",
        "output_verdict": verdict,
        "root_cause": root,
        "ok": verdict == "ACCEPT",
        "accepted_founder_text": accepted,
        "return_reasons": return_reasons[:8],
        "rewrite_hints": rewrite_hints[:8],
        "rewrite_order": rewrite_order,
        "fix_commands": fix_commands if verdict in ("FIX_DISK", "FIX_MACHINES") else [],
        "analyst_findings": findings[:6],
        "agent_line": agent_line,
        "founder_sees": accepted if verdict == "ACCEPT" else "(blocked — fix disk/machines or rewrite first)",
    }


def run_loop(
    *,
    draft: str,
    founder_message: str = "",
    write: bool = True,
) -> dict:
    ssot = _read(SSOT)
    c1 = _circle_understand(founder_message)

    sys_path = str(SCRIPTS)
    import sys

    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)

    # Cloud primary — Railway FBE comprehension bay (no Mac validator stack).
    try:
        from cloud_comprehension_bay_client_v1 import analyze_via_cloud  # noqa: WPS433

        cloud = analyze_via_cloud(
            draft=draft,
            founder_message=founder_message,
            write_receipt=write,
        )
        ff = cloud.get("for_founder") or {}
        if cloud.get("ok") and ff.get("show_this"):
            attempt = _attempt_count() + 1
            ship_text = str(ff["show_this"])
            row = {
                "schema": "cloud-comprehension-pipeline-loop-receipt-v1",
                "at": _now(),
                "ok": True,
                "output_verdict": "ACCEPT",
                "root_cause": "CLOUD_BAY",
                "execution_plane": cloud.get("execution_plane") or "headless_cloud",
                "cloud_primary": True,
                "accepted_founder_text": ship_text,
                "founder_comprehension_text": ship_text,
                "circles": [
                    c1,
                    {"id": "C2", "name": "explain", "ok": True, "explain_text": ship_text[:1200]},
                    {"id": "C7", "name": "output_quality_gate", "ok": True, "output_verdict": "ACCEPT"},
                ],
                "attempt": attempt,
                "comprehension_line": cloud.get("one_line") or "comprehension · cloud bay · ACCEPT",
                "output_quality_line": "cloud bay · ACCEPT · Railway FBE",
                "one_law": ssot.get("one_law"),
                "ssot": str(SSOT.relative_to(ROOT)),
            }
            if write:
                SINA.mkdir(parents=True, exist_ok=True)
                RECEIPT.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                _append_log(row)
            return row
    except Exception:
        pass

    from founder_reply_quality_loop_v1 import run_loop as quality_loop  # noqa: WPS433
    from agent_report_language_gate_v1 import scan_text as scan_language  # noqa: WPS433

    quality = quality_loop(draft=draft, founder_message=founder_message, write_receipt=False)
    ship_text = quality.get("founder_text") or draft.strip()
    lang = scan_language(ship_text, founder_asked_why=bool(INTENT_VERB.search(founder_message or "")))

    c2 = {
        "id": "C2",
        "name": "explain",
        "ok": bool(ship_text) and lang.get("ok", True),
        "explain_text": ship_text[:1200],
        "verdict": quality.get("verdict"),
        "language_hits": lang.get("hits") or [],
    }
    c3 = {
        "id": "C3",
        "name": "benefit",
        "ok": bool(BENEFIT_HINT.search(ship_text[:600])) or len(ship_text) < 80,
        "benefit_line": _extract_benefit_line(ship_text),
    }
    c4 = {
        "id": "C4",
        "name": "proof",
        "ok": True,
        "proof_refs": PROOF_HINT.findall(draft)[:6],
        "note": "Proof paths belong after explanation in final reply",
    }
    issue_signals = scan_disk_bug_signals()
    c5 = {
        "id": "C5",
        "name": "bug_signal",
        "ok": True,
        "issue_signals": issue_signals,
        "count": len(issue_signals),
    }
    c6 = run_output_analyst(draft=draft, issue_signals=issue_signals)
    c7 = _analyze_output(
        draft=draft,
        founder_message=founder_message,
        c1=c1,
        c2=c2,
        c3=c3,
        quality=quality,
        lang=lang,
        analyst=c6,
    )

    attempt = _attempt_count() + 1
    row = {
        "schema": "cloud-comprehension-pipeline-loop-receipt-v1",
        "at": _now(),
        "ok": c7.get("ok"),
        "output_verdict": c7.get("output_verdict"),
        "root_cause": c7.get("root_cause") or c6.get("root_cause"),
        "circles": [c1, c2, c3, c4, c5, c6, c7],
        "accepted_founder_text": c7.get("accepted_founder_text") or "",
        "founder_comprehension_text": c7.get("accepted_founder_text") or "",
        "return_package": {
            "verdict": c7.get("output_verdict"),
            "root_cause": c7.get("root_cause"),
            "return_reasons": c7.get("return_reasons") or [],
            "rewrite_hints": c7.get("rewrite_hints") or [],
            "rewrite_order": c7.get("rewrite_order") or [],
            "fix_commands": c7.get("fix_commands") or [],
            "analyst_findings": c7.get("analyst_findings") or [],
            "agent_line": c7.get("agent_line"),
        },
        "analyst_line": c6.get("analyst_line"),
        "quality_verdict": quality.get("verdict"),
        "meaning_score": quality.get("meaning_score"),
        "attempt": attempt,
        "comprehension_line": _compose_line(c7, c5, c6, quality),
        "output_quality_line": _output_quality_line(c7, c6, quality, attempt),
        "one_law": ssot.get("one_law"),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _append_log(row)
    return row


def _extract_benefit_line(text: str) -> str:
    for sent in re.split(r"(?<=[.!?])\s+", text.strip()):
        if BENEFIT_HINT.search(sent):
            return sent.strip()[:280]
    return text.strip()[:180] if text else ""


def _compose_line(c7: dict, c5: dict, c6: dict, quality: dict) -> str:
    v = c7.get("output_verdict") or quality.get("verdict") or "?"
    root = c6.get("root_cause") or "?"
    score = quality.get("meaning_score")
    bugs = c5.get("count", 0)
    return f"comprehension · C1→C7 · {v} · root={root} · score={score} · bugs={bugs}"


def _output_quality_line(c7: dict, c6: dict, quality: dict, attempt: int) -> str:
    v = c7.get("output_verdict") or "?"
    root = c6.get("root_cause") or "AGENT_DRAFT"
    score = quality.get("meaning_score")
    return (
        f"output-quality · {v} · root={root} · score={score} · attempt={attempt} · "
        "analyst reduces bugs staleness poison"
    )


def inject_slice() -> dict:
    ssot = _read(SSOT)
    row = _read(RECEIPT)
    og = ssot.get("output_quality_gate") or {}
    oa = ssot.get("output_analyst") or {}
    out = {
        "one_law": ssot.get("one_law"),
        "circles": ssot.get("circles") or [],
        "loop_back": ssot.get("loop_back"),
        "output_analyst": {
            "one_law": oa.get("one_law"),
            "root_causes": oa.get("root_causes"),
        },
        "output_quality_gate": {
            "one_law": og.get("one_law"),
            "verdicts": og.get("verdicts"),
        },
        "command": "python3 scripts/cloud_comprehension_pipeline_loop_v1.py --text '<draft>' --founder-message '<founder>' --json",
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if row.get("output_quality_line"):
        out["output_quality_line"] = row["output_quality_line"]
        out["analyst_line"] = row.get("analyst_line")
        out["last_output_verdict"] = row.get("output_verdict")
        out["last_root_cause"] = row.get("root_cause")
        out["comprehension_line"] = row.get("comprehension_line")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloud comprehension pipeline loop v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--file")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--disk-bugs", action="store_true", help="C5 only — scan disk issue signals")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.inject:
        row = inject_slice()
    elif args.disk_bugs:
        row = {"ok": True, "issue_signals": scan_disk_bug_signals()}
    else:
        body = args.text
        if args.file:
            body = Path(args.file).read_text(encoding="utf-8", errors="replace")
        row = run_loop(draft=body, founder_message=args.founder_message, write=True)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("output_quality_line") or row.get("comprehension_line") or row.get("one_law"))
    if args.inject or args.disk_bugs:
        return 0 if row.get("ok", True) else 1
    return 0 if row.get("output_verdict") else 1


if __name__ == "__main__":
    raise SystemExit(main())
