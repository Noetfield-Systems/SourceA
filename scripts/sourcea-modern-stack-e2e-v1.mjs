#!/usr/bin/env node
/**
 * SourceA modern stack E2E — pulse · interact · Cal overlay · feedback · start/sandbox.
 * Default: https://sourcea.app (live). Override: SOURCEA_E2E_BASE=http://127.0.0.1:5180
 */
import { chromium } from "playwright";

const BASE = process.env.SOURCEA_E2E_BASE || "https://sourcea.app";
const CAL_HOST = "cal.com";
const fails = [];

function fail(msg) {
  fails.push(msg);
}

async function fetchJson(path) {
  const r = await fetch(`${BASE}${path}`, { redirect: "follow" });
  if (!r.ok) throw new Error(`${path} status ${r.status}`);
  return r.json();
}

async function main() {
  // Disk / CDN config gates
  const configs = [
    "/sourcea/data/sourcea-site-interact-v1.json",
    "/sourcea/data/sourcea-site-pulse-config-v1.json",
    "/sourcea/data/sourcea-landing-cta-v1.json",
    "/sourcea/data/phase1-proof-pack-public-v1.json",
  ];
  for (const path of configs) {
    try {
      const row = await fetchJson(path);
      if (!row.schema) fail(`config ${path}: missing schema`);
    } catch (e) {
      fail(`config ${path}: ${e.message}`);
    }
  }

  try {
    const cta = await fetchJson("/sourcea/data/sourcea-landing-cta-v1.json");
    if (!String(cta.proof_url || "").includes("proof")) {
      fail(`landing-cta proof_url missing proof path — ${cta.proof_url}`);
    }
    if (cta.hero_primary !== "proof") fail(`landing-cta hero_primary should be proof — ${cta.hero_primary}`);
    const interact = await fetchJson("/sourcea/data/sourcea-site-interact-v1.json");
    if (!Array.isArray(interact.skills) || interact.skills.length < 4) {
      fail(`interact config: expected >=4 skills`);
    }
    if (!Array.isArray(interact.guided_prompts) || interact.guided_prompts.length < 5) {
      fail(`interact config: expected >=5 segment doors, got ${interact.guided_prompts?.length || 0}`);
    }
  } catch (e) {
    fail(`cta/interact gate: ${e.message}`);
  }

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();

  const scriptPaths = [
    "/sourcea/sourcea-site-pulse-v1.js",
    "/sourcea/sourcea-site-interact-v1.js",
    "/sourcea/sourcea-segment-router-v1.js",
    "/sourcea/sourcea-chatbot.js",
    "/sourcea/sourcea-site-fallback-v1.js",
  ];
  for (const path of scriptPaths) {
    const res = await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded", timeout: 20000 });
    if (!res?.ok()) fail(`asset ${path} not 200`);
  }

  await page.goto(`${BASE}/`, { waitUntil: "networkidle", timeout: 35000 });
  const shell = await page.evaluate(() => ({
    pulse: !!document.querySelector('script[src*="sourcea-site-pulse-v1.js"]'),
    interact: !!document.querySelector('script[src*="sourcea-site-interact-v1.js"]'),
    segment: !!document.querySelector('script[src*="sourcea-segment-router-v1.js"]'),
    chatbot: !!document.getElementById("sa-brain-chat"),
    feedbackFab: !!document.getElementById("sa-pulse-feedback-fab"),
    playbook: !!document.getElementById("sa-playbook-dock"),
    proofCta: !!document.querySelector("[data-sa-proof-cta]"),
    bookFallback: !!document.querySelector("[data-sa-book-fallback]"),
  }));
  if (!shell.pulse) fail("home: missing pulse script");
  if (!shell.interact) fail("home: missing interact script");
  if (!shell.segment) fail("home: missing segment router script");
  if (!shell.chatbot) fail("home: Brain not mounted");
  if (!shell.feedbackFab) fail("home: feedback FAB missing");
  if (!shell.playbook) fail("home: playbook dock missing");
  if (!shell.proofCta) fail("home: proof hero CTA missing");
  if (!shell.bookFallback) fail("home: book fallback CTA missing");

  // Cal inline overlay (fallback only — playbook human skill)
  await page.click("#sa-playbook-dock .sa-playbook-toggle");
  await page.waitForTimeout(200);
  await page.click('.sa-playbook-skill[data-sa-skill-id="book-demo"]');
  await page.waitForTimeout(800);
  const cal = await page.evaluate(() => ({
    overlay: !!document.getElementById("sa-cal-overlay") && !document.getElementById("sa-cal-overlay").hidden,
    frame: document.querySelector(".sa-cal-overlay-frame")?.src || "",
    bodyClass: document.body.classList.contains("sa-cal-open"),
  }));
  if (!cal.overlay) fail("cal: overlay did not open on book CTA");
  if (!cal.frame.includes(CAL_HOST)) fail(`cal: iframe src missing cal.com — ${cal.frame}`);
  if (!cal.bodyClass) fail("cal: body missing sa-cal-open");
  await page.click(".sa-cal-overlay-close");
  await page.waitForTimeout(300);
  const calClosed = await page.evaluate(() => document.getElementById("sa-cal-overlay")?.hidden !== false);
  if (!calClosed) fail("cal: overlay did not close");

  // Playbook skills
  await page.click("#sa-playbook-dock .sa-playbook-toggle");
  await page.waitForTimeout(200);
  const skills = await page.$$eval(".sa-playbook-skill strong", (els) => els.map((e) => e.textContent.trim()));
  if (skills.length < 4) fail(`playbook: expected >=4 skills, got ${skills.length}`);
  if (!skills.some((s) => /receipt|learn|quiz|mvp|human/i.test(s))) fail(`playbook: skill labels unexpected — ${skills.join(", ")}`);

  // Learn on-ramp page
  await page.goto(`${BASE}/learn`, { waitUntil: "networkidle", timeout: 35000 });
  const learn = await page.evaluate(() => ({
    steps: document.querySelectorAll(".sa-learn-step").length,
    quiz: !!document.querySelector('a[href*="proof-quiz"]'),
    receipt: !!document.querySelector('a[href*="proof/live"]'),
  }));
  if (learn.steps < 3) fail(`learn: expected 3 steps, got ${learn.steps}`);
  if (!learn.quiz) fail("learn: missing quiz step link");
  if (!learn.receipt) fail("learn: missing live receipt step link");

  // Segment strip on subpage (pricing)
  await page.goto(`${BASE}/sourcea/pricing`, { waitUntil: "networkidle", timeout: 35000 });
  await page.waitForTimeout(600);
  const segmentStrip = await page.evaluate(() => ({
    cards: document.querySelectorAll(".sa-segment-strip-section .sa-segment-card").length,
    script: !!document.querySelector('script[src*="sourcea-segment-router-v1.js"]'),
  }));
  if (segmentStrip.cards < 5) fail(`segment strip: expected 5 cards on pricing, got ${segmentStrip.cards}`);

  // Feedback panel UI (left FAB — avoid Brain intercept)
  await page.evaluate(() => document.getElementById("sa-pulse-feedback-fab")?.click());
  await page.waitForTimeout(200);
  const fb = await page.evaluate(() => ({
    open: !document.getElementById("sa-pulse-feedback-panel")?.hidden,
    types: document.querySelectorAll(".sa-pulse-type-chip").length,
  }));
  if (!fb.open) fail("feedback: panel did not open");
  if (fb.types < 3) fail(`feedback: expected type chips, got ${fb.types}`);

  // Start page — proof receipt + intake
  await page.goto(`${BASE}/start`, { waitUntil: "networkidle", timeout: 35000 });
  const start = await page.evaluate(() => ({
    receipt: !!document.querySelector("[data-sa-proof-receipt]"),
    form: !!document.getElementById("sa-mvp-intake-form"),
    proofHero: !!document.querySelector("[data-sa-proof-cta]"),
    verdict: (document.querySelector("[data-proof-receipt-verdict]")?.textContent || "").length > 2,
  }));
  if (!start.receipt) fail("start: missing proof receipt card");
  if (!start.form) fail("start: missing MVP intake form");
  if (!start.proofHero) fail("start: missing proof hero CTA");
  if (!start.verdict) fail("start: proof verdict not painted");

  // Sandbox intake
  await page.goto(`${BASE}/sandbox`, { waitUntil: "networkidle", timeout: 35000 });
  const sandbox = await page.evaluate(() => ({
    form: !!document.getElementById("sa-sandbox-intake-form"),
    receipt: !!document.querySelector("[data-sa-proof-receipt]"),
  }));
  if (!sandbox.form) fail("sandbox: missing intake form");
  if (!sandbox.receipt) fail("sandbox: missing proof receipt preview");

  // Brain + Report bug chip
  await page.goto(`${BASE}/sourcea/offer`, { waitUntil: "networkidle", timeout: 35000 });
  await page.click("#sa-brain-fab");
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    const chips = [...document.querySelectorAll("button.sa-brain-chip")];
    const bug = chips.find((b) => b.textContent.includes("Report a bug"));
    bug?.click();
  });
  await page.waitForTimeout(300);
  const fbFromBrain = await page.evaluate(
    () => !document.getElementById("sa-pulse-feedback-panel")?.hidden
  );
  const hasBugChip = await page.evaluate(() =>
    [...document.querySelectorAll("button.sa-brain-chip")].some((b) => b.textContent.includes("Report a bug"))
  );
  if (!hasBugChip) fail("brain: missing Report a bug chip");
  if (!fbFromBrain) fail("brain: Report a bug did not open feedback panel");

  // Pulse stats API (worker)
  try {
    const stats = await fetch(
      "https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev/api/site/stats/v1"
    );
    const row = await stats.json();
    if (!row.ok) fail("pulse worker stats: not ok");
  } catch (e) {
    fail(`pulse worker stats: ${e.message}`);
  }

  await browser.close();

  if (fails.length) {
    console.error("sourcea-modern-stack-e2e-v1: FAIL");
    fails.forEach((f) => console.error(`  - ${f}`));
    process.exit(1);
  }
  console.log(`sourcea-modern-stack-e2e-v1: PASS — ${BASE} (pulse · interact · cal · feedback · start · sandbox)`);
}

main().catch((e) => {
  console.error("sourcea-modern-stack-e2e-v1: ERROR", e);
  process.exit(1);
});
