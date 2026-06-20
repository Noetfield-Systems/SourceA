# Cleanup manifest — SourceA root sprawl

**Status:** DRAFT — do not execute until ASF sets `APPROVED`  
**Generated:** 2026-06-19  
**Inventory:** `infra/cleanup/inventory-root.tsv`

## Approval

- [ ] Secret scan clear (`infra/cleanup/secret-scan-report.txt`)
- [ ] ASF reviewed proposed destinations
- [ ] Status → **APPROVED**

## Batch plan

| Batch | Theme | Max files | Commit prefix |
|-------|-------|-----------|---------------|
| 1 | Obvious law → `brain-os/law/` | 25 | `cleanup: batch-1 law` |
| 2 | Docs → `docs/locked/` | 25 | `cleanup: batch-2 docs` |
| 3 | Logs → `archive/logs/` | all `.log` | `cleanup: batch-3 logs` |
| 4 | Remainder triage | per manifest rows | `cleanup: batch-4 …` |

## Manifest rows

<!-- Agent fills from inventory-root.tsv — example row format:

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| ./AGENT_*.md | 4.0K | # Agent … | brain-os/law/ | 1 | move |

-->

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|
| _pending inventory run_ | | | | | |

## Notes

- Virlux stays under `labs/virlux/` — not root sprawl
- Do not move `START_HERE.md`, `data/*.json` SSOTs, or `brain-os/entry/` without explicit row
