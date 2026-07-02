#!/usr/bin/env python3
"""Brain session self-healing startup — mandatory before surfacing to ASF.

Law: brain-os/laws/BRAIN_SELF_HEAL_STARTUP_LOCKED_v1.md
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-self-heal-startup-v1.json"
HUB_HEALTH = "http://127.0.0.1:13020/health"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
QUEUE_REPO = ROOT / "os/plan-library/sourcea-1000/prompts/healthy-queue-30-active.json"
QUEUE_PACK = ROOT / "brain-os/plan-registry/healthy-prompt-pack-v1/healthy-queue-30-active.json"
POINTER = SINA / "next-execution-pointer-v1.json"
REGISTRY = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
FOUNDER_READY = "System ready. AUTO-RUN active — worker batches spawn automatically (no tap)."


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_bash(script: str, *, timeout: int = 120) -> dict:
    path = SCRIPTS / script
    if not path.is_file():
        return {"ok": False, "error": f"missing {script}"}
    try:
        proc = subprocess.run(
            ["bash", str(path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": (proc.stdout or "")[-2000:],
            "stderr": (proc.stderr or "")[-1000:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_hub(*, restart: bool = True) -> dict:
    def _probe() -> bool:
        try:
            with urllib.request.urlopen(HUB_HEALTH, timeout=3) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return bool(body.get("ok"))
        except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
            return False

    if _probe():
        return {"ok": True, "step": "hub_health", "restarted": False}

    if not restart:
        return {"ok": False, "step": "hub_health", "error": "HUB_DOWN", "p0": True}

    plist = Path.home() / "Library/LaunchAgents/com.sourcea.hub.plist"
    label = "com.sourcea.hub"
    domain = f"gui/{os.getuid()}"
    try:
        if plist.is_file():
            subprocess.run(
                ["launchctl", "kickstart", "-k", f"{domain}/{label}"],
                capture_output=True,
                timeout=15,
                check=False,
            )
        install = SCRIPTS / "install-hub-launchd-v1.sh"
        if install.is_file():
            subprocess.run(["bash", str(install)], cwd=str(ROOT), capture_output=True, timeout=90, check=False)
        elif not plist.is_file():
            subprocess.Popen(
                [sys.executable, str(SCRIPTS / "sina-command-server.py")],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        time.sleep(2.0)
    except Exception as exc:
        return {"ok": False, "step": "hub_restart", "error": str(exc), "p0": True}

    if _probe():
        return {"ok": True, "step": "hub_health", "restarted": True}

    return {
        "ok": False,
        "step": "hub_health",
        "error": "HUB_DOWN_AFTER_RESTART",
        "p0": True,
        "hint": "Hub failed to bind :13020 — check port conflict",
    }


def run_validators(*, autfix: bool = True) -> dict:
    rows = {}
    for name in ("validate-file-storage-v1.sh", "validate-master-operating-tracker-v1.sh"):
        rows[name] = _run_bash(name)

    if all(r.get("ok") for r in rows.values()):
        return {"ok": True, "validators": rows}

    if autfix:
        # P1/P2 autonomous fixes: sync pointer + tracker stamp
        try:
            sys.path.insert(0, str(SCRIPTS))
            try:
                from execution_event_log_v1 import ensure_daily_events_file  # noqa: WPS433

                ensure_daily_events_file(actor="brain_self_heal_startup_v1")
            except Exception:
                pass
            subprocess.run(
                [sys.executable, str(SCRIPTS / "sync_next_execution_pointer_v1.py")],
                cwd=str(ROOT),
                capture_output=True,
                timeout=60,
                check=False,
            )
            sys.path.insert(0, str(SCRIPTS))
            try:
                from authority_enforce_p1_lib import sync_tracker_executive_pointer  # noqa: WPS433

                sync_tracker_executive_pointer()
            except Exception:
                pass
            try:
                from active_now_v1 import sync_active_now_from_queue  # noqa: WPS433

                sync_active_now_from_queue()
            except Exception:
                pass
            _run_bash("validate-master-operating-tracker-v1.sh")
            rows["validate-master-operating-tracker-v1.sh"] = _run_bash(
                "validate-master-operating-tracker-v1.sh"
            )
            rows["validate-file-storage-v1.sh"] = _run_bash("validate-file-storage-v1.sh")
        except Exception as exc:
            rows["autfix_error"] = str(exc)

    ok = all(rows.get(n, {}).get("ok") for n in ("validate-file-storage-v1.sh", "validate-master-operating-tracker-v1.sh"))
    return {
        "ok": ok,
        "validators": rows,
        "p0": not ok,
        "severity": "P1" if not ok else None,
    }


def check_queue(*, rebuild: bool = True) -> dict:
    def _queue_ok(path: Path) -> bool:
        if not path.is_file():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data.get("queue") or []
            return len(items) > 0
        except (OSError, json.JSONDecodeError):
            return False

    if not _queue_ok(QUEUE_HOME) and rebuild:
        sys.path.insert(0, str(SCRIPTS))
        from healthy_queue_ssot_lib import is_commercial_default_queue  # noqa: WPS433

        for src in (QUEUE_REPO, QUEUE_PACK):
            if not _queue_ok(src):
                continue
            try:
                data = json.loads(src.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if is_commercial_default_queue(data):
                continue
            QUEUE_HOME.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, QUEUE_HOME)
            break
        if not _queue_ok(QUEUE_HOME):
            gen = SCRIPTS / "generate-healthy-prompt-pack-v1.py"
            if gen.is_file():
                subprocess.run(
                    [sys.executable, str(gen)],
                    cwd=str(ROOT),
                    capture_output=True,
                    timeout=120,
                    check=False,
                )
                if _queue_ok(QUEUE_PACK):
                    shutil.copy2(QUEUE_PACK, QUEUE_HOME)

    queue_ok = _queue_ok(QUEUE_HOME)
    pointer_ok = POINTER.is_file()
    pointer_sa = None
    if pointer_ok:
        try:
            pointer_sa = json.loads(POINTER.read_text(encoding="utf-8")).get("next_sa")
        except (OSError, json.JSONDecodeError):
            pointer_ok = False

    if not pointer_ok and REGISTRY.is_file():
        subprocess.run(
            [sys.executable, str(SCRIPTS / "sync_next_execution_pointer_v1.py")],
            cwd=str(ROOT),
            capture_output=True,
            timeout=60,
            check=False,
        )
        pointer_ok = POINTER.is_file()
        if pointer_ok:
            try:
                pointer_sa = json.loads(POINTER.read_text(encoding="utf-8")).get("next_sa")
            except (OSError, json.JSONDecodeError):
                pointer_ok = False

    ok = queue_ok and pointer_ok and bool(pointer_sa)
    return {
        "ok": ok,
        "queue_populated": queue_ok,
        "queue_path": str(QUEUE_HOME),
        "pointer_ok": pointer_ok,
        "next_sa": pointer_sa,
        "registry": str(REGISTRY) if REGISTRY.is_file() else None,
        "p0": not ok,
    }


def window_preflight_check() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from cursor_window_preflight_v1 import run_cursor_window_preflight  # noqa: WPS433

    row = run_cursor_window_preflight(caller="brain_self_heal_startup", sleep_sec=1.0)
    return {**row, "ok": bool(row.get("ok"))}


def run_self_heal_startup(*, caller: str = "brain") -> dict:
    if os.environ.get("SINA_BRAIN_FAST", "").strip().lower() in ("1", "true", "yes"):
        sys.path.insert(0, str(SCRIPTS))
        from brain_fast_startup_v1 import run_fast_brain  # noqa: WPS433

        fast = run_fast_brain(caller=caller)
        return {
            "schema": "brain-self-heal-startup-v1",
            "at": fast.get("at") or _now(),
            "caller": caller,
            "ok": bool(fast.get("ok")),
            "founder_ready": bool(fast.get("ok")),
            "founder_message": (
                "System ready. FAST_BRAIN active — Worker INBOX route only."
                if fast.get("ok")
                else None
            ),
            "p0_blockers": [] if fast.get("ok") else ["FAST_BRAIN_FAIL"],
            "steps": fast.get("steps") or [],
            "fast_brain": True,
            "elapsed_ms": fast.get("elapsed_ms"),
            "brain_action": fast.get("brain_action"),
        }

    steps: list[dict] = []
    p0_blockers: list[str] = []

    hub = check_hub(restart=True)
    steps.append({"id": "check_hub", **hub})
    if not hub.get("ok"):
        p0_blockers.append(f"HUB: {hub.get('error')}")

    if p0_blockers:
        out = _finalize(steps, p0_blockers, founder_ready=False, caller=caller)
        return out

    validators = run_validators(autfix=True)
    steps.append({"id": "run_validators", **validators})
    if not validators.get("ok"):
        p0_blockers.append("VALIDATORS: file-storage or master-tracker FAIL after autfix")

    queue = check_queue(rebuild=True)
    steps.append({"id": "check_queue", **queue})
    if not queue.get("ok"):
        p0_blockers.append("QUEUE: healthy-queue or next-execution-pointer missing")

    preflight = window_preflight_check()
    steps.append({"id": "window_preflight", **preflight})
    if not preflight.get("ok"):
        p0_blockers.append(f"PREFLIGHT: {preflight.get('error')}")

    founder_ready = not p0_blockers
    return _finalize(steps, p0_blockers, founder_ready=founder_ready, caller=caller)


def _finalize(steps: list, p0_blockers: list, *, founder_ready: bool, caller: str) -> dict:
    row = {
        "schema": "brain-self-heal-startup-v1",
        "at": _now(),
        "caller": caller,
        "ok": founder_ready,
        "founder_ready": founder_ready,
        "founder_message": FOUNDER_READY if founder_ready else None,
        "p0_blockers": p0_blockers,
        "steps": steps,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Brain self-healing startup sequence")
    p.add_argument("--caller", default="cli")
    p.add_argument("--json-only", action="store_true", help="Stdout JSON only (for shell gates)")
    args = p.parse_args()
    row = run_self_heal_startup(caller=args.caller)
    print(json.dumps(row, indent=2))
    if args.json_only:
        return 0 if row.get("ok") else 1
    if row.get("founder_ready"):
        print(f"\n{FOUNDER_READY}")
    elif row.get("p0_blockers"):
        print("\nP0 BLOCKERS (ASF decision required):")
        for b in row["p0_blockers"]:
            print(f"  - {b}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
