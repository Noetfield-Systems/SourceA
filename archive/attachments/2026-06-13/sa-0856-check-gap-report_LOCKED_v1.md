# sa-0856 CHECK — Cross-check SINA_COMMAND_NO_TERMINAL_FOUNDER law in hub copy

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T23:30Z · **Turn:** CHECK · **Worker:** SourceA  
**Tier:** T2 (duplicate: sa-0806 T0 · sa-0830 T1 · sa-0881 T3)

## Task (read-only)

Cross-check **SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md** against founder-visible **hub copy** (Worker Hub + legacy panel payloads).

## Law summary

Founder must **never** be asked to open Terminal or run `bash` / `python3` / `curl`. Agents run shell or ship **one-tap Actions**.

## Hub surfaces scanned

| Surface | Scope | Law alignment |
|---------|-------|---------------|
| **Legacy** `app.js` | Nav, site guide, agent loop, essentials render | **Mostly aligned** — 6× "no Terminal" copy |
| **Worker Hub** `/` | Policy links via API | **Aligned** — `no-terminal` policy row |
| **command-data** `hub_essentials` | Essentials tab payload | **VIOLATION** — see GAP-2 |
| **Site guide API** | `POST /api/site-guide` terminal query | **Aligned** — one-tap answer |
| **ASF founder docs** | `founder/ASF_*.md` | **PASS** — `validate-founder-docs-no-terminal-v1` |

## Live disk (CHECK 2026-06-13)

| Piece | Status |
|-------|--------|
| Law on disk | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` |
| `hub_essentials` read chain | includes No Terminal law (L23 hub_essentials_index.py) |
| `app.js` positive copy | Site guide banner · Actions desc · agent loop cards |
| `app.js` forbidden instruct | **0** hits (open Terminal / copy command / shell fences) |
| Worker Hub policy API | `no-terminal` → law path |
| `validate-founder-docs-no-terminal-v1` | **PASS** (ASF markdown only) |
| `validate-hub-copy-no-terminal-v1` | **absent** |

## Violation found (hub copy)

**Essentials tab → Noetfield unified guide → "Mac founder (one-time refresh)"** renders shell commands to founder:

| Label | Rendered hint (forbidden) |
|-------|---------------------------|
| Sync SourceA → Noetfield mirror | `cd ~/Desktop/Noetfield && ./scripts/sync-sourceA-desktop.sh` |
| Rebuild agent notices | `cd ~/Desktop/SourceA && python3 scripts/build_repo_agent_notices.py` |
| Start hub | `~/Desktop/SourceA/scripts/serve-sina-command.sh` |

Source: `scripts/noetfield_unified_guide.py` `mac_actions` → `renderNoetfieldUnifiedGuide()` in `app.js` (Essentials tab).

## Partial coverage (existing)

| Validator | Covers |
|-----------|--------|
| `validate-founder-docs-no-terminal-v1.sh` | `founder/ASF_*.md` only — **not hub UI/payload** |
| `site_guide.py` canned answer | Runtime terminal Q — not disk gate |
| `worker_hub_v1.py` policy link | Worker Hub law row — not legacy Essentials |

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix |
|----|-----|----------|---------|
| **GAP-1** | No sa-0856 hub-copy cross-check validator | **high** | `validate-hub-copy-no-terminal-v1.sh` |
| **GAP-2** | `noetfield_guide.mac_actions` shows shell in Essentials | **high** | Replace hints with one-tap Actions copy **or** move to maintainer-only block |
| **GAP-3** | `validate-founder-docs-no-terminal-v1` scope too narrow | medium | Chain from hub-copy validator |
| **GAP-4** | Worker Hub static HTML has no explicit no-Terminal banner | informational | Policy link via API is sufficient |
| **GAP-5** | Duplicate sa-0806/sa-0830/sa-0880 | low | One validator + mac_actions fix closes chain |

## Recommended ACT (minimal)

1. Ship `validate-hub-copy-no-terminal-v1.sh`:
   - Law file exists + in `hub_essentials` read chain
   - `app.js` has positive no-Terminal copy (min count)
   - `app.js` / `command-data` hub_essentials: **no** founder-visible `cd`/`bash`/`python3` hints
   - Worker Hub policy includes `no-terminal` link
   - Chain `validate-founder-docs-no-terminal-v1.sh`
2. Fix `noetfield_unified_guide.py` `mac_actions` — one-tap wording (e.g. "Actions → Rebuild notices") **or** drop founder-visible shell block
3. **No** broad `app.js` rewrite unless validator fails on positives

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| validate-founder-docs-no-terminal-v1 | PASS |
| worker_verify_fast_v1 | PASS (L1) |
| Site guide API (terminal Q) | PASS — one-tap answer |
| Worker Hub policy `no-terminal` | PASS |

## Verdict

**CHECK complete** — law is **wired in most hub copy** but **Essentials Noetfield mac_actions violates founder law**; gap = **hub-copy validator + mac_actions heal**. **STOP** — no implement · no closeout.

*End sa-0856 CHECK*
