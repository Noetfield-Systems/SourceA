#!/usr/bin/env python3
"""Activate WitnessBC toolkits freemium Quick Start + client sandbox (P0-15).

Patches witnessbc-site SSOT + renders sandbox page + rebuilds deploy.
Run: python3 scripts/witnessbc_freemium_sandbox_activate_v1.py --json
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WBC = ROOT / "witnessbc-site"
DATA = WBC / "data" / "toolkits-v1.json"
CONTENT = WBC / "content" / "toolkits.html"
RENDER = WBC / "scripts" / "render_toolkits_v1.py"
CSS = WBC / "assets" / "toolkits.css"
SANDBOX_JS = WBC / "assets" / "toolkits-sandbox.js"
E2E = WBC / "scripts" / "validate_witnessbc_full_e2e_v1.sh"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _patch_toolkits_json(data: dict) -> None:
    data["saved_at"] = _now()
    data["freemium"] = {
        "active": True,
        "label": "Freemium active",
        "free_forever": True,
        "upgrade_optional": True,
    }
    data["quickstart"] = {
        "active": True,
        "steps": [
            "Start free — open a template (HTML, copy/paste)",
            "Run minimum standard — 5-minute checklist on page",
            "Upgrade only if you repeat the work — Pro PDF optional",
        ],
        "default_free_path": "/toolkits/free/sourcing/",
        "default_free_label": "Start free — Source Log",
        "sandbox_path": "/toolkits/sandbox/",
        "sandbox_label": "Client sandbox",
    }
    data["sandbox"] = {
        "active": True,
        "path": "toolkits/sandbox/",
        "title": "Toolkit Sandbox (Free)",
        "intro": (
            "Try all six accountability templates in your browser — no account, no payment. "
            "Edits stay local (localStorage). Education only — not legal advice."
        ),
        "honesty": "browser_local_only · no server storage · freemium forever",
        "templates_from": "free_pages",
    }


def _patch_quickstart_html(html: str) -> str:
    hero_old = """        <div class="hero-actions toolkit-actions">
          <button class="btn btn-primary" type="button" data-buy="pro">Buy Pro Bundle ($99)</button>
          <a class="btn btn-outline" href="#quickstart">Quick start</a>"""
    hero_new = """        <div class="hero-actions toolkit-actions" data-freemium-active="true">
          <a class="btn btn-primary" href="/toolkits/free/sourcing/">Start free</a>
          <a class="btn btn-outline" href="/toolkits/sandbox/">Client sandbox</a>
          <a class="btn btn-ghost" href="#quickstart">Quick start</a>"""
    if hero_old in html:
        html = html.replace(hero_old, hero_new)

    pills_add = """          <span class="toolkit-pill toolkit-pill-live">Freemium active</span>
          <span class="toolkit-pill">Sandbox · browser-local</span>
