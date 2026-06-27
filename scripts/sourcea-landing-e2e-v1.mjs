#!/usr/bin/env node
/**
 * SourceA green-unified landing E2E — canonical host :5180 (Agent Run).
 * Requires: npx playwright install chromium (once).
 */
import { chromium } from "playwright";

const BASE = process.env.SOURCEA_E2E_BASE || "http://127.0.0.1:5180";
const PAGES = [
  "/sourcea/",
  "/sourcea/platform.html",
  "/sourcea/team.html",
  "/sourcea/growth.html",
  "/sourcea/scenario.html",
  "/sourcea/proof.html",
  "/sourcea/proof/live.html",
  "/sourcea/compare.html",
  "/sourcea/pricing.html",
  "/sourcea/offer.html",
  "/sourcea/case-studies/",
  "/sourcea/case-studies/pureflow.html",
  "/sourcea/case-studies/agentgo.html",
  "/sourcea/security.html",
  "/sourcea/sources.html",
  "/sourcea/forge/terminal",
  "/start",
  "/sandbox",
  "/sourcea/loops/index.html",
  "/sourcea/loops/outreach.html",
  "/sourcea/loops/ops-monitor.html",
  "/sourcea/loops/research.html",
  "/sourcea/loops/eval-booking.html",
  "/sourcea/loops/session-gate.html",
  "/sourcea/loops/proof-export.html",
];
const ATTACH_PAGES = ["/sourcea/attach/agency-onepager.html"];
const WIDTHS = [
  { name: "mobile-375", w: 375, h: 812 },
  { name: "tablet-768", w: 768, h: 1024 },
  { name: "desktop-1280", w: 1280, h: 800 },
];
const NAV_HREFS = [
  "/",
  "/start",
  "/sourcea/platform",
  "/sourcea/offer",
  "/sourcea/case-studies/",
  "/sourcea/team",
  "/sourcea/growth",
  "/sourcea/scenario",
  "/sourcea/proof",
  "/sourcea/compare",
  "/sourcea/pricing",
];
const NAV_LABELS = {
  "/": "Home",
  "/start": "48h MVP",
  "/sourcea/platform": "Platform",
  "/sourcea/offer": "Offer",
  "/sourcea/case-studies/": "Case studies",
  "/sourcea/team": "Team",
  "/sourcea/growth": "Growth",
  "/sourcea/scenario": "Scenario",
  "/sourcea/proof": "Proof",
  "/sourcea/compare": "Compare",
  "/sourcea/pricing": "Pricing",
};

function normNavHref(href) {
  if (!href) return "";
  const base = href.split("#")[0].replace(/\/$/, "") || "/";
  return base.replace(/\.html$/, "");
}
const REQUIRED = {
  "/sourcea/": ["#outcomes", "#how-to-buy", ".sa-cta-band", "[data-sa-proof-cta]"],
  "/start": ["#sa-start-form", "[data-sa-proof-receipt]", "#sa-mvp-intake-form"],
  "/sandbox": ["#sa-sandbox-form-wrap", "#sa-sandbox-intake-form"],
  "/sourcea/team.html": ["#sa-biz-command", "#sa-biz-orbit", "#team", ".sa-agent-swarm-biz"],
  "/sourcea/growth.html": [".sa-growth-console", ".sa-growth-flywheel", ".sa-win-stories"],
  "/sourcea/scenario.html": ["#sa-sandbox", ".sa-sb-stage", ".sa-screen-share-script", "#proof-quiz", "#sa-proof-quiz"],
  "/sourcea/proof.html": [".sa-steps", ".sa-chain-flow", ".sa-chain-beats", "#w1-demo-film"],
  "/sourcea/proof/live.html": ["#sa-aeg-verdict", "#sa-aeg-terminal", ".sa-aeg-panel"],
  "/sourcea/compare.html": [".sa-matrix"],
  "/sourcea/security.html": ["#trust", ".sa-trust-grid"],
  "/sourcea/sources.html": ["#evidence", ".sa-evidence-grid", "#frameworks"],
  "/sourcea/pricing.html": [".sa-handoff-list"],
  "/sourcea/loops/index.html": [".sa-loop-hub-grid"],
  "/sourcea/loops/outreach.html": [".sa-email-snippet"],
};

