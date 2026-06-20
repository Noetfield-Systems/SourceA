# Paste into Noetfield cloud Cursor chat — acknowledge & correct

**Copy everything below the line into the Noetfield (`~/Desktop/Noetfield`) chat only.**

---

```
FOUNDER CORRECTION + ACKNOWLEDGMENT — Noetfield cloud chat (noetfield_cloud)

You are in the **Noetfield cloud / GitHub ship** workspace (`~/Desktop/Noetfield`).
You are **not** in Noetfield-All-Documents, SourceA, wire, MergePack, or Cursor OS Pro.

## Acknowledge (what you got RIGHT)

1. Cloud agents need an **in-repo entry path** without founder Mac hub — correct.
2. Committed ops docs (`docs/ops/…`) + `os/plan.json` / `os/SHIP_NOW.md` are the right ship SSOT in git.
3. **Do not** commit full `~/Desktop/SourceA` or `ops/private/sourceA/` — correct.
4. **Mac hub** `http://127.0.0.1:13020/` is founder loopback only — cloud must not depend on it.
5. Split **local docs** vs **cloud ship** is correct — two agent ids, two folders.

## Correct (what was WRONG or drift — fix your model)

| Wrong | Right |
|-------|--------|
| Primary paste `ready_to_paste_noetfield.txt` | **`ready_to_paste_noetfield_cloud.txt`** (this chat only) |
| Primary notice `REPO_NOTICE_noetfield_v1.md` | **`SEMI_NOTICE_noetfield_cloud_v1.md`** (semi-separate ship lane) |
| `REPO_NOTICE_noetfield` = this chat | That notice is **noetfield_local** (All-Documents) only |
| Root `AGENT_READ_LINKS_INDEX.md` as new git SSOT | **Canonical** index: `~/Desktop/SourceA/founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md` — in-repo use **`docs/ops/AGENT_READ_LINKS_LOCKED_v1.md`** (mirror, § Cloud ship) |
| Add duplicate `docs/agent/` tree | **One path:** `docs/ops/` only — do not fork read-order docs |
| Copy index **from repo → SourceA** | **Wrong direction.** Mac: SourceA → `./scripts/sync-sourceA-desktop.sh` → `ops/private/sourceA/` (gitignored) |
| Hub URLs required in cloud VM | **Optional** on Mac; cloud uses git + sync mirror after founder runs sync |
| “Smarter cloud = hub” | Smarter = read **locked order in this repo** + ship `os/plan.json` |

## SSOT layers (memorize)

- **Layer A (git):** This repo — code, `docs/ops/*_LOCKED.md`, `os/plan.json`, `os/SHIP_NOW.md`
- **Layer B (Mac gitignored):** `ops/private/sourceA/` after founder runs `sync-sourceA-desktop.sh`
- **Layer C (Mac):** `~/Desktop/SourceA/` + Sina Command Essentials → **Noetfield lanes** card

**Never** treat git copy as newer than SourceA.

## Your read order THIS session (cloud ship)

1. `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` → **§ Cloud ship** only
2. `docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md`
3. `docs/ops/NOETFIELD_CLOUD_AGENT_ENTRY_POINTER_LOCKED_v1.md` (if present)
4. `os/SHIP_NOW.md` → `os/plan.json` (lane_a_sprint_map)
5. After founder sync: `ops/private/sourceA/founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md`

Unified law on founder Mac / hub UI: `NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md` (Essentials tab).

## Forbidden in this chat

- Edit `~/Desktop/Noetfield-All-Documents`
- Edit `~/Desktop/SourceA` or `~/Desktop/SinaPromptOS` (ingest/dispatch)
- Portfolio tasks from trustfield / mono / virlux / 777 as primary work
- Wait idle for “next Prompt OS order” — **ship from os/plan.json**

## This week (one verifiable outcome)

Pick **one** item from `os/plan.json` lane_a_sprint_map or `os/sprint-trust-ledger-v1.2.md`, implement in **this repo**, run `scripts/verify-local-dev.sh` or `scripts/tle-smoke.sh`, report evidence paths.

## Reply format (required)

Line 1: `Active thread: THREAD-PORTFOLIO`
Line 2: One primary outcome for this session only
Then:
- **ACK** — bullet list confirming corrections above
- **READ** — which files you opened (paths)
- **DONE / PARTIAL / BLOCKED** — with evidence
- **VERIFY** — per AGENT_OUTPUT_CONTRACT (after sync mirror if on cloud)
- **NEXT** — single next action for founder (no Terminal — Actions/hub on Mac)

Confirm you will not treat hub :13020 or Desktop paths as available unless founder confirms Mac session.
```

---

**File:** paste from `~/Desktop/SinaPromptOS/outputs/ready_to_paste/ready_to_paste_noetfield_cloud.txt` after rebuild, or hub **Repos** → lane brief for `noetfield_cloud`.
