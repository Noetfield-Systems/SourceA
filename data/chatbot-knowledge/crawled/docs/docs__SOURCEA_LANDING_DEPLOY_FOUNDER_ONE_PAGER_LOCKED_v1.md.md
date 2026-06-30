---
lane: core
updated: 2026-06-30T08:50:46Z
source_path: docs/SOURCEA_LANDING_DEPLOY_FOUNDER_ONE_PAGER_LOCKED_v1.md
public: true
---

# SourceA landing deploy — founder one-pager

**Version:** v1.0.0 LOCKED  
**Saved at:** 2026-06-24T01:30:00Z  
**STAB:** STAB-014 · STAB-015  
**Receipt:** `~/.sina/sourcea-landing-publish-receipt-v1.json`

---

## One law

> **Disk merge → live sourcea.app within 24 hours.** If visitors see stale hero or poison URLs, nothing else counts as shipped.

---

## Single deploy command (Cloudflare Pages + custom domain)

Run from `[REDACTED]`:

```bash
cd [REDACTED]
PYTHONPATH=packages/sourcea-boot/src python3 scripts/inject_sourcea_boot_terminal_v1.py
python3 scripts/publish_sourcea_landing_v1.py \
  --backend cloudflare \
  --project sourcea-com \
  --custom-domain \
  --skip-recipe
```

**Only if proxy worker changed:**

```bash
cd [REDACTED]/cloud/workers/sourcea-app-proxy-v1
npx wrangler deploy
```

---

## Verify (≤90s — no validator marathon)

```bash
curl -sL https://sourcea.app/sourcea/ | grep -c "Run your agentic startup"
curl -sL https://sourcea.app/sourcea/data/boot-proof.json | python3 -c "import sys,json; print(json.load(sys.stdin)['verdict'])"
curl -sL https://sourcea.app/sourcea/ | grep -cE 'sourcea\.com|hello@sourcea\.com'   # expect 0
curl -sI https://sourcea.app/sourcea/ | grep x-sourcea-origin   # pages-green-unified
```

---

## Architecture (do not regress)

| Layer | Path |
|-------|------|
| Source HTML | `sites/SourceA-landing/green-unified/` |
| Build dist | `python3 scripts/build_sourcea_vercel_output_v1.py` |
| Publish stages | **always** `green-unified/dist` (not `~/Desktop/agentrun-app`) |
| Pages project | `sourcea-com` |
| Custom domain | `sourcea.app` + `www.sourcea.app` |
| Edge proxy | `cloud/workers/sourcea-app-proxy-v1` → Pages |

---

## 24h deploy rule (STAB-015)

1. Landing or forge HTML merge → run inject + publish **same day**.
2. Proxy or `_redirects` change → wrangler deploy + publish if dist changed.
3. Receipt must show `boot_verdict: PASS` in staging.
4. If verify step 403 on `*.pages.dev`, check **custom domain** — that is the public truth.

---

## Chat Unify bundle (after app UI change)

```bash
bash scripts/sync-chat-unify-bundle-v1.sh
bash scripts/chat-unify-stack-boot.sh
```

Cmd+Q → reopen **Chat Unify.app** on Desktop.

---

## Download artifact (P1)

```bash
bash scripts/build-chat-unify-standalone-app-v1.sh
bash scripts/publish_chat_unify_dmg_v1.sh
# then re-run landing publish so /downloads/ is live
```
