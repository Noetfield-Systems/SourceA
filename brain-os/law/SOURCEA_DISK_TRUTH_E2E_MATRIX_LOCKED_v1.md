# SourceA — Disk truth E2E matrix (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority ID:** `DISK_TRUTH_E2E`  
**Version:** 1.0  
**Date:** 2026-06-10  
**Parent:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` §3 Execution truth  
**Supersedes:** `archive/attachments/2026-06-10/SOURCEA_CONVERSATION_FULL_INSIGHT_S10_SSOT_V2_LOCKED_v1.md` §3 (archive = pointer only)

---

## Law (2026 agentic factory)

1. **Control plane** (factory_control, spawn gate, FREEZE, run-inbox truth) and **projection plane** (hub command-data, P0 hero, live_pick text) are **both** subject to validators.
2. If projection ≠ control, the system must **FAIL loud** — not PASS quiet (`validate-ecosystem-safety-v1.sh` dual-pick gate).
3. **RT** = real-time with disk · **LAG** = stale/cache/build snapshot (document TTL) · **GAP** = known wrong (must FAIL or flag until healed).

**Machine mirrors:**

| Artifact | Path |
|----------|------|
| Run inbox truth | `~/.sina/run-inbox-disk-truth-v1.json` |
| Factory now | `~/.sina/factory-now-v1.json` |
| Hub panel | `agent-control-panel/command-data.json` |
| S10 receipt | `~/.sina/s10-eternal-receipt-v1.json` |
| Dual-pick gate | `scripts/_ecosystem_safety_dual_pick_check_v1.py` |

---

## Full E2E table (25 rows)

| # | Layer | Disk SSOT (truth) | UI / chat reads | Sync | Status | S10 | Heal |
|---|-------|-------------------|-----------------|------|--------|-----|------|
| 1 | Honest progress | `receipts/sa-*-receipt.json` + REGISTRY | monitor · factory-now · hub cards | On closeout + brain_sync | **RT** (±1 receipt lag OK) | P1·P5 | brain_sync |
| 2 | Valid YES count | `monitor_honesty_lib` audit | monitor.html · command-data | `monitor_live_sync` ~5s | **RT** | P1 | sync_disk |
| 3 | Brain column | `brain-goal1-validation-v1.json` | Brain chat · hub brain card | `brain_sync_lib` on honest change | **RT** after 014 fix | P2·P5 | brain_sync |
| 4 | Queue cursor | `healthy-queue-state-v1.json` | run-inbox-truth · INBOX meta | On advance / deliver | **RT** | P1·P3 | bind heal |
| 5 | Run inbox truth | `run-inbox-disk-truth-v1.json` | INBOX DISK TRUTH block | `run_inbox_disk_truth_v1` | **RT** | P1·P3 | ensure_inbox_truth |
| 6 | Inbox pending SA | `worker-prompt-inbox-v1.json` | Worker session | Broker deliver | **RT** (bind OK today) | P1 | patch block |
| 7 | Factory now line | `factory-now-v1.json` (5s cache) | cursor_entry_gate · chat | rebuild on stop/sync | **LAG** (TTL by design) | P2 | rebuild |
| 8 | FREEZE / kill flag | `auto-run-disabled-v1.flag` + stop receipt | Hub START button · next_action text | Partial | **GAP** if START visible under FREEZE | P2·P6 | panel lane |
| 9 | Spawn gate | `factory_control_v1` in-process + flag | Hub autorun · Shell | At spawn entry | **RT** (machine) | P2·P10 | N/A |
| 10 | Hub command-data | `command-data.json` `built_at` | Sina Command panel | Panel build / poll | **LAG** (minutes) | P6 | build panel |
| 11 | Hub shell preload | `command-data-shell.json` | First paint | Build time snapshot | **LAG** | P6 | rebuild |
| 12 | P0 next_action string | Built from goal1 + live_pick | Founder hero line | Panel build | **GAP** if dual pick text | P6 | panel lane |
| 13 | live_pick vs queue | Queue = execution SA; live_pick = REGISTRY phase-first | goal1 tab · next_action | Must align or FAIL gate | **GAP** until aligned | P6 | panel + gate |
| 14 | START AUTO RUN CTA | Should hide when FREEZE | Visible in next_action | Wire to factory-now | **GAP** if visible under FREEZE | P6 | panel lane |
| 15 | Monitor live pulse | `monitor-live-v1.json` | monitor.html iframe | 5s sync thread | **RT** | P1·P10 | sync_disk |
| 16 | Broker cycle | `goal1-lane-broker-events.jsonl` | batch log · brain validate | Per submit | **RT** at closeout | P3·P5 | hygiene |
| 17 | Pack receipts | `pack-drain-receipts/pack-*.json` | Worker audit | Per pack turn | **RT** when drain runs | P8 | N/A |
| 18 | Phase-strict queue | `phase-strict-drain-v1.json` + manifests | run-inbox-truth | Builder script | **RT** | P8 | build-phase-strict |
| 19 | S10 receipt | `s10-eternal-receipt-v1.json` | Hub Advisor track · monitor | Daily 06:00 + monitor | **RT** on disk | P10 | launchd |
| 20 | Prompt feed batch | OpenRouter propose | Prompt feed UI | Advisory curl | **Not execution** | — | — |
| 21 | TrustField tracker | `TrustField…/plan.json` | Portfolio thread | Separate repo | **Separate lane** | P7 | agent lane |
| 22 | Cursor plan todos | IDE state | Cursor runtime | None | **GAP** — survives STOP | P7·P9 | manual cancel |
| 23 | Chat memory | None (forbidden) | Agent replies | None | **GAP** if used | P9 | factory-now law |
| 24 | dual_proof | monitor + brain receipt | validators | ecosystem safety | **RT** (595/595) | P2·P5 | — |
| 25 | Governance events | `agent-governance-events.jsonl` | Maintainer | S10 + incidents | **RT** | P7 | append |

---

## Summary

**Execution path** (rows 1–6, 9, 15–18) is **mostly RT**.  
**Hub hero UX** (rows 8, 10–14) is where founder *feels* stuck — panel snapshot ≠ factory-now until projection lane ships.

**Validators:**

```bash
bash scripts/validate-ecosystem-safety-v1.sh      # includes dual-pick FAIL
bash scripts/validate-mandatory-read-paths-v1.sh  # agent navigation front door
python3 scripts/_ecosystem_safety_dual_pick_check_v1.py --json
```

---

*End DISK_TRUTH_E2E_MATRIX v1*
