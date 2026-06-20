# Branch B03 — W1 Demo Film (PLAN-041–050) LOCKED v1

**Saved:** 2026-06-16T04:33:36Z · **Retrofit:** doc-datetime-law batch retrofit
**Parent:** `SOURCEA_CONTROL_PLANE_200_PLAN_BRANCH_INDEX_LOCKED_v1.md`  
**Thesis:** **Tamper FAIL on camera** — category moment; Geordie parity requires filmed proof.

**Execution repo:** **OTHER REPO** (not SourceA hub)  
**SourceA substitute until film ships:** `NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md` + `run_noetfield_compliance_demo_v1.sh`

---

## Bucket dependency map

```
026(K1) + 038(CI) → 041-044 film core
041-044 → 045 YouTube → 046 LinkedIn cut → 107 PH/HN
047 reset → sales repeatability
```

---

## PLAN-041 · Film ALLOW — receipt + PASS

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** ASF · **Repo** other |
| **Objective** | Continuous take: policy allows action → signed receipt → PASS visible |
| **Acceptance** | Unedited sequence · terminal visible · receipt hash on screen |
| **Depends** | K1 gate PLAN-026 · demo reset PLAN-047 |
| **Unblocks** | 042 · 045 · buyer eval |
| **Failure mode** | Cuts hiding latency · pre-recorded fake terminal |

---

## PLAN-042 · Film TAMPER — hand edit → FAIL

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** ASF · **Repo** other |
| **Objective** | Hand-edit receipt file present → validator FAIL on read |
| **Acceptance** | FAIL message legible · no cut before outcome |
| **Depends** | PLAN-026 · PLAN-038 |
| **** | **Primary differentiator** vs observability-only (LangSmith, Datadog) |
| **Unblocks** | PLAN-046 · PLAN-114 newsletter · RSAC abstract |

---

## PLAN-043 · Film BLOCK policy case

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** ASF · **Repo** other |
| **Objective** | Policy violation → BLOCK before action · no receipt for forbidden act |
| **Acceptance** | BLOCK visible · critic_boot or gate path shown |
| **** | vs Microsoft Auth Fabric DIY — show disk PASS/BLOCK in minutes |

---

## PLAN-044 · Terminal visible — no cuts <6 min

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** ASF · **Repo** other |
| **Objective** | Full film ≥6 min · authentic terminal · single session |
| **Acceptance** | YouTube upload ready master |
| **Failure mode** | Sizzle reel without proof — buyers smell marketing |

---

## PLAN-045 · Upload unlisted YouTube + hub link

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** ASF · **Repo** other |
| **Objective** | Unlisted URL in outreach templates |
| **Depends** | 041-044 master |
| **Unblocks** | PLAN-002 attach · PLAN-107 launch |

---

## PLAN-046 · 90-sec cut for LinkedIn

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** ASF · **Repo** other |
| **Objective** | Tamper FAIL highlight reel ≤90s |
| **Depends** | PLAN-042 footage |
| **Unblocks** | PLAN-004 distribution |

---

## PLAN-047 · Demo env reset script — repeatable

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** W · **Repo** SourceA OK |
| **Objective** | One command resets demo state for sales |
| **Acceptance** | `run_noetfield_compliance_demo_v1.sh` idempotent reset documented |
| **Unblocks** | Film + live demos |

---

## PLAN-048 · Hub Run tab → “Play demo” deep link

| Field | Value |
|-------|-------|
| **P** | P2 · **Owner** M2 |
| **Objective** | Founder one-tap to demo |
| **Note** | Hub quarantined — standalone deep link acceptable |

---

## PLAN-049 · B-roll: spine jsonl append visible

| Field | Value |
|-------|-------|
| **P** | P2 · **Owner** ASF · **Repo** other |
| **Objective** | Event sourcing append visible in film |
| **Unblocks** | PLAN-165 diagram sales asset |

---

## PLAN-050 · Demo subtitle — commercial sentence

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** ASF · **Repo** other |
| **Objective** | SSOT §1 sentence burned in captions |
| **Depends** | PLAN-161 voice lock |

---

## SourceA live path (until film)

| Step | Action |
|------|--------|
| 1 | Founder opens NF demo via runner `--open-only` |
| 2 | PLAN-014 10-min script on live BLOCK→PASS |
| 3 | Record Zoom for PLAN-020 (interim, not W1 film) |

---

*End B03 — 10 plans*
