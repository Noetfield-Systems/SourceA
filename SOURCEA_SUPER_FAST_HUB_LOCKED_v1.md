# SourceA — Two-Hub Model + Super Fast Hub (LOCKED v1.2)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF — two hubs · form on H1 picks · pending on H2 · scheduled builds only · no wheel  
**Supersedes daily use:** monolith `agent-control-panel/` · **Extends:** `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · `HUB_LITE_REBUILD_PHASE0_LOCKED_v1.md`  
**Machine cadence:** `~/.sina/integration-fabric-registry-v1.yaml` → `two_hub_model` · `build_cadence_schedule`  
**Light hub built by:** Governance Goal Specialist (`e54ddfa8`)

---

## Law (one sentence)

**Hub 1 (Daily Necessities) is flawless every day — Hub 2 (Heavy Machines) is on the other side of the water; nothing rebuilds on a whim — only on the locked daily / 3-day / weekly / monthly schedule.**

---

## 0. Two-hub model (not three daily surfaces)

| Hub | Name | URL | Audience | Payload | Mistake tolerance |
|-----|------|-----|----------|---------|-------------------|
| **H1** | **Daily Necessities** (Super Fast) | `http://127.0.0.1:13020/` | Founder · workers · every day | ~4 KB `worker-hub/v1` | **Zero** — must never lie |
| **H2** | **Machine / Heavy** (other side) | `http://127.0.0.1:13020/machines/` *(SHIP)* | Maintainer · governance · deep machines | Disk receipts · tab slices · no 9MB hero | Scheduled only |
| **Archive** | Legacy Sina Command | `http://127.0.0.1:13020/legacy/` | Examples · rare Actions · agent loop | 9MB monolith | **Not built on schedule** — frozen reference |

**Rule:** H1 and H2 are **siblings** — not layers. H1 never loads H2 payload. H2 never replaces H1 as default bookmark.

---

## 1. H1 — Daily Necessities (Super Fast Hub)

**Must be there every day. No mistake.**

| Item | Value |
|------|--------|
| **UI** | `agent-control-panel/worker-hub/index.html` |
| **API** | `GET /api/worker-hub/v1` |
| **Build cadence** | **Daily** light refresh · **never** full monolith rebuild on founder Refresh |
| **Validator** | `validate-super-fast-hub-v1.sh` — **daily** gate |

### H1 screen — necessary only (ASF 2026-06-14)

1. Worker task (sa + title)
2. Queue / FREEZE / Valid YES
3. Live health + auto-heal (anti-staleness)
4. **Form open count** + top open PICK ids (from `live_founder_decision_form_v1.py` — not chat memory)
5. Judge **alarm strip one line** only (RIGHT/STALE/BAD count — full Judge on H2)
6. Safety check
7. Light refresh
8. Deep link → **H2 `/machines/`** (pending · Thread Room · next phases) or legacy `/legacy/` — new tab only

**Forbidden on H1:** Thread Room panels · full pending tables · multi-paragraph founder forks · `command-data.json` hero.

### Forbidden on H1

- Fetch `command-data.json` or `command-data-shell.json` on idle
- Auto full rebuild
- “Is it green?” from hub hero alone
- Embed heavy machine panels inline
- Thread Room scout/cartographer/curator UI inline (→ H2 second hop)
- List next-phase pending beyond one alarm line (→ H2 registry)

---

## 2. H2 — Machine / Heavy Hub (other side of the water)

**For heavy machines + all organized pending — not everyday clutter.**

| Item | Planned |
|------|---------|
| **Purpose** | **Pending registry** · next-phase queue · Thread Room · scoreboards · drift · council · WTM slice · packet readiness · fleet · research digest |
| **Pending SSOT** | `~/.sina/h2-pending-registry-v1.json` — Brain updates every session · Maintainer renders on SHIP |
| **Thread Room** | **Second hop** — scout/cartographer/curator receipts · §THREAD drafts · T30 arcs — **weekly run** · H1 shows alarm line only |
| **Data source** | `~/.sina/*-v1.json` receipts + `hub_surface_v1.py` tab slices — **not** live 9MB build |
| **Build cadence** | Per machine row in §3 — **never** on founder daily Refresh |
| **Founder** | Optional deep link from H1 — not default home |
| **SHIP owner** | Maintainer 2 after `Q-GOV-FAST-WIRE-v1` PICK |

