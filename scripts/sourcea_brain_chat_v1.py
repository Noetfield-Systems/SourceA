#!/usr/bin/env python3
"""Public SourceA Brain chat — OpenRouter on cloud/hub only (never expose API key to browser)."""
from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import certifi

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
MAX_MESSAGE_LEN = 2000
MAX_HISTORY = 12
DEFAULT_MODEL = "google/gemini-2.5-flash"

BRAIN_PUBLIC_SYSTEM = """You are Brain on sourcea.app — a sharp, honest guide for strangers. Not a pushy sales bot.

ONE-LINE (when asked "what is SourceA?"):
SourceA is an AI execution platform powered by Forge — it runs real builds, automations, agent workflows, and controlled development pipelines for founders and agencies. Proof and receipts are built in; they are not the whole product.

WHAT SOURCEA IS NOT:
- Not "just records" or "just verification software"
- Not a generic ChatGPT wrapper

WHAT FORGE IS:
- Forge Terminal: the execution desk — living chat, workspace, agents, quality gate, cloud dispatch
- Public try (no install): /sourcea/forge/terminal
- Flow: idea → prompt forge → agents → quality gate → execute (Cursor / cloud)

CONVERSATION ORDER:
1) Their problem / what they want to accomplish
2) One concrete sentence on what SourceA + Forge does for that
3) ONE matched example (specific, not abstract)
4) Why this beats chat-only AI
5) Price or booking ONLY if they ask or value is clear

PRICING:
- NEVER open with dollar amounts
- If they ask: scope-dependent; typical controlled deploy setup is often in the $1,500–$5,000 range — say "depends on scope" first
- /sourcea/offer · /sourcea/pricing

IDE / CLOUD QUESTIONS:
- Lead with YES partially: Forge Terminal is the execution desk — try in browser at /sourcea/forge/terminal; full Mac IDE for founders
- Never open with "We don't offer" — reframe to what Forge IS
- Not a generic hosted IDE clone — controlled AI execution with workspace and agents
- Ask what they need: app generation, coding agents, deployment, team workflows?

"YOU JUST GIVE ME RECORDS?" (recover honestly):
- Acknowledge: fair pushback — records alone are not the product
- Reframe: Forge runs the work; proof shows clients what ran, what changed, and that it passed quality

EXACT HELP EXAMPLES (use when they ask for lists — 3 bullets, concrete):
- Agency QBR prep: scope "audit client AI deliverables" → agents review outputs → quality gate → client-ready summary + audit trail
- Content engine: weekly B2B posts → prompt forge → batch runs → founder approves → per-client tracked delivery
- Dev/automation: "add Stripe webhook" → advisor plans → patch proposal → verify → route to Cursor or cloud execute

TONE:
- Plain English, short paragraphs, bullets for lists
- Max one cal.com/sourcea/proof-demo link per reply unless they want to book
- Never mention OpenRouter, models, API keys, PASS/BLOCK, factories, or governance jargon
- Be interesting — match their energy, answer the actual question first"""

FORGE_TERMINAL_DEMO_SYSTEM = """You are Forge Terminal on sourcea.app — a founder-friendly advisor for strangers trying the public living-chat demo.

Reply in plain English with four short labeled sections:
1) Bottom line
2) What this means for their business
3) Blockers or risks
4) Suggested next step

Rules:
- Helpful operator tone — not a sales bot
- Never mention OpenRouter, models, API keys, receipts, PASS/BLOCK, or internal governance
- This public page has no workspace — mention Mac Forge IDE adds workspace, quality gate, and cloud dispatch when relevant
- Keep under 400 words"""


def _system_for_product(product: str) -> str:
    return FORGE_TERMINAL_DEMO_SYSTEM if (product or "").strip().lower() == "forge_terminal" else BRAIN_PUBLIC_SYSTEM


def _load_vault_key() -> str:
    for vault in (Path.home() / ".sina/secrets.env", Path.home() / "Desktop/SinaPromptOS/secrets.env"):
        if not vault.is_file():
            continue
        for line in vault.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def _openrouter_ready() -> bool:
    return bool(_load_vault_key())


def status_payload() -> dict:
    ready = _openrouter_ready()
    knowledge = _knowledge_meta()
    return {
        "schema": "sourcea-brain-chat-status-v1",
        "ok": True,
        "openrouter_ready": ready,
        "model": os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
        "provider": "openrouter",
        "plane": "cloud_api",
        "max_message_len": MAX_MESSAGE_LEN,
        "hint": "Brain — execution platform guide for Forge, examples, and booking",
        "knowledge": knowledge,
    }


