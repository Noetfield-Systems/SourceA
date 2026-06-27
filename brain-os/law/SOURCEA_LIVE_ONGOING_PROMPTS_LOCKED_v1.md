# Live ongoing prompts — machine order + Next steps mirror (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**2026-06-10** · ASF order · **renamed 2026-06-14:** founder daily surface = **Next steps** (not “Prompt feed”)  
**sequence_id:** SA-2026-06-10-LIVE-ONGOING-PROMPTS  
**Supersedes:** static OpenRouter 10-pack as execution or display SSOT

---

## 0. One sentence

**The machine owns order, validation, and delivery; Super Fast Hub Next steps shows the live next 10 queue turns from disk — founder confirm/edit/quarantine/delete is optional and never blocks delivery.**

---

## 1. Two lanes

| Lane | SSOT | Blocks delivery? |
|------|------|------------------|
| **Machine execution** | `run inbox` · healthy queue · INBOX | **Yes** — `validate-next-prompt-pack-live` FAIL only |
| **Founder display (Next steps)** | **Super Fast Hub** `http://127.0.0.1:13020/` · queue line + daily rooms | **No** — &lt;1s poll · not legacy monolith |
| **Legacy queue tab** | `/legacy/?tab=prompt-feed` | **Archive only** — never daily ops (INCIDENT-028) |

OpenRouter `prompt-direction` = **optional AI commentary** — not the list source.

---

## 2. Live next-10 SSOT

**File:** `~/.sina/live-ongoing-prompts-next-10-v1.json`  
**Schema:** `live-ongoing-prompts-next-10-v1`

| Field | Rule |
|-------|------|
| `cursor_pos` | `healthy-queue-state-v1.json` `next_pos` |
| `turns` | **10 consecutive queue rows** `cursor_pos` .. `cursor_pos+9` (CHECK/ACT/VERIFY slots — **not** deduped by sa_id) |
| `built_at` | ISO UTC — must refresh within 10s of cursor move |
| `validator_receipt` | Embedded from `live-pack-validator-receipt-v1.json` |

**Builder:** `python3 scripts/live_ongoing_prompts_v1.py --rebuild`  
**Validator:** `bash scripts/validate-live-ongoing-prompts-v1.sh`

---

## 3. Rebuild triggers (never stale)

1. `monitor_live_sync_v1.py` — 5s disk wire on queue/state change  
2. `advance-healthy-queue-v1.py` — after cursor advance  
3. `healthy-drain-orchestrator-v1.py` — pre-deliver  
4. `run_inbox_disk_truth_v1.py` — `write_truth`  
5. Hub command-data build — `sina_command_lib` embeds payload  

When cursor moves **106 → 107**, `turns[0].queue_pos` must become **107** in the repository before next hub poll.

---

## 4. Founder optional controls

**File:** `~/.sina/live-prompt-overrides-v1.json`  
**API:** `POST /api/live-prompt-overrides` (hub)

| Action | Effect |
|--------|--------|
| **Edit** | Override `instruction` for a `queue_pos` at rebuild |
| **Quarantine** | Skip turn at deliver — orchestrator logs skip receipt |
| **Delete** | Hide from slice + mark `excluded` in overrides |
| **Confirm** | Stamp `founder_confirmed_at` — **cosmetic only** |

Founder validation is **never** a delivery gate.

---

## 5. Execution gate

**Only gate:** `python3 scripts/validate-next-prompt-pack-live-v1.py --strict`  
Receipt: `~/.sina/live-pack-validator-receipt-v1.json`  
On FAIL: `~/.sina/live-pack-blocked-v1.json` — no INBOX inject.

FREEZE (`kill_flag` ON): auto-deliver **CHECK** turns only until ASF `Cloud Forge Run PHASE_STRICT`.

---

## 6. Related laws

- `RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` — execution SSOT (updated: feed = live mirror)  
- `SINA_CURSOR_PROMPT_QUEUE_ORDER_v1.md` — confirm optional  
- `SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md` — dual-pick · projection rows  

---

## 7. Incident

`brain-os/incidents/SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_022_*` — subject `PROMPT_FEED_LIVE`
