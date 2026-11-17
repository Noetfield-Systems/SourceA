import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const base=process.env.WITNESS_WEB3_BASE||'http://127.0.0.1:8091';
const live=Boolean(process.env.WITNESS_WEB3_BASE);
const route=(s)=>base+(live?(s==='index'?'/':'/'+s):'/'+s+'.html');
const browser=await chromium.launch({headless:true});
try{
 for(const width of [320,390,1440]){
  const page=await browser.newPage({viewport:{width,height:850},reducedMotion:'reduce'});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const resp=await page.goto(route('index'),{waitUntil:'networkidle'});
  assert.equal(resp.status(),200,'Home HTTP 200 '+width);
  assert.match(await page.locator('h1').innerText(),/Build the rules/i);
  assert.equal(await page.locator('a[href="/genesis"]').count()>0,true);
  assert.equal(await page.locator('a[href="/quests"]').count()>0,true);
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
   await page.waitForURL('**/guild'+(live?'':'.html'));
   assert.match(await page.locator('h1').innerText(),/people.*ship the proof/is);
  }else{
   assert.ok(await page.locator('.desktop-nav a[href="/guild"]').isVisible());
  }
  const all=['genesis','quests','arena','reputation','governance','economy','builders','manifesto','guild'];
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
  assert.deepEqual(errors,[],width+'px JS errors');
  await page.close();
  console.log('PASS WITNESS WEB3 '+width+'px: 10 routes, real Genesis links, 3 quests, 2 policy interactions, navigation, no overflow/errors');
 }
}finally{await browser.close();}
