# Branch B11 — Kernel Tier-1 / API Moat (PLAN-141–160) LOCKED v1

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Parent:** `SOURCEA_CONTROL_PLANE_200_PLAN_BRANCH_INDEX_LOCKED_v1.md`  
**Thesis:** **Embed moat** — SDK + receipt API + bypass=0 CI = Buyer 1 GitHub eval path.

**Shipped partial:** critic_boot · model_dispatch · ai_unify_api · orchestrator partner doc

---

## PLAN-141 · Receipt API v1 REST read + verify

| Field | Value |
|-------|-------|
| **P** | P0 · M2 · W3 |
| **Objective** | `GET /receipt/{id}` + `POST /verify` with FAIL on tamper |
| **Acceptance** | OpenAPI stub · auth key · p99 <500ms dev |
| **Depends** | PLAN-026 K1 |
| **Unblocks** | 142 · 143 · 146 · 089 white-label · 137 audit portal |
| **Competitor** | vs Delve evidence automation — validator-on-read API |

---

## PLAN-142 · Receipt API OpenAPI published

| **P** P1 · M2 · W4 | Public spec in repo · GitHub eval

## PLAN-143 · SDK Python `sourcea.verify(receipt)`

| **P** P1 · W · W4 | `pip install` path · 3-line quickstart

## PLAN-144 · SDK TypeScript mirror

| **P** P2 · W · W5 | JS ecosystem · Buyer 1 full-stack shops

## PLAN-145 · CLI `sourcea export --bundle` Art 12 zip

| Field | Value |
|-------|-------|
| **P** | P0 · M2 · W3 |
| **Objective** | One CLI command = PLAN-035 export for regulators |
| **Acceptance** | Manifest JWS optional (151) · exit 0 on valid bundle |
| **Depends** | 035 · 051 field map |

---

## PLAN-146 · Webhook receipt.verified / policy.blocked

| **P** P2 · M2 · W5 | Integration SKU · n8n + Temporal hook

## PLAN-147 · Multi-tenant org_id on spine

| **P** P2 · W · W6 | Buyer 2 scale · data isolation story

## PLAN-148 · Rate limits + API keys portal

| **P** P2 · M2 · W6 | Self-serve · pairs 095 Starter SKU

## PLAN-149 · SLO verify p99 <200ms

| **P** P2 · W · W7 | Performance diligence answer

## PLAN-150 · Horizontal read replica receipt store

| **P** P3 · W · W10 | Volume — don't build before deposits

## PLAN-151 · Signed export manifest JWS

| **P** P1 · M2 · W4 | Regulator-grade · EU Art 12 attach

## PLAN-152 · Policy version pinning on receipt

| **P** P1 · M2 · W4 | Audit replay · NF TLE story

## PLAN-153 · Replay CLI `--as-of` timestamp

| **P** P2 · W · W6 | Ops trust · incident reconstruction

## PLAN-154 · Chaos test delete receipt → FAIL

| **P** P1 · W · W4 | Immutability proof · pairs 028 K3

## PLAN-155 · Load test 10k receipts/hour

| **P** P3 · W · W10 | Buyer 2 sizing doc only

## PLAN-156 · Receipt schema registry versioned JSON

| **P** P2 · M2 · W5 | Interop · MCP + webhook contracts

## PLAN-157 · Public metric bypass count = 0

| Field | Value |
|-------|-------|
| **P** | P0 · M2 · W3 |
| **Objective** | Published metric or dashboard field: bypass_inventory_count |
| **Acceptance** | Value 0 · updated on each release |
| **Depends** | PLAN-027 |

---

## PLAN-158 · CI gate no merge if bypass >0

| Field | Value |
|-------|-------|
| **P** | P0 · W · W3 |
| **Objective** | PR blocked if bypass inventory non-empty |
| **Depends** | 027 · 040 |
| **Competitor** | Unique vs OSS PEP repos — **CI-enforced governance**

---

## PLAN-159 · Customer-facing validator catalog

| **P** P2 · M2 · W6 | Transparency · what checks run at boot

## PLAN-160 · Kernel Tier-1 scorecard K1–K8 %

| **P** P1 · M2 · W4 | Board metric · honest % not fake-green

---

## API + partner stack (smart wiring)

```
026 K1 → 141 API → 142 OpenAPI → 106 GitHub README
035 export → 145 CLI → 176 EU SKU card
069 Temporal partner → 146 webhooks
```

---

*End B11 — 20 plans*
