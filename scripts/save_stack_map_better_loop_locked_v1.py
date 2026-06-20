#!/usr/bin/env python3
"""LOCK stack map (future you) + Better Loop v2 · route into portfolio plans."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parents[1]
PAGER = Path.home() / "Desktop" / "1 PAGER"
OS_COMM = ROOT / "os" / "commercial"
DATA = ROOT / "data" / "commercial"
DOC = "SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md"
ROUTE_YAML = PAGER / "portfolio-300-locked" / "STACK_MAP_BETTER_LOOP_ROUTE.yaml"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def body(saved: str) -> str:
    return f"""# SourceA Stack Map (Future You) + Better Loop — LOCKED v2

**Version:** 2.0.0 · **Saved:** {saved} · **Status:** LOCKED
**Path:** `~/Desktop/SourceA/docs/{DOC}`
**Authority:** Founder · post-factory-design era · check + optimize only
**Phase:** **POST-DESIGN** — no new architecture waves; operate the loop

**Parents:**
- `docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md` (FBE · two-plane law)
- `docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md` (commercial horizons)
- `1 PAGER/PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md` (brand routing)
- `1 PAGER/PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md` (30-day plans)

---

## 0. Was the stack map locked before this file?

| Artifact | Stack map? | Better Loop? |
|----------|------------|--------------|
| FBE charter | Control vs execution plane (partial) | No |
| Business model v2 | 4-layer stack + horizons | No |
| Portfolio all-paths | Brand cross-cut mermaid | No |
| Portfolio insight plan | Four engines map | No |
| **This file** | **Full future stack map** | **Yes — operating loop** |

Chat-only diagrams are **not SSOT** until this file (and mirrors below).

---

## 1. Stack map — future you (LOCKED)

```mermaid
flowchart TB
  subgraph brands[What buyers see]
    TF[TrustField · evidence · trustfield.ca]
    NF[Noetfield · Copilot governance · noetfield.com]
    SA[SourceA · agency + factory builder · sourcea.com]
    WBC[WitnessBC · accountability]
    S77[777 · nonprofit only]
  end

  subgraph edge[Cloudflare · free edge]
    WWW[noetfield-www-proxy Worker]
    AEG[sourcea-aeg-proof Pages]
    DNS[trustfield.ca · noetfield.com zones]
  end

  subgraph fbe[SourceA FBE · cloud execution plane]
    CAT[Factory catalog SKUs]
    POL[Policy packs · pre-LLM gate]
    LED[Trust ledger · receipts]
    FLY[Fly worker · auto-stop · pending billing]
  end

  subgraph campus[PLUS ONE · product campus read-only]
    CREED[CREED refinery · 36 nodes]
    CHURCH[CHURCH assembly · 22 nodes]
  end

  subgraph mac[Mac · control plane ONLY]
    HUB[Worker Hub :13020]
    BRAIN[Brain · route · decide]
    INBOX[RUN INBOX · one sa/turn]
    GATE[Session gate · SASCIP · zero-drift]
  end

  brands --> edge
  mac --> fbe
  mac --> campus
  fbe --> campus
  edge --> brands
  GATE --> INBOX --> fbe
  fbe --> LED
```

### Layer table

| Layer | Lives | Job | Status (Jun 2026) |
|-------|-------|-----|-------------------|
| **L0 Mac control** | Hub · Brain · session gate | Spawn · approve · check · optimize | **LIVE** |
| **L1 Edge** | Cloudflare Workers/Pages | Proxy · AEG proof host | **DEPLOYED** (www proxy + aeg-proof) |
| **L2 FBE cloud** | Fly/Railway skeleton | Headless factory jobs | **BUILT** · Fly billing pending |
| **L3 Campus** | PLUS ONE / CREED / CHURCH | Refinery + assembly patterns | **READ-ONLY import** |
| **L4 Brands** | TF · NF · SA · WBC · 777 | Separate vocabulary · separate SOW | **ROUTING LOCKED** |

**Law:** Mac never runs production at scale. Mac manages platform; cloud runs factories.

---

## 2. Better Loop v1 (POST-DESIGN — LOCKED)

> Mac manages the platform · cloud runs factories · agents execute one `sa`/turn · founder approves money and messages · everything else receipts itself.

### Four auto loops

