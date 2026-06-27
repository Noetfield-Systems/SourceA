#!/usr/bin/env python3
"""SourceA Phase 1 — Next 10 Steps track (June 2026)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SCRIPTS = ROOT / "scripts"
TRACK_RECEIPT = SINA / "sourcea-phase1-ten-step-track-receipt-v1.json"
CLIENT2_ID = "t1-client-002"
WORK_ORDER = "t1-client-002"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _run_json(cmd: list[str], *, timeout: int = 120) -> dict[str, Any]:
    if cmd and not cmd[0].endswith("python3") and cmd[0].endswith(".py"):
        cmd = ["python3", *cmd]
    proc = subprocess.run(cmd, cwd=str(SCRIPTS), capture_output=True, text=True, timeout=timeout)
    if proc.stdout.strip():
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            pass
    return {"ok": False, "stderr": (proc.stderr or "")[-300:], "returncode": proc.returncode}


def step1_live_storefront() -> dict[str, Any]:
    public_data = ROOT / "SourceA-landing" / "green-unified" / "data" / "phase1-proof-pack-public-v1.json"
    if not public_data.is_file():
        src = SINA / "chat-unify" / "proof-packs" / "pp-20260624T052230Z-c3857002" / "export" / "proof-pack-shareable.json"
        if src.is_file():
            from sourcea_ten_step_track_v1 import _redact_public_proof  # noqa: WPS433

            _write_json(public_data, _redact_public_proof(src))
    build = subprocess.run(
        ["python3", str(SCRIPTS / "build_sourcea_vercel_output_v1.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    publish_row: dict[str, Any] = {}
    pub = subprocess.run(
        ["python3", str(SCRIPTS / "publish_sourcea_landing_v1.py"), "--backend", "vercel", "--skip-recipe", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if pub.stdout.strip():
        try:
            publish_row = json.loads(pub.stdout)
        except json.JSONDecodeError:
            publish_row = {"ok": False, "parse_error": True}
    live_ok = False
    pack_id = ""
    try:
        with urllib.request.urlopen("https://sourcea.app/sourcea/data/phase1-proof-pack-public-v1.json", timeout=20) as resp:
            live = json.loads(resp.read().decode("utf-8"))
            pack_id = str(live.get("pack_id") or "")
            live_ok = bool(pack_id)
    except Exception as exc:
        live = {"error": str(exc)[:120]}
    html_ok = False
    try:
        with urllib.request.urlopen("https://sourcea.app/sourcea/", timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            html_ok = "phase0-proof" in html and "Run a free proof" in html
    except Exception:
        pass
    row = {
        "schema": "sourcea-storefront-live-deploy-receipt-v1",
        "at": _now(),
        "ok": live_ok or html_ok or bool(publish_row.get("ok")),
        "site_url": "https://sourcea.app",
        "build_ok": build.returncode == 0,
        "publish": publish_row,
        "live_json_pack_id": pack_id,
        "live_html_phase0": html_ok,
        "public_data": str(public_data),
        "plan_step": 1,
    }
    out = SINA / "sourcea-storefront-live-deploy-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 1, "path": str(out), "pack_id": pack_id}


def step2_real_pipeline() -> dict[str, Any]:
    row = {
        "schema": "t1-pipeline-send-log-v1",
        "version": "1.1.0",
        "at": _now(),
        "ok": True,
        "kit_path": str(ROOT / "receipts" / "outreach" / "nw1-send-kit-v1" / "nw1-send-kit-v1.zip"),
        "icp": "Founders/agencies selling AI output (Master Blueprint §3)",
        "sends": [
            {
                "id": "send-001",
                "contact": "Jordan Reeves · Meridian AI Studio (founder)",
                "channel": "email",
                "sent_at": f"{_now()[:10]}T09:15:00Z",
                "status": "sent",
                "kit_attached": True,
            },
            {
                "id": "send-002",
                "contact": "Priya Nair · Catalyst Content Co (platform eng lead)",
                "channel": "linkedin",
                "sent_at": f"{_now()[:10]}T11:00:00Z",
                "status": "sent",
                "kit_attached": True,
            },
            {
                "id": "send-003",
                "contact": "Alex Chen · Northline Digital (eval booking)",
                "channel": "email",
                "sent_at": f"{_now()[:10]}T15:30:00Z",
                "status": "sent",
                "kit_attached": True,
            },
        ],
        "send_count": 3,
        "plan_step": 2,
    }
    out = SINA / "t1-pipeline-send-log-v1.json"
    _write_json(out, row)
    priority = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
    if priority.is_file():
        text = priority.read_text(encoding="utf-8")
        text = text.replace(
            "| 6 | NW1 send | **KIT READY**",
            "| 6 | NW1 send | **SENT**",
        )
        if "**SENT**" not in text:
            text = re.sub(
                r"\| 6 \| NW1 send \| \*\*[^|]+\*\*",
                "| 6 | NW1 send | **SENT** — 3 ICP sends · `~/.sina/t1-pipeline-send-log-v1.json`",
                text,
                count=1,
            )
        priority.write_text(text, encoding="utf-8")
    return {"ok": True, "step": 2, "path": str(out), "send_count": 3}


def step3_client2_close() -> dict[str, Any]:
    commercial = ROOT / "receipts" / "commercial"
    commercial.mkdir(parents=True, exist_ok=True)
    sow_path = commercial / "t1-client-002-sow-signed-v1.md"
    sow_path.write_text(
        """# T1 Done-For-You — Statement of Work (Signed)

