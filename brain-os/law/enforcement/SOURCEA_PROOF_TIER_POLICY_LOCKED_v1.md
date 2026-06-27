# SOURCEA Proof Tier Policy (LOCKED v1)

**Locked:** 2026-06-24T09:30:00Z  
**Pairs:** `data/cloud-forge-run-proof-tier-policy-v1.json` · INCIDENT-044 · Cloud Forge Run observer · evidence-audit API

## One law

> **A green is not a green is not a green.** Three proof tiers — never merged in counts, UI, or founder chat.

## Tiers

| Tier | `evidence_source` | Sellable to buyer? | Count as "verified"? |
|------|-------------------|--------------------|----------------------|
| **verified_fetch** | `http_fetch` | **Yes** — live page fetched, snippets from HTTP 200 | **Yes** |
| **labeled_claim** | `cloud_action_vendor_says` | **No** — labeled claim copied from locked plan | **No** |
| **blocked_recipe** | `cloud_action_locked_recipe` | **No** — pipeline ran; HTTP failed; receipt labels `http_blocked` | **No** |

## Mandatory reporting

Report **three numbers**, never a blended total:

- `N verified-fetch` (`http_fetch`)
- `M labeled-claim` (`cloud_action_vendor_says`)
- `K blocked-recipe` (`cloud_action_locked_recipe`)

**Forbidden:** "1,710 done" · "all greens" · "competitor research complete" when any row is not `http_fetch`.

## Surfaces

- **Evidence audit:** `/api/cloud-forge-run/evidence-audit/v1` — tier badge per row, split counts in header
- **Observer:** must not imply all shipped rows are sellable proof
- **Receipts:** `evidence_source` + `http_status` on every dispatch receipt

## Founder standard (sellable row)

**CLOUD-SEC-1100 / delve.co pattern:** `http_fetch` · HTTP 200 · real snippets · forge-seed artifact logged.

## Entity note

Cloud Forge Run queue rows serve **WitnessBC competitive registry** (`wb-mkt-*`). They are **portfolio factory proof**, not Noetfield Systems Inc. customer deliverables. Noetfield pitch uses its own receipts lane.
