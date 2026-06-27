/**
 * Customer-facing display — humanize internal IDs on public pages (not eval/proof dev UI).
 */
(function () {
  "use strict";

  const BLUEPRINT_LABELS = {
    "MAC-CTL-002": "Security review",
    "MAC-CTL-001": "Platform review",
    "CLOUD-SEC-052": "Cloud security",
    "CLOUD-SEC-053": "Cloud security",
  };

  const VERDICT_LABELS = {
    APPROVED: "Approved",
    PASS: "Verified",
    BLOCK: "Needs review",
    FAIL: "Needs review",
    FROZEN: "Paused",
    LIVE: "Live",
  };

  function isDevUi() {
    const b = document.body;
    if (!b) return false;
    return b.dataset.saDevUi === "1" || b.classList.contains("sa-dev-ui");
  }

  function humanizePackId(id) {
    const raw = String(id || "");
    const m = raw.match(/pp-(\d{4})(\d{2})(\d{2})/);
    if (m) {
      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const mo = months[Math.max(0, parseInt(m[2], 10) - 1)] || m[2];
      return `Sample job · ${mo} ${parseInt(m[3], 10)}, ${m[1]}`;
    }
    return "Sample client job";
  }

  function humanizeVerdict(v) {
    const key = String(v || "").toUpperCase();
    return VERDICT_LABELS[key] || "Complete";
  }

  function humanizeBlueprint(id) {
    const raw = String(id || "");
    if (BLUEPRINT_LABELS[raw]) return BLUEPRINT_LABELS[raw];
    if (/MAC-CTL/i.test(raw)) return "Security review";
    if (/CLOUD-SEC/i.test(raw)) return "Cloud security";
    return "Custom project";
  }

  function humanizeQueue() {
    return "Ready for client call";
  }

  function humanizeGovernance(v) {
    return humanizeVerdict(v);
  }

  function humanizeReceiptId(id) {
    return isDevUi() ? String(id || "") : "Job record";
  }

  function paintPhase0Proof(proof) {
    if (!proof) return;
    const dev = isDevUi();
    const pd = proof.public_display || {};
    const set = (sel, val) => {
      const el = document.querySelector(sel);
      if (el && val != null) el.textContent = String(val);
    };
    set(
      "[data-phase0-pack-id]",
      dev ? proof.pack_id : pd.job_label || humanizePackId(proof.pack_id)
    );
    set(
      "[data-phase0-verdict]",
      dev ? proof.verdict : pd.result || humanizeVerdict(proof.verdict)
    );
    set("[data-phase0-score]", proof.truth_gate_score);
    set(
      "[data-phase0-blueprint]",
      dev ? proof.blueprint_id : pd.project_type || humanizeBlueprint(proof.blueprint_id)
    );
    set(
      "[data-phase0-queue], [data-phase0-status]",
      dev ? proof.queue_completed : pd.status || humanizeQueue()
    );
  }

  window.SourceAPublicDisplay = {
    isDevUi,
    humanizePackId,
    humanizeVerdict,
    humanizeBlueprint,
    humanizeQueue,
    humanizeGovernance,
    humanizeReceiptId,
    paintPhase0Proof,
  };
})();
