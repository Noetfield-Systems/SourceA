# Live Status Map v1

Status: report/spec only, not deployed  
Implementation: `scripts/brain_core_v1/live_status_probe.py`  
Probe CLI: `scripts/brain_core_v1/run_decision_probe.py`

## Purpose

Live Status Map v1 gives Decision Core deterministic status evidence before any model draft. It is a small HTTP probe layer for the founder-approved status signals in `reports/locked-definitions-v1.json`.

## Probe Targets

| Status key | Target |
|---|---|
| `sourcea_app_http_status` | `https://sourcea.app` |
| `forge_terminal_runtime_status` | `https://sourcea.app/sourcea/forge/terminal` |
| `specific_run_public_proof_status` | `https://sourcea.app/sourcea/proof/live` |

## Normalized Statuses

The public probe status vocabulary is:

- `good`: HTTP status is 2xx or 3xx.
- `degraded`: HTTP status is available but outside 2xx/3xx.
- `unknown`: request failed, timed out, or no HTTP status was available.

The Decision Core adapter converts:

- `good` -> `ok`
- `degraded` -> `degraded`
- `unknown` -> `unknown`

## Probe Row Shape

Each status key returns:

```json
{
  "key": "sourcea_app_http_status",
  "target": "https://sourcea.app",
  "status": "good",
  "timestamp": "2026-06-30T15:38:00Z",
  "http_status": 200,
  "latency_ms": 123.0,
  "error": null
}
```

## Public-Language Rule

The probe never uses `PASS` or `BLOCK` as public status language. Errors are reduced to safe diagnostic strings and scrubbed for `PASS`, `BLOCK`, and provider terms before returning.

## CLI Modes

Manual mocked status map:

```bash
python3 scripts/brain_core_v1/run_decision_probe.py \
  --message "Is SourceA live?" \
  --status-json '{"sourcea_app_http_status":"ok"}'
```

Real live probe status map:

```bash
python3 scripts/brain_core_v1/run_decision_probe.py \
  --message "Is SourceA live?" \
  --live-probe
```

The CLI returns both the live probe map and the converted status map when `--live-probe` is used.

## Test Rule

Tests for the live-status probe mock network calls. No test depends on real network availability.
