"""Debug session bab1ff — NDJSON dev trace, capped and edition-gated.

Personal edition only: this is the maintainer's own request-tracing
instrumentation, not a product feature. Commercial builds skip it entirely
so a customer's disk never accumulates a private developer's debug log.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from mac_health_edition_v1 import IS_PERSONAL, SINA

LOG = SINA / "debug-bab1ff.log"
SESSION = "bab1ff"
MAX_BYTES = 5 * 1024 * 1024  # rotate well before this becomes a liability


def _rotate_if_needed() -> None:
    try:
        if LOG.exists() and LOG.stat().st_size > MAX_BYTES:
            LOG.replace(LOG.with_suffix(".log.1"))
    except OSError:
        pass


def dbg(*, hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    if not IS_PERSONAL:
        return
    row = {
        "sessionId": SESSION,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    line = json.dumps(row, ensure_ascii=False) + "\n"
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        _rotate_if_needed()
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass
