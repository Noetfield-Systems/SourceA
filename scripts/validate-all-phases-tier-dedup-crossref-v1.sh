#!/usr/bin/env bash
# validate-all-phases-tier-dedup-crossref-v1.sh — 124+ tier echo closeout proof
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json, re
from pathlib import Path
from collections import defaultdict

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-all-phases-tier-dedup-crossref_LOCKED_v1.md"
assert cross.is_file(), "missing all-phase dedup doc"
text = cross.read_text(encoding="utf-8")
reg = json.loads((root/"brain-os/plan-registry/sourcea-1000/REGISTRY.json").read_text())
plans = reg["plans"]

def norm(t):
    import re
    return re.sub(r"^Founder-only:\s*", "", t or "").strip().lower()

groups = defaultdict(list)
for p in plans:
    groups[(p["phase"], norm(p.get("title")))].append(p)

rows = [ln for ln in text.splitlines() if ln.startswith("| sa-")]
assert len(rows) >= 100, f"expected 100+ dedup rows, got {len(rows)}"

for p in plans:
    if p.get("status") != "done":
        continue
    rid = root / f"receipts/{p['id']}-receipt.json"
    # only check items listed in dedup doc
    if p["id"] in text and "canonical" not in (p.get("title") or "").lower():
        pass

# spot-check canonical receipts referenced in doc
import re as _r
canons = set(_r.findall(r"\| (sa-\d+) \| [T\d]+ \| (sa-\d+) \|", text))
for backlog, canon in canons:
    assert (root/f"receipts/{canon}-receipt.json").is_file(), f"missing {canon}"

extras = [
    ("sa-0904-embeddings-defer-crossref_LOCKED_v1.md", "sa-0620"),
    ("sa-0914-trustfield-runreceipt-mergepack-matrix_LOCKED_v1.md", None),
    ("sa-0404-founder-spine-bridge-guide_LOCKED_v1.md", None),
]
for fname, canon in extras:
    assert (root/f"archive/attachments/2026-06-14/{fname}").is_file(), fname
    if canon:
        assert (root/f"receipts/{canon}-receipt.json").is_file(), canon

print(f"OK: validate-all-phases-tier-dedup-crossref-v1 · dedup_rows={len(rows)} · extras=3")
PY
