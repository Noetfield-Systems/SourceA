#!/usr/bin/env python3
"""Mac performance snapshot — RAM, CPU, GPU, thermal, disk, lag suspects. Local only."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path.home() / ".sina" / "mac-health"
OUT_JSON = OUT_DIR / "last-performance-snapshot.json"


def run(cmd: list[str], *, timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return f"ERROR: {e}"


def sysctl(key: str) -> str:
    return run(["sysctl", "-n", key]).strip()


def parse_vm_stat() -> dict:
    raw = run(["vm_stat"])
    page = 4096
    try:
        page = int(sysctl("hw.pagesize"))
    except ValueError:
        pass
    stats: dict[str, int] = {}
    for line in raw.splitlines():
        m = re.match(r"^([^:]+):\s+([\d.]+)", line.strip())
        if m:
            stats[m.group(1).strip()] = int(float(m.group(2)))
    free = stats.get("Pages free", 0) * page
    active = stats.get("Pages active", 0) * page
    inactive = stats.get("Pages inactive", 0) * page
    wired = stats.get("Pages wired down", 0) * page
    compressed = stats.get("Pages occupied by compressor", 0) * page
    swapins = stats.get("Swapins", 0)
    swapouts = stats.get("Swapouts", 0)
    return {
        "page_bytes": page,
        "free_mb": round(free / 1024 / 1024, 1),
        "active_mb": round(active / 1024 / 1024, 1),
        "inactive_mb": round(inactive / 1024 / 1024, 1),
        "wired_mb": round(wired / 1024 / 1024, 1),
        "compressed_mb": round(compressed / 1024 / 1024, 1),
        "swapins": swapins,
        "swapouts": swapouts,
    }


def memory_pressure() -> dict:
    raw = run(["memory_pressure"])
    level = "unknown"
    for line in raw.splitlines():
        if "System-wide memory free percentage" in line:
            level = line.strip()
        if re.search(r"\b(normal|warn|critical)\b", line, re.I):
            level = line.strip()
    return {"raw": raw.strip()[:500], "summary": level}


def parse_top_cpu_busy() -> dict[str, float]:
    """Activity Monitor-style system CPU busy % (100 − idle) from top."""
    raw = run(["top", "-l", "1", "-n", "0", "-s", "0"], timeout=6)
    m = re.search(
        r"CPU usage:\s+([\d.]+)% user,\s+([\d.]+)% sys,\s+([\d.]+)% idle",
        raw,
    )
    if not m:
        return {}
    user = float(m.group(1))
    sys_p = float(m.group(2))
    idle = float(m.group(3))
    busy = round(max(0.0, min(100.0, 100.0 - idle)), 1)
    return {
        "system_cpu_busy_pct": busy,
        "cpu_user_pct": round(user, 1),
        "cpu_sys_pct": round(sys_p, 1),
        "cpu_idle_pct": round(idle, 1),
    }


def cpu_snapshot() -> dict:
    total_ram = int(sysctl("hw.memsize"))
    cores = int(sysctl("hw.ncpu") or "0")
    load = run(["sysctl", "-n", "vm.loadavg"]).strip()
    top = run(["ps", "-axo", "pid,pcpu,pmem,rss,comm"])
    rows: list[dict] = []
    for line in top.splitlines()[1:]:
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        pid, pcpu, pmem, rss, comm = parts
        try:
            rows.append(
                {
                    "pid": int(pid),
                    "cpu_pct": float(pcpu),
                    "mem_pct": float(pmem),
                    "rss_mb": round(int(rss) / 1024, 1),
                    "comm": comm.strip()[:120],
                }
            )
        except ValueError:
            continue
    by_cpu = sorted(rows, key=lambda x: x["cpu_pct"], reverse=True)[:12]
    by_ram = sorted(rows, key=lambda x: x["rss_mb"], reverse=True)[:15]
    return {
        "cores": cores,
        "loadavg": load,
        "top_cpu": by_cpu,
        "top_ram": by_ram,
        "total_ram_gb": round(total_ram / 1024 / 1024 / 1024, 1),
    }


def _classify_app(comm: str, full_cmd: str) -> str:
    text = f"{comm} {full_cmd}"
    rules = [
        ("Legacy hub", re.compile(r"sina-command-server", re.I)),
        ("Cursor", re.compile(r"Cursor", re.I)),
        ("Chrome", re.compile(r"Google Chrome|Chrome Helper", re.I)),
        ("Safari", re.compile(r"Safari|com\.apple\.WebKit", re.I)),
        ("Claude", re.compile(r"Claude", re.I)),
        ("Python (other)", re.compile(r"Python|python3", re.I)),
        ("WindowServer", re.compile(r"WindowServer", re.I)),
        ("CodeLLM / ML", re.compile(r"mlhostd|embedding|LanguageModel", re.I)),
        ("Ollama", re.compile(r"ollama|Ollama", re.I)),
    ]
    for name, rx in rules:
        if rx.search(text):
            return name
    return "Other"


def group_apps(processes: list[dict]) -> list[dict]:
    buckets: dict[str, dict] = defaultdict(lambda: {"rss_mb": 0.0, "cpu_pct": 0.0, "count": 0})
    full_cmds = run(["ps", "-axo", "rss,command"])
    cmd_by_rss: list[tuple[int, str]] = []
    for line in full_cmds.splitlines()[1:]:
        parts = line.split(None, 1)
        if len(parts) == 2:
            try:
                cmd_by_rss.append((int(parts[0]), parts[1]))
            except ValueError:
                pass

    def full_for(comm: str, rss_mb: float) -> str:
        target = int(rss_mb * 1024)
        for rss, cmd in cmd_by_rss:
            if abs(rss - target) < 64 and comm[:20] in cmd:
                return cmd
        return comm

    for p in processes:
        comm = p.get("comm", "")
        full = full_for(comm, p.get("rss_mb", 0))
        matched = _classify_app(comm, full)
        buckets[matched]["rss_mb"] += p.get("rss_mb", 0)
        buckets[matched]["cpu_pct"] += p.get("cpu_pct", 0)
        buckets[matched]["count"] += 1
    out = [
        {
            "app": k,
            "rss_mb": round(v["rss_mb"], 1),
            "rss_gb": round(v["rss_mb"] / 1024, 2),
            "cpu_pct": round(v["cpu_pct"], 1),
            "processes": v["count"],
        }
        for k, v in buckets.items()
    ]
    return sorted(out, key=lambda x: x["rss_mb"], reverse=True)


def gpu_snapshot() -> dict:
    displays = run(["system_profiler", "SPDisplaysDataType"])
    chips: list[str] = []
    for line in displays.splitlines():
        if "Chipset Model" in line or "Model:" in line:
            chips.append(line.strip())
    ioreg = run(["ioreg", "-r", "-d", "1", "-c", "IOAccelerator"])
    gpu_notes = []
    if "Apple" in ioreg or "AGX" in ioreg:
        gpu_notes.append("Apple Silicon GPU (AGX) present")
    therm = run(["pmset", "-g", "therm"])
    return {
        "displays": chips[:6],
        "gpu_note": gpu_notes or ["See system_profiler SPDisplaysDataType"],
        "thermal": therm.strip()[:400],
    }


def disk_snapshot() -> dict:
    df = run(["df", "-h", "/"])
    lines = [ln for ln in df.splitlines() if ln.startswith("/dev") or ln.startswith("map")]
    free_gb = None
    used_pct = None
    if lines:
        parts = lines[0].split()
        if len(parts) >= 5:
            used_pct = parts[4]
            if len(parts) >= 4:
                try:
                    free_gb = parts[3]
                except IndexError:
                    pass
    return {"root_volume": lines[0] if lines else df.strip(), "used_pct": used_pct, "avail": free_gb}


def thermal_and_power() -> dict:
    therm = run(["pmset", "-g", "therm"])
    batt = run(["pmset", "-g", "batt"])
    return {"therm": therm.strip(), "power": batt.strip()[:300]}


def lag_verdict(groups: list[dict], vm: dict, cpu: dict) -> dict:
    cursor_gb = next((g["rss_gb"] for g in groups if g["app"] == "Cursor"), 0)
    sina_mb = next((g["rss_mb"] for g in groups if g["app"] == "Legacy hub"), 0)
    swap_active = vm.get("swapouts", 0) > 0 or vm.get("swapins", 0) > 1000
    load_parts = (cpu.get("loadavg") or "0 0 0").split()
    try:
        load1 = float(load_parts[0].strip("{}"))
    except (ValueError, IndexError):
        load1 = 0.0
    cores = cpu.get("cores") or 8
    pressure = "low"
    reasons: list[str] = []
    if cursor_gb >= 8:
        pressure = "high"
        reasons.append(f"Cursor using ~{cursor_gb} GB — restart Cursor when sluggish")
    elif cursor_gb >= 4:
        pressure = "medium"
        reasons.append(f"Cursor using ~{cursor_gb} GB — memory creep likely")
    if sina_mb >= 400:
        reasons.append(f"Legacy hub process ~{sina_mb:.0f} MB — should be OFF; quit if running")
    elif sina_mb >= 80:
        reasons.append(f"Legacy hub process ~{sina_mb:.0f} MB — quarantine violated")
    if swap_active:
        pressure = "high" if pressure != "high" else pressure
        reasons.append("Swap activity detected — Mac is memory-starved")
    if load1 > cores * 1.5:
        reasons.append(f"CPU load {load1:.1f} on {cores} cores — thermal throttle possible")
    if not reasons:
        reasons.append("No dominant lag suspect — system within normal range")
    return {"pressure": pressure, "reasons": reasons}


def build_snapshot() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    vm = parse_vm_stat()
    mem_press = memory_pressure()
    cpu = cpu_snapshot()
    all_procs = cpu["top_ram"] + [p for p in cpu["top_cpu"] if p not in cpu["top_ram"]]
    # full process list for grouping
    top = run(["ps", "-axo", "pcpu,rss,comm"])
    procs: list[dict] = []
    for line in top.splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        try:
            procs.append(
                {"cpu_pct": float(parts[0]), "rss_mb": round(int(parts[1]) / 1024, 1), "comm": parts[2][:120]}
            )
        except ValueError:
            continue
    groups = group_apps(procs)
    verdict = lag_verdict(groups, vm, cpu)
    return {
        "captured_at_utc": now,
        "captured_at_local": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "machine": {
            "model": sysctl("hw.model"),
            "chip": sysctl("machdep.cpu.brand_string") if run(["sysctl", "-n", "machdep.cpu.brand_string"]).strip() else "Apple Silicon",
            "ram_gb": cpu["total_ram_gb"],
            "cores": cpu["cores"],
        },
        "memory": {**vm, "pressure": mem_press},
        "cpu": {"loadavg": cpu["loadavg"], "top_cpu": cpu["top_cpu"], "top_ram": cpu["top_ram"]},
        "gpu": gpu_snapshot(),
        "disk": disk_snapshot(),
        "thermal_power": thermal_and_power(),
        "apps_grouped": groups,
        "lag_verdict": verdict,
    }


def format_report(s: dict) -> str:
    lines = [
        f"MAC SNAPSHOT — {s['captured_at_local']}",
        "=" * 56,
        f"Machine: {s['machine'].get('model')} · {s['machine']['ram_gb']} GB RAM · {s['machine']['cores']} cores",
        "",
        "MEMORY",
        f"  Wired:      {s['memory']['wired_mb']} MB",
        f"  Active:     {s['memory']['active_mb']} MB",
        f"  Compressed: {s['memory']['compressed_mb']} MB",
        f"  Free:       {s['memory']['free_mb']} MB",
        f"  Swap in/out: {s['memory']['swapins']} / {s['memory']['swapouts']}",
        f"  Pressure:   {s['memory']['pressure'].get('summary', 'n/a')[:80]}",
        "",
        f"CPU load (1/5/15m): {s['cpu']['loadavg']}",
        "",
        "APPS BY RAM (grouped)",
    ]
    for g in s["apps_grouped"][:10]:
        if g["rss_mb"] < 50 and g["app"] == "Other":
            continue
        gb = f" ({g['rss_gb']} GB)" if g["rss_gb"] >= 1 else ""
        lines.append(f"  {g['app']:<18} {g['rss_mb']:>8.0f} MB{gb}  ·  {g['processes']} proc  ·  CPU {g['cpu_pct']:.0f}%")
    lines.extend(["", "TOP RAM PROCESSES"])
    for p in s["cpu"]["top_ram"][:8]:
        lines.append(f"  {p['rss_mb']:>7.0f} MB  CPU {p['cpu_pct']:>5.1f}%  {p['comm'][:70]}")
    lines.extend(["", "TOP CPU PROCESSES"])
    for p in s["cpu"]["top_cpu"][:6]:
        lines.append(f"  {p['rss_mb']:>7.0f} MB  CPU {p['cpu_pct']:>5.1f}%  {p['comm'][:70]}")
    gpu = s.get("gpu", {})
    if gpu.get("displays"):
        lines.extend(["", "GPU / DISPLAY", *[f"  {d}" for d in gpu["displays"][:3]]])
    tp = s.get("thermal_power", {})
    if tp.get("therm"):
        lines.extend(["", "THERMAL", *[f"  {ln}" for ln in tp["therm"].splitlines()[:4]]])
    d = s.get("disk", {})
    lines.extend(["", "DISK /", f"  {d.get('root_volume', 'n/a')}"])
    v = s["lag_verdict"]
    lines.extend(["", f"LAG VERDICT: {v['pressure'].upper()}"])
    for r in v["reasons"]:
        lines.append(f"  • {r}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    snap = build_snapshot()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(format_report(snap))
    print(f"(saved {OUT_JSON})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
