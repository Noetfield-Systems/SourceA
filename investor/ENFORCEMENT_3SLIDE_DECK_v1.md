# ENFORCEMENT-6MO — 3-slide deck (honest seed version)

**Use for:** NF/TF design partners · seed intros · advisor forwards  
**Not for:** $100M centaur close claims · whitepaper-first  
**Demo:** `investor/ENFORCEMENT_DEMO_5MIN.md`  
**Category line:** *We make AI execution impossible to bypass governance.*

---

## Slide 1 — Problem

**Headline:** Uncontrolled AI execution fails audit — not because the model is wrong.

**Bullets:**

- Copilot and agent stacks execute actions; enterprises cannot prove what ran, what was blocked, or whether policy was bypassed.
- Dashboards and chat logs are not receipts — they are projections. Projections are disposable; validators are authority.
- Regulated buyers (MSB, procurement, health) need **block + record + tamper-detect** before they scale agent deployments.

**Speaker note:** Do not say "agent orchestrator" or "AI OS." Say **enforceable execution**.

**Visual:** Simple flow — `Intent → Gate → Receipt → Spine` (one line diagram).

---

## Slide 2 — Proof (live demo)

**Headline:** If it can bypass, it doesn't exist.

**Bullets:**

- **BLOCK** — high-risk Copilot policy change without `approval_ref` → gate DENY, no DONE receipt.
- **ALLOW** — same wedge with approval → single commit path → receipt + spine row + checksum.
- **TAMPER** — hand-edit receipt logged → validator **HARD FAIL** on camera.
- Factory honesty: controlled tasks with receipts; **zero** unproven-done (anti-fake-velocity).

**Proof assets present today:**

- RT LIVE receipt ↔ spine bound (`validate-universe-invariants-v1.sh` PASS)
- Copilot demo path (`validate-demo-enforcement-v1.sh` PASS)

**Speaker note:** Offer to run 5-min live demo or share recording. Lead with tamper FAIL, not architecture essay.

**Visual:** Terminal screenshot — BLOCK output + tamper FAIL line.

---

## Slide 3 — Wedge + Ask

**Headline:** Regulated pilot — Copilot governance with exportable receipts.

**Bullets:**

- **Wedge:** Noetfield (Copilot policy governance) · TrustField (MSB / FINTRAC-adjacent controls).
- **Pilot scope:** 90-day design partner · read-only governance path · receipt JSONL export for compliance.
- **Market:** AI governance execution layer — Saidot/Credo class ACV; we sell **proof**, not prompts.
- **Ask:** Signed LOI or paid sandbox (CAD ≥2K) · intro to compliance owner · seed conversation post-pilot.

**Tier honesty (footer, small):**

- 6-month realistic: seed $3–10M @ $15–40M pre with demo + pilot signal.
- $100M narrative = 24-month game with ARR path — not promised this round.

**Do not say:** Trust OS · Decision Cloud · AWS for AI · 1000-pack hero.

**Close line:**

> Enterprise AI runs the model. SourceA runs the decision — with a receipt.

---

## Paste-ready one-liners

| Use | Text |
|-----|------|
| Email subject | Live demo: AI execution that fails when you tamper the receipt |
| LinkedIn DM | We block unapproved Copilot policy changes and prove allowed ones — want 15 min? |
| Investor hook | Governance infra with live tamper-FAIL — not another agent framework |
