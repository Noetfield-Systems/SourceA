#!/usr/bin/env python3
"""Forge Terminal OS bridge — Chat Unify :13023 · Mac .app :13029 · DevBridge · Cursor OS Pro Expo."""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-terminal-os-bridge-v1.json"
DEVBRIDGE_STATE = Path.home() / ".devbridge" / "state.json"
CURSOR_OS_PRO = Path.home() / "Desktop" / "Cursor OS Pro"
DEVBRIDGE_ROOT = Path.home() / "Desktop" / "AI Dev Bridge OS"

CHAT_UNIFY_PORT = int(os.environ.get("CHAT_UNIFY_PORT", "13023"))
FORGE_TERMINAL_PORT = int(os.environ.get("FORGE_TERMINAL_PORT", "13029"))
CURSOR_BRIDGE_PORT = int(os.environ.get("CURSOR_BRIDGE_PORT", "9473"))

TAILSCALE_BINS = (
    "tailscale",
    "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
    "/usr/local/bin/tailscale",
    "/opt/homebrew/bin/tailscale",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tailscale_ip() -> str | None:
    for bin_path in TAILSCALE_BINS:
        try:
            out = subprocess.check_output([bin_path, "ip", "-4"], stderr=subprocess.DEVNULL, text=True)
            ip = out.strip()
            if ip:
                return ip
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            continue
    return None


def lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def _probe(url: str, timeout: float = 2.5) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip() else {"ok": True}
    except Exception:
        return None


def _port_listening(port: int) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        ok = s.connect_ex(("127.0.0.1", port)) == 0
        s.close()
        return ok
    except OSError:
        return False


def ensure_chat_unify() -> bool:
    health = _probe(f"http://127.0.0.1:{CHAT_UNIFY_PORT}/health")
    forge = _probe(f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/forge-terminal/v1?status=1")
    if health and health.get("ok") and forge and (forge.get("models") or forge.get("ok") is not False):
        return True
    script = SOURCE_A / "scripts" / "serve-chat-unify.sh"
    if not script.is_file():
        return False
    # Stale Chat Unify without forge routes — force port recycle
    env = os.environ.copy()
    env["CHAT_UNIFY_PORT"] = str(CHAT_UNIFY_PORT)
    env["SINA_SOURCE_A"] = str(SOURCE_A)
    env["CHAT_UNIFY_UI_VERSION"] = "4.8.0"
    lsof = "/usr/sbin/lsof"
    if os.path.isfile(lsof):
        try:
            subprocess.run(
                f'{lsof} -t -iTCP:{CHAT_UNIFY_PORT} | xargs kill 2>/dev/null || true',
                shell=True,
                check=False,
            )
            import time

            time.sleep(0.4)
        except OSError:
            pass
    try:
        subprocess.run(["bash", str(script)], cwd=str(SOURCE_A), env=env, check=False, timeout=90)
    except subprocess.TimeoutExpired:
        pass
    return bool(_probe(f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/forge-terminal/v1?status=1"))


def forge_models_ok(port: int) -> bool:
    payload = _probe(f"http://127.0.0.1:{port}/api/forge-terminal/v1?status=1")
    if not payload or payload.get("ok") is False:
        return False
    models = payload.get("models") or payload.get("model_matrix") or []
    return len(models) >= 4


def build_payload(*, sync_devbridge: bool = False) -> dict:
    ts = tailscale_ip()
    lan = lan_ip()
    chat_health = _probe(f"http://127.0.0.1:{CHAT_UNIFY_PORT}/health") or {}
    forge_health = _probe(f"http://127.0.0.1:{FORGE_TERMINAL_PORT}/health") or {}
    forge_status = _probe(f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/forge-terminal/v1?status=1") or {}

    devbridge: dict = {}
    if DEVBRIDGE_STATE.is_file():
        try:
            devbridge = json.loads(DEVBRIDGE_STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            devbridge = {}

    forge_api_path = "/api/forge-terminal/v1"
    terminal_path = "/terminal/"

    urls = {
        "mac_standalone_app": f"http://127.0.0.1:{FORGE_TERMINAL_PORT}{terminal_path}",
        "mac_forge_api": f"http://127.0.0.1:{CHAT_UNIFY_PORT}{forge_api_path}",
        "lan_forge_api": f"http://{lan}:{CHAT_UNIFY_PORT}{forge_api_path}",
        "lan_forge_terminal_ui": f"http://{lan}:{CHAT_UNIFY_PORT}{terminal_path}",
        "lan_cursor_bridge": f"http://{lan}:{CURSOR_BRIDGE_PORT}",
    }
    if ts:
        urls["tailscale_forge_api"] = f"http://{ts}:{CHAT_UNIFY_PORT}{forge_api_path}"
        urls["tailscale_forge_terminal_ui"] = f"http://{ts}:{CHAT_UNIFY_PORT}{terminal_path}"
        urls["tailscale_cursor_bridge"] = f"http://{ts}:{CURSOR_BRIDGE_PORT}"
        desk_port = devbridge.get("deskPort") or "3004"
        agent_port = devbridge.get("port") or 8766
        code = devbridge.get("pairingCode") or "000000"
        urls["tailscale_devbridge_desk"] = (
            f"http://{ts}:{desk_port}/?host={ts}&port={agent_port}&code={code}&lane=full_m8"
        )

    payload = {
        "schema": "forge-terminal-os-bridge-v1",
        "updated_at": _now(),
        "source_a": str(SOURCE_A),
        "ports": {
            "chat_unify_forge_api": CHAT_UNIFY_PORT,
            "forge_terminal_standalone": FORGE_TERMINAL_PORT,
            "cursor_os_pro_bridge": CURSOR_BRIDGE_PORT,
            "devbridge_agent": devbridge.get("port") or 8766,
            "devbridge_desk": devbridge.get("deskPort") or 3004,
        },
        "ready": {
            "chat_unify": bool(chat_health.get("ok")),
            "forge_api_models": forge_models_ok(CHAT_UNIFY_PORT),
            "forge_standalone_app": bool(forge_health.get("ok")),
            "tailscale": bool(ts),
            "devbridge_state": DEVBRIDGE_STATE.is_file(),
            "cursor_os_pro_repo": CURSOR_OS_PRO.is_dir(),
        },
        "model_matrix": forge_status.get("models") or forge_status.get("model_matrix") or [],
        "urls": urls,
        "inheritance": {
            "ai_dev_bridge_os": str(DEVBRIDGE_ROOT),
            "cursor_os_pro": str(CURSOR_OS_PRO),
            "sina_prompt_os": "scripts/sina_command_lib.py · promptos-ui :8899",
            "forge_standalone_build": "scripts/build-forge-terminal-standalone-app-v1.sh",
        },
    }

    if sync_devbridge and DEVBRIDGE_STATE.parent.is_dir():
        merged = {**devbridge, "forgeTerminal": urls, "forgeOsBridgeUpdatedAt": _now()}
        DEVBRIDGE_STATE.parent.mkdir(parents=True, exist_ok=True)
        DEVBRIDGE_STATE.write_text(json.dumps(merged, indent=2), encoding="utf-8")
        payload["devbridge_state_synced"] = True

    return payload


def write_receipt(payload: dict) -> Path:
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return RECEIPT


def print_bridge(payload: dict) -> None:
    u = payload.get("urls") or {}
    r = payload.get("ready") or {}
    print("")
    print("══ Forge Terminal OS Bridge ══")
    print(f"Receipt: {RECEIPT}")
    print("")
    print("── Standalone macOS window ──")
    print(f"  open \"$HOME/Desktop/Forge Terminal.app\"")
    print(f"  UI: {u.get('mac_standalone_app', '—')}")
    print("")
    print("── Mobile Forge API (Chat Unify :13023 · Master Model Matrix) ──")
    print(f"  Mac:  {u.get('mac_forge_api', '—')}")
    if u.get("lan_forge_api"):
        print(f"  LAN:  {u['lan_forge_api']}")
    if u.get("tailscale_forge_api"):
        print(f"  TS:   {u['tailscale_forge_api']}")
    else:
        print("  TS:   (Tailscale not connected — install + tailscale up)")
    print("")
    print("── Cursor OS Pro · Expo Go + Tailscale ──")
    print("  Terminal A — bridge + Expo (same Wi‑Fi or Tailscale):")
    print(f"    cd \"$HOME/Desktop/Cursor OS Pro\"")
    print(f"    FORGE_API_URL=http://127.0.0.1:{CHAT_UNIFY_PORT} npm run dev")
    print("  Terminal B — pair phone to bridge (use TS URL when off-LAN):")
    bridge = u.get("tailscale_cursor_bridge") or u.get("lan_cursor_bridge")
    print(f"    Bridge URL in Expo pair screen: {bridge}")
    print(f"    Forge via bridge proxy: {bridge}/api/forge-terminal/v1")
    print("")
    print("── AI Dev Bridge OS · Safari desk (inherits G3 Tailscale) ──")
    if u.get("tailscale_devbridge_desk"):
        print(f"  {u['tailscale_devbridge_desk']}")
    else:
        print("  cd \"$HOME/Desktop/AI Dev Bridge OS\" && npm start")
        print("  npm run proof:g3")
    print("")
    models = payload.get("model_matrix") or []
    if models:
        print(f"── Master Model Matrix ({len(models)} models) ──")
        for m in models[:8]:
            if isinstance(m, dict):
                print(f"  · {m.get('id', m.get('label', m))}")
            else:
                print(f"  · {m}")
    print("")
    print("Ready:", ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in r.items()))
    print("")


def main() -> int:
    parser = argparse.ArgumentParser(description="Forge Terminal OS bridge")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    parser.add_argument("--print", dest="print_bridge", action="store_true", help="Print human bridge card")
    parser.add_argument("--sync", action="store_true", help="Merge forge URLs into ~/.devbridge/state.json")
    parser.add_argument("--ensure-chat-unify", action="store_true", help="Start Chat Unify :13023 if down")
    args = parser.parse_args()

    if args.ensure_chat_unify:
        ensure_chat_unify()

    payload = build_payload(sync_devbridge=args.sync)
    write_receipt(payload)

    if args.json:
        print(json.dumps(payload, indent=2))
    elif args.print_bridge or not args.json:
        print_bridge(payload)

    return 0 if payload["ready"].get("chat_unify") else 1


if __name__ == "__main__":
    sys.exit(main())
