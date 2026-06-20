#!/usr/bin/env bash
# validate-sourcea-1000-s9-bibliography-v1.sh — sa-0975 ACT s9 bibliography in LOCK doc
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lock = root / "brain-os" / "plan-registry" / "SOURCEA-1000-LOCK.md"
text = lock.read_text(encoding="utf-8")

assert "## Phase s9 research bibliography" in text, "bibliography section missing in SOURCEA-1000-LOCK.md"
assert "sa-0975" in text, "sa-0975 maintainer marker missing"

rows = re.findall(r"\| (sa-\d{4}) \|", text)
s9_rows = [r for r in rows if int(r.split("-")[1]) >= 951]
assert len(s9_rows) >= 20, f"expected >=20 s9 bibliography rows, got {len(s9_rows)}"

must_have = ("sa-0960", "sa-0971", "sa-0974")
for sa in must_have:
    assert sa in s9_rows, f"missing canonical row {sa}"

missing = 0
for line in text.splitlines():
    if "archive/attachments/" not in line or "sa-" not in line:
        continue
    m = re.search(r"`(archive/attachments/[^`]+)`", line)
    if not m:
        continue
    rel = m.group(1)
    if not (root / rel).is_file():
        print(f"FAIL: bibliography path missing {rel}")
        missing += 1

assert missing == 0, f"{missing} attachment paths missing locally"

print(
    f"OK: validate-sourcea-1000-s9-bibliography-v1 · "
    f"rows={len(s9_rows)} attachments verified · sa-0975"
)
PY