const TRUST_PAGES = [
  "/sourcea/",
  "/sourcea/platform.html",
  "/sourcea/proof.html",
  "/sourcea/security.html",
  "/sourcea/status.html",
];

const fails = [];

function fail(msg) {
  fails.push(msg);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();

  for (const width of WIDTHS) {
    const page = await ctx.newPage();
    await page.setViewportSize({ width: width.w, height: width.h });
    for (const path of PAGES) {
      const errors = [];
      page.removeAllListeners("pageerror");
      page.removeAllListeners("console");
      page.on("pageerror", (e) => errors.push(e.message));
      page.on("console", (m) => {
        if (m.type() === "error") errors.push(m.text());
      });
      const url = `${BASE}${path}`;
      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 25000 });
      } catch (e) {
        fail(`${path} @ ${width.name}: load — ${e.message}`);
        continue;
      }
      const metrics = await page.evaluate((req) => {
        const miss = (req || []).filter((s) => !document.querySelector(s));
        const overflowX = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth;
        const toggle = document.querySelector(".ar-nav-toggle");
        const headerCta = document.querySelector(".ar-header-cta");
        return {
          miss,
          overflowX,
          navToggleVisible: toggle ? getComputedStyle(toggle).display !== "none" : false,
          headerCtaDisplay: headerCta ? getComputedStyle(headerCta).display : "missing",
          hasGrowthNav: !!document.querySelector(
            'a[href="/sourcea/growth"], a[href="/sourcea/growth.html"]'
          ),
          hasTeamNav: !!document.querySelector('a[href="/sourcea/team"], a[href="/sourcea/team.html"]'),
          hasMvpNav: !!document.querySelector('a[href="/start"], a[href="/sourcea/start"]'),
          hasSignIn: !!document.querySelector('.ar-header-signin[href="/platform"]'),
          headerCtaText: headerCta ? headerCta.textContent.trim() : "",
          navHrefs: [...document.querySelectorAll('nav.ar-nav a[data-sa-nav]')].map((a) => a.getAttribute("href")),
          headerShell: document.querySelector("header.ar-header")?.outerHTML.replace(/\s+/g, " ").trim() || "",
          hasLegacyCta: (document.body.innerText || "").includes("Get Started"),
          hasMotion: !!document.querySelector('script[src*="sourcea-motion.js"]'),
          hasAgentrun: !!document.querySelector('script[src*="agentrun.js"]'),
        };
      }, REQUIRED[path] || []);
      if (metrics.miss.length) fail(`${path} @ ${width.name}: missing ${metrics.miss.join(", ")}`);
      if (metrics.overflowX > 8) fail(`${path} @ ${width.name}: overflow ${Math.round(metrics.overflowX)}px`);
      if (width.w <= 900 && !metrics.navToggleVisible) fail(`${path} @ ${width.name}: nav toggle hidden`);
      if (width.w <= 900 && metrics.headerCtaDisplay !== "none") fail(`${path} @ ${width.name}: header CTA visible`);
      if (!metrics.hasGrowthNav) fail(`${path} @ ${width.name}: no growth nav link`);
      if (!metrics.hasTeamNav) fail(`${path} @ ${width.name}: no team nav link`);
      if (!metrics.hasMvpNav) fail(`${path} @ ${width.name}: no 48h MVP nav link`);
      if (!metrics.hasSignIn) fail(`${path} @ ${width.name}: no Sign in header`);
      if (!metrics.headerCtaText.includes("See live receipt")) fail(`${path} @ ${width.name}: header CTA not unified`);
      if (metrics.hasLegacyCta) fail(`${path} @ ${width.name}: legacy Get Started text`);
      if (width.w >= 900) {
        const got = metrics.navHrefs.map(normNavHref);
        const want = NAV_HREFS.map(normNavHref);
        if (JSON.stringify(got) !== JSON.stringify(want)) {
          fail(`${path} @ ${width.name}: nav order drift ${got.join(",")}`);
        }
      }
      if (!metrics.hasMotion || !metrics.hasAgentrun) fail(`${path} @ ${width.name}: missing scripts`);
      if (errors.length) fail(`${path} @ ${width.name}: js — ${errors.slice(0, 2).join(" | ")}`);
    }
    await page.close();
  }

  const navPage = await ctx.newPage();
  await navPage.setViewportSize({ width: 375, height: 812 });
  await navPage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  await navPage.click(".ar-nav-toggle");
  await navPage.click('a[href="/sourcea/growth"], a[href="/sourcea/growth.html"]');
  await navPage.waitForURL(/\/growth(?:\.html)?/, { timeout: 10000 });
  const title = await navPage.title();
  if (!title.includes("Growth")) fail("mobile nav flow: growth page title");
  await navPage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  const exploreLinks = await navPage.$$eval("a.sa-explore-card", (as) => as.map((a) => a.getAttribute("href")));
  for (const href of exploreLinks) {
    const target = href.startsWith("http") ? href : `${BASE}${href}`;
    try {
      await navPage.goto(target, { waitUntil: "domcontentloaded", timeout: 15000 });
    } catch (e) {
      fail(`explore link ${href}: ${e.message}`);
    }
  }
  await navPage.close();

  // Header unity — structural signature (ignores runtime is-active / is-scrolled)
  const headerPage = await ctx.newPage();
  await headerPage.setViewportSize({ width: 1280, height: 800 });
  const EXPECT_SIG = JSON.stringify({
    nav: NAV_HREFS.map((h) => `${h}:${NAV_LABELS[h]}`),
    cta: "See live receipt",
    mobile: "See live receipt",
    logo: "/",
  });
  for (const path of PAGES) {
    await headerPage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    const sig = await headerPage.evaluate(() => {
      const nav = [...document.querySelectorAll("nav.ar-nav a[data-sa-nav]")].map(
        (a) => `${a.getAttribute("href")}:${a.textContent.trim()}`
      );
      return JSON.stringify({
        nav,
        cta: document.querySelector(".ar-header-cta")?.textContent.trim() || "",
        mobile: document.querySelector(".ar-nav-cta-mobile")?.textContent.trim() || "",
        logo: document.querySelector(".ar-logo")?.getAttribute("href") || "",
      });
    });
    if (sig !== EXPECT_SIG) fail(`header unity: signature drift on ${path}`);
  }
  await headerPage.close();

  // Agency / commercial lane (home commercial at /sourcea/ + founder at /)
  const agencyPage = await ctx.newPage();
  await agencyPage.setViewportSize({ width: 1280, height: 800 });
  await agencyPage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  const commercialHome = await agencyPage.evaluate(() => ({
    ctaBand: !!document.querySelector(".sa-cta-band"),
    proofCta: !!document.querySelector("[data-sa-proof-cta]"),
    bookFallback: !!document.querySelector("[data-sa-book-fallback]"),
    chainFlow: !!document.querySelector(".sa-chain-flow"),
    metricNote: (document.body.innerText || "").includes("Illustrative") || (document.body.innerText || "").includes("pureflow"),
  }));
  if (!commercialHome.ctaBand) fail("commercial: /sourcea/ missing CTA band");
  if (!commercialHome.proofCta) fail("commercial: /sourcea/ missing proof hero CTA");
  if (!commercialHome.chainFlow) fail("commercial: /sourcea/ missing chain flow");

  await agencyPage.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const founderHome = await agencyPage.evaluate(() => ({
    chips: document.querySelectorAll(".sa-buyer-chip").length,
    toggle: !!document.querySelector(".sa-buyer-toggle"),
    mockPanel: !!document.querySelector("#sa-biz-command.sa-mock-panel"),
    pulse: !!document.getElementById("sa-pulse-feedback-fab"),
    playbook: !!document.getElementById("sa-playbook-dock"),
    chatbot: !!document.getElementById("sa-brain-chat"),
  }));
  if (founderHome.chips < 2) fail("founder: home missing buyer chips");
  if (!founderHome.toggle) fail("founder: home missing sa-buyer-toggle");
  if (!founderHome.mockPanel) fail("founder: home missing sa-mock-panel");
  if (!founderHome.pulse) fail("founder: home missing feedback FAB");
  if (!founderHome.playbook) fail("founder: home missing playbook dock");
  if (!founderHome.chatbot) fail("founder: home missing Brain chatbot");

  await agencyPage.goto(`${BASE}/sourcea/proof.html`, { waitUntil: "networkidle" });
  const proofBeats = await agencyPage.$$eval(".sa-chain-beat", (els) => els.length);
  if (proofBeats !== 6) fail(`mock: proof chain beats ${proofBeats} !== 6`);

  await agencyPage.goto(`${BASE}/sourcea/platform.html`, { waitUntil: "networkidle" });
  const platformLane = await agencyPage.evaluate(() => ({
    chips: document.querySelectorAll(".sa-buyer-chip").length,
    boot: !!document.querySelector('a[href="https://github.com/sourcea-io/sourcea-boot"]'),
    agencyLink: !!document.querySelector('a[href="/sourcea/#agency-path"]'),
  }));
  if (platformLane.chips < 2) fail("dual-lane: platform missing buyer chips");
  if (!platformLane.boot) fail("dual-lane: platform missing boot CTA");
  if (!platformLane.agencyLink) fail("dual-lane: platform missing agency path link");

  await agencyPage.goto(`${BASE}/sourcea/growth.html`, { waitUntil: "networkidle" });
  const growthWins = await agencyPage.$$eval(".sa-win-story-card", (els) => els.length);
  if (growthWins < 3) fail(`agency: growth win cards ${growthWins} < 3`);

  await agencyPage.goto(`${BASE}/sourcea/pricing.html`, { waitUntil: "networkidle" });
  const pricingText = await agencyPage.evaluate(() => document.body.innerText || "");
  if (!pricingText.includes("$3–10K")) fail("agency: pricing missing build band");
  if (!pricingText.includes("$2K") && !pricingText.includes("from $2K")) fail("agency: pricing missing retainer band");
  await agencyPage.close();

  // SMART-301 — trust strip (fallback paint — not —)
  const trustPage = await ctx.newPage();
  await trustPage.setViewportSize({ width: 1280, height: 800 });
  for (const path of TRUST_PAGES) {
    await trustPage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    try {
      await trustPage.waitForFunction(
        () => {
          const el = document.querySelector("[data-trust-receipts-lifetime]");
          const t = (el?.textContent || "").trim();
          return t && !t.includes("—") && /\d/.test(t);
        },
        { timeout: 8000 }
      );
    } catch {
      const snap = await trustPage.evaluate(
        () => document.querySelector("[data-trust-receipts-lifetime]")?.textContent || "missing"
      );
      fail(`SMART-301: receipts lifetime not live on ${path} — "${snap}"`);
    }
  }
  await trustPage.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const pill = await trustPage.evaluate(() => document.getElementById("sa-agent-pill-text")?.textContent || "");
  if (!pill || pill.includes("Checking")) {
    fail(`SMART-301: factory log/pill not painted on founder home — "${pill}"`);
  }
  await trustPage.close();

  // Live console (founder home — mock panel, no biz tabs required)
  const consolePage = await ctx.newPage();
  await consolePage.setViewportSize({ width: 1280, height: 800 });
  await consolePage.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const log = await consolePage.evaluate(() => document.getElementById("sa-factory-log")?.textContent || "");
  if (!log || log.includes("Checking latest job")) {
    fail(`console: factory log not painted — "${log}"`);
  }
  await consolePage.close();

  // Attach one-pager (standalone — no site header)
  const attachPage = await ctx.newPage();
  await attachPage.goto(`${BASE}/sourcea/attach/agency-onepager.html`, { waitUntil: "networkidle" });
  const attachOk = await attachPage.evaluate(() => ({
    h1: !!document.querySelector("h1"),
    mail: (document.body.innerText || "").includes("hello@sourcea.app"),
    pricing: (document.body.innerText || "").includes("$3–10K"),
    terminal: (document.body.innerText || "").includes("sourcea-boot --json"),
  }));
  if (!attachOk.h1) fail("attach: missing h1");
  if (!attachOk.mail) fail("attach: missing hello@sourcea.app");
  if (!attachOk.pricing) fail("attach: missing pricing band");
  if (!attachOk.terminal) fail("attach: missing honest terminal");
  await attachPage.close();

  // Brain chatbot + Governance Gauntlet quiz
  const interactPage = await ctx.newPage();
  await interactPage.goto(`${BASE}/sourcea/scenario.html`, { waitUntil: "networkidle" });
  const interactOk = await interactPage.evaluate(() => ({
    chatbot: !!document.getElementById("sa-brain-chat"),
    quiz: !!document.getElementById("sa-proof-quiz"),
    quizPrompt: (document.getElementById("sa-quiz-prompt")?.textContent || "").length > 10,
    bodyChatClass: document.body.classList.contains("sa-has-chatbot"),
  }));
  if (!interactOk.chatbot) fail("interact: missing Brain chatbot widget");
  if (!interactOk.bodyChatClass) fail("interact: missing sa-has-chatbot body class");
  if (!interactOk.quiz) fail("interact: scenario missing proof quiz section");
  if (!interactOk.quizPrompt) fail("interact: proof quiz did not mount");
  const modernShell = await interactPage.evaluate(() => ({
    pulse: !!document.querySelector('script[src*="sourcea-site-pulse-v1.js"]'),
    interact: !!document.querySelector('script[src*="sourcea-site-interact-v1.js"]'),
    feedback: !!document.getElementById("sa-pulse-feedback-fab"),
  }));
  if (!modernShell.pulse) fail("interact: missing pulse script on scenario");
  if (!modernShell.interact) fail("interact: missing interact script on scenario");
  if (!modernShell.feedback) fail("interact: missing feedback FAB on scenario");
  await interactPage.click("#sa-brain-fab");
  const chatOpen = await interactPage.evaluate(() => ({
    open: document.getElementById("sa-brain-chat")?.classList.contains("is-open"),
    overflowX: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth,
  }));
  if (!chatOpen.open) fail("interact: chatbot did not open");
  if (chatOpen.overflowX > 8) fail(`interact: chatbot open overflow ${Math.round(chatOpen.overflowX)}px`);
  const composerOk = await interactPage.evaluate(() => ({
    composer: !!document.getElementById("sa-brain-composer"),
    input: !!document.getElementById("sa-brain-input"),
  }));
  if (!composerOk.composer) fail("interact: missing Brain chat composer");
  if (!composerOk.input) fail("interact: missing Brain chat input");
  await interactPage.click('button.sa-brain-chip:has-text("What is SourceA?")');
  await interactPage.waitForFunction(
    () => {
      const bots = [...document.querySelectorAll(".sa-brain-msg-bot")].filter(
        (n) => !n.classList.contains("is-typing")
      );
      const last = bots[bots.length - 1];
      return bots.length >= 2 && (last?.textContent || "").trim().length > 40;
    },
    { timeout: 30000 }
  );
  const brainReplyOk = await interactPage.evaluate(() => {
    const offline = document.getElementById("sa-brain-offline");
    const bots = [...document.querySelectorAll(".sa-brain-msg-bot")].filter(
      (n) => !n.classList.contains("is-typing")
    );
    const last = (bots[bots.length - 1]?.textContent || "").trim();
    return {
      offlineHidden: !offline || offline.hidden,
      providerLive: document.getElementById("sa-brain-provider")?.classList.contains("is-live"),
      noInfraLeak: !(document.getElementById("sa-brain-panel")?.innerText || "").match(/openrouter/i),
      replyLen: last.length,
      hasError: !!document.querySelector(".sa-brain-msg-error"),
    };
  });
  if (!brainReplyOk.offlineHidden) fail("interact: Brain offline banner visible after reply");
  if (!brainReplyOk.providerLive) fail("interact: Brain not live after reply");
  if (!brainReplyOk.noInfraLeak) fail("interact: OpenRouter or infra leaked in Brain UI");
  if (brainReplyOk.replyLen < 40) fail("interact: Brain reply too short");
  if (brainReplyOk.hasError) fail("interact: Brain returned error message");
  const bootRes = await interactPage.goto(`${BASE}/sourcea/data/boot-proof.json`, { waitUntil: "networkidle" });
  if (!bootRes || !bootRes.ok()) fail("interact: boot-proof.json not served");
  const brainCfgRes = await interactPage.goto(`${BASE}/sourcea/data/sourcea-brain-chat-config-v1.json`, {
    waitUntil: "networkidle",
  });
  if (!brainCfgRes || !brainCfgRes.ok()) fail("interact: brain-chat-config.json not served");
  const brainCfgOk = await interactPage.evaluate(() => {
    try {
      const t = document.body.innerText || "";
      const row = JSON.parse(t);
      return Boolean(row.api_worker_url);
    } catch {
      return false;
    }
  });
  if (!brainCfgOk) fail("interact: brain-chat-config.json not valid JSON");
  await interactPage.close();

  const hubRes = await ctx.newPage();
  const hubNav = await hubRes.goto(`${BASE}/sourcea/case-studies/`, { waitUntil: "networkidle" });
  if (!hubNav || !hubNav.ok()) fail("case-studies-hub: page not 200");
  const hubOk = await hubRes.evaluate(() => ({
    grid: !!document.querySelector("[data-mode='case-studies']"),
    title: (document.title || "").toLowerCase().includes("case"),
  }));
  if (!hubOk.grid) fail("case-studies-hub: missing case-studies grid");
  await hubRes.close();

  const platPage = await ctx.newPage();
  await platPage.goto(`${BASE}/sourcea/platform`, { waitUntil: "networkidle" });
  try {
    await platPage.waitForFunction(
      () =>
        document.querySelector("#sa-products-grid[data-mounted='1']") ||
        document.querySelector("#sa-products-grid .sa-product-card"),
      { timeout: 8000 }
    );
  } catch {
    fail("platform: product grid did not mount");
  }
  await platPage.close();

  const mobilePage = await ctx.newPage();
  await mobilePage.setViewportSize({ width: 375, height: 812 });
  await mobilePage.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const mobileOk = await mobilePage.evaluate(() => ({
    overflowX: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth,
    chatbot: !!document.getElementById("sa-brain-fab"),
    feedback: !!document.getElementById("sa-pulse-feedback-fab"),
    orchestratorPad: document.body.classList.contains("sa-has-chatbot"),
  }));
  if (mobileOk.overflowX > 8) fail(`mobile-home: overflow ${Math.round(mobileOk.overflowX)}px`);
  if (!mobileOk.chatbot) fail("mobile-home: missing chatbot fab");
  if (!mobileOk.feedback) fail("mobile-home: missing feedback fab");
  await mobilePage.close();

  await browser.close();

  if (fails.length) {
    console.error("sourcea-landing-e2e-v1: FAIL");
    fails.forEach((f) => console.error(`  - ${f}`));
    process.exit(1);
  }
  console.log(`sourcea-landing-e2e-v1: PASS — ${PAGES.length} pages × ${WIDTHS.length} breakpoints + nav + ${exploreLinks.length} explore links`);
}

main().catch((e) => {
  console.error("sourcea-landing-e2e-v1: ERROR", e);
  process.exit(1);
});
