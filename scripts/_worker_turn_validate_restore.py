"""Backup/restore worker turn files around gate validators (no poisoned open turns)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from worker_turn_lib import ROUND_REPORT, TURN_STATE  # noqa: E402


def _backup() -> dict[Path, str]:
    out: dict[Path, str] = {}
    for p in (TURN_STATE, ROUND_REPORT):
        if p.is_file():
            out[p] = p.read_text(encoding="utf-8")
    return out


def _clear() -> None:
    for p in (TURN_STATE, ROUND_REPORT):
        if p.is_file():
            p.unlink()


def _restore(backup: dict[Path, str]) -> None:
    _clear()
    for p, text in backup.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def main() -> int:
    backup = _backup()
    _clear()
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "cursor_entry_gate.py"), "--role", "worker"],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        _restore(backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
