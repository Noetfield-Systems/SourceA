# Founder rule — NO credit card / FREE infra only (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**sequence_id:** SA-2026-06-02-017  
**Locked:** 2026-06-02  
**Authority:** ASF concrete rule — overrides any doc that pushes paid Postgres/Redis or “upgrade plan”

---

## 1. The rule (non-negotiable)

| Allowed | Forbidden |
|---------|-----------|
| Free-tier clouds (Vercel Hobby, Render **free web** + SQLite, Cloudflare free DNS, Railway free where already used, Supabase/Neon free tiers) | **Credit card** on any provider for “API key” or “Starter upgrade” |
| Free APIs (Cloudflare token, Telegram, OpenRouter `:free` models, GitHub) | Render **paid** Postgres + Redis (“Starter” DB attach) |
| Automation via `founder_free_auto.sh` | `founder_infra_full_auto.sh` **commercial** path unless ASF explicitly opts in after revenue |
| `PHASE1_LIGHT=true` production | Forcing `PHASE1_LIGHT=false` + Postgres + Redis to pass gates |

**If Render demands a card for API keys → do not use Render API.** Use GitHub → Render auto-deploy (dashboard connect once, no card on API) + Cloudflare API only.

---

## 2. TrustField canonical stack (free)

```text
www.trustfield.ca     → Vercel (free)
API                   → Render free web service (Docker), SQLite, in-memory limits
api.trustfield.ca     → Cloudflare CNAME (CF_API_TOKEN — free)
Telegram              → existing bot + webhook
Verify                → ./scripts/founder_free_verify.sh  (PASS = success)
```

**Deferred until revenue:** `render.yaml` Postgres + Redis commercial blueprint.

---

## 3. Commands (use these)

```bash
cd ~/Desktop/TrustField\ Technologies
./scripts/founder_free_auto.sh          # DEFAULT automation
./scripts/founder_free_verify.sh        # PASS/FAIL for free tier
```

**Do not run** for daily ops:

- `founder_infra_full_auto.sh` (commercial)
- `founder_post_deploy_verify.sh` when it requires postgres/redis
- Dashboard “upgrade plan” on Render databases

---

## 4. Secrets vault (`~/.sina/secrets.env`)

| Key | Free path |
|-----|-----------|
| `CF_API_TOKEN` | **Yes** — DNS automation |
| `CF_ZONE_ID` | **Yes** (or auto-resolve in script) |
| `RENDER_API_KEY` | **No** — leave empty / remove |
| `M4_TELEGRAM_CHAT_ID` | Optional — morning digest |

---

## 5. Free cloud map (ecosystem)

| Project | Free stack already in use |
|---------|---------------------------|
| TrustField | Vercel + Render free web + CF |
| VIRLUX | Railway + Vercel (see `.env.staging`) |
| 777 / web | Vercel |
| SinaaiRuntime | Local / free LLM keys |
| Prompt OS | Local Python — no cloud bill |

**LLM policy:** OpenRouter / Groq / Gemini free tiers only unless ASF adds paid key deliberately.

---

## 6. What “PASS” means now

**Success =** `founder_free_verify.sh` exit 0:

- `ready=true`, `phase1_light=true`
- Render `/health` ok with **sqlite** (expected)
- Telegram inbound ok
- `api.trustfield.ca` optional WARN (DNS propagate)

**Not success:** commercial-readiness FAIL on missing Postgres — **ignore** for this phase.

---

## Document control

Subordinate to `SINA_OS_SSOT_LOCKED.md` for structure; **equal** to delivery freeze for infra spend.