| Loop | Flow | Founder |
|------|------|---------|
| **Governance pulse** | session gate → truth bundle → queue → SASCIP → zero-drift | Nothing unless red → **hospital** |
| **Product spine** | RUN INBOX → one sa → ACT → validator → receipt | Worker chat **RUN INBOX** |
| **Commercial** | Attract → Prove → Close → Expand | Approve sends · reply · book demo |
| **Factory execution** | work order → policy gate → cloud run → receipt → sleep | Check receipt ZIP |

### Founder check card (5 min)

1. Worker Hub → Next steps — one clear row  
2. factory-now — Valid YES · drift 0  
3. RUN INBOX — one turn + receipt  
4. W3 — replies · no stuck approved_not_sent  
5. Edge — www.noetfield.com · landing proof links  

### Optimize cadence (one lever / week)

| Week | Lever |
|------|-------|
| Money | Ocree + Fundmore deposit |
| Cloud | Fly worker + MARKET_READY receipt |
| Loop | queue_sa align |
| Surface | film → book rate |
| Factory | one catalog shadow pilot |

### Stop list (loop discipline)

No new FBE waves before first deposit · no blended emails · no architecture as procrastination.

---

## 2b. Better Loop v2 — 11-step cart (BL1–BL11 · MACHINE WIRED)

**Check cart SSOT:** `~/.sina/better-loop-checkcart-v1.json`  
**Pulse:** `python3 scripts/better_loop_pulse_v1.py --json`  
**Receipt:** `~/.sina/better-loop-pulse-receipt-v1.json`  
**Live line:** `better_loop_line` on `~/.sina/agent-live-surfaces-v1.json`  
**Hub card:** `GET /api/worker-hub/v1` → `better_loop` slice

| Step | Name | Owner | Pass |
|------|------|-------|------|
| BL1 | LOCK doctrine v2 | executor | doc + mirrors synced |
| BL2 | Check cart SSOT | executor | `better-loop-checkcart-v1.json` |
| BL3 | Pulse engine | executor | `better_loop_pulse_v1.py --json` |
| BL4 | Pulse receipt | executor | mandatory loops green |
| BL5 | Live wire line | executor | `better_loop_line` on surfaces |
| BL6 | Session gate inject | executor | gate step `better_loop_pulse` |
| BL7 | Hub founder card | executor | 5 checks + weekly lever |
| BL8 | Commercial loop | commercial | W3 `approved_not_sent` surfaced |
| BL9 | Factory loop | worker | FBE bundle + Fly receipt read-only |
| BL10 | Validator | executor | `validate-better-loop-v1.sh` |
| BL11 | Ship wire W1–W10 | executor | law wire cart on lock ship |

**Weekly lever (disk):** `money` — Ocree + Fundmore send (W1 scoreboard)

**Founder path unchanged:** RUN INBOX · Hub Better Loop glance · approve money/messages only.

---

## 3. Horizon routing (from business model v2 — federated here)

| Horizon | When | Win metric |
|---------|------|------------|
| **H1 Prove it pays** | 30–60d | CAD ≥ $2K deposit + shadow pilot |
| **H2 Prove it scales** | mo 2–4 | Cloud receipt + 2–3 factory customers |
| **H3 Platform** | 2027 | NF/TF retainers + catalog maintenance ARR |

---

## 4. Disk routing index (where each piece lives)

| Topic | LOCKED path |
|-------|-------------|
| Stack map + Better Loop | `docs/{DOC}` |
| FBE engine | `docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md` |
| FBE machine bundle | `data/fbe_factory_builder_bundle_v1.json` |
| Business model horizons | `docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md` |
| Brand routing | `1 PAGER/PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md` |
| Canada W3 sends | `1 PAGER/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` |
| W3 approvals | `data/commercial/w3-canada-send-approvals-v1.json` |
| Portfolio 30-day | `1 PAGER/PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md` |
| CF www proxy code | `Noetfield/.../infra/cf-www-proxy/` |
| AEG host script | `SourceA/scripts/host_aeg_bundle_v1.py` |
| Fly deploy (free-only) | `SourceA/cloud/fly.toml` · `scripts/deploy_fbe_fly_free_v1.sh` |
| Portfolio route YAML | `1 PAGER/portfolio-300-locked/STACK_MAP_BETTER_LOOP_ROUTE.yaml` |
| Machine routing JSON | `data/commercial/stack-map-routing-v1.json` |
| Better Loop check cart | `~/.sina/better-loop-checkcart-v1.json` |
| Better Loop pulse receipt | `~/.sina/better-loop-pulse-receipt-v1.json` |
| Pulse script | `scripts/better_loop_pulse_v1.py` |
| Validator | `scripts/validate-better-loop-v1.sh` |

