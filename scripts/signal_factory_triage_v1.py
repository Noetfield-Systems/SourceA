#!/usr/bin/env python3
"""Signal Factory triage — unprocessed gmail_inbox_signals → rubric → Telegram verdict."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "signal-factory" / "triage"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _supabase() -> tuple[str, str]:
    _load_secrets()
    return os.environ.get("SUPABASE_URL", "").strip().rstrip("/"), os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY", ""
    ).strip()


def _fetch_unprocessed(*, limit: int) -> list[dict[str, Any]]:
    url, key = _supabase()
    if not url or not key:
        return []
    q = (
        f"{url}/rest/v1/gmail_inbox_signals"
        f"?select=*&processed=eq.false&order=swept_at.asc&limit={limit}"
    )
    req = urllib.request.Request(
        q,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
    return rows if isinstance(rows, list) else []


def _patch_signal(signal_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    url, key = _supabase()
    req = urllib.request.Request(
        f"{url}/rest/v1/gmail_inbox_signals?id=eq.{signal_id}",
        data=json.dumps(patch).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=representation",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
        return body[0] if isinstance(body, list) and body else {}


def _decision_to_verdict(decision: str, risk: int) -> str:
    if risk >= 4:
        return "ROUTE"
    mapping = {
        "route": "ROUTE",
        "monitor": "MONITOR",
        "archive": "ARCHIVE",
        "defer": "DEFER",
        "build_automation": "PASS",
        "create_service_pattern": "PASS",
    }
    return mapping.get(decision, "PASS")


def run_triage(*, max_batch: int = 10, notify: bool = True) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from signal_factory_core_v1 import analyze_signal, verify_report  # noqa: WPS433
    from telegram_alert_v1 import send_telegram_alert  # noqa: WPS433

    pending = _fetch_unprocessed(limit=max_batch)
    if not pending:
        return {
            "schema": "signal-factory-triage-v1",
            "ok": True,
            "at": _now(),
            "decision": "IDLE_NO_WORK",
            "processed": 0,
            "report_line": "signal_triage · IDLE_NO_WORK",
        }

    results: list[dict[str, Any]] = []
    for row in pending:
        sid = str(row.get("id") or "")
        text = "\n".join(
            x
            for x in (
                str(row.get("subject") or ""),
                str(row.get("from_addr") or ""),
                str(row.get("body_text") or row.get("snippet") or ""),
            )
            if x
        )
        report = analyze_signal(text, entity_scope=None, sender_claims=[])
        verification = verify_report(report)
        scores = (report.get("receipt") or {}).get("scores") or {}
        risk = int(scores.get("risk_score") or 0)
        decision = str(report.get("decision") or "defer")
        verdict = _decision_to_verdict(decision, risk)
        ok = bool(verification.get("ok"))
        if not ok:
            verdict = "FAIL"

        patch = {
            "processed": True,
            "triage_at": _now(),
            "triage_verdict": verdict,
            "signal_factory_decision": decision,
            "signal_factory_classification": report.get("classification"),
            "triage_report": report,
            "updated_at": _now(),
        }
        updated = _patch_signal(sid, patch)
        telegram_sent = False
        if notify:
            subj = str(row.get("subject") or "—")[:80]
            tg = send_telegram_alert(
                f"<b>Signal triage {verdict}</b>\n"
                f"{row.get('mailbox')} · {subj}\n"
                f"class={report.get('classification')} decision={decision} risk={risk}"
            )
            telegram_sent = bool(tg.get("ok"))
            if telegram_sent:
                _patch_signal(sid, {"telegram_notified": True})

        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        receipt_path = RECEIPT_DIR / f"{row.get('gmail_message_id', sid)}.json"
        receipt_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        results.append(
            {
                "id": sid,
                "gmail_message_id": row.get("gmail_message_id"),
                "ok": ok,
                "verdict": verdict,
                "decision": decision,
                "classification": report.get("classification"),
                "telegram_sent": telegram_sent,
            }
        )

    return {
        "schema": "signal-factory-triage-v1",
        "ok": True,
        "at": _now(),
        "decision": "COMPLETE",
        "processed": len(results),
        "results": results,
        "report_line": f"signal_triage · COMPLETE · processed={len(results)}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-batch", type=int, default=10)
    ap.add_argument("--no-telegram", action="store_true")
    args = ap.parse_args()
    row = run_triage(max_batch=args.max_batch, notify=not args.no_telegram)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
