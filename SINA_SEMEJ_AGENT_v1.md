# SEMEJ — multi-AI Chrome agent

**SEMEJ** chains your **signed-in** web AIs in Chrome: Gemini → ChatGPT → Perplexity → Grok → Claude (configurable).

## How it works (like Agent loop)

| Role | What |
|------|------|
| **SEMEJ** | Opens Chrome, pastes prompt into each chatbot |
| **Bridge** | OpenRouter rewrites the next prompt (“analyze Gemini’s answer for ChatGPT…”) |
| **Heal** | Retry, skip AI, or you **inject answer** manually |

Flow: **Idea** → AI₁ → answer → bridge → AI₂ → … → **artifact** (markdown in `~/.sina/semej-artifacts/`).

## One-time setup (no Terminal for daily use)

In **Sina Command → Actions**:

1. **Install SEMEJ browser tools** (Playwright)
2. **Start Chrome for SEMEJ** (remote debugging port 9222)
3. In that Chrome window, **sign in** to Gemini, ChatGPT, Perplexity, Grok, etc.

## Daily use

1. **Sina Command → SEMEJ**
2. Enter your **idea** → **Start SEMEJ**
3. Watch Chrome; if the app says **Paste answer**, copy from the tab and tap **Inject answer → next AI**

Manual inject (from Cursor or Terminal):

```bash
~/Desktop/SourceA/scripts/semej-inject-answer.sh "Full text of the AI reply"
```

## Config

Edit chain and selectors: `~/.sina/semej-providers.json`

## API

`POST /api/semej` — `start`, `response`, `cancel`, `status`, `capture_now`, `skip_provider`, `open_chrome`

---

*SEMEJ v1 — local only, your Chrome profile, your accounts.*
