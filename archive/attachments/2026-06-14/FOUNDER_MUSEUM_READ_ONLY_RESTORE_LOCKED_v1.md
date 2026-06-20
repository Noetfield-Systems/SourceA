# Founder Museum — READ ONLY restore (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order — *bring back old hub as archived read-only · do not erase founder museum*  
**Status:** **RESTORED IN REPOSITORY** — data never deleted · route live · agents must stop saying erased  
**Related:** INCIDENT-032 · INCIDENT-033 · `HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` · backlog **AR-b9955efbce**

---

## 1. ASF order (verbatim intent)

> Bring back the old hub the same as ordered to be **archived**.  
> **Do not erase founder museum.**  
> **READ ONLY.**

**Investigator verdict:** Museum was **never erased**. Default `/` changed to Worker Hub. Museum lives at **`/legacy/`**. Agents wrongly said erased + steered to dead Prompt feed path.

---

## 2. Founder Museum — where it is NOW (live)

| Item | Value |
|------|-------|
| **Name** | **Founder Museum** (read-only frozen monolith) |
| **URL** | **`http://127.0.0.1:13020/legacy/`** |
| **HTTP** | **200** (verified 2026-06-14) |
| **Shell** | `agent-control-panel/index.html` — title **Sina Command** · full sidebar |
| **Data** | `command-data.json` **10,724,891 bytes** (~10.7 MB) |
| **Also logged** | `command-data-canonical.json` · `command-data-runtime.json` · `command-data-shell.json` |
| **Mode** | **READ ONLY** — browse · reference · rare Actions · **not daily ops** |

**Bookmark this for museum:** `http://127.0.0.1:13020/legacy/`

---

## 3. What is NOT the museum (do not confuse)

| Surface | URL | Role |
|---------|-----|------|
| **Worker Hub (daily)** | `http://127.0.0.1:13020/` | Factory slice only — **not** museum |
| **Machine Hub (H2)** | `http://127.0.0.1:13020/machines/` | Heavy machines — **not** museum |
| **Prompt feed** | `/legacy/?tab=prompt-feed` only | **DEPRECATED** daily path — INCIDENT-028 |

---

## 4. What was the mistake (agent — not data)

| Mistake | Truth |
|---------|-------|
| "Museum erased" | **FALSE** — 10.7 MB logged |
| "Archived = gone" | **FALSE** — archived = **frozen at `/legacy/`** |
| "Open Sina Command Prompt feed" | **STALE** — contradicts archive law |
| H1 at `/` replaced bookmark | **UX fail** — museum link too small |
| `/oldhubsinacommand/` not shipped | **Maintainer backlog** AR-b9955efbce |

**No revert of data needed.** Revert = **stop false erasure language** + **prominent museum link** (maintainer).

---

## 5. READ ONLY law

1. **Founder may browse** all legacy tabs at `/legacy/` — subjects · Actions · advisor · backlog · everything that was in the monolith.
2. **Agents must not** say museum was deleted · wiped · erased · replaced.
3. **Agents must not** steer founder to **Prompt feed** or **Sina Command** as daily path.
4. **Daily factory** = **Worker chat → RUN INBOX** only.
5. **Edits to museum UI** = Maintainer (SinaaiDataBase) only — add **READ ONLY** banner · `/oldhubsinacommand/` alias.
6. **`command-data.json`** = projection/museum payload — **not** Brain/Worker runtime SSOT (INCIDENT-033).

---

## 6. Maintainer ship (hub code — required for founder-visible restore)

| # | Action |
|---|--------|
| 1 | `GET /oldhubsinacommand/` → same as `/legacy/` |
| 2 | Banner on museum: **READ ONLY — Founder Museum — frozen reference** |
| 3 | H1 button: **Open Founder Museum (read-only)** → `/oldhubsinacommand/` |
| 4 | Never remove `/legacy/` route |

---

## 7. Verification (any agent — before claiming erased)

```bash
wc -c ~/Desktop/SourceA/agent-control-panel/command-data.json
curl -sf -o /dev/null -w "%{http_code}\n" http://127.0.0.1:13020/legacy/
```

Both must pass. If pass → **museum exists** — do not say erased.

---

## 8. Status

**RESTORED** — archive file + disk proof · **2026-06-14**  
**OPEN** — maintainer museum banner + `/oldhubsinacommand/` alias

**END FOUNDER_MUSEUM_READ_ONLY_RESTORE**
