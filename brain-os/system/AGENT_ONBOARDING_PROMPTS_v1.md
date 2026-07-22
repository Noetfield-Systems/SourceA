# AGENT ONBOARDING PROMPTS
## New Governance Docs — Copy-Paste Ready

**Purpose:** Onboard all agents to two new LOCKED governance documents:
1. `brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md`
2. `brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md`

**Date:** 2026-06-08  
**Issued by:** ASF

---

# STEP-BY-STEP INSTRUCTIONS FOR ASF

## Step 1 — Brain first (do this before all others)

Brain must wire both docs into `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b` so
all future sessions pick them up automatically. Without this step, the other
agents will read the docs once but forget them next session.

Open your Brain chat → paste Prompt A below → wait for DONE.

## Step 2 — Governance Specialist

Open Governance Specialist chat → paste Prompt B → wait for ACK.

## Step 3 — Worker (SourceA Worker 1)

Open Worker chat → paste Prompt C → wait for ACK.

## Step 4 — Commercial Specialist

Open Commercial Specialist chat → paste Prompt D → wait for ACK.

## Step 5 — Old Brain / SinaaiDataBase

Open Old Brain chat → paste Prompt E → wait for ACK.

## Step 6 — Verify

In Brain chat → paste Prompt F (verification check) → confirm PASS.

---
---

# PROMPT A — BRAIN (SourceA Execution Core)

```
ASF DIRECTIVE — MANDATORY GOVERNANCE UPDATE

Read these two new LOCKED governance documents immediately:

1. brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
2. brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md

After reading both, do the following in order:

1. Update SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b to add both documents 
   to the mandatory read list. Every agent session must be directed to 
   read them at startup. Wire them exactly as the other LOCKED docs are 
   wired — with path, purpose, and read-before-execute instruction.

2. Confirm the Master Tracker Section 1 (Executive Snapshot) reflects 
   current system state.

3. Confirm FILE_STORAGE_GOVERNANCE_LOCKED_v1.md is consistent with 
   current brain-os/ directory structure and ~/.sina/ paths on disk.

4. If any current file is stored in the wrong tier per the new 
   FILE_STORAGE_GOVERNANCE law, log it as MISS-XXX in the Master 
   Tracker Section 5 (Missing Registry) with severity P1.

Reply with:
- DONE
- Confirmation that §0b is updated with both doc pointers
- Any MISS entries logged
- validate-master-operating-tracker-v1.sh result
```

---

# PROMPT B — GOVERNANCE SPECIALIST

```
ASF DIRECTIVE — MANDATORY GOVERNANCE READ

Read these two new LOCKED governance documents immediately:

1. brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
2. brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md

After reading both:

1. Verify the governance law in FILE_STORAGE_GOVERNANCE_LOCKED_v1.md 
   is consistent with all existing LOCKED governance docs on disk.
   Flag any conflicts.

2. Verify the Master Tracker's enforcement model (Section 0 and 
   Validation section) is consistent with GOVERNANCE_P1_LOOPS_LOCKED_v1.md 
   and EXECUTION_AUTHORITY_MAP_LOCKED_v1.md.

3. Register this read as a governance trace in RESEARCH with 
   execution_authority: false.

4. If no conflicts found, reply with: GOVERNANCE ACK — no conflicts.
   If conflicts found, list them precisely.

Do NOT modify any LOCKED doc. Advise only.
Your execution_authority is false.
```

---

# PROMPT C — WORKER (SourceA Worker 1)

```
ASF DIRECTIVE — MANDATORY SESSION READ

Before any build work this session, read:

1. brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
2. brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md

After reading:

1. Confirm the current execution pointer matches your INBOX 
   (check ~/.sina/next-execution-pointer-v1.json).

2. Confirm you understand the two-tier storage model:
   - Governance docs → brain-os/system/ (Tier 1)
   - Runtime state → ~/.sina/ (Tier 2)
   - You may NOT save runtime state to brain-os/
   - You may NOT save governance docs to ~/.sina/

3. For any file you create this session, confirm it is saved 
   to the correct tier per FILE_STORAGE_GOVERNANCE_LOCKED_v1.md 
   Section 1 before the session closes.

Reply with: WORKER ACK — pointer confirmed — tiers understood.
Then wait for your INBOX task.
```

