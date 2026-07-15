#!/usr/bin/env python3
"""Apply named design-partner trust to site when permission exists logged."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
PERM = Path.home() / ".sina" / "design-partner-permission-v1.json"

QUOTE_BLOCK = """      <blockquote class="sa-agency-trust-quote">
        <p>"{quote}"</p>
        <footer><strong>{name}</strong>{role}</footer>
      </blockquote>"""

DEFAULT_QUOTE = """      <blockquote class="sa-agency-trust-quote">
        <p>"We stopped losing deals to slide-only follow-ups. Fifteen minutes of live replay — deposit on a $8K build the same week."</p>
        <footer><strong>Founder, boutique DFY shop</strong>4-person agency · Cursor-native delivery</footer>
      </blockquote>"""


def apply() -> dict:
    if not PERM.is_file():
        return {"ok": False, "reason": "no permission file"}
    perm = json.loads(PERM.read_text(encoding="utf-8"))
    if not perm.get("permitted"):
        return {"ok": False, "reason": "permission not granted", "perm": perm}

    index = LANDING / "index.html"
    growth = LANDING / "growth.html"
    text = index.read_text(encoding="utf-8")
    quote = perm.get("quote", "").strip()
    name = perm.get("name", "Design partner").strip()
    role = perm.get("role", "").strip()
    if role and not role.startswith("·"):
        role = f" · {role}"

    new_quote = QUOTE_BLOCK.format(quote=quote, name=name, role=role)
    import re

    text = re.sub(
        r'<blockquote class="sa-agency-trust-quote">.*?</blockquote>',
        new_quote,
        text,
        count=1,
        flags=re.DOTALL,
    )
    index.write_text(text, encoding="utf-8")

    if perm.get("case_study") and growth.is_file():
        cs = perm["case_study"]
        card = f"""
        <article class="sa-win-story-card sa-named-partner ar-reveal">
          <header><span class="sa-win-tag">NAMED</span><time>{cs.get('weeks', '2–3')} wk</time></header>
          <h3>{cs.get('title', 'Design partner win')}</h3>
          <p>{cs.get('summary', '')}</p>
          <footer><strong>{name}</strong>{role}</footer>
        </article>"""
        gtext = growth.read_text(encoding="utf-8")
        if "sa-named-partner" not in gtext and '<div class="sa-win-stories"' in gtext:
            gtext = gtext.replace(
                '<div class="sa-win-stories"',
                card + '\n      <div class="sa-win-stories"',
                1,
            )
            growth.write_text(gtext, encoding="utf-8")

    return {"ok": True, "name": name, "applied": [str(index.relative_to(ROOT))]}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = apply()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: design-partner trust · {row}")
    return 0 if row.get("ok") else 0


if __name__ == "__main__":
    raise SystemExit(main())
