# Founder museum erasure perception — H1 default replaced monolith without visible museum link (INCIDENT-032 LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-14-INCIDENT-032  
**Classification:** MANDATORY READ — Brain · Maintainer · Worker · any agent answering hub/archive questions  
**Agent:** Cursor Brain/Worker (SourceA session — Super Fast Hub ship + archive wording)  
**Window:** 2026-06-14 (founder screenshot + *"you literally erase founder museum"*)  
**Related:** INCIDENT-025 (name fragmentation) · INCIDENT-031 (stale hub steer) · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · near-miss `BRAIN_ARCHIVE_WORDING_MISLEAD_NEAR_MISS_2026-06-14_LOCKED_v1.md` · backlog **AR-b9955efbce** (`/oldhubsinacommand/`)

---

## 1. Executive summary

Founder opened **`http://127.0.0.1:13020/`** and saw the **H1 Worker Hub** (sa-0529 · Form clear · 0 open PICKs · alarm strip) instead of the full **Sina Command monolith** they know as the **founder museum** — every tab, subject, Action, and historical surface in one place.

Agents described the old hub as **"archived"** without a prominent **read-only museum URL** on the default home. Founder experience: **the museum was erased**.

**Disk truth (2026-06-14 verify):** the museum was **not deleted**.

| Asset | Status |
|-------|--------|
| `agent-control-panel/command-data.json` | **10.7 MB** — intact |
| `agent-control-panel/index.html` | **9.4 KB** monolith shell — intact |
| `GET http://127.0.0.1:13020/legacy/` | **HTTP 200** — serves frozen monolith |
| `~/.sina/live-founder-decision-form-v1.json` | **11 KB** — v2 answers + history |
| `archive/attachments/2026-06-11/` … `2026-06-12/` form LOCKED snapshots | **Present** — 52 applied picks · 0 open remaining |
| `~/.sina/founder-picks-applied-v1.jsonl` | **Present** — pick receipt log |

**Severity:** **Critical (perception + trust)** — founder believes founder-owned UI and picks were destroyed. Even when data survives, **default-surface replacement without museum link** is indistinguishable from erasure.

**One-line verdict:** **H1 may be default for workers — never without a first-class, labeled Founder Museum link and zero "erased/archived" language without URL + disk receipt.**

---

## 2. What founder calls "founder museum"

| Founder term | SSOT name | What it is |
|--------------|-----------|------------|
| **Founder museum** | Legacy Sina Command monolith | Full `agent-control-panel/` — all tabs, subjects, Actions, agent loop, backlog, advisor surfaces |
| **Not museum** | H1 Super Fast Hub | `worker-hub/index.html` — worker task · health · form slice · alarms only (~4 KB API) |
| **Not museum** | H2 Machine Hub | `http://127.0.0.1:13020/machines/` — heavy machines · pending tables |
| **Anti-pattern label** | "feature museum" | Deliberately avoided in new UI (`founder-light-v1`, `HUB_UI_IA_UPGRADE_PROPOSAL_v3`) — **founder still uses "museum" for the old monolith** |

**Law:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §0 — H1 at `/` · Archive at `/legacy/` · H2 sibling. **Law does not excuse hiding the museum from the founder's default bookmark.**

---

## 3. What founder saw (screenshot 2026-06-14 ~08:04)

| UI element | Value | Founder read |
|------------|-------|--------------|
| Title | **Source A · Worker** | "This is not my Command" |
| Banner | Super Fast Hub (H1) · Machine Hub (H2) · **Legacy archive** | Archive sounds like dead storage — not live museum |
| Form | **Form clear · 0 open PICKs** | "My picks were wiped" (prior debug logs had 9–11 open — picks were **applied**, not deleted) |
| Worker | sa-0529 idle | Factory surface — not founder museum |
| URL | `127.0.0.1:13020/` **root** | Expectation: full monolith |

---

## 4. Root causes

| # | Root cause | Evidence |
|---|------------|----------|
| R1 | **Default home hijacked** | `/` serves H1 Worker Hub per Super Fast Hub law — monolith no longer default |
| R2 | **Museum link demoted** | Only small "Legacy archive" text — no **Founder Museum · read-only · all tabs** hero |
| R3 | **Agent wording = erasure** | Brain/Worker said "archived" / "old hub" without `http://127.0.0.1:13020/legacy/` every time |
| R4 | **`/oldhubsinacommand/` not shipped** | ASF order + **AR-b9955efbce** — maintainer backlog; founder still lacks named museum URL |
| R5 | **Form slice misread** | H1 shows `open_questions_count: 0` because **second form picks were applied** (`open_remaining_count: 0`) — looks like empty museum |
| R6 | **No READ ONLY banner on legacy** | `/legacy/` serves monolith but does not scream **"your museum — frozen reference"** |
| R7 | **Two-hub law not founder-translated** | Agents cited law; founder got worker UI at bookmark they used for 9MB monolith |

