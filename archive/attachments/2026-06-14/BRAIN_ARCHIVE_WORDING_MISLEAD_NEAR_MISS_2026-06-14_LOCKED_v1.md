# Brain archive wording mislead — near-miss audit + self-repair (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**Class:** Near-miss (trust) · INCIDENT-025 class (name/URL fragmentation)  
**Reporter:** Cursor Brain executor  
**Founder signal:** *"brain is suspicious saying wrong and false!!! if sinacommand was old hub so why its not in the archive???"*

---

## 1. What went wrong

| # | Mistake | Harm |
|---|---------|------|
| M1 | Said **"Sina Command archived"** without **URL** | Sounded like app deleted |
| M2 | Did not lead with **`/legacy/` = old monolith** | Founder could not find old hub |
| M3 | Used **archive** as metaphor, not **route + banner** | Broke trust (INCIDENT-025 class) |
| M4 | Implied `:13020` = one surface | Root `/` is Worker Hub; old UI is `/legacy/` |

**Disk truth:** Old panel = `agent-control-panel/index.html` served at `http://127.0.0.1:13020/legacy/`. Not deleted. Not default home.

---

## 2. Self-repair actions (2026-06-14)

| Action | Status |
|--------|--------|
| Founder correction acknowledged | Done |
| Maintainer backlog **AR-b9955efbce** — `/oldhubsinacommand/` read-only alias + banner | Filed |
| Queue bind drift detected (7/9 brain) | **Rebuilt** `healthy-queue-30-active.json` |
| Mac Health E2E | PASS · 93 Excellent |
| This near-miss doc | **This file** |

---

## 3. Brain law (mandatory wording)

| Say | Never say alone |
|-----|-----------------|
| **Worker Hub** → `http://127.0.0.1:13020/` | "Sina Command is the hub" |
| **Old Hub (read-only)** → `/legacy/` (ship: `/oldhubsinacommand/`) | "archived" without URL |
| **Machine Hub** → `/machines/` | "the hub" |
| **Heart** → `http://127.0.0.1:13024/` | Mac health from chat memory |

**Archive definition:** Frozen monolith route — **not** deleted · **not** daily default.

---

## 4. Hardening (Maintainer ship)

1. Route `/oldhubsinacommand/` → same as `/legacy/`
2. READ ONLY banner on monolith HTML
3. H1 one-tap: "Old Hub Sina Command (read-only)"
4. Validator: forbid Brain closeout saying "archive" without `legacy_url` field

---

## 5. Line test (repeat)

Would founder find old hub from Brain words alone? **Before: NO. After this doc: YES** — use `/legacy/` until alias ships.

**LOCKED near-miss — do not repeat M1–M4.**
