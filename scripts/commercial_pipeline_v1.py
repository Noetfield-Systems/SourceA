#!/usr/bin/env python3
"""Commercial pipeline tracker — state transitions over volume (AB1 + NW1 only).

SSOT: ~/.sina/commercial-pipeline-v1.jsonl (append-only row snapshots)
Glance: ~/.sina/commercial-pipeline-glance-v1.json · worker hub payload

States (ordered funnel):
  researched → personalized_sent → replied → proof_viewed → eval_scheduled → pilot_deposit → close
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PIPELINE = SINA / "commercial-pipeline-v1.jsonl"
GLANCE = SINA / "commercial-pipeline-glance-v1.json"
LANES = frozenset({"AB1", "NW1", "AEG_PROOF", "WBC"})
STATUSES = (
    "researched",
    "personalized_sent",
    "replied",
    "proof_viewed",
    "eval_scheduled",
    "pilot_deposit",
    "close",
    "lost",
)
FUNNEL = STATUSES[:7]
FUNNEL_RANK = {
    "researched": 0,
    "personalized_sent": 1,
    "replied": 2,
    "proof_viewed": 3,
    "eval_scheduled": 4,
    "pilot_deposit": 5,
    "close": 6,
    "lost": -1,
}
TARGETS = {
    "researched": 500,
    "personalized_sent": 100,
    "replied": 30,
    "proof_viewed": 20,
    "eval_scheduled": 10,
    "pilot_deposit": 5,
    "close": 1,
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_id() -> str:
    return f"cp-{uuid.uuid4().hex[:10]}"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _append_row(row: dict[str, Any]) -> None:
    PIPELINE.parent.mkdir(parents=True, exist_ok=True)
    with PIPELINE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def load_rows() -> dict[str, dict[str, Any]]:
    """Latest snapshot per row id."""
    if not PIPELINE.is_file():
        return {}
    latest: dict[str, dict[str, Any]] = {}
    for line in PIPELINE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = str(row.get("id") or "")
        if rid:
            latest[rid] = row
    return latest


def add_row(
    *,
    company: str,
    lane: str,
    status: str = "researched",
    contact: str = "",
    icp_score: int = 0,
    proof_url: str = "",
    last_agent: str = "commercial_pipeline_v1",
    next_action: str = "",
    founder_pick: bool = False,
    notes: str = "",
    row_id: str | None = None,
) -> dict[str, Any]:
    lane_u = lane.upper().replace("ASSET_B", "AB1")
    if lane_u not in LANES:
        if lane_u.startswith("NW"):
            lane_u = "NW1"
        elif lane_u in ("WITNESSBC", "WITNESS_BC"):
            lane_u = "WBC"
        else:
            raise ValueError(f"lane must be one of {sorted(LANES)} (got {lane})")
    if status not in STATUSES:
        raise ValueError(f"invalid status {status}")
    ts = _now()
    row = {
        "schema": "commercial-pipeline-row-v1",
        "id": row_id or _row_id(),
        "company": company.strip(),
        "contact": contact.strip(),
        "lane": lane_u,
        "icp_score": max(0, min(100, int(icp_score))),
        "status": status,
        "proof_url": proof_url.strip(),
        "last_agent": last_agent,
        "next_action": next_action.strip(),
        "founder_pick": bool(founder_pick),
        "notes": notes.strip(),
        "at": ts,
        "updated_at": ts,
    }
    _append_row(row)
    return row


def _sync_transition(
    row_id: str,
    *,
    status: str,
    proof_url: str | None = None,
    next_action: str | None = None,
    last_agent: str = "sync_from_receipts",
    notes: str | None = None,
) -> dict[str, Any]:
    """Never downgrade funnel status or next_action during receipt sync."""
    rows = load_rows()
    base = rows.get(row_id) or {}
    cur = str(base.get("status") or "researched")
    target = status
    action = next_action
    if status in FUNNEL_RANK and cur in FUNNEL_RANK:
        if FUNNEL_RANK[status] < FUNNEL_RANK[cur] and status != "lost":
            target = cur
            action = None
    return transition(
        row_id,
        status=target,
        proof_url=proof_url,
        next_action=action,
        last_agent=last_agent,
        notes=notes,
    )


def transition(
    row_id: str,
    *,
    status: str,
    proof_url: str | None = None,
    next_action: str | None = None,
    last_agent: str = "commercial_pipeline_v1",
    notes: str | None = None,
) -> dict[str, Any]:
    rows = load_rows()
    base = rows.get(row_id)
    if not base:
        raise ValueError(f"unknown row id {row_id}")
    if status not in STATUSES:
        raise ValueError(f"invalid status {status}")
    row = dict(base)
    row["status"] = status
    row["updated_at"] = _now()
    row["last_agent"] = last_agent
    if proof_url is not None:
        row["proof_url"] = proof_url
    if next_action is not None:
        row["next_action"] = next_action
    if notes is not None:
        row["notes"] = notes
    _append_row(row)
    return row


def funnel_counts(rows: dict[str, dict[str, Any]] | None = None) -> dict[str, int]:
    data = rows if rows is not None else load_rows()
    counts = {s: 0 for s in FUNNEL}
    counts["lost"] = 0
    for row in data.values():
        st = str(row.get("status") or "researched")
        if st in counts:
            counts[st] += 1
    return counts


def _active_rows(rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    active_statuses = {"personalized_sent", "replied", "proof_viewed", "eval_scheduled", "pilot_deposit"}
    out = [r for r in rows.values() if r.get("status") in active_statuses]
    out.sort(key=lambda r: str(r.get("updated_at") or ""), reverse=True)
    return out[:8]


def _headline(counts: dict[str, int]) -> str:
    active = sum(counts.get(s, 0) for s in ("replied", "proof_viewed", "eval_scheduled", "pilot_deposit"))
    sent = counts.get("personalized_sent", 0)
    close = counts.get("close", 0)
    return f"{sent} sent · {active} active · {close} close — optimize pipeline state"


def _next_agent_for_row(row: dict[str, Any]) -> str:
    try:
        from commercial_agents_wire_v1 import next_agent_for_row  # noqa: WPS433

        return next_agent_for_row(row)
    except Exception:
        status = str(row.get("status") or "")
        if status == "personalized_sent":
            return "reply_qualification_agent"
        if status == "replied":
            return "reply_followup_sent"
        if status == "proof_viewed":
            return "eval_booking_agent"
        return ""


def pipeline_glance_payload(*, refresh: bool = True) -> dict[str, Any]:
    rows = load_rows()
    counts = funnel_counts(rows)
    active = _active_rows(rows)
    payload = {
        "schema": "commercial-pipeline-glance-v1",
        "at": _now(),
        "lanes": ["AB1", "NW1", "WBC"],
        "counts": counts,
        "targets": TARGETS,
        "active_conversations": sum(
            counts.get(s, 0) for s in ("replied", "proof_viewed", "eval_scheduled", "pilot_deposit")
        ),
        "headline": _headline(counts),
        "founder_line": f"Pipeline · {counts.get('personalized_sent', 0)} personalized · {counts.get('eval_scheduled', 0)} eval · {counts.get('pilot_deposit', 0)} pilot",
        "top_next": [
            {
                "id": r.get("id"),
                "company": r.get("company"),
                "lane": r.get("lane"),
                "status": r.get("status"),
                "next_action": r.get("next_action"),
                "proof_url": r.get("proof_url"),
                "next_agent": _next_agent_for_row(r),
            }
            for r in active[:5]
        ],
        "rows_total": len(rows),
    }
    if refresh:
        _write_json(GLANCE, payload)
    return payload


def sync_from_receipts() -> list[dict[str, Any]]:
    """Seed/update rows from outbound + AEG receipts on disk."""
    rows = load_rows()
    by_company: dict[str, str] = {str(r.get("company")): rid for rid, r in rows.items()}
    synced: list[dict[str, Any]] = []

    ab1 = _read_json(SINA / "ab1-outbound-send-receipt-v1.json")
    if ab1.get("schema") == "ab1-outbound-send-receipt-v1":
        company = "AB1 prospect (draft)"
        ab1_status = str(ab1.get("ab1_status") or "")
        if ab1_status == "sent":
            status = "personalized_sent"
            next_action = "Await inbound reply · agent watches Mail"
        elif ab1_status == "awaiting_founder_send_click":
            status = "personalized_sent"
            next_action = "Founder send click · AB1 mail draft"
        else:
            status = "researched"
            next_action = "Draft AB1 outbound"
        if company not in by_company:
            row = add_row(
                company=company,
                lane="AB1",
                status=status,
                icp_score=72,
                next_action=next_action,
                last_agent="sync_from_receipts",
                notes=f"subject: {ab1.get('subject', '')[:80]}",
            )
        else:
            row = _sync_transition(
                by_company[company],
                status=status,
                next_action=next_action,
                last_agent="sync_from_receipts",
            )
        synced.append(row)

    aeg = _read_json(SINA / "aeg-outbound-send-receipt-v1.json")
    host = _read_json(SINA / "aeg-host-receipt-v1.json")
    proof_url = str(aeg.get("proof_url") or host.get("proof_url") or "")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from commercial_recipient_guard_v1 import resolve_aeg_proof_url  # noqa: WPS433

        site_aeg = resolve_aeg_proof_url()
        if site_aeg.startswith("http"):
            proof_url = site_aeg
    except (ImportError, SystemExit, OSError):
        pass
    eval_book_pre = _read_json(SINA / "eval-booking-receipt-v1.json")
    eval_row_id = str(eval_book_pre.get("row_id") or "")
    if aeg.get("schema") == "aeg-outbound-send-receipt-v1":
        company = "AEG proof prospect (draft)"
        status = "proof_viewed" if proof_url.startswith("http") else "personalized_sent"
        next_action = "Send proof URL in outbound · book 15 min eval"
        if eval_row_id and eval_book_pre.get("schema") == "eval-booking-receipt-v1":
            if eval_book_pre.get("eval_status") == "sent":
                status = "eval_scheduled"
                next_action = "Await prospect slot · prep BLOCK live screen-share"
            else:
                next_action = "Founder send eval invite · Mail draft in outbound pack"
        if company not in by_company:
            row = add_row(
                company=company,
                lane="AB1",
                status=status,
                icp_score=85,
                proof_url=proof_url,
                next_action=next_action,
                last_agent="sync_from_receipts",
                founder_pick=True,
            )
        else:
            row = _sync_transition(
                by_company[company],
                status=status,
                proof_url=proof_url,
                next_action=next_action,
                last_agent="sync_from_receipts",
            )
        synced.append(row)

    nw1_pack = SINA / "outbound" / "nw1-send-001"
    nw1_receipt = _read_json(SINA / "nw1-outbound-send-receipt-v1.json")
    if nw1_pack.is_dir():
        company = "NW1 design partner (draft)"
        nw1_status = str(nw1_receipt.get("nw1_status") or "")
        if nw1_status == "sent":
            status = "personalized_sent"
            next_action = "Await inbound reply · agent watches Mail"
        else:
            status = "personalized_sent"
            next_action = "Attach merged one-pager + battle card · founder send"
        if company not in by_company:
            row = add_row(
                company=company,
                lane="NW1",
                status=status,
                icp_score=78,
                next_action=next_action,
                last_agent="sync_from_receipts",
            )
        else:
            row = _sync_transition(
                by_company[company],
                status=status,
                next_action=next_action,
                last_agent="sync_from_receipts",
            )
        synced.append(row)

    eval_book = _read_json(SINA / "eval-booking-receipt-v1.json")
    if eval_book.get("schema") == "eval-booking-receipt-v1":
        entries = list(eval_book.get("results") or [])
        if not entries and eval_book.get("row_id"):
            entries = [{"row_id": eval_book.get("row_id"), "eval_status": eval_book.get("eval_status")}]
        for entry in entries:
            row_id = str(entry.get("row_id") or "")
            if not row_id:
                continue
            rows_now = load_rows()
            base = rows_now.get(row_id)
            if not base:
                continue
            eval_status = str(entry.get("eval_status") or eval_book.get("eval_status") or "")
            proof_url = str(entry.get("proof_url") or eval_book.get("proof_url") or base.get("proof_url") or "")
            if eval_status == "sent":
                row = transition(
                    row_id,
                    status="eval_scheduled",
                    proof_url=proof_url,
                    next_action="Await prospect slot · prep BLOCK live screen-share",
                    last_agent="sync_from_receipts",
                    notes="booked_by: agentic",
                )
            else:
                row = transition(
                    row_id,
                    status=str(base.get("status") or "proof_viewed"),
                    proof_url=proof_url,
                    next_action="Founder send eval invite · Mail draft in outbound pack",
                    last_agent="sync_from_receipts",
                    notes=f"eval pack: {entry.get('pack_dir') or eval_book.get('pack_dir', '')}",
                )
            synced.append(row)

    reply_qual = _read_json(SINA / "reply-qualification-receipt-v1.json")
    if reply_qual.get("schema") == "reply-qualification-receipt-v1":
        for entry in reply_qual.get("results") or []:
            row_id = str(entry.get("row_id") or "")
            if not row_id:
                continue
            rows_now = load_rows()
            base = rows_now.get(row_id)
            if not base:
                continue
            phase = str(entry.get("phase") or "")
            followup_sent = str(entry.get("followup_status") or "") == "sent" or (
                str(reply_qual.get("followup_status") or "") == "sent"
                and str(reply_qual.get("row_id") or "") == row_id
            )
            proof_url = str(entry.get("proof_url") or reply_qual.get("proof_url") or base.get("proof_url") or "")
            if followup_sent and str(reply_qual.get("row_id")) == row_id:
                row = transition(
                    row_id,
                    status="proof_viewed",
                    proof_url=proof_url,
                    next_action="Book 15 min eval · eval booking agent",
                    last_agent="sync_from_receipts",
                    notes="qualified_by: agentic",
                )
            elif phase == "replied":
                row = transition(
                    row_id,
                    status="replied",
                    proof_url=proof_url,
                    next_action="Founder send proof follow-up · Mail draft in outbound pack",
                    last_agent="sync_from_receipts",
                    notes=f"reply pack: {entry.get('pack_dir', '')}",
                )
            elif phase == "lost":
                row = transition(
                    row_id,
                    status="lost",
                    next_action="Disqualified · no follow-up",
                    last_agent="sync_from_receipts",
                )
            elif phase == "watch":
                row = transition(
                    row_id,
                    status="personalized_sent",
                    proof_url=proof_url,
                    next_action="Await inbound reply · agent watches Mail",
                    last_agent="sync_from_receipts",
                    notes="reply_watch",
                )
            else:
                continue
            synced.append(row)

    return synced


def main() -> int:
    ap = argparse.ArgumentParser(description="Commercial pipeline tracker (AB1 + NW1)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--glance", action="store_true", help="Print glance payload + write cache")
    ap.add_argument("--sync", action="store_true", help="Sync rows from outbound receipts")
    ap.add_argument("--list", action="store_true", help="List latest rows")
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--company", default="")
    ap.add_argument("--lane", default="AB1")
    ap.add_argument("--status", default="researched")
    ap.add_argument("--icp-score", type=int, default=0)
    ap.add_argument("--proof-url", default="")
    ap.add_argument("--next-action", default="")
    ap.add_argument("--transition", metavar="ROW_ID")
    ap.add_argument("--to-status", default="")
    args = ap.parse_args()

    if args.sync:
        synced = sync_from_receipts()
        glance = pipeline_glance_payload()
        out = {"ok": True, "synced": len(synced), "rows": synced, "glance": glance}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"OK: synced {len(synced)} rows · {glance.get('headline')}")
        return 0

    if args.add:
        if not args.company:
            print("FAIL: --company required", file=sys.stderr)
            return 1
        row = add_row(
            company=args.company,
            lane=args.lane,
            status=args.status,
            icp_score=args.icp_score,
            proof_url=args.proof_url,
            next_action=args.next_action,
        )
        pipeline_glance_payload()
        print(json.dumps(row, indent=2) if args.json else f"OK: added {row['id']} · {row['company']} · {row['status']}")
        return 0

    if args.transition:
        if not args.to_status:
            print("FAIL: --to-status required", file=sys.stderr)
            return 1
        row = transition(
            args.transition,
            status=args.to_status,
            proof_url=args.proof_url or None,
            next_action=args.next_action or None,
        )
        pipeline_glance_payload()
        print(json.dumps(row, indent=2) if args.json else f"OK: {row['id']} → {row['status']}")
        return 0

    if args.list:
        rows = list(load_rows().values())
        rows.sort(key=lambda r: str(r.get("updated_at") or ""), reverse=True)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for r in rows:
                print(f"{r.get('id')}\t{r.get('lane')}\t{r.get('status')}\t{r.get('company')}")
        return 0

    glance = pipeline_glance_payload()
    if args.glance or args.json:
        print(json.dumps(glance, indent=2))
    else:
        print(glance.get("headline"))
        for k in FUNNEL:
            print(f"  {k}: {glance['counts'].get(k, 0)}/{TARGETS.get(k, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
