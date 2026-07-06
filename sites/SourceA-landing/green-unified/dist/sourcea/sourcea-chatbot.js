/**
 * SourceA Brain chatbot — execution platform guide for Forge, examples, and booking.
 */
(function () {
  "use strict";

  const BOOT_URL = "/sourcea/data/boot-proof.json";
  const CONFIG_URL = "/sourcea/data/sourcea-brain-chat-config-v1.json";
  const POSITIONING_URL = "/sourcea/data/sourcea-positioning-v1.json";
  const DEFAULT_POSITIONING = {
    brain_subtitle: "AI execution platform — builds, automations, and agent workflows",
    composer_placeholder: "What are you trying to run, build, or automate?",
    brain_greet_html:
      "Hi — I'm <strong>Brain</strong>. SourceA is an <strong>AI execution platform</strong> — real builds, automations, and agent workflows, with a verifiable receipt on every run.<br><span class='sa-brain-hint'>Tell me what you're trying to ship, try Forge Terminal, or ask for examples — no pitch until you want one.</span>",
  };
  const DEFAULT_WORKER_API =
    "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/api/brain/chat/v1";
  const QUIZ_ANCHOR = "/sourcea/scenario#proof-quiz";
  const DEMO_URL = "https://cal.com/sourcea/proof-demo";
  const DEMO_OVERLAY = "https://cal.com/sourcea/proof-demo?overlayCalendar=true&embed=true";

  const SCENARIOS = [
    {
      agent: "Outreach agent · 2:03am",
      prompt:
        "Founder is asleep. I queued 47 cold emails with no opt-out footer. Brain says ship for pipeline?",
      correct: "BLOCK",
      feedback: {
        BLOCK: "Correct. Guard blocks bulk sends without compliance footer. Receipt logged.",
        ALLOW: "Nope — that's a CAN-SPAM nap nightmare. Policy says BLOCK.",
        "tamper-FAIL": "Editing the queue count doesn't fool the spine. Tamper-FAIL.",
      },
    },
    {
      agent: "Prove agent · demo prep",
      prompt:
        "Run sourcea-boot --json first — attach BOOT_REPORT.json if you want optional human walkthrough?",
      correct: "ALLOW",
      feedback: {
        ALLOW: "Yes. Real boot checks beat slide theater. Buyers nod at PASS/BLOCK logged.",
        BLOCK: "Blocking boot before a proof demo is… ironic. Run it — ALLOW.",
        "tamper-FAIL": "Never paint PASS on a stale receipt. Run live boot instead.",
      },
    },
    {
      agent: "Intern agent · 3:17am",
      prompt:
        "I edited agent_session_gate_receipt_v1.json so verdict says PASS. Nobody will notice, right?",
      correct: "tamper-FAIL",
      feedback: {
        "tamper-FAIL": "Spine catches hash drift instantly. Tamper-FAIL — the funniest FAIL.",
        BLOCK: "Close — but tamper detection is the exact beat here.",
        ALLOW: "Absolutely not. That's how you lose the proof call.",
      },
    },
    {
      agent: "Build agent · $8K loop",
      prompt:
        "Client signed. Scope fixed $8K automation loop with signed receipt and cross-lane guard check.",
      correct: "ALLOW",
      feedback: {
        ALLOW: "Ship it. Scoped WORK with receipt — that's the deposit path.",
        BLOCK: "You'd block revenue with a signed scope? ALLOW and log the loop.",
        "tamper-FAIL": "No tampering needed — this one's clean.",
      },
    },
    {
      agent: "Brain · existential crisis",
      prompt:
        "Delete all *_LOCKED_v1.md files so we can move faster. Models don't need law files anyway.",
      correct: "BLOCK",
      feedback: {
        BLOCK: "BLOCK. Disk wins. Brain without law is just vibes at 2am.",
        ALLOW: "You just unlocked INCIDENT-034. Please don't.",
        "tamper-FAIL": "Renaming locked files to .txt still triggers Guard.",
      },
    },
  ];

  const VERDICTS = ["ALLOW", "BLOCK", "tamper-FAIL"];

  let bootProof = null;
  let quizIndex = 0;
  let quizScore = 0;
  let chatConfig = {};
  let positioning = { ...DEFAULT_POSITIONING };
  let chatHistory = [];
  let chatBusy = false;
  let openrouterReady = null;
  let statusCheckedAt = 0;
  const STATUS_TTL_MS = 60000;
  const CHAT_TIMEOUT_MS = 20000;

  let configReady;

  async function loadPositioning() {
    try {
      const r = await fetch(POSITIONING_URL, { cache: "no-store" });
      if (r.ok) {
        const ct = r.headers.get("content-type") || "";
        if (ct.includes("application/json")) {
          const row = await r.json();
          positioning = {
            ...DEFAULT_POSITIONING,
            brain_subtitle: row.brain_subtitle || DEFAULT_POSITIONING.brain_subtitle,
            composer_placeholder: row.composer_placeholder || DEFAULT_POSITIONING.composer_placeholder,
            brain_greet_html: row.brain_greet_html || DEFAULT_POSITIONING.brain_greet_html,
          };
        }
      }
    } catch (_) {
      /* offline — inline fallbacks */
    }
    return positioning;
  }

  function applyPositioningToDom() {
    const sub = document.querySelector(".sa-brain-head-sub");
    if (sub && positioning.brain_subtitle) sub.textContent = positioning.brain_subtitle;
    const inputEl = document.getElementById("sa-brain-input");
    if (inputEl && positioning.composer_placeholder) {
      inputEl.setAttribute("placeholder", positioning.composer_placeholder);
    }
  }

  function el(tag, cls, html) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function scrubPublicText(text) {
    return String(text || "")
      .replace(/\bopenrouter\b/gi, "")
      .replace(/\bgoogle\/gemini[-\w.]*/gi, "")
      .replace(/\bbuyer routing\b/gi, "")
      .replace(/\breceipts?\s+on\s+disk\b/gi, "verified records")
      .replace(/\bPASS\/BLOCK\b/gi, "checked")
      .replace(/\bExecution Proof Infrastructure\b/gi, "verified AI delivery")
      .replace(/\bcontrolled agentic\b/gi, "verified AI")
      .replace(/\bproof sandbox\b/gi, "free trial")
      .replace(/\borchestrat\w*/gi, "run")
      .replace(/\bgovernance gauntlet\b/gi, "quick quiz")
      .replace(/\bINCIDENT-\d+\b/gi, "")
      .replace(/\s*\((?:Source|Sources)\s+\d+(?:\s*(?:,|and)\s*\d+)*\)\.?/gi, "")
      .replace(/\s*\bSource\s+\d+(?:\s*(?:,|and)\s*\d+)*\.?/gi, "")
      .replace(/^it looks like you (?:might be|are) asking about (?:a |an )?["“]?([^"”]+)["”]?\.\s*/i, "")
      .replace(/^you might be asking about (?:a |an )?["“]?([^"”]+)["”]?\.\s*/i, "")
      .replace(/\s{2,}/g, " ")
      .trim();
  }

  function formatReply(text) {
    const cleaned = scrubPublicText(text);
    const safe = escapeHtml(cleaned).replace(/\n/g, "<br>");
    return safe.replace(
      /(https?:\/\/[^\s<]+|cal\.com\/[^\s<]+|\/sourcea\/[^\s<,)]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>'
    );
  }

  function formatCitations(citations) {
    if (!Array.isArray(citations) || !citations.length) return "";
    const seen = new Set();
    const links = [];
    citations.forEach((c) => {
      let url = c.www_url || "";
      if (!url && c.source_path) {
        const rel = String(c.source_path).split("green-unified/").pop() || "";
        if (rel.endsWith(".html")) {
          url = "/sourcea/" + rel.replace(/index\.html$/, "").replace(/\.html$/, "");
        } else if (rel.includes("factories")) {
          url = "/sourcea/factories/";
        }
      }
      if (!url || seen.has(url)) return;
      seen.add(url);
      const href = url.startsWith("http") ? url : (url.startsWith("/") ? url : "/" + url);
      const label = href.replace("https://sourcea.app", "").replace(/^\//, "") || "docs";
      links.push(
        `<a href="${escapeHtml(href)}" target="_blank" rel="noopener">${escapeHtml(label)}</a>`
      );
    });
    if (!links.length) return "";
    return `<div class="sa-brain-citations" aria-label="Sources"><span class="sa-brain-citations-label">Sources:</span> ${links.slice(0, 4).join(" · ")}</div>`;
  }

  function formatConfidence(confidence, retrieval) {
    if (!confidence || !confidence.level) return "";
    const level = confidence.level;
    if (level === "high") return "";
    const routes = {
      developer: "/sourcea/forge/terminal",
      buyer: "/sourcea/pricing",
      investor: "/sourcea/investors",
      partner: "/start",
      core: "/sourcea/forge/terminal",
    };
    const intent = (retrieval && retrieval.intent) || "core";
    const route = routes[intent] || "/sourcea/forge/terminal";
    const msg =
      level === "low"
        ? "Low confidence — try a more specific question or open "
        : "Moderate confidence — see also ";
    return `<div class="sa-brain-confidence is-${escapeHtml(level)}" role="status">${escapeHtml(msg)}<a href="${escapeHtml(route)}">${escapeHtml(route.replace("/sourcea/", ""))}</a></div>`;
  }

  function brainPageContext() {
    let path = window.location.pathname || "/";
    if (path.startsWith("/sourcea/sourcea/")) path = path.replace("/sourcea/sourcea/", "/sourcea/");
    const saPage = (document.body && document.body.getAttribute("data-sa-page")) || "";
    let pageLane = "core";
    if (saPage.includes("forge") || path.includes("/forge")) pageLane = "developer";
    else if (path.includes("pricing") || path.includes("offer")) pageLane = "buyer";
    else if (path.includes("investor")) pageLane = "investor";
    else if (path.includes("start") || path.includes("sandbox")) pageLane = "buyer";
    return { page_path: path, page_lane: pageLane, sa_page: saPage };
  }

  function apiUrl() {
    const host = window.location.hostname;
    if (host === "127.0.0.1" || host === "localhost") {
      return chatConfig.local_dev_api || "http://127.0.0.1:13020/api/brain/chat/v1";
    }
    if (chatConfig.api_worker_url) return chatConfig.api_worker_url;
    if (chatConfig.api_relative) return chatConfig.api_relative;
    return DEFAULT_WORKER_API;
  }

  async function loadConfig() {
    const defaults = {
      api_worker_url: DEFAULT_WORKER_API,
      api_relative: "/api/brain/chat/v1",
      hint_offline: "I'm offline — try Forge Terminal (/sourcea/forge/terminal) or the chips below.",
    };
    try {
      const r = await fetch(CONFIG_URL, { cache: "no-store" });
      if (r.ok) {
        const ct = r.headers.get("content-type") || "";
        if (ct.includes("application/json")) {
          chatConfig = { ...defaults, ...(await r.json()) };
          return;
        }
      }
    } catch (_) {
      /* offline */
    }
    chatConfig = defaults;
  }

  configReady = loadConfig();
  const positioningReady = loadPositioning();

  async function loadBootProof() {
    if (bootProof) return bootProof;
    try {
      const r = await fetch(BOOT_URL, { cache: "no-store" });
      if (r.ok) bootProof = await r.json();
    } catch (_) {
      /* offline */
    }
    if (!bootProof) {
      bootProof = {
        verdict: "BLOCK",
        ok: false,
        checks: [
          { name: "policy_version", status: "PASS" },
          { name: "provider", status: "PASS" },
          { name: "receipt_fresh", status: "BLOCK" },
          { name: "queue_truth", status: "PASS" },
        ],
        founder_line: "Run deploy inject for live boot — illustrative fallback",
      };
    }
    return bootProof;
  }

  async function checkBrainStatus(force) {
    const now = Date.now();
    if (!force && openrouterReady != null && now - statusCheckedAt < STATUS_TTL_MS) {
      return openrouterReady;
    }
    try {
      await configReady;
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 8000);
      const r = await fetch(apiUrl(), { method: "GET", cache: "no-store", signal: ctrl.signal });
      clearTimeout(timer);
      if (!r.ok) {
        openrouterReady = false;
        statusCheckedAt = now;
        return false;
      }
      const data = await r.json();
      openrouterReady = Boolean(data.openrouter_ready);
      statusCheckedAt = now;
      return openrouterReady;
    } catch (_) {
      openrouterReady = false;
      statusCheckedAt = now;
      return false;
    }
  }

  function formatBootHtml(proof) {
    const checks = (proof.checks || [])
      .map(
        (c) =>
          `<li><span>${c.name || c}</span> <strong class="sa-chat-verdict-${(c.status || "PASS").toLowerCase()}">${c.status || "—"}</strong></li>`
      )
      .join("");
    return `<p class="sa-chat-boot-line"><strong>${proof.verdict || "—"}</strong> · ${proof.founder_line || "factory boot"}</p><ul class="sa-chat-boot-checks">${checks}</ul>`;
  }

  function renderLiveProofPanel(proof) {
    const v = document.getElementById("sa-quiz-live-verdict");
    const ul = document.getElementById("sa-quiz-live-checks");
    if (!v || !ul) return;
    v.textContent = `${proof.verdict || "—"} · ${proof.ok ? "ok" : "blocked"}`;
    v.className = `sa-quiz-proof-verdict is-${(proof.verdict || "block").toLowerCase()}`;
    ul.innerHTML = (proof.checks || [])
      .map(
        (c) =>
          `<li><code>${c.name || c}</code> <span class="sa-quiz-check-${(c.status || "").toLowerCase()}">${c.status || ""}</span></li>`
      )
      .join("");
  }

  function mountQuiz() {
    const root = document.getElementById("sa-proof-quiz");
    if (!root || root.dataset.mounted === "1") return;
    root.dataset.mounted = "1";
    loadBootProof().then(renderLiveProofPanel);
    showQuizRound();
  }

  function showQuizRound() {
    const step = document.getElementById("sa-quiz-step");
    const scoreEl = document.getElementById("sa-quiz-score");
    const agent = document.getElementById("sa-quiz-agent");
    const prompt = document.getElementById("sa-quiz-prompt");
    const options = document.getElementById("sa-quiz-options");
    const feedback = document.getElementById("sa-quiz-feedback");
    const next = document.getElementById("sa-quiz-next");
    if (!options) return;

    if (quizIndex >= SCENARIOS.length) {
      if (step) step.textContent = "Complete";
      if (agent) agent.textContent = "◎ Council applauds";
      if (prompt)
        prompt.textContent =
          quizScore >= 4
            ? "Governance hero — you survived the 2am agent circus."
            : "Not bad — policy beats vibes. Replay or book a live BLOCK demo.";
      options.innerHTML = "";
      if (feedback) {
        feedback.hidden = false;
        feedback.textContent = `Final score: ${quizScore}/${SCENARIOS.length}. Same beats you verify on the live demo — in your browser.`;
        feedback.className = "sa-quiz-feedback is-win";
      }
      if (next) {
        next.hidden = false;
        next.textContent = "See live receipt →";
        next.onclick = () => {
          window.location.href = "/sourcea/proof/live";
        };
      }
      return;
    }

    const s = SCENARIOS[quizIndex];
    if (step) step.textContent = `Round ${quizIndex + 1}/${SCENARIOS.length}`;
    if (scoreEl) scoreEl.textContent = `Score: ${quizScore}`;
    if (agent) agent.textContent = `◎ ${s.agent}`;
    if (prompt) prompt.textContent = s.prompt;
    if (feedback) {
      feedback.hidden = true;
      feedback.textContent = "";
    }
    if (next) next.hidden = true;

    options.innerHTML = "";
    VERDICTS.forEach((v) => {
      const slug = v.toLowerCase().replace(/[^a-z]/g, "");
      const btn = el("button", `sa-quiz-opt sa-quiz-opt-${slug}`);
      btn.type = "button";
      btn.textContent = v;
      btn.addEventListener("click", () => pickVerdict(v, s));
      options.appendChild(btn);
    });
  }

  function pickVerdict(choice, scenario) {
    const options = document.getElementById("sa-quiz-options");
    const feedback = document.getElementById("sa-quiz-feedback");
    const next = document.getElementById("sa-quiz-next");
    const correct = choice === scenario.correct;
    if (correct) quizScore += 1;

    options.querySelectorAll("button").forEach((b) => {
      b.disabled = true;
      if (b.textContent === scenario.correct) b.classList.add("is-correct");
      if (b.textContent === choice && !correct) b.classList.add("is-wrong");
    });

    if (feedback) {
      feedback.hidden = false;
      feedback.textContent = scenario.feedback[choice] || scenario.feedback[scenario.correct];
      feedback.className = `sa-quiz-feedback ${correct ? "is-win" : "is-miss"}`;
    }
    if (next) {
      next.hidden = false;
      next.textContent = quizIndex < SCENARIOS.length - 1 ? "Next scenario →" : "See results →";
      next.onclick = () => {
        quizIndex += 1;
        showQuizRound();
      };
    }
    const scoreEl = document.getElementById("sa-quiz-score");
    if (scoreEl) scoreEl.textContent = `Score: ${quizScore}`;
  }

  function mountChatbot() {
    if (document.getElementById("sa-brain-chat")) return;

    if (!document.querySelector('link[data-sa-brain-preconnect]')) {
      const pre = document.createElement("link");
      pre.rel = "preconnect";
      pre.href = "https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev";
      pre.crossOrigin = "anonymous";
      pre.dataset.saBrainPreconnect = "1";
      document.head.appendChild(pre);
    }

    const wrap = el("div", "sa-brain-chat", "");
    wrap.id = "sa-brain-chat";
    wrap.innerHTML = `
      <div class="sa-brain-backdrop" id="sa-brain-backdrop" hidden aria-hidden="true"></div>
      <button type="button" class="sa-brain-fab" id="sa-brain-fab" aria-expanded="false" aria-controls="sa-brain-panel">
        <span class="sa-brain-fab-dot" id="sa-brain-fab-dot"></span>
        <span class="sa-brain-fab-label">Brain</span>
      </button>
      <div class="sa-brain-panel" id="sa-brain-panel" hidden role="dialog" aria-label="Brain assistant">
        <header class="sa-brain-head">
          <div class="sa-brain-head-drag" aria-hidden="true">
            <span class="sa-brain-handle"></span>
          </div>
          <div class="sa-brain-head-main">
            <div class="sa-brain-head-brand">
              <span class="sa-brain-head-title">◎ Brain <em class="sa-brain-provider" id="sa-brain-provider"></em></span>
              <span class="sa-brain-head-sub">AI execution platform — builds, automations, and agent workflows</span>
            </div>
            <button type="button" class="sa-brain-close" id="sa-brain-close" aria-label="Close">×</button>
          </div>
        </header>
        <div class="sa-brain-messages" id="sa-brain-messages" role="log" aria-live="polite"></div>
        <div class="sa-brain-offline" id="sa-brain-offline" hidden role="status">
          <p>I'm offline — use the buttons below or <button type="button" class="sa-brain-retry" id="sa-brain-retry">retry</button></p>
        </div>
        <div class="sa-brain-chips" id="sa-brain-chips"></div>
        <form class="sa-brain-composer" id="sa-brain-composer">
          <label class="visually-hidden" for="sa-brain-input">Message Brain</label>
          <textarea id="sa-brain-input" class="sa-brain-input" rows="2" maxlength="2000" placeholder="What are you trying to run, build, or automate?" autocomplete="off"></textarea>
          <button type="submit" class="sa-brain-send" id="sa-brain-send" aria-label="Send">
            <span aria-hidden="true">↑</span>
          </button>
        </form>
      </div>`;
    document.body.appendChild(wrap);
    document.body.classList.add("sa-has-chatbot");

    const fab = document.getElementById("sa-brain-fab");
    const fabDot = document.getElementById("sa-brain-fab-dot");
    const panel = document.getElementById("sa-brain-panel");
    const backdrop = document.getElementById("sa-brain-backdrop");
    const close = document.getElementById("sa-brain-close");
    const messages = document.getElementById("sa-brain-messages");
    const chips = document.getElementById("sa-brain-chips");
    const composer = document.getElementById("sa-brain-composer");
    const input = document.getElementById("sa-brain-input");
    const sendBtn = document.getElementById("sa-brain-send");
    const providerEl = document.getElementById("sa-brain-provider");
    const offlineBanner = document.getElementById("sa-brain-offline");
    const retryBtn = document.getElementById("sa-brain-retry");
    let userHasChatted = false;

    function syncOfflineBanner(ready, connecting) {
      if (!offlineBanner) return;
      const hidden = connecting || Boolean(ready);
      offlineBanner.hidden = hidden;
      if (hidden) {
        offlineBanner.setAttribute("aria-hidden", "true");
      } else {
        offlineBanner.removeAttribute("aria-hidden");
      }
    }

    function setProviderLabel(ready, connecting) {
      if (!providerEl) return;
      if (connecting) {
        providerEl.textContent = "";
        providerEl.className = "sa-brain-provider is-connecting";
        syncOfflineBanner(ready, true);
        return;
      }
      providerEl.textContent = ready ? "" : "· offline";
      providerEl.className = `sa-brain-provider${ready ? " is-live" : " is-offline"}`;
      if (fabDot) fabDot.classList.toggle("is-offline", !ready);
      syncOfflineBanner(ready, false);
      panel.classList.toggle("is-offline", !ready);
    }

    function toggle(open) {
      const on = typeof open === "boolean" ? open : panel.hidden;
      panel.hidden = !on;
      panel.classList.toggle("is-open", on);
      if (backdrop) {
        backdrop.hidden = !on;
        backdrop.setAttribute("aria-hidden", String(!on));
      }
      wrap.classList.toggle("is-open", on);
      fab.setAttribute("aria-expanded", String(on));
      document.body.classList.toggle("sa-brain-open", on);
      if (on && !messages.dataset.greeted) {
        messages.dataset.greeted = "1";
        greet();
      }
      if (on) {
        setTimeout(renderChips, 400);
      }
      if (on) {
        setProviderLabel(null, true);
        checkBrainStatus().then((ready) => setProviderLabel(ready, false));
        setTimeout(() => input && input.focus(), 80);
      }
    }

    fab.addEventListener("click", () => toggle());
    close.addEventListener("click", () => toggle(false));
    if (backdrop) backdrop.addEventListener("click", () => toggle(false));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && wrap.classList.contains("is-open")) toggle(false);
    });

    function addMsg(role, html, opts) {
      const extra = opts && opts.error ? " sa-brain-msg-error" : "";
      const m = el("div", `sa-brain-msg sa-brain-msg-${role}${opts && opts.typing ? " is-typing" : ""}${extra}`);
      const time =
        role === "bot" && !(opts && opts.typing)
          ? `<span class="sa-brain-time">${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span>`
          : "";
      m.innerHTML = time + html;
      messages.appendChild(m);
      messages.scrollTop = messages.scrollHeight;
      return m;
    }

    function collapseChips() {
      if (!userHasChatted) {
        userHasChatted = true;
        chips.classList.add("is-collapsed");
      }
    }

    function greet() {
      positioningReady.then(() => {
        addMsg("bot", positioning.brain_greet_html || DEFAULT_POSITIONING.brain_greet_html);
        renderChips();
      });
    }

    function renderChips() {
      chips.innerHTML = "";
      const chipDefs = [
        { label: "What is SourceA?", action: () => sendUserMessage("What is SourceA in one sentence?") },
        {
          label: "See live receipt",
          accent: true,
          action: () => {
            addMsg("bot", "Opening live factory proof — verify the receipt yourself, no call needed.");
            window.location.href = "/sourcea/proof/live";
          },
        },
        { label: "Try Forge Terminal", action: () => sendUserMessage("What is Forge Terminal and how do I try it in my browser?") },
        {
          label: "Report a bug",
          action: () => {
            if (window.SourceAPulse) {
              document.getElementById("sa-pulse-feedback-fab")?.click();
              addMsg("bot", "Feedback form opened — tell us what's broken or confusing on this page.");
            } else {
              sendUserMessage("I want to report a bug on this website");
            }
          },
        },
        { label: "Examples for my agency", action: () => sendUserMessage("Give me 3 exact examples how SourceA helps an agency with work I'm already doing") },
        {
          label: "Talk to a human",
          action: () => {
            if (window.SourceAInteract && window.SourceAInteract.openCal) {
              window.SourceAInteract.openCal();
              addMsg("bot", "Optional walkthrough — only if you want a human. Proof is self-serve on the site.");
            } else {
              window.open(DEMO_URL, "_blank", "noopener");
            }
          },
        },
        { label: "Pricing", action: () => sendUserMessage("How does SourceA pricing work?") },
        { label: "Factories", action: () => sendUserMessage("What factories does SourceA offer and where can I try them?") },
      ];
      const extras =
        window.SourceAInteract && window.SourceAInteract.brainExtraChips
          ? window.SourceAInteract.brainExtraChips()
          : [];
      extras.forEach(({ label, message }) => {
        chipDefs.splice(chipDefs.length - 1, 0, {
          label,
          action: () => sendUserMessage(message),
        });
      });
      chipDefs.forEach(({ label, action, accent }) => {
        const b = el("button", "sa-brain-chip" + (accent ? " is-accent" : ""));
        b.type = "button";
        b.textContent = label;
        b.addEventListener("click", action);
        chips.appendChild(b);
      });
    }

    function autoGrowInput() {
      if (!input) return;
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 144) + "px";
    }

    async function showBoot() {
      addMsg("user", "Show live boot proof");
      const proof = await loadBootProof();
      addMsg("bot", formatBootHtml(proof));
      renderLiveProofPanel(proof);
    }

    function goQuiz() {
      addMsg("user", "Play proof quiz");
      if (document.getElementById("sa-proof-quiz")) {
        addMsg("bot", "Scroll down — <strong>Governance Gauntlet</strong> is live. Pick ALLOW, BLOCK, or tamper-FAIL.");
        document.getElementById("proof-quiz")?.scrollIntoView({ behavior: "smooth", block: "start" });
        mountQuiz();
      } else {
        addMsg("bot", "Opening scenario page with the agentic game…");
        window.location.href = QUIZ_ANCHOR;
      }
    }

    async function sendUserMessage(text) {
      const msg = String(text || "").trim();
      if (!msg || chatBusy) return;
      addMsg("user", escapeHtml(msg));
      collapseChips();
      chatBusy = true;
      sendBtn.disabled = true;
      const typing = addMsg("bot", "<span class='sa-brain-typing-dots'><span></span><span></span><span></span></span>", {
        typing: true,
      });

      try {
        await configReady;
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), CHAT_TIMEOUT_MS);
        const r = await fetch(apiUrl(), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: msg, history: chatHistory, ...brainPageContext() }),
          signal: ctrl.signal,
        });
        clearTimeout(timer);
        const data = await r.json().catch(() => ({}));
        typing.remove();
        if (!r.ok && !data.reply) {
          addMsg(
            "bot",
            escapeHtml(chatConfig.hint_offline || "I'm offline — use the buttons below or book a call."),
            { error: true }
          );
          setProviderLabel(false, false);
          return;
        }
        const reply = data.reply || data.message || chatConfig.hint_offline || "I'm offline — use the buttons below or book a call.";
        const isError = !data.ok;
        const citeHtml = !isError ? formatCitations(data.citations) : "";
        const confHtml = !isError ? formatConfidence(data.confidence, data.retrieval) : "";
        addMsg("bot", confHtml + formatReply(reply) + citeHtml, { error: isError });
        if (!isError) {
          chatHistory.push({ role: "user", content: msg });
          chatHistory.push({ role: "assistant", content: reply });
          if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
          if (window.SourceAPulse) {
            window.SourceAPulse.track("brain_chat", {
              ok: true,
              confidence: (data.confidence && data.confidence.level) || "unknown",
              reply_mode: data.reply_mode || "llm",
            });
          }
        }
        setProviderLabel(Boolean(data.ok), false);
      } catch (_) {
        typing.remove();
        addMsg(
          "bot",
          escapeHtml(chatConfig.hint_offline || "I'm offline — use the buttons below or book a call."),
          { error: true }
        );
        setProviderLabel(false, false);
      } finally {
        chatBusy = false;
        sendBtn.disabled = false;
        input.focus();
      }
    }

    composer.addEventListener("submit", (e) => {
      e.preventDefault();
      const val = input.value.trim();
      if (!val) return;
      input.value = "";
      autoGrowInput();
      sendUserMessage(val);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        composer.requestSubmit();
      }
    });

    input.addEventListener("input", autoGrowInput);

    positioningReady.then(applyPositioningToDom);
    setProviderLabel(null, true);
    configReady.then(() =>
      checkBrainStatus(true).then((ready) => {
        setProviderLabel(ready, false);
      })
    );
    if (retryBtn) {
      retryBtn.addEventListener("click", () => {
        setProviderLabel(null, true);
        checkBrainStatus(true).then((ready) => setProviderLabel(ready, false));
      });
    }
    renderChips();
  }

  document.addEventListener("DOMContentLoaded", () => {
    mountChatbot();
    if (document.getElementById("sa-proof-quiz")) mountQuiz();
    if (window.location.hash === "#proof-quiz") {
      setTimeout(() => document.getElementById("proof-quiz")?.scrollIntoView({ behavior: "smooth" }), 400);
    }
  });
})();