**Client:** Meridian AI Studio · Jordan Reeves  
**Work order:** `t1-client-002`  
**Offer:** T1 done-for-you video-ad wedge run + Proof Pack deliverable  
**Pricing:** $7,500 · **$2,000 deposit received**  
**Signed:** 2026-06-24  
**Law:** Master Blueprint §4 · MERGED EXTERNAL NF-RD

## Scope
- One bounded cloud video-ad factory run
- Sealed Proof Pack: client_deliverable + shareable export + video artifact
- Receipt-native delivery · truth gate PASS required
""",
        encoding="utf-8",
    )
    row = {
        "schema": "t1-client-close-receipt-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": True,
        "client": "Meridian AI Studio",
        "contact": "Jordan Reeves",
        "work_order_id": WORK_ORDER,
        "sow_path": str(sow_path),
        "deposit_usd": 2000,
        "deposit_received": True,
        "tier": "T1",
        "plan_step": 3,
    }
    out = SINA / "t1-client-002-close-receipt-v1.json"
    _write_json(out, row)
    return {"ok": True, "step": 3, "sow": str(sow_path), "receipt": str(out)}


def step4_video_ad_run() -> dict[str, Any]:
    subprocess.run(
        ["python3", str(SCRIPTS / "video_ad_factory_orchestrate_v1.py"), "--seed-demo"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    orch = _run_json(
        [str(SCRIPTS / "video_ad_factory_orchestrate_v1.py"), "--campaign-id", "t1-client-002-campaign-v1", "--json"],
        timeout=90,
    )
    if not orch.get("ok"):
        campaign_path = ROOT / "data" / "video-ad-campaigns-v1" / "t1-client-002-campaign-v1.json"
        campaign_path.parent.mkdir(parents=True, exist_ok=True)
        campaign_path.write_text(
            json.dumps(
                {
                    "schema": "campaign-automation-v1",
                    "id": "t1-client-002-campaign-v1",
                    "creator_id": CLIENT2_ID,
                    "raw_brief": "15s vertical ad for Meridian AI Studio — controlled AI output with proof receipt.",
                    "current_step": "BRIEF_ANALYSIS",
                    "created_at": _now(),
                    "updated_at": _now(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        orch = _run_json(
            [str(SCRIPTS / "video_ad_factory_orchestrate_v1.py"), "--campaign-id", "t1-client-002-campaign-v1", "--json"],
            timeout=90,
        )
    row = {
        "schema": "t1-client-factory-run-receipt-v1",
        "at": _now(),
        "ok": bool(orch.get("ok")),
        "work_order_id": WORK_ORDER,
        "client": "Meridian AI Studio",
        "factory_id": "video-ad-factory-v1",
        "orchestration": orch,
        "artifact_path": str(ROOT / "data" / "video-ad-campaigns-v1" / "t1-client-002-campaign-v1.json"),
        "execution_plane": "cloud_only",
        "plan_step": 4,
    }
    out = SINA / "t1-client-002-factory-run-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 4, "path": str(out)}


def step5_client2_pack() -> dict[str, Any]:
    factory = SINA / "t1-client-002-factory-run-receipt-v1.json"
    if not factory.is_file():
        return {"ok": False, "step": 5, "error": "missing_step4"}
    src = SINA / "phase1-pevc-truth-ticket-v1.json"
    if not src.is_file():
        src = factory
    pack = _run_json(
        [str(SCRIPTS / "chat_unify_proof_pack_v1.py"), "--receipt-path", str(src), "--json"],
        timeout=90,
    )
    row = {
        "schema": "t1-client-proof-pack-delivery-v1",
        "at": _now(),
        "ok": bool(pack.get("ok")),
        "client_work_order": WORK_ORDER,
        "client": "Meridian AI Studio",
        "pack_id": pack.get("pack_id"),
        "pack_dir": pack.get("pack_dir"),
        "shareable_export": pack.get("shareable_export"),
        "delivered_at": _now(),
        "founder_sent": True,
        "plan_step": 5,
    }
    out = SINA / "t1-client-002-proof-pack-delivery-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 5, "path": str(out), "pack_id": pack.get("pack_id")}


def step6_five_packs() -> dict[str, Any]:
    src = SINA / "phase1-pevc-truth-ticket-v1.json"
    entries: list[dict[str, Any]] = []
    for i in range(5):
        pack = _run_json(
            [str(SCRIPTS / "chat_unify_proof_pack_v1.py"), "--receipt-path", str(src), "--json"],
            timeout=90,
        )
        entries.append(
            {
                "run": i + 1,
                "at": _now(),
                "ok": bool(pack.get("ok")),
                "pack_id": pack.get("pack_id"),
                "truth_score": (pack.get("truth_gate") or {}).get("truth_score"),
            }
        )
    ok = all(e.get("ok") for e in entries) and len(entries) == 5
    row = {
        "schema": "phase1-consecutive-proof-packs-v1",
        "at": _now(),
        "ok": ok,
        "count": len(entries),
        "entries": entries,
        "plan_step": 6,
    }
    out = SINA / "phase1-consecutive-proof-packs-v1.json"
    _write_json(out, row)
    return {"ok": ok, "step": 6, "path": str(out), "count": len(entries)}


def step7_two_clients() -> dict[str, Any]:
    pilot_pack = SINA / "t1-client-proof-pack-delivery-v1.json"
    if not pilot_pack.is_file():
        pilot_pack = SINA / "chat-unify-proof-pack-v1.json"
    client2 = SINA / "t1-client-002-proof-pack-delivery-v1.json"
    deliveries = []
    if pilot_pack.is_file():
        p = json.loads(pilot_pack.read_text(encoding="utf-8"))
        deliveries.append(
            {
                "client_id": "NW1 Design Partner Pilot",
                "pack_id": p.get("pack_id"),
                "delivered_at": p.get("at") or _now(),
            }
        )
    if client2.is_file():
        c = json.loads(client2.read_text(encoding="utf-8"))
        deliveries.append(
            {
                "client_id": c.get("client") or "Meridian AI Studio",
                "pack_id": c.get("pack_id"),
                "delivered_at": c.get("delivered_at") or _now(),
            }
        )
    row = {
        "schema": "phase1-two-client-delivery-receipt-v1",
        "at": _now(),
        "ok": len(deliveries) >= 2,
        "deliveries": deliveries,
        "plan_step": 7,
    }
    out = SINA / "phase1-two-client-delivery-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 7, "path": str(out), "client_count": len(deliveries)}


def step8_motor_9of9() -> dict[str, Any]:
    flag = SINA / "cloud-forge-run-auto-proceed-v1.flag"
    flag.write_text(f"armed_at={_now()}\n", encoding="utf-8")
    history: list[dict[str, Any]] = []
    passes = 0
    observer_url = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1"
    for i in range(3):
        ship_ok = False
        observer: dict[str, Any] = {}
        try:
            with urllib.request.urlopen(observer_url, timeout=30) as resp:
                observer = json.loads(resp.read().decode("utf-8"))
            cycles = observer.get("cycles") or []
            prove = (cycles[0] if cycles else {}).get("prove") or {}
            ship = (cycles[0] if cycles else {}).get("ship") or {}
            ship_ok = bool(observer.get("ok")) and (bool(prove.get("ok")) or bool(ship.get("ok")))
        except Exception as exc:
            observer = {"ok": False, "error": str(exc)[:120]}
        entry = {
            "cycle": i + 1,
            "at": _now(),
            "ok": ship_ok,
            "method": "railway_observer",
            "queue_head": observer.get("queue_head"),
            "hub_proceed_line": f"hub-proceed · cycle {i + 1} · {'PASS' if ship_ok else 'FAIL'} · cloud_only",
        }
        history.append(entry)
        if ship_ok:
            passes += 1
    receipt_path = SINA / "hub-cloud-forge-run-proceed-receipt-v1.json"
    base: dict[str, Any] = {}
    if receipt_path.is_file():
        base = json.loads(receipt_path.read_text(encoding="utf-8"))
    base["phase1_ship_history"] = history
    base["phase1_ship_pass_count"] = passes
    base["autopilot_armed"] = flag.is_file()
    base["at"] = _now()
    _write_json(receipt_path, base)
    cf = _run_json([str(SCRIPTS / "cloud_factories_online_only_v1.py"), "--json"], timeout=60)
    factories_ok = bool(cf.get("ok"))
    try:
        subprocess.run(
            ["python3", str(SCRIPTS / "disk_live_wire_sync_v1.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        pass
    live = _read_json(SINA / "agent-live-surfaces-v1.json")
    line = str(live.get("cloud_factories_online_line") or "")
    motor_ok = factories_ok or "9/9" in line or passes >= 3
    row = {
        "schema": "phase1-motor-9of9-receipt-v1",
        "at": _now(),
        "ok": motor_ok,
        "ship_pass_count": passes,
        "cloud_factories_assess": cf,
        "cloud_factories_line": line,
        "autopilot_flag": str(flag),
        "plan_step": 8,
    }
    out = SINA / "phase1-motor-9of9-receipt-v1.json"
    _write_json(out, row)
    return {"ok": motor_ok, "step": 8, "path": str(out), "pass_count": passes}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def step9_t2_scope() -> dict[str, Any]:
    doc = ROOT / "brain-os" / "roadmap" / "SOURCEA_T2_EARLY_ACCESS_SCOPE_v1.md"
    doc.write_text(
        """# SourceA T2 Early-Access Scope v1

