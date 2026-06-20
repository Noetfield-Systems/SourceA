# sa-0799 ACT — Harden essay mark-best POST without ASF as sole actor

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no hub code diff** (FREEZE + repair-only)

## Task scope

Document how `POST /api/essay-discourse` `action: mark_best` works today, what “without ASF as sole actor” means vs locked law, and what hardening options exist **without** making ASF the verify/progress authority.

**Related:** `sa-0795` (founder vs machine verify) · `sa-0774` (T2 same title — done, no hardening crosswalk) · `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md`

## Authority order

| Layer | Source | Role |
|-------|--------|------|
| Essay law §0 | `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` | **ASF marks the best** (qualitative) |
| Machine verify | `agent_scoreboard.py` · fleet validators | `auto_pass` — **not** mark_best |
| Worker law | `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` | No ASF as REGISTRY verify authority |
| Task sa-0799 | T3 spike | Harden POST — **not** replace fleet verify with founder click |

**Clarifying sentence:** “Without ASF as sole actor” = add **machine-side guardrails and optional co-actors** on `mark_best`; it does **not** mean mark_best becomes the factory verify gate (that stays `auto_pass` + broker VERIFY).

## Current implementation (disk)

| Piece | Path / behavior |
|-------|-----------------|
| Handler | `scripts/agent_essay_discourse.py` → `mark_best_essay()` |
| Storage | `~/.sina/essay-discourse/best-by-subject.json` |
| API | `POST /api/essay-discourse` `{action, subject, essay_id}` |
| Hub UI | `app.js` → `.sc-essay-mark-best` click → `essayDiscourseApi` |
| Server | `sina-command-server.py` — hub mutates after success |
| Governance event | `essay_best_marked` via `log_governance_event` |

**Live disk (ACT 2026-06-11T22:18Z):**

| Signal | Value |
|--------|-------|
| `best-by-subject.json` | **absent** |
| Essays | **9** · nudges **0** · active subject `governance-drift-detection` |
| `best_essay_id` | **null** |
| Fleet scoreboard | **8/8** verified · auto_pass |

## Security / actor gaps (CHECK → ACT)

| ID | Gap | Severity |
|----|-----|----------|
| **GAP-1** | **No actor auth** on `mark_best` — any localhost caller can set best | high (Maintainer) |
| **GAP-2** | **No E2E validator** — `audit_backend_e2e.py` has no essay-discourse / mark_best path | medium |
| **GAP-3** | **No** `validate-essay-mark-best-v1.sh` | medium |
| **GAP-4** | Law §0 names ASF sole qualitative actor — task wants documented **co-actor** options below | informational |
| **GAP-5** | **sa-0774** closed without hardening artifact — sa-0799 T3 re-spike justified | informational |

## Hardening options (document only — no D-modules this ACT)

| Option | Actor | Mechanism | Touches verify? |
|--------|-------|-----------|-----------------|
| **A — Founder token** | ASF hub session | Require hub founder cookie / one-tap Safety attestation on POST | No |
| **B — Maintainer co-sign** | Maintainer | `mark_best` accepts `actor: maintainer` + disk receipt | No |
| **C — Council quorum** | Machine + founder | N agent brief votes → suggest best; founder confirms in hub | No |
| **D — Auto-suggest only** | Machine | Rank essays by length/tags/agent diversity; **never** auto-write best without founder | No |
| **E — Validator warn** | Machine | `validate-essay-mark-best-v1.sh` — POST round-trip + best file schema | No |

**Recommended line (beneficial, minimal):** **A + E** under repair-only — founder still picks winner; machine proves POST path and blocks anonymous localhost writes.

**Explicitly out of scope:** Using `mark_best` as scoreboard verify, REGISTRY done, or `eval_1b_gate_ok` input.

## Distinct from sa-0795

| Surface | ASF qualitative? | Machine gate? |
|---------|------------------|---------------|
| Mark best essay | **Yes** (subject winner) | Optional hardening only |
| Fleet green / nudges | No | **Yes** — `auto_pass` · `nudge_count` |
| sa-0799 done | No | Broker VERIFY + receipt |

## OPEN (Maintainer / ASF — not Worker under FREEZE)

1. **OPEN-1:** Ship **A+E** when hub repair allows — auth gate + validator script.
2. **OPEN-2:** Law addendum clause: mark_best = founder qualitative; fleet verify unchanged.
3. **OPEN-3:** ASF optional hub click **Mark best** when ready (8 agents · 9 essays logged).
4. **OPEN-4:** Dedupe 9th essay row (sa-0791 OPEN-3) — hygiene only.

## Validators (ACT — 2026-06-11T22:18Z)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0 verify_gap 0
- `validate-spine-bridge-founder-v1.sh` — PASS
- `validate-dispatch-policy-v1.sh` — PASS · gate_ok=True
- `find_critical_bugs.py` — critical **3** (global — blocks VERIFY)

## Verdict

**ACT complete** — crosswalk logged; hardening options documented; **no code diff** per T3 + FREEZE/repair-only. VERIFY blocked until global critical **0**.
