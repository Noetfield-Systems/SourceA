from urllib.error import HTTPError, URLError

from scripts.brain_core_v1.live_status_probe import (
    FORGE_TERMINAL,
    PROOF_ROUTE,
    SOURCEA_APP,
    TARGETS,
    decision_status_map,
    probe_live_status_map,
    probe_url,
)


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status


class FakeClock:
    def __init__(self) -> None:
        self.values = iter([10.0, 10.123])

    def __call__(self) -> float:
        return next(self.values)


def fixed_timestamp() -> str:
    return "2026-06-30T15:38:00Z"


def test_probe_url_good_status() -> None:
    def fake_urlopen(_request, timeout):
        assert timeout == 3.0
        return FakeResponse(200)

    row = probe_url(
        SOURCEA_APP,
        TARGETS[SOURCEA_APP],
        timeout=3.0,
        urlopen_func=fake_urlopen,
        timestamp_func=fixed_timestamp,
        perf_counter=FakeClock(),
    )
    assert row["status"] == "good"
    assert row["http_status"] == 200
    assert row["timestamp"] == "2026-06-30T15:38:00Z"
    assert row["latency_ms"] == 123.0
    assert row["error"] is None


def test_probe_url_degraded_http_status() -> None:
    def fake_urlopen(_request, timeout):
        assert timeout == 5.0
        return FakeResponse(503)

    row = probe_url(
        FORGE_TERMINAL,
        TARGETS[FORGE_TERMINAL],
        urlopen_func=fake_urlopen,
        timestamp_func=fixed_timestamp,
        perf_counter=FakeClock(),
    )
    assert row["status"] == "degraded"
    assert row["http_status"] == 503


def test_probe_url_http_error_degraded() -> None:
    def fake_urlopen(_request, timeout):
        assert timeout == 5.0
        raise HTTPError(TARGETS[PROOF_ROUTE], 500, "server BLOCK", {}, None)

    row = probe_url(
        PROOF_ROUTE,
        TARGETS[PROOF_ROUTE],
        urlopen_func=fake_urlopen,
        timestamp_func=fixed_timestamp,
        perf_counter=FakeClock(),
    )
    assert row["status"] == "degraded"
    assert row["http_status"] == 500
    assert "BLOCK" not in str(row["error"])


def test_probe_url_url_error_unknown() -> None:
    def fake_urlopen(_request, timeout):
        assert timeout == 5.0
        raise URLError("network PASS failed")

    row = probe_url(
        SOURCEA_APP,
        TARGETS[SOURCEA_APP],
        urlopen_func=fake_urlopen,
        timestamp_func=fixed_timestamp,
        perf_counter=FakeClock(),
    )
    assert row["status"] == "unknown"
    assert row["http_status"] is None
    assert "PASS" not in str(row["error"])


def test_probe_live_status_map_has_required_keys() -> None:
    def fake_urlopen(request, timeout):
        assert timeout == 5.0
        url = request.full_url
        if url == TARGETS[SOURCEA_APP]:
            return FakeResponse(200)
        if url == TARGETS[FORGE_TERMINAL]:
            return FakeResponse(503)
        return FakeResponse(302)

    rows = probe_live_status_map(
        urlopen_func=fake_urlopen,
        timestamp_func=fixed_timestamp,
        perf_counter=lambda: 1.0,
    )
    assert set(rows) == {SOURCEA_APP, FORGE_TERMINAL, PROOF_ROUTE}
    assert rows[SOURCEA_APP]["target"] == "https://sourcea.app"
    assert rows[FORGE_TERMINAL]["target"] == "https://sourcea.app/sourcea/forge/terminal"
    assert rows[PROOF_ROUTE]["target"] == "https://sourcea.app/sourcea/proof/live"
    assert rows[SOURCEA_APP]["status"] == "good"
    assert rows[FORGE_TERMINAL]["status"] == "degraded"
    assert rows[PROOF_ROUTE]["status"] == "good"


def test_decision_status_map_converts_probe_and_manual_statuses() -> None:
    converted = decision_status_map(
        {
            SOURCEA_APP: {"status": "good"},
            FORGE_TERMINAL: {"status": "degraded"},
            PROOF_ROUTE: "ok",
            "route_or_tool_status": "unavailable",
        }
    )
    assert converted == {
        SOURCEA_APP: "ok",
        FORGE_TERMINAL: "degraded",
        PROOF_ROUTE: "ok",
        "route_or_tool_status": "unavailable",
    }
