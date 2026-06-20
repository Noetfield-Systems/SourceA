#!/usr/bin/env python3
"""Commercial Mail draft — official FROM only; never personal Gmail/iCloud."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
BLOCKLIST = SINA / "founder-blocked-recipients-v1.json"
GATE_DOC = ROOT / "data" / "commercial-mail-from-gate-v1.json"
REQUIRED_W3_FROM = ("hello@trustfield.ca", "operation@noetfield.com")
MAIL_APPLESCRIPT_ALLOWLIST = frozenset({"commercial_mail_draft_v1.py"})

# SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md
LANE_FROM: dict[str, tuple[str, str]] = {
    "AB1": ("SourceA", "hello@sourcea.com"),
    "NW1": ("Noetfield Systems Inc.", "operations@noetfield.com"),
    "NF": ("Noetfield", "operation@noetfield.com"),
    "AEG": ("SourceA", "hello@sourcea.com"),
    "TF": ("TrustField Technologies", "hello@trustfield.ca"),
}

OFFICIAL_FROM = frozenset(email for _, email in LANE_FROM.values())

PERSONAL_FROM_SUFFIXES = (
    "@gmail.com",
    "@googlemail.com",
    "@icloud.com",
    "@me.com",
    "@mac.com",
    "@hotmail.com",
    "@outlook.com",
    "@live.com",
    "@yahoo.com",
)


def lane_from(lane: str) -> tuple[str, str]:
    key = str(lane or "AB1").strip().upper()
    return LANE_FROM.get(key, LANE_FROM["AB1"])


def _escape_apple(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def mail_configured_addresses() -> list[str]:
    disk = _disk_mail_addresses()
    script = (
        'tell application "Mail"\n'
        "  set out to {}\n"
        "  repeat with acct in accounts\n"
        "    set out to out & (email addresses of acct)\n"
        "  end repeat\n"
        "  return out\n"
        "end tell\n"
    )
    live: list[str] = []
    try:
        proc = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if proc.returncode == 0:
            raw = (proc.stdout or "").strip()
            if raw:
                live = [a.strip() for a in raw.split(",") if a.strip() and "@" in a]
    except (OSError, subprocess.TimeoutExpired):
        live = []
    merged: list[str] = []
    seen: set[str] = set()
    for addr in disk + live:
        key = addr.lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(addr)
    return merged


def _disk_mail_addresses() -> list[str]:
    """Founder-confirmed Mail FROM on disk when Mail.app probe unavailable."""
    ssot = SINA / "commercial-mail-from-ssot-v1.json"
    if not ssot.is_file():
        return []
    try:
        row = json.loads(ssot.read_text(encoding="utf-8"))
        if not row.get("founder_confirmed"):
            return []
        return [
            str(a.get("email") or "").strip()
            for a in (row.get("accounts") or [])
            if a.get("configured") and a.get("email")
        ]
    except (OSError, json.JSONDecodeError):
        return []


def is_personal_from(from_email: str) -> bool:
    t = str(from_email or "").strip().lower()
    if not t or "@" not in t:
        return True
    return any(t.endswith(sfx) for sfx in PERSONAL_FROM_SUFFIXES)


def assert_official_from_configured(from_email: str, *, lane: str = "") -> str:
    """Raise SystemExit if FROM is personal or not a Mail.app account."""
    from_addr = str(from_email or "").strip().lower()
    if not from_addr or "@" not in from_addr:
        raise SystemExit("FAIL: commercial send requires official from_email")
    if is_personal_from(from_addr):
        name, official = lane_from(lane)
        raise SystemExit(
            f"FAIL: personal email cannot send commercial outbound ({from_addr}).\n"
            f"  Use {official} ({name}) — SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md"
        )
    if from_addr not in OFFICIAL_FROM:
        raise SystemExit(
            f"FAIL: {from_addr} is not a locked commercial sender.\n"
            f"  Allowed: {', '.join(sorted(OFFICIAL_FROM))}"
        )
    configured = [a.lower() for a in mail_configured_addresses()]
    if from_addr not in configured:
        listed = ", ".join(configured) if configured else "(none)"
        name, _ = lane_from(lane)
        raise SystemExit(
            f"FAIL: {from_addr} is NOT configured in Mail.app — draft would send from personal Gmail.\n"
            f"  Mail.app accounts now: {listed}\n"
            f"  Fix: Mail → Settings → Accounts → Add Account → add {from_addr}\n"
            f"  Then re-run with --open-mail. Never send {lane or 'AB1'} from personal email."
        )
    return from_addr


def open_commercial_mail_draft(
    *,
    subject: str,
    body: str,
    to_email: str,
    from_email: str,
    from_name: str = "",
    lane: str = "",
    attachments: list[Path] | None = None,
    context: str = "commercial Mail",
) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from commercial_recipient_guard_v1 import assert_safe_before_open_mail  # noqa: WPS433

    safe_to = assert_safe_before_open_mail(to_email, context=context)
    assert_official_from_configured(from_email, lane=lane)
    sender = f"{from_name.strip()} <{from_email.strip()}>" if from_name.strip() else from_email.strip()
    escaped_body = _escape_apple(body).replace("\n", "\\n")
    escaped_subject = _escape_apple(subject)
    escaped_sender = _escape_apple(sender)
    to_clause = (
        f'make new to recipient at end of to recipients '
        f'with properties {{address:"{_escape_apple(safe_to)}"}}'
    )
    attach_lines: list[str] = []
    for path in attachments or []:
        if path.is_file():
            posix = str(path.resolve())
            attach_lines.append(
                '      make new attachment with properties '
                f'{{file name:POSIX file "{posix}"}} at after the last paragraph'
            )
    attach_block = ""
    if attach_lines:
        attach_block = (
            "    tell content\n"
            + "\n".join(attach_lines)
            + "\n    end tell\n"
        )
    script = (
        'tell application "Mail"\n'
        f'  set msg to make new outgoing message with properties {{sender:"{escaped_sender}", '
        f'subject:"{escaped_subject}", content:"{escaped_body}", visible:true}}\n'
        "  tell msg\n"
        f'    set sender to "{escaped_sender}"\n'
        f"    {to_clause}\n"
        f"{attach_block}"
        "  end tell\n"
        "  activate\n"
        "end tell\n"
    )
    subprocess.run(["osascript", "-e", script], check=True)


def ensure_founder_blocklist() -> None:
    """Seed ~/.sina blocklist so personal addresses never land in to.txt."""
    defaults = {
        "schema": "founder-blocked-recipients-v1",
        "blocked": [
            "sina.kazemnezhad@gmail.com",
            "sina.kazemnezhad@icloud.com",
            "me@sourcea.com",
        ],
    }
    if BLOCKLIST.is_file():
        return
    BLOCKLIST.parent.mkdir(parents=True, exist_ok=True)
    BLOCKLIST.write_text(json.dumps(defaults, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _scan_agent_mail_configure_violations() -> list[dict]:
    """U069 — only allowlisted scripts may AppleScript Mail.app."""
    violations: list[dict] = []
    for py in (ROOT / "scripts").glob("*.py"):
        if py.name in MAIL_APPLESCRIPT_ALLOWLIST:
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if 'tell application "Mail"' in text or "tell application 'Mail'" in text:
            violations.append({"script": py.name, "issue": "mail_applescript_outside_allowlist"})
    return violations


def validate_mail_from_gate_acceptance() -> dict:
    """U069 acceptance — founder configures Mail FROM · agents never configure Mail."""
    gate = _read_json(GATE_DOC)
    gate_ok = (
        gate.get("schema") == "commercial-mail-from-gate-v1"
        and gate.get("founder_only_configure") is True
        and gate.get("nerve_gate") == "w3_mail_from"
    )
    configured = {a.lower() for a in mail_configured_addresses()}
    w3_ok = all(addr in configured for addr in REQUIRED_W3_FROM)
    violations = _scan_agent_mail_configure_violations()
    nerve_receipt = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    ship = nerve_receipt.get("ship_gates") or {}
    nerve_ok = bool(ship.get("w3_mail_from_configured")) or w3_ok
    nerve_row = {"w3_mail_from_configured": ship.get("w3_mail_from_configured")}
    ok = gate_ok and w3_ok and nerve_ok and not violations
    return {
        "ok": ok,
        "upgrade": "U069",
        "gate_doc": str(GATE_DOC.relative_to(ROOT)),
        "gate_ok": gate_ok,
        "w3_mail_from": w3_ok,
        "nerve_w3_mail_from_configured": nerve_row.get("w3_mail_from_configured"),
        "configured_accounts": sorted(configured),
        "required_from": list(REQUIRED_W3_FROM),
        "mail_script_violations": violations,
        "acceptance": "Agent never configures Mail",
        "check": "python3 scripts/commercial_mail_draft_v1.py --check-mail-from-gate --json",
        "founder_action": "Mail → Settings → Accounts — founder adds official FROM only",
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Commercial Mail sender guard")
    ap.add_argument("--lane", default="AB1", help="AB1 | NW1 | AEG | TF")
    ap.add_argument("--check-mail", action="store_true", help="Verify official FROM in Mail.app")
    ap.add_argument("--check-mail-from-gate", action="store_true", help="U069 — founder-only Mail FROM gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.check_mail_from_gate:
        row = validate_mail_from_gate_acceptance()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print("check_mail_from_gate:", "PASS" if row.get("ok") else row)
        return 0 if row.get("ok") else 1
    ensure_founder_blocklist()
    name, email = lane_from(args.lane)
    configured = mail_configured_addresses()
    ok = email.lower() in [a.lower() for a in configured]
    row = {
        "ok": ok,
        "lane": args.lane.upper(),
        "from_name": name,
        "from_email": email,
        "mail_accounts": configured,
        "personal_blocked": True,
    }
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if ok:
            print(f"OK: {email} configured in Mail.app")
        else:
            print(f"FAIL: {email} NOT in Mail.app — accounts: {', '.join(configured) or 'none'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
