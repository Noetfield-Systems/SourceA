#!/usr/bin/env python3
"""Kaizen handler — NOTIFY pgrst reload (machine_safe)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import _apply_via_psycopg, ensure_env  # noqa: WPS433

    ensure_env()
    row = _apply_via_psycopg("NOTIFY pgrst, 'reload schema';")
    print(row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
