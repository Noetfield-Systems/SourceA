#!/usr/bin/env python3
"""Lock Canada Priority A pack + portfolio insight plan (SourceA · WitnessBC · 777).

Writes LOCKED markdown to 1 PAGER + os/commercial + lock manifest JSON.
Re-runs email generation and brand surface patches.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PAGER = Path.home() / "Desktop" / "1 PAGER"
OS_COMM = ROOT / "os" / "commercial"
DATA_COMM = ROOT / "data" / "commercial"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lock_header(title: str, path: str, version: str = "1.0.0") -> str:
    return f"""# {title}

**Version:** {version} · **Saved:** {_utc()} · **Status:** LOCKED
**Path:** `{path}`
**Authority:** Founder SAVE + lock · portfolio free-market routing

"""


def _write_locked(src: Path, dest_locked: Path, title: str) -> None:
    body = src.read_text(encoding="utf-8") if src.is_file() else ""
    if "**Saved:**" in body[:400]:
        lines = body.splitlines()
        out = []
        for line in lines:
            if line.startswith("**Saved:**"):
                out.append(f"**Saved:** {_utc()} · **Status:** LOCKED")
            else:
                out.append(line)
        body = "\n".join(lines[:0]) + "\n".join(out) if False else "\n".join(out)
    else:
        body = _lock_header(title, str(dest_locked)) + body
    dest_locked.parent.mkdir(parents=True, exist_ok=True)
    dest_locked.write_text(body, encoding="utf-8")


def portfolio_insight_plan() -> str:
    saved = _utc()
    return f"""# Portfolio Insight & Plan — SourceA · WitnessBC · The 777 Foundation

**Version:** 1.0.0 · **Saved:** {saved} · **Status:** LOCKED
**Path:** `~/Desktop/1 PAGER/PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md`
**Law:** `PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md` · `CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md`
**Rule:** Free-market routing — implement each brand separately; overlap only where disk law allows.

---

## 0. One map (four engines · one founder)

```text
SourceA          → builds controlled factories (engine · proof spine)
Noetfield        → trust at dispatch (Copilot / internal AI)
TrustField       → commercial evidence (MSB · RWA · attestation)
WitnessBC        → human accountability (editorial · corrections)
777 Foundation   → nonprofit readiness (navigation · partners)
```

**Canada RWA June 2026:** TrustField + Noetfield only. SourceA = demo spine. WitnessBC = tertiary. **777 = zero cross-pollination.**

---

## 1. SourceA — insight & 30-day plan

### Identity (locked)

SourceA is the **factory builder** — not the hero on every outbound email. It compiles specs (FBE 76-node graph), ships scoped loops, and runs the live demo every vertical sells.

### Strategic insight

| Force | SourceA move |
|-------|----------------|
| Canada regulatory convergence | Power TrustField/Noetfield sends — never lead cold email as SourceA |
| FBE W0–W3 logged | Factory 1 first bay + motor delegate = **prove the builder works** |
| Living system debate | Pitch control layer for continuous agents — factory is the proof |
| Agency landing | Close on 15-min replay — commercial film + live forensic page |

### 30-day plan (SourceA)

| Week | Ship | Metric |
|------|------|--------|
| W1 | Regenerate factory catalog · validate Phase C · publish landing tunnel | `validate-fbe-w2-v1` PASS |
| W2 | One MARKET_READY factory bundle (`fbe_run_job` full) | Receipt logged |
| W3 | Proof demo script tied to Canada hooks (CSA · FINTRAC) | 3 screen-shares logged |
| W4 | S-P6 white-label receipts for TF/NF deploys | 1 partner pack exported |

### Overlap rules

- **TrustField / Noetfield:** SourceA engine underneath · separate brand invoices
- **WitnessBC:** Proof Lab film uses SourceA BLOCK demo · not Copilot hero
- **777:** No commercial factory sale framing · optional mirror tech only

### Anti-paths

- SourceA as FINTRAC KYB product hero
- Blended portfolio email
- Billion-dollar platform language

---

## 2. WitnessBC (witnessbc.com) — insight & 30-day plan

### Identity (locked)

**Question:** *How do we publish high-stakes updates with sourcing, corrections, and tamper-evident proof?*

