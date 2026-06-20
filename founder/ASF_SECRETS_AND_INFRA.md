# Secrets + infra — ASF reference (hub taps)

## Vault (maintainer runs — not agents in chat, not ASF Terminal)

| Step | Who |
|------|-----|
| Create `~/.sina/secrets.env` locally | **ASF** (one-time setup per `SECRETS_VAULT.md`) |
| Sync vault to repos | **Maintainer** runs `vault-sync-all.sh` in SinaPromptOS |

**Never paste API keys in Cursor chat.**

Doc: `SourceA/SECRETS_VAULT.md`  
Rule: `SourceA/FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md`

---

## TrustField free path (maintainer)

Maintainer or TrustField agent runs:

- `founder_free_auto.sh`
- `founder_free_verify.sh`

in `~/Desktop/TrustField Technologies` — uses `.env.founder` (Cloudflare token + zone).

Founder: hub **Actions** when wired — not Terminal.

---

## Ports law

| Port | Use |
|------|-----|
| **3004+** | DevBridge desk |
| **8766** | DevBridge agent WS |
| **8000** | Mono SinaaiRuntime spine |
| 3000–3003 | **Blocked** for DevBridge |

`SourceA/PORT_NOTICE_BOARD.md`

---

## Tailscale (G3)

Install on Mac + iPhone → maintainer runs `proof:g3` → `record:g3` with phone Run ID.

---

## When deploy fails

1. Hub **Refresh** — check blockers
2. **Backlog** → Agent reports
3. Check blocker doc in that repo `docs/`
4. Logs: `SourceA/REPO_EXECUTION_LOGS/<repo>/`

Do **not** stop wire work for unrelated repo deploy.
