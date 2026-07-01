# W1 Film Checklist — 5-Min Enforcement Demo (LOCKED)

**Saved:** 2026-07-01T10:42:00Z  
**Version:** 1.0 — LOCKED  
**route_id:** `locked_product_spec_doc`  
**sequence_id:** SA-2026-07-01-W1-FILM-CHECKLIST  
**Plan:** 555-04  
**Transcript proof:** `receipts/w1-demo-transcript-2026/W1_DEMO_TRANSCRIPT.txt`  
**Speaker script:** `investor/ENFORCEMENT_DEMO_5MIN.md`  
**Executor command:** `bash scripts/demo-enforcement-5min-v1.sh`

---

## One-take law

| Rule | Detail |
|------|--------|
| Pre-flight | Run transcript capture once before camera — all beats must PASS |
| On camera | Founder speaks · executor runs commands only |
| Forbidden | Discovery on camera · fake UI · claim M365 production integration |
| Done | `investor/media/W1_ENFORCEMENT_DEMO_5MIN.mp4` on disk → ANG-05 `[x]` |

---

## Pre-flight (T-15 min)

```bash
cd ~/Desktop/SourceA   # or repo root on cloud body
bash scripts/validate-demo-enforcement-v1.sh          # expect OK
bash scripts/demo-enforcement-5min-v1.sh | tee /tmp/w1-rehearsal.txt
grep -q BLOCKED /tmp/w1-rehearsal.txt && grep -q COMMITTED /tmp/w1-rehearsal.txt && grep -q "tamper detected" /tmp/w1-rehearsal.txt
```

| Check | Expect |
|-------|--------|
| Receipt dir writable | `~/.sina/demo-enforcement/receipts/` |
| BLOCK beat | `outcome: BLOCKED` · reason includes `approval_ref` |
| ALLOW beat | `status: DONE` · `spine_event_id` present |
| Tamper beat | `OK: tamper detected` |
| Category sentence memorized | *We make AI execution impossible to bypass governance.* |

---

## Equipment and framing

| Item | Spec |
|------|------|
| Camera | 1080p minimum · landscape 16:9 |
| Mic | Lapel or USB — founder voice primary |
| Screen capture | Terminal only — no browser chrome · font 18pt+ |
| Lighting | Face visible first 30s · then terminal dominates |
| Backup | Second device records screen independently |
| Output path | `investor/media/W1_ENFORCEMENT_DEMO_5MIN.mp4` |
| 90s cut output | `investor/media/W1_ENFORCEMENT_DEMO_90S.mp4` (ANG-10) |

**Framing:** Split or picture-in-picture — founder chest-up 0:00–0:30, full terminal 0:30–4:30, founder close 4:30–5:00.

---

## Beat sheet (5 min)

| Time | Beat | Founder says (short) | Executor runs | Screen must show |
|------|------|----------------------|---------------|------------------|
| 0:00 | Thesis | Category sentence + audit failure without proof | — | Title or blank terminal |
| 0:30 | **BLOCK** | "High-risk change without approval — watch the gate stop it." | `python3 scripts/commit_intent_v1.py --demo-enforcement --case block --json` | `BLOCKED` · P-001 · no DONE |
| 1:30 | **ALLOW** | "Same wedge with approval on record — one write path." | `python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --json` | `COMMITTED` · `DONE` · checksum |
| 2:30 | **Tamper** | "Insider edits receipt — validators are authority." | `bash scripts/validate-demo-enforcement-v1.sh --tamper-test` | `OK: tamper detected` |
| 3:30 | Trace (opt) | "Receipt links to spine — one audit chain." | optional spine lookup | `spine_event_id` match |
| 4:00 | Kill switch | "Freeze on disk — not a slide." | show FREEZE flag if present | flag file or honest skip |
| 4:30 | Disk truth | "We show RED before we lie GREEN." | `bash scripts/validate-demo-enforcement-v1.sh` | final OK lines |
| 5:00 | Close | "90-day pilot with exportable receipt bundle — who owns agent governance?" | — | founder face |

**Full speaker notes:** `investor/ENFORCEMENT_DEMO_5MIN.md`

---

## 90s email cut markers (ANG-10)

Edit from full W1 take — no re-record required.

| Mark | In | Out | Content |
|------|-----|-----|---------|
| A | 0:00 | 0:12 | Category sentence + thesis |
| B | 0:30 | 0:55 | BLOCK terminal output |
| C | 1:30 | 1:55 | ALLOW receipt + checksum line |
| D | 2:30 | 2:50 | Tamper FAIL lines |
| E | 4:30 | 5:00 | Close + pilot ask |

**Target file:** `investor/media/W1_ENFORCEMENT_DEMO_90S.mp4`  
**Use:** Angel email attach · LinkedIn DM · data room `03-Product/`

---

## Post-film checklist

- [ ] Full 5-min MP4 at `investor/media/W1_ENFORCEMENT_DEMO_5MIN.mp4`
- [ ] 90s cut at `investor/media/W1_ENFORCEMENT_DEMO_90S.mp4`
- [ ] Update entity matrix ANG-05 → `[x]` · ANG-10 → `[x]`
- [ ] Add video path to `investor/data-room-v1/MANIFEST.json`
- [ ] Upload redacted still (terminal BLOCK frame) to data room if no video hosting yet

---

## Honest counter (say if asked)

| Claim | Truth |
|-------|-------|
| Production M365 API | No — governance proof path; integration follows pilot |
| eval_packet structural mode | Absent on disk — validators are authority |
| W3 revenue | $0 — next economic signal is paid TrustField pilot |
| FREEZE flag | Optional beat — not required for W1 PASS |

---

*Locked for 555-04. Bump `Saved:` UTC when video lands.*
