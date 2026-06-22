#!/usr/bin/env python3
"""Agent loop: obtain witnessbc CF DNS token → apply cutover → verify prod.

Token sources (first match wins):
  1. WITNESSBC_CF_API_TOKEN in ~/.sina/secrets.env
  2. ~/.sina/witnessbc-cf-dns-token-v1.json
  3. Clipboard (Cloudflare one-time token shape)

Receipt: ~/.sina/witnessbc-dns-cutover-agent-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRETS = Path.home() / ".sina/secrets.env"
TOKEN_FILE = Path.home() / ".sina/witnessbc-cf-dns-token-v1.json"
RECEIPT = Path.home() / ".sina/witnessbc-dns-cutover-agent-receipt-v1.json"
ZONE_ID = "fbaba5b3d756fa9c2d6e5e6368df4414"
CUTOVER = ROOT / "scripts/dns_cutover_witnessbc_vercel_main_v1.py"
BOOTSTRAP = ROOT / "scripts/bootstrap_witnessbc_cf_dns_token_v1.py"
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{32,128}$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_secrets_token() -> str | None:
    if not SECRETS.is_file():
        return None
    for ln in SECRETS.read_text(encoding="utf-8").splitlines():
        if ln.startswith("WITNESSBC_CF_API_TOKEN="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v or None
    return None


def _read_file_token() -> str | None:
    if not TOKEN_FILE.is_file():
        return None
    try:
        row = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return row.get("api_token") or row.get("token")


def _read_clipboard_token() -> str | None:
    proc = subprocess.run(["pbpaste"], capture_output=True, text=True, check=False)
    val = (proc.stdout or "").strip()
    if TOKEN_RE.match(val):
        return val
    return None


def _sync_token(token: str) -> None:
    TOKEN_FILE.write_text(
        json.dumps(
            {
                "schema": "witnessbc-cf-dns-token-v1",
                "api_token": token,
                "zone_id": ZONE_ID,
                "saved_at": _now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lines: list[str] = []
    if SECRETS.is_file():
        lines = SECRETS.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    seen_t = seen_z = False
    for ln in lines:
        if ln.startswith("WITNESSBC_CF_API_TOKEN="):
            out.append(f"WITNESSBC_CF_API_TOKEN={token}")
            seen_t = True
        elif ln.startswith("WITNESSBC_CF_ZONE_ID="):
            out.append(f"WITNESSBC_CF_ZONE_ID={ZONE_ID}")
            seen_z = True
        else:
            out.append(ln)
    if not seen_t:
        out.append(f"WITNESSBC_CF_API_TOKEN={token}")
    if not seen_z:
        out.append(f"WITNESSBC_CF_ZONE_ID={ZONE_ID}")
    SECRETS.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def _focus_chrome_tab(url_part: str) -> bool:
    script = f'''
tell application "Google Chrome"
  activate
  repeat with w in windows
    set tabIdx to 0
    repeat with t in tabs of w
      set tabIdx to tabIdx + 1
      if URL of t contains "{url_part}" then
        set index of w to 1
        set active tab index of w to tabIdx
        return "ok"
      end if
    end repeat
  end repeat
  return "miss"
end tell
'''
    proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
    return (proc.stdout or "").strip() == "ok"


def _verify_prod() -> dict:
    checks: dict[str, str] = {}
    for label, url, needle in (
        ("www_title", "https://www.witnessbc.com/", "Witness AI"),
        ("observe", "https://www.witnessbc.com/observe/", "observe and narrate"),
        ("preview", "https://deploy-witnessbc-agentic-governance-theta.vercel.app/", "Witness AI"),
    ):
        try:
            with urllib.request.urlopen(url, timeout=25) as resp:
                body = resp.read(500_000).decode("utf-8", errors="replace")
            checks[label] = "PASS" if needle in body else "FAIL"
        except Exception as exc:
            checks[label] = f"ERR:{type(exc).__name__}"
    return checks


def acquire_token(poll_sec: int, open_bootstrap: bool) -> tuple[str | None, str]:
    deadline = time.time() + poll_sec
    if open_bootstrap and not _read_secrets_token() and not _read_file_token():
        subprocess.run(["python3", str(BOOTSTRAP)], check=False)
        _focus_chrome_tab("api-tokens")

    while time.time() < deadline:
        for source, tok in (
            ("secrets", _read_secrets_token()),
            ("token_file", _read_file_token()),
            ("clipboard", _read_clipboard_token()),
        ):
            if tok:
                _sync_token(tok)
                return tok, source
        time.sleep(2)
    return None, "timeout"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--poll-sec", type=int, default=90)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--apply", action="store_true", default=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    receipt: dict = {"schema": "witnessbc-dns-cutover-agent-receipt-v1", "at": _now(), "ok": False}
    tok, src = acquire_token(args.poll_sec, open_bootstrap=not args.no_open)
    receipt["token_source"] = src
    if not tok:
        receipt["phase"] = "await_token"
        receipt["error"] = "No WITNESSBC_CF_API_TOKEN within poll window"
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(receipt, indent=2))
        return 1

    proc = subprocess.run(
        ["python3", str(CUTOVER), "--apply", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        cutover = json.loads(proc.stdout) if proc.stdout.strip() else {"ok": False, "stderr": proc.stderr}
    except json.JSONDecodeError:
        cutover = {"ok": False, "stdout": proc.stdout, "stderr": proc.stderr}
    receipt["cutover"] = cutover
    receipt["verify"] = _verify_prod()
    receipt["ok"] = bool(cutover.get("ok")) and receipt["verify"].get("www_title") == "PASS"
    receipt["phase"] = "done" if receipt["ok"] else "cutover_or_verify_failed"
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"ok={receipt['ok']} phase={receipt['phase']} receipt={RECEIPT}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
