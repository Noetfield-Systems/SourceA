# Founder law — no Terminal (locked)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## What it means (plain)

**Do not ask the founder to open Terminal or run a command** (`bash`, `python3`, `curl`, `tailscale status`, etc.).

If work needs a shell command, **agents** must either:

1. **Run it themselves** (executor / API / background), or  
2. **Ship a one-tap control in Sina Command** in the right place for that product.

“No Terminal” is not “never use computers” — it means **the founder only taps buttons in the app**, never copies shell from chat.

## Where to put one-tap controls

| Need | Put the button/link here |
|------|---------------------------|
| Repo-specific check (TrustField DB, VIRLUX DNS, wire G3) | **Actions** tab — one tap per command |
| Multi-step Cursor work | **Private agents** (sidebar) → that agent's page — Start / Submit round |
| Copy a lane prompt | **Repos** → **Copy lane brief** |
| Open a live URL | **Live products** or **Actions** → Open … |
| “What is P0 / Submit round?” | **Home** → **Ask** |

## Example (TrustField chat)

**Wrong (forbidden):**  
“Open Terminal and run `tailscale status`, then paste the output here.”

**Right:**

- TrustField agent runs the check itself, **or**
- TrustField agent files **Backlog → Agent report**: “Need Actions button: G3 Tailscale check”
- **SinaaiDataBase maintainer chat** adds **Actions → Run G3 Tailscale check** (one tap)
- Founder taps that button — **no Terminal**

Same pattern for deploy, ingest, refresh, pack activate, health checks.

## Never ask founder to Refresh (agent law)

Hub **auto-syncs** every 15–45s (`/api/hub-sync`, Goal 1 loop status). Agents run `scripts/hub_self_refresh_v1.py` — **never** tell ASF “refresh the hub” or “hard-refresh”.

Gold **Refresh** remains for founder if they want — agents must not depend on it.

## Founder allowed clicks

| Action | Where |
|--------|--------|
| Refresh hub (optional) | Gold **Refresh** — hub also auto-syncs |
| Agent loop | **Private agents** → agent page — 10 prompts, Start, **Submit round**, Stop |
| Repo / wire ops | **Actions** tab |
| Help | **Search** / **Ask** on Home |
| Report app bugs | **Backlog** → Agent reports |

## Forbidden for founder

- Copying any command into Terminal from Cursor chat or docs
- `python3`, `bash`, `curl`, `agent-loop-done.sh`, `activate-portfolio-loop.py`

## Who edits Sina Command (adds new buttons)

- **ASF** (you)
- **SinaaiDataBase** Cursor chat only  

All other chats: **Backlog → Agent reports** or `POST /api/agent-review` — do not edit `~/Desktop/SourceA/`.

See `SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md`.