"""
    if "toolkit-pill-live" not in html:
        html = html.replace(
            '          <span class="toolkit-pill">No outcome sales</span>\n',
            '          <span class="toolkit-pill">No outcome sales</span>\n' + pills_add,
        )

    qs_old = """          <div class="toolkit-picker-actions" style="margin-top:1rem">
            <button class="btn btn-outline btn-sm" type="button" data-buy="starter">Buy Starter ($39)</button>
            <button class="btn btn-primary btn-sm" type="button" data-buy="pro">Buy Pro ($99)</button>
          </div>"""
    qs_new = """          <div class="toolkit-freemium-status" data-freemium-active="true" role="status">
            <span class="toolkit-pill toolkit-pill-live">Freemium ON</span>
            <span class="toolkit-pill">6 free templates · sandbox · Pro optional</span>
          </div>
          <div class="toolkit-picker-actions toolkit-freemium-actions" style="margin-top:1rem">
            <a class="btn btn-primary btn-sm" href="/toolkits/free/sourcing/">Start free — Source Log</a>
            <a class="btn btn-outline btn-sm" href="/toolkits/sandbox/">Open sandbox</a>
            <button class="btn btn-ghost btn-sm" type="button" data-buy="starter">Pro: Starter ($39)</button>
            <button class="btn btn-ghost btn-sm" type="button" data-buy="pro">Pro: Bundle ($99)</button>
          </div>"""
    if qs_old in html:
        html = html.replace(qs_old, qs_new)
    return html


def _sandbox_js() -> str:
    return """(function () {
  "use strict";
  var STORAGE_PREFIX = "wbc-sandbox-v1:";
  var templates = [];
  var select = null;
  var area = null;
  var status = null;

  function loadTemplates(cb) {
    fetch("/data/toolkits-v1.json", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        templates = (d && d.free_pages) || [];
        if (typeof cb === "function") cb();
      })
      .catch(function () { if (typeof cb === "function") cb(); });
  }

  function slug() {
    return select ? select.value : "";
  }

  function tpl() {
    var s = slug();
    for (var i = 0; i < templates.length; i++) {
      if (templates[i].slug === s) return templates[i];
    }
    return templates[0] || null;
  }

  function persist() {
    if (!area) return;
    try { localStorage.setItem(STORAGE_PREFIX + slug(), area.value); } catch (_e) {}
  }

  function restore() {
    if (!area) return;
    var row = tpl();
    var saved = "";
    try { saved = localStorage.getItem(STORAGE_PREFIX + slug()) || ""; } catch (_e) {}
    area.value = saved || (row && row.template_text) || "";
    if (status) {
      status.textContent = "Sandbox · browser-local · " + (row ? row.title : "—");
    }
  }

  function wire() {
    select = document.getElementById("sandbox-select");
    area = document.getElementById("sandbox-editor");
    status = document.getElementById("sandbox-status");
    if (!select || !area) return;
    select.addEventListener("change", function () { restore(); });
    area.addEventListener("input", persist);
    var copyBtn = document.getElementById("sandbox-copy");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        area.select();
        if (navigator.clipboard) navigator.clipboard.writeText(area.value).catch(function () {});
      });
    }
    var resetBtn = document.getElementById("sandbox-reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        try { localStorage.removeItem(STORAGE_PREFIX + slug()); } catch (_e) {}
        restore();
      });
    }
    restore();
  }

  function init() {
    loadTemplates(wire);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
"""


def _patch_render_py(src: str) -> str:
    if "def _sandbox_body" in src:
        return src

    sandbox_fn = '''

def _sandbox_body(data: dict) -> str:
    sandbox = data.get("sandbox") or {}
    pages = data.get("free_pages") or []
    options = "\\n".join(
        f'            <option value="{p["slug"]}">{p["title"]}</option>' for p in pages
    )
    intro = sandbox.get("intro") or "Try templates in your browser — free forever."
    honesty = sandbox.get("honesty") or "browser_local_only"
    return f"""  <main id="main-content">
    <section class="page-hero page-hero-toolkit">
      <div class="container">
        <p class="section-eyebrow">Toolkits · Sandbox · Freemium</p>
        <h1>Client sandbox — try templates free</h1>
        <p class="section-lead">{intro} <strong>Education only — not legal advice.</strong></p>
        <div class="toolkit-freemium-status" data-freemium-active="true" role="status">
          <span class="toolkit-pill toolkit-pill-live">Freemium active</span>
          <span class="toolkit-pill">{honesty}</span>
        </div>
        <div class="hero-actions toolkit-actions">
          <a class="btn btn-ghost" href="/toolkits.html">← Toolkits hub</a>
          <a class="btn btn-outline" href="/toolkits/free/sourcing/">Start free — Source Log</a>
        </div>
      </div>
    </section>

    <section class="toolkit-section" id="sandbox">
      <div class="container">
        <article class="surface-card toolkit-sandbox-card">
          <div class="toolkit-sandbox-toolbar">
            <label for="sandbox-select">Template</label>
            <select id="sandbox-select" class="toolkit-sandbox-select" aria-label="Choose template">
{options}
            </select>
            <button class="btn btn-outline btn-sm" type="button" id="sandbox-copy">Copy</button>
            <button class="btn btn-ghost btn-sm" type="button" id="sandbox-reset">Reset</button>
          </div>
          <p id="sandbox-status" class="meta toolkit-sandbox-status">Sandbox · loading…</p>
          <textarea id="sandbox-editor" class="toolkit-textarea toolkit-sandbox-editor" spellcheck="false" aria-label="Sandbox editor"></textarea>
        </article>
      </div>
    </section>
  </main>
"""
'''

    insert_at = src.find("\ndef _assemble_subpage(")
    if insert_at < 0:
        raise SystemExit("FAIL: render_toolkits_v1.py missing _assemble_subpage anchor")
    src = src[:insert_at] + sandbox_fn + src[insert_at:]

    if "# Training hub" in src and "sandbox_dir" not in src:
        src = src.replace(
            "    # Training hub\n    train_dir = ROOT / \"toolkits\" / \"training\"",
            """    # Sandbox (freemium · browser-local)
    sandbox_dir = ROOT / "toolkits" / "sandbox"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    sandbox_html = _assemble_subpage(
        body=_sandbox_body(data),
        title="Toolkit Sandbox (Free) – WitnessBC",
        description=(data.get("sandbox") or {}).get("intro", "Free toolkit sandbox."),
        canonical="https://witnessbc.com/toolkits/sandbox/",
    )
    sandbox_html = sandbox_html.replace(
        _scripts_block(["toolkits", "site"]),
        _scripts_block(["toolkits", "toolkits-sandbox", "site"]),
    )
    (sandbox_dir / "index.html").write_text(sandbox_html, encoding="utf-8")
    written.append("toolkits/sandbox/index.html")

    # Training hub
    train_dir = ROOT / "toolkits" / "training\"""",
        )

    if 'href="toolkits/' in src and 'href="/toolkits/sandbox/' not in src:
        src = src.replace(
            'html = html.replace(\'href="toolkits/\', \'href="/toolkits/\')',
            'html = html.replace(\'href="toolkits/\', \'href="/toolkits/\')\n'
            '    html = html.replace(\'href="/toolkits.html#quickstart"\', \'href="/toolkits.html#quickstart"\')',
        )

    return src


