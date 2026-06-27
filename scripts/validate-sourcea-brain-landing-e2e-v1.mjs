#!/usr/bin/env node
/** Brain widget E2E — mount, open, chip click, OpenRouter reply (live or local). */
import { chromium } from "playwright";

const BASE = process.env.SOURCEA_E2E_BASE || "https://sourcea.app";
const PAGES = ["/sourcea/scenario", "/sourcea/growth", "/"];

const fails = [];
function fail(msg) {
  fails.push(msg);
}

async function testBrain(page, label) {
  await page.goto(`${BASE}${label === "root" ? "/" : label}`, { waitUntil: "domcontentloaded", timeout: 30000 });
  const mounted = await page.evaluate(() => ({
    chat: !!document.getElementById("sa-brain-chat"),
    fab: !!document.getElementById("sa-brain-fab"),
    script: !!document.querySelector('script[src*="sourcea-chatbot.js"]'),
  }));
  if (!mounted.chat || !mounted.fab) fail(`${label}: Brain widget not mounted`);
  if (!mounted.script) fail(`${label}: sourcea-chatbot.js not loaded`);

  await page.click("#sa-brain-fab");
  const opened = await page.evaluate(() => document.getElementById("sa-brain-chat")?.classList.contains("is-open"));
  if (!opened) fail(`${label}: Brain panel did not open`);

  await page.fill("#sa-brain-input", "What packages do you offer?");
  await page.click("#sa-brain-send");
  await page.waitForFunction(
    () => {
      const bots = [...document.querySelectorAll(".sa-brain-msg-bot")].filter((n) => !n.classList.contains("is-typing"));
      const last = bots[bots.length - 1];
      return bots.length >= 2 && (last?.textContent || "").trim().length > 40;
    },
    { timeout: 35000 }
  );

  const ok = await page.evaluate(() => {
    const providerEl = document.getElementById("sa-brain-provider");
    const offline = document.getElementById("sa-brain-offline");
    const bots = [...document.querySelectorAll(".sa-brain-msg-bot")].filter((n) => !n.classList.contains("is-typing"));
    const reply = (bots[bots.length - 1]?.textContent || "").trim();
    return {
      providerLive: providerEl?.classList.contains("is-live"),
      noInfraLeak: !(document.getElementById("sa-brain-panel")?.innerText || "").match(/openrouter/i),
      offlineHidden: !offline || offline.hidden,
      replyLen: reply.length,
      hasError: !!document.querySelector(".sa-brain-msg-error"),
    };
  });
  if (!ok.providerLive) fail(`${label}: Brain not live after reply`);
  if (!ok.noInfraLeak) fail(`${label}: infrastructure name leaked in Brain UI`);
  if (!ok.offlineHidden) fail(`${label}: offline banner still visible`);
  if (ok.replyLen < 40) fail(`${label}: reply too short (${ok.replyLen})`);
  if (ok.hasError) fail(`${label}: error message in chat`);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await testBrain(page, "/sourcea/scenario");
  await testBrain(page, "/sourcea/growth");
  await testBrain(page, "root");
  await browser.close();

  if (fails.length) {
    console.error("validate-sourcea-brain-landing-e2e-v1: FAIL");
    fails.forEach((f) => console.error(`  - ${f}`));
    process.exit(1);
  }
  console.log(`validate-sourcea-brain-landing-e2e-v1: PASS — Brain on ${BASE} (scenario + growth + home)`);
}

main().catch((e) => {
  console.error("validate-sourcea-brain-landing-e2e-v1: ERROR", e);
  process.exit(1);
});
