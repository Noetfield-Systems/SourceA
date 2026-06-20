# CHECK note — G3 Tailscale proof recorded? (2026-06-11)

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · CHECK only · **no code diff**

## Question

Is **G3 Tailscale** proof recorded logged? Gap vs hub **WIRE-G3** ops card and `WIRE_LANE_PROGRESS.md`?

## Verdict

**G3 NOT recorded** — remains **`pending`** across all wire SSOTs. **Gap confirmed.**

---

## Disk proof (aligned)

| Source | Field | Value |
|--------|-------|-------|
| `WIRE_LANE_PROGRESS.md` §Open | G3 Tailscale checkbox | **[ ] open** |
| `AI Dev Bridge OS/config/locked_plan.json` | `wire_proof.g3_tailscale` | **`pending`** |
| `~/.sina/wire_g3_status_v1.json` | `g3_tailscale` | **`pending`** |
| `PROGRAM_PROGRESS.json` → `signals_auto.wire` | `g3_tailscale` | **`pending`** |
| Hub ops card **WIRE-G3** | `status` | **`pending`** |
| `TO-WIRE` task order | status · judgment | **open · missed** |
| WTM pending **P11** | Wire RunReceipt / verify:wire | **`done`** (machine gate — not G3 physical proof) |

### What *is* green (wire lane)

| Signal | Status |
|--------|--------|
| `wire_preflight` | **pass** (`wire_g3_status_v1.json`) |
| `full_m8_iphone` | **pass** (locked_plan + status json) |
| G1 / G2 desktop | **done** per `WIRE_LANE_PROGRESS.md` |
| `physical_iphone` | **fail** (locked_plan — separate from G3) |

### What G3 requires (law — not done)

From `WIRE_LANE_PROGRESS.md`:

```text
G3 Tailscale — lane=full_m8 on 100.x URL →
  npm run record:g3 -- --host ... --run-id ... --pass true
```

After Tailscale on Mac + iPhone: `npm run proof:g3` → real Run ID from phone → `record:g3`.

**No G3 evidence file** found under `AI Dev Bridge OS/scripts/evidence/` (unlike G1/G2 result JSONs).

---

## Hub WIRE-G3 ops card

| Field | Value |
|-------|-------|
| id | `WIRE-G3` |
| severity | medium |
| action | Run g3 proof + record in `WIRE_LANE_PROGRESS.md` |
| founder_actions | `founder-wire-preflight` · `founder-open-wire-progress` |

**Founder one-tap (Actions tab):**

1. **Wire preflight check** (`founder-wire-preflight`) — runs `npm run wire:preflight` in AI Dev Bridge OS  
   - Hint logged: *"Code gates only — G3 Tailscale still needs iPhone proof"*
2. **Open wire progress doc** — read checklist (optional)

**Preflight does NOT close G3** — it validates code gates only.

---

## Gap analysis

| Gap | Detail |
|-----|--------|
| **G1** | G3 proof never recorded — `pending` since 2026-06-06 status json |
| **G2** | P11 WTM `done` ≠ G3 physical proof — pendings crosswalk intentional lag |
| **G3** | `full_m8_iphone` pass but G3 still open — Tailscale 100.x session not logged |
| **G4** | `physical_iphone: fail` — may block confidence but G3 checklist is separate open item |
| **G5** | ASF todo `T-WIRE-1` still open: *Verify g3_tailscale + record if pending* |

---

## Founder path (no Terminal)

1. Open **Sina Command** → **Actions**
2. Tap **Wire preflight check** — confirms code gates (expected **pass**)
3. For G3 close: **iPhone session** per `founder/ASF_WIRE_AND_PHONE.md` — Tailscale on Mac + phone → production proof URL on `100.x` → maintainer records `record:g3` with real run-id (maintainer/ASF physical step — not hub shell for founder beyond preflight)

After G3 recorded: maintainer updates `locked_plan.json` + `wire_g3_status_v1.json` → hub refresh → WIRE-G3 card clears · `TO-WIRE` reconcile candidate.

---

## Law alignment

- Form v2 **Q-RT-LIVE YES** — factory/wire proof is **portfolio parallel**, not Maintainer P0
- **Do not fabricate G3 PASS** — `wire_g3_status_v1.json` law + `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` §8

## Verdict

**CHECK complete** — G3 Tailscale proof **not recorded**; preflight may pass; physical G3 remains founder+iPhone work. Document only.
