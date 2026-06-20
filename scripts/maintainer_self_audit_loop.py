#!/usr/bin/env python3
"""
Maintainer self-audit loop — disk memory, incident reports, skills, repeat-mistake guard.

Agent: sinaai_maintainer only.
Storage: ~/.sina/agent-workspaces/sinaai_maintainer/private-reference/ (tagged docs)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_A = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

MAINTAINER_ID = "sinaai_maintainer"
PRIV = Path.home() / ".sina" / "agent-workspaces" / MAINTAINER_ID
PRIVATE_REF = PRIV / "private-reference"
AUDITS_DIR = PRIVATE_REF / "audits"
MEMORY = PRIV / "memory"
MISTAKE_REGISTRY_POINTER = MEMORY / "MISTAKE_REGISTRY_LOCKED.md"
AUDIT_LOOP_LOG = MEMORY / "audit-loop.jsonl"
AUDIT_STATE = MEMORY / "audit-loop-state.json"
MANIFEST = PRIVATE_REF / "MANIFEST.json"
TAG_STANDARD = PRIV / "MAINTAINER_DOC_TAG_STANDARD.md"
MAINTAINER_INCIDENT = SOURCE_A / "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md"
CONTEXT_INCIDENT = SOURCE_A / "CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md"
SELF_AUDIT_SCRIPT = SCRIPT_DIR / "cursor_agent_self_audit.py"
HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))
HUB_BASE = f"http://127.0.0.1:{HUB_PORT}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_log(event: dict) -> None:
    MEMORY.mkdir(parents=True, exist_ok=True)
    row = {"ts": _now(), **event}
    with AUDIT_LOOP_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_state() -> dict:
    if not AUDIT_STATE.is_file():
        return {}
    try:
        return json.loads(AUDIT_STATE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(patch: dict) -> None:
    st = _load_state()
    st.update(patch)
    st["updated_at"] = _now()
    MEMORY.mkdir(parents=True, exist_ok=True)
    AUDIT_STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")


def _run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=SOURCE_A, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out.strip()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _tag_header(*, topic: str, seq: int, subpath: str, title: str) -> str:
    ref_tag = f"MAINT-REF-{topic}-{seq:03d}"
    trace_id = f"MAINT-REF-{_today()}-{topic}-{seq:03d}"
    ws = f"~/.sina/agent-workspaces/{MAINTAINER_ID}/private-reference/{subpath}"
    return f"""[MAINTAINER_AGENT_REF · {MAINTAINER_ID} · {ref_tag}]

| Field | Value |
|-------|-------|
| **ref_tag** | `{ref_tag}` |
| **trace_id** | `{trace_id}` |
| **agent_id** | `{MAINTAINER_ID}` |
| **repo_chat** | `SinaaiDataBase` |
| **workspace** | `{ws}` |
| **plane** | `COMMAND` |
| **thread** | `THREAD-FACTORY` |
| **canonical** | `false` |
| **adoption** | `GOVERNANCE_UNIFICATION_ENGINE` only |
| **written** | `{_today()}` |

# {title}

"""


def _latest_mistake_registry() -> Path:
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    dated = sorted(AUDITS_DIR.glob("MISTAKE_REGISTRY_*.md"), reverse=True)
    if dated:
        return dated[0]
    path = AUDITS_DIR / f"MISTAKE_REGISTRY_{_today()}.md"
    body = _tag_header(topic="MISTAKE-REG", seq=1, subpath=f"audits/{path.name}", title="Mistake registry — Sina Command maintainer")
    body += """**Chat is not SSOT.** Append every repeat-mistake here.

