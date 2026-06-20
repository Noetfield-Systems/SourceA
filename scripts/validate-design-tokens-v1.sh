#!/usr/bin/env bash
# UI-6 — design tokens + page shell; migrated tabs must not use rainbow heroes or emoji actions.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TOKENS_CSS="$ROOT/agent-control-panel/assets/design-tokens-v1.css"
PAGE_SHELL_JS="$ROOT/agent-control-panel/assets/page-shell-v1.js"
SHELL_HTML="$ROOT/agent-control-panel/assets/shell.html"
INDEX_HTML="$ROOT/agent-control-panel/index.html"
APP_JS="$ROOT/agent-control-panel/assets/app.js"

test -f "$TOKENS_CSS" || { echo "FAIL: missing design-tokens-v1.css"; exit 1; }
test -f "$PAGE_SHELL_JS" || { echo "FAIL: missing page-shell-v1.js"; exit 1; }

for f in "$SHELL_HTML" "$INDEX_HTML"; do
  grep -q "design-tokens-v1.css" "$f" || { echo "FAIL: $f missing design-tokens-v1.css link"; exit 1; }
  grep -q "page-shell-v1.js" "$f" || { echo "FAIL: $f missing page-shell-v1.js script"; exit 1; }
done

grep -q "SCPageShell" "$PAGE_SHELL_JS" || { echo "FAIL: page-shell-v1.js must export SCPageShell"; exit 1; }
grep -q "renderPageShell" "$PAGE_SHELL_JS" || { echo "FAIL: page-shell-v1.js missing renderPageShell"; exit 1; }
grep -q "renderPanelV2" "$PAGE_SHELL_JS" || { echo "FAIL: page-shell-v1.js missing renderPanelV2"; exit 1; }
grep -q "sc-page-v2" "$TOKENS_CSS" || { echo "FAIL: design-tokens-v1.css missing sc-page-v2"; exit 1; }
grep -q "sc-panel-v2" "$TOKENS_CSS" || { echo "FAIL: design-tokens-v1.css missing sc-panel-v2"; exit 1; }

python3 - <<'PY'
import re
import sys
from pathlib import Path

app = (Path("agent-control-panel/assets/app.js")).read_text(encoding="utf-8")
errors: list[str] = []

def extract_fn(name: str) -> str:
    pat = rf"function {name}\(\) \{{"
    m = re.search(pat, app)
    if not m:
        errors.append(f"missing function {name}")
        return ""
    start = m.start()
    i = m.end()
    depth = 1
    while i < len(app) and depth:
        if app[i] == "{":
            depth += 1
        elif app[i] == "}":
            depth -= 1
        i += 1
    return app[start:i]

migrated = {
    "renderTrack": "track",
    "renderActionsPage": "actions",
    "renderAdvisorDiscussion": "advisor",
    "renderEssentials": "essentials",
}

for fn, label in migrated.items():
    block = extract_fn(fn)
    if not block:
        continue
    if "sc-page-hero--" in block:
        errors.append(f"{fn}: still uses sc-page-hero--* ({label} tab)")
    if "pageShell(" not in block:
        errors.append(f"{fn}: must use pageShell() ({label} tab)")
    if "panelV2(" not in block and fn != "renderTrack":
        errors.append(f"{fn}: must use panelV2() ({label} tab)")

actions = extract_fn("renderActionsPage")
if actions:
    if re.search(r"esc\(a\.icon", actions):
        errors.append("renderActionsPage: still prefixes buttons with a.icon emoji")
    if re.search(r"[\U0001F300-\U0001FAFF]", actions):
        errors.append("renderActionsPage: emoji found in migrated section")

run = extract_fn("renderGoal1AutoRun")
if run:
    if "sc-run-v2-kicker" in run:
        errors.append("renderGoal1AutoRun: duplicate sc-run-v2-kicker title remains")
    if "pageShell(" not in run:
        errors.append("renderGoal1AutoRun: must wrap in pageShell()")

if "function panelV2(" not in app:
    errors.append("app.js missing panelV2 helper")
if "function pageShell(" not in app:
    errors.append("app.js missing pageShell helper")

if errors:
    print("FAIL: validate-design-tokens-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("OK: validate-design-tokens-v1 · track/actions/advisor/essentials/run migrated")
PY

echo "OK: validate-design-tokens-v1"
