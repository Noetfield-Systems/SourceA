#!/usr/bin/env python3
"""DL-U1 — Trust Center publish (T0-safe sanitized dashboard).

Law: data/trust-center-v1.json · docs/SOURCEA_DISCLOSURE_LADDER_AND_PUBLIC_VOICE_LOCKED_v1.md
Output: SourceA-landing/green-unified/trust/index.html + data/trust-signals-public-v1.json
Receipt: ~/.sina/trust-center-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "trust-center-v1.json"
OUT_HTML = ROOT / "SourceA-landing" / "green-unified" / "trust" / "index.html"
OUT_JSON = ROOT / "SourceA-landing" / "green-unified" / "data" / "trust-signals-public-v1.json"
RECEIPT = SINA / "trust-center-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _public_signals() -> dict:
    disc = _read_json(SINA / "disclosure-ladder-receipt-v1.json")
    mcp = _read_json(SINA / "mcp-stack-free-tier-receipt-v1.json")
    return {
        "schema": "trust-signals-public-v1",
        "saved_at": _now(),
        "disclosure_line": disc.get("public_one_line")
        or "Prove every agent action — before the model runs, after it ships.",
        "perimeter": "Powered by SourceA governed execution — advisory only · no custody · no payment initiation.",
        "mcp_free_tier_summary": (mcp.get("mcp_stack_line") or "").split("·")[0].strip() or "Free-tier integrations first",
        "proof_urls": [
            "https://sourcea-landing.vercel.app/sourcea/",
            "https://www.noetfield.com/copilot/pilot/",
            "https://www.trustfield.ca/demo",
        ],
    }


def _render_html(signals: dict, ssot: dict) -> str:
    perimeter = signals.get("perimeter") or ""
    headline = signals.get("disclosure_line") or ""
    urls = signals.get("proof_urls") or []
    url_rows = "\n".join(
        f'        <li><a href="{u}" rel="noopener">{u}</a></li>' for u in urls
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trust Center | SourceA</title>
  <meta name="description" content="T0-safe governance summary — advisory only · no custody · no payment initiation." />
  <link rel="stylesheet" href="../sourcea.css" />
</head>
<body class="sa-v2" data-sa-page="trust-center">
  <main id="main-content" class="ar-container" style="max-width:720px;margin:2rem auto;padding:1rem;">
    <h1>SourceA Trust Center</h1>
    <p class="next">{headline}</p>
    <p>{perimeter}</p>
    <h2>Public proof</h2>
    <ul>
{url_rows}
    </ul>
    <p class="sub">DL-U1 · T0 public tier · no architecture internals on this page.</p>
  </main>
  <script type="application/json" id="trust-signals-public">{json.dumps(signals)}</script>
</body>
</html>
"""


def run_publish(*, write: bool = True) -> dict:
    ssot = _read_json(SSOT)
    signals = _public_signals()
    html = _render_html(signals, ssot)
    row = {
        "schema": "trust-center-receipt-v1",
        "saved_at": _now(),
        "ok": ssot.get("schema") == "trust-center-v1",
        "upgrade_id": "DL-U1",
        "public_url": ssot.get("public_url"),
        "gate_k_url": ssot.get("gate_k_url"),
        "html_path": str(OUT_HTML.relative_to(ROOT)),
        "json_path": str(OUT_JSON.relative_to(ROOT)),
        "disclosure_tier": ssot.get("disclosure_tier"),
        "trust_center_line": f"Trust Center · T0 · {ssot.get('gate_k_url') or ssot.get('public_url')}",
    }
    if write:
        OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_HTML.write_text(html, encoding="utf-8")
        OUT_JSON.write_text(json.dumps(signals, indent=2) + "\n", encoding="utf-8")
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        disc_ssot = _read_json(ROOT / "data" / "disclosure-ladder-v1.json")
        for idea in disc_ssot.get("upgrade_ideas") or []:
            if idea.get("id") == "DL-U1":
                idea["status"] = "shipped"
                idea["note"] = f"Published {OUT_HTML.relative_to(ROOT)} · gate K path live"
        disc_ssot_path = ROOT / "data" / "disclosure-ladder-v1.json"
        disc_ssot_path.write_text(json.dumps(disc_ssot, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Trust Center publish DL-U1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_publish(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("trust_center_line") or "—")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
