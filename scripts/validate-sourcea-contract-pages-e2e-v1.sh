#!/usr/bin/env bash
# Contract landing pages E2E — clean URLs, titles, booking CTAs, contract@ inbox SSOT.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
RECEIPT="${HOME}/.sina/e2e-logs/validate-sourcea-contract-pages-e2e-v1.log"
SSOT="${ROOT}/data/sourcea-contract-email-routes-v1.json"
mkdir -p "$(dirname "$RECEIPT")"

echo "=== validate-sourcea-contract-pages-e2e-v1 ===" | tee "$RECEIPT"
echo "base ${BASE}" | tee -a "$RECEIPT"
echo "ssot ${SSOT}" | tee -a "$RECEIPT"

python3 - <<PY 2>&1 | tee -a "$RECEIPT"
import json
import os
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
SSOT_PATH = Path("${SSOT}")

ssot = json.loads(SSOT_PATH.read_text(encoding="utf-8"))
TRUST = ssot.get("trust_e2e_v1") or {}
ADMIN = ssot["google_workspace_admin"]
ROUTING = ssot["routing_mode"]
PERSONAL_LEAKS = ssot.get("forbidden_public_leaks") or []
GOOGLE_MX = ssot.get("dns_expectations", {}).get("google_workspace_mx_host", "smtp.google.com")

PAGES = []
for row in ssot["contract_routes"]:
    src_name = {
        "operating-brain-install": "operating-brain-install.html",
        "ai-value-governance": "ai-value-governance.html",
        "enterprise-ai-control-plane": "enterprise-ai-control-plane.html",
    }[row["id"]]
    PAGES.append(
        {
            "path": row["path"],
            "title": row["title"],
            "cta": row["cta"],
            "subject": row["mailto_subject"],
            "email": row["public_address"],
            "delivers_to": row["delivers_to"],
            "source": GREEN / src_name,
        }
    )

REGIONAL = []
for row in ssot.get("regional_mirror_checks") or []:
    REGIONAL.append(
        {
            "hosts": tuple(row["hosts"]),
            "path": row["path"],
            "title": next(
                (p["title"] for p in PAGES if p["email"] == row["public_address"]),
                row["path"].strip("/").replace("-", " ").title(),
            ),
            "cta": next(
                (p["cta"] for p in PAGES if p["email"] == row["public_address"]),
                "",
            ),
            "email": row["public_address"],
        }
    )

ctx = ssl.create_default_context()
fails = []
notes = []
remaining = []
checks_passed = 0


def ok(msg: str) -> None:
    global checks_passed
    checks_passed += 1
    print(msg)


class NoRedirect(urllib.request.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response

    https_response = http_response


def fetch_http_no_redirect(url: str, host: str | None = None) -> tuple[int, str]:
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(NoRedirect, https_handler)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SourceA-contract-pages-e2e/1",
            **({"Host": host} if host else {}),
        },
    )
    with opener.open(req, timeout=25) as resp:
        return resp.status, resp.read(250_000).decode("utf-8", errors="replace")


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


