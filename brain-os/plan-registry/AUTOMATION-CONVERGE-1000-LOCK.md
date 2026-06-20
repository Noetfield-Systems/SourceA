# Automation Converge 1000 — RETIRED (do not use)

**Status:** **RETIRED 2026-06-07** · superseded by `AUTOMATION-FAST-TRACK-100-LOCK.md` (`ft-*` unique)  
**Was:** LOCKED · **Count:** 1000 · **Date:** 2026-06-07  
**Program:** [`AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md`](../contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md)

## Pick

```bash
bash scripts/plan-automation-converge-run.sh pick 1
```

## Regenerate

```bash
python3 scripts/generate-automation-converge-1000.py
```

## IDs

`ac-0001` … `ac-1000` in [`automation-converge-1000/REGISTRY.json`](automation-converge-1000/REGISTRY.json)

## Phases

| Phase | Focus |
|-------|--------|
| ac1 | Loop A headless autoloop |
| ac2 | inject→activate chain |
| ac3 | L2 dispatch gates |
| ac4 | s1 fast drain |
| ac5 | Loop B PromptOS |
| ac6 | Loop C hub↔Cursor |
| ac7 | Spine s4 minimal |
| ac8 | FORGE + TrustField ship |
| ac9 | Enforcement minimal |
| ac10 | L3 exit blockers |
