#!/usr/bin/env python3
"""Commercial outbound guard — recipients, public URLs, no personal email."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

SINA = Path.home() / ".sina"
BLOCKLIST = SINA / "founder-blocked-recipients-v1.json"
PUBLIC_URLS = SINA / "sourcea-public-urls-v1.json"
PLACEHOLDER = "PASTE_RECIPIENT@company.com"
CANONICAL_W1 = "https://sourcea.com/sourcea/proof.html#w1-demo-film"
LOCALHOST_MARKERS = ("127.0.0.1", "localhost", "0.0.0.0")

# Commercial FROM addresses — valid TO for prospects only, never auto-target
COMMERCIAL_FROM = frozenset(
    {
        "hello@sourcea.app",
        "operations@noetfield.com",
        "operation@noetfield.com",
        "hello@trustfield.ca",
    }
)


def _load_blocklist() -> set[str]:
    blocked: set[str] = set()
    env = os.environ.get("SOURCEA_FOUNDER_BLOCKED_EMAILS", "").strip()
    for part in env.split(","):
        e = part.strip().lower()
        if e and "@" in e:
            blocked.add(e)
    if BLOCKLIST.is_file():
        try:
            data = json.loads(BLOCKLIST.read_text(encoding="utf-8"))
            for e in data.get("blocked") or []:
                if str(e).strip() and "@" in str(e):
                    blocked.add(str(e).strip().lower())
        except (OSError, json.JSONDecodeError):
            pass
    return blocked


def normalize_to(to_email: str) -> str:
    return str(to_email or "").strip()


def is_placeholder_to(to_email: str) -> bool:
    t = normalize_to(to_email).lower()
    return not t or "paste" in t or t == PLACEHOLDER.lower()


def is_blocked_recipient(to_email: str) -> tuple[bool, str]:
    t = normalize_to(to_email).lower()
    if not t or "@" not in t:
        return True, "empty or invalid recipient"
    if t in COMMERCIAL_FROM:
        return True, "cannot send commercial outbound to your own FROM address"
    for b in _load_blocklist():
        if t == b:
            return True, f"blocked founder/personal address ({b})"
    personal_domains = ("@gmail.com", "@googlemail.com", "@icloud.com", "@me.com", "@mac.com", "@hotmail.com", "@outlook.com", "@live.com", "@yahoo.com")
    if any(t.endswith(dom) for dom in personal_domains):
        for b in _load_blocklist():
            if t == b:
                return True, f"blocked founder/personal address ({b})"
        return True, f"personal email domain blocked for commercial To ({t})"
    founder_hint = os.environ.get("SOURCEA_FOUNDER_EMAIL_LOCAL", "").strip().lower()
    if founder_hint and founder_hint in t:
        for dom in personal_domains:
            if t.endswith(dom):
                return True, f"looks like founder personal email ({t})"
    return False, ""


def assert_valid_outbound_to(to_email: str, *, context: str = "outbound") -> str:
    """Raise SystemExit if To is missing, placeholder, or blocked."""
    to = normalize_to(to_email)
    if is_placeholder_to(to):
        raise SystemExit(
            f"FAIL: {context} — recipient required.\n"
            "  Pass --to prospect@company.com (never your personal me@).\n"
            f"  Placeholder {PLACEHOLDER} is draft-only — not sendable."
        )
    bad, reason = is_blocked_recipient(to)
    if bad:
        raise SystemExit(f"FAIL: {context} — blocked recipient: {reason}")
    return to


def assert_safe_before_open_mail(to_email: str, *, context: str = "Mail draft") -> str:
    return assert_valid_outbound_to(to_email, context=context)


_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)


def _urls_in_text(text: str) -> list[str]:
    return _URL_RE.findall(str(text or ""))


def is_localhost_url(url: str) -> bool:
    raw = str(url or "").strip()
    if not raw:
        return True
    if any(m in raw.lower() for m in LOCALHOST_MARKERS):
        return True
    try:
        host = (urlparse(raw).hostname or "").lower()
    except ValueError:
        return True
    return host in ("127.0.0.1", "localhost", "0.0.0.0")


def assert_public_outbound_url(url: str, *, label: str = "URL") -> str:
    u = str(url or "").strip()
    if not u.startswith("https://"):
        raise SystemExit(
            f"FAIL: {label} must be public https — got {u!r}\n"
            "  Set SOURCEA_W1_PROOF_URL or ~/.sina/sourcea-public-urls-v1.json"
        )
    if is_localhost_url(u):
        raise SystemExit(
            f"FAIL: {label} cannot be localhost — prospects cannot open {u}\n"
            f"  Use {CANONICAL_W1} or publish landing first."
        )
    return u


def _read_public_urls() -> dict:
    if not PUBLIC_URLS.is_file():
        return {}
    try:
        row = json.loads(PUBLIC_URLS.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_aeg_proof_url() -> str:
    """Buyer-facing live AEG proof on SourceA landing — not forensic file:// bundle."""
    env = os.environ.get("SOURCEA_AEG_LIVE_URL", "").strip()
    if env and not is_localhost_url(env):
        return assert_public_outbound_url(env, label="SOURCEA_AEG_LIVE_URL")
    row = _read_public_urls()
    u = str(row.get("aeg_live_url") or "").strip()
    if u and not is_localhost_url(u):
        return assert_public_outbound_url(u, label="aeg_live_url")
    base = str(row.get("base_url") or "").strip().rstrip("/")
    if base and not is_localhost_url(base):
        return assert_public_outbound_url(f"{base}/sourcea/proof/live.html", label="aeg_live derived")
    local = os.environ.get("SOURCEA_LOCAL_BASE", "http://127.0.0.1:5180").strip().rstrip("/")
    return f"{local}/sourcea/proof/live.html"


