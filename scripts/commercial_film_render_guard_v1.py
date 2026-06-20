#!/usr/bin/env python3
"""Commercial film render guard — one render at a time, RAM gate, checkpoint finish.

Rules SSOT: data/commercial-film-render-rules-v1.json

  python3 scripts/commercial_film_render_guard_v1.py machine-check --json
  python3 scripts/commercial_film_render_guard_v1.py status --json
  python3 scripts/commercial_film_render_guard_v1.py acquire --lane witnessbc --json
  python3 scripts/commercial_film_render_guard_v1.py release --lane witnessbc
  python3 scripts/commercial_film_render_guard_v1.py ram-check --json
  python3 scripts/commercial_film_render_guard_v1.py finish --work-dir ~/.sina/... --beats data/....json --json
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
LOCK_PATH = SINA / "commercial-film-render.lock"
META_PATH = SINA / "commercial-film-render-meta-v1.json"
RULES_PATH = ROOT / "data" / "commercial-film-render-rules-v1.json"
METRICS_LOG = SINA / "commercial-film-render-metrics.jsonl"
MAC_GUARD_LIVE = os.environ.get("MAC_HEALTH_LIVE_URL", "http://127.0.0.1:13024/api/mac-health/live")
MAC_GUARD_HEALTH = os.environ.get("MAC_HEALTH_HEALTH_URL", "http://127.0.0.1:13024/health")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_rules() -> dict[str, Any]:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _ram_stats() -> dict[str, float]:
    """Free RAM (GB) on macOS via vm_stat."""
    page_size = 16384  # Apple Silicon default
    try:
        out = subprocess.run(["sysctl", "-n", "hw.pagesize"], capture_output=True, text=True, check=True)
        page_size = int(out.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        pass
    free_pages = 0
    inactive_pages = 0
    speculative_pages = 0
    vm = subprocess.run(["vm_stat"], capture_output=True, text=True, check=True)
    for line in vm.stdout.splitlines():
        if "page size" in line.lower():
            try:
                page_size = int(line.split("of")[-1].strip().split()[0])
            except (ValueError, IndexError):
                pass
        elif line.strip().startswith("Pages free"):
            free_pages = int(line.split(":")[-1].strip().rstrip("."))
        elif line.strip().startswith("Pages inactive"):
            inactive_pages = int(line.split(":")[-1].strip().rstrip("."))
        elif line.strip().startswith("Pages speculative"):
            speculative_pages = int(line.split(":")[-1].strip().rstrip("."))
    reclaimable = free_pages + inactive_pages + speculative_pages
    total_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") if hasattr(os, "sysconf") else 0
    try:
        mem = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, check=True)
        total_bytes = int(mem.stdout.strip())
    except subprocess.CalledProcessError:
        pass
    free_gb = reclaimable * page_size / (1024**3)
    total_gb = total_bytes / (1024**3) if total_bytes else 0.0
    return {
        "free_gb": round(free_gb, 2),
        "total_gb": round(total_gb, 2),
        "used_gb": round(total_gb - free_gb, 2) if total_gb else 0.0,
    }


def log_render_event(event: str, **fields: Any) -> None:
    """Append factory metric row (R14) — safe to call from film compiler."""
    SINA.mkdir(parents=True, exist_ok=True)
    row = {"schema": "commercial-film-render-metric-v1", "at": _now(), "event": event, **fields}
    with METRICS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def _fetch_mac_guard_live() -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(MAC_GUARD_LIVE, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def _fetch_mac_guard_offline_pulse() -> dict[str, Any] | None:
    pulse = SINA / "mac-health" / "live-pulse-v1.json"
    if not pulse.is_file():
        return None
    try:
        return json.loads(pulse.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _local_machine_pressure() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from mac_health_guard import _machine_pressure  # noqa: WPS433

        return _machine_pressure()
    except Exception as exc:
        ram = _ram_stats()
        return {
            "ok": ram["free_gb"] >= 4.0,
            "at": _now(),
            "ram_free_gb": ram["free_gb"],
            "ram_gb": ram["total_gb"],
            "ram_used_pct": round(ram["used_gb"] / ram["total_gb"] * 100, 1) if ram["total_gb"] else 0,
            "cpu_pct": None,
            "fallback": str(exc)[:120],
        }


def machine_snapshot() -> dict[str, Any]:
    """Full machine snapshot — Mac Guard live API preferred (R9)."""
    live = _fetch_mac_guard_live()
    source = "mac_guard_live"
    if live is None:
        live = _fetch_mac_guard_offline_pulse()
        source = "mac_guard_pulse_file"
    mp: dict[str, Any] = {}
    live_status = "OFFLINE"
    score = None
    grade = None
    if live:
        mp = dict(live.get("machine_pressure") or {})
        live_status = str(live.get("live_status") or "UNKNOWN")
        score = live.get("score")
        grade = live.get("grade")
        if not mp:
            mp = _local_machine_pressure()
            source = "mac_health_guard_local"
    else:
        mp = _local_machine_pressure()
        source = "mac_health_guard_local"
    ram = _ram_stats()
    return {
        "at": _now(),
        "source": source,
        "mac_guard_url": MAC_GUARD_LIVE.replace("/api/mac-health/live", "/"),
        "mac_guard_online": source == "mac_guard_live",
        "live_status": live_status,
        "score": score,
        "grade": grade,
        "machine_pressure": mp,
        "ram_vm_stat": ram,
        "founder_line": _founder_machine_line(mp, ram, live_status, score),
    }


def _founder_machine_line(
    mp: dict[str, Any], ram: dict[str, float], live_status: str, score: Any
) -> str:
    cpu = mp.get("cpu_pct")
    rused = mp.get("ram_used_pct")
    rfree = mp.get("ram_free_gb") or ram.get("free_gb")
    gpu = mp.get("gpu_note") or ("thermal" if mp.get("thermal_pressure") else "SoC nominal")
    parts = [
        f"Mac Guard {live_status}",
        f"CPU {cpu}%" if cpu is not None else "CPU n/a",
        f"RAM {rused}% used · {rfree} GB free" if rused is not None else f"RAM {rfree} GB free",
        f"GPU {gpu}",
    ]
    if score is not None:
        parts.append(f"score {score}")
    return " · ".join(parts)


def machine_check(*, fail: bool = False) -> dict[str, Any]:
    rules = _read_rules()
    snap = machine_snapshot()
    mp = snap.get("machine_pressure") or {}
    ram_vm = snap.get("ram_vm_stat") or {}

    r2 = rules.get("rules", {}).get("R2_ram_gate", {})
    r10 = rules.get("rules", {}).get("R10_cpu_gate", {})
    r11 = rules.get("rules", {}).get("R11_disk_gate", {})
    r12 = rules.get("rules", {}).get("R12_gpu_thermal_gate", {})
    r13 = rules.get("rules", {}).get("R13_zombie_gate", {})

    min_free = float(r2.get("min_free_gb", 4.0))
    max_cpu = float(r10.get("max_cpu_pct", 85))
    warn_cpu = float(r10.get("warn_cpu_pct", 70))
    max_disk = float(r11.get("max_disk_pct", 90))
    max_zombies = int(r13.get("max_queue_zombies", 8))
    max_ghosts = int(r13.get("max_ghost_terminals", 3))

    free_gb = float(mp.get("ram_free_gb") or ram_vm.get("free_gb") or 0)
    cpu_pct = float(mp.get("cpu_pct") or 0)
    ram_used_pct = float(mp.get("ram_used_pct") or 0)
    disk_pct = float(mp.get("disk_root_pct") or 0)
    mem_level = str(mp.get("memory_pressure_level") or "normal").lower()
    thermal = bool(mp.get("thermal_pressure"))
    qz = int(mp.get("queue_zombies") or 0)
    ghosts = int(mp.get("ghost_terminals") or 0)
    live_status = str(snap.get("live_status") or "OFFLINE")

    blockers: list[str] = []
    warnings: list[str] = []

    if free_gb < min_free:
        blockers.append(f"RAM free {free_gb} GB < {min_free} GB min")
    if cpu_pct >= max_cpu:
        blockers.append(f"CPU {cpu_pct}% >= {max_cpu}% max")
    elif cpu_pct >= warn_cpu:
        warnings.append(f"CPU {cpu_pct}% high (warn {warn_cpu}%)")
    if ram_used_pct >= 90:
        blockers.append(f"RAM used {ram_used_pct}% >= 90%")
    if disk_pct >= max_disk:
        blockers.append(f"Disk {disk_pct}% >= {max_disk}%")
    if mem_level == "critical":
        blockers.append("memory_pressure critical")
    elif mem_level == "warn":
        warnings.append("memory_pressure warn")
    if thermal and mem_level == "critical":
        blockers.append("SoC thermal + memory critical")
    elif thermal:
        warnings.append(f"SoC thermal active — {mp.get('gpu_note') or 'gpu_note'}")
    if qz >= max_zombies:
        blockers.append(f"queue_zombies {qz} >= {max_zombies}")
    if ghosts >= max_ghosts:
        blockers.append(f"ghost_terminals {ghosts} >= {max_ghosts}")
    if live_status == "SICK":
        warnings.append("Mac Guard LIVE status SICK — consider heal before render")
    if live_status == "OFFLINE":
        warnings.append("Mac Guard offline — using local pressure only; open :13024")

    ok = len(blockers) == 0
    result = {
        "ok": ok,
        "warn": len(warnings) > 0,
        "blockers": blockers,
        "warnings": warnings,
        "snapshot": snap,
        "thresholds": {
            "min_free_gb": min_free,
            "max_cpu_pct": max_cpu,
            "max_disk_pct": max_disk,
            "max_queue_zombies": max_zombies,
        },
        "at": _now(),
    }
    log_render_event("machine_check", ok=ok, blockers=blockers, warnings=warnings, source=snap.get("source"))
    if fail and not ok:
        msg = "; ".join(blockers)
        raise SystemExit(
            f"FAIL: machine gate — {msg}. "
            f"Open Mac Health Guard http://127.0.0.1:13024/ or run machine-check --json"
        )
    return result


def ram_check(*, fail: bool = False) -> dict[str, Any]:
    rules = _read_rules()
    gate = rules.get("rules", {}).get("R2_ram_gate", {})
    min_free = float(gate.get("min_free_gb", 4.0))
    warn_free = float(gate.get("warn_free_gb", 8.0))
    stats = _ram_stats()
    ok = stats["free_gb"] >= min_free
    warn = stats["free_gb"] < warn_free
    result = {
        "ok": ok,
        "warn": warn,
        "min_free_gb": min_free,
        "warn_free_gb": warn_free,
        **stats,
        "at": _now(),
    }
    if fail and not ok:
        raise SystemExit(
            f"FAIL: RAM gate — {stats['free_gb']} GB free < {min_free} GB minimum. "
            "Close apps or wait before starting film render."
        )
    return result


def _read_meta() -> dict[str, Any] | None:
    if not META_PATH.is_file():
        return None
    try:
        return json.loads(META_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _write_meta(meta: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def status() -> dict[str, Any]:
    meta = _read_meta() or {}
    pid = int(meta.get("pid") or 0)
    alive = _pid_alive(pid)
    if pid and not alive:
        meta["stale"] = True
    machine = machine_check()
    ram = ram_check()
    work_dirs = []
    for name in (
        "witnessbc-commercial-film-work-v1",
        "witnessbc-commercial-film-work-v5",
        "commercial-short-film-work-v1",
    ):
        w = SINA / name
        raw = w / "commercial-short-raw.mp4"
        demo = w / "commercial-short-demo.mp4"
        ck = w / "checkpoint.json"
        if w.is_dir():
            work_dirs.append(
                {
                    "path": str(w),
                    "raw": raw.is_file(),
                    "demo": demo.is_file(),
                    "checkpoint": ck.is_file(),
                    "needs_finish": raw.is_file() and not demo.is_file(),
                }
            )
    return {
        "schema": "commercial-film-render-status-v1",
        "at": _now(),
        "lock_file": str(LOCK_PATH),
        "render_active": alive,
        "freeze": freeze_status(),
        "active_probe": probe_active_renders(),
        "meta": meta if meta else None,
        "machine": machine,
        "ram": ram,
        "mac_guard_url": MAC_GUARD_LIVE.replace("/api/mac-health/live", "/"),
        "metrics_log": str(METRICS_LOG),
        "work_dirs": work_dirs,
    }


FREEZE_FLAG = SINA / "commercial-film-render-frozen-v1.flag"


def _render_frozen() -> tuple[bool, str]:
    if not FREEZE_FLAG.is_file():
        return False, ""
    try:
        data = json.loads(FREEZE_FLAG.read_text(encoding="utf-8"))
        return True, str(data.get("reason") or data.get("until") or "critic circle freeze")
    except json.JSONDecodeError:
        return True, FREEZE_FLAG.read_text(encoding="utf-8").strip() or "critic circle freeze"


def freeze_status() -> dict[str, Any]:
    frozen, reason = _render_frozen()
    data: dict[str, Any] = {}
    if FREEZE_FLAG.is_file():
        try:
            data = json.loads(FREEZE_FLAG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "frozen": frozen,
        "reason": reason,
        "path": str(FREEZE_FLAG),
        "until": data.get("until"),
        "next_action": data.get("next_action"),
        "frozen_at": data.get("frozen_at"),
    }


def set_freeze(
    *,
    reason: str,
    until: str = "",
    next_action: str = "",
) -> dict[str, Any]:
    SINA.mkdir(parents=True, exist_ok=True)
    row = {
        "frozen_at": _now(),
        "reason": reason,
        "until": until,
        "next_action": next_action,
    }
    FREEZE_FLAG.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    log_render_event("freeze_set", reason=reason, until=until)
    return {"ok": True, "frozen": True, **row, "path": str(FREEZE_FLAG)}


def assert_render_allowed(*, force: bool = False) -> None:
    frozen, frozen_reason = _render_frozen()
    if frozen and not force:
        raise SystemExit(
            f"FAIL: commercial film render FROZEN — {frozen_reason}\n"
            "  Playwright screenshot capture + ffmpeg compile blocked.\n"
            "  Unfreeze only after Screen Studio master + critic PASS (--force overrides)"
        )


_FILM_PROCESS_MARKERS = (
    "commercial_short_film_v1.py",
    "sourcea_commercial_film_v1.py",
    "witnessbc_commercial_film_v1.py",
    "cinematic-film-factory/compiler.py",
    "commercial_film_render_guard_v1.py finish",
)


def probe_active_renders() -> dict[str, Any]:
    """Detect running commercial film / Playwright capture processes."""
    try:
        out = subprocess.run(
            ["ps", "-axo", "pid,pcpu,rss,command"],
            capture_output=True,
            text=True,
            timeout=5.0,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {"processes": 0, "cpu_sum": 0.0, "rss_mb": 0.0, "pids": [], "active": False}
    rows: list[dict[str, Any]] = []
    cpu_sum = 0.0
    rss_kb = 0
    for line in out.splitlines()[1:]:
        low = line.lower()
        if not any(marker.lower() in low for marker in _FILM_PROCESS_MARKERS):
            if "ffmpeg" in low and "commercial-short-film" not in low and "commercial-film" not in low:
                continue
            elif "ffmpeg" not in low:
                continue
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        try:
            pid = int(parts[0])
            cpu = float(parts[1])
            rss = int(parts[2])
        except ValueError:
            continue
        cpu_sum += cpu
        rss_kb += rss
        rows.append({"pid": pid, "cpu_pct": cpu, "rss_mb": round(rss / 1024, 1), "command": parts[3][:200]})
    return {
        "processes": len(rows),
        "cpu_sum": round(cpu_sum, 1),
        "rss_mb": round(rss_kb / 1024, 1),
        "pids": [r["pid"] for r in rows],
        "rows": rows,
        "active": len(rows) > 0,
        "freeze": freeze_status(),
    }


def kill_active_renders() -> dict[str, Any]:
    """SIGTERM commercial film / ffmpeg capture workers (not Mac Health)."""
    probe = probe_active_renders()
    killed: list[int] = []
    for pid in probe.get("pids") or []:
        if pid <= 1:
            continue
        try:
            os.kill(int(pid), signal.SIGTERM)
            killed.append(int(pid))
        except OSError:
            continue
    if killed:
        time.sleep(0.5)
    still = probe_active_renders()
    return {
        "ok": True,
        "killed": killed,
        "before": probe,
        "after_processes": still.get("processes", 0),
    }


def acquire(*, lane: str, force: bool = False, holder_pid: int | None = None) -> dict[str, Any]:
    rules = _read_rules()
    SINA.mkdir(parents=True, exist_ok=True)
    frozen, frozen_reason = _render_frozen()
    if frozen and not force:
        raise SystemExit(
            f"FAIL: commercial film render FROZEN — {frozen_reason}\n"
            "  Run: python3 scripts/commercial_film_critic_circle_v1.py --json\n"
            "  Unfreeze only after Screen Studio master + critic PASS (--force overrides)"
        )
    machine = machine_check(fail=True)
    meta = _read_meta() or {}
    old_pid = int(meta.get("holder_pid") or meta.get("pid") or 0)
    if old_pid and _pid_alive(old_pid) and not force:
        raise SystemExit(
            f"FAIL: render already running — PID {old_pid} lane={meta.get('lane')} "
            f"(status --json; --force only if stale)"
        )
    if force and old_pid and _pid_alive(old_pid):
        try:
            os.kill(old_pid, signal.SIGTERM)
            time.sleep(1)
        except OSError:
            pass

    holder = holder_pid or os.getpid()
    new_meta = {
        "schema": "commercial-film-render-meta-v1",
        "at": _now(),
        "holder_pid": holder,
        "pid": holder,
        "lane": lane,
        "phase": "starting",
        "rules": str(RULES_PATH.relative_to(ROOT)),
    }
    _write_meta(new_meta)
    if LOCK_PATH.is_file():
        try:
            LOCK_PATH.unlink()
        except OSError:
            pass
    LOCK_PATH.write_text(json.dumps(new_meta) + "\n", encoding="utf-8")
    log_render_event("acquire", lane=lane, holder_pid=holder, machine=machine.get("snapshot", {}).get("founder_line"))
    return {"ok": True, "acquired": True, "lane": lane, "holder_pid": holder, "machine": machine, "ram": machine.get("snapshot", {}).get("ram_vm_stat")}


def release(*, lane: str | None = None) -> dict[str, Any]:
    meta = _read_meta() or {}
    if lane and meta.get("lane") and meta.get("lane") != lane:
        return {"ok": True, "skipped": True, "reason": "lane mismatch"}
    if LOCK_PATH.is_file():
        try:
            LOCK_PATH.unlink()
        except OSError:
            pass
    if META_PATH.is_file():
        try:
            finished = dict(meta)
            finished["released_at"] = _now()
            finished["finished"] = True
            META_PATH.write_text(json.dumps(finished, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass
    log_render_event("release", lane=lane or meta.get("lane"))
    return {"ok": True, "released": True}


def finish(*, work_dir: Path, beats: Path, skip_publish: bool = False) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from commercial_short_film_v1 import finish_from_checkpoint  # noqa: WPS433

    if not work_dir.is_dir():
        raise SystemExit(f"FAIL: work dir missing: {work_dir}")
    raw = work_dir / "commercial-short-raw.mp4"
    if not raw.is_file():
        raise SystemExit(f"FAIL: no raw mp4 in {work_dir} — full render required")
    machine_check(fail=True)
    return finish_from_checkpoint(beats_path=beats, work=work_dir, skip_publish=skip_publish)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status")
    p_status.add_argument("--json", action="store_true")

    p_acquire = sub.add_parser("acquire")
    p_acquire.add_argument("--lane", required=True, choices=["witnessbc", "sourcea", "avatar", "other"])
    p_acquire.add_argument("--holder-pid", type=int, default=0)
    p_acquire.add_argument("--force", action="store_true")
    p_acquire.add_argument("--json", action="store_true")

    p_release = sub.add_parser("release")
    p_release.add_argument("--lane", default="")
    p_release.add_argument("--json", action="store_true")

    p_ram = sub.add_parser("ram-check")
    p_ram.add_argument("--json", action="store_true")

    p_machine = sub.add_parser("machine-check")
    p_machine.add_argument("--fail", action="store_true", help="Exit 1 if gate blocked")
    p_machine.add_argument("--json", action="store_true")

    p_finish = sub.add_parser("finish")
    p_finish.add_argument("--work-dir", type=Path, required=True)
    p_finish.add_argument("--beats", type=Path, required=True)
    p_finish.add_argument("--skip-publish", action="store_true")
    p_finish.add_argument("--json", action="store_true")

    p_freeze = sub.add_parser("freeze", help="Set render freeze flag (blocks Playwright capture)")
    p_freeze.add_argument("--reason", required=True)
    p_freeze.add_argument("--until", default="")
    p_freeze.add_argument("--next-action", default="")
    p_freeze.add_argument("--json", action="store_true")

    p_probe = sub.add_parser("probe", help="Probe active film render processes")
    p_probe.add_argument("--json", action="store_true")

    p_kill = sub.add_parser("kill-active", help="SIGTERM active film render processes")
    p_kill.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.cmd == "status":
        out = status()
    elif args.cmd == "acquire":
        out = acquire(lane=args.lane, force=args.force, holder_pid=args.holder_pid or None)
    elif args.cmd == "release":
        out = release(lane=args.lane or None)
    elif args.cmd == "ram-check":
        out = ram_check()
    elif args.cmd == "machine-check":
        out = machine_check(fail=args.fail)
    elif args.cmd == "finish":
        beats = args.beats if args.beats.is_absolute() else ROOT / args.beats
        out = finish(work_dir=args.work_dir.expanduser(), beats=beats, skip_publish=args.skip_publish)
    elif args.cmd == "freeze":
        out = set_freeze(reason=args.reason, until=args.until, next_action=args.next_action)
    elif args.cmd == "probe":
        out = probe_active_renders()
    elif args.cmd == "kill-active":
        out = kill_active_renders()
    else:
        return 1

    if getattr(args, "json", False):
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
