# sourcea-founder-gates-v1

Daily founder interrupt surface for SourceA executive runs.

- **Primary UI (v3):** `/gates` — pulse · filters · governor terminal badges · last E2E strip
- **E2E:** `POST /v1/e2e/run` (Bearer `GATES_SIGNING_SECRET`) · `GET /v1/e2e/last`
- **Events:** `GET /v1/events`
- **Telegram:** mint / callback / **webhook** (`/v1/telegram/webhook`)
- **Governor wire:** resolve → `founder.gate.resolved` → **ACCEPTED** observe-only
- **ASK** keeps gate OPEN · **Red** DEFER only

```bash
bash scripts/sourcea_founder_gates_e2e_v1.sh
```

Live: https://sourcea-founder-gates-v1.sina-kazemnezhad-ca.workers.dev/gates

Law: Canvas proposes. Git defines. CI validates. Supabase activates. n8n orchestrates. Cockpit interrupts.

Never writes Goal Contracts, DecisionRecords, or canonical memory.