def _patch_css(css: str) -> str:
    block = """
.toolkit-pill-live {
  border-color: var(--accent, #0d9488);
  color: var(--accent, #0d9488);
  background: rgba(13, 148, 136, 0.08);
}

.toolkit-freemium-status {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.toolkit-freemium-actions .btn-primary {
  order: -2;
}

.toolkit-sandbox-card {
  max-width: 960px;
  margin: 0 auto;
}

.toolkit-sandbox-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.toolkit-sandbox-select {
  min-width: 220px;
  padding: 0.45rem 0.65rem;
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--border-subtle);
  background: var(--surface);
}

.toolkit-sandbox-editor {
  min-height: 420px;
  width: 100%;
}

.toolkit-sandbox-status {
  margin-bottom: 0.75rem;
}
"""
    if "toolkit-pill-live" not in css:
        css += block
    return css


def _patch_e2e(sh: str) -> str:
    marker = """checked=$((checked + 1))
curl -sS -L "${BASE%/}/toolkits.html" -o "$TMP"
if grep -q 'data-buy="pro"' "$TMP" && grep -q 'Education only' "$TMP"; then"""
    add = """checked=$((checked + 1))
curl -sS -L "${BASE%/}/toolkits.html" -o "$TMP"
if grep -q 'data-freemium-active="true"' "$TMP" && grep -q '/toolkits/sandbox/' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] freemium quickstart + sandbox links on toolkits hub"
else
  echo "FAIL [marker] toolkits hub missing freemium/sandbox activation"
  fail=1
fi

"""
    if "freemium quickstart + sandbox" not in sh:
        sh = sh.replace(marker, add + marker)
    return sh


def activate(*, build: bool = True) -> dict:
    steps: list[dict] = []
    if not WBC.is_dir():
        return {"ok": False, "error": "witnessbc-site missing"}

    data = json.loads(DATA.read_text(encoding="utf-8"))
    _patch_toolkits_json(data)
    DATA.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "toolkits-v1.json", "ok": True})

    html = CONTENT.read_text(encoding="utf-8")
    html2 = _patch_quickstart_html(html)
    if html2 != html:
        CONTENT.write_text(html2, encoding="utf-8")
        steps.append({"step": "content/toolkits.html", "ok": True})
    else:
        steps.append({"step": "content/toolkits.html", "ok": True, "note": "already patched"})

    SANDBOX_JS.write_text(_sandbox_js(), encoding="utf-8")
    steps.append({"step": "assets/toolkits-sandbox.js", "ok": True})

    render_src = RENDER.read_text(encoding="utf-8")
    render_new = _patch_render_py(render_src)
    if render_new != render_src:
        RENDER.write_text(render_new, encoding="utf-8")
    steps.append({"step": "render_toolkits_v1.py", "ok": True})

    css = CSS.read_text(encoding="utf-8")
    css2 = _patch_css(css)
    if css2 != css:
        CSS.write_text(css2, encoding="utf-8")
    steps.append({"step": "toolkits.css", "ok": True})

    if E2E.is_file():
        e2e = E2E.read_text(encoding="utf-8")
        e2e2 = _patch_e2e(e2e)
        if e2e2 != e2e:
            E2E.write_text(e2e2, encoding="utf-8")
        steps.append({"step": "validate_witnessbc_full_e2e", "ok": True})

    if build:
        for cmd in (
            [sys.executable, str(WBC / "scripts" / "assemble_pages.py")],
            [sys.executable, str(RENDER), "--json"],
            [sys.executable, str(WBC / "scripts" / "build.py")],
        ):
            proc = subprocess.run(cmd, cwd=str(WBC), capture_output=True, text=True, timeout=300)
            steps.append({
                "step": " ".join(cmd[1:]),
                "ok": proc.returncode == 0,
                "tail": (proc.stdout or proc.stderr or "")[-200:],
            })
            if proc.returncode != 0:
                return {"ok": False, "steps": steps, "error": "build failed"}

    drift = subprocess.run(
        ["bash", str(ROOT / "scripts" / "validate-witnessbc-ui-zero-drift-v1.sh")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    steps.append({
        "step": "validate-witnessbc-ui-zero-drift-v1.sh",
        "ok": drift.returncode == 0,
        "tail": (drift.stdout or drift.stderr or "")[-200:],
    })
    if drift.returncode != 0:
        return {"ok": False, "steps": steps, "error": "witnessbc zero-drift FAIL"}

    return {"ok": True, "at": _now(), "steps": steps, "sandbox_url": "/toolkits/sandbox/"}


def main() -> int:
    ap = __import__("argparse").ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()
    result = activate(build=not args.no_build)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("OK" if result.get("ok") else "FAIL", result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