### 2a. H2 pending registry (mandatory)

| Bucket | What lives here | When → Form |
|--------|-----------------|-------------|
| `form_open` | Mirror of `open_questions[]` — link to M1 Canvas | Always on Form until PICK |
| `next_phase` | W1 film · OpenRouter packs · phase resume items | When founder must choose |
| `deferred` | DEFER/RECONCILE picks (wire G3 · ENF-13 · 1.10 seal) | When unblocked |
| `ops_blocker` | MP-SHIP · WIRE-G3 · B-001 · portfolio lanes | Human gate — Form row if multi-step |
| `maintainer_ship` | H2 route · legacy hero · n8n wire | After Form PICK receipts |
| `thread_room` | `latest-curation-v1.json` summary · draft row count | §THREAD → Form append when decisive |

**Brain duty:** `thread_room_run_v1.py` + `h2-pending-registry-v1.json` + form `--json` → **organized reasoning** in closeout — never orphan pending in chat.

**Anti-wheel law:** H2 panels refresh from **pre-built receipts** on schedule — not `build-sina-command-panel.py` on every click.

---

## 3. Build cadence schedule (mandatory — no wheel)

| Cadence | What rebuilds / refreshes | Hub | Owner |
|---------|---------------------------|-----|-------|
| **Daily** | H1 worker-hub pins · session gate · truth bundle mirror · light refresh · super-fast validator | H1 | Auto + Maintainer watch |
| **Daily** | Governance center `--tier fast` · policy reasoning `--status` | Disk | n8n `wf-governance-fast-15m` after PICK |
| **Every 3 days** | Anti-staleness fast subset · hub copy validator · scoreboard receipt sync | H1/H2 | Maintainer |
| **Weekly** | Judge full batch · Thread scout · Change Quorum · governance center `--tier full` | H2 receipts → H1 alarm lines | n8n + one-tap |
| **Weekly** | H2 machine-hub receipt bundle regen (when SHIP) | H2 | Maintainer |
| **Monthly** | Strict hub build + `audit_hub_source_alignment` + full anti-staleness 38-step | Legacy/H2 only | ASF strict-hub Action |
| **Never scheduled** | Legacy monolith feature creep · random `command-data.json` hero · worker full rebuild on Refresh | Archive | Forbidden |

**Wheel = forbidden:** no agent triggers full build because “something feels stale.” Schedule or Form PICK only.

---

## 4. Why the old heavy hub was archived

| Problem | Cost |
|---------|------|
| `command-data.json` ~9.7 MB | Slow · stale hero · false green |
| `build-sina-command-panel.py` strict chain | Minutes · random FAIL |
| 30+ tabs · 480 KB `app.js` | Always broken |
| One hub for everything | Workers slow · governance slow · founder mistrust |

**Archive value:** Actions catalog · agent-loop · UI patterns — **not** daily truth.

---

## 5. Legacy monolith (archive — not H2)

| Item | Value |
|------|--------|
| **URL** | `http://127.0.0.1:13020/legacy/` |
| **Build** | Monthly strict only · or `SINA_PANEL_BUILD_ON_START=1` maintainer |
| **Rule** | Banner: Archive — use H1 for daily |

---

## 6. Agent law

| Do | Don't |
|----|-------|
| Founder → H1 `/` daily | Default bookmark to legacy or H2 |
| H1 light refresh only | Full rebuild on founder Refresh |
| H2 on schedule / deep link | Patch monolith for daily fixes |
| Disk receipts for machine truth | `command-data.json` hero for progress |
| Multi-sentence founder fork → Form | Chat-only decision lists |
| Pending / Thread Room → H2 | Thread Room panels on H1 |
| Brain updates `h2-pending-registry-v1.json` | Orphan pending in chat |

**Conduct:** `AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md`

---

## 7. Machine proof

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-super-fast-hub-v1.sh
curl -s http://127.0.0.1:13020/api/worker-hub/v1 | wc -c   # expect < 8192
python3 ~/Desktop/SourceA/scripts/live_founder_decision_form_v1.py --json | jq '.open_questions_count'
```

---

*End SOURCEA_SUPER_FAST_HUB_LOCKED_v1.2*