---

## 5. Timeline

| When | Founder / disk | Agent / system did | Wrong? |
|------|----------------|-------------------|--------|
| 2026-06-11–13 | Form v2 filled · 52 picks applied | Archives + `~/.sina/live-founder-decision-form-*` saved | **OK** |
| 2026-06-13 | ASF hub-worker-only pick | H1 ship · monolith frozen to `/legacy/` | **Intent OK · UX FAIL** |
| 2026-06-14 | Founder opens `/` | Sees Worker Hub not museum | **Perceived erasure** |
| 2026-06-14 | Founder: *erase founder museum* | Prior agent said "archived" without URL | **VIOLATION** |
| 2026-06-14 | `command-data.json` 10.7MB · `/legacy/` 200 | Incident filed · museum link remediation queued | **This incident** |

---

## 6. Impact

- Founder trust: believes **months of hub subjects, tabs, and picks** were deleted.
- Wrong remediation path: founder may re-enter data or bypass SSOT if they think disk is empty.
- Brain credibility: "archived" without receipt reads as **agent destroyed founder property**.
- H1 law undermined: daily hub must **never lie** — showing empty form while museum is elsewhere **feels like lying**.

---

## 7. Law (never again)

1. **Never say erased, archived, moved, or replaced** without **URL + disk path + byte size or receipt** in the same sentence.
2. **Default `/` change** requires **founder-visible museum link** above the fold — label **Founder Museum (read-only)** not "Legacy archive" alone.
3. **H1 form slice** must subtitle: *"Open picks here only — full form history in Museum → Form tab"* when `open_questions_count === 0` but disk has applied history.
4. **Three URLs every hub answer:** H1 daily `http://127.0.0.1:13020/` · H2 `http://127.0.0.1:13020/machines/` · Museum `http://127.0.0.1:13020/legacy/` (until `/oldhubsinacommand/` ships).
5. **Maintainer gate:** `validate-super-fast-hub-v1.sh` must fail if museum link missing or unlabeled.

---

## 8. Remediation

### 8.1 Immediate (this incident — read-only)

| Item | Action | Owner |
|------|--------|-------|
| LOCKED body | This file | Worker/Brain |
| Registry row | INCIDENT-032 | Worker/Brain |
| Root pointer | `SINA_FOUNDER_MUSEUM_HUB_ERASURE_PERCEPTION_INCIDENT_032_REPORT_LOCKED_v1.md` | Worker/Brain |
| Disk proof | `command-data.json` size + `/legacy/` 200 + form JSON paths in §1 | Worker/Brain |
| Agent-review | Confirm **AR-b9955efbce** open — `/oldhubsinacommand/` + READ ONLY banner | Maintainer |

### 8.2 Maintainer ship (SinaaiDataBase — hub code)

| Item | Action |
|------|--------|
| Route | `GET /oldhubsinacommand/` → same monolith as `/legacy/` |
| Banner | **READ ONLY — Founder Museum — do not edit here** on museum surfaces |
| H1 hero | Prominent button: **Open Founder Museum (read-only)** → `/oldhubsinacommand/` |
| Rename link | Replace or augment "Legacy archive" with **Founder Museum** |
| Validator | Extend `validate-super-fast-hub-v1.sh` — museum link + label |

### 8.3 Brain / Worker behavior

| Item | Action |
|------|--------|
| Reply template | "Data not erased — museum at `/legacy/` (10.7MB command-data)" |
| Stop | Implying H1 screenshot **is** the archive version |
| Latch | Reuse archive near-miss — no "archived" without URL |

---

## 9. Verification

```bash
# Museum still logged
wc -c ~/Desktop/SourceA/agent-control-panel/command-data.json
curl -sf -o /dev/null -w "%{http_code}\n" http://127.0.0.1:13020/legacy/

# Form history (not erased — may show 0 open)
python3 ~/Desktop/SourceA/scripts/live_founder_decision_form_v1.py --json | python3 -c "
import sys,json;d=json.load(sys.stdin)
print('second_form', d.get('second_form'))
print('v2_filled', d.get('v2_answers',{}).get('filled'))
"

# H1 must expose museum link (after maintainer ship)
bash ~/Desktop/SourceA/scripts/validate-super-fast-hub-v1.sh
```

**Founder museum today:** `http://127.0.0.1:13020/legacy/` — full monolith · **not deleted**.

---

## 10. Status

**OPEN** — perception incident filed 2026-06-14 · data intact · **remediation = museum link + wording + maintainer route** · closes when AR-b9955efbce ships + validator green + founder confirms museum reachable from H1.

**END INCIDENT-032**
