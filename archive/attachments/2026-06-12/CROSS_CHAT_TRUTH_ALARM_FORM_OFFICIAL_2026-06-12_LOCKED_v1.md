# Cross-chat truth alarm — FORM_OFFICIAL (LOCKED v1)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-12  
**ASF order:** *EVERYTHING MUST BE ON THE FORM* — official human–machine conv  
**Law:** `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` §1 FORM_OFFICIAL · **Q-FORM-OFFICIAL** YES  
**Method:** Megachat anchors RT + transcript grep + form JSON + disk receipts — **not chat memory**  
**Form rows now:** core 11 + pending 8 + ENF 20 = **39 OPEN** (`live_founder_decision_form_v1.py --json`)

---

## Executive alarm — who is RIGHT / STALE / BAD / GOOD (2026-06-12)

| Who | Verdict | Say this |
|-----|---------|----------|
| **ASF FORM_OFFICIAL order** | **RIGHT** | Everything on form — chat backup only |
| **Maintainer 1 (`a53f3fa1`)** | **RIGHT (historical)** | Built PACK5 + M1 Canvas — **STALE** if used for live queue/AUTO-RUN |
| **Maintainer 2 (`74f5ccab`)** | **MIXED** | **GOOD:** RT LIVE · FR-003 · synthesis · **BAD:** 029 scratch canvas · 027 drain hero |
| **MonoRepo (`3369d11c`)** | **LANE RIGHT** | mx/runtime E2E — **BAD** if form picks imported without §OPEN append |
| **Gov Specialist** | **RIGHT** | Cascade · form JSON before hub · 3.07 NO — **STALE:** auto-send (028) |
| **Commercial Specialist** | **RIGHT** | 9.07 A · execution_authority false — **BAD:** Canvas tick = law |
| **SourceA Worker** | **STALE→FIXED** | Said confirm auto-send — **028** remediated logged |
| **Brain (`58148ac9`)** | **MIXED** | Law diagnosis **GOOD** — chat essays **BAD** vs form rows |
| **This chat (any agent)** | **BAD** if | Plain tables · no Canvas · no RIGHT/STALE tags |

---

## Megachat anchors (machine RT)

```bash
python3 scripts/ecosystem_master_catalog_v1.py --json → mega_chat_anchors
```

| ID | Workspace | Transcript | Role | Form relation |
|----|-----------|------------|------|---------------|
| **ECOSYSTEM / M1** | SinaaiDataBase | `a53f3fa1` | Retired · search only | **Built** PACK5 + M1 Canvas — **RIGHT** |
| **MAINTAINER_2** | SinaaiDataBase | `74f5ccab` | Active maintainer | Must **OPEN** M1 Canvas — **029 FAIL** if not |
| **MONOREPO** | SinaaiMonoRepo | `3369d11c` | SSOT · mx · runtime E2E | **Wrong lane** for founder form — MonoRepo ≠ PACK5 UI |
| **MONOREPO_PRIOR** | SinaaiMonoRepo | `720ee790` | Predecessor | Historical — do not set form picks from here |
| **BRAIN (this arc)** | SourceA | `58148ac9` | Brain executor | Bridge 039 miss · job-title sprawl — **partial BAD** |
| **GOV/COMMERCIAL** | SourceA | `e54ddfa8` | Gov + Commercial specialist | Scratch canvas **029 BAD** · synthesis **GOOD** |

---

## Alarm legend

| Tag | Meaning |
|-----|---------|
| **RIGHT** | Matches disk + form + PACK5 law today |
| **STALE** | Was true once; superseded by form v2 / RT LIVE / incidents |
| **BAD** | Violates FORM_OFFICIAL · LOST_LINK · 029 · chat-as-SSOT |
| **LANE** | Correct in its workspace; **wrong** if imported to form chat |

---

## Per-chat verdicts

### Maintainer 1 (`a53f3fa1`) — **RIGHT (historical) · search only**

| Claim / behavior | Verdict | Proof |
|------------------|---------|-------|
| INTEGRITY PACK 5 slots A–E | **RIGHT** | Batch 2 constitution |
| M1 Canvas choice4 model | **RIGHT** | `sourcea-system-integrity-100.canvas.tsx` |
| Bridge 039 continuity | **RIGHT** | `2026-06-12_M1-INTEGRITY-PACK5-CONTINUITY-039.md` |
| Early AUTO-RUN / n8n SoT engine prose | **STALE / REJECTED** | INCIDENT-022 · `auto-run-disabled-v1.flag` |
| Use as live queue head | **BAD** | Retired — search only |

### Maintainer 2 (`74f5ccab`) — **MIXED**

