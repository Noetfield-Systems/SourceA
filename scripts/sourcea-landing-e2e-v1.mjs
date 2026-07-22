#!/usr/bin/env node
/**
 * SourceA green-unified landing E2E — canonical host :5180 (Agent Run).
 * Best effort mode:
 * - Browser mode: requires Playwright + local test server.
 * - Static mode: validates shipped HTML contracts directly from dist.
 */
import fs from "node:fs";
import path from "node:path";

const BASE = process.env.SOURCEA_E2E_BASE || "http://127.0.0.1:5180";
const IS_REMOTE_BASE = /^https?:\/\//.test(BASE);
const IS_LOCALHOST_BASE = /^https?:\/\/(localhost|127\.0\.0\.1)[:/]/.test(BASE);
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
  "/sourcea/ai-value-governance",
  "/sourcea/enterprise-ai-control-plane",
];
const WIDTHS = [
  { name: "mobile-375", w: 375, h: 812 },
  { name: "tablet-768", w: 768, h: 1024 },
  { name: "desktop-1280", w: 1280, h: 800 },
];
const BASE_NAV_LINKS = [
  "/",
  "/start",
  "/sourcea/",
  "/sourcea/offer",
  "/sourcea/pricing",
  "/sourcea/team",
  "/sourcea/growth",
  "/sourcea/proof",
  "/sourcea/compare",
];
const CORE_NAV_PATTERN = new Set(BASE_NAV_LINKS.concat(["/sourcea/platform", "/sourcea/scenario", "/sourcea/case-studies/"]));

function normNavHref(href) {
  if (!href) return "";
  const base = href.split("#")[0].replace(/\/$/, "") || "/";
  return base.replace(/\.html$/, "");
}
const REQUIRED = {
  "/sourcea/": ["#outcomes", "#how-to-start", ".sa-cta-band", "[data-sa-proof-cta]"],
  "/start": ["#sa-start-form", "[data-sa-proof-receipt]", "#sa-mvp-intake-form"],
  "/sandbox": ["#sa-sandbox-form-wrap", "#sa-sandbox-intake-form"],
  "/sourcea/team.html": ["#sa-biz-command", "#sa-biz-orbit", "#team", ".sa-agent-swarm-biz", ".sa-agent-swarm"],
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
  "/sourcea/ai-value-governance",
  "/sourcea/enterprise-ai-control-plane",
];
const LANDING_DIST = path.join(process.cwd(), "sites/SourceA-landing/green-unified/dist/sourcea");

function classifyNetworkFailure(msg) {
  const line = (msg || "").toLowerCase();
  return (
    line.includes("could not resolve host") ||
    line.includes("enotfound") ||
    line.includes("name or service not known") ||
    line.includes("network") ||
    line.includes("fetch failed") ||
    line.includes("failed to connect")
  );
}

function routeToLocalFile(route) {
  if (route === "/sourcea/" || route === "/") return path.join(LANDING_DIST, "index.html");
  if (route === "/start") return path.join(LANDING_DIST, "start.html");
  if (route === "/sandbox") return path.join(LANDING_DIST, "sandbox.html");
  const normalized = route.startsWith("/") ? route.slice(1) : route;
  const noSourceaPrefix = normalized.startsWith("sourcea/") ? normalized.slice("sourcea/".length) : normalized;
  if (noSourceaPrefix.endsWith("/")) {
    const candidate = path.join(LANDING_DIST, noSourceaPrefix, "index.html");
    if (fs.existsSync(candidate)) return candidate;
  }
  const withHtml = noSourceaPrefix.endsWith(".html") ? noSourceaPrefix : `${noSourceaPrefix}.html`;
  const direct = path.join(LANDING_DIST, withHtml);
  if (fs.existsSync(direct)) return direct;
  const regional = path.join(LANDING_DIST, "sourcea", withHtml);
  if (fs.existsSync(regional)) return regional;
  if (noSourceaPrefix.endsWith("/")) {
    const regionalDirIndex = path.join(LANDING_DIST, "sourcea", noSourceaPrefix, "index.html");
    if (fs.existsSync(regionalDirIndex)) return regionalDirIndex;
  }
  const regionalDir = path.join(LANDING_DIST, "sourcea", `${withHtml}/index.html`);
  if (fs.existsSync(regionalDir)) return regionalDir;
  return path.join(LANDING_DIST, `${withHtml}/index.html`);
}

