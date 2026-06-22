#!/usr/bin/env python3
"""Portfolio fix plan pulse — TF ladder · WBC prod · defer gate · role-separated tasks.

Law: docs/SOURCEA_PORTFOLIO_FIX_PLAN_LOCKED_v1.md
SSOT: data/portfolio-fix-plan-v1.json
Receipt: ~/.sina/portfolio-fix-plan-pulse-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "portfolio-fix-plan-v1.json"
RECEIPT = SINA / "portfolio-fix-plan-pulse-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
DEFER_RECEIPT = SINA / "commercial-email-send-defer-receipt-v1.json"
TF_LADDER = Path.home() / "Desktop" / "TrustField Technologies" / "os" / "ladder_state.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _curl_text(url: str, *, timeout: float = 12.0) -> tuple[bool, str, float]:
    t0 = datetime.now(timezone.utc).timestamp()
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "SourceA-portfolio-pulse/1.0 (+https://www.trustfield.ca)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            ok = int(getattr(resp, "status", 200) or 200) < 400
        elapsed = datetime.now(timezone.utc).timestamp() - t0
        return ok, body, elapsed
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as exc:
        elapsed = datetime.now(timezone.utc).timestamp() - t0
        return False, str(exc)[:160], elapsed


def _witnessbc_markers(html: str) -> dict:
    return {
        "dispatch": "AI policy at dispatch" in html or "policy at dispatch" in html,
        "brand_disambig": "brand-disambiguation" in html,
        "journalism_stale": "Independent Public-interest Journalism" in html
        or ("journalism" in html.lower() and "dispatch" not in html.lower()[:8000]),
    }


def _assess_ladder() -> dict:
    row = _read(TF_LADDER)
    steps = row.get("steps") or {}
    red = [int(k) for k, v in steps.items() if str(v.get("status") or "").lower() == "red"]
    blocked_1_4 = [i for i in red if i <= 4]
    trackers = row.get("trackers") or {}
    return {
        "ok": not row.get("commercial_blocked") and not blocked_1_4,
        "commercial_blocked": bool(row.get("commercial_blocked")),
        "steps_1_4_red": blocked_1_4,
        "priority_step": row.get("priority_step"),
        "outreach_sent_agent": int(trackers.get("outreach_sent_agent") or 0),
        "demos_booked_agentic": int(trackers.get("demos_booked_agentic") or 0),
        "demos_completed": int(trackers.get("demos_completed") or 0),
        "path": str(TF_LADDER),
    }


def _assess_trustfield_pages() -> dict:
    urls = [
        "https://www.trustfield.ca/",
        "https://www.trustfield.ca/start",
        "https://www.trustfield.ca/pricing",
        "https://www.trustfield.ca/register?partner=demo-msb-tor",
        "https://www.trustfield.ca/api/readiness",
    ]
    results = []
    all_ok = True
    for url in urls:
        timeout = 20.0 if url.endswith("/api/readiness") else 15.0
        ok, _, elapsed = _curl_text(url, timeout=timeout)
        results.append({"url": url, "ok": ok, "elapsed_sec": round(elapsed, 2)})
        if not ok:
            all_ok = False
    return {"ok": all_ok, "pages": results}


def _assess_witnessbc() -> dict:
    preview_from_disk = False
    preview_ok, preview_html, _ = _curl_text("https://witnessbc-commercial.pages.dev/")
    prod_ok, prod_html, _ = _curl_text("https://www.witnessbc.com/")
    preview_m = _witnessbc_markers(preview_html) if preview_ok else {}
    if not preview_ok:
        deploy_index = ROOT / "witnessbc-site" / "dist" / "deploy" / "index.html"
        if deploy_index.is_file():
            preview_m = _witnessbc_markers(deploy_index.read_text(encoding="utf-8", errors="replace"))
            preview_ok = True
            preview_from_disk = True
    prod_m = _witnessbc_markers(prod_html) if prod_ok else {}
    prod_pass = (
        prod_ok
        and prod_m.get("dispatch")
        and prod_m.get("brand_disambig")
        and not prod_m.get("journalism_stale")
    )
    preview_pass = preview_ok and preview_m.get("dispatch") and preview_m.get("brand_disambig")
    return {
        "preview_ok": preview_pass,
        "prod_ok": prod_pass,
        "preview": preview_m,
        "prod": prod_m,
        "blocker": "dns_cutover" if preview_pass and not prod_pass else None,
        "preview_source": "disk_deploy" if preview_from_disk else "live_curl",
    }


def _assess_defer() -> dict:
    defer = _read(DEFER_RECEIPT)
    sites = defer.get("product_sites") or []
    wbc = next((s for s in sites if s.get("id") == "witnessbc"), {})
    return {
        "defer_line": defer.get("email_send_defer_line") or "",
        "sites_online": bool(defer.get("sites_online")),
        "main_factories_online": bool(defer.get("main_factories_online")),
        "founder_lift": bool(defer.get("founder_lift")),
        "witnessbc_site_ok": bool(wbc.get("ok")),
        "witnessbc_detail": str(wbc.get("detail") or "")[:120],
    }


def _assess_wbc_guards() -> dict:
    script = ROOT / "scripts" / "validate-witnessbc-ui-zero-drift-v1.sh"
    if not script.is_file():
        return {"ok": False, "error": "missing validator"}
    proc = subprocess.run(["bash", str(script)], cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    return {"ok": proc.returncode == 0, "tail": (proc.stdout or proc.stderr or "")[-200:]}


def _compose_line(*, ladder: dict, wbc: dict, defer: dict) -> str:
    tf = "GREEN" if ladder.get("ok") else "RED"
    wbc_s = "GREEN" if wbc.get("prod_ok") else ("PREVIEW" if wbc.get("preview_ok") else "RED")
    sites = "GREEN" if defer.get("sites_online") else "RED"
    if not ladder.get("ok"):
        nxt = "TF ladder"
    elif not wbc.get("prod_ok"):
        nxt = "WBC DNS"
    elif not defer.get("sites_online"):
        nxt = "sites"
    elif not defer.get("founder_lift"):
        nxt = "lift"
    else:
        nxt = "MSB outreach"
    return f"portfolio-fix · P0 TF={tf} WBC={wbc_s} defer=sites:{sites} · next={nxt}"


def run_pulse(*, wire: bool = False) -> dict:
    ssot = _read(SSOT)
    ladder = _assess_ladder()
    tf_pages = _assess_trustfield_pages()
    wbc = _assess_witnessbc()
    defer = _assess_defer()
    guards = _assess_wbc_guards()
    line = _compose_line(ladder=ladder, wbc=wbc, defer=defer)

    p0_ok = ladder.get("ok") and wbc.get("prod_ok") and defer.get("sites_online")
    row = {
        "schema": "portfolio-fix-plan-pulse-v1",
        "at": _now(),
        "ok": p0_ok,
        "portfolio_fix_line": line,
        "phase": "P0" if not p0_ok else ("P1" if not defer.get("founder_lift") else "P2"),
        "ladder": ladder,
        "trustfield_pages": tf_pages,
        "witnessbc": wbc,
        "defer": defer,
        "wbc_guards": guards,
        "tasks_ready": {
            "trustfield_agent": bool(defer.get("founder_lift") and ladder.get("ok")),
            "sourcea_worker": not guards.get("ok"),
            "founder": bool(defer.get("sites_online") and not defer.get("founder_lift")),
        },
        "ssot": str(SSOT.relative_to(ROOT)),
        "human_doc": ssot.get("human_doc"),
    }

    if wire:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        surfaces = _read(SURFACES)
        surfaces["portfolio_fix_line"] = line
        surfaces["portfolio_fix"] = {
            "ok": p0_ok,
            "phase": row["phase"],
            "receipt": str(RECEIPT),
            "at": row["at"],
        }
        SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--wire", action="store_true")
    args = ap.parse_args()
    row = run_pulse(wire=args.wire)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("portfolio_fix_line") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
