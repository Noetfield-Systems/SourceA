#!/usr/bin/env bash
# validate-h2-enforce-shadow-maintainer-slice-v1.sh — sa-0823 ENFORCE/shadow on H2 maintainer slice
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-h2-enforce-shadow-maintainer-slice-v1 — $*" >&2; exit 1; }

DOC="$ROOT/archive/attachments/2026-06-15/sa-0823-h2-enforce-shadow-maintainer-slice_LOCKED_v1.md"
LAW="$ROOT/SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md"
HTML="$ROOT/agent-control-panel/machines/index.html"

[[ -f "$DOC" ]] || fail "missing LOCKED doc $DOC"
[[ -f "$LAW" ]] || fail "missing $LAW"
[[ -f "$HTML" ]] || fail "missing $HTML"
grep -q "ENFORCE / packet readiness maintainer slice" "$LAW" || fail "H2 plan missing slot 23 pointer"
grep -q "enforce-line" "$HTML" || fail "machines/index.html missing enforce-line hook"
grep -q "maintainer_enforce_slice" "$HTML" || fail "machines/index.html missing maintainer_enforce_slice render"

python3 - <<'PY' || fail "maintainer enforce slice audit"
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path("..").resolve()
DOC = ROOT / "archive/attachments/2026-06-15/sa-0823-h2-enforce-shadow-maintainer-slice_LOCKED_v1.md"
text = DOC.read_text(encoding="utf-8")
for needle in (
    "maintainer_enforce_slice",
    "h2-maintainer-enforce-slice-v1",
    "cross_check_ok",
    "gate_mode",
    "packet_gate_mode",
):
    if needle not in text:
        raise SystemExit(f"LOCKED doc missing {needle}")

sys.path.insert(0, str(ROOT / "scripts"))
import model_dispatch  # noqa: E402
from h2_maintainer_enforce_slice_v1 import maintainer_enforce_slice_payload  # noqa: E402
from machine_hub_v1 import machine_hub_payload  # noqa: E402
from pre_llm.packet_readiness.hub_surface import packet_readiness_hub_payload  # noqa: E402

disk = model_dispatch.current_gate_mode()
if disk not in ("off", "shadow", "enforce"):
    raise SystemExit(f"unexpected gate_mode {disk!r}")

slice_row = maintainer_enforce_slice_payload()
if slice_row.get("schema") != "h2-maintainer-enforce-slice-v1":
    raise SystemExit(f"bad schema {slice_row.get('schema')}")
if slice_row.get("gate_mode") != disk:
    raise SystemExit(f"slice gate_mode {slice_row.get('gate_mode')!r} != disk {disk!r}")
if not slice_row.get("cross_check_ok"):
    raise SystemExit(
        f"cross_check_ok false: gate={slice_row.get('gate_mode')} "
        f"packet={slice_row.get('packet_gate_mode')}"
    )

pr = packet_readiness_hub_payload(task_id="h2-maintainer-enforce-slice")
if str(pr.get("gate_mode") or "") != disk:
    raise SystemExit(
        f"packet_readiness gate_mode {pr.get('gate_mode')!r} != disk {disk!r}"
    )

hub = machine_hub_payload(skip_cache=True)
es = hub.get("maintainer_enforce_slice") or {}
if es.get("gate_mode") != disk:
    raise SystemExit(f"hub slice gate_mode drift {es.get('gate_mode')!r}")
for key in (
    "display_line",
    "shadow_note",
    "packet_readiness_pct",
    "packet_gate_eligible",
    "gate_is_enforce",
    "gate_is_shadow",
):
    if key not in es:
        raise SystemExit(f"machine-hub missing maintainer_enforce_slice.{key}")

line = str(es.get("display_line") or "")
if disk == "enforce" and "ENFORCE" not in line:
    raise SystemExit(f"enforce mode display_line missing ENFORCE: {line!r}")
if disk == "shadow" and "SHADOW" not in line:
    raise SystemExit(f"shadow mode display_line missing SHADOW: {line!r}")
if disk == "off" and "Gate OFF" not in line:
    raise SystemExit(f"off mode display_line missing Gate OFF: {line!r}")

try:
    with urllib.request.urlopen("http://127.0.0.1:13020/api/packet-readiness-v1", timeout=30) as resp:
        api_pr = json.loads(resp.read().decode())
except OSError as exc:
    raise SystemExit(f"packet-readiness API unreachable: {exc}") from exc
if not api_pr.get("ok"):
    raise SystemExit(f"packet-readiness API not ok: {api_pr}")
if str(api_pr.get("gate_mode") or "") != disk:
    raise SystemExit(
        f"API packet-readiness gate_mode {api_pr.get('gate_mode')!r} != disk {disk!r}"
    )

print(
    f"OK: maintainer_enforce_slice · mode={disk} · "
    f"packet={es.get('packet_readiness_pct')}% · cross_check_ok"
)
PY

bash "$ROOT/scripts/validate-enforce-dispatch-policy-alignment-v1.sh" >/dev/null || fail "enforce dispatch alignment"
bash "$ROOT/scripts/validate-machine-hub-v1.sh" >/dev/null || fail "machine hub base"

echo "OK: validate-h2-enforce-shadow-maintainer-slice-v1 · sa-0823"
