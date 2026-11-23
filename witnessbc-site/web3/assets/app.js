/* Witness public UX: no mail client, checkout, cookies, simulated memberships or wallets. */
(function(){
 'use strict';
 const themeToggle=document.getElementById('themeToggle');
 const root=document.documentElement;
 const setTheme=(theme)=>{
   const dark=theme==='dark';
   root.setAttribute('data-theme',dark?'dark':'light');
   if(themeToggle){
     themeToggle.setAttribute('aria-label',dark?'Switch to light theme':'Switch to dark theme');
     themeToggle.setAttribute('aria-pressed',String(dark));
     const icon=themeToggle.querySelector('.theme-icon');
     if(icon)icon.textContent=dark?'☼':'☾';
   }
 };
 let storedTheme='light';
 try { if(localStorage.getItem('witness-theme')==='dark')storedTheme='dark'; } catch {}
 setTheme(storedTheme);
 if(themeToggle)themeToggle.addEventListener('click',()=>{
   const next=root.getAttribute('data-theme')==='light'?'dark':'light';
   setTheme(next);
   try { localStorage.setItem('witness-theme',next); } catch {}
 });
 const $=selector=>document.querySelector(selector);
 const $$=selector=>Array.from(document.querySelectorAll(selector));
 const toggle=$('#menuToggle'),mobile=$('#mobileNav');
 if(toggle&&mobile){
   function close(){mobile.hidden=true;toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label','Open navigation');}
   toggle.addEventListener('click',function(){const open=mobile.hidden;mobile.hidden=!open;toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Close navigation':'Open navigation');});
   document.addEventListener('keydown',event=>{if(event.key==='Escape')close();});
   mobile.addEventListener('click',event=>{if(event.target.closest('a'))close();});
   window.addEventListener('resize',()=>{if(innerWidth>960)close();});
 }
 const path=location.pathname.replace(/\/$/,'')||'/';
 $$('.nav-link').forEach(link=>{if(link.getAttribute('href')===path){link.classList.add('active');link.setAttribute('aria-current','page');}});
 const toastRoot=$('#toastRoot');
 let toastTimer;
 function toast(msg){if(!toastRoot)return;clearTimeout(toastTimer);toastRoot.textContent='';const e=document.createElement('div');e.className='toast';e.textContent=msg;toastRoot.append(e);toastTimer=setTimeout(()=>e.remove(),3300);}
 const inviteUrl='https://witnessbc.com/genesis';
 const shareText='Witness Genesis: build AI governance rules, complete Web3 community quests and earn human-reviewed reputation. Join Season Zero.';
 $$('#shareLink,[data-share]').forEach(button=>button.addEventListener('click',async()=>{
   const action=button.getAttribute('data-share')||'copy';
   if(action==='copy'){
     try{await navigator.clipboard.writeText(inviteUrl+'?utm_source=member_share&utm_campaign=genesis');toast('Genesis invitation link copied.');}
     catch{toast('Copy this URL: '+inviteUrl);}
   }else{
     const link=action==='farcaster'?'https://warpcast.com/~/compose?text='+encodeURIComponent(shareText+' '+inviteUrl):
       action==='telegram'?'https://t.me/share/url?url='+encodeURIComponent(inviteUrl)+'&text='+encodeURIComponent(shareText):
       action==='x'?'https://x.com/intent/post?text='+encodeURIComponent(shareText+' '+inviteUrl):'';
     if(link)window.open(link,'_blank','noopener,noreferrer');
   }
 }));
 const defs={
   tool:{title:'Untrusted tool-call escalation',code:'agent_request: tool.execute\ntool: external_write\npolicy: require_human_review\nevidence: test-only',verdict:'REVIEW',why:'An external tool attempts a consequential write. In this illustration, the policy requires explicit review before proceeding.',type:'review'},
   leak:{title:'Sensitive context exfiltration',code:'agent_request: publish\npayload: includes_secret\npolicy: redact_or_block\nevidence: test-only',verdict:'BLOCK',why:'The simulated action exposes protected data. A safety rule blocks it and requests a sanitized public test.',type:'block'},
   read:{title:'Public repository documentation',code:'agent_request: read_docs\nsource: public_repo\npolicy: allow_public_read\nevidence: test-only',verdict:'ALLOW',why:'The simulated operation reads only public material and changes nothing. The illustrative policy allows it.',type:'allow'}
 };
 const consoleTitle=$('#scenarioTitle'),consoleCode=$('#scenarioCode'),consoleVerdict=$('#scenarioVerdict'),consoleWhy=$('#scenarioWhy');
 if(consoleTitle&&consoleCode&&consoleVerdict&&consoleWhy){
   function setScenario(id){
     const data=defs[id]||defs.tool;
     consoleTitle.textContent=data.title;
     consoleCode.textContent=data.code;
     consoleVerdict.textContent=data.verdict;
     consoleVerdict.className='console-verdict '+data.type;
     consoleWhy.textContent=data.why;
     $$('[data-scenario]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.scenario===id)));
   }
   $$('[data-scenario]').forEach(button=>button.addEventListener('click',()=>setScenario(button.dataset.scenario)));
   setScenario(new URLSearchParams(location.search).get('scenario')||'tool');
 }
 const copyArtifact=$('#copyScenario');
 if(copyArtifact)copyArtifact.addEventListener('click',async()=>{
   const selected=$('[data-scenario][aria-pressed="true"]')?.dataset.scenario||'tool';
   const d=defs[selected];
   const artifact='Witness Policy Arena — illustrative local scenario\n'+d.title+'\n'+d.code+'\nVerdict: '+d.verdict+'\nObservation: '+d.why+'\nThis is NOT a real audit or accepted quest contribution.\n\nSubmit your independently reproduced evidence via: https://community-economy-production.up.railway.app/?utm_source=witnessbc&utm_campaign=season-zero#/pilot/witness-ai-builders';
   try{await navigator.clipboard.writeText(artifact);toast('Demo note copied. Reproduce and verify before submitting.');}
   catch{toast('Clipboard unavailable; select the scenario text manually.');}
 });

 // All form content remains on the user's device until their email app sends it.
 const dignityForm=$('#dignityReportForm');
 if(dignityForm){
  const draft=$('#dignityDraft');
  const value=name=>String(dignityForm.elements.namedItem(name)?.value||'').trim();
  function compose(){
   return 'Witness BC — Dignity Concern\n'
     +'Category: '+value('category')+'\n'
     +'Location: '+value('place')+'\n'
     +'Date / period: '+value('when')+'\n'
     +'First-hand account:\n'+value('account')+'\n'
     +'Evidence: '+value('evidence')+'\n'
     +'Reply email: '+value('reply')+'\n'
     +'Please acknowledge this concern. This account is not a verified public finding.';
  }
  dignityForm.addEventListener('submit',event=>{
   event.preventDefault();
   if(!dignityForm.reportValidity())return;
   const note=compose();
   if(draft){draft.hidden=false;draft.value=note;}
   const url='mailto:hello@witnessbc.com?subject='+encodeURIComponent('Witness BC community dignity concern — '+value('place'))+'&body='+encodeURIComponent(note);
   window.location.href=url;
   toast('Your mail app was opened. Send there; the website has not submitted anything.');
  });
  const copy=$('#copyDignityDraft');
  if(copy)copy.addEventListener('click',async()=>{
   if(!dignityForm.reportValidity())return;
   const note=compose();
   if(draft){draft.hidden=false;draft.value=note;}
   try{await navigator.clipboard.writeText(note);toast('Report copied; not submitted.');}
   catch{if(draft){draft.focus();draft.select();}toast('Select and copy the prepared report.');}
  });
 }
 $('.dignity-share').forEach(button=>button.addEventListener('click',async()=>{
  const url=button.dataset.url;
  if(!url)return;
  try{await navigator.clipboard.writeText(url);toast('Public case link copied.');}
  catch{toast('Share this URL: '+url);}
 }));
 const externalLinks=$('a[target="_blank"]');
 externalLinks.forEach(link=>{link.rel='noopener noreferrer';});
})();
