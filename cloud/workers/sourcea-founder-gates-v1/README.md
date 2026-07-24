# sourcea-founder-gates-v1

Daily founder interrupt surface for SourceA executive runs.

- **Primary UI (v2):** `/gates` — pulse strip · Open/Resolved/All · Approve / Reject / Defer / Ask
- **Pulse:** `/v1/pulse` (read-only; includes `resolved_count`)
- **List filter:** `GET /v1/gates?status=OPEN|RESOLVED`
- **Amber Telegram:** signed callback packets (expiry, nonce, idempotency)
- **Red:** view / defer only
- **Governor wire:** on resolve → `POST {SOURCEA_GOVERNOR_URL}/v1/executive/runs?org=sourcea` (`founder.gate.resolved`)

Secrets: `GATES_SIGNING_SECRET` · `TELEGRAM_BOT_TOKEN` · `TELEGRAM_CHAT_ID_AMBER` · `TELEGRAM_CHAT_ID_RED`  
Chat IDs follow `data/telegram-routing-ssot-v1.json` (`TELEGRAM_OPS_CHAT_ID`).

Law: Canvas proposes. Git defines. CI validates. Supabase activates. n8n orchestrates. Cockpit interrupts.

Never writes Goal Contracts, DecisionRecords, or canonical memory.

Live: https://sourcea-founder-gates-v1.sina-kazemnezhad-ca.workers.dev/gates
