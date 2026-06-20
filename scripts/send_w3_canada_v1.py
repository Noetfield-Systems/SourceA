#!/usr/bin/env python3
"""W3 Canada send — Ocree (TrustField) + Fundmore (Noetfield) from LOCKED pack.

Law: CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md · w3-canada-send-approvals-v1.json
Opens Mail.app drafts (official FROM only). Marks sent on --confirm-sent after founder clicks Send.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
EMAILS_JSON = ROOT / "data" / "commercial" / "canada-priority-a-emails-v1.json"
APPROVALS_JSON = ROOT / "data" / "commercial" / "w3-canada-send-approvals-v1.json"
RECEIPT = SINA / "w3-canada-outbound-send-receipt-v1.json"
FOUNDER = os.environ.get("SOURCEA_FOUNDER_NAME", "Sina Kazemnezhad").strip() or "Sina Kazemnezhad"

# Public contacts verified on ocreefg.com / crunchbase / newswire (2026-06-18)
DEFAULT_CONTACTS: dict[str, dict] = {
    "ocree": {
        "to": "aramsay@ocreefg.com",
        "first_name": "Anne",
        "champion": "Chief Compliance Officer",
        "relationship_basis": (
            "CASL: industry context — CSA Project Tokenization workshop (June 11, 2026, Toronto)."
        ),
        "lane": "TF",
        "from_email": "hello@trustfield.ca",
        "from_name": "TrustField Technologies",
        "calendar": "https://trustfield.ca",
        "attach": None,
    },
    "fundmore": {
        "to": "chris@fundmore.ai",
        "first_name": "Chris",
        "champion": "CEO",
        "relationship_basis": (
            "CASL: public company profile and press — fundmore.ai."
        ),
        "lane": "NF",
        "from_email": "operation@noetfield.com",
        "from_name": "Noetfield",
        "calendar": "https://www.noetfield.com/copilot/pilot/",
        "attach": ROOT / "NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_MERGED_EXTERNAL_v1.md",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _account_row(data: dict, account_id: str) -> dict | None:
    for row in data.get("accounts") or []:
        if str(row.get("id") or "") == account_id:
            return row
    return None


def _personalize_body(template: str, *, first_name: str, basis: str, calendar: str, founder: str, lane: str) -> str:
    body = template
    body = body.replace("[First name]", first_name)
    body = re.sub(
        r"\[True relationship basis[^\]]*\]",
        basis,
        body,
        flags=re.I,
    )
    body = body.replace("[calendar link]", calendar)
    body = body.replace("[Full name]", founder)
    body = body.replace("[Phone]", "")
    body = body.replace("[Canadian address for CASL]", "Canada")
    body = re.sub(r" · \[Phone\]", "", body)
    body = re.sub(r" · \[Canadian address for CASL\]", "", body)
    if lane == "TF":
        body = body.replace("hello@trustfield.ca ·  · Canada", "hello@trustfield.ca · Canada")
    else:
        body = body.replace("hello@noetfield.com ·  · Canada", "operation@noetfield.com · Canada")
        body = body.replace("hello@noetfield.com", "operation@noetfield.com")
    return body.strip() + "\n"


def _out_dir(account_id: str) -> Path:
    return SINA / "outbound" / f"w3-canada-{account_id}"


def prepare_send(account_id: str, *, to_email: str = "", first_name: str = "") -> dict:
    data = _read_json(EMAILS_JSON)
    row = _account_row(data, account_id)
    if not row:
        raise SystemExit(f"FAIL: unknown account {account_id} in {EMAILS_JSON}")
    defaults = DEFAULT_CONTACTS.get(account_id, {})
    to = (to_email or defaults.get("to") or "").strip()
    if not to or "@" not in to:
        raise SystemExit(f"FAIL: --to required for {account_id}")
    fname = (first_name or defaults.get("first_name") or "").strip()
    subject = str(row.get("subject") or "")
    template = str(row.get("body_full") or row.get("body") or "")
    lane = str(row.get("lane") or defaults.get("lane") or "")
    body = _personalize_body(
        template,
        first_name=fname,
        basis=str(defaults.get("relationship_basis") or ""),
        calendar=str(defaults.get("calendar") or ""),
        founder=FOUNDER,
        lane="TF" if "TrustField" in lane else "NF",
    )
    out = _out_dir(account_id)
    out.mkdir(parents=True, exist_ok=True)
    (out / "subject.txt").write_text(subject + "\n", encoding="utf-8")
    (out / "body.txt").write_text(body, encoding="utf-8")
    (out / "to.txt").write_text(to + "\n", encoding="utf-8")
    attach = defaults.get("attach")
    attach_path = str(attach) if attach and Path(attach).is_file() else None
    meta = {
        "schema": "w3-canada-outbound-send-pack-v1",
        "account_id": account_id,
        "company": row.get("company"),
        "lane": row.get("lane"),
        "sku": row.get("sku"),
        "subject": subject,
        "to": to,
        "first_name": fname,
        "champion": defaults.get("champion"),
        "from_email": defaults.get("from_email"),
        "from_name": defaults.get("from_name"),
        "attach": attach_path,
        "relationship_basis": defaults.get("relationship_basis"),
        "prepared_at": _now(),
        "status": "prepared",
    }
    oqg = _apply_oqg_gate(meta, body=body, lane=str(row.get("lane") or ""), attach=attach_path)
    meta.update(oqg)
    (out / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def _require_sina_read(meta: dict) -> None:
    sina = meta.get("sina_read_score_pct")
    if sina is None:
        sina = meta.get("founder_score_pct")
    if sina is None or int(sina) < 90:
        raise SystemExit(
            f"BLOCK {meta.get('account_id')}: Sina read ≥90 required before Mail draft "
            f"(status={meta.get('status')}) · law: scripts/validate_ship_authority_v1.py"
        )


def _apply_oqg_gate(meta: dict, *, body: str, lane: str, attach: str | None) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from best_loop_oqg_score_v1 import assert_oqg_pass  # noqa: WPS433
    from w3_founder_review_v1 import _effective_pack_status  # noqa: WPS433

    attach_path = Path(attach) if attach else None
    scored = assert_oqg_pass(
        account_id=str(meta["account_id"]),
        body=body,
        lane=lane,
        attach=attach_path,
        subject=str(meta.get("subject") or ""),
        relationship_basis=str(meta.get("relationship_basis") or ""),
    )
    merged = {**meta, **{
        "output_clean_pct": scored.get("output_clean_pct"),
        "oqg_pass": scored.get("oqg_pass_effective"),
        "oqg_at": scored.get("oqg_at"),
        "waiver_id": scored.get("waiver_id"),
        "oqg_checks": scored.get("checks"),
        "machine_verdict": "PASS" if scored.get("oqg_pass_effective") else "FAIL",
    }}
    return {
        "output_clean_pct": merged.get("output_clean_pct"),
        "oqg_pass": merged.get("oqg_pass"),
        "oqg_at": merged.get("oqg_at"),
        "waiver_id": merged.get("waiver_id"),
        "oqg_checks": merged.get("oqg_checks"),
        "machine_verdict": merged.get("machine_verdict"),
        "status": _effective_pack_status(merged),
        "ship_authority_note": "RRL D/E + OQG PASS are not ship authority — Sina read ≥90 required",
    }


def open_draft(meta: dict) -> None:
    _require_sina_read(meta)
    sys.path.insert(0, str(ROOT / "scripts"))
    from commercial_mail_draft_v1 import open_commercial_mail_draft  # noqa: WPS433

    aid = str(meta.get("account_id") or "")
    body_path = _out_dir(aid) / "body.txt"
    body = body_path.read_text(encoding="utf-8") if body_path.is_file() else ""
    attach = meta.get("attach")
    oqg = _apply_oqg_gate(
        meta,
        body=body,
        lane=str(meta.get("lane") or ""),
        attach=str(attach) if attach else None,
    )
    meta.update(oqg)
    (_out_dir(aid) / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    attach_paths: list[Path] = []
    if meta.get("attach"):
        p = Path(meta["attach"])
        if p.is_file():
            attach_paths.append(p)
    lane = "TF" if "TrustField" in str(meta.get("lane") or "") else "NF"
    body = (_out_dir(str(meta["account_id"])) / "body.txt").read_text(encoding="utf-8")
    open_commercial_mail_draft(
        subject=str(meta["subject"]),
        body=body,
        to_email=str(meta["to"]),
        from_email=str(meta["from_email"]),
        from_name=str(meta["from_name"]),
        lane=lane,
        attachments=attach_paths,
        context=f"W3 Canada {meta.get('account_id')}",
    )


def mark_sent(account_ids: list[str], *, mode: str = "founder_confirmed_send") -> dict:
    saved = _now()
    emails = _read_json(EMAILS_JSON)
    approvals = _read_json(APPROVALS_JSON)
    sent_rows: list[dict] = []

    for aid in account_ids:
        pack_path = _out_dir(aid) / "pack.json"
        meta: dict = {}
        if pack_path.is_file():
            meta = json.loads(pack_path.read_text(encoding="utf-8"))
            body_path = _out_dir(aid) / "body.txt"
            body = body_path.read_text(encoding="utf-8") if body_path.is_file() else ""
            attach = meta.get("attach")
            oqg = _apply_oqg_gate(
                meta,
                body=body,
                lane=str(meta.get("lane") or ""),
                attach=str(attach) if attach else None,
            )
            meta.update(oqg)
            meta["status"] = "sent"
            meta["sent_at"] = saved
            pack_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        for acct in emails.get("accounts") or []:
            if acct.get("id") == aid:
                acct["sent_at"] = saved
                acct["send_mode"] = mode
                acct["hub_send_status"] = "sent"
        for acct in approvals.get("accounts") or []:
            if acct.get("id") == aid:
                acct["sent_at"] = saved
                acct["send_mode"] = mode
                acct["hub_send_status"] = "sent"
        sent_rows.append(
            {
                "id": aid,
                "sent_at": saved,
                "mode": mode,
                "output_clean_pct": meta.get("output_clean_pct"),
                "oqg_at": meta.get("oqg_at"),
                "waiver_id": meta.get("waiver_id"),
            }
        )

    emails["saved_at"] = saved
    approvals["saved_at"] = saved
    approvals["send_policy"] = "sent — await replies · Better Loop W3 check clears"
    EMAILS_JSON.write_text(json.dumps(emails, indent=2) + "\n", encoding="utf-8")
    APPROVALS_JSON.write_text(json.dumps(approvals, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "w3-canada-outbound-send-receipt-v1",
        "saved_at": saved,
        "accounts": sent_rows,
        "oqg_gate": "BQ2 assert_oqg_pass",
        "law": "CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md",
        "approvals": str(APPROVALS_JSON),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        append_event(
            event_type="COMMERCIAL_SEND",
            object_id="w3-canada-ocree-fundmore",
            object_kind="commercial",
            agent_id="cursor",
            payload={"accounts": sent_rows, "lane": "W3"},
            gate="w3-canada-send",
            proof=str(RECEIPT),
            status="committed",
        )
    except Exception:
        pass

    return receipt


def run_send(account_ids: list[str], *, confirm_sent: bool = False, pack_only: bool = False, to_overrides: dict[str, str] | None = None) -> dict:
    if not pack_only:
        sys.path.insert(0, str(ROOT / "scripts"))
        from commercial_email_send_defer_v1 import assert_send_allowed  # noqa: WPS433

        assert_send_allowed(action="confirm-sent" if confirm_sent else "draft")
    to_overrides = to_overrides or {}
    opened: list[dict] = []
    for aid in account_ids:
        meta = prepare_send(aid, to_email=to_overrides.get(aid, ""))
        if pack_only:
            meta["status"] = "pack_ready"
            (_out_dir(aid) / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            opened.append(meta)
            continue
        try:
            _require_sina_read(meta)
            open_draft(meta)
            meta["status"] = "draft_opened"
            (_out_dir(aid) / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            opened.append(meta)
        except SystemExit as exc:
            meta["status"] = "draft_failed"
            meta["error"] = str(exc)
            (_out_dir(aid) / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            opened.append(meta)

    receipt: dict = {"opened": opened, "confirm_sent": confirm_sent}
    if confirm_sent:
        receipt["mark"] = mark_sent(account_ids)
    else:
        receipt["next"] = (
            "Review Mail drafts → click Send for each → "
            f"python3 scripts/send_w3_canada_v1.py --confirm-sent {' '.join(account_ids)}"
        )
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="W3 Canada send — Ocree + Fundmore")
    ap.add_argument(
        "accounts",
        nargs="*",
        default=["ocree", "fundmore"],
        help="Account ids (default: ocree fundmore)",
    )
    ap.add_argument("--confirm-sent", action="store_true", help="Mark sent after founder clicked Send in Mail")
    ap.add_argument("--pack-only", action="store_true", help="Write outbound packs only — skip Mail.app draft")
    ap.add_argument("--to", dest="to_map", action="append", default=[], help="Override: ocree=email@…")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    overrides: dict[str, str] = {}
    for item in args.to_map:
        if "=" in item:
            k, v = item.split("=", 1)
            overrides[k.strip()] = v.strip()

    row = run_send(
        list(args.accounts),
        confirm_sent=args.confirm_sent,
        pack_only=args.pack_only,
        to_overrides=overrides,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        for m in row.get("opened") or []:
            print(f"OK: {m.get('account_id')} → {m.get('to')} · pack {_out_dir(str(m.get('account_id')))}")
        if args.confirm_sent:
            print(f"Marked sent · receipt {RECEIPT}")
        else:
            print(row.get("next", ""))
    failed = any(m.get("status") == "draft_failed" for m in row.get("opened") or [])
    if failed and not args.pack_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
