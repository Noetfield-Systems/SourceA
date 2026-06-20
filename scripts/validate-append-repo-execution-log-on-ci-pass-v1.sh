#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

mod = Path("append_repo_execution_log_v1.py").read_text(encoding="utf-8")
bugs = Path("find_critical_bugs.py").read_text(encoding="utf-8")

assert "append_on_ci_pass" in mod, "append_on_ci_pass missing"
assert "sa-0225" in mod, "sa-0225 marker missing in append module"
assert "latest.yaml" in mod, "latest.yaml write missing"
assert "append_repo_execution_log_v1" in bugs, "find_critical_bugs must import append module"
assert "append_on_ci_pass" in bugs, "find_critical_bugs must call append_on_ci_pass"
assert "sa-0225" in bugs, "sa-0225 marker missing in find_critical_bugs"
print("OK: validate-append-repo-execution-log-on-ci-pass-v1 · CI pass append wired (sa-0225)")
PY
