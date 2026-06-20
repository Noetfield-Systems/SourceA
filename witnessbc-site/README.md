# Witness AI Site v3

**Standalone commercial site** for [witnessbc.com](https://witnessbc.com) — runtime governance infrastructure with AI policy at dispatch.

## Layout

```
witnessbc-site/
├── index.html              Single page (light/dark theme toggle)
├── dark.html               Redirect stub → index.html
├── data/
│   ├── references.json     Citations SSOT (10 refs + crosswalk metadata)
│   ├── pages.json          Multi-page manifest
│   ├── cta.json            Proof mailto + live demo URL SSOT
│   ├── cohort.json         Founding Shadow Cohort SSOT
│   └── proof-scenarios-v1.json  Live proof scenarios SSOT (v8.1)
├── assets/
│   ├── tokens.css          Design tokens (light + dark)
│   ├── styles.css          Component styles
│   ├── favicon.svg         Site favicon
│   ├── og-card.svg         Social preview card
│   ├── control-plane.js    Live hero panel animation
│   ├── site.js             Nav, theme, sticky CTA, loop stepper
│   └── proof-demo.js       Interactive proof terminal + scenarios
├── dist/
│   └── witnessbc-site-v1.html   Single-file send bundle
├── scripts/
│   ├── run-recipe.sh       Canonical run recipe (inject · validate · receipt)
│   ├── build.py            Inline CSS/JS + inject refs → dist
│   ├── inject_refs.py      Regenerate footer from references.json
│   ├── validate.sh         Brand + structure gate
│   ├── deploy_witnessbc_v1.sh  Stage dist/deploy/ (+ optional wrangler)
│   └── serve.sh            Run recipe + local :8090
├── open.sh                 cwd-safe browser open
└── README.md
```

## Commands (run recipe)

**Canonical one command** — inject refs · validate · build · sync · receipt:

```bash
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh --open    # + browser
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh --serve   # + :8090
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh --json    # receipt stdout
```

Receipt: `~/.sina/witnessbc-site-run-receipt-v1.json`

Individual steps (if debugging):

```bash
python3 witnessbc-site/scripts/build.py --json   # rebuild bundle + inject refs
bash witnessbc-site/scripts/validate.sh          # brand + structure gate
bash ~/Desktop/SourceA/witnessbc-site/open.sh    # run recipe + open
bash witnessbc-site/scripts/serve.sh             # run recipe + http://127.0.0.1:8090
```

## v3.1 polish

- Skip link · focus-visible · scroll-padding for sticky header
- Logo mark + SVG theme toggle icons
- Section eyebrows (Platform · Loop · Proof · Compare · Policy)
- Capability detail bullets · architecture label · matrix caption
- Proof terminal title bar · scenario-synced label
- **Motion layer** — `assets/motion.css` hero entrance, shimmer, float, chip/button/card interactions
- Evidence card hover · crosswalk zebra rows · control plane glow

- **References SSOT** — `data/references.json` drives footer `#ref-1`–`#ref-10`; build validates citation integrity
- **Framework crosswalk** — collapsible table mapping Witness AI gates to NIST, ISO, EU AI Act, OWASP, MITRE ATLAS, NIST GenAI Profile
- **Architecture diagram** — dispatch path (ALLOW / ESCALATE / BLOCK) in Platform section
- **Autonomy tiers** — L0 observe · L1 policy gates · L2 human-in-loop
- **Live control plane** — cycling roster verdicts in hero panel (respects reduced motion)
- **Proof scenarios** — Outbound send · Tool call · Publish pills with step-synced chain highlight
- **Integrations strip** — MCP, HTTP, OpenTelemetry, YAML policy packs, SIEM export (generic, no vendor names)

## Phase A — deploy + conversion (2026-06-15)

- **CTA SSOT** — `data/cta.json` drives proof mailto, live demo URL, toolkits link (injected at assemble)
- **Brand disambiguation** — header bar: Witness AI on witnessbc.com ≠ WitnessAI (witness.ai)
- **Proof bridge** — live demo CTA on proof.html page-hero + mailto on all proof paths
- **Deploy artifact** — `dist/deploy/` (9 HTML + assets) via `scripts/deploy_witnessbc_v1.sh`

## Deploy (no paid Cloudflare)

**Default — free only:**

```bash
python3 scripts/publish_witnessbc_landing_v1.py --backend tunnel   # free trycloudflare
python3 scripts/publish_witnessbc_landing_v1.py --backend local    # 127.0.0.1:8090 only
bash witnessbc-site/scripts/run-recipe.sh --serve
```

**Optional (requires CF token — skip if avoiding paid Cloudflare):**

```bash
bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --wrangler
```

Receipt: `~/.sina/witnessbc-site-deploy-receipt-v1.json`

## v8 100-grade upgrade (2026-06-15)

- **Live trust signals** — `data/trust-signals.json` + `inject_trust_signals_v1.py` · `assets/trust-signals.js` on home
- **Breadcrumbs** — `partials/breadcrumb.html` on all sub-pages
- **Control plane density** — Compact / Detailed toggle with receipt codes per agent row
- **W1 film wired** — `w1-demo.mp4` primary · live demo iframe fallback · five-beat aside on proof
- **Commercial short bridge** — `commercial_short_url` in `cta.json` until film ships
- **Deploy coexistence** — `dist/deploy/_redirects` clean URLs · `_routes.json` excludes `/toolkits` + `/principles`
- **Validate v8** — trust bar · breadcrumbs · deploy routes · optional `lighthouse_witnessbc_v1.sh`

```bash
python3 witnessbc-site/scripts/inject_trust_signals_v1.py --json
bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --wrangler
bash witnessbc-site/scripts/lighthouse_witnessbc_v1.sh http://127.0.0.1:8090/
```

Phased ship: **v8.0** local PASS · **v8.1** live proof JSON + evidence panel · **v8.2** wrangler deploy witnessbc.com · trust dimension 8→10 (customer logos when approved).

## v8.1 live proof upgrade (2026-06-15)

- **Scenarios SSOT** — `data/proof-scenarios-v1.json` · 6 scenarios (outbound ESCALATE · tool BLOCK · publish ALLOW · PII leak BLOCK · MCP ESCALATE · tamper FAIL)
- **Live proof terminal** — `assets/proof-demo.js` loads JSON · typewriter receipt · scenario pills · `#scenario=` deep-links
- **Evidence panel** — policy excerpt · signed hash · timestamp · verdict badge beside terminal
- **Replay mode** — prev/next step through chain · step counter
- **Tamper demo** — button mutates receipt → tamper-FAIL · aria-live verdict
- **Evidence cards grid** — artifact hashes below terminal · JSON bundle download
- **Home hero ticker** — cycling verdict strip → `proof.html#scenario=X`
- **Deploy inject** — `dist/deploy/data/proof-scenarios-v1.json` · embedded JSON in assembled proof.html
- **Validate v8.1** — `bash scripts/validate.sh` → PASS v8.1 live-proof

```bash
bash witnessbc-site/scripts/run-recipe.sh --serve   # http://127.0.0.1:8090/
bash witnessbc-site/scripts/run-recipe.sh --json
```

Research: `archive/attachments/commercial/WITNESSBC_LIVE_PROOF_MARKET_TOP100_2026-06-15_v1.md`

## v9 Proof Lab (2026-06-15)

- **3-column proof lab** — scenario cards (left) · terminal + gate scrubber + play/pause (center) · evidence drawer with copy-hash (right)
- **JSON SSOT fully wired** — 6 scenarios from `proof-scenarios-v1.json` · embedded at assemble · fetch fallback · deploy copy
- **Engagement** — localStorage progress tracker · tamper shake · glassmorphism terminal · stats scenario chips · clickable control-plane rows
- **Deep links** — `proof.html#scenario=outbound|tool|publish|pii-leak|mcp-escalate|tamper`
- **Validate v9** — `bash scripts/run-recipe.sh --json` until PASS

## v7 high-grade upgrade (2026-06-15)

- **Founding Shadow Cohort** — `data/cohort.json` SSOT · scarcity band on home + pricing
- **Pricing conversion** — Flow/Ops CTAs → proof mailto · deposit SOW micro-copy
- **Lane router** — Witness AI Flow vs Noetfield NF-RD on pricing + FAQ
- **Diligence strip** — `policy.html#diligence` procurement checklist (no SOC2 claim)
- **Platform integrations** — `#integrations` quickstart + YAML snippet · WBC-COMPLEMENT card
- **W1 film slot** — `#w1-demo-film` on proof.html · fallback to interactive terminal
- **Send bundles** — `dist/witnessbc-site-{proof|pricing|faq}-v1.html` via `build.py`
- **Validate v7** — `bash scripts/validate.sh` · optional `scripts/lighthouse_witnessbc_v1.sh`

```bash
python3 witnessbc-site/scripts/build.py --page proof --json
python3 witnessbc-site/scripts/build.py --page pricing --json
bash witnessbc-site/scripts/lighthouse_witnessbc_v1.sh http://127.0.0.1:8090/
```

Outbound attach: WBC-FLOW → proof bundle · pricing page → pricing bundle · NW1 → Noetfield attach (separate lane).

## v5 UI upgrade (2026-06-15)

- **Trust layer** — shadow / metadata-only / fail-closed pills · framework alignment strip · cohort label
- **Hero polish** — category line · buyer chips · Zenity-style CTA order · stat count-up
- **Proof page** — film-strip autoplay · segmented scenario pills · aria-live verdict
- **Responsive** — compare matrix cards · lifecycle scroll-snap · mobile hero stack · mobile CTA bar
- **Pricing** — Flow tier elevation · deposit micro-copy
- **Dark mode** — WCAG AA contrast pass on matrix · crosswalk · proof terminal

### Motion budget

- One hero entrance (`.reveal-on-scroll` on first viewport)
- One hover transition per card type (evidence · explore · price)
- Control-plane glow pulse only (respects `prefers-reduced-motion`)
- Stat count-up and film-strip autoplay **disabled** when reduced motion is on
- No infinite scroll parallax

## Theme toggle

- Header sun/moon button switches `data-theme="light|dark"` on `<html>`
- Preference persisted in `localStorage` key `witness-ai-theme`

## Page structure (10 sections)

1. Hero — split copy + live governance control plane
2. Trust — cited evidence (deduped), framework badges, crosswalk table
3. Why — three problem cards (SVG icons)
4. Platform — architecture diagram + autonomy tiers + Observe · Govern · Prove
5. Governance loop — horizontal stepper
6. Proof — scenario pills + interactive receipt terminal
7. Compare — feature matrix
8. AI policy — chip grid + integrations strip
9. Pricing — tier cards + feature table
10. FAQ — demo CTA block

References `#ref-1`–`#ref-10` in footer **Sources** collapsible panel.

## Brand

- **Witness AI** only — no third-party competitor names on customer pages
- Framework badges are **alignment maps only** — not certification

## Output paths

| Artifact | Path |
|----------|------|
| Source | `witnessbc-site/index.html` |
| Bundled | `witnessbc-site/dist/witnessbc-site-v1.html` |
| Deploy | `witnessbc-site/dist/deploy/` |
| Send copy | `~/.sina/witnessbc-site-v1.html` |
| Archive | `archive/attachments/commercial/witnessbc-site-v1.html` |
