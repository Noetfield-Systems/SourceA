#!/usr/bin/env bash
# validate-hub-copy-no-terminal-v1.sh — sa-0856 / sa-0806 hub copy vs founder no-Terminal law
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-founder-docs-no-terminal-v1.sh

python3 - <<'PY'
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
law = ROOT / "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md"
assert law.is_file(), "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md missing"

app = (ROOT / "agent-control-panel/assets/app.js").read_text(encoding="utf-8")
assert "no Terminal" in app or "never Terminal" in app, "app.js missing no-Terminal founder copy"
assert "Never ask the founder to run Terminal" in app, "agent loop no-Terminal law copy missing"

from hub_essentials_index import READ_CHAIN
chain_paths = [r.get("path") for r in READ_CHAIN]
assert "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md" in chain_paths, (
    "hub essentials read chain missing no-Terminal law"
)

from noetfield_unified_guide import noetfield_unified_guide_payload

nf = noetfield_unified_guide_payload()
shell_re = re.compile(
    r"(?i)(^|\s)(cd |bash |python3 |curl |\./scripts/|serve-sina-command\.sh|\.sh\b)",
)
for act in nf.get("mac_actions") or []:
    hint = act.get("hint") or ""
    assert not shell_re.search(hint), (
        f"noetfield mac_actions shell hint forbidden: {act.get('label')!r} -> {hint!r}"
    )
    assert "one tap" in hint.lower() or "actions tab" in hint.lower() or "worker hub" in hint.lower(), (
        f"mac_actions hint must be one-tap hub copy: {act.get('label')!r}"
    )

# Legacy essentials render must not expose shell commands in mac_actions block
sb_start = app.index("function renderNoetfieldUnifiedGuide")
sb_end = app.index("function renderEssentials", sb_start)
guide_fn = app[sb_start:sb_end]
assert "sc-nf-cmd" in guide_fn, "renderNoetfieldUnifiedGuide mac_actions render missing"
assert "Mac founder" in guide_fn or "one-tap" in guide_fn.lower(), "guide section label missing"

bad_instruct = re.compile(
    r"(open Terminal|copy (?:this )?(?:command|into Terminal)|paste (?:into|in) Terminal)",
    re.I,
)
assert not bad_instruct.search(app), "app.js has forbidden Terminal instruct copy"

with urllib.request.urlopen("http://127.0.0.1:13020/api/worker-hub/v1", timeout=15) as resp:
    wh = json.loads(resp.read().decode())
policies = wh.get("policy_links") or []
assert any(p.get("id") == "no-terminal" for p in policies), "worker hub missing no-terminal policy link"

print(
    "OK: validate-hub-copy-no-terminal-v1 · law in read chain · "
    f"mac_actions={len(nf.get('mac_actions') or [])} hub-only · worker-hub policy wired (sa-0856)"
)
PY
