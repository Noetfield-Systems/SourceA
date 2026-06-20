# sa-0955 — L0-full Cursor MCP editor telemetry (defer per phase 6)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules · No OpenRouter**

## Factory today (disk truth)

| Layer | SourceA state |
|-------|----------------|
| **L0 MVP** | `pre_llm/user_signals/` · hub touch → `~/.sina/user_signals_v1.json` + `workspace_state_v1.json` |
| **L0-full target** | Editor `open_files` + session focus in packet slice (`packet_workspace_slice`) |
| **WTM pendings** | L0-full **partial** — hub workspace POST only (`SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` §6) |
| **Disk now** | `open_files: []` · signals from hub tab POST — not live Cursor IDE feed |

## L0-full vs what exists

| Signal | L0-full (industry / WTM) | SourceA today | Gap |
|--------|--------------------------|---------------|-----|
| **open_files** | IDE reports active buffers | `record_workspace_files()` exists; **no producer** | Cursor does not POST open tabs to hub |
| **Keystroke / cursor** | Optional L0-full depth | **Not in scope** MVP | Correctly excluded — phase 6 defer |
| **MCP bridge** | MCP tool could emit workspace snapshot | MCP servers (Notion, Figma, Supabase…) **read-only to factory** | No `L0-telemetry` MCP → `user_signals` wire |
| **Packet injection** | `active_files` in context assembly | `packet_workspace_slice()` ready | Empty until IDE hook ships |

## Phase 6 defer (law-aligned)

Per `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` · P2 L0-full editor telemetry:

- **Now:** L0 MVP done — hub Refresh / workspace POST sustains slice
- **Phase 6:** Deepen editor hooks — **not** current strategic slice gate
- **ACT rule:** Research note only — **no new D-modules** until ASF orders L0-full build

## Integration sketch (research — not built)

1. Cursor extension or MCP server → `POST /api/user-workspace-signals-v1` with `open_files[]`
2. Reuse `record_workspace_files()` in `pre_llm/user_signals/store.py` — no schema change
3. Validator: `validate-user-workspace-signals-v1.sh` green when `open_files` non-empty in CI fixture
4. Founder law preserved — one-tap hub Actions for manual workspace snapshot until IDE hook

## Verdict

**Defer L0-full MCP editor telemetry to phase 6.** Factory has L0 MVP + packet slice hook; missing piece is **Cursor→hub producer**, not pre-LLM schema.

**One-line:** L0-full is **partial by design** — research debt documented; dispatch/eval spine not blocked.
