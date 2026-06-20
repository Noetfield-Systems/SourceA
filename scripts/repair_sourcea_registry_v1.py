#!/usr/bin/env python3
"""Repair truncated brain-os/plan-registry/sourcea-1000/REGISTRY.json from salvage + prompt MD."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
PROMPTS = REG.parent / "prompts"
BACKUP = REG.parent / ".REGISTRY.json.truncated-backup"

VERIFY = {
    "T0": "cd scripts && SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py && python3 find_critical_bugs.py",
    "T1": "cd scripts && bash validate-eval-packet-v1b-live.sh && bash validate-governance-fleet-v1.sh && python3 audit_hub_source_alignment.py",
    "T2": "cd scripts && python3 audit_backend_e2e.py && bash validate-spine-bridge-founder-v1.sh",
    "T3": "cd scripts && python3 find_critical_bugs.py",
}
TAG = "AGENT-AUTO-SOURCEA"


def _extract_plan_objects(text: str) -> list[dict]:
    start = text.find('"plans":')
    if start < 0:
        return []
    chunk = text[start:]
    bracket = chunk.find("[")
    if bracket < 0:
        return []
    s = chunk[bracket + 1 :]
    objs: list[dict] = []
    i = 0
    while i < len(s):
        while i < len(s) and s[i] not in "{[":
            i += 1
        if i >= len(s) or s[i] != "{":
            break
        depth = 0
        j = i
        in_str = False
        esc = False
        while j < len(s):
            ch = s[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        blob = s[i : j + 1]
                        try:
                            objs.append(json.loads(blob))
                        except json.JSONDecodeError:
                            pass
                        i = j + 1
                        break
            j += 1
        else:
            break
    return objs


def _load_header(text: str) -> dict:
    idx = text.find('"plans":')
    if idx < 0:
        raise ValueError("plans key missing")
    header_text = text[:idx].rstrip().rstrip(",") + "\n}"
    return json.loads(header_text)


def _parse_md(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm: dict[str, str] = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
    title = ""
    m = re.search(r"^# \[.*?\]\s+sa-\d{4}\s+—\s+(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
    if not title:
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    return fm, title


def _entry_from_md(path: Path) -> dict:
    fm, title = _parse_md(path)
    pid = fm.get("id") or path.stem
    tier = fm.get("tier") or "T1"
    rel = str(path.relative_to(REG.parent))
    task = title or pid
    return {
        "id": pid,
        "phase": fm.get("phase") or "",
        "tier": tier,
        "priority": fm.get("priority") or {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}.get(tier, "P2"),
        "lane": fm.get("lane") or "sourcea",
        "slot": int(fm.get("slot") or 0),
        "title": task[:120],
        "path": rel,
        "status": fm.get("status") or "backlog",
        "verify": VERIFY.get(tier, VERIFY["T3"]),
        "agent_tag": TAG,
        "agent_prompt": f"PLAN WITH NO ASF — {pid}: {task}",
    }


def repair_registry() -> dict:
    if not REG.is_file():
        return {"ok": False, "error": "REGISTRY missing"}

    raw = REG.read_text(encoding="utf-8", errors="replace")
    try:
        json.loads(raw)
        return {"ok": True, "repaired": False, "message": "REGISTRY already valid"}
    except json.JSONDecodeError as exc:
        pass

    if not BACKUP.is_file():
        BACKUP.write_text(raw, encoding="utf-8")

    header = _load_header(raw)
    salvaged = _extract_plan_objects(raw)
    by_id = {p["id"]: p for p in salvaged if p.get("id")}

    for md in sorted(PROMPTS.rglob("sa-*.md")):
        entry = _entry_from_md(md)
        pid = entry["id"]
        if pid not in by_id:
            by_id[pid] = entry
        else:
            # keep salvaged status; fill missing fields from md
            cur = by_id[pid]
            for k, v in entry.items():
                if k not in cur or cur[k] in ("", None):
                    cur[k] = v

    plans = [by_id[f"sa-{i:04d}"] for i in range(1, 1001) if f"sa-{i:04d}" in by_id]
    missing = [f"sa-{i:04d}" for i in range(1, 1001) if f"sa-{i:04d}" not in by_id]
    if missing:
        return {"ok": False, "error": f"missing plans after repair: {missing[:5]} count={len(missing)}"}

    header["plans"] = plans
    header["count"] = len(plans)
    header["repaired_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header["repair_script"] = "scripts/repair_sourcea_registry_v1.py"
    header["salvaged_count"] = len(salvaged)

    REG.write_text(json.dumps(header, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(REG.read_text(encoding="utf-8"))
    return {
        "ok": True,
        "repaired": True,
        "salvaged": len(salvaged),
        "total": len(plans),
        "backup": str(BACKUP),
    }


def main() -> int:
    out = repair_registry()
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
