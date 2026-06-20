# AI Dev Bridge + Cursor OS Pro — IDE Integration & No-Code Layer Research (June 2026)

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-06 · **Producer:** cursor-agent (Research Acquisitor class)  
**Disk SSOT:** `AI Dev Bridge OS/docs/PRODUCT_CANON.md` (UNIFIED-2.0) · `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`  
**Execution authority:** false · advise + architecture only

---

## 0. Executive summary

You already have the **correct split**:

| Product | Role | Customer |
|---------|------|----------|
| **Cursor OS Pro** | Commercial remote IDE (App Store) | Paying mobile users |
| **AI Dev Bridge** | Mac agent + wire + RUN SYSTEM moat | Internal now · enterprise later |
| **SourceA** | Governed execution engine | Infra buyers + powers portfolio |

**Upgrade path:** Do **not** merge into one blob. Upgrade into a **four-link chain** with a **no-code client shell** on top:

```text
Client (no-code workflows) → Cursor OS Pro / desk → Mac Agent :8766 → Cursor/other IDE → SourceA proof (optional)
```

**Best near-term move:** Ship **G2 physical iPhone proof** + **Cursor Extension / MCP layer** that registers your governance + RUN SYSTEM as one-click workflows inside Cursor — before chasing multi-IDE or full no-code builder.

---

## 1. What you have today (honest disk state)

### AI Dev Bridge (wire lane)

| Piece | Status | Port/path |
|-------|--------|-----------|
| Mac agent | READY | `:8766` |
| Safari desk | IDE-first UI | `desk.html` · ports 3004–3010 |
| G1 `cursor.prompt.send` | Code shipped | Device verify pending |
| G2 RUN SYSTEM | P2 shipped | Desktop PASS · **physical iPhone pending** |
| G3 Tailscale | Documented | Repeat G2 on 100.x |
| Orchestrator | SinaPromptOS spawn | No second orchestrator in `agent/` |

**Golden wire:** `RUN SYSTEM → automation.run_lane → SinaPromptOS → PASS/FAIL on phone`

### Cursor OS Pro (commercial lane)

| Piece | Status |
|-------|--------|
| Flutter mobile | ~99% reference parity target |
| IAP / TestFlight | Roadmap month 2–3 |
| Integration with wire | **Only when ASF says `integrate UI`** |

**Law:** Two Cursor chats — never mix orchestrator work into Pro chat (`CURSOR_OS_PRO_TWO_CHAT_POLICY`).

### Gap vs “integrated no-code app for clients”

| Have | Missing for client layer |
|------|--------------------------|
| Remote IDE + automation moat | **Packaged workflows** (not raw terminal) |
| Mac-local agent | **Cursor Extension** surface inside IDE |
| Internal ASF use | **Tenant / client onboarding** |
| SourceA proof on disk | **Bridge receipt** into DevBridge UI |

---

## 2. Market map — who plays at each layer (June 2026)

### Layer A — Native IDE (Cursor, VS Code, JetBrains, Windsurf)

| Player | Model | Mobile native? |
|--------|-------|----------------|
| **Cursor** | Desktop AI IDE · MCP native | **No** — bridge required |
| **VS Code** | Extension platform · Remote Tunnel | Browser mobile only |
| **Windsurf** | Agent IDE (Cognition) | No |
| **JetBrains** | IDE + AI plugins | No |
| **Replit** | **Cloud IDE** · Agent 3 | **Yes** (browser mobile) |

**Implication:** Cursor + local Mac is a **valid wedge** — but mobile requires **your bridge**, not Cursor native app.

### Layer B — Remote / mobile bridge (your category)

| Player | Approach | vs you |
|--------|----------|--------|
| **Cursor OS Pro (you)** | Phone → Mac agent → files/terminal/agent | Full IDE parity goal |
| **CursorRemote** (OSS) | CDP relay · approve agent from phone | Agent monitor only · not full IDE |
| **VS Code Tunnel + Cline** | Browser IDE + autonomous agent | DIY · not productized |
| **GitHub Codespaces** | Cloud workspace | No local Cursor |
| **Tailscale + SSH** | Raw access | No UX |

