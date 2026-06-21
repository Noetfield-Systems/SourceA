#!/usr/bin/env python3
"""Assemble Witness AI multi-page site from partials + content/*.html."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTIALS = ROOT / "partials"
CONTENT = ROOT / "content"
DATA = ROOT / "data" / "pages.json"
CTA_DATA = ROOT / "data" / "cta.json"
PROOF_SCENARIOS_DATA = ROOT / "data" / "proof-scenarios-v1.json"
LEARN_CHAPTERS_DATA = ROOT / "data" / "learn-chapters-v1.json"
COHORT_DATA = ROOT / "data" / "cohort.json"
STRIPE_DATA = ROOT / "data" / "stripe-links-v1.json"
STRIPE_RECEIPT = Path.home() / ".sina" / "witnessbc-stripe-inject-receipt-v1.json"

NAV_KEYS = ("platform", "lifecycle", "proof", "pricing", "policy", "compare", "faq", "sources", "learn", "toolkits", "observe")


def _cta_tokens() -> dict[str, str]:
    if not CTA_DATA.is_file():
        raise SystemExit("FAIL assemble: missing data/cta.json")
    cta = json.loads(CTA_DATA.read_text(encoding="utf-8"))
    return {
        "PROOF_MAILTO": cta["proof_mailto"],
        "LIVE_DEMO_URL": cta["live_demo_url"],
        "TOOLKITS_URL": cta.get("toolkits_url", "toolkits.html"),
        "OBSERVE_URL": cta.get("observe_url", "observe/index.html"),
        "NOETFIELD_PILOT_URL": cta.get("noetfield_pilot_url", "policy.html"),
        "W1_DEMO_FILM_URL": cta.get("w1_demo_film_url", "assets/w1-demo.mp4"),
        "COMMERCIAL_SHORT_URL": cta.get("commercial_short_url", cta["live_demo_url"]),
        "COMMERCIAL_SHORT_NOTE": cta.get(
            "commercial_short_note", "Live governance walkthrough · interactive until W1 film ships"
        ),
    }


def _cohort_tokens() -> dict[str, str]:
    if not COHORT_DATA.is_file():
        raise SystemExit("FAIL assemble: missing data/cohort.json")
    cohort = json.loads(COHORT_DATA.read_text(encoding="utf-8"))
    return {
        "COHORT_NAME": cohort["name"],
        "COHORT_SEATS_MAX": str(cohort["seats_max"]),
        "COHORT_SEATS_REMAINING": str(cohort["seats_remaining"]),
        "COHORT_TAGLINE": cohort["tagline"],
    }


def _stripe_tokens() -> dict[str, str]:
    toolkits = "toolkits.html"
    if STRIPE_RECEIPT.is_file():
        try:
            receipt = json.loads(STRIPE_RECEIPT.read_text(encoding="utf-8"))
            tokens = receipt.get("tokens") or {}
            if tokens:
                return {str(k): str(v) for k, v in tokens.items()}
        except (OSError, json.JSONDecodeError):
            pass
    if not STRIPE_DATA.is_file():
        return {
            "STRIPE_PRO_99_URL": toolkits,
            "STRIPE_STARTER_39_URL": toolkits,
            "STRIPE_TEAM_149_URL": toolkits,
            "STRIPE_CORRECTIONS_9_URL": toolkits,
            "STRIPE_SOURCING_19_URL": toolkits,
            "STRIPE_TOOLKITS_HUB_URL": toolkits,
            "STRIPE_LINKS_LIVE": "false",
        }
    data = json.loads(STRIPE_DATA.read_text(encoding="utf-8"))
    links = data.get("links") or {}

    def _live(key: str) -> bool:
        u = str(links.get(key) or "")
        return bool(u) and u.startswith("https://buy.stripe.com/") and "REPLACE_" not in u

    def _url(key: str) -> str:
        u = str(links.get(key) or "")
        return u if _live(key) else toolkits

    live_count = sum(1 for k in links if _live(k))
    return {
        "STRIPE_PRO_99_URL": _url("pro"),
        "STRIPE_STARTER_39_URL": _url("starter"),
        "STRIPE_TEAM_149_URL": _url("team"),
        "STRIPE_CORRECTIONS_9_URL": _url("corrections"),
        "STRIPE_SOURCING_19_URL": _url("sourcing"),
        "STRIPE_TOOLKITS_HUB_URL": toolkits,
        "STRIPE_LINKS_LIVE": "true" if live_count >= 3 else "false",
    }


def _site_tokens() -> dict[str, str]:
    return {**_cta_tokens(), **_cohort_tokens(), **_stripe_tokens()}


def _apply_tokens(text: str, tokens: dict[str, str]) -> str:
    for k, v in tokens.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def _nav_classes(active: str) -> dict[str, str]:
    active = (active or "").lower()
    out: dict[str, str] = {
        "ACTIVE_PLATFORM": "",
        "ACTIVE_RESOURCES": "",
    }
    for key in NAV_KEYS:
        cls = "is-active" if key == active else ""
        out[f"ACTIVE_{key.upper()}"] = cls
    if active in ("platform", "lifecycle", "policy", "compare"):
        out["ACTIVE_PLATFORM"] = "is-active"
    if active in ("faq", "sources", "learn", "toolkits", "observe"):
        out["ACTIVE_RESOURCES"] = "is-active"
    return out


def _scripts_block(names: list[str]) -> str:
    lines = []
    if "control-plane" in names:
        lines.append('  <script src="assets/control-plane.js"></script>')
    if "trust-signals" in names:
        lines.append('  <script src="assets/trust-signals.js"></script>')
    if "proof-demo" in names:
        lines.append('  <script src="assets/proof-demo.js"></script>')
    if "learn-hub" in names:
        lines.append('  <script src="assets/learn-hub.js"></script>')
    if "toolkits" in names:
        lines.append('  <script src="assets/toolkits.js"></script>')
    if "toolkits-sandbox" in names:
        lines.append('  <script src="assets/toolkits-sandbox.js"></script>')
    if "observe-feed" in names:
        lines.append('  <script src="assets/observe-feed.js"></script>')
    if "site" in names:
        lines.append('  <script src="assets/site.js"></script>')
    return "\n".join(lines) + "\n</body>\n</html>\n"


def _load_partial(name: str) -> str:
    path = PARTIALS / name
    if not path.is_file():
        raise SystemExit(f"FAIL assemble: missing partials/{name}")
    return path.read_text(encoding="utf-8")


def assemble_page(
    page: dict,
    head: str,
    header: str,
    breadcrumb_tpl: str,
    footer_tpl: str,
    refs_list: str,
    cta: dict[str, str],
) -> str:
    body_file = CONTENT / page["content"]
    if not body_file.is_file():
        raise SystemExit(f"FAIL assemble: missing content/{page['content']}")

    nav = _nav_classes(page.get("nav_active", ""))
    tokens = {**cta, **nav, "BREADCRUMB_LABEL": page.get("breadcrumb", "")}

    header_out = _apply_tokens(header, tokens)
    breadcrumb_out = ""
    if page.get("breadcrumb"):
        breadcrumb_out = _apply_tokens(breadcrumb_tpl, tokens)

    footer = _apply_tokens(
        footer_tpl.replace(
            "{{SCRIPTS}}",
            _scripts_block(page.get("scripts", ["site"])),
        ),
        tokens,
    )

    head_out = _apply_tokens(
        head.replace("{{TITLE}}", page["title"])
        .replace("{{DESCRIPTION}}", page["description"])
        .replace("{{CANONICAL}}", page["canonical"])
        .replace("{{BODY_CLASS}}", page.get("body_class", "")),
        tokens,
    )
    if page.get("file") == "toolkits.html" or page.get("body_class", "").startswith("page-toolkits"):
        head_out = head_out.replace(
            "</head>",
            '  <link rel="stylesheet" href="assets/toolkits.css" />\n</head>',
        )

    body = _apply_tokens(body_file.read_text(encoding="utf-8"), tokens)
    if "{{REFS_LIST}}" in body:
        body = body.replace("{{REFS_LIST}}", refs_list)

    if page.get("file") == "proof.html" and PROOF_SCENARIOS_DATA.is_file():
        scenarios_json = PROOF_SCENARIOS_DATA.read_text(encoding="utf-8").strip()
        body += (
            '\n  <script type="application/json" id="wbcProofScenarios">'
            + scenarios_json
            + "</script>\n"
        )

    if page.get("file") == "learn.html" and LEARN_CHAPTERS_DATA.is_file():
        learn_json = _apply_tokens(
            LEARN_CHAPTERS_DATA.read_text(encoding="utf-8").strip(), tokens
        )
        body += (
            '\n  <script type="application/json" id="wbcLearnChapters">'
            + learn_json
            + "</script>\n"
        )

    return head_out + header_out + breadcrumb_out + body + footer


def assemble_all() -> dict:
    pages_data = json.loads(DATA.read_text(encoding="utf-8"))
    head = _load_partial("head.html")
    header = _load_partial("header.html")
    breadcrumb_tpl = _load_partial("breadcrumb.html")
    footer_tpl = _load_partial("footer.html")
    refs_list = _load_partial("refs-list.html")
    cta = _site_tokens()

    written: list[str] = []
    for page in pages_data["pages"]:
        html = assemble_page(page, head, header, breadcrumb_tpl, footer_tpl, refs_list, cta)
        out_path = ROOT / page["file"]
        out_path.write_text(html, encoding="utf-8")
        written.append(page["file"])

    return {"ok": True, "pages": written, "count": len(written)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = assemble_all()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: assembled {result['count']} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
