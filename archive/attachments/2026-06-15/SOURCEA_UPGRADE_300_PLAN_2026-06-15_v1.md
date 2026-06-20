# SourceA Upgrade — 300 Plans (organized v1)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15  
**Trace:** SOURCEA-UPGRADE-300-PLAN-20260615  
**Authority:** `SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md`  
**IDs:** UPGR-001 … UPGR-300 · 30 buckets × 10  
**Path:** `archive/attachments/2026-06-15/SOURCEA_UPGRADE_300_PLAN_2026-06-15_v1.md`

---

## Executive summary

Organized upgrade backlog from Mac Health stop honesty, landing/tunnel reliability, factory/hub truth, commercial W1–W3, Witness deploy, and machine test ladder law. **P0 first** — honest stop receipts, tab UX, tunnel protection, run-recipe, founder docs.

**Law:** Map each implemented UPGR to H2 `UP-*` registry row · validator before code · receipt before/after.

---

## Bucket index

| # | Bucket | IDs | P0 |
|---|--------|-----|-----|
| 1 | Mac Health — stop & honesty | UPGR-001–010 | 6 |
| 2 | Mac Health — UI & tabs | UPGR-011–020 | 7 |
| 3 | Mac Health — native & panic | UPGR-021–030 | 3 |
| 4 | Agent prevention | UPGR-031–040 | 3 |
| 5 | Process targeting | UPGR-041–050 | 3 |
| 6 | Tunnel & deploy | UPGR-051–060 | 3 |
| 7 | Landing run-recipe | UPGR-061–070 | 0 |
| 8 | Landing proof | UPGR-071–080 | 0 |
| 9 | Landing GTM | UPGR-081–090 | 0 |
| 10 | Cursor founder UX | UPGR-091–100 | 1 |
| 11 | Factory freeze | UPGR-101–110 | 1 |
| 12 | Hub H1 live | UPGR-111–120 | 0 |
| 13 | Broker INBOX Worker | UPGR-121–130 | 0 |
| 14 | Pipeline queue | UPGR-131–140 | 0 |
| 15 | Validators ladder | UPGR-141–150 | 0 |
| 16 | Receipts SSOT | UPGR-151–160 | 0 |
| 17 | Session gate | UPGR-161–170 | 0 |
| 18 | Commercial W1 | UPGR-171–180 | 1 |
| 19 | Commercial W2 | UPGR-181–190 | 0 |
| 20 | Commercial W3 | UPGR-191–200 | 0 |
| 21 | Witness UI trust | UPGR-201–210 | 0 |
| 22 | Witness deploy | UPGR-211–220 | 1 |
| 23 | DevBridge wire | UPGR-221–230 | 0 |
| 24 | N8N integrations | UPGR-231–240 | 0 |
| 25 | Desktop apps | UPGR-241–250 | 0 |
| 26 | Performance | UPGR-251–260 | 1 |
| 27 | Security vs body | UPGR-261–270 | 0 |
| 28 | Founder docs | UPGR-271–280 | 1 |
| 29 | Metrics | UPGR-281–290 | 0 |
| 30 | Stage gates | UPGR-291–300 | 5 |

---

## All 300 plans


### Bucket 1 — Mac Health — stop & honesty

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-001 | Honest modal when 0 kills | Modal ⛔ Paused — Cursor still open | mac_health_emergency_stop_v1.py | P0 | S |
| UPGR-002 | Sync cool-down on UI stop | Run wake_cool_down synchronously | emergency_stop | P0 | S |
| UPGR-003 | PID enumeration before kill | pgrep proof in receipt | emergency_stop | P0 | S |
| UPGR-004 | still_running in receipt | Top 8 when kill_count=0 | receipt schema | P0 | S |
| UPGR-005 | launchd bootout + kill | Pause and kill instances | PAUSE_LAUNCH_AGENTS | P0 | S |
| UPGR-006 | Port 13020/13030 sweep | lsof kill hub listeners | KILL_PORTS | P1 | S |
| UPGR-007 | Plan revoke on panic | plan_revoked + cancel flag | plan_revoked_v1.py | P0 | S |
| UPGR-008 | Guard belt on stop | auto-paste off · inbox clear | _guard_belt | P1 | S |
| UPGR-009 | CPU/RAM before/after | cursor + system_ram fields | receipt | P1 | S |
| UPGR-010 | Dry-run CLI | --dry-run --json for founder | CLI | P1 | S |