**Your differentiation:** Reference IDE **plus** RUN SYSTEM autonomy **plus** (future) SourceA receipt strip.

### Layer C — IDE extension / agent layer (integrate here)

| Player | Works in Cursor? | Model |
|--------|------------------|-------|
| **Continue.dev** | Yes · VS Code + JetBrains | Configurable AI layer · autocomplete |
| **Cline** | Yes · VS Code/Cursor/Windsurf | Autonomous agent · **SDK May 2026** |
| **Cody / Augment** | Yes | Enterprise codebase agent |
| **Cursor built-in Agent** | Native | Commodity |

**Implication:** Your **integration layer** should use **Cursor Extension API + MCP** (register servers, plugin paths) — not fight the built-in agent.

### Layer D — No-code / workflow shell (client-facing)

| Player | What “no-code” means | vs your opportunity |
|--------|----------------------|---------------------|
| **Replit Agent workflows** | Visual workflow + deploy | Cloud-only |
| **n8n / Make** | Glue automation | Not IDE-aware |
| **Vapi / Retell** | Voice workflow | Different modality |
| **Demosmith** | URL → demo video | Marketing not dev |

**Your no-code angle:** **Pre-built dev workflows** — “Run enforcement demo”, “Wire G2 smoke”, “Noetfield export bundle” — triggered from phone **without** exposing orchestrator guts.

### Layer E — Autonomous dev platforms (compete with RUN SYSTEM moat)

| Player | Funding/class | vs RUN SYSTEM |
|--------|---------------|---------------|
| **Devin / Cognition** | Autonomous engineer | Cloud sandbox · not local Cursor |
| **Factory.ai** | Agent swarms | Enterprise |
| **Sweep AI** | PR bot | Narrow |
| **Cline SDK** | Embeddable agent runtime | **Partner pattern** — embed moat |

---

## 3. Integration patterns (how to upgrade)

### Pattern 1 — **Bridge + App (current — keep)**

```text
Phone (Flutter) ──WiFi/Tailscale──► Mac Agent :8766 ──► Cursor IDE
```

**Pros:** Own the mobile SKU · App Store revenue · full local files  
**Cons:** Mac must stay on · pairing friction · Apple review  
**Best for:** Cursor OS Pro commercial line

### Pattern 2 — **Cursor Extension + MCP (add next — highest ROI)**

Cursor docs (2026): `vscode.cursor.mcp.registerServer`, `vscode.cursor.plugins.registerPath`

```text
"Sina DevBridge" extension
  ├── MCP: mac-agent (terminal.run, files, run_lane)
  ├── MCP: sourcea-proof (validate demo, export receipt)  [read-only]
  ├── Rules/skills: portfolio workflows
  └── One-click commands: "RUN SYSTEM", "Film W1 beat"
```

**Pros:** Lives **inside** Cursor where clients already work · enterprise onboarding without App Store  
**Cons:** Extension API bugs (remote MCP headers issue 2026) · Cursor-only unless duplicated  
**Best for:** **Client “layer”** — makes work easier without leaving IDE

### Pattern 3 — **Multi-IDE via Continue / Cline SDK**

| IDE | Integration path |
|-----|------------------|
| Cursor | Extension + MCP (primary) |
| VS Code | Same extension manifest |
| JetBrains | Continue.dev or Cline plugin |
| Windsurf | Cline-compatible |
| Zed | Limited · CLI fallback |

**Cline `@cline/sdk` (May 2026):** embed agent runtime in **your product** — RUN SYSTEM could call SDK instead of bespoke spawn logic long-term.

**Pros:** “We work wherever teams code”  
**Cons:** 3× QA surface · not W3-critical  
**Best for:** Phase 3 after Cursor extension proves value

### Pattern 4 — **No-code workflow shell (client UX)**

Not a new IDE — a **template layer** on top of Patterns 1–2:

| Workflow pack | User sees | Engine does |
|---------------|-----------|-------------|
| **Enforcement proof** | [Run demo] [Export receipt] | SourceA scripts + validator |
| **Wire smoke** | [Test iPhone desk] | G2 lane scripts |
| **Noetfield export** | [Generate board PDF] | NF pipeline |
| **Agent task** | [Fix failing test] | SinaPromptOS loop |

