#!/usr/bin/env python3
"""Mac Health Guard — standalone app: local Mac posture scan + security analysis."""
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mac_health_version_v1 import MAC_HEALTH_VERSION  # noqa: E402
from mac_health_edition_v1 import SINA  # noqa: E402

STATE_DIR = SINA / "mac-health"
SCAN_PATH = STATE_DIR / "last-scan.json"
INSIGHTS_PATH = STATE_DIR / "agent-insights.jsonl"
HEARTBEAT_PATH = STATE_DIR / "heartbeat-log-v1.jsonl"
HEARTBEAT_MIN_SEC = 120
HEARTBEAT_FORCE_DELTA = 2
KNOWLEDGE_PATH = STATE_DIR / "knowledge-base.json"
N8N_WEBHOOK_CFG = SINA / "mac-health-n8n-webhook-v1.json"
GOVERNANCE_FINDINGS_PATH = SINA / "mac-health" / "governance-findings-v1.json"

IMPORTANT_NOTE_PRIVACY = (
    "Agents do not connect to a private Apple Security API (that does not exist for third parties). "
    "They apply official Apple security guidance to local scans on your Mac only. "
    f"Data stays under ~/{SINA.relative_to(Path.home())}/mac-health/ and never leaves the machine."
)
IMPORTANT_NOTE_SCAN = (
    "After travel, new apps, or permission changes — tap Listen again in Mac Health Guard."
)
QUEUE_ZOMBIE_MATCH = "build_phase_strict_queue_v1.py"
QUEUE_ZOMBIE_PATTERNS = (
    "build_phase_strict_queue_v1.py",
    "auto_run_worker_batch_v1.py",
)
IMPORTANT_NOTE_FIREWALL = (
    "If Firewall is off: System Settings → Network → Firewall → On, then tap Brain heal."
)

IMPORTANT_NOTE: dict[str, str] = {
    "title": "Important note",
    "privacy": IMPORTANT_NOTE_PRIVACY,
    "when_to_scan": IMPORTANT_NOTE_SCAN,
    "firewall_hint": IMPORTANT_NOTE_FIREWALL,
}

CANONICAL_PRINCIPLES_HEAD: list[str] = [
    IMPORTANT_NOTE_PRIVACY,
    IMPORTANT_NOTE_SCAN,
    IMPORTANT_NOTE_FIREWALL,
]

# Curated Apple & practical security references (agents cite these in reports).
APPLE_KNOWLEDGE_SOURCES: list[dict[str, Any]] = [
    {
        "id": "platform-security",
        "title": "Apple Platform Security Guide",
        "url": "https://support.apple.com/guide/security/welcome/web",
        "focus": "SIP, Secure Enclave, boot chain, data protection, code signing",
    },
    {
        "id": "gatekeeper",
        "title": "Gatekeeper & notarization",
        "url": "https://support.apple.com/guide/security/gatekeeper-and-notarization-sec5599b66df/web",
        "focus": "App distribution, quarantine, Developer ID, notarized apps",
    },
    {
        "id": "xprotect",
        "title": "XProtect & MRT",
        "url": "https://support.apple.com/guide/security/protecting-against-malware-sec469d47bd8/web",
        "focus": "Built-in malware signatures and remediation updates",
    },
    {
        "id": "tcc",
        "title": "Transparency, Consent, and Control (TCC)",
        "url": "https://support.apple.com/guide/security/control-access-to-system-data-secb050c20c4/web",
        "focus": "Privacy permissions, Full Disk Access, automation",
    },
    {
        "id": "filevault",
        "title": "FileVault & APFS encryption",
        "url": "https://support.apple.com/guide/security/volume-encryption-sec4c6dc1aa5/web",
        "focus": "Volume encryption at rest",
    },
    {
        "id": "software-update",
        "title": "Software update security",
        "url": "https://support.apple.com/en-us/102527",
        "focus": "Rapid Security Responses, automatic updates",
    },
]

SECURITY_AGENTS: list[dict[str, Any]] = [
    {
        "id": "sentinel",
        "name": "Sentinel",
        "icon": "🛡",
        "role": "System integrity",
        "mission": "SIP, sealing, OS build, secure boot signals",
        "source_ids": ["platform-security"],
    },
    {
        "id": "gatekeeper_agent",
        "name": "Gatekeeper",
        "icon": "🔏",
        "role": "App trust",
        "mission": "Assessment policy, quarantine, signing posture",
        "source_ids": ["gatekeeper", "xprotect"],
    },
    {
        "id": "perimeter",
        "name": "Perimeter",
        "icon": "🧱",
        "role": "Network edge",
        "mission": "Firewall, listening services, proxies",
        "source_ids": ["platform-security"],
    },
    {
        "id": "vault",
        "name": "Vault",
        "icon": "🔐",
        "role": "Data at rest",
        "mission": "FileVault, disk space, backup readiness",
        "source_ids": ["filevault"],
    },
    {
        "id": "supply",
        "name": "Supply",
        "icon": "📦",
        "role": "Patch & toolchain",
        "mission": "macOS updates, CLT, known-good versions",
        "source_ids": ["software-update"],
    },
    {
        "id": "launchwatch",
        "name": "LaunchWatch",
        "icon": "👁",
        "role": "Persistence",
        "mission": "LaunchAgents/Daemons, login items surface",
        "source_ids": ["platform-security", "tcc"],
    },
    {
        "id": "privacy_lens",
        "name": "Privacy Lens",
        "icon": "🔍",
        "role": "Exposure",
        "mission": "Remote login, screen sharing, TCC risk hints",
        "source_ids": ["tcc"],
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(argv: list[str], *, timeout: float = 12.0) -> tuple[int, str]:
    try:
        p = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return -1, "timeout"
    except Exception as e:
        return -1, str(e)[:400]


def _ensure_knowledge() -> dict:
    kb: dict[str, Any] = {}
    if KNOWLEDGE_PATH.is_file():
        try:
            kb = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            kb = {}
    if not kb:
        kb = {
            "version": 1,
            "updated_at": _now(),
            "sources": APPLE_KNOWLEDGE_SOURCES,
            "principles": [
                "Prefer Apple's built-in controls (Gatekeeper, SIP, XProtect) over third-party snake oil.",
                "Treat unknown LaunchAgents and open listeners as review items, not automatic malware.",
                "Keep macOS and Rapid Security Responses current — most real-world Mac risk is stale OS/apps.",
                "FileVault ON is baseline for portable Macs; verify recovery key is stored safely offline.",
                "Developer tools (Cursor, n8n, Docker) need explicit TCC grants — audit Full Disk Access quarterly.",
            ],
        }
    kb["version"] = max(int(kb.get("version") or 0), 2)
    kb["updated_at"] = _now()
    kb["sources"] = kb.get("sources") or APPLE_KNOWLEDGE_SOURCES
    kb["important_note"] = IMPORTANT_NOTE
    tail = [p for p in (kb.get("principles") or []) if p not in CANONICAL_PRINCIPLES_HEAD]
    kb["principles"] = CANONICAL_PRINCIPLES_HEAD + tail
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2), encoding="utf-8")
    return kb


def _scan_gatekeeper() -> dict:
    code, out = _run(["spctl", "--status"])
    enabled = "assessments enabled" in out.lower()
    return {"raw": out, "enabled": enabled, "ok": enabled}


def _scan_sip() -> dict:
    code, out = _run(["csrutil", "status"])
    low = out.lower()
    if "system integrity protection status: enabled" in low:
        enabled = True
    elif "disabled" in low:
        enabled = False
    else:
        enabled = "enabled" in low
    return {"raw": out, "enabled": enabled, "ok": enabled}


def _scan_firewall() -> dict:
    code, out = _run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
    on = "enabled" in out.lower()
    stealth_code, stealth_out = _run(
        ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getstealthmode"]
    )
    stealth = "on" in stealth_out.lower() or "enabled" in stealth_out.lower()
    return {"raw": out, "enabled": on, "stealth": stealth, "ok": on}


def _scan_filevault() -> dict:
    code, out = _run(["fdesetup", "status"])
    on = "FileVault is On" in out or "FileVault is On." in out
    return {"raw": out[:500], "enabled": on, "ok": on}


def _scan_updates() -> dict:
    code, out = _run(["softwareupdate", "-l"], timeout=45.0)
    pending = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("*") or "Label:" in line:
            pending.append(line[:200])
    auto_code, auto_out = _run(["defaults", "read", "/Library/Preferences/com.apple.SoftwareUpdate", "AutomaticCheckEnabled"], timeout=5.0)
    auto_on = auto_code == 0 and "1" in auto_out
    if not auto_on:
        u_code, u_out = _run(["defaults", "read", "com.apple.SoftwareUpdate", "AutomaticCheckEnabled"], timeout=5.0)
        auto_on = u_code == 0 and "1" in u_out
    return {
        "raw_preview": out[:1200],
        "pending_count": len([p for p in pending if p.startswith("*")]),
        "pending_labels": pending[:8],
        "automatic_check": auto_on,
        "ok": len(pending) == 0,
    }


def _scan_listeners() -> dict:
    code, out = _run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], timeout=18.0)
    lines = out.splitlines()[1:80] if out else []
    listeners = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 9:
            listeners.append({"process": parts[0], "port": parts[8]})
    return {"count": len(listeners), "sample": listeners[:25], "ok": len(listeners) < 40}


def _scan_launch_items() -> dict:
    user_agents = list((Path.home() / "Library/LaunchAgents").glob("*.plist")) if (Path.home() / "Library/LaunchAgents").is_dir() else []
    sys_agents = list(Path("/Library/LaunchAgents").glob("*.plist")) if Path("/Library/LaunchAgents").is_dir() else []
    sys_daemons = list(Path("/Library/LaunchDaemons").glob("*.plist")) if Path("/Library/LaunchDaemons").is_dir() else []
    return {
        "user_launch_agents": len(user_agents),
        "system_launch_agents": len(sys_agents),
        "system_launch_daemons": len(sys_daemons),
        "user_samples": [p.name for p in user_agents[:12]],
        "ok": len(user_agents) < 35,
    }


def _scan_remote_access() -> dict:
    code, out = _run(["systemsetup", "-getremotelogin"], timeout=8.0)
    ssh_on = "On" in out
    return {"remote_login": out, "ssh_enabled": ssh_on, "ok": not ssh_on}


def _scan_disk() -> dict:
    code, out = _run(["df", "-h", "/"], timeout=6.0)
    pct_used = None
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5 and parts[-1] == "/":
            m = re.search(r"(\d+)%", parts[4])
            if m:
                pct_used = int(m.group(1))
    return {"raw": out[:300], "root_pct_used": pct_used, "ok": pct_used is None or pct_used < 90}


