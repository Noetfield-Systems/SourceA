#!/usr/bin/env python3
"""Best Loop OQG — output_clean_pct scoring (artifact quality · not founder approval).

Law: docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md
Receipt: ~/.sina/best-loop-oqg-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "best-loop-oqg-receipt-v1.json"
HISTORY = SINA / "best-loop-oqg-history-v1.jsonl"
EMAILS_JSON = ROOT / "data" / "commercial" / "canada-priority-a-emails-v1.json"
COPY_SAFETY = SINA / "brain" / "COPY_SAFETY_AND_CLAIMS_REGISTRY_v1.yaml"
W3_PACK_ROOT = SINA / "outbound"

PLACEHOLDER_RES = [
    re.compile(r"\[First name\]", re.I),
    re.compile(r"\[calendar link\]", re.I),
    re.compile(r"\[Full name\]", re.I),
    re.compile(r"\[Phone\]", re.I),
    re.compile(r"\[True relationship", re.I),
    re.compile(r"\[Canadian address", re.I),
    re.compile(r"\[relationship basis\]", re.I),
    re.compile(r"PASTE_RECIPIENT", re.I),
]

W3_APPROVED = ("ocree", "fundmore")
WAIVERS_TEMPLATE = ROOT / "data" / "commercial" / "oqg-waiver-v1.json"
WAIVERS_LIVE = SINA / "oqg-waiver-v1.json"
OQG_BAR = 90
FEFS_LAW = "docs/SOURCEA_FOUNDER_EMAIL_FACTORY_STANDARD_LOCKED_v1.md"

BUZZWORDS = frozenset(
    {"governance", "ledger", "replay", "dispatch", "attestation", "tokenization", "runtime", "subordinates"}
)
SCRAPE_OPEN_RE = re.compile(
    r"(are public on|leadership contact|public on \w+\.(com|ca|ai)|"
    r"Your OSC-registered|I saw your platform|Saw \w+'s live)",
    re.I,
)


def check_scrape_open(text: str) -> dict:
    """U049 — scrape-style opener SSOT (shared CIL hard-fail + OQG FEFS R1)."""
    match = SCRAPE_OPEN_RE.search(text or "")
    return {
        "ok": match is None,
        "id": "scrape_open",
        "matched": match.group(0) if match else None,
        "hard_fail": match is not None,
        "upgrade": "U049",
    }
# U001 — salvage hard_fail: generic_skeleton_weve_been_spending_time_with_teams
GENERIC_SKELETON_RE = re.compile(
    r"(?:we'?ve been )?spending time with teams|"
    r"teams using ai|"
    r"helping teams get value from ai|"
    r"one pattern keeps appearing",
    re.I,
)


def check_generic_skeleton(text: str) -> dict:
    """U001 — deterministic generic-skeleton detector (OQG/FEFS hard fail)."""
    match = GENERIC_SKELETON_RE.search(text or "")
    return {
        "ok": match is None,
        "pattern": "generic_skeleton_weve_been_spending_time_with_teams",
        "matched": match.group(0) if match else None,
        "hard_fail": match is not None,
    }
SUBJECT_FLUFF_RE = re.compile(
    r"\b(quick question|partnership opportunity|synergy|touching base|"
    r"just checking in|introductory call|exciting opportunity)\b",
    re.I,
)
# U002 — allow known proper-noun stacks (Ocree Capital Winnipeg, etc.)
PROPER_NOUN_ALLOW = re.compile(
    r"\b(Ocree|Fundmore|Winnipeg|Capital|Region|Canada|Ontario|British Columbia|"
    r"Toronto|Vancouver|Calgary|Edmonton|Montreal|Royal|Bank|Chris|Aram|Anne|"
    r"Noetfield|Systems|TrustField|Fundmore\.ai)\b"
)
MAX_ATTACH_BYTES = 5 * 1024 * 1024
URL_CACHE_PATH = SINA / "oqg-url-cache-v1.json"
URL_CACHE_TTL_S = 86400
DEFENSIVE_RE = re.compile(
    r"not custody|not payment|advisory only|not fintrac|no payment rails",
    re.I,
)
ARCH_RE = re.compile(
    r"evaluate\s*→|enforce\s*→|execution receipt chain|tamper-evidence|Trust Ledger Entry",
    re.I,
)
REFUND_RE = re.compile(r"refund|deposit|\$\d+k|\bcad \$", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_forbidden_phrases() -> list[str]:
    if not COPY_SAFETY.is_file():
        return []
    phrases: list[str] = []
    for line in COPY_SAFETY.read_text(encoding="utf-8").splitlines():
        m = re.search(r'phrase:\s*["\']?(.+?)["\']?\s*$', line)
        if m:
            phrases.append(m.group(1).strip())
    return phrases


def _url_ok(url: str, *, timeout: float = 4.0) -> bool:
    if not url or not url.startswith("http"):
        return False
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except (urllib.error.URLError, OSError, ValueError):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return 200 <= resp.getcode() < 400
        except (urllib.error.URLError, OSError, ValueError):
            return False


def _url_ok_cached(url: str) -> bool:
    """U009 — 24h reachability cache for interest-asset URLs."""
    if not url or not url.startswith("http"):
        return False
    now = datetime.now(timezone.utc).timestamp()
    cache = _read_json(URL_CACHE_PATH)
    entries: dict = cache.get("entries") or {}
    row = entries.get(url)
    if row and (now - float(row.get("at") or 0)) < URL_CACHE_TTL_S:
        return bool(row.get("ok"))
    ok = _url_ok(url)
    entries[url] = {"ok": ok, "at": now}
    SINA.mkdir(parents=True, exist_ok=True)
    URL_CACHE_PATH.write_text(
        json.dumps({"schema": "oqg-url-cache-v1", "entries": entries}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ok


def check_url_reachability(text: str) -> dict:
    """U009 — 24h reachability cache for interest-asset URLs; stale unreachable flagged once."""
    urls = re.findall(r"https?://[^\s\])<>]+", text)
    if not urls:
        return {
            "ok": False,
            "issues": ["no_url"],
            "cached": 0,
            "probed": 0,
            "cache_ttl_s": URL_CACHE_TTL_S,
            "hard_fail": False,
        }
    now = datetime.now(timezone.utc).timestamp()
    cache = _read_json(URL_CACHE_PATH)
    entries: dict = cache.get("entries") or {}
    cached_hits = 0
    live_probes = 0
    ok_any = False
    for u in urls[:3]:
        url = u.rstrip(".,)")
        row = entries.get(url)
        if row and (now - float(row.get("at") or 0)) < URL_CACHE_TTL_S:
            cached_hits += 1
        else:
            live_probes += 1
        if _url_ok_cached(url):
            ok_any = True
    issues: list[str] = []
    if not ok_any:
        issues.append("url_not_reachable")
    return {
        "ok": ok_any,
        "issues": issues,
        "cached": cached_hits,
        "probed": live_probes,
        "cache_ttl_s": URL_CACHE_TTL_S,
        "hard_fail": False,
    }


def _score_copy_safety(text: str, *, max_pts: int = 25) -> tuple[int, list[str]]:
    forbidden = _load_forbidden_phrases()
    hits = [p for p in forbidden if p and p.lower() in text.lower()]
    if not forbidden:
        return max_pts // 2, ["registry_missing_half_credit"]
    if not hits:
        return max_pts, []
    deduct = min(max_pts, len(hits) * 8)
    return max(0, max_pts - deduct), [f"forbidden:{h}" for h in hits[:5]]


def _score_brand_separation(text: str, lane: str, *, max_pts: int = 20) -> tuple[int, list[str]]:
    t = text.lower()
    issues: list[str] = []
    if lane == "TrustField":
        if "noetfield" in t and "separate" not in t:
            issues.append("noetfield_mention_tf_lane")
        if "nf-rd" in t or "copilot governance receipt" in t:
            issues.append("nf_vocabulary_in_tf")
    elif lane == "Noetfield":
        if "fintrac kyb pack" in t:
            issues.append("fintrac_kyb_claim_nf")
        if "trustfield" in t and "separate" not in t and "not " not in t:
            issues.append("trustfield_bleed_nf")
    elif lane in ("SourceA", "fbe_sourcea", "sourcea-factory"):
        if "noetfield" in t and "trustfield" in t and "separate" not in t:
            issues.append("dual_brand_bleed_sa")
        if "nf-rd" in t and "tf-kyb" in t:
            issues.append("sku_cross_bleed_sa")
    deduct = len(issues) * 10
    return max(0, max_pts - deduct), issues


def check_brand_separation(text: str, lane: str) -> dict:
    """U007 — brand separation per lane (NF/TF/SA); cross-brand bleed hard fail."""
    pts, issues = _score_brand_separation(text, lane, max_pts=6)
    bleed = len(issues) > 0
    return {
        "ok": not bleed,
        "points": pts,
        "max": 6,
        "issues": issues,
        "hard_fail": bleed,
        "lane": lane,
    }


def check_relationship_basis(basis: str | None) -> dict:
    """U006 — CASL relationship_basis required on pack metadata."""
    pts, issues = _score_relationship_basis(basis, max_pts=6)
    missing = "missing_relationship_basis" in issues
    return {
        "ok": not missing and pts >= 6,
        "points": pts,
        "max": 6,
        "issues": issues,
        "hard_fail": missing,
    }


def _score_relationship_basis(basis: str | None, *, max_pts: int = 6) -> tuple[int, list[str]]:
    """U006 — CASL relationship_basis required on pack metadata."""
    b = str(basis or "").strip()
    if not b:
        return 0, ["missing_relationship_basis"]
    if len(b) < 12:
        return max_pts // 2, ["basis_too_short"]
    return max_pts, []


def check_subject_fluff(subject: str | None) -> dict:
    """U003 — subject-line marketing fluff gate (partnership/synergy/quick question)."""
    pts, issues = _score_subject_line(subject, max_pts=4)
    return {
        "ok": "subject_fluff" not in issues,
        "points": pts,
        "max": 4,
        "issues": issues,
        "hard_fail": "subject_fluff" in issues,
    }


def _score_subject_line(subject: str | None, *, max_pts: int = 6) -> tuple[int, list[str]]:
    """U003 — subject marketing fluff gate."""
    subj = str(subject or "").strip()
    if not subj:
        return max_pts // 2, ["missing_subject"]
    if SUBJECT_FLUFF_RE.search(subj):
        return 0, ["subject_fluff"]
    return max_pts, []


def _score_placeholders(text: str, *, max_pts: int = 20) -> tuple[int, list[str]]:
    hits = [p.pattern for p in PLACEHOLDER_RES if p.search(text)]
    if not hits:
        return max_pts, []
    return 0, hits


def _score_casl(text: str, *, max_pts: int = 20) -> tuple[int, list[str]]:
    t = text.lower()
    issues: list[str] = []
    if "stop" not in t and "opt out" not in t:
        issues.append("missing_stop_line")
    if "[true relationship" in t or "[relationship basis]" in t:
        issues.append("basis_placeholder")
    if len(t) < 200:
        issues.append("body_too_short")
    deduct = len(issues) * 7
    return max(0, max_pts - deduct), issues


def _score_attach_urls(text: str, attach: Path | None, *, max_pts: int = 15) -> tuple[int, list[str]]:
    url_check = check_url_reachability(text)
    issues: list[str] = list(url_check.get("issues") or [])
    pts = max_pts
    if "no_url" in issues:
        pts -= 2
    elif "url_not_reachable" in issues:
        pts -= 4
    if attach and not attach.is_file():
        issues.append("attach_missing")
        pts -= 7
    elif attach and attach.is_file():
        try:
            if attach.stat().st_size > MAX_ATTACH_BYTES:
                issues.append("attach_too_large")
                pts -= 5
        except OSError:
            issues.append("attach_stat_fail")
            pts -= 3
    return max(0, pts), issues


def check_attach_path(text: str, attach: Path | None) -> dict:
    """U008 — attach path exists + size cap; broken attach hard fails before send."""
    pts, issues = _score_attach_urls(text, attach, max_pts=4)
    attach_hard = any(i in issues for i in ("attach_missing", "attach_too_large", "attach_stat_fail"))
    return {
        "ok": not attach_hard,
        "points": pts,
        "max": 4,
        "issues": issues,
        "hard_fail": attach_hard,
    }


def _word_count_body(text: str) -> int:
    lines: list[str] = []
    for line in text.splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("*") or "Reply **stop**" in t:
            break
        if "@" in t and "." in t and len(t) < 80:
            continue
        lines.append(t)
    return len(" ".join(lines).split())


def check_word_count_sweet_spot(text: str) -> dict:
    """U004 — FEFS word-count tier: 90–110 = 8/8 · 70–140 edge = 4/8."""
    body_words = _word_count_body(text)
    if 90 <= body_words <= 110:
        return {
            "ok": True,
            "word_count": body_words,
            "points": 8,
            "max": 8,
            "band": "sweet_spot",
            "issues": [],
        }
    if 70 <= body_words <= 140:
        return {
            "ok": False,
            "word_count": body_words,
            "points": 4,
            "max": 8,
            "band": "edge",
            "issues": [f"word_count_edge:{body_words}"],
        }
    return {
        "ok": False,
        "word_count": body_words,
        "points": 0,
        "max": 8,
        "band": "fail",
        "issues": [f"word_count_fail:{body_words}"],
    }


def _duplicate_phrase_penalty(text: str) -> tuple[int, list[str]]:
    """U005 — penalize repeated 4-gram phrases; flat deduct once per body."""
    issues: list[str] = []
    norm = re.sub(r"\s+", " ", text.lower())
    words = norm.split()
    seen: dict[str, int] = {}
    for i in range(len(words) - 3):
        phrase = " ".join(words[i : i + 4])
        if len(phrase) < 12:
            continue
        seen[phrase] = seen.get(phrase, 0) + 1
    dups = [p for p, n in seen.items() if n > 1]
    if dups:
        issues.append(f"duplicate_phrase:{dups[0][:40]}")
    deduct = 5 if dups else 0
    return deduct, issues


def check_duplicate_phrase(text: str) -> dict:
    """U005 — repeated 4-gram phrases deduct once only (flat -5)."""
    deduct, issues = _duplicate_phrase_penalty(text)
    return {
        "ok": deduct == 0,
        "deduct": deduct,
        "issues": issues,
        "once_only": True,
    }


def check_noun_stack(text: str) -> dict:
    """U002 — noun-stack penalty with proper-noun allowlist (Ocree Capital Winnipeg)."""
    deduct, issues = _noun_stack_penalty(text)
    return {
        "ok": deduct == 0,
        "deduct": deduct,
        "issues": issues,
        "hard_fail": deduct > 0,
        "allowlist": "PROPER_NOUN_ALLOW",
    }


def _noun_stack_penalty(text: str) -> tuple[int, list[str]]:
    """U002 — penalize 5+ consecutive capitalized generic words; allow proper nouns."""
    issues: list[str] = []
    for m in re.finditer(r"\b(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+\b", text):
        span = m.group(0)
        if PROPER_NOUN_ALLOW.search(span):
            continue
        issues.append(f"noun_stack:{span[:48]}")
        break
    return (6 if issues else 0), issues


def _score_fefs_persuasion(text: str) -> tuple[int, list[dict]]:
    """FEFS R1–R10 persuasion block — max 60 pts."""
    checks: list[dict] = []
    total = 0
    body_words = _word_count_body(text)

    # R1 human opening (10)
    scrape_row = check_scrape_open(text)
    scrape = scrape_row["hard_fail"]
    skeleton = check_generic_skeleton(text)
    r1_issues: list[str] = []
    if scrape:
        r1_issues.append("scrape_open")
    if skeleton["hard_fail"]:
        r1_issues.append("generic_skeleton")
    r1 = 10 if not scrape and not skeleton["hard_fail"] else (0 if skeleton["hard_fail"] else 2)
    total += r1
    checks.append({"id": "fefs_human_opening", "points": r1, "max": 10, "issues": r1_issues})

    # R9 word count (8) — U004 sweet spot 90–110
    wc = check_word_count_sweet_spot(text)
    r9 = wc["points"]
    w_issues = list(wc["issues"])
    body_words = wc["word_count"]
    total += r9
    checks.append({"id": "fefs_word_count", "points": r9, "max": 8, "issues": w_issues, "word_count": body_words})

    # R3 pain before product (10) — pain cues in first 400 chars after greeting
    head = text[:400].lower()
    pain_cues = ("question", "harder", "boards", "regulators", "prove", "evidence", "uncomfortable", "before ")
    product_first = head.startswith("hi") and ("we built" in head or "delivers" in head[:200] or "**trustfield**" in head[:250])
    pain_ok = any(p in head for p in pain_cues) and not product_first
    r3 = 10 if pain_ok else 3
    total += r3
    checks.append(
        {
            "id": "fefs_pain_first",
            "points": r3,
            "max": 10,
            "issues": [] if pain_ok else ["product_before_pain"],
        }
    )

    # R2/R6 one idea no architecture (10)
    arch = ARCH_RE.findall(text)
    arch_n = len(arch)
    r26 = 10 if arch_n == 0 else max(0, 10 - arch_n * 5)
    total += r26
    checks.append({"id": "fefs_no_architecture", "points": r26, "max": 10, "issues": arch[:3] if arch else []})

    # R5 no defensive stack (8)
    def_hits = DEFENSIVE_RE.findall(text)
    r5 = 8 if len(def_hits) <= 1 else max(0, 8 - (len(def_hits) - 1) * 4)
    total += r5
    checks.append({"id": "fefs_no_defensive", "points": r5, "max": 8, "issues": def_hits[:4] if len(def_hits) > 1 else []})

    # R10 no cold refund (6)
    refund = bool(REFUND_RE.search(text))
    r10r = 0 if refund else 6
    total += r10r
    checks.append({"id": "fefs_no_cold_refund", "points": r10r, "max": 6, "issues": ["cold_refund_offer"] if refund else []})

    # R7/R10 curiosity close (8) — U028: question last before link block
    try:
        from icp_curiosity_gate_v1 import check_curiosity_before_link  # noqa: WPS433

        cur = check_curiosity_before_link(text)
        r710 = 8 if cur.get("ok") else 0
        r710_issues = cur.get("issues") or (["no_easy_question"] if not cur.get("ok") else [])
    except Exception:
        pre_sig = text.split("Reply **stop**")[0] if "Reply **stop**" in text else text
        last_q = "?" in pre_sig
        r710 = 8 if last_q else 2
        r710_issues = [] if last_q else ["no_easy_question"]
    total += r710
    checks.append({"id": "fefs_curiosity_close", "points": r710, "max": 8, "issues": r710_issues, "upgrade": "U028"})

    # U029 — one product paragraph max
    try:
        from icp_one_product_line_gate_v1 import check_one_product_line  # noqa: WPS433

        prod = check_one_product_line(text)
        r729 = 6 if prod.get("ok") else 0
        r729_issues = prod.get("issues") or (["two_product_paragraphs"] if not prod.get("ok") else [])
    except Exception:
        r729 = 6
        r729_issues = []
    total += r729
    checks.append(
        {
            "id": "fefs_one_product_line",
            "points": r729,
            "max": 6,
            "issues": r729_issues,
            "upgrade": "U029",
        }
    )

    # R8 buzzword stacking per paragraph (deduct up to 10 from persuasion via separate check)
    buzz_issues: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        if not para.strip():
            continue
        low = para.lower()
        hits = sum(1 for b in BUZZWORDS if b in low)
        if hits > 2:
            buzz_issues.append(f"buzz_stack:{hits}")
    buzz_deduct = min(10, len(buzz_issues) * 4)
    dup = check_duplicate_phrase(text)
    dup_deduct, dup_issues = dup["deduct"], dup["issues"]
    noun = check_noun_stack(text)
    noun_deduct, noun_issues = noun["deduct"], noun["issues"]
    extra = buzz_deduct + dup_deduct + noun_deduct
    total = max(0, total - extra)
    if buzz_issues or dup_issues or noun_issues:
        checks.append(
            {
                "id": "fefs_buzzword_duplicate",
                "points": -extra,
                "max": 0,
                "issues": buzz_issues + dup_issues + noun_issues,
            }
        )

    return min(60, total), checks


def _score_w3_structural(
    text: str,
    lane: str,
    attach: Path | None,
    *,
    subject: str | None = None,
    relationship_basis: str | None = None,
) -> tuple[int, list[dict]]:
    """Structural block — max 40 pts."""
    checks: list[dict] = []
    total = 0
    for name, fn, mx in (
        ("copy_safety", lambda: _score_copy_safety(text, max_pts=8), 8),
        ("brand_separation", lambda: _score_brand_separation(text, lane, max_pts=6), 6),
        ("no_placeholders", lambda: _score_placeholders(text, max_pts=6), 6),
        ("casl_basis", lambda: _score_casl(text, max_pts=6), 6),
        ("relationship_basis_field", lambda: _score_relationship_basis(relationship_basis, max_pts=6), 6),
        ("subject_fluff", lambda: _score_subject_line(subject, max_pts=4), 4),
        ("attach_urls", lambda: _score_attach_urls(text, attach, max_pts=4), 4),
    ):
        pts, issues = fn()
        # Scale down from old max to new max proportionally handled by max_pts above
        total += pts
        checks.append({"id": name, "points": pts, "max": mx, "issues": issues})
    return min(40, total), checks


def score_w3_email(
    *,
    account_id: str,
    body: str,
    lane: str,
    attach: Path | None = None,
    subject: str | None = None,
    relationship_basis: str | None = None,
) -> dict:
    struct_pts, struct_checks = _score_w3_structural(
        body,
        lane,
        attach,
        subject=subject,
        relationship_basis=relationship_basis,
    )
    pers_pts, pers_checks = _score_fefs_persuasion(body)
    checks = struct_checks + pers_checks
    total = struct_pts + pers_pts
    clean = min(100, max(0, total))
    skeleton = check_generic_skeleton(body)
    if skeleton["hard_fail"]:
        clean = min(clean, OQG_BAR - 1)
    rel_basis = check_relationship_basis(relationship_basis)
    if rel_basis["hard_fail"]:
        clean = min(clean, OQG_BAR - 1)
    brand = check_brand_separation(body, lane)
    if brand["hard_fail"]:
        clean = min(clean, OQG_BAR - 1)
    attach_check = check_attach_path(body, attach)
    if attach_check["hard_fail"]:
        clean = min(clean, OQG_BAR - 1)
    noun = check_noun_stack(body)
    subject_fluff = check_subject_fluff(subject)
    word_count = check_word_count_sweet_spot(body)
    duplicate_phrase = check_duplicate_phrase(body)
    url_reachability = check_url_reachability(body)
    return {
        "account_id": account_id,
        "lane": lane,
        "output_clean_pct": clean,
        "output_clean_now": clean,
        "structural_pct": struct_pts,
        "persuasion_fefs_pct": pers_pts,
        "oqg_pass": clean >= OQG_BAR
        and not skeleton["hard_fail"]
        and not rel_basis["hard_fail"]
        and not brand["hard_fail"]
        and not attach_check["hard_fail"],
        "generic_skeleton": skeleton,
        "relationship_basis": rel_basis,
        "brand_separation": brand,
        "attach_path": attach_check,
        "url_reachability": url_reachability,
        "noun_stack": noun,
        "subject_fluff": subject_fluff,
        "word_count_sweet_spot": word_count,
        "duplicate_phrase": duplicate_phrase,
        "trust_mode": _trust_mode(clean),
        "fefs_law": FEFS_LAW,
        "checks": checks,
    }


OQG_EXPORTED_CHECK_KEYS = (
    "generic_skeleton",
    "relationship_basis",
    "brand_separation",
    "attach_path",
    "url_reachability",
    "noun_stack",
    "subject_fluff",
    "word_count_sweet_spot",
    "duplicate_phrase",
)


def export_oqg_checks_bundle(scored: dict) -> dict:
    """U010 — deterministic OQG export for pack.json compile stamp."""
    line_items = list(scored.get("checks") or [])
    exported = {k: scored[k] for k in OQG_EXPORTED_CHECK_KEYS if k in scored}
    return {
        "schema": "oqg-checks-bundle-v1",
        "upgrade": "U010",
        "at": _now(),
        "line_items": line_items,
        "exported": exported,
        "oqg_pass": bool(scored.get("oqg_pass")),
        "output_clean_pct": int(scored.get("output_clean_pct") or 0),
    }


def _w3_pack_meta(account_id: str) -> dict:
    return _read_json(W3_PACK_ROOT / f"w3-canada-{account_id}" / "pack.json")


def _w3_body_for(account_id: str) -> tuple[str, str, Path | None, str | None, str | None]:
    pack_dir = W3_PACK_ROOT / f"w3-canada-{account_id}"
    body_path = pack_dir / "body.txt"
    if body_path.is_file():
        body = body_path.read_text(encoding="utf-8")
        pack = _read_json(pack_dir / "pack.json")
        lane = str(pack.get("lane") or "")
        attach = Path(pack["attach"]) if pack.get("attach") else None
        return body, lane, attach, pack.get("subject"), pack.get("relationship_basis")

    data = _read_json(EMAILS_JSON)
    for row in data.get("accounts") or []:
        if row.get("id") == account_id:
            body = str(row.get("body_full") or row.get("body") or "")
            lane = str(row.get("lane") or "")
            return body, lane, None, row.get("subject"), row.get("relationship_basis")
    return "", "", None, None, None


def score_w3_lane(*, account_ids: tuple[str, ...] = W3_APPROVED) -> dict:
    artifacts: list[dict] = []
    for aid in account_ids:
        body, lane, attach, subject, basis = _w3_body_for(aid)
        if not body.strip():
            artifacts.append(
                {
                    "account_id": aid,
                    "output_clean_pct": 0,
                    "oqg_pass": False,
                    "error": "missing_body",
                }
            )
            continue
        artifacts.append(
            score_w3_email(
                account_id=aid,
                body=body,
                lane=lane,
                attach=attach,
                subject=subject,
                relationship_basis=basis,
            )
        )

    scores = [int(a.get("output_clean_pct") or 0) for a in artifacts if "error" not in a]
    avg = round(sum(scores) / len(scores)) if scores else 0
    return {
        "lane": "w3_commercial",
        "output_clean_pct": avg,
        "output_clean_now": avg,
        "oqg_pass": avg >= OQG_BAR and all(a.get("oqg_pass") for a in artifacts if "error" not in a),
        "trust_mode": _trust_mode(avg),
        "artifacts": artifacts,
    }


def _receipt_field_ok(path: Path, field: str = "ok") -> bool:
    row = _read_json(path)
    if not row:
        return False
    val = row.get(field)
    if val is True:
        return True
    if isinstance(val, str) and val.upper() in ("PASS", "YES", "OK"):
        return True
    proof = str(row.get("proof") or "")
    return "PASS" in proof.upper()


def _validator_script_pass(script_name: str) -> bool:
    script = SCRIPTS / script_name
    if not script.is_file():
        return False
    import subprocess

    try:
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _runreceipt_zip_ok() -> bool:
    candidates = [
        ROOT / "receipts" / "bays" / "sample-bay" / "runreceipt.zip",
        SINA / "fbe-runreceipt-sample-bay-v1.zip",
    ]
    return any(p.is_file() and p.stat().st_size > 100 for p in candidates)


def score_fbe_lane() -> dict:
    checks: list[dict] = []
    total = 0

    contract = _read_json(ROOT / "data" / "fbe_quality_contract_v1.json")
    honest_cap = str(contract.get("w2_honest_cap") or "GOLD")
    tier_pts = 25 if honest_cap != "GOLD" else 20
    total += tier_pts
    checks.append({"id": "honest_tier_cap", "points": tier_pts, "max": 25, "detail": honest_cap})

    refinery = SINA / "fbe-refinery-verify-receipt-v1.json"
    ref_row = _read_json(refinery)
    ref_ok = _receipt_field_ok(refinery)
    ref_pts = 25 if ref_ok else 5
    total += ref_pts
    checks.append({"id": "refinery_verify", "points": ref_pts, "max": 25, "ok": ref_ok})

    critic = ref_row.get("critic_score") or ref_row.get("score")
    assets = ref_row.get("assets_fidelity_pct") or ref_row.get("assets_fidelity")
    critic_pts = 0
    if critic is not None:
        try:
            c = float(critic)
            critic_pts = 25 if c >= 90 else int(25 * c / 90)
        except (TypeError, ValueError):
            critic_pts = 10 if ref_ok else 0
    else:
        critic_pts = 15 if ref_ok else 0
    total += critic_pts
    checks.append({"id": "critic_90", "points": critic_pts, "max": 25})

    assets_pts = 0
    if assets is not None:
        try:
            a = float(assets)
            assets_pts = 20 if a >= 99 else int(20 * a / 99)
        except (TypeError, ValueError):
            assets_pts = 10 if ref_ok else 0
    else:
        assets_pts = 12 if ref_ok else 0
    total += assets_pts
    checks.append({"id": "assets_fidelity_99", "points": assets_pts, "max": 20})

    assembly = SINA / "fbe-assembly-verify-receipt-v1.json"
    asm_ok = _receipt_field_ok(assembly)
    w2_ok = _validator_script_pass("validate-fbe-w2-v1.sh") or (ref_ok and asm_ok)
    w2_pts = 20 if w2_ok else 8
    total += w2_pts
    checks.append({"id": "fbe_w2_validators", "points": w2_pts, "max": 20, "ok": w2_ok})

    zip_ok = _runreceipt_zip_ok()
    z_pts = 10 if zip_ok else 3
    total += z_pts
    checks.append({"id": "runreceipt_zip", "points": z_pts, "max": 10, "ok": zip_ok})

    gap_penalty = 5 if (w2_ok and asm_ok) else 15
    charter_note = "sample-bay gap reduced" if gap_penalty == 5 else "sample-bay incomplete · dealer 14/15"
    total = max(0, total - gap_penalty)
    checks.append({"id": "sample_bay_honest_gap", "points": -gap_penalty, "max": 0, "detail": charter_note})

    clean = min(100, max(0, total))
    return {
        "lane": "fbe_sourcea",
        "output_clean_pct": clean,
        "output_clean_now": clean,
        "oqg_pass": clean >= OQG_BAR,
        "trust_mode": _trust_mode(clean),
        "checks": checks,
    }


def score_creed_lane() -> dict:
    checks: list[dict] = []
    total = 0
    dealer = ROOT / "receipts" / "bays" / "sample-bay" / "assembly" / "church-verify-v1-v1.json"
    dealer_ok = _receipt_field_ok(dealer)
    d_pts = 30 if dealer_ok else 10
    total += d_pts
    checks.append({"id": "dealer_16_step", "points": d_pts, "max": 30, "ok": dealer_ok})

    refinery = SINA / "fbe-refinery-verify-receipt-v1.json"
    r_pts = 35 if _receipt_field_ok(refinery) else 15
    total += r_pts
    checks.append({"id": "refinery_fidelity", "points": r_pts, "max": 35})

    intake = SINA / "fbe-assembly-verify-receipt-v1.json"
    intake_ok = _receipt_field_ok(intake)
    i_pts = 20 if intake_ok else 5
    total += i_pts
    checks.append({"id": "disbrand_intake_gate", "points": i_pts, "max": 20, "ok": intake_ok})

    campus_ok = (ROOT / "docs" / "SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md").is_file()
    c_pts = 15 if campus_ok else 0
    total += c_pts
    checks.append({"id": "read_only_campus", "points": c_pts, "max": 15, "ok": campus_ok})

    clean = min(100, max(0, total))
    return {
        "lane": "creed_campus",
        "output_clean_pct": clean,
        "output_clean_now": clean,
        "oqg_pass": clean >= OQG_BAR,
        "trust_mode": _trust_mode(clean),
        "checks": checks,
    }


def _trust_mode(clean: int) -> str:
    if clean >= 95:
        return "trusted"
    if clean >= 90:
        return "assisted"
    return "supervised"


def _parse_iso_at(at: str) -> datetime | None:
    if not at:
        return None
    try:
        return datetime.strptime(at.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            return datetime.fromisoformat(at.replace("Z", "+00:00"))
        except ValueError:
            return None


def load_waivers() -> dict:
    row = _read_json(WAIVERS_LIVE)
    if not row.get("schema"):
        row = _read_json(WAIVERS_TEMPLATE)
    return row if row.get("schema") == "oqg-waiver-v1" else {"schema": "oqg-waiver-v1", "waivers": []}


def active_waiver(*, artifact_id: str, lane: str = "") -> dict | None:
    now = datetime.now(timezone.utc)
    for w in load_waivers().get("waivers") or []:
        if str(w.get("artifact_id") or "") != artifact_id:
            continue
        if lane and str(w.get("lane") or "") and str(w.get("lane")) != lane:
            continue
        exp = _parse_iso_at(str(w.get("expires_at") or ""))
        if exp and exp < now:
            continue
        return w
    return None


def active_waiver_count() -> int:
    now = datetime.now(timezone.utc)
    n = 0
    for w in load_waivers().get("waivers") or []:
        exp = _parse_iso_at(str(w.get("expires_at") or ""))
        if exp and exp < now:
            continue
        n += 1
    return n


def score_w3_artifact(
    *,
    account_id: str,
    body: str,
    lane: str,
    attach: Path | None = None,
) -> dict:
    """Score one W3 email body (alias for score_w3_email)."""
    return score_w3_email(account_id=account_id, body=body, lane=lane, attach=attach)


def assert_oqg_pass(
    *,
    account_id: str,
    body: str,
    lane: str,
    attach: Path | None = None,
    artifact_id: str | None = None,
    subject: str | None = None,
    relationship_basis: str | None = None,
) -> dict:
    """BQ2 gate — raise SystemExit if output_clean < 90 without active waiver."""
    aid = artifact_id or f"w3-canada-{account_id}"
    if subject is None or relationship_basis is None:
        pack = _w3_pack_meta(account_id)
        subject = subject if subject is not None else pack.get("subject")
        relationship_basis = (
            relationship_basis if relationship_basis is not None else pack.get("relationship_basis")
        )
    scored = score_w3_email(
        account_id=account_id,
        body=body,
        lane=lane,
        attach=attach,
        subject=subject,
        relationship_basis=relationship_basis,
    )
    waiver = active_waiver(artifact_id=aid, lane=lane)
    clean = int(scored.get("output_clean_pct") or 0)
    passed = bool(scored.get("oqg_pass")) or waiver is not None
    row = {
        **scored,
        "artifact_id": aid,
        "oqg_at": _now(),
        "oqg_bar": OQG_BAR,
        "oqg_pass_effective": passed,
        "waiver_id": waiver.get("id") if waiver else None,
    }
    if not passed:
        issues = []
        for chk in scored.get("checks") or []:
            if chk.get("issues"):
                issues.extend(chk["issues"])
        raise SystemExit(
            f"OQG BLOCK: {account_id} output_clean={clean}% < {OQG_BAR} — "
            f"issues={','.join(issues[:5]) or 'rubric_fail'} · "
            f"add waiver to ~/.sina/oqg-waiver-v1.json or harden pack"
        )
    return row


def _append_history(row: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as fh:
        slim = []
        for lane in row.get("lanes") or []:
            slim.append(
                {
                    "lane": lane.get("lane"),
                    "output_clean_pct": lane.get("output_clean_now") or lane.get("output_clean_pct"),
                    "output_clean_now": lane.get("output_clean_now") or lane.get("output_clean_pct"),
                }
            )
        fh.write(json.dumps({"at": row.get("at"), "lanes": slim}) + "\n")


def _rolling_7d_avg(lane_id: str) -> int | None:
    if not HISTORY.is_file():
        return None
    now = datetime.now(timezone.utc)
    vals: list[int] = []
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            at = entry.get("at") or ""
            ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if (now - ts).days > 7:
                continue
            for lane in entry.get("lanes") or []:
                if lane.get("lane") == lane_id:
                    vals.append(int(lane.get("output_clean_now") or lane.get("output_clean_pct") or 0))
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
    return round(sum(vals) / len(vals)) if vals else None


def _rolling_7d_fleet_avg() -> int | None:
    if not HISTORY.is_file():
        return None
    now = datetime.now(timezone.utc)
    vals: list[int] = []
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            at = entry.get("at") or ""
            ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if (now - ts).days > 7:
                continue
            lanes = entry.get("lanes") or []
            lane_vals = [
                int(l.get("output_clean_now") or l.get("output_clean_pct") or 0) for l in lanes
            ]
            if lane_vals:
                vals.append(round(sum(lane_vals) / len(lane_vals)))
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
    return round(sum(vals) / len(vals)) if vals else None


def _promotion_state(*, fleet_now: int, fleet_7d: int | None) -> dict:
    base = fleet_7d if fleet_7d is not None else fleet_now
    mode = _trust_mode(base)
    promote = base >= 95 and (fleet_7d is None or fleet_7d >= 95)
    demote = base < 85
    return {
        "trust_mode_effective": mode,
        "promote_eligible": promote,
        "demote_recommended": demote,
        "fleet_output_clean_now": fleet_now,
        "fleet_output_clean_7d": fleet_7d,
    }


def run_oqg(*, write: bool = True) -> dict:
    w3 = score_w3_lane()
    fbe = score_fbe_lane()
    creed = score_creed_lane()
    lanes = [w3, fbe, creed]

    fleet_vals = [int(l.get("output_clean_pct") or 0) for l in lanes]
    fleet_avg = round(sum(fleet_vals) / len(fleet_vals)) if fleet_vals else 0
    waiver_n = active_waiver_count()

    for lane in lanes:
        roll = _rolling_7d_avg(str(lane.get("lane")))
        now_pct = int(lane.get("output_clean_now") or lane.get("output_clean_pct") or 0)
        lane["output_clean_now"] = now_pct
        if roll is not None:
            lane["rolling_7d_output_clean_pct"] = roll
            lane["output_clean_pct"] = roll
            lane["trust_mode_7d"] = _trust_mode(roll)
            lane["trust_mode"] = _trust_mode(roll)
        else:
            lane["trust_mode_7d"] = _trust_mode(now_pct)

    fleet_7d = _rolling_7d_fleet_avg()
    promo = _promotion_state(fleet_now=fleet_avg, fleet_7d=fleet_7d)

    row = {
        "schema": "best-loop-oqg-receipt-v1",
        "at": _now(),
        "law": "docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md",
        "metric": "output_clean_pct",
        "fleet_output_clean_pct": fleet_7d if fleet_7d is not None else fleet_avg,
        "fleet_output_clean_now": fleet_avg,
        "fleet_output_clean_7d": fleet_7d,
        "fleet_trust_mode": promo["trust_mode_effective"],
        "promotion": promo,
        "active_waiver_count": waiver_n,
        "oqg_bar": OQG_BAR,
        "lanes": lanes,
        "best_loop_oqg_line": _oqg_line(lanes, fleet_avg, waiver_n),
    }
    try:
        from outbound_anti_template_v1 import build_template_fingerprint  # noqa: WPS433

        row["template_fingerprint"] = build_template_fingerprint()
    except Exception:
        pass

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        _append_history(row)
    return row


def _oqg_line(lanes: list[dict], fleet: int, waiver_n: int = 0) -> str:
    short = {"w3_commercial": "w3", "fbe_sourcea": "fbe", "creed_campus": "creed"}
    parts = []
    for lane in lanes:
        key = str(lane.get("lane") or "")
        lid = short.get(key, key[:4] or "?")
        pct = lane.get("output_clean_now") or lane.get("output_clean_pct") or 0
        parts.append(f"{lid}={pct}%")
    w = f" · waiver={waiver_n}" if waiver_n else ""
    return f"oqg · fleet={fleet}% clean · {' · '.join(parts)}{w}"


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "best-loop-oqg-receipt-v1":
        row = run_oqg(write=True)
    return {
        "schema": "worker-hub-best-loop-oqg-v1",
        "at": row.get("at"),
        "metric": "output_clean_pct",
        "fleet_output_clean_pct": row.get("fleet_output_clean_pct"),
        "fleet_output_clean_now": row.get("fleet_output_clean_now"),
        "fleet_output_clean_7d": row.get("fleet_output_clean_7d"),
        "fleet_trust_mode": row.get("fleet_trust_mode"),
        "promotion": row.get("promotion"),
        "active_waiver_count": row.get("active_waiver_count", 0),
        "oqg_bar": row.get("oqg_bar", 90),
        "best_loop_oqg_line": row.get("best_loop_oqg_line"),
        "lanes": row.get("lanes") or [],
        "law": row.get("law"),
        "command": "python3 scripts/best_loop_oqg_score_v1.py --json",
    }


def verify_noun_stack_regression() -> dict:
    """U002 regression — Royal Bank of Canada must not noun-stack fail."""
    sample = "Royal Bank of Canada Capital Markets Risk team asked for evidence."
    result = check_noun_stack(sample)
    return {"ok": bool(result.get("ok")), "sample": sample[:60], "noun_stack": result}


def verify_pattern_skeleton_acceptance() -> dict:
    """U071 — convergence skeleton hard-fails in OQG."""
    sys.path.insert(0, str(SCRIPTS))
    from outbound_anti_template_v1 import check_u071_pattern_skeleton  # noqa: WPS433

    return check_u071_pattern_skeleton()


def main() -> int:
    ap = argparse.ArgumentParser(description="Best Loop OQG output clean scoring")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--w3-only", action="store_true")
    ap.add_argument("--verify-noun-stack", action="store_true")
    ap.add_argument("--check-pattern-skeleton", action="store_true", help="U071 OQG hard fail")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.check_pattern_skeleton:
        row = verify_pattern_skeleton_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"pattern_skeleton ok={row.get('ok')}")
        return 0 if row.get("ok") else 1
    if args.verify_noun_stack:
        row = verify_noun_stack_regression()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"noun_stack_regression ok={row.get('ok')}")
        return 0 if row.get("ok") else 1
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    if args.w3_only:
        row = score_w3_lane()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"W3 clean={row.get('output_clean_pct')}% pass={row.get('oqg_pass')}")
        return 0
    row = run_oqg(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("best_loop_oqg_line", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
