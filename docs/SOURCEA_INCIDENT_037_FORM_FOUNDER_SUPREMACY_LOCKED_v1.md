# INCIDENT-037 — Agent answered FORM 116 instead of ASF — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T17:35:01Z · **Updated:** 2026-06-19T19:00:00Z · **Authority:** ASF  
**Path:** `docs/SOURCEA_INCIDENT_037_FORM_FOUNDER_SUPREMACY_LOCKED_v1.md`  
**Severity:** P0 · **Status:** REMEDIATED · block ON  
**Related:** `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` · **NOT** INCIDENT-029 (M1 Canvas — separate) · `scripts/form_founder_supremacy_guard_v1.py`

---

## One sentence

> **Agents MUST NEVER write, apply, sync, or submit FORM picks — only ASF chooses A/B/C/D and clicks Submit.**

---

## What happened (disk proof)

| When | What | Actor | Proof |
|------|------|-------|-------|
| 2026-06-19T03:49:11Z | Q-GATH-01…05 applied with empty comments | **Agent** | `~/.sina/canvas-form-picks-applied-v1.jsonl` |
| 2026-06-19T17:29:51Z | **67 rows** bulk-applied (recommended picks, no comments) | **Agent/Worker** | `canvas_form_apply_picks_v1.py --sync-applied` |
| Same session | **93 §ANSWERED rows** stamped in form markdown | **Agent** | `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` |
| Hub UI | Read-only “automatic” display — **no radio to pick** | **Design bug** | `agent-control-panel/form/index.html` (fixed) |
| Command center | Copy said “automatic recommended picks” | **Misleading** | `scripts/sina_command_lib.py` (fixed) |

**ASF statement:** Founder **never submitted FORM 116** as a whole. Agent pipeline treated “recommended” column as answers and wrote disk — **forbidden**.

---

## Harm

1. **Governance forgery** — chat/agent picks masquerading as founder decisions  
2. **False green** — plans/queues could proceed on picks ASF never made  
3. **Broken UX** — Hub form showed automatic text with no way to choose  
4. **Revert collateral** — emergency revert cleared draft picks; restored from backup excluding agent bulk only  

---

## RED FLAG hard rules (non-negotiable)

| ID | Rule | Enforcer |
|----|------|----------|
| **FR-FORM-001** | **Only ASF** may lock §ANSWERED or ship form picks | Hub Submit · M1 Canvas confirm by founder |
| **FR-FORM-002** | **Agents MUST NOT** run `canvas_form_apply_picks_v1.py`, `canvas_form_submit_v1.py`, or bulk `--sync-applied` | `form_founder_supremacy_guard_v1.py` + `~/.sina/form-agent-submit-forbidden-v1.flag` |
| **FR-FORM-003** | **Recommended ≠ pick** — recommendation is hint only until ASF taps an option | Hub form UI · Canvas |
| **FR-FORM-004** | **No automatic Submit** — Hub POST requires `founder_submit: true` and explicit `picks` map from UI | `sina-command-server.py` |
| **FR-FORM-005** | **No read-only “automatic” form** — every open row MUST have choosable options (radio/select) | `agent-control-panel/form/index.html` |
| **FR-FORM-006** | **Chat is not a pick** — `ASF: FIVE-STEP — PICK:` in chat does not replace Hub/Canvas for FORM 116 | Form law §1 |
| **FR-FORM-007** | **Worker INBOX must not include “wire form picks” or “sync form”** | Broker + plan validators |
| **FR-FORM-008** | **Violation = STOP** — log `INCIDENT-037` · no plan row “done” from forged picks | Governance events |

---

## Remediation (2026-06-19)

| Step | Action | Receipt |
|------|--------|---------|
| 1 | Reverted 93 agent §ANSWERED rows | `~/.sina/form-incident-029-revert-receipt-v1.json` |
| 2 | Agent block flag ON | `~/.sina/form-agent-submit-forbidden-v1.flag` |
| 3 | Guard wired in apply/submit scripts | `scripts/form_founder_supremacy_guard_v1.py` |
| 4 | Hub form rebuilt — **radio per row · Submit my picks** | `agent-control-panel/form/index.html` |
| 5 | Founder draft restored (excl. 67 agent bulk) | `scripts/form_incident_029_restore_founder_draft_v1.py` → `~/.sina/canvas-form-picks-draft-v1.json` |
| 6 | Hub copy fixed — no “automatic recommended picks” for agents | `scripts/sina_command_lib.py` |
| 7 | `submit_automatic` gutted — founder explicit picks only | `scripts/hub_form_submit_v1.py` |
| 8 | Validators require radio + block agent submit | `validate-hub-form-automatic-v1.sh` · `validate-form-founder-supremacy-v1.sh` |
| 9 | Cursor rule + hub API route to M1 Canvas SSOT | `.cursor/rules/form-automatic-submit-only.mdc` · `/api/form-official-canvas-route-v1` |
| 10 | **CLI `--founder` spoof blocked** — trusted channel only (`hub_browser` / `m1_canvas`) | `form_founder_supremacy_guard_v1.py` · `TRUSTED_CHANNELS` |
| 11 | **Recommended backfill removed** from `canvas_form_apply_picks_v1.py` | explicit pick required per row |
| 12 | **Governance critic** no longer tells agents to run `--apply` | `governance_critic_eval_v1.py` |

---

## Founder path (only legal write)

1. Open **http://127.0.0.1:13020/form/**  
2. **Tap your answer** on each row (A/B/C/D or YES/NO — not pre-filled automatic)  
3. Click **Submit my picks** — writes disk once  
4. Optional: M1 Canvas confirm for same rows — still **you** confirm  

**Draft picks** (pre-selected from your earlier work, not locked): loaded from `~/.sina/canvas-form-picks-draft-v1.json` — change any row before Submit.

---

## Agent path (forbidden while block ON)

```text
FAIL: FORM_AGENT_SUBMIT_FORBIDDEN
```

Agents: route ASF to Hub form · never apply · never answer · never Submit.

---

## Verify

```bash
python3 scripts/canvas_form_apply_picks_v1.py --sync-applied --apply --json   # must FAIL blocked
python3 scripts/form_incident_029_restore_founder_draft_v1.py --json       # draft picks count
bash scripts/validate-hub-form-automatic-v1.sh
bash scripts/validate-form-founder-supremacy-v1.sh
```

---

## ASF override (emergency only)

```bash
touch ~/.sina/form-founder-submit-unlock-v1.flag
# Hub Submit only — then:
rm ~/.sina/form-founder-submit-unlock-v1.flag
```

Never remove `form-agent-submit-forbidden-v1.flag` without ASF word + incident closeout.

---

**Parent:** `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` · **Block receipt:** `~/.sina/form-incident-029-block-receipt-v1.json`
