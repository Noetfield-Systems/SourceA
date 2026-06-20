#!/usr/bin/env python3
"""FAIL if REPO_EXECUTION_LOGS latest.yaml next_task != disk queue_sa."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "REPO_EXECUTION_LOGS" / "sourcea" / "latest.yaml"

sys.path.insert(0, str(ROOT / "scripts"))
from queue_sa_pick_lib_v1 import queue_sa_from_disk  # noqa: E402


def _read_latest_next() -> str:
    if not LATEST.is_file():
        return ""
    for line in LATEST.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("next_task:"):
            return line.split(":", 1)[1].strip()
    return ""


def main() -> int:
    qsa = queue_sa_from_disk()
    nxt = _read_latest_next()
    if not qsa:
        print("OK: validate-repo-execution-log-queue-v1 · no queue_sa on disk")
        return 0
    if nxt != qsa:
        print(f"FAIL: latest.yaml next_task={nxt!r} != queue_sa {qsa!r}")
        return 1
    print(f"OK: validate-repo-execution-log-queue-v1 · next_task={qsa}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
