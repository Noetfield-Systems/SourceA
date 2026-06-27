/**
 * SourceA site interact — Cal overlay, playbook skills dock, guided paths, CTA wiring.
 */
(function () {
  "use strict";

  const CONFIG_URL = "/sourcea/data/sourcea-site-interact-v1.json";
  const GUIDED_KEY = "sourcea-guided-v1";
  const DEFAULTS = {
    booking_url: "https://cal.com/sourcea/proof-demo",
    booking_overlay_url: "https://cal.com/sourcea/proof-demo?overlayCalendar=true&embed=true",
    booking_label: "Talk to a human",
    use_cal_overlay: true,
    skills: [],
    guided_prompts: [],
  };

  let config = { ...DEFAULTS };

  function track(event, meta) {
    if (window.SourceAPulse) window.SourceAPulse.track(event, meta);
  }

  async function loadConfig() {
    try {
      const r = await fetch(CONFIG_URL, { cache: "no-store" });
      if (r.ok) config = { ...DEFAULTS, ...(await r.json()) };
    } catch {
      config = { ...DEFAULTS };
    }
  }

  function calOverlayUrl() {
    return config.booking_overlay_url || config.booking_url + "?overlayCalendar=true&embed=true";
  }

  function openCalOverlay() {
    let root = document.getElementById("sa-cal-overlay");
    if (!root) {
      root = document.createElement("div");
      root.id = "sa-cal-overlay";
      root.className = "sa-cal-overlay";
      root.hidden = true;
      root.innerHTML = `
        <div class="sa-cal-overlay-backdrop" data-sa-cal-close></div>
        <div class="sa-cal-overlay-panel" role="dialog" aria-label="Talk to a human">
          <header class="sa-cal-overlay-head">
            <strong>${config.booking_label || "Talk to a human"}</strong>
            <button type="button" class="sa-cal-overlay-close" data-sa-cal-close aria-label="Close">×</button>
          </header>
          <iframe class="sa-cal-overlay-frame" title="Cal.com booking" loading="lazy"></iframe>
        </div>`;
      document.body.appendChild(root);
      root.querySelectorAll("[data-sa-cal-close]").forEach(function (btn) {
        btn.addEventListener("click", closeCalOverlay);
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !root.hidden) closeCalOverlay();
      });
    }
    const frame = root.querySelector(".sa-cal-overlay-frame");
    if (frame && !frame.src) frame.src = calOverlayUrl();
    root.hidden = false;
    document.body.classList.add("sa-cal-open");
    track("cal_overlay_open");
  }

  function closeCalOverlay() {
    const root = document.getElementById("sa-cal-overlay");
    if (!root) return;
    root.hidden = true;
    document.body.classList.remove("sa-cal-open");
    track("cal_overlay_close");
  }

  function wireBookingCtas() {
    document.querySelectorAll("[data-sa-book-fallback], [data-sa-book-cta]").forEach(function (el) {
      if (config.booking_url) el.setAttribute("href", config.booking_url);
      if (config.booking_label && el.classList.contains("ar-btn")) {
        const arrow = el.querySelector(".ar-btn-arrow");
        el.textContent = config.booking_label;
        if (arrow) el.appendChild(arrow);
      }
      el.setAttribute("data-sa-cal-overlay", "1");
    });

    document.addEventListener(
      "click",
      function (e) {
        const el = e.target.closest("[data-sa-cal-overlay], [data-sa-book-fallback], [data-sa-book-cta]");
        if (!el || !config.use_cal_overlay) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        e.preventDefault();
        openCalOverlay();
      },
      true
    );
  }

  function mountPlaybookDock() {
    if (document.getElementById("sa-playbook-dock") || !config.skills?.length) return;

    const dock = document.createElement("aside");
    dock.id = "sa-playbook-dock";
    dock.className = "sa-playbook-dock";
    dock.setAttribute("aria-label", "SourceA tools");

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "sa-playbook-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.innerHTML = `<span class="sa-playbook-toggle-icon">⚡</span><span>${config.playbook_label || "Tools"}</span>`;

    const panel = document.createElement("div");
    panel.className = "sa-playbook-panel";
    panel.hidden = true;
    panel.innerHTML = `<p class="sa-playbook-intro">${config.playbook_intro || ""}</p><div class="sa-playbook-skills"></div>`;

    const skillsWrap = panel.querySelector(".sa-playbook-skills");
    config.skills.forEach(function (skill) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sa-playbook-skill";
      btn.setAttribute("data-sa-skill-id", skill.id);
      btn.innerHTML = `<span class="sa-playbook-skill-icon">${skill.icon || "•"}</span><span class="sa-playbook-skill-text"><strong>${skill.label}</strong><em>${skill.hint || ""}</em></span>`;
      btn.addEventListener("click", function () {
        track("skill_click", { skill_id: skill.id, technique: skill.technique });
        if (skill.action === "cal_overlay") {
          openCalOverlay();
        } else if (skill.href) {
          window.location.href = skill.href;
        }
        panel.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        dock.classList.remove("is-open");
      });
      skillsWrap.appendChild(btn);
    });

    toggle.addEventListener("click", function () {
      const open = panel.hidden;
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
      dock.classList.toggle("is-open", open);
      if (open) track("playbook_open");
    });

    dock.appendChild(toggle);
    dock.appendChild(panel);
    document.body.appendChild(dock);
  }

  function mountGuidedPrompt() {
    if (!config.guided_prompts?.length) return;
    try {
      if (config.guided_once_per_session && sessionStorage.getItem(GUIDED_KEY)) return;
    } catch {
      return;
    }

    const banner = document.createElement("div");
    banner.className = "sa-guided-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-label", config.guided_title || "What brings you here?");
    banner.innerHTML = `
      <div class="sa-guided-inner">
        <p class="sa-guided-title">${config.guided_title || "What brings you here?"}</p>
        ${config.guided_subtitle ? `<p class="sa-guided-subtitle">${config.guided_subtitle}</p>` : ""}
        <div class="sa-guided-chips"></div>
        <button type="button" class="sa-guided-dismiss">Not now</button>
      </div>`;

    const chips = banner.querySelector(".sa-guided-chips");
    config.guided_prompts.forEach(function (p) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "sa-guided-chip";
      b.textContent = p.label;
      b.setAttribute("data-sa-segment-id", p.id);
      b.addEventListener("click", function () {
        track(p.track || "guided_pick", { id: p.id, audience: p.audience || "unknown", segment: p.id });
        try {
          sessionStorage.setItem(GUIDED_KEY, "1");
        } catch {
          /* ignore */
        }
        banner.remove();
        if (p.href) window.location.href = p.href;
      });
      chips.appendChild(b);
    });

    banner.querySelector(".sa-guided-dismiss").addEventListener("click", function () {
      try {
        sessionStorage.setItem(GUIDED_KEY, "1");
      } catch {
        /* ignore */
      }
      banner.remove();
      track("guided_dismiss");
    });

    document.body.appendChild(banner);
    track("guided_show");
  }

  function exposeBrainSkills() {
    window.SourceAInteract = {
      config: function () {
        return config;
      },
      openCal: openCalOverlay,
      brainExtraChips: function () {
        return config.brain_extra_chips || [];
      },
    };
  }

  async function init() {
    await loadConfig();
    wireBookingCtas();
    mountPlaybookDock();
    exposeBrainSkills();
    setTimeout(mountGuidedPrompt, 1800);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
