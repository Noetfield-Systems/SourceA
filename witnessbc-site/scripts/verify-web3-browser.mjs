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
  assert.match(await page.locator('h1').innerText(),/Witness the world/i);
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
   assert.ok(await page.locator('#mobileNav a[href="/world"]').isVisible());
   await page.locator('#mobileNav a[href="/world"]').click();
   await page.waitForURL('**/world');
   assert.match(await page.locator('h1').innerText(),/old world.*stopped remembering/is);
  }else{
   assert.ok(await page.locator('.desktop-nav a[href="/world"]').isVisible());
  }
  const all=['genesis','commons','mythos','world','stories','circles','gatherings','fandom','collectibles','quests','arena','reputation','governance','economy','builders','manifesto','guild'];
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
  await page.goto(route('mythos'),{waitUntil:'domcontentloaded'});
  assert.equal(await page.locator('.witness-archetype-grid .card').count(),12,'Twelve mythic forces, not a fixed personality diagnosis');
  await page.locator('#witnessFirstForce').selectOption('guardian');
  await page.locator('#witnessSecondForce').selectOption('trickster');
  await page.locator('#witnessEpoch').selectOption('covenant');
  await page.locator('#witnessMakeMyth').click();
  assert.equal(await page.locator('#witnessMythTitle').innerText(),'Between the Guardian and the Trickster');
  assert.match(await page.locator('#witnessMythStory').innerText(),/meeting at the mountain/i);
  assert.equal(await page.locator('#witnessCopyMyth').isEnabled(),true);
  await page.reload({waitUntil:'domcontentloaded'});
  assert.equal(await page.locator('#witnessFirstForce').inputValue(),'guardian','Mythic paradox saved locally');
  await page.locator('#witnessSecondForce').selectOption('guardian');
  await page.locator('#witnessMakeMyth').click();
  assert.equal(await page.locator('#witnessMythTitle').innerText(),'The Double Face of the Guardian');
  await page.goto(route('world'),{waitUntil:'domcontentloaded'});
  assert.ok(await page.locator('.witness-character').count()===6,'Six original fictional Witness personalities');
  await page.locator('[data-world-choice="resist"]').click();
  assert.equal(await page.locator('#witnessWorldBranchTitle').innerText(),'The Night the Grid Went Silent');
  assert.equal(await page.locator('[data-world-choice="resist"]').getAttribute('aria-pressed'),'true');
  assert.equal(await page.locator('#witnessShareBranch').isEnabled(),true,'Story branch can be shared');
  await page.reload({waitUntil:'domcontentloaded'});
  assert.equal(await page.locator('[data-world-choice="resist"]').getAttribute('aria-pressed'),'true','Fiction choice persists across reload');
  await page.goto(route('stories'),{waitUntil:'domcontentloaded'});
  assert.ok(await page.locator('[data-copy-prompt]').count()>=3,'Original serial fiction offers creative next-step prompts');
  await page.locator('[data-copy-prompt]').first().click();
  await page.goto(route('commons'),{waitUntil:'domcontentloaded'});
  assert.match(await page.locator('h1').innerText(),/place to belong/i);
  assert.ok(await page.locator('a[href="/stories"]').count()>0);
  await page.goto(route('arena'),{waitUntil:'domcontentloaded'});
  await page.locator('[data-scenario="leak"]').click();
  assert.equal(await page.locator('#scenarioVerdict').innerText(),'BLOCK');
  await page.locator('[data-scenario="read"]').click();
  assert.equal(await page.locator('#scenarioVerdict').innerText(),'ALLOW');
  assert.ok((await page.locator('body').innerText()).includes('LOCAL SIMULATION ONLY'));
  assert.deepEqual(errors,[],width+'px JS errors');
  await page.close();
  console.log('PASS WITNESS WEB3 '+width+'px: 18 routes, mythic paradox engine, original Witness theme, interactive fiction, creative prompts, real Genesis links, 3 quests, policy interactions, navigation, no overflow/errors');
 }
}finally{await browser.close();}
