#!/usr/bin/env python3
"""Keep SourceA landing tunnel alive — restart if dead · fix Mac DNS · print public URL."""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PUBLIC_URLS = SINA / "sourcea-public-urls-v1.json"
TUNNEL_PID = SINA / "sourcea-landing-tunnel-v1.pid"
TUNNEL_LOG = SINA / "sourcea-landing-tunnel-v1.log"
TUNNEL_PORT = int(os.environ.get("SOURCEA_LANDING_TUNNEL_PORT", "8190"))


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _trycloudflare_dns_ok(hostname: str) -> bool:
    try:
        socket.gethostbyname(hostname)
        return True
    except OSError:
        return False


def _fix_mac_dns_if_needed(hostname: str) -> dict:
    if _trycloudflare_dns_ok(hostname):
        return {"ok": True, "action": "noop"}
    try:
        proc = subprocess.run(
            ["networksetup", "-setdnsservers", "Wi-Fi", "1.1.1.1", "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        subprocess.run(["dscacheutil", "-flushcache"], capture_output=True, timeout=10)
        subprocess.run(["killall", "-HUP", "mDNSResponder"], capture_output=True, timeout=10)
        ok = proc.returncode == 0 and _trycloudflare_dns_ok(hostname)
        return {
            "ok": ok,
            "action": "set_wifi_dns",
            "detail": "Wi-Fi DNS → 1.1.1.1 · 8.8.8.8 (router DNS was NXDOMAIN for trycloudflare)",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "action": "set_wifi_dns_failed", "error": str(exc)}


def _tunnel_url_from_log() -> str | None:
    if not TUNNEL_LOG.is_file():
        return None
    matches = re.findall(
        r"https://[a-z0-9-]+\.trycloudflare\.com",
        TUNNEL_LOG.read_text(encoding="utf-8", errors="replace"),
    )
    return matches[-1].rstrip("/") if matches else None


def _local_ok() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{TUNNEL_PORT}/sourcea/scenario.html", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def _public_reachable(scenario_url: str) -> bool:
    try:
        with urllib.request.urlopen(scenario_url, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def status() -> dict:
    row: dict = {"schema": "sourcea-landing-tunnel-guard-v1", "local_port": TUNNEL_PORT}
    scenario_url = ""
    if PUBLIC_URLS.is_file():
        try:
            pub = json.loads(PUBLIC_URLS.read_text(encoding="utf-8"))
            scenario_url = str(pub.get("scenario_url") or "")
            row["scenario_url"] = scenario_url
            row["base_url"] = pub.get("base_url")
        except (OSError, json.JSONDecodeError):
            pass
    log_url = _tunnel_url_from_log()
    if log_url and scenario_url and log_url not in scenario_url:
        row["url_stale_warning"] = f"public-urls stale — log has {log_url}"

    tunnel_pid = None
    if TUNNEL_PID.is_file():
        try:
            tunnel_pid = int(TUNNEL_PID.read_text().strip())
        except ValueError:
            pass
    row["tunnel_pid"] = tunnel_pid
    row["tunnel_alive"] = bool(tunnel_pid and _pid_alive(tunnel_pid))
    row["local_ok"] = _local_ok()

    host = urlparse(scenario_url or log_url or "").hostname or ""
    if host.endswith(".trycloudflare.com"):
        row["dns_ok"] = _trycloudflare_dns_ok(host)
        if not row["dns_ok"]:
            row["dns_fix"] = "networksetup -setdnsservers Wi-Fi 1.1.1.1 8.8.8.8"
    else:
        row["dns_ok"] = None

    row["public_ok"] = bool(scenario_url and _public_reachable(scenario_url))
    row["ok"] = row["tunnel_alive"] and row["local_ok"] and row.get("dns_ok", True) and row["public_ok"]
    if not row["ok"]:
        row["fix"] = f"python3 {ROOT}/scripts/sourcea_landing_tunnel_guard_v1.py --ensure --fix-dns --open"
    return row


def ensure(*, restart: bool = False, fix_dns: bool = False) -> dict:
    st = status()
    if fix_dns and st.get("scenario_url"):
        host = urlparse(str(st["scenario_url"])).hostname or ""
        if host:
            st["dns_repair"] = _fix_mac_dns_if_needed(host)

    if st.get("ok") and not restart:
        st["action"] = "noop"
        return st

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "publish_sourcea_landing_v1.py"), "--skip-recipe", "--backend", "tunnel", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        pub = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    except json.JSONDecodeError:
        pub = {"ok": False, "error": (proc.stderr or proc.stdout or "")[-500:]}

    row = status()
    if fix_dns and row.get("scenario_url"):
        host = urlparse(str(row["scenario_url"])).hostname or ""
        if host:
            row["dns_repair"] = _fix_mac_dns_if_needed(host)
            row["public_ok"] = _public_reachable(str(row["scenario_url"]))
            row["ok"] = bool(row.get("tunnel_alive")) and row.get("local_ok") and row.get("dns_ok", True) and row["public_ok"]

    row["action"] = "restarted" if restart or not st.get("tunnel_alive") else "refreshed"
    row["publish"] = pub
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA landing tunnel guard")
    ap.add_argument("--ensure", action="store_true", help="Restart tunnel if dead")
    ap.add_argument("--restart", action="store_true", help="Force restart tunnel")
    ap.add_argument("--fix-dns", action="store_true", help="Set Wi-Fi DNS to 1.1.1.1 if trycloudflare NXDOMAIN")
    ap.add_argument("--open", action="store_true", help="Open scenario URL in browser (macOS)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.ensure or args.restart:
        row = ensure(restart=args.restart, fix_dns=args.fix_dns or True)
    else:
        row = status()
        if args.fix_dns and row.get("scenario_url"):
            host = urlparse(str(row["scenario_url"])).hostname or ""
            if host:
                row["dns_repair"] = _fix_mac_dns_if_needed(host)
                row["public_ok"] = _public_reachable(str(row["scenario_url"]))
                row["ok"] = bool(row.get("tunnel_alive")) and row.get("local_ok") and row.get("dns_ok", True) and row["public_ok"]

    if args.open and row.get("scenario_url"):
        subprocess.run(["open", str(row["scenario_url"])], check=False)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        url = row.get("scenario_url") or "(not published)"
        if row.get("ok"):
            print(f"OK: tunnel live · {url}")
        else:
            print(f"FAIL: {url}")
            if row.get("url_stale_warning"):
                print(f"  WARN: {row['url_stale_warning']}")
            if row.get("dns_ok") is False:
                print("  DNS: router cannot resolve trycloudflare — run with --fix-dns")
            print(f"  Fix: {row.get('fix')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
