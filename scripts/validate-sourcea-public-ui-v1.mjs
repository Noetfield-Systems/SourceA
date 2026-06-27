#!/usr/bin/env node
/** Public UI — no raw internal IDs on customer pages (home, pricing, growth, platform). */
import { chromium } from "playwright";

const BASE = process.env.SOURCEA_E2E_BASE || "https://sourcea.app";
const PAGES = [
  { path: "/", name: "home" },
  { path: "/sourcea/pricing", name: "pricing" },
  { path: "/sourcea/growth", name: "growth" },
  { path: "/sourcea/platform", name: "platform" },
  { path: "/sourcea/offer", name: "offer" },
];

const FORBIDDEN = [
  /\bpp-\d{8}T/i,
  /MAC-CTL-\d+/,
  /CLOUD-SEC-\d+/,
  /\{ENTITY\}/,
  /factory\.sourcea\.app/,
  /growth\.sourcea\.local/,
];

const REQUIRED_HOME = [
  "Sample job",
  "Sample client delivery",
  "Security review",
  "Approved",
  "Ready for client call",
];

async function visibleText(page) {
  return page.evaluate(() => {
    const clone = document.body.cloneNode(true);
    clone.querySelectorAll("script, style, noscript").forEach((n) => n.remove());
    return clone.innerText || "";
  });
}

async function testPage(page, { path, name }) {
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle", timeout: 45000 });
  await page.waitForTimeout(1500);
  const text = await visibleText(page);

  for (const re of FORBIDDEN) {
    if (re.test(text)) {
      throw new Error(`${name}: forbidden pattern ${re} in visible text`);
    }
  }

  if (name === "home") {
    const phase0 = await page.evaluate(() => {
      const bar = document.getElementById("sa-phase0-proof-bar");
      return bar ? bar.innerText : "";
    });
    if (/pp-|MAC-CTL|CLOUD-SEC|Queue/i.test(phase0)) {
      throw new Error(`home: phase0 bar still shows internal codes: ${phase0.slice(0, 120)}`);
    }
    const ok = REQUIRED_HOME.some((s) => phase0.includes(s));
    if (!ok) {
      throw new Error(`home: phase0 missing human labels — got: ${phase0.slice(0, 160)}`);
    }
    const hero = await page.evaluate(() => {
      const url = document.querySelector("#sa-biz-command .sa-console-url");
      const panels = document.querySelectorAll("#sa-biz-command .sa-biz-panel");
      return { url: url?.textContent?.trim(), panels: panels.length };
    });
    if (hero.url && /factory\.sourcea/i.test(hero.url)) {
      throw new Error(`home: hero console url still internal: ${hero.url}`);
    }
    if (hero.panels > 0) {
      throw new Error(`home: live console expanded ${hero.panels} technical panels on public hero`);
    }
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  for (const p of PAGES) {
    await testPage(page, p);
    console.log(`OK ${p.name}`);
  }
  await browser.close();
  console.log(`validate-sourcea-public-ui-v1: PASS — ${PAGES.length} pages on ${BASE}`);
}

main().catch((e) => {
  console.error("validate-sourcea-public-ui-v1: FAIL", e.message || e);
  process.exit(1);
});
