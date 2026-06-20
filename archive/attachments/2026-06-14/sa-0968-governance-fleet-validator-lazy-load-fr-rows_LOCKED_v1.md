# sa-0968 — Governance fleet validator extensions for lazy-load FR rows

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No validator code edits in CHECK**

## One-line verdict

> **Governance fleet and FR sync are adjacent but split validators today.** Research extension: unify **essay/scoreboard SSOT** (`validate-governance-fleet-v1`) with **lazy-load FR-010 closeout** (`sync_shipped_from_disk` + `validate-app-js-lazy-bootstrap-v1`) in one quarterly gate — defer implement until ASF orders maintainer ACT.

---

## Fabric today (disk truth)

| Validator | Scope | FR rows touched | Build tier |
|-----------|-------|-----------------|------------|
| `validate-governance-fleet-v1.sh` | `essay_nudges` · `fleet_verify_gap` · `fleet_report_gap` · TRUST_LEDGER · `__COMMAND_DATA_LAZY` in `index.html` | **FR-008** (nudges) · **FR-009** (auto_pass) · **FR-010** (lazy flag only) | Strict after eval live (sa-0213) |
| `validate-founder-request-fleet-sync-v1.sh` | `sync_shipped_from_disk()` · FR-007/008/009/010/011 rules in source | **FR-007** · **FR-008** · **FR-009** · **FR-010** · **FR-011** | Strict build (sa-0310–0312) |
| `validate-app-js-lazy-bootstrap-v1.sh` | Legacy `app.js` shell-first · `__COMMAND_DATA_LAZY` contract · shell ≤512KB | **FR-010** evidence path | On-demand / sa-0851 ACT |
| `validate-command-data-lazy-shell-v1.sh` | `index.html` lazy bootstrap + shell size | **FR-010** | Chained by lazy-bootstrap |

**Sync logic (`founder_request_tracker.py`):**

```text
index.html contains __COMMAND_DATA_LAZY → mark FR-2026-06-05-010 shipped
essay nudges ≤2 → FR-008 shipped · else in_progress
auto_pass_count ≥6 → FR-009 shipped · else in_progress
```

**Gap:** `validate-governance-fleet-v1` asserts lazy **string in HTML** but does **not** run `sync_shipped_from_disk()` or confirm FR-010 `status: shipped` in `~/.sina/founder-requests/requests.jsonl`. Fleet and FR validators can PASS independently with stale FR row state.

---

## FR row crosswalk (lazy-load cluster)

| FR id | Title | Governance fleet link | Lazy-load link | Current sync |
|-------|-------|----------------------|----------------|--------------|
| FR-008 | Fleet essay discourse | `essay_nudges` / `nudge_count` | — | sync on nudge threshold |
| FR-009 | Scoreboard reports + verify | `fleet_verify_gap` · `auto_pass_count` | — | sync on auto_pass ≥6 |
| FR-010 | Lazy-load / split COMMAND_DATA | index.html flag check only | shell bootstrap · app.js contract | sync when flag present |
| FR-011 | Founder directives jsonl | — | — | sync when file exists |

**sa-0851 shipped:** lazy bootstrap validator without merging into governance-fleet chain — this sa researches the **merge spec**.

---

## Proposed extensions (research — not enforced)

### E1 — Post-fleet FR reconcile (minimal)

After governance-fleet PASS:

1. Call `sync_shipped_from_disk()`
2. Assert `FR-2026-06-05-010` status ∈ `{shipped}` when `validate-command-data-lazy-shell-v1` would PASS
3. Assert `FR-2026-06-05-008/009` statuses match live `nudge_count` / `auto_pass_count`

**Owner:** Maintainer · **Risk:** low · **Touches:** extend `validate-governance-fleet-v1.sh` or new wrapper

### E2 — Chain lazy-bootstrap on FR-010 open

If FR-010 still `open` in summary → run `validate-app-js-lazy-bootstrap-v1.sh` before marking shipped.

**Owner:** Maintainer · **Risk:** medium (legacy `/legacy/` path only) · **Law:** Worker Hub daily path uses `validate-super-fast-hub-v1` — do not conflate

### E3 — Single quarterly gate name

`validate-governance-fleet-lazy-fr-v1.sh`:

```text
validate-governance-fleet-v1.sh
  → validate-founder-request-fleet-sync-v1.sh
  → validate-command-data-lazy-shell-v1.sh (if FR-010 not shipped)
```