| Date | Pattern | Root cause | Fix / never again |
|------|---------|------------|---------------------|
"""
    path.write_text(body, encoding="utf-8")
    _register_manifest(path, topic="MISTAKE-REG", seq=1, title="Mistake registry")
    return path


def _register_manifest(path: Path, *, topic: str, seq: int, title: str) -> None:
    ref_tag = f"MAINT-REF-{topic}-{seq:03d}"
    trace_id = f"MAINT-REF-{_today()}-{topic}-{seq:03d}"
    rel = path.relative_to(PRIVATE_REF).as_posix()
    entry = {
        "ref_tag": ref_tag,
        "trace_id": trace_id,
        "path": rel,
        "title": title,
        "version": "1.0",
        "canonical": False,
        "written": _today(),
    }
    manifest: dict = {"schema": "maintainer-private-reference-manifest-v1", "entries": []}
    if MANIFEST.is_file():
        try:
            manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    entries = manifest.setdefault("entries", [])
    if not any(e.get("ref_tag") == ref_tag for e in entries):
        entries.append(entry)
    manifest["generated_at"] = _now()
    manifest["agent_id"] = MAINTAINER_ID
    PRIVATE_REF.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _sync_mistake_pointer(registry: Path) -> None:
    MEMORY.mkdir(parents=True, exist_ok=True)
    MISTAKE_REGISTRY_POINTER.write_text(
        f"# Mistake registry pointer\n\n"
        f"**SSOT (tagged):** `{registry}`\n\n"
        f"Tag on line 1 of that file. Trace includes date: `MAINT-REF-{_today()}-...`\n",
        encoding="utf-8",
    )


def _ensure_mistake_registry() -> Path:
    reg = _latest_mistake_registry()
    _sync_mistake_pointer(reg)
    return reg


def _mandatory_reads() -> list[Path]:
    return [
        PRIV / "INCIDENT_REPORT_ALWAYS.md",
        CONTEXT_INCIDENT,
        MAINTAINER_INCIDENT,
        TAG_STANDARD,
        _ensure_mistake_registry(),
        PRIV / "SESSION_CLOSEOUT_LATEST.md",
        Path.home() / ".cursor/skills/agent-self-audit-loop/SKILL.md",
    ]


def cmd_start() -> int:
    _ensure_mistake_registry()
    _run(
        [
            "python3",
            str(SCRIPT_DIR / "agent_rules_loop_orchestrator.py"),
            "--phase",
            "session_start",
            "--agent-id",
            MAINTAINER_ID,
        ]
    )
    code, out = _run(["python3", str(SELF_AUDIT_SCRIPT), "session-start", "--agent", MAINTAINER_ID])
    print(out)
    missing = [p for p in _mandatory_reads() if not p.is_file()]
    if missing:
        print("WARN_MISSING_READS")
        for p in missing:
            print(f"  - {p}")
    else:
        print("OK_ALL_MANDATORY_READS_PRESENT")
    _append_log({"type": "loop_start", "missing": [str(p) for p in missing]})
    _save_state({"last_loop_start_at": _now(), "last_missing_reads": [str(p) for p in missing]})
    return 0 if code == 0 else code


def cmd_preflight() -> int:
    _ensure_mistake_registry()
    rc_rules, rules_out = _run(
        [
            "python3",
            str(SCRIPT_DIR / "agent_rules_loop_orchestrator.py"),
            "--phase",
            "maintainer_preflight",
            "--agent-id",
            MAINTAINER_ID,
        ]
    )
    print(rules_out)
    if rc_rules != 0:
        print("PREFLIGHT_FAIL — rules-in-charge loop check failed")
        return 1
    code, out = _run(["python3", str(SELF_AUDIT_SCRIPT), "audit", "--agent", MAINTAINER_ID])
    print(out)
    if code != 0:
        print("PREFLIGHT_FAIL — run: maintainer_self_audit_loop.py start")
        return 1
    print(f"READ_MISTAKE_REGISTRY={_ensure_mistake_registry()}")
    print(f"READ_MAINTAINER_INCIDENT={MAINTAINER_INCIDENT}")
    _append_log({"type": "preflight", "audit": "pass"})
    _save_state({"last_preflight_at": _now()})
    return 0


def cmd_log(summary: str, evidence: str) -> int:
    code, out = _run(
        [
            "python3",
            str(SELF_AUDIT_SCRIPT),
            "log-event",
            "--agent",
            MAINTAINER_ID,
            "--summary",
            summary,
            "--evidence",
            evidence,
        ]
    )
    print(out)
    _append_log({"type": "milestone", "summary": summary, "evidence": evidence})
    return code


def _hub_health() -> dict:
    out: dict = {"ok": False, "health_ms": None, "data_ms": None, "error": None}
    try:
        t0 = datetime.now(timezone.utc)
        with urllib.request.urlopen(f"{HUB_BASE}/health", timeout=5) as resp:
            out["health_ok"] = resp.status == 200
        out["health_ms"] = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)
        t1 = datetime.now(timezone.utc)
        with urllib.request.urlopen(f"{HUB_BASE}/command-data.json", timeout=30) as resp:
            resp.read(4096)
            out["data_ok"] = resp.status == 200
        out["data_ms"] = int((datetime.now(timezone.utc) - t1).total_seconds() * 1000)
        out["ok"] = True
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        out["error"] = str(e)
    return out


def _server_rss_mb() -> int | None:
    try:
        out = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in out.stdout.splitlines():
            if "sina-command-server.py" in line and "grep" not in line:
                parts = line.split()
                if len(parts) > 5:
                    return int(int(parts[5]) / 1024)
    except (OSError, ValueError):
        pass
    return None


def cmd_postflight(summary: str, files: str, verify: str, next_steps: str, incidents: str) -> int:
    failures: list[str] = []
    code, bugs_out = _run(["python3", str(SCRIPT_DIR / "find_critical_bugs.py")])
    print(bugs_out)
    if code != 0 or '"critical": 0' not in bugs_out.replace(" ", ""):
        if '"critical": 0' not in bugs_out:
            failures.append("find_critical_bugs not clean")
    health = _hub_health()
    print(f"HUB_HEALTH={json.dumps(health)}")
    if not health.get("ok"):
        failures.append(f"hub unreachable: {health.get('error')}")
    rss = _server_rss_mb()
    print(f"SERVER_RSS_MB={rss}")
    if rss is not None and rss > 200:
        failures.append(f"server RSS high: {rss}MB (restart hub)")
    index_html = SOURCE_A / "agent-control-panel" / "index.html"
    if index_html.is_file():
        size_kb = index_html.stat().st_size / 1024
        print(f"INDEX_HTML_KB={size_kb:.1f}")
        if size_kb > 50:
            failures.append(f"index.html bloated ({size_kb:.0f}KB) — rebuild panel")
    close_code, close_out = _run(
        [
            "python3",
            str(SELF_AUDIT_SCRIPT),
            "session-close",
            "--agent",
            MAINTAINER_ID,
            "--summary",
            summary,
            "--files",
            files,
            "--verify",
            verify or bugs_out[:800],
            "--next",
            next_steps,
            "--incidents",
            incidents,
        ]
    )
    print(close_out)
    _append_log(
        {
            "type": "postflight",
            "summary": summary[:300],
            "health": health,
            "rss_mb": rss,
            "failures": failures,
        }
    )
    _save_state({"last_postflight_at": _now(), "last_failures": failures})
    if failures:
        print("POSTFLIGHT_WARN")
        for f in failures:
            print(f"  - {f}")
    else:
        print("POSTFLIGHT_PASS")
    return 0 if close_code == 0 else close_code


def cmd_record_mistake(pattern: str, fix: str, root_cause: str) -> int:
    reg = _ensure_mistake_registry()
    date = _today()
    line = f"| {date} | {pattern.strip()} | {root_cause.strip() or 'repeat'} | {fix.strip()} |"
    with reg.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    _append_log({"type": "mistake_recorded", "pattern": pattern, "fix": fix, "registry": str(reg)})
    print(f"OK recorded mistake in {reg}")
    return 0


def cmd_write_doc(topic: str, title: str, body: str, seq: int) -> int:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", topic).strip("-").upper()[:24] or "DOC"
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{slug}_{_today()}.md"
    path = AUDITS_DIR / fname
    if path.is_file():
        fname = f"{slug}_{_today()}_{seq:03d}.md"
        path = AUDITS_DIR / fname
    text = _tag_header(topic=topic, seq=seq, subpath=f"audits/{path.name}", title=title)
    text += body.strip() + "\n"
    path.write_text(text, encoding="utf-8")
    _register_manifest(path, topic=topic, seq=seq, title=title)
    _append_log({"type": "doc_written", "path": str(path), "topic": topic})
    print(f"OK tagged doc: {path}")
    print(f"TAG_LINE=[MAINTAINER_AGENT_REF · {MAINTAINER_ID} · MAINT-REF-{topic}-{seq:03d}]")
    return 0


def cmd_status() -> int:
    st = _load_state()
    reg = _ensure_mistake_registry()
    print(json.dumps({"state": st, "mistake_registry": str(reg), "log": str(AUDIT_LOOP_LOG)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Maintainer self-audit loop")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("start", help="Session start + mandatory reads")
    sub.add_parser("preflight", help="Gate before hub edits")
    sub.add_parser("status", help="Loop state + paths")

    p_log = sub.add_parser("log", help="Milestone during work")
    p_log.add_argument("--summary", required=True)
    p_log.add_argument("--evidence", default="")

    p_post = sub.add_parser("postflight", help="Audits + session close")
    p_post.add_argument("--summary", required=True)
    p_post.add_argument("--files", default="")
    p_post.add_argument("--verify", default="")
    p_post.add_argument("--next", default="")
    p_post.add_argument("--incidents", default="")

    p_rec = sub.add_parser("record-mistake", help="Append to mistake registry")
    p_rec.add_argument("--pattern", required=True)
    p_rec.add_argument("--fix", required=True)
    p_rec.add_argument("--root-cause", default="")

    p_doc = sub.add_parser("write-doc", help="New tagged private-reference doc (date in trace_id + filename)")
    p_doc.add_argument("--topic", required=True, help="TOPIC slug e.g. SELF-AUDIT")
    p_doc.add_argument("--title", required=True)
    p_doc.add_argument("--body", required=True)
    p_doc.add_argument("--seq", type=int, default=1)

    args = parser.parse_args()
    if args.cmd == "start":
        return cmd_start()
    if args.cmd == "preflight":
        return cmd_preflight()
    if args.cmd == "log":
        return cmd_log(args.summary, args.evidence)
    if args.cmd == "postflight":
        return cmd_postflight(args.summary, args.files, args.verify, args.next, args.incidents)
    if args.cmd == "record-mistake":
        return cmd_record_mistake(args.pattern, args.fix, args.root_cause)
    if args.cmd == "write-doc":
        return cmd_write_doc(args.topic, args.title, args.body, args.seq)
    if args.cmd == "status":
        return cmd_status()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