### Bucket 2 — Mac Health — UI & tabs

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-011 | No auto Cool Down steal | userPickedTab sticks | app.js | P0 | S |
| UPGR-012 | RAM truth always clickable | z-index · skip grid rebuild | app.js | P0 | S |
| UPGR-013 | Split score vs Cursor emergency | No STRONG BEAT at cursor_hot | mac_health_guard.py | P0 | S |
| UPGR-014 | cursor_busy no nag | Hide prevention banner | app.js | P0 | S |
| UPGR-015 | Stop button label | Stop background agents | index.html | P0 | S |
| UPGR-016 | Panic strip honest | Factory only · Restart for IDE | index.html | P0 | S |
| UPGR-017 | Warn flash at 0 kills | panic-flash warn not done | app.js | P0 | S |
| UPGR-018 | Live poll mutex | liveFetchInFlight | app.js | P1 | S |
| UPGR-019 | Cooldown cursor_busy copy | Normal while you work | paintCooldownLive | P1 | S |
| UPGR-020 | Version cache bust | app.js?v= on ship | index.html | P1 | S |

### Bucket 3 — Mac Health — native & panic

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-021 | Native bridge | Implement native bridge | bucket-21 | P0 | S |
| UPGR-022 | Desktop STOP app | Implement desktop stop app | bucket-21 | P0 | S |
| UPGR-023 | Protect panic listener | Implement protect panic listener | bucket-21 | P0 | S |
| UPGR-024 | PANIC.now trigger | Implement panic.now trigger | bucket-21 | P1 | S |
| UPGR-025 | Menubar STOP | Implement menubar stop | bucket-21 | P1 | S |
| UPGR-026 | Keyboard shortcut guide | Implement keyboard shortcut guide | bucket-21 | P1 | S |
| UPGR-027 | Rebuild on ship | Implement rebuild on ship | bucket-21 | P1 | S |
| UPGR-028 | Cold-start gate | Implement cold-start gate | bucket-21 | P1 | S |
| UPGR-029 | Native restart Cursor | Implement native restart cursor | bucket-21 | P1 | S |
| UPGR-030 | Launch log footer | Implement launch log footer | bucket-21 | P1 | S |

### Bucket 4 — Agent prevention

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-031 | cursor_busy thresholds | Implement cursor_busy thresholds | bucket-31 | P0 | S |
| UPGR-032 | Unattended streak | Implement unattended streak | bucket-31 | P0 | S |
| UPGR-033 | Wake storm | Implement wake storm | bucket-31 | P0 | S |
| UPGR-034 | Founder away detect | Implement founder away detect | bucket-31 | P1 | S |
| UPGR-035 | Freeze flag audit | Implement freeze flag audit | bucket-31 | P1 | S |
| UPGR-036 | Banner gating | Implement banner gating | bucket-31 | P1 | S |
| UPGR-037 | No restart default tap | Implement no restart default tap | bucket-31 | P1 | S |
| UPGR-038 | panic config SSOT | Implement panic config ssot | bucket-31 | P1 | S |
| UPGR-039 | Streak reset | Implement streak reset | bucket-31 | P1 | S |
| UPGR-040 | Live pulse prevention | Implement live pulse prevention | bucket-31 | P1 | S |

### Bucket 5 — Process targeting

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-041 | Orphan script killer | Implement orphan script killer | bucket-41 | P0 | S |
| UPGR-042 | Expand KILL_PATTERNS | Implement expand kill_patterns | bucket-41 | P0 | S |
| UPGR-043 | Protected heart list | Implement protected heart list | bucket-41 | P0 | S |
| UPGR-044 | No Cursor on UI stop | Implement no cursor on ui stop | bucket-41 | P1 | S |
| UPGR-045 | Desktop restart bar | Implement desktop restart bar | bucket-41 | P1 | S |
| UPGR-046 | Unique kill count | Implement unique kill count | bucket-41 | P1 | S |
| UPGR-047 | targets_before dry-run | Implement targets_before dry-run | bucket-41 | P1 | S |
| UPGR-048 | Receipt schema v1 | Implement receipt schema v1 | bucket-41 | P1 | S |
| UPGR-049 | TERM then KILL | Implement term then kill | bucket-41 | P1 | S |
| UPGR-050 | Pattern audit quarterly | Implement pattern audit quarterly | bucket-41 | P1 | S |

