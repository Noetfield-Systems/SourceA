# Branch B02 — W2 Kernel Hardening (PLAN-026–040) LOCKED v1

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Parent:** `SOURCEA_CONTROL_PLANE_200_PLAN_BRANCH_INDEX_LOCKED_v1.md`  
**Thesis:** **Proof beats observability** — K1–K8 receipts, bypass=0, tamper FAIL is the product.

**Shipped Jun 2026:** `critic_boot_v1.py` · `validate-critic-boot-v1.sh` · session gate `--in-gate`

---

## Bucket dependency map

```
critic_boot(done) → 027 → 034 → 038
026(K1) → 035 → 041-044 film → 141 API
028(K3) → 051 Art12 spec
157/158 → category claims
```

---

## PLAN-026 · K1: Receipt validator on read

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** M2 · **Week** W2 |
| **Objective** | Any read of receipt verifies signature + spine bind; forged edit → FAIL |
| **Acceptance** | `validate-enforcement-kernel-v1.sh` includes tamper case PASS=FAIL |
| **Depends** | Spine bind checksum (039) |
| **Unblocks** | K1 gate · PLAN-038 CI · PLAN-041-044 film · PLAN-141 API |
| **Artifact** | Validator script + negative test fixture |
| **Competitor** | vs LangSmith traces · vs WitnessAI observe — **validator on read** is wedge |
| **Failure mode** | Validate only on write — buyer edits file on disk |

---

## PLAN-027 · K2: Bypass inventory → 0

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** W · **Week** W2 |
| **Objective** | Enumerate every execution path; bypass count = 0 |
| **Acceptance** | `find_critical_bugs` bypass section empty · PLAN-157 public metric |
| **Depends** | critic_boot paths inventoried |
| **Unblocks** | PLAN-040 · 158 CI gate · sales claim “if it can bypass, it doesn't exist” |
| **Competitor** | vs AgentPEP — integrated briefing + SSOT fingerprint, not orphan PEP |
| **Failure mode** | Hidden hub-only path · emergency disable flags counted as bypass |

---

## PLAN-028 · K3: Append-only receipt log

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** M2 · **Week** W3 |
| **Objective** | jsonl spine append-only; delete/truncate blocked |
| **Acceptance** | Chaos delete test FAIL (154) · Art 12 retention hook |
| **Unblocks** | PLAN-051 · 059 export |
| **Competitor** | Art 12 immutability — EU deployer RFP scenario |

---

## PLAN-029 · K7: Hub Commit → demo enforcement

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** M2 · **Week** W3 |
| **Objective** | One-tap demo triggers real enforcement path |
| **Acceptance** | Founder Action or standalone equivalent · receipt emitted |
| **Note** | Hub quarantined — standalone Chat Unify / NF demo runner acceptable |
| **Unblocks** | PLAN-048 |

---

## PLAN-030 · K4: Hub disposable PASS

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** M2 · **Week** W3 |
| **Objective** | Demo PASS receipt provably ephemeral / scoped — diligence story |
| **Acceptance** | Doc + demo shows disposable vs production bind |
| **Unblocks** | Investor data room PLAN-037 |

---

## PLAN-031 · K6: Voyage live — vault bootstrap

| Field | Value |
|-------|-------|
| **P** | P2 · **Owner** M2 · **Status** partial |
| **Objective** | Semantic audit search over receipt corpus |
| **Acceptance** | Hub vault bootstrap · one query demo |
| **Unblocks** | PLAN-087 credits story |

---

## PLAN-032 · K5: G3 LAW_CHANGED end-to-end

| Field | Value |
|-------|-------|
| **P** | P2 · **Owner** W · **Week** W4 |
| **Objective** | Policy change propagates → agent re-brief → BLOCK until clear |
| **Acceptance** | E2E test · inbox shows LAW_CHANGED |
| **Competitor** | vs  build-time refresh — **runtime re-brief same day** |
| **Unblocks** | Buyer 2 propagation story |

---

## PLAN-033 · K8: propagation live inbox truth

| Field | Value |
|-------|-------|
| **P** | P3 · **Owner** M2 · **Status** partial |
| **Objective** | Monitor reflects propagation state accurately |
| **Acceptance** | No fake-green — maintainer audit PASS |

---

## PLAN-034 · validate-enforcement-kernel-v1.sh

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** M2 · **Week** W2 |
| **Objective** | Single validator customer diligence can run |
| **Acceptance** | Exit 0 only when K1+K2 checks pass |
| **Depends** | 026 · 027 |
| **Unblocks** | Procurement technical appendix |

---

## PLAN-035 · Export bundle — zip receipts + spine slice

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** M2 · **Week** W3 |
| **Objective** | One command produces procurement ZIP |
| **Acceptance** | Manifest checksum · regulator drill ready |
| **Unblocks** | PLAN-059 · 145 CLI · NF procurement ZIP |

---

## PLAN-036 · Art 12 field mapping doc (internal)

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** M2 · **Week** W3 |
| **Objective** | Map receipt fields → EU Art 12 log requirements |
| **Unblocks** | PLAN-051 product spec · sales engineer enablement |

---

## PLAN-037 · Single write path diagram

| Field | Value |
|-------|-------|
| **P** | P2 · **Owner** M2 · **Week** W4 |
| **Objective** | Data room diagram: one write path, no shadow writes |
| **Unblocks** | Investor · Buyer 2 DD |

---

## PLAN-038 · Forged receipt negative test in CI

| Field | Value |
|-------|-------|
| **P** | P0 · **Owner** M2 · **Week** W2 |
| **Objective** | CI fails if tamper does not produce FAIL |
| **Acceptance** | CI red on broken K1 |
| **Depends** | PLAN-026 |
| **Unblocks** | Film authenticity · GitHub eval trust |

---

## PLAN-039 · Receipt checksum on spine bind — audit

| Field | Value |
|-------|-------|
| **P** | P2 · **Owner** M2 · **Week** W3 |
| **Objective** | Cryptographic bind audit documented |
| **Depends** | 026 |

---

## PLAN-040 · Bypass regression in find_critical_bugs

| Field | Value |
|-------|-------|
| **P** | P1 · **Owner** W · **Week** W3 |
| **Objective** | Every release scans bypass inventory |
| **Depends** | PLAN-027 |
| **Unblocks** | PLAN-158 |

---

*End B02 — 15 plans*
