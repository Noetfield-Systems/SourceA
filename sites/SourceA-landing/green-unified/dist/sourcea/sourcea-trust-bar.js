/**
 * Buyer 1 trust bar — Valid YES, governance boot, GitHub eval, proof sample,
 * lifetime receipt ticker, platform API hook, powered-by hero strip.
 * Data: /sourcea/data/trust-signals.json (injected on deploy recipe).
 */
(function () {
  const URL = "/sourcea/data/trust-signals.json";
  const TRUST_VERDICT_TEXT = "valid yes";

  function fmtStars(n) {
    const x = Number(n) || 0;
    if (x >= 1000) return (x / 1000).toFixed(1).replace(/\.0$/, "") + "k";
    return String(x);
  }

  function fmtCount(n) {
    const x = Number(n) || 0;
    return x.toLocaleString("en-US");
  }

  function relTime(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "";
    const diff = Date.now() - d.getTime();
    const days = Math.floor(diff / 86400000);
    if (days < 1) return "today";
    if (days === 1) return "1d ago";
    if (days < 30) return days + "d ago";
    return d.toISOString().slice(0, 10);
  }

  function paintBuiltOn(data, selector) {
    document.querySelectorAll(selector).forEach((ul) => {
      if (!data.built_on || !data.built_on.length) return;
      ul.innerHTML = data.built_on
        .map((row) => {
          const label = row.label || row.id || "";
          const note = row.note ? ' title="' + row.note.replace(/"/g, "&quot;") + '"' : "";
          return "<li" + note + ">" + label + "</li>";
        })
        .join("");
    });
  }

  function publicUi() {
    return window.SourceAPublicDisplay && !window.SourceAPublicDisplay.isDevUi();
  }

  function paintApiHook(data) {
    const hook = data.api_hook || {};
    const pub = publicUi();
    document.querySelectorAll("[data-trust-api-endpoint]").forEach((el) => {
      if (hook.endpoint) el.textContent = pub ? "POST /v1/check" : hook.endpoint;
    });
    document.querySelectorAll("[data-trust-api-verdict]").forEach((el) => {
      if (hook.verdict) {
        const v = pub ? window.SourceAPublicDisplay.humanizeVerdict(hook.verdict) : hook.verdict;
        el.textContent = '"' + v + '"';
        el.classList.toggle("is-pass", hook.verdict === "PASS" || hook.verdict === "APPROVED");
        el.classList.toggle("is-block", hook.verdict === "BLOCK");
      }
    });
    document.querySelectorAll("[data-trust-api-receipt]").forEach((el) => {
      if (hook.receipt_id) {
        el.textContent = '"' + (pub ? "job-record" : hook.receipt_id) + '"';
      }
    });
    document.querySelectorAll("[data-trust-api-signed]").forEach((el) => {
      if (hook.signed_at) {
        el.textContent = pub
          ? '"just now"'
          : '"' + String(hook.signed_at).slice(0, 19) + 'Z"';
      }
    });
  }

  function paintReceipts(data) {
    const lifetime = document.querySelectorAll("[data-trust-receipts-lifetime]");
    const lifetimeN = Number(data.receipts_signed_lifetime) || 0;
    lifetime.forEach((el) => {
      el.textContent = lifetimeN ? fmtCount(lifetimeN) : "—";
      el.setAttribute("title", data.receipts_lifetime_label || "Governance receipts on disk");
    });
    const lifetimeLabel = document.querySelectorAll("[data-trust-receipts-lifetime-label]");
    lifetimeLabel.forEach((el) => {
      if (data.receipts_lifetime_label) el.textContent = data.receipts_lifetime_label;
    });
    document.querySelectorAll("[data-trust-receipts]").forEach((rc) => {
      const n = Number(data.receipts_signed_today) || 0;
      rc.textContent = String(n);
      const label = data.receipt_metric_label || "Governance events today";
      rc.setAttribute("title", n + " " + label.toLowerCase() + " · " + (data.receipts_date || "today"));
    });
    const rcLabel = document.querySelectorAll("[data-trust-receipts-label]");
    rcLabel.forEach((el) => {
      if (data.receipt_metric_label) el.textContent = data.receipt_metric_label;
    });
  }

  function paintFactoryChip(data) {
    const pill = document.getElementById("sa-agent-pill-text");
    if (!pill || !data) return;
    pill.dataset.saFactoryVerdict = TRUST_VERDICT_TEXT;
    const n = data.valid_yes;
    const total = data.valid_yes_total || 1000;
    const gov = data.governance || {};
    const rawVerdict = gov.verdict || "live";
    const verdict = publicUi() ? window.SourceAPublicDisplay.humanizeGovernance(rawVerdict) : rawVerdict;
    const checks = n != null ? `${n}/${total} checks` : "checks passing";
    pill.textContent = publicUi()
      ? `Live demo · ${verdict} · ${checks}`
      : `Live proof · sample · ${verdict} · ${checks}`;
    pill.dataset.saLive = "1";
  }

  function paint(root, data) {
    if (!data) return;

    const valid = root.querySelector("[data-trust-valid-yes]");
    if (valid) {
      const n = data.valid_yes;
      const total = data.valid_yes_total || 1000;
      valid.textContent = n != null ? n + "/" + total : "—";
      valid.setAttribute("title", data.factory_now_line || "Factory truth bundle");
    }

    paintReceipts(data);

    const gh = root.querySelector("[data-trust-github-stars]");
    if (gh && data.github) {
      gh.textContent = data.github.ok ? fmtStars(data.github.stars) : "Eval";
    }

    const ghi = root.querySelector("[data-trust-github-issues]");
    if (ghi && data.github) {
      ghi.textContent = data.github.ok ? String(data.github.open_issues || 0) : "—";
    }

    const ghp = root.querySelector("[data-trust-github-pushed]");
    if (ghp && data.github) {
      ghp.textContent = data.github.ok ? relTime(data.github.pushed_at) : "repo pending";
    }

    const gov = root.querySelector("[data-trust-governance]");
    if (gov && data.governance) {
      const raw = data.governance.verdict || "UNKNOWN";
      const v = publicUi() ? window.SourceAPublicDisplay.humanizeGovernance(raw) : raw;
      gov.textContent = v;
      gov.classList.toggle("is-pass", raw === "PASS" || raw === "APPROVED");
      gov.classList.toggle("is-block", raw === "BLOCK");
    }

    const fac = root.querySelector("[data-trust-factory]");
    if (fac && data.governance) {
      const rawFac = data.governance.factory || "—";
      fac.textContent = publicUi() && rawFac === "FROZEN" ? "Paused" : rawFac === "LIVE" ? "Active" : rawFac;
      fac.classList.toggle("is-frozen", data.governance.factory === "FROZEN");
    }

    const ghLink = root.querySelector("[data-trust-github-link]");
    if (ghLink && data.github && data.github.url) {
      ghLink.href = data.github.url;
      if (!data.github.ok) {
        ghLink.setAttribute("title", "Public eval repo — stars when published");
      }
    }

    const statusLink = root.querySelector("[data-trust-status-link]");
    if (statusLink && data.status_page) {
      statusLink.href = data.status_page;
    }

    const sampleLink = root.querySelector("[data-trust-sample-link]");
    if (sampleLink && data.proof_sample) {
      sampleLink.href = data.proof_sample;
    }

    paintBuiltOn(data, "[data-trust-built-on]");
  }

  function init() {
    if (window.SourceASiteFallback) {
      window.SourceASiteFallback.paintTrust(window.SourceASiteFallback.TRUST);
    }
    fetch(URL, { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error("trust fetch");
        const ct = (r.headers.get("content-type") || "").toLowerCase();
        if (ct.includes("text/html")) throw new Error("html not json");
        return r.json();
      })
      .then((data) => {
        document.querySelectorAll("[data-sa-trust-bar]").forEach((root) => paint(root, data));
        paintBuiltOn(data, "[data-trust-built-on-hero]");
        paintReceipts(data);
        paintApiHook(data);
        paintFactoryChip(data);
        if (window.SourceASiteFallback) window.SourceASiteFallback.paintTrust(data);
      })
      .catch(() => {
        if (window.SourceASiteFallback) {
          window.SourceASiteFallback.paintTrust(window.SourceASiteFallback.TRUST);
        } else {
          document.querySelectorAll("[data-sa-trust-bar]").forEach((root) => root.classList.add("is-stale"));
        }
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