### Bucket 6 — Tunnel & deploy

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-051 | Exclude landing tunnel | Implement exclude landing tunnel | bucket-51 | P0 | S |
| UPGR-052 | URL on Desktop note | Implement url on desktop note | bucket-51 | P0 | S |
| UPGR-053 | Republish recovery doc | Implement republish recovery doc | bucket-51 | P0 | S |
| UPGR-054 | Local 8190 fallback | Implement local 8190 fallback | bucket-51 | P1 | S |
| UPGR-055 | DNS flush hint | Implement dns flush hint | bucket-51 | P1 | S |
| UPGR-056 | witnessbc.com stable | Implement witnessbc.com stable | bucket-51 | P1 | S |
| UPGR-057 | Tunnel pid hygiene | Implement tunnel pid hygiene | bucket-51 | P1 | S |
| UPGR-058 | Stop before redeploy | Implement stop before redeploy | bucket-51 | P1 | S |
| UPGR-059 | Verify public HTTP | Implement verify public http | bucket-51 | P1 | S |
| UPGR-060 | Ephemeral flag warn | Implement ephemeral flag warn | bucket-51 | P1 | S |

### Bucket 7 — Landing run-recipe

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-061 | run-recipe canonical | Implement run-recipe canonical | bucket-61 | P1 | S |
| UPGR-062 | validate v7 gate | Implement validate v7 gate | bucket-61 | P1 | S |
| UPGR-063 | pages.json SSOT | Implement pages.json ssot | bucket-61 | P1 | S |
| UPGR-064 | build.py bundles | Implement build.py bundles | bucket-61 | P1 | S |
| UPGR-065 | nav/footer sync | Implement nav/footer sync | bucket-61 | P1 | S |
| UPGR-066 | run receipt JSON | Implement run receipt json | bucket-61 | P1 | S |
| UPGR-067 | Playwright --e2e | Implement playwright --e2e | bucket-61 | P1 | S |
| UPGR-068 | --open flag | Implement --open flag | bucket-61 | P1 | S |
| UPGR-069 | PORT 5180 default | Implement port 5180 default | bucket-61 | P1 | S |
| UPGR-070 | usage on bad args | Implement usage on bad args | bucket-61 | P1 | S |

### Bucket 8 — Landing proof

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-071 | W1 film slot | Implement w1 film slot | bucket-71 | P1 | S |
| UPGR-072 | scenario crosswalk | Implement scenario crosswalk | bucket-71 | P1 | S |
| UPGR-073 | boot-proof visible | Implement boot-proof visible | bucket-71 | P1 | S |
| UPGR-074 | tamper FAIL fallback | Implement tamper fail fallback | bucket-71 | P1 | S |
| UPGR-075 | cohort block 2026 | Implement cohort block 2026 | bucket-71 | P1 | S |
| UPGR-076 | proof mailto CTAs | Implement proof mailto ctas | bucket-71 | P1 | S |
| UPGR-077 | SKU lane router | Implement sku lane router | bucket-71 | P1 | S |
| UPGR-078 | platform quickstart | Implement platform quickstart | bucket-71 | P1 | S |
| UPGR-079 | og-card refresh | Implement og-card refresh | bucket-71 | P1 | S |
| UPGR-080 | film strip autoplay | Implement film strip autoplay | bucket-71 | P1 | S |

### Bucket 9 — Landing GTM

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-081 | procurement strip | Implement procurement strip | bucket-81 | P1 | S |
| UPGR-082 | Flow/Ops CTAs | Implement flow/ops ctas | bucket-81 | P1 | S |
| UPGR-083 | tier clarity | Implement tier clarity | bucket-81 | P1 | S |
| UPGR-084 | deposit micro-copy | Implement deposit micro-copy | bucket-81 | P1 | S |
| UPGR-085 | buyer chips | Implement buyer chips | bucket-81 | P1 | S |
| UPGR-086 | stat cites | Implement stat cites | bucket-81 | P1 | S |
| UPGR-087 | dual CTA hero | Implement dual cta hero | bucket-81 | P1 | S |
| UPGR-088 | category headline | Implement category headline | bucket-81 | P1 | S |
| UPGR-089 | sticky mobile CTA | Implement sticky mobile cta | bucket-81 | P1 | S |
| UPGR-090 | trust row | Implement trust row | bucket-81 | P1 | S |

