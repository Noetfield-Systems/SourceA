#!/usr/bin/env python3
"""Founder voice SSOT pointers — LinkedIn · Hub notes · founder-language corpus."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUNDER_LANGUAGE = ROOT / "archive/attachments/founder-language"
LINKEDIN_VOICE = FOUNDER_LANGUAGE / "linkedin-voice.yaml"
LINKEDIN_PROFILE = (
    Path.home()
    / "Desktop/Noetfield-All-Documents/hierarchy/L2-reference/noetfield_commercial_positioning__linkedin-profile-hyper-commercial-v4.md"
)
FOUNDER_NOTES = Path.home() / ".sina/founder-notes.json"
TERMINOLOGY_DICT = ROOT / "SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md"
DIRECTION_TERMS = ROOT / "SOURCEA_FOUNDER_DIRECTION_TERMINOLOGY_LOCKED_v1.md"
NORM_MD = ROOT / "SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md"


def _load_linkedin_voice_summary() -> dict:
    if not LINKEDIN_VOICE.is_file():
        return {"ok": False}
    try:
        import yaml  # type: ignore

        row = yaml.safe_load(LINKEDIN_VOICE.read_text(encoding="utf-8")) or {}
        return {
            "ok": True,
            "path": str(LINKEDIN_VOICE),
            "headline": row.get("headline"),
            "category_line": row.get("category_line"),
            "products": [p.get("name") for p in (row.get("products") or [])],
            "sync_script": "scripts/sync_founder_linkedin_voice_v1.py",
            "skill": ".cursor/skills/founder-linkedin-language/SKILL.md",
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def payload() -> dict:
    notes_count = 0
    if FOUNDER_NOTES.is_file():
        try:
            import json

            notes_count = len(json.loads(FOUNDER_NOTES.read_text(encoding="utf-8")).get("notes") or [])
        except Exception:
            pass
    li = _load_linkedin_voice_summary()
    return {
        "ok": True,
        "schema": "founder-voice-sources-v1",
        "policy": "Form row copy + agent SAY must match founder voice from these sources — not agent jargon.",
        "linkedin_voice": li,
        "sources": [
            {
                "id": "linkedin_voice",
                "label": "LinkedIn founder voice pack",
                "path": str(LINKEDIN_VOICE) if LINKEDIN_VOICE.is_file() else None,
                "headline": li.get("headline"),
            },
            {
                "id": "founder_language_corpus",
                "label": "Founder language pack (messages + chat research)",
                "path": str(FOUNDER_LANGUAGE / "dictionary.yaml"),
                "master": str(FOUNDER_LANGUAGE / "FOUNDER_LANGUAGE_CORPUS_v3.md"),
                "forbidden": str(FOUNDER_LANGUAGE / "forbidden.yaml"),
            },
            {
                "id": "linkedin_profile",
                "label": "LinkedIn profile SOT (markdown)",
                "path": str(LINKEDIN_PROFILE) if LINKEDIN_PROFILE.is_file() else None,
                "alt_paths": [
                    str(FOUNDER_LANGUAGE / "phrase-corpus.yaml"),
                    str(Path.home() / "Desktop/The 777 Foundation/ops/outbound-ready/linkedin-oneliner.txt"),
                ],
            },
            {
                "id": "founder_notes",
                "label": "Sina Command founder notes (Hub)",
                "path": str(FOUNDER_NOTES),
                "count": notes_count,
            },
            {
                "id": "terminology_dict",
                "label": "Machine terminology dictionary",
                "path": str(TERMINOLOGY_DICT),
            },
            {
                "id": "direction_terms",
                "label": "Direction lock terms",
                "path": str(DIRECTION_TERMS),
            },
            {
                "id": "message_normalization",
                "label": "CAPS = intent (founder messages)",
                "path": str(NORM_MD),
            },
        ],
        "scan_order": [
            "linkedin_voice",
            "founder_language_corpus",
            "linkedin_profile",
            "founder_notes",
            "terminology_dict",
            "direction_terms",
        ],
    }


def main() -> int:
    import json

    print(json.dumps(payload(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