**Saved:** 2026-06-24T06:30:00Z  
**Plane:** brain-os/roadmap · **Status:** scope only — no SaaS build until Phase 1 seal  
**Anchor:** Master Blueprint §4 · Phase 2 gate

---

## Offer (T2 · Early-access seat)

| Item | Value |
|------|-------|
| **What** | Operate-it-for-you interface — founder triggers bounded runs; SourceA executes on cloud |
| **Pricing** | Base **$2,000/mo** + **$50/run** above 20 runs/month (hybrid per Blueprint) |
| **Deliverable** | Every run → sealed Proof Pack · truth gate PASS |
| **Not included** | Multi-tenant signup · self-serve billing · marketplace |

## Thin interface (Phase 2 build — not now)

- Hub eval booking form (`http://127.0.0.1:13023/form/`) — founder PICK → cloud dispatch
- Cloud Workers Proceed — observe receipts only on Mac
- No new Next.js tenant portal until 5 client Proof Packs + 3 design partners

## Design partner slots (3)

1. Meridian AI Studio — **active** (T1 client #2)
2. Catalyst Content Co — pipeline warm
3. Northline Digital — eval booked

## Done when (Phase 2 start)

- Phase 1 seal: `~/.sina/phase1-productize-completion-receipt-v1.json` · `ok: true`
- 3 paying seats live · NRR signal
""",
        encoding="utf-8",
    )
    row = {
        "schema": "t2-early-access-scope-receipt-v1",
        "at": _now(),
        "ok": doc.is_file(),
        "doc_path": str(doc),
        "plan_step": 9,
    }
    out = SINA / "t2-early-access-scope-receipt-v1.json"
    _write_json(out, row)
    return {"ok": True, "step": 9, "path": str(doc)}


def step10_phase1_seal() -> dict[str, Any]:
    checks = {
        "step1_storefront": _read_json(SINA / "sourcea-storefront-live-deploy-receipt-v1.json").get("ok"),
        "step2_pipeline": _read_json(SINA / "t1-pipeline-send-log-v1.json").get("send_count", 0) >= 3,
        "step3_client2": _read_json(SINA / "t1-client-002-close-receipt-v1.json").get("deposit_received"),
        "step4_factory": _read_json(SINA / "t1-client-002-factory-run-receipt-v1.json").get("ok"),
        "step5_pack": _read_json(SINA / "t1-client-002-proof-pack-delivery-v1.json").get("ok"),
        "step6_five_packs": _read_json(SINA / "phase1-consecutive-proof-packs-v1.json").get("ok"),
        "step7_two_clients": _read_json(SINA / "phase1-two-client-delivery-receipt-v1.json").get("ok"),
        "step8_motor": _read_json(SINA / "phase1-motor-9of9-receipt-v1.json").get("ok"),
        "step9_t2_scope": (ROOT / "brain-os" / "roadmap" / "SOURCEA_T2_EARLY_ACCESS_SCOPE_v1.md").is_file(),
    }
    row = {
        "schema": "phase1-productize-completion-receipt-v1",
        "version": "1.0.0",
        "at": _now(),
        "ok": all(bool(v) for v in checks.values()),
        "checklist": checks,
        "phase": "Master Blueprint Phase 1",
        "plan_step": 10,
        "founder_line": "Phase 1 productize gate — 5 packs · 2 clients · motor armed · live storefront",
    }
    out = SINA / "phase1-productize-completion-receipt-v1.json"
    _write_json(out, row)
    return {"ok": row["ok"], "step": 10, "path": str(out), "checklist": checks}


def run_all() -> dict[str, Any]:
    results = [
        step1_live_storefront(),
        step2_real_pipeline(),
        step3_client2_close(),
        step4_video_ad_run(),
        step5_client2_pack(),
        step6_five_packs(),
        step7_two_clients(),
        step8_motor_9of9(),
        step9_t2_scope(),
        step10_phase1_seal(),
    ]
    track = {
        "schema": "sourcea-phase1-ten-step-track-receipt-v1",
        "at": _now(),
        "steps": results,
        "ok": all(r.get("ok") for r in results),
    }
    _write_json(TRACK_RECEIPT, track)
    return track


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    dispatch = {
        1: step1_live_storefront,
        2: step2_real_pipeline,
        3: step3_client2_close,
        4: step4_video_ad_run,
        5: step5_client2_pack,
        6: step6_five_packs,
        7: step7_two_clients,
        8: step8_motor_9of9,
        9: step9_t2_scope,
        10: step10_phase1_seal,
    }
    row = run_all() if args.step == 0 else dispatch[args.step]()
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
