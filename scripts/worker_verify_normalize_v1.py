#!/usr/bin/env python3
"""Normalize sa verify strings for Worker loop — fast lane only (no 3 min shell)."""
from __future__ import annotations

import re

FAST_VERIFY = "cd scripts && bash worker_verify_ultra_v1.sh"
SLOW_MARKERS = (
    "build-sina-command-panel.py",
    "validate-anti-staleness-bundle-v1.sh",
    "validate-sourcea-e2e-full",
    "validate-sourcea-e2e-standard",
)


def normalize_worker_verify(verify: str | None, *, role: str = "") -> str:
    """Return Worker-loop-safe verify commands (~7s, not full fleet)."""
    raw = (verify or "").strip()
    low = raw.lower()

    if not raw:
        return FAST_VERIFY if "verify" in role else raw

    if "worker_verify_fast" in low:
        return raw

    # Full find_critical_bugs / strict build / anti-staleness bundle → fast script
    if any(m in raw for m in SLOW_MARKERS):
        return _merge_task_specific(raw, FAST_VERIFY)

    if re.search(r"find_critical_bugs\.py", raw) and "SINA_FCB_FAST" not in raw:
        return _merge_task_specific(raw, FAST_VERIFY)

    if "strict build" in low and "build-sina-command-panel" in low:
        return _merge_task_specific(raw, FAST_VERIFY)

    return raw


def _merge_task_specific(original: str, fast: str) -> str:
    """Keep sa-specific validators; drop fleet/hub rebuild lines."""
    kept: list[str] = []
    for part in re.split(r"\s*&&\s*|\n", original):
        p = part.strip()
        if not p:
            continue
        if any(m in p for m in SLOW_MARKERS):
            continue
        if "find_critical_bugs.py" in p and "SINA_FCB_FAST" not in p:
            continue
        if p.startswith("cd scripts"):
            continue
        kept.append(p)
    if kept:
        return fast + " && " + " && ".join(kept)
    return fast


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Normalize worker verify string")
    ap.add_argument("verify", nargs="?", default="")
    ap.add_argument("--role", default="verify")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = normalize_worker_verify(args.verify, role=args.role)
    if args.json:
        import json

        print(json.dumps({"in": args.verify, "out": out}))
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
