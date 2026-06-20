#!/usr/bin/env python3
"""Chat Unify — founder reasoning engine (think beside plain language).

Local rules always. Optional AI when keys exist (18s cap).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REASONING_SYSTEM = """You are the founder's reasoning partner — not a parrot of the agent.

Read the agent answer and help the founder DECIDE.

Structure (exact headings):
What you're really deciding
What the agent assumes
Options on the table
What I'd lean toward
What could go wrong

Rules:
- Plain English · short paragraphs · because/so
- Name tradeoffs honestly (speed vs safety, trim vs break refs)
- "What I'd lean toward" = one recommendation + why — not both sides forever
- If founder question provided, anchor section 1 to it
- No bash, no Terminal, no validator names without translation
- No fake certainty — say when disk proof is missing

Output only the five sections."""

OPTION_RE = re.compile(
    r"\b(option\s*[ab]|taxonomy\s*[ab]|path\s*[12]|batch\s*\d|approve|frozen|trim|rollback)\b",
    re.I,
)
ASSUME_RE = re.compile(
    r"\b(assume|assumption|likely|should|must|expect|believe|if you|unless)\b",
    re.I,
)
RISK_RE = re.compile(
    r"\b(risk|wrong|break|regression|confusion|drift|duplicate|lose|fail|poison|stale)\b",
    re.I,
)
CLAIM_RE = re.compile(
    r"\b(recommend|suggest|decide|pick|choose|next|north star|block|unblock)\b",
    re.I,
)


def _segments(text: str) -> list[str]:
    from chat_founder_language_v1 import _segments as seg  # noqa: WPS433

    return seg(text)


def _glossary_line(line: str) -> str:
    from chat_founder_language_v1 import _glossary_line as gl  # noqa: WPS433

    return gl(line)


def _preprocess(raw: str) -> str:
    from chat_founder_language_v1 import preprocess  # noqa: WPS433

    return preprocess(raw)


def _bucket(segments: list[str]) -> dict[str, list[str]]:
    options: list[str] = []
    assumptions: list[str] = []
    risks: list[str] = []
    claims: list[str] = []
    for s in segments:
        low = s.lower()
        if OPTION_RE.search(low):
            options.append(s[:240])
        elif ASSUME_RE.search(low):
            assumptions.append(s[:240])
        elif RISK_RE.search(low):
            risks.append(s[:240])
        elif CLAIM_RE.search(low):
            claims.append(s[:240])
    return {
        "options": options[:5],
        "assumptions": assumptions[:4],
        "risks": risks[:4],
        "claims": claims[:5],
    }


def _compose_rules(*, cleaned: str, founder_message: str) -> str:
    segments = _segments(cleaned) or ([cleaned[:400]] if cleaned.strip() else [])
    buckets = _bucket(segments)

    deciding = founder_message.strip() or "What single decision this agent answer is pushing you toward."
    if founder_message.strip():
        deciding = f"You asked: {founder_message.strip()} — the real decision is whether to act on that now or defer."

    claim_line = buckets["claims"][0] if buckets["claims"] else segments[0] if segments else ""
    if claim_line:
        deciding = f"{deciding} The agent's main push: {_glossary_line(claim_line)}"

    if buckets["assumptions"]:
        assume = "\n".join(f"· {_glossary_line(x)}" for x in buckets["assumptions"][:3])
    else:
        assume = "· The agent treats its last answer as complete — you still verify logged.\n· It may be optimizing for cleanup speed over breaking live refs."

    if buckets["options"]:
        opts = "\n".join(f"· {_glossary_line(x)}" for x in buckets["options"][:4])
    else:
        opts = "· Approve the next manifest batch vs wait for taxonomy pick.\n· Trim cold storage vs keep until grep proves zero refs."

    lean_parts: list[str] = []
    if "archive" in (founder_message + cleaned).lower():
        lean_parts.append(
            "Lean toward trim on purpose: one live tree, delete or cold-store superseded only after grep — not blindfolding the whole folder."
        )
    if "batch 4" in cleaned.lower() or "batch 4" in founder_message.lower():
        lean_parts.append("Do not execute Batch 4 until taxonomy is picked — otherwise paths drift again.")
    if buckets["options"]:
        lean_parts.append(f"Short term: resolve what the agent named first — {_glossary_line(buckets['options'][0])}.")
    if not lean_parts:
        lean_parts.append("Take the one bounded next action the agent named — ignore the rest until that lands.")
    lean = " ".join(lean_parts[:2])

    if buckets["risks"]:
        wrong = "\n".join(f"· {_glossary_line(x)}" for x in buckets["risks"][:3])
    else:
        wrong = "· Moving files without manifest approval breaks script pointers.\n· Agents reading stale paths looks like success but isn't zero drift."

    return "\n".join(
        [
            "What you're really deciding",
            deciding,
            "",
            "What the agent assumes",
            assume,
            "",
            "Options on the table",
            opts,
            "",
            "What I'd lean toward",
            lean,
            "",
            "What could go wrong",
            wrong,
        ]
    ).strip()


def _try_ai(*, cleaned: str, founder_message: str, provider: str, timeout_sec: int = 18) -> dict | None:
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
        from ai_unify_api_v1 import dispatch_raw, pick_provider  # noqa: WPS433
    except ImportError:
        return None
    if pick_provider(provider) == "none":
        return None
    user = cleaned[:14000]
    if founder_message.strip():
        user = f"Founder question:\n{founder_message.strip()}\n\n---\n\nAgent answer:\n{user}"

    def _call() -> dict:
        return dispatch_raw(
            system=REASONING_SYSTEM,
            user=user,
            provider=provider,
            light_gate=True,
            source="chat-founder-reasoning",
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            row = pool.submit(_call).result(timeout=timeout_sec)
    except FutTimeout:
        return None
    except Exception:
        return None
    if not row.get("ok") or not (row.get("response") or "").strip():
        return None
    headings = {
        "what you're really deciding",
        "what the agent assumes",
        "options on the table",
        "what i'd lean toward",
        "what could go wrong",
    }
    fixed: list[str] = []
    for line in (row.get("response") or "").splitlines():
        h = line.strip().lower().lstrip("#").strip()
        if h in headings:
            fixed.append(line.strip().lstrip("#").strip())
        elif line.strip():
            fixed.append(_glossary_line(line))
        else:
            fixed.append("")
    return {"reasoning_text": "\n".join(fixed).strip(), "method": "ai", "provider": row.get("provider")}


def reason_for_founder(
    *,
    draft: str,
    founder_message: str = "",
    provider: str = "auto",
    prefer_ai: bool = False,
) -> dict:
    cleaned = _preprocess(draft)
    if not cleaned.strip():
        return {
            "ok": False,
            "error": "empty_after_clean",
            "message": "Paste agent prose first.",
            "reasoning_text": "",
            "method": "none",
        }

    rules_text = _compose_rules(cleaned=cleaned, founder_message=founder_message)
    ai_row = None
    if prefer_ai:
        try:
            ai_row = _try_ai(cleaned=cleaned, founder_message=founder_message, provider=provider)
        except Exception:
            ai_row = None

    if ai_row and len(ai_row.get("reasoning_text") or "") > 100:
        text = ai_row["reasoning_text"]
        method = "ai"
    else:
        text = rules_text
        method = "rules"
        ai_row = ai_row or {}

    return {
        "ok": bool(text.strip()),
        "reasoning_text": text,
        "method": method,
        "provider": ai_row.get("provider"),
        "cleaned_chars": len(cleaned),
        "input_chars": len(draft or ""),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Chat founder reasoning v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--ai", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = reason_for_founder(
        draft=args.text,
        founder_message=args.founder_message,
        prefer_ai=args.ai,
    )
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("reasoning_text") or row.get("message") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
