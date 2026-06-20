#!/usr/bin/env python3
"""Mac pipeline & validator pressure law v1.1 — enforce tier registry on Mac body."""
from __future__ import annotations

import fnmatch
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REGISTRY = ROOT / "data" / "mac-pipeline-validator-pressure-registry-v1.json"
SINA = Path.home() / ".sina"
LIGHT_ONLY_FLAG = SINA / "mac-light-validators-only-v1.flag"
SHIP_WINDOW_FLAG = SINA / "asf-ship-window-v1.flag"
LAW_DOC = Path.home() / "Desktop/MacLaw/MAC_PIPELINE_VALIDATOR_PRESSURE_LAW_LOCKED_v1.md"
RECEIPT_PATH = SINA / "mac-health" / "pipeline-validator-pressure-latest-v1.json"
GATE_MARKER = "_founder_session_gate_or_exit"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_registry() -> dict[str, Any]:
    if not REGISTRY.is_file():
        return {}
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _expand(path_str: str) -> Path:
    return Path(str(path_str).replace("~", str(Path.home()))).expanduser()


def ship_window_open() -> bool:
    reg = _load_registry()
    raw = reg.get("ship_window_flag") or str(SHIP_WINDOW_FLAG)
    return _expand(str(raw)).is_file()


def founder_session_active() -> bool:
    reg = _load_registry()
    for raw in reg.get("founder_session_flags") or []:
        if _expand(raw).is_file():
            return True
    return False


def _tier_scripts(tier: str) -> list[str]:
    reg = _load_registry()
    return list(((reg.get("tiers") or {}).get(tier) or {}).get("scripts") or [])


def _tier_globs(tier: str) -> list[str]:
    reg = _load_registry()
    return list(((reg.get("tiers") or {}).get(tier) or {}).get("globs") or [])


def _light_scripts() -> frozenset[str]:
    return frozenset(_tier_scripts("light"))


def classify_script(script_name: str) -> str:
    name = Path(script_name).name
    if name in _light_scripts():
        return "light"
    for tier in ("medium", "heavy"):
        if name in _tier_scripts(tier):
            return tier
        for glob in _tier_globs(tier):
            if fnmatch.fnmatch(name, glob):
                return tier
    return "light"


def heavy_deny_set() -> frozenset[str]:
    names: set[str] = set(_tier_scripts("heavy")) | set(_tier_scripts("medium"))
    for tier in ("medium", "heavy"):
        for glob in _tier_globs(tier):
            if SCRIPTS.is_dir():
                for path in SCRIPTS.glob("*.sh"):
                    if fnmatch.fnmatch(path.name, glob):
                        names.add(path.name)
    return frozenset(names)


def forbidden_body_patterns() -> list[str]:
    reg = _load_registry()
    return list(((reg.get("tiers") or {}).get("forbidden_body") or {}).get("process_patterns") or [])


def check_script_allowed(*, script_name: str) -> dict[str, Any]:
    name = Path(script_name).name
    tier = classify_script(name)
    if tier in ("medium", "heavy") and founder_session_active() and not ship_window_open():
        return {
            "ok": False,
            "blocked": True,
            "tier": tier,
            "script": name,
            "reason": "founder_session_no_heavy_gates",
            "action": (
                "Cloud CI or ASF ship window (touch ~/.sina/asf-ship-window-v1.flag) — "
                "see MAC_PIPELINE_VALIDATOR_PRESSURE_LAW_LOCKED_v1.md"
            ),
        }
    return {"ok": True, "blocked": False, "tier": tier, "script": name}


def audit_heavy_gate_wiring() -> dict[str, Any]:
    """HEAVY/MEDIUM scripts should source founder session gate (defense in depth)."""
    missing: list[str] = []
    wired: list[str] = []
    for name in sorted(heavy_deny_set()):
        path = SCRIPTS / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if GATE_MARKER in text:
            wired.append(name)
        else:
            missing.append(name)
    return {
        "ok": len(missing) == 0,
        "wired_count": len(wired),
        "missing_count": len(missing),
        "missing": missing[:40],
        "wired_sample": wired[:8],
    }


