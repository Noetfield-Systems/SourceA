#!/usr/bin/env bash
# sa-0519 — evidence flywheel doc linked from hub essentials
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0519-evidence-flywheel-hub-essentials_LOCKED_v1.md"
FLYWHEEL="product/EVIDENCE_FLYWHEEL_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
test -f "$FLYWHEEL" || { echo "FAIL: missing $FLYWHEEL"; exit 1; }
python3 - <<'PY'
import json
import importlib.util
from pathlib import Path

spec_he = importlib.util.spec_from_file_location("hei", Path("scripts/hub_essentials_index.py"))
hei = importlib.util.module_from_spec(spec_he)
spec_he.loader.exec_module(hei)

found_pillar = False
for pillar in hei._PILLAR_DEFS:
    for item in pillar.get("items", []):
        if item.get("path") == "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md":
            found_pillar = True
            if pillar.get("id") != "execute":
                raise SystemExit(f"FAIL: flywheel pillar {pillar.get('id')!r} expected execute")
if not found_pillar:
    raise SystemExit("FAIL: hub_essentials_index missing EVIDENCE_FLYWHEEL doc in pillars")

spec_idi = importlib.util.spec_from_file_location("idi", Path("scripts/important_docs_index.py"))
idi = importlib.util.module_from_spec(spec_idi)
spec_idi.loader.exec_module(idi)
paths = [row[0] for _sid, _title, _aud, docs in idi._RAW_SECTIONS for row in docs]
if "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md" not in paths:
    raise SystemExit("FAIL: important_docs_index missing flywheel doc")

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
mp = (pp.get("signals_auto") or {}).get("mergepack") or {}
if mp.get("ecosystem") != "EVIDENCE_FLYWHEEL_LOCKED_v1.md":
    raise SystemExit(f"FAIL: mergepack.ecosystem {mp.get('ecosystem')!r}")

efh = (pp.get("signals_auto") or {}).get("evidence_flywheel_hub") or {}
for key in ("flywheel_doc", "crossref_doc", "hub_essentials_pillar", "important_docs_section"):
    if key not in efh:
        raise SystemExit(f"FAIL: signals_auto.evidence_flywheel_hub missing {key}")
if "sa-0519-evidence-flywheel" not in str(efh.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0519 attachment")
if efh.get("flywheel_doc") != "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md":
    raise SystemExit("FAIL: flywheel_doc path mismatch")

print("OK: validate-evidence-flywheel-hub-essentials-v1 · sa-0519")
PY
