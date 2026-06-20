# Goal 1 auto-run broker STALE receipts — incident report (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**LOCKED body:** `brain-os/incidents/SINA_GOAL1_AUTORUN_BROKER_STALE_RECEIPT_INCIDENT_LOCKED_v1.md`  
**sequence_id:** SA-2026-06-09-INCIDENT-007  
**MANDATORY READ:** Brain · Worker · Maintainer · all Cursor agents  

**Summary:** Auto-run closed sa-0004..0008 while agents claimed success. **77 receipts · 67 STALE broker.** VERIFY turns had **`sa_mismatch`** masked by **`receipt_on_disk`**. ACT skipped. **Only 1 line built** (sa-0006 L29). Rest = verify-only closeout on prior disk.

**Never forget:** Report **RECIPE + VALIDATION + EVIDENCE + BUILT** every closeout. Receipt ≠ proof when broker is STALE.

Read the full incident at the path above before reporting progress, enabling autorun, or calling any `sa` complete.
