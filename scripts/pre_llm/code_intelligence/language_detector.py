"""Extension-based language detection."""
from __future__ import annotations

from pathlib import Path

EXTENSION_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".sh": "shell",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
}


def detect_language(path: str) -> str:
    p = Path(path)
    ext = p.suffix.lower()
    if ext in EXTENSION_LANGUAGE:
        return EXTENSION_LANGUAGE[ext]
    name = p.name.lower()
    if name in ("dockerfile", "containerfile"):
        return "dockerfile"
    if name == "makefile":
        return "makefile"
    return "unknown"


def detect_languages(paths: list[str]) -> list[dict]:
    return [{"path": p, "language": detect_language(p)} for p in paths]
