# WitnessBC Live Proof — Agentic Governance Market Scan (June 2026)

**Saved:** 2026-06-15T21:32:29Z · **Retrofit:** doc-datetime-law batch retrofit
**Schema:** `witnessbc-market-scan-v1`  
**Generated:** 2026-06-15  
**Scope:** ~40 vendors in tiers · live demo patterns · v9 Proof Lab mapping  
**Brand law:** witnessbc.com ≠ witness.ai —  names for internal research only; not on customer pages.

---

## Executive summary

Buyers evaluating agentic governance in 2026 expect **runtime enforcement at dispatch**, not post-hoc logs. Top vendors converge on: proxy/gateway interception, YAML or declarative policy packs, ALLOW / DENY / APPROVAL verdicts, and **verifiable evidence** (signed receipts, replay, tamper detection). WitnessBC v9 Proof Lab implements this engagement pattern in-browser without naming  on-site.

---

## Tier 1 — Runtime enforcement + live proof (dispatch gate)

| Vendor | Pattern | Live demo style |
|--------|---------|-----------------|
| Navil | Rust MCP/CLI proxy · YAML policy at install | Browser live demo + `navil policy test` fixtures |
| Execlave | SDK + enforcement between agent and world | In-browser dashboard stream · sub-20ms gate |
| Strix | Execution control · Ed25519 receipts | Live verifiable receipt counter · npm quickstart |
| Apotheon (THEMIS) | Zero-trust governance runtime · Merkle evidence | Whitepaper + runtime overlay narrative |
| TrueFoundry | Agent Gateway · VPC-native orchestration | Gateway sandbox · policy on tool calls |

---

## Tier 2 — Discovery + governance platform (ADG / registry)

| Vendor | Pattern | Live demo style |
|--------|---------|-----------------|
| Arthur | Agent Discovery & Governance (ADG) | Book demo · runtime guardrails + eval |
| Credo AI | Agent registry · policy packs · EU AI Act | Governance Knowledge Graph · workflow layer |
| Holistic AI | Risk + compliance automation | Enterprise demo · policy templates |
| OneTrust | AI governance module | Trust center · assessment workflows |
| IBM watsonx.governance | Model + agent lifecycle | Enterprise trial · integration story |
| Microsoft Purview | DLP + AI hub | Tenant demo · Copilot governance |
| Google Cloud Model Armor | Safety filters at API | Console sandbox |
| AWS Bedrock Guardrails | Content + topic filters | AWS console demo |

---

## Tier 3 — Security / CASB / API gateway extensions

| Vendor | Pattern | Live demo style |
|--------|---------|-----------------|
| Palo Alto Prisma AIRS | AI security posture | Briefing + lab |
| Zscaler | AI security in SSE | PoC environment |
| CrowdStrike Charlotte AI | Agent + endpoint narrative | Falcon demo |
| Lakera | Prompt injection / guardrails API | API playground |
| Robust Intelligence | AI firewall | Trial + integration |
| HiddenLayer | Model / agent security | Enterprise PoC |
| Protect AI | MLSecOps | Assessment demo |

---

## Tier 4 — Observability + eval (often paired with Tier 1)

| Vendor | Pattern | Live demo style |
|--------|---------|-----------------|
| LangSmith | Trace + eval for agents | Free tier traces |
| Arize | ML + LLM observability | Phoenix open source |
| Weights & Biases | Experiment + eval | W&B Weave |
| Braintrust | Eval + scoring | Sandbox projects |
| Galileo | Agent eval metrics | Product demo |
| Patronus AI | Automated eval | API trial |

---

## Tier 5 — Open source / framework-native

| Project | Pattern | Live demo style |
|---------|---------|-----------------|
| LangGraph | Graph checkpoints · human-in-loop | Local notebooks |
| CrewAI | Multi-agent crews | CLI + docs |
| AutoGen | Agent conversations | GitHub examples |
| OpenAI Agents SDK | Tool use + handoffs | API playground |
| Anthropic MCP | Tool protocol standard | MCP server demos |

---

## Live demo patterns (2026 best practice)

| Pattern | Why it converts | WitnessBC v9 implementation |
|---------|-----------------|------------------------------|
| **Interactive terminal replay** | Shows policy-before-action, not slides | Typewriter terminal · step scrubber · 6 gate markers |
| **Verdict triad ALLOW/BLOCK/ESCALATE** | Maps to buyer mental model | Scenario cards color-coded · aria-live verdict |
| **Tamper-FAIL moment** | Proves crypto integrity vs log editing | Tamper demo button · receipt JSON mutation · shake animation |
| **Evidence on disk** | Audit / GRC language | Artifact cards · hash copy · bundle download |
| **Progress / exploration gamification** | Increases time-on-page | localStorage "Scenarios explored N/6" |
| **Hero → proof bridge** | Zero friction from marketing to proof | Control-plane row click · stats chips · verdict ticker |
| **Deep links** | Shareable sales moments | `#scenario=outbound` etc. |
| **Reduced motion respect** | Enterprise accessibility | `prefers-reduced-motion` disables autoplay |

---

## What v9 ships (WitnessBC)

1. **JSON SSOT** — `proof-scenarios-v1.json` with 6 scenarios (outbound, tool, publish, pii-leak, mcp-escalate, tamper)
2. **Proof Lab layout** — 3-column desktop grid · evidence-on-disk section
3. **Engagement stack** — play/pause · scrubber · progress tracker · glassmorphism terminal
4. **Home bridge** — clickable control plane · scenario chips under stats · cycling ticker
5. **Deploy** — JSON copied to `dist/deploy/data/` · validate gate ≥ 5 scenarios

---

## Sources (research pass)

- Navil.ai — live demo + policy test CLI (June 2026)
- Execlave.com — browser dashboard stream
- Strixgov.com — Ed25519 receipt verification narrative
- Apotheon.ai — Governance Runtime whitepaper (THEMIS)
- Arthur.ai — Best AI Governance Platforms 2026 column
- Gartner / McKinsey agentic AI governance citations (via witnessbc-site sources.json)

---

*Internal research attachment — not for customer-facing paste.*
