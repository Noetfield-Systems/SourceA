#!/usr/bin/env node
/**
 * Browser QA for the SourceA v4 app studio in a local production-dist server.
 * Uses a downloaded Playwright Chromium on GitHub Actions; no external app APIs.
 */
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const { chromium }=require('playwright');
const base=process.env.SOURCEA_QA_URL||'http://127.0.0.1:8765';
const shots=process.env.SOURCEA_QA_SCREENSHOTS||'/tmp/sourcea-app-studio-screenshots';
const sizes=[{name:'phone320',width:320,height:750},{name:'phone390',width:390,height:844},{name:'tablet768',width:768,height:1024},{name:'desktop1440',width:1440,height:900}];
(async()=>{
  fs.mkdirSync(shots,{recursive:true});
  const browser=await chromium.launch({headless:true});
  const results=[];
  const mirraInvite = 'https://sourcea.app/?utm_source=app_studio&utm_medium=share&utm_campaign=mirra#mirra';
  try{
    for(const size of sizes){
      const page=await browser.newPage({viewport:{width:size.width,height:size.height},deviceScaleFactor:1,reducedMotion:'reduce'});
      const errors=[];
      page.on('pageerror',e=>errors.push({message:e.message,stack:e.stack}));
      await page.addInitScript(()=>{window.__studioShareAttempts=[];Object.defineProperty(navigator,'share',{configurable:true,value:async payload=>{window.__studioShareAttempts.push(payload);}});});
      const response=await page.goto(base+'/sourcea/app-studio.html',{waitUntil:'domcontentloaded',timeout:30000});
      await page.locator('#studio-title').waitFor();
      await page.evaluate(()=>document.fonts.ready);
      const dimensions=await page.evaluate(()=>({
        innerWidth:window.innerWidth,
        documentWidth:document.documentElement.scrollWidth,
        bodyWidth:document.body.scrollWidth,
        title:document.title,
        hero:getComputedStyle(document.querySelector('.studio-hero')).display,
        css:getComputedStyle(document.querySelector('body')).backgroundColor
      }));
      const overflow=Math.max(dimensions.documentWidth,dimensions.bodyWidth)-dimensions.innerWidth;
      const cardCount=await page.locator('.work-card').count();
      const ownership=await page.locator('.ownership-note').innerText();
      if(response.status()!==200)throw Error(size.name+': HTTP '+response.status());
      if(overflow>2)throw Error(size.name+': '+overflow+'px horizontal overflow '+JSON.stringify(dimensions));
      if(dimensions.css==='rgba(0, 0, 0, 0)')throw Error(size.name+': stylesheet did not load');
      if(cardCount!==3)throw Error(size.name+': expected exactly 3 live product cards, got '+cardCount);
      if(!ownership.includes('independently branded'))throw Error(size.name+': independent ownership notice missing');
      await page.locator('[data-studio-share="mirra"]').click();
      const sharePayload=await page.evaluate(()=>window.__studioShareAttempts[0]);
      if(!sharePayload||sharePayload.url!==mirraInvite)throw Error(size.name+': live MIRRA share payload was not dispatched');
      if(!(await page.locator('#studio-share-status').innerText()).includes('Shared'))throw Error(size.name+': share status was not announced');
      if(errors.length)throw Error(size.name+': JS errors: '+JSON.stringify(errors));
      if(size.width<=768){
        const toggle=page.locator('.nav-toggle');
        await toggle.click();
        if(await toggle.getAttribute('aria-expanded')!=='true')throw Error(size.name+': mobile menu did not open');
        await page.keyboard.press('Escape');
        if(await toggle.getAttribute('aria-expanded')!=='false')throw Error(size.name+': Escape did not close menu');
      }
      await page.screenshot({path:path.join(shots,size.name+'.png'),fullPage:true,animations:'disabled'});
      results.push({size:size.name,width:size.width,overflow,products:cardCount,jsErrors:errors.length,cssLoaded:true,mobileNavigation:size.width<=768?'PASS':'DESKTOP'});
      const home = await page.goto(base + '/', {waitUntil:'domcontentloaded'});
      if(home.status()!==200) throw Error(size.name+': public home HTTP '+home.status());
      await page.getByRole('heading', {name:'The next generation of apps starts here.'}).waitFor();
      const homeOverflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if(homeOverflow>2) throw Error(size.name+': homepage overflow '+homeOverflow);
      if(await page.locator('.home-grid-partners article').count()!==4) throw Error(size.name+': four outreach paths are required');
      if(await page.getByRole('link',{name:'Open Forge Terminal'}).getAttribute('href')!=='/sourcea/forge/terminal') throw Error(size.name+': Forge path changed');
      await page.screenshot({path:path.join(shots,'home-'+size.name+'.png'),fullPage:true,animations:'disabled'});
      await page.close();
    }
    const journey = await browser.newPage();
    const recorded = [];
    await journey.route('**/api/site/event/v1', async route => {
      recorded.push(...route.request().postDataJSON().events);
      await route.fulfill({json:{ok:true}});
    });
    await journey.addInitScript(() => localStorage.setItem('sourcea-cookie-consent-v1', JSON.stringify({
      schema:'sourcea-cookie-consent-v1', policy_version:999, categories:{analytics:true, functional:false}
    })));
    const visitRecorded = journey.waitForRequest(request =>
      request.url().endsWith('/api/site/event/v1') &&
      request.postDataJSON().events.some(row => row.event==='studio_invite_mirra_visit'));
    await journey.goto(base + new URL(mirraInvite).search + '#mirra');
    await visitRecorded;
    await journey.locator('#mirra').waitFor();
    await journey.locator('#mirra a').evaluate(link => link.addEventListener('click', event => event.preventDefault(), {once:true}));
    const clickRecorded = journey.waitForResponse(response =>
      response.url().endsWith('/api/site/event/v1') &&
      response.request().postDataJSON().events.some(row => row.event==='home_mirra_open'));
    await journey.locator('#mirra a').click();
    await journey.evaluate(() => window.SourceAPulse.flushEvents());
    await clickRecorded;
    if(!recorded.some(row => row.event==='studio_invite_mirra_visit') ||
       !recorded.some(row => row.event==='home_mirra_open') ||
       recorded.some(row => new URL(row.url).search)) throw Error('Invite journey did not produce privacy-safe visit and click events');
    await journey.close();
    console.log('SOURCEA_APP_STUDIO_BROWSER_QA_PASS '+JSON.stringify({summary:{checked:results.length,failed:0},results,screenshotDirectory:shots}));
  }finally{await browser.close()}
})().catch(e=>{console.error('SOURCEA_APP_STUDIO_BROWSER_QA_FAIL',e.stack||e);process.exitCode=1});
