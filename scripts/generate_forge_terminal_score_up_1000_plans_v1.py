#!/usr/bin/env python3
"""Generate 1000 Forge Terminal score-up plans — local :13029 + online /sourcea/forge/terminal.

SSOT: docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md
Dedup: sa-score*, sa-score2*, cu-score* titles.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = 1
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "forge-terminal-score-up-1000"
PREFIX = "ft-score"

THEMES = [
    ("t31-visual-parity", "Visual parity with sourcea.app", 52, 94, "Vercel / Linear"),
    ("t32-living-ui", "Living chat UI (Cursor/Replit)", 58, 95, "Cursor IDE"),
    ("t33-online-local-sync", "Online demo ↔ Mac IDE sync", 48, 93, "Replit web + desktop"),
    ("t34-founder-language", "Founder-language replies", 70, 98, "Duolingo clarity"),
    ("t35-quality-gate", "Quality gate & exec block", 65, 96, "CI quality gates"),
    ("t36-pre-llm-pipeline", "Pre-LLM prompt forge pipeline", 72, 99, "SourceA pre-LLM spine"),
    ("t37-desktop-mesh", "Desktop mesh & peers UI", 60, 92, "Raycast / Arc"),
    ("t38-cloud-dispatch", "Cloud dispatch from terminal", 55, 94, "Railway / Trigger.dev"),
    ("t39-workspace-ide", "Workspace IDE & explorer", 62, 91, "VS Code"),
    ("t40-forge-e2e", "Forge Terminal E2E proof", 68, 100, "Playwright"),
]

WORKSTREAMS = [
    ("w31-ship", "Ship"),
    ("w32-sync", "Sync surfaces"),
    ("w33-css", "CSS tokens"),
    ("w34-js", "JS behavior"),
    ("w35-api", "API wire"),
    ("w36-embed", "Embed mode"),
    ("w37-feedback", "Feedback loop"),
    ("w38-deploy", "Deploy online"),
    ("w39-bench", "Bench market"),
    ("w40-receipt", "Receipt"),
]

DELIVERABLES: dict[str, list[str]] = {
    "t31-visual-parity": [
        "import forge-visual-parity-contract-v1.json tokens into terminal.css",
        "Plus Jakarta Sans + Inter on apps/forge-terminal-v1 matching sourcea.css",
        "ar-header clone on SourceA-landing/green-unified/forge/terminal.html",
        "sa-btn-glow primary Send button on local IDE",
        "dark shell #0c0e12 parity on forge-connect shell",
        "forge-mark logo matches ar-logo-run accent wipe",
        "sidebar explorer typography 14px Inter not system-ui",
        "quality chips PASS/REVISE colors match site accent",
        "remove visual drift between connect-v1 and terminal-v1",
        "screenshot diff gate local vs online header chrome",
    ],
    "t32-living-ui": [
        "resizable chat column --dock-h persisted localStorage",
        "Enter send Shift+Enter newline on online demo composer",
        "renderFounderSections four-block layout on public demo",
        "compact embed mode for connect iframe tab",
        "mesh sidebar green/red peer dots like Replit",
        "status bar model latency cost on local topbar",
        "skeleton loader on Connecting… state online",
        "thread scroll anchor on new message both surfaces",
        "markdown tables in chat without raw HTML leak",
        "mobile viewport chat-first layout online demo",
    ],
    "t33-online-local-sync": [
        "shared terminal.js module stub for online + local",
        "version pin sourcea-forge-demo-version = terminal.css v",
        "same chip prompts on aside local help panel",
        "online brain-chat worker = local API response shape",
        "feature flag matrix: what online lacks vs Mac honest list",
        "deep link Mac app from online after 2 turns",
        "pulse event forge_terminal_turn on both surfaces",
        "sync feedback form fields online ↔ local optional panel",
        "OG meta online matches forge product page",
        "build script copies terminal.css subset to landing dist",
    ],
    "t34-founder-language": [
        "translate_for_founder on every online demo reply",
        "no JSON bubble leak on public demo",
        "Bottom line chip first in online render",
        "blockers list human readable not tool names",
        "founder tone law enforced in demo system prompt",
        "display_response field only in online API client",
        "error messages founder-friendly not stack traces",
        "offline banner copy matches site vocabulary",
        "Try asking chips use segment router labels",
        "post-turn CTA See live receipt not Talk to us",
    ],
    "t35-quality-gate": [
        "quality_gate chip inline online after reply",
        "exec blocked until PASS on local Send",
        "quality score visible in thread meta reload",
        "REJECT state red panel like site proof quiz",
        "re-run quality from thread context menu",
        "export quality receipt JSON for founder",
        "online demo show quality tier public-safe",
        "bridge forge-quality-bridge.js to online demo",
        "gate layers count chip not wall of PASS",
        "E2E assert quality_gate present in API",
    ],
    "t36-pre-llm-pipeline": [
        "chat_unify_prompt_forge_v1 on online send path",
        "prompt forge badge visible in composer chrome",
        "RAW AI worker path documented not Cursor implement",
        "session gate receipt before first local send",
        "feasibility gate on cloud dispatch only",
        "pre-llm-world-model MANIFEST link in help aside",
        "dispatch log row in status bar",
        "forbidden cursor-as-worker banner in dev build",
        "plan pick → paste → RAW AI closeout loop UI",
        "receipt path ~/.sina/forge-plan-receipt-v1.json",
    ],
    "t37-desktop-mesh": [
        "mesh list styling matches site sa-engine chips",
        "Chat Unify peer row live/degraded/offline colors",
        "cloud workers dispatch link in mesh panel",
        "hub 13020 glance row honest degraded state",
        "click peer opens URL in system browser",
        "mesh probe auto-refresh 30s without flicker",
        "forge_self health pill in topbar",
        "integrations probe row when n8n wired",
        "desktop mesh JSON API for founder dashboard",
        "mesh empty state copy when only forge live",
    ],
    "t38-cloud-dispatch": [
        "Proceed to cloud button gated quality PASS",
        "dry_run=true default on Mac control plane",
        "cloud worker receipt link in thread",
        ":13027 dispatch status in status bar",
        "Railway FBE link honest not fake progress",
        "swarm dispatch optional panel v3 blackboard",
        "hundred rows vocabulary in dispatch modal",
        "no fbe_motor_delegate on Mac body",
        "dispatch error founder language translate",
        "online demo does NOT dispatch cloud (honest)",
    ],
    "t39-workspace-ide": [
        "open folder ⌘O matches Cursor pattern",
        "file tree monospace paths truncated ellipsis",
        "workspace horizontal strip in embed mode",
        "multi-root workspace switcher polish",
        "agent list cards with role labels",
        "explorer empty state link Open Folder",
        "sidebar width drag persist forge-sidebar-resize",
        "bottom dock terminal logs resizable",
        "tabs for open files stub honest coming",
        "git status chip stub without fake green",
    ],
    "t40-forge-e2e": [
        "forge_terminal_living_ui_e2e_verify_v1.py PASS",
        "playwright online /sourcea/forge/terminal send",
        "playwright local :13029 health 200",
        "visual parity script validate-forge-visual-parity-v1.sh",
        "no mailto primary CTA grep gate on forge paths",
        "api forge-terminal v1 compile smoke",
        "connect server UI_VERSION matches package",
        "online demo brain worker 200 OPTIONS",
        "feedback form preventDefault online",
        "mission plan closeout updates REGISTRY.json",
    ],
}

WS_ACTION = {
    "w31-ship": "Ship",
    "w32-sync": "Sync",
    "w33-css": "Tokenize CSS for",
    "w34-js": "Wire JS for",
    "w35-api": "API bind",
    "w36-embed": "Embed polish",
    "w37-feedback": "Feedback wire",
    "w38-deploy": "Deploy",
    "w39-bench": "Bench",
    "w40-receipt": "Receipt for",
}

TIER_FOR_SLICE = ["T0", "T0", "T1", "T1", "T1", "T2", "T2", "T2", "T3", "T3"]
TIER_DEPTH = {
    "T0": "P0 — ship on BOTH local :13029 AND online /sourcea/forge/terminal",
    "T1": "P1 — measurable visual or UX delta with screenshot receipt",
    "T2": "P2 — harden · E2E · document",
    "T3": "P3 — bench · defer",
}


def load_existing_titles() -> set[str]:
    titles: set[str] = set()
    for rel in (
        "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
        "brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json",
        "brain-os/plan-registry/chat-unify-score-up-1000/REGISTRY.json",
    ):
        p = SOURCEA_ROOT / rel
        if p.is_file():
            reg = json.loads(p.read_text(encoding="utf-8"))
            titles |= {x["title"].lower().strip() for x in reg.get("plans", [])}
    return titles


def plan_title(theme_id: str, ws_id: str, slice_n: int) -> str:
    ws_idx = next(i for i, (wid, _) in enumerate(WORKSTREAMS) if wid == ws_id)
    items = DELIVERABLES[theme_id]
    idx = (ws_idx + slice_n - 1) % len(items)
    return f"{WS_ACTION[ws_id]} {items[idx]}"


def phase_for_rank(rank: int) -> str:
    if rank <= 60:
        return "NOW"
    if rank <= 220:
        return "NEXT"
    if rank <= 550:
        return "LATER"
    return "MOONSHOT"


def generate(now: str) -> dict:
    existing = load_existing_titles()
    entries = []
    phases = []
    seq = 0
    dupes = []

    for theme_id, theme_label, sn, st, market in THEMES:
        phase_id = f"phase-{PREFIX}-{theme_id}"
        phases.append({"id": phase_id, "theme": theme_id, "theme_label": theme_label, "score_now": sn, "score_target": st, "market_analog": market})
        for ws_id, ws_label in WORKSTREAMS:
            for slice_n in range(1, 11):
                seq += 1
                plan_id = f"{PREFIX}-{seq:04d}"
                title = plan_title(theme_id, ws_id, slice_n)
                if title.lower().strip() in existing:
                    dupes.append(title)
                tier = TIER_FOR_SLICE[slice_n - 1]
                phase = phase_for_rank(seq)
                rel = f"prompts/{phase_id}/{ws_id}/slice-{slice_n:02d}.md"
                path = PACK_BASE / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    f"# {plan_id} — {title}\n\n"
                    f"**Surfaces:** local `http://127.0.0.1:13029/` + online `https://sourcea.app/sourcea/forge/terminal`\n"
                    f"**Worker:** Pre-LLM Mac RAW AI · Cursor observes only\n"
                    f"**SSOT:** docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md\n\n"
                    f"## Task\n\n{TIER_DEPTH[tier]}\n\n**Deliverable:** {title}\n",
                    encoding="utf-8",
                )
                entries.append({
                    "id": plan_id,
                    "pack": "forge-terminal",
                    "surfaces": ["local:13029", "online:/sourcea/forge/terminal"],
                    "built_by": "pre-llm-mac",
                    "cursor_role": "observer",
                    "theme": theme_id,
                    "theme_label": theme_label,
                    "workstream": ws_id,
                    "slice": slice_n,
                    "tier": tier,
                    "phase": phase,
                    "title": title,
                    "status": "open",
                    "priority_rank": seq,
                    "path": rel,
                    "agent_prompt": f"RAW AI WORK — {plan_id}: {title}",
                })

    if dupes:
        raise SystemExit(f"dupes: {dupes[:3]} ({len(dupes)})")

    reg = {
        "schema": "forge-terminal-score-up-1000-registry-v1",
        "generated_at": now,
        "count": len(entries),
        "prefix": PREFIX,
        "baseline_score": 58,
        "target_score": 93,
        "law_doc": "docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md",
        "visual_contract": "data/forge-visual-parity-contract-v1.json",
        "phases": phases,
        "plans": entries,
    }
    PACK_BASE.mkdir(parents=True, exist_ok=True)
    (PACK_BASE / "REGISTRY.json").write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    return {"ok": len(entries) == 1000}


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = generate(now)
    print(json.dumps({"ok": r["ok"], "pack": "forge-terminal", "count": 1000, "generated_at": now}))
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
