# REGISTRY batch fake progress — incident report (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**LOCKED body:** `brain-os/incidents/SINA_REGISTRY_BATCH_FAKE_PROGRESS_INCIDENT_LOCKED_v1.md`  
**sequence_id:** SA-2026-06-09-INCIDENT-006  
**MANDATORY READ:** Brain · Worker · Maintainer · all Cursor agents  

**Summary:** On 2026-06-08, `cursor-worker-batch` stamped **~607 REGISTRY rows `done`** with YAML only (~11 honest receipts). Monitor showed 61% complete; real progress was ~1%. **Reverted + receipt gate shipped.** Current: **23 honest / 1000 · 0 unproven**.

**Never forget:** `done` = `receipts/sa-XXXX-receipt.json` only. Founder workflow = Worker → **`run inbox`** manual. No batch stamp. No YAML-only proof.

Read the full incident at the path above before reporting progress, enabling autorun, or calling any `sa` complete.
