(function () {
  const nav = document.querySelector("#ar-nav");
  const toggle = document.querySelector(".ar-nav-toggle");
  const backdrop = document.querySelector(".ar-nav-backdrop");

  function setNav(open) {
    if (!nav || !toggle) return;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.classList.toggle("is-open", open);
    nav.classList.toggle("is-open", open);
    if (backdrop) backdrop.classList.toggle("is-visible", open);
    document.body.classList.toggle("ar-nav-locked", open);
  }

  if (toggle && nav) {
    toggle.addEventListener("click", () => setNav(toggle.getAttribute("aria-expanded") !== "true"));
    nav.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setNav(false)));
    if (backdrop) backdrop.addEventListener("click", () => setNav(false));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setNav(false);
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const id = link.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      setNav(false);
      const top = target.getBoundingClientRect().top + window.scrollY - 88;
      window.scrollTo({ top, behavior: "smooth" });
    });
  });

  const bar = document.querySelector(".ar-scroll-progress-bar");
  const backTop = document.querySelector("#ar-back-top");

  function onScroll() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.width = max > 0 ? (window.scrollY / max) * 100 + "%" : "0%";
    if (backTop) backTop.classList.toggle("is-visible", window.scrollY > 480);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (backTop) {
    backTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function animateCount(el) {
    if (!el || el.dataset.arAnimated === "1") return;
    const target = parseInt(el.getAttribute("data-ar-count"), 10);
    if (Number.isNaN(target)) return;
    const prefix = el.getAttribute("data-ar-prefix") || "";
    const suffix = el.getAttribute("data-ar-suffix") || "";
    el.dataset.arAnimated = "1";
    const duration = 1200;
    const startTime = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - startTime) / duration);
      const val = Math.round(target * (1 - Math.pow(1 - t, 3)));
      el.textContent = prefix + val + suffix;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function revealStagger(container) {
    if (!container || container.dataset.arStaggered === "1") return;
    container.dataset.arStaggered = "1";
    const kids = container.querySelectorAll(":scope > .ar-reveal");
    kids.forEach((el, i) => {
      el.style.transitionDelay = `${i * 0.08}s`;
    });
  }

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll(".sa-root-hero, #top.sa-hero-stable").forEach((el) => {
    el.classList.add("ar-visible");
  });
  if (!reduced) {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            const el = e.target;
            el.classList.add("ar-visible");
            if (el.classList.contains("ar-stagger")) revealStagger(el);
            el.querySelectorAll("[data-ar-count]").forEach(animateCount);
            obs.unobserve(el);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -8% 0px" }
    );
    document.querySelectorAll(".ar-reveal").forEach((el) => obs.observe(el));
    document.querySelectorAll(".ar-stagger").forEach((el) => {
      if (el.classList.contains("ar-visible")) revealStagger(el);
    });
  } else {
    document.querySelectorAll(".ar-reveal").forEach((el) => el.classList.add("ar-visible"));
    document.querySelectorAll("[data-ar-count]").forEach((el) => {
      const target = el.getAttribute("data-ar-count") || "0";
      el.textContent =
        (el.getAttribute("data-ar-prefix") || "") + target + (el.getAttribute("data-ar-suffix") || "");
    });
  }

  const tabs = document.querySelectorAll(".ar-value-tab");
  const panels = {
    visibility: document.querySelector("#ar-panel-visibility"),
    authority: document.querySelector("#ar-panel-authority"),
    revenue: document.querySelector("#ar-panel-revenue"),
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const key = tab.getAttribute("data-ar-tab");
      tabs.forEach((t) => {
        const active = t === tab;
        t.classList.toggle("is-active", active);
        t.setAttribute("aria-selected", String(active));
      });
      Object.entries(panels).forEach(([k, panel]) => {
        if (!panel) return;
        const active = k === key;
        panel.classList.toggle("is-active", active);
        panel.hidden = !active;
        if (active) {
          panel.classList.remove("ar-tab-enter");
          requestAnimationFrame(() => panel.classList.add("ar-tab-enter"));
          panel.querySelectorAll("[data-ar-count]").forEach(animateCount);
        }
      });
    });
  });

  document.querySelectorAll(".ar-faq-trigger").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".ar-faq-item");
      if (!item) return;
      const open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
    });
  });

  const heroStage = document.querySelector("#ar-hero-stage");
  const orbStage = document.querySelector("#ar-orb-stage");
  if (heroStage && orbStage && !reduced) {
    heroStage.addEventListener("mousemove", (e) => {
      const rect = heroStage.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      orbStage.style.transform = `translate(${x * 12}px, ${y * 10}px)`;
    });
    heroStage.addEventListener("mouseleave", () => {
      orbStage.style.transform = "";
    });
  }
})();
