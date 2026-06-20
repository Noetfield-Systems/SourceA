(function () {
  "use strict";

  var STORAGE_KEY = "witnessbc-learn-progress-v1";
  var nav = document.getElementById("learnChapterNav");
  var panel = document.getElementById("learnChapterPanel");
  if (!nav || !panel) return;

  var dataEl = document.getElementById("wbcLearnChapters");
  if (!dataEl) return;

  var data;
  try {
    data = JSON.parse(dataEl.textContent);
  } catch (e) {
    return;
  }

  var chapters = data.chapters || [];
  var workflows = data.workflows || [];
  var resources = data.resources || [];
  var current = 0;

  function loadProgress() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return {};
      return JSON.parse(raw) || {};
    } catch (e) {
      return {};
    }
  }

  function saveProgress(map) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
    } catch (e) {}
  }

  function progressMap() {
    return loadProgress();
  }

  function doneCount() {
    var map = progressMap();
    return chapters.filter(function (ch) {
      return map[ch.id];
    }).length;
  }

  function updateProgressUi() {
    var done = doneCount();
    var fill = document.getElementById("learnProgressFill");
    var text = document.getElementById("learnProgressText");
    var bar = document.getElementById("learnProgressBar");
    if (fill) fill.style.width = Math.round((done / chapters.length) * 100) + "%";
    if (text) text.textContent = done + " / " + chapters.length;
    if (bar) bar.setAttribute("aria-valuenow", String(done));
    nav.querySelectorAll(".learn-chapter-btn").forEach(function (btn) {
      var id = btn.getAttribute("data-chapter-id");
      btn.classList.toggle("is-done", !!progressMap()[id]);
    });
  }

  function chapterFromHash() {
    var h = (window.location.hash || "").replace(/^#/, "");
    if (!h) return 0;
    if (h.indexOf("chapter=") === 0) {
      var id = decodeURIComponent(h.slice(8));
      for (var i = 0; i < chapters.length; i++) {
        if (chapters[i].id === id) return i;
      }
    }
    return 0;
  }

  function setHash(id) {
    var next = "#chapter=" + encodeURIComponent(id);
    if (window.location.hash !== next) {
      history.replaceState(null, "", next);
    }
  }

  function renderNav() {
    nav.innerHTML = "";
    chapters.forEach(function (ch, i) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "learn-chapter-btn" + (i === current ? " active" : "");
      btn.setAttribute("data-chapter-id", ch.id);
      btn.setAttribute("data-index", String(i));
      btn.innerHTML =
        '<span class="learn-ch-btn-time">' +
        ch.timestamp +
        '</span><span class="learn-ch-btn-title">' +
        ch.title +
        "</span>";
      btn.addEventListener("click", function () {
        showChapter(i);
      });
      nav.appendChild(btn);
    });
    updateProgressUi();
  }

  function renderWorkflows() {
    var list = document.getElementById("learnWorkflowList");
    if (!list) return;
    list.innerHTML = "";
    workflows.forEach(function (wf) {
      var li = document.createElement("li");
      li.innerHTML =
        "<strong>" +
        wf.label +
        "</strong><span>" +
        wf.description +
        "</span>";
      list.appendChild(li);
    });
  }

  function renderResources() {
    var grid = document.getElementById("learnResourceGrid");
    if (!grid) return;
    grid.innerHTML = "";
    resources.forEach(function (res) {
      var a = document.createElement("a");
      a.className = "learn-resource-card";
      a.href = res.href;
      if (res.href.indexOf("mailto:") === 0) {
        a.setAttribute("href", res.href);
      }
      a.innerHTML =
        '<span class="learn-res-kind">' +
        res.kind +
        '</span><h4>' +
        res.label +
        "</h4><p>" +
        res.description +
        "</p>";
      grid.appendChild(a);
    });
  }

  function showChapter(i) {
    if (i < 0 || i >= chapters.length) return;
    current = i;
    var ch = chapters[i];
    setHash(ch.id);

    document.getElementById("learnChapterTime").textContent = ch.timestamp;
    document.getElementById("learnChapterTitle").textContent = ch.title;
    document.getElementById("learnChapterSub").textContent = ch.subtitle || "";
    document.getElementById("learnChapterSummary").textContent = ch.summary || "";

    var proofWrap = document.getElementById("learnChapterProof");
    var proofSlug = document.getElementById("learnProofSlug");
    if (ch.proof_slug) {
      proofWrap.hidden = false;
      proofSlug.textContent = "proof.html#scenario=" + ch.proof_slug;
    } else {
      proofWrap.hidden = true;
    }

    var cta = document.getElementById("learnChapterCta");
    cta.textContent = ch.cta_label || "Continue";
    cta.href = ch.cta_href || "proof.html";

    document.getElementById("learnPrev").disabled = i === 0;
    document.getElementById("learnNext").disabled = i === chapters.length - 1;

    nav.querySelectorAll(".learn-chapter-btn").forEach(function (btn, j) {
      btn.classList.toggle("active", j === i);
    });
    updateProgressUi();
  }

  document.getElementById("learnPrev").addEventListener("click", function () {
    showChapter(current - 1);
  });
  document.getElementById("learnNext").addEventListener("click", function () {
    showChapter(current + 1);
  });

  document.getElementById("learnMarkDone").addEventListener("click", function () {
    var ch = chapters[current];
    var map = progressMap();
    map[ch.id] = true;
    saveProgress(map);
    updateProgressUi();
    if (current < chapters.length - 1) {
      showChapter(current + 1);
    }
  });

  window.addEventListener("hashchange", function () {
    showChapter(chapterFromHash());
  });

  renderNav();
  renderWorkflows();
  renderResources();
  showChapter(chapterFromHash());
})();