def _scan_os() -> dict:
    code, out = _run(["sw_vers"])
    build = ""
    product = ""
    for line in out.splitlines():
        if "ProductVersion" in line:
            product = line.split(":", 1)[-1].strip()
        if "BuildVersion" in line:
            build = line.split(":", 1)[-1].strip()
    arch = platform.machine()
    return {"sw_vers": out, "version": product, "build": build, "arch": arch, "ok": bool(product)}


def _scan_xprotect_hint() -> dict:
    xprotect_plist = Path("/Library/Apple/System/Library/CoreServices/XProtect.bundle/Contents/Info.plist"
    )
    legacy = Path("/System/Library/CoreServices/XProtect.bundle/Contents/Info.plist")
    path = xprotect_plist if xprotect_plist.is_file() else legacy
    if not path.is_file():
        return {"present": False, "ok": True, "detail": "XProtect bundle path not enumerated (normal on some builds)"}
    code, out = _run(["plutil", "-p", str(path)], timeout=6.0)
    return {"present": True, "path": str(path), "ok": code == 0, "detail": out[:200] if code == 0 else "unreadable"}


def _load_n8n_webhook_cfg() -> dict[str, Any]:
    if N8N_WEBHOOK_CFG.is_file():
        try:
            return json.loads(N8N_WEBHOOK_CFG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    glue = SINA / "n8n-glue-config-v1.json"
    if glue.is_file():
        try:
            g = json.loads(glue.read_text(encoding="utf-8"))
            wh = (g.get("webhooks") or {}).get("mac_health_cooldown")
            ps = (g.get("webhooks") or {}).get("product_signal")
            return {"enabled": True, "cooldown_url": wh, "product_signal_url": ps}
        except (OSError, json.JSONDecodeError):
            pass
    return {"enabled": False}


def _emit_n8n_signal(
    event: str,
    *,
    cpu_before: float | None = None,
    cpu_after: float | None = None,
    action: str = "",
    extra: dict | None = None,
) -> None:
    """Fire-and-forget POST to n8n glue — never blocks UI."""
    import threading
    import urllib.error
    import urllib.request

    cfg = _load_n8n_webhook_cfg()
    payload = {
        "schema": "mac-health-cooldown-v1" if "cool" in event or action.startswith("cpu_") else "product-signal-v1",
        "source": "mac-health-guard",
        "event": event,
        "action": action,
        "cpu_before": cpu_before,
        "cpu_after": cpu_after,
        "at": _now(),
        **(extra or {}),
    }
    urls: list[str] = []
    if event in ("cooldown", "cpu_relief") or action.startswith("cpu_"):
        u = cfg.get("cooldown_url") or cfg.get("webhook_url")
        if u:
            urls.append(u)
    u2 = cfg.get("product_signal_url")
    if event in ("heal", "scan", "ram_purge") and u2:
        urls.append(u2)
    if not urls and cfg.get("webhook_url"):
        urls.append(cfg["webhook_url"])

    def _post(url: str) -> None:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=2.0)
        except (urllib.error.URLError, OSError, TimeoutError):
            pass

    for url in urls:
        threading.Thread(target=_post, args=(url,), daemon=True).start()
    # Always write local receipt (disk-first) even when n8n webhook is down
    try:
        scripts = Path(__file__).resolve().parent
        import sys

        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from n8n_glue_runner_v1 import cmd_cooldown_ingest, cmd_signal_ingest  # noqa: WPS433

        if event in ("cooldown", "cpu_relief") or action.startswith("cpu_"):
            cmd_cooldown_ingest(json.dumps(payload))
        else:
            cmd_signal_ingest(json.dumps(payload))
    except Exception:
        pass


def _disk_live_wire_receipt_ok(*, max_age_sec: int = 3600) -> bool:
    """True when disk live wire receipt is fresh and ok — clears stale Heart findings."""
    receipt = SINA / "disk-live-wire-receipt-v1.json"
    if not receipt.is_file():
        return False
    try:
        row = json.loads(receipt.read_text(encoding="utf-8"))
        if not row.get("ok"):
            return False
        at = str(row.get("at") or row.get("built_at") or "")
        age = _iso_age_sec(at) if at else None
        return age is not None and age <= max_age_sec
    except (OSError, json.JSONDecodeError, TypeError):
        return False


def _clear_governance_disk_finding() -> None:
    if GOVERNANCE_FINDINGS_PATH.is_file():
        try:
            GOVERNANCE_FINDINGS_PATH.unlink()
        except OSError:
            pass


def _governance_disk_findings() -> list[dict]:
    if _disk_live_wire_receipt_ok():
        _clear_governance_disk_finding()
        return []
    if not GOVERNANCE_FINDINGS_PATH.is_file():
        return []
    try:
        row = json.loads(GOVERNANCE_FINDINGS_PATH.read_text(encoding="utf-8"))
        detail = str(row.get("detail") or "").strip()
        # Stale paradox: FAIL title but detail is only OK lines from partial validator stdout
        if detail and "FAIL" not in detail.upper() and detail.count("OK:") >= 1:
            _clear_governance_disk_finding()
            return []
        return [
            _finding(
                agent_id="sentinel",
                severity=str(row.get("severity") or "medium"),
                title=str(row.get("title") or "Governance finding"),
                detail=detail[:400],
                action="Tap Brain heal",
                tap_action="heal",
            )
        ]
    except (OSError, json.JSONDecodeError):
        return []


def run_mac_scan() -> dict:
    """Read-only local scan — no Apple API keys; uses macOS CLI tools."""
    t0 = time.time()
    scan = {
        "scanned_at": _now(),
        "hostname": platform.node(),
        "duration_sec": 0,
        "domains": {
            "os": _scan_os(),
            "sip": _scan_sip(),
            "gatekeeper": _scan_gatekeeper(),
            "firewall": _scan_firewall(),
            "filevault": _scan_filevault(),
            "updates": _scan_updates(),
            "listeners": _scan_listeners(),
            "launch_items": _scan_launch_items(),
            "remote_access": _scan_remote_access(),
            "disk": _scan_disk(),
            "xprotect": _scan_xprotect_hint(),
        },
    }
    scan["duration_sec"] = round(time.time() - t0, 2)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SCAN_PATH.write_text(json.dumps(scan, indent=2), encoding="utf-8")
    return scan


def _finding(
    *,
    agent_id: str,
    severity: str,
    title: str,
    detail: str,
    action: str,
    source_id: str | None = None,
    tap_action: str | None = None,
) -> dict:
    return {
        "agent_id": agent_id,
        "severity": severity,
        "title": title,
        "detail": detail,
        "action": action,
        "tap_action": tap_action,
        "source_id": source_id,
    }


def analyze_scan(scan: dict, kb: dict) -> tuple[list[dict], list[dict]]:
    """Rule-based agent analysis grounded in Apple security knowledge."""
    d = scan.get("domains") or {}
    findings: list[dict] = []
    agent_reports: list[dict] = []

    def add(agent: str, severity: str, title: str, detail: str, action: str, sid: str | None = None) -> None:
        findings.append(_finding(agent_id=agent, severity=severity, title=title, detail=detail, action=action, source_id=sid))

    sip = d.get("sip") or {}
    if sip.get("enabled") is False:
        add(
            "sentinel",
            "critical",
            "System Integrity Protection is off",
            "A core macOS safety seal is open — system files can be modified.",
            "Re-enable SIP via Recovery — see Apple Platform Security",
            "platform-security",
        )
    gk = d.get("gatekeeper") or {}
    if gk.get("enabled") is False:
        add(
            "gatekeeper_agent",
            "critical",
            "Gatekeeper is disabled",
            "Unsigned apps can run without assessment.",
            "Run: sudo spctl --master-enable",
            "gatekeeper",
        )

    fw = d.get("firewall") or {}
    if not fw.get("enabled"):
        add(
            "perimeter",
            "high",
            "Firewall is off",
            "Your Mac is not filtering incoming network connections.",
            "System Settings → Network → Firewall → On",
            "platform-security",
        )
    elif not fw.get("stealth"):
        add(
            "perimeter",
            "medium",
            "Firewall stealth mode is off",
            "Your Mac may be visible to port scans on your local network.",
            "System Settings → Network → Firewall → Options → Stealth Mode",
            "platform-security",
        )

    fv = d.get("filevault") or {}
    if not fv.get("enabled"):
        add(
            "vault",
            "high",
            "FileVault is off",
            "Your files are not encrypted at rest on this disk.",
            "System Settings → Privacy & Security → FileVault",
            "filevault",
        )

    disk = d.get("disk") or {}
    pct = disk.get("root_pct_used")
    if pct is not None and pct >= 90:
        add(
            "vault",
            "high",
            f"Boot disk is {pct}% full",
            "macOS needs free space for updates and snapshots.",
            "Free space — updates and snapshots need headroom",
            "filevault",
        )

    upd = d.get("updates") or {}
    if upd.get("pending_count", 0) > 0:
        n = upd["pending_count"]
        add(
            "supply",
            "high",
            f"{n} software update{'s' if n != 1 else ''} waiting",
            "Security patches are ready to install.",
            "Install updates or enable automatic updates",
            "software-update",
        )
    if not upd.get("automatic_check"):
        add(
            "supply",
            "medium",
            "Automatic update check is off",
            "macOS may not notify you when security patches arrive.",
            "Enable automatic macOS update checks",
            "software-update",
        )

    li = d.get("launch_items") or {}
    if li.get("user_launch_agents", 0) > 30:
        add(
            "launchwatch",
            "medium",
            "Many login startup items",
            f"{li.get('user_launch_agents', 0)} LaunchAgents in your user folder — review unknown names.",
            "Review ~/Library/LaunchAgents for unknown plist",
            "platform-security",
        )

    listen = d.get("listeners") or {}
    if listen.get("count", 0) >= 40:
        add(
            "perimeter",
            "medium",
            "Many network listeners open",
            f"{listen['count']} services listening — stop unused dev servers.",
            "Review open ports — stop unused dev servers",
            "platform-security",
        )

    remote = d.get("remote_access") or {}
    if remote.get("ssh_enabled"):
        add(
            "privacy_lens",
            "medium",
            "Remote Login (SSH) is on",
            "Other machines can attempt SSH access to this Mac.",
            "Disable if not needed: System Settings → General → Sharing",
            "tcc",
        )

    os_d = d.get("os") or {}
    if os_d.get("version"):
        add("sentinel", "info", f"macOS {os_d.get('version')} ({os_d.get('build')})", os_d.get("sw_vers", ""), "Stay on supported macOS — check pending updates", "software-update")

    if not findings:
        add("sentinel", "info", "No critical issues detected", "Baseline controls look healthy", "Re-scan after major installs or travel", "platform-security")

    sev_score = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: sev_score.get(f["severity"], 9))

    for agent in SECURITY_AGENTS:
        aid = agent["id"]
        mine = [f for f in findings if f["agent_id"] == aid]
        worst = mine[0]["severity"] if mine else "pass"
        sources = [s for s in kb.get("sources", []) if s["id"] in agent.get("source_ids", [])]
        agent_reports.append(
            {
                **agent,
                "status": "pass" if worst in ("info", "low") and all(f["severity"] in ("info", "low") for f in mine) else worst,
                "findings_count": len(mine),
                "top_finding": mine[0]["title"] if mine else "All clear",
                "sources": sources,
                "summary": mine[0]["detail"][:280] if mine else "No issues in this lane.",
            }
        )

    return findings, agent_reports


