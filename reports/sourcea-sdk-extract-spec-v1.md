# sourcea-sdk Extract Spec — P1 Chain Tool

**Saved:** 2026-07-01T23:58:00Z  
**Status:** spec_only — no extract until founder approves  
**Authority:** `brain-os/law/SOURCEA_CHAIN_TOOLS_PUBLISH_LOCKED_v1.md` · `packages/sourcea-boot/PUBLISH_PLAN_LOCKED_v1.md`  
**Prerequisite:** Phase 0 complete — public GitHub eval path live; PyPI Phase 0b optional

---

## Purpose

Extract a **portable Python package** (`sourcea-sdk`) from the monorepo governance receipt spine so developers can sign, append, and replay agent actions **after** `sourcea-boot` PASS — without running the full SourceA factory on Mac.

**Category:** Infrastructure between developer and AI (Graphify class) — not a new agent.

---

## Relationship to sourcea-boot

| Layer | Tool | When it runs | Output |
|-------|------|--------------|--------|
| **Pre-flight** | `sourcea-boot` | Before any agent work | `BOOT_REPORT.json` · exit 0 PASS / 1 BLOCK |
| **During/after** | `sourcea-sdk` | After boot PASS, on each controlled action | Signed governance receipt + spine event |

**Law:** Boot gate is mandatory first step (SW1). SDK never replaces boot — it extends the chain with durable receipts.

```bash
# Intended developer flow (P1)
sourcea-boot --json          # PASS required
sourcea-sdk sign --intent …  # append receipt + optional spine bind
sourcea-sdk replay --last    # verify checksum + spine linkage
```

Portable mode writes under `.sourcea/` (mirrors boot’s portable contract). Factory mode may delegate to `~/.sina/governance-event-spine-v1.jsonl` when spine bind is enabled.

---

## Extract path (monorepo → package)

### Source modules (candidate)

| Monorepo path | Role in SDK |
|---------------|-------------|
| `scripts/governance_event_spine_v1.py` | Append-only spine · event types · checksum · replay |
| `scripts/commit_intent_v1.py` | Intent → gatekeeper → spine → receipt pattern (trim demo/copilot paths) |
| `scripts/rt_live_gate_v1.py` | Receipt checksum + spine bind helper (portable subset) |
| `shared/types/` (Zod/JSON schemas) | Receipt + spine event schema exports |

### Package layout (target)

```
packages/sourcea-sdk/
  pyproject.toml          # name=sourcea-sdk · MIT · requires-python>=3.10
  README.md               # 3-line install + one example (sign + replay)
  src/sourcea_sdk/
    __init__.py
    cli.py                # sourcea-sdk sign | replay | spine-tail
    receipt.py            # checksum, write, verify (from commit_intent patterns)
    spine.py              # portable append + read (extract from governance_event_spine_v1)
    portable_paths.py     # .sourcea/receipts.jsonl · .sourcea/spine-v1.jsonl
  tests/
    test_receipt_roundtrip.py
    test_spine_append_replay.py
```

### Export script (new — not built in this phase)

`scripts/publish_sourcea_sdk_public_v1.py` — mirror `publish_sourcea_boot_public_v1.py`:

1. Copy extract tree to `.publish-export/`
2. Run `validate-sourcea-sdk-v1.sh` (new — lightweight, ≤4 checks)
3. Push to `kazemnezhadsina144-dot/sourcea-sdk` (repo TBD)
4. PyPI publish only after founder token + honest site copy flip

---

## Public API surface (v0.1.0 target)

### CLI

```bash
pip install sourcea-sdk   # P1 — after extract + PyPI

sourcea-sdk sign \
  --intent .sourcea/intent.json \
  --out .sourcea/receipts/latest.json

sourcea-sdk replay --file .sourcea/receipts/latest.json

sourcea-sdk spine-tail --n 5   # last N spine events (portable jsonl)
```

### Python API (minimal)

```python
from sourcea_sdk import sign_receipt, verify_receipt, append_spine_event

rec = sign_receipt(intent=..., bind_spine=True)
assert verify_receipt(rec)
```

### Schema contracts

- Receipt body: `intent_id`, `outcome`, `agent_id`, `object_id`, `receipt_checksum`, optional `spine_event_id` / `spine_checksum`
- Spine event: `governance-event-spine-v1.1` — see `scripts/governance_event_spine_v1.py` `EVENT_TYPES`

---

## Validators (new — spec only)

| Script | Checks |
|--------|--------|
| `validate-sourcea-sdk-v1.sh` | Package import · sign roundtrip · replay PASS · portable paths only |
| Extend `validate-sourcea-boot-v1.sh` | Optional: boot PASS → sdk sign smoke (factory CI only, not Mac founder session) |

---

## Site / eval honesty rules

| Claim | Allowed when |
|-------|--------------|
| `git clone …/sourcea-boot` | Now (Phase 0) |
| `pip install sourcea-boot` | Phase 0b only — PyPI resolves |
| `pip install sourcea-sdk` | After P1 extract + PyPI — **do not add to /eval until then** |
| “Governance receipt on every action” | SDK live OR factory-only disclaimer |

Primary hero remains **Forge → /eval (sourcea-boot) → live receipt** — SDK is secondary depth on `/eval` and kernel, not hero replacement.

---

## P2 — Noetfield `POST /v1/decision`

**Out of scope for sourcea-sdk v0.1.0.**

Per chain-tools law, policy gate before execution ships as:

- **Hosted API:** Noetfield OS `POST /v1/decision` (policy pack + intent → ALLOW/BLOCK)
- **npm SDK:** `@noetfield/decision-client` (parallel lane — not Python extract)

Relationship: `sourcea-boot` = local disk pre-flight · `sourcea-sdk` = receipt spine · Noetfield decision API = remote policy gate for Copilot/compliance buyers. Wire in P2 after SDK extract approved.

---

## Extraction checklist (founder approval gate)

- [ ] Confirm portable `.sourcea/` paths match boot portable mode
- [ ] Strip factory-only deps (`~/.sina`, Hub, Supabase) from default SDK path
- [ ] MIT LICENSE + public repo + CI (copy boot pattern)
- [ ] `validate-sourcea-sdk-v1.sh` PASS in monorepo
- [ ] Public README runnable in <5 min after boot PASS
- [ ] Site copy update scoped to `/eval` + trust-signals — no hero rewrite
- [ ] PyPI publish (optional sub-gate)

---

## Blockers

| Item | Status |
|------|--------|
| Founder approval to extract | **Required** — this doc is spec only |
| PyPI token (boot + sdk) | Phase 0b / P1b — report BLOCKED if absent |
| brain-core-v1 runtime | Sandbox spec — not SDK dependency |
| Noetfield decision API | P2 — separate Noetfield lane |

---

**End spec v1**
