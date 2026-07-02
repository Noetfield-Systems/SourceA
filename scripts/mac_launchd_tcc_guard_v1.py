"""Mac launchd + Desktop TCC guard — detect block, FDA hint, nohup fallback."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "mac-launchd-tcc-receipt-v1.json"

PROTECTED_SEGMENTS = ("/Desktop/", "/Documents/", "/Downloads/")
TCC_ERR_MARKERS = (
    "operation not permitted",
    "permissionerror",
    "tcc",
    "sandbox restriction",
    "deny(1) file-read-data",
)

DEFAULT_PYTHON = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def is_protected_path(path: str | Path) -> bool:
    p = str(path).replace("\\", "/")
    return any(seg in p for seg in PROTECTED_SEGMENTS)


def fda_binaries() -> list[str]:
    bins: list[str] = []
    py = DEFAULT_PYTHON if Path(DEFAULT_PYTHON).is_file() else ""
    if py:
        bins.append(py)
    mono = _read_json(SINA / "mono-root-v1.json").get("root") or str(Path.home() / "Desktop/SinaaiMonoRepo")
    venv_py = Path(str(mono)) / "SinaaiRuntime/.venv/bin/python3"
    if venv_py.is_file():
        bins.append(str(venv_py))
    return sorted(set(bins))


def err_log_signals_tcc(*paths: Path) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            tail = path.read_text(encoding="utf-8", errors="replace")[-8000:].lower()
        except OSError:
            continue
        for marker in TCC_ERR_MARKERS:
            if marker in tail:
                hits.append(f"{path.name}:{marker}")
    return hits


def launchd_loaded(label: str) -> bool:
    uid = os.getuid()
    try:
        subprocess.run(
            ["launchctl", "print", f"gui/{uid}/{label}"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def hub_health_ok(port: int = 13020) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def assess(*, sourcea_root: Path | None = None) -> dict[str, Any]:
    root = sourcea_root or Path(_read_json(SINA / "sourcea-root-v1.json").get("root") or ROOT)
    mac_law = Path(_read_json(SINA / "mac-law-root-v1.json").get("root") or Path.home() / "Desktop/MacLaw")
    desktop_repo = is_protected_path(root) or is_protected_path(mac_law)
    tcc_hits = err_log_signals_tcc(
        SINA / "command-server-launchd.err",
        SINA / "mac-law-launchd.err",
        SINA / "routing-panel-launchd.err",
    )
    hub_label = "com.sourcea.hub"
    return {
        "ok": True,
        "schema": "mac-launchd-tcc-assess-v1",
        "at": _now(),
        "sourcea_root": str(root),
        "desktop_repo": desktop_repo,
        "launchd_hub_loaded": launchd_loaded(hub_label),
        "hub_health_ok": hub_health_ok(),
        "tcc_err_hits": tcc_hits,
        "likely_tcc_block": bool(desktop_repo and (tcc_hits or (not hub_health_ok() and not launchd_loaded(hub_label)))),
        "fda_binaries": fda_binaries(),
        "fix_one_tap": "bash ~/Desktop/SourceA/scripts/open-mac-launchd-fda-v1.sh",
        "fallback_boot": "bash ~/Desktop/SourceA/scripts/serve-sina-command.sh",
        "for_founder": {
            "show_this": (
                "Desktop repo + launchd needs Full Disk Access on Python 3.12 — "
                "or use nohup fallback (Hub still starts from Terminal)."
            ),
        },
    }


def sync_root_pointers(*, sourcea_root: Path | None = None) -> dict[str, Any]:
    root = sourcea_root or ROOT
    mono_candidates = [
        Path.home() / "Desktop/SinaaiMonoRepo",
        Path.home() / "Desktop/Noetfield/SinaaiMonoRepo",
    ]
    mono = next((p for p in mono_candidates if (p / "routing-panel/server.py").is_file()), mono_candidates[0])
    mac_law = Path.home() / "Desktop/MacLaw"
    SINA.mkdir(parents=True, exist_ok=True)
    wrappers_src = root / "scripts/launchd-wrappers"
    mapping = {
        "start-sourcea-hub-launchd.sh": "start-sourcea-hub-launchd.sh",
        "start-mac-law-launchd.sh": "start-mac-law-launchd.sh",
        "start-routing-panel-launchd.sh": "start-routing-panel-launchd.sh",
        "sourcea-mac-v1.sh": "sourcea-mac-v1.sh",
    }
    installed: list[str] = []
    for src_name, dst_name in mapping.items():
        src = wrappers_src / src_name
        dst = SINA / dst_name
        if src.is_file():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            dst.chmod(0o755)
            installed.append(str(dst))
    _write_json(SINA / "sourcea-root-v1.json", {"schema": "sourcea-root-v1", "root": str(root), "at": _now()})
    _write_json(SINA / "mac-law-root-v1.json", {"schema": "mac-law-root-v1", "root": str(mac_law), "at": _now()})
    _write_json(SINA / "mono-root-v1.json", {"schema": "mono-root-v1", "root": str(mono), "at": _now()})
    return {"ok": True, "installed_wrappers": installed, "sourcea_root": str(root)}


def boot_hub_fallback(*, sourcea_root: Path | None = None) -> dict[str, Any]:
    root = sourcea_root or ROOT
    sync_root_pointers(sourcea_root=root)
    assess_row = assess(sourcea_root=root)
    if assess_row.get("hub_health_ok"):
        row = {**assess_row, "boot": "already_healthy", "ok": True}
        _write_json(RECEIPT, row)
        return row

    skip_launchd = bool(
        assess_row.get("likely_tcc_block") or os.environ.get("SINA_LAUNCHD_TCC_FALLBACK") == "1"
    )
    boot_mode = "nohup_fallback" if skip_launchd else "launchd"

    if not skip_launchd:
        proc = subprocess.run(
            ["bash", str(root / "scripts/install-hub-launchd-v1.sh")],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if hub_health_ok():
            row = {
                **assess_row,
                "ok": True,
                "boot": "launchd",
                "returncode": proc.returncode,
                "stdout_tail": (proc.stdout or "")[-1200:],
            }
            _write_json(RECEIPT, row)
            return row
        boot_mode = "nohup_fallback"

    proc = subprocess.run(
        ["bash", str(root / "scripts/serve-sina-command.sh")],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    ok = hub_health_ok()
    row = {
        **assess_row,
        "ok": ok,
        "boot": boot_mode,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-800:],
        "for_founder": {
            "show_this": (
                f"Hub {'UP' if ok else 'DOWN'} via {boot_mode} · "
                "For persistent launchd on Desktop repo: grant Full Disk Access to Python 3.12 — "
                "bash scripts/open-mac-launchd-fda-v1.sh"
            ),
        },
    }
    _write_json(RECEIPT, row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac launchd TCC guard")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--sync-wrappers", action="store_true")
    ap.add_argument("--boot-hub", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.sync_wrappers:
        row = sync_root_pointers()
    elif args.boot_hub:
        row = boot_hub_fallback()
    else:
        row = assess()
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
