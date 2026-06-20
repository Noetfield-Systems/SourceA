#!/usr/bin/env python3
"""Founder Agents Window use guide — 100-task catalog, wanted reminders, hub payload."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / ".sina" / "founder-agent-guide"
STATE_PATH = ROOT / "state.json"
from governance_paths_v1 import (
    FOUNDER_AGENT_USE_GUIDE as LAW_PATH,
    FOUNDER_SAVE_AND_LOCK as SAVE_LOCK_LAW,
)

# ASF priority picks — Noetfield credibility stack
FOUNDER_PRIORITY_IDS = frozenset({1, 5, 10, 22, 35, 66, 86, 94, 96, 100, 93})

CATEGORIES: list[tuple[str, str, list[str]]] = [
    ("setup", "Setup & scaffolding", [
        "Bootstrap Next.js/Astro/React app with folder structure, linting, and README",
        "Convert test-repo into commercial marketing site from pitch docs",
        "Add package.json, scripts, and dev dependencies for chosen stack",
        "Set up monorepo layout (apps/, packages/, shared config)",
        "Initialize git, .gitignore, first commit, branch strategy",
        "Create Docker + docker-compose for local dev",
        "Scaffold API + frontend in one pass with shared types",
        "Generate env template (.env.example) from codebase usage",
        "Add CI workflow (GitHub Actions) for lint, test, build",
        "Create project docs: architecture, runbook, onboarding guide",
    ]),
    ("explore", "Codebase exploration", [
        "Map entire repo: what does this project do and where is X?",
        "Trace auth flow from login UI to database",
        "Find all API endpoints and document them",
        "Identify dead code and unused dependencies",
        "Compare two folders/repos and summarize differences",
        "Explain a 500-line file in plain English with a diagram",
        "Find where a bug likely lives from an error message",
        "Audit how secrets/env vars are loaded",
        "List all external integrations (Stripe, Supabase, etc.)",
        "Build a dependency graph of modules",
    ]),
    ("feature", "Feature implementation", [
        "Add user authentication (login, signup, session, protected routes)",
        "Build contact form with validation + email/API hookup",
        "Add dark mode across entire app",
        "Implement search with filters and pagination",
        "Add file upload to S3/Supabase Storage",
        "Create admin dashboard with CRUD for a resource",
        "Add Stripe checkout for pricing page",
        "Implement role-based access control (admin vs user)",
        "Add i18n (multi-language) support",
        "Build notification system (email or in-app)",
        "Add real-time updates with WebSockets or Supabase Realtime",
        "Create PDF/export for reports",
        "Add OAuth (Google/GitHub login)",
        "Implement webhook receiver + signature verification",
        "Build onboarding wizard for new users",
    ]),
    ("refactor", "Refactoring & cleanup", [
        "Rename a function/type across the whole codebase safely",
        "Migrate JavaScript → TypeScript file-by-file",
        "Split a god-file into modules with correct imports",
        "Replace deprecated API/library with modern equivalent",
        "Standardize error handling pattern project-wide",
        "Extract shared components from duplicated UI",
        "Move from pages router → app router (Next.js)",
        "Consolidate duplicate API client code",
        "Apply consistent naming (files, components, hooks)",
        "Remove any types and tighten TypeScript",
    ]),
    ("bugs", "Bug fixing & debugging", [
        "Fix failing tests and explain root cause",
        "Debug works locally, fails in prod from logs",
        "Fix CORS, 401, 500 errors from stack traces",
        "Resolve build failures after dependency upgrade",
        "Fix memory leak or slow query from symptoms",
        "Patch security issue (XSS, SQL injection pattern)",
        "Fix mobile layout breakage across pages",
        "Repair broken git merge conflicts",
        "Fix flaky CI (timing, env, cache)",
        "Diagnose cannot find module / path alias issues",
    ]),
    ("testing", "Testing & quality", [
        "Add unit tests for untested critical functions",
        "Add integration tests for API routes",
        "Add E2E tests (Playwright/Cypress) for main user flows",
        "Raise test coverage for a module to target %",
        "Add snapshot tests for UI components",
        "Set up pre-commit hooks (lint + format + test)",
        "Add ESLint/Prettier config and fix all violations",
        "Run accessibility audit and fix top issues",
        "Add load test script for an endpoint",
        "Create test fixtures and seed data scripts",
    ]),
    ("git", "Git, GitHub & delivery", [
        "Create feature branch, implement, commit with good messages",
        "Open pull request with summary + test plan",
        "Split one big change into multiple reviewable PRs",
        "Respond to PR review comments with code fixes",
        "Investigate failing CI check on a PR",
        "Write changelog for a release",
        "Tag version and draft release notes",
        "Rebase/fix branch that diverged from main",
        "Cherry-pick a fix onto another branch",
        "Set up branch protection + required checks docs",
    ]),
    ("database", "Database & backend", [
        "Design Postgres schema from product requirements",
        "Write Supabase migrations + RLS policies",
        "Add indexes for slow queries",
        "Seed database with realistic demo data",
        "Build REST or GraphQL API for new resources",
        "Add rate limiting and input validation middleware",
        "Implement audit log / event ledger table",
        "Set up background jobs (cron, queue)",
        "Migrate data from JSON/CSV into DB",
        "Add backup/restore documentation and scripts",
    ]),
    ("devops", "DevOps & deployment", [
        "Deploy app to Vercel/Railway with env vars",
        "Configure custom domain + DNS checklist",
        "Set up staging vs production environments",
        "Add health check endpoint + monitoring hooks",
        "Write deploy runbook (smoke tests after deploy)",
        "Fix Docker build that fails in CI",
        "Configure CDN/cache headers for static assets",
    ]),
    ("research", "Research, content & business", [
        " analysis doc from live market research",
        "Turn pitch deck bullets into website copy (Home, Product, Pricing)",
        "Generate privacy policy / terms draft structure (not legal advice)",
        "Build pricing page from commercial ladder ($10K / $50K / $120K)",
        "Create sales one-pager from product docs",
        "Notion: create tasks from spec page and track implementation",
        "Figma: generate diagram for architecture or user flow",
        "Full credibility v1 ship: marketing site + contact CTA + deploy + git — live URL",
    ]),
]

EDITOR_WINS = [
    "Changing one line you already see",
    "Tweaking CSS pixel-by-pixel while looking at the screen",
    "Stepping through a debugger breakpoint-by-breakpoint",
    "Renaming one variable in one file",
    "Pasting a snippet you already have",
]

PRIORITY_STACK = [
    {"rank": 1, "task_ids": [10, 94, 96, 100], "outcome": "Live marketing site with GEL/pricing story"},
    {"rank": 2, "task_ids": [1, 5, 66, 86], "outcome": "Real repo + git + deploy on noetfield.com"},
    {"rank": 3, "task_ids": [22, 35], "outcome": "Contact/demo CTA that captures leads"},
    {"rank": 4, "task_ids": [93], "outcome": " positioning doc"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_catalog() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    n = 0
    for cat_id, cat_title, titles in CATEGORIES:
        for title in titles:
            n += 1
            tasks.append(
                {
                    "id": n,
                    "code": f"AW-{n:03d}",
                    "title": title,
                    "category": cat_id,
                    "category_title": cat_title,
                    "use_agent_window": True,
                    "founder_priority": n in FOUNDER_PRIORITY_IDS,
                    "agent_prompt": f"Do task {n} — {title}",
                }
            )
    return tasks


CATALOG: list[dict[str, Any]] = _build_catalog()


def _ensure_dir() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)


def _read_state() -> dict[str, Any]:
    _ensure_dir()
    if not STATE_PATH.exists():
        return {"wanted_ids": list(FOUNDER_PRIORITY_IDS), "done_ids": [], "updated_at": _now()}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"wanted_ids": [], "done_ids": [], "updated_at": _now()}


def _write_state(state: dict[str, Any]) -> None:
    _ensure_dir()
    state["updated_at"] = _now()
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _task_by_id(tid: int) -> dict[str, Any] | None:
    for t in CATALOG:
        if t["id"] == tid:
            return t
    return None


def reminder_payload(hub: dict[str, Any] | None = None) -> dict[str, Any]:
    """What founder should do in Agents Window now."""
    state = _read_state()
    wanted = [i for i in state.get("wanted_ids", []) if i not in state.get("done_ids", [])]
    wanted_tasks = [_task_by_id(i) for i in wanted]
    wanted_tasks = [t for t in wanted_tasks if t]

    # Rank: priority stack order, then numeric id
    def rank(t: dict) -> tuple:
        pr = 99
        for row in PRIORITY_STACK:
            if t["id"] in row["task_ids"]:
                pr = row["rank"]
                break
        return (pr, t["id"])

    wanted_tasks.sort(key=rank)
    do_now = wanted_tasks[0] if wanted_tasks else None

    brief_parts = []
    if do_now:
        brief_parts.append(f"Agents Window — do task {do_now['id']}: {do_now['title'][:60]}")
        brief_parts.append(f"Copy: {do_now['agent_prompt']}")
    else:
        brief_parts.append("Mark tasks Wanted on Agents Window tab — hub will remind you.")

    return {
        "do_now": do_now,
        "wanted_count": len(wanted_tasks),
        "wanted_tasks": wanted_tasks[:10],
        "brief": " · ".join(brief_parts),
        "open_cursor": "Cursor → Agents (Agents Window) — not inline Editor chat",
        "computed_at": _now(),
    }


def guide_payload(hub: dict[str, Any] | None = None) -> dict[str, Any]:
    state = _read_state()
    done = set(state.get("done_ids", []))
    wanted = set(state.get("wanted_ids", [])) - done
    by_category: dict[str, list] = {}
    for t in CATALOG:
        st = "done" if t["id"] in done else ("wanted" if t["id"] in wanted else "catalog")
        row = {**t, "status": st}
        by_category.setdefault(t["category"], []).append(row)

    rem = reminder_payload(hub)
    return {
        "ok": True,
        "law_path": LAW_PATH.name,
        "save_lock_law": SAVE_LOCK_LAW.name,
        "total_tasks": len(CATALOG),
        "wanted_count": rem["wanted_count"],
        "done_count": len(done),
        "founder_priority_count": len(FOUNDER_PRIORITY_IDS),
        "catalog": CATALOG,
        "by_category": by_category,
        "categories": [{"id": c[0], "title": c[1], "count": len(c[2])} for c in CATEGORIES],
        "editor_wins": EDITOR_WINS,
        "priority_stack": PRIORITY_STACK,
        "comparison": {
            "editor_better": EDITOR_WINS,
            "agent_window_better": "Multi-step · cross-file · research→build→test · tool chains",
        },
        "reminder": rem,
        "invoke_examples": [
            "Do task 100 — ship credibility v1 for Noetfield using noetfeld-os docs.",
            "Do tasks 1, 5, 94, 96, 22, 86 in order.",
        ],
        "hub_tab": "agent-window",
        "updated_at": _now(),
    }


def handle_action(body: dict[str, Any], hub: dict[str, Any] | None = None) -> dict[str, Any]:
    action = (body.get("action") or "list").strip().lower()
    if action == "list":
        return guide_payload(hub)

    state = _read_state()
    wanted = list(state.get("wanted_ids", []))
    done = list(state.get("done_ids", []))

    if action == "want":
        tid = int(body.get("id") or body.get("task_id") or 0)
        if not _task_by_id(tid):
            return {"ok": False, "error": f"unknown task id: {tid}"}
        if tid not in wanted:
            wanted.append(tid)
        state["wanted_ids"] = wanted
        _write_state(state)
        return {"ok": True, "payload": guide_payload(hub)}

    if action == "unwant":
        tid = int(body.get("id") or 0)
        state["wanted_ids"] = [i for i in wanted if i != tid]
        _write_state(state)
        return {"ok": True, "payload": guide_payload(hub)}

    if action == "done":
        tid = int(body.get("id") or 0)
        if tid not in done:
            done.append(tid)
        state["done_ids"] = done
        state["wanted_ids"] = [i for i in wanted if i != tid]
        _write_state(state)
        return {"ok": True, "payload": guide_payload(hub)}

    if action == "reset_priorities":
        state["wanted_ids"] = list(FOUNDER_PRIORITY_IDS)
        _write_state(state)
        return {"ok": True, "payload": guide_payload(hub)}

    return {"ok": False, "error": f"unknown action: {action}"}


if __name__ == "__main__":
    p = guide_payload()
    print(json.dumps({"total": p["total_tasks"], "wanted": p["wanted_count"], "brief": p["reminder"]["brief"]}, indent=2))
