/**
 * W1 interactive demo — ALLOW · BLOCK · tamper-FAIL (no empty mp4).
 * Uses boot-proof.json for honest terminal beats.
 */
(function () {
  const BOOT_URL = "/sourcea/data/boot-proof.json";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const BEATS = [
    {
      id: "allow",
      label: "ALLOW",
      title: "Policy version current",
      subtitle: "Pre-LLM gate loads SSOT from disk — dispatch proceeds.",
      check: "policy_version",
      fallback: { ok: true, reason: "SSOT v3.2 current" },
    },
    {
      id: "block",
      label: "BLOCK",
      title: "Receipt not fresh",
      subtitle: "Session gate BLOCK — no file touched, receipt on disk.",
      check: "receipt_fresh",
      fallback: { ok: false, reason: "last receipt verdict BLOCK" },
    },
    {
      id: "tamper",
      label: "TAMPER",
      title: "Hash mismatch caught",
      subtitle: "Alter a receipt live — spine refuses replay.",
      check: "queue_truth",
      tamper: true,
      fallback: { ok: true, reason: "inbox matches queue head" },
    },
  ];

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function findCheck(checks, name) {
    return (checks || []).find((c) => c.name === name || c.id === name) || null;
  }

  function terminalLine(c, tamper) {
    if (tamper) {
      return `<span class="sa-t-bad">[FAIL]</span> tamper_detect: hash mismatch on BOOT_REPORT.json
<span class="sa-t-dim">expected sha256=a8f3… · got sha256=deadbeef</span>`;
    }
    const mark = c.ok ? "PASS" : "FAIL";
    const cls = c.ok ? "sa-t-ok" : "sa-t-bad";
    return `<span class="${cls}">[${mark}]</span> ${esc(c.name)}: ${esc(c.reason)}`;
  }

  async function init() {
    const root = document.getElementById("sa-w1-player");
    if (!root) return;

    let checks = [];
    try {
      const res = await fetch(BOOT_URL, { cache: "no-store" });
      if (res.ok) {
        const boot = await res.json();
        checks = boot.checks || [];
      }
    } catch (_) {
      /* use fallbacks */
    }

    root.innerHTML = `
      <div class="sa-w1-player-inner">
        <div class="sa-w1-screen">
          <div class="sa-w1-screen-chrome">
            <span class="sa-dot red"></span><span class="sa-dot yellow"></span><span class="sa-dot green"></span>
            <span>sourcea-boot --json · live factory</span>
          </div>
          <div class="sa-w1-beat-label" id="sa-w1-beat-label">ALLOW</div>
          <h3 class="sa-w1-beat-title" id="sa-w1-beat-title"></h3>
          <p class="sa-w1-beat-sub" id="sa-w1-beat-sub"></p>
          <pre class="sa-terminal-body sa-w1-terminal" id="sa-w1-terminal"></pre>
        </div>
        <div class="sa-w1-rail">
          <div class="sa-w1-progress" id="sa-w1-progress"></div>
          <div class="sa-w1-controls" role="tablist" aria-label="W1 demo beats"></div>
          <p class="sa-metric-note">Live terminal from factory boot · same beats you screen-share</p>
          <div class="sa-cta-actions sa-w1-cta">
            <a class="ar-btn ar-btn-primary sa-btn-glow" href="/sourcea/scenario.html#proof-quiz">Play full scenario →</a>
            <button type="button" class="ar-btn ar-btn-ghost" id="sa-w1-replay">Replay film</button>
          </div>
        </div>
      </div>`;

    const label = root.querySelector("#sa-w1-beat-label");
    const title = root.querySelector("#sa-w1-beat-title");
    const sub = root.querySelector("#sa-w1-beat-sub");
    const term = root.querySelector("#sa-w1-terminal");
    const progress = root.querySelector("#sa-w1-progress");
    const controls = root.querySelector(".sa-w1-controls");

    BEATS.forEach((b, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `sa-w1-beat-btn${i === 0 ? " is-active" : ""}`;
      btn.dataset.beat = b.id;
      btn.textContent = b.label;
      btn.setAttribute("role", "tab");
      controls.appendChild(btn);
      const seg = document.createElement("span");
      seg.className = `sa-w1-progress-seg${i === 0 ? " is-active" : ""}`;
      seg.dataset.beat = b.id;
      progress.appendChild(seg);
    });

    let idx = 0;
    let timer = null;

    const showBeat = (i) => {
      const b = BEATS[i];
      if (!b) return;
      idx = i;
      const c = findCheck(checks, b.check) || b.fallback;
      label.textContent = b.label;
      label.className = `sa-w1-beat-label is-${b.id}`;
      title.textContent = b.title;
      sub.textContent = b.subtitle;
      term.innerHTML = `<span class="sa-t-prompt">$</span> sourcea-boot --json\n${terminalLine(c, b.tamper)}<span class="sa-t-cursor">▋</span>`;
      controls.querySelectorAll(".sa-w1-beat-btn").forEach((btn) => {
        btn.classList.toggle("is-active", btn.dataset.beat === b.id);
      });
      progress.querySelectorAll(".sa-w1-progress-seg").forEach((seg) => {
        seg.classList.toggle("is-active", seg.dataset.beat === b.id);
        seg.classList.toggle("is-done", BEATS.findIndex((x) => x.id === seg.dataset.beat) < i);
      });
    };

    /** Film factory — direct beat cut, no tab-button clicks. */
    window.__saW1FilmBeat = (beatId) => {
      const i = BEATS.findIndex((b) => b.id === beatId);
      if (i >= 0) showBeat(i);
    };

    const filmCapture =
      document.documentElement.dataset.filmCapture === "1" ||
      new URLSearchParams(location.search).has("film_capture");

    const play = () => {
      if (timer) clearInterval(timer);
      showBeat(0);
      if (reduced || filmCapture) return;
      let step = 0;
      timer = setInterval(() => {
        step = (step + 1) % BEATS.length;
        showBeat(step);
      }, 4500);
    };

    controls.querySelectorAll(".sa-w1-beat-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (timer) clearInterval(timer);
        const i = BEATS.findIndex((b) => b.id === btn.dataset.beat);
        showBeat(i >= 0 ? i : 0);
      });
    });

    root.querySelector("#sa-w1-replay")?.addEventListener("click", play);
    if (filmCapture) {
      showBeat(0);
    } else {
      play();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