### Bucket 10 — Cursor founder UX

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-091 | never Terminal | Implement never terminal | bucket-91 | P0 | S |
| UPGR-092 | subagent cancel | Implement subagent cancel | bucket-91 | P1 | S |
| UPGR-093 | cancel flag readers | Implement cancel flag readers | bucket-91 | P1 | S |
| UPGR-094 | INBOX slim | Implement inbox slim | bucket-91 | P1 | S |
| UPGR-095 | one Worker chat | Implement one worker chat | bucket-91 | P1 | S |
| UPGR-096 | session gate | Implement session gate | bucket-91 | P1 | S |
| UPGR-097 | disk wins | Implement disk wins | bucket-91 | P1 | S |
| UPGR-098 | re-gate after summary | Implement re-gate after summary | bucket-91 | P1 | S |
| UPGR-099 | Brain 90s shell | Implement brain 90s shell | bucket-91 | P1 | S |
| UPGR-100 | app badges honest | Implement app badges honest | bucket-91 | P1 | S |

### Bucket 11 — Factory freeze

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-101 | freeze flag semantics | Implement freeze flag semantics | bucket-101 | P0 | S |
| UPGR-102 | panic active flag | Implement panic active flag | bucket-101 | P1 | S |
| UPGR-103 | autorun respects freeze | Implement autorun respects freeze | bucket-101 | P1 | S |
| UPGR-104 | goal1 lock clear | Implement goal1 lock clear | bucket-101 | P1 | S |
| UPGR-105 | inbox clear | Implement inbox clear | bucket-101 | P1 | S |
| UPGR-106 | auto-paste off | Implement auto-paste off | bucket-101 | P1 | S |
| UPGR-107 | live automation off | Implement live automation off | bucket-101 | P1 | S |
| UPGR-108 | freeze in Safety | Implement freeze in safety | bucket-101 | P1 | S |
| UPGR-109 | manual unfreeze doc | Implement manual unfreeze doc | bucket-101 | P1 | S |
| UPGR-110 | freeze not kill Cursor | Implement freeze not kill cursor | bucket-101 | P1 | S |

### Bucket 12 — Hub H1 live

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-111 | H1 bookmark truth | Implement h1 bookmark truth | bucket-111 | P1 | S |
| UPGR-112 | factory_now_line | Implement factory_now_line | bucket-111 | P1 | S |
| UPGR-113 | command-data not SSOT | Implement command-data not ssot | bucket-111 | P1 | S |
| UPGR-114 | Next steps SSOT | Implement next steps ssot | bucket-111 | P1 | S |
| UPGR-115 | Safety not Command | Implement safety not command | bucket-111 | P1 | S |
| UPGR-116 | legacy museum | Implement legacy museum | bucket-111 | P1 | S |
| UPGR-117 | Hub Actions one-tap | Implement hub actions one-tap | bucket-111 | P1 | S |
| UPGR-118 | live wire sync | Implement live wire sync | bucket-111 | P1 | S |
| UPGR-119 | truth bundle fresh | Implement truth bundle fresh | bucket-111 | P1 | S |
| UPGR-120 | H1 in Mac Health | Implement h1 in mac health | bucket-111 | P1 | S |

### Bucket 13 — Broker INBOX Worker

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-121 | RUN INBOX executes | Implement run inbox executes | bucket-121 | P1 | S |
| UPGR-122 | feasibility gate | Implement feasibility gate | bucket-121 | P1 | S |
| UPGR-123 | broker submit | Implement broker submit | bucket-121 | P1 | S |
| UPGR-124 | ROUND_REPORT | Implement round_report | bucket-121 | P1 | S |
| UPGR-125 | slim inbox schema | Implement slim inbox schema | bucket-121 | P1 | S |
| UPGR-126 | no giant Brain paste | Implement no giant brain paste | bucket-121 | P1 | S |
| UPGR-127 | entry gate worker | Implement entry gate worker | bucket-121 | P1 | S |
| UPGR-128 | self-audit start | Implement self-audit start | bucket-121 | P1 | S |
| UPGR-129 | empty inbox honest | Implement empty inbox honest | bucket-121 | P1 | S |
| UPGR-130 | EDIT ALLOWED law | Implement edit allowed law | bucket-121 | P1 | S |

