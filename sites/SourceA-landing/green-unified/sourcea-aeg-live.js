/**
 * Live AEG forensic proof — buyer-facing panel on /sourcea/proof/live
 * Data: aeg-live.json + factory-live.json (injected on deploy)
 */
(function () {
  const AEG_URL = "/sourcea/data/aeg-live.json";
  const FACTORY_URL = "/sourcea/data/factory-live.json";

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function paintChecks(root, checks) {
    if (!root || !checks || !checks.length) return;
    root.innerHTML = checks
      .map(function (c) {
        var ok = c.ok;
        var mark = ok ? "PASS" : "FAIL";
        var cls = ok ? "sa-t-ok" : "sa-t-bad";
        var name = c.name || c.id || "check";
        var reason = c.reason || "";
        return (
          '<div class="sa-aeg-check">' +
          '<span class="' + cls + '">[' + mark + "]</span> " +
          esc(name) +
          (reason ? ": " + esc(reason) : "") +
          "</div>"
        );
      })
      .join("");
  }

  function paintPipeline(factory) {
    if (!factory) return;
    var pipe = factory.pipeline || {};
    var counts = pipe.counts || {};
    var m = factory.metrics || {};
    var pv = $("sa-aeg-proof-viewed");
    var ev = $("sa-aeg-eval-scheduled");
    var dep = $("sa-aeg-deposits");
    if (pv) pv.textContent = String(counts.proof_viewed != null ? counts.proof_viewed : m.proof_viewed || 0);
    if (ev) ev.textContent = String(counts.eval_scheduled != null ? counts.eval_scheduled : m.eval_scheduled || 0);
    if (dep) dep.textContent = String(counts.pilot_deposit != null ? counts.pilot_deposit : 0);
    var rows = $("sa-aeg-pipeline-rows");
    if (!rows) return;
    var top = pipe.top_next || [];
    if (!top.length) {
      rows.innerHTML = '<li><code>—</code><span>No pipeline rows logged</span><span class="sa-v">—</span></li>';
      return;
    }
    rows.innerHTML = top
      .map(function (r) {
        var founder = r.id === "cp-a0c7c6c607" || r.founder_pick;
        var status = String(r.status || "").replace(/_/g, " ");
        var cls = r.status === "eval_scheduled" ? "pass" : "";
        return (
          '<li class="' + (founder ? "is-founder" : "") + '">' +
          "<code>" + esc(r.lane || "AB1") + "</code>" +
          "<span><strong>" + esc(r.company || "prospect") + "</strong> · " + esc(r.next_action || "") + "</span>" +
          '<span class="sa-v ' + cls + '">' + esc(status) + "</span>" +
          "</li>"
        );
      })
      .join("");
  }

  function paint(data, factory) {
    if (!data) return;
    var verdict = String(data.verdict || data.boot_verdict || "UNKNOWN");
    var hero = $("sa-aeg-verdict");
    if (hero) {
      hero.textContent = verdict;
      hero.classList.toggle("is-pass", verdict === "PASS");
      hero.classList.toggle("is-block", verdict === "BLOCK");
    }
    var eid = $("sa-aeg-evidence");
    if (eid && data.evidence_id) {
      eid.textContent = "Evidence ID · " + data.evidence_id;
    }
    var meta = $("sa-aeg-meta");
    if (meta) {
      var parts = [];
      if (data.hosted_at) parts.push("Synced " + String(data.hosted_at).slice(0, 19).replace("T", " UTC"));
      if (factory && factory.valid_yes != null) {
        parts.push("Valid YES " + factory.valid_yes + "/" + (factory.valid_yes_total || 1000));
      }
      if (data.evidence_id) parts.push(data.evidence_id);
      meta.textContent = parts.join(" · ");
    }
    var blockers = $("sa-aeg-blockers");
    if (blockers) {
      var list = data.blockers || [];
      blockers.innerHTML = list.length
        ? "<ul>" + list.map(function (b) { return "<li>" + esc(b) + "</li>"; }).join("") + "</ul>"
        : "<p>No blockers — factory boot PASS.</p>";
    }
    var term = $("sa-aeg-terminal");
    if (term && data.terminal_transcript) {
      term.textContent = data.terminal_transcript;
    }
    paintChecks($("sa-aeg-checks"), data.checks);
    paintPipeline(factory);
    var sync = $("sa-aeg-sync");
    if (sync) {
      var line = factory && factory.factory_now_line ? factory.factory_now_line : data.disclaimer || "Live from factory repository";
      sync.textContent = line;
    }
  }

  function readBootstrap() {
    var el = document.getElementById("sa-aeg-bootstrap");
    if (!el || !el.textContent) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return null;
    }
  }

  function init() {
    var boot = readBootstrap();
    if (boot && boot.aeg) {
      paint(boot.aeg, boot.factory || null);
    }
    Promise.all([
      fetch(AEG_URL, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }),
      fetch(FACTORY_URL, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }),
    ]).then(function (res) {
      if (res[0]) paint(res[0], res[1]);
      else {
        var sync = $("sa-aeg-sync");
        if (sync) sync.textContent = "Could not load aeg-live.json — run landing deploy recipe.";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