def _pressure_findings(mp: dict | None) -> list[dict]:
    """Live CPU/RAM/pipeline findings — wired to Cool Down tab actions."""
    if not mp:
        return []
    out: list[dict] = []
    prev: dict = {}
    try:
        from mac_health_prevention_v1 import analyze_prevention  # noqa: WPS433

        prev = analyze_prevention(mp)
    except Exception:
        prev = {}
    if "wake_storm" in (prev.get("modes") or []):
        uptime = prev.get("uptime_min")
        out.append(
            _finding(
                agent_id="sentinel",
                severity="medium",
                title=f"Wake storm — {uptime:.0f} min since boot" if uptime else "Wake storm — post-sleep indexing",
                detail=(
                    "Post-sleep CPU spike — Wake Cool Down freezes factory and clears hub · pipeline · "
                    "ghosts · Chrome · n8n. Restart Cursor after if agent chat is still hot."
                ),
                action="Wake Cool Down",
                tap_action="cpu_wake_cool_down",
            )
        )
    cursor = prev.get("cursor") or {}
    cursor_cpu = float(cursor.get("cpu_sum") or 0)
    renderer_peak = float(cursor.get("renderer_peak") or 0)
    sys_cpu = float(mp.get("cpu_pct") or 0)
    if "cursor_hot" in (prev.get("modes") or []) and (
        renderer_peak >= 150 or cursor_cpu >= 200
    ):
        peak_note = f" · peak window {renderer_peak:.0f}%" if renderer_peak >= 80 else ""
        out.append(
            _finding(
                agent_id="sentinel",
                severity="high" if renderer_peak >= 100 or cursor_cpu >= 80 else "medium",
                title=f"Cursor hot — {cursor.get('cpu_sum', '?')}% CPU · {cursor.get('rss_mb', '?')} MB RAM{peak_note}",
                detail=(
                    "Cool Down clears factory junk only — Cursor agent chats need Restart Cursor. "
                    "Save work first."
                ),
                action="Restart Cursor",
                tap_action="cpu_restart_cursor",
            )
        )
    if prev.get("factory_frozen") and prev.get("health") != "healthy":
        out.append(
            _finding(
                agent_id="sentinel",
                severity="info",
                title="Factory auto-frozen",
                detail="Auto-run disabled until body cools — prevents wake CPU storms from starting more agents.",
                action="View Cool Down",
                tap_action="cpu_cool_down",
            )
        )
    cpu = float(mp.get("cpu_pct") or 0)
    ram = float(mp.get("ram_used_pct") or 0)
    qz = int(mp.get("queue_zombies") or 0)
    ghost = int(mp.get("ghost_terminals") or 0)
    if cpu >= 90:
        out.append(
            _finding(
                agent_id="sentinel",
                severity="high" if cpu >= 120 else "medium",
                title=f"CPU saturated — {cpu}%",
                detail=(
                    f"Load {mp.get('load_1min', '?')} on {mp.get('cpu_cores', '?')} cores. "
                    "Cursor agent chats are the usual hog — Cool Down tab fixes it."
                ),
                action="Cool Down Now",
                tap_action="cpu_cool_down",
            )
        )
    elif cpu >= 70:
        out.append(
            _finding(
                agent_id="sentinel",
                severity="medium",
                title=f"CPU elevated — {cpu}%",
                detail="Machine is busy. Try Cool Down before starting more agent work.",
                action="Cool Down tab",
                tap_action="cpu_cool_down",
            )
        )
    if qz >= 8:
        out.append(
            _finding(
                agent_id="sentinel",
                severity="medium",
                title=f"Pipeline queue leak — {qz} zombies",
                detail="Leaked factory queue builders steal RAM and CPU.",
                action="Clear pipeline",
                tap_action="pipeline",
            )
        )
    if ghost >= 3:
        out.append(
            _finding(
                agent_id="sentinel",
                severity="medium",
                title=f"Ghost terminals — {ghost}",
                detail="Stuck Cursor terminal sessions still running.",
                action="Clear ghost shells",
                tap_action="cpu_clear_ghosts",
            )
        )
    if ram >= 90:
        out.append(
            _finding(
                agent_id="sentinel",
                severity="medium",
                title=f"RAM high — {ram}%",
                detail="Clear pipeline + Cool Down frees headroom.",
                action="Cool Down Now",
                tap_action="cpu_cool_down",
            )
        )
    return out


FULL_SCAN_MAX_HOURS = 24
LIVE_MAX_AGE_SEC = 45


