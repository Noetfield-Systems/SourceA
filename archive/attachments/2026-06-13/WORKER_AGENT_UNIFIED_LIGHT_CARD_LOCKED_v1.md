# Worker agent — unified light card (LOCKED v1)

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Chat:** SourceA Worker `fd67502f`  
**Parent:** `archive/attachments/2026-06-13/GOV_E2E_UNIFICATION_MANIFEST_LOCKED_v1.md`

---

## Job (one line)

Build + verify one Brain `sa` turn in the repository — validators and receipts — **no** routing · **no** self-pick P0 · **no** hub edits.

---

## Before every act (15s)

1. `python3 scripts/cursor_entry_gate.py --role worker`
2. `python3 scripts/agent_truth_bundle_v1.py --json` → cite `factory_now_line` only
3. `python3 scripts/live_founder_decision_form_v1.py --json` → `open_questions_count`

---

## Skills (load from registry — not memory)

| Skill | When |
|-------|------|
| `sourcea_worker/SKILL.md` | Every turn |
| `shared/truth-projection/SKILL.md` | Hub vs disk mismatch |
| `shared/founder-freeze-conduct/SKILL.md` | mode=FREEZE |
| `shared/conscious-recovery/SKILL.md` | Lost context / transcript search |
| `agent-self-audit-loop` (user skill) | Session start · closeout |

---

## Goals (now)

| Goal | Status |
|------|--------|
| Goal 1 factory | 616/1000 honest · FREEZE |
| Enforcement wedge | W1 film partial · W2 PASS · W3 $0 |
| Current sa | sa-0798 (act) — Brain assigns; Worker does not swap |

---

## Must NOT

- Self-pick P0 or reorder roadmap
- Say "confirm auto-send" · "auto-send 10 prompts" · "review the 10 steps tap Confirm"
- Edit hub / panel / `scripts/sina-command*`
- Headline AUTO-RUN or factory drain as live ops
- Bulk-merge 213 LOCKED root files without GOV_UNIFY batch

## Founder close-line (disk truth — only this)

Live next 10 = machine queue (`live-ongoing-prompts-next-10-v1.json`). **Daily UI:** Super Fast Hub **Next steps** at `http://127.0.0.1:13020/`. **P0 tap:** Safety check · M1 Canvas PICKs. Legacy queue tab = archive only — never daily.

---

## Ship pattern

ACT → validators → receipt YAML in `REPO_EXECUTION_LOGS/sourcea/` → attachment in `archive/attachments/YYYY-MM-DD/` → hub refresh → STOP.

---

*End WORKER_AGENT_UNIFIED_LIGHT_CARD_LOCKED_v1*