### Bucket 14 — Pipeline queue

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-131 | pipeline sweep force | Implement pipeline sweep force | bucket-131 | P1 | S |
| UPGR-132 | cart ghost sweep | Implement cart ghost sweep | bucket-131 | P1 | S |
| UPGR-133 | strict queue kill | Implement strict queue kill | bucket-131 | P1 | S |
| UPGR-134 | align UI kill | Implement align ui kill | bucket-131 | P1 | S |
| UPGR-135 | queue SSOT audit | Implement queue ssot audit | bucket-131 | P1 | S |
| UPGR-136 | Clear pipeline btn | Implement clear pipeline btn | bucket-131 | P1 | S |
| UPGR-137 | pipeline in receipt | Implement pipeline in receipt | bucket-131 | P1 | S |
| UPGR-138 | bootout before kill | Implement bootout before kill | bucket-131 | P1 | S |
| UPGR-139 | queue idle metric | Implement queue idle metric | bucket-131 | P1 | S |
| UPGR-140 | queue validator | Implement queue validator | bucket-131 | P1 | S |

### Bucket 15 — Validators ladder

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-141 | intent groups cadence | Implement intent groups cadence | bucket-141 | P1 | S |
| UPGR-142 | ladder runner | Implement ladder runner | bucket-141 | P1 | S |
| UPGR-143 | ladder validator | Implement ladder validator | bucket-141 | P1 | S |
| UPGR-144 | ladder receipt | Implement ladder receipt | bucket-141 | P1 | S |
| UPGR-145 | W1/W2/W3 gap | Implement w1/w2/w3 gap | bucket-141 | P1 | S |
| UPGR-146 | UP-id before code | Implement up-id before code | bucket-141 | P1 | S |
| UPGR-147 | before/after photo | Implement before/after photo | bucket-141 | P1 | S |
| UPGR-148 | law supersession | Implement law supersession | bucket-141 | P1 | S |
| UPGR-149 | no validator chains | Implement no validator chains | bucket-141 | P1 | S |
| UPGR-150 | calibrate trigger | Implement calibrate trigger | bucket-141 | P1 | S |

### Bucket 16 — Receipts SSOT

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-151 | chat not SSOT | Implement chat not ssot | bucket-151 | P1 | S |
| UPGR-152 | emergency receipt path | Implement emergency receipt path | bucket-151 | P1 | S |
| UPGR-153 | publish receipt | Implement publish receipt | bucket-151 | P1 | S |
| UPGR-154 | gate receipt | Implement gate receipt | bucket-151 | P1 | S |
| UPGR-155 | plan revoked receipt | Implement plan revoked receipt | bucket-151 | P1 | S |
| UPGR-156 | broker receipt | Implement broker receipt | bucket-151 | P1 | S |
| UPGR-157 | no fake progress | Implement no fake progress | bucket-151 | P1 | S |
| UPGR-158 | receipt wins UI | Implement receipt wins ui | bucket-151 | P1 | S |
| UPGR-159 | schema stable | Implement schema stable | bucket-151 | P1 | S |
| UPGR-160 | governance jsonl | Implement governance jsonl | bucket-151 | P1 | S |

### Bucket 17 — Session gate

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-161 | gate fail-closed | Implement gate fail-closed | bucket-161 | P1 | S |
| UPGR-162 | pre-ship scan | Implement pre-ship scan | bucket-161 | P1 | S |
| UPGR-163 | duty card read | Implement duty card read | bucket-161 | P1 | S |
| UPGR-164 | no auto hospital | Implement no auto hospital | bucket-161 | P1 | S |
| UPGR-165 | no auto orientation | Implement no auto orientation | bucket-161 | P1 | S |
| UPGR-166 | Brain zero violations | Implement brain zero violations | bucket-161 | P1 | S |
| UPGR-167 | stack v2 | Implement stack v2 | bucket-161 | P1 | S |
| UPGR-168 | mirror read order | Implement mirror read order | bucket-161 | P1 | S |
| UPGR-169 | STOP plan_revoked | Implement stop plan_revoked | bucket-161 | P1 | S |
| UPGR-170 | validate duty card | Implement validate duty card | bucket-161 | P1 | S |

### Bucket 18 — Commercial W1

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-171 | W1 film ship | Implement w1 film ship | bucket-171 | P0 | S |
| UPGR-172 | 10-min instrument | Implement 10-min instrument | bucket-171 | P1 | S |
| UPGR-173 | K1 signing | Implement k1 signing | bucket-171 | P1 | S |
| UPGR-174 | proof terminal keep | Implement proof terminal keep | bucket-171 | P1 | S |
| UPGR-175 | boot BLOCK visible | Implement boot block visible | bucket-171 | P1 | S |
| UPGR-176 | film + fallback | Implement film + fallback | bucket-171 | P1 | S |
| UPGR-177 | autoplay strip | Implement autoplay strip | bucket-171 | P1 | S |
| UPGR-178 | crosswalk keep | Implement crosswalk keep | bucket-171 | P1 | S |
| UPGR-179 | stepper keep | Implement stepper keep | bucket-171 | P1 | S |
| UPGR-180 | unfilmed gap close | Implement unfilmed gap close | bucket-171 | P1 | S |