def probe_cursor_caps() -> dict[str, Any]:
    reg = _load_registry()
    caps = reg.get("cursor_caps") or {}
    max_hosts = int(caps.get("max_extension_hosts") or 3)
    try:
        sys_path = SCRIPTS
        if str(sys_path) not in __import__("sys").path:
            __import__("sys").path.insert(0, str(sys_path))
        from cursor_session_relief_v1 import probe_cursor_session  # noqa: WPS433

        row = probe_cursor_session()
        hosts = int(row.get("extension_host_count") or 0)
        rss_gb = float(row.get("rss_mb") or 0) / 1024.0
        over = hosts > max_hosts
        return {
            "ok": not over,
            "extension_hosts": hosts,
            "max_extension_hosts": max_hosts,
            "rss_gb": round(rss_gb, 2),
            "founder_line": row.get("founder_line"),
            "needs_restart": bool(row.get("needs_restart")),
        }
    except Exception as exc:
        return {"ok": True, "skipped": True, "error": str(exc)[:120]}


def _pgrep(pattern: str) -> list[int]:
    try:
        proc = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    return [int(x) for x in (proc.stdout or "").split() if x.strip().isdigit()]


def probe_forbidden_body_processes() -> dict[str, Any]:
    running: list[dict[str, Any]] = []
    for pat in forbidden_body_patterns():
        pids = _pgrep(pat)
        if pids:
            running.append({"pattern": pat, "pids": pids})
    return {"ok": len(running) == 0, "running": running}


def _ensure_light_only_flag() -> dict[str, Any]:
    if LIGHT_ONLY_FLAG.is_file():
        return {"path": str(LIGHT_ONLY_FLAG), "action": "already"}
    SINA.mkdir(parents=True, exist_ok=True)
    LIGHT_ONLY_FLAG.write_text(
        f"mac-light-validators-only-v1 · {_now()} · heavy gates forbidden on Mac body\n",
        encoding="utf-8",
    )
    return {"path": str(LIGHT_ONLY_FLAG), "action": "created"}


