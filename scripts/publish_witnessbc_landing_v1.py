#!/usr/bin/env python3
"""Publish WitnessBC site — local · free trycloudflare tunnel · NO paid Cloudflare.

Law: default backend = tunnel (free ephemeral) or local-only.
Does NOT require CLOUDFLARE_API_TOKEN or wrangler Pages deploy.

Receipt: ~/.sina/witnessbc-landing-publish-receipt-v1.json
Desktop: ~/Desktop/WitnessBC-Landing-URL.txt
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SITE = ROOT / "witnessbc-site"
DEPLOY = SITE / "dist" / "deploy"
RECEIPT = SINA / "witnessbc-landing-publish-receipt-v1.json"
PUBLIC_URLS = SINA / "witnessbc-public-urls-v1.json"
TUNNEL_LOG = SINA / "witnessbc-landing-tunnel-v1.log"
TUNNEL_PID = SINA / "witnessbc-landing-tunnel-v1.pid"
TUNNEL_PORT = int(os.environ.get("WITNESSBC_LANDING_TUNNEL_PORT", "8090"))
CLOUDFLARED = SINA / "bin" / "cloudflared"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=timeout)


def run_recipe() -> dict:
    script = SITE / "scripts" / "run-recipe.sh"
    proc = _run(["bash", str(script)], cwd=ROOT, timeout=600)
    return {"ok": proc.returncode == 0, "returncode": proc.returncode}


def _cloudflared() -> Path | None:
    if CLOUDFLARED.is_file() and os.access(CLOUDFLARED, os.X_OK):
        return CLOUDFLARED
    from shutil import which

    w = which("cloudflared")
    return Path(w) if w else None


def _pids_on_port(port: int) -> list[int]:
    proc = _run(["lsof", "-ti", f":{port}"], timeout=10)
    if proc.returncode != 0:
        return []
    return [int(x) for x in (proc.stdout or "").split() if x.strip().isdigit()]


def _stop_tunnel() -> None:
    if TUNNEL_PID.is_file():
        try:
            os.kill(int(TUNNEL_PID.read_text().strip()), 15)
        except (OSError, ValueError):
            pass
        TUNNEL_PID.unlink(missing_ok=True)


def deploy_tunnel(staging: Path) -> dict:
    cf = _cloudflared()
    if not cf:
        return {"ok": False, "backend": "cloudflared_tunnel", "error": "cloudflared not available — brew install cloudflared or use --backend local"}
    _stop_tunnel()
    for pid in _pids_on_port(TUNNEL_PORT):
        try:
            os.kill(pid, 15)
        except OSError:
            pass
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(TUNNEL_PORT), "--bind", "127.0.0.1"],
        cwd=str(staging),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    TUNNEL_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_fh = TUNNEL_LOG.open("w", encoding="utf-8")
    tunnel = subprocess.Popen(
        [str(cf), "tunnel", "--url", f"http://127.0.0.1:{TUNNEL_PORT}"],
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )
    TUNNEL_PID.write_text(f"{tunnel.pid}\n", encoding="utf-8")
    base_url = None
    for _ in range(35):
        time.sleep(1)
        if TUNNEL_LOG.is_file():
            text = TUNNEL_LOG.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", text)
            if m:
                base_url = m.group(0)
                break
        if tunnel.poll() is not None:
            break
    if not base_url:
        server.terminate()
        return {
            "ok": False,
            "backend": "cloudflared_tunnel",
            "error": "tunnel URL not found",
            "log_tail": TUNNEL_LOG.read_text(encoding="utf-8", errors="replace")[-600:] if TUNNEL_LOG.is_file() else "",
        }
    return {
        "ok": True,
        "backend": "cloudflared_tunnel",
        "base_url": base_url.rstrip("/"),
        "ephemeral": True,
        "free": True,
        "note": "Free trycloudflare — not paid Cloudflare Pages",
    }


def write_desktop_note(public: dict) -> Path:
    note = Path.home() / "Desktop" / "WitnessBC-Landing-URL.txt"
    base = public.get("base_url") or f"http://127.0.0.1:{TUNNEL_PORT}"
    body = "\n".join(
        [
            f"WitnessBC · updated {_now()}",
            f"Public:  {base}/",
            f"Proof:   {base}/proof.html",
            f"Local:   http://127.0.0.1:{TUNNEL_PORT}/",
            "",
            "Republish (free tunnel, no paid CF):",
            "  python3 scripts/publish_witnessbc_landing_v1.py --backend tunnel",
            "",
            "Local only:",
            "  bash witnessbc-site/scripts/run-recipe.sh --serve",
            "",
        ]
    )
    note.write_text(body, encoding="utf-8")
    return note


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish WitnessBC — free tunnel or local (no paid Cloudflare)")
    ap.add_argument("--backend", choices=("tunnel", "local"), default="tunnel")
    ap.add_argument("--skip-recipe", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    recipe = {"ok": True, "skipped": True} if args.skip_recipe else run_recipe()
    if not recipe.get("ok"):
        print("FAIL: witnessbc run-recipe", file=sys.stderr)
        return 1
    if not DEPLOY.is_dir():
        print(f"FAIL: missing {DEPLOY}", file=sys.stderr)
        return 1

    if args.backend == "local":
        deploy = {
            "ok": True,
            "backend": "local",
            "base_url": f"http://127.0.0.1:{TUNNEL_PORT}",
            "free": True,
        }
    else:
        deploy = deploy_tunnel(DEPLOY)

    if not deploy.get("ok"):
        print(json.dumps({"ok": False, "deploy": deploy}, indent=2) if args.json else f"FAIL: {deploy.get('error')}")
        return 1

    public = {
        "schema": "witnessbc-public-urls-v1",
        "at": _now(),
        "base_url": deploy["base_url"],
        "proof_url": f"{deploy['base_url']}/proof.html",
        "backend": deploy["backend"],
        "paid_cloudflare": False,
    }
    PUBLIC_URLS.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    note = write_desktop_note(public)
    receipt = {
        "schema": "witnessbc-landing-publish-receipt-v1",
        "at": _now(),
        "ok": True,
        "recipe": recipe,
        "deploy": deploy,
        "public": public,
        "desktop_note": str(note),
        "law": "free tunnel or local — no paid Cloudflare required",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"PASS: WitnessBC publish · {deploy['backend']} · {deploy['base_url']}")
        print(f"NOTE={note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
