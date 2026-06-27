#!/usr/bin/env node
/** Forge page — mobile Brain header + execution-first copy (live). */
import { chromium } from "playwright";

const BASE = process.env.SOURCEA_E2E_BASE || "https://sourcea.app";
const FORGE = "/sourcea/forge/";
const WIDTHS = [375, 466];
const POSITION =
  "AI execution platform powered by Forge — real builds, automations, and agent workflows";

async function measureHeader(page) {
  return page.evaluate(() => {
    const sub = document.querySelector(".sa-brain-head-sub");
    const handle = document.querySelector(".sa-brain-handle");
    if (!sub) return { ok: false, reason: "no subtitle el" };
    const sr = sub.getBoundingClientRect();
    const hr = handle ? handle.getBoundingClientRect() : null;
    const cs = getComputedStyle(sub);
    return {
      ok: sr.width > 120 && sr.height > 12 && parseFloat(cs.fontSize) >= 11,
      subW: Math.round(sr.width),
      subH: Math.round(sr.height),
      handleW: hr ? Math.round(hr.width) : null,
      subText: (sub.textContent || "").trim().slice(0, 120),
    };
  });
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();
  const fails = [];

  for (const w of WIDTHS) {
    const page = await ctx.newPage();
    await page.setViewportSize({ width: w, height: 812 });
    await page.goto(`${BASE}${FORGE}?cb=${Date.now()}`, { waitUntil: "networkidle", timeout: 45000 });
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (!bodyText.includes("AI execution platform powered by Forge")) {
      fails.push(`${w}px: Forge page missing execution-first positioning`);
    }
    await page.click("#sa-brain-fab");
    await page.waitForSelector(".sa-brain-panel.is-open, .sa-brain-panel:not([hidden])", { timeout: 8000 });
    const m = await measureHeader(page);
    if (!m.ok) fails.push(`${w}px: Brain subtitle crushed (${JSON.stringify(m)})`);
    else console.log(`OK ${w}px header subW=${m.subW} subH=${m.subH} handleW=${m.handleW}`);
    const greet = await page.evaluate(() => {
      const bots = [...document.querySelectorAll(".sa-brain-msg-bot")];
      return (bots[0]?.textContent || "").includes("verifiable receipt on every run");
    });
    if (!greet) fails.push(`${w}px: Brain greet missing receipt-byproduct line`);
    const ph = await page.getAttribute("#sa-brain-input", "placeholder");
    if (!ph || !/run|build|automate/i.test(ph)) fails.push(`${w}px: composer placeholder not execution-first`);
    await page.close();
  }

  await browser.close();
  if (fails.length) {
    console.error("validate-sourcea-forge-mobile-v1: FAIL");
    fails.forEach((f) => console.error("  -", f));
    process.exit(1);
  }
  console.log(`validate-sourcea-forge-mobile-v1: PASS — Forge @ ${WIDTHS.join(", ")}px on ${BASE}`);
}

main().catch((e) => {
  console.error("validate-sourcea-forge-mobile-v1: ERROR", e);
  process.exit(1);
});