### Bucket 19 — Commercial W2

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-181 | pre-LLM gate | Implement pre-llm gate | bucket-181 | P1 | S |
| UPGR-182 | export checksum | Implement export checksum | bucket-181 | P1 | S |
| UPGR-183 | validator-on-read | Implement validator-on-read | bucket-181 | P1 | S |
| UPGR-184 | SDK receipt API | Implement sdk receipt api | bucket-181 | P1 | S |
| UPGR-185 | bypass=0 CI | Implement bypass=0 ci | bucket-181 | P1 | S |
| UPGR-186 | multi-tenant | Implement multi-tenant | bucket-181 | P1 | S |
| UPGR-187 | SLO honest | Implement slo honest | bucket-181 | P1 | S |
| UPGR-188 | GitHub eval README | Implement github eval readme | bucket-181 | P1 | S |
| UPGR-189 | MCP surface | Implement mcp surface | bucket-181 | P1 | S |
| UPGR-190 | kernel retro | Implement kernel retro | bucket-181 | P1 | S |

### Bucket 20 — Commercial W3

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-191 | 20 emails/week | Implement 20 emails/week | bucket-191 | P1 | S |
| UPGR-192 | ABM CA 100 | Implement abm ca 100 | bucket-191 | P1 | S |
| UPGR-193 | qualifier form | Implement qualifier form | bucket-191 | P1 | S |
| UPGR-194 | deposits dashboard | Implement deposits dashboard | bucket-191 | P1 | S |
| UPGR-195 | win/loss script | Implement win/loss script | bucket-191 | P1 | S |
| UPGR-196 | inbound SLA | Implement inbound sla | bucket-191 | P1 | S |
| UPGR-197 | NF outreach ship | Implement nf outreach ship | bucket-191 | P1 | S |
| UPGR-198 | outbound approve | Implement outbound approve | bucket-191 | P1 | S |
| UPGR-199 | energy law 45% | Implement energy law 45% | bucket-191 | P1 | S |
| UPGR-200 | 3 deposit gate | Implement 3 deposit gate | bucket-191 | P1 | S |

### Bucket 21 — Witness UI trust

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-201 | trust 5→8 | Implement trust 5→8 | bucket-201 | P1 | S |
| UPGR-202 | category headline | Implement category headline | bucket-201 | P1 | S |
| UPGR-203 | dual CTA touch | Implement dual cta touch | bucket-201 | P1 | S |
| UPGR-204 | stat cites | Implement stat cites | bucket-201 | P1 | S |
| UPGR-205 | buyer pills | Implement buyer pills | bucket-201 | P1 | S |
| UPGR-206 | control-plane keep | Implement control-plane keep | bucket-201 | P1 | S |
| UPGR-207 | multi-page IA | Implement multi-page ia | bucket-201 | P1 | S |
| UPGR-208 | nav active | Implement nav active | bucket-201 | P1 | S |
| UPGR-209 | reduced motion | Implement reduced motion | bucket-201 | P1 | S |
| UPGR-210 | UI 88→92 | Implement ui 88→92 | bucket-201 | P1 | S |

### Bucket 22 — Witness deploy

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-211 | wrangler primary | Implement wrangler primary | bucket-211 | P0 | S |
| UPGR-212 | tunnel fallback doc | Implement tunnel fallback doc | bucket-211 | P1 | S |
| UPGR-213 | post-deploy verify | Implement post-deploy verify | bucket-211 | P1 | S |
| UPGR-214 | Lighthouse gate | Implement lighthouse gate | bucket-211 | P1 | S |
| UPGR-215 | OG per page | Implement og per page | bucket-211 | P1 | S |
| UPGR-216 | CDN headers | Implement cdn headers | bucket-211 | P1 | S |
| UPGR-217 | rollback runbook | Implement rollback runbook | bucket-211 | P1 | S |
| UPGR-218 | staging vs prod | Implement staging vs prod | bucket-211 | P1 | S |
| UPGR-219 | secrets not in repo | Implement secrets not in repo | bucket-211 | P1 | S |
| UPGR-220 | deploy receipt | Implement deploy receipt | bucket-211 | P1 | S |

