#!/usr/bin/env python3
"""Restore truncated agent-control-panel/assets/app.js boot tail."""
from __future__ import annotations

import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "agent-control-panel" / "assets" / "app.js"
RECOVERED = Path("/tmp/recovered_funcs.js")
RWP = Path("/tmp/renderWorkspacePage.js")

SKIP_FUNCS = {
    "renderIncidentRoom",
    "renderConflictRoom",
    "renderIntelligence",
    "bindIntelligence",
    "bindCouncilRoom",
    "bindSystemUnified",
    "bindAgentScoreboard",
    "bindWorkspaceMirror",
    "bindWorkspaceVault",
    "renderWorkspaceMirrorPanel",
    "renderWorkspaceVaultPanel",
    "renderWorkspaceMirrorSection",
    "renderWorkspaceMirrorDocEntry",
    "hydrateWorkspaceMirrorFull",
    "scrollToWorkspaceLoop",
}

EXTRA_FUNCS = []
if RECOVERED.is_file():
    blob = RECOVERED.read_text(encoding="utf-8")
    for m in re.finditer(r"function (\w+)\(", blob):
        name = m.group(1)
        if name in SKIP_FUNCS:
            continue
        start = m.start()
        depth = 0
        end = start
        for j, ch in enumerate(blob[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        EXTRA_FUNCS.append(blob[start:end])

rwp = RWP.read_text(encoding="utf-8") if RWP.is_file() else ""
rwp = rwp.replace(
    "Only this agent — rules, private notes folder, repo, and 10-pack. Other agents have separate pages in the sidebar.",
    "This page is the app middle layer — deposit every document and log all activity in Workspace vault below. Governance, 10-round loop, submit rounds.",
)
rwp = rwp.replace(
    """      ${card("Governance & rules", `
        ${maint}
        <p class="sc-list-meta"><strong>Focus:</strong> ${esc(w.governance_focus || "")}</p>
        <p class="sc-list-meta"><strong>Thread:</strong> ${esc(w.thread || "")} · <strong>Plane:</strong> ${esc(w.plane || "")}</p>
        <p class="sc-list-meta">${esc(w.command_tabs || "")}</p>
        <p class="sc-list-meta"><strong>Cursor workspace:</strong> <code>${esc(w.cursor_workspace_hint || "")}</code></p>
        ${forb}
        ${needsList ? `<ul class="sc-loop-ws-needs">${needsList}</ul>` : ""}
      `)}

      ${activePanel}""",
    """      ${card("Governance & rules", `
        ${maint}
        <p class="sc-list-meta"><strong>Focus:</strong> ${esc(w.governance_focus || "")}</p>
        <p class="sc-list-meta"><strong>Thread:</strong> ${esc(w.thread || "")} · <strong>Plane:</strong> ${esc(w.plane || "")}</p>
        <p class="sc-list-meta">${esc(w.command_tabs || "")}</p>
        <p class="sc-list-meta"><strong>Cursor workspace:</strong> <code>${esc(w.cursor_workspace_hint || "")}</code></p>
        ${forb}
        ${needsList ? `<ul class="sc-loop-ws-needs">${needsList}</ul>` : ""}
      `)}

      ${renderWorkspaceMirrorPanel(w)}
      ${renderAgentIncidentPanel(w.incident || {}, w.label)}
      ${renderAgentConflictPanel(w.conflict || {}, w.label)}
      ${renderWorkspaceVaultPanel(w)}

      ${activePanel}""",
)

TAIL = """

  function renderAgentLoop() {
    return renderAgentLoopHub();
  }

  function bindAgentLoop() {
    const attach = (id, fn) => {
      const el = $(id);
      if (!el || el.dataset.loopBound) return;
      el.dataset.loopBound = "1";
      el.addEventListener("click", fn);
    };
    attach("btn-loop-start", async () => {
      const goal = document.getElementById("loop-goal")?.value?.trim() || "";
      const mx = Number(document.getElementById("loop-max-rounds")?.value) || 10;
      await startLoopWithGoal(goal, mx);
    });
    attach("btn-loop-cancel", async () => {
      const json = await agentLoopApi({ action: "cancel" });
      if (json.data) applyPayload(json.data);
      stopLoopPoll();
      render();
      toast(json.message || json.error || "Loop stopped", json.ok ? 4000 : 6000);
    });
    attach("btn-loop-cancel-top", async () => {
      const json = await agentLoopApi({ action: "cancel" });
      if (json.data) applyPayload(json.data);
      stopLoopPoll();
      render();
      toast(json.message || json.error || "Loop stopped", json.ok ? 4000 : 6000);
    });
    attach("btn-loop-reinject", async () => {
      const json = await agentLoopApi({ action: "reinject" });
      if (json.data) applyPayload(json.data);
      toast(json.inject?.ok ? "Sent to Cursor" : json.error || "Inject failed", 5000);
      render();
    });
    attach("btn-loop-submit", async () => {
      const summary = document.getElementById("loop-response-summary")?.value?.trim() || "";
      const body = document.getElementById("loop-response-body")?.value?.trim() || "";
      if (!body) {
        toast("Paste the Cursor answer first", 4000);
        return;
      }
      const json = await agentLoopApi({ action: "response", summary, body, trigger_source: "app" });
      if (json.data) applyPayload(json.data);
      if (json.ok && data().agentLoop?.active) startLoopPoll();
      toast(json.message || json.error || (json.ok ? "Round submitted" : "Submit failed"), json.ok ? 6000 : 8000);
      render();
    });
  }

  function bindAgentWorkspaces() {
    bindWorkspaceVault();
    bindWorkspaceMirror();
    $("btn-ws-focus-loop")?.addEventListener("click", () => scrollToWorkspaceLoop());
  }

  function bindInteractions() {
    $("main")?.querySelectorAll(".sc-open-src[data-path]").forEach((el) => {
      if (el.dataset.bound) return;
      el.dataset.bound = "1";
      el.addEventListener("click", (e) => {
        e.preventDefault();
        openPath(el.dataset.path);
      });
    });
    $("main")?.querySelectorAll(".sc-open-abs[data-path], [data-open-abs]").forEach((el) => {
      if (el.dataset.bound) return;
      el.dataset.bound = "1";
      el.addEventListener("click", (e) => {
        e.preventDefault();
        openPath(el.dataset.path || el.dataset.openAbs);
      });
    });
    $("main")?.querySelectorAll(".sc-open-mono[data-path]").forEach((el) => {
      if (el.dataset.bound) return;
      el.dataset.bound = "1";
      el.addEventListener("click", () => {
        const p = el.dataset.path;
        openPath(p.startsWith("/") ? p : `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/${p}`);
      });
    });
    $("main")?.querySelectorAll(".sc-todo-done[data-todo]").forEach((btn) => {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "1";
      btn.addEventListener("click", () => todoDone(btn.dataset.todo));
    });
    if (activeTab === "audio") {
      const en = data().state.brief_text || D.brief_text || "";
      $("btn-say-en")?.addEventListener("click", () => speak(en));
      $("btn-say-fa")?.addEventListener("click", () => speak(D.brief_fa || en));
      $("btn-copy-brief")?.addEventListener("click", () => navigator.clipboard.writeText(en));
    }
  }

  function speak(text) {
    if (!window.speechSynthesis) {
      alert("Use: ~/Desktop/SourceA/scripts/sina-morning-brief.sh");
      return;
    }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.92;
    speechSynthesis.speak(u);
  }

  function render() {
    const main = $("main");
    if (!main) return;
    if (detailPage && window.SinaPages) {
      main.classList.add("sc-main--detail");
      main.innerHTML = window.SinaPages.render(detailPage, detailId, pageCtx());
      bindInteractions();
      return;
    }
    main.classList.remove("sc-main--detail");
    if (isWorkspaceTab(activeTab)) {
      const wsId = workspaceIdFromTab(activeTab);
      main.innerHTML = renderWorkspacePage(wsId);
      bindAgentLoop();
      bindAgentWorkspaces();
      paintJourney();
      bindInteractions();
      updateBriefButtonLabel();
      updateLoopSubmitSticky();
      return;
    }
    const map = {
      command: renderCommand,
      essentials: renderEssentials,
      track: renderTrack,
      "order-guardian": renderOrderGuardian,
      "agent-window": renderAgentWindow,
      backlog: renderBacklog,
      today: renderToday,
      roadmaps: renderRoadmapsGoals,
      "system-roadmap": renderSystemRoadmap,
      "decision-governance": renderDecisionGovernance,
      actions: renderActionsPage,
      "council-room": renderCouncilRoom,
      "agent-scoreboard": renderAgentScoreboard,
      "agent-loop": renderAgentLoop,
      "incident-room": renderIncidentRoom,
      "conflict-room": renderConflictRoom,
      intelligence: renderIntelligence,
      semej: renderSemej,
      "prompt-feed": renderPromptFeed,
      threads: renderThreads,
      work: renderWork,
      apps: renderApps,
      branches: renderApps,
      notes: renderNotes,
      "ai-advisory": renderAiAdvisory,
      guide: renderGuide,
      agents: renderAgents,
      repos: renderRepos,
      daily: renderDaily,
      audio: renderAudio,
      products: renderProducts,
      ecosystem: renderEcosystem,
      "personal-db": renderPersonalDb,
      orders: renderOrders,
      hq: renderHQ,
      fleet: renderFleet,
      roles: renderRoles,
      plans: renderPlans,
      "prompt-os": renderPromptOs,
      runtime: renderRuntime,
      "doc-library": renderDocLibrary,
      sources: renderSources,
    };
    const fn = map[activeTab] || renderCommand;
    main.innerHTML = typeof fn === "function" ? fn() : renderCommand();
    paintJourney();
    bindInteractions();
    if (activeTab === "track") bindTrack();
    if (activeTab === "backlog") bindBacklog();
    if (activeTab === "order-guardian") bindOrderGuardian();
    if (activeTab === "agent-scoreboard") bindAgentScoreboard();
    if (activeTab === "council-room") {
      bindCouncilRoom();
      bindSystemUnified();
    }
    if (activeTab === "intelligence") bindIntelligence();
    if (activeTab === "agent-loop") bindAgentLoop();
    updateBriefButtonLabel();
    updateLoopSubmitSticky();
  }

  function initFromUrl() {
    const p = new URLSearchParams(window.location.search);
    const tab = normalizeTab(p.get("tab") || "");
    readSrViewFromUrl();
    if (tab && (PAGE[tab] || isWorkspaceTab(tab))) go(tab);
    else if (p.get("workspace")) go(workspaceTabFromId(p.get("workspace")));
    else go("command");
    const action = p.get("action") || p.get("run");
    const launch = p.get("launch");
    if (launch || action) {
      ensureServer().then(async (ok) => {
        if (!ok) {
          toast("Hub offline — double-click Sina Command on Desktop", 6000);
          return;
        }
        if (launch) await openMiniApp(launch);
        else if (action) await runBranchAction(action);
      });
    }
  }

  async function boot() {
    await loadCommandData();
    setupAppDelegation();
    bindSitePanels();
    buildNav();
    $("meta-sync").textContent = D.built_at ? `Synced ${fmtTime(D.built_at)}` : "Loading…";
    $("btn-refresh")?.addEventListener("click", refreshFromApi);
    $("btn-refresh-hint")?.addEventListener("click", () => go("guide"));
    $("menu-btn")?.addEventListener("click", () => {
      $("sidebar").classList.add("is-open");
      $("backdrop").hidden = false;
    });
    $("backdrop")?.addEventListener("click", () => {
      $("sidebar").classList.remove("is-open");
      $("backdrop").hidden = true;
    });
    $("btn-brief-quick")?.addEventListener("click", () => copyWholeSystemBrief());
    window.addEventListener("popstate", () => {
      const q = new URLSearchParams(window.location.search);
      detailPage = q.get("page");
      detailId = q.get("id") || "";
      readSrViewFromUrl();
      ensureWorkspacePages();
      const t = normalizeTab(q.get("tab") || "");
      if (t && (PAGE[t] || isWorkspaceTab(t))) activeTab = t;
      if (q.get("workspace")) activeTab = workspaceTabFromId(q.get("workspace"));
      buildNav();
      render();
    });
    ensureServer().then((ok) => {
      if (!ok) toast("Double-click Sina Command on Desktop to start", 6000);
    });
    setInterval(() => {
      if (document.visibilityState === "visible") pingApi();
    }, 20000);
    const p = new URLSearchParams(window.location.search);
    if (p.get("tab") || p.get("workspace") || p.get("action") || p.get("launch")) initFromUrl();
    else go("command");
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
"""

src = APP.read_text(encoding="utf-8")
if src.rstrip().endswith("})();"):
    print("app.js already closed — no repair needed")
    raise SystemExit(0)

existing = set(re.findall(r"function (\w+)\(", src))
parts = [src.rstrip()]
for block in EXTRA_FUNCS:
    m = re.match(r"function (\w+)\(", block)
    if m and m.group(1) not in existing:
        parts.append(block)
        existing.add(m.group(1))

if "function renderWorkspacePage" not in existing and rwp.strip():
    parts.append(rwp.strip())

parts.append(TAIL.strip())
APP.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
print("repaired app.js — added", len(parts) - 1, "blocks, total lines", APP.read_text().count("\n"))
