# Site Pulse + Forms — founder setup

## 1. Founder dashboard (see feedback + analytics)

```bash
cd cloud/workers/sourcea-site-pulse-v1
npx wrangler secret put FOUNDER_PULSE_KEY   # pick a long random password — save in 1Password
npx wrangler deploy
```

Open https://sourcea.app/pulse-founder and paste the **same** key.

## 2. Email when strangers submit feedback or MVP intake

Get API key from https://resend.com/api-keys (you already have Resend).

```bash
# Feedback + site forms
cd cloud/workers/sourcea-site-pulse-v1
npx wrangler secret put RESEND_API_KEY

# 48h MVP intake at /start
cd ../sourcea-mvp-intake-v1
npx wrangler secret put RESEND_API_KEY
npx wrangler deploy
```

Emails go to `forge@sourcea.app` + `hello@sourcea.app` (feedback) and `hello@sourcea.app` (MVP intake).

## 3. Verify

```bash
curl -s "https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev/api/site/stats/v1" | jq .stats
```

Submit test feedback on sourcea.app → refresh pulse-founder inbox.
