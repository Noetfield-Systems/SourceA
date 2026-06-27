#!/usr/bin/env node
/**
 * Forge Terminal public demo E2E — sourcea.app/sourcea/forge/terminal
 * Requires: npx playwright install chromium (once)
 */
import { chromium } from "playwright";

const BASE = process.env.SOURCEA_E2E_BASE || "https://sourcea.app";
const DEMO_PATH = "/sourcea/forge/terminal";
const SHORT_PATH = "/forge/terminal";

function fail(msg) {
  console.error("FAIL:", msg);
  process.exit(1);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();

  const shortRes = await page.goto(`${BASE}${SHORT_PATH}`, { waitUntil: "domcontentloaded" });
  if (!shortRes || ![200, 302].includes(shortRes.status())) {
    fail(`short URL ${SHORT_PATH} status ${shortRes?.status()}`);
  }
  if (!page.url().includes("/sourcea/forge/terminal")) {
    fail(`short URL did not land on canonical demo (got ${page.url()})`);
  }

  await page.goto(`${BASE}${DEMO_PATH}`, { waitUntil: "networkidle" });
  const shellOk = await page.evaluate(() => ({
    title: document.title.includes("Forge Terminal"),
    input: !!document.getElementById("sa-ft-input"),
    send: !!document.getElementById("sa-ft-send"),
    thread: !!document.getElementById("sa-ft-thread"),
    chips: document.querySelectorAll(".sa-ft-chip").length >= 3,
    demoPage: document.body.getAttribute("data-sa-page") === "forge-terminal-demo",
  }));
  if (!shellOk.title) fail("missing Forge Terminal title");
  if (!shellOk.input || !shellOk.send || !shellOk.thread) fail("missing demo shell IDs");
  if (!shellOk.chips) fail("missing prompt chips");
  if (!shellOk.demoPage) fail("missing data-sa-page=forge-terminal-demo");

  await page.waitForFunction(
    () => {
      const t = (document.getElementById("sa-ft-status")?.textContent || "").trim();
      return t.length > 3 && t !== "Connecting…";
    },
    { timeout: 20000 },
  );
  const statusOk = await page.evaluate(() => {
    const el = document.getElementById("sa-ft-status");
    const text = (el?.textContent || "").trim();
    return {
      text,
      live: el?.classList.contains("is-live") || text.includes("Live"),
      offlineOk: text.includes("offline") || text.includes("Live"),
    };
  });
  if (!statusOk.offlineOk) fail(`status stuck or unknown: ${statusOk.text}`);

  await page.click(".sa-ft-chip");
  const chipVal = await page.inputValue("#sa-ft-input");
  if (!chipVal || chipVal.length < 10) fail("chip did not fill input");

  await page.fill("#sa-ft-input", "What is Forge Terminal in one sentence for an agency founder?");
  await page.click("#sa-ft-send");

  await page.waitForFunction(
    () => {
      const bubbles = document.querySelectorAll(".sa-ft-bubble.assistant");
      const last = bubbles[bubbles.length - 1];
      return last && !last.classList.contains("typing") && (last.textContent || "").trim().length > 40;
    },
    { timeout: 90000 },
  );

  const chatOk = await page.evaluate(() => {
    const thread = document.getElementById("sa-ft-thread");
    const text = thread?.innerText || "";
    const assistants = [...document.querySelectorAll(".sa-ft-bubble.assistant")];
    const last = (assistants[assistants.length - 1]?.textContent || "").trim();
    return {
      hasSystemForge: text.includes("Prompt forge shaped"),
      replyLen: last.length,
      noOpenRouter: !/openrouter/i.test(text),
      noJsonBlob: !/^\s*\{/.test(last),
    };
  });
  if (!chatOk.hasSystemForge) fail("missing prompt forge system bubble");
  if (chatOk.replyLen < 40) fail(`assistant reply too short (${chatOk.replyLen})`);
  if (!chatOk.noOpenRouter) fail("OpenRouter leaked in thread");
  if (!chatOk.noJsonBlob) fail("JSON blob in assistant reply");

  console.log("PASS forge terminal public demo E2E");
  console.log("  status:", statusOk.text);
  console.log("  reply_len:", chatOk.replyLen);
  await browser.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
