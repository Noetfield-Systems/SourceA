# SourceA — Brain Operational Runbook

Purpose
-------
One-page runbook for Brain sessions to keep the autorun motor healthy, capture mandatory receipts, perform minimal health checks, and hand off Worker tasks safely. This document is readonly guidance — do not run heavy validators during a founder session.

Quick-start (one-liners)
------------------------
- Start session receipt (always):  
  `python3 scripts/agent_session_gate_run_v1.py --role brain --json`
- Show last Brain session receipt:  
  `jq '.' ~/.sina/brain_session_receipt_v1.json`
- Show last Worker inbox (if needed):  
  `jq '.' ~/.sina/worker-prompt-inbox-v1.json`

Mandatory receipts & pre-conditions
-----------------------------------
- Always read the Brain session receipt before action: `~/.sina/brain_session_receipt_v1.json`  
- Follow Entry Gate rules: see `.cursor/rules/000-entry-gate.mdc` and `data/cursor-bootstrap-ledger-v1.json`. Key requirements:
  - Do not re-run `brain-session-start.sh` mid-turn. Read the session receipt instead.
  - For cross-lane or rule edits, run the filing registry / pre-write guard first.

Mac launchd autorun (DISABLED)
------------------------------
**Status (2026-07-05):** `com.sourcea.autorun-worker` is **DISABLED** on Mac founder sessions.

- Law: `.cursor/rules/mac-control-plane.mdc` — factory mode **FREEZE**; do not bootstrap autorun-worker without ASF.
- Prior failure: launchd pointed at wrong path `~/Desktop/SourceA` (ENOENT) — job not loaded now.
- Action if re-enable needed: fix plist to `~/Desktop/Noetfield-Systems/SourceA` **only** with explicit ASF order.

Emergency stop / safe abort
---------------------------
- If a validator or long-running check starts accidentally: stop immediately and capture the receipt file(s). One-line report to founder and stop.  
- Example abort steps (founder session): capture receipts, then stop any spawned validators; do NOT attempt a full rebuild or full E2E run.

Minimal health checks (read-only examples)
----------------------------------------
Goal: surface three signals quickly without heavy work.

1) Autorun tick (recent dispatch)
  - Example: read autorun receipts or last-run timestamp (receipt pattern varies by infra). Quick check:  
    `ls -lt ~/.sina | rg autorun || echo "no autorun receipt found"`  
  - Recommended: `python3 scripts/agent_session_gate_run_v1.py --role brain --json` (captures session proof)

2) Worker heartbeat / last successful run
  - Quick-check: `jq '.last_tick // empty' ~/.sina/autorun_receipt_v1.json 2>/dev/null || echo "no autorun_receipt"`  
  - If Worker inbox is used: `jq '.' ~/.sina/worker-prompt-inbox-v1.json`

3) Last error age
  - Inspect recent receipts/log lines for errors and timestamps; if last-error > 10 minutes escalate. Example (plan-only):  
    `rg -n "ERROR|Exception" receipts/ -S --sort=time | head -n 5`

Monitoring & alarms (who to notify)
-----------------------------------
- Primary notify: founder (direct) + Worker channel (where Worker listens). Configure thresholds in runbook:  
  - Missing autorun tick > 5m → notify Worker + founder  
  - Last error age > 10m or repeated failures → escalate to maintainer

Founder session checklist (5 one-line steps)
--------------------------------------------
1. Run: `python3 scripts/agent_session_gate_run_v1.py --role brain --json` and read the receipt.  
2. Run minimal health checks above (read-only). Do not run validators.  
3. If change required, prepare Worker handoff (see next).  
4. Capture receipts & paste the minimal evidence line. End session.  
5. If emergency, run the Emergency stop procedure and notify maintainer.

Worker handoff procedure (safe, registry-first)
-----------------------------------------------
1. Resolve target path with filing registry (do NOT guess):  
   `python3 scripts/agent_filing_registry_gate_v1.py resolve --agent <id> --intent "<one-line intent>" --json`  
   - Use returned `route_id` and `path`. If `ok:false`, ask ASF for scope/category.  
2. Prepare a single atomic change (one lane). Keep changes ≤ 20–40 files.  
3. Run pre-write guard when editing rules/governance:  
   `python3 scripts/pre_write_guard_v1.py post-write --agent cursor --path "<path>" --json`  
4. Provide Worker with: route_id, path, short test steps, and required receipts to attach.  
5. Commit guidance: one atomic commit per lane; do not amend pushed commits; do not force-push.

Review & confirm
-----------------
This runbook is a short, actionable guide for Brain sessions. Before any automated edits or heavy checks, the Brain must present this plan and the session receipts to the founder for approval.

Notes / Constraints
-------------------
- Respect Mac control-plane rules: no heavy local validators in founder session. See `.cursor/rules/mac-control-plane.mdc`.  
- This file is docs-only; creation is allowed under Entry Gate (SAVE = one file in docs).

Locations referenced
--------------------
- Entry gate rule: `.cursor/rules/000-entry-gate.mdc`  
- Ledger: `data/cursor-bootstrap-ledger-v1.json`  
- Session receipt: `~/.sina/brain_session_receipt_v1.json`  
- Filing registry: `scripts/agent_filing_registry_gate_v1.py`  

Mac Health Guard (:13024)
-------------------------
- **Open heart:** `bash scripts/serve-mac-health-guard.sh` then `open http://127.0.0.1:13024/`  
- **Path SSOT:** `scripts/resolve_sourcea_root_v1.sh` — never boot from stale `~/Desktop/SourceA` alone  
- **Founder session proof:** `bash scripts/validate-mac-health-ship-fast-v1.sh` (not full e2e on Mac)  
- **W2 plan pulse:** `python3 scripts/ecosystem_mac_health_111_plan_pulse_v1.py --json`

