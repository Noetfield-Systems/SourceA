#!/usr/bin/env python3
"""Generate 1000 Chat Unify score-up plans — :13023 standalone + DMG shell.

SSOT: docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md
Dedup: all other mission pack titles.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "chat-unify-score-up-1000"
PREFIX = "cu-score"

THEMES = [
    ("t41-platform-shell", "Platform shell visual parity", 50, 92, "Arc / Raycast"),
    ("t42-multi-machine", "Multi-machine tabs UX", 55, 90, "Shift browser"),
    ("t43-ord-atoms", "ORD atoms & work orders", 48, 88, "Linear issues"),
    ("t44-integrations", "Integrations catalog UI", 52, 91, "Zapier"),
    ("t45-forge-embed", "Forge Terminal embed tab", 58, 93, "Cursor tab"),
    ("t46-paste-receipt", "Paste → receipt verify loop", 60, 94, "Grammarly"),
    ("t47-onboarding", "Onboarding & first win", 45, 90, "Duolingo"),
    ("t48-mobile-forge", "Mobile / narrow layout", 42, 88, "ChatGPT mobile"),
    ("t49-sync-forge", "Sync with Forge Connect", 55, 92, "Replit"),
    ("t50-unify-e2e", "Chat Unify E2E proof", 65, 100, "Playwright"),
]

WORKSTREAMS = [
    ("w41-ship", "Ship"),
    ("w42-ui", "UI polish"),
    ("w43-css", "CSS tokens"),
    ("w44-js", "JS wire"),
    ("w45-api", "API"),
    ("w46-machine", "Machine tab"),
    ("w47-onboard", "Onboard"),
    ("w48-deploy", "Deploy DMG"),
    ("w49-bench", "Bench"),
    ("w50-receipt", "Receipt"),
]

DELIVERABLES: dict[str, list[str]] = {
    "t41-platform-shell": [
        "home-enterprise.css imports sourcea.css token variables",
        "platform home hero matches founder-home sa-hero-grid rhythm",
        "cu header uses ar-header pattern not legacy cu-bar",
        "tab strip typography Inter 13px uppercase labels",
        "dark bg #0c0e12 across chat-unify-standalone",
        "primary buttons sa-btn-glow on platform CTAs",
        "footer links match site footer grid",
        "remove visual gap vs sourcea.app platform page",
        "Chat Unify.app window chrome title SourceA",
        "screenshot parity gate vs sourcea.app/learn",
    ],
    "t42-multi-machine": [
        "machine tab cards with live HTTP verify dot",
        "add machine flow matches site segment picker",
        "tab drag reorder persist localStorage",
        "machine rename inline edit",
        "per-machine last sync timestamp",
        "empty machines state with honest onboarding",
        "10 machine cap UI warning",
        "machine color accent per lane",
        "keyboard shortcut switch tabs ⌘1-9",
        "export machines JSON backup",
    ],
    "t43-ord-atoms": [
        "ORD atom cards match site sa-explore-card style",
        "work order queue visible on platform home",
        "claim rules UI from chat-unify-ord-claim-rules-v1.json",
        "atom status chips PASS/BLOCK site colors",
        "paste atom → trace to disk animation",
        "ord receipt row in thread sidebar",
        "founder glance UI contract wired",
        "filter atoms by lane startup/agency/cursor",
        "bulk atom import CSV",
        "ord validator script in CI hook",
    ],
    "t44-integrations": [
        "integrations grid from chat-unify-integrations-v1.json styled",
        "n8n template card links to site sandbox",
        "Cursor plugin card honest install steps",
        "integration connect OAuth honest not fake",
        "per-integration pulse track event",
        "integrations search filter",
        "recommended integrations for segment",
        "integration receipt on successful wire",
        "disable broken integration graceful UI",
        "partner logo wall from site trust page",
    ],
    "t45-forge-embed": [
        "/terminal/ tab iframe uses live forge-terminal-v1",
        "FORGE_TERMINAL_USE_LIVE_UI=1 embed chrome contract",
        "embed sidebar kept compact per forge skill",
        "switch forge ↔ platform without losing thread",
        "forge quality bridge visible in embed",
        "mesh shows forge peer when embed active",
        "deep link open in full forge app",
        "embed loading skeleton site-styled",
        "postMessage height sync parent shell",
        "embed E2E playwright chat-unify tab",
    ],
    "t46-paste-receipt": [
        "paste panel cu-hint styled like site proof aside",
        "claims trace UI not raw JSON dump",
        "unverified claims amber chip count",
        "export receipt markdown for client",
        "share receipt link with pulse UTM",
        "paste history last 5 items",
        "compare two pastes diff view",
        "pre-llm policy banner above paste area",
        "RAW AI parses paste not Cursor",
        "receipt verify links to /sourcea/proof/live",
    ],
    "t47-onboarding": [
        "chat-unify-onboarding-v1.js site visual parity",
        "first-run tour 3 steps max Duolingo style",
        "segment pick on onboarding matches site doors",
        "skip tour persists flag",
        "onboarding ends on first successful paste receipt",
        "DMG first open launches onboarding",
        "onboarding pulse events onboard_step_*",
        "help panel links /learn and /forge/terminal",
        "confetti on first machine live verify",
        "onboarding receipt in ~/.sina/",
    ],
    "t48-mobile-forge": [
        "narrow viewport machine tabs scroll horizontal",
        "composer fixed bottom safe-area-inset",
        "touch targets 44px on primary actions",
        "collapse sidebar to hamburger <768px",
        "mobile pulse feedback FAB optional",
        "PWA manifest stub for chat unify",
        "font-size 16px inputs prevent iOS zoom",
        "swipe between machine tabs",
        "mobile E2E playwright iPhone viewport",
        "honest 'desktop recommended' banner mobile",
    ],
    "t49-sync-forge": [
        "sync-forge-connect script auto-run on boot",
        "shared secrets path ~/.sina/secrets.env doc link",
        "chat unify API hits same prompt forge as forge",
        "version parity display cu vs forge UI_VERSION",
        "single sign-on local token shared ports",
        "conflict resolution when both edit same ws",
        "sync status row on platform home",
        "launchd plist health probe both ports",
        "founder one-click boot chat-unify-stack-boot.sh UI",
        "mesh diagram on site /platform honest",
    ],
    "t50-unify-e2e": [
        "validate-chat-unify-standalone-v1.sh PASS",
        "playwright :13023 platform home 200",
        "playwright machine add flow",
        "grep no mailto primary CTA chat-unify paths",
        "ord rules validator PASS",
        "integrations JSON schema valid",
        "DMG build script smoke",
        "visual parity vs site script extended to cu",
        "mission REGISTRY closeout built_by pre-llm-mac",
        "combined 6000 validate script PASS",
    ],
}

WS_ACTION = {w: lbl.split()[0] for w, lbl in WORKSTREAMS}
WS_ACTION.update({
    "w41-ship": "Ship", "w42-ui": "Polish UI", "w43-css": "Tokenize", "w44-js": "Wire",
    "w45-api": "API", "w46-machine": "Machine tab", "w47-onboard": "Onboard",
    "w48-deploy": "Deploy", "w49-bench": "Bench", "w50-receipt": "Receipt for",
})

TIER_FOR_SLICE = ["T0", "T0", "T1", "T1", "T1", "T2", "T2", "T2", "T3", "T3"]
TIER_DEPTH = {
    "T0": "P0 — ship on Chat Unify :13023 + DMG shell · site visual parity",
    "T1": "P1 — UX delta with receipt",
    "T2": "P2 — harden · validate",
    "T3": "P3 — bench",
}


def load_existing_titles() -> set[str]:
    titles: set[str] = set()
    for rel in (
        "brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json",
        "brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json",
        "brain-os/plan-registry/forge-terminal-score-up-1000/REGISTRY.json",
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
        phases.append({"id": phase_id, "theme": theme_id, "theme_label": theme_label, "market_analog": market})
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
                    f"**Surface:** Chat Unify `http://127.0.0.1:13023/` + DMG\n"
                    f"**Worker:** Pre-LLM Mac RAW AI · Cursor observes only\n\n"
                    f"## Task\n\n{TIER_DEPTH[tier]}\n\n**Deliverable:** {title}\n",
                    encoding="utf-8",
                )
                entries.append({
                    "id": plan_id,
                    "pack": "chat-unify",
                    "surfaces": ["local:13023", "dmg:chat-unify-mac"],
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
        "schema": "chat-unify-score-up-1000-registry-v1",
        "generated_at": now,
        "count": len(entries),
        "prefix": PREFIX,
        "law_doc": "docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md",
        "phases": phases,
        "plans": entries,
    }
    PACK_BASE.mkdir(parents=True, exist_ok=True)
    (PACK_BASE / "REGISTRY.json").write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    return {"ok": len(entries) == 1000}


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = generate(now)
    print(json.dumps({"ok": r["ok"], "pack": "chat-unify", "count": 1000}))
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
