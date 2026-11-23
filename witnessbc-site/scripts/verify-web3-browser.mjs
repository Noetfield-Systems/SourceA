import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const base=process.env.WITNESS_WEB3_BASE||'http://127.0.0.1:8091';
const live=Boolean(process.env.WITNESS_WEB3_BASE);
const route=(s)=>base+(s==='index'?'/':'/'+s);
const browser=await chromium.launch({headless:true});
try{
 for(const width of [320,390,1440]){
  const page=await browser.newPage({viewport:{width,height:850},reducedMotion:'reduce'});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const resp=await page.goto(route('index'),{waitUntil:'networkidle'});
  assert.equal(resp.status(),200,'Home HTTP 200 '+width);
  assert.match(await page.locator('h1').innerText(),/Stand for dignity/i);
  assert.equal(await page.locator('a[href="/genesis"]').count()>0,true);
  assert.equal(await page.locator('a[href="/quests"]').count()>0,true);
  assert.ok(await page.locator('.brand-hex').count(),'Original Witness geometric symbol is restored');
  assert.ok(await page.locator('.witness-workbench').count(),'Original policy control-panel composition is restored');
  assert.equal(await page.locator('.core-orb').count(),0,'Borrowed glowing green orb cannot remain');
  const brandLight=await page.evaluate(()=>({
    theme:document.documentElement.dataset.theme,
    background:getComputedStyle(document.body).backgroundColor,
    family:getComputedStyle(document.body).fontFamily,
    primary:getComputedStyle(document.querySelector('.nav-join')).backgroundColor
  }));
  assert.equal(brandLight.theme,'light','Witness must default to its original light theme');
  assert.equal(brandLight.background,'rgb(255, 255, 255)','Original Witness white site background');
  assert.match(brandLight.family,/Inter/i,'Original Witness typography');
  assert.equal(brandLight.primary,'rgb(14, 116, 144)','Slate-blue Witness primary CTA (not BuildRelay green)');
  await page.locator('#themeToggle').click();
  assert.equal(await page.locator('html').getAttribute('data-theme'),'dark','Original light/dark switch works');
  assert.equal(await page.evaluate(()=>getComputedStyle(document.body).backgroundColor),'rgb(6, 10, 15)','Dark theme matches original slate-black design');
  await page.locator('#themeToggle').click();
  assert.equal(await page.locator('html').getAttribute('data-theme'),'light','Restored light mode');
  let overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  if(overflow>2){const offenders=await page.evaluate(()=>Array.from(document.querySelectorAll('body *')).map(el=>({el,right:el.getBoundingClientRect().right,left:el.getBoundingClientRect().left})).filter(x=>x.right>innerWidth+2||x.left< -2).slice(0,10).map(x=>({tag:x.el.tagName,className:typeof x.el.className==='string'?x.el.className.slice(0,80):'',left:Math.round(x.left),right:Math.round(x.right)})));console.error(JSON.stringify({width,overflow,offenders}));}
  assert.ok(overflow<=2,'Home horizontal overflow '+overflow+' at '+width);
  if(width<=390){
   const menu=page.locator('#menuToggle');
   assert.ok(await menu.isVisible());
   await menu.click();
   assert.equal(await menu.getAttribute('aria-expanded'),'true');
   assert.ok(await page.locator('#mobileNav a[href="/guild"]').isVisible());
   await page.locator('#mobileNav a[href="/guild"]').click();
   await page.waitForURL('**/guild');
   assert.match(await page.locator('h1').innerText(),/people.*ship the proof/is);
  }else{
   assert.ok(await page.locator('.desktop-nav a[href="/guild"]').isVisible());
  }
  const all=['genesis','quests','arena','reputation','governance','economy','builders','manifesto','guild','dignity','dignity/report','dignity/cases','dignity/cases/richmond-delivery','dignity/press','dignity/standards','dignity/atlas','dignity/track','dignity/operations'];
  for(const name of all){
   const response=await page.goto(route(name),{waitUntil:'domcontentloaded'});
   assert.equal(response.status(),200,name+' HTTP '+width);
   assert.ok(await page.locator('main h1').count(),name+' has headline');
   overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
   assert.ok(overflow<=2,name+' overflow '+overflow+' at '+width);
  }
  const q=await page.goto(route('quests'),{waitUntil:'domcontentloaded'});
  assert.equal(q.status(),200);
  for(const xp of ['80 XP','150 XP','100 XP'])assert.ok((await page.locator('body').innerText()).includes(xp));
  await page.goto(route('genesis'),{waitUntil:'domcontentloaded'});
  assert.ok(await page.locator('a[href*="#/pilot/witness-ai-builders"]').count(),'Community Economy real pilot link');
  await page.goto(route('arena'),{waitUntil:'domcontentloaded'});
  await page.locator('[data-scenario="leak"]').click();
  assert.equal(await page.locator('#scenarioVerdict').innerText(),'BLOCK');
  await page.locator('[data-scenario="read"]').click();
  assert.equal(await page.locator('#scenarioVerdict').innerText(),'ALLOW');
  assert.ok((await page.locator('body').innerText()).includes('LOCAL SIMULATION ONLY'));
  // The simulated API tests only frontend state; no real record or company action is created.
  await page.goto(route('dignity/report'),{waitUntil:'domcontentloaded'});
  await page.route('**/api/dignity/report',async route=>route.fulfill({status:201,contentType:'application/json',body:JSON.stringify({saved:true,id:'WBC-20261123-aaaaaaaaaaaaaaaaaaaa',accessCode:'fixture-not-real',status:'received'})}));
  await page.locator('select[name="category"]').selectOption('Delivery / gig work');
  await page.locator('input[name="place"]').fill('Richmond, BC');
  await page.locator('input[name="when"]').fill('November 2026');
  await page.locator('textarea[name="account"]').fill('I experienced repeated disrespect at a restaurant pickup over several visits.');
  await page.locator('input[name="consent"]').check();
  await page.locator('#dignitySubmit').click();
  assert.ok(await page.locator('#dignityReceipt').isVisible(),'Receipt shown only for simulated successful storage response');
  await page.unroute('**/api/dignity/report');
  assert.deepEqual(errors,[],width+'px JS errors');
  await page.close();
  console.log('PASS WITNESS WEB3 '+width+'px: 19 routes, real Genesis links, 3 quests, 2 policy interactions, navigation, no overflow/errors');
 }
}finally{await browser.close();}
