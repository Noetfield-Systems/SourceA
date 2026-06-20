# Run inbox disk truth execution (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**2026-06-10** · ASF order

## Two lanes (never mix)

| Lane | Role | Machine? |
|------|------|----------|
| **Next steps** | **Live mirror** · next 10 queue turns from disk | Display + optional founder override · **not execution gate** |
| **run inbox** | Execution · one CHECK→ACT→VERIFY turn | **100% disk truth** in INBOX |

## Law

1. Founder says **`run inbox`** → machine runs `run_inbox_disk_truth_v1.py --gate-pickup`.
2. INBOX prompt **must** start with **DISK TRUTH** block (queue pos, honest count, factory, phase-strict).
3. If INBOX stale vs queue cursor → **auto-redeliver** (no agent).
4. Monitor `:13021` = read-only truth display (5s disk wire).
5. Super Fast Hub **Next steps** **Confirm** is optional stamp only — does **not** replace run inbox or block delivery.
6. Live next-10 list: `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md` · `~/.sina/live-ongoing-prompts-next-10-v1.json`

## SSOT files

- `~/.sina/run-inbox-disk-truth-v1.json`
- `~/.sina/execution-lane-v1.json`
- `~/.sina/monitor-live-v1.json`
- `~/.sina/live-ongoing-prompts-next-10-v1.json`

## Validator

`bash scripts/validate-run-inbox-disk-truth-v1.sh`
