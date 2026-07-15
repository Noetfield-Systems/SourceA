#!/usr/bin/env python3
"""Chat Unify ORD — general claim rules engine (data-driven, not example-specific).

SSOT: data/chat-unify-ord-claim-rules-v1.json
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOTS_OVERRIDE = Path.home() / ".sina" / "chat-unify-repo-roots-v1.json"
RULES_VERSION = "1.2.0"


def _resolve_rules_path() -> Path:
    bundle = os.environ.get("CHAT_UNIFY_BUNDLE_ROOT", "").strip()
    if bundle:
        bp = Path(bundle) / "data" / "chat-unify-ord-claim-rules-v1.json"
        if bp.is_file():
            return bp
    sa = os.environ.get("SINA_SOURCE_A", "").strip()
    if sa:
        sp = Path(sa) / "data" / "chat-unify-ord-claim-rules-v1.json"
        if sp.is_file():
            return sp
    return ROOT / "data" / "chat-unify-ord-claim-rules-v1.json"


RULES_PATH = _resolve_rules_path()

_PATH_INLINE = re.compile(
    r"(?:`([^`]+\.(?:md|json|py|sh|ts|tsx|html|css|toml|yaml|yml))`|"
    r"\b((?:assets|docs|governance|infra|scripts|apps|brand)/[\w./_-]+\."
    r"(?:md|json|py|sh|html|tsx|ts|css|toml|yaml|yml))\b|"
    r"\b(vercel\.json|\.vercelignore|package\.json)\b)",
    re.I,
)
_API_RE = re.compile(r"\b(api/[a-z0-9_/-]+)\b", re.I)
_PR_RE = re.compile(r"\bPR\s*#\s*(\d+)", re.I)
_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)

_URL_PATH_RE = re.compile(r"(/[\w./_-]+(?:\.md|\.json)?)", re.I)

_rules_cache: dict | None = None
_deploy_cache: list[dict] | None = None


def load_rules() -> dict:
    global _rules_cache
    if _rules_cache is not None:
        return _rules_cache
    if RULES_PATH.is_file():
        _rules_cache = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    else:
        _rules_cache = {"schema": "chat-unify-ord-claim-rules-v1", "claim_types": [], "consistency_rules": []}
    return _rules_cache


def _path_exists(rel: str) -> bool:
    return (ROOT / rel.lstrip("/")).is_file()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _grep_repo(needle: str, limit: int = 8) -> list[str]:
    hits: list[str] = []
    if not needle or len(needle) < 3:
        return hits
    for base in (ROOT / "agent-control-panel", ROOT / "scripts", ROOT / "docs", ROOT / "infra", ROOT):
        if not base.is_dir() or len(hits) >= limit:
            continue
        try:
            for path in base.rglob("*"):
                if len(hits) >= limit:
                    break
                if not path.is_file() or path.suffix not in {
                    ".py",
                    ".md",
                    ".json",
                    ".html",
                    ".ts",
                    ".tsx",
                    ".js",
                    ".sh",
                    ".toml",
                }:
                    continue
                if path.stat().st_size > 800_000:
                    continue
                try:
                    if needle in path.read_text(encoding="utf-8", errors="replace"):
                        hits.append(str(path.relative_to(ROOT)))
                except OSError:
                    continue
        except OSError:
            continue
    return hits


def is_table_noise_line(text: str) -> bool:
    """Drop tab-table / persona rows before atom creation."""
    t = (text or "").strip()
    if not t:
        return True
    if is_garbage_atom(t):
        return True
    if "\t" in t and len(t) < 80:
        return True
    if re.match(r"^(Persona|CISO|Procurement|Federal|MSP|Investor|Sandbox)", t, re.I):
        return True
    if re.match(r"^(Cold|Warm|Unlikely|Likely|Maybe|Mixed|N/A)\b", t, re.I):
        return True
    return False


def _repo_scan_roots() -> list[Path]:
    rules = load_rules()
    roots: list[Path] = []
    for rel in (rules.get("deploy_verify") or {}).get("repo_scan_roots") or []:
        p = ROOT if rel in (".", "./") else (ROOT / rel).resolve()
        if p.is_dir():
            roots.append(p)
    if REPO_ROOTS_OVERRIDE.is_file():
        try:
            ov = json.loads(REPO_ROOTS_OVERRIDE.read_text(encoding="utf-8"))
            for rel in ov.get("roots") or []:
                p = Path(str(rel).expanduser())
                if p.is_dir() and p not in roots:
                    roots.append(p)
        except (OSError, json.JSONDecodeError):
            pass
    if not roots:
        roots = [ROOT, ROOT / "apps", ROOT / "packages", ROOT / "brand"]
    return roots


def _find_deploy_configs() -> list[dict]:
    global _deploy_cache
    if _deploy_cache is not None:
        return _deploy_cache
    rules = load_rules()
    names = set((rules.get("disk_binders") or {}).get("deploy_config_globs") or ["vercel.json", ".vercelignore"])
    found: list[dict] = []
    for base in _repo_scan_roots():
        if not base.is_dir():
            continue
        try:
            for path in base.rglob("*"):
                if path.name not in names or not path.is_file():
                    continue
                if path.stat().st_size > 500_000:
                    continue
                try:
                    body = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                found.append({"path": str(path.relative_to(ROOT)), "body": body})
                if len(found) >= 8:
                    break
        except OSError:
            continue
        if len(found) >= 8:
            break
    _deploy_cache = found
    return found


def _extract_route_paths(text: str) -> list[str]:
    paths: list[str] = []
    for m in _URL_PATH_RE.finditer(text or ""):
        p = m.group(1).rstrip(".,;:")
        if len(p) > 2 and p not in paths:
            paths.append(p)
    return paths[:6]


def _path_blocked_in_configs(route_path: str, configs: list[dict]) -> tuple[bool, str | None]:
    if not route_path or not configs:
        return False, None
    needle = route_path.strip().rstrip("/")
    if not needle.startswith("/"):
        needle = f"/{needle}"
    prefix = needle.split("*")[0].rstrip("/") if "*" in needle else needle
    for cfg in configs:
        body = cfg.get("body") or ""
        rel = cfg.get("path") or "?"
        if needle in body or prefix in body:
            return True, rel
        if f"{prefix}/*" in body or f"{prefix}*" in body:
            return True, rel
    return False, None


def load_deploy_configs_into_disk(snap: dict) -> dict:
    configs = _find_deploy_configs()
    out = dict(snap or {})
    out["deploy_configs"] = [{"path": c["path"]} for c in configs]
    paths = list(out.get("paths_checked") or [])
    for c in configs:
        full = str(ROOT / c["path"])
        if full not in paths:
            paths.append(full)
    out["paths_checked"] = paths
    return out


def is_garbage_atom(text: str) -> bool:
    rules = load_rules()
    q = rules.get("atom_quality") or {}
    t = (text or "").strip()
    if len(t) < int(q.get("reject_if_shorter_than") or 12):
        return True
    if t in set(q.get("reject_exact") or []):
        return True
    for pat in q.get("table_fragment_patterns") or []:
        if re.search(pat, t, re.I):
            return True
    if "\t" in t and len(t) < 40 and not re.search(r"[.!?]$", t):
        return True
    return False


def sanitize_atoms(atoms: list[dict]) -> list[dict]:
    out: list[dict] = []
    for a in atoms:
        if is_garbage_atom(a.get("text") or ""):
            continue
        out.append(a)
    for i, a in enumerate(out[: int((load_rules().get("atom_quality") or {}).get("max_atoms") or 32)], start=1):
        a["id"] = f"a{i}"
    return out


def classify_claim_type(atom: dict) -> str:
    rules = load_rules()
    text = atom.get("text") or ""
    kind = (atom.get("kind") or "CLAIM").upper()
    typed = sorted(rules.get("claim_types") or [], key=lambda r: int(r.get("priority") or 999))
    for row in typed:
        if row.get("match_kinds") and kind not in [k.upper() for k in row["match_kinds"]]:
            continue
        matched = False
        for pat in row.get("match_any_regex") or []:
            if re.search(pat, text, re.I):
                matched = True
                break
        if row.get("match_kinds") and not row.get("match_any_regex"):
            matched = True
        if matched:
            return str(row.get("id") or "CHECKABLE_CLAIM")
    return "CHECKABLE_CLAIM"


def tag_atoms_claim_types(atoms: list[dict]) -> list[dict]:
    out: list[dict] = []
    for a in atoms:
        row = dict(a)
        row["claim_type"] = classify_claim_type(row)
        rules = load_rules()
        for ct in rules.get("claim_types") or []:
            if ct.get("id") == row["claim_type"]:
                row["verify_predicate"] = ct.get("verify_predicate")
                break
        out.append(row)
    return out


def extract_draft_paths(draft: str) -> list[str]:
    rules = load_rules()
    cfg = (rules.get("disk_binders") or {}).get("draft_path_extract") or {}
    found: list[str] = []
    for m in _PATH_INLINE.finditer(draft or ""):
        rel = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if rel:
            found.append(rel.replace("~/Desktop/SourceA/", "").lstrip("/"))
    for named in cfg.get("named_files") or []:
        if named.lower() in (draft or "").lower() and _path_exists(named):
            found.append(named)
    # dedupe preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for p in found:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq[:12]


def enrich_disk_hints(*, draft: str, snap: dict) -> dict:
    rules = load_rules()
    out = dict(snap or {})
    paths = list(out.get("paths_checked") or [])
    for p in (rules.get("disk_binders") or {}).get("always_peek") or []:
        full = ROOT / p
        if full.is_file() and str(full) not in paths:
            paths.append(str(full))
    for rel in extract_draft_paths(draft):
        full = ROOT / rel
        if full.is_file() and str(full) not in paths:
            paths.append(str(full))
    out["paths_checked"] = paths
    out["draft_paths"] = extract_draft_paths(draft)
    manifest = ROOT / "infra" / "cleanup" / "cleanup-manifest.md"
    if manifest.is_file():
        body = manifest.read_text(encoding="utf-8", errors="replace")
        out["batch_4_frozen"] = "Batch 4 FROZEN" in body or "FROZEN — Batch 4" in body
        out["batch_4_approved"] = (
            re.search(r"Batch 4[^\n]*APPROVED|Status:\s*APPROVED", body, re.I) is not None
            and not out.get("batch_4_frozen")
        )
    return load_deploy_configs_into_disk(out)


# --- verify predicates ---


def _verify_skip_fragment(_atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    return "skip", None, "table fragment — excluded from truth counts"


def _verify_opinion(_atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    return "opinion", None, "analysis/opinion — not disk-checkable from hub"


def _verify_live_http(atom: dict, disk: dict) -> tuple[str, str | None, str]:
    text = atom.get("text") or ""
    urls = _URL_RE.findall(text)
    routes = _extract_route_paths(text)
    configs = _find_deploy_configs()
    tl = text.lower()
    claims_leak = bool(re.search(r"\b(200|reachable|visible|leak|exposed)\b", tl))
    claims_blocked = bool(re.search(r"\b(block|404|fixed|blocks?)\b", tl))

    for route in routes:
        blocked, ref = _path_blocked_in_configs(route, configs)
        if blocked and ref:
            if claims_blocked or re.search(r"\bblocks?\b", tl):
                return "verified", ref, f"deploy config mentions {route} ({ref})"
            if claims_leak:
                return "unverified", ref, f"{route} in deploy config — live 200 not curl'd from Mac"
        elif claims_blocked and configs:
            return "unverified", routes[0], f"block claimed for {route} — not found in repo deploy configs"

    ref = urls[0][:120] if urls else (routes[0] if routes else "live-http")
    return "unverified", ref, "live HTTP/URL claim — hub does not curl production"


def _verify_deploy_config_bind(atom: dict, disk: dict) -> tuple[str, str | None, str]:
    text = atom.get("text") or ""
    configs = _find_deploy_configs()
    if not configs:
        return "unverified", None, "no vercel.json/.vercelignore found in repo"
    routes = _extract_route_paths(text)
    for route in routes:
        blocked, ref = _path_blocked_in_configs(route, configs)
        if blocked and ref:
            return "verified", ref, f"deploy config binds {route} in {ref}"
    if re.search(r"\bvercel\.json\b", text, re.I):
        for c in configs:
            if c["path"].endswith("vercel.json"):
                return "verified", c["path"], "vercel.json present in repo"
    return "unverified", configs[0]["path"], "deploy path cited — block rule not grep-matched"


def _verify_pr_ref(atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    m = _PR_RE.search(atom.get("text") or "")
    if not m:
        return "unverified", None, "PR mentioned — number not parsed"
    num = m.group(1)
    needle = f"#{num}"
    hits = _grep_repo(needle, limit=5)
    if hits:
        return "verified", hits[0], f"PR #{num} referenced in repo ({hits[0]})"
    hits2 = _grep_repo(f"PR #{num}", limit=3)
    if hits2:
        return "verified", hits2[0], f"PR #{num} text found in repo"
    return "unverified", None, f"PR #{num} — no reference found in repo from Mac"


def _verify_manifest_batch(atom: dict, disk: dict) -> tuple[str, str | None, str]:
    ref = "infra/cleanup/cleanup-manifest.md"
    tl = (atom.get("text") or "").lower()
    frozen = disk.get("batch_4_frozen")
    if re.search(r"\bapproved\b", tl, re.I):
        if frozen or not disk.get("batch_4_approved"):
            return "mismatch", ref, "manifest says FROZEN — not APPROVED"
        return "verified", ref, "manifest batch approved logged"
    if frozen and re.search(r"\b(execute|run batch|run)\b", tl, re.I):
        return "mismatch", ref, "batch 4 FROZEN — execute blocked logged"
    if re.search(r"\bfrozen\b", tl, re.I) and frozen:
        return "verified", ref, "batch frozen matches disk"
    return "unverified", ref, "manifest/batch mentioned — read cleanup-manifest.md"


def _verify_eval_receipt(atom: dict, disk: dict) -> tuple[str, str | None, str]:
    eval_row = disk.get("eval_1b") or {}
    ref = str(Path.home() / ".sina" / "eval_packet_v1b_report.json")
    tl = (atom.get("text") or "").lower()
    if not eval_row:
        return "unverified", ref, "eval-1b receipt missing logged"
    ok = eval_row.get("live_ok") if eval_row.get("mode") == "live" else eval_row.get("ok")
    claims_pass = bool(re.search(r"\b(green|pass|ok|100%)\b", tl))
    claims_fail = bool(re.search(r"\b(fail|red|broken)\b", tl))
    if claims_pass and ok is False:
        return "mismatch", ref, "agent claims eval pass — disk says fail"
    if claims_fail and ok is True:
        return "mismatch", ref, "agent claims eval fail — disk says pass"
    if claims_pass and ok is True:
        if re.search(r"\b(all validators|zero drift|everything pass)\b", tl):
            return "unverified", ref, "eval ok — sweeping pass claims not proven"
        return "verified", ref, "eval-1b matches receipt"
    return "unverified", ref, "eval-1b mentioned — receipt present, wording unclear"


def _verify_sweeping_pass(atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    return "unverified", None, "sweeping pass claim — no receipt bound"


def _verify_api_route(atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    m = _API_RE.search(atom.get("text") or "")
    if not m:
        return "unverified", None, "API route not parsed"
    route = m.group(1)
    if _grep_repo(route, limit=1):
        return "verified", route, "API route found in repo"
    return "mismatch", route, "API route not found in repo"


def _verify_execution(atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    refs = _extract_paths_from_text(atom.get("text") or "")
    if not refs:
        return "unverified", None, "execution claim — no path to verify"
    rel = refs[0]
    if _path_exists(rel):
        return "unverified", rel, "file exists — git/commit not verified from hub"
    return "mismatch", rel, "cited file missing logged"


def _verify_repo_path(atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    refs = _extract_paths_from_text(atom.get("text") or "")
    if not refs:
        return "unverified", None, "path not parsed"
    rel = refs[0]
    tl = (atom.get("text") or "").lower()
    kind = (atom.get("kind") or "").upper()
    if kind in ("ACTION", "INSTRUCTION") and re.search(r"\b(run|execute|bash|sh)\b", tl):
        if _path_exists(rel):
            return "unverified", rel, "script exists — outcome/approval not proven"
        return "mismatch", rel, "script path missing"
    if re.search(r"\b(exists|present|in the repository|matches)\b", tl):
        if _path_exists(rel):
            return "verified", rel, "path exists logged"
        return "mismatch", rel, "path not found logged"
    if _path_exists(rel):
        return "unverified", rel, "path cited — existence not explicitly claimed"
    return "mismatch", rel, "cited path missing"


def _verify_action_unverified(_atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    return "unverified", None, "action/instruction — verify before executing"


def _verify_claim_unbound(_atom: dict, _disk: dict) -> tuple[str, str | None, str]:
    ct = _atom.get("claim_type") or ""
    if ct in ("OPINION", "ASSUMPTION"):
        return _verify_opinion(_atom, _disk)
    return "unverified", None, "checkable claim — not bound to disk receipt"


def _extract_paths_from_text(text: str) -> list[str]:
    out: list[str] = []
    for m in _PATH_INLINE.finditer(text):
        rel = (m.group(1) or m.group(2) or m.group(3) or "").replace("~/Desktop/SourceA/", "").lstrip("/")
        if rel:
            out.append(rel)
    return out


_PREDICATES = {
    "skip_fragment": _verify_skip_fragment,
    "opinion_not_checkable": _verify_opinion,
    "live_http_not_run": _verify_live_http,
    "deploy_config_bind": _verify_deploy_config_bind,
    "pr_ref_in_repo": _verify_pr_ref,
    "manifest_batch_state": _verify_manifest_batch,
    "eval_receipt_match": _verify_eval_receipt,
    "sweeping_pass_unproven": _verify_sweeping_pass,
    "api_route_in_repo": _verify_api_route,
    "execution_path_check": _verify_execution,
    "repo_path_claim": _verify_repo_path,
    "action_unverified": _verify_action_unverified,
    "claim_unbound": _verify_claim_unbound,
}


def verify_atom(atom: dict, disk: dict) -> dict:
    row = dict(atom)
    pred_id = row.get("verify_predicate") or "claim_unbound"
    if not row.get("claim_type"):
        row["claim_type"] = classify_claim_type(row)
    fn = _PREDICATES.get(pred_id) or _verify_claim_unbound
    status, ref, reason = fn(row, disk)
    row["disk_status"] = status
    row["disk_ref"] = ref
    row["verify_reason"] = reason
    return row


def verify_atoms_on_disk(*, atoms: list[dict], disk: dict) -> list[dict]:
    tagged = tag_atoms_claim_types(atoms)
    cleaned = sanitize_atoms(tagged)
    return [verify_atom(a, disk) for a in cleaned]


def atom_stats(atoms: list[dict], graph: dict) -> dict:
    countable = [a for a in atoms if a.get("disk_status") not in ("skip", "opinion", "n/a")]
    verified = sum(1 for a in countable if a.get("disk_status") == "verified")
    unverified = sum(1 for a in countable if a.get("disk_status") == "unverified")
    mismatch = sum(1 for a in countable if a.get("disk_status") == "mismatch")
    opinions = sum(1 for a in atoms if a.get("disk_status") == "opinion")
    skipped = sum(1 for a in atoms if a.get("disk_status") == "skip")
    contradictions = sum(1 for e in (graph or {}).get("edges", []) if e.get("type") == "contradicts")
    checkable = len(countable)
    return {
        "atom_count": len(atoms),
        "checkable_count": checkable,
        "verified": verified,
        "unverified": unverified,
        "disk_mismatch": mismatch,
        "opinion_count": opinions,
        "skipped_fragments": skipped,
        "hallucinated": unverified + mismatch,
        "contradictions": contradictions,
        "edge_count": len((graph or {}).get("edges", [])),
    }


def enrich_stats_for_gate(atoms: list[dict], stats: dict) -> dict:
    st = dict(stats or {})
    st["deploy_verified"] = sum(
        1
        for a in atoms
        if a.get("claim_type") in ("DEPLOY_BLOCK", "PR_REF") and a.get("disk_status") == "verified"
    )
    st["live_http_unverified"] = sum(
        1 for a in atoms if a.get("claim_type") == "LIVE_HTTP" and a.get("disk_status") == "unverified"
    )
    return st


def run_consistency_rules(
    *,
    draft: str,
    parsed: dict,
    atoms: list[dict],
    disk: dict,
    stats: dict | None = None,
) -> list[str]:
    rules = load_rules()
    issues: list[str] = []
    low = draft or ""
    st = stats or atom_stats(atoms, {"edges": []})

    for rule in rules.get("consistency_rules") or []:
        rid = rule.get("id") or ""
        msg = str(rule.get("message") or "")

        if rule.get("match_draft_regex"):
            if rule.get("min_matches"):
                hits = re.findall(rule["match_draft_regex"], low, re.I)
                if len(hits) >= int(rule["min_matches"]):
                    issues.append(msg.replace("{count}", str(len(hits))))
            elif re.search(rule["match_draft_regex"], low, re.I | re.S):
                if rule.get("disk_key"):
                    if disk.get(rule["disk_key"]) == rule.get("disk_expect"):
                        prefix = rule.get("prefix") or ""
                        issues.append(f"{prefix}{msg}" if prefix else msg)
                else:
                    issues.append(msg)

        if rule.get("match_parsed") == "actions_plus_claims":
            ac = len(parsed.get("actions") or []) + len(parsed.get("claims") or [])
            if len(parsed.get("actions") or []) >= int(rule.get("actions_min") or 99) and len(
                parsed.get("claims") or []
            ) >= int(rule.get("claims_min") or 99):
                issues.append(msg)

        ct = rule.get("requires_atoms_claim_type")
        if ct:
            subset = [a for a in atoms if a.get("claim_type") == ct]
            if len(subset) >= int(rule.get("min_atoms") or 1):
                statuses = {a.get("disk_status") for a in subset}
                if rule.get("if_all_verify_status"):
                    want = set(rule["if_all_verify_status"])
                    if statuses and statuses.issubset(want):
                        issues.append(msg)
                if rule.get("if_any_verify_status"):
                    want = set(rule["if_any_verify_status"])
                    if statuses & want:
                        issues.append(msg)

        if rule.get("requires_checkable_atoms"):
            if st.get("checkable_count", 0) >= int(rule.get("checkable_min") or 1):
                if st.get("verified", 0) <= int(rule.get("verified_max") or 0):
                    issues.append(msg)

    # dedupe
    seen: set[str] = set()
    uniq: list[str] = []
    for i in issues:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return uniq


def simplify_from_atoms(*, atoms: list[dict], issues: list[str], stats: dict, decision: dict | None) -> str:
    lines = ["Plain read", ""]
    mism = [a for a in atoms if a.get("disk_status") == "mismatch"]
    unver = [a for a in atoms if a.get("disk_status") == "unverified"]
    ver = [a for a in atoms if a.get("disk_status") == "verified"]

    lines.append("What the AI said (one line)")
    if atoms:
        lines.append(f"· {atoms[0]['text'][:140]}…" if len(atoms[0]["text"]) > 140 else f"· {atoms[0]['text']}")
    lines.append("")
    lines.append("What looks checkable")
    if ver:
        for a in ver[:3]:
            lines.append(f"· ✓ {a['text'][:100]}")
    else:
        lines.append("· Nothing verified logged from this Mac.")
    lines.append("")
    lines.append("What needs your eyes")
    for a in (mism + unver)[:5]:
        reason = a.get("verify_reason") or a.get("claim_type") or "?"
        lines.append(f"· {a['text'][:90]} — {reason}")
    if not mism and not unver:
        lines.append("· Mostly opinion/analysis — ORD cannot prove buyer UX claims from disk.")
    lines.append("")
    if issues:
        lines.append(f"Consistency flags: {len(issues)}")
        for i in issues[:3]:
            lines.append(f"· {i}")
    if decision:
        lines.append("")
        lines.append(f"Gate: {str(decision.get('action', '?')).upper()} ({decision.get('truth_score')}/100)")
    return "\n".join(lines)


def top_verify_actions(atoms: list[dict], limit: int = 5) -> list[str]:
    out: list[str] = []
    for a in atoms:
        if a.get("disk_status") in ("mismatch", "unverified") and a.get("verify_reason"):
            out.append(f"{a.get('id')}: {a['verify_reason']}")
        if len(out) >= limit:
            break
    return out
