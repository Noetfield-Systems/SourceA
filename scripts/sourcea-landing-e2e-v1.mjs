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
  "/sourcea/security.html",
  "/sourcea/sources.html",
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
  "/sourcea/",
  "/sourcea/platform.html",
  "/sourcea/team.html",
  "/sourcea/growth.html",
  "/sourcea/scenario.html",
  "/sourcea/proof.html",
  "/sourcea/compare.html",
  "/sourcea/pricing.html",
];
const REQUIRED = {
  "/sourcea/": ["#sa-biz-command", "#sa-biz-orbit", "#team", "#growth", "#sandbox", ".sa-agent-swarm-biz", "#sa-orchestrator", "#reference", ".sa-buyer-chips", ".sa-buyer-toggle", ".sa-chain-beats", "#agency-flywheel", "#agency-path", ".sa-mock-panel"],
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
          hasGrowthNav: !!document.querySelector('a[href="/sourcea/growth.html"]'),
          hasTeamNav: !!document.querySelector('a[href="/sourcea/team.html"]'),
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
      if (!metrics.headerCtaText.includes("Book proof demo")) fail(`${path} @ ${width.name}: header CTA not unified`);
      if (metrics.hasLegacyCta) fail(`${path} @ ${width.name}: legacy Get Started text`);
      if (width.w >= 900 && JSON.stringify(metrics.navHrefs) !== JSON.stringify(NAV_HREFS)) {
        fail(`${path} @ ${width.name}: nav order drift ${metrics.navHrefs.join(",")}`);
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
  await navPage.click('a[href="/sourcea/growth.html"]');
  await navPage.waitForURL("**/growth.html", { timeout: 10000 });
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
    nav: NAV_HREFS.map((h) => {
      const labels = {
        "/sourcea/": "Home",
        "/sourcea/platform.html": "Platform",
        "/sourcea/team.html": "Team",
        "/sourcea/growth.html": "Growth",
        "/sourcea/scenario.html": "Scenario",
        "/sourcea/proof.html": "Verification",
        "/sourcea/compare.html": "Compare",
        "/sourcea/pricing.html": "Pricing",
      };
      return `${h}:${labels[h]}`;
    }),
    cta: "Book proof demo",
    mobile: "Book proof demo",
    logo: "/sourcea/",
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

  // Agency lane assertions (home + growth + pricing)
  const agencyPage = await ctx.newPage();
  await agencyPage.setViewportSize({ width: 1280, height: 800 });
  await agencyPage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  const homeAgency = await agencyPage.evaluate(() => ({
    chips: document.querySelectorAll(".sa-buyer-chip").length,
    toggle: !!document.querySelector(".sa-buyer-toggle"),
    activeBuyer: (document.querySelector(".sa-buyer-toggle .sa-buyer-chip.is-active")?.textContent || "").toLowerCase(),
    chainBeats: document.querySelectorAll(".sa-chain-beat").length,
    mockPanel: !!document.querySelector("#sa-biz-command.sa-mock-panel"),
    ctaHeadline: document.querySelector(".sa-cta-band h2")?.textContent || "",
    forensicCta: !!document.querySelector('.sa-cta-band a[href="/sourcea/proof/live.html"]'),
    flywheel: !!document.querySelector("#agency-flywheel .sa-growth-flywheel"),
    metricNote: (document.body.innerText || "").includes("Illustrative"),
    winCard: !!document.querySelector("#agency-path .sa-win-story-card"),
    onepager: !!document.querySelector('a[href="/sourcea/attach/agency-onepager.html"]'),
  }));
  if (homeAgency.chips < 2) fail("agency: home missing buyer chips");
  if (!homeAgency.toggle) fail("mock: home missing sa-buyer-toggle");
  if (!homeAgency.activeBuyer.includes("agency")) fail("mock: buyer toggle active lane not agency");
  if (homeAgency.chainBeats !== 6) fail(`mock: home chain beats ${homeAgency.chainBeats} !== 6`);
  if (!homeAgency.mockPanel) fail("mock: home missing sa-mock-panel on command center");
  if (!homeAgency.ctaHeadline.includes("Close clients with live proof")) fail("mock: CTA band headline drift");
  if (!homeAgency.forensicCta) fail("mock: CTA band missing forensic proof link");
  if (!homeAgency.flywheel) fail("agency: home missing flywheel");
  if (!homeAgency.metricNote) fail("agency: home missing illustrative label");
  if (!homeAgency.winCard) fail("agency: home missing featured win card");
  if (!homeAgency.onepager) fail("agency: home missing onepager CTA");
  const heroBoot = await agencyPage.$('a[href="https://github.com/sourcea-io/sourcea-boot"]');
  if (!heroBoot) fail("truth: home hero missing Try sourcea-boot link");
  const homeTerminal = await agencyPage.evaluate(() => {
    const t = document.body.innerText || "";
    return (
      t.includes("sourcea-boot --json") &&
      ["policy_version", "provider", "receipt_fresh", "queue_truth"].every((n) => t.includes(n)) &&
      !!document.querySelector(".sa-boot-terminal-label")
    );
  });
  if (!homeTerminal) fail("truth: home missing live boot terminal with four checks");

  try {
    await agencyPage.waitForFunction(
      () => /valid yes \d+\/\d+/.test(document.getElementById("sa-agent-pill-text")?.textContent || ""),
      { timeout: 5000 }
    );
  } catch {
    const snap = await agencyPage.evaluate(() => document.getElementById("sa-agent-pill-text")?.textContent || "");
    fail(`SMART-301: factory pill not live on home — "${snap}"`);
  }

  await agencyPage.goto(`${BASE}/sourcea/proof.html`, { waitUntil: "networkidle" });
  const proofBeats = await agencyPage.$$eval(".sa-chain-beat", (els) => els.length);
  if (proofBeats !== 6) fail(`mock: verification beats ${proofBeats} !== 6`);

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

  // SMART-301 — trust strip live on 5 pages (valid_yes not —)
  const trustPage = await ctx.newPage();
  await trustPage.setViewportSize({ width: 1280, height: 800 });
  for (const path of TRUST_PAGES) {
    await trustPage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    try {
      await trustPage.waitForFunction(
        () => {
          const el = document.querySelector("[data-trust-valid-yes]");
          return el && !el.textContent.includes("—") && /^\d+\/\d+$/.test(el.textContent.trim());
        },
        { timeout: 5000 }
      );
    } catch {
      const snap = await trustPage.evaluate(
        () => document.querySelector("[data-trust-valid-yes]")?.textContent || "missing"
      );
      fail(`SMART-301: trust valid_yes not live on ${path} — "${snap}"`);
    }
    const lifetime = await trustPage.evaluate(
      () => document.querySelector("[data-trust-receipts-lifetime]")?.textContent || ""
    );
    if (!lifetime || lifetime.includes("—") || !/\d/.test(lifetime)) {
      fail(`SMART-301: receipts lifetime not live on ${path} — "${lifetime}"`);
    }
  }
  await trustPage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  try {
    await trustPage.waitForFunction(
      () => {
        const t = document.getElementById("sa-agent-pill-text")?.textContent || "";
        return /valid yes \d+\/\d+/.test(t);
      },
      { timeout: 5000 }
    );
  } catch {
    const snap = await trustPage.evaluate(() => document.getElementById("sa-agent-pill-text")?.textContent || "");
    fail(`SMART-301: factory pill not painted on home — "${snap}"`);
  }
  await trustPage.close();

  // Live console tab switch (home hero)
  const consolePage = await ctx.newPage();
  await consolePage.setViewportSize({ width: 1280, height: 800 });
  await consolePage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  const aegHtml = await consolePage.evaluate(() => document.getElementById("sa-biz-command")?.innerHTML || "");
  const hasAegTerm = await consolePage.evaluate(
    () => !!document.querySelector(".sa-aeg-mini-term, .sa-w1-mini-terminal")
  );
  if (!hasAegTerm) fail("console: Live proof tab missing mini terminal");
  await consolePage.click('.sa-biz-tab[data-biz-tab="overview"]');
  await consolePage.waitForTimeout(400);
  const overviewHtml = await consolePage.evaluate(() => document.getElementById("sa-biz-command")?.innerHTML || "");
  if (overviewHtml === aegHtml) fail("console: overview tab did not swap panel content");
  await consolePage.close();

  // Attach one-pager (standalone — no site header)
  const attachPage = await ctx.newPage();
  await attachPage.goto(`${BASE}/sourcea/attach/agency-onepager.html`, { waitUntil: "networkidle" });
  const attachOk = await attachPage.evaluate(() => ({
    h1: !!document.querySelector("h1"),
    mail: (document.body.innerText || "").includes("hello@sourcea.com"),
    pricing: (document.body.innerText || "").includes("$3–10K"),
    terminal: (document.body.innerText || "").includes("sourcea-boot --json"),
  }));
  if (!attachOk.h1) fail("attach: missing h1");
  if (!attachOk.mail) fail("attach: missing hello@sourcea.com");
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
  await interactPage.click("#sa-brain-fab");
  const chatOpen = await interactPage.evaluate(() => ({
    open: document.getElementById("sa-brain-chat")?.classList.contains("is-open"),
    overflowX: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth,
  }));
  if (!chatOpen.open) fail("interact: chatbot did not open");
  if (chatOpen.overflowX > 8) fail(`interact: chatbot open overflow ${Math.round(chatOpen.overflowX)}px`);
  const bootRes = await interactPage.goto(`${BASE}/sourcea/data/boot-proof.json`, { waitUntil: "networkidle" });
  if (!bootRes || !bootRes.ok()) fail("interact: boot-proof.json not served");
  await interactPage.close();

  const mobilePage = await ctx.newPage();
  await mobilePage.setViewportSize({ width: 375, height: 812 });
  await mobilePage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  const mobileOk = await mobilePage.evaluate(() => ({
    overflowX: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth,
    secondaryActions: !!document.querySelector(".sa-hero-secondary-actions"),
    chatbot: !!document.getElementById("sa-brain-fab"),
    orchestratorPad: getComputedStyle(document.body).getPropertyValue("--sa-chat-bottom").trim().length > 0
      || document.body.classList.contains("sa-has-chatbot"),
  }));
  if (mobileOk.overflowX > 8) fail(`mobile-home: overflow ${Math.round(mobileOk.overflowX)}px`);
  if (!mobileOk.secondaryActions) fail("mobile-home: missing hero secondary actions group");
  if (!mobileOk.chatbot) fail("mobile-home: missing chatbot fab");
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
