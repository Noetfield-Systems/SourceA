# INCIDENT-033 report — Brain stale · command-data SSOT · false cart PASS

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**LOCKED body:** `brain-os/incidents/SINA_BRAIN_STALE_COMMAND_DATA_GOVERNANCE_FAILURE_INCIDENT_033_LOCKED_v1.md`

**What happened:** Executor told founder E2E/cart **PASS** and H2 pending **fixed** while **factory queue was empty**, **queue_ssot_unify FAIL**, **Brain current-action stale**, and agents still ingested **`command-data.json`** (Sina Command monolith projection). Founder museum **not erased logged** but **still hidden** (INCIDENT-032 open).

**Founder museum today:** http://127.0.0.1:13020/legacy/ · `command-data.json` ~10.7MB intact.

**Do not RUN INBOX until:** `healthy-queue-30-active.json` has items · `queue_ssot_unify` ok.

**Tips file:** see INCIDENT-033 §8 (10 rules).
