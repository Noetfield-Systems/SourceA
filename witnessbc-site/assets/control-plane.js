(function () {
  "use strict";

  var panel = document.querySelector(".control-plane-panel");
  if (!panel) return;

  var roster = panel.querySelector(".roster");
  var statsEl = panel.querySelector(".fleet-stats");
  var densityBtn = document.getElementById("controlPlaneDensity");
  if (!roster) return;

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var compact = false;

  var agents = [
    { name: "research-agent", score: "policy", verdict: "allow", code: "wbc.triage.complete", scenario: "publish" },
    { name: "outbound-agent", score: "human gate", verdict: "escalate", code: "wbc.review.pending", scenario: "outbound" },
    { name: "tool-call-agent", score: "ai-policy", verdict: "block", code: "wbc.policy.block", scenario: "tool" },
    { name: "publish-agent", score: "approve", verdict: "allow", code: "wbc.publish.sent", scenario: "publish" },
  ];

  var verdictCycle = ["allow", "escalate", "block", "allow"];
  var tick = 0;
  var statTargets = { active: 4, escalate: 2 };

  function setDensity(mode) {
    compact = mode === "compact";
    panel.classList.toggle("is-compact", compact);
    if (densityBtn) {
      densityBtn.textContent = compact ? "Detailed" : "Compact";
      densityBtn.setAttribute("aria-pressed", compact ? "true" : "false");
    }
    renderRoster(-1);
  }

  if (densityBtn) {
    densityBtn.addEventListener("click", function () {
      setDensity(compact ? "detailed" : "compact");
    });
  }

  function navigateToScenario(scenario) {
    if (!scenario) return;
    window.location.href = "proof.html#scenario=" + scenario;
  }

  function renderRoster(highlightIdx) {
    roster.innerHTML = agents
      .map(function (a, i) {
        var flash = i === highlightIdx ? ' class="verdict-flash"' : "";
        var codeHtml = compact
          ? ""
          : '<span class="receipt-code">' + a.code + "</span>";
        return (
          "<li" +
          flash +
          ' data-agent="' +
          a.name +
          '" data-scenario="' +
          a.scenario +
          '" tabindex="0" role="button" aria-label="Run ' +
          a.name +
          ' proof scenario">' +
          '<span class="agent">' +
          a.name +
          '</span><span class="score">' +
          a.score +
          "</span>" +
          codeHtml +
          '<span class="verdict ' +
          a.verdict +
          '">' +
          a.verdict.toUpperCase() +
          "</span>" +
          '<span class="roster-run-hint" aria-hidden="true">↗</span></li>'
        );
      })
      .join("");

    roster.querySelectorAll("li[data-scenario]").forEach(function (row) {
      row.addEventListener("click", function () {
        navigateToScenario(row.getAttribute("data-scenario"));
      });
      row.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          navigateToScenario(row.getAttribute("data-scenario"));
        }
      });
    });

    if (highlightIdx >= 0) {
      setTimeout(function () {
        var row = roster.querySelector(".verdict-flash");
        if (row) row.classList.remove("verdict-flash");
      }, 600);
    }
  }

  function pulseStat(el, value) {
    if (!el) return;
    var strong = el.querySelector("strong");
    if (strong) strong.textContent = String(value);
    el.classList.add("stat-pulse");
    setTimeout(function () {
      el.classList.remove("stat-pulse");
    }, 400);
  }

  function cycle() {
    tick += 1;
    var idx = tick % agents.length;
    var nextVerdict = verdictCycle[tick % verdictCycle.length];
    agents[idx].verdict = nextVerdict;

    if (nextVerdict === "escalate") {
      statTargets.escalate = Math.min(4, statTargets.escalate + (tick % 2 === 0 ? 1 : 0));
    } else if (nextVerdict === "allow") {
      statTargets.escalate = Math.max(1, statTargets.escalate - (tick % 3 === 0 ? 1 : 0));
    }

    renderRoster(idx);

    if (statsEl && !compact) {
      var statDivs = statsEl.querySelectorAll("div");
      pulseStat(statDivs[0], statTargets.active);
      if (statDivs[1]) pulseStat(statDivs[1], statTargets.escalate);
    }
  }

  setDensity("detailed");
  if (!reducedMotion) {
    setInterval(cycle, 5000);
  }
})();
