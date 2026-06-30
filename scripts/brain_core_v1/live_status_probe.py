"""Real live-status probe for Brain Core v1.

The probe returns public-safe status words only: good, degraded, unknown.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SOURCEA_APP = "sourcea_app_http_status"
FORGE_TERMINAL = "forge_terminal_runtime_status"
PROOF_ROUTE = "specific_run_public_proof_status"

TARGETS = {
    SOURCEA_APP: "https://sourcea.app",
    FORGE_TERMINAL: "https://sourcea.app/sourcea/forge/terminal",
    PROOF_ROUTE: "https://sourcea.app/sourcea/proof/live",
}

GOOD = "good"
DEGRADED = "degraded"
UNKNOWN = "unknown"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _status_for_http(http_status: int | None) -> str:
    if http_status is None:
        return UNKNOWN
    if 200 <= http_status < 400:
        return GOOD
    return DEGRADED


def _safe_error(exc: BaseException) -> str:
    text = f"{exc.__class__.__name__}: {exc}"
    for token in ("PASS", "BLOCK", "OpenRouter"):
        text = text.replace(token, "internal-status-token")
    return text[:240]


def probe_url(
    key: str,
    target: str,
    *,
    timeout: float = 5.0,
    urlopen_func: Callable[..., object] = urlopen,
    timestamp_func: Callable[[], str] = utc_timestamp,
    perf_counter: Callable[[], float] = time.perf_counter,
) -> dict[str, object]:
    started = perf_counter()
    timestamp = timestamp_func()
    http_status: int | None = None
    error: str | None = None

    try:
        request = Request(
            target,
            headers={
                "User-Agent": "SourceA-Brain-Core-Live-Status-Probe/1.0",
                "Referer": "https://sourcea.app/",
            },
        )
        response = urlopen_func(request, timeout=timeout)
        http_status = int(getattr(response, "status", getattr(response, "code", 0)) or 0)
    except HTTPError as exc:
        http_status = int(exc.code)
        error = _safe_error(exc)
    except (URLError, TimeoutError, OSError) as exc:
        error = _safe_error(exc)
    latency_ms = round((perf_counter() - started) * 1000, 2)

    return {
        "key": key,
        "target": target,
        "status": _status_for_http(http_status),
        "timestamp": timestamp,
        "http_status": http_status,
        "latency_ms": latency_ms,
        "error": error,
    }


def probe_live_status_map(
    *,
    timeout: float = 5.0,
    urlopen_func: Callable[..., object] = urlopen,
    timestamp_func: Callable[[], str] = utc_timestamp,
    perf_counter: Callable[[], float] = time.perf_counter,
) -> dict[str, dict[str, object]]:
    return {
        key: probe_url(
            key,
            target,
            timeout=timeout,
            urlopen_func=urlopen_func,
            timestamp_func=timestamp_func,
            perf_counter=perf_counter,
        )
        for key, target in TARGETS.items()
    }


def decision_status_map(probe_map: dict[str, object]) -> dict[str, object]:
    """Convert probe statuses to the status vocabulary consumed by decision_core."""
    converted: dict[str, object] = {}
    for key, value in probe_map.items():
        status = value.get("status") if isinstance(value, dict) else value
        if status == GOOD:
            converted[key] = "ok"
        elif status == "ok":
            converted[key] = "ok"
        elif status == DEGRADED:
            converted[key] = "degraded"
        elif status == "unavailable":
            converted[key] = "unavailable"
        else:
            converted[key] = "unknown"
    return converted