**Analog:** Replit “Agent workflows” but **local-first + governed receipts**.

---

## 4. Recommended target architecture (integrated winner)

```text
┌─────────────────────────────────────────────────────────────────┐
│ L4 CLIENT — No-code workflow packs (per lane: NF · TF · ENF)      │
│   Tap: "Run governed demo" · "Ship pilot export" · "Wire smoke"   │
├─────────────────────────────────────────────────────────────────┤
│ L3 SURFACE — Cursor OS Pro (App Store) · Safari desk · Extension │
│   Files · Terminal · Agent chat · RUN SYSTEM button              │
├─────────────────────────────────────────────────────────────────┤
│ L2 WIRE — Mac Agent :8766 (single engine)                        │
│   cursor.prompt.send · automation.run_lane · files · terminal    │
├─────────────────────────────────────────────────────────────────┤
│ L1 IDE — Cursor (primary) · VS Code/JetBrains (phase 3)          │
│   Native agent + your MCP tools                                  │
├─────────────────────────────────────────────────────────────────┤
│ L0 PROOF — SourceA spine (optional hook)                         │
│   Receipt export · validator PASS strip in workflow results      │
└─────────────────────────────────────────────────────────────────┘
```

**Commercial packaging:**

| SKU | Layer | Buyer |
|-----|-------|-------|
| **Cursor OS Pro** | L3 mobile | Prosumer devs |
| **DevBridge Team** (future) | L3–L4 extension + workflows | Startup eng teams |
| **SourceA** | L0 | Infra / platform (separate sale) |
| **Noetfield** | L4 NF pack | Compliance |

---

## 5. Scoring integration options (for your business needs)

*Scale 0–100 · weighted for: client ease, chain improvement, cost, time-to-ship, alignment with disk law*

| Option | Client ease | Chain | Cost | Time | Law fit | **Total** |
|--------|-------------|-------|------|------|---------|-----------|
| **A. Finish G2 + integrate Flutter UI** | 75 | 80 | 60 | 70 | 90 | **76** |
| **B. Cursor Extension + MCP** | 90 | 95 | 85 | 80 | 85 | **88** |
| **C. No-code workflow packs on desk** | 85 | 90 | 90 | 75 | 90 | **87** |
| **D. Cline SDK replace orchestrator** | 60 | 70 | 50 | 40 | 70 | **58** |
| **E. Cloud IDE (Replit-style)** | 70 | 50 | 30 | 30 | 40 | **45** |
| **F. Merge Pro + Wire chats now** | 40 | 50 | 70 | 60 | **20** | **42** |

**Winner combo:** **B + C in parallel after G2** · **A** for App Store · **never F** until PRODUCT_CANON integration gate.

---

## 6. How to make the chain better (concrete)

### Today’s chain (fragmented)

```text
SourceA (disk)     DevBridge (wire)     Cursor (manual)     Client (none)
     │                    │                    │                  │
   validators          desk.html            founder              —
```

### Target chain (integrated)

```text
Client tap workflow
    → Cursor OS Pro or Extension
    → Mac Agent :8766
    → cursor.prompt.send OR automation.run_lane
    → SinaPromptOS loop OR Cursor agent
    → Result + optional SourceA receipt JSON on phone
```

**Improvements:**

1. **Single pairing** — one 6-digit code powers Flutter + desk + extension discovery  
2. **Unified status** — PASS/FAIL + receipt hash on all surfaces  
3. **Workflow IDs** — `WIRE2-*`, `ENF-W1`, `NF-EXPORT` in plan catalog (already started)  
4. **Extension registers MCP** — clients never edit `mcp.json` manually  
5. **No-code packs hide** SinaPromptOS role names — client sees outcomes

---

## 7. No-code positioning (what it is / is not)

### IS

- Template buttons for repeated dev operations  
- Guardrailed agent tasks with approval gates  
- “Run my stack until green” without reading orchestrator docs  
- Portfolio-specific packs (enforcement, Copilot export, wire smoke)

