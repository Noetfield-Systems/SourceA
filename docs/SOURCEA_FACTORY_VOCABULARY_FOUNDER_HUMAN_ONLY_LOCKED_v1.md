# Factory vocabulary — FOUNDER = human Sina only — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-18T21:05:49Z-06-18T21:04:57Z · **Status:** LOCKED
**Path:** `~/Desktop/SourceA/docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md`
**Authority:** Founder (Sina Kazemnezhad · human only)
**Machine mirror:** `data/sourcea-forge-vocabulary-disambiguation-v1.json`

---

## 0. One law

> **Founder** means **Sina Kazemnezhad (human) only.**  
> Never machines · never AI critics · never GPT · never Gemini · never advisors · never other humans.

---

## 1. Allowed uses of “founder”

| Term | Meaning | Who sets it |
|------|---------|-------------|
| **Founder** | Sina Kazemnezhad | — |
| **Sina read score** / `sina_read_score_pct` | Human 0–100 after reading full email | **Sina only** |
| **Advisor pre-call email** | `advisor_pre_call` lane — human clarity loop | APC loop + **Sina read** ship |
| **Founder daily path** | RUN INBOX · Hub glance | Sina's ops |

---

## 2. Forbidden uses of “founder” (rename on sight)

| Wrong | Correct |
|-------|---------|
| GPT founder score | **Advisor critique** or **external LLM opinion** — not ship authority |
| Gemini founder reviewer | **Advisor critique** |
| Machine founder score | **machine_oqg_pct** · **conversation_interest_pct** · **receiver_interest_pct** |
| AI critic founder | **Critic circle verdict** (machine) |
| `founder_checks` on pulse | **`ship_checks`** — system gates, not Sina acting |
| `founder_approved` on send | **`pipeline_send_slot: cleared`** (workflow) |
| “Human founder” for anyone else | **Sina** or **recipient executive** (name the role) |

---

## 3. Score ladder (canonical names)

| # | Field | Who | Ship authority |
|---|-------|-----|----------------|
| 1 | `machine_oqg_pct` | Machine OQG | No |
| 2 | `conversation_interest_pct` | Conversation Loop (CIL) | No |
| 3 | `receiver_interest_pct` | Receiver Interest Loop (RIL) | No |
| 4 | `brain_lane_line` | Brain inject | **Never** |
| 5 | `pipeline_send_slot` | Hub workflow | No (not quality) |
| 6 | `sina_read_score_pct` | **Sina (human) only** | **Yes — final quality** |
| 7 | `advisor_critique` | GPT/Gemini/external | **Never** |

---

## 4. Ship gate (W3)

Send requires **Sina read ≥90** — not machine ≥90, not advisor opinion, not critic PASS alone.

---

## 5. Forge name disambiguation (INCIDENT-034 — mandatory)

Five names — never substitute:

| Say | Means | Never confuse with |
|-----|-------|-------------------|
| **Forge** (capital F) | **Product** — AI-native dev platform · `~/Desktop/forge` · THREAD-FORGE | ICP compile · machine prove · Governed App Factory |
| **ICP compile** | FDG failure moment → specialized body → CIL/RIL/OQG → RRL → Sina read | “forge email” · legacy icp-forge paths · `forge ocree` |
| **Governed App Factory** | FBE factory line 3 — governed app deploy packs | Forge product |
| **machine prove** | Calibrate · Tune · Prove upgrade gauntlet | Forge product · ICP compile |
| **DevBridge** | Cursor extension + MCP wire lane — subset of Forge integration | Forge product (not equal) |

**Founder trigger word `forge`** still runs `machine_forge_pipeline_v1.py` — agents label it **machine prove** in prose.

**Deprecated paths (rename on sight):** see `data/sourcea-forge-vocabulary-disambiguation-v1.json` → `drift_watch.stale_terms` and `replacements` (full path table on disk — do not resurrect old compile dir names).

---

## 6. Brand ICP compile order (commercial factory)

**Active brands only:** SourceA → Noetfield → TrustField

```text
1. SourceA   (fbe_sourcea · e.g. sourcea-factory)
2. Noetfield (w3_commercial · e.g. fundmore)     — gate: blocked_until_sourcea_compiled
3. TrustField (w3_commercial · e.g. ocree)       — gate: blocked_until_noetfield_compiled
THEN: Forge product build (~/Desktop/forge)
THEN: WitnessBC · 777 Foundation · advisor_pre_call (deferred — not front door)
```

**Law:** ICP compile is the email/output factory. **Forge** is the future product repo — not the verb for composing email.

---

## 7. Disk routing

| Topic | Path |
|-------|------|
| This law | `docs/SOURCEA_FACTORY_VOCABULARY_FOUNDER_HUMAN_ONLY_LOCKED_v1.md` |
| Machine mirror | `data/sourcea-forge-vocabulary-disambiguation-v1.json` |
| Email factory v2 | `docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md` |
| ICP compiler SSOT | `data/icp-output-compiler-v1.json` · `scripts/icp_output_compiler_v1.py` |
| ICP compile accounts | `data/icp-compile/{account}-v1.json` |
| Machine three pipelines vocab | `data/machine-three-pipelines-vocabulary-v1.json` |
| Sina read bundle | `scripts/w3_founder_review_v1.py` → `~/.sina/w3-founder-review-v1.json` |
| Advisor pre-call | `docs/SOURCEA_ADVISOR_PRE_CALL_EMAIL_STANDARD_LOCKED_v1.md` · `scripts/advisor_pre_call_email_loop_v1.py` |
