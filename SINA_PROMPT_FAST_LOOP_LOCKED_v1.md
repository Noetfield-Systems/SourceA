# Sina Prompt-Fast Loop — Canonical 10 (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**sequence_id:** SA-2026-06-04-027  
**Supersedes:** informal “analyze everything every round” habit  
**Related:** `SINA_AGENT_LOOP_ORDER_v1.md` · `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`

---

## Three stacked loops (not one)

| Layer | Where | Cadence | Founder mental model |
|-------|--------|---------|----------------------|
| **Meta / prompt fasting** | Command chat · Prompt feed · prompt-direction | Last reply → big picture → up to 10 prompts → **queue in app only** (no auto-paste) | Think here, execute elsewhere |
| **Factory / 10-round loop** | Private agents · `[SINA_LOOP n/10]` · `AGENT_LOOP_ROUND*.md` | One round = one task → work → **Submit round** in app | Ship P0 with receipts |
| **Repo execution** | Per-repo `os/plan.json` · Prompt OS dispatch | One repo · one task · VERIFY · update plan | FAST TRACK — no global wait |

**Founder law (all layers):** you click — Refresh, Confirm direction, Start loop, Submit round, Send next. Agents run Terminal/API; you do not.

**Compression rule:** In one session, pick **either** a full prompt-direction 10 **or** a full agent-loop 10 for one P0 — not both back-to-back unless the plan says “orchestration sprint.”

---

## Canonical 10 — one round OR one fasting session

| Step | Name | Do | Stop when |
|------|------|-----|-----------|
| 1 | **Snapshot** | Refresh hub; P0 + open blockers + this agent’s pack row | One screen of facts |
| 2 | **Plan** | Goal, thread, non-goals, done criteria (≤8 lines) | Plan fits one card |
| 3 | **Implement** | One concrete deliverable (file / audit / API) | Bounded diff |
| 4 | **Verify backend** | Script/audit/API proves step 3 | Exit 0 or logged FAIL |
| 5 | **Verify UI** | One Sina Command path OR `ui_e2e: "N/A"` with reason | Audit OK / noted |
| 6 | **Fix loop** | Only if 4–5 failed; max 2 tries | Green or escalated blocker |
| 7 | **Summarize** | PASS/FAIL + 3 founder bullets | Round MD + receipt line |
| 8 | **Near-miss** | 0–3 bullets: almost broke X | **Required** in receipt (can be `[]`) |
| 9 | **Lock** | Receipt + locked doc pointer; Submit round / queue next | Next step ready in **app** |
| 10 | **Delta analyze** | **Only** new risks/blockers vs step 1 | Feeds step 2 next cycle |

**After round 1:** Round MD sections 1–3 (goal, blockers, P0) become a **delta block** only — do not full-rescan the ecosystem every round.

---

## Meta layer (prompt-direction) — steps 1–2 + 9 planning

1. `set_context` — founder’s last AI reply  
2. `propose` — big picture + 10-step outline  
3. Founder **confirms in app** (auto-paste **OFF**)  
4. `confirm` → 10 prompts → **prompt queue** (manual copy if needed)

This is **analyze → plan → 10 fast prompts** before or beside the coding loop — not a substitute for Verify UI / near-miss in receipts.

---

## Factory layer — maps to steps 3–9

Private agent page → Start loop → each round executor fills:

- `AGENT_LOOP_ROUNDn.md` — human narrative (use delta after round 1)  
- `runreceipt/run.jsonl` — machine line (schema below)  
- `runreceipt/summary.json` — aggregate  
- `runreceipt/receipt-pack.html` — founder-readable table  

**Inject:** Round prompt appears in **Private agents UI + INBOX** only. **Never** auto-paste into Cursor (`SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`).

---

## RunReceipt line schema (required fields from step 4 onward)

```json
{
  "round": 1,
  "ts": "2026-06-04T12:00:00Z",
  "plan": "P0-RUNRECEIPT",
  "outcome": "PASS",
  "summary": "one line",
  "blockers": ["B-001", "MP-SHIP", "WIRE-G3"],
  "backend_verify": {"ok": true, "detail": "audit_backend_e2e or script name"},
  "ui_e2e": {"ok": true, "detail": "tab path or N/A reason"},
  "near_misses": ["optional bullet 1"],
  "delta_vs_round1": ["only from round 2+"]
}
```

---

## Where Sina OS beats “pro prompt fasting”

- Governance + lock-in (B-001 class collisions)  
- Meta ≠ execution ≠ Live agents (no wrong-chat paste)  
- Receipts: `run.jsonl` + round MDs  
- UI E2E explicit (step 5)  
- Parallel lanes — repo blocked ≠ ecosystem paused  

## Where to compress like pros

- Steps 1+10: delta-only after round 1  
- One outcome per session (one PR or one receipt pack)  
- CI/script = “check fully” for backend; UI = one path not full manual QA every time  

---

**LOCKED:** Maintainer 10-pack for P0 should align to steps 1–10 above — see `SinaaiDataBase/prompts/loop-pack-prompt-fast-10.json`.
