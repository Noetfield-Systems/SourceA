#!/usr/bin/env python3
"""Agent session scoreboard — track reports, auto-check compliance, auto-green when checks pass.

No ASF eval/progress authority (PLAN WITH NO ASF)
-------------------------------------------------
Fleet green = ``auto_pass`` from machine auto-checks only — not founder click, not manual attestation.
``verify_report(..., force=True)`` is maintainer API override only; default path is ``_auto_verify``
(``verified_by: auto`` on ``auto_pass`` — sa-0301).
Eval gates (Eval-1/1b) live in validators + ``~/.sina/*_report.json`` — not scoreboard verify column.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_workspace_registry import AGENT_WORKSPACES, GOVERNANCE_VERSION, get_workspace

SINA_HOME = Path.home() / ".sina"
SCOREBOARD_ROOT = SINA_HOME / "agent-scoreboard"
REPORTS_PATH = SCOREBOARD_ROOT / "reports.jsonl"
VERIFIED_PATH = SCOREBOARD_ROOT / "verified.json"

LAW_DOC = "AGENT_SCOREBOARD_LOCKED_v1.md"
SCOREBOARD_TAGLINE = (  # sa-0304
    "Every agent chat files a session report — auto-checks green rows when machine checks pass "
    "(not ASF verify)"
)
FLEET_AUTO_GREEN_COUNT_KEY = "fleet_auto_green_count"  # sa-0302, sa-0352
REPORT_WINDOW_HOURS = 72

REQUIREMENTS: list[dict] = [
    {"id": "session_report", "label": "Session report filed", "auto": True},
    {"id": "council_brief", "label": "Council brief attested", "auto": False},
    {"id": "vault_deposit", "label": "Vault document deposited", "auto": True},
    {"id": "vault_activity", "label": "Activity logged in vault", "auto": True},
    {"id": "workspace_ready", "label": "Workspace integration ready", "auto": True},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_at(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_reports(limit: int = 500) -> list[dict]:
    if not REPORTS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in REPORTS_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _append_report(row: dict) -> None:
    SCOREBOARD_ROOT.mkdir(parents=True, exist_ok=True)
    with REPORTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_verified() -> dict:
    if not VERIFIED_PATH.is_file():
        return {}
    try:
        return json.loads(VERIFIED_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_verified(data: dict) -> None:
    SCOREBOARD_ROOT.mkdir(parents=True, exist_ok=True)
    VERIFIED_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _latest_report(agent_id: str) -> dict | None:
    rows = [r for r in _load_reports() if r.get("agent_id") == agent_id]
    return rows[-1] if rows else None


def _activity_since(agent_id: str, since: datetime | None) -> list[dict]:
    try:
        from agent_workspace_vault import _load_activity  # noqa: WPS433

        acts = _load_activity(agent_id, limit=200)
    except Exception:
        return []
    if not since:
        return acts
    out = []
    for a in acts:
        at = _parse_at(a.get("at") or "")
        if at and at >= since:
            out.append(a)
    return out


def _docs_since(agent_id: str, since: datetime | None) -> list[dict]:
    try:
        from agent_workspace_vault import _list_documents  # noqa: WPS433

        docs = _list_documents(agent_id, limit=50)
    except Exception:
        return []
    if not since:
        return docs
    out = []
    for d in docs:
        at = _parse_at(d.get("deposited_at") or "")
        if at and at >= since:
            out.append(d)
    return out


def _integration_ready(agent_id: str) -> dict:
    try:
        from agent_council_room import workspace_integration_readiness  # noqa: WPS433
        from agent_private_workspaces import WORKSPACES_ROOT  # noqa: WPS433
        from loop_pack_registry import pack_paths  # noqa: WPS433

        spec = get_workspace(agent_id)
        if not spec:
            return {"ok": False, "pct": 0}
        private_root = WORKSPACES_ROOT / agent_id
        pack_ready = False
        pid = spec.get("pack_id")
        if pid:
            _c, pack_p, _ = pack_paths(pid)
            pack_ready = bool(pack_p and pack_p.is_file())
        integration = workspace_integration_readiness(
            spec,
            private_root=private_root,
            pack_ready=pack_ready,
            incident={},
        )
        return {"ok": bool(integration.get("ready")), "pct": integration.get("pct", 0)}
    except Exception:
        return {"ok": False, "pct": 0}


def _run_auto_checks(agent_id: str, report: dict | None) -> dict[str, dict]:
    checks: dict[str, dict] = {}
    report_at = _parse_at((report or {}).get("at") or "")
    window_start = report_at
    if report_at:
        window_start = report_at - timedelta(hours=REPORT_WINDOW_HOURS)

    summary = (report or {}).get("summary") or ""
    attest = (report or {}).get("attestations") or {}

    checks["session_report"] = {
        "ok": bool(report) and len(summary.strip()) >= 40,
        "detail": "Report ≥40 chars" if report else "No report",
    }
    checks["council_brief"] = {
        "ok": bool(attest.get("council_brief")),
        "detail": "Self-attested in report" if attest.get("council_brief") else "Not attested",
    }
    docs = _docs_since(agent_id, window_start)
    checks["vault_deposit"] = {
        "ok": len(docs) > 0,
        "detail": f"{len(docs)} doc(s) in window",
    }
    acts = _activity_since(agent_id, window_start)
    checks["vault_activity"] = {
        "ok": len(acts) > 0,
        "detail": f"{len(acts)} activity row(s) in window",
    }
    integ = _integration_ready(agent_id)
    checks["workspace_ready"] = {
        "ok": bool(integ.get("ok")),
        "detail": f"Integration {integ.get('pct', 0)}%",
    }
    return checks


def _all_auto_pass(checks: dict[str, dict], *, include_attest: bool = True) -> bool:
    for req in REQUIREMENTS:
        cid = req["id"]
        if cid == "council_brief" and not include_attest:
            continue
        if not checks.get(cid, {}).get("ok"):
            return False
    return True


def _chat_pointer(spec: dict) -> dict:
    aid = spec["id"]
    return {
        "agent_id": aid,
        "label": spec.get("label"),
        "cursor_workspace": spec.get("cursor_workspace_hint") or "",
        "repo_root": spec.get("repo_root") or "",
        "hub_tab": f"workspace-{aid}",
        "hub_url": f"http://127.0.0.1:13020/?tab=workspace-{aid}",
        "thread": spec.get("thread") or "",
        "lane": spec.get("lane") or "",
    }


def submit_report(
    agent_id: str,
    *,
    summary: str,
    chat_pointer: str = "",
    attestations: dict | None = None,
    source: str = "app",
) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    summary = (summary or "").strip()
    if len(summary) < 40:
        return {"ok": False, "error": "Session report must be at least 40 characters"}
    attest = {
        "council_brief": bool((attestations or {}).get("council_brief")),
        "vault_used": bool((attestations or {}).get("vault_used")),
        "no_sourcea_edit": bool((attestations or {}).get("no_sourcea_edit", True)),
    }
    row = {
        "id": f"RPT-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "agent_id": agent_id,
        "label": spec.get("label"),
        "summary": summary[:8000],
        "chat_pointer": (chat_pointer or spec.get("cursor_workspace_hint") or "")[:200],
        "attestations": attest,
        "source": source,
    }
    _append_report(row)
    checks = _run_auto_checks(agent_id, row)
    row["auto_checks"] = checks
    row["auto_pass"] = _all_auto_pass(checks)
    if row["auto_pass"]:
        _auto_verify(agent_id, report=row, checks=checks)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event("session_report", workspace_id=agent_id, detail=summary[:200])
    except Exception:
        pass
    try:
        from agent_workspace_vault import log_activity  # noqa: WPS433

        log_activity(agent_id, action="session_report_filed", detail=summary[:120], kind="report", source="scoreboard")
    except Exception:
        pass
    return {"ok": True, "report": row}


def _auto_verify(agent_id: str, *, report: dict, checks: dict) -> dict:
    """Persist machine verify when auto_pass — never ASF/founder attestation (sa-0301, sa-0351)."""
    verified = _load_verified()
    row = {
        "report_id": report.get("id"),
        "verified_at": _now(),
        "verified_by": "auto",
        "auto_checks": checks,
    }
    verified[agent_id] = row
    _save_verified(verified)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "scoreboard_auto_verified",
            workspace_id=agent_id,
            detail=report.get("id", ""),
        )
    except Exception:
        pass
    return row


def _maybe_backfill_auto_verify(
    agent_id: str,
    *,
    report: dict | None,
    checks: dict,
    ver: dict,
    auto_pass: bool,
) -> dict:
    """Persist auto verify when auto_pass + report — backfill stale/missing rows (sa-0303, sa-0353)."""
    if not (auto_pass and report):
        return ver
    stale = (
        not ver
        or ver.get("report_id") != report.get("id")
        or ver.get("verified_by") != "auto"
    )
    if stale:
        return _auto_verify(agent_id, report=report, checks=checks)
    return ver


def verify_report(agent_id: str, *, report_id: str = "", force: bool = False) -> dict:
    spec = get_workspace(agent_id)
    if not spec:
        return {"ok": False, "error": f"unknown agent: {agent_id}"}
    report = _latest_report(agent_id)
    if report_id:
        match = next((r for r in _load_reports() if r.get("id") == report_id), None)
        if match:
            report = match
    if not report:
        return {"ok": False, "error": "No session report to verify"}
    checks = _run_auto_checks(agent_id, report)
    if not force and not _all_auto_pass(checks):
        failed = [k for k, v in checks.items() if not v.get("ok")]
        return {
            "ok": False,
            "error": f"Auto checks failed: {', '.join(failed)} — use force=true to override",
            "auto_checks": checks,
        }
    verified = _load_verified()
    verified[agent_id] = {
        "report_id": report.get("id"),
        "verified_at": _now(),
        "verified_by": "force_override",
        "auto_checks": checks,
    }
    _save_verified(verified)
    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event("scoreboard_verified", workspace_id=agent_id, detail=report.get("id", ""))
    except Exception:
        pass
    return {"ok": True, "verified": verified[agent_id]}


def unverify_report(agent_id: str) -> dict:
    verified = _load_verified()
    if agent_id in verified:
        del verified[agent_id]
        _save_verified(verified)
    return {"ok": True, "agent_id": agent_id}


def scoreboard_row(spec: dict) -> dict:
    aid = spec["id"]
    report = _latest_report(aid)
    checks = _run_auto_checks(aid, report)
    ver = (_load_verified().get(aid) or {})
    auto_pass = _all_auto_pass(checks)
    ver = _maybe_backfill_auto_verify(aid, report=report, checks=checks, ver=ver, auto_pass=auto_pass)
    verified = auto_pass or (bool(ver) and ver.get("report_id") == (report or {}).get("id"))
    return {
        "agent_id": aid,
        "label": spec.get("label"),
        "role": spec.get("role"),
        "lane": spec.get("lane"),
        "chat": _chat_pointer(spec),
        "latest_report": report,
        "has_report": bool(report),
        "auto_checks": checks,
        "auto_pass": auto_pass,
        "auto_green": auto_pass,
        "verified": verified,
        "verified_by": ver.get("verified_by") if verified else None,
        "verified_at": ver.get("verified_at") if verified else None,
        "requirements": REQUIREMENTS,
        "hub_tab": f"workspace-{aid}",
    }


def scoreboard_payload() -> dict:
    """Hub + command-data SSOT — exposes ``fleet_auto_green_count`` (sa-0302, sa-0352)."""
    rows = [scoreboard_row(spec) for spec in AGENT_WORKSPACES]
    verified_n = sum(1 for r in rows if r.get("verified"))
    reported_n = sum(1 for r in rows if r.get("has_report"))
    auto_pass_n = sum(1 for r in rows if r.get("auto_pass"))
    auto_green_n = sum(1 for r in rows if r.get("auto_green"))
    missing_verify = [r["agent_id"] for r in rows if r.get("has_report") and not r.get("auto_pass")]
    missing_report = [r["agent_id"] for r in rows if not r.get("has_report")]
    return {
        "ok": True,
        "built_at": _now(),
        "law_doc": LAW_DOC,
        "governance_version": GOVERNANCE_VERSION,
        "agent_count": len(rows),
        "reported_count": reported_n,
        "auto_pass_count": auto_pass_n,
        FLEET_AUTO_GREEN_COUNT_KEY: auto_green_n,
        "verified_count": verified_n,
        "fleet_verify_gap": missing_verify,
        "fleet_report_gap": missing_report,
        "requirements": REQUIREMENTS,
        "rows": rows,
        "reports_path": str(REPORTS_PATH),
        "verified_path": str(VERIFIED_PATH),
        "tagline": SCOREBOARD_TAGLINE,
        "no_asf_eval_authority": True,
        "verify_authority": "auto_pass",
        "mergepack_note": "MergePack is NOT a registered agent — use Live products / Repos.",
    }


def handle_scoreboard_action(body: dict) -> dict:
    action = (body.get("action") or "list").strip().lower()
    agent_id = (body.get("agent_id") or body.get("id") or "").strip()
    if action == "submit_report":
        return submit_report(
            agent_id,
            summary=body.get("summary") or body.get("report") or "",
            chat_pointer=body.get("chat_pointer") or "",
            attestations=body.get("attestations") or {},
            source=body.get("source") or "app",
        )
    if action == "verify":
        return verify_report(agent_id, report_id=body.get("report_id") or "", force=bool(body.get("force")))
    if action == "unverify":
        return unverify_report(agent_id)
    if action == "list" and agent_id:
        spec = get_workspace(agent_id)
        if not spec:
            return {"ok": False, "error": f"unknown agent: {agent_id}"}
        return {"ok": True, "row": scoreboard_row(spec)}
    return scoreboard_payload()
