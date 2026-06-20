"""Canonical founder law copy — one source for UI, planner, site guide, docs."""

# One-line (nav / badges)
FOUNDER_LAW_SHORT = (
    "Never ask the founder to run Terminal — give a one-tap button in Sina Command instead"
)

# Agent loop banner (2–3 sentences)
FOUNDER_LAW_UI = (
    "Do not tell the founder to open Terminal or paste shell commands. "
    "If something needs a command (checks, deploy, tailscale, python), either run it yourself (executor) "
    "or add a one-tap control in the right Sina Command tab: Actions (repo ops), Private agents page (10-round loop), "
    "Repos (lane briefs), Live products (URLs). Example: TrustField needs Tailscale proof → "
    "maintainer adds Actions → “Run G3 check”, not “run tailscale status in Terminal”."
)

# Planner / executing agent system text
FOUNDER_LAW_AGENT = (
    "Founder law: NEVER instruct the founder to use Terminal, bash, curl, or python3. "
    "When a step would require a shell command, you MUST (a) run it as executor yourself, OR "
    "(b) request a one-tap Action/link in Sina Command (Actions for repo ops, Private agents sidebar page "
    "for multi-round work, Repos for lane brief). Portfolio agents (TrustField, VIRLUX, etc.) "
    "file agent-review if they need a new button — only SinaaiDataBase chat + ASF edit the app. "
    "Governance matrix: AGENT_GOVERNANCE_INDEX_LOCKED_v1.md — each agent has forbidden_roots on its Private agents page."
)


def founder_law_payload() -> dict:
    return {
        "founder_law": FOUNDER_LAW_SHORT,
        "founder_law_detail": FOUNDER_LAW_UI,
        "founder_law_agent": FOUNDER_LAW_AGENT,
    }
