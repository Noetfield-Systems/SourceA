#!/usr/bin/env python3
"""FR-003 — EXTERNAL_CRITIC report-only default on paste paths (form Q-CRITIC YES)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "external-critic-default-v1.json"
LAW = ROOT / "brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"

PASTE_SIGNALS = (
    r"\bchatgpt\b",
    r"\bchat\s*gpt\b",
    r"\bgpt\s+said\b",
    r"\bexternal\s+critic\b",
    r"\badvisor\s+paste\b",
    r"\baudit\s+paste\b",
    r"trust\s+os\b",
    r"decision\s+cloud\b",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_external_paste(text: str) -> bool:
    low = (text or "").lower()
    return any(re.search(pat, low, re.I) for pat in PASTE_SIGNALS)


def classify_paste(text: str, *, source: str = "") -> dict:
    """Return input class — never promotes critic to ASF order."""
    src = (source or "").lower()
    if is_external_paste(text) or "critic" in src or "gpt" in src:
        return {
            "input_class": "EXTERNAL_CRITIC",
            "mode": "report_only",
            "may_steers_build": False,
            "requires_adopt_row": True,
            "law": str(LAW.relative_to(ROOT)) if LAW.is_file() else "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
        }
    return {"input_class": "UNCLASSIFIED", "mode": "disk_first", "may_steers_build": False}


def wire_default(*, reason: str = "maintainer_fr003") -> dict:
    """Persist FR-003 latch — report-only default for external paste."""
    row = {
        "schema": "external-critic-default-v1",
        "wired_at": _now(),
        "reason": reason,
        "default_mode": "report_only",
        "input_class": "EXTERNAL_CRITIC",
        "form_pick": "Q-CRITIC YES",
        "founder_request": "FR-2026-06-05-003",
        "law": "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
        "rule_mdc": ".cursor/rules/chatgpt-external-critic.mdc",
        "forbidden": "auto-apply build specs from GPT paste",
        "agent_reply_prefix": "INPUT CLASS: EXTERNAL_CRITIC",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def is_wired() -> bool:
    if not RECEIPT.is_file():
        return False
    try:
        row = json.loads(RECEIPT.read_text(encoding="utf-8"))
        return row.get("default_mode") == "report_only"
    except Exception:
        return False


def validate_wiring() -> tuple[bool, str]:
    if not LAW.is_file():
        return False, "missing CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"
    mdc = ROOT / ".cursor/rules/chatgpt-external-critic.mdc"
    if not mdc.is_file():
        return False, "missing chatgpt-external-critic.mdc"
    if not is_wired():
        return False, "external-critic-default-v1.json not wired"
    return True, "ok"


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="FR-003 EXTERNAL_CRITIC default wiring")
    p.add_argument("--wire", action="store_true")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--classify", default="", help="Classify sample text")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.wire:
        out = wire_default()
    elif args.classify:
        out = classify_paste(args.classify)
    elif args.validate:
        ok, msg = validate_wiring()
        out = {"ok": ok, "message": msg}
    else:
        out = {"wired": is_wired(), "receipt": str(RECEIPT)}
    if args.json or True:
        print(json.dumps(out, indent=2))
    return 0 if (out.get("ok", True) and out.get("wired", True)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