def dig_mx(domain: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["dig", "+short", "MX", domain],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    out = []
    for ln in (proc.stdout or "").splitlines():
        ln = ln.strip()
        if ln and GOOGLE_MX.split(".")[0] in ln:
            out.append(ln)
    return out


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
    for leak in PERSONAL_LEAKS:
        if leak in body:
            fails.append(f"{label}: leaked personal email {leak}")
    if mailto and mailto not in body:
        fails.append(f"{label}: missing mailto {mailto}")
    ok(f"OK {label} · {title}")


def check_trust_contract(label: str, body: str, disk: str | None = None) -> None:
    must = TRUST.get("contract_page_must_include") or []
    forbidden = TRUST.get("forbidden_public_strings") or []
    for needle in must:
        if needle not in body:
            fails.append(f"{label}: trust missing {needle!r}")
        else:
            ok(f"OK trust {label} · includes {needle!r}")
    for bad in forbidden:
        if bad in body:
            fails.append(f"{label}: trust forbidden string {bad!r}")
        else:
            ok(f"OK trust {label} · absent {bad!r}")
    if disk:
        for needle in must:
            if needle not in disk:
                fails.append(f"disk {label}: trust missing {needle!r}")


def check_trust_eval(label: str, status: int, body: str) -> None:
    if status != 200:
        fails.append(f"{label}: HTTP {status}")
        return
    for needle in TRUST.get("eval_must_include") or []:
        if needle not in body:
            fails.append(f"{label}: eval trust missing {needle!r}")
        else:
            ok(f"OK trust {label} · includes {needle!r}")
    try:
        direct_status, _ = fetch_http_no_redirect(label)
        if direct_status != 200:
            fails.append(f"{label}: expected direct HTTP 200, got {direct_status}")
        else:
            ok(f"OK direct 200 {label}")
    except urllib.error.HTTPError as exc:
        fails.append(f"{label}: direct check HTTP {exc.code}")


def check_trust_home(label: str, status: int, body: str) -> None:
    if status != 200:
        fails.append(f"{label}: HTTP {status}")
        return
    for needle in TRUST.get("home_must_include") or []:
        if needle not in body:
            fails.append(f"{label}: home trust missing {needle!r}")
        else:
            ok(f"OK trust {label} · includes {needle!r}")


def check_procurement_pack(host: str) -> None:
    path = TRUST.get("procurement_pack_path") or "/attach/procurement-pack.html"
    url = f"https://{host}{path}"
    try:
        status, body = fetch_http(url, host=None)
        if status != 200:
            fails.append(f"{url}: HTTP {status}")
            return
        if "procurement" not in body.lower():
            fails.append(f"{url}: missing procurement content marker")
            return
        direct_status, _ = fetch_http_no_redirect(url)
        if direct_status != 200:
            fails.append(f"{url}: expected direct HTTP 200, got {direct_status}")
        else:
            ok(f"OK procurement pack direct 200 {url}")
    except Exception as exc:
        fails.append(f"{url}: {exc}")


def check_noetfield_optional() -> None:
    strict = os.environ.get("SOURCEA_E2E_STRICT_NOETFIELD", "").strip() in ("1", "true", "yes")
    for row in TRUST.get("noetfield_live_optional") or []:
        url = row["url"]
        try:
            status, body = fetch_http(url)
        except Exception as exc:
            msg = f"{url}: fetch failed — {exc}"
            if strict:
                fails.append(msg)
            else:
                remaining.append(msg)
            continue
        if status != 200:
            msg = f"{url}: HTTP {status}"
            if strict:
                fails.append(msg)
            else:
                remaining.append(msg)
            continue
        local_fails = []
        for needle in row.get("must_include") or []:
            if needle not in body:
                local_fails.append(f"missing {needle!r}")
        for bad in row.get("forbidden") or []:
            if bad in body:
                local_fails.append(f"forbidden {bad!r} still present")
        if local_fails:
            msg = f"{url}: " + "; ".join(local_fails) + " (disk updated · live deploy pending)"
            if strict:
                fails.extend([f"{url}: {x}" for x in local_fails])
            else:
                remaining.append(msg)
        else:
            ok(f"OK noetfield live {url}")


if not ssot.get("buyer_path_note"):
    fails.append("SSOT: missing buyer_path_note")

# Inbox routing truth (Google Workspace aliases → operations@noetfield.com)
for row in PAGES:
    if row["delivers_to"] != ADMIN:
        fails.append(f"SSOT {row['email']}: delivers_to must be {ADMIN}")

mx_app = dig_mx("sourcea.app")
mx_nf = dig_mx("noetfield.com")
if not mx_app:
    fails.append(f"DNS: sourcea.app missing Google Workspace MX ({GOOGLE_MX})")
else:
    print(f"OK DNS sourcea.app MX · {mx_app[0]}")
if not mx_nf:
    notes.append(f"NOTE: noetfield.com MX not visible — admin inbox may still be wired in Workspace")
else:
    print(f"OK DNS noetfield.com MX · {mx_nf[0]}")

print(f"OK inbox routing · mode={ROUTING} · admin={ADMIN}")

for row in PAGES:
    path = row["path"]
    status, body = fetch_http(f"{BASE}{path}")
    check_page(
        f"{BASE}{path}",
        status,
        body,
        row["title"],
        row["cta"],
        mailto=f"mailto:{row['email']}?subject={row['subject']}",
    )
    check_trust_contract(f"{BASE}{path}", body)
    try:
        direct_status, _ = fetch_http_no_redirect(f"{BASE}{path}")
        if direct_status != 200:
            fails.append(f"{BASE}{path}: expected direct HTTP 200, got {direct_status} (no redirect follow)")
        else:
            print(f"OK direct 200 {BASE}{path}")
    except urllib.error.HTTPError as exc:
        fails.append(f"{BASE}{path}: direct check HTTP {exc.code}")
    src = row["source"]
    if not src.is_file():
        fails.append(f"disk missing {src}")
    else:
        disk = src.read_text(encoding="utf-8")
        if row["cta"] not in disk:
            fails.append(f"disk {src.name}: missing CTA {row['cta']!r}")
        if row["email"] not in disk:
            fails.append(f"disk {src.name}: missing public address {row['email']!r}")

for row in REGIONAL:
    host_primary = row["hosts"][0]
    path = row["path"]
    try:
        status, body, used_host = fetch_regional(row["hosts"], path)
        check_page(
            f"https://{host_primary}{path}",
            status,
            body,
            row["title"],
            row["cta"],
            mailto=f"mailto:{row['email']}",
        )
        try:
            direct_status, _ = fetch_http_no_redirect(f"https://{used_host}{path}")
            if direct_status != 200:
                fails.append(
                    f"https://{host_primary}{path}: expected direct HTTP 200, got {direct_status} (no redirect follow)"
                )
            else:
                print(f"OK direct 200 https://{host_primary}{path}")
        except urllib.error.HTTPError as exc:
            fails.append(f"https://{host_primary}{path}: direct check HTTP {exc.code}")
        if used_host != host_primary:
            notes.append(f"verified via {used_host}; canonical host {host_primary}")
        check_trust_contract(f"https://{host_primary}{path}", body)
    except Exception as exc:
        fails.append(f"https://{host_primary}{path}: {exc}")

eval_path = TRUST.get("eval_path") or "/eval"
eval_url = f"{BASE}{eval_path}"
try:
    eval_status, eval_body = fetch_http(eval_url)
    check_trust_eval(eval_url, eval_status, eval_body)
except Exception as exc:
    fails.append(f"{eval_url}: {exc}")

for home_path in TRUST.get("home_paths") or ["/"]:
    home_url = f"{BASE}{home_path}"
    try:
        home_status, home_body = fetch_http(home_url)
        check_trust_home(home_url, home_status, home_body)
    except Exception as exc:
        fails.append(f"{home_url}: {exc}")

for host in TRUST.get("procurement_hosts") or ["sourcea.app"]:
    check_procurement_pack(host)

check_noetfield_optional()

for note in notes:
    print(f"NOTE: {note}")

for item in remaining:
    print(f"REMAINING: {item}")

if fails:
    for f in fails:
        print("FAIL:", f, file=sys.stderr)
    sys.exit(1)

import time

receipt_path = Path.home() / ".sina" / "sourcea-contract-pages-e2e-v1.json"
receipt_path.write_text(
    json.dumps(
        {
            "schema": "sourcea-contract-pages-e2e-v1",
            "version": "1.1.0",
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "base": BASE,
            "ok": True,
            "checks_passed": checks_passed,
            "inbox_admin": ADMIN,
            "routing_mode": ROUTING,
            "contract_addresses": [r["public_address"] for r in ssot["contract_routes"]],
            "trust_e2e_v1": bool(TRUST),
            "remaining": remaining,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(f"OK receipt {receipt_path}")

if remaining:
    print(f"validate-sourcea-contract-pages-e2e-v1.sh: ALL PASS (SourceA) · {len(remaining)} remaining item(s)")
else:
    print("validate-sourcea-contract-pages-e2e-v1.sh: ALL PASS")
PY
ec=${PIPESTATUS[0]}
if [[ "$ec" -ne 0 ]]; then
  exit "$ec"
fi
