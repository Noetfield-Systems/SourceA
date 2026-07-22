(function () {
  "use strict";

  var FILM_STEPS = [
    { label: "Request received", film: 0 },
    { label: "Policy evaluation at dispatch", film: 1 },
    { label: "Decision: ALLOW / BLOCK / ESCALATE", film: 2 },
    { label: "Human gate when required", film: 3 },
    { label: "Signed receipt on disk", film: 4 },
    { label: "Replay from ledger", film: 5 },
    { label: "Tamper-FAIL on hand edit", film: 6 },
  ];

  var PROGRESS_KEY = "witnessbc-proof-explored-v1";

  var body = document.getElementById("proofTerminalBody");
  var terminal = document.getElementById("proofTerminal");
  var cursor = document.getElementById("proofTerminalCursor");
  var cardsWrap = document.getElementById("proofScenarioCards");
  var pillsWrap = document.getElementById("proofScenarioPills");
  var verdictLive = document.getElementById("proofVerdictLive");
  var filmToggle = document.getElementById("proofFilmToggle");
  var filmStrip = document.getElementById("proofFilmStrip");
  var evidencePanel = document.getElementById("proofEvidencePanel");
  var evidenceCards = document.getElementById("proofEvidenceCards");
  var artifactList = document.getElementById("proofArtifactList");
  var replayPrev = document.getElementById("proofReplayPrev");
  var replayNext = document.getElementById("proofReplayNext");
  var replayPlay = document.getElementById("proofReplayPlay");
  var replayStep = document.getElementById("proofReplayStep");
  var scrubber = document.getElementById("proofScrubber");
  var tamperBtn = document.getElementById("proofTamperBtn");
  var receiptJson = document.getElementById("proofReceiptJson");
  var copyHashBtn = document.getElementById("proofCopyHash");
  var progressCount = document.getElementById("proofProgressCount");
  var progressFill = document.getElementById("proofProgressFill");
  var labGrid = document.getElementById("proofLabGrid");

  if (!body || !terminal) return;

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var scenarios = {};
  var scenarioOrder = [];
  var currentScenario = null;
  var currentSteps = [];
  var stepIndex = 0;
  var replayMode = false;
  var autoPlaying = !reducedMotion;
  var tampered = false;
  var paused = false;
  var timer = null;
  var filmTimer = null;
  var filmPlaying = false;
  var filmIdx = 0;
  var typewriterTimer = null;
  var explored = loadExplored();

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function badgeClass(verdict) {
    var v = (verdict || "").toLowerCase();
    if (v === "block") return "block";
    if (v === "escalate") return "escalate";
    if (v === "fail") return "fail";
    return "allow";
  }

  function loadExplored() {
    try {
      var raw = localStorage.getItem(PROGRESS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveExplored() {
    try {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(explored));
    } catch (e) {
      /* ignore */
    }
  }

  function markExplored(slug) {
    if (explored.indexOf(slug) === -1) {
      explored.push(slug);
      saveExplored();
    }
    updateProgressUI();
  }

  function updateProgressUI() {
    var total = scenarioOrder.length || 6;
    var count = explored.length;
    if (progressCount) progressCount.textContent = count + " / " + total;
    if (progressFill) progressFill.style.width = total ? Math.round((count / total) * 100) + "%" : "0%";
    if (cardsWrap) {
      cardsWrap.querySelectorAll(".proof-scenario-card").forEach(function (card) {
        var slug = card.getAttribute("data-scenario");
        card.classList.toggle("is-explored", explored.indexOf(slug) !== -1);
      });
    }
  }

  function setVerdict(text) {
    if (verdictLive) verdictLive.textContent = text || "";
  }

  function highlightPhase(phase) {
    document.querySelectorAll(".proof-chain-step").forEach(function (el) {
      var film = el.getAttribute("data-film");
      if (film !== null) {
        el.classList.toggle("active", parseInt(film, 10) === phase);
      }
    });
    if (scrubber) {
      var gate = Math.min(5, Math.max(0, phase));
      document.querySelectorAll(".proof-scrubber-gates span").forEach(function (el, idx) {
        var g = el.getAttribute("data-gate");
        var match = g !== null ? parseInt(g, 10) === gate : idx === gate;
        el.classList.toggle("active", match);
      });
    }
  }

  function highlightFilm(idx) {
    if (!filmStrip) return;
    filmStrip.querySelectorAll(".proof-chain-step").forEach(function (el) {
      var f = el.getAttribute("data-film");
      el.classList.toggle("active", f !== null && parseInt(f, 10) === idx);
    });
    var step = FILM_STEPS[idx];
    if (step) setVerdict("Film: " + step.label);
  }

  function stopFilm() {
    filmPlaying = false;
    if (filmTimer) clearInterval(filmTimer);
    filmTimer = null;
    if (filmToggle) {
      filmToggle.textContent = "Play film strip";
      filmToggle.setAttribute("aria-pressed", "false");
    }
  }

  function startFilm() {
    if (reducedMotion) return;
    stopFilm();
    replayMode = false;
    autoPlaying = false;
    updatePlayBtn();
    filmPlaying = true;
    filmIdx = 0;
    if (filmToggle) {
      filmToggle.textContent = "Pause film strip";
      filmToggle.setAttribute("aria-pressed", "true");
    }
    highlightFilm(0);
    filmTimer = setInterval(function () {
      filmIdx = (filmIdx + 1) % FILM_STEPS.length;
      highlightFilm(filmIdx);
    }, 2143);
  }

  if (filmToggle) {
    filmToggle.addEventListener("click", function () {
      if (filmPlaying) stopFilm();
      else startFilm();
    });
  }

  function updateEvidencePanel(scenario) {
    if (!evidencePanel || !scenario) return;
    var badge = evidencePanel.querySelector(".proof-evidence-verdict");
    var rule = evidencePanel.querySelector("[data-evidence-rule]");
    var excerpt = evidencePanel.querySelector("[data-evidence-excerpt]");
    var hash = evidencePanel.querySelector("[data-evidence-hash]");
    var ts = evidencePanel.querySelector("[data-evidence-ts]");
    var narrative = evidencePanel.querySelector("[data-evidence-narrative]");

    if (badge) {
      badge.textContent = tampered ? "tamper-FAIL" : scenario.verdict;
      badge.className = "proof-evidence-verdict verdict-" + (tampered ? "fail" : badgeClass(scenario.verdict));
    }
    if (rule) rule.textContent = scenario.policy_rule;
    if (excerpt) excerpt.textContent = scenario.policy_excerpt;
    if (hash) {
      hash.textContent = tampered
        ? scenario.receipt_hash.replace(/[a-f0-9]{4}…[a-f0-9]{4}/, "0000…dead (mutated)")
        : scenario.receipt_hash;
    }
    if (ts) ts.textContent = scenario.timestamp;
    if (narrative) narrative.textContent = scenario.narrative;
    if (receiptJson) {
      var receipt = JSON.parse(JSON.stringify(scenario.receipt));
      if (tampered && receipt.verdict) {
        receipt.verdict = receipt.tamper_mutated || "BLOCK";
        receipt.integrity = "FAIL";
        receipt.signature = "INVALID (tampered)";
      }
      receiptJson.textContent = JSON.stringify(receipt, null, 2);
    }
    renderArtifactList(scenario);
  }

  function renderArtifactList(scenario) {
    if (!artifactList || !scenario || !scenario.evidence_artifacts) return;
    artifactList.innerHTML = scenario.evidence_artifacts
      .map(function (art, i) {
        return (
          '<li><a class="proof-artifact-link" href="data/proof-scenarios-v1.json" download="' +
          escapeHtml(art.name) +
          '" data-artifact-index="' +
          i +
          '">' +
          escapeHtml(art.name) +
          " <span>↓</span></a></li>"
        );
      })
      .join("");
  }

  function renderEvidenceCards(scenario) {
    if (!evidenceCards || !scenario || !scenario.evidence_artifacts) return;
    evidenceCards.innerHTML = scenario.evidence_artifacts
      .map(function (art) {
        var border = badgeClass(scenario.verdict);
        return (
          '<article class="proof-evidence-card verdict-border-' +
          border +
          '">' +
          '<span class="proof-evidence-card-type">' +
          escapeHtml(art.type) +
          "</span>" +
          "<strong>" +
          escapeHtml(art.name) +
          "</strong>" +
          '<code class="proof-evidence-card-hash">' +
          escapeHtml(art.hash) +
          "</code>" +
          '<a class="proof-evidence-card-dl" href="data/proof-scenarios-v1.json" download="' +
          escapeHtml(art.name) +
          '">Download ↓</a>' +
          "</article>"
        );
      })
      .join("");
  }

  function renderTerminalLines(upToIndex, animate) {
    body.innerHTML = "";
    for (var i = 0; i <= upToIndex && i < currentSteps.length; i++) {
      var s = currentSteps[i];
      var cls = "line" + (animate && i === upToIndex ? " line-in" : "");
      body.innerHTML += '<span class="' + cls + " " + s.cls + '">' + escapeHtml(s.text) + "</span>";
    }
    if (cursor) {
      body.appendChild(cursor);
      cursor.style.display = upToIndex < currentSteps.length - 1 || autoPlaying ? "inline-block" : "none";
    }
    body.scrollTop = body.scrollHeight;
    if (currentSteps[upToIndex]) highlightPhase(currentSteps[upToIndex].phase);
    if (scrubber) {
      scrubber.max = String(Math.max(0, currentSteps.length - 1));
      scrubber.value = String(upToIndex);
    }
  }

  function updateReplayUI() {
    if (!replayStep) return;
    var total = currentSteps.length;
    replayStep.textContent = total ? stepIndex + 1 + " / " + total : "—";
    if (replayPrev) replayPrev.disabled = stepIndex <= 0;
    if (replayNext) replayNext.disabled = stepIndex >= total - 1;
    if (scrubber) scrubber.value = String(stepIndex);
  }

  function updatePlayBtn() {
    if (!replayPlay) return;
    var playing = autoPlaying && !replayMode && !paused;
    replayPlay.textContent = playing ? "⏸ Pause" : "▶ Play";
    replayPlay.setAttribute("aria-pressed", playing ? "true" : "false");
  }

  function showStep(idx) {
    stepIndex = Math.max(0, Math.min(idx, currentSteps.length - 1));
    renderTerminalLines(stepIndex, false);
    updateReplayUI();
    var step = currentSteps[stepIndex];
    if (step && currentScenario) {
      setVerdict(
        (tampered ? "tamper-FAIL — " : "") + currentScenario.verdict_summary + " · step " + (stepIndex + 1)
      );
    }
  }

  function runAutoLoop() {
    if (replayMode || reducedMotion || !autoPlaying) return;
    var i = stepIndex >= 0 ? stepIndex : 0;
    if (i >= currentSteps.length) i = 0;
    tampered = false;

    function tick() {
      if (paused || replayMode || !autoPlaying) return;
      if (i >= currentSteps.length) {
        body.innerHTML += '<span class="line dim">— loop restart —</span>';
        if (cursor && body.contains(cursor)) body.appendChild(cursor);
        timer = setTimeout(function () {
          i = 0;
          stepIndex = 0;
          highlightPhase(0);
          tick();
        }, 1800);
        return;
      }
      var step = currentSteps[i];
      body.innerHTML += '<span class="line line-in ' + step.cls + '">' + escapeHtml(step.text) + "</span>";
      if (cursor) body.appendChild(cursor);
      body.scrollTop = body.scrollHeight;
      highlightPhase(step.phase);
      stepIndex = i;
      updateReplayUI();
      i += 1;
      timer = setTimeout(tick, i === 1 ? 400 : 650);
    }

    if (timer) clearTimeout(timer);
    tick();
    updatePlayBtn();
  }

  function typewriterReceipt(scenario) {
    if (!receiptJson) return;
    if (typewriterTimer) clearInterval(typewriterTimer);
    if (reducedMotion) {
      updateEvidencePanel(scenario);
      return;
    }
    var receipt = JSON.parse(JSON.stringify(scenario.receipt));
    var full = JSON.stringify(receipt, null, 2);
    var pos = 0;
    receiptJson.textContent = "";
    typewriterTimer = setInterval(function () {
      pos += 4;
      receiptJson.textContent = full.slice(0, pos);
      if (pos >= full.length) clearInterval(typewriterTimer);
    }, 10);
  }

  function transitionLab(cb) {
    if (!labGrid || reducedMotion) {
      cb();
      return;
    }
    labGrid.classList.add("is-switching");
    window.setTimeout(function () {
      cb();
      labGrid.classList.remove("is-switching");
    }, 180);
  }

  function setActiveScenarioUI(key) {
    if (cardsWrap) {
      cardsWrap.querySelectorAll(".proof-scenario-card").forEach(function (card) {
        var on = card.getAttribute("data-scenario") === key;
        card.classList.toggle("active", on);
        card.setAttribute("aria-selected", on ? "true" : "false");
      });
    }
    if (pillsWrap) {
      pillsWrap.querySelectorAll(".proof-pill").forEach(function (btn) {
        var on = btn.getAttribute("data-scenario") === key;
        btn.classList.toggle("active", on);
        btn.setAttribute("aria-selected", on ? "true" : "false");
      });
    }
  }

  function startScenario(key) {
    var scenario = scenarios[key];
    if (!scenario) return;

    transitionLab(function () {
      currentScenario = scenario;
      currentSteps = scenario.steps || [];
      stepIndex = 0;
      tampered = false;
      replayMode = false;
      autoPlaying = !reducedMotion;
      stopFilm();
      if (timer) clearTimeout(timer);

      setActiveScenarioUI(key);
      markExplored(key);

      setVerdict(scenario.verdict_summary);
      var titleEl = document.querySelector(".proof-terminal-title");
      if (titleEl) titleEl.textContent = "witness-ai proof — " + scenario.label.toLowerCase();

      updateEvidencePanel(scenario);
      renderEvidenceCards(scenario);
      typewriterReceipt(scenario);
      updateReplayUI();
      updatePlayBtn();

      if (location.hash !== "#scenario=" + key) {
        history.replaceState(null, "", "#scenario=" + key);
      }

      body.innerHTML = "";
      if (reducedMotion) {
        renderTerminalLines(currentSteps.length - 1, false);
      } else {
        runAutoLoop();
      }
    });
  }

  function runTamperDemo() {
    if (!currentScenario) return;
    tampered = true;
    replayMode = true;
    autoPlaying = false;
    stopFilm();
    if (timer) clearTimeout(timer);
    paused = true;
    updatePlayBtn();

    updateEvidencePanel(currentScenario);
    setVerdict("tamper-FAIL — signature invalid after hand edit");

    body.innerHTML = "";
    currentSteps.forEach(function (s) {
      body.innerHTML += '<span class="line ' + s.cls + '">' + escapeHtml(s.text) + "</span>";
    });
    if (cursor) {
      body.appendChild(cursor);
      cursor.style.display = "none";
    }
    highlightPhase(6);

    if (tamperBtn) {
      tamperBtn.setAttribute("aria-pressed", "true");
      terminal.classList.add("proof-terminal-tamper-shake");
      window.setTimeout(function () {
        tamperBtn.setAttribute("aria-pressed", "false");
        terminal.classList.remove("proof-terminal-tamper-shake");
      }, 2000);
    }
  }

  if (replayPrev) {
    replayPrev.addEventListener("click", function () {
      replayMode = true;
      autoPlaying = false;
      stopFilm();
      if (timer) clearTimeout(timer);
      updatePlayBtn();
      showStep(stepIndex - 1);
    });
  }
  if (replayNext) {
    replayNext.addEventListener("click", function () {
      replayMode = true;
      autoPlaying = false;
      stopFilm();
      if (timer) clearTimeout(timer);
      updatePlayBtn();
      showStep(stepIndex + 1);
    });
  }
  if (replayPlay) {
    replayPlay.addEventListener("click", function () {
      if (autoPlaying && !replayMode) {
        paused = !paused;
        if (paused) {
          if (timer) clearTimeout(timer);
        } else {
          runAutoLoop();
        }
      } else {
        replayMode = false;
        autoPlaying = true;
        paused = false;
        body.innerHTML = "";
        stepIndex = 0;
        runAutoLoop();
      }
      updatePlayBtn();
    });
  }
  if (scrubber) {
    scrubber.addEventListener("input", function () {
      replayMode = true;
      autoPlaying = false;
      stopFilm();
      if (timer) clearTimeout(timer);
      updatePlayBtn();
      showStep(parseInt(scrubber.value, 10));
    });
  }
  if (tamperBtn) {
    tamperBtn.addEventListener("click", runTamperDemo);
  }
  if (copyHashBtn) {
    copyHashBtn.addEventListener("click", function () {
      if (!currentScenario) return;
      var hashEl = evidencePanel && evidencePanel.querySelector("[data-evidence-hash]");
      var text = hashEl ? hashEl.textContent : currentScenario.receipt_hash;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          copyHashBtn.textContent = "Copied!";
          window.setTimeout(function () {
            copyHashBtn.textContent = "Copy";
          }, 1500);
        });
      }
    });
  }

  terminal.addEventListener("mouseenter", function () {
    if (!replayMode) {
      paused = true;
      if (timer) clearTimeout(timer);
      updatePlayBtn();
    }
  });

  terminal.addEventListener("mouseleave", function () {
    if (reducedMotion || replayMode) return;
    if (autoPlaying) {
      paused = false;
      runAutoLoop();
    }
  });

  function buildScenarioCards() {
    if (!cardsWrap) return;
    cardsWrap.innerHTML = "";
    scenarioOrder.forEach(function (key, idx) {
      var scenario = scenarios[key];
      var card = document.createElement("button");
      card.type = "button";
      card.className = "proof-scenario-card verdict-border-" + badgeClass(scenario.verdict) + (idx === 0 ? " active" : "");
      card.setAttribute("data-scenario", key);
      card.setAttribute("role", "tab");
      card.setAttribute("aria-selected", idx === 0 ? "true" : "false");
      card.innerHTML =
        '<span class="proof-scenario-card-verdict verdict-' +
        badgeClass(scenario.verdict) +
        '">' +
        escapeHtml(scenario.verdict) +
        "</span>" +
        "<strong>" +
        escapeHtml(scenario.label) +
        "</strong>" +
        '<p class="proof-scenario-card-teaser">' +
        escapeHtml(scenario.narrative.slice(0, 90)) +
        "…</p>";
      card.addEventListener("click", function () {
        startScenario(key);
      });
      cardsWrap.appendChild(card);
    });
  }

  function buildPills() {
    if (!pillsWrap) return;
    pillsWrap.innerHTML = "";
    scenarioOrder.forEach(function (key, idx) {
      var scenario = scenarios[key];
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "proof-pill" + (idx === 0 ? " active" : "");
      btn.setAttribute("data-scenario", key);
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", idx === 0 ? "true" : "false");
      btn.textContent = scenario.label;
      btn.addEventListener("click", function () {
        startScenario(key);
      });
      pillsWrap.appendChild(btn);
    });
  }

  function parseHashScenario() {
    var hash = location.hash || "";
    var m = hash.match(/[#&]scenario=([a-z0-9-]+)/i);
    if (m && scenarios[m[1]]) return m[1];
    return scenarioOrder[0] || null;
  }

  function loadScenarios(cb) {
    var embedded = document.getElementById("wbcProofScenarios");
    if (embedded && embedded.textContent) {
      try {
        var data = JSON.parse(embedded.textContent);
        ingest(data);
        cb();
        return;
      } catch (e) {
        /* fall through to fetch */
      }
    }
    fetch("data/proof-scenarios-v1.json")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        ingest(data);
        cb();
      })
      .catch(function () {
        cb();
      });
  }

  function ingest(data) {
    if (!data || !data.scenarios) return;
    data.scenarios.forEach(function (s) {
      scenarios[s.slug] = s;
      scenarioOrder.push(s.slug);
    });
    var dl = document.getElementById("proofBundleDownload");
    if (dl && data.bundle_download) dl.setAttribute("href", data.bundle_download);
  }

  loadScenarios(function () {
    if (!scenarioOrder.length) return;
    buildScenarioCards();
    buildPills();
    updateProgressUI();
    var initial = parseHashScenario();
    startScenario(initial || scenarioOrder[0]);
  });

  window.addEventListener("hashchange", function () {
    var key = parseHashScenario();
    if (key && currentScenario && key !== currentScenario.slug) startScenario(key);
  });

  var w1Film = document.getElementById("w1DemoFilm");
  var w1Video = document.getElementById("w1DemoVideo");
  if (w1Film && w1Video) {
    function useW1Fallback() {
      w1Film.classList.add("w1-demo-film--fallback");
    }
    w1Video.addEventListener("error", useW1Fallback);
    w1Video.addEventListener("loadeddata", function () {
      w1Film.classList.remove("w1-demo-film--fallback");
    });
    if (w1Video.readyState === 0) {
      window.setTimeout(function () {
        if (w1Video.error || w1Video.networkState === 3) useW1Fallback();
      }, 400);
    }
  }
})();
