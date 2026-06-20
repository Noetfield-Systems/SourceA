# SourceA Site v1 — QUARANTINED (UI experiment)

**Moved:** 2026-06-11  
**Do not scan in Brain / E2E / hub verify.**

| | |
|--|--|
| **Location** | `/Users/sinakazemnezhad/Desktop/_quarantine/sourcea-site-v1/` |
| **Port** | `13060` (manual only — not part of production spine) |
| **Status** | UI lineage test — Linear hero + Stripe docs — **not production** |

## Run (manual only)

```bash
python3 /Users/sinakazemnezhad/Desktop/_quarantine/sourcea-site-v1/server.py
```

- http://127.0.0.1:13060/
- http://127.0.0.1:13060/docs

## Frozen production surfaces (unchanged)

| Surface | Port |
|---------|------|
| Legacy hub `agent-control-panel/` | 13020 |
| Agent Pro | 13050 |

This folder intentionally **does not** live under `SourceA/` so fleet scans and Brain E2E skip it.
