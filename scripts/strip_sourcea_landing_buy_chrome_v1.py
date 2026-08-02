#!/usr/bin/env python3
"""Strip orphan homepage buy chrome from SourceA landing HTML (idempotent).

Removes triple-injected #sa-buy-bar, header "$750 audit" spam, and duplicate
Ops Health Product JSON-LD that was orphaned onto production outside git.

Law: Ops Health Audit stays on /audit + pricing — never homepage chrome.
Receipt: ~/.sina/sourcea-landing-buy-chrome-strip-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-landing-buy-chrome-strip-receipt-v1.json"

BUY_BAR_RE = re.compile(
    r'<div\s+id=["\']sa-buy-bar["\'][\s\S]*?</div>\s*'
    r'(?:<style>\s*body\s*\{\s*padding-bottom:\s*78px\s*!important\s*\}\s*</style>\s*)?',
    re.I,
)
HEADER_AUDIT_LINK_RE = re.compile(
    r'<a\s+href=["\']/audit["\'][^>]*>\s*or buy the \$750 audit[^<]*</a>',
    re.I,
)
OPS_PRODUCT_LD_RE = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']>\s*\{[^<]*?"Ops Health Audit"[^<]*?\}\s*</script>\s*',
    re.I,
)
BODY_PADDING_RE = re.compile(
    r'<style>\s*body\s*\{\s*padding-bottom:\s*78px\s*!important\s*\}\s*</style>\s*',
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def strip_html(text: str) -> tuple[str, dict[str, int]]:
    counts = {"buy_bar": 0, "header_audit": 0, "ops_ld": 0, "body_pad": 0}

    def _sub(rx: re.Pattern[str], key: str, src: str) -> str:
        new, n = rx.subn("", src)
        counts[key] += n
        return new

    out = text
    out = _sub(BUY_BAR_RE, "buy_bar", out)
    out = _sub(HEADER_AUDIT_LINK_RE, "header_audit", out)
    out = _sub(OPS_PRODUCT_LD_RE, "ops_ld", out)
    out = _sub(BODY_PADDING_RE, "body_pad", out)
    return out, counts


def strip_tree(root: Path) -> dict[str, Any]:
    changed: list[dict[str, Any]] = []
    scanned = 0
    for path in sorted(root.rglob("*.html")):
        scanned += 1
        raw = path.read_text(encoding="utf-8", errors="replace")
        new, counts = strip_html(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(
                {
                    "path": str(path.relative_to(root)),
                    "counts": counts,
                }
            )
    return {
        "schema": "sourcea-landing-buy-chrome-strip-v1",
        "at": _now(),
        "root": str(root),
        "scanned": scanned,
        "changed_count": len(changed),
        "changed": changed,
        "ok": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root",
        default=str(ROOT / "SourceA-landing" / "green-unified" / "dist"),
        help="HTML tree to strip (default: landing dist)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        row = {"ok": False, "error": f"missing root: {root}", "at": _now()}
        print(json.dumps(row, indent=2) if args.json else row["error"])
        return 1
    row = strip_tree(root)
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"strip-buy-chrome · scanned={row['scanned']} · changed={row['changed_count']} · ok=PASS"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
