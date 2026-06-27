# Chat Unify founder smoke — Verify & Act (STAB-043)

**Saved at:** 2026-06-24T01:40:00Z  
**Time:** ≤10 minutes · **Browser:** Safari (not Cursor embedded browser — STAB-037)

## Steps

1. Open **Chat Unify.app** (or http://127.0.0.1:13023/ in Safari).
2. Home → click **Verify & Act** card (or tab).
3. Paste a short founder intent in the input.
4. Run pipeline — watch 7 steps complete.
5. Confirm receipt path shown in UI or `~/.sina/` grep `founder_loop`.

**If offline:** run `bash scripts/chat-unify-stack-boot.sh` or install LaunchAgent: `bash scripts/install-chat-unify-launchagent-v1.sh`

## Pass

- All 7 steps green or honest BLOCK with reason
- Receipt JSON logged
