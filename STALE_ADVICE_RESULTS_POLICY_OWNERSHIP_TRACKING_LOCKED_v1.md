# Stale advice — results policy · ownership · tracking (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Authority:** ASF order — everything clarified · who owns · who tracks  
**Parent law:** `AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`  
**Incident:** INCIDENT-028 · INCIDENT-034  
**Executor CART:** `archive/attachments/2026-06-14/BRAIN_DISK_LIVE_WIRE_EXECUTOR_MANDATORY_CART_LOCKED_v1.md`  
**Investigation:** `archive/attachments/2026-06-14/OLD_INJECT_HUNT_CHAT_TIMELINE_PIPELINE_MAP_LOCKED_v1.md`

---

## 1. Policy (one paragraph)

**Result we enforce:** Every Brain · Worker · Governance agent session reads **live disk** and tells the founder only the **canonical close-line** — never “Prompt feed → Confirm auto-send” unless disk explicitly says so (it must not).

**How we enforce:** Machine validators **PASS** · live context JSON files **clean** · inject chain **named owner per surface** · Governance **tracks receipts** · ASF **closes incidents** when proof is in the repository — not when an agent “promises” in chat.

**What we do not do:** Prohibition tables · blame Brain/Worker for reading inject · “fresh chat” as fix · separate executor team fiction.

---

## 2. Roles — who owns · who tracks · who approves

| Role | Who | **Owns (R)** | **Tracks (A)** | **Approves close (C)** |
|------|-----|--------------|----------------|------------------------|
| **ASF** | Founder | Product truth · final vocabulary · incident close | Visual confirm H1/H2 when needed | **Yes** — INCIDENT-034 · INCIDENT-028 |
| **Cursor agent (SourceA)** | This workspace executor | Run C-00–C-16 · fix disk/scripts/rules · log events | Self — validators before every ship | No |
| **Governance Specialist** | Governance chat `e54ddfa8` | Meta-audit · cart checklist · backlog hygiene | **Primary tracker** — CART receipts · 3-session green streak | Recommends close to ASF |
| **Brain chat** | Brain workspace `58148ac9` | Consume `brain-live-context-v1.json` when clean | None — **never blamed** for drift | No |
| **Worker chat** | Worker workspace `fd67502f` | RUN INBOX when disk clean | None — **never blamed** for drift | No |
| **Maintainer 2** | SinaaiDataBase hub workspace | Hub UI/API only (AR-034-01 · AR-034-02) | Governance verifies ship | No |

**No other owner exists.** There is no “Brain executor team,” “Worker executor,” or third-party fixer for disk wire.

---

## 3. Results — definition of done (measurable)

| Result ID | Pass condition | Proof artifact | Who verifies |
|-----------|----------------|----------------|--------------|
| **R1** | Brain disk has zero Prompt-feed steer | `bash scripts/validate-brain-disk-no-prompt-feed-v1.sh` exit 0 | Cursor agent · Governance reads stdout |
| **R2** | Worker disk has zero Prompt-feed steer | `bash scripts/validate-worker-disk-no-prompt-feed-v1.sh` exit 0 | Same |
| **R3** | Unified live wire | `bash scripts/validate-disk-live-wire-v1.sh` exit 0 | Same |
| **R4** | Brain live context canonical | `~/.sina/brain-live-context-v1.json` — RUN INBOX · no Prompt feed · no Confirm auto-send | C-03 receipt |
| **R5** | Worker live context canonical | `~/.sina/worker-live-context-v1.json` — same | C-03 paired |
| **R6** | Session inject clean | `~/.sina/agent_session_gate_receipt_v1.json` — no Prompt feed in inject | C-06 |
| **R7** | Founder close-line clean | `founder_close_line_gate_v1.py --text "<draft>"` ok:true | C-13 every ship |
| **R8** | 12s disk stability | After hub restart — execution-lane stays `live_next10_mirror` | C-14 |
| **R9** | 3 consecutive sessions | Brain **and** Worker — R1–R3 green without re-poison | Governance tracker |
| **R10** | Hub API clean | `prompt-direction` does not embed command-data | AR-034-01 ship + Governance test |

**INCIDENT-034 closes when:** R1–R7 + R9 + R10 + AR-034-02 + **ASF confirms** close-line in live chat with disk proof — **not** “open fresh Brain chat.”

---

## 4. Inject surfaces — owner · tracker · result per surface

Each row is a **disk or API writer** that can poison all three chats. One owner fixes; Governance tracks.

