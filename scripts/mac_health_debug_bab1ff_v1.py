"""Debug session bab1ff — NDJSON to MacLaw debug log (remove after verify)."""
from __future__ import annotations

import json
import time
from pathlib import Path

LOG = Path("/Users/sinakazemnezhad/Desktop/MacLaw/.cursor/debug-bab1ff.log")
LOG_FALLBACK = Path.home() / ".sina" / "debug-bab1ff.log"
SESSION = "bab1ff"


def dbg(*, hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    row = {
        "sessionId": SESSION,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    line = json.dumps(row, ensure_ascii=False) + "\n"
    for path in (LOG, LOG_FALLBACK):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line)
        except OSError:
            pass
