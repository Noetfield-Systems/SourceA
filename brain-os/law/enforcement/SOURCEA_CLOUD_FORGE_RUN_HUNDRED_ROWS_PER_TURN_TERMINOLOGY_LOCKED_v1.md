# SourceA — Cloud Forge Run hundred-rows-per-turn terminology (LOCKED)

> **SUPERSEDED 2026-07-05 (INCIDENT-045).** Active law: `SOURCEA_CLOUD_FORGE_RUN_REALISTIC_MOTOR_LOCKED_v1.md` · SSOT: `data/cloud-forge-run-realistic-motor-law-v1.json`. Retained below for history only.

**Saved:** 2026-06-24 · **UTC:** 2026-06-24T07:45:00Z · **v1.1** (founder correction — 100 is minimum, not “up to”)  
**Unified vocabulary:** `data/sourcea-vocabulary-unified-index-v1.json` · `SOURCEA_VOCABULARY_UNIFIED_LOCKED_v1.md`  
**Incident:** INCIDENT-043 · **Pair:** INCIDENT-042 · `SOURCEA_CLOUD_FORGE_RUN_FULL_PACK_PATTERN_LOCKED_v1.md`  
**SSOT:** `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json`  
**Founder names:** `data/cloud-motor-founder-vocabulary-v1.json` — **Cloud Forge Run** · **Auto Runtime** (drain/loop = poison)  
**Cursor rule:** `.cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc` · `.cursor/rules/038-cloud-forge-run-vocabulary-v1.mdc`

---

## One law (ASF — mandatory for every agent)

> **Auto Runtime (~10 min) triggers one Cloud Forge Run POST that must move exactly 100 queue rows — mandatory quota, not “up to 100”. Never say drain or loop to the founder (anti-poison). `full_pack` is the internal mode flag — not a background job.**

---

## Definitions (do not paraphrase)

| Term | Definition |
|------|------------|
| **Turn** | One CF cron fire (`*/10 * * * *`) or one Cloud Workers Proceed tap |
| **Row** | One `CLOUD-SEC-*` queue head step |
| **100 rows per turn** | **Mandatory minimum** `max_advance: 100` — `run_auto_runtime_pack` must consume **100 rows** (`processed === 100`) when the batch has ≥100 cloud rows left |
| **`max_advance: 100`** | Row **quota** per turn — **100 is the quantity ASF ordered**, not “maximum allowed” |
| **`full_pack`** | Boolean: enable internal 100-row loop in **this** request |
| **Batch** | Locked JSON file (`secondary-cloud-forge-run-batch-N-locked-v1.json`) — not a turn |
| **Batch tail exception** | Only when **<100** cloud rows remain in active batch → turn drains all remaining (e.g. 10 rows at end of batch 10) |
| **processed** | `shipped + skipped` this turn — rows moved down |
| **shipped** | Motor PASS + `advance_on_pass` |
| **skipped** | Motor FAIL + `skip_head` self-heal — **still counts as row down** |

---

## Chain (one sentence)

```text
Auto Runtime CF cron (~10 min) → ONE Cloud Forge Run POST { full_pack: true, max_advance: 100 } → MUST process 100 rows (batch tail excepted) → ONE observer row → done until next cron.
```

Code: `scripts/cloud_auto_runtime_v1.py` (`run_auto_runtime_pack`) · `cloud/workers/cloud-auto-runtime-tick-v1/src/index.js`

---

## PASS / FAIL per turn

| Situation | PASS | FAIL |
|-----------|------|------|
| ≥100 cloud rows left in batch | `processed === 100` | `processed < 100` (idle, stuck gate, motor halt mid-loop) |
| Batch tail (<100 rows left) | `processed === rows_remaining` + `queue_batch_complete` | Stuck before batch end |
| Agent language | “**100 rows per turn**” | “**up to 100**” · “as many as possible” · “some rows” |

---

## Mandatory agent conduct

Before any cloud-forge-run answer, agents **MUST** read:

1. This law  
2. `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json`  
3. Live `GET …/api/cloud-forge-run/queue/v1` (head + `batch_id`)

Replies **MUST** state:

- turn cadence (10 min · **100 rows minimum** · one POST), and  
- `processed N/100` from last observer cycle — **N must be 100** unless batch tail.

---

## Forbidden (instant fail — INCIDENT-043)

| Forbidden phrase / claim | Why |
|----------------------------|-----|
| **“drain” / “loop” in founder reply** | **Anti-poison — say Cloud Forge Run / Auto Runtime** |
| **“up to 100 rows”** | **Founder correction v1.1 — weakens mandatory 100 quota** |
| “The 100 pack is still running” (no gate proof) | Pack ends inside one HTTP request |
| “Skipped means the turn didn’t run” | `processed` can be 100 with high `skipped` |
| “Redeploy Railway to drain rows” | Deploy ≠ cron motor |
| “full_pack = 100 separate cron ticks” | Vocabulary poison |
| “max_advance is a ceiling” | Wrong — it is the **per-turn row quota** |
| Using **batch** when meaning **turn** | Conflation (INCIDENT-020 class) |
| “Wait for the pack” across cron boundary | No standing pack between turns |

---

## Railway deploy REMOVED (clarification)

Older deploys show **REMOVED** when a newer `railway up` supersedes them. **Normal.** Not drain failure. Proof of drain = queue head movement + observer `processed === 100` (or batch tail complete).

---

## Validator (ship window)

```bash
bash scripts/validate-cloud-forge-run-hundred-rows-vocabulary-v1.sh
```

Mac founder session: **do not** chain validators — one light read of SSOT JSON is enough for chat.

---

## Related

- `data/sourcea-vocabulary-unified-index-v1.json` — display vs machine vocabulary spine
- `brain-os/incidents/SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md`
- `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_FULL_PACK_PATTERN_LOCKED_v1.md`
- `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_AUTO_RUNTIME_VOCABULARY_LOCKED_v1.md`
- `data/cloud-motor-founder-vocabulary-v1.json`

**LOCKED v1.1**