Register in `find_critical_bugs.py` as optional T2 hardening — **not** new CRITICAL until soak.

### E4 — Hub Track projection check

When `founder_requests.open_top` includes FR-010 as `open` but lazy validators PASS → anti-staleness incident class (INCIDENT-027 family).

**Owner:** Maintainer + hub projection sync · **No** new D-modules

---

## What not to merge

| Anti-pattern | Why |
|--------------|-----|
| Fold FR sync into essay_discourse module | Violates single-responsibility · breaks sa-0310 isolation |
| Require full `command-data.json` load in governance-fleet | Defeats lazy-load purpose |
| ASF verify column for FR-010 | Machine `sync_shipped_from_disk` only (sa-0960 law) |
| New CRITICAL before 2-week soak | Quarterly T2 hardening — research first |

---

## Relation to prior sas

| SA | Link |
|----|------|
| sa-0213 / sa-0309 / sa-0359 | Governance-fleet nudges + verify_gap SSOT |
| sa-0310–0312 | FR fleet sync validator |
| sa-0851 / sa-0801 | Lazy bootstrap ACT — validator exists, not chained |
| sa-0324 | "Run governance fleet after essay/scoreboard change" — operational, not FR-010 |

---

## ACT — Live disk snapshot (2026-06-14)

After `sync_shipped_from_disk()`:

| FR id | Status | Evidence |
|-------|--------|----------|
| FR-008 | **shipped** | essay nudges **0** |
| FR-009 | **shipped** | auto_pass_count **8** |
| FR-010 | **shipped** | index.html lazy-load shell |
| FR-011 | **shipped** | `~/.sina/founder-directives.jsonl` |

**Reconcile note:** Live rows are **shipped** while governance-fleet and FR-sync validators remain **separate gates** — E1 extension would assert this coupling on every strict build, not only on manual sync.

---

## ACT — Strict build chain map

From `build-sina-command-panel.py` (post eval-live tier):

| Order | Validator | sa marker | Coupled to lazy FR? |
|-------|-----------|-----------|---------------------|
| 1 | `validate-governance-fleet-v1.sh` | sa-0213 | Partial — HTML flag only |
| 2 | `validate-governance-fleet-nudges-ssot-v1.sh` | sa-0309 | FR-008 SSOT |
| 3 | `validate-founder-request-fleet-sync-v1.sh` | sa-0310–0312 | FR-007–011 sync |
| — | `validate-command-data-lazy-shell-v1.sh` | sa-0041 | FR-010 — **not in same chain today** |
| — | `validate-app-js-lazy-bootstrap-v1.sh` | sa-0851 | Legacy path — on-demand |

**ACT wiring spec (E3 — maintainer implement):**

```bash
# validate-governance-fleet-lazy-fr-v1.sh (proposed — not shipped)
bash validate-governance-fleet-v1.sh
bash validate-founder-request-fleet-sync-v1.sh
python3 -c "from founder_request_tracker import sync_shipped_from_disk as s; r=s(); assert r.get('ok')"
# Optional if FR-010 regression suspected:
# bash validate-command-data-lazy-shell-v1.sh
```

Register in `build-sina-command-panel.py` **after** sa-0312 row · soak 2 weeks before `find_critical_bugs.py` CRITICAL promotion.

---

## ACT — Soak gate (before CRITICAL)

| Criterion | PASS signal |
|-----------|-------------|
| 14 consecutive strict builds green | `build-sina-command-panel.py` log |
| FR-010 stays shipped across hub refresh | Track + `requests.jsonl` |
| No INCIDENT-027 projection drift | `founder_requests.open_top` lacks FR-010 open |
| Worker daily path unchanged | `validate-super-fast-hub-v1` still default |
| Maintainer-only ship | No Worker RUN INBOX validator edits |

---

## Duplicate sa titles

Same task at **sa-0918**, **sa-0943**, **sa-0968**, **sa-0993**. Canonical research for **sa-0968** CHECK→ACT→VERIFY closeout.

---

## Verdict

**Governance fleet validator should gain optional FR-010 reconcile extensions** — not replace existing validators. Minimal path: E1 post-fleet sync assert; full path: E3 wrapper in strict build after maintainer soak.

**One-line:** Fleet SSOT + lazy FR rows need one reconcile gate — research spec ready, implement deferred.