function selectorExists(html, selector) {
  if (selector.startsWith("#")) {
    const id = selector.slice(1);
    return new RegExp(`id=(["'])${id}\\1`).test(html);
  }
  if (selector.startsWith(".")) {
    const cls = selector.slice(1);
    return new RegExp(`class=(["'])[^"']*\\b${cls}\\b[^"']*\\1`).test(html);
  }
  if (selector.startsWith("[") && selector.endsWith("]")) {
    const name = selector.slice(1, -1).split("=")[0];
    return new RegExp(`\\b${name}\\b`).test(html);
  }
  return html.includes(selector);
}

function collectLandingFailures(pathName, html) {
  const required = REQUIRED[pathName];
  if (!required) return [];

  const failures = [];
  const missingSelectors = required.filter((selector) => !selectorExists(html, selector));
  if (missingSelectors.length) {
    failures.push(`${pathName}: missing selectors -> ${missingSelectors.join(", ")}`);
  }

  const navCount = (html.match(/<nav\b/gi) || []).length;
  if (navCount === 0) {
    failures.push(`${pathName}: no <nav> tags found`);
  }

  const hasHeaderSignIn = /ar-header-signin/.test(html);
  const hasSignIn =
    /href=("|')\/platform\1/i.test(html) ||
    /href=("|')\/auth\/sign-in\1/i.test(html) ||
    /href=("|')\/sourcea\/forge\/terminal\/signin\1/i.test(html) ||
    /href=("|')\/sourcea\/forge\/terminal\/signup\1/i.test(html);
  if (hasHeaderSignIn && !hasSignIn) {
    failures.push(`${pathName}: header has ar-header-signin but no sign-in target`);
  }

  const hasMotion =
    /sourcea-motion\.js/.test(html) ||
    /agentrun\.js/.test(html) ||
    /sourcea-site-pulse-v1\.js/.test(html) ||
    /sourcea-site-interact-v1\.js/.test(html);
  if (!hasMotion) {
    failures.push(`${pathName}: no sourcea-motion.js or agentrun.js script found`);
  }

  return failures;
}

async function runRemoteLandingContract() {
  const remoteFails = [];
  for (const pathName of Object.keys(REQUIRED)) {
    const target = `${BASE}${pathName}`;
    let response;
    let html;
    try {
      response = await fetch(target, { redirect: "follow" });
    } catch (error) {
      remoteFails.push(`${pathName}: network fetch failed — ${error.message}`);
      continue;
    }
    if (!response.ok) {
      remoteFails.push(`${pathName}: load failed (${response.status} ${response.statusText})`);
      continue;
    }
    html = await response.text();
    remoteFails.push(...collectLandingFailures(pathName, html));
  }
  return remoteFails;
}

async function runRemoteTrustArtifacts() {
  const remoteTrustFailures = [];
  const routes = TRUST_PAGES;
  for (const route of routes) {
    const target = `${BASE}${route}`;
    try {
      const response = await fetch(target, { redirect: "follow" });
      if (!response.ok) {
        remoteTrustFailures.push(`${route}: trust load failed (${response.status} ${response.statusText})`);
        continue;
      }
      const html = await response.text();
      if (!/data-trust-receipts-lifetime|data-trust-governance|sa-agent-log-text/.test(html)) {
        remoteTrustFailures.push(`${route}: trust signal not found in source`);
      }
    } catch (error) {
      remoteTrustFailures.push(`${route}: trust fetch failed — ${error.message}`);
    }
  }
  return remoteTrustFailures;
}

function runStaticLandingContract() {
  const staticFails = [];
  for (const [pathName] of Object.entries(REQUIRED)) {
    const filePath = routeToLocalFile(pathName);
    if (!filePath || !fs.existsSync(filePath)) {
      staticFails.push(`${pathName}: missing dist file ${path.relative(LANDING_DIST, filePath || "missing")}`);
      continue;
    }
    const html = fs.readFileSync(filePath, "utf8");
    staticFails.push(...collectLandingFailures(pathName, html));
  }
  return staticFails;
}

function isSignInHref(href) {
  const normalized = (href || "").split("?")[0].split("#")[0].toLowerCase();
  return (
    normalized === "/platform" ||
    normalized === "/auth/sign-in" ||
    normalized === "/sourcea/forge/terminal/signin" ||
    normalized === "/sourcea/forge/terminal/signup" ||
    normalized.includes("/sign-in") ||
    normalized.includes("/signin") ||
    normalized.endsWith("/platform")
  );
}

const fails = [];

function fail(msg) {
  fails.push(msg);
}

async function main() {
  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch (error) {
    const staticFails = runStaticLandingContract();
    if (IS_REMOTE_BASE && !IS_LOCALHOST_BASE) {
      const remoteFails = await runRemoteLandingContract();
      const remoteTrustFails = await runRemoteTrustArtifacts();
      const remoteCombined = [...remoteFails, ...remoteTrustFails];
      const isRemoteNetworkOnly = remoteCombined.length > 0 && remoteCombined.every((row) => classifyNetworkFailure(row));
      if (remoteCombined.length && !isRemoteNetworkOnly) {
        console.error("sourcea-landing-e2e-v1: FAIL — browser not available; remote contract failed");
        remoteCombined.forEach((f) => console.error(`  - ${f}`));
        process.exit(1);
      }
      if (isRemoteNetworkOnly) {
        console.warn("sourcea-landing-e2e-v1: WARN — remote contract skipped (network unavailable in this environment)");
      }
    }
    if (staticFails.length) {
      console.error("sourcea-landing-e2e-v1: FAIL — static contract check");
      staticFails.forEach((f) => console.error(`  - ${f}`));
      process.exit(1);
    }
    console.log(`sourcea-landing-e2e-v1: PASS — static contract check (${Object.keys(REQUIRED).length} contracts)`);
    console.log("sourcea-landing-e2e-v1: PAGE:", `${BASE.replace(/\/$/, "")}/sourcea/`);
    console.log("sourcea-landing-e2e-v1: LOCAL_DIST:", path.resolve(LANDING_DIST, "index.html"));
    return;
  }
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
          navCount: [...document.querySelectorAll("nav.ar-nav a")].length,
          headerCtaDisplay: headerCta ? getComputedStyle(headerCta).display : "missing",
          headerActions: !!document.querySelector(".ar-header-actions"),
          signInHrefs: [...document.querySelectorAll(".ar-header-signin")].map((a) => (a.getAttribute("href") || "").toLowerCase()),
          headerCtaText: headerCta ? headerCta.textContent.trim() : "",
          navHrefs: [...document.querySelectorAll("nav.ar-nav a")].map((a) => a.getAttribute("href")),
          headerShell: document.querySelector("header.ar-header")?.outerHTML.replace(/\s+/g, " ").trim() || "",
          hasLegacyCta: (document.body.innerText || "").includes("Get Started"),
          hasMotion: !!document.querySelector('script[src*="sourcea-motion.js"]'),
          hasAgentrun: !!document.querySelector('script[src*="agentrun.js"]'),
        };
      }, REQUIRED[path] || []);
      const signInLinks = metrics.signInHrefs || [];
      metrics.hasSignIn = signInLinks.some((href) => isSignInHref(href || ""));
      if (metrics.miss.length) fail(`${path} @ ${width.name}: missing ${metrics.miss.join(", ")}`);
      if (metrics.overflowX > 8) fail(`${path} @ ${width.name}: overflow ${Math.round(metrics.overflowX)}px`);
      if (metrics.navCount === 0) fail(`${path} @ ${width.name}: missing nav`);
      if (width.w <= 900 && !metrics.navToggleVisible) fail(`${path} @ ${width.name}: nav toggle hidden`);
      if (width.w <= 900 && metrics.headerCtaDisplay !== "none") fail(`${path} @ ${width.name}: header CTA visible`);
      if (metrics.headerActions && !metrics.hasSignIn) fail(`${path} @ ${width.name}: no Sign in header`);
      if (metrics.headerActions && !metrics.headerCtaText) fail(`${path} @ ${width.name}: no header CTA`);
      if (
        metrics.headerActions &&
        !/(See live receipt|Try Forge Terminal|Try live receipt|Try forge terminal|Request a 48-hour build|Try)|Request an|Request a|See live proof/i.test(
          metrics.headerCtaText
        )
      ) {
        fail(`${path} @ ${width.name}: header CTA not aligned`);
      }
      if (metrics.hasLegacyCta) fail(`${path} @ ${width.name}: legacy Get Started text`);
      if (
        width.w >= 900 &&
        !["/start", "/sandbox"].includes(path) &&
        !metrics.navHrefs.some((href) => CORE_NAV_PATTERN.has(normNavHref(href)))
      ) {
        fail(`${path} @ ${width.name}: nav missing core lane links`);
      }
      if (!(metrics.hasMotion || metrics.hasAgentrun)) fail(`${path} @ ${width.name}: missing scripts`);
      if (errors.length) fail(`${path} @ ${width.name}: js — ${errors.slice(0, 2).join(" | ")}`);
    }
    await page.close();
  }

  const navPage = await ctx.newPage();
  await navPage.setViewportSize({ width: 375, height: 812 });
  await navPage.goto(`${BASE}/sourcea/`, { waitUntil: "networkidle" });
  await navPage.click(".ar-nav-toggle");
  const navTarget = await navPage.evaluate(() => {
    const candidates = [
      "/sourcea/growth",
      "/sourcea/growth.html",
      "/sourcea/team",
      "/sourcea/team.html",
      "/sourcea/offer",
      "/sourcea/platform",
      "/sourcea/proof",
      "/sourcea/pricing",
    ];
    for (const href of candidates) {
      if (document.querySelector(`a[href="${href}"]`)) return href;
    }
    return null;
  });
  if (!navTarget) {
    fail("mobile nav flow: no buyer flow destination found in nav");
  } else {
    await navPage.click(`a[href="${navTarget}"]`);
    await navPage.waitForURL(new RegExp(`${navTarget.replace(".html", "(?:\\.html)?")}`), { timeout: 10000 });
  }
  const title = await navPage.title();
  if (!title) fail("mobile nav flow: destination has no title");
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

  // Header quality across key pages (ignores full nav-order strictness)
  const headerPage = await ctx.newPage();
  await headerPage.setViewportSize({ width: 1280, height: 800 });
  const CQA_PAGES = PAGES.filter((path) => path !== "/start" && path !== "/sandbox");
  for (const path of CQA_PAGES) {
    await headerPage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  const sig = await headerPage.evaluate(() => {
      return {
        navCount: [...document.querySelectorAll("nav.ar-nav a")].length,
        cta: document.querySelector(".ar-header-cta")?.textContent.trim() || "",
        logo: document.querySelector(".ar-logo")?.getAttribute("href") || "",
        hasHeaderActions: !!document.querySelector(".ar-header-actions"),
      };
    });
    if (!sig.logo) fail(`header unity: missing logo on ${path}`);
    if (sig.navCount === 0) fail(`header unity: missing nav on ${path}`);
    if (
      sig.hasHeaderActions &&
      !/(See live receipt|Try Forge Terminal|Request a 48-hour build|Try live receipt|Try)/i.test(sig.cta)
    ) {
      fail(`header unity: CTA drift on ${path}`);
    }
  }
  await headerPage.close();

  const FOUNDER_ROUTES = ["/sourcea/founder-home.html", "/sourcea/", "/"];
  // Agency / commercial lane (home commercial at /sourcea/ + founder variants)
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

  let founderHome = null;
  let founderPath = null;
  for (const path of FOUNDER_ROUTES) {
    await agencyPage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    const snapshot = await agencyPage.evaluate(() => ({
      pageMarker: document.body?.dataset?.saPage || "",
      chips: document.querySelectorAll(".sa-buyer-chip").length,
      segmentCards: document.querySelectorAll(".sa-segment-card").length,
      heroPanel: !!document.querySelector("#sa-biz-command"),
      pulse: !!document.getElementById("sa-pulse-feedback-fab"),
      chatbot: !!document.getElementById("sa-brain-chat"),
      trustNote: (document.body.innerText || "").includes("Trust") || (document.body.innerText || "").includes("proof"),
    }));
    if (
      snapshot.pageMarker === "founder-home" ||
      snapshot.heroPanel ||
      snapshot.chips > 0 ||
      snapshot.segmentCards > 0
    ) {
      founderHome = snapshot;
      founderPath = path;
      break;
    }
  }
  if (!founderHome || !founderPath) fail("founder: no founder route detected");
  if (founderHome.chips + founderHome.segmentCards < 1) fail("founder: home missing entry cards/chips");
  if (!founderHome.heroPanel) fail("founder: home missing hero command panel");
  if (!founderHome.pulse) fail("founder: home missing feedback FAB");
  if (!founderHome.chatbot) fail("founder: home missing Brain chatbot");
  if (!founderHome.trustNote) fail("founder: home missing trust messaging copy");

  await agencyPage.goto(`${BASE}/sourcea/proof.html`, { waitUntil: "networkidle" });
  const proofBeats = await agencyPage.$$eval(".sa-chain-beat", (els) => els.length);
  if (proofBeats !== 6) fail(`mock: proof chain beats ${proofBeats} !== 6`);

  await agencyPage.goto(`${BASE}/sourcea/platform.html`, { waitUntil: "networkidle" });
  const platformLane = await agencyPage.evaluate(() => ({
    chips: document.querySelectorAll(".sa-buyer-chip").length,
    apiHook: !!document.querySelector("#platform-api"),
    procurement: (document.body.innerText || "").includes("procurement"),
  }));
  if (platformLane.chips < 2) fail("dual-lane: platform missing buyer chips");
  if (!platformLane.apiHook) fail("dual-lane: platform missing API hook");
  if (!platformLane.procurement) fail("dual-lane: platform missing procurement signal");

  await agencyPage.goto(`${BASE}/sourcea/growth.html`, { waitUntil: "networkidle" });
  const growthWins = await agencyPage.$$eval(".sa-win-story-card", (els) => els.length);
  if (growthWins < 2) fail(`agency: growth win cards ${growthWins} < 2`);

  await agencyPage.goto(`${BASE}/sourcea/pricing.html`, { waitUntil: "networkidle" });
  const pricingText = await agencyPage.evaluate(() => document.body.innerText || "");
  const buildBandMatch = /\$\s*3(?:[.,]000)?\s*[–-]\s*\$?\s*10(?:[.,]000)?/i.test(pricingText)
    || /\$3\s*[-–]\s*10K/i.test(pricingText);
  const retainerMatch = /\$\s*2(?:,?000)?\b/i.test(pricingText) || /\$2K/i.test(pricingText);
  if (!buildBandMatch) fail("agency: pricing missing build band");
  if (!retainerMatch) fail("agency: pricing missing retainer band");
  await agencyPage.close();

  // SMART-301 — trust strip (fallback paint — not —)
  const trustPage = await ctx.newPage();
  await trustPage.setViewportSize({ width: 1280, height: 800 });
  let trustSamplePath = TRUST_PAGES[0] || "/sourcea/";
  for (const path of TRUST_PAGES) {
    await trustPage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    trustSamplePath = path;
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
  const trustSignal = await trustPage.evaluate(() => {
    const receiptValues = [...document.querySelectorAll("[data-trust-receipts-lifetime]")]
      .map((el) => (el.textContent || "").trim())
      .filter((value) => value && value !== "—");
    return {
      receipt: receiptValues[0] || "",
      logText: document.querySelector(".sa-agent-log-text")?.textContent?.trim() || "",
      governance: document.querySelector("[data-trust-governance]")?.textContent?.trim() || "",
    };
  });
  if (!trustSignal.receipt && !trustSignal.logText && !trustSignal.governance) {
    fail(`SMART-301: trust signal not found on ${trustSamplePath}`);
  }
  await trustPage.close();

  // Live console (founder home — mock panel, no biz tabs required)
  const consolePage = await ctx.newPage();
  await consolePage.setViewportSize({ width: 1280, height: 800 });
  const consoleCandidates = ["/sourcea/founder-home.html", "/sourcea/team.html", "/sourcea/"];
  let log = "";
  for (const path of consoleCandidates) {
    await consolePage.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    log = await consolePage.evaluate(() => document.querySelector("#sa-factory-log")?.textContent?.trim() || "");
    if (log) break;
  }
  if (!log) {
    fail("console: factory log not found on founder/team route");
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