Human accountability + agentic editorial — **not** WitnessAI (witness.ai) · **not** pure Copilot governance (that is Noetfield).

### Strategic insight

| Opportunity | Wedge |
|-------------|-------|
| NGO / civic / small newsroom | Tip → approve → publish → **correction with receipt** |
| AI-generated comms risk | Prove what was approved before publish |
| Investor demo | Proof Lab BLOCK publish · 5-min cold start |
| Canada RWA | **Tertiary only** — tokenization issuer **communications discipline** |

### 30-day plan (WitnessBC)

| Week | Ship | Metric |
|------|------|--------|
| W1 | STYLE-B1 hero film ingest · ship gate | `witnessbc-commercial-film-ship` PASS |
| W2 | Proof page + correction flow demo on site | 1 live BLOCK recording |
| W3 | W-P1 outreach (3 NGO/civic targets) | 1 discovery call |
| W4 | W-P3 toolkit ladder (free → Pro PDF) | 1 paid bundle test |

### Site implementation notes

- Keep **WitnessBC** vocabulary — fix any **Witness AI** title drift on public HTML when publishing
- Add Canada tertiary line only on proof/comms pages — not MSB/FINTRAC hero
- Handoff: governance buyer → Noetfield · MSB program → TrustField

### Anti-paths (portfolio law)

- Conflate with WitnessAI
- Hero on M365/Copilot procurement calls
- Automated pay-to-publish
- LOCKED one-pager until ASF single SHIP pick

---

## 3. The 777 Foundation (the777foundation.org) — insight & 30-day plan

### Identity (locked)

**Question:** *How do newcomers and workers in precarious situations get navigation readiness and peer support?*

Nonprofit delivery plane — **independent** from TrustField, VIRLUX, and mono governance spine.

### Strategic insight

| Stakeholder | Motion | Now? |
|-------------|--------|------|
| Settlement agencies · multicultural allies | Gate 0 referral MOU | **YES** |
| Vancouver Foundation · Vancity | Funder pilot budget ($75K scenario) | Gate 0 |
| C3 translation cohort | Guild ops | Parallel |
| LinkedIn partner discovery | Low-volume agentic queue | Background |

### 30-day plan (777)

| Week | Ship | Metric |
|------|------|--------|
| W1 | Partners kit refresh · settlement-bc page audit | 2 partner conversations |
| W2 | Funder pack brief (Gate 0) | 1 LOI meeting |
| W3 | Readiness path map · safeguarding copy pass | Lighthouse a11y check |
| W4 | Impact note draft · donor CTA test | 1 funder follow-up |

### Hard boundaries

| Never | Why |
|-------|-----|
| Canada RWA / FINTRAC outreach | Wrong mission · wrong buyer |
| TrustField / Noetfield product sale | Commercial lane separation |
| SinaaiRuntime on-mission experiments | Independent deploy |
| Legal / clinical / emergency positioning | Safeguarding law |

### SourceA relationship

Alignment only: SourceA builds **infrastructure patterns** 777 may mirror for receipts — not customer-facing brand merge.

---

## 4. Cross-brand overlap matrix (implement separately · wire where useful)

| Capability | SourceA | WitnessBC | 777 | TrustField | Noetfield |
|------------|---------|-----------|-----|------------|-----------|
| Verification demo | **owns** | film | — | attach | attach |
| Signed receipt / TLE | engine | publish | mirror? | attestation | governance |
| Canada June 2026 | spine only | tertiary | **none** | **lead** | AI-native |
| Commercial film | SourceA + WBC hero | **hero** | — | TF attach | NF attach |
| Factory deploy (FBE) | **builder** | — | — | client | client |

---

## 5. Implementation checklist (this lock)

- [x] `CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` — 12 sends
- [x] `canada-priority-a-emails-v1.json` — machine SSOT
- [x] `canada-brand-routing-v1.json` — lane router
- [x] TrustField `compliance.html` — Canada RWA block
- [x] Noetfield `bank-pilot` + `copilot` — Canada NF-RD block
- [x] This insight plan LOCKED
- [ ] WitnessBC film ship (W1)
- [ ] 777 Gate 0 partner send (founder)

