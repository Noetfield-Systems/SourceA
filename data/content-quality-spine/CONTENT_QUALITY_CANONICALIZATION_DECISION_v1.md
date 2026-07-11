# Content Quality Canonicalization Decision v1

**Saved:** 2026-07-11T05:45:00Z  
**Canonical repo:** `Noetfield-Systems/SourceA`  
**Audited HEAD:** see runtime receipt `audited_head_sha`

## Decision

Extend SourceA with a **shared semantic-quality core** at `scripts/content_quality_spine_core_v1.py` backed by evidence in `data/content-quality-spine/`. Do **not** create a parallel SourceB-only factory.

SourceB remains a **consumer/instance** lane. Locked conversation-script rules live in `SourceB-ca-release` (commit `3449f566`) until merged to main SourceB (`d786e212` has no `data/` conversation lock).

## Architecture

### Shared semantic-quality core (portfolio)

| Concern | Canonical owner | Status |
|---------|-----------------|--------|
| Artifact classification | `content_quality_spine_core_v1` + SourceB D1 | EXISTING_PARTIAL → wired |
| Claim/evidence validation | `truth_evidence_verifier` + R1 + OEGCC linter | EXISTING_PROVEN |
| Truthfulness / promise discipline | SourceB R8 + outbound linter | EXISTING_PROVEN |
| Naturalness / tone / grammar | rule-based semantic critic (SourceB port) | EXISTING_PARTIAL |
| Brand separation | D2 + film routing + landing gates | EXISTING_PROVEN |
| Critic/advisor/judge loop | spine + `governance_critic_eval_v1` + `chat_founder_loop_v1` | EXISTING_PARTIAL |
| Revision + quarantine | `outbound_email_controller_v1` + spine judge | EXISTING_PARTIAL |
| Receipts | spine JSON + `~/.sina/*` patterns | EXISTING_PROVEN |
| Cost routing | `model_dispatch.py` + `ai_unify_api_v1.py` | EXISTING_PROVEN (not invoked in proof) |

### Artifact adapters (thin)

| Adapter | Delegates to |
|---------|--------------|
| `ivr_receptionist` | SourceB R1–R16 patterns (Python port) |
| `commercial_film` | D1–D6 + `commercial_film_critic_circle_v1` (post-approval) |
| `email` | `outbound_email_linter_v1` (OEGCC) |
| `landing_page` | landing gate rules (subset) + full gates at ship |

### Domain-policy packs (not in core)

`automotive`, `medical`, `financial`, `general_SMB` — safety/regulatory blocks stay in packs, not generic core.

## Why not a new package?

- `packages/sourcea-sdk/spine.py` is **governance event append**, not content QC.
- `packages/noetfield/governance.py` is hub governance, not copy spine.
- Proven executables already live in `scripts/` with validators in `scripts/validate-*`.

New package deferred until spine adapters stabilize; current home is `scripts/` + `data/content-quality-spine/`.

## SourceB lock status

```
SOURCEB_MAIN_LOCK: NOT_YET_AVAILABLE (no conversation-script data/ on d786e212)
SOURCEB_CA_RELEASE_LOCK: AVAILABLE at 3449f56687e5ab4da924668184c04770e02f3e2a
```

## Proof scope (Phase H)

Pre-generation/pre-send only. No video/audio synthesis, email send, deploy, or live copy change.

**Command:** `python3 scripts/content_quality_spine_run_v1.py --proof --canaries --json`

## Next smallest moves

1. Wire `content_quality_spine_run_v1.py` into SourceB golden-set orchestrator as pre-synthesis gate.
2. Deploy `brain_core_v1` sanitizer to Brain Worker (staging → production).
3. Add LLM semantic critic behind `ai_unify_api_v1` with explicit receipts (optional escalation only).
4. Unify SourceB-ca-release lock into main SourceB `data/` via PR.
