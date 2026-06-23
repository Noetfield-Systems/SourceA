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
      var last = cp.last_line || (cp.last_ok === true ? "Last proceed PASS" : cp.last_ok === false ? "Last proceed FAIL" : "—");
      lastEl.textContent = last;
    }
  }

  function renderCloudWorkers(cw) {
    if (!cw) return;
    var st = $("cloud-workers-status");
    var probe = cw.probe || {};
    var situation = cw.situation || {};
    var ff = situation.for_founder || cw.for_founder || probe.for_founder || {};
    var stale = probe.cloud_stale || ff.cloud_stale;
    var failureClass = situation.last_proceed && situation.last_proceed.failure_class;
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
          "24/7 auto drain ARMED — CF cron (primary) + n8n backup skip scaffold, heal motor fail, and proceed. No manual Skip needed.";
      }
    }
    if (mockBanner) mockBanner.hidden = autoArmed || !headIsMock;
    if (motorBanner) motorBanner.hidden = autoArmed || !(headProceedFail && !headIsMock);
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
      { label: "Worker Hub H1", href: "http://127.0.0.1:13020/" },
      { label: "Machine Hub H2", href: "http://127.0.0.1:13020/machines/" },
      { label: "Official Form", href: "http://127.0.0.1:13020/form/" },
      { label: "Portfolio Mail", href: "http://127.0.0.1:13020/mail-hub/" },
      { label: "Mac Health", href: "http://127.0.0.1:13024/" },
      { label: "Proceed receipt", path: "~/.sina/hub-cloud-drain-proceed-receipt-v1.json" },
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
    var live = cw && (cw.hub_live === true || (cw.probe && cw.probe.modules_ok));
    pill.textContent = live ? "Hub LIVE :13020" : "Hub check :13020";
    pill.className = "cw-hub-pill " + (live ? "ok" : "warn");
  }

  function init(opts) {
    var API = (opts && opts.api) || window.location.origin;
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

    async function loadCloudWorkers() {
      try {
        var res = await fetch(API + "/api/cloud-workers/v1", { cache: "no-store" });
        var cw = await res.json();
        renderCloudWorkers(cw);
        var line = $("cw-hub-line");
        if (line) {
          var chain = cw.living_system_chain || {};
          var chainNote = chain.summary_line ? " · " + chain.summary_line : "";
          line.textContent =
            "Live sync " +
            new Date().toLocaleTimeString() +
            " · queue " +
            (((cw.situation || {}).queue_head) || "—") +
            " · pending " +
            (((cw.plans || {}).counts || {}).pending_estimate || 0) +
            chainNote;
        }
        try {
          var hres = await fetch(API + "/health", { cache: "no-store" });
          var h = await hres.json();
          cw.hub_live = h.hub_live;
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
        return null;
      }
    }

    $("btn-cloud-proceed") &&
      $("btn-cloud-proceed").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        var llm = ($("cloud-proceed-llm") && $("cloud-proceed-llm").value) || "openrouter";
        $("btn-cloud-proceed").disabled = true;
        if (out) out.textContent = "Proceeding on Railway via " + llm + "…";
        try {
          var res = await fetchWithTimeout(
            API + "/api/cloud-drain/proceed/v1",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ llm_provider: llm, full_motor: true }),
            },
            180000
          );
          var raw = await res.text();
          var j = JSON.parse(raw);
          var ff = j.for_founder || {};
          var line = ff.show_this || j.hub_proceed_line || j.message || j.error || "—";
          var failNote = j.failure_class === "motor_failed" ? "\n\nPipe LIVE — FORGE motor failure on Railway." : "";
          if (out) out.textContent = "HTTP " + res.status + " · " + line + failNote + "\n\n" + JSON.stringify(j, null, 2);
          await loadCloudWorkers();
        } catch (e) {
          if (out) out.textContent = e.name === "AbortError" ? "Timed out — check ~/.sina/hub-cloud-drain-proceed-receipt-v1.json" : "Error: " + e.message;
        } finally {
          $("btn-cloud-proceed").disabled = false;
        }
      });

    $("btn-cloud-refresh") &&
      $("btn-cloud-refresh").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        if (out) out.textContent = "Probing Railway…";
        try {
          var j = await cwAction("probe");
          renderCloudWorkers(j);
          if (out) out.textContent = JSON.stringify(j.probe || j, null, 2);
        } catch (e) {
          if (out) out.textContent = "Probe error: " + e.message;
        }
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

    $("btn-cw-refresh-all") &&
      $("btn-cw-refresh-all").addEventListener("click", async function () {
        var out = $("cloud-proceed-result");
        if (out) out.textContent = "Refreshing…";
        var cw = await loadCloudWorkers();
        if (out) out.textContent = (cw && cw.situation && cw.situation.summary_line) || "Refreshed.";
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
      var btns = document.querySelectorAll("#btn-cw-skip-mock, #btn-cw-skip-head, #btn-cw-skip-fail");
      btns.forEach(function (b) {
        b.disabled = true;
      });
      if (out) out.textContent = label || "Skipping…";
      try {
        var j = await cwAction(action, body || {});
        if (!j.ok) {
          var errLine =
            (j.for_founder && j.for_founder.show_this) ||
            j.error ||
            j.message ||
            ("HTTP " + (j.http_status || "?"));
          if (out) out.textContent = "Skip failed: " + errLine;
          await loadCloudWorkers();
          return j;
        }
        var line =
          (j.for_founder && j.for_founder.show_this) ||
          (j.ok && j.to ? "Skipped " + j.from + " → head now " + j.to : "") ||
          (j.ok && j.head_now ? "Head now " + j.head_now + (j.skipped_count ? " (skipped " + j.skipped_count + " mock row(s))" : "") : "") ||
          JSON.stringify(j, null, 2);
        if (out) out.textContent = line;
        await loadCloudWorkers();
        return j;
      } catch (e) {
        if (out) out.textContent = "Skip failed: " + e.message;
        return null;
      } finally {
        btns.forEach(function (b) {
          b.disabled = false;
        });
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
        var out = $("cloud-proceed-result");
        $("btn-cw-auto-tick").disabled = true;
        if (out) out.textContent = "Running auto tick (skip mock · optional proceed)…";
        try {
          var j = await cwAction("auto_tick", {});
          if (out) out.textContent = (j.for_founder && j.for_founder.show_this) || JSON.stringify(j, null, 2);
          await loadCloudWorkers();
        } catch (e) {
          if (out) out.textContent = e.message;
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
              " · To arm: touch ~/.sina/cloud-drain-auto-proceed-v1.flag or set CLOUD_DRAIN_AUTO_PROCEED=true on cloud cron.\n" +
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
