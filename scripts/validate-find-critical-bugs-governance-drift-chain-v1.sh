#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import ast
from pathlib import Path

src = Path("find_critical_bugs.py").read_text(encoding="utf-8")
assert "validate-governance-drift-v1.sh" in src, "governance-drift missing from find_critical_bugs"
tree = ast.parse(src)
mod = next(n for n in tree.body if isinstance(n, ast.Assign) and any(
    isinstance(t, ast.Name) and t.id == "SHELL_VALIDATORS" for t in n.targets
))
validators = ast.literal_eval(mod.value)
row = next(v for v in validators if v.get("id") == "validate-governance-drift-v1.sh")
assert row.get("severity") == "critical", f"governance-drift must be critical, got {row.get('severity')}"
print("OK: validate-find-critical-bugs-governance-drift-chain-v1 · critical shell validator wired")
PY