### IS NOT

- Replacing Cursor for coding  
- Competing with Replit cloud IDE  
- Another general automation platform (Zapier)  
- Exposing internal multi-agent loop as v1 SKU (PRODUCT_CANON forbids)

**Client sentence:**  
> “IDE For Cursor on your phone — plus one-tap workflows that run your local stack until PASS, with proof you can export.”

---

## 8. Phased roadmap (cost-intelligent)

| Phase | Weeks | Deliverable | Cost |
|-------|-------|-------------|------|
| **P0** | 1–2 | G2 physical iPhone PASS · evidence JSON | Founder time |
| **P1** | 2–4 | Cursor OS Pro TestFlight + `integrate UI` when ASF picks | Dev time |
| **P2** | 4–8 | **Cursor Extension v0** — MCP to :8766 · 3 workflow commands | 1 engineer |
| **P3** | 8–12 | **No-code pack v1** — Enforcement + Wire smoke on desk + extension | 1 engineer |
| **P4** | 12+ | VS Code parity via Continue/Cline · enterprise tenant | Optional |

**Do not start P4 before W3 signal** unless buyer demands multi-IDE.

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Cursor API drift (CDP, MCP headers) | Prefer `.cursor/mcp.json` fallback · version pin |
| Apple rejects “remote control IDE” | Reference category precedents · clear IAP |
| Product sprawl (SourceA vs Pro vs NF) | Identity separation law per PORTFOLIO SSOT |
| W3 distraction | Extension is **post-G2** unless enterprise buyer waiting |
| Security (terminal on phone) | Pairing expiry · SAFE MODE · no clipboard hijack |

---

## 10. Golden recommendations (10)

1. **Keep two chats** until `integrate UI` — PRODUCT_CANON is correct.  
2. **Ship G2 on real iPhone** — without it, “integrated app” is theoretical.  
3. **Build Cursor Extension next** — biggest client-ease lift · stays in IDE.  
4. **MCP surface:** `terminal.run`, `run_lane`, `proof.export` — not raw orchestrator.  
5. **No-code = workflow catalog** — extend `wire-plan-library/catalog-v2.jsonl` pattern to client packs.  
6. **Optional SourceA receipt** on every RUN SYSTEM result — chain to L0 proof.  
7. **Do not rebuild Replit** — local-first + governed is the moat.  
8. **Evaluate Cline SDK** for Phase 4 orchestrator — don’t rewrite now.  
9. **Commercial:** App Store (Pro) + Team extension license (DevBridge) — two SKUs.  
10. **Parallel to W3:** Extension dev is **background** until NW1 outreach sent (energy law).

---

## 11. Peer comparison table (integration layer)

| Company | Layer | Integrated with Cursor? | No-code? | Local Mac? | Your beat |
|---------|-------|-------------------------|----------|------------|-----------|
| **You (target)** | Bridge + extension + workflows | Yes | Yes (packs) | Yes | RUN SYSTEM + proof |
| CursorRemote | CDP relay | Yes | Partial | Yes | No full IDE |
| Continue.dev | AI layer | Yes | No | Yes | No autonomy |
| Cline | Agent + SDK | Yes | Plan/Act | Yes | No mobile product |
| Replit Agent | Cloud IDE | No | Yes | No | Cloud vs local |
| Augment | Enterprise agent | Yes | No | Yes | No mobile |
| GitHub Copilot | Assistant | Yes | No | Yes | No RUN SYSTEM |

---

**Execution plan (300 steps · one doc · v2.1):** `DEVBRIDGE_EXTENSION_NO_CODE_300_STEP_PLAN_LOCKED_v1.md` §0.1 founder sequence  
**Registry:** `brain-os/plan-registry/devbridge-extension-300/REGISTRY.json` — `founder_sequence` · `anti_fragmentation`  
**Pick:** `scripts/pick-devbridge-ext-step.py --status` · `--next`

*Research v1 · ties PRODUCT_CANON UNIFIED-2.0 · PORTFOLIO SSOT v3.1 · Cursor Extension API docs 2026*
