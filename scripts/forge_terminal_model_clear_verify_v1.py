#!/usr/bin/env python3
"""Light verify — model lock + clear thread (Mac founder session, no Playwright)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
JS = ROOT / "apps/forge-terminal-v1/terminal.js"
HTML = ROOT / "apps/forge-terminal-v1/index.html"


def main() -> int:
    js = JS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    checks = [
        ("model_lock_key", "MODEL_LOCK_KEY" in js),
        ("hidden_gemini_flash_lite", "HIDDEN_DEFAULT_MODELS" in js and "gemini-3.1-flash-lite" in js),
        ("no_apply_role_on_refresh", "applyRolePick(lastRole, row, true)" not in js),
        ("clear_guard", "chatClearGuardUntil" in js),
        ("lock_on_send", "lockUserModel(model)" in js),
        ("gpt4o_default_html", 'value="gpt-4o" selected' in html),
        ("no_gemini31_in_html", "gemini-3.1-flash-lite" not in html),
        ("toolbar_clear", 'id="btn-clear-chat-toolbar"' in html),
        ("version", "4.11.8-buttons-e2e" in js),
    ]
    from forge_terminal_desktop_mesh_v1 import clear_thread, load_thread

    clear_thread(workspace_path=None)
    row = load_thread(workspace_path=None)
    checks.append(("clear_thread_api", bool(row.get("ok")) and len(row.get("turns") or []) == 0))

    failed = [name for name, ok in checks if not ok]
    out = {"ok": not failed, "checks": {n: ok for n, ok in checks}, "failed": failed}
    print(json.dumps(out, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
