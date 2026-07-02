/**
 * SourceA site fallback — instant paint before fetch (proof + trust).
 * Synced from phase1-proof-pack-public-v1.json + trust-signals.json on deploy.
 */
(function () {
  const TRUST = {
    schema: "sourcea-trust-signals-v1",
    receipts_signed_lifetime: 5655,
    receipts_signed_today: 4,
    receipts_lifetime_label: "jobs verified for clients",
    receipts_metric_label: "Jobs verified today",
    receipts_date: "2026-06-24",
    valid_yes: 98,
    valid_yes_total: 100,
    governance: { verdict: "PASS", factory: "Paused", status: "operational" },
    github: { ok: true, url: "https://pypi.org/project/sourcea-boot/" },
    status_page: "/sourcea/status",
    proof_sample: "/sourcea/attach/proof-bundle-sample",
    api_hook: { endpoint: "POST /v1/check", verdict: "PASS", receipt_id: "job-record" },
  };

  const PROOF = {
    schema: "sourcea-phase1-proof-pack-public-v1",
    pack_id: "pp-20260624T052230Z-c3857002",
    truth_gate_score: 98,
    verdict: "APPROVED",
    blueprint_id: "Sample job",
    queue_completed: "Complete",
    prove_summary: "All checks passed · verify in your browser",
    seal_hash_prefix: "225d90aaba2deec9",
  };

  const FACTORY = {
    boot: { verdict: "PASS", ok: true },
    metrics: { proof_viewed: 3, eval_scheduled: 1, active: 4 },
    factory_now_line: "Latest job verified · proof ready to share",
  };

  function fmtCount(n) {
    const x = Number(n) || 0;
    return x.toLocaleString("en-US");
  }

  function humanGov(v) {
    if (window.SourceAPublicDisplay && !window.SourceAPublicDisplay.isDevUi()) {
      return window.SourceAPublicDisplay.humanizeGovernance(v);
    }
    return v === "APPROVED" ? "Approved" : v;
  }

  function setAll(sel, val) {
    if (val == null) return;
    document.querySelectorAll(sel).forEach((el) => {
      el.textContent = String(val);
    });
  }

  function paintTrust(data) {
    if (!data) return;
    setAll("[data-trust-receipts-lifetime]", data.receipts_signed_lifetime ? fmtCount(data.receipts_signed_lifetime) : null);
    setAll("[data-trust-receipts]", String(data.receipts_signed_today ?? ""));
    setAll("[data-trust-valid-yes]", data.valid_yes != null ? data.valid_yes + "/" + (data.valid_yes_total || 100) : null);
    const gov = data.governance || {};
    document.querySelectorAll("[data-trust-governance]").forEach((el) => {
      const raw = gov.verdict || "PASS";
      el.textContent = humanGov(raw);
      el.classList.toggle("is-pass", raw === "PASS" || raw === "APPROVED");
    });
    document.querySelectorAll("[data-trust-receipts-lifetime-label]").forEach((el) => {
      if (data.receipts_lifetime_label) el.textContent = data.receipts_lifetime_label;
    });
    document.querySelectorAll("[data-trust-github-stars]").forEach((el) => {
      el.textContent = data.github && data.github.ok ? "★" : "Eval";
    });
  }

  function paintProof(proof) {
    if (!proof) return;
    if (window.SourceAPublicDisplay) {
      window.SourceAPublicDisplay.paintPhase0Proof(proof);
    } else {
      setAll("[data-phase0-pack-id]", proof.pack_id ? proof.pack_id.slice(-12) : null);
      setAll("[data-phase0-verdict]", humanGov(proof.verdict));
      setAll("[data-phase0-score]", proof.truth_gate_score);
      setAll("[data-phase0-blueprint]", proof.blueprint_id);
      setAll("[data-phase0-queue]", proof.queue_completed);
    }
    setAll("[data-proof-seal]", proof.seal_hash_prefix);
    setAll("[data-proof-summary]", proof.prove_summary);
  }

  function paintFactoryHero(data) {
    const log = document.getElementById("sa-factory-log");
    if (!log || log.dataset.saLive === "1") return;
    const m = data.metrics || {};
    const pub = window.SourceAPublicDisplay && !window.SourceAPublicDisplay.isDevUi();
    const viewed = m.proof_viewed || 0;
    log.textContent = pub
      ? `Latest job verified · ${viewed} demo${viewed === 1 ? "" : "s"} scheduled`
      : data.factory_now_line || "Latest job verified · proof ready";
    log.dataset.saLive = "1";
  }

  function paintReceiptCard(root) {
    if (!root || !PROOF) return;
    const pub = window.SourceAPublicDisplay && !window.SourceAPublicDisplay.isDevUi();
    const packLabel = pub
      ? window.SourceAPublicDisplay.humanizePackId(PROOF.pack_id)
      : PROOF.pack_id ? PROOF.pack_id.slice(-16) : "";
    const verdictLabel = pub
      ? window.SourceAPublicDisplay.humanizeVerdict(PROOF.verdict)
      : PROOF.verdict;
    root.querySelectorAll("[data-proof-receipt-pack]").forEach((el) => {
      el.textContent = packLabel;
    });
    root.querySelectorAll("[data-proof-receipt-verdict]").forEach((el) => {
      el.textContent = verdictLabel;
      el.classList.add("is-pass");
    });
    root.querySelectorAll("[data-proof-receipt-score]").forEach((el) => {
      el.textContent = String(PROOF.truth_gate_score) + "/100";
    });
    root.querySelectorAll("[data-proof-receipt-seal]").forEach((el) => {
      el.textContent = pub ? PROOF.seal_hash_prefix.slice(0, 8) + "…" : PROOF.seal_hash_prefix || "";
    });
    root.querySelectorAll("[data-proof-receipt-summary]").forEach((el) => {
      el.textContent = PROOF.prove_summary || "";
    });
  }

  function paintAll() {
    paintTrust(TRUST);
    paintProof(PROOF);
    paintFactoryHero(FACTORY);
    document.querySelectorAll("[data-sa-proof-receipt]").forEach(paintReceiptCard);
  }

  window.SourceASiteFallback = {
    TRUST,
    PROOF,
    FACTORY,
    paintTrust,
    paintProof,
    paintFactoryHero,
    paintReceiptCard,
    paintAll,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", paintAll);
  } else {
    paintAll();
  }
})();
