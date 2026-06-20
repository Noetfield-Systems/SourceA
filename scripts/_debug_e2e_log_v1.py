"""Debug-mode NDJSON logger for E2E flake investigation (session fd6750)."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

LOG_PATH = Path(__file__).resolve().parents[1] / ".cursor" / "debug-fd6750.log"
SESSION_ID = "fd6750"


def dbg(
    *,
    hypothesis_id: str,
    location: str,
    message: str,
    data: dict[str, Any] | None = None,
    run_id: str = "pre-fix",
) -> None:
    import os

    if os.environ.get("SINA_E2E_DEBUG_LOG", "").strip() not in ("1", "true", "yes"):
        return
    # #region agent log
    payload = {
        "sessionId": SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    # #endregion