### Bucket 23 — DevBridge wire

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-221 | Week1 B+C gate | Implement week1 b+c gate | bucket-221 | P1 | S |
| UPGR-222 | Mac Agent MCP | Implement mac agent mcp | bucket-221 | P1 | S |
| UPGR-223 | Extension VSIX | Implement extension vsix | bucket-221 | P1 | S |
| UPGR-224 | 10 workflow packs | Implement 10 workflow packs | bucket-221 | P1 | S |
| UPGR-225 | RUN SYSTEM receipt | Implement run system receipt | bucket-221 | P1 | S |
| UPGR-226 | one plan doc | Implement one plan doc | bucket-221 | P1 | S |
| UPGR-227 | pick step script | Implement pick step script | bucket-221 | P1 | S |
| UPGR-228 | no parallel plans | Implement no parallel plans | bucket-221 | P1 | S |
| UPGR-229 | track A week2 | Implement track a week2 | bucket-221 | P1 | S |
| UPGR-230 | evidence folder | Implement evidence folder | bucket-221 | P1 | S |

### Bucket 24 — N8N integrations

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-231 | pause n8n cool down | Implement pause n8n cool down | bucket-231 | P1 | S |
| UPGR-232 | N8N app health | Implement n8n app health | bucket-231 | P1 | S |
| UPGR-233 | n8n in kill patterns | Implement n8n in kill patterns | bucket-231 | P1 | S |
| UPGR-234 | Chat Unify port | Implement chat unify port | bucket-231 | P1 | S |
| UPGR-235 | Apple Health port | Implement apple health port | bucket-231 | P1 | S |
| UPGR-236 | protect mini-apps | Implement protect mini-apps | bucket-231 | P1 | S |
| UPGR-237 | SEMEJ chrome separate | Implement semej chrome separate | bucket-231 | P1 | S |
| UPGR-238 | port registry | Implement port registry | bucket-231 | P1 | S |
| UPGR-239 | glue audit | Implement glue audit | bucket-231 | P1 | S |
| UPGR-240 | n8n step receipt | Implement n8n step receipt | bucket-231 | P1 | S |

### Bucket 25 — Desktop apps

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-241 | Mac Health rebuild | Implement mac health rebuild | bucket-241 | P1 | S |
| UPGR-242 | System Truth badge | Implement system truth badge | bucket-241 | P1 | S |
| UPGR-243 | STOP AGENTS real | Implement stop agents real | bucket-241 | P1 | S |
| UPGR-244 | icon set unified | Implement icon set unified | bucket-241 | P1 | S |
| UPGR-245 | cold-start all apps | Implement cold-start all apps | bucket-241 | P1 | S |
| UPGR-246 | launch logs | Implement launch logs | bucket-241 | P1 | S |
| UPGR-247 | native menu Stop | Implement native menu stop | bucket-241 | P1 | S |
| UPGR-248 | menubar visible | Implement menubar visible | bucket-241 | P1 | S |
| UPGR-249 | code sign install | Implement code sign install | bucket-241 | P1 | S |
| UPGR-250 | footer links | Implement footer links | bucket-241 | P1 | S |

### Bucket 26 — Performance

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-251 | poll 8s/4s | Implement poll 8s/4s | bucket-251 | P0 | S |
| UPGR-252 | skip pressure off rhythm | Implement skip pressure off rhythm | bucket-251 | P1 | S |
| UPGR-253 | skip history off rhythm | Implement skip history off rhythm | bucket-251 | P1 | S |
| UPGR-254 | fetch mutex | Implement fetch mutex | bucket-251 | P1 | S |
| UPGR-255 | full poll 60s | Implement full poll 60s | bucket-251 | P1 | S |
| UPGR-256 | no-store headers | Implement no-store headers | bucket-251 | P1 | S |
| UPGR-257 | RAM truth lightweight | Implement ram truth lightweight | bucket-251 | P1 | S |
| UPGR-258 | no full grid pulse | Implement no full grid pulse | bucket-251 | P1 | S |
| UPGR-259 | WKWebView native | Implement wkwebview native | bucket-251 | P1 | S |
| UPGR-260 | renderer peak CPU | Implement renderer peak cpu | bucket-251 | P1 | S |

