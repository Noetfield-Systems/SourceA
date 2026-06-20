#!/usr/bin/env bash
# validate-founder-hub-only-moat-v1.sh — sa-0972 ACT hub-only vs terminal-first moat crosswalk
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-hub-copy-no-terminal-v1.sh
bash validate-founder-docs-no-terminal-v1.sh

python3 - <<'PY'
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"

# Law stack
for rel in (
    "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md",
    "brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md",
):
    p = ROOT / rel
    assert p.is_file(), f"missing {rel}"
    text = p.read_text(encoding="utf-8")
    assert "Terminal" in text or "terminal" in text.lower(), f"{rel} missing terminal law"

# AUTO-RUN must stay disabled per founder commercial law
flag = SINA / "auto-run-disabled-v1.flag"
assert flag.is_file(), "auto-run-disabled-v1.flag must exist (Cursor AUTO-RUN not P0)"

commercial = (ROOT / "brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md").read_text(
    encoding="utf-8"
)
assert "FORBIDDEN" in commercial and "AUTO-RUN" in commercial, "commercial law must forbid AUTO-RUN P0"

# Worker hub policy link
with urllib.request.urlopen("http://127.0.0.1:13020/api/worker-hub/v1", timeout=15) as resp:
    wh = json.loads(resp.read().decode())
policies = wh.get("policy_links") or []
no_term = next((p for p in policies if p.get("id") == "no-terminal"), None)
assert no_term, "worker hub missing no-terminal policy"
assert no_term.get("path"), "no-terminal policy must cite law doc path"

# Architecture moat reference
arch = ROOT / "brain-os/law/SOURCEA_REFERENCE_ARCHITECTURE_CONSTELLATION_LOCKED_v1.md"
assert arch.is_file(), "architecture constellation missing"
assert "no Terminal" in arch.read_text(encoding="utf-8"), "architecture moat #2 missing"

print(
    "OK: validate-founder-hub-only-moat-v1 · hub-copy PASS · auto-run flag ON · "
    f"worker-hub policy={no_term.get('id')} · sa-0972"
)
PY
