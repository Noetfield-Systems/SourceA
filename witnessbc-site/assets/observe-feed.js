(function () {
  "use strict";

  var el = document.getElementById("wbcObserveFeed");
  var mount = document.getElementById("observeFeedGrid");
  var filters = document.getElementById("observeFeedFilters");
  if (!el || !mount) return;

  var data;
  try {
    data = JSON.parse(el.textContent || "{}");
  } catch (e) {
    return;
  }

  var items = (data.items || []).slice();
  var categories = data.categories || [];
  var active = "all";

  function render(list) {
    if (!list.length) {
      mount.innerHTML = '<p class="meta">No posts in this category yet.</p>';
      return;
    }
    mount.innerHTML = list
      .map(function (it) {
        var tags = (it.tags || [])
          .map(function (t) {
            return '<span class="observe-tag">' + t + "</span>";
          })
          .join("");
        return (
          '<article class="observe-card">' +
          '<div class="observe-card-meta"><span>' +
          (it.date || "") +
          "</span>" +
          tags +
          "</div>" +
          "<h3>" +
          (it.title || "") +
          "</h3>" +
          "<p>" +
          (it.excerpt || "") +
          "</p>" +
          "</article>"
        );
      })
      .join("");
  }

  function filtered() {
    if (active === "all") return items;
    return items.filter(function (it) {
      return it.category === active || (it.tags || []).indexOf(active) >= 0;
    });
  }

  if (filters && categories.length) {
    var btns =
      '<button type="button" class="observe-filter-btn is-active" data-cat="all">All</button>' +
      categories
        .map(function (c) {
          return (
            '<button type="button" class="observe-filter-btn" data-cat="' +
            c +
            '">' +
            c +
            "</button>"
          );
        })
        .join("");
    filters.innerHTML = btns;
    filters.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-cat]");
      if (!btn) return;
      active = btn.getAttribute("data-cat") || "all";
      filters.querySelectorAll(".observe-filter-btn").forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
      });
      render(filtered());
    });
  }

  render(filtered());
})();

(function () {
  "use strict";
  var form = document.getElementById("observeCorrectionsForm");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var url = (document.getElementById("observe_c_url") || {}).value || "";
    var what = (document.getElementById("observe_c_what") || {}).value || "";
    var evidence = (document.getElementById("observe_c_evidence") || {}).value || "";
    var body = [
      "Hello WitnessBC Observe,",
      "",
      "Requesting a correction / clarification.",
      "",
      "Article URL: " + (url.trim() || "[paste URL]"),
    ];
    if (what.trim()) {
      body.push("", "What appears incorrect:", what.trim());
    }
    if (evidence.trim()) {
      body.push("", "Evidence link(s):", evidence.trim());
    }
    body.push("", "Privacy-first — avoiding unnecessary identifiers in first contact.");
    window.location.href =
      "mailto:hello@witnessbc.com" +
      "?subject=" +
      encodeURIComponent("Correction request — WitnessBC Observe") +
      "&body=" +
      encodeURIComponent(body.join("\n"));
  });
})();