def _launchd_loaded(label: str) -> bool:
    uid = os.getuid()
    try:
        proc = subprocess.run(
            ["launchctl", "print", f"gui/{uid}/{label}"],
            capture_output=True,
            text=True,
            timeout=4.0,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _collect_violations(*, strict_audit: bool) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    reg = _load_registry()
    if founder_session_active() and not LIGHT_ONLY_FLAG.is_file():
        violations.append({"id": "light_only_flag_missing", "detail": str(LIGHT_ONLY_FLAG)})
    body = probe_forbidden_body_processes()
    if not body.get("ok"):
        violations.append({"id": "forbidden_body_running", "detail": str(body.get("running"))})
    for label in ((reg.get("tiers") or {}).get("forbidden_body") or {}).get("launch_labels_forbidden") or []:
        if _launchd_loaded(str(label)):
            violations.append({"id": "forbidden_launchd", "detail": str(label)})
    audit = audit_heavy_gate_wiring()
    if strict_audit and audit.get("missing"):
        violations.append(
            {
                "id": "heavy_scripts_missing_gate",
                "detail": f"missing={audit.get('missing_count')} sample={audit.get('missing')[:5]}",
            }
        )
    return violations


def run_pressure_probe(*, side_effects: bool = True, strict_audit: bool = False) -> dict[str, Any]:
    reg = _load_registry()
    violations: list[dict[str, str]] = []
    if not LAW_DOC.is_file():
        violations.append({"id": "missing_law_doc", "detail": str(LAW_DOC)})
    if not REGISTRY.is_file():
        violations.append({"id": "missing_registry", "detail": str(REGISTRY)})
    violations.extend(_collect_violations(strict_audit=strict_audit))

    enforce: dict[str, Any] = {}
    if side_effects and violations:
        enforce["light_only_flag"] = _ensure_light_only_flag()
        body = probe_forbidden_body_processes()
        if not body.get("ok"):
            for row in body.get("running") or []:
                for pid in row.get("pids") or []:
                    try:
                        subprocess.run(["kill", "-TERM", str(pid)], capture_output=True, timeout=3.0)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
            enforce["body_kill"] = probe_forbidden_body_processes()
        for label in ((reg.get("tiers") or {}).get("forbidden_body") or {}).get("launch_labels_forbidden") or []:
            if _launchd_loaded(str(label)):
                uid = os.getuid()
                try:
                    subprocess.run(
                        ["launchctl", "bootout", f"gui/{uid}/{label}"],
                        capture_output=True,
                        timeout=8.0,
                    )
                    enforce.setdefault("bootout", []).append(label)
                except (OSError, subprocess.TimeoutExpired):
                    pass
        violations = _collect_violations(strict_audit=strict_audit)
        if not LAW_DOC.is_file():
            violations.insert(0, {"id": "missing_law_doc", "detail": str(LAW_DOC)})

    row = {
        "schema": "mac-pipeline-validator-pressure-v1",
        "version": str(reg.get("version") or "1.0.0"),
        "at": _now(),
        "law_doc": str(LAW_DOC),
        "registry": str(REGISTRY),
        "founder_session_active": founder_session_active(),
        "ship_window_open": ship_window_open(),
        "light_only_flag": LIGHT_ONLY_FLAG.is_file(),
        "heavy_deny_count": len(heavy_deny_set()),
        "gate_audit": audit_heavy_gate_wiring(),
        "cursor_caps": probe_cursor_caps(),
        "forbidden_body": probe_forbidden_body_processes(),
        "side_effects": side_effects,
        "strict_audit": strict_audit,
        "enforce": enforce,
        "violations": violations,
        "ok": len(violations) == 0,
    }
    if side_effects:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def wire_gate_into_script(path: Path) -> bool:
    if not path.is_file() or GATE_MARKER in path.read_text(encoding="utf-8", errors="replace"):
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    inserted = False
    for i, line in enumerate(lines):
        out.append(line)
        if not inserted and line.strip() == 'cd "$ROOT"':
            out.extend(
                [
                    "# shellcheck source=_founder_session_gate_entry_v1.sh",
                    'source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"',
                    '_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"',
                ]
            )
            inserted = True
    if not inserted:
        return False
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return True


def wire_all_heavy_gates() -> dict[str, Any]:
    wired: list[str] = []
    skipped: list[str] = []
    for name in sorted(heavy_deny_set()):
        path = SCRIPTS / name
        if not path.is_file():
            skipped.append(name)
            continue
        if GATE_MARKER in path.read_text(encoding="utf-8", errors="replace"):
            skipped.append(name)
            continue
        if wire_gate_into_script(path):
            wired.append(name)
    return {"ok": True, "wired": wired, "skipped": len(skipped)}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Mac pipeline/validator pressure law v1.1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict-audit", action="store_true", help="Fail if heavy scripts lack gate source")
    ap.add_argument("--wire-gates", action="store_true", help="Insert gate into unwired heavy scripts")
    ap.add_argument("--check", metavar="SCRIPT", help="Check if script allowed")
    ap.add_argument("--classify", metavar="SCRIPT", help="Print tier")
    args = ap.parse_args()
    if args.wire_gates:
        row = wire_all_heavy_gates()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"wired={len(row.get('wired') or [])}")
        return 0
    if args.classify:
        print(classify_script(args.classify))
        return 0
    if args.check:
        row = check_script_allowed(script_name=args.check)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("ALLOWED" if row.get("ok") else f"BLOCKED {row.get('reason')}")
        return 0 if row.get("ok") else 2
    side = not args.dry_run
    row = run_pressure_probe(side_effects=side, strict_audit=args.strict_audit)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        status = "OK" if row.get("ok") else "VIOLATIONS"
        print(f"pipeline-validator-pressure · {status} · violations={len(row.get('violations') or [])}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
