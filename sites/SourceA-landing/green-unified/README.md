# SourceA green-unified landing (canonical)

**Execution Proof Infrastructure** — 12-page commercial site for Agent Run `:5180`.

## Layout

```
SourceA-landing/green-unified/
├── index.html              Home — reference · team · growth · sandbox
├── platform.html           Platform story
├── team.html               Agentic business team + command center
├── growth.html             Growth flywheel + pipeline console
├── scenario.html           Council sandbox theater
├── proof.html              Verification + demo script
├── compare.html            Category matrix
├── pricing.html            SKUs
├── loops/
│   ├── index.html          Loops hub
│   ├── outreach.html
│   ├── ops-monitor.html
│   └── research.html
├── sourcea.css             Styles + motion polish
├── sourcea-motion.js       Interactions · orbit · growth console
├── scripts/
│   ├── run-recipe.sh       Canonical run recipe
│   ├── serve.sh            Run recipe + serve hint
│   └── open.sh             (symlink via ../open.sh)
└── open.sh                 cwd-safe browser open
```

## Commands (run recipe)

**Preflight (step 1):** both deploy roots must exist before sync/deploy (auto-linked from YA5 if needed):

```bash
bash ~/Desktop/SourceA/scripts/bootstrap_sourcea_desktop_deploy_v1.sh
test -d ~/Desktop/SA4 && test -d ~/Desktop/agentrun-app
```

**Canonical one command** — sync nav/footer · deploy · validate · receipt:

```bash
bash ~/Desktop/SourceA/SourceA-landing/green-unified/scripts/run-recipe.sh
bash ~/Desktop/SourceA/SourceA-landing/green-unified/scripts/run-recipe.sh --open    # + browser
bash ~/Desktop/SourceA/SourceA-landing/green-unified/scripts/run-recipe.sh --e2e     # + Playwright (server required)
bash ~/Desktop/SourceA/SourceA-landing/green-unified/scripts/run-recipe.sh --json      # receipt stdout
```

Receipt: `~/.sina/sourcea-landing-run-receipt-v1.json`

### Full E2E (Playwright + SMART-301)

Requires **both** deploy targets and Agent Run server:

```bash
test -d ~/Desktop/SA4 && test -d ~/Desktop/agentrun-app
cd ~/Desktop/agentrun-app && ./serve.sh   # :5180 in another terminal
bash ~/Desktop/SourceA/SourceA-landing/green-unified/scripts/run-recipe.sh --e2e --json
```

E2E asserts (among others):

- Mock UI: `.sa-buyer-toggle`, `.sa-chain-beats` (6), `.sa-mock-panel`, CTA band copy
- **SMART-301:** `[data-trust-valid-yes]` shows `N/1000` (not `—`) on index · platform · proof · security · status
- Live console tab switch on home hero
- Static crawl includes `status.html`, trust JSON, and deploy sync for trust/live JS

Or standalone:

```bash
bash ~/Desktop/SourceA/scripts/validate-sourcea-landing-e2e-v1.sh
```

### Individual steps (debugging)

```bash
python3 scripts/sync_sourcea_landing_pages_v1.py      # nav · footer · explore sync
python3 scripts/deploy_sourcea_desktop_landing_v1.py    # → agentrun-app + SA4
bash scripts/validate-sourcea-desktop-landing-v1.sh   # 12-page disk gate
```

### UI upgrade (no downgrade — agents)

Before editing HTML/CSS/JS under `green-unified/`, prove you hold the current version:

```bash
python3 scripts/ui_upgrade_baseline_guard_v1.py baseline --json
python3 scripts/ui_upgrade_baseline_guard_v1.py check --path "SourceA-landing/green-unified/index.html" --json
bash scripts/validate-ui-upgrade-no-downgrade-v1.sh
bash SourceA-landing/green-unified/scripts/run-recipe.sh --e2e
```

Law: `brain-os/law/enforcement/SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md` · baseline SSOT: `data/ui-upgrade-baseline-v1.json`

## Live URLs

| Surface | URL |
|---------|-----|
| **Canonical** | http://127.0.0.1:5180/sourcea/ |
| Legacy stub | http://127.0.0.1:8080/sourcea/ |

## Deploy targets

| Path | Role |
|------|------|
| `~/Desktop/agentrun-app/sourcea/` | Agent Run — full 12-page site |
| `~/Desktop/SA4/sourcea/` | AgentGo — legacy one-pager stub |
| `~/.sina/sourcea-green-unified-v1.css` | Synced CSS copy |
| `~/.sina/sourcea-green-unified-motion-v1.js` | Synced motion copy |

## Brand

- **SourceA** · hello@sourcea.com · https://sourcea.com
- No Noetfield on first touch
- Category: Execution Proof Infrastructure
