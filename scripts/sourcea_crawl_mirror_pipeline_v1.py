#!/usr/bin/env python3
"""SourceA crawl–mirror pipeline — CRAWL→EXTRACT→RANK→MIRROR→PROVE→SERVE (session tier).

Law: docs/SOURCEA_CRAWL_MIRROR_PIPELINE_LOCKED_v1.md
Receipt: ~/.sina/crawl-mirror-receipt-v1.json
Wraps anti_staleness_auto_wire_v1.py — does not replace it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "crawl-mirror-receipt-v1.json"
ANTI_RECEIPT = SINA / "anti-staleness-auto-wire-v1.json"
PY = sys.executable
SESSION_BUDGET_SEC = 90


def _age_sec(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        return time.time() - path.stat().st_mtime
    except OSError:
        return None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_json(out: str) -> dict:
    i = out.find("{")
    if i < 0:
        return {}
    try:
        return json.loads(out[i:])
    except json.JSONDecodeError:
        return {}


def _run(cmd: list[str], *, timeout: int = 120) -> tuple[int, str]:
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), timeout=timeout
        )
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or ""
    except subprocess.TimeoutExpired as e:
        return 124, (e.output or "") + "\nTIMEOUT"


def crawl_c4_factory_queue() -> dict:
    """C4 — factory queue SSOT (read-only crawl)."""
    factory = _read_json(SINA / "factory-now-v1.json")
    inbox = _read_json(SINA / "worker-prompt-inbox-v1.json")
    next10 = _read_json(SINA / "live-ongoing-prompts-next-10-v1.json")
    fn = factory.get("factory_now") or factory
    queue_sa = str(fn.get("queue_sa") or factory.get("queue_sa") or "")
    inbox_sa = str(
        (inbox.get("active") or {}).get("sa_id")
        or inbox.get("queue_sa")
        or (inbox.get("meta") or {}).get("sa_id")
        or ""
    )
    head = (next10.get("head") or {}) if isinstance(next10.get("head"), dict) else {}
    next_sa = str(head.get("sa_id") or "")
    refs = [v for v in (queue_sa, inbox_sa, next_sa) if v]
    aligned = len(set(refs)) <= 1 if refs else True
    pulse = _read_json(SINA / "outbound-factory-upgrade-pulse-v1.json")
    exec_h = pulse.get("execution_honesty") or {}
    exec_ok = bool(exec_h.get("ok", True))
    return {
        "ok": aligned,
        "crawler": "C4",
        "queue_sa": queue_sa or inbox_sa or next_sa,
        "refs": {"factory_now": queue_sa, "inbox": inbox_sa, "next10": next_sa},
        "aligned": aligned,
        "execution_honesty_ok": exec_ok,
        "execution_blocked": not exec_ok,
        "outbound_pulse": pulse.get("pulse_line"),
        "maturity_level": pulse.get("maturity_level"),
        "verified_done": (pulse.get("progress") or {}).get("verified_done"),
        "bulk_done": (pulse.get("progress") or {}).get("bulk_done"),
        "epic_bridge": pulse.get("epic_bridge"),
    }


def crawl_c7_validators_fast() -> dict:
    """C7 — validator health from last find_critical_bugs run."""
    last = _read_json(SINA / "find-bugs" / "last-run.json")
    critical = int(last.get("critical_count") or 0)
    ok = last.get("ok", True) and critical == 0
    return {
        "ok": ok,
        "crawler": "C7",
        "critical_count": critical,
        "verdict": last.get("verdict") or "",
        "ran_at": last.get("ran_at") or "",
        "findings": len(last.get("findings") or []),
    }


def prove_mirrors(anti: dict) -> dict:
    """M1–M4 proof from anti-staleness mirror steps."""
    paths = {
        "M1": SINA / "agent-memory-mirror-v1.json",
        "M2": SINA / "agent-live-surfaces-v1.json",
        "M3": SINA / "brain-live-context-v1.json",
        "M4": SINA / "worker-live-context-v1.json",
    }
    rows: dict[str, bool] = {}
    for mid, path in paths.items():
        rows[mid] = path.is_file()
    ok = all(rows.values()) and bool(anti.get("ok"))
    return {"ok": ok, "mirrors": rows}


def run_crawl_mirror_pipeline(
    *, role: str = "any", tier: str = "session", skip_anti_staleness: bool = False
) -> dict:
    t0 = time.monotonic()
    steps: list[dict] = []
    ok = True

    anti_age = _age_sec(ANTI_RECEIPT)
    need_anti = tier == "full" or not skip_anti_staleness or anti_age is None or anti_age > 120
    if need_anti:
        code, out = _run(
            [PY, str(SCRIPTS / "anti_staleness_auto_wire_v1.py"), "--role", role, "--tier", tier, "--json"],
            timeout=120,
        )
        anti = _parse_json(out)
        step_ok = code == 0 and anti.get("ok", True)
        steps.append(
            {
                "stage": "MIRROR",
                "step": "anti_staleness_auto_wire",
                "ok": step_ok,
                "exit": code,
                "queue_sa": anti.get("queue_sa"),
            }
        )
        ok = ok and step_ok
    else:
        anti = _read_json(ANTI_RECEIPT)
        steps.append(
            {
                "stage": "MIRROR",
                "step": "anti_staleness_auto_wire",
                "ok": bool(anti.get("ok")),
                "exit": 0,
                "note": f"fresh age_sec={round(anti_age or 0, 1)}",
                "queue_sa": anti.get("queue_sa"),
            }
        )
        ok = ok and bool(anti.get("ok"))

    c4 = crawl_c4_factory_queue()
    steps.append({"stage": "CRAWL", "step": "C4_factory_queue", **c4})
    ok = ok and bool(c4.get("ok"))

    c7 = crawl_c7_validators_fast()
    steps.append({"stage": "CRAWL", "step": "C7_validators_fast", **c7})
    # C7 ok=false is advisory in session tier — do not block mirror chain
    if tier == "full" and not c7.get("ok"):
        ok = False

    mirrors = prove_mirrors(anti)
    steps.append({"stage": "PROVE", "step": "M1_M4_mirrors", **mirrors})
    ok = ok and bool(mirrors.get("ok"))

    l8_ok = False
    try:
        from voyage_ai_live_wire_v1 import run_voyage_ai_live_wire  # noqa: WPS433

        voyage = run_voyage_ai_live_wire(tier="session")
        l8_ok = bool((voyage.get("provider") or {}).get("ok"))
        steps.append(
            {
                "stage": "L8",
                "step": "voyage_ai_live_wire",
                "ok": l8_ok,
                "voyage_line": (voyage.get("voyage_line") or "")[:96],
                "search_hits": (voyage.get("search") or {}).get("hits"),
            }
        )
        ok = ok and l8_ok
    except Exception as exc:
        steps.append({"stage": "L8", "step": "voyage_ai_live_wire", "ok": False, "error": str(exc)})
        ok = False

    elapsed = round(time.monotonic() - t0, 2)
    within_budget = elapsed <= SESSION_BUDGET_SEC if tier == "session" else True
    if tier == "session" and not within_budget:
        ok = False

    queue_sa = c4.get("queue_sa") or anti.get("queue_sa") or ""
    receipt = {
        "schema": "crawl-mirror-receipt-v1",
        "ok": ok,
        "at": _now(),
        "role": role,
        "tier": tier,
        "law": "docs/SOURCEA_CRAWL_MIRROR_PIPELINE_LOCKED_v1.md",
        "queue_sa": queue_sa,
        "factory_now_line": anti.get("factory_now_line") or _read_json(SINA / "agent-live-surfaces-v1.json").get("factory_now_line") or "",
        "critical_count": c7.get("critical_count"),
        "elapsed_sec": elapsed,
        "within_budget": within_budget,
        "stages": {
            "crawl": {"C4": c4.get("ok"), "C7": c7.get("ok")},
            "mirror": bool(anti.get("ok")),
            "prove": mirrors.get("ok"),
            "L8_voyage": l8_ok,
        },
        "steps": steps,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA crawl–mirror pipeline")
    ap.add_argument("--role", default="any")
    ap.add_argument("--tier", default="session", choices=["session", "worker", "nightly", "law_ship"])
    ap.add_argument("--skip-anti-staleness", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    tier = "session" if args.tier == "worker" else args.tier
    if args.tier == "worker":
        tier = "worker"
    row = run_crawl_mirror_pipeline(
        role=args.role, tier=tier, skip_anti_staleness=args.skip_anti_staleness
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"CRAWL_MIRROR ok={row['ok']} tier={args.tier} "
            f"queue={row.get('queue_sa')} elapsed={row.get('elapsed_sec')}s"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
