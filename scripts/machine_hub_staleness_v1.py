#!/usr/bin/env python3
"""H2 Machine Hub staleness probe — registry age + form alignment."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
H2_REGISTRY = SINA / "h2-pending-registry-v1.json"

STALE_SEC = 600
AGING_SEC = 180
CRITICAL_SEC = 3600


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _age_sec(ts: str | None) -> float | None:
    dt = _parse_iso(ts)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())


def machine_hub_staleness_probe(*, registry: dict | None = None) -> dict:
    if registry is None:
        if not H2_REGISTRY.is_file():
            registry = {}
        else:
            try:
                registry = json.loads(H2_REGISTRY.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                registry = {}

    updated_at = registry.get("updated_at")
    age = _age_sec(updated_at)
    issues: list[str] = []

    live_oq = None
    try:
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        live_oq = int(live_form_payload().get("open_questions_count") or 0)
    except Exception:
        live_oq = None

    fo = registry.get("form_open") or {}
    reg_oq_raw = fo.get("count")
    reg_oq = int(reg_oq_raw) if reg_oq_raw is not None else None
    form_aligned = live_oq is None or reg_oq is None or reg_oq == live_oq
    if reg_oq is not None and live_oq is not None and reg_oq != live_oq:
        issues.append(f"form_open drift registry={reg_oq} live={live_oq}")

    if age is None:
        status = "unknown"
        auto_heal = True
    elif not form_aligned or age >= CRITICAL_SEC:
        status = "critical"
        auto_heal = True
    elif age >= STALE_SEC:
        status = "stale"
        auto_heal = True
    elif age >= AGING_SEC:
        status = "aging"
        auto_heal = True
    else:
        status = "fresh"
        auto_heal = False

    return {
        "schema": "machine-hub-staleness-v1",
        "status": status,
        "age_sec": round(age, 1) if age is not None else None,
        "updated_at": updated_at,
        "auto_heal_recommended": auto_heal,
        "form_aligned": form_aligned,
        "issues": issues,
        "poll_interval_sec": 30 if status in ("stale", "critical", "aging") else 60,
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Machine hub staleness probe")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = machine_hub_staleness_probe()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"H2-STALE: {row.get('status')} age={row.get('age_sec')} heal={row.get('auto_heal_recommended')}")
    return 0 if row.get("status") not in ("critical",) or not row.get("issues") else 1


if __name__ == "__main__":
    raise SystemExit(main())