---

## 5. Portfolio folder routing

| Folder / plan | What to read | Action |
|---------------|--------------|--------|
| `1 PAGER/` | All LOCKED commercial + this file mirror | Strategy · sends |
| `portfolio-300-locked/W3_FIRST_QUEUE.yaml` | Ocree · Fundmore approve | Hub send |
| `portfolio-300-locked/prompts/canada-rwa/` | pf-0242–0244 | Email drafts |
| `portfolio-300-locked/prompts/sourcea/` | S-P* agency paths | Asset B loop |
| `portfolio-300-locked/prompts/trustfield/` | T-P* · TF-* | Ocree lane |
| `portfolio-300-locked/prompts/noetfield/` | N-P* · NF-RD | Fundmore lane |
| `SourceA/docs/` | FBE + stack map | Worker implementation |
| `SourceA/os/commercial/` | Mirrors for Worker INBOX | Same content |
| `~/.sina/` | Receipts · truth bundle | Session gate only |

---

## 6. 30-day Better Loop scoreboard

| Week | Auto wins | Founder optimize |
|------|-----------|------------------|
| W1 | Proxy live · landing client-language · W3 approved | **Send** Ocree + Fundmore |
| W2 | INBOX 5+ sa without paste | Follow-ups on replies |
| W3 | One cloud factory job receipt | Fly billing + deploy |
| W4 | First deposit + pilot scoped | Case study row |

---

*LOCKED v2 — Better Loop machine wired BL1–BL11 · founder check + optimize only.*
"""


def route_yaml(saved: str) -> str:
    return f"""schema: stack-map-better-loop-route-v1
saved_at: "{saved}"
phase: POST-DESIGN
authority: docs/{DOC}
better_loop_version: v2

stack_map:
  locked_doc: ~/Desktop/SourceA/docs/{DOC}
  mirrors:
    - ~/Desktop/1 PAGER/{DOC}
    - ~/Desktop/SourceA/os/commercial/{DOC}
  fbe_charter: ~/Desktop/SourceA/docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md
  business_model: ~/Desktop/1 PAGER/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md

