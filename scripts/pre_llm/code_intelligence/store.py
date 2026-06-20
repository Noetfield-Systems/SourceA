"""D1 SSOT — ~/.sina/code_intelligence_v1.json (atomic rebuild only)."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
CODE_INTEL_SSOT_PATH = STATE_DIR / "code_intelligence_v1.json"

SCHEMA = "code-intelligence-v1"

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    ".cursor",
    ".idea",
}

SKIP_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".bin",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp4",
    ".mov",
    ".sqlite",
    ".db",
}

MAX_FILE_BYTES = 512_000

# v1 mandatory; optional extensions indexed but not AST-parsed
MANDATORY_EXTENSIONS = {".py", ".pyi"}
OPTIONAL_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}


def load_snapshot() -> dict:
    if not CODE_INTEL_SSOT_PATH.is_file():
        return {}
    try:
        data = json.loads(CODE_INTEL_SSOT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def write_canonical(*, canonical: dict, task_id: str = "default") -> None:
    """Append-safe rebuild — replace latest atomically; never leave partial JSON."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    envelope = load_snapshot() if CODE_INTEL_SSOT_PATH.is_file() else {"schema": SCHEMA, "builds": {}}
    envelope["schema"] = SCHEMA
    envelope["generated_at"] = canonical.get("generated_at")
    envelope["path"] = str(CODE_INTEL_SSOT_PATH)
    envelope["latest"] = canonical
    envelope.setdefault("builds", {})[task_id] = canonical

    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(envelope, indent=2, sort_keys=True))
            fh.write("\n")
        os.replace(tmp, CODE_INTEL_SSOT_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_canonical() -> dict:
    snap = load_snapshot()
    latest = snap.get("latest") or {}
    if latest.get("schema") == SCHEMA:
        return latest
    return {}
