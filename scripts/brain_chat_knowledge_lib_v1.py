#!/usr/bin/env python3
"""Shared Brain chatbot knowledge — strip, chunk, lane, BM25 search."""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STRIP_PATTERNS = [
    re.compile(r"<script[\s\S]*?</script>", re.I),
    re.compile(r"<style[\s\S]*?</style>", re.I),
    re.compile(r"<!--[\s\S]*?-->"),
]
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_./-]{1,}")

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)OPENROUTER_API_KEY"),
    re.compile(r"~/Desktop/SourceA"),
    re.compile(r"/Users/\S+"),
    re.compile(r"com\.sourcea\."),
]

SKIP_HTML_PARTS = {
    "reference",
    "legacy-full-home",
    "pulse-founder",
}

PINNED_STEMS = {
    "positioning-public",
    "positioning-law",
    "pricing-matrix",
    "offer-48h",
    "sandbox-freemium",
    "forge-runtime",
    "developer-tools",
    "products-catalog",
    "kernel-overview",
    "site-map",
    "brain-public-rules",
    "trust-signals-public-v1",
    "sourcea-landing-cta-v1",
}

CURATED_DIR_MARKERS = (
    "/distilled/",
    "/manual/",
    "/rules/",
    "chatbot-knowledge/distilled/",
    "chatbot-knowledge/manual/",
    "chatbot-knowledge/rules/",
)


def is_curated_source(path: str) -> bool:
    p = (path or "").replace("\\", "/").lower()
    return any(m in p for m in CURATED_DIR_MARKERS)


def source_file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def strip_secrets(text: str) -> str:
    for pat in SECRET_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


def scrub_public_voice(text: str) -> str:
    """Sync-time only — prefer failing sync over silent rewrite at runtime."""
    return str(text or "")


def strip_html(html: str) -> str:
    text = html
    for pat in STRIP_PATTERNS:
        text = pat.sub(" ", text)
    text = unescape(TAG_RE.sub(" ", text))
    return strip_secrets(WS_RE.sub(" ", text).strip())


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def infer_lane(rel_path: str, page_hint: str = "") -> str:
    p = rel_path.lower()
    hint = (page_hint or "").lower()
    if "investor" in p or hint == "investor":
        return "investor"
    if any(x in p for x in ("forge", "kernel", "eval", "platform", "cursor", "chat-unify", "unify")):
        return "developer"
    if any(x in p for x in ("pricing", "offer", "sandbox", "proof", "case-stud", "start", "funnel", "growth")):
        return "buyer"
    if any(x in p for x in ("factory", "loop", "security", "trust", "team", "learn")):
        return "core"
    return "core"


def path_to_www_url(rel_path: str) -> str:
    """Map repo path under green-unified to public URL."""
    p = rel_path.replace("\\", "/")
    if p in ("index.html", "home.html", "founder-home.html"):
        return "https://sourcea.app/"
    if p.endswith("/index.html"):
        p = p[: -len("index.html")]
    elif p.endswith(".html"):
        p = p[: -len(".html")]
    p = p.strip("/")
    if not p or p in ("index", "home", "founder-home"):
        return "https://sourcea.app/"
    return f"https://sourcea.app/sourcea/{p}"


def extract_html_sections(html: str) -> list[str]:
    blocks: list[str] = []
    title_m = re.search(r"<title[^>]*>([\s\S]*?)</title>", html, re.I)
    if title_m:
        t = strip_html(title_m.group(1))
        if t:
            blocks.append(f"## Page title\n{t}")
    desc_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if desc_m:
        blocks.append(f"## Summary\n{strip_html(desc_m.group(1))}")
    for m in re.finditer(r"<h[1-3][^>]*>([\s\S]*?)</h[1-3]>", html, re.I):
        heading = strip_html(m.group(1))
        if heading and len(heading) > 2:
            blocks.append(f"## {heading}")
    # paragraph chunks
    for m in re.finditer(r"<p[^>]*>([\s\S]*?)</p>", html, re.I):
        para = strip_html(m.group(1))
        if len(para) > 60:
            blocks.append(para)
    if not blocks:
        body = strip_html(html)
        if body:
            blocks.append(body[:6000])
    return blocks


def chunk_text(text: str, *, max_chars: int = 1800, overlap: int = 120) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if len(text) >= 40 else []
    parts = re.split(r"(?=^## )", text, flags=re.M)
    out: list[str] = []
    for part in parts:
        part = part.strip()
        if len(part) <= max_chars:
            if len(part) >= 40:
                out.append(part)
            continue
        start = 0
        while start < len(part):
            end = min(start + max_chars, len(part))
            slice_ = part[start:end].strip()
            if len(slice_) >= 40:
                out.append(slice_)
            if end >= len(part):
                break
            start = max(end - overlap, start + 1)
    return out


