# Noetfield — cloud git, Mac hub, and agent entry (unified)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-04 · **Status:** LOCKED  
**Audience:** Founder, `noetfield_local`, `noetfield_cloud`, cloud Cursor clones  
**Hub:** Essentials tab → **Noetfield lanes** card (same content in app)

---

## One-line policy

> **Noetfield git = product + ship + in-repo agent entry. Ecosystem law lives on founder Mac (`SourceA`). Cloud agents read git ops docs; Mac adds hub + sync mirror — never the other way around.**

---

## Two Noetfield workspaces (never mix)

| Agent id | Open folder | Role |
|----------|-------------|------|
| **noetfield_local** | `~/Desktop/Noetfield-All-Documents` | Docs archive — hierarchy, registry, L0–L3 |
| **noetfield_cloud** | `~/Desktop/Noetfield` | **Ship code** — APIs, UI, `:13080`, GitHub |

**Wrong chat = wrong edits.** Local chat must not touch `Desktop/Noetfield`. Cloud chat must not touch All-Documents.

---

## Three layers (SSOT)

```text
LAYER C — Mac founder only
  ~/Desktop/SourceA/          ecosystem law, notices, rebuild scripts
  http://127.0.0.1:13020/     Sina Command hub (loopback)

LAYER B — gitignored on Mac (never commit)
  Noetfield/ops/private/sourceA/   after ./scripts/sync-sourceA-desktop.sh

LAYER A — in git (cloud clone has this)
  Noetfield/docs/ops/*_LOCKED.md
  Noetfield/os/plan.json · os/SHIP_NOW.md
  product code
```

**Newest notices:** `SourceA/founder/repo-agent-notices/` → rebuild → sync to Layer B.

---

## Mac vs cloud — who can use what

| Surface | Mac founder | Cloud VM / other clone |
|---------|-------------|-------------------------|
| Hub `:13020` | Yes | No — not your machine |
| `sync-sourceA-desktop.sh` | Yes | No — needs Desktop SourceA path |
| `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` in git | Yes | **Yes — primary entry** |
| `os/SHIP_NOW.md` / `os/plan.json` | Yes | Yes |
| Full `AGENT_READ_LINKS_INDEX.md` (all repos) | Yes | Only via sync mirror or paste |

---

## HOW cloud works “without your Mac”

Cloud does **not** get your Mac files automatically.

1. `git clone` Noetfield repo  
2. Read **in git:** `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` → § Cloud ship  
3. Read `docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md`  
4. Ship from `os/SHIP_NOW.md` → `os/plan.json`  
5. For ecosystem law: founder runs sync on Mac → `ops/private/sourceA/` (gitignored) — or founder pastes notices into chat  

That is the **entry path without Mac** — **committed docs in the repo**, not remote hub access.

---

## Cloud read order (`noetfield_cloud`)

1. `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` (§ Cloud ship)  
2. `docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md`  
3. `os/SHIP_NOW.md` → `os/plan.json`  
4. After Mac sync: `SEMI_NOTICE_noetfield_cloud_v1.md` in `ops/private/sourceA/founder/repo-agent-notices/`  
5. **Thread:** `THREAD-PORTFOLIO` · **Paste:** `ready_to_paste_noetfield_cloud.txt` (Mac Prompt OS)

---

## Local read order (`noetfield_local`)

1. `REPO_NOTICE_noetfield_v1.md` (SourceA or sync mirror)  
2. `Noetfield-All-Documents/HIERARCHY_INDEX.md` + `registry/source_of_truth_registry.json`  
3. **Never** edit `~/Desktop/Noetfield` from this chat  

---

## Share in git (commit)

| Item | Why |
|------|-----|
| Product code, tests, Makefile | The product |
| `os/plan.json`, `os/SHIP_NOW.md`, sprint docs | Ship SSOT |
| `docs/ops/NOETFIELD_AGENT_CONTEXT_*`, `AGENT_READ_LINKS_LOCKED_v1.md` | Cloud entry + boundaries |
| Strategy/spec locks, `PRODUCT_TRUTH.md` | Scope and ship truth |
| `.cursor/rules` (repo-scoped) | In-workspace agent behavior |
| `prompts/loop-pack*` (cloud pack) | This agent only |

---

## Do not share in git

| Item | Why |
|------|-----|
| Full `~/Desktop/SourceA/**` | Ecosystem SSOT — drift + leak risk |
| `ops/private/sourceA/**` contents | Mirror may contain blockers, fleet JSON |
| Hub as dependency | Loopback only |
| Secrets, `.env`, tokens | Security |
| Full fleet `ready_to_paste_*` / other repo notices | Wrong lane |
| Personal DB paths, GLOBAL_BLOCKERS, bowl | Founder-only ops |
| Maintaining two masters of `AGENT_READ_LINKS_INDEX` | SourceA wins; repo gets locked mirror |

---

## Never (public repo)

Credentials · unredacted private mirror · founder PII · auto-paste inject configs

---

## Mac founder checklist

```bash
cd ~/Desktop/Noetfield && ./scripts/sync-sourceA-desktop.sh
cd ~/Desktop/SourceA && python3 scripts/build_repo_agent_notices.py
~/Desktop/SourceA/scripts/serve-sina-command.sh   # if hub 404
```

Hub: **Essentials** → Noetfield lanes · **Repos** → copy lane brief · **Agent hub** → noetfield_cloud / noetfield_local

---

## Pointers

- Full ecosystem links: `founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`  
- Semi notice (cloud): `SEMI_NOTICE_noetfield_cloud_v1.md`  
- Semi master: `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md`  
- In-repo mirror: `Noetfield/docs/ops/AGENT_READ_LINKS_LOCKED_v1.md`
