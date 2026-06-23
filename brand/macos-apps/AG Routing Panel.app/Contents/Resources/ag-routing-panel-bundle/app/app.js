(function () {
  "use strict";

  const API = window.location.origin + "/api/ag-routing-panel";
  const $ = (id) => document.getElementById(id);
  let mode = "light";
  let mermaidReady = false;

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  async function fetchJson(url, opts) {
    const r = await fetch(url, { cache: "no-store", ...(opts || {}) });
    return r.json();
  }

  async function renderMermaid(id, def) {
    const el = $(id);
    if (!el || !def || !window.mermaid) return;
    el.innerHTML = "";
    const pre = document.createElement("pre");
    pre.className = "mermaid";
    pre.textContent = def;
    el.appendChild(pre);
    try {
      if (!mermaidReady) {
        mermaid.initialize({ startOnLoad: false, theme: "dark", securityLevel: "loose" });
        mermaidReady = true;
      }
      await mermaid.run({ nodes: [pre] });
    } catch (e) {
      el.textContent = def;
    }
  }

  function renderTiers(tiers) {
    const box = $("arp-tiers");
    if (!box || !tiers) return;
    box.innerHTML = Object.entries(tiers)
      .map(([k, v]) => {
        const row = v || {};
        return (
          '<div class="arp-tier"><strong>' +
          esc(k) +
          "</strong>" +
          esc(row.where || row.model || JSON.stringify(row)) +
          "</div>"
        );
      })
      .join("");
  }

  function renderActive(active) {
    const dl = $("arp-active");
    if (!dl) return;
    const rows = [
      ["Primary", active.primary],
      ["Loop verdict", active.loop_verdict],
      ["Tick", active.tick_decision],
      ["Investigation", active.investigation_verdict],
      ["Founder action", active.founder_action],
    ];
    dl.innerHTML = rows
      .map(([k, v]) => "<dt>" + esc(k) + "</dt><dd>" + esc(v || "—") + "</dd>")
      .join("");
  }

  function renderBrands(brands) {
    const tb = $("arp-brands")?.querySelector("tbody");
    if (!tb) return;
    tb.innerHTML = (brands || [])
      .map(
        (b) =>
          "<tr><td>" +
          esc(b.if_they_say) +
          "</td><td>" +
          esc(b.route_to) +
          "</td><td>" +
          esc(b.sku) +
          "</td></tr>"
      )
      .join("");
  }

  function renderLoop(loop) {
    const ul = $("arp-loop");
    if (!ul) return;
    const items = [
      ["Observatory", loop.observatory],
      ["Investigator", loop.investigator],
      ["Judge", loop.judge],
      ["Specialist", loop.specialist],
      ["Compile order", loop.compile_order],
    ];
    ul.innerHTML = items.map(([k, v]) => "<li><strong>" + esc(k) + ":</strong> " + esc(v || "—") + "</li>").join("");
  }

  function renderTips(tips) {
    const ul = $("arp-tips");
    if (!ul) return;
    ul.innerHTML = (tips || []).map((t) => "<li>" + esc(t) + "</li>").join("");
  }

  function openApp(appId, label) {
    const term = window.SinaMainTerminal;
    const links = window.SinaOfficialLinks;
    if (term) {
      term.log("→ Agent jump: " + (label || appId));
      const link = (links?.links || []).find((l) => l.id === appId);
      if (link?.plain) term.log("  " + link.plain);
    }
    if (links?.openNativeApp?.(appId)) return;
    const row = (links?.links || []).find((l) => l.id === appId);
    if (row?.href) window.location.href = row.href;
  }

  function renderAgentGlance(glance) {
    if (!glance) return;
    const now = $("arp-glance-now");
    if (now) now.textContent = glance.factory_line || "—";
    const role = $("arp-role-hint");
    if (role) role.textContent = glance.role_hint || "";
    const q = $("arp-glance-queue");
    if (q) q.textContent = "Queue · " + (glance.queue_head || "—");
    const p = $("arp-glance-priority");
    if (p) p.textContent = glance.priority_line ? "Priority · " + glance.priority_line : "Priority · daily stack";
    const c = $("arp-glance-cost");
    if (c) c.textContent = glance.cost_one_liner || "Cost · Auto/Composer";
    const primary = glance.primary_action || {};
    const go = $("arp-go-primary");
    if (go) {
      go.hidden = !primary.label;
      go.textContent = primary.label ? (primary.action === "refresh_panel" ? primary.label + " →" : "Open " + primary.label + " →") : "—";
      go.onclick = () => {
        if (primary.action === "refresh_panel") {
          postAction("refresh_panel").catch(() => {});
          return;
        }
        openApp(primary.id, primary.label);
      };
    }
    const reason = $("arp-glance-reason");
    if (reason) reason.textContent = primary.reason || "";
    const quick = $("arp-glance-quick");
    if (quick) {
      quick.innerHTML = (glance.quick_apps || [])
        .filter((a) => a.id !== primary.id)
        .map(
          (a) =>
            '<button type="button" class="arp-quick-btn" data-app="' +
            esc(a.id) +
            '">' +
            esc(a.label) +
            "</button>"
        )
        .join("");
      quick.querySelectorAll("[data-app]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const id = btn.getAttribute("data-app");
          const row = (glance.quick_apps || []).find((x) => x.id === id);
          openApp(id, row?.label);
        });
      });
    }
  }

  function renderFull(data) {
    const inv = $("arp-inv-routes")?.querySelector("tbody");
    if (inv) {
      inv.innerHTML = (data.investigator_routes || [])
        .slice(0, 20)
        .map(
          (r) =>
            "<tr><td>" +
            esc(r.primary_label || r.primary) +
            "</td><td>" +
            esc(r.secondary_label || r.secondary || "—") +
            "</td><td>" +
            esc(r.when || r.trigger || "—") +
            "</td></tr>"
        )
        .join("");
    }
    const stack = $("arp-stack");
    if (stack) stack.textContent = JSON.stringify(data.stack_map || {}, null, 2).slice(0, 2500);
    const orient = $("arp-orient-full");
    if (orient) orient.textContent = JSON.stringify(data.orient_report || {}, null, 2);
    if (data.mermaid?.loop_chain) renderMermaid("mermaid-loop", data.mermaid.loop_chain);
  }

  async function loadReport() {
    const term = window.SinaMainTerminal;
    if (term) term.log("→ loading AG routing " + mode + "…");
    const url = mode === "full" ? API + "?full=1" : API;
    const data = await fetchJson(url);
    if (!data.ok) {
      if (term) term.finish(false, data.error || "load failed");
      $("arp-headline").textContent = "Load failed: " + (data.error || "?");
      return;
    }
    $("arp-version").textContent = "v" + (data.version || "1.1");
    $("arp-headline").textContent = data.headline || "—";
    renderAgentGlance(data.agent_glance);
    const cost = data.cursor_cost || {};
    $("arp-cost-law").textContent = cost.one_law || cost.line || "—";
    renderTiers(cost.task_tiers);
    renderActive(data.active_route || {});
    $("arp-queue").textContent = "CLOUD " + (data.queue_head || "—");
    const orient = $("arp-orient");
    if (orient) {
      orient.innerHTML = (data.orient_roles || [])
        .slice(0, 6)
        .map((r) => "<li>" + esc(r.role || r.id || JSON.stringify(r)) + "</li>")
        .join("");
    }
    renderBrands(data.brand_routes);
    renderLoop(data.loop_chain || {});
    renderTips(data.golden_tips);
    if (data.mermaid) {
      await renderMermaid("mermaid-flow", data.mermaid.agent_flow);
      await renderMermaid("mermaid-brands", data.mermaid.brand_routes);
    }
    $("arp-light").classList.toggle("arp-hidden", mode === "full");
    $("arp-full").classList.toggle("arp-hidden", mode !== "full");
    if (mode === "full") renderFull(data);
    if (term) {
      term.log("→ " + (data.headline || "loaded"));
      term.finish(true, "AG routing " + mode + " loaded");
    }
  }

  async function postAction(action) {
    const term = window.SinaMainTerminal;
    if (term) term.start(action, action);
    const data = await fetchJson(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    });
    if (term) term.log(JSON.stringify(data).slice(0, 400));
    await loadReport();
  }

  document.querySelectorAll(".arp-mode").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".arp-mode").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      mode = btn.getAttribute("data-mode") || "light";
      loadReport().catch(() => {});
    });
  });

  $("btn-refresh")?.addEventListener("click", () => loadReport().catch(() => {}));
  $("btn-refresh-panel")?.addEventListener("click", () => postAction("refresh_panel").catch(() => {}));

  loadReport().catch((e) => {
    $("arp-headline").textContent = "Server unreachable: " + e.message;
  });

  setInterval(() => {
    if (mode === "light") loadReport().catch(() => {});
  }, 45000);
})();
