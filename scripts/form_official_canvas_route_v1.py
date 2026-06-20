#!/usr/bin/env python3
"""Resolve FORM_OFFICIAL Hub → Canvas path from nerve map (M1 only — INCIDENT-029)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NERVE_MAP = ROOT / "data/form_official_nerve_map_v1.json"
M1_DEFAULT = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
)
H1_HUB_URL = "http://127.0.0.1:13020/"
FORM_PAGE_URL = "http://127.0.0.1:13020/form/"
H2_MACHINES_URL = "http://127.0.0.1:13020/machines/"
MUSEUM_URL = "http://127.0.0.1:13020/legacy/"
FORM_ACTION_ID = "founder-open-integrity-form"


def _expand(raw: str) -> Path:
    return Path(str(raw or "").replace("~", str(Path.home()))).expanduser()


def _load_nerve() -> dict:
    if not NERVE_MAP.is_file():
        return {}
    try:
        return json.loads(NERVE_MAP.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def hub_canvas_target() -> dict:
    """Hub FORM_OFFICIAL always opens M1 Canvas — never scratch gather packs (INCIDENT-029)."""
    nerve = _load_nerve()
    canvas = nerve.get("canvas") or {}
    m1 = _expand(str(canvas.get("m1_canvas") or str(M1_DEFAULT)))
    if not m1.is_file():
        m1 = M1_DEFAULT

    open_count = 0
    open_ids: list[str] = []
    edition = str((nerve.get("active") or {}).get("edition") or "final_fix_gathering")
    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from live_founder_decision_form_v1 import payload  # noqa: WPS433

        form = payload()
        open_count = int(form.get("open_questions_count") or 0)
        open_ids = [str(q.get("id") or "") for q in (form.get("open_questions") or [])]
        edition = str(form.get("active_form_edition") or edition)
    except Exception:
        open_ids = list((nerve.get("active") or {}).get("open_ids") or [])
        open_count = int((nerve.get("active") or {}).get("open_count") or len(open_ids))

    head_card: dict | None = None
    form_headline = ""
    try:
        from live_founder_decision_form_v1 import founder_readable_cards, _form_headline  # noqa: WPS433

        cards = founder_readable_cards(limit=1)
        head_card = cards[0] if cards else None
        form_headline = _form_headline(open_count)
    except Exception:
        pass

    subject_preview = (head_card or {}).get("subject") or "—"
    if open_count:
        form_line = (
            f"{open_count} open PICKs logged · M1 Canvas · "
            "INCIDENT-037 block ON · agent-submit forbidden"
        )
        form_hub_line = (
            f"{open_count} open PICKs · M1 Canvas · {subject_preview[:72]} · guard active"
        )
    else:
        form_line = "Form clear — 0 open PICKs logged · guard PASS"
        form_hub_line = "Form clear — 0 open PICKs · guard PASS"

    return {
        "surface": "m1",
        "path": str(m1),
        "canvas_data": "",
        "label": "Official founder form (M1)",
        "button_label": "M1 Canvas",
        "form_line": form_line,
        "form_headline": form_headline,
        "founder_head_card": head_card,
        "form_page_url": FORM_PAGE_URL,
        "hint": (
            f"M1 Canvas Pending confirmations · {open_count} open PICKs logged · "
            "founder supremacy guard · agent-submit blocked"
        ),
        "open_gath_ids": sorted(i for i in open_ids if i.startswith("Q-GATH-")),
        "edition": edition,
        "view": "pending-confirmations",
        "open_canvas_hint": (
            "Hub form page = same PICK rows as M1 Canvas slot D · "
            "Cursor Canvas optional beside chat"
        ),
        "hub_url": H1_HUB_URL,
        "h2_machines_url": H2_MACHINES_URL,
        "museum_url": MUSEUM_URL,
        "form_action_id": FORM_ACTION_ID,
        "form_api": "/api/live-founder-decision-form-v1",
        "open_pick_ids_head": open_ids[:5],
        "form_hub_line": form_hub_line,
    }


def form_hub_line() -> str:
    return str(hub_canvas_target().get("form_hub_line") or "")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="FORM_OFFICIAL Hub canvas route (M1 only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = hub_canvas_target()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result.get('surface')}: {result.get('path')}")
    return 0 if result.get("path") else 1


if __name__ == "__main__":
    raise SystemExit(main())