def json_to_markdown(data: dict | list, title: str) -> str:
    """Public-safe JSON → readable markdown (no deep nesting secrets)."""
    lines = [f"# {title}", ""]

    def walk(obj, depth=0):
        if depth > 4:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in {"api_key", "secret", "password", "token", "private_key"}:
                    continue
                if isinstance(v, (dict, list)):
                    lines.append(f"{'#' * min(depth + 2, 4)} {k}")
                    walk(v, depth + 1)
                elif v is not None and str(v).strip():
                    sv = strip_secrets(str(v))
                    sv = sv.replace("Noetfield", "SourceA")
                    if len(sv) < 500:
                        lines.append(f"- **{k}**: {sv}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:30]):
                if isinstance(item, dict):
                    label = item.get("title") or item.get("name") or item.get("id") or f"item {i+1}"
                    lines.append(f"## {label}")
                    walk(item, depth + 1)
                elif item is not None:
                    lines.append(f"- {strip_secrets(str(item))[:300]}")

    walk(data)
    return "\n".join(lines).strip()


def bm25_score(query_tokens: list[str], doc_tokens: list[str], df: Counter, N: int, avgdl: float) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    k1, b = 1.2, 0.75
    dl = len(doc_tokens)
    dcount = Counter(doc_tokens)
    score = 0.0
    for t in query_tokens:
        if t not in dcount:
            continue
        tf = dcount[t]
        idf = math.log(1 + (N - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5))
        score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / max(avgdl, 1)))
    return score


def classify_intent(query: str) -> str:
    q = query.lower()
    if any(x in q for x in ("invest", "fund", "raise", "valuation", "cap table")):
        return "investor"
    if any(x in q for x in ("cursor", "developer", "api", "code", "forge terminal", "kernel", "pypi", "npm", "deploy", "chat unify", "unify")):
        return "developer"
    if any(x in q for x in ("factory", "factories", "workflow", "video", "avatar", "outbound")):
        return "developer"
    if any(x in q for x in ("price", "pricing", "cost", "how much", "$", "buy", "sandbox", "demo", "proof", "offer", "48")):
        return "buyer"
    if any(x in q for x in ("partner", "agency", "procurement", "enterprise")):
        return "partner"
    return "core"


def infer_page_context(page_path: str = "", sa_page: str = "") -> dict:
    path = (page_path or "/").lower().rstrip("/") or "/"
    hint = (sa_page or "").lower()
    ctx: dict = {"page_path": path, "page_lane": "core", "segments": []}
    if "forge" in hint or "/forge" in path:
        ctx["page_lane"] = "developer"
        ctx["segments"].extend(["forge", "terminal", "forge-runtime"])
    if "pricing" in path or "offer" in path:
        ctx["page_lane"] = "buyer"
        ctx["segments"].extend(["pricing", "offer", "pricing-matrix"])
    if "factor" in path:
        ctx["page_lane"] = "developer"
        ctx["segments"].extend(["factories", "factory", "products-catalog"])
    if "investor" in path:
        ctx["page_lane"] = "investor"
        ctx["segments"].append("investor")
    if any(x in path for x in ("proof", "trust", "security")):
        ctx["page_lane"] = "buyer"
        ctx["segments"].extend(["proof", "trust", "security"])
    if any(x in path for x in ("start", "sandbox", "mvp")):
        ctx["page_lane"] = "buyer"
        ctx["segments"].extend(["sandbox", "start", "48h", "mvp"])
    if "scenario" in path or path in ("/", "/sourcea"):
        ctx["segments"].extend(["positioning", "founder-home", "scenario"])
    return ctx


def page_boost(chunk: dict, page_ctx: dict | None) -> float:
    if not page_ctx:
        return 0.0
    boost = 0.0
    path = (chunk.get("source_path") or "").lower()
    www = (chunk.get("www_url") or "").lower()
    page_path = (page_ctx.get("page_path") or "").lower()
    if page_ctx.get("page_lane") and chunk.get("lane") == page_ctx["page_lane"]:
        boost += 2.5
    for seg in page_ctx.get("segments") or []:
        if seg in path or seg in www:
            boost += 2.0
    if page_path and page_path != "/":
        parts = [p for p in page_path.split("/") if p]
        if parts:
            slug = parts[-1]
            if slug in path or slug in www:
                boost += 2.5
    return boost


def search_chunks(
    chunks: list[dict],
    query: str,
    *,
    k: int = 8,
    lane: str | None = None,
    page_ctx: dict | None = None,
) -> list[dict]:
    qtok = tokenize(query)
    if not qtok:
        return chunks[:k]
    doc_tokens_list = [tokenize(c.get("content") or "") for c in chunks]
    N = len(chunks) or 1
    df: Counter = Counter()
    for dt in doc_tokens_list:
        for t in set(dt):
            df[t] += 1
    avgdl = sum(len(dt) for dt in doc_tokens_list) / N
    intent = lane or classify_intent(query)
    scored: list[tuple[float, dict]] = []
    for c, dt in zip(chunks, doc_tokens_list):
        s = bm25_score(qtok, dt, df, N, avgdl)
        if c.get("pinned"):
            s += 2.0
        if c.get("kind") in ("rule", "rules") or c.get("lane") == "rules":
            s += 1.0
        if c.get("lane") == intent:
            s += 1.5
        s += page_boost(c, page_ctx)
        if s > 0:
            scored.append((s, {**c, "score": round(s, 4)}))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]


def make_chunk(
    *,
    chunk_id: str,
    lane: str,
    source_path: str,
    content: str,
    www_url: str | None = None,
    pinned: bool = False,
    kind: str = "doc",
) -> dict:
    content = strip_secrets(content.strip())[:2000]
    return {
        "id": chunk_id,
        "lane": lane,
        "source_path": source_path,
        "www_url": www_url,
        "content": content,
        "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
        "pinned": pinned,
        "kind": kind,
        "tokens": tokenize(content)[:80],
    }
