/**
 * SourceA Brain chatbot + Governance Gauntlet proof quiz.
 * Loads live boot-proof.json from deploy inject; honest illustrative game only.
 */
(function () {
  "use strict";

  const BOOT_URL = "/sourcea/data/boot-proof.json";
  const QUIZ_ANCHOR = "/sourcea/scenario.html#proof-quiz";
  const DEMO_URL = "https://cal.com/sourcea/proof-demo";

  const SCENARIOS = [
    {
      agent: "Outreach agent · 2:03am",
      prompt:
        "Founder is asleep. I queued 47 cold emails with no opt-out footer. Brain says ship for pipeline?",
      correct: "BLOCK",
      feedback: {
        BLOCK: "Correct. Guard blocks bulk sends without compliance footer. Receipt on disk.",
        ALLOW: "Nope — that's a CAN-SPAM nap nightmare. Policy says BLOCK.",
        "tamper-FAIL": "Editing the queue count doesn't fool the spine. Tamper-FAIL.",
      },
    },
    {
      agent: "Prove agent · demo prep",
      prompt:
        "Discovery call in 8 minutes. Run sourcea-boot --json and attach verdict before screen-share?",
      correct: "ALLOW",
      feedback: {
        ALLOW: "Yes. Real boot checks beat slide theater. Buyers nod at PASS/BLOCK on disk.",
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

  function el(tag, cls, html) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  async function loadBootProof() {
    if (bootProof) return bootProof;
    try {
      const r = await fetch(BOOT_URL, { cache: "no-store" });
      if (r.ok) bootProof = await r.json();
    } catch (_) {
      /* offline / pre-inject */
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
        feedback.textContent = `Final score: ${quizScore}/${SCENARIOS.length}. Same beats we screen-share on proof calls.`;
        feedback.className = "sa-quiz-feedback is-win";
      }
      if (next) {
        next.hidden = false;
        next.textContent = "Book proof demo →";
        next.onclick = () => window.open(DEMO_URL, "_blank", "noopener");
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
    document.getElementById("sa-quiz-score").textContent = `Score: ${quizScore}`;
  }

  function mountChatbot() {
    if (document.getElementById("sa-brain-chat")) return;

    const wrap = el("div", "sa-brain-chat", "");
    wrap.id = "sa-brain-chat";
    wrap.innerHTML = `
      <div class="sa-brain-backdrop" id="sa-brain-backdrop" hidden aria-hidden="true"></div>
      <button type="button" class="sa-brain-fab" id="sa-brain-fab" aria-expanded="false" aria-controls="sa-brain-panel">
        <span class="sa-brain-fab-dot"></span>
        <span class="sa-brain-fab-label">Brain</span>
      </button>
      <div class="sa-brain-panel" id="sa-brain-panel" hidden role="dialog" aria-label="Brain assistant">
        <header class="sa-brain-head">
          <span class="sa-brain-handle" aria-hidden="true"></span>
          <span>◎ Brain</span>
          <button type="button" class="sa-brain-close" id="sa-brain-close" aria-label="Close">×</button>
        </header>
        <div class="sa-brain-messages" id="sa-brain-messages"></div>
        <div class="sa-brain-chips" id="sa-brain-chips"></div>
      </div>`;
    document.body.appendChild(wrap);
    document.body.classList.add("sa-has-chatbot");

    const fab = document.getElementById("sa-brain-fab");
    const panel = document.getElementById("sa-brain-panel");
    const backdrop = document.getElementById("sa-brain-backdrop");
    const close = document.getElementById("sa-brain-close");
    const messages = document.getElementById("sa-brain-messages");
    const chips = document.getElementById("sa-brain-chips");

    function toggle(open) {
      const on = typeof open === "boolean" ? open : panel.hidden;
      panel.hidden = !on;
      if (backdrop) {
        backdrop.hidden = !on;
        backdrop.setAttribute("aria-hidden", String(!on));
      }
      wrap.classList.toggle("is-open", on);
      fab.setAttribute("aria-expanded", String(on));
      document.body.classList.toggle("sa-brain-open", on);
      if (on && !messages.dataset.greeted) {
        messages.dataset.greeted = "1";
        addMsg(
          "bot",
          "Hi — I'm Brain. Want <strong>live boot proof</strong>, the <strong>Governance Gauntlet</strong> quiz, or a demo slot?"
        );
        renderChips();
      }
      if (on) close.focus();
    }

    fab.addEventListener("click", () => toggle());
    close.addEventListener("click", () => toggle(false));
    if (backdrop) backdrop.addEventListener("click", () => toggle(false));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && wrap.classList.contains("is-open")) toggle(false);
    });

    function addMsg(role, html) {
      const m = el("div", `sa-brain-msg sa-brain-msg-${role}`);
      m.innerHTML = html;
      messages.appendChild(m);
      messages.scrollTop = messages.scrollHeight;
    }

    function renderChips() {
      chips.innerHTML = "";
      [
        { label: "Live boot proof", action: showBoot },
        { label: "Play proof quiz", action: goQuiz },
        { label: "Book proof demo", action: () => window.open(DEMO_URL, "_blank", "noopener") },
        { label: "Proof chain", action: () => (window.location.href = "/sourcea/proof.html") },
      ].forEach(({ label, action }) => {
        const b = el("button", "sa-brain-chip");
        b.type = "button";
        b.textContent = label;
        b.addEventListener("click", action);
        chips.appendChild(b);
      });
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