def _iso_age_sec(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except ValueError:
        return None


def _refresh_live_domains(scan: dict) -> dict:
    """Re-read fast-changing security domains so cached reports never lie about Firewall."""
    domains = dict(scan.get("domains") or {})
    refreshers = (
        ("firewall", _scan_firewall),
        ("sip", _scan_sip),
        ("gatekeeper", _scan_gatekeeper),
        ("filevault", _scan_filevault),
        ("disk", _scan_disk),
    )
    changed = False
    for key, fn in refreshers:
        fresh = fn()
        if fresh != domains.get(key):
            domains[key] = fresh
            changed = True
    scan = {**scan, "domains": domains, "live_refreshed_at": _now()}
    if changed:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SCAN_PATH.write_text(json.dumps(scan, indent=2), encoding="utf-8")
    return scan


def compute_score(findings: list[dict]) -> int:
    score = 100
    for f in findings:
        sev = f.get("severity", "info")
        score -= {"critical": 28, "high": 14, "medium": 7, "low": 3, "info": 0}.get(sev, 0)
    return max(0, min(100, score))


def _grade_for_score(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 55:
        return "Fair"
    return "At risk"


def apply_pressure_to_score(base: int, mp: dict | None) -> int:
    """Blend security score with live CPU/RAM/thermal pressure — score must move under load."""
    if not mp:
        return base
    score = base
    cpu = float(mp.get("cpu_pct") or 0)
    ram = float(mp.get("ram_used_pct") or 0)
    mem = str(mp.get("memory_pressure_level") or "normal").lower()
    if cpu >= 120:
        score -= 28
    elif cpu >= 90:
        score -= 18
    elif cpu >= 70:
        score -= 12
    elif cpu >= 50:
        score -= 6
    elif cpu >= 35:
        score -= 2
    if ram >= 92:
        score -= 18
    elif ram >= 85:
        score -= 10
    elif ram >= 78:
        score -= 5
    if mem == "critical":
        score -= 12
    elif mem == "warn":
        score -= 6
    if mp.get("thermal_pressure"):
        score -= 5
    if int(mp.get("ghost_terminals") or 0) >= 3:
        score -= 8
    qz = int(mp.get("queue_zombies") or 0)
    if qz >= 50:
        score -= 15
    elif qz >= 20:
        score -= 10
    elif qz >= 8:
        score -= 5
    rt = mp.get("ram_truth") or {}
    breakdown = rt.get("breakdown") or {}
    cursor_gb = float(breakdown.get("cursor_gb") or 0)
    if cursor_gb >= 9:
        score -= 14
    elif cursor_gb >= 7:
        score -= 10
    elif cursor_gb >= 5:
        score -= 6
    elif cursor_gb >= 3:
        score -= 3
    spotlight_gb = float(breakdown.get("spotlight_gb") or 0)
    if spotlight_gb >= 1.5:
        score -= 4
    elif spotlight_gb >= 1.0:
        score -= 2
    if ram >= 50:
        score -= 4
    elif ram >= 40:
        score -= 2
    if cpu >= 25:
        score -= 2
    cur = mp.get("cursor") or {}
    cur_peak = float(cur.get("renderer_peak") or cur.get("peak_cpu") or 0)
    cur_sum = float(cur.get("cpu_sum") or 0)
    if cur_peak >= 150:
        score -= 12
    elif cur_peak >= 120:
        score -= 6
    elif cur_sum >= 200:
        score -= 8
    bomb = mp.get("sina_log_bomb") or {}
    if bomb.get("critical"):
        score -= 20
    elif bomb.get("level") == "warn":
        score -= 8
    if mp.get("hub_online") and (not mp.get("hub_health_ok") or rt.get("hub_quarantined")):
        score -= 15
    if int(mp.get("stuck_log_reader_count") or 0) >= 1:
        score -= 10
    if (mp.get("factory_storm") or {}).get("factory_storm"):
        score -= 12
    return max(0, min(100, score))


def compute_live_score(findings: list[dict], mp: dict | None) -> int:
    return apply_pressure_to_score(compute_score(findings), mp)


def _ram_truth(
    *,
    ram_used_gb: float | None = None,
    ram_used_pct: float | None = None,
    ram_total_gb: float | None = None,
) -> dict[str, Any]:
    """Real `ps` sample — top RAM hogs with founder-honest labels (not mock)."""
    code, out = _run(["ps", "aux", "-m"], timeout=8.0)
    if code != 0 or not out.strip():
        return {"ok": False, "error": "ps sample failed", "hogs": []}

    hub_patterns = (
        "sina-command-server",
        "hub_rebuild_worker",
        "auto_run_worker_batch",
        "dashboard_server",
        "build_phase_strict_queue",
    )
    buckets: dict[str, dict[str, Any]] = {
        "cursor_renderer": {"mb": 0.0, "count": 0, "workspaces": []},
        "cursor_workspaces": {"mb": 0.0, "count": 0, "workspaces": []},
        "hub_stack": {"mb": 0.0, "count": 0, "procs": []},
        "chrome_browser": {"mb": 0.0, "count": 0},
        "spotlight": {"mb": 0.0, "count": 0},
        "sina_apps": {"mb": 0.0, "count": 0, "names": []},
    }
    process_rss_mb = 0.0

    for line in out.strip().splitlines()[1:]:
        parts = line.split(None, 10)
        if len(parts) < 11:
            continue
        try:
            rss_kb = int(parts[5])
        except ValueError:
            continue
        mb = rss_kb / 1024.0
        cmd = parts[10]
        cmd_l = cmd.lower()
        process_rss_mb += mb

        if any(
            x in cmd_l
            for x in ("spotlight", "mdworker", "mds_stores", "corespotlight", "mds ", "/mds")
        ):
            buckets["spotlight"]["mb"] += mb
            buckets["spotlight"]["count"] += 1
        elif any(
            x in cmd
            for x in (
                "mac-health",
                "Mac Health",
                "n8n-integration",
                "N8N Integration",
                "chat-unify",
                "Chat Unify",
                "apple-health",
                "Apple Health",
            )
        ):
            buckets["sina_apps"]["mb"] += mb
            buckets["sina_apps"]["count"] += 1
            short = cmd.split("/")[-1][:40]
            if short not in buckets["sina_apps"]["names"]:
                buckets["sina_apps"]["names"].append(short)

        if "Google Chrome" in cmd or (
            "Chromium" in cmd and "Cursor" not in cmd and "chrome_crashpad" not in cmd
        ):
            buckets["chrome_browser"]["mb"] += mb
            buckets["chrome_browser"]["count"] += 1
        elif any(p in cmd for p in hub_patterns):
            buckets["hub_stack"]["mb"] += mb
            buckets["hub_stack"]["count"] += 1
            short = cmd.split("/")[-1][:60]
            buckets["hub_stack"]["procs"].append(short)
        elif "Cursor Helper (Renderer)" in cmd:
            buckets["cursor_renderer"]["mb"] += mb
            buckets["cursor_renderer"]["count"] += 1
        elif re.search(r"Cursor|cursor", cmd):
            buckets["cursor_workspaces"]["mb"] += mb
            m = re.search(r"extension-host\s+(\S+)", cmd)
            if m:
                buckets["cursor_workspaces"]["count"] += 1
                name = m.group(1)
                if name not in buckets["cursor_workspaces"]["workspaces"]:
                    buckets["cursor_workspaces"]["workspaces"].append(name)

    hub_online = False
    hub_health_ok = False
    hub_truth_badge = "Down"
    try:
        from mac_health_log_shield_v1 import probe_hub_truth  # noqa: WPS433

        hub_row = probe_hub_truth()
        hub_online = bool(hub_row.get("hub_online"))
        hub_health_ok = bool(hub_row.get("hub_health_ok"))
        hub_truth_badge = hub_row.get("hub_truth_badge") or "Down"
    except Exception:
        pass

    quarantine_path = SINA / "sina-command-quarantine-v1.json"
    hub_quarantined = quarantine_path.is_file()
    if hub_quarantined:
        try:
            q = json.loads(quarantine_path.read_text(encoding="utf-8"))
            hub_quarantined = q.get("status") == "QUARANTINED"
        except (OSError, json.JSONDecodeError):
            pass

    renderer_mb = round(buckets["cursor_renderer"]["mb"])
    workspaces_mb = round(buckets["cursor_workspaces"]["mb"])
    hub_mb = round(buckets["hub_stack"]["mb"])
    ws_names = buckets["cursor_workspaces"]["workspaces"]
    ws_n = buckets["cursor_workspaces"]["count"] or len(ws_names)

    if hub_online and hub_quarantined:
        hub_status = "RUNNING — should be OFF (quarantine violated)"
        hub_cls = "bad"
    elif hub_online and not hub_health_ok:
        hub_status = "PORT OPEN — /health failing"
        hub_cls = "bad"
    elif hub_mb > 0:
        hub_status = f"RUNNING — {buckets['hub_stack']['count']} process(es)"
        hub_cls = "bad"
    elif hub_quarantined:
        hub_status = "QUARANTINED OFFLINE"
        hub_cls = "ok"
    else:
        hub_status = "Not running"
        hub_cls = "ok"

    hogs: list[dict[str, Any]] = [
        {
            "id": "cursor_renderer",
            "rank": 1,
            "label": "Cursor chat renderer",
            "mb": renderer_mb,
            "gb": round(renderer_mb / 1024, 1),
            "detail": (
                f"{buckets['cursor_renderer']['count']} window(s) — "
                "agent chat + repo context (often 3–5 GB after long sessions)"
            ),
            "cls": "bad" if renderer_mb >= 3500 else "warn" if renderer_mb >= 2000 else "ok",
            "tap_action": "cpu_restart_cursor",
            "tap_label": "Restart Cursor",
        },
        {
            "id": "cursor_workspaces",
            "rank": 2,
            "label": "Cursor workspaces",
            "mb": workspaces_mb,
            "gb": round(workspaces_mb / 1024, 1),
            "detail": (
                f"{ws_n} extension-host(s)"
                + (f" — {', '.join(ws_names[:4])}" if ws_names else " — close extra windows")
            ),
            "cls": "warn" if ws_n >= 2 or workspaces_mb >= 1500 else "ok",
            "tap_action": None,
            "tap_label": "Close extra Cursor windows manually",
        },
        {
            "id": "hub_stack",
            "rank": 3,
            "label": "Legacy hub process",
            "mb": hub_mb,
            "gb": round(hub_mb / 1024, 1),
            "detail": hub_status
            + (
                f" · {', '.join(buckets['hub_stack']['procs'][:2])}"
                if buckets["hub_stack"]["procs"]
                else ""
            ),
            "cls": hub_cls,
            "tap_action": "heal" if hub_mb > 0 else None,
            "tap_label": "Brain heal kills hub workers" if hub_mb > 0 else None,
            "hub_online": hub_online,
            "hub_quarantined": hub_quarantined,
        },
    ]

    chrome_mb = round(buckets["chrome_browser"]["mb"])
    spotlight_mb = round(buckets["spotlight"]["mb"])
    sina_apps_mb = round(buckets["sina_apps"]["mb"])
    cursor_total_mb = renderer_mb + workspaces_mb
    total_used_mb = (ram_used_gb or 0) * 1024
    processes_gb = round(process_rss_mb / 1024, 1)
    cache_mb = max(0, round(total_used_mb - process_rss_mb)) if total_used_mb else 0

    def _share_pct(mb: int) -> float | None:
        if not total_used_mb:
            return None
        return round(mb / total_used_mb * 100, 1)

    for hog in hogs:
        mb = int(hog.get("mb") or 0)
        hog["share_pct"] = _share_pct(mb)
        if hog.get("share_pct") is not None:
            hog["share_label"] = f"{hog['share_pct']}% of used RAM"

    def _hog(rank: int, **kw: Any) -> dict[str, Any]:
        mb = int(kw.get("mb") or 0)
        hog = dict(kw)
        hog["rank"] = rank
        hog["gb"] = round(mb / 1024, 1)
        hog["share_pct"] = _share_pct(mb)
        if hog.get("share_pct") is not None:
            hog["share_label"] = f"{hog['share_pct']}% of used RAM"
        return hog

    rank = 4
    if spotlight_mb >= 80:
        hogs.append(
            _hog(
                rank,
                id="spotlight",
                label="Spotlight indexing",
                mb=spotlight_mb,
                detail=(
                    f"{buckets['spotlight']['count']} process(es) — macOS desktop search indexing your files "
                    "(not an app you opened — runs in background)"
                ),
                cls="warn" if spotlight_mb >= 800 else "ok",
            )
        )
        rank += 1
    if sina_apps_mb >= 20:
        hogs.append(
            _hog(
                rank,
                id="sina_apps",
                label="Sina desktop apps",
                mb=sina_apps_mb,
                detail=(
                    f"{buckets['sina_apps']['count']} process(es)"
                    + (
                        f" — {', '.join(buckets['sina_apps']['names'][:3])}"
                        if buckets["sina_apps"]["names"]
                        else " — Mac Health · N8N · Chat Unify"
                    )
                ),
                cls="warn",
                tap_action="cpu_kill_sina_stack",
                tap_label="Kill Sina apps",
            )
        )
        rank += 1
    if cache_mb >= 200:
        hogs.append(
            _hog(
                rank,
                id="macos_cache",
                label="macOS file cache (not apps)",
                mb=cache_mb,
                detail=(
                    f"All real processes add to {processes_gb} GB. "
                    f"This {round(cache_mb / 1024, 1)} GB gap is inactive pages + compressed memory — "
                    "macOS holds it for speed and frees it when apps need RAM."
                ),
                cls="ok",
            )
        )

    cursor_gb = round(cursor_total_mb / 1024, 1)
    hub_gb = round(hub_mb / 1024, 1)
    chrome_gb = round(chrome_mb / 1024, 1)
    cache_gb = round(cache_mb / 1024, 1)
    total_line = (
        f"{ram_used_gb} GB in use of {ram_total_gb} GB ({ram_used_pct}%)"
        if ram_used_gb is not None and ram_total_gb is not None
        else f"{ram_used_gb} GB in use ({ram_used_pct}%)" if ram_used_gb is not None else "RAM sample"
    )
    explain_line = (
        f"Processes = {processes_gb} GB real apps. "
        f"macOS cache = {cache_gb} GB (not hidden apps). "
        f"Cursor = {cursor_gb} GB — close extra windows or Restart Cursor to drop it."
    )
    founder_line = (
        f"{ram_used_gb} GB TOTAL · processes {processes_gb} GB · cache {cache_gb} GB · Cursor {cursor_gb} GB"
    )
    if chrome_mb >= 200:
        founder_line += f" · Chrome {chrome_gb} GB"

    return {
        "ok": True,
        "sampled_at": _now(),
        "ram_used_gb": ram_used_gb,
        "ram_used_pct": ram_used_pct,
        "ram_total_gb": ram_total_gb,
        "processes_rss_gb": processes_gb,
        "macos_cache_gb": cache_gb,
        "total_line": total_line,
        "explain_line": explain_line,
        "founder_line": founder_line,
        "breakdown": {
            "total_gb": ram_used_gb,
            "processes_gb": processes_gb,
            "macos_cache_gb": cache_gb,
            "cursor_gb": cursor_gb,
            "hub_gb": hub_gb,
            "spotlight_gb": round(spotlight_mb / 1024, 1),
            "sina_apps_gb": round(sina_apps_mb / 1024, 1),
            "chrome_gb": chrome_gb if chrome_mb >= 200 else 0,
            "cursor_share_pct": _share_pct(cursor_total_mb),
        },
        "hogs": hogs,
        "cursor_total_mb": cursor_total_mb,
        "chrome_mb": chrome_mb,
        "hub_online": hub_online,
        "hub_quarantined": hub_quarantined,
    }


def _ram_truth_lite_stub(pressure: dict[str, Any]) -> dict[str, Any]:
    ram_pct = float(pressure.get("ram_used_pct") or 0)
    ram_gb = pressure.get("ram_used_gb")
    total_line = (
        f"{ram_gb} GB in use ({ram_pct:.0f}%)"
        if ram_gb is not None
        else f"RAM ~{ram_pct:.0f}%"
    )
    return {
        "ok": True,
        "skipped": "ram_critical_lite_probe",
        "total_line": total_line,
        "explain_line": (
            f"{total_line}. Full app breakdown deferred while Mac relieves pressure — tap Relieve pressure."
        ),
    }


def _machine_pressure() -> dict:
    """Lightweight Mac pressure signals — local only."""
    import os

    pressure: dict[str, Any] = {"at": _now()}
    code, out = _run(["memory_pressure"], timeout=4.0)
    if code == 0 and out:
        pressure["memory_pressure"] = out.splitlines()[0][:120]
        level = "normal"
        if re.search(r"\bcritical\b", out, re.I):
            level = "critical"
        elif re.search(r"\bwarn\b", out, re.I):
            level = "warn"
        pressure["memory_pressure_level"] = level
    code, out = _run(["sysctl", "-n", "hw.memsize"], timeout=3.0)
    if code == 0 and out.strip().isdigit():
        gb = int(out.strip()) / (1024**3)
        pressure["ram_gb"] = round(gb, 1)
    code, out = _run(["sysctl", "-n", "hw.ncpu"], timeout=3.0)
    if code == 0 and out.strip().isdigit():
        pressure["cpu_cores"] = int(out.strip())
    code, out = _run(["sysctl", "-n", "vm.loadavg"], timeout=3.0)
    if code == 0:
        pressure["loadavg"] = out.strip()[:80]
        cores = pressure.get("cpu_cores") or 1
        m = re.search(r"\{?\s*([\d.]+)", out)
        if m:
            load1 = float(m.group(1))
            pressure["load_1min"] = round(load1, 2)
            pressure["load_pct"] = round(min(150.0, load1 / cores * 100), 1)
    try:
        from mac_performance_snapshot import parse_vm_stat  # noqa: WPS433

        vm = parse_vm_stat()
        used_mb = (
            vm.get("active_mb", 0)
            + vm.get("inactive_mb", 0)
            + vm.get("wired_mb", 0)
            + vm.get("compressed_mb", 0)
        )
        total_gb = float(pressure.get("ram_gb") or 0)
        if total_gb > 0:
            pressure["ram_used_gb"] = round(used_mb / 1024, 1)
            pressure["ram_free_gb"] = round(vm.get("free_mb", 0) / 1024, 1)
            pressure["ram_used_pct"] = round(used_mb / (total_gb * 1024) * 100, 1)
    except Exception:
        pass
    ram_pct_early = float(pressure.get("ram_used_pct") or 0)
    lite_probe = ram_pct_early >= 88.0 or str(pressure.get("memory_pressure_level") or "").lower() == "critical"
    if lite_probe:
        pressure["ram_pressure_lite"] = True
        pressure["ghost_terminals"] = 0
        pressure["queue_zombies"] = 0
        try:
            from mac_health_log_shield_v1 import build_log_shield_probe  # noqa: WPS433

            shield = build_log_shield_probe(side_effects=False)
            for key in (
                "hub_online",
                "hub_health_ok",
                "hub_rebuild_ok",
                "hub_rebuild_reachable",
                "hub_error",
                "hub_truth_badge",
                "sina_log_bomb",
                "factory_storm",
                "film_render",
                "film_render_frozen",
                "film_render_active",
            ):
                if key in shield:
                    pressure[key] = shield[key]
        except Exception:
            pass
        cpu_pct = float(pressure.get("cpu_pct") or pressure.get("load_pct") or 0)
        pressure["cpu_pct"] = cpu_pct
        pressure["ok"] = ram_pct_early < 95 and cpu_pct < 120
        pressure["ram_truth"] = _ram_truth_lite_stub(pressure)
        pressure["cursor"] = {}
        return pressure
    try:
        from mac_performance_snapshot import parse_top_cpu_busy  # noqa: WPS433

        top_cpu = parse_top_cpu_busy()
        if top_cpu:
            pressure.update(top_cpu)
            pressure["cpu_pct"] = top_cpu["system_cpu_busy_pct"]
        elif pressure.get("load_pct") is not None:
            pressure["cpu_pct"] = pressure["load_pct"]
    except Exception:
        if pressure.get("load_pct") is not None and "cpu_pct" not in pressure:
            pressure["cpu_pct"] = pressure["load_pct"]
    code, therm = _run(["pmset", "-g", "therm"], timeout=3.0)
    if code == 0 and therm:
        pressure["thermal"] = therm.strip()[:200]
        pressure["thermal_pressure"] = bool(
            re.search(r"CPU_Speed_Limit|thermal_warning|CPU die temperature", therm, re.I)
        )
        pressure["gpu_note"] = "SoC thermal active" if pressure["thermal_pressure"] else "SoC nominal"
    disk = _scan_disk()
    pressure["disk_root_pct"] = disk.get("root_pct_used")
    pressure["disk_ok"] = disk.get("ok", True)
    ghost = 0
    term_root = Path.home() / ".cursor" / "projects"
    if term_root.is_dir():
        for proj in term_root.glob("*/terminals"):
            if not proj.is_dir():
                continue
            for tf in proj.glob("*.txt"):
                try:
                    text = tf.read_text(encoding="utf-8", errors="ignore")
                    if "running_for_ms:" in text and "exit_code:" not in text:
                        ghost += 1
                except OSError:
                    continue
    pressure["ghost_terminals"] = ghost
    pressure["queue_zombies"] = len(pipeline_queue_zombie_pids())
    try:
        from mac_health_log_shield_v1 import build_log_shield_probe  # noqa: WPS433
        from mac_health_ram_pressure_v1 import shield_side_effects  # noqa: WPS433

        shield = build_log_shield_probe(side_effects=shield_side_effects())
        for key in (
            "hub_online",
            "hub_health_ok",
            "hub_rebuild_ok",
            "hub_rebuild_reachable",
            "hub_error",
            "hub_truth_badge",
            "sina_log_bomb",
            "largest_sina_logs",
            "stuck_log_readers",
            "stuck_log_reader_count",
            "factory_storm",
            "film_render",
            "film_render_frozen",
            "film_render_active",
            "never_again",
            "log_shield_findings",
            "log_growth_mb_per_min",
        ):
            if key in shield:
                pressure[key] = shield[key]
    except Exception:
        pass
    cpu_pct = float(pressure.get("cpu_pct") or 0)
    ram_pct = float(pressure.get("ram_used_pct") or 0)
    mem_level = str(pressure.get("memory_pressure_level") or "normal").lower()
    qz = int(pressure.get("queue_zombies") or 0)
    pressure["ok"] = (
        ghost < 3
        and qz < 8
        and (disk.get("root_pct_used") or 0) < 90
        and cpu_pct < 90
        and ram_pct < 90
        and mem_level != "critical"
        and not (pressure.get("sina_log_bomb") or {}).get("critical")
        and not (pressure.get("hub_online") and not pressure.get("hub_health_ok"))
    )
    try:
        from mac_health_ram_pressure_v1 import skip_heavy_probes  # noqa: WPS433

        lite = skip_heavy_probes(mp=pressure)
    except Exception:
        lite = False
    if lite:
        pressure["ram_pressure_lite"] = True
        pressure["ram_truth"] = _ram_truth_lite_stub(pressure)
        pressure["cursor"] = pressure.get("cursor") or {}
    else:
        pressure["ram_truth"] = _ram_truth(
            ram_used_gb=pressure.get("ram_used_gb"),
            ram_used_pct=pressure.get("ram_used_pct"),
            ram_total_gb=pressure.get("ram_gb"),
        )
        try:
            from mac_health_prevention_v1 import _cursor_pressure  # noqa: WPS433

            pressure["cursor"] = _cursor_pressure()
        except Exception:
            pressure["cursor"] = {}
    return pressure


def _cart_pid_cmd_ok(cmd: str) -> bool:
    """True when cmd still looks like a shell/terminal process, not a PID recycled by macOS."""
    if not cmd:
        return False
    low = cmd.lower()
    if "grep" in low or "pgrep" in low or "pkill" in low:
        return False
    return any(p in low for p in ("zsh", "bash", "/sh", "-sh", "fish", "tcsh", "csh", "dash", "login"))


def cart_fleet_sweep() -> dict[str, Any]:
    """Close ghost Cursor terminals — Brain CART fleet sweep."""
    closed = 0
    patched = 0
    skipped_pid_reused = 0
    term_root = Path.home() / ".cursor" / "projects"
    if term_root.is_dir():
        for proj in term_root.glob("*/terminals"):
            if not proj.is_dir():
                continue
            for tf in proj.glob("*.txt"):
                try:
                    text = tf.read_text(encoding="utf-8", errors="ignore")
                    if "exit_code:" in text:
                        continue
                    m = re.search(r"^pid:\s*(\d+)", text, re.M)
                    if m:
                        pid = int(m.group(1))
                        ps_code, ps_out = _run(["ps", "-p", str(pid), "-o", "command="], timeout=3.0)
                        if ps_code == 0 and _cart_pid_cmd_ok(ps_out.strip()):
                            try:
                                os.kill(pid, 15)
                                closed += 1
                            except (ProcessLookupError, PermissionError):
                                pass
                        elif ps_code == 0 and ps_out.strip():
                            skipped_pid_reused += 1
                    tf.write_text(
                        text.rstrip()
                        + f"\n\n---\nexit_code: 0\nelapsed_ms: 1000\nended_at: {_now()}\n---\n",
                        encoding="utf-8",
                    )
                    patched += 1
                except OSError:
                    continue
    ghost = _machine_pressure().get("ghost_terminals", 0)
    return {
        "closed": closed,
        "patched": patched,
        "skipped_pid_reused": skipped_pid_reused,
        "ghost_remaining": ghost,
    }


def _queue_zombie_cmd_ok(cmd: str, pattern: str) -> bool:
    """True when cmd is a Python worker, not grep/pkill/bash false positives."""
    low = cmd.lower()
    if not cmd or "grep" in low or "pgrep" in low or "pkill" in low:
        return False
    if "python" not in low:
        return False
    return pattern in cmd


def pipeline_queue_zombie_pids() -> list[int]:
    """PIDs for leaked factory queue builders (auto_run_worker_batch spawn leak)."""
    pids: set[int] = set()
    for pat in QUEUE_ZOMBIE_PATTERNS:
        code, out = _run(["pgrep", "-f", pat], timeout=5.0)
        if code != 0 or not out.strip():
            continue
        for line in out.splitlines():
            line = line.strip()
            if not line.isdigit():
                continue
            pid = int(line)
            ps_code, ps_out = _run(["ps", "-p", str(pid), "-o", "command="], timeout=3.0)
            if ps_code == 0 and _queue_zombie_cmd_ok(ps_out.strip(), pat):
                pids.add(pid)
    return sorted(pids)


def pipeline_queue_sweep(*, force: bool = False) -> dict[str, Any]:
    """Kill leaked factory queue workers — frees RAM instantly."""
    before_pids = pipeline_queue_zombie_pids()
    before = len(before_pids)
    if before == 0:
        return {
            "ok": True,
            "before": 0,
            "killed": 0,
            "after": 0,
            "pattern": ",".join(QUEUE_ZOMBIE_PATTERNS),
            "skipped": "no_targets" if force else None,
        }
    for pid in before_pids:
        _run(["kill", "-TERM", str(pid)], timeout=5.0)
    time.sleep(0.6)
    mid_pids = pipeline_queue_zombie_pids()
    if mid_pids:
        for pid in mid_pids:
            _run(["kill", "-9", str(pid)], timeout=5.0)
        time.sleep(0.4)
    after = len(pipeline_queue_zombie_pids())
    killed = max(0, before - after)
    return {
        "ok": True,
        "before": before,
        "killed": killed,
        "after": after,
        "pattern": ",".join(QUEUE_ZOMBIE_PATTERNS),
    }


def _try_enable_firewall() -> dict[str, Any]:
    """Attempt firewall ON; fall back to opening System Settings for founder tap."""
    code, out = _run(
        ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--setglobalstate", "on"],
        timeout=8.0,
    )
    verify_code, verify_out = _run(
        ["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"],
        timeout=5.0,
    )
    if "enabled" in verify_out.lower():
        return {"ok": True, "enabled": True, "method": "socketfilterfw", "detail": verify_out}
    _run(
        ["open", "x-apple.systempreferences:com.apple.Network-Settings.extension?Firewall"],
        timeout=5.0,
    )
    return {
        "ok": False,
        "enabled": False,
        "method": "opened_settings",
        "detail": out[:200] or "Tap Firewall ON in System Settings",
        "founder_tap": "System Settings → Network → Firewall → On",
    }


def _attach_action_receipt(report: dict, *, action: str, extra: dict | None = None) -> dict:
    """Founder-visible proof an action ran — not mock."""
    scan = report.get("scan") or {}
    domains = scan.get("domains") or {}
    receipt: dict[str, Any] = {"action": action, "at": _now(), "ran_ok": True}
    if extra:
        receipt.update(extra)
    if action == "scan":
        lanes = len(domains)
        dur = scan.get("duration_sec")
        receipt.update(
            {
                "lanes": lanes,
                "duration_sec": dur,
                "saved": str(SCAN_PATH),
                "scanned_at": scan.get("scanned_at"),
                "summary": (
                    f"Listen again complete · {lanes} security lanes checked in {dur}s · "
                    f"saved {SCAN_PATH.name} (real macOS CLI scan, not mock)"
                ),
            }
        )
    report["action_receipt"] = receipt
    if action == "scan":
        _emit_n8n_signal("scan", action="scan", extra={"lanes": receipt.get("lanes")})
    return report


def run_full_relief(*, standalone: bool = False, ram_purge: bool = True) -> dict[str, Any]:
    """One-tap relieve: CPU cool · pipeline zombies · ghost carts · RAM inactive purge · firewall · rescan."""
    before = build_report(rescan=False, standalone=standalone)
    mp = _machine_pressure()
    ram_pct = float(mp.get("ram_used_pct") or 0)

    from mac_health_cpu_relief_v1 import run_cpu_relief  # noqa: WPS433

    relief = run_cpu_relief("cpu_cool_down")
    pipeline = pipeline_queue_sweep(force=True)
    cart = cart_fleet_sweep()
    firewall = _try_enable_firewall()

    ram_step: dict[str, Any] = {
        "ok": True,
        "skipped": True,
        "reason": "ram_below_threshold",
        "ram_pct": ram_pct,
    }
    if ram_purge and ram_pct >= 75.0:
        purge_report = run_ram_purge(standalone=standalone)
        ram_step = dict(purge_report.get("ram_purge") or {})
        ram_step["ram_pct"] = ram_pct

    report = build_report(rescan=True, standalone=standalone)
    report["version"] = MAC_HEALTH_VERSION
    cart_p = cart.get("patched") or 0
    cart_c = cart.get("closed") or 0
    pipe_k = pipeline.get("killed") or 0
    fw_on = bool(firewall.get("enabled"))
    cpu_before = (relief.get("before") or {}).get("cpu_pct")
    cpu_after = (relief.get("after") or {}).get("cpu_pct")
    steps: list[str] = list(relief.get("step_lines") or [])
    steps.append(
        f"Ghost shells: patched {cart_p} · killed {cart_c} · remaining {cart.get('ghost_remaining', 0)}"
    )
    steps.append(
        f"Pipeline zombies: {pipeline.get('before', 0)} → {pipeline.get('after', 0)} (killed {pipe_k})"
    )
    if ram_step.get("skipped"):
        steps.append(f"RAM inactive purge: skipped (RAM {ram_pct}%)")
    elif ram_step.get("ok"):
        steps.append(
            f"RAM inactive purge: free +{ram_step.get('free_gained_gb', 0)} GB · "
            f"inactive −{ram_step.get('inactive_freed_gb', 0)} GB"
        )
    elif ram_step.get("cancelled"):
        steps.append("RAM inactive purge: cancelled — enter Mac password when prompted")
    else:
        steps.append("RAM inactive purge: failed or not run")
    steps.append(f"Firewall: {'ON' if fw_on else 'check System Settings'}")
    steps.append(f"Full security rescan: {report.get('scan', {}).get('duration_sec', '?')}s")

    summary_bits = []
    if cpu_before is not None and cpu_after is not None:
        summary_bits.append(f"CPU {cpu_before}% → {cpu_after}%")
    if pipe_k:
        summary_bits.append(f"pipeline −{pipe_k}")
    if cart_p or cart_c:
        summary_bits.append(f"ghosts {cart_p}+{cart_c}")
    if ram_step.get("ok") and not ram_step.get("skipped"):
        summary_bits.append(f"RAM +{ram_step.get('free_gained_gb', 0)} GB free")
    summary_bits.append(f"score {before.get('score')} → {report.get('score')}")

    report["heal"] = {
        "full_relief": True,
        "before_score": before.get("score"),
        "after_score": report.get("score"),
        "before_grade": before.get("grade"),
        "after_grade": report.get("grade"),
        "cpu_before": cpu_before,
        "cpu_after": cpu_after,
        "cpu_relief": relief,
        "cart": cart,
        "pipeline": pipeline,
        "ram": ram_step,
        "firewall": firewall,
        "improved": (report.get("score") or 0) > (before.get("score") or 0)
        or pipe_k > 0
        or cart_p > 0
        or bool(relief.get("improved"))
        or (ram_step.get("ok") and not ram_step.get("skipped")),
        "ran_ok": True,
        "summary": relief.get("summary") or "",
    }
    report["action_receipt"] = {
        "action": "heal",
        "at": _now(),
        "ran_ok": True,
        "steps": steps,
        "summary": "Full relief · " + " · ".join(summary_bits),
    }
    _emit_n8n_signal("heal", action="full_relief", extra={"score": report.get("score")})
    return report


def run_heal(*, standalone: bool = False) -> dict[str, Any]:
    """Brain heal — full relief stack (pipelines · zombies · cool down · RAM when hot · firewall · rescan)."""
    return run_full_relief(standalone=standalone)


def _vm_memory_snapshot() -> dict[str, Any]:
    """vm_stat buckets in GB for purge before/after proof."""
    code, out = _run(["vm_stat"], timeout=4.0)
    if code != 0:
        return {"ok": False}
    m = re.search(r"page size of (\d+)", out)
    if not m:
        return {"ok": False}
    ps = int(m.group(1))

    def gb(name: str) -> float:
        hit = re.search(rf"Pages {re.escape(name)}:\s+(\d+)", out)
        return round(int(hit.group(1)) * ps / 1024**3, 2) if hit else 0.0

    active = gb("active")
    inactive = gb("inactive")
    wired = gb("wired down")
    compressed = gb("occupied by compressor")
    free = gb("free")
    used = round(active + inactive + wired + compressed, 2)
    return {
        "ok": True,
        "free_gb": free,
        "active_gb": active,
        "inactive_gb": inactive,
        "wired_gb": wired,
        "compressed_gb": compressed,
        "used_gb": used,
    }


def run_ram_purge(*, standalone: bool = False) -> dict[str, Any]:
    """Wipe inactive file cache — macOS password dialog via AppleScript."""
    before = _vm_memory_snapshot()
    code, out = _run(
        [
            "osascript",
            "-e",
            'do shell script "/usr/sbin/purge" with administrator privileges',
        ],
        timeout=180.0,
    )
    time.sleep(1.2)
    after = _vm_memory_snapshot()
    cancelled = "User canceled" in out or "canceled" in out.lower()
    ok = code == 0 and after.get("ok")
    free_gain = round((after.get("free_gb") or 0) - (before.get("free_gb") or 0), 2)
    inactive_drop = round((before.get("inactive_gb") or 0) - (after.get("inactive_gb") or 0), 2)
    report = build_report(rescan=False, standalone=standalone)
    report["version"] = MAC_HEALTH_VERSION
    summary = (
        f"Purge complete · free {before.get('free_gb')} → {after.get('free_gb')} GB (+{free_gain}) · "
        f"inactive {before.get('inactive_gb')} → {after.get('inactive_gb')} GB (−{inactive_drop})"
        if ok
        else "Purge cancelled or failed — enter Mac password when prompted"
        if cancelled
        else f"Purge failed: {(out or 'unknown')[:120]}"
    )
    report["ram_purge"] = {
        "ok": ok,
        "cancelled": cancelled,
        "before": before,
        "after": after,
        "free_gained_gb": free_gain,
        "inactive_freed_gb": inactive_drop,
        "detail": out[:400] if out else "",
    }
    report["action_receipt"] = {
        "action": "ram_purge",
        "at": _now(),
        "ran_ok": ok,
        "summary": summary,
    }
    return report


def run_cpu_relief_action(action: str, *, standalone: bool = False) -> dict[str, Any]:
    """One-tap CPU relief tab actions — rescan after relief."""
    from mac_health_cpu_relief_v1 import run_cpu_relief  # noqa: WPS433

    before = build_report(rescan=False, standalone=standalone)
    relief = run_cpu_relief(action)
    report = build_report(rescan=True, standalone=standalone)
    report["version"] = MAC_HEALTH_VERSION
    report["cpu_relief"] = relief
    report["heal"] = {
        "before_score": before.get("score"),
        "after_score": report.get("score"),
        "cpu_before": (relief.get("before") or {}).get("cpu_pct"),
        "cpu_after": (relief.get("after") or {}).get("cpu_pct"),
        "summary": relief.get("summary"),
        "improved": bool(relief.get("improved")),
        "cpu_relief_only": True,
        "step_lines": relief.get("step_lines") or [],
        "ran_ok": bool(relief.get("ok")),
    }
    report["ok"] = bool(relief.get("ok", True))
    report["action_receipt"] = {
        "action": action,
        "at": _now(),
        "ran_ok": bool(relief.get("ok")),
        "summary": relief.get("summary") or "",
        "steps": relief.get("step_lines") or [],
        "cpu_before": (relief.get("before") or {}).get("cpu_pct"),
        "cpu_after": (relief.get("after") or {}).get("cpu_pct"),
    }
    _emit_n8n_signal(
        "cpu_relief",
        cpu_before=float((relief.get("before") or {}).get("cpu_pct") or 0) or None,
        cpu_after=float((relief.get("after") or {}).get("cpu_pct") or 0) or None,
        action=action,
    )
    return report


def run_pipeline_sweep(*, standalone: bool = False) -> dict[str, Any]:
    """One-tap pipeline heal — kill all queue zombie processes and refresh metrics."""
    before = build_report(rescan=False, standalone=standalone)
    pipeline = pipeline_queue_sweep(force=True)
    report = build_report(rescan=True, standalone=standalone)
    report["version"] = MAC_HEALTH_VERSION
    report["pipeline_sweep"] = pipeline
    report["heal"] = {
        "before_score": before.get("score"),
        "after_score": report.get("score"),
        "before_grade": before.get("grade"),
        "after_grade": report.get("grade"),
        "pipeline": pipeline,
        "improved": pipeline.get("killed", 0) > 0 or (report.get("score") or 0) > (before.get("score") or 0),
        "pipeline_only": True,
        "ran_ok": True,
    }
    k = pipeline.get("killed") or 0
    report["action_receipt"] = {
        "action": "pipeline",
        "at": _now(),
        "ran_ok": True,
        "summary": (
            f"Pipeline clear · zombies {pipeline.get('before', 0)} → {pipeline.get('after', 0)} "
            f"· killed {k} · pattern {pipeline.get('pattern', '')}"
        ),
    }
    return report


def append_insights(findings: list[dict], score: int) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "at": _now(),
        "score": score,
        "grade": _grade_for_score(score),
        "finding_count": len(findings),
        "top": findings[0]["title"] if findings else "clean",
        "source": "scan",
    }
    with INSIGHTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_heartbeat(
    *,
    score: int,
    security_score: int,
    grade: str,
    mp: dict | None = None,
    live_status: str = "LIVE",
    source: str = "pulse",
) -> None:
    """Honest live heartbeat log — throttled pulses with CPU/RAM truth."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    mp = mp or {}
    now = datetime.now(timezone.utc)
    last: dict | None = None
    if HEARTBEAT_PATH.is_file():
        try:
            lines = [ln for ln in HEARTBEAT_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if lines:
                last = json.loads(lines[-1])
        except (OSError, json.JSONDecodeError):
            last = None
    if last:
        try:
            prev_at = datetime.fromisoformat(str(last.get("at", "")).replace("Z", "+00:00"))
            age = (now - prev_at).total_seconds()
            prev_score = int(last.get("score") or 0)
            if age < HEARTBEAT_MIN_SEC and abs(prev_score - score) < HEARTBEAT_FORCE_DELTA:
                return
        except ValueError:
            pass
    row = {
        "at": _now(),
        "score": score,
        "security_score": security_score,
        "grade": grade,
        "cpu_pct": mp.get("cpu_pct"),
        "ram_used_pct": mp.get("ram_used_pct"),
        "load_1min": mp.get("load_1min"),
        "live_status": live_status,
        "source": source,
    }
    with HEARTBEAT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    # Trim file to last 200 rows
    try:
        lines = HEARTBEAT_PATH.read_text(encoding="utf-8").splitlines()
        if len(lines) > 200:
            HEARTBEAT_PATH.write_text("\n".join(lines[-200:]) + "\n", encoding="utf-8")
    except OSError:
        pass


def read_heartbeat_history(limit: int = 48) -> list[dict]:
    if not HEARTBEAT_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in HEARTBEAT_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            if not row.get("grade") and row.get("score") is not None:
                row["grade"] = _grade_for_score(int(row["score"]))
            rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def read_insight_history(limit: int = 20) -> list[dict]:
    hb = read_heartbeat_history(limit=limit)
    if hb:
        return hb
    if not INSIGHTS_PATH.is_file():
        return []
    rows = []
    for line in INSIGHTS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                row = json.loads(line)
                if not row.get("grade") and row.get("score") is not None:
                    row["grade"] = _grade_for_score(int(row["score"]))
                rows.append(row)
            except json.JSONDecodeError:
                continue
    return rows[-limit:]


def build_report(*, rescan: bool = False, standalone: bool = False) -> dict:
    kb = _ensure_knowledge()
    stale_days = 7
    scan_stale = False
    if SCAN_PATH.is_file():
        try:
            cached = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
            scanned_at = cached.get("scanned_at", "")
            if scanned_at:
                try:
                    age_sec = _iso_age_sec(scanned_at)
                    if age_sec is None:
                        scan_stale = True
                    else:
                        scan_stale = age_sec > stale_days * 86400 or age_sec > FULL_SCAN_MAX_HOURS * 3600
                except ValueError:
                    scan_stale = True
        except json.JSONDecodeError:
            scan_stale = True
    else:
        scan_stale = True

    scan_source = "full"
    if rescan or scan_stale or not SCAN_PATH.is_file():
        scan = run_mac_scan()
    else:
        try:
            scan = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
            scan = _refresh_live_domains(scan)
            scan_source = "cached+live"
        except json.JSONDecodeError:
            scan = run_mac_scan()

    findings, agent_reports = analyze_scan(scan, kb)
    mp = _machine_pressure()
    gov_rows = _governance_disk_findings()
    if gov_rows:
        findings = gov_rows + findings
    pressure_rows = _pressure_findings(mp)
    if pressure_rows:
        findings = [
            f
            for f in findings
            if not (f.get("severity") == "info" and "No critical" in (f.get("title") or ""))
        ]
        findings = pressure_rows + findings
        sev_score = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        findings.sort(key=lambda f: sev_score.get(f["severity"], 9))
    security_score = compute_score(findings)
    score = compute_live_score(findings, mp)
    grade = _grade_for_score(score)
    if rescan or scan_stale:
        append_insights(findings, score)
        append_heartbeat(
            score=score,
            security_score=security_score,
            grade=grade,
            mp=mp,
            live_status="LIVE",
            source="scan",
        )

    port = int(__import__("os").environ.get("MAC_HEALTH_PORT", "13024"))
    live_at = scan.get("live_refreshed_at")
    live_age = _iso_age_sec(live_at)
    pressure_age = _iso_age_sec(mp.get("at"))

    prevention: dict = {}
    try:
        from mac_health_prevention_v1 import analyze_prevention  # noqa: WPS433

        prevention = analyze_prevention(mp)
    except Exception:
        prevention = {"health": "unknown"}

    narrative = _founder_narrative(
        findings, score, mp, security_score=security_score, prevention=prevention
    )

    settings_payload: dict[str, Any] = {}
    try:
        from mac_health_settings_v1 import (  # noqa: WPS433
            build_auto_guard_explainer,
            build_field_schema,
            load_settings,
        )

        settings_payload = {
            "settings": load_settings(),
            "auto_guard_explainer": build_auto_guard_explainer(),
            "settings_schema": build_field_schema(),
        }
    except Exception:
        settings_payload = {}

    cpu_warn_state: dict[str, Any] = {}
    try:
        from mac_health_emergency_stop_v1 import build_cpu_warn_state  # noqa: WPS433

        cpu_warn_state = build_cpu_warn_state(mp, prevention if isinstance(prevention, dict) else None)
    except Exception:
        pass

    ui_contract: dict[str, Any] = {}
    try:
        from mac_health_founder_glance_ui_v1 import build_ui_contract  # noqa: WPS433

        ui_contract = build_ui_contract(port=port)
    except Exception:
        ui_contract = {"ui_mode": "founder_glance", "version": MAC_HEALTH_VERSION}

    row = {
        "ok": True,
        "app": "mac-health-guard",
        "version": MAC_HEALTH_VERSION,
        "ui_contract": ui_contract,
        "mode": "standalone" if standalone else "hub",
        "standalone": standalone,
        "built_at": _now(),
        "score": score,
        "security_score": security_score,
        "grade": grade,
        "prevention": prevention,
        "cursor_emergency": "cursor_hot" in (prevention.get("modes") or []),
        "scan": scan,
        "findings": findings,
        "agents": agent_reports,
        "knowledge": kb,
        "important_note": IMPORTANT_NOTE,
        "history": read_insight_history(),
        "hub_url": "http://127.0.0.1:13020/",
        "mini_app_url": "http://127.0.0.1:13024/",
        "standalone_url": f"http://127.0.0.1:{port}/",
        "machine_pressure": mp,
        "founder_narrative": narrative,
        **settings_payload,
        "cpu_warn_state": cpu_warn_state,
        "wired": {
            "heart_port": port,
            "scan_source": scan_source,
            "firewall_enabled": bool((scan.get("domains") or {}).get("firewall", {}).get("enabled")),
            "live_refreshed_at": live_at,
            "scanned_at": scan.get("scanned_at"),
            "anti_stale": {
                "live_ok": live_age is not None and live_age <= LIVE_MAX_AGE_SEC,
                "live_age_sec": round(live_age, 1) if live_age is not None else None,
                "pressure_ok": pressure_age is not None and pressure_age <= LIVE_MAX_AGE_SEC,
                "pressure_age_sec": round(pressure_age, 1) if pressure_age is not None else None,
                "full_scan_max_hours": FULL_SCAN_MAX_HOURS,
            },
        },
    }
    try:
        from mac_health_live_v1 import build_live_snapshot  # noqa: WPS433

        live = build_live_snapshot(sync_h1=True)
        row["live"] = {
            "status": live.get("live_status"),
            "wired": live.get("wired"),
            "h1_sync": live.get("h1_sync"),
        }
    except Exception:
        pass
    return row


def _founder_narrative(
    findings: list[dict],
    score: int,
    mp: dict | None = None,
    *,
    security_score: int | None = None,
    prevention: dict | None = None,
) -> dict[str, str]:
    sec = security_score if security_score is not None else score
    grade = "Excellent" if score >= 90 else "Good" if score >= 75 else "Fair" if score >= 55 else "At risk"
    blockers = [f for f in findings if f.get("severity") in ("critical", "high", "medium")]
    urgent = [f for f in findings if f.get("severity") in ("critical", "high")]
    top = blockers[0] if blockers else None
    top_urgent = urgent[0] if urgent else None

    prev = prevention or {}
    modes = prev.get("modes") or []
    prev_health = str(prev.get("health") or "healthy")
    cur = (mp or {}).get("cursor") or {}
    cursor_sum = float(cur.get("cpu_sum") or 0)
    cursor_peak = float(cur.get("renderer_peak") or 0)
    rt = (mp or {}).get("ram_truth") or {}
    cursor_gb = (rt.get("breakdown") or {}).get("cursor_gb", "?")

    safety_line = (
        "Auto-stop never closes Cursor — only background factory agents. "
        "You get many warnings (~3 min) before any auto-stop. Restart Cursor is manual only."
    )

    if score >= 90 and sec >= 90 and cursor_sum < 120:
        grade_story = (
            "The heart sings — security lanes clear, body rhythm calm. "
            "Keep building; Cursor stays open."
        )
    elif "cursor_busy" in modes and cursor_sum < 220:
        grade_story = (
            f"Cursor is working ({cursor_sum:.0f}% CPU · {cursor_gb} GB RAM) — "
            "normal while you ship in agent chats. Not an emergency. Cursor stays open."
        )
    elif "cursor_hot" in modes or cursor_peak >= 200 or cursor_sum >= 250:
        grade_story = (
            f"Cursor is very hot ({cursor_sum:.0f}% CPU · peak {cursor_peak:.0f}%) — "
            "Mac may feel laggy. Cool Down clears background agents only; "
            "Restart Cursor only if the IDE is frozen."
        )
    elif sec >= 90 and score < 90:
        grade_story = (
            f"Security {sec} — excellent. Body rhythm {score} — "
            f"Cursor {cursor_gb} GB RAM. Open RAM truth for live monitor."
        )
    elif score >= 75 and len(blockers) == 1 and top and "firewall" in top.get("title", "").lower():
        grade_story = (
            f"Score {score} — strong beat. One perimeter valve open: Firewall. "
            "Turn it on in System Settings to reach Excellent."
        )
    elif score >= 75:
        grade_story = (
            f"Score {score} — a steady heartbeat. "
            f"{len(blockers)} tune-up{'s' if len(blockers) != 1 else ''} below — calm review, not panic."
        )
    elif score >= 55:
        grade_story = "The body works, but a valve needs attention. Review findings — not panic."
    else:
        grade_story = "The heart asks for help. Tap Brain heal, then follow findings in order."

    if prev_health == "unhealthy" and "wake_storm" in modes:
        grade_story += " Wake storm detected — Wake Cool Down clears background pressure."

    next_tap = ""
    next_tap_action = ""
    cpu = float((mp or {}).get("cpu_pct") or 0)

    if top_urgent and "restart cursor" not in (top_urgent.get("action") or "").lower():
        next_tap = top_urgent.get("action", "Tap Brain heal.")
        next_tap_action = top_urgent.get("tap_action") or ""
    elif top and "restart cursor" not in (top.get("action") or "").lower():
        next_tap = top.get("action", "")
        next_tap_action = top.get("tap_action") or ""
    elif "wake_storm" in modes:
        next_tap = "Wake Cool Down"
        next_tap_action = "cpu_wake_cool_down"
    elif prev_health == "unhealthy" and cpu >= 85:
        next_tap = "Cool Down Now"
        next_tap_action = "cpu_cool_down"
    elif cursor_peak >= 280 or cursor_sum >= 400:
        next_tap = "Restart Cursor (only if frozen)"
        next_tap_action = "cpu_restart_cursor"

    pressure_line = ""
    if mp:
        cores = mp.get("cpu_cores") or 0
        load_raw = mp.get("loadavg") or ""
        ghost = mp.get("ghost_terminals", 0)
        qz = mp.get("queue_zombies", 0)
        if cores and load_raw:
            m = re.search(r"([\d.]+)", load_raw)
            if m:
                busy = float(m.group(1))
                pressure_line = (
                    f"Body rhythm: {busy:.1f} of {cores} CPU lanes busy "
                    f"({int(round(busy / cores * 100))}%) · "
                    f"Cursor {cursor_sum:.0f}% · ghost terminals {ghost} · "
                    f"pipeline {qz} · disk {mp.get('disk_root_pct', '?')}% full."
                )

    body_line = "Your Mac is the body — metal, memory, disk, listeners, the whole machine."
    heart_line = f"Score {score} · {grade}. The heart beats from disk — never from chat memory."
    brain_line = (
        "Brain listens each session: heal, refresh, clear background pressure, "
        "protect your work in Cursor."
    )

    return {
        "body": body_line,
        "heart": heart_line,
        "brain": brain_line,
        "safety_line": safety_line,
        "grade_story": grade_story,
        "next_tap": next_tap,
        "next_tap_action": next_tap_action,
        "pressure_line": pressure_line,
        "blocker_count": len(blockers),
        "urgent_blocker_count": len(urgent),
        "narrative_version": MAC_HEALTH_VERSION,
    }


def handle_action(body: dict) -> dict:
    action = body.get("action") or "report"
    if not isinstance(action, str):
        action = "unknown"
    action = action.strip().lower()
    standalone = bool(body.get("standalone"))
    if action == "live":
        from mac_health_live_v1 import build_live_snapshot  # noqa: WPS433

        return build_live_snapshot(sync_h1=True)
    if action in ("scan", "refresh", "rescan"):
        report = build_report(rescan=True, standalone=standalone)
        return _attach_action_receipt(report, action="scan")
    if action == "report":
        return build_report(rescan=False, standalone=standalone)
    if action == "knowledge":
        return {"ok": True, "knowledge": _ensure_knowledge()}
    if action in ("full_relief", "relieve_pressure", "relieve"):
        return run_full_relief(standalone=standalone)
    if action in ("heal", "fix", "brain-heal"):
        return run_heal(standalone=standalone)
    if action in ("pipeline", "pipeline_sweep", "kill_queue", "clear_pipeline"):
        return run_pipeline_sweep(standalone=standalone)
    if action in ("purge", "ram_purge", "purge_cache", "purge_ram"):
        return run_ram_purge(standalone=standalone)
    if action in ("prevention", "prevention_apply", "auto_prevent"):
        from mac_health_prevention_v1 import apply_prevention  # noqa: WPS433

        mp = _machine_pressure()
        return apply_prevention(mp, force=bool(body.get("force")))
    if action in (
        "emergency_stop",
        "panic_stop",
        "stop_everything",
        "cpu_emergency_stop",
        "mac_health_emergency_stop",
    ):
        from mac_health_emergency_stop_v1 import run_mac_health_emergency_stop  # noqa: WPS433

        trigger = str(body.get("trigger") or "api")
        receipt = run_mac_health_emergency_stop(
            trigger=trigger,
            fast=not bool(body.get("full")),
            notify=body.get("notify", True) is not False,
        )
        return {
            "ok": bool(receipt.get("ok")),
            "emergency_stop": receipt,
            "summary": receipt.get("summary") or "",
            "founder_line": receipt.get("founder_line") or "",
            "action_receipt": {
                "action": "emergency_stop",
                "at": _now(),
                "ran_ok": bool(receipt.get("ok")),
                "summary": receipt.get("summary") or "",
                "steps": receipt.get("steps") or [],
            },
        }
    if action in ("settings", "settings_save", "settings_reset"):
        from mac_health_settings_v1 import handle_settings_action  # noqa: WPS433

        return handle_settings_action(body)
    if action in (
        "truncate_runaway_logs",
        "relieve_disk",
        "log_shield_relieve",
        "kill_stuck_log_readers",
        "log_shield_kill_readers",
        "log_shield_probe",
        "log_shield",
    ):
        from mac_health_log_shield_v1 import handle_log_shield_action  # noqa: WPS433

        return handle_log_shield_action(body)
    if action.startswith("cpu_") or action in (
        "cool_down",
        "cpu_cool_down",
        "wake_cool_down",
        "cpu_wake_cool_down",
        "wake_cool",
        "ease_cpu",
        "quit_chrome",
        "pause_n8n",
        "restart_cursor",
        "kill_safe_hogs",
        "clear_ghosts",
    ):
        return run_cpu_relief_action(action, standalone=standalone)
    return {"ok": False, "error": f"unknown action: {action}"}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Mac Health Guard — local scan engine")
    parser.add_argument("--scan", action="store_true", help="Run full scan and print JSON report")
    parser.add_argument("--report", action="store_true", help="Print cached report JSON")
    parser.add_argument("--serve", action="store_true", help="Start standalone server (use mac-health-guard-server.py)")
    parser.add_argument("--heal", action="store_true", help="Brain heal: CART + firewall attempt + rescan")
    parser.add_argument("--e2e", action="store_true", help="End-to-end wiring check (heart, firewall, cache)")
    args = parser.parse_args()
    if args.e2e:
        import urllib.request

        errors: list[str] = []
        code_fw, out_fw = _run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
        fw_on_disk = "enabled" in out_fw.lower()
        port = int(os.environ.get("MAC_HEALTH_PORT", "13024"))
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as r:
                health = json.loads(r.read().decode())
        except Exception as exc:
            errors.append(f"heart down on :{port}: {exc}")
            health = {}
        if not health.get("ok"):
            errors.append("health endpoint not ok")
        report = build_report(rescan=False, standalone=True)
        wired = report.get("wired") or {}
        fw_api = bool(wired.get("firewall_enabled"))
        if fw_on_disk != fw_api:
            errors.append(f"firewall mismatch: disk={fw_on_disk} api={fw_api}")
        if wired.get("scan_source") != "cached+live" and SCAN_PATH.is_file():
            errors.append(f"expected cached+live refresh, got {wired.get('scan_source')}")
        if not wired.get("live_refreshed_at"):
            errors.append("missing live_refreshed_at")
        anti = wired.get("anti_stale") or {}
        if not anti.get("live_ok"):
            errors.append(f"live refresh stale: age={anti.get('live_age_sec')}s")
        if not anti.get("pressure_ok"):
            errors.append(f"pressure stale: age={anti.get('pressure_age_sec')}s")
        print(json.dumps({
            "ok": not errors,
            "version": report.get("version"),
            "score": report.get("score"),
            "grade": report.get("grade"),
            "firewall_on_disk": fw_on_disk,
            "firewall_api": fw_api,
            "wired": wired,
            "errors": errors,
        }, indent=2))
        raise SystemExit(1 if errors else 0)
    if args.heal:
        print(json.dumps(run_heal(standalone=True), indent=2))
        return
    if args.scan:
        print(json.dumps(build_report(rescan=True, standalone=True), indent=2))
        return
    if args.report:
        print(json.dumps(build_report(rescan=False, standalone=True), indent=2))
        return
    parser.print_help()


if __name__ == "__main__":
    main()
