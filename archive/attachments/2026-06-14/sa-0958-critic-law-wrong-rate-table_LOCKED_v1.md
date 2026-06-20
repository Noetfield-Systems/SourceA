# sa-0958 — Critic law effectiveness · external chat wrong-rate table

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules**

## Law in force

| Artifact | Role |
|----------|------|
| `brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | Classify · compare · verdict · no reorder |
| `.cursor/rules/chatgpt-external-critic.mdc` | Mandatory first line `INPUT CLASS: EXTERNAL_CRITIC` |
| `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | Critic rank 5 — ASF + LOCKED win |

## External chat wrong-rate table (incident-derived)

| Failure mode | What went wrong | Incident / evidence | Est. rate* | Critic law fix |
|--------------|-----------------|---------------------|------------|----------------|
| **Skipped INPUT CLASS** | Treated GPT paste as ASF order | INCIDENT-005a · **~15% compliance** on label | **High miss** | §4 step 1 — first line mandatory |
| **Reorder from critic** | Changed build order / step IDs from audit table | INCIDENT-004 goal hierarchy · 003b Brain/Worker mix | **Medium** | §4 step 5 — keep build order |
| **Ship critic as law** | GPT prose → hub / LOCKED without §6 | INCIDENT-005a Gatekeeper from paste | **Low but severe** | §5 MUST NOT · convince gate |
| **Duplicate step IDs** | Critic invents D0 / new phases | WTM v5 audit — **rejected** in §7 example | **Common in paste** | Verdict: reject · map to existing |
| **Valid gap missed** | Agent rejects true observation | Less documented — law §7 shows accept path | **Low** | Accept observation · SSOT patch w/ ASF yes |
| **Hub tables from critic** | Founder UI shows GPT score tables | Law §5 — critic MUST NOT push hub tables | **Prevented when law obeyed** | Reject always |
| **Mixed message mishandled** | ASF clause executed + paste steered build | chatgpt-external-critic.mdc — split message | **Medium** | Split: ASF clauses + critic §4 only |

\*Rates are **qualitative** from incident compendium — not automated telemetry. INCIDENT-005a is the only quantified compliance metric (~15% label compliance pre-remediation).

## Critic content accuracy (WTM v5 worked example — law §7)

| Critic claim type | Typical outcome | Wrong-rate feel |
|-------------------|-----------------|-----------------|
| Architecture direction (A→B→C→D) | ✅ Accept observation | **Low wrong** |
| Governance gap (memory, planning ambiguity) | ✅ Valid → law clause | **Low wrong** |
| “Missing step” (already in SSOT as D7 etc.) | ❌ Reject — critic missed disk | **High wrong** on step inventory |
| “Reorder phases / build X next” | ❌ Reject always | **Very high wrong** as build steering |
| Score / verdict tables | Input only — never authority | **N/A** — not truth |

## Effectiveness verdict

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Prevents catastrophic reorder** | **Strong** when obeyed | INCIDENT-004/005 class harm |
| **Agent compliance** | **Weak historically (~15%)** | Probation + `.mdc` wire improved; needs audit loop |
| **Extracts value** | **Moderate** | §7 example — good gaps adopted, bad steering rejected |
| **Founder clarity** | **Strong** | §0 plain language — paste ≠ order |
| **Missing instrumentation** | **Gap** | No auto counter for label/§6 compliance — research only |

## Recommendations (deferred — no build this sa)

1. **Session audit** — sample last N critic pastes → label present? §6 table? (maintainer script — ASF order)
2. **Never** add critic score tables to hub UI (already law)
3. **Keep** convince gate for any critic-derived law patch

**ACT shipped:** wrong-rate + effectiveness table only.

**One-line:** Critic law is **high-leverage guardrail** with **low historical compliance** — external chat is **often wrong on build steering**, **sometimes right on governance gaps**.
