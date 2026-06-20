#!/usr/bin/env python3
"""Scan ~/.cursor/projects agent transcripts → AGENT_FLEET_REGISTRY.json + static dashboard."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"
OUT_DIR = SOURCE_A / "data" / "agent_fleet"
REGISTRY_PATH = OUT_DIR / "AGENT_FLEET_REGISTRY.json"
DASHBOARD_PATH = SOURCE_A / "agent-control-panel" / "index.html"


def slug_to_name(slug: str) -> str:
    m = re.match(r"Users-sinakazemnezhad-Desktop-(.+)", slug)
    if m:
        return m.group(1).replace("-", " ")
    return slug


def first_user_preview(jsonl: Path, max_len: int = 120) -> str:
    try:
        with jsonl.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if len(line) < 10:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("role") != "user":
                    continue
                text = ""
                for part in row.get("message", {}).get("content", []):
                    if isinstance(part, dict) and part.get("type") == "text":
                        text += part.get("text", "")
                    elif isinstance(part, str):
                        text += part
                if not text:
                    text = str(row.get("message", ""))[:max_len]
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    return text[:max_len] + ("…" if len(text) > max_len else "")
    except OSError:
        pass
    return ""


def scan_workspace(transcripts_root: Path) -> list[dict]:
    sessions = []
    for child in sorted(transcripts_root.iterdir()):
        if not child.is_dir():
            continue
        main = child / f"{child.name}.jsonl"
        if not main.is_file():
            continue
        stat = main.stat()
        subagents = list((child / "subagents").glob("*.jsonl")) if (child / "subagents").is_dir() else []
        sessions.append(
            {
                "transcript_id": child.name,
                "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "size_kb": round(stat.st_size / 1024, 1),
                "preview": first_user_preview(main),
                "subagent_count": len(subagents),
            }
        )
    sessions.sort(key=lambda s: s["updated_at"], reverse=True)
    return sessions


def scan_all() -> dict:
    workspaces = []
    if not CURSOR_PROJECTS.is_dir():
        return {"error": "cursor projects dir missing", "workspaces": []}

    for proj in sorted(CURSOR_PROJECTS.iterdir()):
        if not proj.is_dir():
            continue
        tr = proj / "agent-transcripts"
        if not tr.is_dir():
            continue
        sessions = scan_workspace(tr)
        if not sessions:
            continue
        workspaces.append(
            {
                "slug": proj.name,
                "display_name": slug_to_name(proj.name),
                "path_hint": str(proj),
                "sessions": sessions,
                "session_count": len(sessions),
                "last_active": sessions[0]["updated_at"] if sessions else None,
            }
        )

    workspaces.sort(key=lambda w: w.get("last_active") or "", reverse=True)
    now = datetime.now(timezone.utc)
    active_24h = 0
    for w in workspaces:
        for s in w["sessions"]:
            try:
                ts = datetime.fromisoformat(s["updated_at"].replace("Z", "+00:00"))
                if (now - ts).total_seconds() < 86400:
                    active_24h += 1
            except ValueError:
                pass

    return {
        "schema_version": 1,
        "scanned_at": now.isoformat(),
        "cursor_projects_root": str(CURSOR_PROJECTS),
        "workspaces": workspaces,
        "summary": {
            "workspace_count": len(workspaces),
            "session_count": sum(w["session_count"] for w in workspaces),
            "active_sessions_24h": active_24h,
        },
    }


def refresh_command_panel() -> None:
    import os
    import subprocess

    if os.environ.get("SINA_SKIP_PANEL_BUILD", "").strip() in ("1", "true", "yes"):
        return
    panel = SOURCE_A / "scripts/build-sina-command-panel.py"
    if panel.is_file():
        subprocess.run(["python3", str(panel)], check=False, cwd=SOURCE_A)


def write_dashboard_legacy(data: dict) -> None:
    """Deprecated — Sina Command panel replaces minimal desk."""
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ASF Agent Desk</title>
  <style>
    :root {{ font-family: system-ui, sans-serif; background: #0f1419; color: #e7ecf3; }}
    body {{ margin: 0; padding: 24px; max-width: 1100px; margin-inline: auto; }}
    h1 {{ font-size: 1.4rem; margin: 0 0 8px; }}
    .meta {{ color: #8b9cb3; font-size: 0.9rem; margin-bottom: 24px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-bottom: 28px; }}
    .card {{ background: #1a2332; border: 1px solid #2a3a52; border-radius: 8px; padding: 14px; }}
    .card strong {{ display: block; font-size: 1.5rem; }}
    details {{ background: #1a2332; border: 1px solid #2a3a52; border-radius: 8px; margin-bottom: 10px; padding: 12px; }}
    summary {{ cursor: pointer; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 10px; }}
    th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #2a3a52; }}
    .preview {{ color: #8b9cb3; max-width: 420px; }}
    code {{ font-size: 0.75rem; }}
  </style>
</head>
<body>
  <h1>ASF Agent Desk</h1>
  <p class="meta">Local fleet monitor · spec: AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md</p>
  <div class="cards" id="summary"></div>
  <div id="list"></div>
  <script>
    const DATA = {payload};
    const s = DATA.summary || {{}};
    document.getElementById("summary").innerHTML = `
      <div class="card"><strong>${{s.workspace_count ?? 0}}</strong>workspaces</div>
      <div class="card"><strong>${{s.session_count ?? 0}}</strong>sessions</div>
      <div class="card"><strong>${{s.active_sessions_24h ?? 0}}</strong>active 24h</div>
    `;
    document.getElementById("list").innerHTML = (DATA.workspaces || []).map(w => `
      <details>
        <summary>${{w.display_name}} (${{w.session_count}})</summary>
        <p class="meta">Last: ${{w.last_active || "—"}} · <code>${{w.slug}}</code></p>
        <table>
          <tr><th>Updated</th><th>KB</th><th>Sub</th><th>Preview</th><th>ID</th></tr>
          ${{(w.sessions || []).map(x => `
            <tr>
              <td>${{x.updated_at?.slice(0,19)}}</td>
              <td>${{x.size_kb}}</td>
              <td>${{x.subagent_count}}</td>
              <td class="preview">${{x.preview || "—"}}</td>
              <td><code>${{x.transcript_id?.slice(0,8)}}…</code></td>
            </tr>
          `).join("")}}
        </table>
      </details>
    `).join("");
  </script>
</body>
</html>
"""
    DASHBOARD_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = scan_all()
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    refresh_command_panel()
    print(f"Wrote {REGISTRY_PATH}")
    print(f"Panel: {DASHBOARD_PATH}")
    print(f"Summary: {data.get('summary')}")


if __name__ == "__main__":
    main()
