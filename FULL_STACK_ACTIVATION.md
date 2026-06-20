# Full Stack Activation — Brain/Worker Run This Once

## What was built
- `scripts/claude_api_agent_v1.py` — headless Claude API worker (no Cursor needed)
- `scripts/goal1_worker_batch_loop_v1.py` — updated: uses API mode when `ANTHROPIC_API_KEY` is set
- `scripts/telegram_bot_v1.py` — phone control bot
- `scripts/com.sourcea.telegram-bot.plist` — launchd daemon for bot

---

## Step 1 — Install anthropic package (one time)

```bash
cd ~/Desktop/SourceA
python3 scripts/claude_api_agent_v1.py --install-deps
```

---

## Step 2 — Set ANTHROPIC_API_KEY

Add to `~/.zshrc`:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Then reload:
```bash
source ~/.zshrc
```

Verify:
```bash
python3 scripts/claude_api_agent_v1.py --dry-run
```

Expected output: `"dry_run": true, "sa_id": "sa-XXXX"`

---

## Step 3 — Test one API turn

```bash
python3 scripts/claude_api_agent_v1.py --role worker
```

This runs one real Worker turn via Claude API (no Cursor, no window focus).
Result saved to `~/.sina/api-agent-results/`

---

## Step 4 — Set up Telegram bot

### 4a. Get bot token
1. Open Telegram → message `@BotFather`
2. `/newbot` → name it `SourceA` → copy token

### 4b. Get your chat_id
1. Message your new bot: `/start`
2. Run: `TELEGRAM_BOT_TOKEN=<token> python3 scripts/telegram_bot_v1.py --get-chat-id`
3. Copy your `chat_id` from output

### 4c. Edit the plist with real values
Edit `scripts/com.sourcea.telegram-bot.plist`:
- Replace `PASTE_YOUR_BOT_TOKEN_HERE` with your token
- Replace `PASTE_YOUR_CHAT_ID_HERE` with your chat_id

### 4d. Install the launchd daemon
```bash
cp ~/Desktop/SourceA/scripts/com.sourcea.telegram-bot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.sourcea.telegram-bot.plist
```

### 4e. Test
```bash
TELEGRAM_BOT_TOKEN=<token> TELEGRAM_ALLOWED_CHAT_ID=<chat_id> python3 scripts/telegram_bot_v1.py --test
```

---

## Step 5 — Verify API mode batch

```bash
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY python3 scripts/goal1_worker_batch_loop_v1.py --batch-size 1 --max-batches 1
```

Should print: `BATCH MODE: Claude API (headless — no Cursor required)`

---

## Phone commands (via Telegram)

| Command   | Action |
|-----------|--------|
| /status   | system health + queue position |
| /start    | start worker batch (5 turns) |
| /start10  | start worker batch (10 turns) |
| /pause    | pause autorun |
| /resume   | resume autorun |
| /stop     | emergency stop (kill everything) |
| /log      | last 20 lines of batch log |
| /cost     | API spend today |

---

## Cost estimate

Claude Sonnet: $3/MTok in, $15/MTok out  
Each Worker turn ≈ 5k in + 2k out ≈ $0.045  
Full 30-task queue ≈ $1.35

---

## Architecture now

```
Phone (Telegram) → Bot → Hub :13020
                         ↓
                  claude_api_agent_v1.py
                         ↓
                  Anthropic API (claude-sonnet-4-6)
                         ↓
                  advance queue + broker submit
                         ↓
                  ~/.sina/api-agent-results/
```

No Cursor. No clipboard. No window focus. Works 24/7 from phone.