| Claim / behavior | Verdict | Proof |
|------------------|---------|-------|
| RT LIVE gate · FR-003 · form v2 | **RIGHT** | Receipt · §ANSWERED |
| Gov read order (form JSON first) | **RIGHT** | Cross-chat synthesis §1 |
| Built `live-founder-decision-form.canvas.tsx` | **BAD** | INCIDENT-029 · deleted |
| "Form in sidebar now" without proof | **BAD** | Screenshot error |
| Pending lists in chat not Canvas | **BAD** | §AGENT_DUTY forbidden |
| Hub drain hero after form filled | **STALE** | INCIDENT-027 · partial fix |

### MonoRepo Anchor (`3369d11c`) — **RIGHT in lane · STALE for form**

| Claim / behavior | Verdict | Proof |
|------------------|---------|-------|
| SinaaiRuntime :8000 · governance registry | **RIGHT** | MonoRepo disk |
| Two SSOT roots (Desktop vs Notice Board) | **RIGHT** diagnosis | GPT critique merged in anchor |
| Founder integrity form lives here | **BAD / LANE** | Form is SourceA PACK5 slot D in SinaaiDataBase canvases |
| Phase 0 declaration only | **RIGHT** | `SINA_OS_SSOT_LOCKED.md` |
| Import Mono picks into PACK5 Canvas | **BAD** | Wrong plane — append to form §OPEN with evidence only |

### Gov Specialist (disk + `e54ddfa8`) — **MOSTLY RIGHT**

| Claim / behavior | Verdict | Proof |
|------------------|---------|-------|
| Zero governance latency = cascade not second audit | **RIGHT** | `governance_propagation_cascade_v1.py` |
| Read form JSON before hub hero | **RIGHT** | INCIDENT-027 law |
| INCIDENT-029 filing | **RIGHT** | Registry row 029 |
| Validators 31/31 GREEN (Mono verify) | **RIGHT** | If bundle run today — re-prove each session |
| "Confirm → auto-send" prompt feed | **STALE** | INCIDENT-028 remediated |
| Commercial GOV_UNIFY batch | **STALE** | Form pick **3.07 NO** |

### Commercial Specialist — **RIGHT (advise lane)**

| Claim / behavior | Verdict | Proof |
|------------------|---------|-------|
| `execution_authority: false` | **RIGHT** | Draft PICKs only |
| 9.07 A W1+W3 parallel | **RIGHT** | §ANSWERED · batch 2026-06-12 |
| Canvas checkbox = law | **BAD if claimed** | Batch 2 §14.3 — ASF paste required |
| Thread-integrated standing order | **RIGHT** | Scan T30 — tag THREAD-* on **form rows** not chat essays |

### Brain SourceA (`58148ac9`) — **MIXED**

| Claim / behavior | Verdict | Proof |
|------------------|---------|-------|
| Law without gates diagnosis | **RIGHT** | Matches incident corpus |
| Duplicate bridge before 039 | **BAD** | LOST_LINK |
| Three job-title LOCKED docs | **STALE risk** | Scope creep — catalog on form row only |
| PICK batch 2026-06-12 to disk | **RIGHT** | Receipt shipped |
| Chat essays instead of form rows | **BAD** | FORM_OFFICIAL violation |

---

## FORM_OFFICIAL gap (honest · updated)

| On form (law + machine) | On Canvas UI (you click) |
|-------------------------|---------------------------|
| **Q-FORM-OFFICIAL** YES locked | **39 rows** in `--json` after ENF+pending merge |
| **ENF-01..20** | YAML → machine §OPEN · Canvas cards **in progress** |
| **§PENDING migrated** | 8 rows now §OPEN — not law-only |
| **Hub Track banner** | Gold **39 QUESTIONS** after Refresh |
| **Canvas compile** | Must prove before “visible” claims (029) |

**Open form:** `~/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx`

---

## Mandatory alarm procedure (all chats)

```text
EVERY REPLY
  1. SCAN  live_founder_decision_form_v1.py --json
  2. OPEN  M1 Canvas if open_questions_count > 0
  3. TAG    each claim: RIGHT | STALE | BAD | LANE
  4. SAY    from form rows — max 5 lines
  5. SHIP   new forks → §OPEN_QUESTIONS + Canvas — never chat-only
```

**FORBIDDEN:** cross-chat summary without form row · stale hero · scratch canvas · "sidebar ready" without compile proof

---

*Companion: MAINTAINER_2_CROSS_CHAT_GOV_COMMERCIAL_INCIDENT_SYNTHESIS_LOCKED_v1.md · INCIDENT-029*
