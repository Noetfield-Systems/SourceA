#!/usr/bin/env bash
# validate-h2-legacy-quarantine-banner-bookmark-v1.sh — sa-0825 legacy quarantine vs H2 bookmark law
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-h2-legacy-quarantine-banner-bookmark-v1 — $*" >&2; exit 1; }

DOC="$ROOT/archive/attachments/2026-06-15/sa-0825-h2-legacy-quarantine-banner-bookmark_LOCKED_v1.md"
LAW="$ROOT/SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md"
HTML="$ROOT/agent-control-panel/machines/index.html"

[[ -f "$DOC" ]] || fail "missing LOCKED doc $DOC"
[[ -f "$LAW" ]] || fail "missing $LAW"
[[ -f "$HTML" ]] || fail "missing $HTML"
grep -q "Sina Command archive banner vs Hub 2 bookmark law" "$LAW" || fail "H2 plan missing slot 25 pointer"
grep -q "quarantine-line" "$HTML" || fail "machines/index.html missing quarantine-line hook"
grep -q "quarantine_bookmark_slice" "$HTML" || fail "machines/index.html missing quarantine_bookmark_slice render"
grep -q 'href="/legacy/"' "$HTML" && fail "machines/index.html must not link /legacy/ on daily H2 banner"

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"

python3 - <<'PY' || fail "quarantine bookmark slice audit"
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path("..").resolve()
DOC = ROOT / "archive/attachments/2026-06-15/sa-0825-h2-legacy-quarantine-banner-bookmark_LOCKED_v1.md"
text = DOC.read_text(encoding="utf-8")
for needle in (
    "quarantine_bookmark_slice",
    "h2-quarantine-bookmark-slice-v1",
    "cross_check_ok",
    "/legacy/",
    "READ ONLY",
):
    if needle not in text:
        raise SystemExit(f"LOCKED doc missing {needle}")

sys.path.insert(0, str(ROOT / "scripts"))
from h2_quarantine_bookmark_slice_v1 import quarantine_bookmark_slice_payload  # noqa: E402
from machine_hub_v1 import machine_hub_payload  # noqa: E402

base = "http://127.0.0.1:13020"
slice_row = quarantine_bookmark_slice_payload(base=base)
if slice_row.get("schema") != "h2-quarantine-bookmark-slice-v1":
    raise SystemExit(f"bad schema {slice_row.get('schema')}")
if slice_row.get("legacy_retired") is not True and slice_row.get("legacy_url") != "/legacy/":
    raise SystemExit(f"legacy_url drift {slice_row.get('legacy_url')!r}")
if slice_row.get("h2_museum_href"):
    raise SystemExit(f"H2 daily banner must not link legacy — got {slice_row.get('h2_museum_href')!r}")
if not slice_row.get("cross_check_ok"):
    raise SystemExit(f"cross_check_ok false: {slice_row}")

lb = slice_row.get("legacy_banner") or {}
if lb.get("retired"):
    if lb.get("http_status") not in (301, 302, 303, 307, 308):
        raise SystemExit(f"legacy retired but bad status {lb.get('http_status')}")
elif not (lb.get("has_readonly_banner") and lb.get("mentions_read_only")):
    raise SystemExit("legacy missing museum-readonly-banner or READ ONLY wording")

hub = machine_hub_payload(skip_cache=True)
qs = hub.get("quarantine_bookmark_slice") or {}
if not qs.get("cross_check_ok"):
    raise SystemExit("machine-hub quarantine_bookmark_slice cross_check_ok false")
if hub.get("legacy_retired") is not True:
    raise SystemExit(f"hub legacy_retired {hub.get('legacy_retired')!r}")

import urllib.request
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener = urllib.request.build_opener(_NoRedirect, urllib.request.HTTPHandler)
try:
    opener.open(base + "/legacy/", timeout=20)
    raise SystemExit("live /legacy/ must not serve 200")
except urllib.error.HTTPError as exc:
    if exc.code not in (301, 302, 303, 307, 308):
        raise SystemExit(f"live /legacy/ expected redirect got {exc.code}") from exc

live_machines = urllib.request.urlopen(base + "/machines/", timeout=20).read().decode("utf-8", errors="replace")
if 'href="/legacy/"' in live_machines:
    raise SystemExit("live /machines/ must not link /legacy/ on daily banner")

print(
    f"OK: quarantine_bookmark_slice · archive quarantined · no H2 legacy link · cross_check_ok"
)
PY

bash "$ROOT/scripts/validate-machines-banner-sibling-v1.sh" >/dev/null || fail "machines sibling banner"
bash "$ROOT/scripts/validate-machine-hub-v1.sh" >/dev/null || fail "machine hub base"

echo "OK: validate-h2-legacy-quarantine-banner-bookmark-v1 · sa-0825"
