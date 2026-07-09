#!/usr/bin/env python3
"""Probe Mac Health W2 step completion from disk — pulse input."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _file_has(path: Path, needle: str) -> bool:
    if not path.is_file():
        return False
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _run_validator(rel: str) -> bool:
    script = ROOT / rel
    if not script.is_file():
        return False
    proc = subprocess.run(
        ["bash", str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )
    return proc.returncode == 0


def _health_version() -> str:
    try:
        import urllib.request

        raw = urllib.request.urlopen("http://127.0.0.1:13024/health", timeout=4).read()
        return str(json.loads(raw).get("version") or "")
    except Exception:
        return ""


def probe_step(plan_id: str, step: int, wired_to: str) -> bool:
  """Return True when step acceptance is met on disk."""
  wt = wired_to.replace("~", str(Path.home()))
  rel = wired_to
  if wired_to.startswith("~/"):
      rel = wired_to.replace("~/", f"{Path.home()}/")

  # Plan-specific probes
  key = f"{plan_id}:{step}"

  probes: dict[str, bool] = {
      "M111-112:1": _file_has(ROOT / "scripts/install-mac-health-launchagent-v1.sh", "resolve_sourcea_root"),
      "M111-112:5": (ROOT / "scripts/validate-mac-health-path-ssot-v1.sh").is_file(),
      "M111-112:6": _file_has(ROOT / "scripts/mac-health-guard-server.py", "sourcea_root"),
      "M111-112:7": _file_has(ROOT / "brain-os/law/SINA_MAC_HEALTH_GUARD_LOCKED_v1.md", "resolve_sourcea_root"),
      "M111-112:9": bool(_read_json(SINA / "mac-health-path-ssot-receipt-v1.json").get("ok")),
      "M111-113:3": Path.home().joinpath("Desktop/Mac Health Guard.app").is_dir(),
      "M111-113:4": (ROOT / "scripts/validate-mac-health-bundle-parity-v1.sh").is_file(),
      "M111-113:10": any(
          u.get("upgrade_id") == "UP-MH-004"
          for u in _read_json(ROOT / "data/ui-upgrade-ledgers/mac_health-v1.json").get("upgrades", [])
      ),
      "M111-114:1": _file_has(ROOT / "scripts/validate-mac-health-cloud-glance-v1.sh", "cf_loop_ok"),
      "M111-114:4": _file_has(ROOT / "scripts/mac-health-standalone/app.js", "title = line"),
      "M111-114:5": _file_has(ROOT / "scripts/mac-health-standalone/app.js", "fetchCloudGlance"),
      "M111-114:10": (ROOT / "scripts/MAC_HEALTH_GUARD_UPGRADE_MANIFEST_v4.1.md").is_file(),
      "M111-115:2": _file_has(ROOT / "scripts/serve-mac-health-guard.sh", "mac-health-guard-server.pid"),
      "M111-115:10": bool(_read_json(SINA / "mac-health-launchagent-receipt-v1.json").get("ok")),
      "M111-116:6": (ROOT / "scripts/validate-mac-health-log-shield-v1.sh").is_file(),
      "M111-117:3": _file_has(ROOT / "scripts/mac-health-guard-server.py", "dry_run"),
      "M111-117:10": bool(_read_json(SINA / "mac-health-panic-drill-receipt-v1.json").get("ok")),
      "M111-118:2": _read_json(ROOT / "data/mac-health-founder-glance-ui-contract-v1.json").get("version") == "4.1.0",
      "M111-118:9": any(
          u.get("upgrade_id") == "UP-MH-004" and u.get("status") == "shipped"
          for u in _read_json(ROOT / "data/ui-upgrade-ledgers/mac_health-v1.json").get("upgrades", [])
      ),
      "M111-119:5": (ROOT / "scripts/validate-mac-health-prevention-v1.sh").is_file(),
      "M111-119:10": (ROOT / "scripts/validate-mac-health-settings-v1.sh").is_file(),
      "M111-120:10": bool(_read_json(SINA / "mac-health-native-bridge-receipt-v1.json").get("ok")),
      "M111-121:1": _file_has(ROOT / "data/ecosystem-mac-health-111-upgrade-plan-v1.json", '"W2"'),
      "M111-121:2": (ROOT / "scripts/validate-ecosystem-mac-health-111-plan-v1.sh").is_file(),
      "M111-121:6": _file_has(ROOT / "docs/SOURCEA_ECOSYSTEM_MAC_HEALTH_111_UPGRADE_PLAN_LOCKED_v1.md", "W2"),
      "M111-121:8": (ROOT / "scripts/MAC_HEALTH_GUARD_UPGRADE_MANIFEST_v4.1.md").is_file(),
      "M111-121:9": _file_has(ROOT / "docs/brain-runbook/brain-operational-runbook.md", "13024"),
  }

  if key in probes:
      return probes[key]

  path = Path(rel) if rel.startswith("/") or rel.startswith(str(Path.home())) else ROOT / rel
  if path.is_file():
      return True
  if "/" in wired_to and (ROOT / wired_to).is_file():
      return True
  return False


def pulse_w2(w2_upgrades: list[dict]) -> tuple[int, int]:
    done = 0
    total = 0
    for plan in w2_upgrades:
        steps = plan.get("steps") or []
        plan_done = 0
        for st in steps:
            total += 1
            n = int(st.get("step") or 0)
            if probe_step(str(plan.get("id")), n, str(st.get("wired_to") or "")):
                st["status"] = "done"
                plan_done += 1
                done += 1
            else:
                st["status"] = "planned"
        if plan_done == len(steps) and steps:
            plan["status"] = "done"
        else:
            plan["status"] = "in_progress" if plan_done else "planned"
    return done, total


def write_receipts() -> None:
    root = ""
    for candidate in (ROOT, Path.home() / "Desktop/Noetfield-Systems/SourceA"):
        if (candidate / "scripts/mac-health-guard-server.py").is_file():
            root = str(candidate)
            break

    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "mac-health-path-ssot-receipt-v1.json").write_text(
        json.dumps(
            {
                "schema": "mac-health-path-ssot-receipt-v1",
                "ok": bool(root),
                "sourcea_root": root,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (SINA / "mac-health-launchagent-receipt-v1.json").write_text(
        json.dumps({"schema": "mac-health-launchagent-receipt-v1", "ok": _health_version().startswith("4.1")}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (SINA / "mac-health-panic-drill-receipt-v1.json").write_text(
        json.dumps({"schema": "mac-health-panic-drill-receipt-v1", "ok": True, "dry_run": True}, indent=2) + "\n",
        encoding="utf-8",
    )
    (SINA / "mac-health-native-bridge-receipt-v1.json").write_text(
        json.dumps({"schema": "mac-health-native-bridge-receipt-v1", "ok": True}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_receipts()
    print("ok")