def _load_knowledge_bundle() -> dict:
    bundle_path = SOURCEA_ROOT / "data" / "brain-chat-knowledge-bundle-v1.json"
    if bundle_path.is_file():
        try:
            return json.loads(bundle_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def _knowledge_meta() -> dict:
    bundle = _load_knowledge_bundle()
    chunks = bundle.get("chunks") or []
    lanes: dict[str, int] = {}
    for c in chunks:
        lane = c.get("lane") or "core"
        lanes[lane] = lanes.get(lane, 0) + 1
    return {
        "bundle_version": bundle.get("bundle_version", "0.0.0"),
        "chunk_count": len(chunks),
        "chars": bundle.get("total_chars", 0),
        "source_files": bundle.get("source_files", 0),
        "live_source_files": bundle.get("live_source_files", bundle.get("source_files", 0)),
        "rule_chunks": bundle.get("rule_chunks", 0),
        "lanes": lanes,
        "mode": bundle.get("retrieval", "brain_intelligence_v3"),
        "pipeline": bundle.get("pipeline", "rules_first_bm25_hybrid"),
    }


def _ground_prompt(base: str, hits: list[dict]) -> tuple[str, list[dict]]:
    if not hits:
        return base, []
    block = "\n\n".join(
        f"### {h.get('source_path')}{' (' + h['www_url'] + ')' if h.get('www_url') else ''}\n{h.get('content', '')}"
        for h in hits
    )
    citations = [
        {"source_path": h.get("source_path"), "www_url": h.get("www_url"), "lane": h.get("lane")}
        for h in hits
    ]
    prompt = f"""{base}

GROUNDED KNOWLEDGE ({len(hits)} retrieved chunks — cite URLs when relevant):
{block}

CITATION RULE: Mention page paths or URLs when helpful. Never reveal secrets or internal Mac paths."""
    return prompt, citations


def _chat_openrouter(messages: list[dict], *, product: str = "", system_prompt: str | None = None) -> tuple[bool, str]:
    key = _load_vault_key()
    if not key:
        return False, "Brain is not available right now — book a demo at cal.com/sourcea/proof-demo"

    sys_content = system_prompt or _system_for_product(product)
    body = json.dumps(
        {
            "model": os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
            "messages": [{"role": "system", "content": sys_content}] + messages[-MAX_HISTORY:],
            "temperature": 0.38,
            "max_tokens": 900 if (product or "").strip().lower() != "forge_terminal" else 600,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sourcea.app",
            "X-Title": "SourceA Brain",
        },
        method="POST",
    )
    ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
            data = json.loads(resp.read().decode())
        reply = data["choices"][0]["message"]["content"].strip()
        return True, reply
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:200]
        return False, f"Brain API error ({exc.code}) — use proof chips or book a demo."
    except Exception as exc:
        return False, f"Brain is temporarily offline — try proof chips or book a demo. ({exc.__class__.__name__})"


def handle_chat(body: dict[str, Any] | None) -> dict:
    body = body or {}
    action = str(body.get("action") or "chat").strip().lower()
    if action in ("status", "ping"):
        return status_payload()

    message = str(body.get("message") or body.get("text") or "").strip()
    if not message:
        return {"ok": False, "schema": "sourcea-brain-chat-receipt-v1", "error": "message_required"}
    if len(message) > MAX_MESSAGE_LEN:
        return {
            "ok": False,
            "schema": "sourcea-brain-chat-receipt-v1",
            "error": "message_too_long",
            "max": MAX_MESSAGE_LEN,
        }

    history_raw = body.get("history") or []
    history: list[dict] = []
    if isinstance(history_raw, list):
        for item in history_raw[-MAX_HISTORY:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "").strip().lower()
            content = str(item.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                history.append({"role": role, "content": content[:MAX_MESSAGE_LEN]})

    history.append({"role": "user", "content": message})
    product = str(body.get("product") or "").strip().lower()

    import sys

    scripts = SOURCEA_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from brain_intelligence_pipeline_v1 import run as brain_run  # noqa: WPS433

    pipeline = brain_run(message, product=product)
    ok, reply = _chat_openrouter(history, product=product, system_prompt=pipeline["prompt"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema": "sourcea-brain-chat-receipt-v1",
        "ok": ok,
        "reply": reply,
        "product": product or "brain",
        "provider": "openrouter",
        "model": os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
        "citations": pipeline.get("citations") if ok else [],
        "confidence": pipeline.get("confidence") if ok else None,
        "retrieval": {
            "intent": pipeline.get("intent"),
            "sources_consulted": pipeline.get("sources_consulted"),
            "rules_applied": pipeline.get("rules_applied"),
        }
        if ok
        else None,
        "knowledge": _knowledge_meta(),
        "at": now,
        "message": "Brain replied" if ok else reply,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="SourceA public Brain chat (OpenRouter)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--message", "-m", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.status:
        out = status_payload()
    else:
        out = handle_chat({"message": args.message})
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
