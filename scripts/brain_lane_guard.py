#!/usr/bin/env python3
"""Shim → brain-os/scripts/brain_lane_guard.py (module load only — no __main__ on import)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CANON = Path(__file__).resolve().parents[1] / "brain-os/scripts/brain_lane_guard.py"


def _load_canon():
    name = "_brain_lane_guard_canon"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _CANON)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_canon = _load_canon()

is_worker_prompt = _canon.is_worker_prompt
check_text = _canon.check_text
refuse_payload = _canon.refuse_payload
write_loop_headsup = _canon.write_loop_headsup

if __name__ == "__main__":
    raise SystemExit(_canon.main())
