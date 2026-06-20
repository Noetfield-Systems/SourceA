# ASF — Retire Sina Command forever (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-15 · **Authority:** ASF order  
**Supersedes for product naming:** daily use of “Sina Command” and `/legacy/` as founder surface  
**Preserves:** Hub 1 `/` · Hub 2 `/machines/` · factory drain · disk law · `~/.sina` registry

---

## One-line policy

> **“Sina Command” is retired forever — the product is Hub (H1 + H2 only). `/legacy/` must not serve. Monolith deleted from disk (purge: `scripts/hub_stale_disk_purge_v1.py`).**

---

## What stays (not deleted)

| Surface | URL | Name in UI |
|---------|-----|------------|
| Hub 1 | `http://127.0.0.1:13020/` | **Hub** (not Sina Command) |
| Hub 2 | `http://127.0.0.1:13020/machines/` | **Machine Hub** |
| Server | `:13020` | **Hub server** (implementation name may remain in code until Maintainer rename) |

---

## What retires (forever)

| Item | Action |
|------|--------|
| `/legacy/` route | **Remove from server** — return 410 or redirect to `/` |
| “Sina Command” in founder UI | **Remove** — all copy says **Hub** |
| “Legacy archive” banner | **Remove** |
| Daily monolith (`app.js` hero, 42 tabs) | **Deleted from disk** — H1/H2 only in `agent-control-panel/worker-hub/` + `machines/` |
| Stale projections (`command-data*.json`) | **Rewritten** hub-only slim JSON (~1KB each) via `hub_stale_disk_purge_v1.py` |

---

## Machine latch

`~/.sina/worker-asf-directive-latch-v1.json`:

- `command_retired_forever: true`
- `no_hub_rebuild: true` · `no_hub_archive: true`
- `hub2_drain_allowed: true` (factory drain continues on H2 validators)

---

## Maintainer execution checklist (SourceA Worker maintainer chat)

1. `sina-command-server.py` — drop `/legacy/` handler; 410 or redirect `/legacy/*` → `/`
2. `worker-hub/index.html` + `worker_hub_v1.py` — remove “Sina Command” / “Legacy” labels; rename factory strip to **Factory** not **SINA COMMAND**
3. `build-sina-command-panel.py` — stop injecting legacy links into H1 projections
4. `validate-*` — add `validate-hub-no-legacy-route-v1.sh` + `validate-hub-no-sina-command-name-v1.sh`
5. Update `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` pointer — `/legacy/` **retired**, not maintenance

**Backlog:** `AR-0d2e1b25da` (filed 2026-06-15)

---

## Law hierarchy

ASF order (this doc) > `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` (partial supersession on `/legacy/` serve) > INCIDENT-032 museum link requirement (**superseded** by explicit retire — museum is `archive/` only, not live URL)

**Do not** restore monolith under `agent-control-panel/` — git history only if audit needed.
