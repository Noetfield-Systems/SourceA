# Founder — Agents Window use guide (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-06-AGENT-WINDOW-GUIDE  
**Hub tab:** `agent-window`  
**Machine catalog:** `scripts/founder_agent_use_guide.py` · `~/.sina/founder-agent-guide/`  
**Law:** `FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md`

---

## 0. One sentence

**Use the Cursor Agents Window for multi-step, cross-file, research→build→test loops; use the Editor for one precise line — the hub reminds you which task to run and gives the copy-paste agent prompt.**

---

## 1. Why Agents Window wins

| Editor is better when… | Agents Window is better when… |
|------------------------|-------------------------------|
| You know exactly what to type | You know the goal, not every step |
| One file, one change | Many files must change together |
| Full manual control | Research → build → test → fix in a loop |
| Quick typo fix | Scaffolding, migrations, refactors |
| Reading line-by-line | Exploring an unfamiliar codebase |
| One command you know | Chaining shell, git, APIs, MCP tools |
| Writing from scratch | Turning specs/docs into working code |

**Editor = keyboard. Agents Window = team member with terminal, git, search, integrations.**

---

## 2. When hub reminds you → go to Agents Window

Hub **Today** + **Agents Window** tab + **Order Guardian** show:

- Tasks you marked **Wanted**
- Priority Noetfield credibility stack (tasks 1, 5, 10, 22, 35, 66, 86, 94, 96, 100)
- Copy-paste prompt: `Do task {N} — {title}`

**Open:** Cursor → **Agents** (not inline chat in one file).

---

## 3. 100 tasks — Agents Window does better (catalog)

### Setup & scaffolding (1–10)
1. Bootstrap Next.js/Astro/React + lint + README  
2. Convert test-repo → commercial marketing site from pitch docs  
3. Add package.json, scripts, dev deps for chosen stack  
4. Monorepo layout (apps/, packages/, shared config)  
5. Initialize git, .gitignore, first commit, branch strategy  
6. Docker + docker-compose for local dev  
7. Scaffold API + frontend with shared types  
8. Generate `.env.example` from codebase usage  
9. CI workflow (GitHub Actions) lint, test, build  
10. Project docs: architecture, runbook, onboarding  

### Codebase exploration (11–20)
11. Map repo — what does it do, where is X?  
12. Trace auth flow login → database  
13. Find all API endpoints and document  
14. Dead code + unused dependencies  
15. Compare two folders/repos  
16. Explain 500-line file + diagram  
17. Find bug from error message  
18. Audit secrets/env loading  
19. List external integrations  
20. Dependency graph of modules  

### Feature implementation (21–35)
21. User auth (login, signup, session, protected routes)  
22. Contact form + validation + email/API  
23. Dark mode across app  
24. Search with filters + pagination  
25. File upload S3/Supabase Storage  
26. Admin dashboard CRUD  
27. Stripe checkout + pricing page  
28. Role-based access control  
29. i18n multi-language  
30. Notification system  
31. Real-time WebSockets / Supabase Realtime  
32. PDF/export reports  
33. OAuth Google/GitHub  
34. Webhook receiver + signature verify  
35. Onboarding wizard  

### Refactoring (36–45)
36. Rename across codebase safely  
37. JS → TypeScript migration  
38. Split god-file into modules  
39. Replace deprecated library  
40. Standardize error handling  
41. Extract shared UI components  
42. Pages router → app router  
43. Consolidate API client code  
44. Consistent naming  
45. Remove any types, tighten TS  

### Bug fixing (46–55)
46. Fix failing tests + root cause  
47. Works local, fails prod  
48. CORS, 401, 500 from stack traces  
49. Build failure after dep upgrade  
50. Memory leak / slow query  
51. Security patch XSS/SQL patterns  
52. Mobile layout breakage  
53. Git merge conflicts  
54. Flaky CI  
55. Cannot find module / path alias  

### Testing (56–65)
56. Unit tests for critical functions  
57. Integration tests API routes  
58. E2E Playwright/Cypress main flows  
59. Raise coverage to target %  
60. Snapshot UI tests  
61. Pre-commit hooks  
62. ESLint/Prettier + fix all  
63. Accessibility audit fixes  
64. Load test endpoint  
65. Test fixtures + seed scripts  

### Git & delivery (66–75)
66. Feature branch, implement, good commits  
67. Open PR summary + test plan  
68. Split big change into reviewable PRs  
69. Respond to PR review  
70. Investigate failing CI on PR  
71. Changelog for release  
72. Tag version + release notes  
73. Rebase diverged branch  
74. Cherry-pick fix  
75. Branch protection docs  

### Database & backend (76–85)
76. Design Postgres schema from requirements  
77. Supabase migrations + RLS  
78. Indexes for slow queries  
79. Seed realistic demo data  
80. REST/GraphQL API new resources  
81. Rate limiting + validation middleware  
82. Audit log / event ledger  
83. Background jobs cron/queue  
84. Migrate JSON/CSV into DB  
85. Backup/restore docs + scripts  

### DevOps (86–92)
86. Deploy Vercel/Railway + env vars  
87. Custom domain + DNS  
88. Staging vs production  
89. Health check + monitoring  
90. Deploy runbook + smoke tests  
91. Fix Docker CI build  
92. CDN/cache headers  

### Research & business (93–100)
93. Competitive analysis from live research  
94. Pitch deck → website copy (Home, Product, Pricing)  
95. Privacy/terms draft structure (not legal advice)  
96. Pricing page from commercial ladder ($10K/$50K/$120K)  
97. Sales one-pager from product docs  
98. Notion tasks from spec page  
99. Figma architecture/user-flow diagram  
100. **Credibility v1** — marketing site + contact CTA + deploy + git → live URL  

---

## 4. Editor still wins (don’t waste the agent)

- One line you already see  
- CSS pixel tweak while looking at screen  
- Debugger breakpoint-by-breakpoint  
- One variable rename in one file  
- Pasting a snippet you already have  

---

## 5. ASF priority stack (Noetfield credibility — LOCKED picks)

| Priority | Tasks | Outcome |
|----------|-------|---------|
| **1** | 10, 94, 96, 100 | Live marketing site + GEL/pricing story |
| **2** | 1, 5, 66, 86 | Real repo + git + deploy noetfield.com |
| **3** | 22, 35 | Contact/demo CTA + onboarding |
| **4** | 93 | Competitive positioning doc |

**Invoke example:** `Do task 100 — ship credibility v1 for Noetfield using noetfeld-os docs.`  
**Batch:** `Do tasks 1, 5, 94, 96, 22, 86 in order.`

---

## 6. Hub integration

| Surface | Role |
|---------|------|
| Tab `agent-window` | Full guide + wanted tasks + copy prompts |
| Today | Reminder strip when wanted tasks exist |
| Order Guardian | Cross-links agent-window vs hub-build orders |
| `POST /api/founder-agent-guide` | Mark wanted · done · list |

**LOCKED** — Maintainer updates catalog when ASF adds tasks.
