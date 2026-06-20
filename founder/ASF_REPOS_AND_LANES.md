# Five repos + lanes — ASF reference

## Repo IDs (ingest + paste files)

| ID | Folder |
|----|--------|
| `trustfield` | `~/Desktop/TrustField Technologies` |
| `sinaai_mono` | `~/Desktop/SinaaiMonoRepo` |
| `virlux` | `~/Desktop/VIRLUX` |
| `noetfield` | `~/Desktop/Noetfield` (chat may use Noetfield-All-Documents) |
| `seven77` | `~/Desktop/The 777 Foundation` |

Paste file: `SinaPromptOS/outputs/ready_to_paste/ready_to_paste_<id>.txt`

---

## Priority order

Read: `SourceA/GLOBAL_PRIORITY.json` (architect / full cycle refreshes).

---

## Blockers (parallel — not wire gates)

| Repo | Typical blocker |
|------|-----------------|
| TrustField | Render / Cloudflare / postgres |
| Mono | Phase 0 exit sign-off (ASF) |
| VIRLUX | Staging deploy |
| 777 | Supabase SERVICE_ROLE |
| Noetfield | Spec sections |

Wire can proceed while these exist.

---

## Mono quick

- Spine: `:8000` only
- Approval: `@SinaaiOSbot` `/brief` → `/approve`
- Verify: `SinaaiMonoRepo/scripts/verify-approval-gate.sh`

---

## Progress checklist

`SourceA/WIRE_LANE_PROGRESS.md`
