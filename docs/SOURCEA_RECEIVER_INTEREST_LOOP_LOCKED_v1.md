# Receiver Interest Loop — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-18T19:32:00Z · **Status:** LOCKED
**Path:** `~/Desktop/SourceA/docs/SOURCEA_RECEIVER_INTEREST_LOOP_LOCKED_v1.md`
**Authority:** Founder · factory builder — recipient POV, not sender POV
**Phase:** POST-DESIGN

**Parents:**
- `docs/SOURCEA_FACTORY_OUTPUT_CRITIC_LOOP_LOCKED_v1.md` (Critic Circle · improve until true)
- `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_STANDARD_LOCKED_v1.md` (FEFS · human persuasion)
- `docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md` (Best Loop · machine OQG)

---

## 0. One law

> **Machine OQG can PASS while the recipient has nothing interesting to click.**  
> **Receiver Interest Loop (RIL)** scores only from the recipient's chair: preview · catalog · demo · website — tied to **their** world.

Better Loop = system running · Best Loop = machine ≥90% · Critic Circle = close gap · **RIL = would they want to know more?**

---

## 1. Separate loop (do not merge with OQG)

| Loop | Question | Script |
|------|----------|--------|
| Best Loop OQG | Structural + FEFS on disk? | `best_loop_oqg_score_v1.py` |
| Critic Circle | One fix until true ≥90%? | `factory_output_critic_circle_v1.py` |
| **Receiver Interest** | Click-worthy preview for **this** recipient? | `receiver_interest_loop_v1.py` |

---

## 2. RIL rubric (100 pts · bar 90)

| ID | Check | Max |
|----|-------|-----|
| RIL1 | Clickable preview/demo/catalog URL in body | 25 |
| RIL2 | URL reachable (HEAD/GET) | 15 |
| RIL3 | Recipient-specific hook (their world named) | 25 |
| RIL4 | Concrete preview promise — not empty "I can walk through" without link | 20 |
| RIL5 | Canonical brand demo/catalog URL from SSOT | 15 |

**SSOT assets:** `data/w3-receiver-interest-assets-v1.json`  
**Receipt:** `~/.sina/receiver-interest-loop-receipt-v1.json`

---

## 3. Observe · Improve (factory repeatable)

1. **Observe** — read W3 pack body + per-account interest asset row  
2. **Analyze** — RIL score vs 90 · list failures  
3. **Improve** — one bounded fix: add demo link · sharpen Ocree/Fundmore hook · re-pack  
4. **Re-run** — `receiver_interest_loop_v1.py --json` until PASS  

Critic circle and Better Loop pulse **surface** RIL red — they do not replace RIL scoring.

---

## 4. Ship gate (W3)

All required before send:

- Machine OQG ≥90%
- **Receiver interest ≥90%**
- Critic circle PASS
- Founder score ≥90%
- Pipeline send slot cleared · Mail FROM · confirm-sent

---

## 5. FEFS addendum (R11)

**R11 — Recipient must see one interest path:** Every W3 first touch includes at least one reachable preview/demo/catalog URL from brand SSOT — not a calendar placeholder alone.

Fail: "I can walk through a five-minute example" with **no link**.
