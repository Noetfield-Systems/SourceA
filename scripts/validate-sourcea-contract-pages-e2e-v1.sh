#!/usr/bin/env bash
# Contract landing pages E2E — clean URLs, titles, and booking CTAs on sourcea.app + regional domains.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
RECEIPT="${HOME}/.sina/e2e-logs/validate-sourcea-contract-pages-e2e-v1.log"
mkdir -p "$(dirname "$RECEIPT")"

echo "=== validate-sourcea-contract-pages-e2e-v1 ===" | tee "$RECEIPT"
echo "base ${BASE}" | tee -a "$RECEIPT"

python3 - <<PY 2>&1 | tee -a "$RECEIPT"
import json
import re
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "${BASE}".rstrip("/")
ROOT = Path("${ROOT}")
GREEN = ROOT / "SourceA-landing" / "green-unified"

PAGES = [
    {
        "path": "/operating-brain-install",
        "title": "Operating Brain Install",
        "cta": "Book an Operating Brain Audit",
        "subject": "Operating%20Brain%20Audit",
        "source": GREEN / "operating-brain-install.html",
    },
    {
        "path": "/ai-value-governance",
        "title": "AI Value Governance",
        "cta": "Book an AI Value Governance Sprint",
        "subject": "AI%20Value%20Governance%20Sprint",
        "source": GREEN / "ai-value-governance.html",
    },
    {
        "path": "/enterprise-ai-control-plane",
        "title": "Enterprise AI Control Plane",
        "cta": "Book an Enterprise AI Control Plane Briefing",
        "subject": "Enterprise%20AI%20Control%20Plane%20Briefing",
        "source": GREEN / "enterprise-ai-control-plane.html",
    },
]

REGIONAL = [
    {
        "hosts": ("sourcea.ca", "www.sourcea.ca"),
        "path": "/ai-value-governance",
        "title": "AI Value Governance",
        "cta": "Book an AI Value Governance Sprint",
    },
    {
        "hosts": ("sourcea.uk", "www.sourcea.uk"),
        "path": "/enterprise-ai-control-plane",
        "title": "Enterprise AI Control Plane",
        "cta": "Book an Enterprise AI Control Plane Briefing",
    },
]

ctx = ssl.create_default_context()
fails = []
notes = []


def fetch_http(url: str, host: str | None = None) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SourceA-contract-pages-e2e/1",
            **({"Host": host} if host else {}),
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
        return resp.status, resp.read(250_000).decode("utf-8", errors="replace")


def dig_a(host: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["dig", "+short", host, "A"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]


def fetch_regional(hosts: tuple[str, ...], path: str) -> tuple[int, str, str]:
    last_err = ""
    for host in hosts:
        url = f"https://{host}{path}"
        try:
            socket.getaddrinfo(host, 443)
            status, body = fetch_http(url)
            return status, body, host
        except OSError as exc:
            last_err = str(exc)
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code}"
        for ip in dig_a(host):
            try:
                status, body = fetch_http(f"https://{ip}{path}", host=host)
                notes.append(f"{host}{path} via A {ip} (local resolver lag)")
                return status, body, host
            except Exception as exc:
                last_err = str(exc)
    raise RuntimeError(last_err or "regional fetch failed")


def check_page(label: str, status: int, body: str, title_need: str, cta_need: str, *, mailto: str | None = None) -> None:
    if status != 200:
        fails.append(f"{label}: HTTP {status}")
        return
    title_m = re.search(r"<title>([^<]+)</title>", body, re.I)
    title = title_m.group(1) if title_m else ""
    if title_need not in title:
        fails.append(f"{label}: title missing {title_need!r} (got {title!r})")
    if cta_need not in body:
        fails.append(f"{label}: missing CTA {cta_need!r}")
    if mailto and mailto not in body:
        fails.append(f"{label}: missing mailto {mailto}")
    print(f"OK {label} · {title}")


for row in PAGES:
    path = row["path"]
    status, body = fetch_http(f"{BASE}{path}")
    check_page(
        f"{BASE}{path}",
        status,
        body,
        row["title"],
        row["cta"],
        mailto=f"mailto:sina.kazemnezhad@gmail.com?subject={row['subject']}",
    )
    src = row["source"]
    if not src.is_file():
        fails.append(f"disk missing {src}")
    elif row["cta"] not in src.read_text(encoding="utf-8"):
        fails.append(f"disk {src.name}: missing CTA {row['cta']!r}")

for row in REGIONAL:
    host_primary = row["hosts"][0]
    path = row["path"]
    try:
        status, body, used_host = fetch_regional(row["hosts"], path)
        check_page(f"https://{host_primary}{path}", status, body, row["title"], row["cta"])
        if used_host != host_primary:
            notes.append(f"verified via {used_host}; canonical host {host_primary}")
    except Exception as exc:
        fails.append(f"https://{host_primary}{path}: {exc}")

for note in notes:
    print(f"NOTE: {note}")

if fails:
    for f in fails:
        print("FAIL:", f, file=sys.stderr)
    sys.exit(1)

print("validate-sourcea-contract-pages-e2e-v1.sh: ALL PASS")
PY
ec=${PIPESTATUS[0]}
if [[ "$ec" -ne 0 ]]; then
  exit "$ec"
fi

python3 -c "
import json, time
from pathlib import Path
p = Path.home() / '.sina' / 'sourcea-contract-pages-e2e-v1.json'
p.write_text(json.dumps({
  'schema': 'sourcea-contract-pages-e2e-v1',
  'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
  'base': '${BASE}',
  'ok': True,
}, indent=2) + '\n', encoding='utf-8')
print('OK receipt', p)
" | tee -a "$RECEIPT"
