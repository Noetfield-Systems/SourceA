#!/usr/bin/env python3
"""Vocabulary Intelligence Machine — scan · classify tier/subject · suggest · receipt.

SSOT: data/vocabulary-intelligence-registry-v1.json
Law: docs/VOCABULARY_INTELLIGENCE_MACHINE_BLUEPRINT_v1.md
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY_PATH = ROOT / "data" / "vocabulary-intelligence-registry-v1.json"
RECEIPT_PATH = SINA / "vocabulary-intelligence-scan-receipt-v1.json"
MAX_FILE_BYTES = 2_000_000
MAX_URL_BYTES = 500_000
URL_FETCH_TIMEOUT = 15
_URL_RE = re.compile(r"^https?://", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _glob_hit(path: Path, patterns: list[str]) -> bool:
    s = path.as_posix()
    for pat in patterns:
        if fnmatch.fnmatch(s, pat) or fnmatch.fnmatch(s, f"**/{pat.lstrip('**/')}"):
            return True
        # pathlib-style ** match
        try:
            if path.match(pat):
                return True
        except ValueError:
            pass
    return False


def _resolve_roots(profile: dict[str, Any]) -> list[Path]:
    roots: list[Path] = []
    for raw in profile.get("roots") or []:
        p = Path(raw).expanduser()
        if profile.get("root_resolve") == "repo":
            p = ROOT / p if not p.is_absolute() else p
        roots.append(p.resolve())
    return [r for r in roots if r.is_dir()]


def _should_skip_dir(path: Path, exclude_globs: list[str]) -> bool:
    return _glob_hit(path, exclude_globs)


def _iter_files(
    roots: list[Path],
    *,
    extensions: list[str],
    exclude_dir_globs: list[str],
) -> Iterator[Path]:
    ext_set = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if path.suffix.lower() not in ext_set:
                continue
            try:
                rel_parts = path.relative_to(root).parts
            except ValueError:
                rel_parts = path.parts
            skip = False
            for part in path.parents:
                if part == root:
                    break
                if _should_skip_dir(part, exclude_dir_globs):
                    skip = True
                    break
            if skip:
                continue
            for g in exclude_dir_globs:
                frag = "/".join(rel_parts)
                if fnmatch.fnmatch(frag, g.replace("**/", "")) or _glob_hit(path, [g]):
                    skip = True
                    break
            if skip:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path


def _path_tier(path: Path, registry: dict[str, Any]) -> int:
    posix = path.as_posix().lower()
    if posix.startswith("url:") or posix.startswith("paste:") or posix.startswith("live-url/"):
        return 1
    if _glob_hit(path, registry.get("tier3_path_globs") or []):
        return 3
    if _glob_hit(path, registry.get("tier2_path_globs") or []):
        return 2
    if path.suffix.lower() in {".html", ".md", ".mdc"}:
        return 1
    if "agent-control-panel" in path.as_posix() and path.suffix.lower() in {".js", ".html"}:
        return 1
    if path.name in {"brain_live_context_v1.py", "worker_hub_v1.py", "loop_specialist_tick_v1.py"}:
        return 1
    return 2


def _line_tier_bump(line: str, path: Path, base_tier: int, registry: dict[str, Any]) -> int:
    for pat in registry.get("tier3_line_patterns") or []:
        if pat in line:
            return 3
    if base_tier >= 3:
        return 3
    if any(k in line for k in ('"one_law"', '"show_this"', "for_founder", "founder_motion")):
        return min(base_tier, 2) if base_tier > 1 else 2
    if path.suffix.lower() == ".html" or "index.html" in path.name:
        return 1
    return base_tier


def _subject_for_line(
    line: str,
    path: Path,
    *,
    registry: dict[str, Any],
    campaign: dict[str, Any],
) -> tuple[str, str]:
    """Return (subject_id, action). action: skip | patch | glossary_only"""
    subjects = registry.get("subjects") or {}
    posix = path.as_posix().lower()
    low = line.lower()

    gov = subjects.get("governance_poison") or {}
    if "poison" in low and "governance" in posix or "anti-poison" in low or "anti_poison" in low:
        if "motor" not in low and "drain" not in low.replace("anti-poison", ""):
            return "governance_poison", "skip"

    product = subjects.get("product_loop") or {}
    for pat in product.get("keep_patterns") or []:
        if pat.lower() in low or pat.lower().strip("/") in posix:
            return "product_loop", "skip"
    if "/sourcea/loops" in posix or "loops-hub" in posix:
        return "product_loop", "skip"

    cu = subjects.get("chat_unify_loop") or {}
    for pat in cu.get("keep_patterns") or []:
        if pat.lower() in low or pat.lower().replace("-", "_") in posix:
            return "chat_unify_loop", "skip"
    if "chat-unify" in posix and "loop" in low and "Auto Runtime" not in low:
        if "founder" in low or "ord" in low or "verify pipeline" in low:
            return "chat_unify_loop", "skip"

    exclude = set(campaign.get("exclude_subjects") or [])
    motor = subjects.get("motor_cloud") or {}
    display = motor.get("display_map") or {}
    retired = motor.get("retired_patterns") or []

    matched_retired: str | None = None
    for pat in sorted(retired, key=len, reverse=True):
        if pat.lower() in low:
            matched_retired = pat
            break

    if not matched_retired:
        return "unclassified", "skip"

    if "motor_cloud" in exclude:
        return "motor_cloud", "skip"

    return "motor_cloud", "patch"


def _suggestion(matched: str, registry: dict[str, Any]) -> str:
    motor = (registry.get("subjects") or {}).get("motor_cloud") or {}
    display = motor.get("display_map") or {}
    key = matched.lower()
    for k, v in display.items():
        if k.lower() == key or k.lower() in key:
            return str(v)
    if "drain" in key:
        return "Cloud Forge Run"
    if "loop" in key:
        return "Auto Runtime"
    return ""


def _reason(hit: dict[str, Any]) -> str:
    tier = hit.get("tier")
    subject = hit.get("subject")
    action = hit.get("action")
    if tier == 3:
        return "Machine path or API symbol — Tier 3 frozen; rename needs migration campaign"
    if subject == "product_loop":
        return "Commercial product loop SKU — keep wording on landing and sales pages"
    if subject == "chat_unify_loop":
        return "Chat Unify verify/ORD machine — different subject from cloud motor"
    if subject == "governance_poison":
        return "Poison is governance-only — not cloud motor display"
    if action == "patch" and tier == 1:
        return "Founder-facing copy — replace with campaign display name"
    if action == "patch" and tier == 2:
        return "Ops display string — safe to update copy; keep JSON keys and API paths"
    return "No campaign action"


def _scan_text(
    text: str,
    virtual_rel: str,
    *,
    patterns: list[str],
    registry: dict[str, Any],
    campaign: dict[str, Any],
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    path = Path(virtual_rel)
    base_tier = _path_tier(path, registry)
    lines = text.splitlines()

    motor = (registry.get("subjects") or {}).get("motor_cloud") or {}
    canonical = {str(c).lower() for c in motor.get("canonical_display") or []}

    for pat in sorted(patterns, key=len, reverse=True):
        pat_low = pat.lower()
        if pat_low in canonical:
            continue
        for i, line in enumerate(lines, start=1):
            if pat_low not in line.lower():
                continue
            suggestion = _suggestion(pat, registry)
            if suggestion and suggestion.lower() == pat_low:
                continue
            tier = _line_tier_bump(line, path, base_tier, registry)
            subject, action = _subject_for_line(line, path, registry=registry, campaign=campaign)
            if tier == 3:
                action = "skip"
            elif subject in ("product_loop", "chat_unify_loop", "governance_poison"):
                action = "skip"
            elif tier == 1 and action == "patch":
                action = "patch"
            elif tier == 2 and action == "patch":
                action = "patch"
            else:
                action = "skip" if tier == 3 else action

            if action == "patch" and suggestion:
                m = re.search(re.escape(pat), line, re.IGNORECASE)
                if m and m.group(0) == suggestion:
                    action = "skip"

            suggestion = suggestion if action == "patch" else ""
            hit = {
                "file": virtual_rel,
                "line": i,
                "match": pat,
                "context": line.strip()[:240],
                "tier": tier,
                "subject": subject,
                "suggestion": suggestion,
                "action": action,
            }
            hit["reason"] = _reason(hit)
            hits.append(hit)

    return hits


def _scan_file(
    path: Path,
    *,
    patterns: list[str],
    registry: dict[str, Any],
    campaign: dict[str, Any],
) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        rel = path.as_posix()

    return _scan_text(
        text,
        rel,
        patterns=patterns,
        registry=registry,
        campaign=campaign,
    )


def _strip_html(raw: str) -> str:
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", raw, flags=re.I)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_url_text(url: str, *, timeout: int = URL_FETCH_TIMEOUT, max_bytes: int = MAX_URL_BYTES) -> dict[str, Any]:
    """Fetch live page text for vocabulary scan."""
    raw_url = (url or "").strip().split()[0].rstrip(".,;:")
    if not raw_url or not _URL_RE.match(raw_url):
        return {"ok": False, "error": "invalid_url", "url": url}

    status: int | None = None
    err: str | None = None
    body = ""
    ctx = ssl.create_default_context()
    try:
        req = Request(
            raw_url,
            method="GET",
            headers={"User-Agent": "SourceA-VocabularyIntel/1.1", "Accept": "text/html,application/json,text/plain"},
        )
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            status = int(resp.status)
            chunk = resp.read(max_bytes + 1)
            if len(chunk) > max_bytes:
                chunk = chunk[:max_bytes]
            body = chunk.decode("utf-8", errors="replace")
    except HTTPError as e:
        status = int(e.code)
        try:
            body = e.read(max_bytes).decode("utf-8", errors="replace")
        except Exception:
            body = ""
        if status and status >= 400 and not body:
            err = f"HTTP {status}"
    except URLError as e:
        err = str(e.reason)[:200]
    except Exception as e:
        err = str(e)[:200]

    if not body and err:
        return {"ok": False, "error": err, "url": raw_url, "status": status}

    plain = body
    if "<" in body and ">" in body:
        plain = _strip_html(body)
    if not plain.strip():
        plain = body[:max_bytes]

    return {
        "ok": True,
        "url": raw_url,
        "status": status,
        "bytes": len(body.encode("utf-8", errors="replace")),
        "text": plain[: max_bytes],
        "fetched_at": _now(),
    }


def _resolve_local_file(file_path: str) -> Path | None:
    raw = (file_path or "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    else:
        p = p.resolve()
    if not p.is_file():
        return None
    try:
        if p.stat().st_size > MAX_FILE_BYTES:
            return None
    except OSError:
        return None
    allowed_roots = [ROOT.resolve(), SINA.resolve(), Path.home() / "Desktop"]
    if not any(str(p).startswith(str(root)) for root in allowed_roots if root.is_dir()):
        return None
    return p


def _pack_scan_result(
    *,
    campaign_id: str,
    campaign: dict[str, Any],
    hits: list[dict[str, Any]],
    registry: dict[str, Any],
    source_type: str,
    source_label: str,
    files_scanned: int = 1,
    profiles: list[str] | None = None,
    roots: list[str] | None = None,
    fetch_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    hits = _dedupe_hits(hits)
    patch_hits = [h for h in hits if h.get("action") == "patch"]
    by_tier: dict[str, int] = {"1": 0, "2": 0, "3": 0}
    for h in hits:
        t = str(h.get("tier", 3))
        by_tier[t] = by_tier.get(t, 0) + 1

    out: dict[str, Any] = {
        "ok": True,
        "schema": "vocabulary-intelligence-scan-v1",
        "at": _now(),
        "campaign_id": campaign_id,
        "goal": campaign.get("goal"),
        "source_type": source_type,
        "source_label": source_label,
        "files_scanned": files_scanned,
        "hits_total": len(hits),
        "hits_patch": len(patch_hits),
        "hits_by_tier": by_tier,
        "hits": hits,
        "patch_queue": patch_hits[:200],
        "registry": str(REGISTRY_PATH.relative_to(ROOT)),
    }
    if profiles is not None:
        out["profiles"] = profiles
    if roots is not None:
        out["roots"] = roots
    if fetch_meta:
        out["fetch"] = fetch_meta
    return out


def _campaign_context(
    campaign_id: str, registry: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str] | None, dict[str, Any] | None]:
    campaigns = registry.get("campaigns") or {}
    if campaign_id not in campaigns:
        return None, None, None, {
            "ok": False,
            "error": f"unknown campaign: {campaign_id}",
            "campaigns": list(campaigns.keys()),
        }
    campaign = campaigns[campaign_id]
    motor = (registry.get("subjects") or {}).get("motor_cloud") or {}
    patterns = list(motor.get("retired_patterns") or [])
    return campaign, motor, patterns, None


def run_scan_paste(
    *,
    campaign_id: str,
    text: str,
    label: str = "paste:snippet",
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or _read_json(REGISTRY_PATH)
    campaign, _motor, patterns, err = _campaign_context(campaign_id, registry)
    if err:
        return err
    assert campaign is not None and patterns is not None
    content = (text or "").strip()
    if not content:
        return {"ok": False, "error": "empty_paste", "message": "Paste text or a URL to scan."}
    hits = _scan_text(content, label, patterns=patterns, registry=registry, campaign=campaign)
    return _pack_scan_result(
        campaign_id=campaign_id,
        campaign=campaign,
        hits=hits,
        registry=registry,
        source_type="paste",
        source_label=label,
        files_scanned=1,
    )


def run_scan_url(
    *,
    campaign_id: str,
    url: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or _read_json(REGISTRY_PATH)
    campaign, _motor, patterns, err = _campaign_context(campaign_id, registry)
    if err:
        return err
    assert campaign is not None and patterns is not None
    fetched = fetch_url_text(url)
    if not fetched.get("ok"):
        return {
            "ok": False,
            "error": fetched.get("error") or "fetch_failed",
            "url": fetched.get("url") or url,
            "message": fetched.get("error") or "Could not fetch URL",
        }
    label = f"url:{fetched['url']}"
    hits = _scan_text(
        fetched.get("text") or "",
        label,
        patterns=patterns,
        registry=registry,
        campaign=campaign,
    )
    return _pack_scan_result(
        campaign_id=campaign_id,
        campaign=campaign,
        hits=hits,
        registry=registry,
        source_type="url",
        source_label=label,
        files_scanned=1,
        fetch_meta={k: v for k, v in fetched.items() if k != "text"},
    )


def run_scan_local_file(
    *,
    campaign_id: str,
    file_path: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or _read_json(REGISTRY_PATH)
    campaign, _motor, patterns, err = _campaign_context(campaign_id, registry)
    if err:
        return err
    assert campaign is not None and patterns is not None
    resolved = _resolve_local_file(file_path)
    if not resolved:
        return {
            "ok": False,
            "error": "file_not_found",
            "message": f"File not found or not allowed: {file_path}",
        }
    try:
        rel = resolved.relative_to(ROOT).as_posix()
    except ValueError:
        try:
            rel = resolved.relative_to(SINA).as_posix()
            rel = f"~/.sina/{rel}"
        except ValueError:
            rel = str(resolved)
    hits = _scan_file(resolved, patterns=patterns, registry=registry, campaign=campaign)
    return _pack_scan_result(
        campaign_id=campaign_id,
        campaign=campaign,
        hits=hits,
        registry=registry,
        source_type="file",
        source_label=rel,
        files_scanned=1,
        roots=[str(resolved.parent)],
    )


def run_scan_source(
    *,
    campaign_id: str,
    source_type: str = "repo",
    profiles: list[str] | None = None,
    url: str = "",
    paste: str = "",
    file_path: str = "",
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    st = (source_type or "repo").strip().lower()
    if st == "url":
        return run_scan_url(campaign_id=campaign_id, url=url, registry=registry)
    if st == "paste":
        return run_scan_paste(campaign_id=campaign_id, text=paste, registry=registry)
    if st == "file":
        return run_scan_local_file(campaign_id=campaign_id, file_path=file_path, registry=registry)
    return run_scan(campaign_id=campaign_id, profiles=profiles or ["sourcea_repo"], registry=registry)


def _dedupe_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for h in hits:
        key = (h.get("file"), h.get("line"), h.get("match"))
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return sorted(out, key=lambda x: (x.get("tier", 9), x.get("file", ""), x.get("line", 0)))


def run_scan(
    *,
    campaign_id: str,
    profiles: list[str],
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or _read_json(REGISTRY_PATH)
    campaigns = registry.get("campaigns") or {}
    if campaign_id not in campaigns:
        return {
            "ok": False,
            "error": f"unknown campaign: {campaign_id}",
            "campaigns": list(campaigns.keys()),
        }

    campaign = campaigns[campaign_id]
    motor = (registry.get("subjects") or {}).get("motor_cloud") or {}
    patterns = list(motor.get("retired_patterns") or [])

    scan_profiles = registry.get("scan_profiles") or {}
    all_hits: list[dict[str, Any]] = []
    scanned_files = 0
    profile_roots: list[str] = []

    for pid in profiles:
        prof = scan_profiles.get(pid)
        if not prof:
            continue
        roots = _resolve_roots(prof)
        profile_roots.extend(str(r) for r in roots)
        exts = prof.get("extensions") or [".py", ".js", ".html", ".json", ".md"]
        exclude = prof.get("exclude_dir_globs") or []
        for fpath in _iter_files(roots, extensions=exts, exclude_dir_globs=exclude):
            scanned_files += 1
            all_hits.extend(
                _scan_file(fpath, patterns=patterns, registry=registry, campaign=campaign)
            )

    hits = _dedupe_hits(all_hits)
    patch_hits = [h for h in hits if h.get("action") == "patch"]
    by_tier: dict[str, int] = {"1": 0, "2": 0, "3": 0}
    for h in hits:
        t = str(h.get("tier", 3))
        by_tier[t] = by_tier.get(t, 0) + 1

    return {
        "ok": True,
        "schema": "vocabulary-intelligence-scan-v1",
        "at": _now(),
        "campaign_id": campaign_id,
        "goal": campaign.get("goal"),
        "profiles": profiles,
        "roots": profile_roots,
        "files_scanned": scanned_files,
        "hits_total": len(hits),
        "hits_patch": len(patch_hits),
        "hits_by_tier": by_tier,
        "hits": hits,
        "patch_queue": patch_hits[:200],
        "registry": str(REGISTRY_PATH.relative_to(ROOT)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Vocabulary Intelligence Machine — scan v1")
    ap.add_argument("--campaign", default="motor-rename-v1", help="Campaign id from registry")
    ap.add_argument(
        "--profile",
        action="append",
        dest="profiles",
        help="Scan profile (repeatable). Default: sourcea_repo",
    )
    ap.add_argument("--write-receipt", action="store_true", help="Write ~/.sina/vocabulary-intelligence-scan-receipt-v1.json")
    ap.add_argument("--json", action="store_true", help="Print JSON summary")
    ap.add_argument("--tier", type=int, choices=[1, 2, 3], help="Filter output to one tier")
    args = ap.parse_args()

    profiles = args.profiles or ["sourcea_repo"]
    out = run_scan(campaign_id=args.campaign, profiles=profiles)

    if args.tier is not None and out.get("hits"):
        t = args.tier
        out["hits"] = [h for h in out["hits"] if h.get("tier") == t]
        out["patch_queue"] = [h for h in out.get("patch_queue") or [] if h.get("tier") == t]
        out["hits_total"] = len(out["hits"])
        out["hits_patch"] = len([h for h in out["hits"] if h.get("action") == "patch"])

    if args.write_receipt:
        _write_json(RECEIPT_PATH, out)

    if args.json:
        slim = {k: v for k, v in out.items() if k != "hits"}
        slim["hits_sample"] = (out.get("patch_queue") or [])[:25]
        print(json.dumps(slim if not args.tier else out, indent=2, ensure_ascii=False))
    else:
        if not out.get("ok"):
            print(out.get("error", "FAIL"))
            return 1
        print(
            f"VIM scan · campaign={args.campaign} · files={out.get('files_scanned')} · "
            f"hits={out.get('hits_total')} · patch={out.get('hits_patch')} · "
            f"tiers={out.get('hits_by_tier')}"
        )
        for h in (out.get("patch_queue") or [])[:15]:
            print(
                f"  T{h.get('tier')} {h.get('file')}:{h.get('line')} "
                f"{h.get('match')} → {h.get('suggestion')}"
            )
        if args.write_receipt:
            print(f"receipt: {RECEIPT_PATH}")

    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
