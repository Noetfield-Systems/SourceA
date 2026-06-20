(function () {
  "use strict";

  var URL = "data/trust-signals.json";

  function paint(root, data) {
    if (!root || !data) return;

    var valid = root.querySelector("[data-trust-valid-yes]");
    if (valid && data.valid_yes != null) {
      var total = data.valid_yes_total || 1000;
      valid.textContent = data.valid_yes + "/" + total;
      valid.setAttribute("title", data.factory_now_line || "Factory truth bundle");
    }

    var rc = root.querySelector("[data-trust-receipts]");
    if (rc) {
      rc.textContent = String(Number(data.receipts_signed_today) || 0);
      var label = data.receipt_metric_label || "Governance events today";
      rc.setAttribute(
        "title",
        rc.textContent + " " + label.toLowerCase() + " · " + (data.receipts_date || "today")
      );
    }

    var rcLabel = root.querySelector("[data-trust-receipts-label]");
    if (rcLabel && data.receipt_metric_label) {
      rcLabel.textContent = data.receipt_metric_label;
    }

    var gov = root.querySelector("[data-trust-governance]");
    if (gov && data.governance) {
      var v = data.governance.verdict || "UNKNOWN";
      gov.textContent = v;
      gov.classList.toggle("is-pass", v === "PASS");
      gov.classList.toggle("is-block", v === "BLOCK");
    }

    var deploy = root.querySelector("[data-trust-deploy]");
    if (deploy && data.deploy) {
      deploy.textContent = data.deploy.status || "ship-local";
    }

    var at = root.querySelector("[data-trust-at]");
    if (at && data.at) {
      at.textContent = data.at.slice(0, 10);
      at.setAttribute("title", data.at);
    }
  }

  function init() {
    document.querySelectorAll("[data-wbc-trust-bar]").forEach(function (root) {
      fetch(URL, { cache: "no-store" })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          paint(root, data);
          root.classList.remove("is-stale");
        })
        .catch(function () {
          root.classList.add("is-stale");
        });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
