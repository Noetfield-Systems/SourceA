#!/usr/bin/env python3
"""Classify file paths to UI upgrade surface_id — every form, app, website.

Law: brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md
SSOT: data/ui-upgrade-surface-registry-v1.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "ui-upgrade-surface-registry-v1.json"
HOME = Path.home()
MAC_LAW = HOME / "Desktop" / "MacLaw"

UI_SUFFIXES = frozenset({".html", ".css", ".js", ".jsx", ".tsx", ".vue", ".svelte", ".scss", ".less"})

# Longest-prefix wins — order matters (specific before general).
PREFIX_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "hub_form",
        (
            "agent-control-panel/form/",
            "scripts/hub_form_submit_v1.py",
            "scripts/form_official_canvas_route_v1.py",
        ),
    ),
    (
        "wtm_tab",
        (
            "agent-control-panel/assets/app.js",
            "agent-control-panel/assets/",
        ),
    ),
    (
        "worker_hub",
        (
            "agent-control-panel/worker-hub/",
            "agent-control-panel/command-center/",
            "agent-control-panel/legacy/",
            "agent-control-panel/machines/",
            "agent-control-panel/index.html",
            "agent-control-panel/app.js",
            "agent-control-panel/styles.css",
        ),
    ),
    (
        "sourcea_landing",
        (
            "SourceA-landing/green-unified/",
            "sourcea-site-v1/",
            "sourcea-site/",
        ),
    ),
    (
        "witnessbc_commercial",
        (
            "witnessbc-site/",
        ),
    ),
    (
        "generic_app",
        (
            "noetfield-site/",
            "trustfield-site/",
        ),
    ),
    (
        "mac_health",
        (
            "mac-health-guard/",
            "scripts/mac-health-standalone/",
            "scripts/mac-health-guard-server.py",
        ),
    ),
    (
        "routing_panel",
        ("routing-panel/",),
    ),
    (
        "mac_law_cockpit",
        (str(MAC_LAW / "public").replace(str(HOME) + "/", "~/") + "/",),
    ),
]

CANVAS_FORM_MARKERS = (
    "sourcea-system-integrity-100.canvas",
    "brain-cloud-mission-form.canvas",
    "live-founder-decision-form.canvas",
    "integrity-form",
    "form.canvas",
)


def _normalize(path: str | Path) -> Path:
    p = Path(str(path).replace("~/", str(HOME) + "/")).resolve()
    return p


def _rel_to_root(path: Path) -> str | None:
    try:
        return str(path.relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        pass
    try:
        rel = path.relative_to(HOME)
        return "~/" + str(rel).replace("\\", "/")
    except ValueError:
        return None


def is_ui_file(path: str | Path) -> bool:
    p = _normalize(path)
    if not p.is_file() and not str(path).endswith("/"):
        return False
    suffix = p.suffix.lower()
    if suffix in UI_SUFFIXES:
        return True
    name = p.name.lower()
    return ".canvas." in name or name.endswith(".canvas.tsx")


def classify_ui_path(path: str | Path) -> dict:
    p = _normalize(path)
    rel = _rel_to_root(p)
    if rel is None:
        return {
            "is_ui": False,
            "surface_id": None,
            "path": str(p),
            "reason": "outside_known_roots",
        }
    if not is_ui_file(p):
        return {
            "is_ui": False,
            "surface_id": None,
            "path": str(p),
            "rel": rel,
            "reason": "not_ui_suffix",
        }

    name_lower = p.name.lower()
    if rel.startswith("agent-control-panel/form/"):
        return {
            "is_ui": True,
            "surface_id": "hub_form",
            "path": str(p),
            "rel": rel,
            "reason": "hub_form_prefix",
        }
    if ".canvas." in name_lower and any(m in name_lower for m in CANVAS_FORM_MARKERS):
        return {
            "is_ui": True,
            "surface_id": "hub_form",
            "path": str(p),
            "rel": rel,
            "reason": "form_canvas",
        }

    for surface_id, prefixes in PREFIX_RULES:
        for prefix in prefixes:
            norm_prefix = prefix.replace("~/", str(HOME) + "/")
            if rel.startswith(prefix) or rel == prefix.rstrip("/"):
                return {
                    "is_ui": True,
                    "surface_id": surface_id,
                    "path": str(p),
                    "rel": rel,
                    "reason": f"prefix:{prefix}",
                }
            try:
                if str(p).startswith(str(Path(norm_prefix).resolve())):
                    return {
                        "is_ui": True,
                        "surface_id": surface_id,
                        "path": str(p),
                        "rel": rel,
                        "reason": f"abs_prefix:{prefix}",
                    }
            except OSError:
                pass

    if rel.startswith("agent-control-panel/"):
        return {
            "is_ui": True,
            "surface_id": "worker_hub",
            "path": str(p),
            "rel": rel,
            "reason": "agent-control-panel_fallback",
        }

    return {
        "is_ui": True,
        "surface_id": "generic_app",
        "path": str(p),
        "rel": rel,
        "reason": "unregistered_ui",
    }


def load_registry_surfaces() -> dict:
    if not REGISTRY.is_file():
        return {}
    row = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return row.get("surfaces") or {}


def main() -> int:
    ap = argparse.ArgumentParser(description="UI path classifier")
    ap.add_argument("--path", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = classify_ui_path(args.path)
    surfaces = load_registry_surfaces()
    sid = row.get("surface_id")
    row["registry_known"] = bool(sid and sid in surfaces)
    row["first_check_cmd"] = (
        f"python3 scripts/ui_upgrade_first_check_v1.py --surface {sid} --ack --json"
        if row.get("is_ui") and sid
        else None
    )
    row["checklist_cmd"] = (
        f"python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface {sid} --print-checklist"
        if row.get("is_ui") and sid
        else None
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"ui={row.get('is_ui')} surface={row.get('surface_id')} "
            f"rel={row.get('rel')} reason={row.get('reason')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
