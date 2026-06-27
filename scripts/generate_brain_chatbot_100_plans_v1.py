#!/usr/bin/env python3
"""Generate SourceA Brain chatbot 100-plan SSOT (10 phases × 10 plans).

Adapted from Noetfield CHAT-P blueprint + SourceA brain_intelligence_v3 as-built audit.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "data" / "brain-chatbot-100-plans-v1.json"
OUT_MD = ROOT / "brain-os" / "plan-registry" / "SOURCEA_BRAIN_CHATBOT_100_PLAN_LOCKED_v1.md"
OUT_DOC = ROOT / "docs" / "BRAIN_CHATBOT_100_PLANS_REGISTRY_LOCKED_v1.md"

PHASES = [
    {
        "phase": 1,
        "title": "Knowledge corpus (foundation)",
        "plans": [
            ("01", "Corpus manifest SSOT", "Single manifest listing every allowed public source, lane, hash, and distill path.", "data/CHATBOT_KNOWLEDGE_MANIFEST.json", "shipped", "P0", "scripts/validate-sourcea-brain-knowledge-v1.sh"),
            ("02", "Public copy ingest", "Export positioning JSON, founder-home, and locked positioning law into chunked markdown.", "scripts/distill_www_to_brain_knowledge_v1.py · data/chatbot-knowledge/manual/", "shipped", "P0", None),
            ("03", "FAQ pack", "Distill live FAQ / scenario / offer pages into Q/A pairs with canonical www_url metadata.", "data/chatbot-knowledge/distilled/faq-live.md", "todo", "P1", None),
            ("04", "API surface ingest", "Ingest public developer pages, kernel docs, and OpenAPI slice for procedural answers.", "sites/SourceA-landing/green-unified/eval · data/chatbot-knowledge/distilled/developer-tools.md", "in_progress", "P1", None),
            ("05", "Public rules guardrail snippets", "Distill brain-public-rules-v1.json into rule lane chunks — retrieved, not prompt-dumped.", "data/brain-public-rules-v1.json · scripts/distill_brain_public_rules_v1.py", "shipped", "P0", None),
            ("06", "llms.txt + sitemap sync", "Auto-regenerate llms.txt and sitemap brain summary from manifest on corpus rebuild.", "sites/SourceA-landing/green-unified/llms.txt", "todo", "P2", None),
            ("07", "Forbidden corpus denylist", "Machine gate blocking brain-os/, Mac ports, secrets, GTM internals from distill.", "data/brain-public-data-allowlist-v1.json · data/brain-chat-public-docs-allowlist-v1.json", "shipped", "P0", None),
            ("08", "Chunk strategy", "400–800 token target chunks with lane, page, updated_at, content_hash, www_url.", "scripts/sync_brain_chat_knowledge_v1.py", "shipped", "P0", None),
            ("09", "Corpus rebuild on deploy", "Hook brain_chatbot_refresh_v1.sh into publish_sourcea_landing_v1.py and worker deploy.", "scripts/brain_chatbot_refresh_v1.sh · scripts/publish_sourcea_landing_v1.py", "shipped", "P0", None),
            ("10", "Verify gate", "Coverage + no-leak verify before deploy; disk bundle matches live worker.", "scripts/validate-sourcea-brain-knowledge-v1.sh", "shipped", "P0", "scripts/validate-sourcea-brain-knowledge-v1.sh"),
        ],
    },
    {
        "phase": 2,
        "title": "Vector index & retrieval",
        "plans": [
            ("01", "Embedding provider", "Semantic-hash vector provider runs in Worker without extra API bill or secrets.", "cloud/workers/sourcea-brain-chat-v1/src/retrieval.js", "shipped", "P1", None),
            ("02", "Vector store", "Bundle exposes vector metadata; Worker projects chunks at runtime with semantic_hash_v1.", "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json", "shipped", "P1", None),
            ("03", "Hybrid BM25 + vector merge", "BM25 + page boost + semantic vector score merged in Worker ranking.", "cloud/workers/sourcea-brain-chat-v1/src/retrieval.js", "shipped", "P1", None),
            ("04", "Retriever service", "Shared retrieve() API in Python hub + JS worker with identical ranking semantics.", "scripts/brain_retrieval_engine_v1.py · retrieval.js", "shipped", "P0", "bash scripts/brain_cli_v1.sh search"),
            ("05", "Page-aware boost", "Widget sends page_path and data-sa-page; boost chunks matching current route.", "sites/SourceA-landing/green-unified/sourcea-chatbot.js · retrieval.js", "shipped", "P0", None),
            ("06", "Intent routing buckets", "sandbox/pricing/API/compliance/contact/developer/investor pre-retrieve lane boost.", "scripts/brain_retrieval_engine_v1.py classify_intent", "in_progress", "P1", None),
            ("07", "Citation objects", "Return {source, url, excerpt, lane, score, kind} on every answer.", "cloud/workers/sourcea-brain-chat-v1/src/index.js", "shipped", "P0", None),
            ("08", "Stale chunk detection", "Flag chunks older than SITE_BUILD_ID or freshness_sla_hours from manifest.", "data/CHATBOT_KNOWLEDGE_MANIFEST.json freshness_sla_hours", "todo", "P2", None),
            ("09", "Re-index cron", "Nightly Railway/cloud CI refresh + worker redeploy without Mac founder validators.", "scripts/brain_chatbot_refresh_v1.sh", "todo", "P1", None),
            ("10", "Retrieval eval set — 50 golden", "Expand brain-chat-eval-canonical-v1.json to 50 questions from FAQ + sales one-pager.", "data/brain-chat-eval-canonical-v1.json · scripts/test_brain_chat_quality_v1.py", "in_progress", "P0", "python3 scripts/test_brain_chat_quality_v1.py --json"),
        ],
    },
    {
        "phase": 3,
        "title": "LLM orchestration (replace hardcode)",
        "plans": [
            ("01", "ChatBrain service", "Replace any keyword branches with retrieve→assemble→generate pipeline.", "cloud/workers/sourcea-brain-chat-v1/src/index.js · scripts/brain_intelligence_pipeline_v1.py", "shipped", "P0", None),
            ("02", "System prompt lock", "Minimal BRAIN_CORE only; all product truth injected per turn from retrieval.", "docs/BRAIN_INTELLIGENCE_PIPELINE_LOCKED_v1.md · retrieval.js BRAIN_CORE", "shipped", "P0", None),
            ("03", "Provider adapter", "OpenRouter primary with model fallback chain; env OPENROUTER_MODEL.", "cloud/workers/sourcea-brain-chat-v1/src/index.js", "shipped", "P0", None),
            ("04", "Fallback ladder", "LLM down → retrieval-only template answer → static offline hint.", "cloud/workers/sourcea-brain-chat-v1/src/guardrails.js", "shipped", "P1", None),
            ("05", "History window", "Last 12 turns worker-side; widget keeps 20; context budget ~4K tokens retrieved.", "sourcea-chatbot.js · index.js MAX_HISTORY", "shipped", "P0", None),
            ("06", "Dynamic chip generator", "LLM or intent engine suggests 3 chips per reply instead of static chip list.", "sites/SourceA-landing/green-unified/sourcea-chatbot.js", "todo", "P2", None),
            ("07", "Streaming SSE", "POST /api/brain/chat/v1/stream for first-token latency on widget.", "cloud/workers/sourcea-brain-chat-v1/src/index.js", "todo", "P1", None),
            ("08", "Token + cost logging", "Log prompt/completion tokens per session in metadata_json receipt.", "cloud/workers/sourcea-brain-chat-v1 · Supabase or KV", "todo", "P2", None),
            ("09", "Rate limit + Turnstile", "Session + IP limits; Turnstile on abuse patterns for public widget.", "cloud/workers/sourcea-brain-chat-v1", "todo", "P1", None),
            ("10", "Feature flag BRAIN_RAG_LEGACY", "Shadow legacy toggle for A/B; default RAG-on after verify green.", "data/sourcea-brain-chat-config-v1.json", "todo", "P2", None),
        ],
    },
    {
        "phase": 4,
        "title": "Guardrails & compliance (public-safe)",
        "plans": [
            ("01", "Pre-filter input", "Block legal advice, custody/compliance filing, and internal ops requests.", "scripts/brain_chat_input_filter_v1.py", "todo", "P1", None),
            ("02", "Post-filter positioning CI", "Run forbidden phrase + must-not-lead-price scan on every generated reply.", "scripts/verify_brain_reply_positioning_v1.py · guardrails.js", "shipped", "P0", "bash scripts/verify_brain_guardrails_v1.sh"),
            ("03", "Forbidden phrase scanner", "Same boundaries as public rules + anti-ICP eval forbidden_any lists.", "data/brain-public-rules-v1.json · brain-chat-eval-canonical-v1.json", "in_progress", "P0", None),
            ("04", "Agentic-first CTA law", "Primary CTAs: Forge Terminal, /start, pricing — not book-a-call first.", "data/brain-public-rules-v1.json · sourcea-positioning-v1.json", "shipped", "P0", None),
            ("05", "No invitation law", "Cal.com proof-demo only on escalation; max one demo link per reply.", "sourcea-chatbot.js · brain-public-rules one-demo-link", "in_progress", "P0", None),
            ("06", "Confidence gate UI", "Low retrieval confidence → honest deferral + route link, not hallucination.", "sourcea-chatbot.js · worker confidence object", "shipped", "P0", None),
            ("07", "Human escalate contact", "Interested buyer → /start or intake prefill, not auto-founder email.", "sites/SourceA-landing/green-unified/start", "todo", "P1", None),
            ("08", "CASL-safe chat", "No unsolicited email capture; feedback opt-in only.", "sourcea-chatbot.js · Site Pulse", "shipped", "P1", None),
            ("09", "Audit trail chunk IDs", "Log retrieved chunk_id list per reply in receipt + optional platform store.", "sync_brain_chat_knowledge_v1.py chunk ids · worker receipt", "todo", "P1", None),
            ("10", "verify_brain_guardrails.sh", "Machine gate in CI: pre/post filters + positioning smoke on live worker.", "scripts/verify_brain_guardrails_v1.sh", "shipped", "P0", "bash scripts/verify_brain_guardrails_v1.sh"),
        ],
    },
    {
        "phase": 5,
        "title": "Live product context (read-only tools)",
        "plans": [
            ("01", "Tool: boot-proof snapshot", "Read /sourcea/data/boot-proof.json for live proof availability answers.", "cloud/workers/sourcea-brain-chat-v1/src/live-tools.js", "shipped", "P1", None),
            ("02", "Tool: products catalog", "Live read sourcea-products-catalog-v1.json at query time for public product truth.", "cloud/workers/sourcea-brain-chat-v1/src/live-tools.js", "shipped", "P1", None),
            ("03", "Tool: factories catalog", "Live factories list with /sourcea/factories links — never deny when catalog exists.", "cloud/workers/sourcea-brain-chat-v1/src/live-tools.js", "shipped", "P0", None),
            ("04", "Tool: pricing tiers", "Route to current public pricing page with Build/Rent/Own explanation; no invented dollar amounts.", "cloud/workers/sourcea-brain-chat-v1/src/live-tools.js", "shipped", "P0", None),
            ("05", "Tool: site map resolver", "Resolve 'where is X?' to manifest www_url or site-map chunk.", "data/chatbot-knowledge/manual/site-map.md", "todo", "P1", None),
            ("06", "Forge Terminal live probe", "HEAD check sourcea.app/sourcea/forge/terminal before claiming demo is up.", "scripts/brain_tool_forge_terminal_probe_v1.py", "todo", "P1", None),
            ("07", "Tool: positioning JSON live", "Fetch positioning-v1.json cache for greet/one-line consistency checks.", "data/sourcea-positioning-v1.json", "todo", "P2", None),
            ("08", "Tool registry allowlist", "os/chat_tools_v1.json listing read-only tools Brain may call.", "data/brain-chat-tools-v1.json", "todo", "P1", None),
            ("09", "Read-only enforcement", "No POST/PATCH from chat except anonymous feedback/intake endpoints.", "cloud/workers/sourcea-brain-chat-v1", "shipped", "P0", None),
            ("10", "Tool eval — 20 live questions", "Golden set requiring live JSON/tool answers not static corpus alone.", "data/brain-chat-tool-eval-v1.json", "todo", "P1", None),
        ],
    },
    {
        "phase": 6,
        "title": "Conversation quality & memory",
        "plans": [
            ("01", "Session summary compress", "Summarize history after 20 turns to stay inside context budget.", "cloud/workers/sourcea-brain-chat-v1/src/index.js", "todo", "P2", None),
            ("02", "Clarifying questions", "Ask one follow-up when intent ambiguous and confidence low.", "retrieval.js · BRAIN_CORE", "todo", "P1", None),
            ("03", "Multi-turn /start guide", "Step user through sandbox intake when they ask how to begin.", "data/chatbot-knowledge/distilled/sandbox-freemium.md", "todo", "P1", None),
            ("04", "Developer mode", "Detect curl/OpenAPI/kernel questions → recipe and /eval links.", "data/chatbot-knowledge/distilled/developer-tools.md", "in_progress", "P1", None),
            ("05", "Agency operator mode", "Agency QBR / deliverable audit vocabulary from public scenario copy.", "sites/SourceA-landing/green-unified/scenario.html", "todo", "P2", None),
            ("06", "Investor mode routing", "Route /showcase?track=investor and investors chunk; no confidential data.", "data/chatbot-knowledge · investors lane", "todo", "P2", None),
            ("07", "Language EN-CA default", "Canadian English default; FR stub deferred for procurement.", "sourcea-chatbot.js", "shipped", "P2", None),
            ("08", "Widget ARIA + keyboard", "Audit Brain panel for focus trap, aria-live, and keyboard send.", "sourcea-chatbot.js · sourcea.css", "todo", "P1", None),
            ("09", "Offline graceful degrade", "Worker+LLM down → cached FAQ chips + Forge Terminal link.", "sourcea-chatbot.js hint_offline", "in_progress", "P1", None),
            ("10", "Golden transcript tests", "30 multi-turn pytest/playwright scenarios in cloud CI.", "scripts/test_brain_chat_transcripts_v1.py", "todo", "P1", None),
        ],
    },
    {
        "phase": 7,
        "title": "Admin, analytics & learning loop",
        "plans": [
            ("01", "Admin chat logs tab", "Surface anonymized Brain sessions in Hub admin (read-only).", "agent-control-panel", "todo", "P2", None),
            ("02", "Thumbs up/down", "Per-reply feedback wired to Site Pulse + gap queue.", "sourcea-site-pulse · sourcea-chatbot.js", "todo", "P1", None),
            ("03", "Gap queue", "Low-score / failed eval sessions → founder review CSV.", "data/brain-chat-gap-queue-v1.json", "todo", "P1", None),
            ("04", "Site Pulse brain metrics", "Track brain_chat starts, citation clicks, Forge Terminal CTR.", "sourcea-site-pulse-v1.js", "in_progress", "P1", None),
            ("05", "Founder alert mirror", "Optional Telegram on first high-intent message (defer Hub ASK).", "deferred", "deferred", "P2", None),
            ("06", "Weekly corpus diff report", "New/changed www pages → re-index reminder artifact.", "scripts/brain_corpus_diff_report_v1.py", "todo", "P2", None),
            ("07", "A/B retrieval metrics", "Compare page-boost vs baseline on /start click-through.", "data/brain-chat-ab-v1.json", "todo", "P2", None),
            ("08", "Search Console → FAQ", "Top search queries feed new FAQ chunks in manifest.", "data/CHATBOT_KNOWLEDGE_MANIFEST.json", "todo", "P2", None),
            ("09", "llms.txt auto-update", "Corpus summary paragraph regenerated on each refresh.", "sites/SourceA-landing/green-unified/llms.txt", "todo", "P2", None),
            ("10", "Weekly analytics JSON", "reports/analytics/brain-weekly-v1.json dashboard feed.", "receipts/brain-analytics/", "todo", "P2", None),
        ],
    },
    {
        "phase": 8,
        "title": "Commercial intelligence (SourceA buyers)",
        "plans": [
            ("01", "Agency wedge vocabulary", "Ingest public agency/SME positioning only — no internal GTM matrix.", "data/chatbot-knowledge/distilled/intelligence-lane.md", "todo", "P2", None),
            ("02", "Build vs Rent vs Own explainer", "Explain tiers without hero dollar anchors; scope-first language.", "pricing-matrix.md · brain-public-rules no-lead-price", "shipped", "P0", None),
            ("03", "Forge handoff explainer", "Homepage vs Forge Terminal vs platform sign-in state machine.", "forge-runtime.md · eval forge-vs-homepage", "shipped", "P0", None),
            ("04", "Proof/receipt framing", "Evidence for buyers — not regulatory filing or compliance SKU claims.", "trust-ledger-public.md · brain-public-rules", "shipped", "P0", None),
            ("05", "Competitor-safe answers", "Categories only; never named peer trash-talk in corpus or replies.", "brain-public-rules forbidden-public", "shipped", "P1", None),
            ("06", "Objection handling playbook", "Public chunks for 'just records', 'we have Cursor', 'too expensive'.", "data/chatbot-knowledge/manual/objections-public.md", "todo", "P1", None),
            ("07", "DEMO async path", "Forge Terminal browser demo before Cal.com; DEMO keyword → terminal URL.", "sourcea-chatbot.js · forge/terminal.html", "in_progress", "P0", None),
            ("08", "Qualification intent tags", "Log agency/founder/developer intent tags without PII.", "Site Pulse metadata", "todo", "P2", None),
            ("09", "Handoff to intake form", "Structured /start prefill from chat context (no auto-email).", "sites/SourceA-landing/green-unified/start", "todo", "P1", None),
            ("10", "Outbound policy sync", "Same boundary language as public outreach policy docs in rules lane.", "data/brain-public-rules-v1.json", "in_progress", "P1", None),
        ],
    },
    {
        "phase": 9,
        "title": "Multi-channel parity",
        "plans": [
            ("01", "Shared brain module", "One retrieval+generate path for web widget and hub Python fallback.", "scripts/sourcea_brain_chat_v1.py · worker", "shipped", "P0", None),
            ("02", "Hub ASK same backend", "Route Hub ASK tab through same worker URL and bundle version.", "scripts/sourcea_brain_chat_v1.py", "todo", "P2", None),
            ("03", "n8n webhook ask", "External agents call worker with shared auth secret (read-only).", "cloud/workers/sourcea-brain-chat-v1", "todo", "P2", None),
            ("04", "Forge Terminal product mode", "forge_terminal product uses same RAG + sectioned reply format.", "sourcea-forge-terminal-demo.js · index.js", "shipped", "P0", None),
            ("05", "Email async defer", "Do not auto-reply outreach; link to Brain on www.", "deferred", "deferred", "P2", None),
            ("06", "Widget rollout audit", "Document which pages mount sourcea-chatbot.js vs Forge-only.", "sites/SourceA-landing/green-unified", "shipped", "P1", None),
            ("07", "Embeddable snippet defer", "Partner white-label widget defer until P0 eval green.", "deferred", "deferred", "P2", None),
            ("08", "Voice defer", "Text-first per phase1-sales-truth.", "deferred", "deferred", "P2", None),
            ("09", "Internal Slack ops defer", "Ops channel internal only — not public Brain.", "deferred", "deferred", "P2", None),
            ("10", "verify_chat_channels.sh", "Smoke all channels hit same bundle_version and citation schema.", "scripts/verify_brain_chat_channels_v1.sh", "todo", "P1", None),
        ],
    },
    {
        "phase": 10,
        "title": "Production hardening & north star",
        "plans": [
            ("01", "Prod deploy RAG always-on", "Worker + landing publish pipeline documented and automated.", "scripts/brain_cli_v1.sh deploy", "shipped", "P0", "bash scripts/brain_cli_v1.sh deploy"),
            ("02", "Latency SLO streaming", "p95 first token < 3s with SSE; full reply < 8s.", "cloud/workers/sourcea-brain-chat-v1", "todo", "P1", None),
            ("03", "Cache hot FAQs at build", "Embed top 20 question answers in bundle pinned chunks.", "sync_brain_chat_knowledge_v1.py pinned", "todo", "P2", None),
            ("04", "DR rebuild < 5 min", "git pull → brain_chatbot_refresh → wrangler deploy runbook.", "docs/CHATBOT_KNOWLEDGE_RUNBOOK.md", "shipped", "P1", None),
            ("05", "Prompt injection suite", "Red-team tests for corpus escape and secret exfil attempts.", "scripts/test_brain_prompt_injection_v1.py", "todo", "P1", None),
            ("06", "Privacy page disclosure", "Chat logging + OpenRouter processor disclosure on /trust.", "sites/SourceA-landing/green-unified/trust", "todo", "P1", None),
            ("07", "SEO FAQ schema", "Inject FAQPage JSON-LD from same corpus as Brain.", "scripts/build_sourcea_vercel_output_v1.py", "todo", "P2", None),
            ("08", "AI search citation", "Structured answers + llms.txt for Google/Perplexity.", "llms.txt · brain citations", "todo", "P2", None),
            ("09", "Machine verify stack", "validate-sourcea-brain-* scripts in cloud CI machines index.", "scripts/validate-sourcea-brain-landing-e2e-v1.sh", "in_progress", "P0", None),
            ("10", "North star metric", "Forge Terminal demo click within 24h of first Brain chat session.", "Site Pulse · brain-weekly analytics", "todo", "P1", None),
        ],
    },
]

STATUS_MAP = {
    "shipped": "done",
    "in_progress": "in_progress",
    "todo": "planned",
    "deferred": "deferred",
}


def build_plans() -> list[dict]:
    plans: list[dict] = []
    for ph in PHASES:
        pnum = ph["phase"]
        for seq, title, summary, paths, status, priority, verify in ph["plans"]:
            pid = f"BRAIN-P{pnum}-{seq}"
            path_list = [p.strip() for p in paths.split(" · ") if p.strip()]
            plans.append(
                {
                    "id": pid,
                    "phase": pnum,
                    "phase_title": ph["title"],
                    "seq": int(seq),
                    "title": title,
                    "summary": summary,
                    "paths": path_list,
                    "status": status,
                    "progress": STATUS_MAP.get(status, "planned"),
                    "priority": priority,
                    "verify": verify,
                    "depends_on": [],
                    "acceptance": f"{title} verified on sourcea.app Brain stack.",
                }
            )
    return plans


def tier_counts(plans: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {"P0": 0, "P1": 0, "P2": 0}
    for p in plans:
        counts[p["priority"]] = counts.get(p["priority"], 0) + 1
    return counts


def progress_summary(plans: list[dict]) -> dict:
    by_progress: dict[str, int] = {}
    for p in plans:
        by_progress[p["progress"]] = by_progress.get(p["progress"], 0) + 1
    done = by_progress.get("done", 0)
    return {
        "total": len(plans),
        "done": done,
        "in_progress": by_progress.get("in_progress", 0),
        "planned": by_progress.get("planned", 0),
        "deferred": by_progress.get("deferred", 0),
        "pct": round(100 * done / len(plans), 1) if plans else 0,
    }


def critical_path(plans: list[dict]) -> list[str]:
    return [p["id"] for p in plans if p["priority"] == "P0" and p["progress"] != "done"][:15]


def render_md(plans: list[dict], doc: dict) -> str:
    lines = [
        "# SourceA Brain chatbot — 10 phases · 100 plans (LOCKED v1)",
        "",
        f"**Saved:** {doc['saved_at']}  ",
        "**Adapted from:** Noetfield CHAT-P blueprint + SourceA brain_intelligence_v3 audit  ",
        f"**Machine SSOT:** `{doc['ssot_json']}`  ",
        f"**Manifest:** `data/CHATBOT_KNOWLEDGE_MANIFEST.json`  ",
        f"**Progress:** {doc['progress']['done']}/{doc['progress']['total']} done ({doc['progress']['pct']}%)  ",
        "",
        "---",
        "",
    ]
    current_phase = None
    for p in plans:
        if p["phase"] != current_phase:
            current_phase = p["phase"]
            lines.append(f"## Phase {current_phase} — {p['phase_title']}")
            lines.append("")
            lines.append("| ID | Plan | Status | Priority |")
            lines.append("|----|------|--------|----------|")
        status_badge = p["status"].upper().replace("_", " ")
        lines.append(f"| {p['id']} | {p['title']} | {status_badge} | {p['priority']} |")
        if p["seq"] == 10:
            lines.append("")
    lines.extend(
        [
            "---",
            "",
            "## Exit criteria",
            "",
            "Public Brain answers **Forge Terminal**, **pricing**, **homepage vs Forge**, **try without install**, and **Cursor path** with citations at **90%+ P0 eval** — parity with public pages only.",
            "",
            "## Commands",
            "",
            "```bash",
            "python3 scripts/generate_brain_chatbot_100_plans_v1.py",
            "bash scripts/validate-brain-chatbot-100-plans-v1.sh",
            "bash scripts/brain_cli_v1.sh deploy",
            "python3 scripts/test_brain_chat_quality_v1.py --write-report --json",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def render_doc(plans: list[dict], doc: dict) -> str:
    lines = [
        "# Brain chatbot 100 plans registry (LOCKED v1)",
        "",
        f"**Saved:** {doc['saved_at']}  ",
        f"**SSOT JSON:** `{doc['ssot_json']}`  ",
        "",
        "## Summary",
        "",
        f"- **Total plans:** {doc['progress']['total']}",
        f"- **Shipped:** {doc['progress']['done']}",
        f"- **In progress:** {doc['progress']['in_progress']}",
        f"- **Planned:** {doc['progress']['planned']}",
        f"- **Deferred:** {doc['progress']['deferred']}",
        f"- **P0 remaining on critical path:** {len(doc['critical_path'])}",
        "",
        "## Critical path (P0 not done)",
        "",
    ]
    for pid in doc["critical_path"]:
        p = next(x for x in plans if x["id"] == pid)
        lines.append(f"- **{pid}** — {p['title']}")
    lines.extend(
        [
            "",
            "## Recommended 30-day waves",
            "",
            "| Week | Plans | Goal |",
            "|------|-------|------|",
            "| 1 | BRAIN-P1-09, P2-05, P2-10, P4-02, P4-06 | Deploy hook + page boost + 50 eval + guardrails |",
            "| 2 | BRAIN-P2-01–03, P3-04, P5-03–04 | Vector hybrid + live pricing/factories tools |",
            "| 3 | BRAIN-P3-07, P4-10, P6-08–10 | Streaming + guardrail CI + a11y/transcripts |",
            "| 4 | BRAIN-P5-01–02, P7-02–03, P10-02, P10-10 | Live tools + feedback loop + north star |",
            "",
            "## Regenerate",
            "",
            "```bash",
            "python3 scripts/generate_brain_chatbot_100_plans_v1.py",
            "bash scripts/validate-brain-chatbot-100-plans-v1.sh",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    plans = build_plans()
    assert len(plans) == 100, f"expected 100 plans, got {len(plans)}"

    doc = {
        "schema": "sourcea-brain-chatbot-100-plans-v1",
        "version": "1.0.0",
        "saved_at": now,
        "law": "100 shippable units for sourcea.app Brain — retrieval-first, not keyword chatbot.",
        "adapted_from": "Noetfield CHAT-P blueprint + SourceA brain_intelligence_v3",
        "ssot_json": "data/brain-chatbot-100-plans-v1.json",
        "human_doc": "brain-os/plan-registry/SOURCEA_BRAIN_CHATBOT_100_PLAN_LOCKED_v1.md",
        "registry_doc": "docs/BRAIN_CHATBOT_100_PLANS_REGISTRY_LOCKED_v1.md",
        "manifest": "data/CHATBOT_KNOWLEDGE_MANIFEST.json",
        "validator": "scripts/validate-brain-chatbot-100-plans-v1.sh",
        "generator": "scripts/generate_brain_chatbot_100_plans_v1.py",
        "cross_ref": {
            "gap_report": "docs/BRAIN_CHATBOT_GAP_REPORT_LOCKED_v1.md",
            "pipeline": "docs/BRAIN_INTELLIGENCE_PIPELINE_LOCKED_v1.md",
            "eval": "data/brain-chat-eval-canonical-v1.json",
            "rules": "data/brain-public-rules-v1.json",
        },
        "tier_counts": tier_counts(plans),
        "progress": progress_summary(plans),
        "critical_path": critical_path(plans),
        "phases": [
            {"phase": ph["phase"], "title": ph["title"], "plan_ids": [f"BRAIN-P{ph['phase']}-{s[0]}" for s in ph["plans"]]}
            for ph in PHASES
        ],
        "plans": plans,
    }

    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(plans, doc), encoding="utf-8")
    OUT_DOC.write_text(render_doc(plans, doc), encoding="utf-8")
    print(json.dumps({"ok": True, "path": str(OUT_JSON), "progress": doc["progress"]}, indent=2))


if __name__ == "__main__":
    main()
