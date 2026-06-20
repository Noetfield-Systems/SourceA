#!/usr/bin/env python3
"""Personal Database (Layer A) — ingestion and hub API for Sina Command."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sina_command_lib import MONO_DATA, MONO_ROOT, parse_frontmatter, personal_db_detail  # noqa: E402

IMPORTS_RAW = MONO_ROOT / "imports" / "raw"
PIPELINE_STAGING = MONO_ROOT / "pipeline" / "staging"
SKIP_RAW_NAMES = {".gitkeep", ".gitignore", "README.md"}
L2 = MONO_DATA / "L2-knowledge"
L3 = MONO_DATA / "L3-process"

ALLOWED_OPEN = [
    MONO_ROOT.resolve(),
    IMPORTS_RAW.resolve(),
    PIPELINE_STAGING.resolve(),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> dict:
    created = []
    for d in (IMPORTS_RAW, PIPELINE_STAGING, L2, L3):
        if not d.is_dir():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d.relative_to(MONO_ROOT)))
    return {"ok": True, "created": created}


def _slug(name: str) -> str:
    base = Path(name).stem.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base[:48] or "import"


def scan_imports() -> dict:
    ensure_dirs()
    staged: list[dict] = []
    errors: list[str] = []
    if not IMPORTS_RAW.is_dir():
        return {"ok": False, "error": "imports/raw missing", "staged": []}

    for src in sorted(IMPORTS_RAW.iterdir()):
        if src.name.startswith(".") or not src.is_file():
            continue
        if src.name in SKIP_RAW_NAMES:
            continue
        if src.suffix.lower() not in (".md", ".txt", ".json"):
            errors.append(f"skipped unsupported: {src.name}")
            continue
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            errors.append(f"{src.name}: {e}")
            continue
        slug = _slug(src.name)
        dest = PIPELINE_STAGING / f"{slug}--{src.stat().st_mtime_ns}.md"
        header = (
            f"---\nid: staging-{slug}\n"
            f"title: {src.stem}\n"
            f"layer: L2-knowledge\n"
            f"access: [owner, agent]\n"
            f"status: draft\n"
            f"source_file: {src.name}\n"
            f"imported_at: {_now()}\n"
            f"---\n\n"
        )
        body = text if src.suffix.lower() == ".md" else f"```\n{text[:12000]}\n```\n"
        dest.write_text(header + body, encoding="utf-8")
        staged.append(
            {
                "source": src.name,
                "staging_path": str(dest.relative_to(MONO_ROOT)),
                "title": src.stem,
            }
        )
        archive = IMPORTS_RAW / "_processed"
        archive.mkdir(exist_ok=True)
        shutil.move(str(src), str(archive / src.name))

    return {
        "ok": True,
        "staged_count": len(staged),
        "staged": staged,
        "errors": errors,
        "imports_raw": str(IMPORTS_RAW),
        "staging_dir": str(PIPELINE_STAGING),
    }


def list_staging() -> list[dict]:
    if not PIPELINE_STAGING.is_dir():
        return []
    rows = []
    for path in sorted(PIPELINE_STAGING.glob("*.md")):
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        rows.append(
            {
                "path": str(path.relative_to(MONO_ROOT)),
                "id": meta.get("id", path.stem),
                "title": meta.get("title", path.stem),
                "status": meta.get("status", "draft"),
            }
        )
    return rows


def promote_draft(*, staging_path: str, target_layer: str = "L2-knowledge") -> dict:
    ensure_dirs()
    rel = staging_path.strip().lstrip("/")
    src = (MONO_ROOT / rel).resolve()
    if not src.is_file() or PIPELINE_STAGING.resolve() not in src.parents:
        return {"ok": False, "error": "invalid staging path"}
    if target_layer not in ("L2-knowledge", "L3-process"):
        return {"ok": False, "error": "target_layer must be L2-knowledge or L3-process"}

    text = src.read_text(encoding="utf-8", errors="replace")
    meta = parse_frontmatter(text)
    eid = meta.get("id") or _slug(src.stem)
    dest_dir = MONO_DATA / target_layer.replace("L2-knowledge", "L2-knowledge").replace("L3-process", "L3-process")
    if target_layer == "L2-knowledge":
        dest_dir = L2
    else:
        dest_dir = L3
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = re.sub(r"[^a-z0-9-]", "-", eid.lower()) + ".md"
    dest = dest_dir / fname
    if not meta.get("status"):
        text = text.replace("status: draft", "status: active", 1) if "status: draft" in text else text
    elif meta.get("status") == "draft":
        text = re.sub(r"^status:\s*draft\s*$", "status: active", text, count=1, flags=re.MULTILINE)
    dest.write_text(text, encoding="utf-8")
    src.unlink(missing_ok=True)
    return {
        "ok": True,
        "promoted_to": str(dest.relative_to(MONO_ROOT)),
        "entry_id": eid,
    }


def resolve_open_path(rel: str) -> Path | None:
    target = (MONO_ROOT / rel.lstrip("/")).resolve()
    if not any(target == r or r in target.parents for r in ALLOWED_OPEN):
        return None
    return target if target.exists() else None


def personal_db_payload() -> dict:
    ensure_dirs()
    detail = personal_db_detail()
    detail["ok"] = True
    detail["mono_root"] = str(MONO_ROOT)
    detail["imports_raw"] = str(IMPORTS_RAW)
    detail["staging_dir"] = str(PIPELINE_STAGING)
    detail["staging_files"] = list_staging()
    detail["layer_legend"] = [
        {"id": "L0-meta", "title": "Meta & ingestion", "path": "data/L0-meta"},
        {"id": "L1-identity", "title": "Identity", "path": "data/L1-identity"},
        {"id": "L2-knowledge", "title": "Knowledge", "path": "data/L2-knowledge"},
        {"id": "L3-process", "title": "Process", "path": "data/L3-process"},
        {"id": "L4-agents", "title": "Agent mandates", "path": "data/L4-agents"},
    ]
    detail["access_legend"] = [
        {"id": "owner", "desc": "Founder-only"},
        {"id": "agent", "desc": "Copy agents may read when training"},
        {"id": "public", "desc": "Rare — safe external cite"},
    ]
    detail["law_path"] = "SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md"
    return detail


def handle_action(body: dict) -> dict:
    action = (body.get("action") or "status").strip().lower()
    if action in ("status", "report"):
        return personal_db_payload()
    if action == "ensure_dirs":
        return {**ensure_dirs(), **personal_db_payload()}
    if action == "scan":
        scan = scan_imports()
        return {**scan, **personal_db_payload()}
    if action == "promote_draft":
        return promote_draft(
            staging_path=body.get("staging_path") or "",
            target_layer=body.get("target_layer") or "L2-knowledge",
        )
    if action == "list_staging":
        return {"ok": True, "staging_files": list_staging()}
    return {"ok": False, "error": f"unknown action: {action}"}
