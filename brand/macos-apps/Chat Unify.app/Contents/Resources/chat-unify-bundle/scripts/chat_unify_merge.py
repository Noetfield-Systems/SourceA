#!/usr/bin/env python3
"""Chat Unify — local merge of Cursor chat extracts + contradiction scan. No cloud."""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

def _bundle_root() -> Path | None:
    raw = os.environ.get("CHAT_UNIFY_BUNDLE_ROOT", "").strip()
    if not raw:
        return None
    root = Path(raw)
    if (root / "scripts" / "chat_unify_merge.py").is_file():
        return root
    return None


def _source_a_root() -> Path:
    """Real SourceA for governance paths (manifest, attachments). Never the .app bundle when set."""
    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    bundle = _bundle_root()
    if bundle:
        return bundle
    return Path(__file__).resolve().parents[1]


def _prompts_dir() -> Path:
    bundle = _bundle_root()
    if bundle:
        bp = bundle / "prompts"
        if bp.is_dir():
            return bp
    sa = _source_a_root()
    pd = sa / "prompts"
    return pd if pd.is_dir() else sa


SOURCE_A = _source_a_root()
STATE_DIR = Path.home() / ".sina" / "chat-unify"
EXTRACTS_DIR = STATE_DIR / "extracts"
UNIFIED_PATH = STATE_DIR / "last-unified.json"
PROMPTS_DIR = _prompts_dir()
EXTRACT_PROMPT_PATH = PROMPTS_DIR / "CHAT_EXTRACT_UNIFY_PROMPT.txt"
if not EXTRACT_PROMPT_PATH.is_file():
    EXTRACT_PROMPT_PATH = SOURCE_A / "CHAT_EXTRACT_UNIFY_PROMPT.txt"
UNIFY_PROMPT_PATH = PROMPTS_DIR / "CHAT_UNIFY_ROLLUP_PROMPT.txt"
if not UNIFY_PROMPT_PATH.is_file():
    UNIFY_PROMPT_PATH = SOURCE_A / "CHAT_UNIFY_ROLLUP_PROMPT.txt"
MANIFEST_PATH = (
    SOURCE_A / "knowledge-library" / "fields" / "pre-llm-world-model" / "01-extracts" / "MANIFEST.md"
)
EXPORTS_DIR = STATE_DIR / "exports"
RECEIPTS_DIR = STATE_DIR / "receipts"
SUGGESTED_TAGS = (
    "WTM-D5",
    "THREAD-FACTORY",
    "THREAD-MERGEPACK",
    "THREAD-CHAT-CONSOLIDATION",
    "THREAD-ECOSYSTEM",
    "THREAD-WIRE",
)