| Surface | What it injects | **Owner (fix)** | **Tracker** | **Result (PASS)** |
|---------|-----------------|-----------------|-------------|-------------------|
| `.cursor/rules/prompt-queue.mdc` | Close-line · POST prompt-direction habit | **Cursor agent** | Governance | v8+ · no Confirm auto-send · `alwaysApply: false` |
| `.cursor/rules/agent-disk-live-wire-first.mdc` | Positive live wire | **Cursor agent** | Governance | `alwaysApply: true` · validator line 14 |
| `scripts/healthy_prompt_turn_v1.py` | INBOX prompt wall | **Cursor agent** | Governance | No Prompt feed LAW in output |
| `scripts/worker_inject_lib.py` | 099 rule · INBOX write | **Cursor agent** | Governance | Steer guard blocks stale |
| `scripts/goal1_lane_broker.py` | Broker cache prompts | **Cursor agent** | Governance | No full prompt in `inbox_after_ack` |
| `scripts/run_inbox_disk_truth_v1.py` | Truth JSON keys | **Cursor agent** | Governance | No `prompt_feed_lane` key |
| `~/.sina/execution-lane-v1.json` | Advisory mirror label | **Cursor agent** | Governance | `live_next10_mirror` not `prompt_feed_live_mirror` |
| `brain-os/cursor/rules/099-worker-inbox-active.mdc` | Embedded stale prompt | **Cursor agent** | Governance | Active sa only · scrubbed |
| `~/.sina/brain-live-context-v1.json` | Brain read-first block | **Cursor agent** | Governance | R4 |
| `~/.sina/worker-live-context-v1.json` | Worker read-first block | **Cursor agent** | Governance | R5 |
| `~/.sina/agent-memory-mirror-v1.json` | INJECT_LAW session receipt | **Cursor agent** | Governance | Positive-only · validator lines 29–54 |
| `~/.sina/brain/*.md` static packs | ASF_MINIMUM · daily rhythm | **Cursor agent** (AR-034-03) | Governance · `rg Prompt\ feed` | Zero founder-facing Prompt feed |
| `POST /api/prompt-direction` | set_context · propose echo | **Maintainer 2** (AR-034-01) | Governance meta-audit | No command-data embed |
| Hub `command-data*.json` | Museum vocabulary lag | **Maintainer 2** (projection) | Governance | Museum-only · not execution SSOT |
| Hub H1 hero / museum link | Visual steer | **Maintainer 2** (AR-034-02) | ASF visual | INCIDENT-032 fixed |
| `dashboard_server_v1.py` (runtime) | Background sync re-poison | **Cursor agent** (C-14) | Governance | Fresh PID · R8 |
| Agent chat transcripts | Self-authored echo | **Nobody owns retroactive chat** | Governance archaeology only | New turns pass R7 |

---

## 5. Tracking cadence — who runs what when

| When | Who runs | What | Tracker receives |
|------|----------|------|------------------|
| **Every Brain/Worker/Gov executor session start** | Cursor agent | C-00 → C-01 → C-03 → C-06 (fast path) | Governance on request · jsonl event |
| **Every substantive ship** | Cursor agent | C-13 close-line gate · C-10–C-12 validators | Governance checklist row |
| **After hub/dashboard restart** | Cursor agent | C-14 · 12s stability · re-run C-01 | Governance event |
| **Drift after validators once PASS** | Cursor agent | **C-16** — name root writer | Governance incident note |
| **Material heal** | Cursor agent | **C-15** → `~/.sina/agent-governance-events.jsonl` | Governance tail |
| **Weekly / INCIDENT close** | Governance Specialist | Meta-audit R1–R10 · AR backlog · 3-session streak | ASF close recommendation |
| **Hub UI/API change** | Maintainer 2 | AR-034-01 · AR-034-02 only | Governance verifies + ASF visual |

**Fast path command block (Cursor agent — ~45s):**

```bash
cd ~/Desktop/SourceA
python3 scripts/anti_staleness_auto_wire_v1.py --role brain --tier session --json
python3 scripts/brain_live_context_v1.py --json
python3 scripts/brain_stale_prompt_scrub_v1.py --json
python3 scripts/agent_session_gate_run_v1.py --role brain --json
bash scripts/validate-brain-disk-no-prompt-feed-v1.sh
bash scripts/validate-disk-live-wire-v1.sh
```

---

## 6. Open backlog — single table

| ID | Task | **Owner** | **Tracker** | **Done when** |
|----|------|-----------|-------------|---------------|
| C-00–C-16 | Executor CART | **Cursor agent** | **Governance** | Per-task verify in CART doc |
| AR-034-01 | Stop prompt-direction embedding command-data | **Maintainer 2** | **Governance** | R10 PASS |
| AR-034-02 | H1 museum hero (INCIDENT-032) | **Maintainer 2** | **ASF** visual | Founder sees `/legacy/` link |
| AR-034-03 | Archive/scrub stale `~/.sina/brain/*.md` | **Cursor agent** | **Governance** | `rg Prompt\ feed ~/.sina/brain/` clean |
| INCIDENT-034 | Prohibition → disk wire meta-failure | **Cursor agent** healed disk | **Governance** tracks | R1–R9 + ASF sign-off |
| INCIDENT-028 | Worker stale prompt-feed advice | Disk wire (done) | **Governance** | R2 + R9 Worker leg |

---

## 7. Canonical founder close-line (quote from disk only)

> Worker chat: **RUN INBOX** one sa/turn. Optional: Worker Hub http://127.0.0.1:13020/ → **Next steps**. Museum: http://127.0.0.1:13020/legacy/. Quote **factory_now_line** from truth bundle.

**Owner of text:** `agent-live-surfaces-v1.json` · `brain-live-context-v1.json` · `worker-live-context-v1.json` — written by **Cursor agent** via `disk_live_wire_sync_v1.py`.

---

## 8. Governance Specialist tracker sheet (copy each session)

```
Session date: ___________
Chat: Brain / Worker / Governance / SourceA executor
Cursor agent ran fast path: Y / N
R1 brain validator: PASS / FAIL
R2 worker validator: PASS / FAIL / N/A
R3 live wire: PASS / FAIL
R4 brain-live-context: PASS / FAIL
R6 session gate receipt: PASS / FAIL
R7 close-line gate on ship: PASS / FAIL / N/A
C-16 hunt needed: Y / N — root writer: ___________
AR-034-01: OPEN / SHIPPED
AR-034-02: OPEN / SHIPPED
AR-034-03: OPEN / DONE
Streak count (R9): ___ / 3
Recommend INCIDENT-034 close: Y / N
```

---

## 9. Retracted guidance (not policy)

| Statement | Status |
|-----------|--------|
| “Fresh Brain chat fixes drift” | **RETRACTED** |
| “Brain reads chat not disk” | **FALSE** — reads inject |
| “Separate executor will fix” | **FALSE** — Cursor agent only |
| “Never say Sina Command” prohibition stacks | **SUPERSEDED** by live wire positive map |

---

**END — single policy for ownership and tracking**
