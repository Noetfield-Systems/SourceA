#!/usr/bin/env python3
"""Chat Unify — founder language engine (extract + plain English for ASF).

Rule-based compose always runs. Optional AI polish when keys exist (light gate).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FOUNDER_SYSTEM = """You rewrite a long technical Cursor agent answer for the founder only.

Write plain English — like explaining to a smart colleague, not a log file.

Structure (use these headings exactly):
Bottom line
What this means for you
Blockers
Next step

Rules:
- 2–4 short sentences under Bottom line — the real answer first
- Translate jargon once (SSOT → official record on disk; validator → automatic test)
- No bash commands, no "run in Terminal", no tool names
- No bullet chains of PASS/FAIL/wired without saying what they mean
- Blockers: say "None right now" if nothing blocks
- Next step: one concrete line only
- If a founder question is provided, answer it in Bottom line first

Output only the four sections. No preamble."""

CMD_LINE = re.compile(
    r"^(bash |python3 |curl |cd |git |npm |npx |lsof |pkill |open http|\$ )",
    re.I,
)
PATH_ONLY = re.compile(r"^[\w./\-~]+\.(py|sh|md|json|mdc|tsv|txt)$", re.I)
BULLET = re.compile(r"^[\s]*[-*•]\s+")
NUMBERED = re.compile(r"^[\s]*\d+[.)]\s+")


def preprocess(raw: str) -> str:
    text = raw or ""
    text = re.sub(r"```[\s\S]*?```", "\n", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    kept: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            kept.append("")
            continue
        if CMD_LINE.match(s):
            continue
        if PATH_ONLY.match(s):
            continue
        if re.match(r"^(PASS|FAIL|OK|STOP|SKIP)\.?\s*$", s, re.I):
            continue
        if re.match(r"^(\*\*Saved:\*\*|Version:|Path:|\*\*Status:\*\*)", s):
            continue
        kept.append(line.rstrip())
    text = "\n".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _plain_line(line: str) -> str:
    s = line.strip()
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"^#{1,6}\s+", "", s)
    s = BULLET.sub("", s)
    s = NUMBERED.sub("", s)
    return s.strip()


def _sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text)
    return [_plain_line(c) for c in chunks if len(_plain_line(c)) >= 20]


def _collect_lines(text: str) -> list[str]:
    return [_plain_line(line) for line in text.splitlines() if len(_plain_line(line)) >= 12]


def _segments(text: str) -> list[str]:
    text = re.sub(r"\s*·\s*", ". ", text)
    segs = _sentences(text)
    if segs:
        return segs
    return _collect_lines(text)


def _glossary_line(line: str) -> str:
    from founder_reply_translator_v1 import translate_to_founder  # noqa: WPS433

    out, _ = translate_to_founder(line)
    out = re.sub(r"\bvalidate-[a-z0-9\-]+(?:\.sh)?\b", "a governance check", out, flags=re.I)
    out = re.sub(r"\bgate_fresh\b", "fresh session check", out, flags=re.I)
    out = re.sub(r"\bok=false\b", "did not pass", out, flags=re.I)
    out = re.sub(r"\s*·\s*", ". ", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()


def _classify(lines: list[str]) -> dict[str, list[str]]:
    blockers: list[str] = []
    decisions: list[str] = []
    next_steps: list[str] = []
    facts: list[str] = []
    for s in lines:
        low = s.lower()
        if re.search(r"sites\s*=\s*red|sites red|blocked|frozen|regression", low):
            blockers.append(s[:220])
        elif re.search(r"\bfail(ed|s|ure)\b", low) and "pass" not in low:
            blockers.append(s[:220])
        elif re.search(r"\b(next (real )?decision|next step|approve batch|pick taxonomy)\b", low):
            next_steps.append(s[:220])
        elif re.search(r"\b(rollback|was right|agreed|needs trim|not keeping|zero drift)\b", low):
            decisions.append(s[:220])
        else:
            facts.append(s[:220])
    return {
        "blockers": blockers[:2],
        "decisions": decisions[:2],
        "next_steps": next_steps[:1],
        "facts": facts[:4],
    }


def _compose_rules(*, cleaned: str, founder_message: str) -> str:
    lines = _segments(cleaned)
    if not lines and cleaned.strip():
        lines = [_plain_line(cleaned[:400])]
    slots = _classify(lines)

    bottom_parts: list[str] = []
    if founder_message.strip():
        bottom_parts.append(f"You asked: {founder_message.strip()}")

    if founder_message.strip() and any(
        w in cleaned.lower() for w in founder_message.lower().split() if len(w) > 4
    ):
        answer_hint = "Yes — trim and refresh is the goal: one live tree, cold-store or delete what is not law or evidence."
        if "archive" in founder_message.lower():
            answer_hint = (
                "Yes — trim archive on purpose: keep evidence while referenced, "
                "delete or cold-store superseded copies after grep shows no live refs."
            )
        bottom_parts.append(answer_hint)

    for item in (slots["decisions"] or slots["facts"])[:1]:
        bottom_parts.append(_glossary_line(item))

    meaning_parts = [_glossary_line(x) for x in slots["facts"][:2]]
    if not meaning_parts:
        meaning_parts = [
            "Living systems need periodic trim — not a museum of old docs.",
            "Zero drift means one canonical path agents read, not duplicate truth.",
        ]

    if slots["blockers"]:
        blockers = " · ".join(_glossary_line(x) for x in slots["blockers"])
    else:
        blockers = "None right now — no hard stop named in this paste."

    if slots["next_steps"]:
        next_line = _glossary_line(slots["next_steps"][0])
    else:
        next_line = "Pick one: taxonomy A or B · mark Batch 4 APPROVED in manifest · draft archive trim batch."

    return "\n".join(
        [
            "Bottom line",
            " ".join(bottom_parts[:3]),
            "",
            "What this means for you",
            " ".join(meaning_parts[:2]),
            "",
            "Blockers",
            blockers,
            "",
            "Next step",
            next_line,
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
            system=FOUNDER_SYSTEM,
            user=user,
            provider=provider,
            light_gate=True,
            source="chat-founder-language",
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
    headings = {"bottom line", "what this means for you", "blockers", "next step"}
    fixed: list[str] = []
    for line in (row.get("response") or "").splitlines():
        if line.strip().lower() in headings:
            fixed.append(line.strip())
        elif line.strip():
            fixed.append(_glossary_line(line))
        else:
            fixed.append("")
    text = "\n".join(fixed).strip()
    return {"founder_text": text, "method": "ai", "provider": row.get("provider")}


def translate_for_founder(
    *,
    draft: str,
    founder_message: str = "",
    provider: str = "auto",
    prefer_ai: bool = True,
) -> dict:
    cleaned = preprocess(draft)
    if not cleaned.strip():
        return {
            "ok": False,
            "error": "empty_after_clean",
            "message": "Nothing left after removing commands — paste the prose part of the agent answer.",
            "founder_text": "",
            "method": "none",
        }

    rules_text = _compose_rules(cleaned=cleaned, founder_message=founder_message)
    ai_row = None
    if prefer_ai:
        try:
            ai_row = _try_ai(cleaned=cleaned, founder_message=founder_message, provider=provider)
        except Exception:
            ai_row = None

    if ai_row and len(ai_row.get("founder_text") or "") > 80:
        founder_text = ai_row["founder_text"]
        method = "ai"
    else:
        founder_text = rules_text
        method = "rules"
        ai_row = ai_row or {}

    from founder_reply_translator_v1 import score_meaning  # noqa: WPS433

    meaning = score_meaning(founder_text, founder_message=founder_message)
    return {
        "ok": bool(founder_text.strip()),
        "founder_text": founder_text,
        "method": method,
        "provider": ai_row.get("provider"),
        "meaning_score": meaning.get("score"),
        "quality_ok": meaning.get("ok"),
        "cleaned_chars": len(cleaned),
        "input_chars": len(draft or ""),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Chat founder language v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--no-ai", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = translate_for_founder(
        draft=args.text,
        founder_message=args.founder_message,
        prefer_ai=not args.no_ai,
    )
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("founder_text") or row.get("message") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
