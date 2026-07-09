> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# SOURCEA 1000 LOCKED prompt library — PLAN WITH NO ASF (v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-06  
**Authority:** `SINA_OS_SSOT_LOCKED.md` · maintainer lane `sourcea`  
**Machine index:** `os/plan-library/sourcea-1000/REGISTRY.json`  
**Count:** 1000 (10 phases × 4 tiers × 25)

---

## Trigger

When you say **PLAN WITH NO ASF**, the agent:

1. Picks next backlog prompt: `bash scripts/plan-no-asf-run.sh pick 1`
2. Reads prompt file → **Agent prompt** section
3. Implements with minimal diff — **no fluff**
4. Runs verify gate from prompt tier
5. Marks `status: done` + updates `SOURCEA-PRIORITY.md`
6. Re-runs `bash scripts/validate-sourcea-1000-pack.sh`

**Founder law:** Hub Refresh / Actions / tabs only — no Terminal.  
**Forbidden:** ASF as verify/progress authority · `dispatch_ready:true` globally · fabricated G3.

---

## Quick commands

```bash
# Pick next task
bash scripts/plan-no-asf-run.sh full 1

# Validate pack
bash scripts/validate-sourcea-1000-pack.sh

# Regenerate (taxonomy change only)
python3 scripts/generate-sourcea-1000-prompts.py
```

---

## Sources synthesized into this pack

| Source | Role |
|--------|------|
| `execute_v6_no_asf` plan | Maintainer phases 0/2/5 + founder P1/P3/P4 gates |
| `SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` | GPT/Claude/Cursor verdicts |
| `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` | Goals, pendings, this_week |
| `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | D-layer + L-layer roadmap |
| `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | Compare only — never steer build |
| Live `~/.sina/*` + validators | Machine truth over chat |
| `mono-1000` / `noetfield-1000` packs | Workflow pattern parity |

---

## Phase map (long-term)

| Phase | IDs (approx) | Theme |
|-------|----------------|-------|
| s0 SSOT | sa-0001–0100 | Drift fixes, synthesis sync, honest_score |
| s1 Eval | sa-0101–0200 | Eval-1b CI, dispatch, grounding |
| s2 Build | sa-0201–0300 | strict build, E2E, refresh perf |
| s3 Fleet | sa-0301–0400 | auto-green, essays, FR tracker |
| s4 Spine | sa-0401–0500 | loop closure, event bus, graph executor |
| s5 Commercial | sa-0501–0600 | RunReceipt, Wire, TrustField |
| s6 WTM | sa-0601–0700 | D1–D16, L0–L16, ENFORCE |
| s7 Council | sa-0701–0800 | governance moat, mind share |
| s8 Hub UI | sa-0801–0900 | panels, lazy load, founder UX law |
| s9 Research | sa-0901–1000 | model compare, deferred L8/OpenRouter |

---

## Status at lock

- **Done:** sa-0001–sa-0075 (v6 maintainer shipment)
- **Backlog:** sa-0076–sa-1000 (long-term execution)
- **Founder-only:** pinned spine bridge, fleet 6, Wire G3, TrustField pilot

---

## World-model comparison (insight)

| Dimension | Sina SourceA hub | Typical agent IDE product |
|-----------|------------------|-------------------------|
| SSOT | Locked docs + validators + `~/.sina` | Chat memory / ad-hoc |
| Pre-LLM packet | D1–D16 assembled context | Raw repo grep |
| Verify | `auto_pass` + CI scripts | Human click / none |
| Governance | Rules-in-charge + scoreboard fleet | Single-user |
| Gap | IDE ENFORCE bypass · fleet proof volume | No packet layer |

---

## Index files

- [`os/plan-library/SOURCEA-1000-LOCK.md`](os/plan-library/SOURCEA-1000-LOCK.md)
- [`os/plan-library/SOURCEA-PRIORITY.md`](os/plan-library/SOURCEA-PRIORITY.md)
- [`os/plan-library/sourcea-1000/VALIDATION.md`](os/plan-library/sourcea-1000/VALIDATION.md)
