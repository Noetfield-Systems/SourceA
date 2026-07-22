(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(pointer: fine)").matches;
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);

  function streamText(el, text, speed = 14) {
    if (!el || reduced) { if (el) el.textContent = text; return; }
    el.classList.add("is-streaming");
    el.textContent = "";
    let i = 0;
    const tick = () => {
      if (i <= text.length) {
        el.textContent = text.slice(0, i);
        i += 1;
        setTimeout(tick, speed);
      } else {
        el.classList.remove("is-streaming");
      }
    };
    tick();
  }

  function showToast(message) {
    const stack = document.querySelector(".sa-toast-stack");
    if (!stack) return;
    const toast = document.createElement("div");
    toast.className = "sa-toast";
    toast.textContent = message;
    stack.appendChild(toast);
    setTimeout(() => toast.remove(), 3200);
  }

  /* ── AgentGo: cursor glow ── */
  if (finePointer && !reduced && !document.body.classList.contains("sa-root-home")) {
    const glow = document.createElement("div");
    glow.className = "sa-cursor-glow";
    document.body.appendChild(glow);
    let gx = 0, gy = 0, tx = 0, ty = 0;
    document.addEventListener("mousemove", (e) => {
      tx = e.clientX; ty = e.clientY;
      glow.classList.add("is-active");
    }, { passive: true });
    const smoothGlow = () => {
      gx += (tx - gx) * 0.08;
      gy += (ty - gy) * 0.08;
      glow.style.left = gx + "px";
      glow.style.top = gy + "px";
      requestAnimationFrame(smoothGlow);
    };
    smoothGlow();
  }

  /* ── AgentGo: green aurora neural canvas ── */
  const canvas = document.getElementById("sa-aurora");
  const isRootHome = document.body.classList.contains("sa-root-home");
  if (canvas && !reduced && !isRootHome) {
    const ctx = canvas.getContext("2d");
    let w = 0, h = 0, dpr = 1, mx = 0.5, my = 0.5, t = 0, active = true;
    const hub = { x: 0.5, y: 0.42 };
    const nodeCount = 12;
    const nodes = Array.from({ length: nodeCount }, (_, i) => {
      const angle = (i / nodeCount) * Math.PI * 2;
      const dist = 0.1 + Math.random() * 0.22;
      return {
        x: hub.x + Math.cos(angle) * dist,
        y: hub.y + Math.sin(angle) * dist * 0.8,
        vx: (Math.random() - 0.5) * 0.00012,
        vy: (Math.random() - 0.5) * 0.0001,
        r: Math.random() * 1.5 + 0.8,
        phase: Math.random() * Math.PI * 2,
      };
    });
    const packets = Array.from({ length: 5 }, () => ({
      from: Math.floor(Math.random() * nodeCount),
      p: Math.random(),
      speed: 0.003 + Math.random() * 0.003,
    }));

    const resize = () => {
      const parent = canvas.parentElement;
      if (!parent) return;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = parent.clientWidth;
      h = parent.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const draw = () => {
      if (!active) { requestAnimationFrame(draw); return; }
      t += 1;
      ctx.clearRect(0, 0, w, h);
      const hx = (hub.x + (mx - 0.5) * 0.03) * w;
      const hy = (hub.y + (my - 0.5) * 0.025) * h;
      const hubPulse = 0.6 + 0.4 * Math.sin(t * 0.04);

      const grad = ctx.createRadialGradient(hx, hy, 0, hx, hy, Math.min(w, h) * 0.32);
      grad.addColorStop(0, `rgba(105, 212, 25, ${0.1 * hubPulse})`);
      grad.addColorStop(0.5, `rgba(4, 68, 65, ${0.04 * hubPulse})`);
      grad.addColorStop(1, "transparent");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);

      nodes.forEach((n) => {
        n.x += n.vx; n.y += n.vy;
        const dx = n.x - hub.x, dy = n.y - hub.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > 0.32 || dist < 0.07) { n.vx *= -1; n.vy *= -1; }
        n.x = Math.max(0.06, Math.min(0.94, n.x));
        n.y = Math.max(0.08, Math.min(0.9, n.y));
      });

      nodes.forEach((n1, i) => {
        const toHub = Math.hypot(n1.x - hub.x, n1.y - hub.y);
        if (toHub < 0.28) {
          ctx.beginPath();
          ctx.moveTo(n1.x * w, n1.y * h);
          ctx.lineTo(hx, hy);
          ctx.strokeStyle = `rgba(105, 212, 25, ${(1 - toHub / 0.28) * 0.1})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
        for (let j = i + 1; j < nodes.length; j++) {
          const n2 = nodes[j];
          const d = Math.hypot(n1.x - n2.x, n1.y - n2.y);
          if (d < 0.1) {
            ctx.beginPath();
            ctx.moveTo(n1.x * w, n1.y * h);
            ctx.lineTo(n2.x * w, n2.y * h);
            ctx.strokeStyle = `rgba(4, 68, 65, ${(1 - d / 0.12) * 0.06})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      });

      packets.forEach((pk) => {
        pk.p += pk.speed;
        if (pk.p > 1) { pk.p = 0; pk.from = Math.floor(Math.random() * nodeCount); }
        const n = nodes[pk.from];
        const px = (n.x + (hub.x - n.x) * pk.p) * w;
        const py = (n.y + (hub.y - n.y) * pk.p) * h;
        ctx.beginPath();
        ctx.arc(px, py, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(154, 231, 97, ${0.4 + 0.4 * Math.sin(pk.p * Math.PI)})`;
        ctx.fill();
      });

      nodes.forEach((n) => {
        const pulse = 0.5 + 0.5 * Math.sin(t * 0.05 + n.phase);
        ctx.beginPath();
        ctx.arc(n.x * w, n.y * h, n.r * pulse, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(105, 212, 25, ${0.25 + pulse * 0.3})`;
        ctx.fill();
      });

      ctx.beginPath();
      ctx.arc(hx, hy, 4 * hubPulse, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(105, 212, 25, ${0.55 * hubPulse})`;
      ctx.fill();

      requestAnimationFrame(draw);
    };

    const obs = new IntersectionObserver((e) => { active = e[0]?.isIntersecting ?? true; }, { threshold: 0.05 });
    if (canvas.parentElement) obs.observe(canvas.parentElement);
    resize();
    window.addEventListener("resize", resize);
    document.addEventListener("mousemove", (e) => {
      mx = e.clientX / window.innerWidth;
      my = e.clientY / window.innerHeight;
    }, { passive: true });
    draw();
  }

  /* ── AgentGo: hero entrance ── */
  function heroEntrance() {
    if (reduced) {
      document.querySelectorAll(".sa-line-reveal, .sa-fade-up").forEach((el) => el.classList.add("is-visible"));
      document.querySelector(".sa-trust-pop")?.classList.add("is-visible");
      return;
    }
    requestAnimationFrame(() => {
      document.querySelectorAll(".sa-line-reveal").forEach((el) => el.classList.add("is-visible"));
      document.querySelectorAll(".sa-fade-up").forEach((el) => el.classList.add("is-visible"));
      document.querySelector(".sa-trust-pop")?.classList.add("is-visible");
    });
  }

  /* ── AgentGo: fleet panel 3D tilt ── */
  function fleetTilt() {
    const panel = document.querySelector(".sa-fleet-panel");
    if (!panel || !finePointer || reduced || window.innerWidth < 860) return;
    panel.classList.add("is-tilt");
    panel.addEventListener("mousemove", (e) => {
      const r = panel.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      panel.style.transform = `perspective(1000px) rotateY(${x * 10}deg) rotateX(${-y * 8}deg) translateZ(12px)`;
    });
    panel.addEventListener("mouseleave", () => {
      panel.style.transform = "perspective(1000px) rotateY(-4deg) rotateX(2deg)";
    });
  }

  /* ── AgentGo: hero pointer parallax ── */
  function heroParallax() {
    const grid = document.querySelector(".sa-hero-parallax-grid");
    const hero = document.querySelector(".sa-hero-cinematic");
    if (!grid || !hero || !finePointer || reduced) return;
    grid.classList.add("is-parallax");
    hero.addEventListener("mousemove", (e) => {
      const r = hero.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      grid.style.transform = `translate3d(${x * 10}px, ${y * 8}px, 0)`;
    }, { passive: true });
    hero.addEventListener("mouseleave", () => { grid.style.transform = ""; });
  }

  /* ── AgentGo: factory log ticker ── */
  function factoryLog() {
    const log = document.getElementById("sa-factory-log");
    if (!log || log.dataset.saLive === "1") return;
    const msgs = [
      "Brain routing · 6 agents active · $24K pipeline",
      "Outreach agent completed 3 proof reviews today",
      "Prove agent sealed replay — demo closes in 15 min",
      "$8K deposit received · Build agent scoping loop",
      "Guard blocked rogue ops edit · client protected",
      "Expand agent renewed retainer · +$2K/mo MRR",
    ];
    let i = 0;
    const cycle = () => {
      i = (i + 1) % msgs.length;
      streamText(log, msgs[i]);
    };
    setInterval(cycle, 3200);
  }

  function agentPillRotate() {
    const pill = document.getElementById("sa-agent-pill-text");
    if (!pill || pill.dataset.saLive === "1" || pill.closest(".sa-factory-pass-chip")) return;
    const msgs = [
      "Execution Proof Infrastructure™ · live on your stack",
      "Reference standard · 6/6 proof row complete",
      "ALLOW · BLOCK · tamper — demo in under 5 minutes",
      "Category leaders ship build + policy + receipt + replay",
      "Agentic command center · revenue + governance unified",
    ];
    let i = 0;
    setInterval(() => {
      if (pill.dataset.saLive === "1") return;
      i = (i + 1) % msgs.length;
      pill.style.opacity = "0.4";
      setTimeout(() => {
        if (pill.dataset.saLive === "1") return;
        pill.textContent = msgs[i];
        pill.style.opacity = "1";
      }, 200);
    }, 2800);
  }

  function engineChipPulse() {
    const chips = document.querySelectorAll(".sa-engine-chip:not([data-engine-tab])");
    if (!chips.length || reduced) return;
    const names = ["Outreach", "Prove", "Build", "Guard", "Expand"];
    let i = 0;
    setInterval(() => {
      chips.forEach((c) => c.classList.remove("is-pulse", "is-active"));
      chips.forEach((c) => {
        if (c.textContent.trim() === names[i % names.length]) c.classList.add("is-pulse", "is-active");
      });
      i += 1;
    }, 2200);
  }

  function agentSwarmCycle() {
    const chips = document.querySelectorAll(".sa-agent-chip");
    if (!chips.length || reduced) return;
    let i = 0;
    setInterval(() => {
      chips.forEach((c) => c.classList.remove("is-running"));
      chips[i % chips.length].classList.add("is-running");
      i += 1;
    }, 3000);
  }

  function receiptFeedCycle() {
    const cards = document.querySelectorAll(".sa-receipt-card");
    if (!cards.length || reduced) return;
    let i = 0;
    setInterval(() => {
      cards.forEach((c) => c.classList.remove("is-active"));
      cards[i % cards.length].classList.add("is-active");
      i += 1;
    }, 2600);
  }

  function lifecycleCycle() {
    const cards = document.querySelectorAll(".sa-lifecycle-card");
    if (!cards.length || reduced) return;
    let i = 0;
    setInterval(() => {
      cards.forEach((c) => c.classList.remove("is-active", "is-running"));
      const active = cards[i % cards.length];
      active.classList.add(i === 0 ? "is-running" : "is-active");
      i += 1;
    }, 3200);
  }

  function orchestrator() {
    const root = document.getElementById("sa-orchestrator");
    if (!root) return;
    setTimeout(() => root.classList.add("is-mounted"), 1200);
    const head = root.querySelector(".sa-orchestrator-head");
    const toggle = root.querySelector(".sa-orchestrator-toggle");
    const tracks = root.querySelectorAll(".sa-agent-track");
    const toggleFn = () => {
      const open = root.classList.toggle("is-expanded");
      root.classList.toggle("is-collapsed", !open);
      if (toggle) toggle.setAttribute("aria-expanded", String(open));
    };
    if (head) head.addEventListener("click", toggleFn);
    if (toggle) toggle.addEventListener("click", (e) => { e.stopPropagation(); toggleFn(); });
    if (tracks.length && !reduced) {
      let i = 0;
      setInterval(() => {
        tracks.forEach((t) => t.classList.remove("is-active"));
        tracks[i % tracks.length].classList.add("is-active");
        i += 1;
      }, 2800);
    }
  }

  function agentChipInteract() {
    const chips = document.querySelectorAll(".sa-agent-chip[data-biz-role]");
    chips.forEach((chip) => {
      chip.addEventListener("mouseenter", () => highlightAgentRole(chip.dataset.bizRole));
      chip.addEventListener("focus", () => highlightAgentRole(chip.dataset.bizRole));
      chip.addEventListener("mouseleave", () => {
        chips.forEach((c) => c.classList.remove("is-highlight"));
        document.querySelectorAll(".sa-biz-orbit-agent").forEach((a) => a.classList.remove("is-synced"));
      });
    });
  }

  function orchestratorMetaRotate() {
    const meta = document.getElementById("sa-orchestrator-meta");
    if (!meta) return;
    const lines = [
      "$24K pipeline · 3 demos · 6 agents running",
      "Outreach · 12 sends · 3 replies today",
      "Prove · replay demo ready · 15 min close",
      "Build · $8K loop scoping · deposit in",
      "Guard · 1 BLOCK · client protected",
      "Expand · +$2K/mo retainer renewed",
    ];
    let i = 0;
    setInterval(() => {
      i = (i + 1) % lines.length;
      meta.classList.add("is-fade");
      setTimeout(() => {
        meta.textContent = lines[i];
        meta.classList.remove("is-fade");
      }, 200);
    }, 3400);
  }

  function commandHint() {
    const hint = document.querySelector(".sa-command-hint");
    if (!hint) return;
    hint.addEventListener("click", () => {
      showToast("Proof agent · replay demo in <5m · hello@sourcea.app");
    });
  }

  /* ── AgentGo: roster row cycle highlight ── */

  function highlightAgentRole(role) {
    document.querySelectorAll(".sa-agent-chip[data-biz-role]").forEach((c) => {
      c.classList.toggle("is-highlight", c.dataset.bizRole === role);
    });
    document.querySelectorAll(".sa-biz-orbit-agent[data-biz-agent]").forEach((a) => {
      a.classList.toggle("is-synced", a.dataset.bizAgent === role);
    });
  }

  function rosterCycle() {
    const rows = document.querySelectorAll(".sa-roster-row");
    if (!rows.length || reduced) return;
    let active = 0;
    const cycle = () => {
      rows.forEach((r, i) => r.classList.toggle("is-active", i === active));
      const role = rows[active]?.dataset.rosterAgent || null;
      if (role) highlightAgentRole(role);
      active = (active + 1) % rows.length;
    };
    cycle();
    setInterval(cycle, 2800);
  }

  function rosterStagger() {
    document.querySelectorAll(".sa-roster-row").forEach((row, i) => {
      if (reduced) { row.classList.add("sa-roster-in"); return; }
      setTimeout(() => row.classList.add("sa-roster-in"), 700 + i * 90);
    });
  }

  function chainPulse() {
    const beats = document.querySelectorAll(".sa-chain-flow [data-beat]");
    if (!beats.length || reduced) return;
    let i = 0;
    setInterval(() => {
      beats.forEach((b) => b.classList.remove("sa-lit"));
      beats[i % beats.length].classList.add("sa-lit");
      i += 1;
    }, 850);
  }

  function stepCarousel() {
    const steps = document.querySelectorAll(".sa-step");
    if (!steps.length || reduced) return;
    let i = 0;
    setInterval(() => {
      steps.forEach((s) => {
        s.classList.remove("sa-step-active");
        s.querySelectorAll("code").forEach((c) => c.classList.remove("sa-typing"));
      });
      const active = steps[i % steps.length];
      active.classList.add("sa-step-active");
      const code = active.querySelector("code");
      if (code) code.classList.add("sa-typing");
      i += 1;
    }, 2600);
  }

  function animateCount(el) {
    if (!el || el.dataset.saDone === "1" || el.hasAttribute("data-sa-static")) return;
    const raw = el.getAttribute("data-sa-count");
    if (!raw) return;
    const target = parseFloat(raw);
    if (Number.isNaN(target)) return;
    const prefix = el.getAttribute("data-sa-prefix") || "";
    const suffix = el.getAttribute("data-sa-suffix") || "";
    el.dataset.saDone = "1";
    const duration = 1600;
    const start = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - start) / duration);
      const val = Math.round(target * easeOut(p));
      el.textContent = prefix + val + suffix;
      if (p < 1) requestAnimationFrame(tick);
      else el.parentElement?.classList.add("is-counted");
    };
    requestAnimationFrame(tick);
  }

  const motionObs = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;

        if (el.classList.contains("sa-fleet-panel")) {
          el.classList.add("is-mounted");
        }

        if (el.classList.contains("sa-metrics-strip")) {
          el.querySelectorAll(".sa-stat").forEach((s) => s.classList.add("is-counted"));
        }

        el.querySelectorAll("[data-sa-count]").forEach(animateCount);
        motionObs.unobserve(el);
      });
    },
    { threshold: 0.18 }
  );

  document.querySelectorAll(".sa-fleet-panel, .sa-fleet-stats, .sa-metrics-strip, .sa-enterprise-quote, .sa-reference-band").forEach((el) => motionObs.observe(el));

  function categoryCardCycle() {
    const cards = document.querySelectorAll(".sa-category-card");
    if (!cards.length || reduced) return;
    let i = 0;
    setInterval(() => {
      cards.forEach((c) => c.classList.remove("is-active"));
      cards[i % cards.length].classList.add("is-active");
      i += 1;
    }, 4000);
  }
  if (document.querySelector(".sa-category-grid")) categoryCardCycle();

  function scrollParallax() {
    const scene = document.querySelector(".sa-hero-scene");
    const orbs = document.querySelectorAll(".sa-orb");
    const grid = document.querySelector(".sa-grid-perspective");
    if (!scene || reduced) return;
    window.addEventListener("scroll", () => {
      const y = window.scrollY;
      orbs.forEach((orb, i) => {
        orb.style.transform = `translateY(${y * (0.05 + i * 0.025)}px)`;
      });
      if (grid) grid.style.transform = `perspective(520px) rotateX(68deg) translateY(${y * 0.04}px)`;
    }, { passive: true });
  }

  function matrixReveal() {
    const rows = document.querySelectorAll(".sa-matrix tbody tr");
    const checks = document.querySelectorAll(".sa-check");
    if (!rows.length) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (!entries[0].isIntersecting) return;
        if (reduced) {
          checks.forEach((c) => c.classList.add("sa-drawn"));
          obs.disconnect();
          return;
        }
        rows.forEach((row, i) => {
          row.style.opacity = "0";
          row.style.transform = "translateX(-14px)";
          row.style.transition = "opacity 0.5s ease, transform 0.5s cubic-bezier(0.22,1,0.36,1)";
          setTimeout(() => { row.style.opacity = "1"; row.style.transform = "none"; }, 60 + i * 65);
        });
        checks.forEach((c, i) => setTimeout(() => c.classList.add("sa-drawn"), 400 + i * 80));
        obs.disconnect();
      },
      { threshold: 0.12 }
    );
    const table = document.querySelector(".sa-matrix");
    if (table) obs.observe(table);
  }

  function sectionRise() {
    const sel = ".ar-problem-card, .ar-feature-card, .ar-price-card, .sa-trust-item, .sa-step, .sa-trust-band .sa-trust-item, .sa-lifecycle-card, .sa-receipt-card, .sa-terminal-replay, .sa-sb-stage, .sa-growth-console, .sa-growth-stage, .sa-biz-orbit-stage, .sa-biz-outcome";
    document.querySelectorAll(sel).forEach((el, i) => {
      el.classList.add("sa-motion-rise");
      el.style.setProperty("--sa-motion-i", String(i % 10));
    });
    document.querySelectorAll(".ar-section-head").forEach((el) => el.classList.add("sa-motion-rise"));

    if (reduced) {
      document.querySelectorAll(".sa-motion-rise").forEach((el) => el.classList.add("is-inview"));
      return;
    }
    const riseObs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-inview");
            riseObs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );
    document.querySelectorAll(".sa-motion-rise").forEach((el) => riseObs.observe(el));
  }

  function headerScroll() {
    const header = document.querySelector(".sa-header");
    if (!header) return;
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  function pageNavActive() {
    const path = window.location.pathname.replace(/\/$/, "") || "/";
    const parts = path.split("/").filter(Boolean);
    const file = parts[parts.length - 1] || "";

    document.querySelectorAll("[data-sa-nav]").forEach((a) => {
      const href = (a.getAttribute("href") || "").replace(/\/$/, "") || "/";
      let active = false;

      if (a.hasAttribute("data-sa-nav-home")) {
        active = path === "/" || path === "" || file === "founder-home";
      } else if (a.hasAttribute("data-sa-nav-mvp")) {
        active =
          path === "/start" ||
          path.endsWith("/start") ||
          file === "48h-mvp" ||
          file === "mvp-landing" ||
          path.endsWith("/48h-mvp");
      } else if (href === "/sourcea" || href.endsWith("/sourcea")) {
        active = path === "/sourcea" || (parts[0] === "sourcea" && parts.length === 1);
      } else {
        const segments = href.split("/").filter(Boolean);
        const target = segments[segments.length - 1] || "";
        active =
          Boolean(target && file === target) ||
          path === href ||
          (href.startsWith("/sourcea/") && path.endsWith(href.replace("/sourcea", "")));
      }

      a.classList.toggle("is-active", active);
      if (active) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function navSpy() {
    const links = document.querySelectorAll("[data-sa-nav]");
    const sections = [];
    links.forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (!href.startsWith("#")) return;
      const id = href.slice(1);
      const el = id ? document.getElementById(id) : null;
      if (el) sections.push({ link, el });
    });
    if (!sections.length) {
      pageNavActive();
      return;
    }
    const onSpy = () => {
      const y = window.scrollY + 120;
      let current = sections[0].el;
      sections.forEach(({ el }) => { if (el.offsetTop <= y) current = el; });
      links.forEach((l) => l.classList.toggle("is-active", l.getAttribute("href") === "#" + current.id));
    };
    window.addEventListener("scroll", onSpy, { passive: true });
    onSpy();
  }

  function btnMagnetic() {
    if (reduced) return;
    document.querySelectorAll(".sa-btn-glow, .ar-btn-primary").forEach((btn) => {
      btn.addEventListener("mousemove", (e) => {
        const r = btn.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) * 0.12;
        const y = (e.clientY - r.top - r.height / 2) * 0.12;
        btn.style.transform = `translate(${x}px, ${y}px)`;
      });
      btn.addEventListener("mouseleave", () => { btn.style.transform = ""; });
    });
  }

  function cardTilt() {
    if (!finePointer || reduced) return;
    document.querySelectorAll(".ar-feature-card, .ar-price-card").forEach((card) => {
      card.addEventListener("mousemove", (e) => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = `perspective(800px) rotateY(${x * 6}deg) rotateX(${-y * 5}deg) translateY(-5px)`;
      });
      card.addEventListener("mouseleave", () => { card.style.transform = ""; });
    });
  }

  /* ── Agent circle sandbox — narrative theater ── */
  function sandboxTheater() {
    const stage = document.getElementById("sa-sandbox");
    if (!stage) return;

    const agents = {};
    stage.querySelectorAll("[data-agent]").forEach((el) => {
      agents[el.dataset.agent] = { el, angle: Number(el.dataset.angle) };
    });
    const arc = document.getElementById("sa-sb-pulse-arc");
    const narrator = document.getElementById("sa-sb-narrator");
    const actEl = document.getElementById("sa-sb-act");
    const verdictEl = document.getElementById("sa-sb-verdict");
    const cx = 210;
    const cy = 210;
    const r = 155;

    const beats = [
      { who: "brain", act: "Act I · Wake", verdict: "· LIVE", narrator: "2:14am. While your team sleeps, the orchestrator reads your disk — not yesterday's chat.", line: "Good morning path starts here — council online." },
      { who: "broker", act: "Act II · Context", verdict: "· FOUND", narrator: "Context arrives first. Benchmarks, prior threads, handoff notes — gathered before anyone prompts.", line: "Found your AB1 thread + benchmark. Handing to worker." },
      { who: "worker", act: "Act III · Propose", verdict: "· QUEUED", narrator: "Your worker proposes the action: a governed send, scoped and slim — no paste-the-entire-repo.", line: "Outreach queued — ready for policy check." },
      { who: "gate", act: "Act IV · Scope", verdict: "· PASS", narrator: "The gate answers: is this role allowed, is the session feasible, is scope within bounds?", line: "Scope clear · session feasible · proceed." },
      { who: "critic", act: "Act V · Policy", verdict: "· ALLOW", narrator: "Policy speaks at dispatch — the moment that matters, not the kickoff meeting last Tuesday.", line: "Policy allows · this action may run." },
      { who: "factory", act: "Act VI · Record", verdict: "· SYNCED", narrator: "The verdict writes to disk. Tomorrow you open evidence, not a Slack thread.", line: "Recorded on disk · dual-proof sealed." },
      { who: "spine", act: "Act VII · Wire", verdict: "· LIVE", narrator: "Automation spine connects — your orchestrator and workflow stay in sync with the receipt.", line: "Loop wired · receipt path connected." },
      { who: "receipt", act: "Act VIII · Seal", verdict: "· PASS", narrator: "PASS means you can replay. Your client gets proof, not promises.", line: "Verdict sealed · export ready for Monday." },
      { who: "brain", act: "Act IX · Align", verdict: "· ALL IN", narrator: "Eight voices, one story: what was proposed, what was checked, what landed on disk.", line: "Council aligned · show this on screen-share." },
      { who: "critic", act: "Act X · Stop", verdict: "· BLOCK", narrator: "Same night — a rogue edit tries to slip through. Policy says no. The loop stops. That is the demo.", line: "Blocked · out-of-scope write refused." },
      { who: "brain", act: "Act XI · Close", verdict: "· SEALED", narrator: "Every turn logged. This is what you owe your buyer — proof of what executed last night.", line: "Night closed · full receipt on disk." },
    ];

    const polar = (deg) => {
      const rad = (deg * Math.PI) / 180;
      return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
    };

    const setArc = (fromDeg, toDeg) => {
      if (!arc) return;
      const a = polar(fromDeg);
      const b = polar(toDeg);
      const large = Math.abs(toDeg - fromDeg) > 180 ? 1 : 0;
      const sweep = toDeg > fromDeg ? 1 : 0;
      arc.setAttribute("d", `M ${a.x} ${a.y} A ${r} ${r} 0 ${large} ${sweep} ${b.x} ${b.y}`);
      arc.classList.add("is-active");
    };

    let beatIdx = 0;
    let prevAngle = beats[0].who;
    let running = false;
    let timer = null;

    const speak = (beat) => {
      Object.values(agents).forEach((a) => {
        if (!a.el) return;
        a.el.classList.remove("is-speaking", "is-listening");
        const bubble = a.el.querySelector(".sa-sb-bubble");
        const p = a.el.querySelector(".sa-sb-bubble p");
        if (bubble) bubble.classList.remove("is-typing");
        if (p) p.textContent = "";
      });

      const current = agents[beat.who];
      if (!current?.el) return;

      Object.values(agents).forEach((a) => {
        if (a.el && a.el !== current.el) a.el.classList.add("is-listening");
      });
      current.el.classList.add("is-speaking");

      const prev = agents[prevAngle];
      if (prev && beat.who !== prevAngle) {
        setArc(prev.angle, current.angle);
      } else {
        arc?.classList.remove("is-active");
      }
      prevAngle = beat.who;

      stage.classList.add("is-speaking");
      if (actEl) actEl.textContent = beat.act;
      if (verdictEl) {
        verdictEl.textContent = beat.verdict;
        verdictEl.className = "sa-sb-verdict" + (beat.verdict.includes("BLOCK") ? " is-block" : beat.verdict.includes("PASS") || beat.verdict.includes("SEALED") ? " is-pass" : "");
      }
      if (narrator) {
        narrator.classList.add("is-fade");
        setTimeout(() => {
          narrator.textContent = beat.narrator;
          narrator.classList.remove("is-fade");
        }, 180);
      }

      const bubble = current.el.querySelector(".sa-sb-bubble");
      const p = current.el.querySelector(".sa-sb-bubble p");
      if (p) {
        if (reduced) {
          p.textContent = beat.line;
        } else {
          bubble?.classList.add("is-typing");
          streamText(p, beat.line, 22);
          setTimeout(() => bubble?.classList.remove("is-typing"), beat.line.length * 22 + 400);
        }
      }
    };

    const tick = () => {
      if (!running) return;
      speak(beats[beatIdx]);
      beatIdx = (beatIdx + 1) % beats.length;
      timer = setTimeout(tick, reduced ? 3800 : 4000);
    };

    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries[0]?.isIntersecting;
        if (visible && !running) {
          running = true;
          beatIdx = 0;
          prevAngle = beats[0].who;
          tick();
        } else if (!visible && running) {
          running = false;
          if (timer) clearTimeout(timer);
          stage.classList.remove("is-speaking");
          arc?.classList.remove("is-active");
        }
      },
      { threshold: 0.35 }
    );
    obs.observe(stage);

    if (reduced) {
      obs.disconnect();
      running = true;
      tick();
      return;
    }
  }

  /* ── Business command center (hero panel) ── */
  function businessCommandCenter() {
    const panel = document.getElementById("sa-biz-command");
    const tabs = document.querySelectorAll(".sa-biz-tab");
    const rays = document.querySelectorAll(".sa-biz-central-rays span");
    const tabCopy = {
      overview: "Brain routing · 6 agents active · $24K pipeline",
      pipeline: "3 demos booked · 34% proof-to-close · $8K deposit in",
      ops: "Guard blocked 1 rogue edit · all other agents PASS",
      proof: "Replay sealed · ALLOW + BLOCK demo ready in 15 min",
    };
    const tabRoles = { overview: "brain", pipeline: "outreach", ops: "guard", proof: "prove" };
    const log = document.getElementById("sa-factory-log");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("is-active"));
        tab.classList.add("is-active");
        const key = tab.dataset.bizTab;
        if (panel) {
          panel.classList.add("is-tab-switch");
          setTimeout(() => panel.classList.remove("is-tab-switch"), 350);
        }
        if (log && tabCopy[key]) streamText(log, tabCopy[key]);
        rays.forEach((r, i) => r.classList.toggle("is-lit", i < (key === "overview" ? 6 : key === "pipeline" ? 4 : key === "ops" ? 2 : 5)));
        if (tabRoles[key]) highlightAgentRole(tabRoles[key]);
      });
    });
    if (rays.length && !reduced) {
      let ri = 0;
      setInterval(() => {
        rays.forEach((r) => r.classList.remove("is-lit"));
        const count = 3 + (ri % 4);
        for (let i = 0; i < count; i++) rays[i]?.classList.add("is-lit");
        ri += 1;
      }, 2400);
    }
    if (!reduced && tabs.length) {
      let ti = 0;
      const tabKeys = ["overview", "pipeline", "ops", "proof"];
      setInterval(() => {
        ti = (ti + 1) % tabKeys.length;
        const tab = document.querySelector(`.sa-biz-tab[data-biz-tab="${tabKeys[ti]}"]`);
        if (tab && !panel?.matches(":hover")) tab.click();
      }, 8000);
    }
  }

  /* ── Business team orbit (central intelligence) ── */
  function businessTeamOrbit() {
    const stage = document.getElementById("sa-biz-orbit");
    if (!stage) return;
    const root = stage.querySelector(".sa-biz-orbit-stage");
    const agents = {};
    stage.querySelectorAll("[data-biz-agent]").forEach((el) => {
      agents[el.dataset.bizAgent] = { el, angle: Number(el.dataset.angle) };
    });
    const arc = document.getElementById("sa-biz-orbit-arc");
    const spoke = document.getElementById("sa-biz-orbit-spoke");
    const narrator = document.getElementById("sa-biz-orbit-narrator");
    const actEl = document.getElementById("sa-biz-orbit-act");
    const cx = 200;
    const cy = 200;
    const r = 148;

    const beats = [
      { who: "brain", act: "Orchestrating", narrator: "Brain assigns tonight's work — outreach warms pipeline while guard watches ops.", line: "Routing all agents from your disk." },
      { who: "outreach", act: "Pipeline", narrator: "Outreach agent books conversations — every send scoped, receipted, on brand.", line: "12 sends · 3 replies · proof deck attached." },
      { who: "prove", act: "Closing", narrator: "Prove agent packs the replay demo — ALLOW, BLOCK, tamper live on screen-share.", line: "Demo ready · 34% proof-to-close rate." },
      { who: "build", act: "Delivering", narrator: "Build agent scopes the $8K loop — fixed price, 2–3 weeks, handoff included.", line: "Deposit in · balance on PASS." },
      { who: "guard", act: "Protecting", narrator: "Guard agent blocks a rogue ops edit — your client's brand stays safe.", line: "BLOCK fired · out-of-scope refused." },
      { who: "expand", act: "Compounding", narrator: "Expand agent renews retainer — weekly proof export signed, +$2K/mo MRR.", line: "Retainer renewed · trust compounds." },
      { who: "brain", act: "Aligned", narrator: "Six specialists, one command center — your buyer sees a team running their business.", line: "All agents aligned · show this live." },
    ];

    const polar = (deg) => {
      const rad = (deg * Math.PI) / 180;
      return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
    };
    const setArc = (fromDeg, toDeg) => {
      if (!arc) return;
      const a = polar(fromDeg);
      const b = polar(toDeg);
      const large = Math.abs(toDeg - fromDeg) > 180 ? 1 : 0;
      const sweep = toDeg > fromDeg ? 1 : 0;
      arc.setAttribute("d", `M ${a.x} ${a.y} A ${r} ${r} 0 ${large} ${sweep} ${b.x} ${b.y}`);
      arc.classList.add("is-active");
    };
    const setSpoke = (angleDeg) => {
      if (!spoke) return;
      const rad = (angleDeg * Math.PI) / 180;
      const end = { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
      spoke.setAttribute("x1", cx);
      spoke.setAttribute("y1", cy);
      spoke.setAttribute("x2", end.x);
      spoke.setAttribute("y2", end.y);
      spoke.classList.add("is-active");
    };

    let beatIdx = 0;
    let prevWho = beats[0].who;
    let running = false;
    let timer = null;

    const speak = (beat) => {
      Object.values(agents).forEach((a) => {
        if (!a.el) return;
        a.el.classList.remove("is-speaking", "is-listening");
        const p = a.el.querySelector(".sa-biz-orbit-bubble p");
        if (p) p.textContent = "";
      });
      const current = agents[beat.who];
      if (!current?.el) return;
      Object.values(agents).forEach((a) => {
        if (a.el && a.el !== current.el) a.el.classList.add("is-listening");
      });
      current.el.classList.add("is-speaking");
      highlightAgentRole(beat.who);
      const prev = agents[prevWho];
      if (prev && beat.who !== prevWho) setArc(prev.angle, current.angle);
      else arc?.classList.remove("is-active");
      setSpoke(current.angle);
      prevWho = beat.who;
      root?.classList.add("is-speaking");
      if (actEl) actEl.textContent = beat.act;
      if (narrator) {
        narrator.classList.add("is-fade");
        setTimeout(() => {
          narrator.textContent = beat.narrator;
          narrator.classList.remove("is-fade");
        }, 180);
      }
      const p = current.el.querySelector(".sa-biz-orbit-bubble p");
      if (p) {
        if (reduced) p.textContent = beat.line;
        else streamText(p, beat.line, 20);
      }
    };

    const tick = () => {
      if (!running) return;
      speak(beats[beatIdx]);
      beatIdx = (beatIdx + 1) % beats.length;
      timer = setTimeout(tick, reduced ? 3500 : 3800);
    };

    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries[0]?.isIntersecting;
        if (visible && !running) { running = true; beatIdx = 0; prevWho = beats[0].who; tick(); }
        else if (!visible && running) { running = false; if (timer) clearTimeout(timer); }
      },
      { threshold: 0.25 }
    );
    obs.observe(stage);

    const outcomes = document.querySelectorAll(".sa-biz-outcome");
    if (outcomes.length && !reduced) {
      let oi = 0;
      setInterval(() => {
        outcomes.forEach((o) => o.classList.remove("is-active"));
        outcomes[oi % outcomes.length].classList.add("is-active");
        oi += 1;
      }, 3200);
    }
  }

  /* ── Growth system motion ── */
  function growthSystem() {
    const stages = document.querySelectorAll("[data-growth-stage]");
    if (stages.length && !reduced) {
      let si = 0;
      setInterval(() => {
        stages.forEach((s) => s.classList.remove("is-active"));
        stages[si % stages.length].classList.add("is-active");
        si += 1;
      }, 2800);
    }

    const weekLine = document.getElementById("sa-growth-week-line");
    if (weekLine) {
      const lines = [
        "3 proof packet reviews completed · proof deck attached to every intake",
        "$24K open pipeline · 2 loop builds in scoping",
        "Proof-to-close at 34% · replay demo is the closer",
        "Retainer expansion +$2K/mo · weekly export signed off",
        "11-day avg close · discovery to deposit",
      ];
      let wi = 0;
      setInterval(() => {
        wi = (wi + 1) % lines.length;
        weekLine.style.opacity = "0.4";
        setTimeout(() => {
          weekLine.textContent = lines[wi];
          weekLine.style.opacity = "1";
        }, 200);
      }, 3600);
    }

    const bars = document.querySelectorAll(".sa-growth-bar-fill");
    const barObs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          const fill = e.target;
          const pct = fill.dataset.saBar || "0";
          setTimeout(() => { fill.style.width = pct + "%"; }, 120);
          barObs.unobserve(fill);
        });
      },
      { threshold: 0.3 }
    );
    bars.forEach((b) => barObs.observe(b));

    const pipelineCards = document.querySelectorAll(".sa-pipeline-card");
    if (pipelineCards.length && !reduced) {
      let pi = 0;
      setInterval(() => {
        pipelineCards.forEach((c) => c.classList.remove("is-active"));
        pipelineCards[pi % pipelineCards.length].classList.add("is-active");
        pi += 1;
      }, 3000);
    }

    const growthAgents = document.querySelectorAll(".sa-growth-agent");
    if (growthAgents.length && !reduced) {
      let gi = 0;
      setInterval(() => {
        growthAgents.forEach((a) => a.classList.remove("is-running"));
        growthAgents[gi % growthAgents.length].classList.add("is-running");
        gi += 1;
      }, 2600);
    }

    document.querySelectorAll(".sa-growth-metric strong[data-sa-count]").forEach((el) => {
      const obs = new IntersectionObserver(
        (entries) => {
          if (!entries[0].isIntersecting) return;
          const target = Number(el.dataset.saCount) || 0;
          const prefix = el.dataset.saPrefix || "";
          const suffix = el.dataset.saSuffix || "";
          if (reduced) { el.textContent = prefix + target + suffix; return; }
          let cur = 0;
          const step = Math.max(1, Math.floor(target / 24));
          const tick = () => {
            cur = Math.min(target, cur + step);
            el.textContent = prefix + cur + suffix;
            if (cur < target) requestAnimationFrame(tick);
          };
          tick();
          obs.disconnect();
        },
        { threshold: 0.5 }
      );
      obs.observe(el);
    });
  }

  headerScroll();
  navSpy();
  sectionRise();
  btnMagnetic();
  cardTilt();

  if (document.querySelector(".sa-hero-cinematic")) {
    heroEntrance();
    if (!document.body.classList.contains("sa-root-home")) {
      fleetTilt();
      heroParallax();
      scrollParallax();
    }
  }
  if (document.querySelector(".sa-roster")) {
    rosterStagger();
    rosterCycle();
  }
  if (document.getElementById("sa-factory-log") && !window.SourceALiveConsole && !document.body.classList.contains("sa-root-home")) factoryLog();
  if (document.getElementById("sa-agent-pill-text")) agentPillRotate();
  if (document.querySelector(".sa-engine-chip")) engineChipPulse();
  if (document.querySelector(".sa-agent-chip")) agentSwarmCycle();
  if (document.querySelector(".sa-receipt-card")) receiptFeedCycle();
  if (document.querySelector(".sa-lifecycle-card")) lifecycleCycle();
  if (document.getElementById("sa-orchestrator")) {
    orchestrator();
    commandHint();
  }
  if (document.querySelector("[data-beat]")) chainPulse();
  if (document.querySelector(".sa-step")) stepCarousel();
  if (document.querySelector(".sa-matrix")) matrixReveal();
  if (document.querySelector(".sa-agent-chip[data-biz-role]")) agentChipInteract();
  if (document.getElementById("sa-orchestrator-meta")) orchestratorMetaRotate();
  if (document.getElementById("sa-biz-command") && !window.SourceALiveConsole && !document.body.classList.contains("sa-root-home")) businessCommandCenter();
  if (document.getElementById("sa-biz-orbit")) businessTeamOrbit();
  if (document.getElementById("sa-sandbox")) sandboxTheater();
  if (document.querySelector(".sa-growth-console")) growthSystem();

  const initCode = document.querySelector(".sa-step.sa-step-active code");
  if (initCode) initCode.classList.add("sa-typing");
})();