### Bucket 27 — Security vs body

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-261 | decouple scores | Implement decouple scores | bucket-261 | P1 | S |
| UPGR-262 | guardians status only | Implement guardians status only | bucket-261 | P1 | S |
| UPGR-263 | findings tap cool down | Implement findings tap cool down | bucket-261 | P1 | S |
| UPGR-264 | firewall button | Implement firewall button | bucket-261 | P1 | S |
| UPGR-265 | scan dont block tabs | Implement scan dont block tabs | bucket-261 | P1 | S |
| UPGR-266 | compact founder mode | Implement compact founder mode | bucket-261 | P1 | S |
| UPGR-267 | important note | Implement important note | bucket-261 | P1 | S |
| UPGR-268 | domains read-only | Implement domains read-only | bucket-261 | P1 | S |
| UPGR-269 | history rhythm only | Implement history rhythm only | bucket-261 | P1 | S |
| UPGR-270 | grade plain language | Implement grade plain language | bucket-261 | P1 | S |

### Bucket 28 — Founder docs

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-271 | When Stop works | Implement when stop works | bucket-271 | P0 | S |
| UPGR-272 | When Restart Cursor | Implement when restart cursor | bucket-271 | P1 | S |
| UPGR-273 | tunnel dies on stop | Implement tunnel dies on stop | bucket-271 | P1 | S |
| UPGR-274 | dry-run guide | Implement dry-run guide | bucket-271 | P1 | S |
| UPGR-275 | app fleet map | Implement app fleet map | bucket-271 | P1 | S |
| UPGR-276 | port map | Implement port map | bucket-271 | P1 | S |
| UPGR-277 | energy law | Implement energy law | bucket-271 | P1 | S |
| UPGR-278 | dead mechanics | Implement dead mechanics | bucket-271 | P1 | S |
| UPGR-279 | three pipelines | Implement three pipelines | bucket-271 | P1 | S |
| UPGR-280 | ladder bookmark | Implement ladder bookmark | bucket-271 | P1 | S |

### Bucket 29 — Metrics

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-281 | kill_count metric | Implement kill_count metric | bucket-281 | P1 | S |
| UPGR-282 | elapsed_ms | Implement elapsed_ms | bucket-281 | P1 | S |
| UPGR-283 | system_ram delta | Implement system_ram delta | bucket-281 | P1 | S |
| UPGR-284 | cool step_lines | Implement cool step_lines | bucket-281 | P1 | S |
| UPGR-285 | tunnel uptime | Implement tunnel uptime | bucket-281 | P1 | S |
| UPGR-286 | LIVE meta line | Implement live meta line | bucket-281 | P1 | S |
| UPGR-287 | factory_now quote | Implement factory_now quote | bucket-281 | P1 | S |
| UPGR-288 | deposits dashboard | Implement deposits dashboard | bucket-281 | P1 | S |
| UPGR-289 | unattended streak | Implement unattended streak | bucket-281 | P1 | S |
| UPGR-290 | governance log | Implement governance log | bucket-281 | P1 | S |

### Bucket 30 — Stage gates

| ID | Title | Action | Surface | P | Eff |
|----|-------|--------|---------|---|-----|
| UPGR-291 | STRATEGIC-SLICE P0 | Implement strategic-slice p0 | bucket-291 | P0 | S |
| UPGR-292 | Phase 3 index | Implement phase 3 index | bucket-291 | P0 | S |
| UPGR-293 | 9.07 A ship | Implement 9.07 a ship | bucket-291 | P0 | S |
| UPGR-294 | 0 open PICKs | Implement 0 open picks | bucket-291 | P0 | S |
| UPGR-295 | Safety daily | Implement safety daily | bucket-291 | P0 | S |
| UPGR-296 | RunReceipt parallel | Implement runreceipt parallel | bucket-291 | P1 | S |
| UPGR-297 | blueprint frozen | Implement blueprint frozen | bucket-291 | P1 | S |
| UPGR-298 | Tier-1 thesis | Implement tier-1 thesis | bucket-291 | P1 | S |
| UPGR-299 | UPGR to UP-id | Implement upgr to up-id | bucket-291 | P1 | S |
| UPGR-300 | monthly retro | Implement monthly retro | bucket-291 | P1 | S |

---

## Cross-references

- UPGR-171–200 → `BLUEPRINT_MARKET_300_PLANS_TIER1_RESEARCH_REPORT_v1.md`

- UPGR-201–210 → `WITNESSBC_UI_UPGRADE_30_PLAN_2026-06-15_v1.md`

- UPGR-221–230 → `DEVBRIDGE_EXTENSION_NO_CODE_300_STEP_PLAN_LOCKED_v1.md`

- UPGR-141–150 → `SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md`

- UPGR-001–050 → Mac Health session 2026-06-15


*End — 300 plans organized v1*