---

## 6. Founder next taps (parallel — no single gate)

1. **Canada:** Send Ocree or Newton from locked email pack
2. **SourceA:** RUN INBOX · Factory 1 MARKET_READY pick
3. **WitnessBC:** `bash witnessbc-commercial-film-ship.sh`
4. **777:** Open partners/settlement-bc · one MOU conversation

---

*LOCKED v1 · free-market portfolio routing · disk wins over chat.*
"""


def main() -> int:
    saved = _utc()
    OS_COMM.mkdir(parents=True, exist_ok=True)
    DATA_COMM.mkdir(parents=True, exist_ok=True)
    PAGER.mkdir(parents=True, exist_ok=True)

    # Regenerate Canada pack
    subprocess.run([sys.executable, str(SCRIPTS / "generate_canada_priority_a_pack_v1.py")], check=True)
    subprocess.run([sys.executable, str(SCRIPTS / "apply_canada_brand_surface_patches_v1.py")], check=False)

    # LOCK mirrors
    pairs = [
        (PAGER / "CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md", PAGER / "CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md", "Canada Priority A Send-Ready Emails"),
        (PAGER / "CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_v2.md", PAGER / "CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md", "Canada RWA Strategy Deep Research Upgrade"),
        (PAGER / "CANADA_RWA_NAMED_ACCOUNT_TARGET_LIST_30_v1.md", PAGER / "CANADA_RWA_NAMED_ACCOUNT_TARGET_LIST_LOCKED_v1.md", "Canada RWA Named Account Target List 30"),
    ]
    for src, dest, title in pairs:
        if src.is_file():
            text = src.read_text(encoding="utf-8")
            if "**Status:** LOCKED" not in text[:500]:
                header = f"# {title} — LOCKED\n\n**Version:** 1.0.0 · **Saved:** {saved} · **Status:** LOCKED\n**Path:** `{dest}`\n\n---\n\n"
                if text.startswith("#"):
                    first_nl = text.find("\n")
                    text = header + text[first_nl + 1 :]
                else:
                    text = header + text
                text = text.replace("**Saved:** 2026-06-17T23:42:11Z", f"**Saved:** {saved} · **Status:** LOCKED", 1)
            dest.write_text(text, encoding="utf-8")
            copy2(dest, OS_COMM / dest.name)

    insight = portfolio_insight_plan()
    insight_paths = [
        PAGER / "PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md",
        OS_COMM / "PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md",
    ]
    for p in insight_paths:
        p.write_text(insight, encoding="utf-8")

    manifest = {
        "schema": "canada-portfolio-lock-manifest-v1",
        "locked_at": saved,
        "files": [
            str(PAGER / "CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md"),
            str(PAGER / "CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md"),
            str(PAGER / "CANADA_RWA_NAMED_ACCOUNT_TARGET_LIST_LOCKED_v1.md"),
            str(PAGER / "PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md"),
            str(DATA_COMM / "canada-priority-a-emails-v1.json"),
            str(DATA_COMM / "canada-brand-routing-v1.json"),
        ],
        "implementation": {
            "trustfield": str(Path.home() / "Desktop/TrustField Technologies/templates/compliance.html"),
            "noetfield": [
                str(Path.home() / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield/bank-pilot/index.html"),
                str(Path.home() / "Desktop/Noetfield/Noetfield-All-Documents/Noetfield/copilot/index.html"),
            ],
            "sourcea": [
                "data/commercial/canada-priority-a-emails-v1.json",
                "os/commercial/PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md",
            ],
            "witnessbc": "witnessbc-commercial-film-ship.sh · witnessbc-site/dist/",
            "seven77": "The 777 Foundation/web · partners/settlement-bc",
            "witnessbc_routing_json": "data/commercial/witnessbc-portfolio-routing-v1.json",
            "seven77_routing_json": "data/commercial/seven77-portfolio-routing-v1.json",
        },
        "brands": ["SourceA", "WitnessBC", "777Foundation", "TrustField", "Noetfield"],
    }
    manifest_path = DATA_COMM / "canada-portfolio-lock-manifest-v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "locked_at": saved, "manifest": str(manifest_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
