# [AGENT-DIAG-2026-05-27] Clipboard hijack — paste becomes LAN URL + pairing PIN

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Tag:** `[AGENT-DIAG-2026-05-27]`  
**Author:** Cursor maintainer agent (this session)  
**Date:** 2026-05-27  
**Status:** FIXED in `Cursor OS Pro/packages/bridge/src/cli.ts`

---

## Symptom

Copying a Noetfield (local or cloud) lane prompt from Sina Command / `ready_to_paste_*.txt`, then pasting into Cursor chat, sometimes yields:

```
http://10.0.0.15:9479
644642
```

instead of the intended prompt text.

---

## Root cause (confirmed)

**Cursor OS Pro LAN bridge** (`npm run link` / `packages/bridge/src/cli.ts`) was calling `pbcopy` with:

1. On bridge start: `"{lanUrl}\n{pairCode}"`
2. Every `PAIR_CODE_TTL_MS` (10 min) on code rotation: same overwrite

That format matches the user report exactly (`http://10.0.0.15:9479` + 6-digit PIN). Port `9479` is the smoke/default override; `10.0.0.15` is the Mac LAN IP.

**Not** caused by:

- Noetfield repo paste files (`ready_to_paste_noetfield*.txt` — no URLs)
- SourceA hub `copyLaneBrief` / prompt queue (browser clipboard only on explicit button click)
- Auto-paste into Cursor (disabled per `SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`)

---

## Fix

| Change | Where |
|--------|--------|
| Clipboard copy **off by default** | `cli.ts` — no `pbcopy` unless `--copy-clipboard` or `CURSOR_OS_PRO_COPY_PAIRING=1` |
| **Removed** interval `pbcopy` on code rotation | `cli.ts` `setInterval` |
| Troubleshooting row | `Cursor OS Pro/README.md` |

---

## Founder / maintainer actions

1. If paste still shows URL+PIN: `cd ~/Desktop/Cursor\ OS\ Pro && npm run stop-bridge`
2. Re-copy lane brief from hub (**Repos → Copy lane brief**) or open `SinaPromptOS/outputs/ready_to_paste/ready_to_paste_noetfield.txt`
3. Paste into Cursor — should be full prompt text
4. Only when pairing iPhone: `npm run link -- --copy-clipboard` (one-shot; does not repeat every 10 min)

---

## Validation

```bash
# Bridge source must not pbcopy on interval
grep -n "copyMacClipboard" ~/Desktop/Cursor\ OS\ Pro/packages/bridge/src/cli.ts
# Expect: only inside startup block guarded by pairingClipboardEnabled

# Noetfield paste packs must not contain LAN bridge URLs
grep -r "10.0.0.15" ~/Desktop/SinaPromptOS/outputs/ready_to_paste/ready_to_paste_noetfield*.txt || echo OK
```

---

## Do not touch

Other agents' locked docs — this file is tagged `[AGENT-DIAG-2026-05-27]` only.
