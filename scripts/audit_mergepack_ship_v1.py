#!/usr/bin/env python3
"""Probe MergePack ship gates — update machine status files."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MERGEPACK_ROOT = Path.home() / "Desktop" / "mergepack"
STATUS_PATH = Path.home() / ".sina" / "mergepack_ship_status_v1.json"
PROG_PATH = MERGEPACK_ROOT / "PROGRAM_PROGRESS.json"

UI_URL = "https://frontend-the-777-foundation.vercel.app"
API_HEALTH = "https://mergepack-api-production.up.railway.app/health"
KPI_URL = "https://mergepack-api-production.up.railway.app/v1/kpi"
FORM_URL = "https://frontend-bice-ten-x2gt8cr50b.vercel.app/form-to-pdf"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _probe(url: str, timeout: int = 20) -> dict:
    import subprocess

    try:
        proc = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", str(timeout), url],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
        code = int((proc.stdout or "0").strip() or "0")
        return {"url": url, "http": code, "ok": 200 <= code < 400}
    except Exception as e:
        return {"url": url, "http": 0, "ok": False, "error": str(e)}


def _load_kpi() -> dict:
    try:
        with urllib.request.urlopen(KPI_URL, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def main() -> int:
    ui = _probe(UI_URL)
    api = _probe(API_HEALTH)
    form = _probe(FORM_URL)
    kpi = _load_kpi()
    mp_ship = ui.get("http") == 200
    mp_pay = bool(kpi.get("kpi_first_payment"))
    row = {
        "schema": "mergepack-ship-status-v1",
        "updated_at": _now(),
        "MP-SHIP": mp_ship,
        "MP-PAY": mp_pay,
        "api_health": {"url": API_HEALTH, "http": api.get("http"), "ok": api.get("ok")},
        "ui_main": {
            "url": UI_URL,
            "http": ui.get("http"),
            "blocker": None if mp_ship else "Vercel Deployment Protection — Actions → MP-SHIP Vercel settings",
        },
        "form_to_pdf": {"url": FORM_URL, "http": form.get("http"), "ok": form.get("ok")},
        "kpi_trio": {
            "kpi_first_payment": bool(kpi.get("kpi_first_payment")),
            "kpi_first_referral_payment": bool(kpi.get("kpi_first_referral_payment")),
            "kpi_first_organic_user": bool(kpi.get("kpi_first_organic_user")),
            "kpi_trio_complete": bool(kpi.get("kpi_trio_complete")),
        },
        "founder_next": (
            "MP-SHIP done — chase MP-PAY + KPI trio"
            if mp_ship
            else "Vercel → disable Deployment Protection on frontend-the-777-foundation → Refresh → re-run audit"
        ),
    }
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if PROG_PATH.is_file():
        prog = json.loads(PROG_PATH.read_text(encoding="utf-8"))
        ms = prog.setdefault("milestones", {})
        ms["MP-SHIP"] = mp_ship
        ms["MP-PAY"] = mp_pay
        ms["MP-KPI-TRIO"] = bool(kpi.get("kpi_trio_complete"))
        trio = prog.setdefault("kpi_trio", {})
        trio["first_payment"] = bool(kpi.get("kpi_first_payment"))
        trio["first_referral_payment"] = bool(kpi.get("kpi_first_referral_payment"))
        trio["first_organic_user"] = bool(kpi.get("kpi_first_organic_user"))
        trio["complete"] = bool(kpi.get("kpi_trio_complete"))
        prog["updated_at"] = _now()
        PROG_PATH.write_text(json.dumps(prog, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "MP-SHIP": mp_ship, "MP-PAY": mp_pay, "ui_http": ui.get("http")}, indent=2))
    return 0 if mp_ship else 1


if __name__ == "__main__":
    raise SystemExit(main())
