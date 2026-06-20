#!/usr/bin/env python3
"""Rule propagation fanout — new rules/SSOT → nerves → gates → surfaces → truth bundle.

Law: data/rule-propagation-zero-latency-v1.json
Receipt: ~/.sina/rule-propagation-fanout-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "rule-propagation-zero-latency-v1.json"
RECEIPT = SINA / "rule-propagation-fanout-receipt-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
TRUTH_CACHE = SINA / "last-truth-bundle-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run_step(script: str, extra: list[str] | None = None, *, timeout: float = 120) -> dict:
    path = SCRIPTS / script
    if not path.is_file():
        return {"ok": False, "error": f"missing:{script}"}
    cmd = [PY, str(path), "--json"]
    if extra:
        cmd.extend(extra)
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), timeout=timeout)
        i = out.find("{")
        row = json.loads(out[i:]) if i >= 0 else {"raw": out[:200]}
        return {"ok": True, "script": script, "result": row}
    except subprocess.CalledProcessError as exc:
        return {"ok": False, "script": script, "error": (exc.output or str(exc))[:200]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "script": script, "error": "timeout"}
    except Exception as exc:
        return {"ok": False, "script": script, "error": str(exc)[:200]}


def _lightweight_surfaces_from_truth() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from agent_truth_bundle_v1 import build_agent_truth_bundle  # noqa: WPS433
    from disk_live_wire_sync_v1 import _surfaces_from_bundle  # noqa: WPS433

    bundle = build_agent_truth_bundle()
    SINA.mkdir(parents=True, exist_ok=True)
    TRUTH_CACHE.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    surfaces = _surfaces_from_bundle(bundle)
    prior = _read(SURFACES)
    if prior.get("rule_wire_line"):
        surfaces["rule_wire_line"] = prior["rule_wire_line"]
    if prior.get("rule_zero_latency_hook"):
        surfaces["rule_zero_latency_hook"] = prior["rule_zero_latency_hook"]
    SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "queue_sa": surfaces.get("queue_sa"), "factory_now_line": (surfaces.get("factory_now_line") or "")[:80]}


def fanout(*, reason: str = "manual", tier: str = "full", trigger_path: str = "") -> dict:
    fast = tier == "fast"
    steps: list[dict] = []
    ok = True
    warns: list[str] = []

    for ssot_rel in (
        "data/factory-era-v1.json",
        "data/forge-factory-unified-brand-v1.json",
        "data/supabase-portfolio-tiers-v1.json",
        "data/goal-registry-v1.json",
    ):
        p = ROOT / ssot_rel
        step_ok = p.is_file()
        steps.append({"step": "ssot_read", "path": ssot_rel, "ok": step_ok})
        ok = ok and step_ok

    era_src = ROOT / "data" / "factory-era-v1.json"
    era_dst = SINA / "factory-era-v1.json"
    if era_src.is_file():
        era_dst.parent.mkdir(parents=True, exist_ok=True)
        era_dst.write_text(era_src.read_text(encoding="utf-8"), encoding="utf-8")
        steps.append({"step": "era_mirror", "ok": True, "path": str(era_dst)})
    else:
        steps.append({"step": "era_mirror", "ok": False})
        ok = False

    anti_tier = "session" if fast else "session"
    anti_row = _run_step(
        "anti_staleness_auto_wire_v1.py",
        ["--role", "any", "--tier", anti_tier],
        timeout=60 if fast else 90,
    )
    anti_ok = bool(anti_row.get("ok")) or fast
    if fast and not anti_row.get("ok"):
        anti_row["warn_only"] = True
    steps.append({"step": "anti_staleness_auto_wire", **anti_row, "ok": anti_ok})
    ok = ok and anti_ok

    queue_extra = ["--fast"] if fast else []
    queue_row = _run_step("queue_ssot_unify_v1.py", queue_extra, timeout=45 if fast else 120)
    queue_ok = bool(queue_row.get("ok")) or (
        fast and bool((queue_row.get("result") or {}).get("steps"))
    )
    if fast and not queue_ok:
        warns.append("queue_ssot_unify_warn")
        queue_row["warn_only"] = True
    steps.append({"step": "queue_ssot_unify_v1", **queue_row, "ok": queue_ok if not fast else True})
    ok = ok and (queue_ok or fast)

    for script in ("active_now_sync_from_factory_now_v1.py",):
        row = _run_step(script, timeout=45 if fast else 90)
        steps.append({"step": script.replace(".py", ""), **row})
        ok = ok and bool(row.get("ok"))

    if fast:
        surf = _lightweight_surfaces_from_truth()
        steps.append({"step": "disk_live_wire_fast", **surf})
        ok = ok and bool(surf.get("ok"))
    else:
        disk_row = _run_step("disk_live_wire_sync_v1.py", ["--skip-factory"], timeout=180)
        disk_ok = bool(disk_row.get("ok"))
        if not disk_ok:
            surf = _lightweight_surfaces_from_truth()
            steps.append({"step": "disk_live_wire_fallback", **surf})
            ok = ok and bool(surf.get("ok"))
        else:
            steps.append({"step": "disk_live_wire_sync_v1", **disk_row})
            ok = ok and disk_ok

    sys.path.insert(0, str(SCRIPTS))
    try:
        from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

        fn = rebuild_factory_now(caller="rule_propagation_fanout", force=True)
        steps.append({"step": "factory_now", "ok": True, "queue_sa": fn.get("queue_sa"), "mode": fn.get("mode")})
    except Exception as exc:
        steps.append({"step": "factory_now", "ok": False, "error": str(exc)[:120]})
        ok = False

    if not fast:
        try:
            from agent_truth_bundle_v1 import build_agent_truth_bundle  # noqa: WPS433

            tb = build_agent_truth_bundle()
            steps.append({"step": "truth_bundle", "ok": bool(tb.get("ok", True))})
        except Exception as exc:
            steps.append({"step": "truth_bundle", "ok": False, "error": str(exc)[:120]})
            ok = False

    receipt = {
        "schema": "rule-propagation-fanout-receipt-v1",
        "ok": ok,
        "at": _now(),
        "reason": reason,
        "tier": tier,
        "trigger_path": trigger_path or None,
        "law": str(SSOT.relative_to(ROOT)),
        "steps": steps,
        "warnings": warns,
        "line": f"rule-fanout · {'PASS' if ok else 'FAIL'} · tier={tier} · zero-latency governance",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Rule propagation fanout — zero-latency governance")
    ap.add_argument("--reason", default="manual")
    ap.add_argument("--tier", choices=("fast", "full"), default="full")
    ap.add_argument("--fast", action="store_true", help="Mac-safe fast tier — no full disk_live_wire")
    ap.add_argument("--path", default="", help="Trigger path for receipt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    tier = "fast" if args.fast else args.tier
    row = fanout(reason=args.reason, tier=tier, trigger_path=args.path)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