def resolve_w1_proof_url() -> str:
    """Public W1 film URL for outbound packs — never localhost."""
    env = os.environ.get("SOURCEA_W1_PROOF_URL", "").strip()
    if env and not is_localhost_url(env):
        return assert_public_outbound_url(env, label="SOURCEA_W1_PROOF_URL")
    row = _read_public_urls()
    u = str(row.get("w1_proof_url") or "").strip()
    if u and not is_localhost_url(u):
        return assert_public_outbound_url(u, label="w1_proof_url")
    return assert_public_outbound_url(CANONICAL_W1, label="W1 proof page")


def resolve_scenario_url() -> str:
    """Public scenario demo URL — primary AB1 proof link after publish."""
    env = os.environ.get("SOURCEA_SCENARIO_URL", "").strip()
    if env and not is_localhost_url(env):
        return assert_public_outbound_url(env, label="SOURCEA_SCENARIO_URL")
    row = _read_public_urls()
    u = str(row.get("scenario_url") or "").strip()
    if u and not is_localhost_url(u):
        return assert_public_outbound_url(u, label="scenario_url")
    return assert_public_outbound_url("https://sourcea.com/sourcea/scenario.html", label="scenario page")


def resolve_demo_proof_url(*, lane: str = "AB1") -> str:
    """Outbound demo link — live AEG on site for AB1; NW1 may use dedicated proof surface."""
    lane_u = str(lane or "AB1").upper()
    if lane_u == "AB1":
        aeg = SINA / "aeg-latest-receipt-v1.json"
        if aeg.is_file():
            try:
                if json.loads(aeg.read_text(encoding="utf-8")).get("evidence_id"):
                    return resolve_aeg_proof_url()
            except (OSError, json.JSONDecodeError):
                pass
    if lane_u == "NW1":
        env = os.environ.get("SOURCEA_NW1_PROOF_URL", "").strip()
        if env and not is_localhost_url(env):
            return assert_public_outbound_url(env, label="SOURCEA_NW1_PROOF_URL")
        row = _read_public_urls()
        u = str(row.get("proof_url") or "").strip()
        if u and not is_localhost_url(u):
            return assert_public_outbound_url(u, label="proof_url")
    return resolve_scenario_url()


def scan_outbound_packs(outbound_root: Path | None = None) -> list[dict]:
    root = outbound_root or (SINA / "outbound")
    issues: list[dict] = []
    if not root.is_dir():
        return issues
    for pack_dir in sorted(root.iterdir()):
        if not pack_dir.is_dir():
            continue
        name = pack_dir.name
        to_file = pack_dir / "to.txt"
        if to_file.is_file():
            to = to_file.read_text(encoding="utf-8").strip()
            if is_placeholder_to(to):
                issues.append({"pack": name, "field": "to.txt", "value": to, "issue": "placeholder"})
            else:
                bad, reason = is_blocked_recipient(to)
                if bad:
                    issues.append({"pack": name, "field": "to.txt", "value": to, "issue": reason})
        from_file = pack_dir / "from.txt"
        if from_file.is_file():
            from_line = from_file.read_text(encoding="utf-8").strip().lower()
            if "gmail.com" in from_line or "icloud.com" in from_line:
                issues.append({"pack": name, "field": "from.txt", "value": from_line, "issue": "personal from"})
            elif not any(addr in from_line for addr in COMMERCIAL_FROM):
                issues.append({"pack": name, "field": "from.txt", "value": from_line, "issue": "non-official from"})
        body_file = pack_dir / "body.txt"
        if body_file.is_file():
            body = body_file.read_text(encoding="utf-8")
            for url in _urls_in_text(body):
                if is_localhost_url(url):
                    issues.append({"pack": name, "field": "body.txt", "value": url, "issue": "localhost url"})
        pack_json = pack_dir / "pack.json"
        if pack_json.is_file():
            try:
                meta = json.loads(pack_json.read_text(encoding="utf-8"))
                for key in ("w1_film_url", "proof_url"):
                    val = str(meta.get(key) or "")
                    if val and is_localhost_url(val):
                        issues.append({"pack": name, "field": key, "value": val, "issue": "localhost url"})
            except (OSError, json.JSONDecodeError):
                issues.append({"pack": name, "field": "pack.json", "issue": "invalid json"})
    return issues


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Scan outbound packs for unsafe recipients")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    issues = scan_outbound_packs()
    blocked = [i for i in issues if i.get("issue") not in ("placeholder",)]
    placeholders = [i for i in issues if i.get("issue") == "placeholder"]
    localhost = [i for i in issues if i.get("issue") == "localhost url"]
    personal_from = [i for i in issues if i.get("issue") == "personal from"]
    payload = {
        "ok": len(blocked) == 0,
        "blocked": blocked,
        "placeholders": len(placeholders),
        "localhost_urls": len(localhost),
        "personal_from": len(personal_from),
        "issues": issues,
    }
    if args.json:
        import json as _json

        print(_json.dumps(payload, indent=2))
    else:
        if blocked:
            for i in blocked:
                print(
                    f"BLOCKED: {i['pack']}\t{i.get('field','')}\t{i.get('value','')}\t{i['issue']}"
                )
        else:
            print(
                f"OK: {len(placeholders)} draft placeholder(s) · "
                f"no founder/personal/localhost in sendable packs"
            )
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
