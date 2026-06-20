#!/usr/bin/env python3
"""Founder reply translator — turn technical agent drafts into plain founder language.

SSOT glossary: data/founder-reply-glossary-v1.json
Law: data/agent-report-language-standard-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_PATH = ROOT / "data" / "founder-reply-glossary-v1.json"

VERB = re.compile(
    r"\b(is|are|was|were|has|have|still|because|means|blocks|helps|explains|"
    r"changed|failed|passes|you|your|for you|so |which means)\b",
    re.I,
)
SENTENCE = re.compile(r"[^.!?\n]+[.!?]")
JARGON = re.compile(
    r"\b(SSOT|probe|pulse|wired|receipt|validator|pre_ship|RUN INBOX|factory-now|"
    r"sites=RED|defer|WBC-P\d|TF-P\d|sa-\d+)\b",
    re.I,
)
STOP_WORDS = frozenset(
    "a an the is are was were be been being to of in on at for and or but not "
    "you your we they it this that with from as so if".split()
)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_glossary() -> dict[str, str]:
    data = _read_json(GLOSSARY_PATH)
    raw = data.get("translations") or {}
    return {str(k): str(v) for k, v in raw.items()}


def _strip_founder_forbidden(text: str) -> str:
    data = _read_json(GLOSSARY_PATH)
    out = text
    for pat in data.get("strip_patterns") or []:
        out = re.sub(re.escape(pat) + r"[^\n]*", "", out, flags=re.I)
    return out


def translate_to_founder(text: str) -> tuple[str, list[str]]:
    """Rule-based translation — no LLM. Returns (founder_text, notes)."""
    glossary = load_glossary()
    notes: list[str] = []
    out = _strip_founder_forbidden(text or "")

    # Replace longest keys first
    for key in sorted(glossary.keys(), key=len, reverse=True):
        if key in out or key.lower() in out.lower():
            val = glossary[key]
            out = re.sub(re.escape(key), val, out, flags=re.I)

    # Collapse middle-dot chains into one sentence hint
    if out.count("·") >= 3:
        notes.append("Collapsed internal label chain — agent should rewrite as full sentences.")
        out = re.sub(r"\s*·\s*", "; ", out)
        out = re.sub(r";{2,}", ";", out)

    # Drop lines that are only paths or flags
    lines: list[str] = []
    for line in out.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r"^[\w./\-]+\.(py|sh|md|json|mdc)$", s, re.I):
            notes.append(f"Dropped path-only line: {s[:60]}")
            continue
        if re.match(r"^(PASS|FAIL|OK|STOP)\.?\s*$", s, re.I):
            notes.append(f"Dropped label-only line: {s}")
            continue
        lines.append(s)
    out = "\n\n".join(lines).strip()
    return out, notes


def _intent_keywords(founder_message: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']{4,}", (founder_message or "").lower())
    return {w for w in words if w not in STOP_WORDS}


def score_meaning(text: str, *, founder_message: str = "") -> dict:
    t = (text or "").strip()
    if not t:
        return {"score": 0, "ok": False, "reasons": ["empty"]}

    reasons: list[str] = []
    score = 100

    sentences = SENTENCE.findall(t)
    verb_sentences = [s for s in sentences if VERB.search(s)]
    if len(t) > 80 and len(verb_sentences) < 1:
        score -= 35
        reasons.append("No complete sentence with because/so/means — reads like labels")

    if len(t) > 120 and len(sentences) < 2:
        score -= 20
        reasons.append("Too thin — needs at least two clear sentences")

    jargon_hits = JARGON.findall(t)
    if len(jargon_hits) >= 3 and not VERB.search(t[:400]):
        score -= 30
        reasons.append("Jargon without explanation")

    if founder_message.strip():
        keys = _intent_keywords(founder_message)
        tl = t.lower()
        overlap = [k for k in keys if k in tl]
        if keys and len(overlap) < max(1, len(keys) // 8):
            score -= 25
            reasons.append("Does not appear to answer what the founder asked")

    if "because" not in t.lower() and "so " not in t.lower() and "which means" not in t.lower():
        if len(t) > 100:
            score -= 15
            reasons.append("Missing causal link (because / so / which means)")

    score = max(0, min(100, score))
    return {"score": score, "ok": score >= 65, "reasons": reasons}


def evaluate(*, draft: str, founder_message: str = "") -> dict:
    from agent_report_language_gate_v1 import scan_text as scan_language  # noqa: WPS433

    original_lang = scan_language(draft, founder_asked_why=bool(founder_message))
    founder_text, translate_notes = translate_to_founder(draft)
    translated_lang = scan_language(founder_text, founder_asked_why=bool(founder_message))
    meaning = score_meaning(founder_text, founder_message=founder_message)

    ship_original = original_lang.get("ok") and meaning.get("ok")
    ship_translated = translated_lang.get("ok") and meaning.get("ok")

    if ship_original:
        verdict = "SHIP"
        ship_text = draft.strip()
    elif ship_translated:
        verdict = "SHIP_TRANSLATED"
        ship_text = founder_text
    else:
        verdict = "REJECT"
        ship_text = ""

    rewrite_hints: list[str] = []
    if verdict == "REJECT":
        for hit in original_lang.get("hits") or []:
            rewrite_hints.append(hit.get("label") or hit.get("id") or "language hit")
        for r in meaning.get("reasons") or []:
            rewrite_hints.append(r)
        rewrite_hints.append(
            "Restate what the founder asked · explain because/so · say what it means for them · proof last"
        )

    return {
        "schema": "founder-reply-translator-v1",
        "ok": verdict in ("SHIP", "SHIP_TRANSLATED"),
        "verdict": verdict,
        "founder_text": ship_text,
        "draft_text": draft,
        "translated_preview": founder_text,
        "translate_notes": translate_notes,
        "original_language": original_lang,
        "translated_language": translated_lang,
        "meaning": meaning,
        "rewrite_hints": rewrite_hints[:8],
        "glossary": str(GLOSSARY_PATH.relative_to(ROOT)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder reply translator v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8", errors="replace")
    row = evaluate(draft=body, founder_message=args.founder_message)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(f"FOUNDER_REPLY ok={row['ok']} verdict={row['verdict']}")
        if row.get("founder_text"):
            print("--- founder ---")
            print(row["founder_text"][:800])
        if row.get("rewrite_hints"):
            print("hints:", "; ".join(row["rewrite_hints"][:3]))
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
