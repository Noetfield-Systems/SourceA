/**
 * SourceA live command center — factory + pipeline + AEG proof on home hero.
 * Data: factory-live.json · aeg-live.json (injected on deploy).
 */
(function () {
  const DATA_URL = "/sourcea/data/factory-live.json";
  const BOOT_URL = "/sourcea/data/boot-proof.json";
  const AEG_URL = "/sourcea/data/aeg-live.json";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function streamText(el, text, speed = 12) {
    if (!el) return;
    if (reduced) {
      el.textContent = text;
      return;
    }
    el.classList.add("is-streaming");
    el.textContent = "";
    let i = 0;
    const tick = () => {
      if (i <= text.length) {
        el.textContent = text.slice(0, i);
        i += 1;
        setTimeout(tick, speed);
      } else {
        el.classList.remove("is-streaming");
      }
    };
    tick();
  }

  function checkBadge(ok) {
    return ok ? '<span class="sa-v pass">PASS</span>' : '<span class="sa-v block">BLOCK</span>';
  }

  function verdictClass(v) {
    return v === "PASS" ? "pass" : v === "BLOCK" ? "block" : "";
  }

  function clientizeTerminal(text) {
    return String(text ?? "")
      .replace(/\bSSOT\b/g, "policy pack")
      .replace(/ssot_brief/gi, "policy_brief")
      .replace(/session gate/gi, "rules check")
      .replace(/run-inbox|queue_truth|truth_match/gi, "pipeline_sync")
      .replace(/factory-now/gi, "live status")
      .replace(/SOURCEA_BOOT/g, "SOURCEA_SAMPLE_BOOT");
  }

  function colorizeTerminal(text) {
    return clientizeTerminal(text)
      .split("\n")
      .map((line) => {
        let s = esc(line);
        s = s.replace(/\[PASS\]/g, '<span class="sa-t-ok">[PASS]</span>');
        s = s.replace(/\[FAIL\]/g, '<span class="sa-t-bad">[FAIL]</span>');
        s = s.replace(/CRITIC_BOOT BLOCK/g, 'CRITIC_BOOT <span class="sa-t-warn">BLOCK</span>');
        s = s.replace(/^(\$.*)$/gm, '<span class="sa-t-dim">$1</span>');
        return s;
      })
      .join("\n");
  }

  function renderAeg(panel, live) {
    const aeg = live.aeg || {};
    const boot = live.boot || {};
    const checks = aeg.checks || boot.checks || [];
    const terminal = (aeg.terminal_transcript || "").split("\n").slice(0, 12).join("\n");
    const verdict = aeg.verdict || boot.verdict || "—";
    const url = live.aeg_live_url || aeg.site_proof_url || "/sourcea/proof/live";
    const eid = aeg.evidence_id || "—";
    const valid = live.valid_yes != null ? `${live.valid_yes}/${live.valid_yes_total || 1000}` : "—";
    const pipe = live.pipeline || {};
    const heroRow = (pipe.top_next || []).find((r) => r.id === "cp-a0c7c6c607") || (pipe.top_next || [])[0];

    const checkRows = checks
      .map(
        (c) => `
      <li class="sa-roster-row sa-aeg-check-row">
        <code>${esc(c.name || c.id)}</code>
        <span>${esc(c.reason || "")}</span>
        ${checkBadge(c.ok)}
      </li>`
      )
      .join("");

    panel.innerHTML = `
      <div class="sa-fleet-head">
        <span>AEG · automated evidence</span>
        <span class="sa-live sa-aeg-verdict-pill ${verdictClass(verdict)}">${esc(verdict)} · on site</span>
      </div>
      <div class="sa-aeg-hero-strip">
        <div class="sa-aeg-hero-metric">
          <strong>${esc(valid)}</strong>
          <span>Checks passing</span>
        </div>
        <div class="sa-aeg-hero-metric">
          <strong>${esc(String(eid).slice(-12))}</strong>
          <span>Evidence ID</span>
        </div>
        <div class="sa-aeg-hero-metric">
          <strong>${(live.metrics || {}).eval_scheduled || 0}</strong>
          <span>Evals live</span>
        </div>
      </div>
      <a class="sa-aeg-open-proof" href="${esc(url)}">
        <span class="sa-aeg-open-label">Open full forensic proof</span>
        <span class="sa-aeg-open-arrow">→</span>
      </a>
      <ul class="sa-roster sa-roster-biz">${checkRows}</ul>
      <div class="sa-w1-mini-terminal sa-aeg-mini-term">
        <pre class="sa-terminal-body sa-terminal-light-body">${colorizeTerminal(terminal || "$ sourcea-boot --json\n  loading transcript…")}</pre>
      </div>
      <div class="sa-receipt-feed sa-biz-activity">
        <article class="sa-receipt-card is-active sa-aeg-founder-card">
          <header><span class="hot">FOUNDER PICK</span><time>${esc((heroRow?.status || "").replace(/_/g, " "))}</time></header>
          <p><strong>${esc(heroRow?.company || "AEG prospect")}</strong> · ${esc(heroRow?.next_action || "Book eval")}</p>
          <p class="sa-aeg-proof-link"><a href="${esc(heroRow?.proof_url || url)}">${esc(heroRow?.proof_label || "Live proof URL")} →</a></p>
        </article>
      </div>`;
  }

  function renderOverview(panel, live) {
    const boot = live.boot || {};
    const m = live.metrics || {};
    const pipe = live.pipeline || {};
    panel.innerHTML = `
      <div class="sa-fleet-head">
        <span>Command center · live sample</span>
        <span class="sa-live">${boot.pass_count || 0}/${(boot.checks || []).length} checks · ${esc(boot.verdict || "—")}</span>
      </div>
      <div class="sa-fleet-stats">
        <div class="sa-metric"><strong>${m.active || 0}</strong><span>Active deals</span></div>
        <div class="sa-metric warn"><strong>${m.eval_scheduled || 0}</strong><span>Evals booked</span></div>
        <div class="sa-metric highlight"><strong>${m.proof_viewed || 0}</strong><span>Proof viewed</span></div>
      </div>
      <ul class="sa-roster sa-roster-biz">
        <li class="sa-roster-row"><code>Brain</code><span>${esc(live.queue_sa || "queue")}</span><span class="sa-v pass">ROUTING</span></li>
        <li class="sa-roster-row"><code>Outreach</code><span>${m.sent || 0} sent</span><span class="sa-v ${m.sent ? "pass" : ""}">${m.sent ? "LIVE" : "DRAFT"}</span></li>
        <li class="sa-roster-row"><code>Prove</code><span>${m.proof_viewed || 0} viewed</span><span class="sa-v pass">READY</span></li>
        <li class="sa-roster-row"><code>Guard</code><span>rules check</span>${checkBadge(boot.ok)}</li>
      </ul>
      <div class="sa-receipt-feed sa-biz-activity">
        <article class="sa-receipt-card is-active"><header><span class="${boot.ok ? "pass" : "block"}">${esc(boot.verdict || "BOOT")}</span><time>Now</time></header><p>${esc(live.factory_now_line || pipe.headline || "Factory sync")}</p></article>
      </div>`;
  }

  function renderPipeline(panel, live) {
    const pipe = live.pipeline || {};
    const counts = pipe.counts || {};
    const top = pipe.top_next || [];
    const rows = top
      .map(
        (r) => `
      <li class="sa-roster-row ${r.id === "cp-a0c7c6c607" ? "sa-aeg-founder-pick" : ""}" data-roster-agent="outreach">
        <code>${esc(r.lane || "AB1")}</code>
        <span>${esc(r.company || "prospect")}</span>
        <span class="sa-v ${r.status === "eval_scheduled" ? "pass" : ""}">${esc((r.status || "").replace(/_/g, " "))}</span>
      </li>`
      )
      .join("");
    panel.innerHTML = `
      <div class="sa-fleet-head">
        <span>Commercial pipeline</span>
        <span class="sa-live">${pipe.active_conversations || 0} active · SourceA only</span>
      </div>
      <div class="sa-fleet-stats">
        <div class="sa-metric"><strong>${counts.proof_viewed || 0}</strong><span>Proof viewed</span></div>
        <div class="sa-metric warn"><strong>${counts.eval_scheduled || 0}</strong><span>Eval scheduled</span></div>
        <div class="sa-metric highlight"><strong>${counts.pilot_deposit || 0}</strong><span>Deposits</span></div>
      </div>
      <ul class="sa-roster sa-roster-biz">${rows || '<li class="sa-roster-row"><code>—</code><span>No rows</span></li>'}</ul>
      <div class="sa-receipt-feed sa-biz-activity">
        ${top
          .slice(0, 3)
          .map(
            (r, i) => `
        <article class="sa-receipt-card ${i === 0 ? "is-active" : ""} ${r.id === "cp-a0c7c6c607" ? "sa-aeg-founder-card" : ""}">
          <header><span class="${r.id === "cp-a0c7c6c607" ? "hot" : "pass"}">${esc(r.lane || "AB1")}</span><time>${esc((r.status || "").replace(/_/g, " "))}</time></header>
          <p><strong>${esc(r.company || "")}</strong> · ${esc(r.next_action || "")}</p>
          ${r.proof_url ? `<p class="sa-aeg-proof-link"><a href="${esc(r.proof_url)}">${esc(r.proof_label || "Proof link")} →</a></p>` : ""}
        </article>`
          )
          .join("")}
      </div>`;
  }

  function renderOps(panel, live) {
    const checks = (live.boot || {}).checks || [];
    const rows = checks
      .map(
        (c) => `
      <li class="sa-roster-row">
        <code>${esc(c.name || c.id)}</code>
        <span>${esc(c.reason || "")}</span>
        ${checkBadge(c.ok)}
      </li>`
      )
      .join("");
    const blocks = checks.filter((c) => !c.ok);
    panel.innerHTML = `
      <div class="sa-fleet-head">
        <span>Ops monitor · policy at dispatch</span>
        <span class="sa-live">${blocks.length ? `${blocks.length} BLOCK` : "All PASS"}</span>
      </div>
      <div class="sa-fleet-stats">
        <div class="sa-metric"><strong>${checks.length}</strong><span>Boot checks</span></div>
        <div class="sa-metric warn"><strong>${blocks.length}</strong><span>Blocked</span></div>
        <div class="sa-metric highlight"><strong>${(live.boot || {}).pass_count || 0}</strong><span>Passed</span></div>
      </div>
      <ul class="sa-roster sa-roster-biz">${rows}</ul>
      <div class="sa-receipt-feed sa-biz-activity">
        ${blocks.length
          ? blocks
              .map(
                (c, i) => `
        <article class="sa-receipt-card ${i === 0 ? "is-active" : ""}">
          <header><span class="block">BLOCK</span><time>Now</time></header>
          <p><strong>${esc(c.name || "")}</strong> — ${esc(c.reason || "")}</p>
        </article>`
              )
              .join("")
          : '<article class="sa-receipt-card is-active"><header><span class="pass">PASS</span><time>Now</time></header><p>All boot checks passed.</p></article>'}
      </div>`;
  }

  function renderProof(panel, live) {
    const aeg = live.aeg || {};
    const boot = live.boot || {};
    const checks = boot.checks || [];
    const terminal = checks
      .map((c) => {
        const mark = c.ok ? "PASS" : "FAIL";
        const cls = c.ok ? "sa-t-ok" : "sa-t-bad";
        return `  <span class="${cls}">[${mark}]</span> ${esc(c.name)}: ${esc(c.reason)}`;
      })
      .join("\n");
    const proofUrl = live.aeg_live_url || "/sourcea/proof/live";
    panel.innerHTML = `
      <div class="sa-fleet-head">
        <span>Verification · replay</span>
        <span class="sa-live">${esc(boot.verdict || "—")} · disk</span>
      </div>
      <div class="sa-w1-mini-terminal">
        <pre class="sa-terminal-body sa-terminal-light-body"><span class="sa-t-prompt">$</span> sourcea-boot --json
<span class="${boot.ok ? "sa-t-ok" : "sa-t-bad"}">SOURCEA_BOOT ${esc(boot.verdict || "—")}</span>
${terminal}
<span class="sa-t-cursor">▋</span></pre>
      </div>
      <div class="sa-receipt-feed sa-biz-activity" style="margin-top:0.75rem">
        <article class="sa-receipt-card is-active"><header><span class="pass">AEG</span><time>${esc((aeg.evidence_id || "").slice(-8) || "live")}</time></header><p><a href="${esc(proofUrl)}">Full forensic page →</a> · <a href="/sourcea/scenario#proof-quiz">Gauntlet quiz →</a></p></article>
      </div>`;
  }

  const tabMeta = {
    aeg: {
      render: renderAeg,
      log: (l) => `AEG · ${(l.aeg || {}).evidence_id || "live"} · boot ${(l.boot || {}).verdict || "—"} · Valid YES ${l.valid_yes || "—"}`,
      role: "prove",
    },
    overview: { render: renderOverview, log: (l) => l.factory_now_line || (l.pipeline || {}).headline || "Factory overview", role: "brain" },
    pipeline: { render: renderPipeline, log: (l) => (l.pipeline || {}).headline || "Pipeline glance", role: "outreach" },
    ops: { render: renderOps, log: (l) => `Ops · ${(l.boot || {}).verdict || "—"} on boot`, role: "guard" },
    proof: { render: renderProof, log: (l) => `Replay · ${(l.boot || {}).verdict || "—"} · four checks`, role: "prove" },
  };

  async function fetchLive() {
    let live = null;
    try {
      const res = await fetch(DATA_URL, { cache: "no-store" });
      if (res.ok) live = await res.json();
    } catch (_) {
      /* fallback */
    }
    if (!live) {
      try {
        const bootRes = await fetch(BOOT_URL, { cache: "no-store" });
        if (bootRes.ok) {
          const boot = await bootRes.json();
          live = { boot, metrics: {}, pipeline: {}, factory_now_line: boot.founder_line };
        }
      } catch (_) {
        /* ignore */
      }
    }
    if (live && !live.aeg) {
      try {
        const aegRes = await fetch(AEG_URL, { cache: "no-store" });
        if (aegRes.ok) live.aeg = await aegRes.json();
      } catch (_) {
        /* ignore */
      }
    }
    return live;
  }

  function ensurePanels(panelRoot) {
    if (panelRoot.querySelector(".sa-biz-panel")) return panelRoot.querySelector(".sa-biz-panels");
    const wrap = document.createElement("div");
    wrap.className = "sa-biz-panels";
    wrap.setAttribute("role", "tabpanel");
    Object.keys(tabMeta).forEach((key, i) => {
      const p = document.createElement("div");
      p.className = `sa-biz-panel${key === "aeg" ? " is-active" : ""}`;
      p.dataset.bizPanel = key;
      wrap.appendChild(p);
    });
    [".sa-biz-activity", ".sa-roster-biz", ".sa-fleet-stats", ".sa-fleet-head", ".sa-w1-mini-terminal"].forEach((sel) => {
      panelRoot.querySelectorAll(sel).forEach((el) => el.remove());
    });
    panelRoot.appendChild(wrap);
    panelRoot.classList.add("is-live-panels");
    return wrap;
  }

  function highlightAgentRole(role) {
    document.querySelectorAll("[data-biz-role]").forEach((el) => {
      el.classList.toggle("is-running", el.dataset.bizRole === role);
    });
  }

  function paintPublicHero(panelRoot, live) {
    const m = live.metrics || {};
    const boot = live.boot || {};
    const pub = window.SourceAPublicDisplay && !window.SourceAPublicDisplay.isDevUi();
    const urlEl = panelRoot.querySelector(".sa-console-url");
    if (urlEl) urlEl.textContent = "Live workspace";
    const log = document.getElementById("sa-factory-log");
    if (log) {
      const viewed = m.proof_viewed || 0;
      log.textContent = pub
        ? `Latest job verified · ${viewed} demo${viewed === 1 ? "" : "s"} this week`
        : live.factory_now_line || "Factory sync";
      log.dataset.saLive = "1";
    }
    const pill = document.getElementById("sa-agent-pill-text");
    if (pill) {
      const verdict = pub
        ? window.SourceAPublicDisplay.humanizeGovernance(boot.verdict || "PASS")
        : boot.verdict || "live";
      pill.textContent = pub ? `Verified · ${verdict}` : `Live · ${verdict}`;
    }
    const livePill = panelRoot.querySelector(".sa-live-pill");
    if (livePill && pub) {
      const label = livePill.querySelector(".sa-live-dot")?.nextSibling;
      if (label && label.nodeType === Node.TEXT_NODE && label.textContent.trim() === "Done") {
        /* keep Done */
      }
    }
  }

  function paintHero(live) {
    const m = live.metrics || {};
    const boot = live.boot || {};
    const pill = document.getElementById("sa-agent-pill-text");
    if (pill) {
      const n = live.valid_yes;
      const total = live.valid_yes_total || 1000;
      const verdict = boot.verdict || (live.governance || {}).verdict || "live";
      // Factory pass · valid yes — baseline markers (ui-upgrade-baseline-v1.json)
      const checks = n != null ? `${n}/${total} checks` : "checks passing";
      pill.textContent = `Live proof · sample · ${verdict} · ${checks}`;
      pill.dataset.saLive = "1";
    }
    const orchMeta = document.getElementById("sa-orchestrator-meta");
    if (orchMeta) {
      orchMeta.textContent = `${m.active || 0} active · ${m.eval_scheduled || 0} evals · boot ${boot.verdict || "—"}`;
    }
    const chipMap = {
      outreach: `${m.sent || 0} sent · ${m.proof_viewed || 0} proof`,
      prove: `AEG live · ${(live.aeg || {}).verdict || boot.verdict || "—"}`,
      guard: `check ${boot.verdict || "—"}`,
      build: "2–3 wk DFY",
      expand: "retainer +$2K",
    };
    document.querySelectorAll("[data-biz-role]").forEach((el) => {
      const role = el.dataset.bizRole;
      const em = el.querySelector("em");
      if (em && chipMap[role]) em.textContent = chipMap[role];
    });
    const sync = document.querySelector(".sa-console-sync");
    if (sync) sync.classList.toggle("is-pass", !!boot.ok);
    const livePill = document.querySelector(".sa-live-pill");
    if (livePill) {
      livePill.classList.toggle("is-pass", !!boot.ok);
      livePill.classList.toggle("is-block", boot.verdict === "BLOCK");
    }
    document.querySelectorAll("[data-sa-live-metric]").forEach((el) => {
      const key = el.dataset.saLiveMetric;
      const val = m[key];
      if (val != null) el.textContent = String(val);
    });
  }

  async function init() {
    const panelRoot = document.getElementById("sa-biz-command");
    if (!panelRoot) return;

    const isPublicHero =
      panelRoot.classList.contains("sa-mock-panel") ||
      document.body.classList.contains("sa-root-home");

    const live = await fetchLive();
    if (!live) return;

    if (isPublicHero) {
      paintPublicHero(panelRoot, live);
      return;
    }

    paintHero(live);

    const urlEl = panelRoot.querySelector(".sa-console-url");
    if (urlEl && live.console_url) urlEl.textContent = live.console_url;

    const note = panelRoot.querySelector(".sa-metric-note");
    if (note) note.textContent = `Live factory · ${(live.at || "").slice(0, 19).replace("T", " ")} UTC · SourceA account`;

    const panelsWrap = ensurePanels(panelRoot);
    const tabs = panelRoot.querySelectorAll(".sa-biz-tab");
    const log = document.getElementById("sa-factory-log");

    Object.keys(tabMeta).forEach((key) => {
      const panel = panelsWrap.querySelector(`[data-biz-panel="${key}"]`);
      if (panel) tabMeta[key].render(panel, live);
    });

    const switchTab = (key) => {
      tabs.forEach((t) => {
        const on = t.dataset.bizTab === key;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      panelsWrap.querySelectorAll(".sa-biz-panel").forEach((p) => {
        p.classList.toggle("is-active", p.dataset.bizPanel === key);
      });
      panelRoot.classList.add("is-tab-switch");
      setTimeout(() => panelRoot.classList.remove("is-tab-switch"), 350);
      if (log && tabMeta[key]) streamText(log, tabMeta[key].log(live));
      if (tabMeta[key]?.role) highlightAgentRole(tabMeta[key].role);
    };

    tabs.forEach((tab) => {
      tab.setAttribute("role", "tab");
      tab.addEventListener("click", () => switchTab(tab.dataset.bizTab));
    });

    switchTab("aeg");

    if (!reduced && tabs.length) {
      const keys = Object.keys(tabMeta);
      let ti = 0;
      setInterval(() => {
        if (panelRoot.matches(":hover") || panelRoot.querySelector(":focus-within")) return;
        ti = (ti + 1) % keys.length;
        switchTab(keys[ti]);
      }, 8000);
    }
  }

  window.SourceALiveConsole = { init };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
