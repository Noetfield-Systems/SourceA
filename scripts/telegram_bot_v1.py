#!/usr/bin/env python3
"""SourceA Telegram Bot — phone control for the full automation system.

Commands:
  /status   — system health + current queue position
  /start    — start worker batch (5 turns, API mode if key set)
  /start10  — start worker batch (10 turns)
  /stop     — hard stop (stop_goal1_auto_run + stop receipt)
  /pause    — pause autorun (sets kill flag)
  /resume   — bounded resume only (factory_control token, max 1 turn)
  /log      — last 20 lines of batch log
  /cost     — total API spend today (from agent log)
  /help     — show all commands

Setup (one time):
  1. Message @BotFather on Telegram → /newbot → copy token
  2. Message your bot → /start → get your chat_id from bot logs
  3. export TELEGRAM_BOT_TOKEN=<token>
  4. export TELEGRAM_ALLOWED_CHAT_ID=<your_chat_id>  (security: only you can command it)
  5. pip install requests --break-system-packages
  6. python3 scripts/telegram_bot_v1.py

Run as daemon via launchd: scripts/com.sourcea.telegram-bot.plist

Requires:
  TELEGRAM_BOT_TOKEN env var
  TELEGRAM_ALLOWED_CHAT_ID env var (optional but strongly recommended)
  Hub running at http://127.0.0.1:13020 (for most actions)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
HUB = "http://127.0.0.1:13020"
LOG_PATH = Path.home() / ".sina" / "telegram-bot-v1.jsonl"
KILL_FLAG = Path.home() / ".sina" / "auto-run-disabled-v1.flag"
BATCH_LOG = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
AGENT_LOG = Path.home() / ".sina" / "claude-api-agent-v1.jsonl"

POLL_TIMEOUT = 30  # long-poll seconds


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(url: str, timeout: int = 5) -> dict:
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _post(url: str, body: dict, timeout: int = 30) -> dict:
    try:
        import urllib.request
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _hub_healthy() -> bool:
    return bool(_get(f"{HUB}/health").get("ok"))


# ── Telegram API ──────────────────────────────────────────────────────────────

def tg(method: str, **kwargs) -> dict:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN not set"}
    url = f"https://api.telegram.org/bot{token}/{method}"
    return _post(url, kwargs, timeout=35)


def send(chat_id: int | str, text: str, parse_mode: str = "HTML") -> dict:
    return tg("sendMessage", chat_id=chat_id, text=text, parse_mode=parse_mode)


def get_updates(offset: int = 0, timeout: int = POLL_TIMEOUT) -> dict:
    return tg("getUpdates", offset=offset, timeout=timeout)


# ── Command handlers ──────────────────────────────────────────────────────────

def cmd_status() -> str:
    hub_up = _hub_healthy()
    hub_icon = "🟢" if hub_up else "🔴"

    # Queue position
    queue_info = ""
    if hub_up:
        loop = _get(f"{HUB}/api/goal1-auto-run-status")
        pos = loop.get("queue_pos") or loop.get("next_pos") or "?"
        total = loop.get("queue_total") or "?"
        sa = loop.get("sa_id") or "?"
        role = loop.get("queue_role") or "?"
        queue_info = f"\n📋 Queue: {pos}/{total} · {sa} ({role})"

    # Autorun flag
    paused = KILL_FLAG.is_file()
    autorun = "⏸ PAUSED" if paused else "▶ ACTIVE"

    # Batch busy?
    lock = Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json"
    batch_running = ""
    if lock.is_file():
        try:
            ldata = json.loads(lock.read_text())
            pid = int(ldata.get("pid") or 0)
            if pid:
                try:
                    os.kill(pid, 0)
                    batch_running = f"\n⚙️ Batch running (pid {pid})"
                except OSError:
                    pass
        except Exception:
            pass

    # API mode?
    api_mode = "🤖 API mode" if os.environ.get("ANTHROPIC_API_KEY") else "🖥 Cursor mode"

    return (
        f"<b>SourceA Status</b>\n"
        f"{hub_icon} Hub: {'UP' if hub_up else 'DOWN'} · {api_mode}\n"
        f"🔄 Autorun: {autorun}"
        f"{queue_info}"
        f"{batch_running}"
    )


def cmd_start(batch_size: int = 5) -> str:
    if not _hub_healthy():
        # Hub down — try to start it
        subprocess.Popen(
            ["bash", str(SCRIPTS / "serve-sina-command.sh")],
            cwd=str(ROOT),
            start_new_session=True,
        )
        time.sleep(3)
        if not _hub_healthy():
            return "❌ Hub is down and restart failed. Check logs."

    result = _post(f"{HUB}/api/run-goal1-batch", {"batch_size": batch_size, "max_batches": 6})
    if result.get("ok"):
        pid = result.get("pid") or "?"
        return f"✅ Worker batch started (size={batch_size}, pid={pid})\nAutorun active — check /status for progress."
    else:
        err = result.get("message") or result.get("error") or "unknown error"
        return f"❌ Batch start failed: {err}"


def cmd_stop() -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "stop_goal1_auto_run_v1.py"), "--note", "telegram_stop", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )
    try:
        row = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        row = {"ok": False, "raw": (proc.stdout or "")[:400]}
    receipt = (row.get("stop_receipt") or {}).get("ok")
    msg = row.get("message") or "Stop script finished"
    if row.get("ok") and receipt:
        return f"🛑 STOP complete.\n{msg}\nFREEZE — bounded resume: ASF token via factory_control only."
    if row.get("ok"):
        return f"🛑 STOP complete.\n{msg}"
    err = (proc.stderr or row.get("raw") or "stop failed")[:300]
    return f"⚠️ Stop script error: {err}"


def cmd_pause() -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "stop_goal1_auto_run_v1.py"), "--note", "telegram_pause", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )
    if proc.returncode == 0:
        return "⏸ FREEZE — stop receipt written. Use /resume only with ASF bounded token (max 1 turn)."
    return "⏸ Pause requested — check /status"


def cmd_resume() -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "founder_resume_drain_v1.py"), "--max-turns", "1", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        row = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        return "❌ Resume failed — invalid response from factory_control"
    if row.get("ok"):
        return "▶ Bounded resume token issued (max 1 turn). Run one manual inbox turn — not batch autodrain."
    return "❌ Resume blocked — ASF: Cloud Forge Run — max 1 — receipt required"


def cmd_log() -> str:
    if not BATCH_LOG.is_file():
        return "📄 No batch log found yet."
    try:
        lines = BATCH_LOG.read_text(encoding="utf-8").splitlines()
        tail = lines[-20:] if len(lines) > 20 else lines
        text = "\n".join(tail)
        return f"<pre>{_esc(text[-3000:])}</pre>"
    except OSError as exc:
        return f"❌ Could not read log: {exc}"


def cmd_cost() -> str:
    if not AGENT_LOG.is_file():
        return "💰 No API agent log yet (API mode not used today)."
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT")
    total_cost = 0.0
    total_tokens_in = 0
    total_tokens_out = 0
    turns = 0
    try:
        for line in AGENT_LOG.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if row.get("at", "").startswith(today) and row.get("event") == "AGENT_DONE":
                    total_cost += float(row.get("cost_usd") or 0)
                    total_tokens_in += int(row.get("tokens_in") or 0)
                    total_tokens_out += int(row.get("tokens_out") or 0)
                    turns += 1
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
    except OSError:
        pass
    return (
        f"💰 <b>API cost today</b>\n"
        f"Turns: {turns}\n"
        f"In: {total_tokens_in:,} tokens\n"
        f"Out: {total_tokens_out:,} tokens\n"
        f"Total: <b>${total_cost:.4f}</b>"
    )


def cmd_help() -> str:
    return (
        "<b>SourceA Bot Commands</b>\n\n"
        "/status — system health + queue\n"
        "/start — start worker batch (5 turns)\n"
        "/start10 — start worker batch (10 turns)\n"
        "/pause — pause autorun (finish current batch)\n"
        "/resume — resume autorun\n"
        "/stop — ⚠️ emergency stop (kill everything)\n"
        "/log — last 20 lines of batch log\n"
        "/cost — API spend today\n"
        "/help — this message"
    )


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── Main loop ─────────────────────────────────────────────────────────────────

def handle_message(chat_id: int | str, text: str) -> str:
    text = (text or "").strip().lower().split()[0] if text.strip() else ""
    if text in ("/start", "start"):
        return cmd_start(batch_size=5)
    if text in ("/start10", "start10"):
        return cmd_start(batch_size=10)
    if text in ("/stop", "stop"):
        return cmd_stop()
    if text in ("/pause", "pause"):
        return cmd_pause()
    if text in ("/resume", "resume"):
        return cmd_resume()
    if text in ("/log", "log"):
        return cmd_log()
    if text in ("/cost", "cost"):
        return cmd_cost()
    if text in ("/status", "status", "/s"):
        return cmd_status()
    if text in ("/help", "help", "/?"):
        return cmd_help()
    return f"Unknown command: <code>{_esc(text)}</code>\nUse /help to see all commands."


def run_bot() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set. Export it in your shell or ~/.zshrc")
        sys.exit(1)

    allowed_id = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID", "")
    if not allowed_id:
        print("WARNING: TELEGRAM_ALLOWED_CHAT_ID not set — bot will respond to anyone!")

    print(f"[{_now()}] SourceA Telegram Bot started")
    _log({"event": "BOT_START", "allowed_chat_id": allowed_id or "any"})

    offset = 0
    while True:
        try:
            result = get_updates(offset=offset, timeout=POLL_TIMEOUT)
            if not result.get("ok"):
                time.sleep(5)
                continue

            for update in result.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message") or update.get("edited_message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                # Security gate
                if allowed_id and str(chat_id) != str(allowed_id):
                    _log({"event": "BLOCKED", "chat_id": chat_id, "text": text[:100]})
                    send(chat_id, "⛔ Not authorized.")
                    continue

                _log({"event": "MSG", "chat_id": chat_id, "text": text[:200]})
                print(f"[{_now()}] MSG from {chat_id}: {text[:80]}")

                reply = handle_message(chat_id, text)
                send(chat_id, reply)

        except KeyboardInterrupt:
            print(f"\n[{_now()}] Bot stopped.")
            _log({"event": "BOT_STOP"})
            break
        except Exception as exc:
            print(f"[{_now()}] ERROR: {exc}")
            _log({"event": "BOT_ERROR", "error": str(exc)})
            time.sleep(10)


def get_my_chat_id() -> None:
    """Helper: send /start to your bot, then run this to find your chat_id."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("Set TELEGRAM_BOT_TOKEN first")
        return
    result = get_updates(offset=0, timeout=5)
    updates = result.get("result", [])
    if not updates:
        print("No updates yet — send /start to your bot first, then re-run.")
        return
    for u in updates[-5:]:
        msg = u.get("message") or {}
        chat = msg.get("chat") or {}
        print(f"chat_id={chat.get('id')} username={chat.get('username')} text={msg.get('text','')[:40]}")


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="SourceA Telegram Bot — phone control")
    p.add_argument("--get-chat-id", action="store_true", help="Print recent chat IDs (after /start to bot)")
    p.add_argument("--test", action="store_true", help="Send a test status message and exit")
    p.add_argument("--install-deps", action="store_true", help="Install requests (not needed — uses urllib)")
    args = p.parse_args()

    if args.get_chat_id:
        get_my_chat_id()
        return 0

    if args.test:
        allowed_id = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID", "")
        if not allowed_id:
            print("Set TELEGRAM_ALLOWED_CHAT_ID to test")
            return 1
        reply = cmd_status()
        result = send(allowed_id, reply)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    run_bot()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
