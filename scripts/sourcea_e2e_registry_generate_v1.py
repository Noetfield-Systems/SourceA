#!/usr/bin/env python3
"""Generate data/sourcea-e2e-check-registry-v1.json — full validator catalog.

Law: brain-os/law/enforcement/SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md
Overrides: data/sourcea-e2e-check-registry-overrides-v1.json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BRAIN_SCRIPTS = ROOT / "brain-os" / "scripts"
WBC_SCRIPTS = ROOT / "witnessbc-site" / "scripts"
OUT = ROOT / "data" / "sourcea-e2e-check-registry-v1.json"
OVERRIDES = ROOT / "data" / "sourcea-e2e-check-registry-overrides-v1.json"
PRESSURE_REG = ROOT / "data" / "mac-pipeline-validator-pressure-registry-v1.json"
RUNTIME_REG = ROOT / "data" / "agent-runtime-validator-index-v1.json"
VALIDATOR_MACHINE = ROOT / "data" / "validator-machine-registry-v1.json"
GATE_MARKER = "_founder_session_gate_or_exit"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _check_id(path: Path) -> str:
    return path.stem


def _basename_script(path: str) -> str:
    return Path(path).name


def _pressure_tier(name: str, pressure: dict) -> str | None:
    tiers = pressure.get("tiers") or {}
    for tier in ("light", "medium", "heavy"):
        scripts = tiers.get(tier, {}).get("scripts") or []
        if name in scripts:
            return tier
        for glob in tiers.get(tier, {}).get("globs") or []:
            if fnmatch.fnmatch(name, glob):
                return tier
    return None


def _runtime_meta(name: str, runtime: dict) -> dict[str, Any]:
    validators = runtime.get("validators") or {}
    key = name
    if key not in validators:
        key = f"scripts/{name}"
    return dict(validators.get(key) or validators.get(name) or {})


def _has_gate(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:8000]
        return GATE_MARKER in text
    except OSError:
        return False


def _unified_tier(
    *,
    check_id: str,
    pressure_tier: str | None,
    runtime_meta: dict,
    is_e2e_name: bool,
    is_probe: bool,
) -> str:
    if is_probe:
        return "T0_probe"
    if is_e2e_name and pressure_tier in (None, "heavy"):
        if "full" in check_id or "all-e2e" in check_id or "marathon" in check_id:
            return "T4_marathon"
        if "landing" in check_id or "playwright" in check_id:
            return "T4_marathon"
        return "T3_heavy"
    if pressure_tier == "light":
        if "t1-crossref" in check_id:
            return "T1_fast"
        return "T1_fast"
    if pressure_tier == "medium":
        return "T2_medium"
    if pressure_tier == "heavy":
        return "T3_heavy"
    rt = str(runtime_meta.get("tier") or "")
    if rt == "cloud_ci" or rt == "deploy_only":
        return "T4_marathon"
    if rt in ("mac_light", "ship"):
        max_s = int(runtime_meta.get("max_runtime_s") or 0)
        if max_s and max_s <= 30:
            return "T1_fast"
        return "T2_medium"
    if "t1-crossref" in check_id:
        return "T1_fast"
    if "t2-crossref" in check_id or "t3-crossref" in check_id:
        return "T2_medium"
    if "e2e" in check_id:
        return "T3_heavy"
    return "T1_fast"


def _cadence(unified: str, check_id: str) -> str:
    if unified == "T0_probe" or unified == "T1_fast":
        return "daily"
    if unified == "T2_medium":
        return "weekly"
    if unified == "T3_heavy":
        return "weekly"
    return "monthly"


def _allowed_context(unified: str) -> list[str]:
    if unified in ("T0_probe", "T1_fast"):
        return ["founder_session", "ship_window", "cloud_ci"]
    if unified == "T2_medium":
        return ["ship_window", "cloud_ci"]
    return ["ship_window", "cloud_ci"]


def _scope(path: Path, runtime_meta: dict) -> str:
    if runtime_meta.get("network"):
        return "cloud"
    rel = str(path.relative_to(ROOT))
    if rel.startswith("witnessbc-site/"):
        return "cloud"
    return "mac_local"


def _est_wall(unified: str, runtime_meta: dict) -> int:
    if runtime_meta.get("max_runtime_s"):
        return int(runtime_meta["max_runtime_s"])
    return {
        "T0_probe": 5,
        "T1_fast": 30,
        "T2_medium": 120,
        "T3_heavy": 300,
        "T4_marathon": 600,
    }.get(unified, 60)


def _slo_defaults(*, cadence: str, est_wall_sec: int) -> dict[str, Any]:
    freshness = {
        "daily": 24 * 60,
        "weekly": 7 * 24 * 60,
        "monthly": 30 * 24 * 60,
        "3day": 3 * 24 * 60,
    }.get(cadence, 24 * 60)
    latency = max(5, int(round(est_wall_sec / 60.0)) + 5)
    return {
        "freshness_target_minutes": freshness,
        "success_rate_target": 0.99,
        "latency_target_minutes": latency,
    }


def _discover_scripts() -> list[Path]:
    found: dict[str, Path] = {}
    patterns = [
        (SCRIPTS, "validate-*-v1.sh"),
        (SCRIPTS, "validate-e2e*.sh"),
        (SCRIPTS, "validate-*e2e*.sh"),
        (SCRIPTS, "wbc-e2e.sh"),
        (BRAIN_SCRIPTS, "validate-*.sh"),
        (WBC_SCRIPTS, "*e2e*"),
    ]
    for base, pat in patterns:
        if not base.is_dir():
            continue
        for p in sorted(base.glob(pat)):
            if p.is_file():
                found[str(p.resolve())] = p
    for p in sorted(SCRIPTS.glob("*e2e*.py")):
        if p.is_file():
            found[str(p.resolve())] = p
    for extra in (
        SCRIPTS / "verify-founder-desktop-apps-v1.sh",
        SCRIPTS / "wbc-e2e.sh",
    ):
        if extra.is_file():
            found[str(extra.resolve())] = extra
    return list(found.values())


def _row_for_path(path: Path, *, pressure: dict, runtime: dict, overrides: dict) -> dict[str, Any]:
    rel = path.relative_to(ROOT).as_posix()
    cid = _check_id(path)
    name = path.name
    pressure_tier = _pressure_tier(name, pressure)
    runtime_meta = _runtime_meta(name, runtime)
    is_e2e = "e2e" in name.lower()
    unified = _unified_tier(
        check_id=cid,
        pressure_tier=pressure_tier,
        runtime_meta=runtime_meta,
        is_e2e_name=is_e2e,
        is_probe=False,
    )
    ov = (overrides.get("check_overrides") or {}).get(cid) or {}
    if ov.get("skip"):
        return {}
    unified = ov.get("unified_tier") or unified
    cadence = ov.get("cadence") or _cadence(unified, cid)
    bundle = ov.get("bundle")
    slo = ov.get("slo") or _slo_defaults(cadence=cadence, est_wall_sec=ov.get("est_wall_sec") or _est_wall(unified, runtime_meta))
    return {
        "id": cid,
        "script": rel,
        "kind": "shell" if path.suffix == ".sh" else "python",
        "scope": ov.get("scope") or _scope(path, runtime_meta),
        "unified_tier": unified,
        "pressure_tier": pressure_tier or "unknown",
        "runtime_tier": runtime_meta.get("tier"),
        "cadence": cadence,
        "est_wall_sec": ov.get("est_wall_sec") or _est_wall(unified, runtime_meta),
        "slo": slo,
        "bundle": bundle,
        "allowed_context": ov.get("allowed_context") or _allowed_context(unified),
        "gated": _has_gate(path) if path.suffix == ".sh" else False,
        "log_path": f"~/.sina/e2e-logs/{cid}.log",
    }


def _hub_probe_rows(overrides: dict) -> list[dict[str, Any]]:
    rows = []
    for probe in overrides.get("hub_probes") or []:
        if not isinstance(probe, dict):
            continue
        pid = str(probe.get("id") or "")
        rows.append(
            {
                "id": pid,
                "script": None,
                "kind": "http_probe",
                "url": probe.get("url"),
                "label": probe.get("label"),
                "scope": probe.get("scope") or "mac_local",
                "unified_tier": probe.get("unified_tier") or "T0_probe",
                "pressure_tier": "light",
                "runtime_tier": "probe",
                "cadence": probe.get("cadence") or "daily",
                "est_wall_sec": 5,
                "slo": probe.get("slo") or _slo_defaults(cadence=str(probe.get("cadence") or "daily"), est_wall_sec=5),
                "bundle": "mac_daily_smoke",
                "allowed_context": ["founder_session", "ship_window", "cloud_ci"],
                "gated": False,
                "log_path": f"~/.sina/e2e-logs/{pid}.log",
            }
        )
    return rows


def generate(*, write: bool = True) -> dict[str, Any]:
    pressure = _read(PRESSURE_REG)
    runtime = _read(RUNTIME_REG)
    overrides = _read(OVERRIDES)

    checks: list[dict[str, Any]] = []
    for path in _discover_scripts():
        row = _row_for_path(path, pressure=pressure, runtime=runtime, overrides=overrides)
        if row:
            checks.append(row)

    checks.extend(_hub_probe_rows(overrides))
    checks.sort(key=lambda r: (r.get("unified_tier") or "", r.get("id") or ""))

    # attach bundle membership from overrides
    bundle_defs = overrides.get("bundles") or {}
    bundle_index = {}
    for bid, bdef in bundle_defs.items():
        if not isinstance(bdef, dict):
            continue
        est_wall_sec = int(bdef.get("est_wall_sec") or 60)
        cadence = str(bdef.get("cadence") or _cadence("T3_heavy", bid))
        bundle_index[bid] = {
            **bdef,
            "id": bid,
            "slo": bdef.get("slo") or _slo_defaults(cadence=cadence, est_wall_sec=est_wall_sec),
        }
        for cid in bdef.get("checks") or []:
            for row in checks:
                if row.get("id") == cid and not row.get("bundle"):
                    row["bundle"] = bid

    e2e_ids = {r["id"] for r in checks if "e2e" in r.get("id", "")}
    row = {
        "schema": "sourcea-e2e-check-registry-v1",
        "version": "1.0.0",
        "generated_at": _now(),
        "generator": "scripts/sourcea_e2e_registry_generate_v1.py",
        "overrides": "data/sourcea-e2e-check-registry-overrides-v1.json",
        "law": "brain-os/law/enforcement/SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md",
        "slo": {
            "freshness_target_minutes": 24 * 60,
            "success_rate_target": 0.99,
            "latency_target_minutes": 60,
        },
        "summary": {
            "total_checks": len(checks),
            "e2e_named": len(e2e_ids),
            "by_tier": {},
        },
        "bundles": bundle_index,
        "checks": checks,
    }
    for tier in ("T0_probe", "T1_fast", "T2_medium", "T3_heavy", "T4_marathon"):
        row["summary"]["by_tier"][tier] = sum(1 for c in checks if c.get("unified_tier") == tier)

    if write:
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate SourceA E2E check registry")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Print summary without writing")
    args = ap.parse_args()
    row = generate(write=not args.dry_run)
    if args.json:
        print(json.dumps(row.get("summary") or row, indent=2))
    else:
        s = row.get("summary") or {}
        print(
            f"E2E_REGISTRY total={s.get('total_checks')} e2e_named={s.get('e2e_named')} "
            f"written={OUT if not args.dry_run else 'dry-run'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
