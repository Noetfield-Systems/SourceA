(function (global) {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  var CF_BASE = "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev";

  function mountTerminal() {
    if (window.SinaMainTerminal && window.SinaMainTerminal.mount) window.SinaMainTerminal.mount();
  }

  function termStart(action, label) {
    mountTerminal();
    if (window.SinaMainTerminal && window.SinaMainTerminal.start) window.SinaMainTerminal.start(action, label);
  }

  function termFinish(ok, summary) {
    if (window.SinaMainTerminal && window.SinaMainTerminal.finish) window.SinaMainTerminal.finish(ok, summary);
  }

  async function fetchLiveChainFromCf() {
    var out = { cf_health: null, cf_queue: null, cf_observer: null, errors: [] };
    try {
      var hres = await fetch(CF_BASE + "/health", { cache: "no-store" });
      out.cf_health = await hres.json();
    } catch (e) {
      out.errors.push("cf_health: " + e.message);
    }
    try {
      var qres = await fetch(CF_BASE + "/queue", { cache: "no-store" });
      out.cf_queue = await qres.json();
      if (out.cf_queue && out.cf_queue.error === "not_found") {
        out.errors.push("cf_queue: deploy CF worker — cd cloud/workers/cloud-auto-runtime-tick-v1 && npx wrangler deploy");
        out.cf_queue = null;
      }
    } catch (e) {
      out.errors.push("cf_queue: " + e.message);
    }
    try {
      var ores = await fetch(CF_BASE + "/observer-json", { cache: "no-store" });
      out.cf_observer = await ores.json();
    } catch (e) {
      out.errors.push("cf_observer: " + e.message);
    }
    return out;
  }

  function formatLiveChainLog(local, live) {
    var lines = [];
    if (local && local.chain) {
      var c = local.chain;
      lines.push("LOCAL · " + ((c.for_founder && c.for_founder.show_this) || "chain_status"));
      lines.push("  deploy " + ((c.railway && c.railway.deploy_at) || "—") + " · health " + (c.railway && c.railway.health_ok ? "PASS" : "FAIL"));
      lines.push("  local head " + ((c.queue_local && c.queue_local.head) || "—") + " · batch " + ((c.queue_local && c.queue_local.batch_id) || "—"));
    }
    if (live) {
      if (live.cf_health) lines.push("CF cron · " + (live.cf_health.cron || "*/10 * * * *") + " · service " + (live.cf_health.service || "—"));
      if (live.cf_queue && live.cf_queue.cloud_forge_run_head) {
        lines.push(
          "LIVE queue · head " +
            live.cf_queue.cloud_forge_run_head +
            " · last " +
            (live.cf_queue.cloud_forge_run_last_completed || "—") +
            " · batch " +
            ((live.cf_queue.observed && live.cf_queue.observed.batch_id) || "—")
        );
      }
      if (live.cf_observer && live.cf_observer.last_pack) {
        var p = live.cf_observer.last_pack;
        lines.push("LIVE last pack · processed " + (p.processed != null ? p.processed : "—") + "/" + (p.max_advance || 100));
      } else if (live.cf_observer && live.cf_observer.cycles && live.cf_observer.cycles.length) {
        var tail = live.cf_observer.cycles[live.cf_observer.cycles.length - 1];
        var pk = tail.pack || {};
        if (pk.processed != null) lines.push("LIVE cycle · processed " + pk.processed + " · advanced " + (pk.advanced || 0));
      }
      if (live.errors && live.errors.length) lines.push("LIVE errors · " + live.errors.join(" · "));
    }
    return lines.join("\n");
  }

  function fetchWithTimeout(url, opts, ms) {
    var ctrl = new AbortController();
    var t = setTimeout(function () {
      ctrl.abort();
    }, ms || 120000);
    return fetch(url, Object.assign({}, opts || {}, { signal: ctrl.signal })).finally(function () {
      clearTimeout(t);
    });
  }

  function renderCloudProceed(cp) {
    if (!cp) return;
    var nxt = cp.next || {};
    var tid = nxt.task_id || nxt.maps_registry || "—";
    var title = nxt.title || nxt.cloud_action || "";
    var nextEl = $("cloud-proceed-next");
    if (nextEl) nextEl.textContent = "Next: " + tid + (title ? " · " + title : "");
    var lastEl = $("cloud-proceed-last");
    if (lastEl) {
      var last = cp.last_line || "Mac observe — CF cron runs full_pack×100 (no Mac proceed)";
      lastEl.textContent = last;
    }
  }

  function renderCloudWorkers(cw) {
    if (!cw) return;
    var st = $("cloud-workers-status");
    var probe = cw.probe || {};
    var situation = cw.situation || {};
    var ff = situation.for_founder || cw.for_founder || probe.for_founder || {};
    var stale = probe.cloud_stale && !situation.mac_observe_only;
    var failureClass = situation.head_proceed_failed && situation.last_proceed && situation.last_proceed.failure_class;
    var line = situation.summary_line || ff.show_this || (probe.modules_ok ? "Cloud worker ready." : "Cloud status unknown.");
    if (st) {
      st.textContent = ff.show_this || line;
      st.className = "cloud-workers-status " + (stale ? "stale" : failureClass === "motor_failed" ? "stale" : probe.modules_ok !== false ? "ok" : "");
    }
    var sitEl = $("cloud-situation-line");
    if (sitEl) {
      sitEl.textContent = line;
      sitEl.className = "cloud-situation-line " + (stale || failureClass === "motor_failed" ? "motor" : situation.pipe === "LIVE" ? "live" : "down");
    }
    var cmdEl = $("cloud-deploy-cmd");
    var deploy = ff.founder_runs_this || (cw.deploy && cw.deploy.founder_runs_this) || "";
    if (cmdEl && deploy && stale) {
      cmdEl.hidden = false;
      cmdEl.textContent = "You run in Terminal:\n" + deploy;
    } else if (cmdEl) {
      cmdEl.hidden = true;
    }
    var plansEl = $("cloud-workers-plans");
    var cloudPlans = (cw.plans && cw.plans.cloud_forge) || cw.plans || [];
    if (plansEl && cloudPlans.length) {
      plansEl.innerHTML = cloudPlans.slice(0, 12).map(function (p) {
        var head = p.is_head || p.status === "head" ? " ▶ " : " · ";
        var badge = p.status === "completed" ? "done" : p.status === "head" ? "head" : "";
        return "<div>" + head + esc(p.id) + " · " + esc(p.title || "") + (badge ? ' <span class="cloud-badge ' + badge + '">' + esc(p.status) + "</span>" : "") + "</div>";
      }).join("");
    }
    var qc = $("cw-queue-cloud");
    if (qc && cw.plans && cw.plans.cloud_forge) {
      qc.innerHTML = cw.plans.cloud_forge.slice(0, 18).map(function (p) {
        var cls = p.status === "head" ? "head" : p.status === "completed" ? "done" : "";
        return '<div class="cloud-row-item"><span class="cloud-badge ' + cls + '">' + esc(p.status || "?") + "</span><span><strong>" + esc(p.id) + "</strong> · " + esc(p.maps_registry || "") + "<br>" + esc((p.title || "").slice(0, 70)) + "</span></div>";
      }).join("");
    }
    var qm = $("cw-queue-mac");
    if (qm && cw.plans && cw.plans.mac_control) {
      qm.innerHTML = cw.plans.mac_control.map(function (p) {
        return '<div class="cloud-row-item"><span class="cloud-badge">mac</span><span><strong>' + esc(p.id) + "</strong><br>" + esc((p.title || "").slice(0, 70)) + "</span></div>";
      }).join("");
    }
    var inbox = cw.inbox || {};
    var note = $("cw-inbox-worker-note");
    if (note && inbox.worker_inbox_note) note.textContent = inbox.worker_inbox_note.show_this || "—";
    var itemsEl = $("cw-inbox-items");
    if (itemsEl && inbox.items) {
      itemsEl.innerHTML = inbox.items.map(function (it) {
        return '<div class="cloud-row-item"><span class="cloud-badge head">' + esc(it.priority) + "</span><span><strong>" + esc(it.id) + "</strong> · " + esc(it.maps_registry || "") + "<br>" + esc(it.title || "") + "<br><em>" + esc(it.note || "") + "</em></span></div>";
      }).join("");
    }
    var evEl = $("cw-events");
    if (evEl && cw.events) {
      evEl.innerHTML = cw.events.slice(0, 25).map(function (e) {
        var ok = e.ok === true ? "done" : e.ok === false ? "fail" : "";
        return '<div class="cloud-row-item"><span class="cloud-badge ' + ok + '">' + esc(e.kind || "?") + "</span><span>" + esc(e.at || "") + " · " + esc(e.plan_id || "") + "<br>" + esc(e.line || "") + (e.failure_class ? " · <em>" + esc(e.failure_class) + "</em>" : "") + "</span></div>";
      }).join("");
    }
    var cliEl = $("cw-cli");
    if (cliEl && cw.cli) {
      cliEl.innerHTML = cw.cli.map(function (c) {
        return "<div class=\"cloud-cli-row\"><strong>" + esc(c.label) + "</strong><br>" + esc(c.cmd) + "</div>";
      }).join("");
    }
    if (cw.proceed_slice) renderCloudProceed(cw.proceed_slice);
    var headId = situation.queue_head || (cw.plans && cw.plans.queue_head) || "";
    var headPlan = ((cw.plans && cw.plans.cloud_forge) || []).find(function (p) {
      return p.status === "head" || p.id === headId;
    });
    var autoArmed = cw.auto_runtime && cw.auto_runtime.auto_proceed_enabled === true;
    var headIsMock = situation.head_is_mock === true;
    var headProceedFail = situation.head_proceed_failed === true;
    var mockBanner = $("cw-mock-banner");
    var motorBanner = $("cw-motor-fail-banner");
    var autoBanner = $("cw-auto-banner");
    if (autoBanner) {
      autoBanner.hidden = !autoArmed;
      if (autoArmed) {
        autoBanner.textContent =
          "CF cron */10 (primary) · full_pack×100 on Railway · Mac observe only — no Mac→Railway commands.";
      }
    }
    var macObserve = situation.mac_observe_only === true || (cw.chain && cw.chain.mac_never_commands_railway);
    if (mockBanner) mockBanner.hidden = macObserve || autoArmed || !headIsMock;
    if (motorBanner) motorBanner.hidden = macObserve || autoArmed || !(headProceedFail && !headIsMock);
    ["btn-cw-skip-head", "btn-cw-skip-mock", "btn-cw-skip-fail"].forEach(function (id) {
      var btn = $(id);
      if (btn) btn.hidden = autoArmed;
    });
    renderLinks(cw);
    renderReports(cw);
    updateHubPill(cw);
    var autoPill = $("cw-auto-pill");
    if (autoPill && cw.auto_runtime) {
      var ar = cw.auto_runtime;
      autoPill.textContent = ar.auto_proceed_enabled ? "Auto drain ARMED" : "Auto drain OFF";
      autoPill.className = "cw-hub-pill " + (ar.auto_proceed_enabled ? "ok" : "warn");
    }
  }

  function cwSelectTab(name) {
    document.querySelectorAll(".cloud-tabs button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-cw-tab") === name);
    });
    ["queue", "inbox", "events", "cli", "links", "reports"].forEach(function (t) {
      var el = $("cw-tab-" + t);
      if (el) el.hidden = t !== name;
    });
  }

  function renderLinks(cw) {
    var el = $("cw-links");
    if (!el) return;
    var apis = (cw && cw.hub_apis) || {};
    var rows = [
      { label: "Railway FBE runner", href: "https://sourcea-fbe-runner-production.up.railway.app/health" },
      { label: "Cloud drain queue", href: "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1" },
      { label: "Observer", href: "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1" },
      { label: "Proceed log", path: "~/.sina/cloud-workers-proceed-log-v1.jsonl" },
      { label: "Proceed receipt", path: "~/.sina/hub-cloud-forge-run-proceed-receipt-v1.json" },
      { label: "Event log", path: "~/.sina/cloud-workers-event-log-v1.json" },
      { label: "Control plane SSOT", path: "data/cloud-workers-control-plane-v1.json" },
    ];
    var apiLines = Object.keys(apis).map(function (k) {
      return "<div class=\"cloud-cli-row\"><strong>" + esc(k) + "</strong><br>" + esc(apis[k]) + "</div>";
    }).join("");
    el.innerHTML =
      "<h4>Portfolio apps</h4>" +
      rows
        .map(function (r) {
          if (r.href) {
            return '<p><a class="cw-link" href="' + esc(r.href) + '" target="_blank" rel="noopener">' + esc(r.label) + "</a></p>";
          }
          return "<p><strong>" + esc(r.label) + "</strong><br><code>" + esc(r.path) + "</code></p>";
        })
        .join("") +
      "<h4>Hub APIs</h4>" +
      apiLines;
  }

  function renderReports(cw) {
    var el = $("cw-reports");
    if (!el) return;
    var reps = (cw && cw.reports) || [];
    if (!reps.length) {
      el.innerHTML = "<p class=\"sub\">No recent reports yet — Proceed or probe to generate receipts.</p>";
      return;
    }
    el.innerHTML = reps
      .map(function (r) {
        return (
          '<div class="cloud-row-item"><span class="cloud-badge">' +
          esc(r.kind || "report") +
          "</span><span>" +
          esc(r.at || "") +
          "<br>" +
          esc(r.line || r.summary || "") +
          "</span></div>"
        );
      })
      .join("");
  }

  function updateHubPill(cw) {
    var pill = $("cw-hub-pill");
    if (!pill) return;
    var chain = (cw && cw.chain) || (cw && cw.situation && cw.situation.chain) || {};
    var railway = chain.railway || {};
    var live = !!(railway.health_ok || (cw.probe && cw.probe.ok));
    var url = railway.url || (cw.probe && cw.probe.cloud_worker_url) || "Railway FBE";
    pill.textContent = live ? "Railway LIVE · Mac observe" : "Railway check deploy receipt";
    pill.title = url;
    pill.className = "cw-hub-pill " + (live ? "ok" : "warn");
  }

  function dbgLog(hypothesisId, location, message, data) {
    // #region agent log
    fetch("http://127.0.0.1:7877/ingest/9e528f93-f3e7-4118-9598-fd5e8f7cc69a", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "23242e" },
      body: JSON.stringify({
        sessionId: "23242e",
        hypothesisId: hypothesisId,
        location: location,
        message: message,
        data: data || {},
        timestamp: Date.now(),
      }),
    }).catch(function () {});
    // #endregion
  }

  function termLog(msg) {
    if (window.SinaMainTerminal && window.SinaMainTerminal.log) window.SinaMainTerminal.log(msg);
  }

  function formatProceedLog(res, j) {
    var ff = typeof j.for_founder === "string" ? { show_this: j.for_founder } : j.for_founder || {};
    var pack = j.pack || (j.cloud && j.cloud.pack) || (j.motor && j.motor.pack) || {};
    var parts = ["HTTP " + res.status];
    if (pack.processed != null) parts.push("pack processed " + pack.processed + "/" + (pack.max_advance || 100));
    if (pack.advanced != null) parts.push("shipped " + pack.advanced);
    if (pack.skipped != null) parts.push("skipped " + pack.skipped);
    if (pack.head_now) parts.push("head " + pack.head_now);
    if (pack.batch_complete) parts.push("BATCH COMPLETE");
    parts.push(ff.show_this || j.hub_proceed_line || j.message || j.error || "—");
    if (j.cloud_worker_url) parts.push("→ " + j.cloud_worker_url);
    var failNote = "";
    if (j.failure_class === "pack_gate_halt") {
      failNote = "\n\nGate latched — Proceed will auto-reset after Railway deploy; not a FORGE motor fail.";
    } else if (j.failure_class === "motor_failed") {
      failNote = "\n\nPipe LIVE — FORGE motor failure on Railway.";
    }
    return parts.join(" · ") + failNote + "\n\n" + JSON.stringify(j, null, 2);
  }

  function init(opts) {
    var API = (opts && opts.api) || window.location.origin;
    mountTerminal();
    document.querySelectorAll(".cloud-tabs button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        cwSelectTab(btn.getAttribute("data-cw-tab"));
      });
    });

    async function cwAction(action, body) {
      var res = await fetchWithTimeout(
        API + "/api/cloud-workers/v1",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.assign({ action: action }, body || {})),
        },
        120000
      );
      var j = await res.json();
      if (!j || (j.ok === false && j.error)) {
        j = j || {};
        j.http_status = res.status;
      }
      return j;
    }

    async function refreshChainToTerminal(label) {
      termStart("refresh", label || "Refresh chain");
      termLog("Reading local chain_status (Mac — no Railway HTTP)…");
      var local = await cwAction("chain_status", {});
      termLog(formatLiveChainLog({ chain: local }, null));
      termLog("Fetching LIVE queue via CF proxy (browser→CF→Railway)…");
      var live = await fetchLiveChainFromCf();
      termLog(formatLiveChainLog(null, live));
      var block = formatLiveChainLog({ chain: local }, live);
      var out = $("cloud-proceed-result");
      if (out) out.textContent = block + "\n\n" + JSON.stringify({ local: local, live: live }, null, 2);
      termFinish(local.ok !== false, (live.cf_queue && live.cf_queue.cloud_forge_run_head) ? "Live head " + live.cf_queue.cloud_forge_run_head : "Chain refreshed");
      return { local: local, live: live };
    }

    async function loadCloudWorkers() {
      try {
        dbgLog("H3", "cloud-workers-panel:load", "start", { api: API });
        var res = await fetch(API + "/api/cloud-workers/v1", { cache: "no-store" });
        var cw = await res.json();
        dbgLog("H3", "cloud-workers-panel:load", "ok", { status: res.status, head: ((cw.situation || {}).queue_head) });
        renderCloudWorkers(cw);
        if (cw.chain && cw.chain.cf_cron && cw.chain.cf_cron.url) {
          CF_BASE = String(cw.chain.cf_cron.url).replace(/\/$/, "");
        }
        try {
          var live = await fetchLiveChainFromCf();
          if (live.cf_queue && live.cf_queue.cloud_forge_run_head) {
            termLog("Live sync · head " + live.cf_queue.cloud_forge_run_head);
            await cwAction("sync_live_queue", { queue: live.cf_queue });
            var res2 = await fetch(API + "/api/cloud-workers/v1", { cache: "no-store" });
            cw = await res2.json();
            renderCloudWorkers(cw);
          }
        } catch (syncErr) {
          termLog("Live sync skip: " + syncErr.message);
        }
        var line = $("cw-hub-line");
        if (line) {
          var chain = cw.chain || (cw.situation && cw.situation.chain) || {};
          line.textContent =
            "Mac observe only · CF cron " +
            ((chain.cf_cron && chain.cf_cron.cron) || "*/10 * * * *") +
            " · local head " +
            (((chain.queue_local && chain.queue_local.head) || (cw.situation || {}).queue_head) || "—");
        }
        try {
          var hres = await fetch(API + "/health", { cache: "no-store" });
          var h = await hres.json();
          cw.railway_live = h.railway_live;
          cw.hub_live = h.railway_live;
          updateHubPill(cw);
        } catch (e) {}
        return cw;
      } catch (e) {
        var st = $("cloud-workers-status");
        if (st) {
          st.textContent = "Cloud Workers load failed: " + e.message;
          st.className = "cloud-workers-status stale";
        }
        var out = $("cloud-proceed-result");
        if (out) out.textContent = "API DOWN at " + new Date().toLocaleTimeString() + " — " + e.message;
        termLog("Load failed: " + e.message);
        return null;
      }
    }

    $("btn-cloud-proceed") &&
      $("btn-cloud-proceed").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        $("btn-cloud-proceed").disabled = true;
        termStart("trigger_cf_pack", "Trigger CF full-pack (browser→cloud)");
        termLog("POST " + CF_BASE + "/tick · full_pack×100 on Railway · Mac does NOT call Railway");
        if (out) out.textContent = "Triggering CF cron full-pack via browser (not Mac server)…";
        try {
          var res = await fetchWithTimeout(
            CF_BASE + "/tick",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ proceed: true }),
            },
            900000
          );
          var raw = await res.text();
          var j;
          try {
            j = JSON.parse(raw);
          } catch (parseErr) {
            j = { ok: false, error: "invalid_json", message: raw.slice(0, 500) };
          }
          var line = formatProceedLog(res, j.motor || j);
          if (j.processed != null) line = "CF tick · processed " + j.processed + "\n" + line;
          if (out) out.textContent = line;
          termLog(line.split("\n\n")[0]);
          termFinish(!!j.ok, j.ok ? "CF full-pack triggered" : "CF tick returned fail");
          await loadCloudWorkers();
        } catch (e) {
          var errMsg = e.name === "AbortError" ? "Timed out — pack may still run on Railway; check CF /observer-json" : "Error: " + e.message;
          if (out) out.textContent = errMsg;
          termLog(errMsg);
          termFinish(false, errMsg);
        } finally {
          $("btn-cloud-proceed").disabled = false;
        }
      });

    $("btn-cloud-refresh") &&
      $("btn-cloud-refresh").addEventListener("click", async function () {
        await refreshChainToTerminal("Probe chain");
      });

    $("btn-cw-refresh-all") &&
      $("btn-cw-refresh-all").addEventListener("click", async function () {
        await refreshChainToTerminal("Refresh all");
        await loadCloudWorkers();
      });

    $("btn-cloud-dry-run") &&
      $("btn-cloud-dry-run").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        try {
          var j = await cwAction("dry_run");
          if (out) out.textContent = (j.for_founder && j.for_founder.show_this) || JSON.stringify(j, null, 2);
        } catch (e) {
          if (out) out.textContent = "Dry run error: " + e.message;
        }
      });

    $("btn-cloud-deploy-info") &&
      $("btn-cloud-deploy-info").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        try {
          var j = await cwAction("deploy_instructions");
          var d = j.deploy || {};
          var cmdEl = $("cloud-deploy-cmd");
          if (cmdEl) {
            cmdEl.hidden = false;
            cmdEl.textContent = (d.why || "") + "\n\nYOU run:\n" + (d.founder_runs_this || "");
          }
          var block = $("cw-deploy-block");
          if (block) {
            block.hidden = false;
            block.textContent = (d.founder_runs_this || "") + "\n\n" + (d.agent_rule || "");
          }
          if (out) out.textContent = JSON.stringify(d, null, 2);
        } catch (e) {
          if (out) out.textContent = e.message;
        }
      });

    $("btn-cw-dry-mac") &&
      $("btn-cw-dry-mac").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        try {
          var j = await cwAction("dry_run");
          if (out) out.textContent = (j.for_founder && j.for_founder.show_this) || JSON.stringify(j, null, 2);
        } catch (e) {
          if (out) out.textContent = e.message;
        }
      });

    $("btn-cw-dry-cloud") &&
      $("btn-cw-dry-cloud").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        var llm = ($("cloud-proceed-llm") && $("cloud-proceed-llm").value) || "openrouter";
        if (out) out.textContent = "Cloud dry-run…";
        try {
          var j = await cwAction("proceed_dry_cloud", { llm_provider: llm });
          if (out) out.textContent = (j.for_founder && j.for_founder.show_this) || JSON.stringify(j, null, 2);
          await loadCloudWorkers();
        } catch (e) {
          if (out) out.textContent = e.message;
        }
      });

    async function runSkip(action, body, label) {
      var out = $("cloud-proceed-result");
      termStart(action, label || "Skip");
      termLog("Mac observe only — skip blocked on Mac; CF cron self-heals on Railway");
      try {
        var j = await cwAction(action, body || {});
        var line = (j.for_founder && j.for_founder.show_this) || j.error || JSON.stringify(j, null, 2);
        if (out) out.textContent = line;
        termLog(line);
        termFinish(false, "Mac observe only");
        await loadCloudWorkers();
        return j;
      } catch (e) {
        if (out) out.textContent = e.message;
        termFinish(false, e.message);
        return null;
      }
    }

    $("btn-cw-skip-head") &&
      $("btn-cw-skip-head").addEventListener("click", function () {
        runSkip("skip_head", { reason: "founder_cloud_panel_skip" }, "Skipping queue head…");
      });

    $("btn-cw-skip-mock") &&
      $("btn-cw-skip-mock").addEventListener("click", function () {
        runSkip("skip_to_next_real", { reason: "founder_skip_mock_banner" }, "Skipping scaffold rows…");
      });

    $("btn-cw-skip-fail") &&
      $("btn-cw-skip-fail").addEventListener("click", function () {
        runSkip("skip_head", { reason: "founder_skip_motor_fail" }, "Skipping failed head row…");
      });

    $("btn-cw-auto-tick") &&
      $("btn-cw-auto-tick").addEventListener("click", async function () {
        $("btn-cw-auto-tick").disabled = true;
        termStart("auto_tick", "Mac auto tick (observe only)");
        try {
          var j = await cwAction("auto_tick", {});
          termLog((j.for_founder && j.for_founder.show_this) || JSON.stringify(j));
          var out = $("cloud-proceed-result");
          if (out) out.textContent = JSON.stringify(j, null, 2);
          termFinish(j.decision === "mac_observe_only", "Mac observe only — use Trigger CF full-pack");
          await loadCloudWorkers();
        } catch (e) {
          termLog(e.message);
          termFinish(false, e.message);
        } finally {
          $("btn-cw-auto-tick").disabled = false;
        }
      });

    $("btn-cw-enable-auto") &&
      $("btn-cw-enable-auto").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        try {
          var j = await cwAction("auto_status", {});
          if (out) {
            out.textContent =
              "Auto proceed: " +
              (j.auto_proceed_enabled ? "ON" : "OFF") +
              " · To arm: touch ~/.sina/cloud-forge-run-auto-proceed-v1.flag or set CLOUD_FORGE_RUN_AUTO_PROCEED=true on cloud cron.\n" +
              JSON.stringify(j, null, 2);
          }
        } catch (e) {
          if (out) out.textContent = e.message;
        }
      });

    $("btn-cw-deploy") &&
      $("btn-cw-deploy").addEventListener("click", function () {
        if ($("btn-cloud-deploy-info")) $("btn-cloud-deploy-info").click();
        cwSelectTab("cli");
      });

    loadCloudWorkers();
    setInterval(function () {
      if (!document.hidden) loadCloudWorkers();
    }, 10000);

    return { loadCloudWorkers: loadCloudWorkers, renderCloudWorkers: renderCloudWorkers };
  }

  global.SinaCloudWorkers = { init: init, renderCloudWorkers: renderCloudWorkers };
})(window);
