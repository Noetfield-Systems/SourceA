#!/usr/bin/env python3
"""Gate commercial mailto CTAs until Workspace inbox verified (STAB-009).

Reads data/sourcea-inbox-live-status-v1.json (copied to /sourcea/data/ in dist).
Unverified mailto → fallback sandbox CTA or disabled state with honest label.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
STATUS_SRC = ROOT / "data" / "sourcea-inbox-live-status-v1.json"
JS_OUT = GREEN / "sourcea-cta-gate.js"


def build_js(status: dict) -> str:
    verified = {
        addr: row.get("verified", False)
        for addr, row in (status.get("inboxes") or {}).items()
    }
    fallback = status.get("fallback_cta") or {}
    return f"""/* sourcea-cta-gate:v1 — STAB-009 */
(function () {{
  var VERIFIED = {json.dumps(verified)};
  var FALLBACK = {json.dumps(fallback)};
  var MAILTO = /^mailto:([^?]+)/i;

  function gate(el) {{
    var href = el.getAttribute("href") || "";
    var m = href.match(MAILTO);
    if (!m) return;
    var addr = m[1].toLowerCase();
    if (VERIFIED[addr]) return;
    el.setAttribute("data-sa-cta-gated", "1");
    el.setAttribute("data-sa-original-href", href);
    if (FALLBACK.href) {{
      el.setAttribute("href", FALLBACK.href);
      var label = FALLBACK.label || "Start free sandbox";
      if (el.textContent && el.textContent.indexOf("@") >= 0) el.textContent = label;
    }} else {{
      el.setAttribute("href", "#");
      el.setAttribute("aria-disabled", "true");
      el.classList.add("sa-cta-gated");
    }}
    el.title = "Email inbox pending — use sandbox or intake form";
  }}

  function run() {{
    document.querySelectorAll('a[href^="mailto:"]').forEach(gate);
  }}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
}})();
"""


def sync_status_to_green() -> None:
    dest = GREEN / "data" / "sourcea-inbox-live-status-v1.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(STATUS_SRC.read_text(encoding="utf-8"), encoding="utf-8")


def inject_script_tag(html_path: Path) -> bool:
    text = html_path.read_text(encoding="utf-8")
    tag = '<script src="/sourcea/sourcea-cta-gate.js" defer></script>'
    if "sourcea-cta-gate.js" in text:
        return False
    if "</body>" not in text:
        return False
    html_path.write_text(text.replace("</body>", f"  {tag}\n</body>", 1), encoding="utf-8")
    return True


def main() -> int:
    status = json.loads(STATUS_SRC.read_text(encoding="utf-8"))
    JS_OUT.write_text(build_js(status), encoding="utf-8")
    sync_status_to_green()
    changed = 0
    for html in GREEN.rglob("*.html"):
        if "dist" in html.parts or "reference" in html.parts:
            continue
        if inject_script_tag(html):
            changed += 1
    print(json.dumps({"ok": True, "js": str(JS_OUT.relative_to(ROOT)), "html_injected": changed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
