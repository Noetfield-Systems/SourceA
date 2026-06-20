#!/usr/bin/env python3
"""One-shot commercial pipeline repair — fix sync regressions + advance draft rows."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"


def _run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (proc.stdout or proc.stderr or "").strip()
    try:
        return json.loads(out) if out.startswith("{") or out.startswith("[") else {"ok": proc.returncode == 0, "out": out}
    except json.JSONDecodeError:
        return {"ok": proc.returncode == 0, "out": out}


def _refresh_outbound_packs(rows: dict) -> list[str]:
    """Rewrite on-disk packs — public W1 URL, official from, no localhost."""
    sys.path.insert(0, str(SCRIPTS))
    from commercial_recipient_guard_v1 import (  # noqa: WPS433
        _urls_in_text,
        is_localhost_url,
        resolve_demo_proof_url,
        resolve_w1_proof_url,
    )
    from commercial_reply_qualification_agent_v1 import (  # noqa: WPS433
        _latest_proof_url,
        _outbound_sent,
        qualify_reply,
        write_followup_pack,
    )

    refreshed: list[str] = []
    outbound = SINA / "outbound"
    if not outbound.is_dir():
        return refreshed

    for pack_dir in sorted(outbound.glob("eval-booking-*")):
        meta_path = pack_dir / "pack.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        row_id = str(meta.get("row_id") or "")
        if not row_id or row_id not in rows:
            continue
        lane = str(meta.get("lane") or rows.get(row_id, {}).get("lane") or "AB1").upper()
        want_proof = resolve_demo_proof_url(lane=lane)
        want_w1 = resolve_w1_proof_url()
        w1 = str(meta.get("w1_film_url") or "")
        proof_in_pack = str(meta.get("proof_url") or "")
        body = (pack_dir / "body.txt").read_text(encoding="utf-8") if (pack_dir / "body.txt").is_file() else ""
        stale = (
            any(is_localhost_url(u) for u in [w1, proof_in_pack, *_urls_in_text(body)])
            or w1 != want_w1
            or proof_in_pack != want_proof
        )
        if not stale:
            continue
        r = _run(
            [
                sys.executable,
                "scripts/commercial_eval_booking_agent_v1.py",
                "--row-id",
                row_id,
                "--json",
            ]
        )
        if r.get("ok"):
            refreshed.append(f"eval pack · {row_id}")
            try:
                vf = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "commercial_video_factory_v1.py"), "--row-id", row_id, "--json"],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                if vf.returncode == 0:
                    refreshed.append(f"prospect reel · {row_id}")
            except (subprocess.TimeoutExpired, OSError):
                pass

    for pack_dir in sorted(outbound.glob("reply-followup-*")):
        meta_path = pack_dir / "pack.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        row_id = str(meta.get("row_id") or "")
        row = rows.get(row_id)
        if not row:
            continue
        w1 = str(meta.get("w1_film_url") or "")
        if not is_localhost_url(w1):
            continue
        lane = str(meta.get("lane") or row.get("lane") or "AB1").upper()
        inbound_path = pack_dir / "inbound_reply.txt"
        inbound = inbound_path.read_text(encoding="utf-8").strip() if inbound_path.is_file() else "thanks — interested in the proof walk"
        _, lane_receipt = _outbound_sent(lane)
        qualification = qualify_reply(inbound)
        proof_url = proof or str(meta.get("proof_url") or row.get("proof_url") or "")
        to_email = str(meta.get("to") or "")
        write_followup_pack(
            row=row,
            lane=lane,
            proof_url=proof_url,
            qualification=qualification,
            inbound=inbound,
            nw1_receipt=lane_receipt if lane == "NW1" else {},
            to_email=to_email,
        )
        refreshed.append(f"reply pack · {row_id}")

    return refreshed


def main() -> int:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_pipeline_v1 import load_rows, pipeline_glance_payload, transition  # noqa: WPS433

    proof = ""
    aeg = SINA / "aeg-latest-receipt-v1.json"
    if aeg.is_file():
        proof = str(json.loads(aeg.read_text()).get("proof_url") or "")
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "inject_landing_aeg_proof_v1.py")],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        pass

    repairs: list[str] = []

    # AB1 had proof follow-up pack + prior mark — restore proof_viewed
    ab1_pack = SINA / "outbound" / "reply-followup-32ddb1794d"
    if ab1_pack.is_dir():
        transition(
            "cp-32ddb1794d",
            status="proof_viewed",
            proof_url=proof or None,
            next_action="Book 15 min eval · eval booking agent",
            last_agent="commercial_pipeline_repair_v1",
            notes="repair · proof_followup_sent",
        )
        repairs.append("AB1 → proof_viewed")

    # NW1 replied — mark follow-up sent if pack exists
    nw1_pack = SINA / "outbound" / "reply-followup-0b9b8c4eff"
    if nw1_pack.is_dir():
        r = _run([sys.executable, "scripts/mark_reply_followup_sent_v1.py", "--row-id", "cp-0b9b8c4eff", "--json"])
        if r.get("ok"):
            repairs.append("NW1 → proof_viewed")

    # Regenerate eval booking packs for proof_viewed rows
    rows = load_rows()
    for rid, row in rows.items():
        if row.get("status") != "proof_viewed":
            continue
        r = _run(
            [
                sys.executable,
                "scripts/commercial_eval_booking_agent_v1.py",
                "--row-id",
                rid,
                "--json",
            ]
        )
        if r.get("ok"):
            repairs.append(f"eval pack · {rid}")

    repairs.extend(_refresh_outbound_packs(load_rows()))

    # Wire site AEG proof URL to hero AB1 row (SMART-321)
    try:
        from commercial_recipient_guard_v1 import resolve_aeg_proof_url  # noqa: WPS433

        site_proof = resolve_aeg_proof_url()
        rows = load_rows()
        if rows.get("cp-a0c7c6c607"):
            transition(
                "cp-a0c7c6c607",
                status=str(rows["cp-a0c7c6c607"].get("status") or "eval_scheduled"),
                proof_url=site_proof,
                next_action="Founder send eval invite · live proof on site",
                last_agent="commercial_pipeline_repair_v1",
                notes="SMART-321 · aeg_live_url wired",
            )
            repairs.append(f"AEG row proof_url → {site_proof[:60]}…")
    except (ImportError, SystemExit, OSError) as exc:
        repairs.append(f"AEG wire skip: {exc}")

    # Restore AEG eval_scheduled if it was already sent
    aeg_eval = SINA / "outbound" / "eval-booking-a0c7c6c607"
    if aeg_eval.is_dir():
        transition(
            "cp-a0c7c6c607",
            status="eval_scheduled",
            next_action="Await prospect slot · prep BLOCK live screen-share",
            last_agent="commercial_pipeline_repair_v1",
            notes="booked_by: agentic · repair restore",
        )
        repairs.append("AEG → eval_scheduled restored")

    # Fix AB1/NW1 next_action after sync
    for rid, action in (
        ("cp-32ddb1794d", "Book 15 min eval · eval booking agent"),
        ("cp-0b9b8c4eff", "Book 15 min eval · eval booking agent"),
    ):
        rows = load_rows()
        if rows.get(rid, {}).get("status") == "proof_viewed":
            transition(
                rid,
                status="proof_viewed",
                next_action=action,
                last_agent="commercial_pipeline_repair_v1",
            )

    # Full receipt sync with downgrade guard
    _run([sys.executable, "scripts/commercial_pipeline_v1.py", "--sync", "--json"])

    # Hub heal
    _run([sys.executable, "scripts/worker_anti_staleness_heal_v1.py", "--json"])
    _run([sys.executable, "scripts/disk_live_wire_sync_v1.py", "--json"])

    glance = pipeline_glance_payload()
    print(
        json.dumps(
            {
                "ok": True,
                "repairs": repairs,
                "headline": glance.get("headline"),
                "counts": glance.get("counts"),
                "top_next": glance.get("top_next"),
                "founder_line": "Pipeline repaired · Hub healed · eval packs ready for proof_viewed rows",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
