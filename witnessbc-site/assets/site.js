(function () {
  "use strict";

  var STORAGE_KEY = "witness-ai-theme";
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.documentElement.classList.add("motion-ready");

  /* Theme toggle */
  var themeBtn = document.getElementById("themeToggle");
  function getTheme() {
    return document.documentElement.getAttribute("data-theme") || "light";
  }
  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      setTheme(getTheme() === "dark" ? "light" : "dark");
    });
  }

  /* Mobile nav */
  var toggle = document.getElementById("menuToggle");
  var nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* Dropdown touch support */
  document.querySelectorAll(".has-dropdown > button").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var parent = btn.closest(".has-dropdown");
      var wasOpen = parent.classList.contains("open");
      document.querySelectorAll(".has-dropdown.open").forEach(function (el) {
        el.classList.remove("open");
      });
      if (!wasOpen) parent.classList.add("open");
    });
  });
  document.addEventListener("click", function () {
    document.querySelectorAll(".has-dropdown.open").forEach(function (el) {
      el.classList.remove("open");
    });
  });

  /* Header scroll polish */
  var header = document.getElementById("siteHeader");
  var hero = document.getElementById("hero");
  var stickyCta = document.getElementById("stickyCta");

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("scrolled", y > 24);
    if (stickyCta && hero) {
      var heroBottom = hero.offsetTop + hero.offsetHeight;
      var show = y > heroBottom - 80;
      stickyCta.classList.toggle("visible", show);
      stickyCta.setAttribute("aria-hidden", show ? "false" : "true");
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Nav scroll spy — home page hash links only */
  var navLinks = document.querySelectorAll('.nav-link[href^="#"]');
  if (navLinks.length && document.body.classList.contains("page-home")) {
    var sectionIds = ["platform", "proof", "pricing", "lifecycle", "compare", "policy"];
    function updateNavSpy() {
      var scrollY = window.scrollY + 120;
      var current = "";
      sectionIds.forEach(function (id) {
        var el = document.getElementById(id);
        if (el && el.offsetTop <= scrollY) current = id;
      });
      navLinks.forEach(function (link) {
        var href = link.getAttribute("href") || "";
        link.classList.toggle("is-active", href === "#" + current);
      });
    }
    window.addEventListener("scroll", updateNavSpy, { passive: true });
    updateNavSpy();
  }

  /* Governance loop stepper */
  var LOOP_STEPS = [
    { title: "Intake", desc: "Agent action arrives · classify scope · initial policy scan.", code: "wbc.intake.received" },
    { title: "Policy eval", desc: "AI policy pack runs at dispatch — BLOCK · ESCALATE · ALLOW.", code: "wbc.triage.complete → verdict" },
    { title: "Human gate", desc: "Approve irreversible agent actions before execution.", code: "wbc.review.approved" },
    { title: "Execute", desc: "Agent runs under policy · signed receipt on disk.", code: "wbc.publish.sent" },
    { title: "Audit", desc: "Log overrides · replay proof · policy version pinned.", code: "wbc.correction.logged" },
    { title: "Prove", desc: "Signed ledger + replay. Hand-edited receipts FAIL validation.", code: "export → replay → tamper-FAIL" },
  ];

  var stepper = document.getElementById("loopStepper");
  var detail = document.getElementById("loopDetail");
  var stepIdx = 0;
  var stepTimer = null;

  function showStep(i) {
    stepIdx = i;
    if (!stepper || !detail) return;
    stepper.querySelectorAll(".loop-step").forEach(function (btn, j) {
      btn.classList.toggle("active", j === i);
      btn.setAttribute("aria-selected", j === i ? "true" : "false");
    });
    var s = LOOP_STEPS[i];
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      detail.classList.add("is-updating");
      setTimeout(function () {
        detail.innerHTML =
          "<h3>" + s.title + "</h3><p>" + s.desc + "</p><code>" + s.code + "</code>";
        detail.classList.remove("is-updating");
      }, 120);
    } else {
      detail.innerHTML =
        "<h3>" + s.title + "</h3><p>" + s.desc + "</p><code>" + s.code + "</code>";
    }
  }

  if (stepper) {
    stepper.querySelectorAll(".loop-step").forEach(function (btn) {
      btn.addEventListener("click", function () {
        showStep(parseInt(btn.getAttribute("data-step"), 10));
        if (stepTimer) clearInterval(stepTimer);
      });
    });
    showStep(0);
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      stepTimer = setInterval(function () {
        showStep((stepIdx + 1) % LOOP_STEPS.length);
      }, 5000);
    }
  }

  /* Subtle scroll reveal for section cards */
  if (!reducedMotion && "IntersectionObserver" in window) {
    var revealSelectors =
      ".evidence-card, .problem-card, .capability-card, .autonomy-tier, .price-card, .arch-diagram, .trust-pill, .explore-card";
    document.querySelectorAll(revealSelectors).forEach(function (el, i) {
      el.classList.add("reveal-on-scroll");
      el.style.setProperty("--reveal-delay", String((i % 4) * 80) + "ms");
    });
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
    );
    document.querySelectorAll(".reveal-on-scroll").forEach(function (el) {
      observer.observe(el);
    });
  } else {
    document.querySelectorAll(".arch-diagram").forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  /* Stat count-up on home hero */
  if (!reducedMotion && document.body.classList.contains("page-home")) {
    var statEls = document.querySelectorAll(".stat-count[data-count]");
    if (statEls.length && "IntersectionObserver" in window) {
      var counted = false;
      var statObs = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting || counted) return;
            counted = true;
            statObs.disconnect();
            statEls.forEach(function (el) {
              var target = parseInt(el.getAttribute("data-count"), 10);
              var suffix = el.getAttribute("data-suffix") || "";
              if (isNaN(target)) return;
              var start = 0;
              var dur = 900;
              var t0 = performance.now();
              function frame(now) {
                var p = Math.min(1, (now - t0) / dur);
                var val = Math.round(start + (target - start) * p);
                el.textContent = val + suffix;
                if (p < 1) requestAnimationFrame(frame);
              }
              requestAnimationFrame(frame);
            });
          });
        },
        { threshold: 0.5 }
      );
      var strip = document.getElementById("statsStrip");
      if (strip) statObs.observe(strip);
    }
  }

  /* Hero proof scenario ticker (home only) */
  if (document.body.classList.contains("page-home") && !reducedMotion) {
    var tickerVerdict = document.getElementById("heroProofTickerVerdict");
    var tickerText = document.getElementById("heroProofTickerText");
    var tickerLink = document.getElementById("heroProofTickerLink");
    var tickerItems = [
      { slug: "outbound", verdict: "ESCALATE", cls: "verdict-escalate", text: "Outbound email → human gate → signed receipt" },
      { slug: "tool", verdict: "BLOCK", cls: "verdict-block", text: "Tool call — PII export denied at dispatch" },
      { slug: "publish", verdict: "ALLOW", cls: "verdict-allow", text: "Publish — policy ran before web publish" },
      { slug: "pii-leak", verdict: "BLOCK", cls: "verdict-block", text: "PII leak — SSN pattern blocked before send" },
      { slug: "mcp-escalate", verdict: "ESCALATE", cls: "verdict-escalate", text: "MCP write — platform lead gate before execute" },
      { slug: "tamper", verdict: "FAIL", cls: "verdict-fail", text: "Tamper demo — signature invalid on replay" },
    ];
    var tickerIdx = 0;
    function tickHeroProof() {
      var item = tickerItems[tickerIdx % tickerItems.length];
      if (tickerVerdict) {
        tickerVerdict.textContent = item.verdict;
        tickerVerdict.className = "hero-proof-ticker-verdict " + item.cls;
      }
      if (tickerText) tickerText.textContent = item.text;
      if (tickerLink) tickerLink.href = "proof.html#scenario=" + item.slug;
      tickerIdx += 1;
    }
    tickHeroProof();
    window.setInterval(tickHeroProof, 3200);
  }

  /* Mobile bottom CTA bar */
  var MOBILE_CTA_KEY = "witness-ai-mobile-cta-dismissed";
  var proofMailto =
    document.body.getAttribute("data-proof-mailto") ||
    "mailto:proof@witnessbc.com?subject=Witness%20AI%20%E2%80%94%2015-min%20live%20proof";
  var liveDemoUrl =
    document.body.getAttribute("data-live-demo-url") ||
    "proof.html";
  if (window.matchMedia("(max-width: 768px)").matches && !sessionStorage.getItem(MOBILE_CTA_KEY)) {
    var bar = document.createElement("div");
    bar.className = "mobile-cta-bar";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Quick actions");
    bar.innerHTML =
      '<div class="mobile-cta-bar-inner">' +
      '<a class="btn btn-primary" href="' +
      proofMailto +
      '">Book proof</a>' +
      '<a class="btn btn-outline" href="' +
      liveDemoUrl +
      '">Proof Lab</a>' +
      '<button type="button" class="mobile-cta-dismiss" aria-label="Dismiss">×</button>' +
      "</div>";
    document.body.appendChild(bar);
    document.body.classList.add("mobile-cta-on");

    var dismissBtn = bar.querySelector(".mobile-cta-dismiss");
    function hideMobileCta() {
      bar.classList.remove("visible");
      document.body.classList.remove("mobile-cta-on");
      sessionStorage.setItem(MOBILE_CTA_KEY, "1");
    }
    if (dismissBtn) dismissBtn.addEventListener("click", hideMobileCta);

    window.addEventListener(
      "scroll",
      function () {
        var y = window.scrollY || window.pageYOffset;
        if (sessionStorage.getItem(MOBILE_CTA_KEY)) return;
        bar.classList.toggle("visible", y > 400);
      },
      { passive: true }
    );
  }
})();