---

# PROMPT D — COMMERCIAL SPECIALIST

```
ASF DIRECTIVE — MANDATORY READ

Read these two documents before any commercial analysis this session:

1. brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
   — focus on Section 1 (Executive Snapshot) and Section 2 (Goal Registry)
   to understand current system priorities before advising.

2. brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md
   — Section 3 (Tier 3) is most relevant: any commercial research or 
   recommendations must be saved to RESEARCH/by_date/ in Tier 1 with 
   a _META.yaml containing execution_authority: false.

After reading:

1. Confirm current founder objective (Section 1 of tracker) is 
   understood before providing any commercial input.

2. Any commercial recommendation this session must include a 
   RESEARCH save path and trace ID.

Reply with: COMMERCIAL ACK — tracker read — storage rules understood.
```

---

# PROMPT E — OLD BRAIN / SINAAIDATABASE

```
ASF DIRECTIVE — MANDATORY READ AND REGISTER

Read these two new LOCKED governance documents:

1. brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
2. brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md

After reading:

1. Note that your role is explicitly defined in FILE_STORAGE_GOVERNANCE_LOCKED_v1.md 
   Section 8: read-only access to Tier 1, no Tier 2 access, 
   execution_authority: false.

2. When you search or compare against disk, cite the canonical 
   Tier 1 path of every document you reference.

3. When you output a finding, end with:
   "Disk path: [path] | execution_authority: false | Tier: 1"

4. If asked where a document should be saved, answer using the 
   two-tier model from FILE_STORAGE_GOVERNANCE_LOCKED_v1.md — 
   not from memory or prior convention.

Reply with: OLD BRAIN ACK — storage governance read — Tier 1 read-only confirmed.
```

---

# PROMPT F — BRAIN VERIFICATION CHECK (send after all others)

```
ASF VERIFICATION ORDER

Run the following checks and report results:

1. scripts/validate-master-operating-tracker-v1.sh — report PASS or FAIL
2. scripts/validate-file-storage-v1.sh — report PASS or FAIL
3. Confirm SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b now includes 
   pointers to both new docs
4. Confirm no agent in WORKERS_REGISTRY.yaml has execution_authority: true 
   except SourceA Brain (Execution Core)
5. Confirm ~/.sina/next-execution-pointer-v1.json is current and 
   consistent with Master Tracker Section 1

Expected reply format:
validate-master-operating-tracker: PASS / FAIL
validate-file-storage: PASS / FAIL
§0b updated: YES / NO
Authority registry clean: YES / NO
Pointer consistent: YES / NO

If any FAIL: state the exact condition that failed and the fix.
Do not proceed to AUTO-RUN until all five are YES/PASS.
```

---

# QUICK REFERENCE — ORDER OF OPERATIONS

```
ASF opens Brain chat
  → Paste Prompt A
  → Wait for DONE + §0b confirmation
  ↓
ASF opens Governance Specialist chat
  → Paste Prompt B
  → Wait for ACK
  ↓
ASF opens Worker chat
  → Paste Prompt C
  → Wait for ACK
  ↓
ASF opens Commercial Specialist chat
  → Paste Prompt D
  → Wait for ACK
  ↓
ASF opens Old Brain chat
  → Paste Prompt E
  → Wait for ACK
  ↓
ASF returns to Brain chat
  → Paste Prompt F
  → All five checks = YES/PASS
  → System is onboarded
  ↓
ASF taps Hub → AUTO-RUN (Rail A)
```

---

# WHAT HAPPENS AFTER THIS

Once all five agents have ACK'd and Prompt F returns all YES/PASS:

- Both governance docs are wired into the entry point permanently
- Every future session will read them at startup automatically
- No manual re-paste required
- The broker gate enforces freshness from this point forward

**You only need to run these prompts once.**  
After Brain updates §0b, the docs become part of the permanent session-start governance chain.
