# SourceA — Cloud Forge Run realistic motor law (LOCKED)

**Saved:** 2026-07-05 · **UTC:** 2026-07-05T15:58:00Z · **v1.0**  
**SSOT:** `data/cloud-forge-run-realistic-motor-law-v1.json`  
**Config:** `data/cloud-auto-runtime-v1.json`  
**Supersedes:** INCIDENT-043/044 hundred-row mandatory quota theater  
**Incident:** INCIDENT-045 · **Cursor:** `.cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc`

---

## One law

> **Auto Runtime (~10 min) fires one Cloud Forge Run POST. Each turn processes up to 10 doable tasks (one recipe unit per row). A row may advance only after worker execution, validator PASS, and a Supabase artifact. Never claim ship success from `processed` counts alone. Scale throughput with cloud workers — not inflated row quotas.**

---

## What changed (founder correction 2026-07-05)

| Retired (theater) | Clean law |
|-------------------|-----------|
| Mandatory 100 rows per turn | **Cap** 10 rows per turn (worker-bounded) |
| `processed === 100` = success | **Recipe + Supabase proof** = success |
| Seed cycle head advance = factory ship | Seed = hygiene only until recipe proves value |
| “Autorun fixed” from counter match | Autorun fixed only when valuable artifacts land |

INCIDENT-043 vocabulary (turn vs batch vs full_pack) **stays valid**.  
INCIDENT-044 no-skip on motor fail **stays valid**.  
Only the **100-row mandatory quota** is retired.

---

## Definitions

| Term | Means |
|------|--------|
| **Turn** | One CF cron (`*/10`) or one Cloud Workers Proceed tap |
| **Row** | One `CLOUD-SEC-*` slot — **one doable task** for one worker |
| **Task** | One recipe execution (`tasks_per_row: 1` default) |
| **`max_advance`** | **Cap** per turn (default **10**) — not a mandatory 100 |
| **`full_pack`** | Internal multi-row loop inside one HTTP request |
| **Shipped** | Motor PASS + `advance_on_pass` + proof gate |
| **Valuable ship** | Shipped + recipe `done_when` verified + Supabase artifact |
| **Counter theater** | Reporting `pack.processed` or head delta without recipe proof |

---

## Proof gate (mandatory before advance)

1. `plan_id` resolves to a recipe on disk  
2. Cloud worker runs the recipe (not Mac)  
3. `validator_result === PASS`  
4. Supabase `cloud_forge_run_rows` row written with `artifact_path`  
5. Founder/agent claims cite **plan_id + artifact** — never count alone  

**Forbidden:** “100/100 shipped” · “autorun fixed” · “sink invariant matched” without inspecting artifacts.

---

## Cadence

```text
Every ~10 min (CF cron */10):
  ONE POST auto-tick { full_pack: true, max_advance: <=10 }
  → up to 10 rows, each one doable task
  → motor fail HALTS turn (no skip — INCIDENT-044)
  → ONE observer row
```

**Throughput:** add Railway workers / parallel dispatch — **not** `mandatory_shipped_per_turn: 100`.

---

## PASS / FAIL per turn

| Situation | PASS | FAIL |
|-----------|------|------|
| Rows with proof | Each advanced row has artifact + PASS | Advance without proof |
| Motor fail mid-pack | Halt · `skipped === 0` | Skip-through head |
| Batch tail | Process remaining ≤ cap | Fake empty batch arm |
| Founder report | Cite recipes + Supabase paths | Cite `processed` only |

---

## Retired files (read for history only)

- `SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md`  
- `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json` (superseded pointer)  
- INCIDENT-043 quota sections · INCIDENT-044 `mandatory_shipped_per_turn: 100`

**LOCKED v1.0**