NEGATION_PAIRS = [
    ("enable", "disable"),
    ("use", "avoid"),
    ("keep", "remove"),
    ("yes", "no"),
    ("open", "close"),
    ("start", "stop"),
    ("add", "delete"),
    ("ship", "freeze"),
    ("active", "inactive"),
    ("allow", "block"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_prompt(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _section(text: str, heading: str) -> str:
    pat = re.compile(
        rf"##\s*{re.escape(heading)}[^\n]*\n(.*?)(?=\n##\s|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pat.search(text)
    return (m.group(1).strip() if m else "")


def _table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "--------" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and any(cells):
            rows.append(cells)
    return rows


def _bullets(section: str) -> list[str]:
    out: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if line.startswith(("-", "•", "*")):
            out.append(line.lstrip("-•* ").strip())
        elif line.startswith(">"):
            out.append(line.lstrip("> ").strip())
    return [b for b in out if b]


def _session_title(text: str) -> str:
    header = _section(text, "1. SESSION HEADER") or _section(text, "SESSION HEADER")
    for line in header.splitlines():
        if "title" in line.lower() and ":" in line:
            return line.split(":", 1)[1].strip().strip("-")
    m = re.search(r"Chat title[:\s]+(.+)", header, re.I)
    return m.group(1).strip() if m else "Untitled chat"


def _archive_verdict(text: str) -> str:
    m = re.search(r"SAFE TO ARCHIVE[^\?]*\?\s*\**\s*(YES|NO|ONLY AFTER[^\n]*)", text, re.I)
    return m.group(1).strip() if m else "UNKNOWN"


def _raw_chat_fallback(text: str) -> dict:
    """When founder pastes raw chat (not CHAT EXTRACT), still produce viewable output."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = "Untitled chat"
    for ln in lines[:8]:
        if len(ln) > 12 and len(ln) < 120 and not ln.startswith("|"):
            title = ln[:100]
            break
    facts = [ln for ln in lines if len(ln) > 20][:24]
    rollup = " ".join(lines[:3])[:500]
    return {
        "title": title,
        "threads": [],
        "decisions": [],
        "suggestions": [],
        "facts": facts,
        "todos": [],
        "repos": [],
        "contradictions_local": [],
        "quotes": [],
        "merge_tags": [],
        "rollup": rollup,
        "archive": "UNKNOWN",
        "raw_paste": True,
        "hint": "Raw chat saved — tap Structure all or Send extract prompt → Cursor.",
    }


def _clean_user_query(text: str) -> str:
    text = re.sub(r"</?user_query>", "", text, flags=re.I).strip()
    text = re.sub(r"\[REDACTED\]", "", text).strip()
    return re.sub(r"\s+", " ", text).strip()


def _split_chat_turns(text: str) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    pattern = re.compile(r"\*\*(USER|ASSISTANT):\*\*\s*", re.I)
    parts = pattern.split(text)
    idx = 1
    while idx < len(parts) - 1:
        role = parts[idx].strip().upper()
        body = parts[idx + 1].strip()
        if body and role in ("USER", "ASSISTANT"):
            turns.append((role, body))
        idx += 2
    if turns:
        return turns
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("USER:"):
            turns.append(("USER", line[5:].strip()))
        elif line.upper().startswith("ASSISTANT:"):
            turns.append(("ASSISTANT", line[10:].strip()))
    return turns


def _unique_lines(rows: list[str], limit: int = 40) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for row in rows:
        key = _norm(row)[:120]
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(row.strip())
        if len(out) >= limit:
            break
    return out


def _mine_threads_from_turns(turns: list[tuple[str, str]]) -> list[list[str]]:
    threads: list[list[str]] = []
    for role, body in turns:
        if role != "USER":
            continue
        q = _clean_user_query(body)
        if len(q) < 8:
            continue
        title = q[:100]
        if q.lower().startswith("check"):
            status = "verify"
        elif any(w in q.lower() for w in ("ship", "fix", "implement", "rebuild")):
            status = "active"
        elif any(w in q.lower() for w in ("analyse", "analyze", "golden")):
            status = "review"
        else:
            status = "discussed"
        threads.append([title, status, q[:180]])
    return threads[:28]


def _mine_decisions(text: str, turns: list[tuple[str, str]]) -> list[list[str]]:
    decisions: list[list[str]] = []
    for line in text.splitlines():
        line = line.strip()
        if "\t" in line and "Verdict" not in line and "Claim" not in line:
            cells = [c.strip() for c in line.split("\t") if c.strip()]
            if len(cells) >= 2 and len(cells[0]) > 8:
                why = cells[1][:120]
                rev = "N" if any(w in why.lower() for w in ("locked", "ship", "pass", "done")) else "Y"
                decisions.append([cells[0][:120], why, rev])
        if line.startswith("|") and "|" in line[1:] and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and len(cells[0]) > 6 and cells[0].lower() not in ("decision", "claim", "thread"):
                decisions.append([cells[0][:120], cells[1][:120] if len(cells) > 1 else "agreed", "N"])
    for pat in (
        r"(?i)(Chat Unify v1\.1[^\n]{0,80})",
        r"(?i)((?:PASS|SHIPPED|DONE|FIXED|LOCKED)[^\n]{10,100})",
        r"(?i)(merge_quality[^\n]{0,80})",
        r"(?i)(native \.app[^\n]{0,80})",
        r"(?i)(auto-?import[^\n]{0,80})",
        r"(?i)(commercial-?grade[^\n]{0,80})",
    ):
        for m in re.finditer(pat, text):
            snippet = m.group(1).strip()
            if len(snippet) > 12:
                decisions.append([snippet[:120], "Detected in session", "N"])
    for role, body in turns:
        if role != "ASSISTANT":
            continue
        for line in body.splitlines():
            line = line.strip()
            if re.search(r"(?i)\b(PASS|SHIPPED|DONE|FIXED|LOCKED|v1\.1)\b", line) and 16 < len(line) < 200:
                decisions.append([line[:120], "Assistant outcome", "N"])
    deduped: list[list[str]] = []
    seen: set[str] = set()
    for row in decisions:
        key = _norm(row[0])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped[:36]


def _mine_facts(text: str) -> list[str]:
    facts: list[str] = []
    for m in re.finditer(r"(/Users/[\w./-]+|~/.sina/[\w./-]+|scripts/[\w./-]+|:\d{4,5}\b)", text):
        facts.append(m.group(1))
    keywords = ("SourceA", "Chat Unify", "Mac Health", "Apple Health", "Sina Command", "merge_quality", "13023", "13024", "13025", "13020")
    for line in text.splitlines():
        line = line.strip()
        if 20 <= len(line) <= 220 and any(k.lower() in line.lower() for k in keywords):
            facts.append(line)
    return _unique_lines(facts, 40)


def _mine_todos(turns: list[tuple[str, str]]) -> list[list[str]]:
    todos: list[list[str]] = []
    for role, body in turns:
        if role != "USER":
            continue
        q = _clean_user_query(body)
        if any(w in q.lower() for w in ("fix", "ship", "implement", "rebuild", "check all", "deliver")):
            todos.append([q[:120], "ASF", "—", "Executor completes locally"])
    return todos[:12]


def _mine_quotes(turns: list[tuple[str, str]]) -> list[str]:
    quotes: list[str] = []
    for role, body in turns:
        q = _clean_user_query(body)
        if role == "USER" and 12 < len(q) < 200:
            quotes.append(f"{role}: {q}")
    return quotes[:5]


def _guess_title(label: str, turns: list[tuple[str, str]]) -> str:
    if label and label != "Untitled chat" and not label.startswith("Cursor:"):
        return label[:100]
    for role, body in turns:
        if role == "USER":
            q = _clean_user_query(body)
            if len(q) > 10:
                return q[:100]
    return label[:100] or "Chat session"


def _guess_outcome(text: str) -> str:
    lower = text.lower()
    if "pass" in lower:
        return "DONE"
    return "IN PROGRESS"


def build_structured_extract_document(
    raw: str,
    *,
    title: str = "",
    tags: list[str] | None = None,
    imported_from: str = "",
) -> str:
    sample = raw[:1_200_000]
    turns = _split_chat_turns(sample)
    chat_title = _guess_title(title, turns)
    threads = _mine_threads_from_turns(turns)
    decisions = _mine_decisions(sample, turns)
    facts = _mine_facts(sample)
    todos = _mine_todos(turns)
    quotes = _mine_quotes(turns)
    outcome = _guess_outcome(sample)
    tag_str = ", ".join(tags or []) or "THREAD-CHAT-CONSOLIDATION"
    rollup = (
        f"This session covered {len(threads)} thread(s) and {len(decisions)} decision signal(s). "
        f"Focus: {chat_title}. Structured locally for merge-ready receipt chain."
    )
    lines = [
        "# CHAT EXTRACT (local auto-structure)",
        "",
        "## 1. SESSION HEADER",
        f"- Chat title: {chat_title}",
        f"- Outcome status: {outcome}",
        f"- Source: {'transcript import' if imported_from else 'paste'}",
        f"- Tags: {tag_str}",
        "",
        "## 2. THREADS & TOPICS",
        "| Thread | Status | One-line summary |",
        "|--------|--------|------------------|",
    ]
    if threads:
        for row in threads:
            cells = row + [""] * (3 - len(row))
            lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} |")
    else:
        lines.append("| General session | discussed | No discrete user threads mined |")
    lines.extend(["", "## 3. DECISIONS LOCKED", "| Decision | Why | Reversible? (Y/N) |", "|----------|-----|-------------------|"])
    if decisions:
        for row in decisions:
            cells = row + [""] * (3 - len(row))
            lines.append(f"| {cells[0]} | {cells[1]} | {cells[2] or 'N'} |")
    else:
        lines.append("| None locked in this chat. | — | Y |")
    lines.extend(["", "## 5. IMPORTANT FACTS & CONTEXT"])
    for f in facts or ["No path/port facts mined."]:
        lines.append(f"- {f}")
    lines.extend(["", "## 6. OPEN LOOPS & TODOs", "| Item | Owner | Blocker | Next action |", "|------|-------|---------|-------------|"])
    for row in todos or [["Review structured extract", "ASF", "—", "Merge when satisfied"]]:
        cells = row + [""] * (4 - len(row))
        lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    lines.extend(["", "## 9. QUOTES WORTH KEEPING"])
    for q in quotes or ["> Structured locally for merge-ready receipt chain."]:
        lines.append(f"> {q.lstrip('> ')}")
    lines.extend(["", "## 10. MERGE TAGS", tag_str, "", "## 11. ONE-PARAGRAPH ROLLUP", rollup, "", "**SAFE TO ARCHIVE THIS CHAT?** ONLY AFTER merge review", ""])
    return "\n".join(lines)


def structure_extract_record(data: dict) -> dict:
    parsed = data.get("parsed") or {}
    if data.get("structured") and not _extract_is_weak(parsed) and not parsed.get("raw_paste"):
        return data
    raw = data.get("text") or ""
    src = (data.get("imported_from") or "").strip()
    if src and Path(src).is_file():
        try:
            raw = _jsonl_to_text(Path(src))
        except OSError:
            pass
    if len(raw) < 40:
        return data
    structured = build_structured_extract_document(
        raw,
        title=data.get("label") or "",
        tags=data.get("tags") or [],
        imported_from=src,
    )
    parsed2 = parse_extract(structured)
    data["text"] = structured
    data["parsed"] = parsed2
    data["chars"] = len(structured)
    data["weak"] = _extract_is_weak(parsed2)
    data["raw_paste"] = bool(parsed2.get("raw_paste"))
    data["structured"] = True
    data["structured_at"] = _now()
    data["raw_chars"] = len(raw)
    if src:
        data["raw_source"] = src
    return data


def upgrade_extract(eid: str) -> dict:
    path = EXTRACTS_DIR / f"{eid}.json"
    if not path.is_file():
        return {"ok": False, "error": "not_found"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"ok": False, "error": str(e)}
    before_weak = _extract_is_weak(data.get("parsed") or {})
    data = structure_extract_record(data)
    data["id"] = path.stem
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "extract": _extract_public_summary(data),
        "was_weak": before_weak,
        "still_weak": _extract_is_weak(data.get("parsed") or {}),
    }


def upgrade_all_weak() -> dict:
    upgraded: list[dict] = []
    for ex in list_extracts():
        parsed = ex.get("parsed") or {}
        needs = _extract_is_weak(parsed) or parsed.get("raw_paste") or not ex.get("structured")
        if not needs:
            continue
        path = EXTRACTS_DIR / f"{ex.get('id')}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        data = structure_extract_record(data)
        data["id"] = path.stem
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        upgraded.append(_extract_public_summary(data))
    quality = merge_quality_report(list_extracts())
    return {"ok": True, "upgraded_count": len(upgraded), "upgraded": upgraded, "quality": quality}


def _is_structured_extract(text: str) -> bool:
    markers = (
        "## 1. SESSION HEADER",
        "## 2. THREADS",
        "## 3. DECISIONS",
        "CHAT EXTRACT",
        "SAFE TO ARCHIVE",
    )
    upper = text.upper()
    return any(m.upper() in upper for m in markers)


def parse_extract(text: str) -> dict:
    text = (text or "").strip()
    if not _is_structured_extract(text):
        return _raw_chat_fallback(text)
    parsed = {
        "title": _session_title(text),
        "threads": _table_rows(_section(text, "2. THREADS") or _section(text, "THREADS")),
        "decisions": _table_rows(_section(text, "3. DECISIONS") or _section(text, "DECISIONS LOCKED")),
        "suggestions": _table_rows(_section(text, "4. SUGGESTIONS") or _section(text, "SUGGESTIONS")),
        "facts": _bullets(_section(text, "5. IMPORTANT FACTS") or _section(text, "IMPORTANT FACTS")),
        "todos": _table_rows(_section(text, "6. OPEN LOOPS") or _section(text, "OPEN LOOPS")),
        "repos": _bullets(_section(text, "7. REPO") or _section(text, "REPO / PRODUCT")),
        "contradictions_local": _bullets(
            _section(text, "8. CONTRADICTIONS") or _section(text, "CONTRADICTIONS")
        ),
        "quotes": _bullets(_section(text, "9. QUOTES") or _section(text, "QUOTES WORTH")),
        "merge_tags": re.findall(r"#\w[\w-]*", _section(text, "10. MERGE TAGS") or text),
        "rollup": (_section(text, "11. ONE-PARAGRAPH") or _section(text, "ONE-PARAGRAPH ROLLUP")).strip(),
        "archive": _archive_verdict(text),
        "raw_paste": False,
    }
    return parsed


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower().strip())


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _has_negation_conflict(a: str, b: str) -> bool:
    na, nb = _norm(a), _norm(b)
    for pos, neg in NEGATION_PAIRS:
        if (pos in na and neg in nb) or (neg in na and pos in nb):
            if _similar(a, b) >= 0.35:
                return True
    return False


def detect_contradictions(extracts: list[dict]) -> list[dict]:
    hits: list[dict] = []
    for ex in extracts:
        for c in ex.get("parsed", {}).get("contradictions_local") or []:
            if c and c.lower() not in ("none", "none.", "n/a", "-"):
                hits.append(
                    {
                        "kind": "local",
                        "severity": "medium",
                        "source": ex.get("label") or ex.get("id"),
                        "detail": c,
                    }
                )

    decisions: list[tuple[str, str, str, str]] = []
    for ex in extracts:
        eid = ex.get("id") or "?"
        label = ex.get("label") or eid
        for row in ex.get("parsed", {}).get("decisions") or []:
            if not row:
                continue
            decisions.append((eid, label, row[0], row[1] if len(row) > 1 else ""))

    for i, (ida, la, da, wa) in enumerate(decisions):
        for idb, lb, db, wb in decisions[i + 1 :]:
            if ida == idb:
                continue
            if _similar(da, db) >= 0.55 and _norm(da) != _norm(db):
                hits.append(
                    {
                        "kind": "decision_overlap",
                        "severity": "high",
                        "source": f"{la} vs {lb}",
                        "detail": f"Similar decisions differ: «{da[:120]}» vs «{db[:120]}»",
                    }
                )
            if _has_negation_conflict(da, db):
                hits.append(
                    {
                        "kind": "decision_negation",
                        "severity": "critical",
                        "source": f"{la} vs {lb}",
                        "detail": f"Opposite direction: «{da[:100]}» vs «{db[:100]}»",
                    }
                )

    threads: dict[str, list[tuple[str, str]]] = {}
    for ex in extracts:
        label = ex.get("label") or ex.get("id") or "?"
        for row in ex.get("parsed", {}).get("threads") or []:
            if len(row) < 2:
                continue
            key = _norm(row[0])
            status = row[1] if len(row) > 1 else "?"
            threads.setdefault(key, []).append((label, status))

    for thread, entries in threads.items():
        labels = {l for l, _ in entries}
        statuses = {_norm(s) for _, s in entries}
        if len(statuses) > 1 and thread and len(labels) > 1:
            hits.append(
                {
                    "kind": "thread_status",
                    "severity": "high",
                    "source": " / ".join(l for l, _ in entries),
                    "detail": f"Thread «{thread[:80]}» has conflicting statuses: {', '.join(sorted(statuses))}",
                }
            )

    archives = [(ex.get("label") or ex.get("id"), ex.get("parsed", {}).get("archive", "")) for ex in extracts]
    yes_labels = [l for l, a in archives if a.upper().startswith("YES")]
    no_labels = [l for l, a in archives if a.upper().startswith("NO")]
    if yes_labels and no_labels and len(extracts) > 1:
        hits.append(
            {
                "kind": "archive_mixed",
                "severity": "low",
                "source": "session mix",
                "detail": f"Some chats marked archive YES ({', '.join(yes_labels[:3])}) while others NO ({', '.join(no_labels[:3])}) — review before closing.",
            }
        )

    seen: set[str] = set()
    deduped: list[dict] = []
    for h in sorted(hits, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["severity"], 9)):
        key = h["kind"] + h["detail"][:80]
        if key not in seen:
            seen.add(key)
            deduped.append(h)
    return deduped


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None._\n"
    line = "| " + " | ".join(headers) + " |\n"
    line += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        cells = row + [""] * (len(headers) - len(row))
        line += "| " + " | ".join(cells[: len(headers)]) + " |\n"
    return line


def build_unified_brief(extracts: list[dict], contradictions: list[dict]) -> str:
    lines = [
        "# UNIFIED CHAT BRIEF (local merge)",
        f"_Generated {_now()}_",
        f"_Sources: {len(extracts)} chat extract(s)_",
        "",
        "## A. Executive summary",
    ]
    rollups = [ex.get("parsed", {}).get("rollup") for ex in extracts if ex.get("parsed", {}).get("rollup")]
    if rollups:
        lines.extend(rollups[:6])
    else:
        lines.append("_No rollups found — run CHAT EXTRACT in each Cursor chat first._")
    raw_any = any((ex.get("parsed") or {}).get("raw_paste") for ex in extracts)
    if raw_any:
        lines.append("")
        lines.append("_Note: some sources are **raw chat** (not structured CHAT EXTRACT). Content is included below._")
    lines.extend(["", "## B. Master decision log", ""])
    dec_rows: list[list[str]] = []
    for ex in extracts:
        label = ex.get("label") or ex.get("id") or "?"
        for row in ex.get("parsed", {}).get("decisions") or []:
            if row:
                dec_rows.append([row[0], label, row[1] if len(row) > 1 else "", "Y"])
    lines.append(_md_table(["Decision", "Source chat", "Why", "Still valid?"], dec_rows))

    lines.extend(["", "## C. Active threads (all sources)", ""])
    thread_rows: list[list[str]] = []
    for ex in extracts:
        label = ex.get("label") or ex.get("id") or "?"
        for row in ex.get("parsed", {}).get("threads") or []:
            if row:
                thread_rows.append(
                    [
                        row[0],
                        row[1] if len(row) > 1 else "",
                        label,
                        row[2] if len(row) > 2 else "",
                    ]
                )
    lines.append(_md_table(["Thread", "Status", "Source", "Summary"], thread_rows))

    lines.extend(["", "## D. Open loops", ""])
    todo_rows: list[list[str]] = []
    for ex in extracts:
        for row in ex.get("parsed", {}).get("todos") or []:
            if row:
                todo_rows.append(row)
    lines.append(_md_table(["Item", "Owner", "Blocker", "Next action"], todo_rows))

    lines.extend(["", "## E. Facts & system map", ""])
    all_facts: list[str] = []
    for ex in extracts:
        all_facts.extend(ex.get("parsed", {}).get("facts") or [])
        all_facts.extend(ex.get("parsed", {}).get("repos") or [])
    for f in dict.fromkeys(all_facts):
        lines.append(f"- {f}")

    lines.extend(["", "## E2. Source text (saved content)", ""])
    for ex in extracts:
        label = ex.get("label") or ex.get("id") or "?"
        body = (ex.get("text") or "").strip()
        if not body:
            continue
        lines.append(f"### {label}")
        if (ex.get("parsed") or {}).get("raw_paste"):
            lines.append("_Raw paste — use extract prompt in Cursor for structured merge._")
        lines.append("")
        lines.append(body[:12000])
        if len(body) > 12000:
            lines.append(f"\n_… truncated ({len(body)} chars total)_")
        lines.append("")

    lines.extend(["", "## F. Contradictions & drift (auto-detected)", ""])
    if contradictions:
        for c in contradictions:
            lines.append(f"- **[{c['severity'].upper()}]** ({c['kind']}) {c['detail']} _— {c['source']}_")
    else:
        lines.append("_No cross-chat contradictions detected by local rules. Review decisions manually before archiving._")

    lines.extend(["", "## G. Archive guidance", ""])
    for ex in extracts:
        p = ex.get("parsed", {})
        lines.append(f"- **{ex.get('label')}**: {p.get('archive', 'UNKNOWN')}")

    tags: list[str] = []
    for ex in extracts:
        tags.extend(ex.get("parsed", {}).get("merge_tags") or [])
    if tags:
        lines.extend(["", "## H. Merge tags", "", ", ".join(dict.fromkeys(tags))])

    lines.extend(
        [
            "",
            "## I. Next step",
            "Paste this file into a new Cursor chat with `CHAT_UNIFY_ROLLUP_PROMPT.txt` for AI polish,",
            "or use **Send unified to Cursor** in the mini app.",
            "",
        ]
    )
    return "\n".join(lines)


def _fresh_parsed(data: dict) -> dict:
    """Always re-parse from text — never trust stale parsed blobs on disk."""
    text = (data.get("text") or "").strip()
    if not text:
        return data.get("parsed") or {}
    return parse_extract(text)


def _extract_is_weak(parsed: dict) -> bool:
    if not parsed:
        return True
    decisions = parsed.get("decisions") or []
    threads = parsed.get("threads") or []
    return len(decisions) == 0 and len(threads) == 0


def _normalize_tags(tags: list | str | None) -> list[str]:
    if not tags:
        return []
    if isinstance(tags, str):
        parts = re.split(r"[,#\s]+", tags)
    else:
        parts = [str(t) for t in tags]
    out: list[str] = []
    for p in parts:
        p = p.strip().lstrip("#")
        if not p:
            continue
        if not p.upper().startswith("THREAD-") and not p.upper().startswith("WTM-"):
            if p.upper().startswith("D"):
                p = f"WTM-{p.upper()}"
            else:
                p = f"THREAD-{p.upper().replace(' ', '-')}"
        out.append(p)
    return list(dict.fromkeys(out))


def _manifest_pointer(path: Path) -> str:
    return f"`{path}`"


def append_manifest_row(
    *,
    row_id: str,
    source_type: str,
    layer: str,
    pointer: str,
    thread: str,
    verdict: str,
) -> dict:
    """Append pointer row to knowledge-library extract manifest (no JSON copy into SourceA)."""
    if not MANIFEST_PATH.is_file():
        return {"ok": False, "error": "manifest_missing", "path": str(MANIFEST_PATH)}
    body = MANIFEST_PATH.read_text(encoding="utf-8")
    if row_id in body:
        return {"ok": True, "skipped": True, "row_id": row_id}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    line = (
        f"| {row_id} | {today} | {source_type} | **{layer}** | {pointer} | {thread} | {verdict} |"
    )
    marker = "## Pending extracts (Chat Unify)"
    if marker in body:
        body = body.replace(marker, f"{marker}\n{line}", 1)
    else:
        body = body.rstrip() + f"\n\n{line}\n"
    MANIFEST_PATH.write_text(body, encoding="utf-8")
    return {"ok": True, "row_id": row_id, "manifest": str(MANIFEST_PATH)}


def _sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def write_unify_receipt(payload: dict, *, founder_tap: bool = True) -> dict:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    brief = payload.get("unified_brief") or ""
    receipt = {
        "schema": "chat-unify-receipt-v1",
        "built_at": payload.get("built_at") or _now(),
        "extract_ids": payload.get("extract_ids") or [],
        "extract_count": payload.get("extract_count") or 0,
        "contradiction_count": payload.get("contradiction_count") or 0,
        "contradiction_hashes": [
            _sha256_text(json.dumps(c, sort_keys=True)) for c in (payload.get("contradictions") or [])
        ],
        "brief_sha256": _sha256_text(brief),
        "brief_chars": len(brief),
        "founder_tap": founder_tap,
        "auto": not founder_tap,
    }
    path = RECEIPTS_DIR / f"unify-{ts}.json"
    path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    receipt["path"] = str(path)
    return receipt


def export_brief_to_disk() -> dict:
    if not UNIFIED_PATH.is_file():
        return {"ok": False, "error": "no_unified_brief", "message": "Merge first — no unified brief on disk."}
    try:
        last = json.loads(UNIFIED_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"ok": False, "error": "corrupt_unified"}
    brief = last.get("unified_brief") or ""
    if not brief.strip():
        return {"ok": False, "error": "empty_brief"}
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    out = EXPORTS_DIR / f"unified-{ts}.md"
    out.write_text(brief, encoding="utf-8")
    attach_root = SOURCE_A / "archive" / "attachments" / "chat-unify"
    attach_path = None
    if SOURCE_A.is_dir():
        attach_root.mkdir(parents=True, exist_ok=True)
        attach_path = attach_root / f"unified-{ts}.md"
        attach_path.write_text(brief, encoding="utf-8")
    return {
        "ok": True,
        "path": str(out),
        "attachment_path": str(attach_path) if attach_path else None,
        "chars": len(brief),
        "sha256": _sha256_text(brief),
    }


def _jsonl_to_text(path: Path) -> str:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        role = (obj.get("role") or "unknown").upper()
        msg = obj.get("message") or {}
        if isinstance(msg, str):
            lines.append(f"**{role}:** {msg}")
            continue
        content = msg.get("content")
        if isinstance(content, str):
            lines.append(f"**{role}:** {content}")
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = (block.get("text") or "").strip()
                    if text:
                        lines.append(f"**{role}:** {text}")
    return "\n\n".join(lines)


def list_transcript_candidates(limit: int = 12) -> list[dict]:
    roots: list[Path] = [
        Path.home() / ".cursor" / "projects",
        Path.home() / "Desktop" / "SourceA",
    ]
    seen: set[str] = set()
    rows: list[dict] = []
    patterns = ("**/agent-transcripts/*.jsonl", "**/agent-transcripts/*/*.jsonl")
    for root in roots:
        if not root.is_dir():
            continue
        for pattern in patterns:
            for path in sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
                key = str(path)
                if key in seen:
                    continue
                seen.add(key)
                try:
                    rows.append(
                        {
                            "path": key,
                            "name": path.stem[:48],
                            "mtime": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                            "size": path.stat().st_size,
                        }
                    )
                except OSError:
                    continue
                if len(rows) >= limit:
                    return sorted(rows, key=lambda r: r.get("mtime") or "", reverse=True)
    return sorted(rows, key=lambda r: r.get("mtime") or "", reverse=True)


def _extract_source_paths() -> set[str]:
    return {str(ex.get("imported_from")) for ex in list_extracts() if ex.get("imported_from")}


def _find_duplicate_extract(text: str) -> dict | None:
    """Return existing extract when identical content is already saved."""
    digest = _sha256_text(text)
    for ex in list_extracts():
        if ex.get("content_sha256") == digest:
            return ex
        if _sha256_text(ex.get("text") or "") == digest:
            return ex
    return None


def _extract_public_summary(ex: dict) -> dict:
    p = ex.get("parsed") or {}
    return {
        "id": ex.get("id"),
        "label": ex.get("label"),
        "chars": ex.get("chars"),
        "saved_at": ex.get("saved_at"),
        "weak": _extract_is_weak(p),
        "raw_paste": bool(p.get("raw_paste")),
        "imported_from": ex.get("imported_from"),
        "tags": ex.get("tags") or [],
        "decision_count": len(p.get("decisions") or []),
        "thread_count": len(p.get("threads") or []),
    }


def import_latest_transcript(*, tags: list | str | None = None) -> dict:
    candidates = list_transcript_candidates(1)
    if not candidates:
        return {"ok": False, "error": "no_transcripts", "message": "No Cursor transcripts found on this Mac."}
    path = candidates[0]["path"]
    for ex in list_extracts():
        if ex.get("imported_from") == path:
            return {
                "ok": True,
                "skipped": True,
                "extract": _extract_public_summary(ex),
                "imported_from": path,
                "message": "Latest transcript already in library.",
            }
    label = f"Cursor: {Path(path).stem[:40]}"
    return import_transcript(path=path, label=label, tags=tags or ["THREAD-CHAT-CONSOLIDATION"])


def import_transcript(*, path: str, label: str = "", tags: list | str | None = None) -> dict:
    p = Path((path or "").strip()).expanduser()
    if not p.is_file():
        return {"ok": False, "error": "not_found", "message": f"No transcript at {path}"}
    for ex in list_extracts():
        if ex.get("imported_from") == str(p):
            return {
                "ok": True,
                "skipped": True,
                "extract": _extract_public_summary(ex),
                "imported_from": str(p),
                "message": "Transcript already in library.",
            }
    text = _jsonl_to_text(p)
    if len(text) < 80:
        return {"ok": False, "error": "transcript_empty", "message": "Transcript too short or unreadable."}
    auto_label = label.strip() or f"Transcript: {p.stem[:36]}"
    row = save_extract(
        label=auto_label,
        text=text,
        tags=tags or ["THREAD-CHAT-CONSOLIDATION"],
        imported_from=str(p),
    )
    if row.get("ok"):
        row["imported_from"] = str(p)
    return row


def list_extracts() -> list[dict]:
    EXTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for path in sorted(EXTRACTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["id"] = path.stem
            if data.get("text"):
                fresh = _fresh_parsed(data)
                stale = json.dumps(data.get("parsed") or {}, sort_keys=True) != json.dumps(fresh, sort_keys=True)
                data["parsed"] = fresh
                if stale:
                    data["re_parsed_at"] = _now()
                    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            rows.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return rows


def save_extract(*, label: str, text: str, tags: list | str | None = None, imported_from: str | None = None) -> dict:
    text = (text or "").strip()
    if len(text) < 40:
        return {"ok": False, "error": "paste_too_short", "message": "Paste a CHAT EXTRACT document (or raw chat) — at least a few lines."}
    if imported_from:
        for ex in list_extracts():
            if ex.get("imported_from") == imported_from:
                return {
                    "ok": True,
                    "skipped": True,
                    "duplicate": True,
                    "extract": _extract_public_summary(ex),
                    "imported_from": imported_from,
                    "message": "This transcript is already in your library.",
                }
    existing = _find_duplicate_extract(text)
    if existing:
        return {
            "ok": True,
            "skipped": True,
            "duplicate": True,
            "extract": _extract_public_summary(existing),
            "message": f"Duplicate of «{existing.get('label') or existing.get('id')}» — not saved again.",
        }
    EXTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    eid = uuid.uuid4().hex[:12]
    parsed = parse_extract(text)
    auto_label = label.strip() or parsed.get("title") or f"Chat {eid[:6]}"
    norm_tags = _normalize_tags(tags) or _normalize_tags(parsed.get("merge_tags"))
    row = {
        "id": eid,
        "label": auto_label,
        "text": text,
        "parsed": parsed,
        "chars": len(text),
        "content_sha256": _sha256_text(text),
        "saved_at": _now(),
        "tags": norm_tags,
        "weak": _extract_is_weak(parsed),
        "raw_paste": bool(parsed.get("raw_paste")),
    }
    if imported_from:
        row["imported_from"] = imported_from
    out_path = EXTRACTS_DIR / f"{eid}.json"
    out_path.write_text(json.dumps(row, indent=2), encoding="utf-8")
    if _extract_is_weak(parsed) or parsed.get("raw_paste"):
        row = structure_extract_record(json.loads(out_path.read_text(encoding="utf-8")))
        row["id"] = eid
        out_path.write_text(json.dumps(row, indent=2), encoding="utf-8")
        parsed = row.get("parsed") or {}
    manifest = append_manifest_row(
        row_id=f"EXT-CHAT-{eid[:8]}",
        source_type="CHAT_UNIFY",
        layer="A — Trigger",
        pointer=_manifest_pointer(out_path),
        thread=", ".join(norm_tags) if norm_tags else "THREAD-CHAT-CONSOLIDATION",
        verdict="Pointer — founder local extract",
    )
    return {"ok": True, "extract": row, "manifest": manifest}


def get_extract(eid: str) -> dict:
    path = EXTRACTS_DIR / f"{eid}.json"
    if not path.is_file():
        return {"ok": False, "error": "not_found"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["id"] = path.stem
        if data.get("text"):
            parsed = parse_extract(data["text"])
            data["parsed"] = parsed
            data["weak"] = _extract_is_weak(parsed)
            data["raw_paste"] = bool(parsed.get("raw_paste"))
        return {"ok": True, "extract": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"ok": False, "error": str(e)}


def delete_extract(eid: str) -> dict:
    path = EXTRACTS_DIR / f"{eid}.json"
    if not path.is_file():
        return {"ok": False, "error": "not_found"}
    path.unlink()
    return {"ok": True, "deleted": eid}


def merge_quality_report(extracts: list[dict]) -> dict:
    weak: list[dict] = []
    for ex in extracts:
        parsed = ex.get("parsed") or {}
        if _extract_is_weak(parsed):
            weak.append(
                {
                    "id": ex.get("id"),
                    "label": ex.get("label"),
                    "raw_paste": bool(parsed.get("raw_paste")),
                }
            )
    return {
        "ok": len(weak) == 0,
        "weak_count": len(weak),
        "weak": weak,
        "message": (
            "Run Send extract prompt → Cursor in each chat, then re-save."
            if weak
            else "All extracts have decisions or threads."
        ),
    }


def run_unify(*, ids: list[str] | None = None, force: bool = False) -> dict:
    extracts = list_extracts()
    if ids:
        idset = set(ids)
        extracts = [e for e in extracts if e.get("id") in idset]
    if not extracts:
        return {"ok": False, "error": "no_extracts", "message": "Save at least one chat extract first."}
    quality = merge_quality_report(extracts)
    if quality["weak_count"] and not force:
        return {
            "ok": False,
            "error": "merge_quality_gate",
            "message": quality["message"],
            "quality": quality,
        }
    contradictions = detect_contradictions(extracts)
    brief = build_unified_brief(extracts, contradictions)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": True,
        "built_at": _now(),
        "extract_count": len(extracts),
        "contradiction_count": len(contradictions),
        "contradictions": contradictions,
        "unified_brief": brief,
        "extract_ids": [e.get("id") for e in extracts],
    }
    UNIFIED_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    receipt = write_unify_receipt(payload, founder_tap=True)
    payload["receipt"] = receipt
    try:
        from n8n_chat_unify_wire_v1 import notify_merge  # noqa: WPS433

        n8n = notify_merge(
            {
                "extract_count": payload.get("extract_count"),
                "contradiction_count": payload.get("contradiction_count"),
                "brief_chars": len(brief),
                "receipt_path": receipt.get("path"),
                "extract_ids": payload.get("extract_ids") or [],
            }
        )
        payload["n8n_notify"] = n8n
    except Exception as e:
        payload["n8n_notify"] = {"ok": False, "error": str(e)}
    payload["quality"] = quality
    all_tags: list[str] = []
    for ex in extracts:
        all_tags.extend(ex.get("tags") or [])
    tags_joined = ", ".join(dict.fromkeys(all_tags)) or "THREAD-CHAT-CONSOLIDATION"
    payload["manifest"] = append_manifest_row(
        row_id=f"EXT-CHAT-UNIFY-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        source_type="CHAT_UNIFY",
        layer="B — Gather",
        pointer=_manifest_pointer(UNIFIED_PATH),
        thread=tags_joined,
        verdict=f"Unified brief · {len(extracts)} chats · {len(contradictions)} contradictions",
    )
    return payload


def build_report() -> dict:
    last = None
    if UNIFIED_PATH.is_file():
        try:
            last = json.loads(UNIFIED_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            last = None
    extracts = list_extracts()
    quality = merge_quality_report(extracts)
    n8n_wire: dict = {"wired": False}
    try:
        from n8n_chat_unify_wire_v1 import wire_status  # noqa: WPS433

        n8n_wire = wire_status()
    except Exception as e:
        n8n_wire = {"wired": False, "error": str(e)}
    try:
        from ai_unify_api_v1 import status_payload  # noqa: WPS433

        ai_api = status_payload()
    except Exception as e:
        ai_api = {"ok": False, "error": str(e)}
    try:
        from founder_glance_cockpit_v1 import build_ui_contract  # noqa: WPS433

        ui_contract = build_ui_contract(
            "chat_unify",
            port=int(os.environ.get("CHAT_UNIFY_PORT", "13023")),
        )
    except Exception:
        ui_contract = {"ui_mode": "founder_glance", "version": "1.4.0"}
    return {
        "ok": True,
        "app": "chat-unify",
        "built_at": _now(),
        "quality": quality,
        "extracts": [
            {
                "id": e.get("id"),
                "label": e.get("label"),
                "chars": e.get("chars"),
                "saved_at": e.get("saved_at"),
                "title": (e.get("parsed") or {}).get("title"),
                "archive": (e.get("parsed") or {}).get("archive"),
                "decision_count": len((e.get("parsed") or {}).get("decisions") or []),
                "thread_count": len((e.get("parsed") or {}).get("threads") or []),
                "raw_paste": bool((e.get("parsed") or {}).get("raw_paste")),
                "weak": _extract_is_weak(e.get("parsed") or {}),
                "structured": bool(e.get("structured")),
                "tags": e.get("tags") or [],
                "imported_from": e.get("imported_from"),
            }
            for e in extracts
        ],
        "suggested_tags": list(SUGGESTED_TAGS),
        "transcript_candidates": list_transcript_candidates(8),
        "last_unified": last,
        "prompts": {
            "extract": _load_prompt(EXTRACT_PROMPT_PATH),
            "unify": _load_prompt(UNIFY_PROMPT_PATH),
        },
        "state_dir": str(STATE_DIR),
        "mini_app_url": f"http://127.0.0.1:{os.environ.get('CHAT_UNIFY_PORT', '13023')}/",
        "standalone": True,
        "version": "1.4.0",
        "ui_contract": ui_contract,
        "commercial_grade": True,
        "privacy": "Extracts stay local. AI polish/critique calls OpenRouter or Gemini only when you tap those buttons.",
        "n8n_wire": n8n_wire,
        "ai_api": ai_api,
        "cursor_roots": ["~/.cursor/projects/**/agent-transcripts"],
    }


def handle_action(body: dict) -> dict:
    action = (body.get("action") or "report").strip().lower()
    if action == "report":
        return build_report()
    if action == "save_extract":
        return save_extract(
            label=body.get("label") or "",
            text=body.get("text") or "",
            tags=body.get("tags"),
        )
    if action == "get_extract":
        return get_extract((body.get("id") or "").strip())
    if action == "delete_extract":
        return delete_extract((body.get("id") or "").strip())
    if action == "unify":
        ids = body.get("ids")
        if ids is not None and not isinstance(ids, list):
            ids = None
        return run_unify(ids=ids, force=bool(body.get("force")))
    if action == "export_brief":
        return export_brief_to_disk()
    if action == "import_transcript":
        return import_transcript(
            path=body.get("path") or "",
            label=body.get("label") or "",
            tags=body.get("tags"),
        )
    if action in ("import_latest_transcript", "import_latest"):
        return import_latest_transcript(tags=body.get("tags"))
    if action == "list_extracts":
        rows = list_extracts()
        return {
            "ok": True,
            "extracts": [_extract_public_summary(ex) for ex in rows],
            "count": len(rows),
        }
    if action in ("structure_all", "upgrade_all_weak"):
        return upgrade_all_weak()
    if action in ("structure_one", "upgrade_extract"):
        return upgrade_extract((body.get("id") or "").strip())
    if action == "list_transcripts":
        return {"ok": True, "candidates": list_transcript_candidates(int(body.get("limit") or 12))}
    if action == "merge_quality":
        extracts = list_extracts()
        ids = body.get("ids")
        if isinstance(ids, list) and ids:
            idset = set(ids)
            extracts = [e for e in extracts if e.get("id") in idset]
        report = merge_quality_report(extracts)
        return {"ok": True, "quality": report, **{k: v for k, v in report.items() if k != "ok"}}
    if action == "send_extract_prompt":
        from clipboard_safe import clipboard_paste_into_cursor  # noqa: WPS433

        text = _load_prompt(EXTRACT_PROMPT_PATH)
        if not text:
            return {"ok": False, "error": "extract_prompt_missing"}
        r = clipboard_paste_into_cursor(text, allow_automation=True)
        ok = bool(r.get("ok"))
        if not ok:
            try:
                import subprocess

                subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=False)
                return {
                    "ok": True,
                    "clipboard_fallback": True,
                    "message": "Copied extract prompt — paste in Cursor (automation blocked).",
                }
            except OSError:
                pass
        return {
            "ok": ok,
            **r,
            "message": "Extract prompt sent to Cursor — run in each chat to close.",
        }
    if action == "send_unify_prompt":
        from clipboard_safe import clipboard_paste_into_cursor  # noqa: WPS433

        text = _load_prompt(UNIFY_PROMPT_PATH)
        last = build_report().get("last_unified") or {}
        brief = last.get("unified_brief") or ""
        if brief:
            text = f"{text}\n\n---\n\n# PASTED EXTRACTS (local merge)\n\n{brief}"
        if not text:
            return {"ok": False, "error": "unify_prompt_missing"}
        r = clipboard_paste_into_cursor(text, allow_automation=True)
        ok = bool(r.get("ok"))
        if not ok:
            try:
                import subprocess

                subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=False)
                return {
                    "ok": True,
                    "clipboard_fallback": True,
                    "message": "Copied unify prompt + brief — paste in Cursor.",
                }
            except OSError:
                pass
        return {
            "ok": ok,
            **r,
            "message": "Unify prompt + local brief sent to Cursor." if ok else r.get("message"),
        }
    if action == "wire_n8n":
        from n8n_chat_unify_wire_v1 import wire_all  # noqa: WPS433

        return wire_all(import_cursor=bool(body.get("import_cursor", True)), cursor_limit=int(body.get("limit") or 2))
    if action == "sync_cursor":
        from n8n_chat_unify_wire_v1 import sync_cursor_transcripts  # noqa: WPS433

        return sync_cursor_transcripts(limit=int(body.get("limit") or 3))
    if action == "n8n_status":
        from n8n_chat_unify_wire_v1 import wire_status  # noqa: WPS433

        return {"ok": True, **wire_status()}
    if action == "ai_status":
        from ai_unify_api_v1 import status_payload  # noqa: WPS433

        row = status_payload()
        row["ok"] = True
        return row
    if action == "ai_chat":
        from ai_unify_api_v1 import handle_action as ai_handle  # noqa: WPS433

        return ai_handle(
            {
                "action": "chat",
                "user": body.get("user") or body.get("text") or "",
                "system": body.get("system") or "",
                "provider": body.get("provider") or "auto",
                "model": body.get("model"),
            }
        )
    if action == "ai_polish":
        from ai_unify_api_v1 import polish_brief  # noqa: WPS433

        last = build_report().get("last_unified") or {}
        text = body.get("text") or body.get("brief") or last.get("unified_brief") or ""
        result = polish_brief(text, provider=body.get("provider") or "auto", model=body.get("model"))
        if result.get("ok") and result.get("response"):
            try:
                from n8n_chat_unify_wire_v1 import notify_merge  # noqa: WPS433

                notify_merge(
                    {
                        "event": "ai_polish",
                        "extract_count": last.get("extract_count") or 0,
                        "chars": len(result.get("response") or ""),
                        "provider": result.get("provider") or "auto",
                    }
                )
            except Exception:
                pass
        return result
    if action == "ai_critique":
        from ai_unify_api_v1 import critique_brief  # noqa: WPS433

        last = build_report().get("last_unified") or {}
        text = body.get("text") or body.get("brief") or last.get("unified_brief") or ""
        result = critique_brief(text, provider=body.get("provider") or "auto", model=body.get("model"))
        if result.get("ok") and result.get("response"):
            try:
                from n8n_chat_unify_wire_v1 import notify_merge  # noqa: WPS433

                notify_merge(
                    {
                        "event": "ai_critique",
                        "extract_count": last.get("extract_count") or 0,
                        "chars": len(result.get("response") or ""),
                    }
                )
            except Exception:
                pass
        return result
    return {"ok": False, "error": f"unknown_action:{action}"}