edge_deployed:
  - name: noetfield-www-proxy
    code: ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/infra/cf-www-proxy/
    route: www.noetfield.com/*
  - name: sourcea-aeg-proof
    script: ~/Desktop/SourceA/scripts/host_aeg_bundle_v1.py

better_loop:
  version: v2
  founder_role: check_and_optimize_only
  weekly_lever: money
  daily: RUN INBOX + Hub Better Loop glance
  weekly_optimize: one_lever
  auto_loops: [governance_pulse, product_spine, commercial_flywheel, factory_execution]
  checkcart: ~/.sina/better-loop-checkcart-v1.json
  pulse_receipt: ~/.sina/better-loop-pulse-receipt-v1.json
  pulse_script: ~/Desktop/SourceA/scripts/better_loop_pulse_v1.py
  validator: ~/Desktop/SourceA/scripts/validate-better-loop-v1.sh

portfolio_routes:
  - plan: pf-0242
    folder: portfolio-300-locked/prompts/canada-rwa/
    action: W3 send queue
  - plan: pf-0243
    brand: trustfield
    account: Ocree
  - plan: pf-0244
    brand: noetfield
    account: Fundmore
  - doc: PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md
    folder: 1 PAGER/
  - doc: PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md
    folder: 1 PAGER/

stop: no_new_factory_architecture_before_first_deposit
"""


def routing_json(saved: str) -> dict:
    return {
        "schema": "stack-map-routing-v1",
        "saved_at": saved,
        "phase": "POST-DESIGN",
        "locked_doc": f"docs/{DOC}",
        "better_loop": {
            "version": "v2",
            "founder_role": "check_and_optimize_only",
            "weekly_lever": "money",
            "daily_path": "Worker chat RUN INBOX + Hub Better Loop glance",
            "checkcart": "~/.sina/better-loop-checkcart-v1.json",
            "pulse_receipt": "~/.sina/better-loop-pulse-receipt-v1.json",
            "pulse_script": "scripts/better_loop_pulse_v1.py",
            "validator": "scripts/validate-better-loop-v1.sh",
            "auto_loops": [
                "governance_pulse",
                "product_spine",
                "commercial_flywheel",
                "factory_execution",
            ],
        },
        "stack_layers": {
            "mac_control": ["Worker Hub", "Brain", "session gate", "RUN INBOX"],
            "cloudflare_edge": ["noetfield-www-proxy", "sourcea-aeg-proof"],
            "fbe_cloud": ["catalog", "policy_packs", "trust_ledger", "fly_worker_pending"],
            "plus_one_campus": ["CREED", "CHURCH"],
            "brands": ["TrustField", "Noetfield", "SourceA", "WitnessBC", "777"],
        },
        "cross_ref": {
            "fbe_charter": "docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md",
            "business_model_v2": "docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md",
            "portfolio_brands": "1 PAGER/PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md",
            "w3_approvals": "data/commercial/w3-canada-send-approvals-v1.json",
            "route_yaml": "1 PAGER/portfolio-300-locked/STACK_MAP_BETTER_LOOP_ROUTE.yaml",
        },
    }


def _append_cross_ref(path: Path, saved: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    line = f"**Stack map + Better Loop:** `docs/{DOC}` · `STACK_MAP_BETTER_LOOP_ROUTE.yaml` · `{saved}`\n"
    if "**Stack map + Better Loop:**" in text:
        text = re.sub(
            r"\*\*Stack map \+ Better Loop:\*\*[^\n]*\n",
            line,
            text,
            count=1,
        )
    elif "**Parents:**" in text[:1200]:
        text = text.replace("**Parents:**", line + "\n**Parents:**", 1)
    elif "**Law:**" in text[:1200]:
        text = text.replace("**Law:**", line + "\n**Law:**", 1)
    else:
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            text = parts[0] + "\n" + line + "\n---\n" + parts[1]
        else:
            text = line + text
    path.write_text(text, encoding="utf-8")


def main() -> int:
    saved = _utc()
    content = body(saved)
    dests = [
        ROOT / "docs" / DOC,
        PAGER / DOC,
        OS_COMM / DOC,
    ]
    for d in dests:
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(content, encoding="utf-8")

    ROUTE_YAML.parent.mkdir(parents=True, exist_ok=True)
    ROUTE_YAML.write_text(route_yaml(saved), encoding="utf-8")

    json_path = DATA / "stack-map-routing-v1.json"
    json_path.write_text(json.dumps(routing_json(saved), indent=2) + "\n", encoding="utf-8")

    for p in [
        ROOT / "docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md",
        PAGER / "SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md",
        ROOT / "docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md",
        PAGER / "PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md",
        OS_COMM / "PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md",
    ]:
        _append_cross_ref(p, saved)

    # FBE bundle pointer
    bundle = ROOT / "data/fbe_factory_builder_bundle_v1.json"
    if bundle.is_file():
        b = json.loads(bundle.read_text(encoding="utf-8"))
        b["stack_map"] = {
            "doc": f"docs/{DOC}",
            "routing_json": "data/commercial/stack-map-routing-v1.json",
            "phase": "POST-DESIGN",
            "saved_at": saved,
        }
        bundle.write_text(json.dumps(b, indent=2) + "\n", encoding="utf-8")

    manifest = DATA / "canada-portfolio-lock-manifest-v1.json"
    if manifest.is_file():
        m = json.loads(manifest.read_text(encoding="utf-8"))
        m["stack_map_better_loop"] = str(ROOT / "docs" / DOC)
        m["locked_at"] = saved
        manifest.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")

    py = sys.executable
    subprocess.run([py, str(ROOT / "scripts" / "better_loop_pulse_v1.py"), "--init-cart"], check=False)
    subprocess.run([py, str(ROOT / "scripts" / "better_loop_pulse_v1.py"), "--json"], check=False)
    subprocess.run([py, str(ROOT / "scripts" / "disk_live_wire_sync_v1.py"), "--json"], check=False)
    subprocess.run(["bash", str(ROOT / "scripts" / "validate-better-loop-v1.sh")], check=False)

    print(json.dumps({"ok": True, "saved_at": saved, "doc": [str(d) for d in dests], "route": str(ROUTE_YAML)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
