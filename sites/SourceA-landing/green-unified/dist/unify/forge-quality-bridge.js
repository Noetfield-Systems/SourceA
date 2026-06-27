(function () {
  "use strict";
  /** Parent Connect shell → iframe token bridge + Verify tab quality lookup */
  document.addEventListener("DOMContentLoaded", function () {
    fetch(window.location.origin + "/health")
      .then(function (r) { return r.json(); })
      .then(function (h) {
        var token = h.forge_local_token || "";
        if (!token) return;
        var frame = document.getElementById("forge-ide-frame");
        if (frame) {
          frame.addEventListener("load", function () {
            try {
              frame.contentWindow.postMessage({ type: "forge-token", token: token }, window.location.origin);
            } catch (_) { /* cross-origin guard */ }
          });
        }
      })
      .catch(function () { /* quiet */ });

    window.addEventListener("message", function (ev) {
      if (ev.data && ev.data.type === "forge-token-ready" && ev.data.token) {
        sessionStorage.setItem("forge_local_token", ev.data.token);
      }
    });
  });

  window.forgeQualityLookupRunId = function (runId, onResult) {
    if (!runId) return;
    fetch(window.location.origin + "/api/forge-terminal/v1", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Forge-Token": sessionStorage.getItem("forge_local_token") || "" },
      body: JSON.stringify({ action: "quality_receipt", run_id: runId }),
    })
      .then(function (r) { return r.json(); })
      .then(function (row) {
        if (typeof onResult === "function") onResult(row);
      })
      .catch(function () { /* quiet */ });
  };

  document.addEventListener("DOMContentLoaded", function () {
    var paste = document.getElementById("input-paste");
    if (!paste) return;
    paste.addEventListener("blur", function () {
      var m = (paste.value || "").match(/ft-[a-f0-9]{8,16}/i);
      if (!m) return;
      window.forgeQualityLookupRunId(m[0], function (row) {
        var qg = row.quality_gate || {};
        if (!qg.verdict) return;
        var line = document.getElementById("home-health-line");
        if (line) line.textContent = "Quality " + qg.verdict + " · " + (qg.passed_layers || 0) + "/" + (qg.total_layers || 11);
      });
    });
  });
})();
