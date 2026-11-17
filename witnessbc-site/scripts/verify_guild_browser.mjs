import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const base = 'http://127.0.0.1:8091';
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 850 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    const response = await page.goto(base + '/guild.html', { waitUntil: 'networkidle' });
    assert.equal(response.status(), 200, 'Guild returns HTTP 200 at ' + width);
    assert.match(await page.locator('h1').innerText(), /Build AI governance/i);
    assert.equal(await page.locator('.guild-quest').count(), 3);
    assert.equal(await page.locator('.guild-quest .guild-xp').count(), 3);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if(overflow > 2){
      const offenders=await page.evaluate(()=>
        [...document.querySelectorAll('body *')].map(el=>({el,right:el.getBoundingClientRect().right,left:el.getBoundingClientRect().left}))
          .filter(o=>o.right>innerWidth+2).slice(0,14).map(o=>({
            tag:o.el.tagName,className:typeof o.el.className==='string'?o.el.className.slice(0,80):'',
            right:Math.round(o.right),left:Math.round(o.left)
          })));
      console.error(JSON.stringify({viewport:width,overflow,offenders}));
    }
    assert.ok(overflow <= 2, 'horizontal overflow ' + overflow + 'px at width ' + width);
    const join = page.locator('.guild-actions [data-guild-link]').first();
    await join.scrollIntoViewIfNeeded();
    assert.ok(await join.isVisible(), 'join path visible at ' + width);
    const destination = new URL(await join.getAttribute('href'));
    assert.equal(destination.hostname, 'community-economy-production.up.railway.app');
    assert.match(destination.hash, /pilot\/witness-ai-builders/);
    assert.equal(destination.searchParams.get('utm_source'), 'witnessbc');
    const checkout = page.locator('[data-guild-checkout="starter"]');
    assert.ok(await checkout.isVisible(), 'direct existing-merchant checkout is visible at ' + width);
    const checkoutUrl = new URL(await checkout.getAttribute('href'));
    assert.equal(checkoutUrl.hostname,'buy.stripe.com');
    assert.equal(checkoutUrl.pathname,'/28EdR9efteMT2xyfHo4Ni07');
    assert.match(checkoutUrl.searchParams.get('client_reference_id')||'',/^wbc_guild_[a-f0-9]{24}$/);
    assert.equal(checkoutUrl.searchParams.get('utm_source'),'witnessbc');
    assert.ok(await page.locator('a[href*="buildrelay-staging-staging.up.railway.app/projects"]').count(), 'BuildRelay deep link exists');


    if (width <= 390) {
      const menu = page.locator('#menuToggle');
      await menu.click();
      assert.ok(await page.locator('#mainNav a[href="guild.html"]').isVisible(), 'mobile Guild navigation accessible');
    } else {
      assert.ok(await page.locator('#mainNav a[href="guild.html"]').isVisible(), 'desktop Guild navigation accessible');
    }
    assert.deepEqual(errors, [], 'JavaScript errors at ' + width);
    await page.close();
    process.stdout.write('PASS Guild viewport: ' + width + 'px\n');
  }
  const page = await browser.newPage({ viewport: { width: 1440, height: 850 } });
  for (const [route,required] of [
    ['/', 'Agentic governance'],
    ['/proof.html', 'Proof Lab'],
    ['/pricing.html', 'Pricing'],
    ['/toolkits.html', 'Toolkits'],
    ['/observe/index.html', 'Observe'],
  ]) {
    const response = await page.goto(base + route, { waitUntil: 'domcontentloaded' });
    assert.equal(response.status(), 200, 'regression HTTP 200: ' + route);
    assert.match((await page.locator('body').innerText()).toLowerCase(), new RegExp(required.toLowerCase()), route);
  }
  assert.ok(await page.locator('a[href*="guild.html"]').count() >= 1);
  await page.close();
  process.stdout.write('PASS Witness existing commercial and product routes\n');
} finally {
  await browser.close();
}
