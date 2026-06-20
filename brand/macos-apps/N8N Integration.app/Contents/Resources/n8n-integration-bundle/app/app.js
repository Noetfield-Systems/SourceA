(function () {
  "use strict";

  const API = window.location.origin;
  const $ = (id) => document.getElementById(id);
  let busy = false;
  let lastWebhook = "";

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function toast(msg, ms) {
    const el = document.createElement("div");
    el.className = "n8-toast";
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), ms || 4000);
  }

  async function api(body) {
    const res = await fetch(`${API}/api/n8n-integration`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || { action: "report" }),
    });
    return res.json();
  }

  function setStat(id, up, text) {
    const el = $(id);
    if (!el) return;
    const val = el.querySelector(".n8-stat-val");
    if (!val) return;
    if (text != null) {
      val.textContent = text;
      val.className = "n8-stat-val";
      return;
    }
    val.textContent = up ? "UP" : "DOWN";
    val.className = "n8-stat-val " + (up ? "n8-up" : "n8-down");
  }

  function renderWorkflows(workflows) {
    const box = $("n8-workflows");
    if (!box) return;
    const rows = workflows || [];
    if (!rows.length) {
      box.innerHTML = "<p class='n8-muted'>No workflow checks yet.</p>";
      return;
    }
    box.innerHTML = rows
      .map((w) => {
        const ok = w.ok;
        const cls = ok ? "n8-wf-ok" : "n8-wf-fail";
        const mark = ok ? "✓" : "✗";
        const src = w.source && w.source !== "mono" ? `<span class="n8-wf-src">${esc(w.source)}</span>` : "";
        return `<div class="n8-wf-row">
          <span><span class="n8-wf-name">${esc(w.name || w.id)}</span><span class="n8-wf-role">${esc(w.role || "")}</span>${src}</span>
          <span class="${cls}">${mark}</span>
        </div>`;
      })
      .join("");
  }

  function formatIntel(intel) {
    if (!intel || !intel.ok) return intel?.error || "No intelligence snapshot yet.";
    const snap = intel.snapshot || {};
    const analysis = intel.analysis || snap.analysis || {};
    const parts = [];
    const score = intel.stack_score ?? analysis.stack_health_score;
    const grade = intel.grade ?? analysis.grade;
    parts.push(`Stack score: ${score ?? "—"}${grade ? " (" + grade + ")" : ""}`);
    if (snap.captured_at) parts.push(`Captured: ${snap.captured_at}`);
    const opps = analysis.product_opportunities || analysis.opportunities || [];
    if (opps.length) {
      parts.push("\n## Opportunities");
      opps.slice(0, 8).forEach((o) => parts.push(`- ${o.title || o.id}: ${o.why || o.rationale || ""}`));
    }
    const signals = analysis.signals || [];
    if (signals.length) {
      parts.push("\n## Signals");
      signals.slice(0, 6).forEach((s) => parts.push(`- ${s.title}: ${s.action || s.severity || ""}`));
    }
    if (intel.brief_preview) parts.push("\n## Brief excerpt\n" + intel.brief_preview);
    return parts.join("\n");
  }

  function formatSteps(result) {
    const steps = result.steps || result.extra_steps || [];
    if (!steps.length) return JSON.stringify(result, null, 2);
    const lines = [result.message || result.ok ? "PASS" : "FAIL", ""];
    steps.forEach((s) => {
      lines.push(`[${s.ok ? "PASS" : "FAIL"}] ${s.title || s.id}: ${s.detail || ""}`);
    });
    return lines.join("\n");
  }

  function renderReport(data) {
    if (!data || !data.ok) {
      const line = $("n8-status-line");
      if (line) {
        line.textContent = data?.error || "Failed to load report";
        line.className = "n8-status-line n8-status-error";
      }
      return;
    }

    const st = data.status || {};
    const line = $("n8-status-line");
    if (line) {
      const parts = [];
      parts.push(st.n8n_running ? "n8n running" : "n8n stopped");
      parts.push(st.runtime_running ? "runtime up" : "runtime down");
      parts.push(st.hub_running ? "hub up" : "hub down");
      line.textContent = parts.join(" · ");
      line.className = "n8-status-line " + (st.n8n_running ? "n8-status-ok" : "");
    }

    setStat("stat-n8n", !!st.n8n_running);
    setStat("stat-runtime", !!st.runtime_running);
    setStat("stat-hub", !!st.hub_running);

    const q = data.quality || {};
    const wfs = data.workflows || [];
    const okCount = q.workflow_ok_count ?? wfs.filter((w) => w.ok).length;
    const total = q.workflow_total ?? wfs.length;
    setStat("stat-workflows", null, `${okCount}/${total}`);

    const intel = data.intelligence || {};
    const score = intel.stack_score ?? (intel.analysis || {}).stack_health_score;
    const grade = intel.grade ?? (intel.analysis || {}).grade;
    setStat("stat-intel", null, score != null ? `${score}${grade ? " " + grade : ""}` : "—");

    const cuWire = data.chat_unify_wire || {};
    const cl = $("n8-commercial-line");
    if (cl && cuWire.wired != null) {
      cl.textContent = cuWire.wired
        ? "⇄ Chat Unify + Cursor wired — merge fires n8n webhook"
        : "⇄ Chat Unify not wired — tap Wire Chat Unify + Cursor";
      cl.className = "n8-quality-line n8-commercial-line " + (cuWire.wired ? "n8-commercial-ready" : "n8-commercial-warn");
    }

    const ql = $("n8-quality-line");
    if (ql) {
      const allOk = q.workflow_all_ok;
      ql.textContent = allOk
        ? `Quality gate PASS — ${total} workflows validated · stack ${score ?? "—"} ${grade || ""}`.trim()
        : `Quality gate PARTIAL — ${okCount}/${total} workflows OK · tap Sync stubs or Capture intelligence`;
    }

    renderWorkflows(wfs);

    const wh = $("n8-webhook");
    lastWebhook = data.webhook_url || data.local_api || "";
    if (wh) wh.textContent = lastWebhook || "—";

    const ver = $("n8-version");
    if (ver) ver.textContent = "v" + (data.version || "1.1").replace(/\.0$/, "");

    const tag = $("n8-tagline");
    if (tag && data.tagline) tag.textContent = data.tagline;

    if (data.brief_preview) {
      const out = $("n8-output");
      const hint = $("output-hint");
      if (out && !busy) out.textContent = data.brief_preview;
      if (hint) hint.textContent = data.brief_exists ? "Latest brief on disk" : "";
    } else if (intel.ok && !busy) {
      const out = $("n8-output");
      if (out) out.textContent = formatIntel(intel);
    }
  }

  async function loadReport() {
    const data = await api({ action: "report" });
    renderReport(data);
    return data;
  }

  async function runAction(action, label, extraBody) {
    if (busy) return;
    busy = true;
    document.querySelectorAll(".n8-btn").forEach((b) => (b.disabled = true));
    toast(label || action + "…");
    try {
      const body = Object.assign({ action }, extraBody || {});
      const result = await api(body);
      if (result.ok === false) {
        toast("Error: " + (result.error || result.message || action));
      } else {
        toast((label || action) + " done");
      }
      const out = $("n8-output");
      if (out) {
        if (action === "open_brief" && result.brief) {
          out.textContent = result.brief;
        } else if (action === "capture_intelligence" || action === "intelligence" || action === "get") {
          out.textContent = formatIntel(result);
        } else if (action === "test_extended" || action === "test_flow" || action === "run_suite") {
          out.textContent = formatSteps(result);
        } else if (action === "validate") {
          const checks = result.checks || [];
          out.textContent = [
            result.message || "",
            "",
            ...checks.map((c) => `[${c.ok ? "PASS" : "FAIL"}] ${c.name || c.id} (${c.source || "?"})`),
          ].join("\n");
        } else if (action === "health_ping") {
          out.textContent = [
            result.message || "",
            `Hub: ${result.hub?.ok ? "ok" : "fail"}`,
            `Runtime: ${result.runtime?.ok ? "ok" : "fail"}`,
          ].join("\n");
        } else if (action === "sync_stubs") {
          out.textContent = [
            result.message || "",
            ...(result.copied || []).map((c) => `Copied: ${c.id}`),
            ...(result.skipped || []).map((s) => `Skipped: ${s.id} — ${s.reason}`),
          ].join("\n");
        } else if (action === "export_receipt") {
          out.textContent = `Receipt exported: ${result.path || "—"}`;
        } else if (action === "commercial_grade") {
          const checks = result.checks || {};
          const lines = [
            result.commercial_ready ? "COMMERCIAL READY ✓" : "NOT READY — fix checks below",
            `Primary SKU: ${result.primary_sku || "SKU-OPS-001"}`,
            "",
            ...Object.entries(checks).map(([k, v]) => `• ${k}: ${v ? "PASS" : "FAIL"}`),
            "",
            result.founder_line || "",
          ];
          out.textContent = lines.join("\n");
          const cl = $("n8-commercial-line");
          if (cl) {
            cl.textContent = result.commercial_ready
              ? "💰 Commercial grade READY — export sales pack for SOW"
              : "Commercial grade incomplete — run checks above";
            cl.className = "n8-quality-line n8-commercial-line " + (result.commercial_ready ? "n8-commercial-ready" : "n8-commercial-warn");
          }
        } else if (action === "export_commercial_pack") {
          out.textContent = [
            "Sales pack exported",
            `Path: ${result.export_paths?.sales_pack || "~/.sina/n8n-commercial-sales-pack-v1.json"}`,
            "",
            `Hero: ${result.hero_sku?.product_name || "Founder Ops Glue"}`,
            `Setup $${result.hero_sku?.setup_usd || 2500} · MRR $${result.hero_sku?.monthly_usd || 499}`,
            "",
            ...(result.sow_bullets || []).map((b) => "• " + b),
          ].join("\n");
        } else if (action === "upgrade_all") {
          const c = result.closeout || {};
          out.textContent = [
            result.ok ? "UPGRADE ALL ✓" : "UPGRADE INCOMPLETE",
            `n8n: ${result.n8n_engine?.version_before || "?"} → ${result.n8n_engine?.version_after || "?"}`,
            `Workflows stamped: ${result.workflows_upgraded ?? "—"}`,
            c.client_buy_ready ? "CLIENT-READY ✓" : "CLIENT COPY check",
            "",
            result.founder_line || "",
            `Proposal: ${c.client_send?.proposal || "—"}`,
            `Weekly: ${c.client_send?.weekly_report || "—"}`,
            "",
            result.next_founder || "",
          ].join("\n");
        } else if (action === "commercial_all") {
          const v = result.validators || {};
          const ev = result.extra_validators || {};
          out.textContent = [
            result.ok ? "FINISH ALL ✓" : "FINISH INCOMPLETE",
            result.client_buy_ready ? "CLIENT-READY ✓" : "CLIENT COPY needs fix",
            result.founder_line || "",
            "",
            `Proposal: ${result.client_send?.proposal || result.client_sow_path || "—"}`,
            `Weekly: ${result.client_send?.weekly_report || result.client_weekly_path || "—"}`,
            "",
            ...Object.entries(v).map(([k, x]) => `• launch ${k}: ${x.ok ? "PASS" : "FAIL"}`),
            ...Object.entries(ev).map(([k, x]) => `• ${k}: ${x.ok ? "PASS" : "FAIL"}`),
            "",
            result.next_founder || "",
          ].join("\n");
          const cl = $("n8-commercial-line");
          if (cl) {
            cl.textContent = result.ok
              ? "🚀 Launch kit on disk — Print SOW · send T01–T03 · wire Stripe"
              : "Launch incomplete — see output";
            cl.className = "n8-quality-line n8-commercial-line " + (result.ok ? "n8-commercial-ready" : "n8-commercial-warn");
          }
        } else if (action === "wire_chat_unify") {
          const st = result.status || {};
          out.textContent = [
            result.ok ? "WIRE PASS ✓" : "WIRE INCOMPLETE",
            result.founder_line || "",
            "",
            `Chat Unify: ${st.chat_unify_up ? "UP" : "DOWN"}`,
            `n8n: ${st.n8n_up ? "UP" : "DOWN"}`,
            `Merge WF active: ${st.merge_workflow_active ? "YES" : "NO"}`,
            `Cursor imports: ${result.cursor_sync?.imported_count ?? "—"}`,
            "",
            ...(result.steps || []).map((s) => `• ${s.step}: ${s.ok === false ? "FAIL" : "OK"}`),
            "",
            result.next_founder || "",
          ].join("\n");
        } else if (action === "sync_cursor_transcripts") {
          out.textContent = [
            result.ok ? "CURSOR IMPORT ✓" : "IMPORT FAILED",
            `Imported: ${result.imported_count ?? 0} · Skipped: ${result.skipped_count ?? 0}`,
            "",
            ...(result.imported || []).map((r) => `+ ${r.path}`),
            ...(result.skipped || []).map((r) => `~ ${r.path}`),
          ].join("\n");
        } else if (action === "film_status" || action === "film_critic" || action === "film_ship_gate" || action === "film_compile" || action === "film_ingest") {
          const fl = $("n8-film-line");
          const line = result.factory_now_line || result.next_action || "";
          if (fl && line) {
            fl.textContent = line;
            fl.className = "n8-quality-line n8-commercial-line " + (result.publish_allowed || result.verdict === "PASS" ? "n8-commercial-ready" : "n8-commercial-warn");
          }
          out.textContent = JSON.stringify(result, null, 2);
        } else if (action === "governance_wire") {
          out.textContent = JSON.stringify(result, null, 2);
        } else if (result.message) {
          out.textContent = result.message;
        } else if (result.tail) {
          out.textContent = result.tail;
        }
      }
      await loadReport();
    } catch (e) {
      toast("Request failed: " + e.message);
    } finally {
      busy = false;
      document.querySelectorAll(".n8-btn").forEach((b) => (b.disabled = false));
    }
  }

  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.getAttribute("data-action");
      const extra = {};
      const lane = btn.getAttribute("data-lane");
      if (lane) extra.lane = lane;
      if (btn.getAttribute("data-skip-capture") === "1") extra.skip_capture = true;
      runAction(action, btn.textContent.trim(), extra);
    });
  });

  $("btn-refresh")?.addEventListener("click", () => loadReport());

  $("btn-copy-webhook")?.addEventListener("click", async () => {
    const url = lastWebhook || $("n8-webhook")?.textContent || "";
    if (!url || url === "—") {
      toast("No webhook URL yet");
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
      toast("Webhook URL copied");
    } catch {
      toast(url);
    }
  });

  loadReport().catch((e) => {
    const line = $("n8-status-line");
    if (line) {
      line.textContent = "Server unreachable: " + e.message;
      line.className = "n8-status-line n8-status-error";
    }
  });

  setInterval(() => {
    if (!busy) loadReport().catch(() => {});
  }, 90000);
})();
