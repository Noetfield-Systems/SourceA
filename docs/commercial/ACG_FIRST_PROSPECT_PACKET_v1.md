# Agentic Cost Governance — First Prospect Packet (Draft)

Version: 1.0.0 (draft for founder review)  
Branch: preserve/acg-2026-07-05  
Commit: 68fa03c4460b1b1b60c3dc1c6bce5c266507f426

---

1) Founder-facing customer brief (one page)

Company: [Company name]
Contact: [Name, Title, Email, Phone]
Sector: [e.g., SaaS, Health Tech, Fintech]

Offer: AI Spend Leak Audit + Premium Model Firewall (pilot) — 5–7 day audit + 30-day pilot

What we do (plain): We map where AI models are used across your systems, measure token/API spend, and identify inefficient or unintended premium-model usage. We provide a prioritized findings report and a pilot policy (routing + budget caps + approval workflow) to test in one or two workflows.

High-level timeline:
- Day 0–1: Intake + scope confirmation
- Day 1–5: Audit (tool inventory, API inventory, spend surface, leakage checklist)
- Day 5–7: Policy design + pilot prep
- Day 7–37: 30-day pilot monitoring + daily snapshots
- Day 38–40: Final report + recommendations

Investment: CAD $2,000–$5,000 (scope on discovery). Pricing examples in templates are placeholders — final price set at discovery.

Non-claims note (copy to client): This audit and policy service is diagnostic and advisory only. We do not guarantee specific cost savings. Any pilot enforcement is scoped and controlled by the client; no production firewall will be enabled without explicit client approval.

---

2) Client-facing intake checklist (to send to prospect)

Please provide the following to start the AI Spend Leak Audit. If you prefer, we can run a short intake call to capture these answers.

- Company legal name:
- Primary contact (name, title, email, phone):
- Approx. org size (employees):
- Primary AI use cases (brief bullet list):
- Known vendors in use (examples): ChatGPT / OpenAI; Claude / Anthropic; Google Gemini; Llama / local models — list exact vendor & team owners
- Do you have spend invoices or API receipts we can share? (Y/N) If Y, attach last 2 months.
- Do you have any spend dashboards or billing exports? (Y/N) If Y, attach sample CSV/JSON.
- Are any AI workflows customer-facing? (Yes/No) If yes, which?
- Are there regulated data concerns (HIPAA, PII, financial, etc.)? List compliance needs.
- Who approves budget/escations? (Name + title + contact)
- Preferred pilot workflow(s) (support chatbot / code-generation / analytics / other):
- Any existing tokens/keys stored centrally (secret manager) or on dev machines? (Y/N — describe)
- Preferred timezone for kickoff call:

Output: Intake receipt (we generate audit_id and audit_scope on receipt)

---

3) AI tool inventory request (structured)

Please fill the table for each tool in use. Example fields below (CSV/JSON acceptable).

- Tool name (vendor):
- Model versions used (e.g., gpt-3.5-turbo, gpt-4, claude-3-sonnet):
- Access method (UI / API / plugin / integration):
- License/tier (Free / Plus / Team / Enterprise / pay-per-use):
- Approx. monthly cost (or best estimate):
- Typical usage pattern (ad-hoc / scheduled / continuous):
- Primary workflows using this tool:
- Number of users or seats:
- Where keys live (env var / secret manager / dev machine / CI):
- Last rotated (if known):
- Any multi-tenant usage concerns?

We will correlate this with your billing/receipts to quantify leakage and duplicate spend.

---

4) Data & security clarification questions (short)

- Do any AI workflows process regulated PHI or financial data? (Y/N — describe)
- Where are API keys stored? (e.g., AWS Secrets Manager, Vault, local env)
- Do you have RLS or dataset access controls that may affect logging? (Y/N)
- Are there retention policies for logs / transcripts? (Y/N — specify retention in days)
- Who owns incident response for AI workflows? (Name + email)
- Are dev/test environments mixed with production for AI calls? (Y/N)
- Any supplier NDAs or contractual restrictions on sharing logs with auditors? (Y/N)

Security handling: We request redacted logs where needed. We will not request customer secrets; we analyze receipts and metadata unless explicit access is approved in writing.

---

5) Audit kickoff email draft (to prospect)

Subject: AI Spend Leak Audit — next steps & intake (short)

Hi [First name],

Thanks for your interest in the AI Spend Leak Audit. To get started we need a short intake so we can scope the audit and confirm timelines. Please complete this short form (attached) or reply with a convenient time for a 20-min kickoff call.

What we'll do in the audit:
- Map your AI tool usage and costs
- Identify premium-model leakage and quick wins
- Deliver a prioritized findings report and pilot policy for one workflow

Investment: CAD $2,000–$5,000 (finalized at discovery). No production changes without your approval.

If you'd like to schedule the kickoff call now: [cal.com link placeholder]

Best,  
Sina — SourceA (proof-backed business systems)  
hello@sourcea.app

---

6) Internal delivery checklist for SourceA (worker + brain)

Pre-kickoff:
- Create audit_id and intake receipt (store in ~/.sina or receipts/)
- Confirm contact + pilot workflow
- Create client folder: receipts/acg/<audit_id>/
- Share intake with client + schedule kickoff call

During audit:
- Collect tool inventory + API receipts
- Populate spend surface map (include projected monthly)
- Run leakage checklist and escalate obvious leaks
- Generate interim findings + share read-only with client for clarification

Policy design & pilot:
- Draft routing policy (cheap-first → escalation rules). Mark model/pricing as placeholders.
- Client signs approval for pilot policy (store approval record)
- Deploy pilot to test workflows (client-controlled environment) — no production routes without client opt-in
- Start 30-day monitoring and daily spend snapshots

Closeout:
- Generate final report (include methodology, findings, estimated savings as ranges)
- Archive receipts + manifest (acg-offline-archive-manifest-v1.json)
- Offer optional implementation SOW (separate purchase)

---

7) Non-claims & audit-time placeholders (must be included in outbound and internal docs)

- Service is diagnostic and advisory only. No guaranteed savings are promised. Any savings examples are illustrative only.
- No production firewall will be activated without explicit client approval and a signed pilot scope.
- Model and pricing examples in templates are placeholders for audit-time pricing and client-specific configuration. Replace placeholders [X] at discovery.

---

8) Send-ready status

Status: DRAFT — ready for founder review. Packet exists locally on branch `preserve/acg-2026-07-05`. Do NOT push changes to remote.

Next founder action: Review packet, confirm contact details and pricing band, approve send to first prospect or request edits.

Remaining issues: None blocking for intake creation. Git divergence and broader reconcile remain deferred until founder/maintainer plan.

